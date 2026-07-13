"""
Exceptions for the USDA FDC client.
"""

class FdcApiError(Exception):
    """Base exception for all FDC API errors."""
    pass

class FdcAuthError(FdcApiError):
    """Exception raised when authentication fails."""
    pass

class FdcRateLimitError(FdcApiError):
    """Exception raised when the API rate limit is exceeded."""
    pass

class FdcTimeoutError(FdcApiError):
    """Exception raised when a request to the FDC API times out.

    Distinct from a generic FdcApiError so callers can tell "slow" from
    "broken" — a timeout is usually worth retrying, a 400 is not.
    """
    pass

class FdcValidationError(FdcApiError):
    """Exception raised when input validation fails."""
    pass

class FdcResourceNotFoundError(FdcApiError):
    """Exception raised when a requested resource is not found."""
    pass