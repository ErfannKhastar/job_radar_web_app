"""
Search Profile API endpoints.

Provides authenticated CRUD operations for managing a user's
job search profiles.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.app.api.dependencies import get_current_user
from src.app.db.session import get_db
from src.app.models.user import User
from src.app.schemas.search_profile import (
    SearchProfileUpdate,
    SearchProfileStatusUpdate,
)
from src.app.schemas.search_profile import (
    SearchProfileCreate,
    SearchProfileResponse,
)
from src.app.services.search_profile import search_profile_service

router = APIRouter(
    prefix="/search-profiles",
    tags=["Search Profiles"],
)


@router.post(
    "",
    response_model=SearchProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new search profile",
)
def create_search_profile(
    profile_data: SearchProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchProfileResponse:
    """
    Create a new search profile for the authenticated user.
    """

    return search_profile_service.create(
        db=db,
        current_user=current_user,
        profile_data=profile_data,
    )


@router.get(
    "",
    response_model=list[SearchProfileResponse],
    summary="List search profiles",
)
def get_search_profiles(
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SearchProfileResponse]:
    """
    Retrieve all search profiles belonging to the authenticated user.

    Optionally filter to only active profiles.
    """

    return search_profile_service.get_all(
        db=db,
        current_user=current_user,
        active_only=active_only,
    )


@router.get(
    "/{profile_id}",
    response_model=SearchProfileResponse,
    summary="Get a search profile",
)
def get_search_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchProfileResponse:
    """
    Retrieve one search profile owned by the authenticated user.
    """

    return search_profile_service.get_by_id(
        db=db,
        current_user=current_user,
        profile_id=profile_id,
    )


@router.patch(
    "/{profile_id}",
    response_model=SearchProfileResponse,
    summary="Update a search profile",
)
def update_search_profile(
    profile_id: int,
    profile_data: SearchProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchProfileResponse:
    """
    Update an existing search profile owned by the authenticated user.
    """

    return search_profile_service.update(
        db=db,
        current_user=current_user,
        profile_id=profile_id,
        profile_data=profile_data,
    )


@router.patch(
    "/{profile_id}/status",
    response_model=SearchProfileResponse,
    summary="Enable or disable a search profile",
)
def set_search_profile_status(
    profile_id: int,
    status_data: SearchProfileStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchProfileResponse:
    """
    Enable or disable a search profile.

    This endpoint only changes the activation status and does not
    modify any search criteria.
    """

    return search_profile_service.set_active_status(
        db=db,
        current_user=current_user,
        profile_id=profile_id,
        is_active=status_data.is_active,
    )


@router.delete(
    "/{profile_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a search profile",
)
def delete_search_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Permanently delete a search profile owned by the authenticated user.
    """

    search_profile_service.delete(
        db=db,
        current_user=current_user,
        profile_id=profile_id,
    )
