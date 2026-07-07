"""
CRUD operations for the Source model.

This module provides reusable, decoupled functions to interact with the 'sources' table.
It handles the creation, retrieval, updating, and global status management (kill-switches)
for the job board platforms targeted by the automation engine.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.app.models.source import Source
from src.app.schemas.source import SourceCreate, SourceUpdate


def get_source_by_id(db: Session, source_id: int) -> Source | None:
    """
    Retrieve a specific job board source by its primary key ID.

    Args:
        db (Session): The active database session.
        source_id (int): The ID of the source.

    Returns:
        Source | None: The Source ORM object if found, otherwise None.
    """
    stmt = select(Source).where(Source.id == source_id)
    return db.scalar(stmt)


def get_source_by_slug(db: Session, slug: str) -> Source | None:
    """
    Retrieve a job board source by its unique URL-friendly slug.
    Highly useful for dynamic URL routing in the API (e.g., /api/jobs/{slug}).

    Args:
        db (Session): The active database session.
        slug (str): The URL-friendly identifier string.

    Returns:
        Source | None: The Source ORM object if found, otherwise None.
    """
    stmt = select(Source).where(Source.slug == slug)
    return db.scalar(stmt)


def get_all_sources(db: Session) -> list[Source]:
    """
    Retrieve all job board sources from the database, regardless of status.
    Typically used for admin dashboards or configuration UIs.

    Args:
        db (Session): The active database session.

    Returns:
        list[Source]: A list of all Source objects, strictly ordered by ID.
    """
    stmt = select(Source).order_by(Source.id)
    return list(db.scalars(stmt).all())


def get_active_sources(db: Session) -> list[Source]:
    """
    Retrieve ONLY the active job board sources.
    CRITICAL: This function is used by the background scheduler to determine
    which target scrapers should be actively executed.

    Args:
        db (Session): The active database session.

    Returns:
        list[Source]: A list of enabled Source objects.
    """
    stmt = select(Source).where(Source.is_active.is_(True))
    return list(db.scalars(stmt).all())


def create_source(db: Session, source_data: SourceCreate) -> Source:
    """
    Register a new job board platform target into the database.

    Args:
        db (Session): The active database session.
        source_data (SourceCreate): The validated schema for the new source.

    Returns:
        Source: The newly created and flushed Source object.
    """
    source = Source(
        name=source_data.name,
        slug=source_data.slug,
        base_url=source_data.base_url,
    )

    db.add(source)
    db.flush()

    return source


def update_source(db: Session, source: Source, source_data: SourceUpdate) -> Source:
    """
    Dynamically update an existing source's configurations.

    Args:
        db (Session): The active database session.
        source (Source): The existing Source ORM object.
        source_data (SourceUpdate): Validated schema containing updated fields.

    Returns:
        Source: The successfully updated Source object.
    """
    # Exclude unset fields to prevent overwriting existing data with None
    update_data = source_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(source, field, value)

    db.flush()

    return source


def activate_source(db: Session, source: Source) -> Source:
    """
    Enable a previously deactivated source.
    Signals the background workers to resume scraping this platform.

    Args:
        db (Session): The active database session.
        source (Source): The Source object to activate.

    Returns:
        Source: The activated Source object.
    """
    source.is_active = True
    db.flush()

    return source


def deactivate_source(db: Session, source: Source) -> Source:
    """
    Disable a source globally.
    Acts as an administrative kill-switch if a specific job board changes
    its HTML layout and causes the scraper to crash continuously.

    Args:
        db (Session): The active database session.
        source (Source): The Source object to deactivate.

    Returns:
        Source: The deactivated Source object.
    """
    source.is_active = False
    db.flush()

    return source
