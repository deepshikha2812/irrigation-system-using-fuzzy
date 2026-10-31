export default function HistoryTable({ history }) {
  return (
    <section className="panel">
      <h2>Prediction history</h2>
      {history.length === 0 ? (
        <p className="hint">No saved predictions yet. Press Analyze to create the first one.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Time</th>
                <th className="num">Soil (%)</th>
                <th className="num">Temp (°C)</th>
                <th className="num">Humidity (%)</th>
                <th className="num">Irrigation (%)</th>
                <th>Category</th>
              </tr>
            </thead>
            <tbody>
              {history.map((row) => (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td>{new Date(row.timestamp).toLocaleString()}</td>
                  <td className="num">{row.soil_moisture}</td>
                  <td className="num">{row.temperature}</td>
                  <td className="num">{row.humidity}</td>
                  <td className="num">{row.irrigation_level.toFixed(1)}</td>
                  <td>{row.irrigation_category}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
