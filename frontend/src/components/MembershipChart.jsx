import {
  Area, CartesianGrid, ComposedChart, Legend, Line, ReferenceLine,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { SET_COLORS, labelOf } from "../utils";

/**
 * Draws all fuzzy sets of one variable.
 *  - currentValue: vertical line at the crisp input (or at the defuzzified output)
 *  - aggregated:   optional shaded area (the combined Mamdani output shape)
 */
export default function MembershipChart({ title, curve, currentValue, aggregated }) {
  const setNames = Object.keys(curve.sets);
  const rows = curve.universe.map((x, i) => {
    const row = { x };
    setNames.forEach((name) => (row[name] = curve.sets[name][i]));
    if (aggregated) row.aggregated = aggregated.membership[i];
    return row;
  });

  return (
    <figure className="chart">
      <figcaption>{title}</figcaption>
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={rows} margin={{ top: 8, right: 12, bottom: 4, left: -12 }}>
          <CartesianGrid stroke="#e3e7ea" strokeDasharray="3 3" />
          <XAxis
            dataKey="x" type="number" domain={[curve.min, curve.max]}
            tick={{ fontSize: 12 }}
            label={{ value: curve.unit, position: "insideBottomRight", offset: -2, fontSize: 12 }}
          />
          <YAxis domain={[0, 1]} ticks={[0, 0.5, 1]} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(v) => Number(v).toFixed(2)} labelFormatter={(x) => `${curve.label}: ${x}${curve.unit}`} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {aggregated && (
            <Area
              dataKey="aggregated" name="Combined output" type="linear"
              stroke="none" fill="#1f2933" fillOpacity={0.18} isAnimationActive={false}
            />
          )}
          {setNames.map((name, i) => (
            <Line
              key={name} dataKey={name} name={labelOf(name)} type="linear" dot={false}
              stroke={SET_COLORS[i % SET_COLORS.length]} strokeWidth={2} isAnimationActive={false}
            />
          ))}
          {currentValue !== undefined && currentValue !== null && (
            <ReferenceLine x={currentValue} stroke="#1f2933" strokeDasharray="5 3" strokeWidth={1.5} />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </figure>
  );
}
