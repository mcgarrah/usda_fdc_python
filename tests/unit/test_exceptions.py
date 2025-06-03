"""Tests for the exception classes."""

import pytest

from usda_fdc.exceptions import (
    FdcApiError,
    FdcAuthError,
    FdcRateLimitError,
    FdcValidationError,
    FdcResourceNotFoundError
)


def test_fdc_api_error():
    """Test the FdcApiError exception."""
    error = FdcApiError("API error")
    assert str(error) == "API error"
    assert isinstance(error, Exception)


def test_fdc_auth_error():
    """Test the FdcAuthError exception."""
    error = FdcAuthError("Authentication failed")
    assert str(error) == "Authentication failed"
    assert isinstance(error, FdcApiError)


def test_fdc_rate_limit_error():
    """Test the FdcRateLimitError exception."""
    error = FdcRateLimitError("Rate limit exceeded")
    assert str(error) == "Rate limit exceeded"
    assert isinstance(error, FdcApiError)


def test_fdc_validation_error():
    """Test the FdcValidationError exception."""
    error = FdcValidationError("Invalid input")
    assert str(error) == "Invalid input"
    assert isinstance(error, FdcApiError)


def test_fdc_resource_not_found_error():
    """Test the FdcResourceNotFoundError exception."""
    error = FdcResourceNotFoundError("Resource not found")
    assert str(error) == "Resource not found"
    assert isinstance(error, FdcApiError)