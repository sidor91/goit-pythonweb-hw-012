from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
    Query,
)
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.database.users.schemas import (
    UserCreate,
    Token,
    User,
    RequestEmail,
    ResetPasswordRequest,
)
from src.auth.service import (
    create_access_token,
    Hash,
    get_email_from_token,
    create_password_reset_token,
    get_email_from_password_token,
)
from src.users.service import UserService
from src.database.config import get_db
from src.services.email.service import send_email, send_password_reset_email
from src.services.cache.service import cache_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)

    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url  # type: ignore
    )

    return new_user


# Логін користувача
@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )

    access_token = await create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    # Cache the authenticated user's minimal info to reduce DB lookups
    try:
        await cache_service.set_user_by_username(
            user.username,
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar": user.avatar,
                "role": user.role,
            },
        )
    except Exception:
        # Cache failures should not block login
        pass
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url  # type: ignore
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.post("/request_password_reset")
async def request_password_reset(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Generate password reset token, store it in Redis and send reset email."""
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )

    # Create password reset token and store it in Redis for one-time use
    token = create_password_reset_token({"sub": user.email})
    try:
        await cache_service.set_key(f"pwdreset:{token}", user.email, ex=3600)
    except Exception:
        pass

    background_tasks.add_task(
        send_password_reset_email, user.email, user.username, request.base_url
    )
    return {"message": "Password reset email sent"}


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(request: Request, token: str = Query(...)):
    """Render an HTML password reset form for the token."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset=\"utf-8\">
        <title>Reset Password</title>
    </head>
    <body>
        <h1>Reset password</h1>
        <form method=\"post\" action=\"/api/auth/reset_password?token={token}\">
            <label for=\"new_password\">New password</label><br />
            <input id=\"new_password\" name=\"new_password\" type=\"password\" required />
            <button type=\"submit\">Reset password</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.post("/reset_password")
async def reset_password(
    token: str = Query(...),
    new_password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Reset password using token from query parameter and new password in form data."""
    if not token or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token and new_password required",
        )

    # Validate token and check one-time usage in Redis
    try:
        email = await get_email_from_password_token(token)
    except HTTPException:
        raise

    cached = await cache_service.get_key(f"pwdreset:{token}")
    if not cached or cached != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    # Update password
    hashed = Hash().get_password_hash(new_password)
    user_service = UserService(db)
    user = await user_service.update_password(email, hashed)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    # Invalidate the one-time token and user cache
    try:
        await cache_service.delete_key(f"pwdreset:{token}")
        await cache_service.delete_user_by_username(user.username)
        await cache_service.delete_user(user.id)
    except Exception:
        pass

    return {"message": "Password has been reset"}
