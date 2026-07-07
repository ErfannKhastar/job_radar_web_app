"""
Standardized error codes for the application.

Defining error codes as Enums ensures that the backend sends consistent
error identifiers to the frontend. This is especially crucial for a
bilingual (i18n) project, as the frontend can use these specific keys
to show the appropriate localized error message to the user.
"""

from enum import Enum


class ErrorCode(str, Enum):
    """
    Specific string identifiers for application-level errors.
    These codes are used by the frontend to map backend errors to
    user-friendly, localized messages.
    """

    # --- Authentication & Authorization Errors ---
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_TOKEN = "INVALID_TOKEN"
    EXPIRED_TOKEN = "EXPIRED_TOKEN"
    INACTIVE_USER = "INACTIVE_USER"
    PERMISSION_DENIED = "PERMISSION_DENIED"

    # --- User Management & Validation Errors ---
    USER_NOT_FOUND = "USER_NOT_FOUND"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    USERNAME_ALREADY_EXISTS = "USERNAME_ALREADY_EXISTS"
    INVALID_PASSWORD = "INVALID_PASSWORD"
    USER_ALREADY_INACTIVE = "USER_ALREADY_INACTIVE"
    CANNOT_DELETE_SUPERUSER = "CANNOT_DELETE_SUPERUSER"
