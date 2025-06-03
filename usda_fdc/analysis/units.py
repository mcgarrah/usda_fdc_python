"""
Unit conversion utilities for nutrient analysis.

This module provides classes and functions for converting between different units
used in nutrient data. All nutrient amounts are internally stored in grams.
"""

from enum import Enum
from typing import Dict, Union, Optional


class Unit:
    """
    Represents a unit of measurement for nutrients.
    
    Attributes:
        name: The full name of the unit.
        symbol: The symbol used for the unit.
        conversion_factor: The factor to convert from this unit to grams.
    """
    
    def __init__(self, name: str, symbol: str, conversion_factor: float):
        """
        Initialize a Unit.
        
        Args:
            name: The full name of the unit.
            symbol: The symbol used for the unit.
            conversion_factor: The factor to convert from this unit to grams.
        """
        self.name = name
        self.symbol = symbol
        self.conversion_factor = conversion_factor
    
    def __str__(self) -> str:
        """Return the string representation of the unit."""
        return self.symbol
    
    def __repr__(self) -> str:
        """Return the string representation of the unit."""
        return f"Unit(name='{self.name}', symbol='{self.symbol}', conversion_factor={self.conversion_factor})"


# Define common units
UNIT_KILOCALORIE = Unit("kilocalorie", "kcal", 1.0)  # Energy unit
UNIT_GRAM = Unit("gram", "g", 1.0)
UNIT_MILLIGRAM = Unit("milligram", "mg", 0.001)
UNIT_MICROGRAM = Unit("microgram", "µg", 0.000001)
UNIT_IU = Unit("international unit", "IU", 0.0)  # Conversion depends on the nutrient


class UnitType(Enum):
    """Enumeration of unit types."""
    MASS = "mass"
    VOLUME = "volume"
    ENERGY = "energy"
    IU = "international unit"


# Map of unit symbols to Unit objects
UNITS: Dict[str, Unit] = {
    "kcal": UNIT_KILOCALORIE,
    "g": UNIT_GRAM,
    "mg": UNIT_MILLIGRAM,
    "µg": UNIT_MICROGRAM,
    "mcg": UNIT_MICROGRAM,  # Alternative symbol for microgram
    "IU": UNIT_IU
}


def convert_to_grams(amount: float, unit: str) -> float:
    """
    Convert an amount from the specified unit to grams.
    
    Args:
        amount: The amount to convert.
        unit: The unit to convert from.
        
    Returns:
        The amount in grams.
        
    Raises:
        ValueError: If the unit is unknown.
    """
    if unit in UNITS:
        return amount * UNITS[unit].conversion_factor
    else:
        raise ValueError(f"Unknown unit: {unit}")


def convert_from_grams(amount: float, unit: str) -> float:
    """
    Convert an amount from grams to the specified unit.
    
    Args:
        amount: The amount in grams.
        unit: The unit to convert to.
        
    Returns:
        The converted amount.
        
    Raises:
        ValueError: If the unit is unknown.
    """
    if unit in UNITS:
        return amount / UNITS[unit].conversion_factor
    else:
        raise ValueError(f"Unknown unit: {unit}")


def format_amount(amount: float, unit: str, precision: int = 2) -> str:
    """
    Format an amount with its unit.
    
    Args:
        amount: The amount to format.
        unit: The unit symbol.
        precision: The number of decimal places to include.
        
    Returns:
        A formatted string with the amount and unit.
    """
    if unit == "µg":
        # Special case for micrograms to ensure proper display
        return f"{amount:.{precision}f} µg"
    else:
        return f"{amount:.{precision}f} {unit}"