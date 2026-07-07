"""
Job Match Module.

This module acts as an association table (many-to-many relationship resolution)
between the `SearchProfile` and `Job` models. It answers the crucial question
in the automation process: "Which specific job ad was found for which user's profile?"
"""

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.app.db.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.models.search_profile import SearchProfile
    from src.app.models.job import Job


class JobMatch(Base):
    """
    Records a successful match between a scraped job posting and a user's search profile.

    This entity ensures that the same job is not repeatedly sent to the same user
    by tracking the history of matches. It utilizes a UniqueConstraint to maintain
    data integrity and prevent duplicate matching records.
    """

    __tablename__ = "job_matches"

    # Enforce uniqueness: A specific search profile can only match a specific job once.
    # This prevents the automation from spamming the user with duplicate notifications
    # if the scraper encounters the same job in subsequent runs.
    __table_args__ = (
        UniqueConstraint(
            "search_profile_id",
            "job_id",
            name="uq_search_profile_job",
        ),
    )

    # Unique identifier for the match record
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key referencing the automation profile that triggered this match
    search_profile_id: Mapped[int] = mapped_column(
        ForeignKey(
            "search_profiles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Foreign key referencing the actual scraped job data
    job_id: Mapped[int] = mapped_column(
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Timestamp indicating exactly when the automation engine detected this match
    matched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ==========================================
    # SQLAlchemy Relationships
    # ==========================================

    # Relationship back to the SearchProfile.
    # Note: Named singular ('search_profile') to correctly align with back_populates.
    search_profile: Mapped["SearchProfile"] = relationship(
        "SearchProfile",
        back_populates="job_matches",
    )

    # Relationship back to the extracted Job.
    # Note: Named singular ('job') to correctly align with back_populates.
    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="job_matches",
    )
