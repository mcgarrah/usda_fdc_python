"""
Unit tests for the exceptions module.
"""

import pytest
import requests

from usda_fdc.exceptions import FdcApiError, FdcRateLimitError, FdcAuthError

def test_fdc_api_error():
    """Test FdcApiError exception."""
    error = FdcApiError("API Error")
    assert str(error) == "API Error"
    
    # Test inheritance
    assert isinstance(error, Exception)

def test_fdc_rate_limit_error():
    """Test FdcRateLimitError exception."""
    error = FdcRateLimitError("Rate limit exceeded")
    assert str(error) == "Rate limit exceeded"
    assert isinstance(error, FdcApiError)
    assert isinstance(error, Exception)

def test_fdc_auth_error():
    """Test FdcAuthError exception."""
    error = FdcAuthError("Authentication failed")
    assert str(error) == "Authentication failed"
    assert isinstance(error, FdcApiError)
    assert isinstance(error, Exception)