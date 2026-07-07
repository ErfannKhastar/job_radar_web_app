"""
CRUD operations for the UserPreferences model.

This module manages the execution settings for specific users, such as
localization and notification channel preferences. These settings dictate
how the background automation workers deliver results to the user.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.app.models.user_preference import UserPreferences
from src.app.schemas.user_preference import UserPreferencesUpdate


def create_preferences(
    db: Session,
    user_id: int,
) -> UserPreferences:
    """
    Create a new default preferences record for a newly registered user.
    Usually triggered by an event or service right after account creation.

    Args:
        db (Session): The active database session.
        user_id (int): The ID of the user these settings belong to.

    Returns:
        UserPreferences: The newly created default preferences object.
    """
    preferences = UserPreferences(
        user_id=user_id,
    )

    db.add(preferences)
    db.flush()

    return preferences


def get_preferences_by_user_id(
    db: Session,
    user_id: int,
) -> UserPreferences | None:
    """
    Retrieve the automation preferences for a specific user.
    The background workers query this before dispatching any scraped job data.

    Args:
        db (Session): The active database session.
        user_id (int): The ID of the target user.

    Returns:
        UserPreferences | None: The preferences ORM object if found, otherwise None.
    """
    stmt = select(UserPreferences).where(UserPreferences.user_id == user_id)
    return db.scalar(stmt)


def update_preferences(
    db: Session,
    db_preferences: UserPreferences,
    preferences_update: UserPreferencesUpdate,
) -> UserPreferences:
    """
    Dynamically update a user's existing preferences payload.

    Args:
        db (Session): The active database session.
        db_preferences (UserPreferences): The existing preferences object to update.
        preferences_update (UserPreferencesUpdate): Validated schema containing specific fields to update.

    Returns:
        UserPreferences: The successfully updated preferences object.
    """
    update_data = preferences_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_preferences, key, value)

    db.flush()

    return db_preferences


def delete_preferences(db: Session, db_preferences: UserPreferences) -> None:
    """
    Permanently delete a user's preferences record.
    Typically handled automatically by SQLAlchemy's cascade delete,
    but provided here for manual administrative overrides.

    Args:
        db (Session): The active database session.
        db_preferences (UserPreferences): The preferences object to delete.
    """
    db.delete(db_preferences)
    db.flush()
