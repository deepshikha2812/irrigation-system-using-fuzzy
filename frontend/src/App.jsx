import { useEffect, useState } from "react";
import { getHistory, getMembershipFunctions, predict } from "./api";
import FuzzyAnalysis from "./components/FuzzyAnalysis";
import HistoryChart from "./components/HistoryChart";
import HistoryTable from "./components/HistoryTable";
import InputForm from "./components/InputForm";
import MembershipCharts from "./components/MembershipCharts";
import ResultCard from "./components/ResultCard";

export default function App() {
  const [curves, setCurves] = useState(null);
  const [history, setHistory] = useState([]);
  const [inputs, setInputs] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getMembershipFunctions(), getHistory()])
      .then(([curveData, historyData]) => {
        setCurves(curveData);
        setHistory(historyData);
      })
      .catch((e) => setError(e.message));
  }, []);

  const analyze = async (values) => {
    setLoading(true);
    setError("");
    try {
      const data = await predict(values);
      setInputs(values);
      setResult(data);
      setHistory(await getHistory());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <header>
        <h1>Smart Plant Irrigation System</h1>
        <p>Mamdani fuzzy inference: soil moisture, temperature and humidity decide the irrigation level.</p>
      </header>

      {error && <div className="alert" role="alert">{error}</div>}

      <main>
        <div className="top-row">
          <InputForm onAnalyze={analyze} loading={loading} />
          <ResultCard result={result} />
        </div>
        <FuzzyAnalysis result={result} />
        <MembershipCharts curves={curves} inputs={inputs} result={result} />
        <HistoryChart history={history} />
        <HistoryTable history={history} />
      </main>

      <footer>
        Academic demonstration. Membership ranges and rules are project assumptions and are not
        calibrated for any specific plant.
      </footer>
    </div>
  );
}
