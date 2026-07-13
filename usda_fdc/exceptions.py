"""
Exceptions for the USDA FDC client.
"""

from typing import Optional


class FdcApiError(Exception):
    """Base exception for all FDC API errors.

    Args:
        message: A description of what went wrong.
        status_code: The HTTP status the API replied with, when there was a
            reply at all. It is ``None`` for failures that never reached the
            API — a refused connection, a timeout, an unreadable body.
    """

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

class FdcAuthError(FdcApiError):
    """Exception raised when authentication fails.

    api.data.gov, which fronts FDC, answers an invalid or missing key with 403
    rather than 401, so both statuses raise this.
    """
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
    """Exception raised when the API rejects the request as invalid (HTTP 400).

    Typically a parameter outside the range FDC accepts, such as a page_size
    above 200.
    """
    pass

class FdcResourceNotFoundError(FdcApiError):
    """Exception raised when a requested resource is not found (HTTP 404).

    A food that does not exist is an ordinary outcome of a lookup, not a
    breakdown, so callers deserve to catch it on its own.
    """
    pass
