"""
Dietary Reference Intakes (DRI) module.

This module provides access to Dietary Reference Intakes (DRI) data,
including Recommended Dietary Allowances (RDA), Adequate Intakes (AI),
and Tolerable Upper Intake Levels (UL).
"""

import json
import os
from enum import Enum
from typing import Dict, Optional, Any, Union

import pkg_resources


class DriType(Enum):
    """Types of Dietary Reference Intakes."""
    RDA = "rda"  # Recommended Dietary Allowance
    AI = "ai"    # Adequate Intake
    UL = "ul"    # Tolerable Upper Intake Level


class Gender(Enum):
    """Gender options for DRI data."""
    MALE = "male"
    FEMALE = "female"


# Define DRI types for easier access
DRI_TYPES = {
    "rda": DriType.RDA,
    "ai": DriType.AI,
    "ul": DriType.UL
}


class DietaryReferenceIntakes:
    """
    Provides access to Dietary Reference Intakes (DRI) data.
    
    Attributes:
        data: The loaded DRI data.
        metadata: Metadata about the DRI data.
    """
    
    def __init__(self, dri_type: DriType = DriType.RDA, gender: Gender = Gender.MALE):
        """
        Initialize DietaryReferenceIntakes.
        
        Args:
            dri_type: The type of DRI to load (RDA, AI, or UL).
            gender: The gender to load data for (only applicable for RDA and AI).
        """
        self.dri_type = dri_type
        self.gender = gender
        self.data: Dict[str, float] = {}
        self.metadata: Dict[str, Any] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load the DRI data from the appropriate file."""
        # Determine the file path based on the DRI type and gender
        if self.dri_type == DriType.UL:
            file_name = "ul.json"
        elif self.dri_type in (DriType.RDA, DriType.AI):
            if self.gender == Gender.MALE:
                file_name = "rda_male.json"
            else:
                file_name = "rda_female.json"
        else:
            raise ValueError(f"Unknown DRI type: {self.dri_type}")
        
        # Get the file path
        file_path = os.path.join(
            os.path.dirname(__file__),
            "resources",
            "dri",
            file_name
        )
        
        # Load the data
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                self.data = data.get("dietary_reference_intakes", {})
                self.metadata = data.get("metadata", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading DRI data: {e}")
    
    def get_dri(self, nutrient_id: str) -> Optional[float]:
        """
        Get the DRI value for a nutrient.
        
        Args:
            nutrient_id: The nutrient ID.
            
        Returns:
            The DRI value if available, None otherwise.
        """
        return self.data.get(nutrient_id)
    
    def get_all_dris(self) -> Dict[str, float]:
        """
        Get all DRI values.
        
        Returns:
            A dictionary of nutrient IDs to DRI values.
        """
        return self.data.copy()


def get_dri(
    nutrient_id: str,
    dri_type: Union[DriType, str] = DriType.RDA,
    gender: Union[Gender, str] = Gender.MALE
) -> Optional[float]:
    """
    Get the DRI value for a nutrient.
    
    Args:
        nutrient_id: The nutrient ID.
        dri_type: The type of DRI to get.
        gender: The gender to get the DRI for.
        
    Returns:
        The DRI value if available, None otherwise.
    """
    # Convert string inputs to enum values if needed
    if isinstance(dri_type, str):
        dri_type = DRI_TYPES.get(dri_type.lower(), DriType.RDA)
    
    if isinstance(gender, str):
        gender = Gender.MALE if gender.lower() == "male" else Gender.FEMALE
    
    # Get the DRI data
    dri = DietaryReferenceIntakes(dri_type, gender)
    return dri.get_dri(nutrient_id)