from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, expires_minutes: int | None = None) -> str:
    minutes = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def create_purpose_token(user_id: str, purpose: str, expires_minutes: int) -> str:
    """Short-lived signed token for a single-use, non-API-access purpose
    (e.g. Telegram account linking) — distinguished from a normal access
    token via the "purpose" claim so decode_purpose_token() can reject one
    used for the wrong flow.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": str(user_id), "purpose": purpose, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_purpose_token(token: str, purpose: str) -> str | None:
    """Returns the user_id encoded in the token if it's valid, unexpired,
    and was created for this exact purpose; otherwise None."""
    payload = decode_token(token)
    if payload is None or payload.get("purpose") != purpose:
        return None
    return payload.get("sub")
