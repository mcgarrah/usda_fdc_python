"""
Nutrient analysis module.

This module provides tools for analyzing nutrient content, comparing to dietary
reference intakes, and calculating nutritional information.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Tuple

from ..client import FdcClient
from ..models import Food, Nutrient as FdcNutrient
from .nutrients import Nutrient, NUTRIENTS, get_nutrient_by_usda_id, get_nutrient_by_name
from .dri import DietaryReferenceIntakes, DriType, Gender, get_dri
from .units import convert_to_grams, convert_from_grams, format_amount


@dataclass
class NutrientValue:
    """
    Represents a nutrient value with its properties.
    
    Attributes:
        nutrient: The nutrient.
        amount: The amount of the nutrient.
        unit: The unit of the amount.
        dri_percent: The percentage of the DRI (if available).
    """
    
    nutrient: Nutrient
    amount: float
    unit: str
    dri_percent: Optional[float] = None


@dataclass
class NutrientAnalysis:
    """
    Represents the nutrient analysis of a food.
    
    Attributes:
        food: The food being analyzed.
        nutrients: The nutrient values.
        dri_type: The type of DRI used for comparison.
        gender: The gender used for DRI comparison.
        serving_size: The serving size in grams.
        calories_per_serving: The calories per serving.
        macronutrient_distribution: The distribution of macronutrients.
    """
    
    food: Food
    nutrients: Dict[str, NutrientValue] = field(default_factory=dict)
    dri_type: DriType = DriType.RDA
    gender: Gender = Gender.MALE
    serving_size: float = 100.0
    calories_per_serving: float = 0.0
    macronutrient_distribution: Dict[str, float] = field(default_factory=dict)
    
    def get_nutrient(self, nutrient_id: str) -> Optional[NutrientValue]:
        """
        Get a nutrient value by ID.
        
        Args:
            nutrient_id: The nutrient ID.
            
        Returns:
            The nutrient value if available, None otherwise.
        """
        return self.nutrients.get(nutrient_id)
    
    def get_nutrients_by_group(self, group: str) -> Dict[str, NutrientValue]:
        """
        Get nutrient values by group.
        
        Args:
            group: The nutrient group.
            
        Returns:
            A dictionary of nutrient IDs to nutrient values.
        """
        return {
            nutrient_id: value
            for nutrient_id, value in self.nutrients.items()
            if value.nutrient.group == group
        }
    
    def get_macronutrients(self) -> Dict[str, NutrientValue]:
        """
        Get macronutrient values.
        
        Returns:
            A dictionary of nutrient IDs to nutrient values.
        """
        return self.get_nutrients_by_group("macronutrient")
    
    def get_vitamins(self) -> Dict[str, NutrientValue]:
        """
        Get vitamin values.
        
        Returns:
            A dictionary of nutrient IDs to nutrient values.
        """
        return self.get_nutrients_by_group("vitamin")
    
    def get_minerals(self) -> Dict[str, NutrientValue]:
        """
        Get mineral values.
        
        Returns:
            A dictionary of nutrient IDs to nutrient values.
        """
        return self.get_nutrients_by_group("mineral")
    
    def get_amino_acids(self) -> Dict[str, NutrientValue]:
        """
        Get amino acid values.
        
        Returns:
            A dictionary of nutrient IDs to nutrient values.
        """
        return self.get_nutrients_by_group("amino_acid")
    
    def get_nutrient_density(self, nutrient_id: str) -> Optional[float]:
        """
        Get the nutrient density (amount per calorie).
        
        Args:
            nutrient_id: The nutrient ID.
            
        Returns:
            The nutrient density if available, None otherwise.
        """
        nutrient_value = self.get_nutrient(nutrient_id)
        if nutrient_value and self.calories_per_serving > 0:
            return nutrient_value.amount / self.calories_per_serving
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the analysis to a dictionary.
        
        Returns:
            A dictionary representation of the analysis.
        """
        return {
            "food": {
                "fdc_id": self.food.fdc_id,
                "description": self.food.description,
                "data_type": self.food.data_type
            },
            "serving_size": self.serving_size,
            "calories_per_serving": self.calories_per_serving,
            "macronutrient_distribution": self.macronutrient_distribution,
            "nutrients": {
                nutrient_id: {
                    "name": value.nutrient.display_name,
                    "amount": value.amount,
                    "unit": value.unit,
                    "dri_percent": value.dri_percent
                }
                for nutrient_id, value in self.nutrients.items()
            }
        }


def analyze_food(
    food: Food,
    dri_type: DriType = DriType.RDA,
    gender: Gender = Gender.MALE,
    serving_size: float = 100.0
) -> NutrientAnalysis:
    """
    Analyze the nutrient content of a food.
    
    Args:
        food: The food to analyze.
        dri_type: The type of DRI to use for comparison.
        gender: The gender to use for DRI comparison.
        serving_size: The serving size in grams.
        
    Returns:
        A NutrientAnalysis object.
    """
    # Create the analysis object
    analysis = NutrientAnalysis(
        food=food,
        dri_type=dri_type,
        gender=gender,
        serving_size=serving_size
    )
    
    # Get the DRI data
    dri = DietaryReferenceIntakes(dri_type, gender)
    
    # Process each nutrient
    for fdc_nutrient in food.nutrients:
        # Try to map the FDC nutrient to our nutrient definitions
        nutrient = get_nutrient_by_usda_id(fdc_nutrient.id)
        if not nutrient:
            # Try by name
            nutrient = get_nutrient_by_name(fdc_nutrient.name)
        
        if nutrient:
            # Calculate the amount for the serving size
            amount = fdc_nutrient.amount * (serving_size / 100.0)
            
            # Get the DRI value and calculate the percentage
            dri_value = dri.get_dri(nutrient.id)
            dri_percent = None
            if dri_value is not None and dri_value > 0:
                # Convert the amount to the same unit as the DRI
                amount_in_grams = convert_to_grams(amount, fdc_nutrient.unit_name)
                dri_percent = (amount_in_grams / dri_value) * 100.0
            
            # Add the nutrient value to the analysis
            analysis.nutrients[nutrient.id] = NutrientValue(
                nutrient=nutrient,
                amount=amount,
                unit=fdc_nutrient.unit_name,
                dri_percent=dri_percent
            )
            
            # Track calories
            if nutrient.id == "energy":
                analysis.calories_per_serving = amount
    
    # Calculate macronutrient distribution
    total_calories = analysis.calories_per_serving
    if total_calories > 0:
        # Get macronutrient values
        protein_value = analysis.get_nutrient("protein")
        fat_value = analysis.get_nutrient("fat")
        carb_value = analysis.get_nutrient("carbohydrate")
        
        # Calculate calories from each macronutrient
        protein_calories = protein_value.amount * 4 if protein_value else 0
        fat_calories = fat_value.amount * 9 if fat_value else 0
        carb_calories = carb_value.amount * 4 if carb_value else 0
        
        # Calculate percentages
        analysis.macronutrient_distribution = {
            "protein": (protein_calories / total_calories) * 100 if protein_calories > 0 else 0,
            "fat": (fat_calories / total_calories) * 100 if fat_calories > 0 else 0,
            "carbohydrate": (carb_calories / total_calories) * 100 if carb_calories > 0 else 0
        }
    
    return analysis


def analyze_foods(
    foods: List[Food],
    dri_type: DriType = DriType.RDA,
    gender: Gender = Gender.MALE,
    serving_sizes: Optional[List[float]] = None
) -> List[NutrientAnalysis]:
    """
    Analyze the nutrient content of multiple foods.
    
    Args:
        foods: The foods to analyze.
        dri_type: The type of DRI to use for comparison.
        gender: The gender to use for DRI comparison.
        serving_sizes: The serving sizes in grams (one per food).
        
    Returns:
        A list of NutrientAnalysis objects.
    """
    # Use default serving size if not provided
    if serving_sizes is None:
        serving_sizes = [100.0] * len(foods)
    
    # Ensure serving_sizes has the same length as foods
    if len(serving_sizes) != len(foods):
        serving_sizes = serving_sizes[:len(foods)]
        serving_sizes.extend([100.0] * (len(foods) - len(serving_sizes)))
    
    # Analyze each food
    return [
        analyze_food(food, dri_type, gender, serving_size)
        for food, serving_size in zip(foods, serving_sizes)
    ]


def compare_foods(
    foods: List[Food],
    nutrient_ids: Optional[List[str]] = None,
    serving_sizes: Optional[List[float]] = None
) -> Dict[str, List[Tuple[str, float, str]]]:
    """
    Compare the nutrient content of multiple foods.
    
    Args:
        foods: The foods to compare.
        nutrient_ids: The nutrient IDs to compare (all if None).
        serving_sizes: The serving sizes in grams (one per food).
        
    Returns:
        A dictionary mapping nutrient IDs to lists of (food description, amount, unit) tuples.
    """
    # Analyze the foods
    analyses = analyze_foods(foods, serving_sizes=serving_sizes)
    
    # Determine which nutrients to compare
    if nutrient_ids is None:
        # Get all nutrients present in any of the foods
        nutrient_ids = set()
        for analysis in analyses:
            nutrient_ids.update(analysis.nutrients.keys())
        nutrient_ids = sorted(nutrient_ids)
    
    # Compare the nutrients
    comparison = {}
    for nutrient_id in nutrient_ids:
        comparison[nutrient_id] = []
        for analysis in analyses:
            nutrient_value = analysis.get_nutrient(nutrient_id)
            if nutrient_value:
                comparison[nutrient_id].append(
                    (analysis.food.description, nutrient_value.amount, nutrient_value.unit)
                )
    
    return comparison