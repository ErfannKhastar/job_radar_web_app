"""
Pydantic schemas for User data validation and serialization.

This module defines the Data Transfer Objects (DTOs) used by FastAPI
to validate incoming request payloads (registration, updates) and format
outgoing responses, strictly separating API data from database models.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """
    Schema for validating user registration data.

    Acts as a strict gatekeeper: ensures that the username meets length
    requirements, the email is structurally valid, and the password meets
    minimum length constraints before creating a database record.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username chosen by the user",
    )

    email: EmailStr = Field(
        ..., description="Valid and unique email address for communication and login"
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plain-text strong password (will be hashed by the core service)",
    )


class UserLogin(BaseModel):
    """
    Schema for validating user login credentials.
    """

    email: EmailStr = Field(..., description="User's registered email")
    password: str = Field(..., description="Plain-text password for authentication")


class UserResponse(BaseModel):
    """
    Schema for serializing User data to be returned in API responses.

    CRITICAL: This schema explicitly excludes sensitive information like
    `hashed_password` to ensure security and prevent data leaks to the frontend.
    """

    id: int = Field(..., description="Unique database identifier for the user")
    username: str = Field(..., description="User's display name")
    email: EmailStr = Field(..., description="User's email address")
    is_active: bool = Field(
        ..., description="Indicates if the account is currently enabled"
    )
    is_superuser: bool = Field(
        ..., description="Indicates if the user has admin privileges"
    )
    created_at: datetime = Field(..., description="Timestamp of account creation")

    # Enable ORM mode for Pydantic V2 to read data directly from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """
    Schema for validating user profile update requests.

    All fields are marked as optional (using `| None` and `default=None`),
    allowing the frontend to send partial updates (PATCH requests) without
    needing to submit the entire user object.
    """

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="New username if the user wishes to change it",
    )

    email: EmailStr | None = Field(
        default=None, description="New email address for the account"
    )
