"""
User related exceptions.
"""

from fastapi import status
from src.app.exceptions.base import AppException
from src.app.core.error_codes import ErrorCode


class UserNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = ErrorCode.USER_NOT_FOUND
    detail = "User not found."


class UsernameAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = ErrorCode.USERNAME_ALREADY_EXISTS
    detail = "Username is already in use."


class EmailAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = ErrorCode.EMAIL_ALREADY_EXISTS
    detail = "Email address is already in use."


class UserAlreadyInactiveException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = ErrorCode.USER_ALREADY_INACTIVE
    detail = "User account is already inactive."


class CannotDeleteSuperuserException(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = ErrorCode.CANNOT_DELETE_SUPERUSER
    detail = "Superuser accounts cannot be deleted."


class InvalidPasswordException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = ErrorCode.INVALID_PASSWORD
    detail = "The provided password is invalid."
