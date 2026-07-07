"""
CRUD operations for the SearchProfile model.

This module provides decoupled functions to manage user's job alerts
and dynamic search filters. It handles the core configurations that tell
the automation engine exactly what data to look for on specific platforms.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.app.models.search_profile import SearchProfile
from src.app.schemas.search_profile import SearchProfileCreate, SearchProfileUpdate


def get_search_profile_by_id(db: Session, profile_id: int) -> SearchProfile | None:
    """
    Retrieve a specific search profile by its primary key ID.

    Args:
        db (Session): The active database session.
        profile_id (int): The ID of the search profile.

    Returns:
        SearchProfile | None: The SearchProfile ORM object if found, otherwise None.
    """
    stmt = select(SearchProfile).where(SearchProfile.id == profile_id)
    return db.scalar(stmt)


def get_search_profiles_by_user(db: Session, user_id: int) -> list[SearchProfile]:
    """
    Retrieve all search profiles (active or inactive) created by a specific user.

    Args:
        db (Session): The active database session.
        user_id (int): The ID of the user who owns the profiles.

    Returns:
        list[SearchProfile]: A list of SearchProfile objects ordered by newest first.
    """
    stmt = (
        select(SearchProfile)
        .where(SearchProfile.user_id == user_id)
        .order_by(SearchProfile.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def create_search_profile(
    db: Session, user_id: int, profile_data: SearchProfileCreate
) -> SearchProfile:
    """
    Create a new dynamic search profile (job alert) for a specific user.

    Args:
        db (Session): The active database session.
        user_id (int): The ID of the user creating the profile.
        profile_data (SearchProfileCreate): Validated schema containing JSON filters.

    Returns:
        SearchProfile: The newly created SearchProfile object.
    """
    profile = SearchProfile(
        user_id=user_id,
        source_id=profile_data.source_id,
        name=profile_data.name,
        filters=profile_data.filters,
    )

    db.add(profile)
    db.flush()

    return profile


def update_search_profile(
    db: Session, profile: SearchProfile, profile_data: SearchProfileUpdate
) -> SearchProfile:
    """
    Dynamically update an existing search profile (e.g., changing keywords or name).

    Args:
        db (Session): The active database session.
        profile (SearchProfile): The existing SearchProfile object.
        profile_data (SearchProfileUpdate): Validated schema containing updated fields.

    Returns:
        SearchProfile: The updated SearchProfile object.
    """
    update_data = profile_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.flush()

    return profile


def activate_search_profile(db: Session, profile: SearchProfile) -> SearchProfile:
    """
    Enable a search profile.
    Signals the background task manager that this alert should be processed.

    Args:
        db (Session): The active database session.
        profile (SearchProfile): The SearchProfile object to activate.

    Returns:
        SearchProfile: The activated SearchProfile object.
    """
    profile.is_active = True
    db.flush()

    return profile


def deactivate_search_profile(db: Session, profile: SearchProfile) -> SearchProfile:
    """
    Disable a search profile.
    Temporarily pauses job searching for these specific criteria without deleting them.

    Args:
        db (Session): The active database session.
        profile (SearchProfile): The SearchProfile object to deactivate.

    Returns:
        SearchProfile: The deactivated SearchProfile object.
    """
    profile.is_active = False
    db.flush()

    return profile


def delete_search_profile(db: Session, profile: SearchProfile) -> None:
    """
    Permanently delete a search profile from the database.
    Due to cascade deletion, this will also clean up its schedules and match history.

    Args:
        db (Session): The active database session.
        profile (SearchProfile): The SearchProfile object to be deleted.
    """
    db.delete(profile)
    db.flush()
