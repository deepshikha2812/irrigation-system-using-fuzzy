import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

export default function HistoryChart({ history }) {
  if (history.length < 2) {
    return (
      <section className="panel">
        <h2>Irrigation history chart</h2>
        <p className="hint">The chart appears after at least two saved predictions.</p>
      </section>
    );
  }
  // History arrives newest first; the chart reads oldest to newest.
  const rows = [...history].reverse().map((row) => ({
    id: `#${row.id}`,
    irrigation: row.irrigation_level,
    soil: row.soil_moisture,
  }));

  return (
    <section className="panel">
      <h2>Irrigation history chart</h2>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={rows} margin={{ top: 8, right: 12, bottom: 4, left: -12 }}>
          <CartesianGrid stroke="#e3e7ea" strokeDasharray="3 3" />
          <XAxis dataKey="id" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(v) => `${Number(v).toFixed(1)}%`} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Line dataKey="irrigation" name="Irrigation level" stroke="#0f766e" strokeWidth={2} />
          <Line dataKey="soil" name="Soil moisture" stroke="#b45309" strokeWidth={2} strokeDasharray="5 3" />
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}
