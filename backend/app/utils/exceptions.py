class AppException(Exception):
    """Base application exception with optional status code."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


class ValidationException(AppException):
    """Raised when business validation fails."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code)

