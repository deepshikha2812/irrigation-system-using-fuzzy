export default function ResultCard({ result }) {
  if (!result) {
    return (
      <section className="panel result">
        <h2>Result</h2>
        <p className="hint">Enter the readings and press Analyze to see the irrigation level.</p>
      </section>
    );
  }
  return (
    <section className="panel result">
      <h2>Result</h2>
      <p className="level">
        {result.irrigation_level.toFixed(1)}
        <span>%</span>
      </p>
      <p className="level-caption">Irrigation level (defuzzified, centroid)</p>
      <dl>
        <dt>Category</dt>
        <dd>
          <span className={`badge badge-${result.category.toLowerCase().replace(" ", "-")}`}>
            {result.category}
          </span>
        </dd>
        <dt>Recommendation</dt>
        <dd>{result.recommendation}</dd>
      </dl>
      <p className="hint">
        The category is the output fuzzy set that fired most strongly. The percentage is the
        centroid of all fired rules combined, so the two can differ slightly.
      </p>
      {!result.saved && <p className="hint">This analysis was not saved.</p>}
    </section>
  );
}
