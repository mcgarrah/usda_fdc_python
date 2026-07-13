"""
Dietary Reference Intake (DRI) data and utilities.
"""

import os
import json
import logging
from enum import Enum
from typing import Dict, NamedTuple, Optional, Any, Union

logger = logging.getLogger(__name__)

# Path to DRI data files
DRI_DATA_DIR = os.path.join(os.path.dirname(__file__), "resources", "dri")

class Gender(str, Enum):
    """Gender for DRI calculations."""
    MALE = "male"
    FEMALE = "female"

class DriType(str, Enum):
    """Types of Dietary Reference Intakes.

    Only RDA and UL ship with data. Asking for a type with no data behind it
    returns ``None`` and logs a warning — see ``get_dri``.
    """
    RDA = "rda"  # Recommended Dietary Allowance
    AI = "ai"    # Adequate Intake
    UL = "ul"    # Tolerable Upper Intake Level
    EAR = "ear"  # Estimated Average Requirement
    AMDR = "amdr"  # Acceptable Macronutrient Distribution Range


class DriValue(NamedTuple):
    """A DRI, with the unit it is expressed in.

    The unit is the whole point: the shipped data files disagree about it.
    rda.json states a natural unit per nutrient (iron in mg, vitamin A in µg),
    while ul.json expresses every nutrient in grams (iron 0.045 = 45 mg).
    Handing a caller a bare number invited it to be compared against a food's
    milligrams, off by a factor of a thousand and with nothing to show for it.
    """
    value: float
    unit: str


# Any age, for a data file that does not break its values down by age.
_ANY_AGE = "*"

# Cache for DRI data, normalized to a single shape
_dri_cache: Dict[str, Dict[str, Any]] = {}

# DRI types we have already warned about, so a missing file is reported once
# rather than once per nutrient per food.
_warned_missing: set = set()


def _parse_age_group(age_group: str) -> str:
    """Turn a metadata age_group ("19+ years", "19-50 years") into a range key."""
    return age_group.replace("years", "").replace("year", "").strip()


def _normalize(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a DRI file into one shape.

    Two schemas ship in this package:

    * ``rda.json`` keys nutrients directly, and breaks each down by gender and
      age with its own unit:
      ``{"iron": {"male": {"19+": 8}, "female": {...}, "unit": "mg"}}``

    * ``ul.json``, ``rda_male.json`` and ``rda_female.json`` wrap a flat table
      in metadata, apply to one age band, and express everything in grams:
      ``{"metadata": {...}, "dietary_reference_intakes": {"iron": 0.045}}``

    Only the first was ever read, which is why every DriType other than RDA
    silently returned None.
    """
    table = raw.get("dietary_reference_intakes")
    if table is None:
        return raw  # rda.json shape: already normalized

    metadata = raw.get("metadata", {})
    age_range = _parse_age_group(metadata.get("age_group", "")) or _ANY_AGE

    gender = metadata.get("gender", "all")
    genders = [g.value for g in Gender] if gender in ("all", "", None) else [gender]

    normalized: Dict[str, Any] = {}
    for nutrient_id, value in table.items():
        entry: Dict[str, Any] = {"unit": "g"}  # this schema is grams throughout
        for g in genders:
            entry[g] = {age_range: value}
        normalized[nutrient_id] = entry

    return normalized


def _load_dri_data(dri_type: DriType) -> Dict[str, Any]:
    """
    Load DRI data from JSON file.

    Args:
        dri_type: The type of DRI to load.

    Returns:
        Dictionary containing DRI data, normalized to a single shape.
    """
    if dri_type.value in _dri_cache:
        return _dri_cache[dri_type.value]

    file_path = os.path.join(DRI_DATA_DIR, f"{dri_type.value}.json")

    try:
        with open(file_path, 'r') as f:
            data = _normalize(json.load(f))
    except FileNotFoundError:
        # No data ships for this type. Say so once, instead of returning None
        # forever and leaving the caller to wonder why every DRI is missing.
        if dri_type.value not in _warned_missing:
            _warned_missing.add(dri_type.value)
            logger.warning(
                "No DRI data is available for %s; %s comparisons will be empty. "
                "This package ships data for %s and %s only.",
                dri_type.value.upper(),
                dri_type.value.upper(),
                DriType.RDA.value.upper(),
                DriType.UL.value.upper(),
            )
        data = {}

    _dri_cache[dri_type.value] = data
    return data


def get_dri_value(
    nutrient_id: Union[str, int],
    dri_type: DriType = DriType.RDA,
    gender: Gender = Gender.MALE,
    age: int = 30
) -> Optional[DriValue]:
    """
    Get the Dietary Reference Intake (DRI) for a nutrient, with its unit.

    Prefer this over ``get_dri``: the shipped data files express their values in
    different units, so a number on its own cannot be compared against a food.

    Args:
        nutrient_id: The nutrient ID or name.
        dri_type: The type of DRI to retrieve.
        gender: The gender to use for the DRI.
        age: The age to use for the DRI.

    Returns:
        The DRI and its unit, or None if there is none for this nutrient.
    """
    nutrient_id = str(nutrient_id).lower()

    dri_data = _load_dri_data(dri_type)

    if nutrient_id not in dri_data:
        return None

    entry = dri_data[nutrient_id]
    unit = entry.get("unit", "g")
    gender_data = entry.get(gender.value, {})

    for age_range, value in gender_data.items():
        if age_range == _ANY_AGE:
            return DriValue(value, unit)
        if "-" in age_range:
            min_age, max_age = map(int, age_range.split("-"))
            if min_age <= age <= max_age:
                return DriValue(value, unit)
        elif age_range.endswith("+"):
            if age >= int(age_range[:-1]):
                return DriValue(value, unit)

    return None


def get_dri(
    nutrient_id: Union[str, int],
    dri_type: DriType = DriType.RDA,
    gender: Gender = Gender.MALE,
    age: int = 30
) -> Optional[float]:
    """
    Get the Dietary Reference Intake (DRI) for a nutrient.

    The value is expressed in the unit the underlying data file uses, which is
    not the same across DRI types: RDA values come in a natural unit per
    nutrient (iron in mg), UL values come in grams (iron 0.045). Use
    ``get_dri_value`` to get the unit along with the number.

    Args:
        nutrient_id: The nutrient ID or name.
        dri_type: The type of DRI to retrieve.
        gender: The gender to use for the DRI.
        age: The age to use for the DRI.

    Returns:
        The DRI value, or None if not found.
    """
    dri = get_dri_value(nutrient_id, dri_type, gender, age)
    return dri.value if dri else None
