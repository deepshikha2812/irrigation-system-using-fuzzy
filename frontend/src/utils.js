// "very_high" -> "Very High"
export const labelOf = (key) =>
  key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

export const RANGES = {
  soil_moisture: { label: "Soil moisture", unit: "%", min: 0, max: 100 },
  temperature: { label: "Temperature", unit: "°C", min: 0, max: 45 },
  humidity: { label: "Humidity", unit: "%", min: 0, max: 100 },
};

// Same three test scenarios used in the backend tests.
export const PRESETS = [
  { name: "Dry and hot", soil_moisture: 20, temperature: 35, humidity: 30 },
  { name: "Wet soil", soil_moisture: 80, temperature: 25, humidity: 70 },
  { name: "Average", soil_moisture: 50, temperature: 25, humidity: 50 },
];

export const SET_COLORS = ["#b45309", "#1d4ed8", "#0f766e", "#7c3aed", "#be123c"];
