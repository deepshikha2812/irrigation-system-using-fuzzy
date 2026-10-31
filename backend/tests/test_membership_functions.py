import numpy as np
import pytest

from app.membership_functions import (
    HUMIDITY, IRRIGATION, SOIL_MOISTURE, TEMPERATURE, fuzzify_all, triangular, trapezoidal,
)


def test_triangular_key_points():
    assert triangular(25, 25, 50, 75) == 0       # left foot
    assert triangular(50, 25, 50, 75) == 1       # peak
    assert triangular(75, 25, 50, 75) == 0       # right foot
    assert triangular(37.5, 25, 50, 75) == pytest.approx(0.5)


def test_trapezoidal_key_points():
    assert trapezoidal(60, 60, 80, 100, 100) == 0
    assert trapezoidal(70, 60, 80, 100, 100) == pytest.approx(0.5)
    assert trapezoidal(90, 60, 80, 100, 100) == 1    # plateau
    assert trapezoidal(100, 60, 80, 100, 100) == 1   # shoulder reaches the end


def test_shoulder_with_vertical_edge():
    assert trapezoidal(0, 0, 0, 20, 40) == 1          # Dry is fully true at 0
    assert trapezoidal(30, 0, 0, 20, 40) == pytest.approx(0.5)


def test_hand_calculated_membership():
    # Soil 28 %: Dry falls from 1 at 20 to 0 at 40 -> (40-28)/20 = 0.6
    #            Medium rises from 0 at 25 to 1 at 50 -> (28-25)/25 = 0.12
    degrees = SOIL_MOISTURE.fuzzify(28)
    assert degrees["dry"] == pytest.approx(0.6)
    assert degrees["medium"] == pytest.approx(0.12)
    assert degrees["wet"] == 0


@pytest.mark.parametrize("variable", [SOIL_MOISTURE, TEMPERATURE, HUMIDITY, IRRIGATION])
def test_every_value_in_range_is_covered_and_valid(variable):
    """Membership is always between 0 and 1, and every value belongs to some set."""
    for x in np.linspace(variable.min_value, variable.max_value, 501):
        degrees = variable.fuzzify(x).values()
        assert all(0 <= d <= 1 for d in degrees)
        assert max(degrees) > 0, f"{variable.label}: no set covers {x}"


def test_fuzzify_all_structure():
    result = fuzzify_all(28, 34, 40)
    assert set(result) == {"soil_moisture", "temperature", "humidity"}
    assert set(result["temperature"]) == {"cold", "normal", "hot"}
