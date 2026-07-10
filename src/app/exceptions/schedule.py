from fastapi import status
from src.app.core.error_codes import ErrorCode
from src.app.exceptions.base import AppException


class ScheduleNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = ErrorCode.SCHEDULE_NOT_FOUND
    message = "Schedule not found."


class ScheduleAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = ErrorCode.SCHEDULE_ALREADY_EXISTS
    message = "A schedule already exists for this search profile."


class InvalidScheduleConfigurationException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = ErrorCode.INVALID_SCHEDULE_CONFIGURATION
    message = "Invalid schedule configuration."


class ScheduleAlreadyActiveException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = ErrorCode.SCHEDULE_ALREADY_ACTIVE
    message = "Schedule is already active."


class ScheduleAlreadyInactiveException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = ErrorCode.SCHEDULE_ALREADY_INACTIVE
    message = "Schedule is already inactive."
