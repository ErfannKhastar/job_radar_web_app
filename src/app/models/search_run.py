"""
Automation Execution History Module.

This module defines the `SearchRun` entity, which acts as a detailed log
for every time the automation engine executes a scraping task. It tracks
successes, failures, and the volume of data extracted during that specific run.
"""

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String
from src.app.core.enums import SearchRunStatus
from src.app.db.session import Base

if TYPE_CHECKING:
    from src.app.models.search_profile import SearchProfile
    from src.app.models.notification import Notification


class SearchRun(Base):
    """
    A single execution instance of a user's search profile.

    Provides observability into the automation engine. If a scraper fails due
    to a network issue or UI change on the target platform, the error is recorded
    here for debugging and user transparency.
    """

    __tablename__ = "search_runs"

    # Unique identifier for the execution log
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key linking the run log to the profile that triggered it
    search_profile_id: Mapped[int] = mapped_column(
        ForeignKey(
            "search_profiles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Current state of the execution (e.g., RUNNING, SUCCESS, FAILED)
    status: Mapped[SearchRunStatus] = mapped_column(
        SqlEnum(SearchRunStatus),
        nullable=False,
        default=SearchRunStatus.RUNNING,
    )

    # Total number of jobs scraped during this execution
    jobs_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Number of jobs that were entirely new (not previously matched for this user)
    new_jobs_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Stores traceback or exception details if the scraper encounters an issue
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Timestamps defining the exact duration of the scraping task
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ==========================================
    # SQLAlchemy Relationships
    # ==========================================

    # Link back to the SearchProfile (Singular to match back_populates)
    search_profile: Mapped["SearchProfile"] = relationship(
        "SearchProfile",
        back_populates="search_runs",
    )

    # Link to the notifications that were generated as a result of this specific run
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="search_run",
        cascade="all, delete-orphan",
    )

    @property
    def duration_seconds(self) -> float | None:
        """
        Calculate the execution duration in seconds.

        Returns:
            float | None: Duration in seconds if the run has finished,
            otherwise None.
        """

        if self.finished_at is None:
            return None

        return (self.finished_at - self.started_at).total_seconds()
