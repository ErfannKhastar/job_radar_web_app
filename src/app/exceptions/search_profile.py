"""
Search Profile related exceptions.
"""

from fastapi import status
from src.app.core.error_codes import ErrorCode
from src.app.exceptions.base import AppException


class SearchProfileNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = ErrorCode.SEARCH_PROFILE_NOT_FOUND
    detail = "Search profile not found."


class SearchProfileAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = ErrorCode.SEARCH_PROFILE_ALREADY_EXISTS
    detail = "A search profile with the same name already exists."


class SourceInactiveException(AppException):
    status_code = 400
    error_code = ErrorCode.SOURCE_INACTIVE
    detail = "The selected source is currently inactive."
