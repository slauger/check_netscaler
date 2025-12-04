"""
Exceptions for NITRO API client
"""


class NITROException(Exception):
    """Base exception for all NITRO client errors"""

    pass


class NITROAuthenticationError(NITROException):
    """Authentication failed (login error)"""

    pass


class NITROConnectionError(NITROException):
    """Connection to NetScaler failed"""

    pass


class NITROTimeoutError(NITROException):
    """Request timed out"""

    pass


class NITROAPIError(NITROException):
    """API returned an error response"""

    def __init__(self, message: str, error_code: int = None, response: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.response = response


class NITROResourceNotFoundError(NITROAPIError):
    """Requested resource not found (404)"""

    pass


class NITROPermissionError(NITROAPIError):
    """Insufficient permissions (403)"""

    pass
