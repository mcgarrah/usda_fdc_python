"""Integration tests for the USDA FDC Python Client."""

import pytest
import os

from usda_fdc import FdcClient


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def client(real_api_key):
    """Return a real FDC client."""
    return FdcClient(real_api_key)


def test_search(client):
    """Test searching for foods."""
    # Skip if no API key is available
    if not os.environ.get("FDC_API_KEY"):
        pytest.skip("FDC_API_KEY environment variable not set")
    
    result = client.search("apple")
    
    assert result.total_hits > 0
    assert len(result.foods) > 0
    assert result.foods[0].description is not None
    assert result.foods[0].fdc_id is not None


def test_get_food(client):
    """Test getting a food by FDC ID."""
    # Skip if no API key is available
    if not os.environ.get("FDC_API_KEY"):
        pytest.skip("FDC_API_KEY environment variable not set")
    
    # Use a known FDC ID for a food that is unlikely to change
    food = client.get_food(1750340)  # Example: Apples, raw, with skin
    
    assert food.fdc_id == 1750340
    assert food.description is not None
    assert food.data_type is not None
    assert len(food.nutrients) > 0
    assert len(food.food_portions) > 0


def test_get_foods(client):
    """Test getting multiple foods by FDC ID."""
    # Skip if no API key is available
    if not os.environ.get("FDC_API_KEY"):
        pytest.skip("FDC_API_KEY environment variable not set")
    
    # Use known FDC IDs for foods that are unlikely to change
    foods = client.get_foods([1750340, 1750341])  # Example: Apples and Bananas
    
    assert len(foods) == 2
    assert foods[0].fdc_id in [1750340, 1750341]
    assert foods[1].fdc_id in [1750340, 1750341]
    assert foods[0].description is not None
    assert foods[1].description is not None


def test_list_foods(client):
    """Test listing foods."""
    # Skip if no API key is available
    if not os.environ.get("FDC_API_KEY"):
        pytest.skip("FDC_API_KEY environment variable not set")
    
    foods = client.list_foods(page_size=10, page_number=1)
    
    assert len(foods) > 0
    assert foods[0].fdc_id is not None
    assert foods[0].description is not None


def test_search_with_data_type(client):
    """Test searching for foods with a specific data type."""
    # Skip if no API key is available
    if not os.environ.get("FDC_API_KEY"):
        pytest.skip("FDC_API_KEY environment variable not set")
    
    result = client.search("apple", data_type=["Branded"])
    
    assert result.total_hits > 0
    assert len(result.foods) > 0
    assert all(food.data_type == "Branded" for food in result.foods)