"""
Tests for how a food's energy is turned into "calories".

FDC reports energy several times per food, under the same name, in different
units and by different derivations:

    1008 / 208  Energy                             kcal
    1062 / 268  Energy                             kJ     (the same energy!)
    2047 / 957  Energy (Atwater General Factors)   kcal
    2048 / 958  Energy (Atwater Specific Factors)  kcal

Matching those on the name alone made every one of them "calories", so whichever
came last in the list won — and the CLI and HTML report printed the winner with a
kcal suffix regardless of what unit it was actually in.
"""

import pytest

from usda_fdc.models import Food, Nutrient
from usda_fdc.analysis import analyze_food


def _food(*nutrients: Nutrient) -> Food:
    return Food(
        fdc_id=171314,
        description="Butter, Clarified butter (ghee)",
        data_type="SR Legacy",
        nutrients=list(nutrients),
    )


ENERGY_KCAL = Nutrient(id=1008, name="Energy", amount=900.0, unit_name="kcal", nutrient_nbr="208")
ENERGY_KJ = Nutrient(id=1062, name="Energy", amount=3766.0, unit_name="kJ", nutrient_nbr="268")
ATWATER_GENERAL = Nutrient(id=2047, name="Energy (Atwater General Factors)", amount=64.66, unit_name="kcal", nutrient_nbr="957")
ATWATER_SPECIFIC = Nutrient(id=2048, name="Energy (Atwater Specific Factors)", amount=58.20, unit_name="kcal", nutrient_nbr="958")


def test_kilojoules_are_not_reported_as_calories():
    """The regression: real fdc_id 171314 lists 900 kcal and then 3766 kJ, and
    was analyzed as 3766 "calories" — a 4.2x overstatement of a food's energy."""
    analysis = analyze_food(_food(ENERGY_KCAL, ENERGY_KJ))

    assert analysis.calories_per_serving == 900.0


def test_kilojoule_row_does_not_win_by_coming_last():
    """Order is the whole bug: the kJ row overwrote the kcal row simply by being
    later in the list."""
    analysis = analyze_food(_food(ENERGY_KJ, ENERGY_KCAL))
    assert analysis.calories_per_serving == 900.0

    analysis = analyze_food(_food(ENERGY_KCAL, ENERGY_KJ))
    assert analysis.calories_per_serving == 900.0


def test_kilojoules_are_still_available_under_their_own_id():
    """Keyed separately rather than dropped, so no data is lost."""
    analysis = analyze_food(_food(ENERGY_KCAL, ENERGY_KJ))

    kj = analysis.get_nutrient("energy_kj")
    assert kj is not None
    assert kj.amount == 3766.0
    assert kj.unit == "kJ"


def test_calories_is_the_kcal_row_even_when_only_kilojoules_and_atwater_exist():
    analysis = analyze_food(_food(ENERGY_KJ, ATWATER_SPECIFIC))

    assert analysis.calories_per_serving == 58.20


def test_competing_kcal_rows_resolve_the_same_way_regardless_of_order():
    """Real foods (fdc_id 1750340) carry both Atwater rows with different values.
    Whichever we prefer, it must not depend on the order FDC happened to send."""
    forwards = analyze_food(_food(ATWATER_GENERAL, ATWATER_SPECIFIC))
    backwards = analyze_food(_food(ATWATER_SPECIFIC, ATWATER_GENERAL))

    assert forwards.calories_per_serving == backwards.calories_per_serving


def test_plain_energy_row_is_preferred_over_atwater_variants():
    analysis = analyze_food(_food(ATWATER_GENERAL, ATWATER_SPECIFIC, ENERGY_KCAL))

    assert analysis.calories_per_serving == 900.0


def test_energy_is_matched_on_an_abridged_food_which_has_no_nutrient_id():
    """An abridged response carries only the nutrient number, and spells the unit
    "KCAL" rather than "kcal"."""
    abridged_kcal = Nutrient(id=None, name="Energy", amount=900.0, unit_name="KCAL", nutrient_nbr="208")
    abridged_kj = Nutrient(id=None, name="Energy", amount=3770.0, unit_name="kJ", nutrient_nbr="268")

    analysis = analyze_food(_food(abridged_kj, abridged_kcal))

    assert analysis.calories_per_serving == 900.0


def test_calories_scale_with_serving_size():
    analysis = analyze_food(_food(ENERGY_KCAL, ENERGY_KJ), serving_size=50.0)

    assert analysis.calories_per_serving == 450.0
