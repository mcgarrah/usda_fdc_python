"""
USDA Food Data Central (FDC) Python Client

A comprehensive Python library for interacting with the USDA Food Data Central API,
designed for easy integration with Django applications and local database caching.
"""

__version__ = "0.1.5"

from .client import FdcClient
from .exceptions import FdcApiError, FdcRateLimitError, FdcAuthError

__all__ = ["FdcClient", "FdcApiError", "FdcRateLimitError", "FdcAuthError"]