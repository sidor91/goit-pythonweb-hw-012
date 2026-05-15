from fastapi import APIRouter, Depends, Request, UploadFile, File
from src.database.users.schemas import User as UserSchema
from src.auth.service import get_current_user, require_role
from src.utils.limiter import limiter
from src.database.config import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.file.service import UploadFileService
from src.utils.env_variables import settings
from src.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
@limiter.limit("5/minute")  # type: ignore
async def me(request: Request, user: UserSchema = Depends(get_current_user)):
    return user


@router.patch("/avatar", response_model=UserSchema)
async def update_avatar_user(
    file: UploadFile = File(),
    user: UserSchema = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
