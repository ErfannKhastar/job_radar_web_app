"""
Base application exception.

All custom exceptions should inherit from this class.
"""


class AppException(Exception):
    """
    Base application exception.
    """

    status_code: int = 500
    error_code: str = "APPLICATION_ERROR"
    detail: str = "Application error."

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
