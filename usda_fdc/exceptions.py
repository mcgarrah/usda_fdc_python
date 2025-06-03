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

class FdcValidationError(FdcApiError):
    """Exception raised when input validation fails."""
    pass

class FdcResourceNotFoundError(FdcApiError):
    """Exception raised when a requested resource is not found."""
    pass