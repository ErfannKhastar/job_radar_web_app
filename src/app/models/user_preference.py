"""
User Preferences Configuration Module.

This module defines the `UserPreferences` entity, which dictates the strict rules
for how the automation engine interacts with a specific user. It covers localization
(language, timezone) and delivery mechanisms (which channel to use, file formats,
and message batch sizes).
"""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import TYPE_CHECKING
from src.app.db.session import Base
from src.app.core.enums import Language, ExportFormat, NotificationChannel

if TYPE_CHECKING:
    from src.app.models.user import User


class UserPreferences(Base):
    """
    Stores the configuration and notification rules for a specific user.

    Acts as an extension of the User model (one-to-one relationship). The automation
    background workers consult this table before generating exports or dispatching
    notifications to ensure the data is formatted and routed exactly as the user requested.
    """

    __tablename__ = "user_preferences"

    # Unique identifier for the preference record
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key linking directly to the User. Enforced as unique to maintain
    # a strict 1-to-1 relationship between a user and their settings.
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    # ==========================================
    # Localization Settings
    # ==========================================

    # Determines the language of the application UI and notification templates
    language: Mapped[Language] = mapped_column(
        SqlEnum(Language),
        default=Language.EN,
        nullable=False,
    )

    # Ensures scraping schedules and delivery times align with the user's local time
    timezone: Mapped[str] = mapped_column(
        String(100),
        default="UTC",
        nullable=False,
    )

    # ==========================================
    # Automation Output & Delivery Settings
    # ==========================================

    # The primary channel the automation tool will use to send scraped jobs
    default_notification_channel: Mapped[NotificationChannel] = mapped_column(
        SqlEnum(NotificationChannel),
        default=NotificationChannel.TELEGRAM,
        nullable=False,
    )

    # The preferred file structure for data dumps (e.g., JSON for developers, XLSX for general users)
    default_export_format: Mapped[ExportFormat] = mapped_column(
        SqlEnum(ExportFormat),
        default=ExportFormat.JSON,
        nullable=False,
    )

    # Stores the specific Telegram Chat ID for bot integrations
    telegram_chat_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # A quick toggle to pause Telegram deliveries without wiping the chat_id
    telegram_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Controls batching: prevents the automation from spamming the user if a
    # specific scraping run finds hundreds of new jobs.
    max_jobs_per_notification: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )

    # ==========================================
    # System Behavior Toggles
    # ==========================================

    # If true, the system will automatically deactivate search profiles that
    # haven't yielded new results in a long period (optimizes server resources).
    auto_disable_expired_profiles: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Toggle for receiving internal app updates or server maintenance alerts
    receive_system_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ==========================================
    # SQLAlchemy Relationships
    # ==========================================

    # Reverse relationship back to the parent User model
    user: Mapped["User"] = relationship("User", back_populates="preferences")
