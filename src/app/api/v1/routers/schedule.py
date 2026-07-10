"""
Schedule API routes.

Endpoints for managing automation schedules attached to a user's
SearchProfiles.
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from src.app.db.session import get_db
from src.app.api.dependencies import get_current_user
from src.app.models.user import User
from src.app.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
)
from src.app.services.schedule import schedule_service

router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"],
)


@router.post(
    "/",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create schedule",
)
def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new execution schedule.
    """

    return schedule_service.create(
        db=db,
        current_user=current_user,
        schedule_data=schedule_data,
    )


@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="Get schedule",
)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve one schedule.
    """

    return schedule_service.get_by_id(
        db=db,
        current_user=current_user,
        schedule_id=schedule_id,
    )


@router.get(
    "/profile/{search_profile_id}",
    response_model=list[ScheduleResponse],
    summary="List schedules",
)
def get_profile_schedules(
    search_profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all schedules for one SearchProfile.
    """

    return schedule_service.get_all(
        db=db,
        current_user=current_user,
        search_profile_id=search_profile_id,
    )


@router.patch(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="Update schedule",
)
def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing schedule.
    """

    return schedule_service.update(
        db=db,
        current_user=current_user,
        schedule_id=schedule_id,
        schedule_data=schedule_data,
    )


@router.patch(
    "/{schedule_id}/status",
    response_model=ScheduleResponse,
    summary="Enable or disable schedule",
)
def change_schedule_status(
    schedule_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Enable or disable a schedule.
    """

    return schedule_service.set_active_status(
        db=db,
        current_user=current_user,
        schedule_id=schedule_id,
        is_active=is_active,
    )


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete schedule",
)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a schedule.
    """

    schedule_service.delete(
        db=db,
        current_user=current_user,
        schedule_id=schedule_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
