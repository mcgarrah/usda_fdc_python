"""Tests for the Django cache."""

import pytest
from unittest.mock import patch, MagicMock

# Mark all tests in this module as django tests
pytestmark = pytest.mark.django

# Skip all tests if Django is not installed
try:
    import django
    from django.test import TestCase
    from django.core.cache import cache
    DJANGO_INSTALLED = True
except ImportError:
    DJANGO_INSTALLED = False

# Skip all tests if Django is not installed
if not DJANGO_INSTALLED:
    pytest.skip("Django not installed", allow_module_level=True)
else:
    # Import Django cache
    from usda_fdc.django.cache import FdcCache
    from usda_fdc.django.models import FoodModel, NutrientModel, FoodPortionModel
    from usda_fdc.models import Food, Nutrient, FoodPortion, SearchResult


    class TestFdcCache(TestCase):
        """Tests for the FdcCache class."""
        
        def setUp(self):
            """Set up test data."""
            self.api_key = "test_api_key"
            self.cache = FdcCache(api_key=self.api_key)
            
            # Create a sample food
            self.food_model = FoodModel.objects.create(
                fdc_id=1234,
                description="Test Food",
                data_type="Branded"
            )
            
            # Create a sample nutrient
            self.nutrient_model = NutrientModel.objects.create(
                food=self.food_model,
                nutrient_id=1003,
                name="Protein",
                amount=10.5,
                unit_name="g"
            )
            
            # Create a sample food portion
            self.food_portion_model = FoodPortionModel.objects.create(
                food=self.food_model,
                portion_id=9876,
                amount=1,
                gram_weight=100,
                measure_unit="serving"
            )
            
            # Sample API response for a food
            self.sample_food_data = {
                "fdcId": 5678,
                "description": "New Test Food",
                "dataType": "Foundation",
                "foodNutrients": [
                    {
                        "nutrient": {
                            "id": 1003,
                            "name": "Protein",
                            "unitName": "g"
                        },
                        "amount": 15.0
                    }
                ],
                "foodPortions": [
                    {
                        "id": 1234,
                        "amount": 1,
                        "gramWeight": 100,
                        "measureUnit": {
                            "name": "serving"
                        }
                    }
                ]
            }
            
            # Sample API response for search results
            self.sample_search_data = {
                "totalHits": 1,
                "currentPage": 1,
                "totalPages": 1,
                "foods": [
                    {
                        "fdcId": 5678,
                        "description": "New Test Food",
                        "dataType": "Foundation"
                    }
                ]
            }
        
        def test_get_cache_key(self):
            """Test generating cache keys."""
            key1 = self.cache._get_cache_key("test", 123)
            key2 = self.cache._get_cache_key("test", 123, "abc")
            
            assert key1 == "fdc:test:123"
            assert key2 == "fdc:test:123:abc"
        
        @patch("usda_fdc.django.cache.cache")
        def test_search_cache_hit(self, mock_cache):
            """Test searching with a cache hit."""
            # Mock the cache to return a search result
            mock_result = MagicMock()
            mock_cache.get.return_value = mock_result
            
            result = self.cache.search("apple")
            
            assert result == mock_result
            mock_cache.get.assert_called_once()
            self.cache.client.search.assert_not_called()
        
        @patch("usda_fdc.django.cache.cache")
        def test_search_cache_miss(self, mock_cache):
            """Test searching with a cache miss."""
            # Mock the cache to return None (cache miss)
            mock_cache.get.return_value = None
            
            # Mock the client to return a search result
            mock_result = MagicMock()
            self.cache.client.search = MagicMock(return_value=mock_result)
            
            result = self.cache.search("apple")
            
            assert result == mock_result
            mock_cache.get.assert_called_once()
            self.cache.client.search.assert_called_once_with(
                query="apple",
                data_type=None,
                page_size=50,
                page_number=1,
                sort_by=None,
                sort_order=None,
                brand_owner=None
            )
            mock_cache.set.assert_called_once()
        
        def test_get_food_from_database(self):
            """Test getting a food from the database."""
            food = self.cache.get_food(1234)
            
            assert isinstance(food, Food)
            assert food.fdc_id == 1234
            assert food.description == "Test Food"
            assert food.data_type == "Branded"
            assert len(food.nutrients) == 1
            assert len(food.food_portions) == 1
            
            # Verify the client was not called
            self.cache.client.get_food.assert_not_called()
        
        @patch.object(FdcCache, "_save_food_to_database")
        def test_get_food_from_api(self, mock_save):
            """Test getting a food from the API."""
            # Mock the client to return a food
            self.cache.client.get_food = MagicMock(return_value=Food.from_api_data(self.sample_food_data))
            
            food = self.cache.get_food(5678)
            
            assert isinstance(food, Food)
            assert food.fdc_id == 5678
            assert food.description == "New Test Food"
            assert food.data_type == "Foundation"
            
            # Verify the client was called
            self.cache.client.get_food.assert_called_once_with(
                fdc_id=5678,
                format="full",
                nutrients=None
            )
            
            # Verify the food was saved to the database
            mock_save.assert_called_once()
        
        def test_get_food_force_refresh(self):
            """Test getting a food with force refresh."""
            # Mock the client to return a food
            self.cache.client.get_food = MagicMock(return_value=Food.from_api_data(self.sample_food_data))
            
            food = self.cache.get_food(1234, force_refresh=True)
            
            assert isinstance(food, Food)
            
            # Verify the client was called even though the food exists in the database
            self.cache.client.get_food.assert_called_once_with(
                fdc_id=1234,
                format="full",
                nutrients=None
            )
        
        def test_get_foods_from_database(self):
            """Test getting multiple foods from the database."""
            # Create another food in the database
            FoodModel.objects.create(
                fdc_id=5678,
                description="Another Test Food",
                data_type="Foundation"
            )
            
            foods = self.cache.get_foods([1234, 5678])
            
            assert len(foods) == 2
            assert foods[0].fdc_id in [1234, 5678]
            assert foods[1].fdc_id in [1234, 5678]
            
            # Verify the client was not called
            self.cache.client.get_foods.assert_not_called()
        
        @patch.object(FdcCache, "_save_food_to_database")
        def test_get_foods_partial_from_api(self, mock_save):
            """Test getting foods partially from the database and partially from the API."""
            # Mock the client to return a food
            self.cache.client.get_foods = MagicMock(return_value=[Food.from_api_data(self.sample_food_data)])
            
            foods = self.cache.get_foods([1234, 5678])
            
            assert len(foods) == 2
            assert foods[0].fdc_id in [1234, 5678]
            assert foods[1].fdc_id in [1234, 5678]
            
            # Verify the client was called for the missing food
            self.cache.client.get_foods.assert_called_once_with(
                fdc_ids=[5678],
                format="full",
                nutrients=None
            )
            
            # Verify the food was saved to the database
            mock_save.assert_called_once()
        
        @patch.object(FdcCache, "_save_food_to_database")
        def test_refresh(self, mock_save):
            """Test refreshing foods."""
            # Mock the client to return foods
            self.cache.client.get_foods = MagicMock(return_value=[
                Food.from_api_data(self.sample_food_data),
                Food.from_api_data({**self.sample_food_data, "fdcId": 1234})
            ])
            
            self.cache.refresh([1234, 5678])
            
            # Verify the client was called for all foods
            self.cache.client.get_foods.assert_called_once_with(
                fdc_ids=[1234, 5678],
                format="full",
                nutrients=None,
                force_refresh=True
            )
            
            # Verify the foods were saved to the database
            assert mock_save.call_count == 2