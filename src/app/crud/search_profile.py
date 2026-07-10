"""
CRUD operations for the SearchProfile model.

This module provides reusable database operations for managing a user's
job search profiles. Business rules (permissions, duplicate validation,
ownership checks, etc.) intentionally belong to the Service layer.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.app.models.search_profile import SearchProfile
from src.app.schemas.search_profile import SearchProfileCreate, SearchProfileUpdate


def get_search_profile_by_id(
    db: Session,
    profile_id: int,
    user_id: int | None = None,
) -> SearchProfile | None:
    """
    Retrieve a search profile by its ID.

    Optionally restrict the lookup to a specific user. This is useful
    when a user should only be allowed to access their own profiles.

    Args:
        db: Active database session.
        profile_id: Search profile ID.
        user_id: Optional owner ID.

    Returns:
        SearchProfile | None
    """

    stmt = select(SearchProfile).where(SearchProfile.id == profile_id)

    if user_id is not None:
        stmt = stmt.where(SearchProfile.user_id == user_id)

    return db.scalar(stmt)


def get_search_profile_by_name(
    db: Session,
    user_id: int,
    name: str,
) -> SearchProfile | None:
    """
    Retrieve one search profile by its name for a specific user.

    Used by the Service layer to prevent duplicate profile names.

    Args:
        db: Active database session.
        user_id: Owner of the profile.
        name: Profile name.

    Returns:
        SearchProfile | None
    """

    stmt = select(SearchProfile).where(
        SearchProfile.user_id == user_id,
        SearchProfile.name == name,
    )

    return db.scalar(stmt)


def get_search_profiles_by_user(
    db: Session,
    user_id: int,
    active_only: bool = False,
) -> list[SearchProfile]:
    """
    Retrieve all search profiles belonging to a user.

    Args:
        db: Active database session.
        user_id: Owner of the profiles.
        active_only: If True, only active profiles are returned.

    Returns:
        List of SearchProfile objects.
    """

    stmt = select(SearchProfile).where(
        SearchProfile.user_id == user_id,
    )

    if active_only:
        stmt = stmt.where(SearchProfile.is_active.is_(True))

    stmt = stmt.order_by(
        SearchProfile.created_at.desc(),
        SearchProfile.id.desc(),
    )

    return list(db.scalars(stmt).all())


def get_search_profile_by_name_excluding_id(
    db: Session,
    user_id: int,
    name: str,
    profile_id: int,
) -> SearchProfile | None:
    """
    Retrieve a search profile by name while excluding a specific profile ID.

    Useful during update operations to detect duplicate names without
    matching the profile currently being edited.
    """

    stmt = select(SearchProfile).where(
        SearchProfile.user_id == user_id,
        SearchProfile.name == name,
        SearchProfile.id != profile_id,
    )

    return db.scalar(stmt)


def create_search_profile(
    db: Session,
    user_id: int,
    profile_data: SearchProfileCreate,
) -> SearchProfile:
    """
    Create a new search profile.

    Args:
        db: Active database session.
        user_id: Owner of the profile.
        profile_data: Validated input schema.

    Returns:
        Newly created SearchProfile object.
    """

    search_profile = SearchProfile(
        user_id=user_id,
        source_id=profile_data.source_id,
        name=profile_data.name,
        filters=profile_data.filters,
    )

    db.add(search_profile)
    db.flush()

    return search_profile


def update_search_profile(
    db: Session,
    profile: SearchProfile,
    profile_data: SearchProfileUpdate,
) -> SearchProfile:
    """
    Update a search profile.

    Only fields explicitly provided by the client will be modified.

    Args:
        db: Active database session.
        profile: Existing ORM object.
        profile_data: Validated update schema.

    Returns:
        Updated SearchProfile object.
    """

    update_data = profile_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.flush()

    return profile


def set_search_profile_active_status(
    db: Session,
    profile: SearchProfile,
    is_active: bool,
) -> SearchProfile:
    """
    Enable or disable a search profile.

    Args:
        db (Session): Active database session.
        profile (SearchProfile): Target profile.
        is_active (bool): Desired active state.

    Returns:
        SearchProfile: Updated profile.
    """
    profile.is_active = is_active
    db.flush()

    return profile


def delete_search_profile(
    db: Session,
    profile: SearchProfile,
) -> None:
    """
    Permanently delete a search profile.

    Related schedules and match history will also be removed due to
    cascade relationships defined in the ORM models.

    Args:
        db: Active database session.
        profile: Existing ORM object.
    """

    db.delete(profile)
    db.flush()
