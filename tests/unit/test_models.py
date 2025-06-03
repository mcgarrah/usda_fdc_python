"""
Unit tests for the models module.
"""

import pytest
from datetime import date

from usda_fdc.models import Food, Nutrient, FoodPortion, SearchResult

def test_food_model():
    """Test the Food model."""
    food = Food(
        fdc_id=1234,
        description="Test Food",
        data_type="Branded",
        publication_date=date(2023, 1, 1),
        food_class="Test Class",
        food_category="Test Category",
        nutrients=[
            Nutrient(id=1001, name="Protein", amount=10.5, unit_name="g")
        ],
        food_portions=[
            FoodPortion(id=101, amount=1.0, gram_weight=100.0, measure_unit="cup")
        ]
    )
    
    assert food.fdc_id == 1234
    assert food.description == "Test Food"
    assert food.data_type == "Branded"
    assert food.publication_date == date(2023, 1, 1)
    assert food.food_class == "Test Class"
    assert food.food_category == "Test Category"
    assert len(food.nutrients) == 1
    assert food.nutrients[0].name == "Protein"
    assert len(food.food_portions) == 1
    assert food.food_portions[0].measure_unit == "cup"

def test_nutrient_model():
    """Test the Nutrient model."""
    nutrient = Nutrient(id=1001, name="Protein", amount=10.5, unit_name="g")
    
    assert nutrient.id == 1001
    assert nutrient.name == "Protein"
    assert nutrient.amount == 10.5
    assert nutrient.unit_name == "g"
    
    # Test string representation
    assert str(nutrient) == "Protein: 10.5 g"

def test_food_portion_model():
    """Test the FoodPortion model."""
    portion = FoodPortion(
        id=101,
        amount=1.0,
        gram_weight=100.0,
        measure_unit="cup",
        portion_description="1 cup"
    )
    
    assert portion.id == 101
    assert portion.amount == 1.0
    assert portion.gram_weight == 100.0
    assert portion.measure_unit == "cup"
    assert portion.portion_description == "1 cup"
    
    # Test string representation
    assert str(portion) == "1.0 cup (100.0g)"

def test_search_result_model():
    """Test the SearchResult model."""
    foods = [
        Food(fdc_id=1234, description="Test Food 1", data_type="Branded"),
        Food(fdc_id=5678, description="Test Food 2", data_type="Foundation")
    ]
    
    result = SearchResult(
        total_hits=2,
        current_page=1,
        total_pages=1,
        foods=foods
    )
    
    assert result.total_hits == 2
    assert result.current_page == 1
    assert result.total_pages == 1
    assert len(result.foods) == 2
    assert result.foods[0].fdc_id == 1234
    assert result.foods[1].fdc_id == 5678