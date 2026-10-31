import { RANGES, labelOf } from "../utils";

function MembershipBars({ title, degrees }) {
  return (
    <div className="membership-group">
      <h3>{title}</h3>
      {Object.entries(degrees).map(([name, degree]) => (
        <div className="bar-row" key={name}>
          <span className="bar-name">{labelOf(name)}</span>
          <span className="bar-track" aria-hidden="true">
            <span className="bar-fill" style={{ width: `${degree * 100}%` }} />
          </span>
          <span className="bar-value">{degree.toFixed(2)}</span>
        </div>
      ))}
    </div>
  );
}

export default function FuzzyAnalysis({ result }) {
  if (!result) return null;
  return (
    <section className="panel">
      <h2>Fuzzy analysis</h2>
      <h3 className="sub">Step 1 – Fuzzification: membership degree of each input</h3>
      <div className="membership-grid">
        {Object.entries(result.membership_values).map(([key, degrees]) => (
          <MembershipBars key={key} title={RANGES[key].label} degrees={degrees} />
        ))}
      </div>

      <h3 className="sub">Step 2 – Rules that fired (strength = minimum of the conditions)</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Rule</th>
              <th>Condition and result</th>
              <th className="num">Strength</th>
            </tr>
          </thead>
          <tbody>
            {result.activated_rules.map((rule) => (
              <tr key={rule.id}>
                <td>R{rule.id}</td>
                <td>
                  {rule.description}
                  <div className="reason">{rule.reason}</div>
                </td>
                <td className="num">{rule.strength.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
