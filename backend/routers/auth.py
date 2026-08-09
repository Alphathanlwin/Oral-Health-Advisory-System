from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from services.auth_service import AuthService
from utils.response import success_response

router = APIRouter()


@router.post("/register", status_code=201)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(AuthService),
):
    user = await auth_service.register(payload, db)
    return success_response(
        data=UserResponse.model_validate(user).model_dump(mode="json"),
        message="Account created successfully.",
    )


@router.post("/login")
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(AuthService),
):
    token = await auth_service.login(payload, db)
    return success_response(
        data=token.model_dump(mode="json"),
        message="Login successful.",
    )
