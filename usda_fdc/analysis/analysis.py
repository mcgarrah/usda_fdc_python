"""
Food nutrient analysis functionality.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple

from ..models import Food, Nutrient
from .dri import DriType, Gender, get_dri

@dataclass
class NutrientValue:
    """
    Represents a nutrient value with additional analysis information.
    """
    nutrient: Nutrient
    amount: float
    unit: str
    dri: Optional[float] = None
    dri_percent: Optional[float] = None
    dri_type: Optional[DriType] = None

@dataclass
class NutrientAnalysis:
    """
    Analysis of a food's nutrient content.
    """
    food: Food
    serving_size: float  # in grams
    nutrients: Dict[str, NutrientValue] = field(default_factory=dict)
    calories_per_serving: float = 0.0
    protein_per_serving: float = 0.0
    carbs_per_serving: float = 0.0
    fat_per_serving: float = 0.0
    macronutrient_distribution: Dict[str, float] = field(default_factory=dict)
    
    def get_nutrient(self, nutrient_id: str) -> Optional[NutrientValue]:
        """
        Get a nutrient value by ID.
        
        Args:
            nutrient_id: The nutrient ID or name.
            
        Returns:
            The nutrient value, or None if not found.
        """
        return self.nutrients.get(nutrient_id.lower())

def _get_nutrient_id(nutrient: Nutrient) -> str:
    """
    Get a standardized nutrient ID from a nutrient.
    
    Args:
        nutrient: The nutrient object.
        
    Returns:
        A standardized nutrient ID.
    """
    # Map common nutrient names to standardized IDs
    name_map = {
        "protein": "protein",
        "total lipid (fat)": "fat",
        "fatty acids, total saturated": "saturated_fat",
        "carbohydrate, by difference": "carbs",
        "fiber, total dietary": "fiber",
        "sugars, total including nlea": "sugar",
        "calcium, ca": "calcium",
        "iron, fe": "iron",
        "sodium, na": "sodium",
        "vitamin c, total ascorbic acid": "vitamin_c",
        "vitamin a, iu": "vitamin_a",
        "cholesterol": "cholesterol",
        "potassium, k": "potassium",
        "energy": "calories"
    }
    
    # Try to match by name
    name_lower = nutrient.name.lower()
    for key, value in name_map.items():
        if key in name_lower:
            return value
    
    # If no match, use a simplified version of the name
    return name_lower.replace(",", "").replace(" ", "_")

def analyze_food(
    food: Food,
    serving_size: float = 100.0,
    dri_type: DriType = DriType.RDA,
    gender: Gender = Gender.MALE,
    age: int = 30
) -> NutrientAnalysis:
    """
    Analyze the nutrient content of a food.
    
    Args:
        food: The food to analyze.
        serving_size: The serving size in grams.
        dri_type: The type of DRI to use for comparison.
        gender: The gender to use for DRI values.
        age: The age to use for DRI values.
        
    Returns:
        A NutrientAnalysis object.
    """
    # Create analysis object
    analysis = NutrientAnalysis(
        food=food,
        serving_size=serving_size
    )
    
    # Process nutrients
    for nutrient in food.nutrients:
        # Get standardized nutrient ID
        nutrient_id = _get_nutrient_id(nutrient)
        
        # Calculate amount for the serving size
        amount = nutrient.amount * (serving_size / 100.0)
        
        # Get DRI value if available
        dri_value = get_dri(nutrient_id, dri_type, gender, age)
        
        # Calculate DRI percentage if DRI is available
        dri_percent = None
        if dri_value is not None and dri_value > 0:
            dri_percent = (amount / dri_value) * 100.0
        
        # Create nutrient value
        nutrient_value = NutrientValue(
            nutrient=nutrient,
            amount=amount,
            unit=nutrient.unit_name,
            dri=dri_value,
            dri_percent=dri_percent,
            dri_type=dri_type
        )
        
        # Add to nutrients dictionary
        analysis.nutrients[nutrient_id] = nutrient_value
        
        # Track macronutrients
        if nutrient_id == "protein":
            analysis.protein_per_serving = amount
        elif nutrient_id == "fat":
            analysis.fat_per_serving = amount
        elif nutrient_id == "carbs":
            analysis.carbs_per_serving = amount
        elif nutrient_id == "calories":
            analysis.calories_per_serving = amount
    
    # Calculate macronutrient distribution
    total_calories = 0.0
    
    # Protein: 4 calories per gram
    protein_calories = analysis.protein_per_serving * 4.0
    total_calories += protein_calories
    
    # Carbs: 4 calories per gram
    carb_calories = analysis.carbs_per_serving * 4.0
    total_calories += carb_calories
    
    # Fat: 9 calories per gram
    fat_calories = analysis.fat_per_serving * 9.0
    total_calories += fat_calories
    
    # If we don't have macronutrient data, use the calories value
    if total_calories == 0.0 and analysis.calories_per_serving > 0:
        total_calories = analysis.calories_per_serving
    
    # Calculate percentages
    if total_calories > 0:
        analysis.macronutrient_distribution = {
            "protein": (protein_calories / total_calories) * 100.0 if protein_calories > 0 else 0.0,
            "carbs": (carb_calories / total_calories) * 100.0 if carb_calories > 0 else 0.0,
            "fat": (fat_calories / total_calories) * 100.0 if fat_calories > 0 else 0.0
        }
    
    return analysis

def analyze_foods(
    foods: List[Food],
    serving_sizes: Optional[List[float]] = None,
    dri_type: DriType = DriType.RDA,
    gender: Gender = Gender.MALE,
    age: int = 30
) -> List[NutrientAnalysis]:
    """
    Analyze the nutrient content of multiple foods.
    
    Args:
        foods: The foods to analyze.
        serving_sizes: The serving sizes in grams (one per food).
        dri_type: The type of DRI to use for comparison.
        gender: The gender to use for DRI values.
        age: The age to use for DRI values.
        
    Returns:
        A list of NutrientAnalysis objects.
    """
    # Use default serving size if not provided
    if serving_sizes is None:
        serving_sizes = [100.0] * len(foods)
    
    # Ensure serving_sizes matches foods length
    if len(serving_sizes) != len(foods):
        raise ValueError("Number of serving sizes must match number of foods")
    
    # Analyze each food
    return [
        analyze_food(food, serving_size, dri_type, gender, age)
        for food, serving_size in zip(foods, serving_sizes)
    ]

def compare_foods(
    foods: List[Food],
    nutrient_ids: Optional[List[str]] = None,
    serving_sizes: Optional[List[float]] = None,
    dri_type: DriType = DriType.RDA,
    gender: Gender = Gender.MALE,
    age: int = 30
) -> Dict[str, List[Tuple[str, float, str]]]:
    """
    Compare the nutrient content of multiple foods.
    
    Args:
        foods: The foods to compare.
        nutrient_ids: The nutrient IDs to compare.
        serving_sizes: The serving sizes in grams (one per food).
        dri_type: The type of DRI to use for comparison.
        gender: The gender to use for DRI values.
        age: The age to use for DRI values.
        
    Returns:
        A dictionary mapping nutrient IDs to lists of (food_name, amount, unit) tuples.
    """
    # Analyze foods
    analyses = analyze_foods(foods, serving_sizes, dri_type, gender, age)
    
    # If no nutrient IDs provided, use common ones
    if nutrient_ids is None:
        nutrient_ids = ["protein", "fat", "carbs", "fiber", "vitamin_c", "calcium", "iron"]
    
    # Initialize result dictionary
    result: Dict[str, List[Tuple[str, float, str]]] = {
        nutrient_id: [] for nutrient_id in nutrient_ids
    }
    
    # Compare nutrients
    for analysis in analyses:
        for nutrient_id in nutrient_ids:
            nutrient_value = analysis.get_nutrient(nutrient_id)
            if nutrient_value:
                result[nutrient_id].append((
                    analysis.food.description,
                    nutrient_value.amount,
                    nutrient_value.unit
                ))
    
    return result