"""
Delivery and Notification Tracking Module.

This module defines the `Notification` entity, responsible for logging
every attempt the system makes to deliver scraped job data to the user.
"""

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.app.db.session import Base
from src.app.core.enums import NotificationChannel, NotificationStatus

if TYPE_CHECKING:
    from src.app.models.search_run import SearchRun


class Notification(Base):
    """
    A record of a data delivery action dispatched by the automation engine.

    Tracks whether a JSON file, Telegram message, or Email was successfully
    sent to the user after a SearchRun completes. It ensures accountability
    and aids in retrying failed deliveries.
    """

    __tablename__ = "notifications"

    # Unique identifier for the notification dispatch record
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key linking the notification to the specific execution run that generated it
    search_run_id: Mapped[int] = mapped_column(
        ForeignKey(
            "search_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # The medium used for delivery (e.g., TELEGRAM, EMAIL, JSON)
    channel: Mapped[NotificationChannel] = mapped_column(
        SqlEnum(NotificationChannel),
        nullable=False,
    )

    # Delivery status (e.g., PENDING, SENT, FAILED)
    status: Mapped[NotificationStatus] = mapped_column(
        SqlEnum(NotificationStatus),
        default=NotificationStatus.PENDING,
        nullable=False,
    )

    # Optional descriptive text or template used in the notification
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # The count of new jobs bundled in this specific notification
    jobs_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Path to the exported data file (useful if the user requested a JSON/CSV dump)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Logs reason for delivery failure (e.g., "Telegram API timeout", "Invalid Email")
    error_details: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Timestamp indicating exactly when the payload was successfully delivered
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ==========================================
    # SQLAlchemy Relationships
    # ==========================================

    # Link back to the SearchRun execution log (Singular to match back_populates)
    search_run: Mapped["SearchRun"] = relationship(
        "SearchRun",
        back_populates="notifications",
    )
