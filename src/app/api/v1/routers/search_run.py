"""
SearchRun API endpoints.

Provides endpoints for viewing the execution history of SearchProfiles.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.app.db.session import get_db
from src.app.models.user import User
from src.app.schemas.search_run import SearchRunResponse
from src.app.services.search_run import search_run_service
from src.app.api.dependencies import get_current_user


router = APIRouter(
    prefix="/search-runs",
    tags=["Search Runs"],
)


@router.get(
    "/{run_id}",
    response_model=SearchRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Get SearchRun by ID",
)
def get_search_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve one SearchRun owned by the authenticated user.
    """

    return search_run_service.get_by_id(
        db=db,
        current_user=current_user,
        run_id=run_id,
    )


@router.get(
    "/profile/{search_profile_id}",
    response_model=list[SearchRunResponse],
    status_code=status.HTTP_200_OK,
    summary="List SearchRuns for a SearchProfile",
)
def get_search_runs(
    search_profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve execution history for one SearchProfile.
    """

    return search_run_service.get_all(
        db=db,
        current_user=current_user,
        search_profile_id=search_profile_id,
    )


@router.delete(
    "/{run_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete SearchRun",
)
def delete_search_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Permanently delete a SearchRun owned by the authenticated user.
    """

    search_run_service.delete(
        db=db,
        current_user=current_user,
        run_id=run_id,
    )