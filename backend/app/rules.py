"""The fuzzy rule base.

Each rule has the form
    IF soil_moisture is X AND temperature is Y AND humidity is Z THEN irrigation is W
A condition set to None means "any value" (that variable is ignored by the rule).

Rules are plain data, so they are easy to read, explain and modify.
NOTE: the rules are PROJECT ASSUMPTIONS for demonstration, not agronomic advice.
"""
from dataclasses import dataclass

from app.membership_functions import INPUT_VARIABLES, IRRIGATION, label_of


@dataclass(frozen=True)
class Rule:
    id: int
    soil_moisture: str | None
    temperature: str | None
    humidity: str | None
    irrigation: str
    reason: str

    def conditions(self) -> dict:
        """The IF-part as {variable: fuzzy set}, skipping 'any' conditions."""
        all_conditions = {
            "soil_moisture": self.soil_moisture,
            "temperature": self.temperature,
            "humidity": self.humidity,
        }
        return {k: v for k, v in all_conditions.items() if v is not None}

    def describe(self) -> str:
        parts = [f"{INPUT_VARIABLES[k].label.lower()} is {label_of(v).upper()}"
                 for k, v in self.conditions().items()]
        return f"IF {' AND '.join(parts)} THEN irrigation is {label_of(self.irrigation).upper()}"


RULES: list[Rule] = [
     # Wet soil already has enough water, regardless of the weather.
    Rule(1, "wet", None, None, "very_low",
         "Wet soil already holds enough water, so irrigation is not needed."),

     # Dry soil needs water; the weather helps determine how much to add.
    Rule(2, "dry", "hot", "low", "very_high",
         "Dry soil with hot, dry air: water is lost fastest and there is no reserve."),
    Rule(3, "dry", "hot", "medium", "very_high",
         "Dry soil and heat; medium humidity does not slow evaporation enough."),
    Rule(4, "dry", "hot", "high", "high",
         "Dry soil and heat need much water, but humid air slows evaporation (one level lower)."),
    Rule(5, "dry", "normal", "low", "high",
         "Dry soil and dry air: strong need even at normal temperature."),
    Rule(6, "dry", "normal", "medium", "high",
         "Dry soil under ordinary conditions: the plant needs plenty of water."),
    Rule(7, "dry", "normal", "high", "medium",
         "Dry soil but humid air reduces water loss, so moderate watering."),
    Rule(8, "dry", "cold", "low", "medium",
         "Cold weather means little evaporation, but dry soil and dry air still need moderate watering."),
    Rule(9, "dry", "cold", "medium", "medium",
         "Dry soil in cold weather: moderate watering is enough."),
    Rule(10, "dry", "cold", "high", "low",
         "Dry soil, but cold and humid conditions lose very little water."),

     # With medium soil moisture, the weather helps determine whether to top up.
    Rule(11, "medium", "hot", "low", "high",
         "Soil is only half full and hot, dry air will drain it quickly."),
    Rule(12, "medium", "hot", "medium", "medium",
         "Heat speeds up drying, so a moderate top-up is useful."),
    Rule(13, "medium", "hot", "high", "low",
         "Heat is offset by humid air, so only a small top-up."),
    Rule(14, "medium", "normal", "low", "medium",
         "Dry air dries the soil faster, so a moderate top-up."),
    Rule(15, "medium", "normal", "medium", "medium",
         "Everything is average, so average irrigation."),
    Rule(16, "medium", "normal", "high", "low",
         "Humid air keeps the soil moist, so little irrigation is needed."),
    Rule(17, "medium", "cold", None, "low",
         "Cold weather evaporates little water, regardless of humidity."),
]


def validate_rule_base(rules: list[Rule] = RULES) -> None:
    """Sanity check: every set name used in a rule must really exist."""
    for rule in rules:
        if not rule.conditions():
            raise ValueError(f"Rule {rule.id} has no conditions")
        for variable_key, set_name in rule.conditions().items():
            if set_name not in INPUT_VARIABLES[variable_key].sets:
                raise ValueError(f"Rule {rule.id}: unknown set '{set_name}' for {variable_key}")
        if rule.irrigation not in IRRIGATION.sets:
            raise ValueError(f"Rule {rule.id}: unknown output set '{rule.irrigation}'")


validate_rule_base()
