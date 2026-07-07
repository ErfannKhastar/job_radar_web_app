"""
Pydantic schemas for UserPreferences data validation and serialization.

This module defines the Data Transfer Objects (DTOs) used to validate
incoming configurations and format the customizable settings for a user,
such as localization, timezone, and delivery mechanisms.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from src.app.core.enums import Language, NotificationChannel, ExportFormat


class UserPreferencesCreate(BaseModel):
    """
    Schema for validating the initial creation of user preferences.

    Typically used automatically upon user registration to set up
    their default workspace and notification settings before they
    customize them.
    """

    language: Language = Field(
        default=Language.EN,
        description="User's preferred interface language (e.g., FA or EN)",
    )

    timezone: str = Field(
        default="UTC",
        max_length=100,
        description="User's local timezone for accurate cron scheduling",
    )

    default_notification_channel: NotificationChannel = Field(
        default=NotificationChannel.TELEGRAM,
        description="Preferred delivery method for scraped job alerts",
    )

    default_export_format: ExportFormat = Field(
        default=ExportFormat.JSON,
        description="Preferred format for exporting bulk scraped data",
    )

    telegram_chat_id: str | None = Field(
        default=None,
        max_length=100,
        description="Target Telegram chat ID (required if channel is TELEGRAM)",
    )

    telegram_notifications_enabled: bool = Field(
        default=True,
        description="Master toggle to quickly pause/resume Telegram alerts",
    )

    max_jobs_per_notification: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Limit on how many jobs to bundle in a single alert to prevent spam (1-20)",
    )

    auto_disable_expired_profiles: bool = Field(
        default=False,
        description="Automatically pause search profiles if they yield no results over time",
    )

    receive_system_notifications: bool = Field(
        default=True,
        description="Opt-in flag for system-wide announcements or critical maintenance alerts",
    )


class UserPreferencesUpdate(BaseModel):
    """
    Schema for validating partial updates to existing user preferences.

    All fields are optional (PATCH method compatibility), allowing the client
    to update only specific settings without sending the entire payload.
    """

    language: Language | None = Field(
        default=None, description="Updated interface language"
    )
    timezone: str | None = Field(
        default=None, max_length=100, description="Updated timezone"
    )
    default_notification_channel: NotificationChannel | None = Field(default=None)
    default_export_format: ExportFormat | None = Field(default=None)
    telegram_chat_id: str | None = Field(default=None, max_length=100)
    telegram_notifications_enabled: bool | None = Field(default=None)
    max_jobs_per_notification: int | None = Field(default=None, ge=1, le=20)
    auto_disable_expired_profiles: bool | None = Field(default=None)
    receive_system_notifications: bool | None = Field(default=None)


class UserPreferencesResponse(BaseModel):
    """
    Schema for serializing UserPreferences data in API responses.
    """

    id: int = Field(..., description="Unique database ID for the preference record")
    user_id: int = Field(..., description="ID of the user owning these preferences")
    language: Language
    timezone: str
    default_notification_channel: NotificationChannel
    default_export_format: ExportFormat
    telegram_chat_id: str | None
    telegram_notifications_enabled: bool
    max_jobs_per_notification: int
    auto_disable_expired_profiles: bool
    receive_system_notifications: bool
    created_at: datetime
    updated_at: datetime

    # Enable ORM mode for Pydantic V2 to map directly from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
