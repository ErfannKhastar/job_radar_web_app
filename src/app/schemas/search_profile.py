"""
Pydantic schemas for SearchProfile data validation and serialization.

This module defines the Data Transfer Objects (DTOs) used to
create, update, and return the dynamic job search filters associated
with a user and a specific job board source. This dictates exactly
*what* the automation engine should look for.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class SearchProfileCreate(BaseModel):
    """
    Schema for creating a new search profile (job alert).

    Validates that a source ID is provided, the name meets length constraints,
    and the dynamic filters are structured as a valid JSON dictionary before
    saving them to the database.
    """

    source_id: int = Field(
        ..., description="ID of the target job board source (e.g., Jobinja's ID)"
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Friendly name for this alert (e.g., 'Python Backend - Remote')",
    )

    filters: dict[str, Any] = Field(
        ...,
        description="Dynamic search criteria specific to the selected source in JSON format (e.g., keywords, location)",
    )


class SearchProfileUpdate(BaseModel):
    """
    Schema for updating an existing search profile.

    All fields are optional (PATCH requests) to allow partial updates
    (e.g., simply toggling the 'is_active' status to pause the automation).
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated friendly name for the alert",
    )

    filters: dict[str, Any] | None = Field(
        default=None, description="Updated dynamic search criteria JSON payload"
    )

    is_active: bool | None = Field(
        default=None,
        description="Master switch to pause or resume this specific automation task",
    )


class SearchProfileResponse(BaseModel):
    """
    Schema for serializing SearchProfile data in API responses.
    """

    id: int = Field(..., description="Unique ID of the search profile")
    user_id: int = Field(..., description="ID of the user who owns this profile")
    source_id: int = Field(..., description="ID of the associated job board")
    name: str = Field(..., description="Profile display name")
    filters: dict[str, Any] = Field(..., description="The applied search filters")
    is_active: bool = Field(
        ..., description="Whether the automation is currently running for this profile"
    )
    created_at: datetime
    updated_at: datetime

    # Enable ORM mode for Pydantic V2 to map seamlessly with SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True)
