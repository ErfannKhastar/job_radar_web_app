"""
Pydantic schemas for Source data validation and serialization.

This module defines the Data Transfer Objects (DTOs) used to
create, update, and format the target job board platforms (Sources)
that the automation engine is configured to scrape.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SourceCreate(BaseModel):
    """
    Schema for validating the creation of a new job board source.

    Acts as a gatekeeper to ensure that the source name, URL slug,
    and base URL meet strict length constraints before hitting the database.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Friendly display name of the job board (e.g., 'Jobinja')",
    )

    slug: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Unique URL-friendly identifier used in routes (e.g., 'jobinja')",
    )

    base_url: str = Field(
        ...,
        max_length=255,
        description="Main website URL or API base URL for the scraper target",
    )


class SourceUpdate(BaseModel):
    """
    Schema for validating updates to an existing job board source.

    Useful for when a target website changes its domain, or when an admin
    needs to temporarily disable scraping for a specific site.
    """

    name: str | None = Field(
        default=None, min_length=2, max_length=100, description="Updated display name"
    )

    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Updated URL-friendly identifier",
    )

    base_url: str | None = Field(
        default=None, max_length=255, description="Updated base URL"
    )

    is_active: bool | None = Field(
        default=None,
        description="Global kill-switch to enable or disable the scraper for this source",
    )


class SourceResponse(BaseModel):
    """
    Schema for serializing Source data in API responses.
    """

    id: int = Field(..., description="Unique database ID of the source")
    name: str = Field(..., description="Display name of the job board")
    slug: str = Field(..., description="URL-friendly identifier")
    base_url: str = Field(..., description="Base URL of the source")
    is_active: bool = Field(
        ..., description="Indicates if the automation is actively scraping this site"
    )
    created_at: datetime = Field(..., description="Timestamp of source creation")

    # Enable ORM mode for Pydantic V2 to map directly from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
