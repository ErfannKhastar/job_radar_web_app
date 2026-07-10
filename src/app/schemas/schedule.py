"""
Pydantic schemas for Schedule data validation and serialization.

This module defines the Data Transfer Objects (DTOs) used to
create, update, and return the automation timing rules for search profiles.
It dictates exactly *when* the background workers should execute tasks.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from src.app.core.enums import ScheduleType


class ScheduleCreate(BaseModel):
    """
    Schema for creating a new execution schedule.

    Ensures that time units (hour, minute, weekday) strictly fall within
    valid chronological ranges to prevent scheduler crashes.
    """

    search_profile_id: int = Field(
        ..., description="ID of the target search profile to be executed"
    )

    schedule_type: ScheduleType = Field(
        ..., description="Frequency of the schedule (e.g., daily, weekly, once)"
    )

    hour: int | None = Field(
        default=None, ge=0, le=23, description="Execution hour (0-23 in 24h format)"
    )

    minute: int | None = Field(
        default=None, ge=0, le=59, description="Execution minute (0-59)"
    )

    # Python's datetime.weekday() uses 0 for Monday and 6 for Sunday
    weekday: int | None = Field(
        default=None,
        ge=0,
        le=6,
        description="Execution day of the week (0=Monday, 6=Sunday)",
    )

    run_once_at: datetime | None = Field(
        default=None, description="Specific precise timestamp for a one-time execution"
    )


class ScheduleUpdate(BaseModel):
    """
    Schema for updating an existing schedule.

    All fields are optional to allow partial updates, such as simply
    pausing the schedule by setting is_active to False.
    """

    schedule_type: ScheduleType | None = Field(
        default=None, description="Updated frequency"
    )
    is_active: bool | None = Field(
        default=None, description="Enable or disable this specific scheduling rule"
    )
    hour: int | None = Field(default=None, ge=0, le=23)
    minute: int | None = Field(default=None, ge=0, le=59)
    weekday: int | None = Field(default=None, ge=0, le=6)
    run_once_at: datetime | None = Field(default=None)


class ScheduleResponse(BaseModel):
    """
    Schema for serializing Schedule data in API responses.
    """

    id: int = Field(..., description="Unique ID of the schedule record")
    search_profile_id: int = Field(..., description="Associated search profile ID")
    schedule_type: ScheduleType
    is_active: bool
    hour: int | None = Field(default=None, ge=0, le=23)
    minute: int | None = Field(default=None, ge=0, le=59)
    weekday: int | None = Field(default=None, ge=0, le=6)
    run_once_at: datetime | None
    cron_expression: str | None

    last_run_at: datetime | None = Field(
        default=None, description="Timestamp of the last successful execution"
    )
    next_run_at: datetime | None = Field(
        default=None, description="Calculated timestamp for the next execution"
    )

    created_at: datetime
    updated_at: datetime

    # Enable ORM mode for Pydantic V2
    model_config = ConfigDict(from_attributes=True)
