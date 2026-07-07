from fastapi import status
from src.app.exceptions.base import AppException
from src.app.core.error_codes import ErrorCode


class InvalidCredentialsException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = ErrorCode.INVALID_CREDENTIALS
    detail = "Invalid email or password."


class InvalidTokenException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = ErrorCode.INVALID_TOKEN
    detail = "Invalid authentication token."


class ExpiredTokenException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = ErrorCode.EXPIRED_TOKEN
    detail = "Authentication token has expired."


class InactiveUserException(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = ErrorCode.INACTIVE_USER
    detail = "User account is inactive."


class PermissionDeniedException(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = ErrorCode.PERMISSION_DENIED
    detail = "You don't have permission to perform this action."
