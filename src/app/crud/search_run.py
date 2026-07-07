"""
CRUD operations for the SearchRun model.

This module handles the execution logs for the job scraping automation tool.
It provides distinct state-transition functions (start, success, fail) that
background workers call to keep the database perfectly synced with their real-time status.
"""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.app.models.search_run import SearchRun
from src.app.core.enums import SearchRunStatus
from src.app.schemas.search_run import SearchRunCreate


def get_search_run_by_id(db: Session, run_id: int) -> SearchRun | None:
    """
    Retrieve a specific search run execution log by its primary key ID.

    Args:
        db (Session): The active database session.
        run_id (int): The ID of the search run log.

    Returns:
        SearchRun | None: The SearchRun ORM object if found, otherwise None.
    """
    stmt = select(SearchRun).where(SearchRun.id == run_id)
    return db.scalar(stmt)


def get_runs_by_profile(db: Session, search_profile_id: int) -> list[SearchRun]:
    """
    Retrieve all execution logs for a specific search profile.
    Allows users to see a history of when their job alerts were checked.

    Args:
        db (Session): The active database session.
        search_profile_id (int): The ID of the search profile.

    Returns:
        list[SearchRun]: A list of SearchRun objects, newest executions first.
    """
    stmt = (
        select(SearchRun)
        .where(SearchRun.search_profile_id == search_profile_id)
        .order_by(SearchRun.started_at.desc())
    )
    return list(db.scalars(stmt).all())


def start_search_run(db: Session, run_data: SearchRunCreate) -> SearchRun:
    """
    Initialize a new search run log at the exact moment the worker starts processing.
    The status is automatically locked to RUNNING.

    Args:
        db (Session): The active database session.
        run_data (SearchRunCreate): Validated schema containing the target profile ID.

    Returns:
        SearchRun: The initialized SearchRun object.
    """
    search_run = SearchRun(
        search_profile_id=run_data.search_profile_id,
        status=SearchRunStatus.RUNNING,
    )

    db.add(search_run)
    db.flush()

    return search_run


def finish_search_run_success(
    db: Session, search_run: SearchRun, jobs_found: int, new_jobs_found: int
) -> SearchRun:
    """
    Mark a running search task as successful and record the extraction metrics.

    Args:
        db (Session): The active database session.
        search_run (SearchRun): The currently active SearchRun object.
        jobs_found (int): Total raw jobs scraped from the job board.
        new_jobs_found (int): Number of newly inserted jobs that matched filters.

    Returns:
        SearchRun: The updated SearchRun object.
    """
    search_run.status = SearchRunStatus.SUCCESS
    search_run.jobs_found = jobs_found
    search_run.new_jobs_found = new_jobs_found
    search_run.finished_at = datetime.now(timezone.utc)

    db.flush()

    return search_run


def finish_search_run_failed(
    db: Session, search_run: SearchRun, error_message: str
) -> SearchRun:
    """
    Mark a search task as failed and log the exception details.
    Ensures that network timeouts or scraper crashes don't leave zombie tasks in the DB.

    Args:
        db (Session): The active database session.
        search_run (SearchRun): The currently active SearchRun object.
        error_message (str): The exception detail or failure reason.

    Returns:
        SearchRun: The updated SearchRun object.
    """
    search_run.status = SearchRunStatus.FAILED
    search_run.error_message = error_message
    search_run.finished_at = datetime.now(timezone.utc)

    db.flush()

    return search_run


def delete_search_run(db: Session, search_run: SearchRun) -> None:
    """
    Permanently delete a search run log from the database.

    Args:
        db (Session): The active database session.
        search_run (SearchRun): The SearchRun object to delete.
    """
    db.delete(search_run)
    db.flush()
