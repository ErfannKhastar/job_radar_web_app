"""
Authentication service.

Contains all business logic related to user authentication.

Responsibilities:
- Register new users.
- Authenticate users.
- Refresh access tokens.
- Return current user profile.
- Handle logout.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from src.app.core.jwt import create_access_token, create_refresh_token, decode_token
from src.app.core.security import hash_password, verify_password
from src.app.core.enums import TokenType
from src.app.crud.user import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    get_user_by_id,
    update_last_login,
    update_password,
)
from src.app.crud.user_preference import create_preferences
from src.app.models.user import User
from src.app.schemas.user import UserCreate, UserResponse
from src.app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from src.app.exceptions.auth import (
    InvalidCredentialsException,
    InvalidTokenException,
    InactiveUserException,
)
from src.app.exceptions.user import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
)
from src.app.services.base import BaseService


class AuthService(BaseService):
    """
    Service responsible for authentication workflows.
    """

    def _create_tokens(self, user_id: int) -> tuple[str, str]:
        """
        Generate access and refresh tokens for a user.
        """
        return (create_access_token(user_id), create_refresh_token(user_id))

    def register(self, db: Session, user_data: UserCreate) -> UserResponse:
        """
        Register a new user.

        Steps:
        - Ensure username is unique.
        - Ensure email is unique.
        - Hash password.
        - Create user.
        - Create default user preferences.
        - Commit transaction.
        - Return created user.
        """

        if get_user_by_username(db=db, username=user_data.username):
            raise UsernameAlreadyExistsException()

        if get_user_by_email(db=db, email=user_data.email):
            raise EmailAlreadyExistsException()

        hashed_password = hash_password(user_data.password)

        try:
            user = create_user(
                db=db,
                user_data=user_data,
                hashed_password=hashed_password,
            )

            create_preferences(db=db, user_id=user.id)

            self.commit(db, user)

            return UserResponse.model_validate(user)

        except SQLAlchemyError:
            db.rollback()

            raise

    def login(
        self,
        db: Session,
        credentials: LoginRequest,
    ) -> LoginResponse:
        """
        Authenticate a user.

        Steps:
        - Verify email.
        - Verify password.
        - Ensure account is active.
        - Update last login.
        - Generate JWT tokens.
        """

        user = get_user_by_email(db=db, email=credentials.email)

        if user is None:
            raise InvalidCredentialsException()

        if not verify_password(credentials.password, user.hashed_password):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InactiveUserException()

        try:
            update_last_login(db=db, user=user)

            self.commit(db, user)

        except SQLAlchemyError:
            db.rollback()

            raise

        access_token, refresh_token = self._create_tokens(user.id)

        return LoginResponse(
            user_id=user.id,
            username=user.username,
            email=user.email,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def refresh(
        self,
        db: Session,
        refresh_data: RefreshTokenRequest,
    ) -> RefreshTokenResponse:
        """
        Generate a new access token using a refresh token.
        """

        payload = decode_token(refresh_data.refresh_token)

        if payload.type != TokenType.REFRESH:
            raise InvalidTokenException()

        user = get_user_by_id(db=db, user_id=int(payload.sub))

        if user is None:
            raise InvalidTokenException()

        if not user.is_active:
            raise InactiveUserException()

        access_token = create_access_token(user.id)

        return RefreshTokenResponse(access_token=access_token)

    def change_password(
        self,
        db: Session,
        current_user: User,
        password_data: ChangePasswordRequest,
    ) -> ChangePasswordResponse:
        """
        Change the authenticated user's password.

        Steps:
        - Verify the current password.
        - Hash the new password.
        - Update the stored password hash.
        - Commit the transaction.
        """

        if not verify_password(
            password_data.current_password,
            current_user.hashed_password,
        ):
            raise InvalidCredentialsException()

        hashed_password = hash_password(password_data.new_password)

        try:
            update_password(
                db=db,
                user=current_user,
                hashed_password=hashed_password,
            )

            self.commit(db, current_user)

        except SQLAlchemyError:
            db.rollback()
            raise

        return ChangePasswordResponse(message="Password changed successfully.")

    def logout(self) -> None:
        """
        Logout current user.

        JWT authentication is stateless, therefore no server-side
        action is required.
        """

        return None

    def get_profile(self, current_user: User) -> UserResponse:
        """
        Return the authenticated user's profile.
        """

        return UserResponse.model_validate(current_user)


auth_service = AuthService()
