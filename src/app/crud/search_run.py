"""
CRUD operations for the SearchRun model.

This module handles the execution logs for the job scraping automation tool.
It provides database operations for creating, tracking, updating and
retrieving scraping execution history.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.app.models.search_run import SearchRun
from src.app.schemas.search_run import SearchRunCreate
from datetime import datetime, timezone
from src.app.core.enums import SearchRunStatus


def get_search_run_by_id(
    db: Session,
    run_id: int,
    search_profile_id: int | None = None,
) -> SearchRun | None:
    """
    Retrieve a search run by its ID.

    Optionally restrict lookup to a specific SearchProfile.

    Args:
        db: Active database session.
        run_id: SearchRun ID.
        search_profile_id: Optional related SearchProfile ID.

    Returns:
        SearchRun | None
    """

    stmt = select(SearchRun).where(SearchRun.id == run_id)

    if search_profile_id is not None:
        stmt = stmt.where(SearchRun.search_profile_id == search_profile_id)

    return db.scalar(stmt)


def get_runs_by_profile(
    db: Session,
    search_profile_id: int,
) -> list[SearchRun]:
    """
    Retrieve execution history for a SearchProfile.

    Args:
        db: Active database session.
        search_profile_id: Target SearchProfile ID.

    Returns:
        List of SearchRun objects ordered by newest first.
    """

    stmt = (
        select(SearchRun)
        .where(SearchRun.search_profile_id == search_profile_id)
        .order_by(
            SearchRun.started_at.desc(),
            SearchRun.id.desc(),
        )
    )

    return list(db.scalars(stmt).all())


def start_search_run(
    db: Session,
    run_data: SearchRunCreate,
) -> SearchRun:
    """
    Create a new SearchRun and mark it as RUNNING.

    This function is called when the worker starts processing
    a SearchProfile.

    Args:
        db: Active database session.
        run_data: Validated creation schema.

    Returns:
        Newly created SearchRun object.
    """

    search_run = SearchRun(
        search_profile_id=run_data.search_profile_id,
        status=SearchRunStatus.RUNNING,
    )

    db.add(search_run)
    db.flush()

    return search_run


def finish_search_run_success(
    db: Session,
    search_run: SearchRun,
    jobs_found: int,
    new_jobs_found: int,
) -> SearchRun:
    """
    Mark a SearchRun as SUCCESS.

    Args:
        db: Active database session.
        search_run: Existing SearchRun ORM object.
        jobs_found: Total scraped jobs.
        new_jobs_found: Newly matched jobs.

    Returns:
        Updated SearchRun object.
    """

    search_run.status = SearchRunStatus.SUCCESS
    search_run.jobs_found = jobs_found
    search_run.new_jobs_found = new_jobs_found
    search_run.finished_at = datetime.now(timezone.utc)

    db.flush()

    return search_run


def finish_search_run_failed(
    db: Session,
    search_run: SearchRun,
    error_message: str,
) -> SearchRun:
    """
    Mark a SearchRun as FAILED.

    Args:
        db: Active database session.
        search_run: Existing SearchRun ORM object.
        error_message: Failure reason or traceback.

    Returns:
        Updated SearchRun object.
    """

    search_run.status = SearchRunStatus.FAILED
    search_run.error_message = error_message
    search_run.finished_at = datetime.now(timezone.utc)

    db.flush()

    return search_run


def delete_search_run(
    db: Session,
    search_run: SearchRun,
) -> None:
    """
    Permanently delete a SearchRun.

    Args:
        db: Active database session.
        search_run: Existing SearchRun ORM object.
    """

    db.delete(search_run)
    db.flush()
