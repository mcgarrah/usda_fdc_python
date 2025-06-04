"""
Integration tests for the USDA FDC Python Client.

These tests require a valid API key and will make actual API calls.
Skip these tests if no API key is provided.
"""

import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from usda_fdc import FdcClient

# Skip if no API key is provided
pytestmark = pytest.mark.skipif(
    os.environ.get("FDC_API_KEY") is None,
    reason="FDC_API_KEY environment variable not set"
)

@pytest.fixture
def client():
    """Create a client with the API key from environment."""
    api_key = os.environ.get("FDC_API_KEY")
    return FdcClient(api_key)

@pytest.mark.integration
def test_search_integration(client):
    """Test search with actual API call."""
    results = client.search("apple", page_size=5)
    assert results.total_hits > 0
    assert len(results.foods) <= 5
    
@pytest.mark.integration
def test_get_food_integration(client):
    """Test get_food with actual API call."""
    # Apple, raw, with skin
    food = client.get_food(1750340)
    assert food.fdc_id == 1750340
    assert "Apple" in food.description
    assert len(food.nutrients) > 0
    
@pytest.mark.integration
def test_get_nutrients_integration(client):
    """Test get_nutrients with actual API call."""
    # Apple, raw, with skin
    nutrients = client.get_nutrients(1750340)
    assert len(nutrients) > 0
    assert nutrients[0].name is not None
    assert nutrients[0].amount is not None
    
@pytest.mark.integration
def test_list_foods_integration(client):
    """Test list_foods with actual API call."""
    foods = client.list_foods(page_size=5)
    assert len(foods) <= 5
    assert foods[0].fdc_id is not None
    assert foods[0].description is not None
    
@pytest.mark.integration
def test_get_foods_integration(client):
    """Test get_foods with actual API call."""
    # Apple and Banana
    foods = client.get_foods([1750340, 1750341])
    assert len(foods) == 2
    assert foods[0].fdc_id in [1750340, 1750341]
    assert foods[1].fdc_id in [1750340, 1750341]