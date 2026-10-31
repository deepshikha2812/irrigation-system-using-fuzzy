import MembershipChart from "./MembershipChart";

const INPUT_KEYS = ["soil_moisture", "temperature", "humidity"];

export default function MembershipCharts({ curves, inputs, result }) {
  if (!curves) return null;
  return (
    <section className="panel">
      <h2>Membership functions</h2>
      <p className="hint">
        Each curve shows how strongly a value belongs to a fuzzy set. The dashed line marks the
        last analyzed input; where it crosses a curve is that set's membership degree.
      </p>
      <div className="chart-grid">
        {INPUT_KEYS.map((key) => (
          <MembershipChart
            key={key}
            title={`${curves[key].label} (${curves[key].unit})`}
            curve={curves[key]}
            currentValue={inputs ? inputs[key] : undefined}
          />
        ))}
        <MembershipChart
          title="Irrigation level: combined output and centroid"
          curve={curves.irrigation}
          aggregated={result ? result.aggregated_output : undefined}
          currentValue={result ? result.irrigation_level : undefined}
        />
      </div>
      {result && (
        <p className="hint">
          The shaded area is the aggregation of every clipped output set. The dashed line on the
          last chart is its centroid, the final irrigation level.
        </p>
      )}
    </section>
  );
}
