import numpy as np
import pytest

from app.fuzzy_engine import (
    OUTPUT_UNIVERSE, calculate_irrigation, centroid, evaluate_rules, aggregate_output,
)
from app.membership_functions import IRRIGATION, fuzzify_all
from app.rules import RULES


# the three required scenarios (expectations are ranges, not exact copies) 
def test_case1_dry_hot_low_humidity_gives_high_or_very_high():
    result = calculate_irrigation(20, 35, 30)
    assert result["category"] in ("High", "Very High")
    assert result["irrigation_level"] >= 75


def test_case2_wet_gives_very_low():
    result = calculate_irrigation(80, 25, 70)
    assert result["category"] == "Very Low"
    assert result["irrigation_level"] <= 20


def test_case3_average_conditions_give_medium():
    result = calculate_irrigation(50, 25, 50)
    assert result["category"] == "Medium"
    assert 40 <= result["irrigation_level"] <= 60


#the mechanics of Mamdani inference 
def test_centroid_of_symmetric_triangle_is_its_peak():
    medium = IRRIGATION.sets["medium"].membership(OUTPUT_UNIVERSE)   # triangle 30-50-70
    assert centroid(OUTPUT_UNIVERSE, medium) == pytest.approx(50, abs=0.01)


def test_centroid_rejects_empty_shape():
    with pytest.raises(ValueError):
        centroid(OUTPUT_UNIVERSE, np.zeros_like(OUTPUT_UNIVERSE))


def test_and_operator_uses_minimum():
    # Case 1: Dry=1.0, Hot=0.625, Low humidity=0.75 -> Rule 2 strength = min = 0.625
    memberships = fuzzify_all(20, 35, 30)
    strengths = {rule.id: s for rule, s in evaluate_rules(memberships)}
    assert strengths[2] == pytest.approx(0.625)


def test_aggregation_is_clipped_by_firing_strength():
    memberships = fuzzify_all(20, 35, 30)
    aggregated = aggregate_output(evaluate_rules(memberships))
    assert aggregated.max() == pytest.approx(0.625)   # only rule 2 fires, clipped at 0.625


def test_category_and_number_are_separate_outputs():
    result = calculate_irrigation(20, 35, 30)
    assert isinstance(result["category"], str)
    assert isinstance(result["irrigation_level"], float)


def test_result_contains_all_required_parts():
    result = calculate_irrigation(28, 34, 40)
    for key in ("irrigation_level", "category", "recommendation", "membership_values",
                "activated_rules", "aggregated_output"):
        assert key in result
    assert result["activated_rules"], "at least one rule must fire"


#  behaviour over the whole input space 
def test_every_input_combination_gives_a_valid_result():
    """Rules must cover the whole input space: a rule always fires, output in 0-100."""
    for soil in range(0, 101, 5):
        for temp in range(0, 46, 3):
            for hum in range(0, 101, 10):
                level = calculate_irrigation(soil, temp, hum)["irrigation_level"]
                assert 0 <= level <= 100


def test_wetter_soil_never_increases_irrigation():
    previous = 101
    for soil in range(0, 101, 5):
        level = calculate_irrigation(soil, 25, 50)["irrigation_level"]
        assert level <= previous + 1e-9
        previous = level


def test_hotter_weather_never_decreases_irrigation_for_dry_soil():
    previous = -1
    for temp in range(0, 46, 3):
        level = calculate_irrigation(10, temp, 40)["irrigation_level"]
        assert level >= previous - 1e-9
        previous = level


def test_smooth_output_no_sudden_jump():
    """Fuzzy logic gives gradual change: a 1-unit input step moves the output only a little."""
    levels = [calculate_irrigation(s, 25, 50)["irrigation_level"] for s in range(0, 101)]
    assert max(abs(b - a) for a, b in zip(levels, levels[1:])) < 5


#boundary and invalid inputs 
@pytest.mark.parametrize("soil,temp,hum", [(0, 0, 0), (100, 45, 100), (0, 45, 0), (100, 0, 100)])
def test_boundary_values_are_accepted(soil, temp, hum):
    assert 0 <= calculate_irrigation(soil, temp, hum)["irrigation_level"] <= 100


@pytest.mark.parametrize("soil,temp,hum", [
    (-1, 25, 50), (101, 25, 50), (50, -1, 50), (50, 46, 50), (50, 25, -1), (50, 25, 101),
    (float("nan"), 25, 50), (50, float("inf"), 50), ("50", 25, 50),
])
def test_invalid_inputs_raise_value_error(soil, temp, hum):
    with pytest.raises(ValueError):
        calculate_irrigation(soil, temp, hum)
