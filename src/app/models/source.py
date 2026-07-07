"""
Source Platform Configuration Module.

This module defines the `Source` entity, representing the target job board websites
(e.g., Jobinja, Jobvision, Remote OK) that the automation engine is configured to scrape.
By keeping sources in the database rather than hardcoding them, the system remains
highly extensible and easy to manage.
"""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.app.db.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.models.search_profile import SearchProfile
    from src.app.models.job import Job


print("Loading Source model")
class Source(Base):
    """
    Represents a target platform from which job postings are extracted.

    This model acts as a registry for all supported scraping targets. It allows
    administrators to globally disable scraping for a specific site (e.g., if the
    site changes its UI and breaks the scraper) without altering the codebase.
    """

    __tablename__ = "sources"

    # Unique identifier for the source platform
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Human-readable name of the platform (e.g., "Jobinja")
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # URL-friendly identifier used in API endpoints or CLI commands (e.g., "jobinja")
    slug: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    # The root URL of the target platform used as a base for building scraping requests
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)

    # Global kill switch: If set to False, all automation profiles tied to this
    # source will be temporarily bypassed until the scraper logic is fixed or updated.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ==========================================
    # SQLAlchemy Relationships
    # ==========================================

    # Links the source to all user search profiles that target this platform
    search_profiles: Mapped[list["SearchProfile"]] = relationship(
        "SearchProfile",
        back_populates="source",
    )

    # Links the source to all the specific job postings extracted from it
    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="source",
    )
