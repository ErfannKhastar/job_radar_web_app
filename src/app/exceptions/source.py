"""
Source related exceptions.
"""

from fastapi import status
from src.app.core.error_codes import ErrorCode
from src.app.exceptions.base import AppException


class SourceNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = ErrorCode.SOURCE_NOT_FOUND
    detail = "Source not found."


class SourceAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = ErrorCode.SOURCE_ALREADY_EXISTS
    detail = "Source already exists."


class InactiveSourceException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = ErrorCode.SOURCE_INACTIVE
    detail = "Source is inactive."
