"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.app.api.dependencies import get_current_user, get_db
from src.app.models.user import User
from src.app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from src.app.schemas.user import UserCreate, UserResponse
from src.app.services.auth import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Authentication required or invalid credentials."},
        403: {"description": "Access denied."},
    },
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
    Create a new user account.

    - Username must be unique.
    - Email must be unique.
    - Password is securely hashed before storage.
    - Default user preferences are created automatically.
    """,
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """

    return auth_service.register(db=db, user_data=user_data)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate user",
    description="""
    Authenticate a user using email and password.

    Returns:

    - Access Token
    - Refresh Token
    - User information
    """,
)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user.
    """

    return auth_service.login(db=db, credentials=credentials)


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="""
    Generate a new access token using a valid refresh token.

    The refresh token remains valid until it expires.
    """,
)
def refresh(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token.
    """

    return auth_service.refresh(db=db, refresh_data=refresh_data)


@router.patch(
    "/change-password",
    response_model=ChangePasswordResponse,
    summary="Change current user's password",
    description="""
    Change the authenticated user's password.

    Requirements:

    - User must be authenticated.
    - Current password must be correct.
    - New password must satisfy password requirements.

    Returns a confirmation message after a successful update.
    """,
    responses={
        400: {"description": "Current password is incorrect."},
        401: {"description": "Authentication required."},
    }
)
def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change the authenticated user's password.
    """

    return auth_service.change_password(
        db=db,
        current_user=current_user,
        password_data=password_data,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout current user",
    description="""
    Logout the authenticated user.

    Since JWT authentication is stateless, no server-side session is destroyed.
    Clients should remove stored tokens after a successful logout.
    """,
)
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.
    """

    auth_service.logout()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="""
    Return the authenticated user's profile information.

    Requires a valid access token.
    """,
)
def me(current_user: User = Depends(get_current_user)):
    """
    Return authenticated user profile.
    """

    return auth_service.get_profile(current_user=current_user)
