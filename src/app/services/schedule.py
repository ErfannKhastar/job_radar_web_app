"""
Schedule service.

Contains the business logic for managing execution schedules
associated with SearchProfiles.

Responsibilities:
- Validate schedule configurations.
- Prevent duplicate schedules.
- Generate cron expressions.
- Create, update and delete schedules.
- Enable / disable schedules.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from src.app.core.enums import ScheduleType
from src.app.crud.source import get_source_by_id
from src.app.crud.schedule import (
    create_schedule,
    get_schedule_by_id,
    get_duplicate_schedule,
    get_schedules_by_profile,
    update_schedule,
    update_last_run,
    set_schedule_status,
    delete_schedule,
)
from src.app.crud.search_profile import (
    get_search_profile_by_id,
)
from src.app.exceptions.schedule import (
    ScheduleNotFoundException,
    ScheduleAlreadyExistsException,
    InvalidScheduleConfigurationException,
    ScheduleAlreadyActiveException,
    ScheduleAlreadyInactiveException,
)
from src.app.exceptions.search_profile import (
    SearchProfileNotFoundException,
)
from src.app.exceptions.source import (
    SourceNotFoundException,
    InactiveSourceException,
)
from src.app.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
)
from src.app.services.base import BaseService
from src.app.models.user import User
from src.app.models.schedule import Schedule


class ScheduleService(BaseService):
    """
    Business logic for SearchProfile schedules.
    """

    # ------------------------------------------------------------------
    # Private Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_cron_expression(
        schedule_data: ScheduleCreate | ScheduleUpdate,
    ) -> str | None:
        """
        Build a cron expression based on the selected schedule type.

        Returns None for ONE_TIME schedules.
        """

        schedule_type = schedule_data.schedule_type

        if schedule_type == ScheduleType.DAILY:
            return f"{schedule_data.minute} {schedule_data.hour} * * *"

        if schedule_type == ScheduleType.WEEKLY:
            return (
                f"{schedule_data.minute} "
                f"{schedule_data.hour} "
                f"* * "
                f"{schedule_data.weekday}"
            )

        return None

    @staticmethod
    def _validate_schedule_configuration(
        schedule_data: ScheduleCreate | ScheduleUpdate,
    ) -> None:
        """
        Validate that the schedule configuration is consistent with the
        selected schedule type.
        """

        schedule_type = schedule_data.schedule_type

        if schedule_type == ScheduleType.ONCE:

            if schedule_data.run_once_at is None:
                raise InvalidScheduleConfigurationException()

            if (
                schedule_data.hour is not None
                or schedule_data.minute is not None
                or schedule_data.weekday is not None
            ):
                raise InvalidScheduleConfigurationException()

            return

        if schedule_type == ScheduleType.DAILY:

            if schedule_data.hour is None or schedule_data.minute is None:
                raise InvalidScheduleConfigurationException()

            if (
                schedule_data.weekday is not None
                or schedule_data.run_once_at is not None
            ):
                raise InvalidScheduleConfigurationException()

            return

        if schedule_type == ScheduleType.WEEKLY:

            if (
                schedule_data.hour is None
                or schedule_data.minute is None
                or schedule_data.weekday is None
            ):
                raise InvalidScheduleConfigurationException()

            if schedule_data.run_once_at is not None:
                raise InvalidScheduleConfigurationException()

    def _get_owned_schedule(
        self,
        db: Session,
        schedule_id: int,
        current_user: User,
    ) -> Schedule:
        """
        Retrieve a schedule only if it belongs to one of the current
        user's SearchProfiles.
        """

        schedule = get_schedule_by_id(
            db=db,
            schedule_id=schedule_id,
        )

        if schedule is None:
            raise ScheduleNotFoundException()

        profile = get_search_profile_by_id(
            db=db,
            profile_id=schedule.search_profile_id,
            user_id=current_user.id,
        )

        if profile is None:
            raise ScheduleNotFoundException()

        return schedule

    @staticmethod
    def _merge_schedule_data(
        schedule,
        schedule_data: ScheduleUpdate,
    ) -> ScheduleCreate:
        """
        Merge the current schedule values with the incoming update payload.

        This produces a complete ScheduleCreate-like object that can be
        validated before persisting changes.
        """

        return ScheduleCreate(
            search_profile_id=schedule.search_profile_id,
            schedule_type=(
                schedule_data.schedule_type
                if schedule_data.schedule_type is not None
                else schedule.schedule_type
            ),
            hour=(
                schedule_data.hour if schedule_data.hour is not None else schedule.hour
            ),
            minute=(
                schedule_data.minute
                if schedule_data.minute is not None
                else schedule.minute
            ),
            weekday=(
                schedule_data.weekday
                if schedule_data.weekday is not None
                else schedule.weekday
            ),
            run_once_at=(
                schedule_data.run_once_at
                if schedule_data.run_once_at is not None
                else schedule.run_once_at
            ),
        )

    def create(
        self,
        db: Session,
        current_user: User,
        schedule_data: ScheduleCreate,
    ) -> ScheduleResponse:
        """
        Create a schedule for one of the user's SearchProfiles.

        Business rules:
        - SearchProfile must exist.
        - User must own the SearchProfile.
        - Source must be active.
        - Only one schedule may exist per SearchProfile.
        - Schedule configuration must be valid.
        """

        profile = get_search_profile_by_id(
            db=db,
            profile_id=schedule_data.search_profile_id,
            user_id=current_user.id,
        )

        if profile is None:
            raise SearchProfileNotFoundException()

        source = get_source_by_id(db=db, source_id=profile.source_id)

        if source is None:
            raise SourceNotFoundException()

        if not source.is_active:
            raise InactiveSourceException()

        duplicate = get_duplicate_schedule(
            db=db,
            search_profile_id=profile.id,
            schedule_type=schedule_data.schedule_type,
            hour=schedule_data.hour,
            minute=schedule_data.minute,
            weekday=schedule_data.weekday,
            run_once_at=schedule_data.run_once_at,
        )

        if duplicate:
            raise ScheduleAlreadyExistsException()

        self._validate_schedule_configuration(schedule_data)

        cron_expression = self._build_cron_expression(schedule_data)

        try:
            schedule = create_schedule(
                db=db,
                schedule_data=schedule_data,
                cron_expression=cron_expression,
            )

            self.commit(db, schedule)

            return ScheduleResponse.model_validate(schedule)

        except SQLAlchemyError:
            db.rollback()
            raise

    def get_by_id(
        self,
        db: Session,
        current_user: User,
        schedule_id: int,
    ) -> ScheduleResponse:
        """
        Return one schedule owned by the authenticated user.
        """

        schedule = self._get_owned_schedule(
            db=db,
            schedule_id=schedule_id,
            current_user=current_user,
        )

        return ScheduleResponse.model_validate(schedule)

    def get_all(
        self,
        db: Session,
        current_user: User,
        search_profile_id: int,
    ) -> list[ScheduleResponse]:
        """
        Return all schedules belonging to one SearchProfile.

        Ownership is verified before returning any data.
        """

        profile = get_search_profile_by_id(
            db=db,
            profile_id=search_profile_id,
            user_id=current_user.id,
        )

        if profile is None:
            raise SearchProfileNotFoundException()

        schedules = get_schedules_by_profile(
            db=db,
            search_profile_id=search_profile_id,
        )

        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]

    def update(
        self,
        db: Session,
        current_user: User,
        schedule_id: int,
        schedule_data: ScheduleUpdate,
    ) -> ScheduleResponse:
        """
        Update an existing schedule.

        Business rules:
        - Schedule must belong to the current user.
        - Updated configuration must remain valid.
        """

        schedule = self._get_owned_schedule(
            db=db,
            schedule_id=schedule_id,
            current_user=current_user,
        )

        merged_data = self._merge_schedule_data(
            schedule=schedule,
            schedule_data=schedule_data,
        )

        duplicate = get_duplicate_schedule(
            db=db,
            search_profile_id=schedule.search_profile_id,
            schedule_type=merged_data.schedule_type,
            hour=merged_data.hour,
            minute=merged_data.minute,
            weekday=merged_data.weekday,
            run_once_at=merged_data.run_once_at,
        )

        if duplicate and duplicate.id != schedule.id:
            raise ScheduleAlreadyExistsException()

        self._validate_schedule_configuration(merged_data)

        cron_expression = self._build_cron_expression(merged_data)

        try:
            update_schedule(
                db=db,
                schedule=schedule,
                schedule_data=schedule_data,
                cron_expression=cron_expression,
            )

            self.commit(db, schedule)

            return ScheduleResponse.model_validate(schedule)

        except SQLAlchemyError:
            db.rollback()
            raise

    def set_active_status(
        self,
        db: Session,
        current_user: User,
        schedule_id: int,
        is_active: bool,
    ) -> ScheduleResponse:
        """
        Enable or disable a schedule.
        """

        schedule = self._get_owned_schedule(
            db=db,
            schedule_id=schedule_id,
            current_user=current_user,
        )

        if schedule.is_active == is_active:

            if is_active:
                raise ScheduleAlreadyActiveException()

            raise ScheduleAlreadyInactiveException()

        try:
            set_schedule_status(
                db=db,
                schedule=schedule,
                is_active=is_active,
            )

            self.commit(db, schedule)

            return ScheduleResponse.model_validate(schedule)

        except SQLAlchemyError:
            db.rollback()
            raise

    def delete(
        self,
        db: Session,
        current_user: User,
        schedule_id: int,
    ) -> None:
        """
        Permanently delete a schedule.
        """

        schedule = self._get_owned_schedule(
            db=db,
            schedule_id=schedule_id,
            current_user=current_user,
        )

        try:
            delete_schedule(
                db=db,
                schedule=schedule,
            )

            self.commit(db)

        except SQLAlchemyError:
            db.rollback()
            raise


schedule_service = ScheduleService()
