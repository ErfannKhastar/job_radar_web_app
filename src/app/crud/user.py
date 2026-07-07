"""
CRUD operations for the User model.

This module contains reusable, decoupled functions to interact with the 'users' table.
It leverages modern SQLAlchemy 2.0 syntax (select, scalar) and relies on db.flush()
to keep transactions manageable at the API/Service layer (Unit of Work pattern).
"""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.app.models.user import User
from src.app.schemas.user import UserCreate, UserUpdate


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Retrieve a user by their unique primary key ID.

    Args:
        db (Session): The active database session.
        user_id (int): The ID of the user to retrieve.

    Returns:
        User | None: The User ORM object if found, otherwise None.
    """
    stmt = select(User).where(User.id == user_id)
    return db.scalar(stmt)


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieve a user by their registered email address.
    Typically used during the login and authentication process.

    Args:
        db (Session): The active database session.
        email (str): The email address to search for.

    Returns:
        User | None: The User ORM object if found, otherwise None.
    """
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)


def get_user_by_username(db: Session, username: str) -> User | None:
    """
    Retrieve a user by their unique username.
    Used for registration checks to prevent duplicate usernames.

    Args:
        db (Session): The active database session.
        username (str): The username to search for.

    Returns:
        User | None: The User ORM object if found, otherwise None.
    """
    stmt = select(User).where(User.username == username)
    return db.scalar(stmt)


def create_user(
    db: Session,
    user_data: UserCreate,
    hashed_password: str,
) -> User:
    """
    Create a new user and safely stage it in the database session.

    Args:
        db (Session): The active database session.
        user_data (UserCreate): The validated schema containing new user data.
        hashed_password (str): The cryptographically hashed password.

    Returns:
        User: The newly created User object (flushed, so it has an ID assigned).
    """
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    db.flush()  # Flushes pending changes to the DB to get the generated ID without committing

    return new_user


def update_user(db: Session, user: User, user_data: UserUpdate) -> User:
    """
    Dynamically update a user's details, modifying only the fields provided.

    Args:
        db (Session): The active database session.
        user (User): The existing User ORM object to update.
        user_data (UserUpdate): The schema containing the specific fields to update.

    Returns:
        User: The updated User object.
    """
    # exclude_unset=True ensures we only touch fields the client actually sent
    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.flush()

    return user


def update_password(db: Session, user: User, hashed_password: str) -> User:
    """
    Replace the user's password hash.

    This function assumes the password has already been validated
    and hashed by the Service layer.

    Args:
        db (Session): The active database session.
        user (User): The User ORM object to update.
        hashed_password (str): The new hashed password.

    Returns:
        User: The updated User object.
    """

    user.hashed_password = hashed_password
    db.flush()

    return user


def update_last_login(db: Session, user: User) -> None:
    """
    Update the 'last_login' timestamp for a user.
    Enforces timezone-aware UTC datetime for consistent time tracking.

    Args:
        db (Session): The active database session.
        user (User): The User object to update.
    """
    user.last_login = datetime.now(timezone.utc)
    db.flush()


def deactivate_user(db: Session, user: User) -> User:
    """
    Deactivate a user account (soft delete).
    This status acts as a kill-switch for all their automation profiles.

    Args:
        db (Session): The active database session.
        user (User): The User object to deactivate.

    Returns:
        User: The deactivated User object.
    """
    user.is_active = False
    db.flush()

    return user


def activate_user(db: Session, user: User) -> User:
    """
    Reactivate a previously suspended user account.

    Args:
        db (Session): The active database session.
        user (User): The User object to activate.

    Returns:
        User: The activated User object.
    """
    user.is_active = True
    db.flush()

    return user
