"""
Unit tests for the utils module.
"""

import pytest

from usda_fdc.utils import (
    parse_unit_and_value,
    convert_to_grams,
    convert_to_milliliters,
    convert_measurement,
    normalize_nutrient_value
)

def test_parse_unit_and_value():
    """Test parse_unit_and_value function."""
    # Test with space between value and unit
    value, unit = parse_unit_and_value("100 g")
    assert value == 100.0
    assert unit == "g"
    
    # Test without space
    value, unit = parse_unit_and_value("100g")
    assert value == 100.0
    assert unit == "g"
    
    # Test with decimal
    value, unit = parse_unit_and_value("1.5 cups")
    assert value == 1.5
    assert unit == "cups"
    
    # Test with fraction
    value, unit = parse_unit_and_value("1/2 cup")
    assert value == 0.5
    assert unit == "cup"
    
    # Test with invalid format
    with pytest.raises(ValueError):
        parse_unit_and_value("invalid")

def test_convert_to_grams():
    """Test convert_to_grams function."""
    # Test with grams
    assert convert_to_grams(100.0, "g") == 100.0
    
    # Test with kilograms
    assert convert_to_grams(1.0, "kg") == 1000.0
    
    # Test with ounces
    assert round(convert_to_grams(1.0, "oz"), 1) == 28.3
    
    # Test with pounds
    assert round(convert_to_grams(1.0, "lb"), 1) == 453.6
    
    # Test with invalid unit
    with pytest.raises(ValueError):
        convert_to_grams(1.0, "invalid")

def test_convert_to_milliliters():
    """Test convert_to_milliliters function."""
    # Test with milliliters
    assert convert_to_milliliters(100.0, "ml") == 100.0
    
    # Test with liters
    assert pytest.approx(convert_to_milliliters(1.0, "l")) == 1000.0
    
    # Test with cups
    assert round(convert_to_milliliters(1.0, "cup"), 1) == 236.6
    
    # Test with tablespoons
    assert round(convert_to_milliliters(1.0, "tbsp"), 1) == 14.8
    
    # Test with invalid unit
    with pytest.raises(ValueError):
        convert_to_milliliters(1.0, "invalid")

def test_convert_measurement():
    """Test convert_measurement function."""
    # Test with same units
    assert convert_measurement(100.0, "g", "g") == 100.0
    
    # Test with different units
    assert convert_measurement(1.0, "kg", "g") == 1000.0
    assert pytest.approx(convert_measurement(1000.0, "g", "kg")) == 1.0
    
    # Test with incompatible units
    with pytest.raises(ValueError):
        convert_measurement(1.0, "g", "ml")

def test_normalize_nutrient_value():
    """Test normalize_nutrient_value function."""
    # Test with same units
    value, unit = normalize_nutrient_value(100.0, "g", "g")
    assert value == 100.0
    assert unit == "g"
    
    # Test with convertible units
    value, unit = normalize_nutrient_value(1000.0, "mg", "g")
    assert value == 1.0
    assert unit == "g"
    
    # Test with uppercase units
    value, unit = normalize_nutrient_value(100.0, "G", "g")
    assert value == 100.0
    assert unit == "g"
    
    # Test with non-convertible units
    value, unit = normalize_nutrient_value(100.0, "IU", "g")
    assert value == 100.0
    assert unit == "IU"