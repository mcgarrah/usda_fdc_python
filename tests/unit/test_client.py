"""Tests for the FdcClient class."""

import pytest
from unittest.mock import patch, MagicMock

from usda_fdc import FdcClient
from usda_fdc.exceptions import FdcApiError, FdcAuthError, FdcRateLimitError


def test_init_with_api_key():
    """Test initializing the client with an API key."""
    client = FdcClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.base_url == "https://api.nal.usda.gov/fdc/v1/"


def test_init_without_api_key():
    """Test initializing the client without an API key."""
    with pytest.raises(ValueError):
        FdcClient(api_key=None)


def test_init_with_custom_base_url():
    """Test initializing the client with a custom base URL."""
    client = FdcClient(api_key="test_key", base_url="https://example.com/api/")
    assert client.base_url == "https://example.com/api/"


def test_make_request_success(mock_client):
    """Test making a successful request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"key": "value"}
    
    mock_client.session.request.return_value = mock_response
    mock_client._make_request = FdcClient._make_request.__get__(mock_client)
    
    result = mock_client._make_request("endpoint")
    
    assert result == {"key": "value"}
    mock_client.session.request.assert_called_once()


def test_make_request_auth_error(mock_client):
    """Test making a request with authentication error."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    
    mock_client.session.request.return_value = mock_response
    mock_client.session.request.return_value.raise_for_status.side_effect = Exception("401 Client Error")
    mock_client._make_request = FdcClient._make_request.__get__(mock_client)
    
    with pytest.raises(FdcAuthError):
        mock_client._make_request("endpoint")


def test_make_request_rate_limit_error(mock_client):
    """Test making a request with rate limit error."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Too Many Requests"
    
    mock_client.session.request.return_value = mock_response
    mock_client.session.request.return_value.raise_for_status.side_effect = Exception("429 Client Error")
    mock_client._make_request = FdcClient._make_request.__get__(mock_client)
    
    with pytest.raises(FdcRateLimitError):
        mock_client._make_request("endpoint")


def test_make_request_api_error(mock_client):
    """Test making a request with API error."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Server Error"
    
    mock_client.session.request.return_value = mock_response
    mock_client.session.request.return_value.raise_for_status.side_effect = Exception("500 Server Error")
    mock_client._make_request = FdcClient._make_request.__get__(mock_client)
    
    with pytest.raises(FdcApiError):
        mock_client._make_request("endpoint")


def test_search(mock_client, sample_search_result_data):
    """Test searching for foods."""
    mock_client._make_request.return_value = sample_search_result_data
    
    result = mock_client.search("apple")
    
    mock_client._make_request.assert_called_once_with(
        "foods/search",
        params={
            "query": "apple",
            "pageSize": 50,
            "pageNumber": 1
        }
    )
    
    assert result.total_hits == sample_search_result_data["totalHits"]
    assert len(result.foods) == len(sample_search_result_data["foods"])
    assert result.foods[0].fdc_id == sample_search_result_data["foods"][0]["fdcId"]
    assert result.foods[0].description == sample_search_result_data["foods"][0]["description"]


def test_get_food(mock_client, sample_food_data):
    """Test getting a food by FDC ID."""
    mock_client._make_request.return_value = sample_food_data
    
    result = mock_client.get_food(1234)
    
    mock_client._make_request.assert_called_once_with(
        "food/1234",
        params={"format": "full"}
    )
    
    assert result.fdc_id == sample_food_data["fdcId"]
    assert result.description == sample_food_data["description"]
    assert len(result.nutrients) == len(sample_food_data["foodNutrients"])
    assert len(result.food_portions) == len(sample_food_data["foodPortions"])


def test_get_foods(mock_client, sample_food_data):
    """Test getting multiple foods by FDC ID."""
    mock_client._make_request.return_value = [sample_food_data, sample_food_data]
    
    result = mock_client.get_foods([1234, 5678])
    
    mock_client._make_request.assert_called_once_with(
        "foods",
        params={
            "fdcIds": [1234, 5678],
            "format": "full"
        }
    )
    
    assert len(result) == 2
    assert result[0].fdc_id == sample_food_data["fdcId"]
    assert result[1].fdc_id == sample_food_data["fdcId"]


def test_get_nutrients(mock_client, sample_food_data):
    """Test getting nutrients for a food."""
    mock_client._make_request.return_value = sample_food_data
    
    result = mock_client.get_nutrients(1234)
    
    mock_client._make_request.assert_called_once_with(
        "food/1234",
        params={"format": "full"}
    )
    
    assert len(result) == len(sample_food_data["foodNutrients"])
    assert result[0].name == sample_food_data["foodNutrients"][0]["nutrient"]["name"]
    assert result[0].amount == sample_food_data["foodNutrients"][0]["amount"]


def test_list_foods(mock_client, sample_food_data):
    """Test listing foods."""
    mock_client._make_request.return_value = [sample_food_data, sample_food_data]
    
    result = mock_client.list_foods(
        data_type=["Branded"],
        page_size=10,
        page_number=2,
        sort_by="description",
        sort_order="asc"
    )
    
    mock_client._make_request.assert_called_once_with(
        "foods/list",
        params={
            "dataType": ["Branded"],
            "pageSize": 10,
            "pageNumber": 2,
            "sortBy": "description",
            "sortOrder": "asc"
        }
    )
    
    assert len(result) == 2
    assert result[0].fdc_id == sample_food_data["fdcId"]
    assert result[1].fdc_id == sample_food_data["fdcId"]