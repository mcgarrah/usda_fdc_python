"""
Unit tests for the FdcClient class.
"""

import pytest
from unittest.mock import patch, MagicMock

import requests

from usda_fdc import FdcClient, FdcApiError, FdcTimeoutError
from usda_fdc.client import DEFAULT_TIMEOUT
from usda_fdc.models import Nutrient

def test_client_initialization():
    """Test client initialization with API key."""
    client = FdcClient("test_api_key")
    assert client.api_key == "test_api_key"
    assert client.base_url == "https://api.nal.usda.gov/fdc/v1/"

def test_client_initialization_with_custom_url():
    """Test client initialization with custom API URL."""
    client = FdcClient("test_api_key", base_url="https://custom-api.example.com/")
    assert client.api_key == "test_api_key"
    assert client.base_url == "https://custom-api.example.com/"

def test_search(mock_client, mock_search_response):
    """Test search method."""
    with patch.object(mock_client, '_make_request', return_value=mock_search_response):
        results = mock_client.search("apple")
        assert results.total_hits == 2
        assert len(results.foods) == 2
        assert results.foods[0].fdc_id == 1234
        assert results.foods[0].description == "Test Food 1"

def test_search_with_parameters(mock_client, mock_search_response):
    """Test search method with additional parameters."""
    with patch.object(mock_client, '_make_request', return_value=mock_search_response) as mock_request:
        results = mock_client.search(
            "apple",
            data_type=["Branded"],
            page_size=25,
            page_number=2,
            sort_by="dataType.keyword",
            sort_order="asc"
        )
        
        # Verify the parameters were passed correctly
        args, kwargs = mock_request.call_args
        assert kwargs["params"]["query"] == "apple"
        assert kwargs["params"]["dataType"] == ["Branded"]
        assert kwargs["params"]["pageSize"] == 25
        assert kwargs["params"]["pageNumber"] == 2
        assert kwargs["params"]["sortBy"] == "dataType.keyword"
        assert kwargs["params"]["sortOrder"] == "asc"

def test_get_food(mock_client, mock_food_response):
    """Test get_food method."""
    with patch.object(mock_client, '_make_request', return_value=mock_food_response):
        food = mock_client.get_food(1234)
        assert food.fdc_id == 1234
        assert food.description == "Test Food"
        assert len(food.nutrients) == 2
        assert food.nutrients[0].name == "Protein"
        assert food.nutrients[0].amount == 10.5
        assert food.nutrients[0].unit_name == "g"

def test_get_foods(mock_client, mock_foods_list_response):
    """Test get_foods method."""
    with patch.object(mock_client, '_make_request', return_value=mock_foods_list_response):
        foods = mock_client.get_foods([1234, 5678])
        assert len(foods) == 2
        assert foods[0].fdc_id == 1234
        assert foods[0].description == "Test Food 1"
        assert foods[1].fdc_id == 5678
        assert foods[1].description == "Test Food 2"

def test_get_nutrients(mock_client, mock_nutrients_response):
    """Test get_nutrients method."""
    # The get_nutrients method first calls get_food, then returns food.nutrients
    with patch.object(mock_client, 'get_food') as mock_get_food:
        # Create real Nutrient objects instead of MagicMocks
        nutrients = [
            Nutrient(id=1001, name="Protein", amount=10.5, unit_name="g"),
            Nutrient(id=1002, name="Fat", amount=5.2, unit_name="g")
        ]
        
        # Create a mock food object with nutrients
        mock_food = MagicMock()
        mock_food.nutrients = nutrients
        mock_get_food.return_value = mock_food
        
        # Call get_nutrients
        result_nutrients = mock_client.get_nutrients(1234)
        
        # Verify get_food was called with the correct ID
        mock_get_food.assert_called_once_with(1234)
        
        # Verify the nutrients
        assert len(result_nutrients) == 2
        assert result_nutrients[0].name == "Protein"
        assert result_nutrients[0].amount == 10.5
        assert result_nutrients[0].unit_name == "g"

def test_list_foods(mock_client, mock_list_foods_response):
    """Test list_foods method."""
    with patch.object(mock_client, '_make_request', return_value=mock_list_foods_response):
        foods = mock_client.list_foods()
        assert len(foods) == 2
        assert foods[0].fdc_id == 1234
        assert foods[0].description == "Test Food 1"

def test_api_error_handling(mock_client):
    """Test API error handling."""
    with patch.object(mock_client, '_make_request', side_effect=FdcApiError("API Error")):
        with pytest.raises(FdcApiError) as excinfo:
            mock_client.search("apple")
        assert "API Error" in str(excinfo.value)

# ── Request timeouts ──────────────────────────────────────────────────
# requests has NO default timeout. Without one, a server that accepts the
# connection and never answers blocks the calling thread forever. Async
# consumers run this synchronous client in a thread pool, and their own
# asyncio.wait_for cannot cancel the blocking call underneath — so an
# unbounded request leaks a thread for the life of the process.

def test_client_has_a_default_timeout():
    client = FdcClient(api_key="test_key")
    assert client.timeout == DEFAULT_TIMEOUT
    assert client.timeout > 0


def test_client_timeout_is_configurable():
    client = FdcClient(api_key="test_key", timeout=5.0)
    assert client.timeout == 5.0


def test_timeout_is_actually_passed_to_the_request():
    """The easy regression: accept a timeout parameter, then forget to use it.

    A client that stores the value but never hands it to requests still blocks
    forever, while looking correct.
    """
    client = FdcClient(api_key="test_key", timeout=7.5)

    with patch.object(client.session, "request") as mock_request:
        mock_request.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={"foods": []}),
            raise_for_status=MagicMock(),
        )
        client._make_request("foods/search")

    assert mock_request.call_args.kwargs["timeout"] == 7.5


def test_timeout_raises_fdc_timeout_error():
    client = FdcClient(api_key="test_key", timeout=0.1)

    with patch.object(client.session, "request",
                      side_effect=requests.exceptions.Timeout("timed out")):
        with pytest.raises(FdcTimeoutError) as exc:
            client._make_request("foods/search")

    assert "timed out" in str(exc.value).lower()
    assert "0.1" in str(exc.value)


def test_timeout_error_is_an_api_error():
    """Callers catching FdcApiError must keep catching timeouts."""
    assert issubclass(FdcTimeoutError, FdcApiError)


def test_timeout_is_distinguishable_from_other_failures():
    """A timeout is usually worth retrying; a 400 is not. Callers need to tell
    them apart, so a timeout must not surface as a bare FdcApiError."""
    client = FdcClient(api_key="test_key")

    with patch.object(client.session, "request",
                      side_effect=requests.exceptions.ConnectionError("refused")):
        with pytest.raises(FdcApiError) as exc:
            client._make_request("foods/search")

    assert not isinstance(exc.value, FdcTimeoutError)


# ── API key handling ──────────────────────────────────────────────────
# The key used to travel as a query parameter. requests puts the full URL into
# its exception messages, so the first connection blip wrote the caller's key
# into their tracebacks, log files and error tracker.

SECRET = "SUPER_SECRET_KEY_12345"


def test_api_key_is_sent_as_a_header():
    client = FdcClient(api_key=SECRET)
    assert client.session.headers["X-Api-Key"] == SECRET


def test_api_key_is_not_put_in_the_query_string():
    """The source of the leak: a key in the URL is a key in every log that URL
    reaches."""
    client = FdcClient(api_key=SECRET)

    with patch.object(client.session, "request") as mock_request:
        mock_request.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={}),
            raise_for_status=MagicMock(),
        )
        client._make_request("foods/search")

    assert "api_key" not in mock_request.call_args.kwargs["params"]


def test_api_key_does_not_leak_into_a_network_error():
    client = FdcClient(api_key=SECRET)

    leaky = requests.exceptions.ConnectionError(
        f"Max retries exceeded with url: /fdc/v1/food/1?api_key={SECRET}"
    )
    with patch.object(client.session, "request", side_effect=leaky):
        with pytest.raises(FdcApiError) as exc:
            client._make_request("food/1")

    assert SECRET not in str(exc.value)


def test_api_key_does_not_leak_into_an_http_error_body():
    client = FdcClient(api_key=SECRET)

    response = MagicMock(status_code=500, text=f"upstream rejected api_key={SECRET}")
    response.raise_for_status.side_effect = requests.exceptions.HTTPError("500")

    with patch.object(client.session, "request", return_value=response):
        with pytest.raises(FdcApiError) as exc:
            client._make_request("food/1")

    assert SECRET not in str(exc.value)
