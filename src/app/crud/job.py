"""
CRUD operations for the Job model.

This module handles database interactions for the core payload of the automation
system: the scraped job postings. It provides functions to safely insert new
ads, update existing ones, and prevent the ingestion of duplicate records.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.app.models.job import Job
from src.app.schemas.job import JobCreate, JobUpdate


def get_job_by_id(db: Session, job_id: int) -> Job | None:
    """
    Retrieve a specific job posting by its primary key ID.

    Args:
        db (Session): The active database session.
        job_id (int): The ID of the job.

    Returns:
        Job | None: The Job ORM object if found, otherwise None.
    """
    stmt = select(Job).where(Job.id == job_id)
    return db.scalar(stmt)


def get_job_by_url(db: Session, url: str) -> Job | None:
    """
    Retrieve a job posting by its unique URL.
    CRITICAL: Used extensively by the scraping workers to check if a newly
    found advertisement has already been ingested in a previous run,
    thereby enforcing data uniqueness.

    Args:
        db (Session): The active database session.
        url (str): The unique URL of the job posting.

    Returns:
        Job | None: The Job ORM object if found, otherwise None.
    """
    stmt = select(Job).where(Job.url == url)
    return db.scalar(stmt)


def get_jobs_by_source(db: Session, source_id: int) -> list[Job]:
    """
    Retrieve all jobs scraped from a specific job board platform.

    Args:
        db (Session): The active database session.
        source_id (int): The ID of the target source.

    Returns:
        list[Job]: A list of Job objects, ordered by scrape time (newest first).
    """
    stmt = select(Job).where(Job.source_id == source_id).order_by(Job.scraped_at.desc())
    return list(db.scalars(stmt).all())


def create_job(db: Session, job_data: JobCreate) -> Job:
    """
    Insert a newly scraped job advertisement into the database.

    Args:
        db (Session): The active database session.
        job_data (JobCreate): Validated schema containing standard and extra job details.

    Returns:
        Job: The newly created Job object.
    """
    job = Job(
        source_id=job_data.source_id,
        title=job_data.title,
        company=job_data.company,
        location=job_data.location,
        # Convert Pydantic HttpUrl strictly to string for PostgreSQL text compatibility
        url=str(job_data.url),
        extra_data=job_data.extra_data,
    )

    db.add(job)
    db.flush()

    return job


def update_job(db: Session, job: Job, job_data: JobUpdate) -> Job:
    """
    Dynamically update an existing job record.
    Useful if the automation engine detects that an employer has modified
    the title, location, or metadata of an existing advertisement.

    Args:
        db (Session): The active database session.
        job (Job): The existing Job ORM object to update.
        job_data (JobUpdate): Validated schema containing specific fields to update.

    Returns:
        Job: The updated Job object.
    """
    update_data = job_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(job, field, value)

    db.flush()

    return job


def delete_job(db: Session, job: Job) -> None:
    """
    Permanently delete a job posting from the database.

    Args:
        db (Session): The active database session.
        job (Job): The Job object to delete.
    """
    db.delete(job)
    db.flush()
