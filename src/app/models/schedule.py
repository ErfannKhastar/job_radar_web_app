"""
Automation Scheduling Module.

This module defines the `Schedule` entity, which dictates exactly when the
background tasks (workers) should execute a specific search profile.
It supports various scheduling strategies (run once, daily, weekly, or custom cron).
"""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.app.db.session import Base
from src.app.core.enums import ScheduleType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.models.search_profile import SearchProfile


class Schedule(Base):
    """
    Configuration for when a user's scraping task should be executed.

    The background task manager (e.g., APScheduler or Celery) constantly queries
    this table to find out which `SearchProfile` needs to be run next based on
    the defined time parameters.
    """

    __tablename__ = "schedules"

    # Unique identifier for the schedule record
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key linking the schedule to a specific automation profile
    search_profile_id: Mapped[int] = mapped_column(
        ForeignKey(
            "search_profiles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Defines the frequency pattern (e.g., ONCE, DAILY, WEEKLY)
    schedule_type: Mapped[ScheduleType] = mapped_column(
        SqlEnum(ScheduleType), nullable=False
    )

    # Toggle to temporarily disable a specific schedule without deleting it
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Standard time parameters for daily/weekly executions
    hour: Mapped[int | None] = mapped_column(Integer, nullable=True)
    minute: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weekday: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Exact execution time for tasks configured to run only once
    run_once_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Advanced scheduling pattern for highly customized execution intervals
    cron_expression: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Tracking fields used by the background worker to calculate the next execution cycle
    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
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

    # Links back to the targeted SearchProfile (Singular to match back_populates)
    search_profile: Mapped["SearchProfile"] = relationship(
        "SearchProfile",
        back_populates="schedules",
    )
