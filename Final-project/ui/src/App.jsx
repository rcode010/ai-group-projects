import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './index.css';

const API = 'http://localhost:5001';

function badgeClass(v) {
  if (v >= 0.85) return 'badge-good';
  if (v >= 0.70) return 'badge-mid';
  return 'badge-low';
}

function AutoInput({ label, id, value, onChange, suggestions = [] }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const filtered = value.length > 0
    ? suggestions.filter(s => s.toLowerCase().includes(value.toLowerCase())).slice(0, 8)
    : [];

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div className="form-group" ref={ref}>
      <label htmlFor={id}>{label}</label>
      <div className="input-wrap">
        <input
          id={id}
          value={value}
          placeholder={`Type ${label.toLowerCase()}…`}
          autoComplete="off"
          onChange={e => { onChange(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
        />
        {open && filtered.length > 0 && (
          <ul className="suggestions">
            {filtered.map(s => (
              <li key={s} onMouseDown={() => { onChange(s); setOpen(false); }}>{s}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function ResultCard({ modelName, result, delay }) {
  const isDangerous = result.label === 'Dangerous';
  const cls = isDangerous ? 'dangerous' : 'safe';
  const icon = isDangerous ? '⚠️' : '✅';
  const conf = result.confidence;

  return (
    <div className={`result-card ${cls}`} style={{ animationDelay: `${delay}ms` }}>
      <div className="model-name">{modelName.replace('_', ' ')}</div>
      <div className={`verdict ${cls}`}>{icon} {result.label}</div>
      <div className="conf-label">
        <span>Confidence</span><span>{conf}%</span>
      </div>
      <div className="conf-bar">
        <div
          className={`conf-fill ${isDangerous ? 'dangerous' : 'conf-fill-safe'}`}
          style={{ width: `${conf}%` }}
        />
      </div>
    </div>
  );
}

function FeatureImportancePanel() {
  const [data, setData] = useState(null);
  const [err, setErr]   = useState(null);

  useEffect(() => {
    axios.get(`${API}/feature-importance`)
      .then(r => {
        if (r.data.error) { setErr(r.data.error); return; }
        const sorted = [...r.data].sort((a, b) => b.Chi2_Score - a.Chi2_Score);
        setData(sorted);
      })
      .catch(() => setErr('Could not load feature importance. Is the API running?'));
  }, []);

  if (err)  return <div className="alert alert-error">{err}</div>;
  if (!data) return <div className="alert alert-info">Loading feature importance…</div>;

  const maxChi2 = Math.max(...data.map(d => d.Chi2_Score));

  return (
    <>
      <p style={{ fontSize: '0.85rem', color: 'var(--muted)', marginBottom: 20 }}>
        Chi-Squared score: higher = stronger statistical link to the target label.
      </p>
      {data.map((row, i) => (
        <div className="fi-row" key={i}>
          <div className="fi-label">{row.Feature}</div>
          <div className="fi-bar-wrap">
            <div className="fi-bar" style={{ width: `${(row.Chi2_Score / maxChi2) * 100}%` }} />
          </div>
          <div className="fi-score">{Number(row.Chi2_Score).toFixed(1)}</div>
        </div>
      ))}
    </>
  );
}

function EvaluationPanel() {
  const [data, setData] = useState(null);
  const [err, setErr]   = useState(null);

  useEffect(() => {
    axios.get(`${API}/evaluation`)
      .then(r => {
        if (r.data.error) { setErr(r.data.error); return; }
        setData(r.data);
      })
      .catch(() => setErr('Could not load evaluation. Is the API running?'));
  }, []);

  if (err)  return <div className="alert alert-error">{err}</div>;
  if (!data) return <div className="alert alert-info">Loading evaluation results…</div>;

  return (
    <>
      <p style={{ fontSize: '0.85rem', color: 'var(--muted)', marginBottom: 20 }}>
        Sorted by F1-Score — the best balanced metric for imbalanced datasets.
      </p>
      <div style={{ overflowX: 'auto' }}>
        <table className="metrics-table">
          <thead>
            <tr>
              <th>#</th><th>Model</th>
              <th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1-Score</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                <td>{row.Rank ?? i + 1}</td>
                <td style={{ fontWeight: 600 }}>{row.Model}</td>
                {['Accuracy','Precision','Recall','F1-Score'].map(m => (
                  <td key={m}>
                    <span className={`metric-badge ${badgeClass(row[m])}`}>
                      {(row[m] * 100).toFixed(1)}%
                    </span>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="alert alert-info" style={{ marginTop: 20, fontSize: '0.82rem' }}>
        <strong>Note:</strong> Recall is the most critical metric here — missing a Dangerous animal
        is a more serious error than a false alarm. Prefer the model with the highest Recall.
      </div>
    </>
  );
}

function App() {
  const [tab, setTab]             = useState('predict');
  const [knownValues, setKnown]   = useState({});
  const [animal, setAnimal]       = useState('');
  const [symptoms, setSymptoms]   = useState(['', '', '', '', '']);
  const [loading, setLoading]     = useState(false);
  const [results, setResults]     = useState(null);
  const [error, setError]         = useState(null);

  useEffect(() => {
    axios.get(`${API}/metadata`)
      .then(r => setKnown(r.data))
      .catch(() => {});
  }, []);

  function updateSymptom(idx, val) {
    setSymptoms(prev => { const s = [...prev]; s[idx] = val; return s; });
  }

  async function handlePredict(e) {
    e.preventDefault();
    setError(null); setResults(null); setLoading(true);
    try {
      const res = await axios.post(`${API}/predict`, {
        animal_name: animal,
        symptom1: symptoms[0], symptom2: symptoms[1],
        symptom3: symptoms[2], symptom4: symptoms[3],
        symptom5: symptoms[4],
      });
      if (res.data.error) {
        setError(res.data.error);
      } else {
        setResults(res.data);
      }
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
         setError(err.response.data.error);
      } else {
         setError('Cannot reach the API. Make sure python main.py is running.');
      }
    } finally {
      setLoading(false);
    }
  }

  const MODEL_LABELS = {
    neural_network: 'Neural Network',
    knn:            'k-Nearest Neighbors',
    naive_bayes:    'Naïve Bayes',
    svm:            'Support Vector Machine',
  };

  const allFilled = animal.trim() && symptoms.every(s => s.trim());

  return (
    <>
      <header>
        <div className="container">
          <div className="header-inner">
            <div className="logo">🐾</div>
            <div className="header-text">
              <h1>Animal Condition Classifier</h1>
              <p>AI-powered diagnosis using Neural Network · kNN · Naïve Bayes · SVM</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container">
        <div className="tabs">
          {[
            { key: 'predict', label: '🔍 Predict' },
            { key: 'evaluation', label: '📊 Model Evaluation' },
            { key: 'features', label: '📈 Feature Importance' },
          ].map(t => (
            <button key={t.key} className={`tab-btn${tab === t.key ? ' active' : ''}`}
              onClick={() => setTab(t.key)}>{t.label}</button>
          ))}
        </div>

        {tab === 'predict' && (
          <>
            <div className="card">
              <div className="section-title">Animal Information</div>
              <form onSubmit={handlePredict}>
                <div className="form-grid">
                  <AutoInput
                    label="Animal Name"
                    id="animal_name"
                    value={animal}
                    onChange={setAnimal}
                    suggestions={knownValues['AnimalName'] || []}
                  />
                  <div />
                  {symptoms.map((s, i) => (
                    <AutoInput
                      key={i}
                      label={`Symptom ${i + 1}`}
                      id={`symptom${i + 1}`}
                      value={s}
                      onChange={v => updateSymptom(i, v)}
                      suggestions={knownValues[`symptoms${i + 1}`] || []}
                    />
                  ))}
                  <button
                    type="submit"
                    className="btn-predict"
                    disabled={loading || !allFilled}
                  >
                    {loading
                      ? <><span className="spinner" /> Analyzing…</>
                      : '🔮 Classify Condition'}
                  </button>
                </div>
              </form>
            </div>

            {error && <div className="alert alert-error">⚠️ {error}</div>}

            {results && (
              <div className="card">
                <div className="section-title">Predictions — {results.animal_name}</div>
                <div className="results-grid">
                  {Object.entries(results.predictions).map(([key, val], i) => (
                    <ResultCard
                      key={key}
                      modelName={MODEL_LABELS[key] || key}
                      result={val}
                      delay={i * 80}
                    />
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {tab === 'evaluation' && (
          <div className="card">
            <div className="section-title">Model Performance Comparison</div>
            <EvaluationPanel />
          </div>
        )}

        {tab === 'features' && (
          <div className="card">
            <div className="section-title">Feature Importance (Chi-Squared)</div>
            <FeatureImportancePanel />
          </div>
        )}
      </main>

      <footer>
        <div className="container">
          Animal Condition Classification System &mdash; AI Final Project &mdash; Team of 5
        </div>
      </footer>
    </>
  );
}

export default App;
