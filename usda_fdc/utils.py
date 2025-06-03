"""
Utility functions for the USDA FDC client.
"""

import re
from typing import Dict, Any, Optional, Tuple, Union
from pint import UnitRegistry, UndefinedUnitError, DimensionalityError

# Initialize unit registry
ureg = UnitRegistry()

# Define common food measurement units
ureg.define('serving = 1 = serving')
ureg.define('cup = 236.588 * milliliter = cup')
ureg.define('tablespoon = 14.7868 * milliliter = tbsp')
ureg.define('teaspoon = 4.92892 * milliliter = tsp')
ureg.define('ounce = 28.3495 * gram = oz')
ureg.define('pound = 453.592 * gram = lb')
ureg.define('slice = 1 = slice')
ureg.define('piece = 1 = piece')


def parse_unit_and_value(measurement_str: str) -> Tuple[float, str]:
    """
    Parse a measurement string into a value and unit.
    
    Args:
        measurement_str: A string containing a measurement (e.g., "100 g", "1 cup").
        
    Returns:
        A tuple of (value, unit).
    """
    # Match patterns like "100g", "100 g", "1.5cups", "1.5 cups", "1/2 cup", etc.
    pattern = r'([\d./]+)\s*([a-zA-Z]+)'
    match = re.match(pattern, measurement_str)
    
    if not match:
        raise ValueError(f"Could not parse measurement: {measurement_str}")
    
    value_str, unit = match.groups()
    
    # Handle fractions
    if '/' in value_str:
        num, denom = value_str.split('/')
        value = float(num) / float(denom)
    else:
        value = float(value_str)
    
    return value, unit


def convert_to_grams(amount: float, unit: str) -> float:
    """
    Convert a measurement to grams.
    
    Args:
        amount: The amount to convert.
        unit: The unit to convert from.
        
    Returns:
        The equivalent amount in grams.
        
    Raises:
        ValueError: If the unit cannot be converted to grams.
    """
    try:
        # Try to convert to grams
        quantity = amount * ureg(unit)
        return quantity.to('gram').magnitude
    except (UndefinedUnitError, DimensionalityError) as e:
        raise ValueError(f"Cannot convert {unit} to grams: {str(e)}")


def convert_to_milliliters(amount: float, unit: str) -> float:
    """
    Convert a measurement to milliliters.
    
    Args:
        amount: The amount to convert.
        unit: The unit to convert from.
        
    Returns:
        The equivalent amount in milliliters.
        
    Raises:
        ValueError: If the unit cannot be converted to milliliters.
    """
    try:
        # Try to convert to milliliters
        quantity = amount * ureg(unit)
        return quantity.to('milliliter').magnitude
    except (UndefinedUnitError, DimensionalityError) as e:
        raise ValueError(f"Cannot convert {unit} to milliliters: {str(e)}")


def convert_measurement(
    amount: float, 
    from_unit: str, 
    to_unit: str
) -> float:
    """
    Convert a measurement from one unit to another.
    
    Args:
        amount: The amount to convert.
        from_unit: The unit to convert from.
        to_unit: The unit to convert to.
        
    Returns:
        The converted amount.
        
    Raises:
        ValueError: If the conversion is not possible.
    """
    try:
        quantity = amount * ureg(from_unit)
        return quantity.to(to_unit).magnitude
    except (UndefinedUnitError, DimensionalityError) as e:
        raise ValueError(f"Cannot convert {from_unit} to {to_unit}: {str(e)}")


def normalize_nutrient_value(
    value: float, 
    unit: str, 
    target_unit: str = 'g'
) -> Tuple[float, str]:
    """
    Normalize a nutrient value to a standard unit.
    
    Args:
        value: The nutrient value.
        unit: The unit of the nutrient value.
        target_unit: The target unit to normalize to.
        
    Returns:
        A tuple of (normalized_value, normalized_unit).
    """
    # Map of common unit conversions
    unit_map = {
        'G': 'g',
        'MG': 'mg',
        'UG': 'µg',
        'IU': 'IU',
        'KCAL': 'kcal',
        'KJ': 'kJ',
    }
    
    # Normalize the unit
    normalized_unit = unit_map.get(unit.upper(), unit.lower())
    
    # If the normalized unit is already the target unit, return as is
    if normalized_unit == target_unit:
        return value, normalized_unit
    
    # Try to convert the value to the target unit
    try:
        converted_value = convert_measurement(value, normalized_unit, target_unit)
        return converted_value, target_unit
    except ValueError:
        # If conversion fails, return the original value and normalized unit
        return value, normalized_unit