"""
Pydantic schemas for SearchRun data validation and serialization.

This module defines the Data Transfer Objects (DTOs) used for recording
and returning the execution logs of the background job scrapers. It ensures
that performance metrics, statuses, and error logs are consistently formatted.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# Fixed import: using the centralized Enums from the Core layer
from src.app.core.enums import SearchRunStatus


class SearchRunCreate(BaseModel):
    """
    Schema for creating a new search run log.

    This is initialized at the exact moment a scheduled background task
    starts executing to track the lifecycle of the scraping process.
    """

    search_profile_id: int = Field(
        ...,
        description="ID of the search profile currently being processed by the worker",
    )


class SearchRunUpdate(BaseModel):
    """
    Schema for updating an existing search run log.

    Used by the background worker to report back its findings (or failures)
    once the scraping execution concludes.
    """

    status: SearchRunStatus = Field(
        ..., description="Current state of the scraper run (e.g., SUCCESS, FAILED)"
    )

    jobs_found: int = Field(
        default=0,
        description="Total raw jobs scraped from the target board during this run",
    )

    new_jobs_found: int = Field(
        default=0,
        description="Number of newly discovered jobs that matched the user's filters",
    )

    error_message: str | None = Field(
        default=None,
        max_length=1000,
        description="Traceback or exception details if the scraper crashed",
    )

    finished_at: datetime | None = Field(
        default=None,
        description="Precise timestamp of when the worker finished execution",
    )


class SearchRunResponse(BaseModel):
    """
    Schema for serializing SearchRun log data in API responses.

    Provides observability for users and admins to monitor the automation engine's health.
    """

    id: int = Field(..., description="Unique ID of the execution log")
    search_profile_id: int
    status: SearchRunStatus
    jobs_found: int
    new_jobs_found: int
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None

    duration_seconds: float | None = Field(
        default=None, description="Dynamically calculated execution duration in seconds"
    )

    # Enable ORM mode for Pydantic V2 to map seamlessly with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
