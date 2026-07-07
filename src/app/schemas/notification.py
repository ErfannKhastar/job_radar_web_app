"""
Pydantic schemas for Notification data validation and serialization.

This module defines the Data Transfer Objects (DTOs) used to
create, update, and return the execution logs for outgoing messages
(Telegram, Email, JSON file generation) dispatched by the automation tool.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from src.app.core.enums import NotificationChannel, NotificationStatus


class NotificationCreate(BaseModel):
    """
    Schema for creating a new notification log.

    Initialized when the automation engine prepares a batch of new jobs
    to be dispatched to the user.
    """

    search_run_id: int = Field(
        ...,
        description="ID of the associated search run that triggered this notification",
    )

    channel: NotificationChannel = Field(
        ..., description="Target delivery method (e.g., TELEGRAM, EMAIL, JSON)"
    )

    message: str | None = Field(
        default=None,
        max_length=500,
        description="Brief summary text or template payload to be sent",
    )

    jobs_sent: int = Field(
        default=0,
        description="Total number of job postings bundled in this specific alert",
    )

    file_path: str | None = Field(
        default=None,
        max_length=500,
        description="Absolute or relative path to the generated export file (if applicable)",
    )


class NotificationUpdate(BaseModel):
    """
    Schema for updating an existing notification log.

    Used by the delivery workers to update the dispatch status (SENT or FAILED)
    and log any network errors encountered during transmission.
    """

    status: NotificationStatus | None = Field(
        default=None, description="Current state of the delivery attempt"
    )

    message: str | None = Field(default=None, max_length=500)
    jobs_sent: int | None = Field(default=None)
    file_path: str | None = Field(default=None, max_length=500)

    error_details: str | None = Field(
        default=None,
        max_length=1000,
        description="Specific error or timeout details if the API call failed",
    )

    sent_at: datetime | None = Field(
        default=None,
        description="Exact timestamp when the message successfully left the server",
    )


class NotificationResponse(BaseModel):
    """
    Schema for serializing Notification log data in API responses.
    """

    id: int
    search_run_id: int
    channel: NotificationChannel
    status: NotificationStatus
    message: str | None
    jobs_sent: int
    file_path: str | None
    error_details: str | None
    sent_at: datetime | None
    created_at: datetime

    # Enable ORM mode for Pydantic V2 to map seamlessly with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
