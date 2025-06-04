"""
Recipe analysis functionality.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple

from ..client import FdcClient
from ..models import Food, Nutrient
from .analysis import analyze_food, NutrientAnalysis
from .dri import DriType, Gender

@dataclass
class Ingredient:
    """
    Represents an ingredient in a recipe.
    """
    food: Food
    weight_g: float
    description: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the ingredient."""
        if self.description:
            return f"{self.description} ({self.weight_g}g)"
        return f"{self.food.description} ({self.weight_g}g)"

@dataclass
class Recipe:
    """
    Represents a recipe with ingredients.
    """
    name: str
    ingredients: List[Ingredient]
    servings: int = 1
    description: Optional[str] = None
    
    @property
    def total_weight_g(self) -> float:
        """Get the total weight of the recipe in grams."""
        return sum(ingredient.weight_g for ingredient in self.ingredients)
    
    def get_weight_per_serving(self) -> float:
        """Get the weight per serving in grams."""
        return self.total_weight_g / self.servings

@dataclass
class RecipeAnalysis:
    """
    Analysis of a recipe's nutrient content.
    """
    recipe: Recipe
    per_serving_analysis: NutrientAnalysis
    ingredient_analyses: List[NutrientAnalysis]

def parse_ingredient(
    text: str,
    client: FdcClient,
    search_limit: int = 5
) -> Optional[Ingredient]:
    """
    Parse an ingredient description into an Ingredient object.
    
    Args:
        text: The ingredient description (e.g., "1 cup flour").
        client: The FDC client to use for food lookup.
        search_limit: Maximum number of search results to consider.
        
    Returns:
        An Ingredient object, or None if parsing failed.
    """
    # Extract quantity and unit if present
    quantity_pattern = r'^([\d./]+)\s*([a-zA-Z]+)?\s+(.+)$'
    match = re.match(quantity_pattern, text)
    
    if match:
        quantity_str, unit, food_name = match.groups()
        
        # Parse quantity
        try:
            if '/' in quantity_str:
                num, denom = quantity_str.split('/')
                quantity = float(num) / float(denom)
            else:
                quantity = float(quantity_str)
        except ValueError:
            quantity = 1.0
        
        # Default unit is piece/item if not specified
        unit = unit or "piece"
    else:
        # No quantity/unit found, assume it's just a food name
        quantity = 1.0
        unit = "piece"
        food_name = text
    
    # Search for the food
    search_results = client.search(food_name, page_size=search_limit)
    
    if not search_results.foods:
        return None
    
    # Use the first search result
    food_id = search_results.foods[0].fdc_id
    food = client.get_food(food_id)
    
    # Estimate weight in grams based on unit and quantity
    weight_g = estimate_weight(food, quantity, unit)
    
    return Ingredient(
        food=food,
        weight_g=weight_g,
        description=text
    )

def estimate_weight(food: Food, quantity: float, unit: str) -> float:
    """
    Estimate the weight in grams based on the food, quantity, and unit.
    
    Args:
        food: The food object.
        quantity: The quantity.
        unit: The unit of measurement.
        
    Returns:
        The estimated weight in grams.
    """
    # Check if the unit is already grams
    if unit.lower() in ["g", "gram", "grams"]:
        return quantity
    
    # Check if the unit is kilograms
    if unit.lower() in ["kg", "kilogram", "kilograms"]:
        return quantity * 1000.0
    
    # Check if the food has portions that match the unit
    for portion in food.food_portions:
        if portion.measure_unit and portion.measure_unit.lower() == unit.lower():
            return quantity * portion.gram_weight
    
    # Default weights for common units
    unit_weights = {
        "cup": 240.0,
        "cups": 240.0,
        "tbsp": 15.0,
        "tablespoon": 15.0,
        "tablespoons": 15.0,
        "tsp": 5.0,
        "teaspoon": 5.0,
        "teaspoons": 5.0,
        "oz": 28.35,
        "ounce": 28.35,
        "ounces": 28.35,
        "lb": 453.59,
        "pound": 453.59,
        "pounds": 453.59,
        "piece": 100.0,
        "pieces": 100.0,
        "item": 100.0,
        "items": 100.0,
        "slice": 30.0,
        "slices": 30.0
    }
    
    # Use default weight if available
    if unit.lower() in unit_weights:
        return quantity * unit_weights[unit.lower()]
    
    # If no match, assume 100g per unit
    return quantity * 100.0

def create_recipe(
    name: str,
    ingredient_texts: List[str],
    client: FdcClient,
    servings: int = 1,
    description: Optional[str] = None
) -> Recipe:
    """
    Create a recipe from ingredient descriptions.
    
    Args:
        name: The name of the recipe.
        ingredient_texts: List of ingredient descriptions.
        client: The FDC client to use for food lookup.
        servings: The number of servings the recipe makes.
        description: Optional description of the recipe.
        
    Returns:
        A Recipe object.
    """
    ingredients = []
    
    for text in ingredient_texts:
        ingredient = parse_ingredient(text, client)
        if ingredient:
            ingredients.append(ingredient)
    
    return Recipe(
        name=name,
        ingredients=ingredients,
        servings=servings,
        description=description
    )

def analyze_recipe(
    recipe: Recipe,
    dri_type: DriType = DriType.RDA,
    gender: Gender = Gender.MALE,
    age: int = 30
) -> RecipeAnalysis:
    """
    Analyze the nutrient content of a recipe.
    
    Args:
        recipe: The recipe to analyze.
        dri_type: The type of DRI to use for comparison.
        gender: The gender to use for DRI values.
        age: The age to use for DRI values.
        
    Returns:
        A RecipeAnalysis object.
    """
    # Analyze each ingredient
    ingredient_analyses = []
    for ingredient in recipe.ingredients:
        analysis = analyze_food(
            ingredient.food,
            serving_size=ingredient.weight_g,
            dri_type=dri_type,
            gender=gender,
            age=age
        )
        ingredient_analyses.append(analysis)
    
    # Create a combined food object for the entire recipe
    combined_food = Food(
        fdc_id=0,
        description=recipe.name,
        data_type="Recipe",
        nutrients=[]
    )
    
    # Combine nutrients from all ingredients
    nutrient_map: Dict[int, Nutrient] = {}
    
    for analysis in ingredient_analyses:
        for nutrient in analysis.food.nutrients:
            if nutrient.id in nutrient_map:
                # Add to existing nutrient
                existing = nutrient_map[nutrient.id]
                existing.amount += nutrient.amount * (analysis.serving_size / 100.0)
            else:
                # Create new nutrient
                new_nutrient = Nutrient(
                    id=nutrient.id,
                    name=nutrient.name,
                    amount=nutrient.amount * (analysis.serving_size / 100.0),
                    unit_name=nutrient.unit_name,
                    nutrient_nbr=nutrient.nutrient_nbr,
                    rank=nutrient.rank
                )
                nutrient_map[nutrient.id] = new_nutrient
                combined_food.nutrients.append(new_nutrient)
    
    # Analyze the combined food per serving
    per_serving_analysis = analyze_food(
        combined_food,
        serving_size=recipe.get_weight_per_serving(),
        dri_type=dri_type,
        gender=gender,
        age=age
    )
    
    return RecipeAnalysis(
        recipe=recipe,
        per_serving_analysis=per_serving_analysis,
        ingredient_analyses=ingredient_analyses
    )