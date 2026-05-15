from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware

from src.contacts.controller import router as contacts_router
from src.utils.healthchecker import router as utils_router
from src.auth.controller import router as auth_router
from src.users.controller import router as users_router
from src.utils.env_variables import settings
from src.utils.limiter import limiter

from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

app = FastAPI()

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )

origins = settings.ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(utils_router, prefix="/api")
app.include_router(contacts_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=settings.PORT, reload=True)
