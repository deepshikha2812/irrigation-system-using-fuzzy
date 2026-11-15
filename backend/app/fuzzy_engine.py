"""Mamdani fuzzy inference engine.

Pipeline (each stage is its own small function):
    1. Fuzzification      crisp inputs      -> membership degrees
    2. Rule evaluation    degrees           -> firing strength of every rule (AND = min)
    3. Implication        strength + output -> clipped output fuzzy set
    4. Aggregation        all clipped sets  -> one combined shape (OR = max)
    5. Defuzzification    combined shape    -> one number (centroid)
"""
import math

import numpy as np

from app.membership_functions import (
    HUMIDITY, INPUT_VARIABLES, IRRIGATION, SOIL_MOISTURE, TEMPERATURE,
    fuzzify_all, label_of,
)
from app.rules import RULES, Rule

# Output universe: 0, 0.1, 0.2 ... 100  (fine grid for an accurate centroid)
OUTPUT_UNIVERSE = np.linspace(IRRIGATION.min_value, IRRIGATION.max_value, 1001)

RECOMMENDATIONS = {
    "very_low":  "Very low irrigation: no watering is needed right now.",
    "low":       "Low irrigation: a light watering is enough.",
    "medium":    "Medium irrigation: water moderately.",
    "high":      "High irrigation: water generously.",
    "very_high": "Very high irrigation: water immediately and thoroughly.",
}


# input validation
def validate_inputs(soil_moisture: float, temperature: float, humidity: float) -> None:
    """Raise ValueError if an input is not a finite number inside its range."""
    values = {"soil_moisture": soil_moisture, "temperature": temperature, "humidity": humidity}
    for key, value in values.items():
        variable = INPUT_VARIABLES[key]
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise ValueError(f"{variable.label} must be a number")
        if not variable.min_value <= value <= variable.max_value:
            raise ValueError(
                f"{variable.label} must be between {variable.min_value} and "
                f"{variable.max_value} {variable.unit}"
            )


# stage 2: rule evaluation 
def rule_firing_strength(rule: Rule, memberships: dict) -> float:
    """Firing strength = smallest membership among the rule's conditions (AND = min)."""
    degrees = [memberships[variable][set_name] for variable, set_name in rule.conditions().items()]
    return min(degrees)


def evaluate_rules(memberships: dict, rules: list[Rule] = RULES) -> list[tuple[Rule, float]]:
    """Firing strength of every rule, as (rule, strength) pairs."""
    return [(rule, rule_firing_strength(rule, memberships)) for rule in rules]


# stages 3 + 4: implication and aggregation
def aggregate_output(rule_strengths: list[tuple[Rule, float]]) -> np.ndarray:
    """Mamdani implication (clip with min) followed by aggregation (max)."""
    aggregated = np.zeros_like(OUTPUT_UNIVERSE)
    for rule, strength in rule_strengths:
        if strength == 0:
            continue  # rule is not active
        output_curve = IRRIGATION.sets[rule.irrigation].membership(OUTPUT_UNIVERSE)
        clipped = np.minimum(strength, output_curve)      # implication
        aggregated = np.maximum(aggregated, clipped)       # aggregation
    return aggregated


#  5: defuzzification 
def centroid(universe: np.ndarray, membership: np.ndarray) -> float:
    """Centre of gravity: sum(x * membership) / sum(membership)."""
    total = membership.sum()
    if total == 0:
        raise ValueError("No rule fired, so the output cannot be defuzzified")
    return float((universe * membership).sum() / total)


#category (separate from the crisp number) 
def output_set_strengths(rule_strengths: list[tuple[Rule, float]]) -> dict:
    """Strongest firing strength reaching each output fuzzy set."""
    strengths = {name: 0.0 for name in IRRIGATION.sets}
    for rule, strength in rule_strengths:
        strengths[rule.irrigation] = max(strengths[rule.irrigation], strength)
    return strengths


def choose_category(set_strengths: dict, level: float) -> str:
    """Category = the output set that is activated the most.
    If two sets tie, the one with higher membership at the crisp level wins."""
    return max(set_strengths,
               key=lambda name: (set_strengths[name], float(IRRIGATION.sets[name].membership(level))))


#public function 
def calculate_irrigation(soil_moisture: float, temperature: float, humidity: float) -> dict:
    """Run the full Mamdani pipeline and return the result with the fuzzy analysis."""
    validate_inputs(soil_moisture, temperature, humidity)

    memberships = fuzzify_all(soil_moisture, temperature, humidity)      # 1
    rule_strengths = evaluate_rules(memberships)                          # 2
    aggregated = aggregate_output(rule_strengths)                         # 3 + 4
    level = centroid(OUTPUT_UNIVERSE, aggregated)                         # 5

    set_strengths = output_set_strengths(rule_strengths)
    category_key = choose_category(set_strengths, level)

    activated = sorted(
        ({
            "id": rule.id,
            "description": rule.describe(),
            "strength": round(strength, 4),
            "output": label_of(rule.irrigation),
            "reason": rule.reason,
        } for rule, strength in rule_strengths if strength > 0),
        key=lambda item: item["strength"], reverse=True,
    )

    return {
        "irrigation_level": round(level, 2),
        "category": label_of(category_key),
        "recommendation": RECOMMENDATIONS[category_key],
        "membership_values": {
            variable: {name: round(degree, 4) for name, degree in degrees.items()}
            for variable, degrees in memberships.items()
        },
        "output_strengths": {name: round(s, 4) for name, s in set_strengths.items()},
        "activated_rules": activated,
        "aggregated_output": {  # every 10th point -> 0, 1, 2 ... 100
            "universe": OUTPUT_UNIVERSE[::10].tolist(),
            "membership": np.round(aggregated[::10], 4).tolist(),
        },
    }
