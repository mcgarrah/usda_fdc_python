"""
Test fixtures and configuration for the USDA FDC Python Client.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock API key for tests
@pytest.fixture
def api_key():
    return "test_api_key"

# Mock client fixture
@pytest.fixture
def mock_client():
    from usda_fdc import FdcClient
    
    with patch.object(FdcClient, '_make_request') as mock_request:
        mock_request.return_value = {"mock_data": True}
        client = FdcClient("test_api_key")
        yield client

# Mock search response
@pytest.fixture
def mock_search_response():
    return {
        "totalHits": 2,
        "currentPage": 1,
        "totalPages": 1,
        "foods": [
            {
                "fdcId": 1234,
                "description": "Test Food 1",
                "dataType": "Branded"
            },
            {
                "fdcId": 5678,
                "description": "Test Food 2",
                "dataType": "Foundation"
            }
        ]
    }

# Mock food response
@pytest.fixture
def mock_food_response():
    return {
        "fdcId": 1234,
        "description": "Test Food",
        "dataType": "Branded",
        "publicationDate": "2023-01-01",
        "foodClass": "Test Class",
        "foodCategory": {
            "description": "Test Category"
        },
        "foodNutrients": [
            {
                "nutrient": {
                    "id": 1001,
                    "name": "Protein",
                    "unitName": "g"
                },
                "amount": 10.5
            },
            {
                "nutrient": {
                    "id": 1002,
                    "name": "Fat",
                    "unitName": "g"
                },
                "amount": 5.2
            }
        ],
        "foodPortions": [
            {
                "id": 101,
                "amount": 1.0,
                "gramWeight": 100.0,
                "measureUnit": {
                    "name": "cup"
                }
            }
        ]
    }

# Mock food list for get_foods
@pytest.fixture
def mock_foods_list_response():
    return [
        {
            "fdcId": 1234,
            "description": "Test Food 1",
            "dataType": "Branded",
            "foodNutrients": [
                {
                    "nutrient": {
                        "id": 1001,
                        "name": "Protein",
                        "unitName": "g"
                    },
                    "amount": 10.5
                }
            ]
        },
        {
            "fdcId": 5678,
            "description": "Test Food 2",
            "dataType": "Foundation",
            "foodNutrients": [
                {
                    "nutrient": {
                        "id": 1002,
                        "name": "Fat",
                        "unitName": "g"
                    },
                    "amount": 5.2
                }
            ]
        }
    ]

# Mock nutrients response - this is actually a Food object with nutrients
@pytest.fixture
def mock_nutrients_response():
    return {
        "fdcId": 1234,
        "description": "Test Food",
        "dataType": "Branded",
        "foodNutrients": [
            {
                "nutrient": {
                    "id": 1001,
                    "name": "Protein",
                    "unitName": "g"
                },
                "amount": 10.5
            },
            {
                "nutrient": {
                    "id": 1002,
                    "name": "Fat",
                    "unitName": "g"
                },
                "amount": 5.2
            }
        ]
    }

# Mock list foods response
@pytest.fixture
def mock_list_foods_response():
    return [
        {
            "fdcId": 1234,
            "description": "Test Food 1",
            "dataType": "Branded"
        },
        {
            "fdcId": 5678,
            "description": "Test Food 2",
            "dataType": "Foundation"
        }
    ]