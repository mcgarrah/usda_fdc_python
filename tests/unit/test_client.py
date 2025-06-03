"""
Unit tests for the FdcClient class.
"""

import pytest
from unittest.mock import patch, MagicMock

from usda_fdc import FdcClient, FdcApiError
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