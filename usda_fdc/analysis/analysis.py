"""
Food nutrient analysis functionality.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple

from ..models import Food, Nutrient
from ..utils import convert_measurement
from .dri import DriType, DriValue, Gender, get_dri, get_dri_value

# FDC writes its units in caps ("MG"), and micrograms as "UG". Anything not
# listed here — IU above all — has no mass dimension we can convert.
_FDC_UNIT_ALIASES = {
    "g": "g",
    "mg": "mg",
    "ug": "µg",
    "µg": "µg",
    "mcg": "µg",
}


def _dri_percent(amount: float, unit: Optional[str], dri: Optional[DriValue]) -> Optional[float]:
    """What percentage of a DRI an amount represents, or None if they cannot be compared.

    The DRI files disagree about units: an RDA for iron is 8 mg, its UL is
    0.045 — grams. Dividing a food's milligrams by the latter would report 1000x
    the truth, so the amount is converted into the DRI's own unit first, and a
    pair that cannot be converted (vitamin A in IU against a µg allowance)
    yields nothing rather than a confident wrong number.
    """
    if dri is None or not dri.value:
        return None

    food_unit = _FDC_UNIT_ALIASES.get((unit or "").strip().lower())
    dri_unit = _FDC_UNIT_ALIASES.get((dri.unit or "").strip().lower())
    if not food_unit or not dri_unit:
        return None

    try:
        comparable = convert_measurement(amount, food_unit, dri_unit)
    except ValueError:
        return None

    return (comparable / dri.value) * 100.0

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
    # The unit ``dri`` is expressed in, which is not always the food's own:
    # an RDA for iron is 8 mg, its UL is 0.045 g.
    dri_unit: Optional[str] = None

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

# FDC reports a food's energy several times over, under the same name:
#
#   1008 / 208  Energy                             kcal
#   1062 / 268  Energy                             kJ     (the same energy!)
#   2047 / 957  Energy (Atwater General Factors)   kcal
#   2048 / 958  Energy (Atwater Specific Factors)  kcal
#
# Matching those on the name alone made every one of them "calories", so
# whichever came last in the list won. Clarified butter (fdc_id 171314) lists
# 900 kcal and then 3766 kJ, and was reported as 3766 "calories" — a figure the
# CLI and the HTML report then printed with a kcal suffix.
#
# Only the kcal rows are calories, and where a food carries more than one of
# them we prefer the plain Energy row so the answer cannot depend on list order.
_ENERGY_KCAL_PRECEDENCE = (
    (1008, "208"),  # Energy
    (2048, "958"),  # Energy (Atwater Specific Factors)
    (2047, "957"),  # Energy (Atwater General Factors)
)

# Abridged responses spell the unit "KCAL"; full ones spell it "kcal".
_KCAL_UNITS = {"kcal", "kilocalorie", "kilocalories"}


def _is_energy(nutrient: Nutrient) -> bool:
    """Whether a nutrient row describes a food's energy, in any unit."""
    return "energy" in (nutrient.name or "").lower()


def _is_kcal(nutrient: Nutrient) -> bool:
    """Whether a nutrient row is measured in kilocalories rather than kilojoules."""
    return (nutrient.unit_name or "").strip().lower() in _KCAL_UNITS


def _energy_precedence(nutrient: Nutrient) -> int:
    """Rank an energy row; lower wins.

    An abridged food carries no nutrient id, only its number, so match on
    either.
    """
    for rank, (nutrient_id, nutrient_nbr) in enumerate(_ENERGY_KCAL_PRECEDENCE):
        if nutrient.id == nutrient_id or str(nutrient.nutrient_nbr or "") == nutrient_nbr:
            return rank
    return len(_ENERGY_KCAL_PRECEDENCE)


def _get_nutrient_id(nutrient: Nutrient) -> str:
    """
    Get a standardized nutrient ID from a nutrient.

    Args:
        nutrient: The nutrient object.

    Returns:
        A standardized nutrient ID.
    """
    if _is_energy(nutrient):
        # A kJ row is not calories. Give it an id of its own so it cannot
        # overwrite the kcal row it sits beside.
        if _is_kcal(nutrient):
            return "calories"
        return f"energy_{(nutrient.unit_name or 'unknown').strip().lower()}"

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
        "potassium, k": "potassium"
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
    
    # Rank of the energy row currently holding "calories", so a lower-ranked
    # one cannot displace it.
    calories_rank: Optional[int] = None

    # Process nutrients
    for nutrient in food.nutrients:
        # Get standardized nutrient ID
        nutrient_id = _get_nutrient_id(nutrient)

        # Calculate amount for the serving size
        amount = nutrient.amount * (serving_size / 100.0)

        # Get DRI value if available, and the unit it is expressed in
        dri = get_dri_value(nutrient_id, dri_type, gender, age)

        # Create nutrient value
        nutrient_value = NutrientValue(
            nutrient=nutrient,
            amount=amount,
            unit=nutrient.unit_name,
            dri=dri.value if dri else None,
            dri_percent=_dri_percent(amount, nutrient.unit_name, dri),
            dri_type=dri_type,
            dri_unit=dri.unit if dri else None
        )

        if nutrient_id == "calories":
            rank = _energy_precedence(nutrient)
            if calories_rank is not None and rank >= calories_rank:
                # Already holding a better energy row; keep it.
                continue
            calories_rank = rank

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