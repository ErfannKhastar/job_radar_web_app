"""
Search Profile Module.

This module defines the `SearchProfile` entity, which acts as the core configuration
unit for the automation engine. Each profile represents a user's specific job search
criteria for a single source (e.g., "Python Developer in Tehran on Jobinja").
It stores complex, dynamic filtering parameters using PostgreSQL's JSONB capabilities.
"""

from datetime import datetime
from typing import Any
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.app.db.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.models.user import User
    from src.app.models.source import Source
    from src.app.models.job_match import JobMatch
    from src.app.models.search_run import SearchRun
    from src.app.models.schedule import Schedule


print("Loading SearchProfile model")
class SearchProfile(Base):
    """
    Represents a customized job search configuration created by a user.

    This model ties together a user, a specific job board (Source), and a set
    of dynamic filters (stored as JSON) to dictate exactly what kind of job
    ads the automation scraper should look for during its scheduled runs.
    """

    __tablename__ = "search_profiles"

    # Unique identifier for the search profile
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key linking the profile to its owner. 'ON DELETE CASCADE' ensures
    # that if a user is deleted, all their automation profiles are also removed.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Foreign key linking the profile to a specific target platform (e.g., Jobinja)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # A human-readable name assigned by the user to identify this search profile
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # JSONB column to flexibly store source-specific filtering criteria
    # (e.g., {"keyword": "FastAPI", "location": "Tehran", "remote_only": true}).
    # Using JSONB is optimal here because each job board may have completely different filter sets.
    filters: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    # Toggle to temporarily pause the automation for this specific profile without deleting it
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Audit timestamps for tracking profile creation and updates
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

    # Relationship to the User model (many-to-one)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="search_profiles",
    )

    # Relationship to the Source model (many-to-one)
    source: Mapped["Source"] = relationship(
        "Source",
        back_populates="search_profiles",
    )

    # Links this profile to all jobs successfully matched by the automation.
    # 'cascade="all, delete-orphan"' ensures match history is cleaned up if the profile is deleted.
    job_matches: Mapped[list["JobMatch"]] = relationship(
        "JobMatch",
        back_populates="search_profile",
        cascade="all, delete-orphan",
    )

    # Links this profile to the history of automation scraping runs (SearchRun)
    search_runs: Mapped[list["SearchRun"]] = relationship(
        "SearchRun",
        back_populates="search_profile",
        cascade="all, delete-orphan",
    )

    # Links this profile to its configured execution schedules (e.g., daily, weekly)
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule",
        back_populates="search_profile",
        cascade="all, delete-orphan",
    )
