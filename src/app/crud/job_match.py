"""
CRUD operations for the JobMatch model.

This module provides functions to record, verify, and retrieve the associations
between scraped jobs and user search profiles. It is highly critical for the
automation engine to ensure it does not send duplicate job alerts to a user.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.app.models.job_match import JobMatch
from src.app.schemas.job_match import JobMatchCreate


def get_job_match_by_id(db: Session, match_id: int) -> JobMatch | None:
    """
    Retrieve a specific job match record by its primary key ID.

    Args:
        db (Session): The active database session.
        match_id (int): The ID of the job match.

    Returns:
        JobMatch | None: The JobMatch ORM object if found, otherwise None.
    """
    stmt = select(JobMatch).where(JobMatch.id == match_id)
    return db.scalar(stmt)


def match_exists(db: Session, search_profile_id: int, job_id: int) -> bool:
    """
    Check if a specific job has already been matched to a specific search profile.
    CRITICAL: The background worker calls this before dispatching any notification
    to guarantee that a user never receives the same job ad twice.

    Args:
        db (Session): The active database session.
        search_profile_id (int): The ID of the target search profile.
        job_id (int): The ID of the job posting.

    Returns:
        bool: True if the match already exists in the database, False otherwise.
    """
    stmt = select(JobMatch).where(
        JobMatch.search_profile_id == search_profile_id,
        JobMatch.job_id == job_id,
    )
    # Using is not None is a fast way to check existence without fetching full rows
    return db.scalar(stmt) is not None


def get_matches_by_profile(db: Session, search_profile_id: int) -> list[JobMatch]:
    """
    Retrieve all job matches associated with a specific search profile.

    Args:
        db (Session): The active database session.
        search_profile_id (int): The ID of the search profile.

    Returns:
        list[JobMatch]: A list of JobMatch objects ordered by newest first.
    """
    stmt = (
        select(JobMatch)
        .where(JobMatch.search_profile_id == search_profile_id)
        .order_by(JobMatch.matched_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_matches_by_job(db: Session, job_id: int) -> list[JobMatch]:
    """
    Retrieve all profiles that a specific job has been matched with.
    Useful for system analytics to see how many users were interested in a specific ad.

    Args:
        db (Session): The active database session.
        job_id (int): The ID of the job.

    Returns:
        list[JobMatch]: A list of JobMatch objects.
    """
    stmt = (
        select(JobMatch)
        .where(JobMatch.job_id == job_id)
        .order_by(JobMatch.matched_at.desc())
    )
    return list(db.scalars(stmt).all())


def create_job_match(db: Session, match_data: JobMatchCreate) -> JobMatch:
    """
    Record a new successful match between a job and a search profile.

    Args:
        db (Session): The active database session.
        match_data (JobMatchCreate): Validated schema containing IDs for the association.

    Returns:
        JobMatch: The newly created JobMatch object.
    """
    job_match = JobMatch(
        search_profile_id=match_data.search_profile_id,
        job_id=match_data.job_id,
    )

    db.add(job_match)
    db.flush()

    return job_match


def delete_job_match(db: Session, job_match: JobMatch) -> None:
    """
    Permanently delete a job match record.

    Args:
        db (Session): The active database session.
        job_match (JobMatch): The JobMatch object to delete.
    """
    db.delete(job_match)
    db.flush()
