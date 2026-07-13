"""
Unit tests for the models module.
"""

import pytest
from datetime import date

from usda_fdc.models import Food, Nutrient, FoodPortion, SearchResult, SearchResultFood

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

def test_food_parses_gtin_upc():
    """Branded foods carry a barcode; from_api_data must not drop it.

    FDC has no barcode-lookup endpoint, so callers looking a product up by
    barcode go through the full-text search — which returns fuzzy matches.
    Without gtin_upc there is no way to verify a hit really is the barcode
    that was asked for, and an unknown barcode silently returns an unrelated
    product's nutrition.
    """
    food = Food.from_api_data({
        "fdcId": 2117779,
        "description": "SPICY SWEET CHILI FLAVORED TORTILLA CHIPS",
        "dataType": "Branded",
        "brandOwner": "Frito-Lay",
        "gtinUpc": "028400642255",
    })

    assert food.gtin_upc == "028400642255"


def test_food_without_gtin_upc_is_none():
    """Foundation and Survey foods have no barcode."""
    food = Food.from_api_data({
        "fdcId": 1234,
        "description": "Broccoli, raw",
        "dataType": "Foundation",
    })

    assert food.gtin_upc is None


def test_search_result_food_parses_gtin_upc():
    """The search result is where the barcode check actually happens, so this
    model needs the field just as much as Food does."""
    result = SearchResultFood.from_api_data({
        "fdcId": 2117779,
        "description": "SPICY SWEET CHILI FLAVORED TORTILLA CHIPS",
        "dataType": "Branded",
        "gtinUpc": "028400642255",
    })

    assert result.gtin_upc == "028400642255"


def test_search_result_food_without_gtin_upc_is_none():
    result = SearchResultFood.from_api_data({
        "fdcId": 1234,
        "description": "Broccoli, raw",
        "dataType": "Foundation",
    })

    assert result.gtin_upc is None


# ── Abridged responses ────────────────────────────────────────────────
# FDC describes a nutrient two ways. format=full nests it under a "nutrient"
# key; format=abridged inlines the fields on the row and carries no nutrient id,
# only its number. Parsing only the nested shape meant every nutrient of an
# abridged food was silently dropped: a food with 35 nutrients came back with 0,
# and no error to say so.

ABRIDGED_NUTRIENT = {
    "number": "208",
    "name": "Energy",
    "amount": 900.0,
    "unitName": "KCAL",
    "derivationCode": "LC",
}

FULL_NUTRIENT = {
    "nutrient": {"id": 1008, "name": "Energy", "unitName": "kcal", "number": "208", "rank": 300},
    "amount": 900.0,
}


def test_nutrient_parses_the_abridged_inline_shape():
    nutrient = Nutrient.from_api_data(ABRIDGED_NUTRIENT)

    assert nutrient.name == "Energy"
    assert nutrient.amount == 900.0
    assert nutrient.unit_name == "KCAL"
    assert nutrient.nutrient_nbr == "208"


def test_nutrient_still_parses_the_full_nested_shape():
    nutrient = Nutrient.from_api_data(FULL_NUTRIENT)

    assert nutrient.id == 1008
    assert nutrient.name == "Energy"
    assert nutrient.amount == 900.0
    assert nutrient.unit_name == "kcal"


def test_abridged_food_keeps_its_nutrients():
    """The regression: a real abridged food (fdc_id 171314) has 18 nutrients and
    was parsed into a Food with none, silently. Anyone computing nutrition from
    it got zeros."""
    food = Food.from_api_data({
        "fdcId": 171314,
        "description": "Butter, Clarified butter (ghee)",
        "dataType": "SR Legacy",
        "foodNutrients": [ABRIDGED_NUTRIENT],
    })

    assert len(food.nutrients) == 1
    assert food.nutrients[0].amount == 900.0
    assert food.nutrients[0].unit_name == "KCAL"


def test_full_food_still_keeps_its_nutrients():
    food = Food.from_api_data({
        "fdcId": 171314,
        "description": "Butter, Clarified butter (ghee)",
        "dataType": "SR Legacy",
        "foodNutrients": [FULL_NUTRIENT],
    })

    assert len(food.nutrients) == 1
    assert food.nutrients[0].id == 1008
