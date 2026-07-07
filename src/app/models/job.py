"""
Extracted Job Posting Module.

This module defines the `Job` entity, which serves as the central repository
for all job advertisements collected by the scraping automation. It is designed
to store both standardized fields common to all job boards and platform-specific
metadata flexibly.
"""

from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.app.db.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.models.source import Source
    from src.app.models.job_match import JobMatch


class Job(Base):
    """
    A single job advertisement extracted by the automation system.

    This model normalizes the core job data (title, company, url) across different
    job boards, while preserving any unique, unstructured data provided by specific
    sources within a JSONB column.
    """

    __tablename__ = "jobs"

    # Unique identifier for the scraped job
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key identifying which platform this job was scraped from
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Standardized core fields extracted from the advertisement
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # The direct URL to the job posting. Marked as unique to prevent the scraper
    # from storing duplicate records if it encounters the same ad multiple times.
    url: Mapped[str] = mapped_column(
        String(1000), unique=True, nullable=False, index=True
    )

    # Flexible storage for unstructured or source-specific data
    # (e.g., {"salary_range": "10-15M", "tags": ["Python", "Django"], "is_remote": True}).
    # Crucial for maintaining a single `jobs` table for all varying platforms.
    extra_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )

    # Timestamp indicating exactly when the automation engine extracted this record
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
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

    # Relationship back to the Source platform (many-to-one)
    source: Mapped["Source"] = relationship(
        "Source",
        back_populates="jobs",
    )

    # Links this specific job to all user profiles that matched its criteria.
    # Named singular ('job') to accurately align with the JobMatch model's relationship.
    job_matches: Mapped[list["JobMatch"]] = relationship(
        "JobMatch",
        back_populates="job",
        cascade="all, delete-orphan",
    )
