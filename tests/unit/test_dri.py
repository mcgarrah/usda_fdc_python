"""
Tests for DRI lookup and the unit arithmetic around it.

Two schemas ship in this package. rda.json keys nutrients directly and states a
natural unit for each (iron in mg). ul.json, rda_male.json and rda_female.json
wrap a flat table in metadata and express everything in grams (iron 0.045 = 45
mg). Only the first was ever read, so every DriType except RDA silently returned
None — and a gram-denominated DRI compared against a food's milligrams would be
off by a factor of a thousand.
"""

import pytest

from usda_fdc.models import Food, Nutrient
from usda_fdc.analysis import analyze_food
from usda_fdc.analysis.dri import DriType, Gender, get_dri, get_dri_value


def _food_with(nutrient: Nutrient) -> Food:
    return Food(fdc_id=1, description="Spinach, baby", data_type="Foundation",
                nutrients=[nutrient])


IRON_MG = Nutrient(id=1089, name="Iron, Fe", amount=1.261, unit_name="mg", nutrient_nbr="303")


def test_rda_is_found_with_its_unit():
    dri = get_dri_value("iron", DriType.RDA, Gender.MALE, 30)

    assert dri.value == 8
    assert dri.unit == "mg"


def test_upper_intake_limits_are_found():
    """The regression: ul.json ships real data, but its schema was never read,
    so every UL lookup came back None."""
    dri = get_dri_value("iron", DriType.UL, Gender.MALE, 30)

    assert dri is not None
    assert dri.value == 0.045
    assert dri.unit == "g"      # this file is grams throughout: 45 mg


def test_upper_intake_limits_apply_to_both_genders():
    """ul.json declares gender "all"."""
    for gender in (Gender.MALE, Gender.FEMALE):
        assert get_dri_value("calcium", DriType.UL, gender, 30) is not None


def test_a_dri_type_with_no_data_returns_none_rather_than_guessing():
    assert get_dri_value("iron", DriType.AI, Gender.MALE, 30) is None
    assert get_dri_value("iron", DriType.EAR, Gender.MALE, 30) is None


def test_a_missing_dri_type_is_reported_once(caplog):
    """Silence was the bug: every AI lookup returned None with no hint why."""
    from usda_fdc.analysis import dri as dri_module
    dri_module._warned_missing.discard(DriType.AI.value)
    dri_module._dri_cache.pop(DriType.AI.value, None)

    with caplog.at_level("WARNING"):
        get_dri_value("iron", DriType.AI, Gender.MALE, 30)
        get_dri_value("calcium", DriType.AI, Gender.MALE, 30)

    warnings = [r for r in caplog.records if "No DRI data" in r.message]
    assert len(warnings) == 1


def test_rda_percentage_is_computed_against_the_rda_unit():
    analysis = analyze_food(_food_with(IRON_MG), serving_size=100.0, dri_type=DriType.RDA)

    iron = analysis.get_nutrient("iron")
    assert iron.dri_percent == pytest.approx(1.261 / 8 * 100, rel=1e-6)


def test_a_gram_denominated_dri_is_not_compared_against_milligrams():
    """The unit trap: iron's UL is 0.045 **g**. Dividing 1.261 mg by 0.045
    straight would report 2802% of the upper limit for a portion of spinach.
    The real answer is 1.261 mg / 45 mg."""
    analysis = analyze_food(_food_with(IRON_MG), serving_size=100.0, dri_type=DriType.UL)

    iron = analysis.get_nutrient("iron")
    assert iron.dri_percent == pytest.approx(1.261 / 45.0 * 100, rel=1e-6)
    assert iron.dri_percent < 5.0


def test_the_dri_unit_is_exposed_alongside_the_value():
    analysis = analyze_food(_food_with(IRON_MG), serving_size=100.0, dri_type=DriType.UL)

    iron = analysis.get_nutrient("iron")
    assert iron.dri == 0.045
    assert iron.dri_unit == "g"


def test_incomparable_units_yield_no_percentage_rather_than_a_wrong_one():
    """Vitamin A in IU cannot be checked against a µg allowance. Reporting
    nothing beats reporting a confident wrong number."""
    vitamin_a_iu = Nutrient(id=1104, name="Vitamin A, IU", amount=9377.0,
                            unit_name="IU", nutrient_nbr="318")

    analysis = analyze_food(_food_with(vitamin_a_iu), serving_size=100.0)

    vitamin_a = analysis.get_nutrient("vitamin_a")
    assert vitamin_a.dri_percent is None


def test_get_dri_still_returns_a_bare_number():
    """The old signature stays, for callers already using it."""
    assert get_dri("iron", DriType.RDA, Gender.MALE, 30) == 8


def test_age_and_gender_still_select_the_right_rda():
    """Iron: 18 mg for women of 19-50, 8 mg after."""
    assert get_dri("iron", DriType.RDA, Gender.FEMALE, 30) == 18
    assert get_dri("iron", DriType.RDA, Gender.FEMALE, 60) == 8
    assert get_dri("iron", DriType.RDA, Gender.MALE, 30) == 8
