"""
SearchRun service.

Contains the business logic for managing execution history
of SearchProfiles.

Responsibilities:
- Verify ownership.
- Start execution logs.
- Finish successful runs.
- Finish failed runs.
- Retrieve execution history.
- Delete execution history.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.app.models.user import User
from src.app.models.search_run import SearchRun
from src.app.schemas.search_run import SearchRunCreate, SearchRunResponse
from src.app.crud.search_run import (
    get_search_run_by_id,
    get_runs_by_profile,
    start_search_run,
    finish_search_run_success,
    finish_search_run_failed,
    delete_search_run,
)
from src.app.crud.search_profile import get_search_profile_by_id
from src.app.exceptions.search_run import SearchRunNotFoundException
from src.app.exceptions.search_profile import SearchProfileNotFoundException
from src.app.services.base import BaseService


class SearchRunService(BaseService):
    """
    Business logic for SearchRun.
    """

    # ---------------------------------------------------------
    # Private Helpers
    # ---------------------------------------------------------

    def _get_owned_profile(
        self,
        db: Session,
        profile_id: int,
        current_user: User,
    ):
        """
        Retrieve a SearchProfile owned by the current user.
        """

        profile = get_search_profile_by_id(
            db=db,
            profile_id=profile_id,
            user_id=current_user.id,
        )

        if profile is None:
            raise SearchProfileNotFoundException()

        return profile

    def _get_owned_search_run(
        self,
        db: Session,
        run_id: int,
        current_user: User,
    ) -> SearchRun:
        """
        Retrieve a SearchRun only if it belongs to one of
        the current user's SearchProfiles.
        """

        search_run = get_search_run_by_id(
            db=db,
            run_id=run_id,
        )

        if search_run is None:
            raise SearchRunNotFoundException()

        self._get_owned_profile(
            db=db,
            profile_id=search_run.search_profile_id,
            current_user=current_user,
        )

        return search_run

    # ---------------------------------------------------------
    # Read Operations
    # ---------------------------------------------------------

    def get_by_id(
        self,
        db: Session,
        current_user: User,
        run_id: int,
    ) -> SearchRunResponse:
        """
        Retrieve a single SearchRun owned by the current user.

        Args:
            db: Active database session.
            current_user: Authenticated user.
            run_id: Target SearchRun ID.

        Returns:
            SearchRunResponse
        """

        search_run = self._get_owned_search_run(
            db=db,
            run_id=run_id,
            current_user=current_user,
        )

        return SearchRunResponse.model_validate(search_run)

    def get_all(
        self,
        db: Session,
        current_user: User,
        search_profile_id: int,
    ) -> list[SearchRunResponse]:
        """
        Retrieve all SearchRuns belonging to one SearchProfile.

        Args:
            db: Active database session.
            current_user: Authenticated user.
            search_profile_id: Target SearchProfile ID.

        Returns:
            List[SearchRunResponse]
        """

        self._get_owned_profile(
            db=db,
            profile_id=search_profile_id,
            current_user=current_user,
        )

        search_runs = get_runs_by_profile(
            db=db,
            search_profile_id=search_profile_id,
        )

        return [
            SearchRunResponse.model_validate(search_run) for search_run in search_runs
        ]

    # ---------------------------------------------------------
    # Execution Operations
    # ---------------------------------------------------------

    def start(
        self,
        db: Session,
        current_user: User,
        run_data: SearchRunCreate,
    ) -> SearchRunResponse:
        """
        Start a new SearchRun for one of the user's SearchProfiles.
        """

        self._get_owned_profile(
            db=db,
            profile_id=run_data.search_profile_id,
            current_user=current_user,
        )

        try:
            search_run = start_search_run(
                db=db,
                run_data=run_data,
            )

            self.commit(db, search_run)

            return SearchRunResponse.model_validate(search_run)

        except SQLAlchemyError:
            db.rollback()
            raise

    def finish_success(
        self,
        db: Session,
        current_user: User,
        run_id: int,
        jobs_found: int,
        new_jobs_found: int,
    ) -> SearchRunResponse:
        """
        Mark a SearchRun as successfully completed.
        """

        search_run = self._get_owned_search_run(
            db=db,
            run_id=run_id,
            current_user=current_user,
        )

        try:
            finish_search_run_success(
                db=db,
                search_run=search_run,
                jobs_found=jobs_found,
                new_jobs_found=new_jobs_found,
            )

            self.commit(db, search_run)

            return SearchRunResponse.model_validate(search_run)

        except SQLAlchemyError:
            db.rollback()
            raise

    def finish_failed(
        self,
        db: Session,
        current_user: User,
        run_id: int,
        error_message: str,
    ) -> SearchRunResponse:
        """
        Mark a SearchRun as failed.
        """

        search_run = self._get_owned_search_run(
            db=db,
            run_id=run_id,
            current_user=current_user,
        )

        try:
            finish_search_run_failed(
                db=db,
                search_run=search_run,
                error_message=error_message,
            )

            self.commit(db, search_run)

            return SearchRunResponse.model_validate(search_run)

        except SQLAlchemyError:
            db.rollback()
            raise

    # ---------------------------------------------------------
    # Delete Operations
    # ---------------------------------------------------------

    def delete(
        self,
        db: Session,
        current_user: User,
        run_id: int,
    ) -> None:
        """
        Permanently delete a SearchRun.

        Args:
            db: Active database session.
            current_user: Authenticated user.
            run_id: Target SearchRun ID.
        """

        search_run = self._get_owned_search_run(
            db=db,
            run_id=run_id,
            current_user=current_user,
        )

        try:
            delete_search_run(
                db=db,
                search_run=search_run,
            )

            self.commit(db)

        except SQLAlchemyError:
            db.rollback()
            raise


search_run_service = SearchRunService()
