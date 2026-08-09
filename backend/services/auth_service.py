from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from exceptions import EmailAlreadyExistsException, InvalidCredentialsException
from models.user import User
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from utils.security import create_access_token, hash_password, verify_password


class AuthService:
    async def register(self, payload: RegisterRequest, db: AsyncSession) -> UserResponse:
        existing = await db.scalar(select(User).where(User.email == payload.email.lower()))
        if existing is not None:
            raise EmailAlreadyExistsException()

        user = User(
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            full_name=payload.full_name.strip(),
            date_of_birth=payload.date_of_birth,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserResponse.model_validate(user)

    async def login(self, payload: LoginRequest, db: AsyncSession) -> TokenResponse:
        user = await db.scalar(select(User).where(User.email == payload.email.lower()))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise InvalidCredentialsException()

        token = create_access_token(str(user.id))
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
