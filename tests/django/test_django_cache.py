"""
Tests for Django cache integration.

These tests require Django to be installed.
Skip these tests if Django is not installed.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock

# Skip if Django is not installed
django_installed = False
try:
    import django
    django_installed = True
except ImportError:
    pass

pytestmark = pytest.mark.skipif(
    not django_installed,
    reason="Django not installed"
)

@pytest.mark.django
def test_django_cache():
    """Test Django cache."""
    if not django_installed:
        pytest.skip("Django not installed")
    
    # Import Django cache
    from usda_fdc.django.cache import FdcCache
    
    # Mock the client
    with patch('usda_fdc.django.cache.FdcClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create a cache instance
        cache = FdcCache(api_key="test_api_key")
        
        # Test that the client was created with the correct API key
        mock_client_class.assert_called_once_with("test_api_key")
        
        # Mock search method
        mock_search_result = MagicMock()
        mock_client.search.return_value = mock_search_result
        
        # Test search method
        result = cache.search("apple")
        
        # Verify that the client's search method was called
        mock_client.search.assert_called_once_with("apple")
        
        # Verify that the result is the same as the mock result
        assert result == mock_search_result

@pytest.mark.django
def test_django_cache_get_food():
    """Test Django cache get_food method."""
    if not django_installed:
        pytest.skip("Django not installed")
    
    # Import Django cache and models
    from usda_fdc.django.cache import FdcCache
    from usda_fdc.django.models import FoodModel
    
    # Mock the client and models
    with patch('usda_fdc.django.cache.FdcClient') as mock_client_class:
        with patch('usda_fdc.django.cache.FoodModel') as mock_food_model_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Mock the objects manager
            mock_objects = MagicMock()
            mock_food_model_class.objects = mock_objects
            
            # Mock the get method to raise DoesNotExist
            mock_objects.get.side_effect = FoodModel.DoesNotExist()
            
            # Mock the client's get_food method
            mock_food = MagicMock()
            mock_client.get_food.return_value = mock_food
            
            # Create a cache instance
            cache = FdcCache(api_key="test_api_key")
            
            # Test get_food method
            result = cache.get_food(1234)
            
            # Verify that the client's get_food method was called
            mock_client.get_food.assert_called_once_with(1234)
            
            # Verify that the result is the same as the mock food
            assert result == mock_food