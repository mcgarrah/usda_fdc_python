"""Tests for the Django models."""

import pytest
from unittest.mock import patch

# Mark all tests in this module as django tests
pytestmark = pytest.mark.django

# Skip all tests if Django is not installed
try:
    import django
    from django.test import TestCase
    from django.db import models
    DJANGO_INSTALLED = True
except ImportError:
    DJANGO_INSTALLED = False

# Skip all tests if Django is not installed
if not DJANGO_INSTALLED:
    pytest.skip("Django not installed", allow_module_level=True)
else:
    # Import Django models
    from usda_fdc.django.models import FoodModel, NutrientModel, FoodPortionModel
    from usda_fdc.models import Food, Nutrient, FoodPortion


    class TestFoodModel(TestCase):
        """Tests for the FoodModel class."""
        
        def setUp(self):
            """Set up test data."""
            self.food_model = FoodModel.objects.create(
                fdc_id=1234,
                description="Test Food",
                data_type="Branded",
                publication_date="2021-10-28",
                food_class="Test Class",
                food_category="Test Category",
                scientific_name="Test Scientific Name",
                brand_owner="Test Brand Owner",
                brand_name="Test Brand",
                ingredients="Test Ingredients",
                serving_size=100,
                serving_size_unit="g",
                household_serving_fulltext="1 serving"
            )
            
            self.nutrient_model = NutrientModel.objects.create(
                food=self.food_model,
                nutrient_id=1003,
                name="Protein",
                amount=10.5,
                unit_name="g",
                nutrient_nbr=203,
                rank=600
            )
            
            self.food_portion_model = FoodPortionModel.objects.create(
                food=self.food_model,
                portion_id=9876,
                amount=1,
                gram_weight=100,
                portion_description="serving",
                modifier="about",
                measure_unit="serving"
            )
        
        def test_food_model_str(self):
            """Test the string representation of a FoodModel."""
            assert str(self.food_model) == "Test Food (1234)"
        
        def test_nutrient_model_str(self):
            """Test the string representation of a NutrientModel."""
            assert str(self.nutrient_model) == "Protein (10.5 g)"
        
        def test_food_portion_model_str(self):
            """Test the string representation of a FoodPortionModel."""
            assert str(self.food_portion_model) == "1 serving (100g)"
        
        def test_to_food_object(self):
            """Test converting a FoodModel to a Food object."""
            food = self.food_model.to_food_object()
            
            assert isinstance(food, Food)
            assert food.fdc_id == self.food_model.fdc_id
            assert food.description == self.food_model.description
            assert food.data_type == self.food_model.data_type
            assert food.publication_date == self.food_model.publication_date.isoformat()
            assert food.food_class == self.food_model.food_class
            assert food.food_category == self.food_model.food_category
            assert food.scientific_name == self.food_model.scientific_name
            assert food.brand_owner == self.food_model.brand_owner
            assert food.brand_name == self.food_model.brand_name
            assert food.ingredients == self.food_model.ingredients
            assert food.serving_size == self.food_model.serving_size
            assert food.serving_size_unit == self.food_model.serving_size_unit
            assert food.household_serving_fulltext == self.food_model.household_serving_fulltext
            
            assert len(food.nutrients) == 1
            assert food.nutrients[0].id == self.nutrient_model.nutrient_id
            assert food.nutrients[0].name == self.nutrient_model.name
            assert food.nutrients[0].amount == self.nutrient_model.amount
            assert food.nutrients[0].unit_name == self.nutrient_model.unit_name
            
            assert len(food.food_portions) == 1
            assert food.food_portions[0].id == self.food_portion_model.portion_id
            assert food.food_portions[0].amount == self.food_portion_model.amount
            assert food.food_portions[0].gram_weight == self.food_portion_model.gram_weight
            assert food.food_portions[0].portion_description == self.food_portion_model.portion_description
            assert food.food_portions[0].modifier == self.food_portion_model.modifier
            assert food.food_portions[0].measure_unit == self.food_portion_model.measure_unit
        
        def test_to_nutrient_object(self):
            """Test converting a NutrientModel to a Nutrient object."""
            nutrient = self.nutrient_model.to_nutrient_object()
            
            assert isinstance(nutrient, Nutrient)
            assert nutrient.id == self.nutrient_model.nutrient_id
            assert nutrient.name == self.nutrient_model.name
            assert nutrient.amount == self.nutrient_model.amount
            assert nutrient.unit_name == self.nutrient_model.unit_name
            assert nutrient.nutrient_nbr == self.nutrient_model.nutrient_nbr
            assert nutrient.rank == self.nutrient_model.rank
        
        def test_to_food_portion_object(self):
            """Test converting a FoodPortionModel to a FoodPortion object."""
            food_portion = self.food_portion_model.to_food_portion_object()
            
            assert isinstance(food_portion, FoodPortion)
            assert food_portion.id == self.food_portion_model.portion_id
            assert food_portion.amount == self.food_portion_model.amount
            assert food_portion.gram_weight == self.food_portion_model.gram_weight
            assert food_portion.portion_description == self.food_portion_model.portion_description
            assert food_portion.modifier == self.food_portion_model.modifier
            assert food_portion.measure_unit == self.food_portion_model.measure_unit