"""
CRUD operations for the Schedule model.

This module handles the database interactions for the automation timing rules.
It allows the background task manager to accurately create, update, and track
the execution cycles for each user's search profile.
"""

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.app.models.schedule import Schedule
from src.app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from src.app.core.enums import ScheduleType


def create_schedule(
    db: Session,
    schedule_data: ScheduleCreate,
    cron_expression: str | None = None,
) -> Schedule:
    """
    Create a new automation execution schedule for a search profile.

    Args:
        db (Session): The active database session.
        schedule_data (ScheduleCreate): Validated schema containing timing rules.
        cron_expression (str | None): Optional advanced cron string for complex intervals.

    Returns:
        Schedule: The newly created Schedule ORM object.
    """
    schedule = Schedule(
        search_profile_id=schedule_data.search_profile_id,
        schedule_type=schedule_data.schedule_type,
        hour=schedule_data.hour,
        minute=schedule_data.minute,
        weekday=schedule_data.weekday,
        run_once_at=schedule_data.run_once_at,
        cron_expression=cron_expression,
    )

    db.add(schedule)
    db.flush()

    return schedule


def get_schedule_by_id(
    db: Session,
    schedule_id: int,
    search_profile_id: int | None = None,
) -> Schedule | None:
    """
    Retrieve a schedule by its ID.

    Optionally restrict the lookup to a specific SearchProfile.

    Args:
        db: Active database session.
        schedule_id: Schedule ID.
        search_profile_id: Optional SearchProfile owner.

    Returns:
        Schedule | None
    """
    stmt = select(Schedule).where(Schedule.id == schedule_id)

    if search_profile_id is not None:
        stmt = stmt.where(Schedule.search_profile_id == search_profile_id)

    return db.scalar(stmt)


def get_schedules_by_profile(db: Session, search_profile_id: int) -> list[Schedule]:
    """
    Retrieve all execution schedules associated with a specific search profile.

    Args:
        db (Session): The active database session.
        search_profile_id (int): The ID of the targeted search profile.

    Returns:
        list[Schedule]: A list of Schedule objects ordered by newest first.
    """
    stmt = (
        select(Schedule)
        .where(Schedule.search_profile_id == search_profile_id)
        .order_by(
            Schedule.created_at.desc(),
            Schedule.id.desc(),
        )
    )

    return list(db.scalars(stmt).all())


def get_duplicate_schedule(
    db: Session,
    search_profile_id: int,
    schedule_type: ScheduleType,
    hour: int | None,
    minute: int | None,
    weekday: int | None,
    run_once_at: datetime | None,
) -> Schedule | None:
    """
    Check whether an identical schedule already exists
    for the given SearchProfile.
    """

    stmt = select(Schedule).where(
        Schedule.search_profile_id == search_profile_id,
        Schedule.schedule_type == schedule_type,
        Schedule.hour == hour,
        Schedule.minute == minute,
        Schedule.weekday == weekday,
        Schedule.run_once_at == run_once_at,
    )

    return db.scalar(stmt)


def update_schedule(
    db: Session,
    schedule: Schedule,
    schedule_data: ScheduleUpdate,
    cron_expression: str | None = None,
) -> Schedule:
    """
    Dynamically update an existing schedule's timing configurations.

    Args:
        db (Session): The active database session.
        schedule (Schedule): The existing Schedule ORM object to update.
        schedule_data (ScheduleUpdate): Validated schema with updated fields.
        cron_expression (str | None): Optional updated cron string.

    Returns:
        Schedule: The successfully updated Schedule object.
    """
    update_data = schedule_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(schedule, key, value)

    if cron_expression is not None:
        schedule.cron_expression = cron_expression

    db.flush()

    return schedule


def update_last_run(
    db: Session,
    schedule: Schedule,
    last_run_at: datetime,
    next_run_at: datetime | None,
) -> Schedule:
    """
    Update the tracking timestamps after a successful automation execution.
    CRITICAL: This function allows the background scheduler to accurately
    calculate and wait for the next execution cycle without overlapping tasks.

    Args:
        db (Session): The active database session.
        schedule (Schedule): The active Schedule object.
        last_run_at (datetime): The precise timestamp of the completed run.
        next_run_at (datetime | None): The calculated timestamp for the next run.

    Returns:
        Schedule: The updated Schedule object.
    """
    schedule.last_run_at = last_run_at
    schedule.next_run_at = next_run_at

    db.flush()

    return schedule


def set_schedule_status(db: Session, schedule: Schedule, is_active: bool) -> Schedule:
    """
    Quickly enable or disable a schedule without altering its timing logic.

    Args:
        db (Session): The active database session.
        schedule (Schedule): The Schedule object to toggle.
        is_active (bool): True to enable, False to disable.

    Returns:
        Schedule: The updated Schedule object.
    """
    schedule.is_active = is_active

    db.flush()
    return schedule


def delete_schedule(db: Session, schedule: Schedule) -> None:
    """
    Permanently delete a schedule from the database.

    Args:
        db (Session): The active database session.
        schedule (Schedule): The Schedule object to delete.
    """
    db.delete(schedule)
    db.flush()
