"""
User Authentication and Identity Module.

This module defines the `User` entity, which is the root of the automation tool.
It handles core credentials and acts as the central hub for all relational data
associated with a user, ensuring that if an account is disabled or deleted,
all their related scraping tasks and preferences are handled gracefully.
"""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.app.db.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.models.search_profile import SearchProfile
    from src.app.models.user_preference import UserPreferences


print("Loading User model")
class User(Base):
    """
    Represents a registered account in the job scraping automation system.

    This model maintains basic authentication details (username, email, password)
    and establishes the primary 'one-to-many' relationships to the user's customized
    automation profiles and settings.
    """

    __tablename__ = "users"

    # Unique identifier for the user account
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Unique username used for login or display purposes
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    # Unique email address used for communication, login, and email notifications
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    # Securely hashed password (managed by pwdlib)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # Global toggle to suspend a user. If set to False, all their background
    # scraping schedules and API access should be strictly blocked.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Determines if the user has administrative rights over the entire automation platform
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

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

    # Tracks the most recent successful login
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ==========================================
    # SQLAlchemy Relationships
    # ==========================================

    # Links the user to all their configured scraping tasks.
    # 'cascade="all, delete-orphan"' ensures that deleting a user completely
    # cleans up their automation footprint (no ghost tasks running in the background).
    search_profiles: Mapped[list["SearchProfile"]] = relationship(
        "SearchProfile",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Links the user to their specific output and localization settings.
    # Also uses cascade delete to maintain database integrity.
    preferences: Mapped["UserPreferences"] = relationship(
        "UserPreferences",
        back_populates="user",
        cascade="all, delete-orphan",
    )
