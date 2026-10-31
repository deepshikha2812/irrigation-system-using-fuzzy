import { useState } from "react";
import { PRESETS, RANGES } from "../utils";

export default function InputForm({ onAnalyze, loading }) {
  const [values, setValues] = useState({ soil_moisture: "28", temperature: "34", humidity: "40" });
  const [errors, setErrors] = useState({});

  const validate = () => {
    const found = {};
    for (const [key, range] of Object.entries(RANGES)) {
      const text = values[key].trim();
      const number = Number(text);
      if (text === "" || Number.isNaN(number)) found[key] = "Enter a number";
      else if (number < range.min || number > range.max)
        found[key] = `Must be between ${range.min} and ${range.max}`;
    }
    setErrors(found);
    return Object.keys(found).length === 0;
  };

  const submit = (event) => {
    event.preventDefault();
    if (!validate()) return;
    onAnalyze({
      soil_moisture: Number(values.soil_moisture),
      temperature: Number(values.temperature),
      humidity: Number(values.humidity),
    });
  };

  const usePreset = (preset) => {
    setErrors({});
    setValues({
      soil_moisture: String(preset.soil_moisture),
      temperature: String(preset.temperature),
      humidity: String(preset.humidity),
    });
  };

  return (
    <section className="panel">
      <h2>Sensor readings</h2>
      <form onSubmit={submit} noValidate>
        {Object.entries(RANGES).map(([key, range]) => (
          <div className="field" key={key}>
            <label htmlFor={key}>
              {range.label} ({range.unit}), {range.min}–{range.max}
            </label>
            <input
              id={key}
              type="number"
              step="any"
              value={values[key]}
              onChange={(e) => setValues({ ...values, [key]: e.target.value })}
              aria-invalid={Boolean(errors[key])}
            />
            {errors[key] && <p className="field-error">{errors[key]}</p>}
          </div>
        ))}
        <button type="submit" className="primary" disabled={loading}>
          {loading ? "Analyzing…" : "Analyze"}
        </button>
      </form>
      <div className="presets">
        <p className="hint">Try an example:</p>
        {PRESETS.map((preset) => (
          <button type="button" key={preset.name} className="secondary" onClick={() => usePreset(preset)}>
            {preset.name}
          </button>
        ))}
      </div>
    </section>
  );
}
