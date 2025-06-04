"""
Dietary Reference Intake (DRI) data and utilities.
"""

import os
import json
from enum import Enum
from typing import Dict, Optional, Any, Union

# Path to DRI data files
DRI_DATA_DIR = os.path.join(os.path.dirname(__file__), "resources", "dri")

class Gender(str, Enum):
    """Gender for DRI calculations."""
    MALE = "male"
    FEMALE = "female"

class DriType(str, Enum):
    """Types of Dietary Reference Intakes."""
    RDA = "rda"  # Recommended Dietary Allowance
    AI = "ai"    # Adequate Intake
    UL = "ul"    # Tolerable Upper Intake Level
    EAR = "ear"  # Estimated Average Requirement
    AMDR = "amdr"  # Acceptable Macronutrient Distribution Range

# Cache for DRI data
_dri_cache: Dict[str, Dict] = {}

def _load_dri_data(dri_type: DriType) -> Dict:
    """
    Load DRI data from JSON file.
    
    Args:
        dri_type: The type of DRI to load.
        
    Returns:
        Dictionary containing DRI data.
    """
    if dri_type.value in _dri_cache:
        return _dri_cache[dri_type.value]
    
    file_path = os.path.join(DRI_DATA_DIR, f"{dri_type.value}.json")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            _dri_cache[dri_type.value] = data
            return data
    except FileNotFoundError:
        # Return empty data if file not found
        return {}

def get_dri(
    nutrient_id: Union[str, int],
    dri_type: DriType = DriType.RDA,
    gender: Gender = Gender.MALE,
    age: int = 30
) -> Optional[float]:
    """
    Get the Dietary Reference Intake (DRI) for a nutrient.
    
    Args:
        nutrient_id: The nutrient ID or name.
        dri_type: The type of DRI to retrieve.
        gender: The gender to use for the DRI.
        age: The age to use for the DRI.
        
    Returns:
        The DRI value, or None if not found.
    """
    # Convert nutrient_id to string
    nutrient_id = str(nutrient_id).lower()
    
    # Load DRI data
    dri_data = _load_dri_data(dri_type)
    
    # Check if nutrient exists in data
    if nutrient_id not in dri_data:
        return None
    
    # Get age groups for the gender
    gender_data = dri_data[nutrient_id].get(gender.value, {})
    
    # Find the appropriate age group
    for age_range, value in gender_data.items():
        # Parse age range
        if "-" in age_range:
            min_age, max_age = map(int, age_range.split("-"))
            if min_age <= age <= max_age:
                return value
        elif age_range.endswith("+"):
            min_age = int(age_range[:-1])
            if age >= min_age:
                return value
    
    return None