"""
Tests for how HTTP failures become exceptions.

The docs have long told callers to branch on ``e.status_code`` and to retry on
5xx — but nothing ever set that attribute, so the documented retry loop could
never fire. FdcResourceNotFoundError and FdcValidationError were defined,
documented, and never raised: a missing food arrived as a nondescript
FdcApiError. And FDC sits behind api.data.gov, which rejects a bad key with 403
rather than 401, so the single most common auth failure missed FdcAuthError too.
"""

import pytest
from unittest.mock import MagicMock, patch

import requests

from usda_fdc import (
    FdcClient,
    FdcApiError,
    FdcAuthError,
    FdcRateLimitError,
    FdcResourceNotFoundError,
    FdcTimeoutError,
    FdcValidationError,
)


def _client_returning(status: int, body: str = "") -> FdcClient:
    client = FdcClient(api_key="test_key")
    response = MagicMock(status_code=status, text=body)
    response.raise_for_status.side_effect = requests.exceptions.HTTPError(str(status))
    client.session.request = MagicMock(return_value=response)
    return client


@pytest.mark.parametrize("status,expected", [
    (400, FdcValidationError),
    (401, FdcAuthError),
    (403, FdcAuthError),           # api.data.gov's answer to a bad key
    (404, FdcResourceNotFoundError),
    (429, FdcRateLimitError),
    (500, FdcApiError),
])
def test_status_maps_to_its_exception(status, expected):
    client = _client_returning(status)

    with pytest.raises(expected):
        client._make_request("food/1")


@pytest.mark.parametrize("status", [400, 401, 403, 404, 429, 500, 503])
def test_status_code_is_carried_on_the_exception(status):
    """The docs tell callers to branch on this; it has to exist."""
    client = _client_returning(status)

    with pytest.raises(FdcApiError) as exc:
        client._make_request("food/1")

    assert exc.value.status_code == status


def test_a_bad_key_is_an_auth_error_not_a_mystery():
    """FDC answers an invalid key with 403. Catching only 401 meant the most
    common mistake a caller can make surfaced as a generic API error."""
    client = _client_returning(403, "API_KEY_INVALID")

    with pytest.raises(FdcAuthError) as exc:
        client._make_request("food/1")

    assert exc.value.status_code == 403


def test_a_missing_food_is_distinguishable_from_a_broken_api():
    """A food that does not exist is a normal outcome of a lookup, not a
    breakdown, and a caller must be able to tell the two apart."""
    client = _client_returning(404)

    with pytest.raises(FdcResourceNotFoundError):
        client._make_request("food/999999999")


def test_the_documented_retry_on_5xx_is_reachable():
    """Verbatim the shape of the retry example in docs/user/error_handling.rst,
    which could never have run: hasattr(e, 'status_code') was always False."""
    client = _client_returning(503)

    retried = False
    try:
        client._make_request("food/1")
    except FdcApiError as e:
        if e.status_code is not None and e.status_code >= 500:
            retried = True

    assert retried


def test_failures_that_never_reached_the_api_have_no_status_code():
    client = FdcClient(api_key="test_key")

    with patch.object(client.session, "request",
                      side_effect=requests.exceptions.ConnectionError("refused")):
        with pytest.raises(FdcApiError) as exc:
            client._make_request("food/1")

    assert exc.value.status_code is None


def test_a_timeout_has_no_status_code_either():
    client = FdcClient(api_key="test_key", timeout=0.1)

    with patch.object(client.session, "request",
                      side_effect=requests.exceptions.Timeout("timed out")):
        with pytest.raises(FdcTimeoutError) as exc:
            client._make_request("food/1")

    assert exc.value.status_code is None


def test_every_error_is_still_catchable_as_the_base_class():
    """Callers with a broad `except FdcApiError` must keep working."""
    for status in (400, 401, 403, 404, 429, 500):
        client = _client_returning(status)
        with pytest.raises(FdcApiError):
            client._make_request("food/1")
