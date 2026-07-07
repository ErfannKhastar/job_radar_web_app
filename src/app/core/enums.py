"""
Enumerations module for standardizing specific values across the application.

Using Enums ensures data consistency, helps Pydantic with input validation,
and makes the codebase more readable and robust by avoiding hardcoded strings.
"""

from enum import Enum


class Language(str, Enum):
    """Supported languages for the application's i18n (Internationalization)."""

    FA = "fa"
    EN = "en"


class ExportFormat(str, Enum):
    """Supported formats for exporting scraped job data to the user."""

    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"


class NotificationChannel(str, Enum):
    """Available channels for delivering the automation results to the user."""

    TELEGRAM = "telegram"
    JSON = "json"
    EMAIL = "email"


class NotificationStatus(str, Enum):
    """Tracking statuses for the delivery of notifications."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class ScheduleType(str, Enum):
    """Execution frequency options for the user's scraping automation profiles."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


class SearchRunStatus(str, Enum):
    """Statuses for background scraping tasks and automation runs."""

    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class TokenType(str, Enum):
    """Types of JWT tokens used for secure authentication."""

    ACCESS = "access"
    REFRESH = "refresh"
