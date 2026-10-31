"""Fuzzy sets, membership functions and fuzzification.

A *linguistic variable* (e.g. "soil moisture") has a numeric range and several
*fuzzy sets* (e.g. dry / medium / wet). Each fuzzy set has a *membership
function* that maps a crisp number to a degree of membership between 0 and 1.

NOTE: every range and breakpoint below is a PROJECT ASSUMPTION chosen for
demonstration. They are not calibrated for any real plant.
"""
from dataclasses import dataclass, field

import numpy as np


# ---------------------------------------------------------------------------
# 1. Shape functions
# ---------------------------------------------------------------------------
def trapezoidal(x, a: float, b: float, c: float, d: float):
    """Trapezoid: 0 below a, rises to 1 at b, stays 1 until c, falls to 0 at d.

    If a == b (or c == d) the shape has a vertical edge, which is how we make
    "shoulder" sets such as Dry (full membership right from 0).
    Works for a single number or a NumPy array.
    """
    x = np.asarray(x, dtype=float)

    if b > a:
        rising = (x - a) / (b - a)
    else:  # vertical left edge
        rising = np.where(x >= a, 1.0, 0.0)

    if d > c:
        falling = (d - x) / (d - c)
    else:  # vertical right edge
        falling = np.where(x <= d, 1.0, 0.0)

    return np.clip(np.minimum(rising, falling), 0.0, 1.0)


def triangular(x, a: float, b: float, c: float):
    """Triangle: 0 at a, peak 1 at b, 0 at c. A trapezoid whose top has width 0."""
    return trapezoidal(x, a, b, b, c)


# ---------------------------------------------------------------------------
# 2. Data structures
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FuzzySet:
    """One fuzzy set: a name, a shape and its corner points."""
    name: str
    shape: str            # "triangular" (3 points) or "trapezoidal" (4 points)
    points: tuple

    def membership(self, x):
        if self.shape == "triangular":
            return triangular(x, *self.points)
        return trapezoidal(x, *self.points)


@dataclass(frozen=True)
class LinguisticVariable:
    """A variable such as soil moisture, with its range and its fuzzy sets."""
    label: str
    unit: str
    min_value: float
    max_value: float
    sets: dict = field(default_factory=dict)
    plot_step: float = 1.0   # spacing of points when drawing curves

    def fuzzify(self, value: float) -> dict:
        """Fuzzification: crisp value -> {set name: membership degree}."""
        return {name: float(fs.membership(value)) for name, fs in self.sets.items()}


# ---------------------------------------------------------------------------
# 3. The fuzzy sets of this project  (points: a, b, c[, d])
# ---------------------------------------------------------------------------
SOIL_MOISTURE = LinguisticVariable(
    label="Soil Moisture", unit="%", min_value=0, max_value=100,
    sets={
        "dry":    FuzzySet("dry",    "trapezoidal", (0, 0, 20, 40)),
        "medium": FuzzySet("medium", "triangular",  (25, 50, 75)),
        "wet":    FuzzySet("wet",    "trapezoidal", (60, 80, 100, 100)),
    },
)

TEMPERATURE = LinguisticVariable(
    label="Temperature", unit="°C", min_value=0, max_value=45, plot_step=0.5,
    sets={
        "cold":   FuzzySet("cold",   "trapezoidal", (0, 0, 10, 20)),
        "normal": FuzzySet("normal", "triangular",  (15, 25, 35)),
        "hot":    FuzzySet("hot",    "trapezoidal", (30, 38, 45, 45)),
    },
)

HUMIDITY = LinguisticVariable(
    label="Humidity", unit="%", min_value=0, max_value=100,
    sets={
        "low":    FuzzySet("low",    "trapezoidal", (0, 0, 25, 45)),
        "medium": FuzzySet("medium", "triangular",  (30, 50, 70)),
        "high":   FuzzySet("high",   "trapezoidal", (55, 75, 100, 100)),
    },
)

IRRIGATION = LinguisticVariable(
    label="Irrigation Level", unit="%", min_value=0, max_value=100,
    sets={
        "very_low":  FuzzySet("very_low",  "trapezoidal", (0, 0, 10, 25)),
        "low":       FuzzySet("low",       "triangular",  (10, 25, 40)),
        "medium":    FuzzySet("medium",    "triangular",  (30, 50, 70)),
        "high":      FuzzySet("high",      "triangular",  (60, 75, 90)),
        "very_high": FuzzySet("very_high", "trapezoidal", (75, 90, 100, 100)),
    },
)

INPUT_VARIABLES = {
    "soil_moisture": SOIL_MOISTURE,
    "temperature": TEMPERATURE,
    "humidity": HUMIDITY,
}


# ---------------------------------------------------------------------------
# 4. Helpers
# ---------------------------------------------------------------------------
def label_of(set_name: str) -> str:
    """'very_high' -> 'Very High'"""
    return set_name.replace("_", " ").title()


def fuzzify_all(soil_moisture: float, temperature: float, humidity: float) -> dict:
    """Fuzzify the three crisp inputs. Returns {variable: {set: degree}}."""
    crisp = {"soil_moisture": soil_moisture, "temperature": temperature, "humidity": humidity}
    return {key: INPUT_VARIABLES[key].fuzzify(value) for key, value in crisp.items()}


def describe_variables() -> dict:
    """Curve data for every variable, used by the frontend to draw the charts."""
    result = {}
    for key, var in {**INPUT_VARIABLES, "irrigation": IRRIGATION}.items():
        universe = np.arange(var.min_value, var.max_value + var.plot_step / 2, var.plot_step)
        result[key] = {
            "label": var.label,
            "unit": var.unit,
            "min": var.min_value,
            "max": var.max_value,
            "universe": universe.tolist(),
            "sets": {n: np.round(fs.membership(universe), 4).tolist() for n, fs in var.sets.items()},
            "parameters": {n: {"shape": fs.shape, "points": list(fs.points)} for n, fs in var.sets.items()},
        }
    return result
