"""
Search Profile service.

Contains the business logic responsible for managing a user's job search
profiles.

Responsibilities:
- Create search profiles.
- Retrieve search profiles.
- Update search profiles.
- Enable/disable search profiles.
- Delete search profiles.

Business rules such as ownership validation, duplicate prevention,
and source validation are implemented here.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from src.app.crud.search_profile import (
    create_search_profile,
    get_search_profile_by_id,
    get_search_profile_by_name,
)
from src.app.crud.source import get_source_by_id
from src.app.exceptions.search_profile import (
    SearchProfileAlreadyExistsException,
    SearchProfileNotFoundException,
)
from src.app.exceptions.source import (
    SourceNotFoundException,
    InactiveSourceException,
)
from src.app.models.search_profile import SearchProfile
from src.app.models.user import User

from src.app.schemas.search_profile import (
    SearchProfileCreate,
    SearchProfileResponse,
)

from src.app.services.base import BaseService

from src.app.crud.search_profile import (
    get_search_profiles_by_user,
    get_search_profile_by_name_excluding_id,
    update_search_profile,
)

from src.app.schemas.search_profile import SearchProfileUpdate
from src.app.crud.search_profile import (
    delete_search_profile,
    set_search_profile_active_status,
)


class SearchProfileService(BaseService):
    """
    Service responsible for SearchProfile business logic.
    """

    def _get_owned_profile(
        self,
        db: Session,
        profile_id: int,
        current_user: User,
    ) -> SearchProfile:
        """
        Retrieve a search profile that belongs to the current user.

        This helper centralizes ownership validation so every public
        method can reuse the same logic.

        Raises:
            SearchProfileNotFoundException:
                If the profile does not exist or does not belong
                to the authenticated user.
        """

        profile = get_search_profile_by_id(
            db=db,
            profile_id=profile_id,
            user_id=current_user.id,
        )

        if profile is None:
            raise SearchProfileNotFoundException()

        return profile

    def create(
        self,
        db: Session,
        current_user: User,
        profile_data: SearchProfileCreate,
    ) -> SearchProfileResponse:
        """
        Create a new search profile.

        Business rules:
        - The referenced Source must exist.
        - The Source must be active.
        - Profile names must be unique per user.
        """

        source = get_source_by_id(
            db=db,
            source_id=profile_data.source_id,
        )

        if source is None:
            raise SourceNotFoundException()

        if not source.is_active:
            raise InactiveSourceException()

        existing_profile = get_search_profile_by_name(
            db=db,
            user_id=current_user.id,
            name=profile_data.name,
        )

        if existing_profile is not None:
            raise SearchProfileAlreadyExistsException()

        try:
            profile = create_search_profile(
                db=db,
                user_id=current_user.id,
                profile_data=profile_data,
            )

            self.commit(db, profile)

            return SearchProfileResponse.model_validate(profile)

        except SQLAlchemyError:
            db.rollback()
            raise

    def get_all(
        self,
        db: Session,
        current_user: User,
        active_only: bool = False,
    ) -> list[SearchProfileResponse]:
        """
        Retrieve all search profiles owned by the current user.

        Args:
            db: Active database session.
            current_user: Authenticated user.
            active_only: Whether to return only active profiles.

        Returns:
            List of serialized search profiles.
        """

        profiles = get_search_profiles_by_user(
            db=db,
            user_id=current_user.id,
            active_only=active_only,
        )

        return [SearchProfileResponse.model_validate(profile) for profile in profiles]

    def get_by_id(
        self,
        db: Session,
        current_user: User,
        profile_id: int,
    ) -> SearchProfileResponse:
        """
        Retrieve a single search profile.

        Raises:
            SearchProfileNotFoundException:
                If the profile does not belong to the current user.
        """

        profile = self._get_owned_profile(
            db=db,
            profile_id=profile_id,
            current_user=current_user,
        )

        return SearchProfileResponse.model_validate(profile)

    def update(
        self,
        db: Session,
        current_user: User,
        profile_id: int,
        profile_data: SearchProfileUpdate,
    ) -> SearchProfileResponse:
        """
        Update an existing search profile.

        Business rules:
        - User must own the profile.
        - Profile name must remain unique for that user.
        """

        profile = self._get_owned_profile(
            db=db,
            profile_id=profile_id,
            current_user=current_user,
        )

        if profile_data.name.strip() is not None and profile_data.name.strip() != profile.name:
            duplicate = get_search_profile_by_name_excluding_id(
                db=db,
                user_id=current_user.id,
                name=profile_data.name,
                profile_id=profile.id,
            )

            if duplicate is not None:
                raise SearchProfileAlreadyExistsException()

        try:
            profile = update_search_profile(
                db=db,
                profile=profile,
                profile_data=profile_data,
            )

            self.commit(db, profile)

            return SearchProfileResponse.model_validate(profile)

        except SQLAlchemyError:
            db.rollback()
            raise

    def set_active_status(
        self,
        db: Session,
        current_user: User,
        profile_id: int,
        is_active: bool,
    ) -> SearchProfileResponse:
        """
        Enable or disable a search profile.

        Args:
            db: Active database session.
            current_user: Authenticated user.
            profile_id: Target profile ID.
            is_active: Desired active state.

        Returns:
            Updated search profile.
        """

        profile = self._get_owned_profile(
            db=db,
            profile_id=profile_id,
            current_user=current_user,
        )

        if profile.is_active == is_active:
            return SearchProfileResponse.model_validate(profile)

        try:
            profile = set_search_profile_active_status(
                db=db,
                profile=profile,
                is_active=is_active,
            )

            self.commit(db, profile)

            return SearchProfileResponse.model_validate(profile)

        except SQLAlchemyError:
            db.rollback()
            raise

    def delete(
        self,
        db: Session,
        current_user: User,
        profile_id: int,
    ) -> None:
        """
        Permanently delete one of the current user's search profiles.

        Raises:
            SearchProfileNotFoundException:
                If the profile does not exist or does not belong to the user.
        """

        profile = self._get_owned_profile(
            db=db,
            profile_id=profile_id,
            current_user=current_user,
        )

        try:
            delete_search_profile(
                db=db,
                profile=profile,
            )

            self.commit(db)

        except SQLAlchemyError:
            db.rollback()
            raise


search_profile_service = SearchProfileService()
