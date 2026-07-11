from fastapi import status

from src.app.core.error_codes import ErrorCode
from src.app.exceptions.base import AppException


class SearchRunNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = ErrorCode.SEARCH_RUN_NOT_FOUND
    message = "Search run not found."


class SearchRunAlreadyRunningException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = ErrorCode.SEARCH_RUN_ALREADY_RUNNING
    message = "A search run is already running."


class SearchRunAlreadyFinishedException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = ErrorCode.SEARCH_RUN_ALREADY_FINISHED
    message = "Search run has already finished."


class InvalidSearchRunStatusException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = ErrorCode.INVALID_SEARCH_RUN_STATUS
    message = "Invalid search run status transition."