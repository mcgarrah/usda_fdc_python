"""Tests for the data models."""

import pytest

from usda_fdc.models import Food, Nutrient, FoodPortion, SearchResult, SearchResultFood


def test_nutrient_init():
    """Test initializing a Nutrient object."""
    nutrient = Nutrient(
        id=1003,
        name="Protein",
        amount=10.5,
        unit_name="g",
        nutrient_nbr="203",
        rank=600
    )
    
    assert nutrient.id == 1003
    assert nutrient.name == "Protein"
    assert nutrient.amount == 10.5
    assert nutrient.unit_name == "g"
    assert nutrient.nutrient_nbr == "203"
    assert nutrient.rank == 600


def test_nutrient_from_api_data():
    """Test creating a Nutrient from API data."""
    data = {
        "nutrient": {
            "id": 1003,
            "name": "Protein",
            "unitName": "g",
            "number": "203",
            "rank": 600
        },
        "amount": 10.5
    }
    
    nutrient = Nutrient.from_api_data(data)
    
    assert nutrient.id == 1003
    assert nutrient.name == "Protein"
    assert nutrient.amount == 10.5
    assert nutrient.unit_name == "g"
    assert nutrient.nutrient_nbr == "203"
    assert nutrient.rank == 600


def test_food_portion_init():
    """Test initializing a FoodPortion object."""
    portion = FoodPortion(
        id=9876,
        amount=1,
        gram_weight=100,
        portion_description="serving",
        modifier="about",
        measure_unit="serving"
    )
    
    assert portion.id == 9876
    assert portion.amount == 1
    assert portion.gram_weight == 100
    assert portion.portion_description == "serving"
    assert portion.modifier == "about"
    assert portion.measure_unit == "serving"


def test_food_portion_from_api_data():
    """Test creating a FoodPortion from API data."""
    data = {
        "id": 9876,
        "amount": 1,
        "gramWeight": 100,
        "portionDescription": "serving",
        "modifier": "about",
        "measureUnit": {
            "name": "serving"
        }
    }
    
    portion = FoodPortion.from_api_data(data)
    
    assert portion.id == 9876
    assert portion.amount == 1
    assert portion.gram_weight == 100
    assert portion.portion_description == "serving"
    assert portion.modifier == "about"
    assert portion.measure_unit == "serving"


def test_food_init(sample_food):
    """Test initializing a Food object."""
    assert sample_food.fdc_id == 1234
    assert sample_food.description == "Test Food"
    assert sample_food.data_type == "Branded"
    assert len(sample_food.nutrients) == 2
    assert len(sample_food.food_portions) == 1


def test_food_from_api_data(sample_food_data):
    """Test creating a Food from API data."""
    food = Food.from_api_data(sample_food_data)
    
    assert food.fdc_id == sample_food_data["fdcId"]
    assert food.description == sample_food_data["description"]
    assert food.data_type == sample_food_data["dataType"]
    assert food.publication_date == sample_food_data["publicationDate"]
    assert food.food_class == sample_food_data["foodClass"]
    assert food.food_category == sample_food_data["foodCategory"]
    assert food.scientific_name == sample_food_data["scientificName"]
    assert food.brand_owner == sample_food_data["brandOwner"]
    assert food.brand_name == sample_food_data["brandName"]
    assert food.ingredients == sample_food_data["ingredients"]
    assert food.serving_size == sample_food_data["servingSize"]
    assert food.serving_size_unit == sample_food_data["servingSizeUnit"]
    assert food.household_serving_fulltext == sample_food_data["householdServingFullText"]
    assert len(food.nutrients) == len(sample_food_data["foodNutrients"])
    assert len(food.food_portions) == len(sample_food_data["foodPortions"])


def test_food_from_api_data_abridged():
    """Test creating a Food from abridged API data."""
    data = {
        "fdcId": 1234,
        "description": "Test Food",
        "dataType": "Branded"
    }
    
    food = Food.from_api_data(data, abridged=True)
    
    assert food.fdc_id == 1234
    assert food.description == "Test Food"
    assert food.data_type == "Branded"
    assert len(food.nutrients) == 0
    assert len(food.food_portions) == 0


def test_search_result_food_init():
    """Test initializing a SearchResultFood object."""
    food = SearchResultFood(
        fdc_id=1234,
        description="Test Food",
        data_type="Branded",
        publication_date="2021-10-28",
        food_category="Test Category",
        brand_owner="Test Brand Owner",
        brand_name="Test Brand"
    )
    
    assert food.fdc_id == 1234
    assert food.description == "Test Food"
    assert food.data_type == "Branded"
    assert food.publication_date == "2021-10-28"
    assert food.food_category == "Test Category"
    assert food.brand_owner == "Test Brand Owner"
    assert food.brand_name == "Test Brand"


def test_search_result_food_from_api_data():
    """Test creating a SearchResultFood from API data."""
    data = {
        "fdcId": 1234,
        "description": "Test Food",
        "dataType": "Branded",
        "publicationDate": "2021-10-28",
        "foodCategory": "Test Category",
        "brandOwner": "Test Brand Owner",
        "brandName": "Test Brand"
    }
    
    food = SearchResultFood.from_api_data(data)
    
    assert food.fdc_id == 1234
    assert food.description == "Test Food"
    assert food.data_type == "Branded"
    assert food.publication_date == "2021-10-28"
    assert food.food_category == "Test Category"
    assert food.brand_owner == "Test Brand Owner"
    assert food.brand_name == "Test Brand"


def test_search_result_init(sample_search_result):
    """Test initializing a SearchResult object."""
    assert sample_search_result.total_hits == 2
    assert sample_search_result.current_page == 1
    assert sample_search_result.total_pages == 1
    assert len(sample_search_result.foods) == 2


def test_search_result_from_api_data(sample_search_result_data):
    """Test creating a SearchResult from API data."""
    result = SearchResult.from_api_data(sample_search_result_data)
    
    assert result.total_hits == sample_search_result_data["totalHits"]
    assert result.current_page == sample_search_result_data["currentPage"]
    assert result.total_pages == sample_search_result_data["totalPages"]
    assert len(result.foods) == len(sample_search_result_data["foods"])
    assert result.foods[0].fdc_id == sample_search_result_data["foods"][0]["fdcId"]
    assert result.foods[0].description == sample_search_result_data["foods"][0]["description"]