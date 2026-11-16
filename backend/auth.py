
from fastapi import Request, HTTPException, status
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError

from config import OWNER_PASSWORD_HASH


# Prepare Argon2 password verification
password_hasher = PasswordHasher()


def verify_owner_password(password: str) -> bool:
    """Check whether the supplied password matches the owner's password hash."""
    try:
        return password_hasher.verify(OWNER_PASSWORD_HASH, password)
    except (VerificationError, InvalidHashError):
        return False


def require_auth(request: Request):
    """Prevent unauthenticated users from accessing private endpoints."""
    if request.session.get("authenticated") is not True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in to access your journal."
        )
