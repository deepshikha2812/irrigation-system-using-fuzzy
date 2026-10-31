"""Request/response shapes for the API (Pydantic). Also performs input validation."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.membership_functions import HUMIDITY, SOIL_MOISTURE, TEMPERATURE


class PredictionRequest(BaseModel):
    soil_moisture: float = Field(ge=SOIL_MOISTURE.min_value, le=SOIL_MOISTURE.max_value,
                                 description="Soil moisture in % (0-100)")
    temperature: float = Field(ge=TEMPERATURE.min_value, le=TEMPERATURE.max_value,
                               description="Temperature in °C (0-45)")
    humidity: float = Field(ge=HUMIDITY.min_value, le=HUMIDITY.max_value,
                            description="Relative humidity in % (0-100)")
    save: bool = Field(default=True, description="Save this prediction to the database")


class ActivatedRule(BaseModel):
    id: int
    description: str
    strength: float
    output: str
    reason: str


class AggregatedOutput(BaseModel):
    universe: list[float]
    membership: list[float]


class PredictionResponse(BaseModel):
    irrigation_level: float
    category: str
    recommendation: str
    membership_values: dict[str, dict[str, float]]
    output_strengths: dict[str, float]
    activated_rules: list[ActivatedRule]
    aggregated_output: AggregatedOutput
    saved: bool
    id: int | None = None


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    soil_moisture: float
    temperature: float
    humidity: float
    irrigation_level: float
    irrigation_category: str
    recommendation: str
