"""
Nutrient definitions and classifications for analysis.

This module defines the Nutrient class and provides lists of nutrients
organized by category (macronutrients, minerals, vitamins, etc.).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .units import Unit, UNIT_GRAM, UNIT_KILOCALORIE, UNIT_MILLIGRAM, UNIT_MICROGRAM


@dataclass
class Nutrient:
    """
    Represents a nutrient with its properties.
    
    Attributes:
        id: The unique identifier for the nutrient.
        name: The name of the nutrient.
        display_name: The display name of the nutrient.
        unit: The unit used to measure the nutrient.
        group: The nutrient group (e.g., macronutrient, vitamin, mineral).
        usda_id: The USDA nutrient ID (optional).
    """
    
    id: str
    name: str
    display_name: str
    unit: Unit
    group: str
    usda_id: Optional[int] = None


# Define all nutrients
NUTRIENTS: Dict[str, Nutrient] = {
    # Macronutrients
    "energy": Nutrient("energy", "energy", "Energy", UNIT_KILOCALORIE, "macronutrient", 1008),
    "protein": Nutrient("protein", "protein", "Protein", UNIT_GRAM, "macronutrient", 1003),
    "fat": Nutrient("fat", "fat", "Total Fat", UNIT_GRAM, "macronutrient", 1004),
    "carbohydrate": Nutrient("carbohydrate", "carbohydrate", "Carbohydrate", UNIT_GRAM, "macronutrient", 1005),
    "fiber": Nutrient("fiber", "fiber", "Fiber", UNIT_GRAM, "macronutrient", 1079),
    "water": Nutrient("water", "water", "Water", UNIT_GRAM, "macronutrient", 1051),
    
    # Fat breakdown
    "saturated": Nutrient("saturated", "saturated", "Saturated Fat", UNIT_GRAM, "fat", 1258),
    "monounsaturated": Nutrient("monounsaturated", "monounsaturated", "Monounsaturated Fat", UNIT_GRAM, "fat", 1292),
    "polyunsaturated": Nutrient("polyunsaturated", "polyunsaturated", "Polyunsaturated Fat", UNIT_GRAM, "fat", 1293),
    "trans": Nutrient("trans", "trans", "Trans Fat", UNIT_GRAM, "fat", 1257),
    "cholesterol": Nutrient("cholesterol", "cholesterol", "Cholesterol", UNIT_MILLIGRAM, "fat", 1253),
    
    # Carbohydrate breakdown
    "sugar": Nutrient("sugar", "sugar", "Total Sugar", UNIT_GRAM, "carbohydrate", 2000),
    "starch": Nutrient("starch", "starch", "Starch", UNIT_GRAM, "carbohydrate", 1009),
    "sucrose": Nutrient("sucrose", "sucrose", "Sucrose", UNIT_GRAM, "carbohydrate", 1010),
    "glucose": Nutrient("glucose", "glucose", "Glucose", UNIT_GRAM, "carbohydrate", 1011),
    "fructose": Nutrient("fructose", "fructose", "Fructose", UNIT_GRAM, "carbohydrate", 1012),
    "lactose": Nutrient("lactose", "lactose", "Lactose", UNIT_GRAM, "carbohydrate", 1013),
    "maltose": Nutrient("maltose", "maltose", "Maltose", UNIT_GRAM, "carbohydrate", 1014),
    "galactose": Nutrient("galactose", "galactose", "Galactose", UNIT_GRAM, "carbohydrate", 1075),
    
    # Minerals
    "calcium": Nutrient("calcium", "calcium", "Calcium", UNIT_MILLIGRAM, "mineral", 1087),
    "iron": Nutrient("iron", "iron", "Iron", UNIT_MILLIGRAM, "mineral", 1089),
    "magnesium": Nutrient("magnesium", "magnesium", "Magnesium", UNIT_MILLIGRAM, "mineral", 1090),
    "phosphorus": Nutrient("phosphorus", "phosphorus", "Phosphorus", UNIT_MILLIGRAM, "mineral", 1091),
    "potassium": Nutrient("potassium", "potassium", "Potassium", UNIT_MILLIGRAM, "mineral", 1092),
    "sodium": Nutrient("sodium", "sodium", "Sodium", UNIT_MILLIGRAM, "mineral", 1093),
    "zinc": Nutrient("zinc", "zinc", "Zinc", UNIT_MILLIGRAM, "mineral", 1095),
    "copper": Nutrient("copper", "copper", "Copper", UNIT_MICROGRAM, "mineral", 1098),
    "manganese": Nutrient("manganese", "manganese", "Manganese", UNIT_MILLIGRAM, "mineral", 1101),
    "selenium": Nutrient("selenium", "selenium", "Selenium", UNIT_MICROGRAM, "mineral", 1103),
    "molybdenum": Nutrient("molybdenum", "molybdenum", "Molybdenum", UNIT_MICROGRAM, "mineral", 1102),
    
    # Vitamins
    "vitamin_a": Nutrient("vitamin_a", "vitamin_a", "Vitamin A", UNIT_MICROGRAM, "vitamin", 1106),
    "vitamin_c": Nutrient("vitamin_c", "vitamin_c", "Vitamin C", UNIT_MILLIGRAM, "vitamin", 1162),
    "vitamin_d": Nutrient("vitamin_d", "vitamin_d", "Vitamin D", UNIT_MICROGRAM, "vitamin", 1114),
    "vitamin_e": Nutrient("vitamin_e", "vitamin_e", "Vitamin E", UNIT_MILLIGRAM, "vitamin", 1109),
    "vitamin_k": Nutrient("vitamin_k", "vitamin_k", "Vitamin K", UNIT_MICROGRAM, "vitamin", 1185),
    "thiamin": Nutrient("thiamin", "thiamin", "Thiamin (B1)", UNIT_MILLIGRAM, "vitamin", 1165),
    "riboflavin": Nutrient("riboflavin", "riboflavin", "Riboflavin (B2)", UNIT_MILLIGRAM, "vitamin", 1166),
    "niacin": Nutrient("niacin", "niacin", "Niacin (B3)", UNIT_MILLIGRAM, "vitamin", 1167),
    "pantothenic_acid": Nutrient("pantothenic_acid", "pantothenic_acid", "Pantothenic Acid (B5)", UNIT_MILLIGRAM, "vitamin", 1170),
    "vitamin_b6": Nutrient("vitamin_b6", "vitamin_b6", "Vitamin B6", UNIT_MILLIGRAM, "vitamin", 1175),
    "biotin": Nutrient("biotin", "biotin", "Biotin (B7)", UNIT_MICROGRAM, "vitamin", 1176),
    "folate": Nutrient("folate", "folate", "Folate (B9)", UNIT_MICROGRAM, "vitamin", 1177),
    "vitamin_b12": Nutrient("vitamin_b12", "vitamin_b12", "Vitamin B12", UNIT_MICROGRAM, "vitamin", 1178),
    "choline": Nutrient("choline", "choline", "Choline", UNIT_MILLIGRAM, "vitamin", 1180),
    
    # Essential amino acids
    "histidine": Nutrient("histidine", "histidine", "Histidine", UNIT_MILLIGRAM, "amino_acid", 1221),
    "isoleucine": Nutrient("isoleucine", "isoleucine", "Isoleucine", UNIT_MILLIGRAM, "amino_acid", 1212),
    "leucine": Nutrient("leucine", "leucine", "Leucine", UNIT_MILLIGRAM, "amino_acid", 1213),
    "lysine": Nutrient("lysine", "lysine", "Lysine", UNIT_MILLIGRAM, "amino_acid", 1214),
    "methionine": Nutrient("methionine", "methionine", "Methionine", UNIT_MILLIGRAM, "amino_acid", 1215),
    "phenylalanine": Nutrient("phenylalanine", "phenylalanine", "Phenylalanine", UNIT_MILLIGRAM, "amino_acid", 1217),
    "threonine": Nutrient("threonine", "threonine", "Threonine", UNIT_MILLIGRAM, "amino_acid", 1211),
    "tryptophan": Nutrient("tryptophan", "tryptophan", "Tryptophan", UNIT_MILLIGRAM, "amino_acid", 1210),
    "valine": Nutrient("valine", "valine", "Valine", UNIT_MILLIGRAM, "amino_acid", 1219),
    
    # Non-essential amino acids
    "alanine": Nutrient("alanine", "alanine", "Alanine", UNIT_MILLIGRAM, "amino_acid", 1222),
    "arginine": Nutrient("arginine", "arginine", "Arginine", UNIT_MILLIGRAM, "amino_acid", 1220),
    "aspartic_acid": Nutrient("aspartic_acid", "aspartic_acid", "Aspartic Acid", UNIT_MILLIGRAM, "amino_acid", 1223),
    "cystine": Nutrient("cystine", "cystine", "Cystine", UNIT_MILLIGRAM, "amino_acid", 1216),
    "glutamic_acid": Nutrient("glutamic_acid", "glutamic_acid", "Glutamic Acid", UNIT_MILLIGRAM, "amino_acid", 1224),
    "glycine": Nutrient("glycine", "glycine", "Glycine", UNIT_MILLIGRAM, "amino_acid", 1225),
    "proline": Nutrient("proline", "proline", "Proline", UNIT_MILLIGRAM, "amino_acid", 1226),
    "serine": Nutrient("serine", "serine", "Serine", UNIT_MILLIGRAM, "amino_acid", 1227),
    "tyrosine": Nutrient("tyrosine", "tyrosine", "Tyrosine", UNIT_MILLIGRAM, "amino_acid", 1218),
}


# Group nutrients by category
MACRONUTRIENTS: List[str] = [
    "energy", "protein", "fat", "carbohydrate", "fiber", "water"
]

FATS: List[str] = [
    "saturated", "monounsaturated", "polyunsaturated", "trans", "cholesterol"
]

CARBOHYDRATES: List[str] = [
    "sugar", "starch", "sucrose", "glucose", "fructose", "lactose", "maltose", "galactose"
]

MINERALS: List[str] = [
    "calcium", "iron", "magnesium", "phosphorus", "potassium", "sodium", "zinc",
    "copper", "manganese", "selenium", "molybdenum"
]

VITAMINS: List[str] = [
    "vitamin_a", "vitamin_c", "vitamin_d", "vitamin_e", "vitamin_k", "thiamin",
    "riboflavin", "niacin", "pantothenic_acid", "vitamin_b6", "biotin", "folate",
    "vitamin_b12", "choline"
]

AMINO_ACIDS: List[str] = [
    "histidine", "isoleucine", "leucine", "lysine", "methionine", "phenylalanine",
    "threonine", "tryptophan", "valine", "alanine", "arginine", "aspartic_acid",
    "cystine", "glutamic_acid", "glycine", "proline", "serine", "tyrosine"
]

# Group all nutrients by category
NUTRIENT_GROUPS: Dict[str, List[str]] = {
    "macronutrient": MACRONUTRIENTS,
    "fat": FATS,
    "carbohydrate": CARBOHYDRATES,
    "mineral": MINERALS,
    "vitamin": VITAMINS,
    "amino_acid": AMINO_ACIDS
}


def get_nutrient_by_usda_id(usda_id: int) -> Optional[Nutrient]:
    """
    Get a nutrient by its USDA ID.
    
    Args:
        usda_id: The USDA nutrient ID.
        
    Returns:
        The nutrient if found, None otherwise.
    """
    for nutrient in NUTRIENTS.values():
        if nutrient.usda_id == usda_id:
            return nutrient
    return None


def get_nutrient_by_name(name: str) -> Optional[Nutrient]:
    """
    Get a nutrient by its name.
    
    Args:
        name: The nutrient name.
        
    Returns:
        The nutrient if found, None otherwise.
    """
    # Try exact match first
    if name in NUTRIENTS:
        return NUTRIENTS[name]
    
    # Try case-insensitive match
    name_lower = name.lower()
    for nutrient in NUTRIENTS.values():
        if nutrient.name.lower() == name_lower or nutrient.display_name.lower() == name_lower:
            return nutrient
    
    return None