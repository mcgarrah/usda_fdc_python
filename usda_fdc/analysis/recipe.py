"""
Recipe analysis module.

This module provides tools for analyzing recipes, including ingredient parsing,
nutrient calculation, and recipe comparison.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Tuple
import re

from ..client import FdcClient
from ..models import Food
from .analysis import NutrientAnalysis, analyze_food
from .dri import DriType, Gender


@dataclass
class Ingredient:
    """
    Represents a recipe ingredient.
    
    Attributes:
        food: The food.
        amount: The amount of the ingredient.
        unit: The unit of the amount.
        weight_g: The weight in grams.
    """
    
    food: Food
    amount: float
    unit: str
    weight_g: float


@dataclass
class Recipe:
    """
    Represents a recipe with ingredients.
    
    Attributes:
        name: The name of the recipe.
        ingredients: The ingredients in the recipe.
        servings: The number of servings the recipe makes.
        instructions: The recipe instructions.
        total_weight_g: The total weight of the recipe in grams.
    """
    
    name: str
    ingredients: List[Ingredient] = field(default_factory=list)
    servings: int = 1
    instructions: Optional[str] = None
    total_weight_g: float = 0.0
    
    def add_ingredient(self, ingredient: Ingredient) -> None:
        """
        Add an ingredient to the recipe.
        
        Args:
            ingredient: The ingredient to add.
        """
        self.ingredients.append(ingredient)
        self.total_weight_g += ingredient.weight_g
    
    def get_weight_per_serving(self) -> float:
        """
        Get the weight per serving in grams.
        
        Returns:
            The weight per serving.
        """
        if self.servings > 0:
            return self.total_weight_g / self.servings
        return 0.0


@dataclass
class RecipeAnalysis:
    """
    Represents the nutrient analysis of a recipe.
    
    Attributes:
        recipe: The recipe being analyzed.
        total_analysis: The nutrient analysis of the entire recipe.
        per_serving_analysis: The nutrient analysis per serving.
        ingredient_analyses: The nutrient analyses of each ingredient.
    """
    
    recipe: Recipe
    total_analysis: NutrientAnalysis
    per_serving_analysis: NutrientAnalysis
    ingredient_analyses: List[NutrientAnalysis] = field(default_factory=list)


def parse_ingredient(
    text: str,
    client: FdcClient,
    default_unit: str = "g"
) -> Optional[Ingredient]:
    """
    Parse an ingredient from text.
    
    Args:
        text: The ingredient text.
        client: The FDC client.
        default_unit: The default unit to use if not specified.
        
    Returns:
        An Ingredient object if parsing succeeds, None otherwise.
    """
    # Regular expression to match amount, unit, and food
    pattern = r"^([\d.\/]+)\s*([a-zA-Z]+)?\s+(.+)$"
    match = re.match(pattern, text.strip())
    
    if not match:
        return None
    
    # Extract amount, unit, and food name
    amount_str, unit, food_name = match.groups()
    
    # Parse amount (handle fractions)
    if "/" in amount_str:
        num, denom = amount_str.split("/")
        amount = float(num) / float(denom)
    else:
        amount = float(amount_str)
    
    # Use default unit if not specified
    if unit is None:
        unit = default_unit
    
    # Search for the food
    search_results = client.search(food_name, page_size=1)
    if not search_results.foods:
        return None
    
    # Get the food details
    food = client.get_food(search_results.foods[0].fdc_id)
    
    # Calculate weight in grams
    weight_g = 0.0
    
    # Try to find a matching portion
    for portion in food.food_portions:
        if portion.measure_unit and portion.measure_unit.lower() == unit.lower():
            weight_g = portion.gram_weight * amount
            break
    
    # If no matching portion, assume the unit is grams
    if weight_g == 0.0:
        if unit.lower() in ["g", "gram", "grams"]:
            weight_g = amount
        elif unit.lower() in ["kg", "kilogram", "kilograms"]:
            weight_g = amount * 1000
        elif unit.lower() in ["oz", "ounce", "ounces"]:
            weight_g = amount * 28.35
        elif unit.lower() in ["lb", "pound", "pounds"]:
            weight_g = amount * 453.59
        else:
            # Default to 100g per unit if no conversion is available
            weight_g = amount * 100
    
    return Ingredient(food=food, amount=amount, unit=unit, weight_g=weight_g)


def create_recipe(
    name: str,
    ingredient_texts: List[str],
    client: FdcClient,
    servings: int = 1,
    instructions: Optional[str] = None
) -> Recipe:
    """
    Create a recipe from ingredient texts.
    
    Args:
        name: The name of the recipe.
        ingredient_texts: The ingredient texts.
        client: The FDC client.
        servings: The number of servings the recipe makes.
        instructions: The recipe instructions.
        
    Returns:
        A Recipe object.
    """
    recipe = Recipe(name=name, servings=servings, instructions=instructions)
    
    for text in ingredient_texts:
        ingredient = parse_ingredient(text, client)
        if ingredient:
            recipe.add_ingredient(ingredient)
    
    return recipe


def analyze_recipe(
    recipe: Recipe,
    dri_type: DriType = DriType.RDA,
    gender: Gender = Gender.MALE
) -> RecipeAnalysis:
    """
    Analyze the nutrient content of a recipe.
    
    Args:
        recipe: The recipe to analyze.
        dri_type: The type of DRI to use for comparison.
        gender: The gender to use for DRI comparison.
        
    Returns:
        A RecipeAnalysis object.
    """
    # Create a combined food for the entire recipe
    combined_food = Food(
        fdc_id=0,
        description=recipe.name,
        data_type="Recipe",
        nutrients=[],
        food_portions=[]
    )
    
    # Analyze each ingredient
    ingredient_analyses = []
    for ingredient in recipe.ingredients:
        # Analyze the ingredient
        analysis = analyze_food(
            ingredient.food,
            dri_type=dri_type,
            gender=gender,
            serving_size=ingredient.weight_g
        )
        ingredient_analyses.append(analysis)
        
        # Add the ingredient's nutrients to the combined food
        for nutrient_id, nutrient_value in analysis.nutrients.items():
            # Find or create the nutrient in the combined food
            found = False
            for combined_nutrient in combined_food.nutrients:
                if combined_nutrient.id == nutrient_value.nutrient.usda_id:
                    # Add the amount
                    combined_nutrient.amount += nutrient_value.amount
                    found = True
                    break
            
            if not found and nutrient_value.nutrient.usda_id:
                # Create a new nutrient
                from ..models import Nutrient as FdcNutrient
                combined_food.nutrients.append(FdcNutrient(
                    id=nutrient_value.nutrient.usda_id,
                    name=nutrient_value.nutrient.display_name,
                    amount=nutrient_value.amount,
                    unit_name=nutrient_value.unit
                ))
    
    # Analyze the combined food for the total recipe
    total_analysis = analyze_food(
        combined_food,
        dri_type=dri_type,
        gender=gender,
        serving_size=recipe.total_weight_g
    )
    
    # Create a per-serving analysis
    per_serving_food = Food(
        fdc_id=0,
        description=f"{recipe.name} (per serving)",
        data_type="Recipe",
        nutrients=[]
    )
    
    # Add nutrients to the per-serving food
    for nutrient in combined_food.nutrients:
        from ..models import Nutrient as FdcNutrient
        per_serving_food.nutrients.append(FdcNutrient(
            id=nutrient.id,
            name=nutrient.name,
            amount=nutrient.amount / recipe.servings if recipe.servings > 0 else 0,
            unit_name=nutrient.unit_name
        ))
    
    # Analyze the per-serving food
    per_serving_analysis = analyze_food(
        per_serving_food,
        dri_type=dri_type,
        gender=gender,
        serving_size=recipe.get_weight_per_serving()
    )
    
    return RecipeAnalysis(
        recipe=recipe,
        total_analysis=total_analysis,
        per_serving_analysis=per_serving_analysis,
        ingredient_analyses=ingredient_analyses
    )