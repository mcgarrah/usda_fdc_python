"""
Tests for Django models integration.

These tests require Django to be installed.
Skip these tests if Django is not installed.
"""

import pytest
import sys

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
def test_django_models():
    """Test Django models."""
    if not django_installed:
        pytest.skip("Django not installed")
    
    # Import Django models
    from usda_fdc.django.models import FoodModel, NutrientModel
    
    # Create a simple test
    food = FoodModel(
        fdc_id=1234,
        description="Test Food",
        data_type="Branded"
    )
    assert food.fdc_id == 1234
    assert food.description == "Test Food"
    assert food.data_type == "Branded"
    
    # Test nutrient model
    nutrient = NutrientModel(
        food=food,
        nutrient_id=1001,
        name="Protein",
        amount=10.5,
        unit_name="g"
    )
    assert nutrient.nutrient_id == 1001
    assert nutrient.name == "Protein"
    assert nutrient.amount == 10.5
    assert nutrient.unit_name == "g"
    assert nutrient.food == food