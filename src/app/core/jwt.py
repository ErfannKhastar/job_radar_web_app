"""
JWT (JSON Web Token) utility module for authentication.

This module handles the generation and decoding of access and refresh tokens.
It uses the configurations defined in the settings and standardizes the token
payload for secure user sessions.
"""

import jwt
from datetime import datetime, timedelta, timezone
from src.app.core.config import settings
from src.app.exceptions.auth import ExpiredTokenException, InvalidTokenException
from src.app.schemas.auth import TokenPayload
from src.app.core.enums import TokenType


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    """
    Internal helper function to create a signed JWT.

    Args:
        subject (str): The subject of the token (typically the user's ID).
        token_type (str): The type of token (e.g., access or refresh).
        expires_delta (timedelta): The lifespan of the token.

    Returns:
        str: The encoded and signed JWT as a string.
    """
    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_access_token(user_id: int) -> str:
    """
    Generates a short-lived access token for API authorization.

    Args:
        user_id (int): The unique identifier of the user.

    Returns:
        str: The encoded access token.
    """
    expires = timedelta(minutes=settings.access_token_expire_minutes)

    return _create_token(
        subject=str(user_id),
        token_type=TokenType.ACCESS,
        expires_delta=expires,
    )


def create_refresh_token(user_id: int) -> str:
    """
    Generates a long-lived refresh token used to obtain new access tokens.

    Args:
        user_id (int): The unique identifier of the user.

    Returns:
        str: The encoded refresh token.
    """
    expires = timedelta(days=settings.refresh_token_expire_days)

    return _create_token(
        subject=str(user_id),
        token_type=TokenType.REFRESH,
        expires_delta=expires,
    )


def decode_token(token: str) -> TokenPayload:
    """
    Decodes and validates a provided JWT.

    Args:
        token (str): The JWT string to be decoded.

    Returns:
        TokenPayload: The validated token payload mapped to a Pydantic schema.

    Raises:
        ExpiredTokenException: If the token has passed its expiration time.
        InvalidTokenException: If the token is malformed or the signature is invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

    except jwt.ExpiredSignatureError:
        raise ExpiredTokenException()

    except jwt.InvalidTokenError:
        raise InvalidTokenException()

    return TokenPayload(**payload)
