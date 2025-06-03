"""Pytest configuration for the USDA FDC Python Client tests."""

import os
import pytest
from unittest.mock import MagicMock

from usda_fdc import FdcClient
from usda_fdc.models import Food, Nutrient, FoodPortion, SearchResult, SearchResultFood


@pytest.fixture
def api_key():
    """Return a test API key."""
    return "test_api_key"


@pytest.fixture
def mock_client(api_key):
    """Return a mock FDC client."""
    client = FdcClient(api_key)
    client._make_request = MagicMock()
    return client


@pytest.fixture
def sample_food_data():
    """Return sample food data."""
    return {
        "fdcId": 1234,
        "description": "Test Food",
        "dataType": "Branded",
        "publicationDate": "2021-10-28",
        "foodClass": "Test Class",
        "foodCategory": "Test Category",
        "scientificName": "Test Scientific Name",
        "brandOwner": "Test Brand Owner",
        "brandName": "Test Brand",
        "ingredients": "Test Ingredients",
        "servingSize": 100,
        "servingSizeUnit": "g",
        "householdServingFullText": "1 serving",
        "foodNutrients": [
            {
                "nutrient": {
                    "id": 1003,
                    "name": "Protein",
                    "unitName": "g",
                    "number": "203",
                    "rank": 600
                },
                "amount": 10.5
            },
            {
                "nutrient": {
                    "id": 1004,
                    "name": "Total lipid (fat)",
                    "unitName": "g",
                    "number": "204",
                    "rank": 800
                },
                "amount": 5.2
            }
        ],
        "foodPortions": [
            {
                "id": 9876,
                "amount": 1,
                "gramWeight": 100,
                "portionDescription": "serving",
                "modifier": "about",
                "measureUnit": {
                    "name": "serving"
                }
            }
        ]
    }


@pytest.fixture
def sample_food(sample_food_data):
    """Return a sample Food object."""
    nutrients = [
        Nutrient(
            id=n["nutrient"]["id"],
            name=n["nutrient"]["name"],
            amount=n["amount"],
            unit_name=n["nutrient"]["unitName"],
            nutrient_nbr=n["nutrient"]["number"],
            rank=n["nutrient"]["rank"]
        )
        for n in sample_food_data["foodNutrients"]
    ]
    
    food_portions = [
        FoodPortion(
            id=p["id"],
            amount=p["amount"],
            gram_weight=p["gramWeight"],
            portion_description=p["portionDescription"],
            modifier=p["modifier"],
            measure_unit=p["measureUnit"]["name"]
        )
        for p in sample_food_data["foodPortions"]
    ]
    
    return Food(
        fdc_id=sample_food_data["fdcId"],
        description=sample_food_data["description"],
        data_type=sample_food_data["dataType"],
        publication_date=sample_food_data["publicationDate"],
        food_class=sample_food_data["foodClass"],
        food_category=sample_food_data["foodCategory"],
        scientific_name=sample_food_data["scientificName"],
        brand_owner=sample_food_data["brandOwner"],
        brand_name=sample_food_data["brandName"],
        ingredients=sample_food_data["ingredients"],
        serving_size=sample_food_data["servingSize"],
        serving_size_unit=sample_food_data["servingSizeUnit"],
        household_serving_fulltext=sample_food_data["householdServingFullText"],
        nutrients=nutrients,
        food_portions=food_portions
    )


@pytest.fixture
def sample_search_result_data():
    """Return sample search result data."""
    return {
        "totalHits": 2,
        "currentPage": 1,
        "totalPages": 1,
        "foods": [
            {
                "fdcId": 1234,
                "description": "Test Food 1",
                "dataType": "Branded",
                "publicationDate": "2021-10-28",
                "foodCategory": "Test Category",
                "brandOwner": "Test Brand Owner",
                "brandName": "Test Brand"
            },
            {
                "fdcId": 5678,
                "description": "Test Food 2",
                "dataType": "Foundation",
                "publicationDate": "2021-10-28",
                "foodCategory": "Test Category 2"
            }
        ]
    }


@pytest.fixture
def sample_search_result(sample_search_result_data):
    """Return a sample SearchResult object."""
    foods = [
        SearchResultFood(
            fdc_id=f["fdcId"],
            description=f["description"],
            data_type=f["dataType"],
            publication_date=f["publicationDate"],
            food_category=f["foodCategory"],
            brand_owner=f.get("brandOwner"),
            brand_name=f.get("brandName")
        )
        for f in sample_search_result_data["foods"]
    ]
    
    return SearchResult(
        foods=foods,
        total_hits=sample_search_result_data["totalHits"],
        current_page=sample_search_result_data["currentPage"],
        total_pages=sample_search_result_data["totalPages"]
    )


@pytest.fixture
def real_api_key():
    """Return the real API key from environment variable."""
    return os.environ.get("FDC_API_KEY")


@pytest.fixture
def real_client(real_api_key):
    """Return a real FDC client if API key is available."""
    if not real_api_key:
        pytest.skip("FDC_API_KEY environment variable not set")
    return FdcClient(real_api_key)