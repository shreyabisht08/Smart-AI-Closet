
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from core.config import settings


# Password hashing using Argon2
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Convert a plain password into a secure hash."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its stored hash."""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Generate a JWT access token."""

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token

def decode_access_token(token: str) -> dict | None:
    """Verify a JWT and return its payload."""

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        return payload

    except jwt.InvalidTokenError:
        return None
