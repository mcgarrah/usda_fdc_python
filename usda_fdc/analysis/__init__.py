"""
Nutrient analysis module for the USDA FDC library.

This module provides tools for analyzing nutrient content, comparing to dietary
reference intakes, and calculating nutritional information for recipes.
"""

from .nutrients import (
    Nutrient, 
    NUTRIENTS, 
    NUTRIENT_GROUPS,
    MACRONUTRIENTS,
    MINERALS,
    VITAMINS,
    AMINO_ACIDS
)
from .dri import (
    DietaryReferenceIntakes,
    get_dri,
    DRI_TYPES
)
from .analysis import (
    NutrientAnalysis,
    analyze_food,
    analyze_foods,
    compare_foods
)

__all__ = [
    'Nutrient',
    'NUTRIENTS',
    'NUTRIENT_GROUPS',
    'MACRONUTRIENTS',
    'MINERALS',
    'VITAMINS',
    'AMINO_ACIDS',
    'DietaryReferenceIntakes',
    'get_dri',
    'DRI_TYPES',
    'NutrientAnalysis',
    'analyze_food',
    'analyze_foods',
    'compare_foods'
]