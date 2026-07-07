"""
Pydantic schemas for Job data validation and serialization.

This module defines the Data Transfer Objects (DTOs) used to
validate incoming scraped job postings from the background workers
and format outgoing API responses for the frontend.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class JobCreate(BaseModel):
    """
    Schema for creating/inserting a newly scraped job posting.

    Acts as a strict validator for the raw data coming from various job boards.
    It ensures that the URL is properly formatted and string lengths do not
    exceed the PostgreSQL database column limits, preventing insertion errors.
    """

    source_id: int = Field(
        ..., description="ID of the job board source where this ad was found"
    )

    title: str = Field(
        ..., min_length=1, max_length=255, description="The official job title"
    )

    company: str = Field(
        ..., min_length=1, max_length=255, description="The hiring company's name"
    )

    location: str | None = Field(
        default=None,
        max_length=255,
        description="Job location (e.g., city, country, or 'Remote')",
    )

    url: HttpUrl = Field(
        ..., description="Unique, fully qualified URL of the job posting"
    )

    extra_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic JSON payload containing unstandardized data specific to the source (e.g., tags, salary range, seniority level)",
    )


class JobUpdate(BaseModel):
    """
    Schema for updating an existing job record.

    All core fields are optional to allow partial updates. This is particularly
    useful if the automation engine revisits a job ad and finds that the title
    or location has been modified by the employer.
    """

    title: str | None = Field(default=None, min_length=1, max_length=255)
    company: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    extra_data: dict[str, Any] | None = Field(
        default=None, description="Updated dynamic JSON data"
    )


class JobResponse(BaseModel):
    """
    Schema for serializing Job data in API responses.
    """

    id: int = Field(..., description="Unique database ID of the job")
    source_id: int = Field(..., description="ID of the source platform")
    title: str
    company: str
    location: str | None
    url: str = Field(..., description="Serialized URL string for JSON responses")
    extra_data: dict[str, Any]
    scraped_at: datetime = Field(
        ..., description="Exact time the scraper fetched this ad"
    )
    created_at: datetime
    updated_at: datetime

    # Enable ORM mode for Pydantic V2 to map seamlessly with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
