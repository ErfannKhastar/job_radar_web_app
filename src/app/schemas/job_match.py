"""
Pydantic schemas for JobMatch data validation and serialization.

This module defines the Data Transfer Objects (DTOs) used for recording
and returning successful matches between scraped jobs and user search profiles.
It acts as the bridge connecting the automation's findings to specific users.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class JobMatchCreate(BaseModel):
    """
    Schema for creating a new job match record.

    This is strictly used internally by the background workers when the
    automation tool successfully determines that a newly scraped job
    satisfies a user's specific search profile criteria.
    """

    search_profile_id: int = Field(
        ..., description="ID of the user's search profile that triggered this match"
    )

    job_id: int = Field(..., description="ID of the specific scraped job ad")


class JobMatchResponse(BaseModel):
    """
    Schema for serializing JobMatch data in API responses.

    Typically used when a user requests their history of found jobs via the frontend.
    """

    id: int = Field(..., description="Unique database ID for this match record")
    search_profile_id: int
    job_id: int
    matched_at: datetime = Field(
        ..., description="Timestamp of when the system identified this match"
    )

    # Enable ORM mode for Pydantic V2 to map seamlessly with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
