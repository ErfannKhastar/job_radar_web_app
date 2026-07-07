"""
Pydantic schemas for Authentication data validation and serialization.

This module defines the Data Transfer Objects (DTOs) used for handling
user login, token generation, and token refresh processes. It ensures
that credentials and JWT payloads are strictly validated before processing.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from src.app.core.enums import TokenType


class LoginRequest(BaseModel):
    """
    Schema for validating user login credentials from the client.

    Ensures the email is properly formatted and a password is provided
    before hitting the database.
    """

    email: EmailStr = Field(..., description="User's registered email address")
    password: str = Field(..., description="Plain-text password")


class RefreshTokenRequest(BaseModel):
    """
    Schema for validating a refresh token request.

    Used when the client's access token expires and they need a new one
    without forcing the user to log in again.
    """

    refresh_token: str = Field(..., description="The unexpired refresh token string")


class TokenPayload(BaseModel):
    """
    Schema representing the decoded internal payload of a JWT.

    Used by the backend to strongly type the data extracted from a token,
    preventing key errors during authorization checks.
    """

    sub: str = Field(..., description="Subject of the token (usually the User ID)")
    type: TokenType = Field(..., description="Token type (ACCESS or REFRESH)")
    iat: datetime = Field(..., description="Issued At timestamp")
    exp: datetime = Field(..., description="Expiration timestamp")


class TokenResponse(BaseModel):
    """
    Schema for the standard token response provided upon successful authentication.
    """

    access_token: str = Field(..., description="Short-lived JWT for API access")
    refresh_token: str = Field(
        ..., description="Long-lived JWT to get new access tokens"
    )
    token_type: str = Field(default="bearer", description="The authentication scheme")


class RefreshTokenResponse(BaseModel):
    """
    Schema for the response when only a new access token is generated via a refresh token.
    """

    access_token: str = Field(..., description="Newly generated access token")
    token_type: str = Field(default="bearer", description="The authentication scheme")


class LoginResponse(BaseModel):
    """
    Schema for a comprehensive login response.

    Provides the frontend with both the authentication tokens and the basic
    user profile data needed to initialize the UI state.
    """

    user_id: int = Field(..., description="The unique ID of the authenticated user")
    username: str = Field(..., description="User's display name")
    email: EmailStr = Field(..., description="User's email address")
    access_token: str = Field(..., description="Short-lived JWT for API access")
    refresh_token: str = Field(..., description="Long-lived JWT for session renewal")
    token_type: str = Field(default="bearer", description="The authentication scheme")

    # Enable ORM mode for Pydantic V2
    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    """
    Schema for changing the authenticated user's password.

    Requires the user's current password for verification before
    allowing the new password to be securely stored.
    """

    current_password: str = Field(..., description="User's current plain-text password")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New plain-text password (will be hashed before storing)",
    )


class ChangePasswordResponse(BaseModel):
    """
    Schema returned after a successful password change.
    """

    message: str = Field(..., description="Confirmation message")
