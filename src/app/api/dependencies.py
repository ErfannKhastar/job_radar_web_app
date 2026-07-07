"""
Authentication dependencies.

Provides reusable FastAPI dependencies for retrieving
the authenticated user from JWT tokens.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.app.core.jwt import decode_token
from src.app.crud.user import get_user_by_id
from src.app.db.session import get_db
from src.app.exceptions.auth import (
    InactiveUserException,
    InvalidTokenException,
    PermissionDeniedException,
)
from src.app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Return authenticated user from JWT.
    """

    payload = decode_token(token)

    user = get_user_by_id(
        db=db,
        user_id=int(payload.sub),
    )

    if user is None:
        raise InvalidTokenException()

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure authenticated user is active.
    """

    if not current_user.is_active:
        raise InactiveUserException()

    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Ensure authenticated user is a superuser.
    """

    if not current_user.is_superuser:
        raise PermissionDeniedException()

    return current_user
