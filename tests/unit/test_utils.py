"""Tests for the utility functions."""

import pytest
from pint import UndefinedUnitError, DimensionalityError

from usda_fdc.utils import (
    parse_unit_and_value,
    convert_to_grams,
    convert_to_milliliters,
    convert_measurement,
    normalize_nutrient_value
)


def test_parse_unit_and_value():
    """Test parsing a unit and value from a string."""
    # Test simple cases
    assert parse_unit_and_value("100g") == (100, "g")
    assert parse_unit_and_value("100 g") == (100, "g")
    assert parse_unit_and_value("1.5cups") == (1.5, "cups")
    assert parse_unit_and_value("1.5 cups") == (1.5, "cups")
    
    # Test fractions
    assert parse_unit_and_value("1/2 cup") == (0.5, "cup")
    assert parse_unit_and_value("1/4tsp") == (0.25, "tsp")
    
    # Test invalid format
    with pytest.raises(ValueError):
        parse_unit_and_value("invalid")


def test_convert_to_grams():
    """Test converting measurements to grams."""
    # Test weight conversions
    assert convert_to_grams(1, "g") == 1
    assert convert_to_grams(1, "kg") == 1000
    assert convert_to_grams(1, "oz") == pytest.approx(28.3495)
    assert convert_to_grams(1, "lb") == pytest.approx(453.592)
    
    # Test invalid conversions
    with pytest.raises(ValueError):
        convert_to_grams(1, "ml")
    
    with pytest.raises(ValueError):
        convert_to_grams(1, "invalid")


def test_convert_to_milliliters():
    """Test converting measurements to milliliters."""
    # Test volume conversions
    assert convert_to_milliliters(1, "ml") == 1
    assert convert_to_milliliters(1, "l") == 1000
    assert convert_to_milliliters(1, "cup") == pytest.approx(236.588)
    assert convert_to_milliliters(1, "tbsp") == pytest.approx(14.7868)
    assert convert_to_milliliters(1, "tsp") == pytest.approx(4.92892)
    
    # Test invalid conversions
    with pytest.raises(ValueError):
        convert_to_milliliters(1, "g")
    
    with pytest.raises(ValueError):
        convert_to_milliliters(1, "invalid")


def test_convert_measurement():
    """Test converting between different units."""
    # Test weight conversions
    assert convert_measurement(1, "g", "mg") == 1000
    assert convert_measurement(1, "kg", "g") == 1000
    assert convert_measurement(1, "oz", "g") == pytest.approx(28.3495)
    
    # Test volume conversions
    assert convert_measurement(1, "l", "ml") == 1000
    assert convert_measurement(1, "cup", "ml") == pytest.approx(236.588)
    assert convert_measurement(1, "tbsp", "tsp") == 3
    
    # Test invalid conversions
    with pytest.raises(ValueError):
        convert_measurement(1, "g", "ml")
    
    with pytest.raises(ValueError):
        convert_measurement(1, "invalid", "g")


def test_normalize_nutrient_value():
    """Test normalizing nutrient values to standard units."""
    # Test normalization to same unit
    assert normalize_nutrient_value(10, "g", "g") == (10, "g")
    
    # Test normalization to different unit
    assert normalize_nutrient_value(1000, "mg", "g") == (1, "g")
    
    # Test normalization with unit mapping
    assert normalize_nutrient_value(10, "G", "g") == (10, "g")
    assert normalize_nutrient_value(1000, "MG", "g") == (1, "g")
    
    # Test normalization with incompatible units
    assert normalize_nutrient_value(10, "IU", "g") == (10, "iu")
    
    # Test normalization with invalid target unit
    assert normalize_nutrient_value(10, "g", "invalid") == (10, "g")