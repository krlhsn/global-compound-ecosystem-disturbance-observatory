import React, { useState } from "react";
import "./app.css";

const signals = [
  {
    id: "D",
    title: "Soil-moisture drought",
    source: "ERA5-Land · monthly aggregates",
    rule: "D = 1 when the three-month, depth-weighted root-zone moisture anomaly is at or below −1.0 SD against the fixed 1981–2000 calendar-month reference.",
    caution: "This is a root-zone soil-moisture proxy, not a universal definition of drought.",
    accent: "ochre"
  },
  {
    id: "F",
    title: "Unusually high burned area",
    source: "MCD64A1.061 · monthly burned area",
    rule: "F = 1 when valid burned-area fraction reaches the 90th percentile of positive training-period values for the ecoregion and calendar month, with a biome fallback.",
    caution: "Burned area is not synonymous with wildfire. Small burns and some cropland burning may be missed or less reliably mapped.",
    accent: "ember"
  },
  {
    id: "V",
    title: "Vegetation-greenness stress",
    source: "MOD13C2.061 · monthly NDVI",
    rule: "V = 1 when the cell/calendar-month NDVI anomaly is at or below −0.5 SD against the 2001–2016 reference. At least 80% of contributing area must pass the MOD13C2.061 pixel-reliability and DetailedQA filters.",
    caution: "MOD13C2 uses product-specific geospatial-contribution flags in DetailedQA bits 14–15; these are not snow/shadow flags. NDVI remains a greenness proxy, not a direct measurement of ecosystem health.",
    accent: "leaf"
  }
];

const categories = [
  { code: "NONE", title: "No compound event", formula: "0 or 1 positive indicator", explanation: "All three indicators are evaluable, but fewer than two are positive." },
  { code: "DF", title: "Drought + fire", formula: "D = 1 · F = 1 · V = 0", explanation: "Soil-moisture drought and unusually high burned-area activity occur together." },
  { code: "DV", title: "Drought + vegetation stress", formula: "D = 1 · F = 0 · V = 1", explanation: "Soil-moisture drought and low vegetation greenness occur together." },
  { code: "FV", title: "Fire + vegetation stress", formula: "D = 0 · F = 1 · V = 1", explanation: "Unusually high burned-area activity and low vegetation greenness occur together." },
  { code: "DFV", title: "All three signals", formula: "D = 1 · F = 1 · V = 1", explanation: "All three environmental indicators cross their proposed thresholds." },
  { code: "NOT_EVALUABLE", title: "Not evaluable", formula: "At least one signal is missing", explanation: "The binary outcome is left missing. An unavailable indicator is never treated as a zero." }
];

const modelRows = [
  ["M0", "Seasonal baseline", "Biome + target calendar month"],
  ["M1", "Drought-only", "Baseline + soil-moisture and drought history"],
  ["M2", "Fire-history-only", "Baseline + burned fraction and fire history"],
  ["M3", "Vegetation-only", "Baseline + NDVI anomaly and vegetation history"],
  ["M4", "Combined", "D/F/V histories + temperature and precipitation"]
];

const sources = [
  ["ERA5-Land monthly aggregates", "Soil water, temperature and precipitation", "https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_MONTHLY_AGGR"],
  ["MOD13C2.061", "NASA LP DAAC monthly NDVI and pixel-quality product", "https://doi.org/10.5067/MODIS/MOD13C2.061"],
  ["MCD64A1.061", "Monthly burned area and pixel-level quality", "https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD64A1"],
  ["RESOLVE Ecoregions 2017", "846 terrestrial ecoregions, 14 biomes and 8 realms", "https://developers.google.com/earth-engine/datasets/catalog/RESOLVE_ECOREGIONS_2017"]
];

export default function App() {
  const [signal, setSignal] = useState("D");
  const [category, setCategory] = useState("DFV");
  const [horizon, setHorizon] = useState("1");
  const [expandedModel, setExpandedModel] = useState("M4");
  const activeSignal = signals.find((item) => item.id === signal);
  const activeCategory = categories.find((item) => item.code === category);

  return (
    <main className="observatory">
      <a className="skip-link" href="#main">Skip to content</a>
      <header className="topbar">
        <a className="wordmark" href="#top" aria-label="Ecosystem Observatory home">
          <span className="wordmark-icon">◉</span><span>ECOSYSTEM<span className="wordmark-light"> OBSERVATORY</span></span>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#signals">Signals</a><a href="#method">Method</a><a href="#models">Models</a><a href="#sources">Sources</a>
        </nav>
        <span className="status"><i /> Research prototype</span>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">GLOBAL ENVIRONMENTAL RESEARCH · PROBABILITY FOR AI</p>
          <h1>When ecosystems<br /><em>disturb together.</em></h1>
          <p className="hero-lede">Can drought, burned-area activity and vegetation stress reveal a compound disturbance signal across the world's terrestrial ecosystems?</p>
          <div className="hero-actions"><a className="primary-link" href="#method">Explore the framework <span>↗</span></a><a className="secondary-link" href="https://github.com/krlhsn/global-compound-ecosystem-disturbance-observatory/blob/main/RESEARCH_PROTOCOL.md" target="_blank" rel="noreferrer">Read the research protocol ↗</a></div>
          <div className="hero-meta"><span>0.5° global grid</span><b>·</b><span>Monthly observations</span><b>·</b><span>2001–2024 target window</span></div>
        </div>
        <div className="hero-visual" role="img" aria-label="Abstract globe with overlapping drought, fire and vegetation signals">
          <div className="orbit orbit-one" /><div className="orbit orbit-two" />
          <div className="globe"><div className="globe-grid" /><div className="land land-a" /><div className="land land-b" /><div className="land land-c" /><span className="globe-dot dot-one" /><span className="globe-dot dot-two" /><span className="globe-dot dot-three" /></div>
          <div className="signal-tag tag-d"><b>D</b><span>MOISTURE</span></div>
          <div className="signal-tag tag-f"><b>F</b><span>BURNED AREA</span></div>
          <div className="signal-tag tag-v"><b>V</b><span>GREENNESS</span></div>
          <div className="visual-caption">THREE PROXIES · ONE PROBABILISTIC QUESTION</div>
        </div>
        <div className="hero-foot"><span>RESEARCH FRAMEWORK</span><b>Remote-sensing indicators · probabilistic models · ecological regions</b><span className="foot-mark">01 / 08</span></div>
      </section>

      <div className="notice" role="status"><span className="notice-mark">i</span><p><strong>Research interface, not a results dashboard.</strong> This release presents the research specification and analysis software. It contains no empirical event counts, regional rankings, model scores or simulated substitutes for environmental observations.</p></div>

      <section className="section intro" id="main">
        <div className="section-kicker">THE RESEARCH QUESTION <span>01 — 08</span></div>
        <div className="intro-grid">
          <h2>Disturbances rarely<br /><em>exist in isolation.</em></h2>
          <div><p className="body-copy">Environmental pressures can overlap. A period of low soil moisture may coincide with unusually high burned-area activity and reduced vegetation greenness. This project asks whether those signals, considered together, can help estimate the probability of a compound event.</p><p className="body-copy muted">The study is retrospective. It is not an operational warning service and does not claim that any one proxy explains why an ecosystem changed.</p></div>
        </div>
      </section>

      <section className="section signals-section" id="signals">
        <div className="section-kicker">THREE ENVIRONMENTAL SIGNALS <span>02 — 08</span></div>
        <div className="section-heading"><h2>Different measurements.<br /><em>Different blind spots.</em></h2><p>Choose a signal to inspect its proposed rule and the limits that must travel with any interpretation.</p></div>
        <div className="signal-explorer">
          <div className="signal-tabs" role="tablist" aria-label="Environmental indicators">
            {signals.map((item) => <button key={item.id} role="tab" aria-selected={signal === item.id} className={"signal-tab " + item.accent + (signal === item.id ? " selected" : "")} onClick={() => setSignal(item.id)}><span>{item.id}</span><b>{item.title}</b><i>↗</i></button>)}
          </div>
          <article className={"signal-detail " + activeSignal.accent} role="tabpanel" aria-live="polite">
            <div className="detail-label"><span>INDICATOR {activeSignal.id}</span><span>PROPOSED OPERATIONAL DEFINITION</span></div>
            <p className="source-line">{activeSignal.source}</p><h3>{activeSignal.title}</h3><p className="definition">{activeSignal.rule}</p>
            <div className="caution"><span>INTERPRETATION LIMIT</span><p>{activeSignal.caution}</p></div>
          </article>
        </div>
      </section>

      <section className="section event-section">
        <div className="section-kicker">THE EVENT DEFINITION <span>03 — 08</span></div>
        <div className="section-heading"><h2>At least two signals<br /><em>must be present.</em></h2><p>All three indicators must be evaluable. Missing values remain unknown; they are never silently converted into zeros.</p></div>
        <div className="event-explorer">
          <div className="event-tabs" role="tablist" aria-label="Compound event categories">
            {categories.map((item) => <button key={item.code} role="tab" aria-selected={category === item.code} className={category === item.code ? "active" : ""} onClick={() => setCategory(item.code)}><strong>{item.code}</strong><span>{item.title}</span></button>)}
          </div>
          <article className="event-detail" role="tabpanel" aria-live="polite"><span className="event-watermark">{activeCategory.code}</span><p className="eyebrow">EVENT CATEGORY</p><h3>{activeCategory.title}</h3><p>{activeCategory.explanation}</p><div className="event-rule"><span>RULE</span><code>{activeCategory.formula}</code></div></article>
        </div>
        <p className="formula-callout"><strong>Binary target:</strong> Y = 1 when D + F + V ≥ 2; Y = 0 otherwise. If any indicator is unevaluable, Y is missing and the category is NOT_EVALUABLE.</p>
      </section>

      <section className="section method-section" id="method">
        <div className="section-kicker">FORECAST DESIGN <span>04 — 08</span></div>
        <div className="section-heading"><h2>One information cutoff.<br /><em>Two exact horizons.</em></h2><p>Each forecast uses predictors available through origin month t. The target is the outcome in one exact future month.</p></div>
        <div className="forecast-panel">
          <label htmlFor="horizon">INSPECT THE FORECAST HORIZON</label>
          <select id="horizon" value={horizon} onChange={(event) => setHorizon(event.target.value)}><option value="1">Exact next month · t+1</option><option value="3">Exact third month · t+3</option></select>
          <div className="timeline"><div className="time-node origin"><span>ORIGIN</span><b>t</b><small>Data available<br />through this month</small></div><div className="time-track"><span>Forecast from information at t</span><i /></div><div className="time-node destination"><span>EXACT TARGET</span><b>t+{horizon}</b><small>{horizon === "1" ? "Next month only" : "Third month only"}<br />Not a rolling window</small></div></div>
          <div className="forecast-note"><span>SEPARATE EXPLORATION</span><b>Any compound event in t+1, t+2 or t+3 would be a different outcome and must be reported separately.</b></div>
        </div>
      </section>

      <section className="section models-section" id="models">
        <div className="section-kicker">MODEL COMPARISON <span>05 — 08</span></div>
        <div className="section-heading"><h2>Does combining signals<br /><em>add predictive value?</em></h2><p>A regularised logistic-regression family gives the combined model meaningful baselines to compare against.</p></div>
        <div className="model-grid">
          {modelRows.map((row) => <button key={row[0]} className={"model-card " + (row[0] === expandedModel ? "expanded " : "") + (row[0] === "M4" ? "combined" : "")} onClick={() => setExpandedModel(row[0])} aria-pressed={expandedModel === row[0]}><span>{row[0]}</span><strong>{row[1]}</strong><small>{row[2]}</small><i>{expandedModel === row[0] ? "Selected" : "Inspect model"}</i></button>)}
        </div>
        <div className="model-explainer" aria-live="polite"><div><span>SELECTED SPECIFICATION</span><b>{modelRows.find((row) => row[0] === expandedModel)[1]}</b></div><p>{modelRows.find((row) => row[0] === expandedModel)[2]}. Predictors include the current origin month and the two preceding months only. Imputation and scaling are fitted within the training pipeline.</p></div>
        <div className="metric-row"><div><b>Log₁₀ likelihood</b><p>How well predicted probabilities assign likelihood to observed outcomes.</p></div><div><b>Brier score</b><p>Mean squared error of predicted event probabilities.</p></div><div><b>Calibration gap</b><p>How far predicted probabilities sit from observed frequencies across bins.</p></div></div>
      </section>

      <section className="section validation-section">
        <div className="section-kicker">TIME-ORDERED VALIDATION <span>06 — 08</span></div>
        <div className="section-heading"><h2>Keep the future<br /><em>out of the training set.</em></h2><p>Split assignment follows the target month. Validation informs design review; the final test stays gated until the prior and freeze are recorded.</p></div>
        <div className="split-bar"><div className="split train"><span>TRAINING</span><b>2001–2016</b><small>Fit models and training thresholds</small></div><div className="split validation"><span>VALIDATION</span><b>2017–2020</b><small>Review and freeze design</small></div><div className="split test"><span>LOCKED TEST</span><b>2021–2024</b><small>Open once after preregistration</small></div></div>
        <div className="lock-message"><span>▣</span><p><strong>Test-set protection is intentional.</strong> The student's own prior prediction and an analysis-freeze manifest are required before the release flag can produce any test output.</p></div>
      </section>

      <section className="section status-section">
        <div className="section-kicker">THE OBSERVATORY SYSTEM <span>07 — 08</span></div>
        <div className="section-heading"><h2>One coherent framework.<br /><em>From signal to probability.</em></h2><p>The project unites the scientific specification, source-quality contract, computational workflow and reproducible interface in one versioned research system.</p></div>
        <div className="capability-list">
          <div><b>01 · Research specification</b><span>Research question, environmental indicators, compound-event definition and exact forecast horizons.</span></div>
          <div><b>02 · Source and quality contract</b><span>Dataset versions, product-specific QA, units, spatial crosswalks and provenance requirements.</span></div>
          <div><b>03 · Probabilistic analysis</b><span>Input validation, indicator construction, event labels, regularised logistic models and calibration metrics.</span></div>
          <div><b>04 · Ecological comparison</b><span>Fractional cell–ecoregion weighting, regional sample safeguards and uncertainty summaries.</span></div>
          <div><b>05 · Reproducibility design</b><span>Chronological splits, source hashes, analysis freeze and one-time held-out evaluation controls.</span></div>
          <div><b>06 · Interactive observatory</b><span>Offline React explainer for signals, event categories, forecast horizons and model specifications.</span></div>
        </div>
        <div className="lock-message"><span>◈</span><p><strong>Measurements are never simulated.</strong> The research software is implemented as a complete framework. Empirical conclusions are only reported when supported by source-verified observations, documented quality control and the preregistered evaluation.</p></div>
      </section>

      <section className="section sources-section" id="sources">
        <div className="section-kicker">DATA SOURCES <span>08 — 08</span></div>
        <div className="section-heading"><h2>Trace every signal<br /><em>back to its source.</em></h2><p>Official product guides, collection documentation, QA definitions and attribution are linked in the repository source register.</p></div>
        <div className="source-list">{sources.map((source, index) => <a className="source-item" href={source[2]} target="_blank" rel="noreferrer" key={source[0]}><span>{String(index + 1).padStart(2, "0")}</span><div><b>{source[0]}</b><small>{source[1]}</small></div><i>↗</i></a>)}</div>
      </section>

      <section className="closing"><p className="eyebrow">A NOTE ON SCIENTIFIC INTERPRETATION</p><h2>Probability is not certainty.<br /><em>And a proxy is not the system.</em></h2><p>This framework is a starting point for transparent, testable environmental analysis. Any future finding must be tied to verified source data, documented quality control, a frozen model specification and uncertainty that is reported rather than hidden.</p><a href="https://github.com/krlhsn/global-compound-ecosystem-disturbance-observatory/blob/main/RESEARCH_PROTOCOL.md" target="_blank" rel="noreferrer">Open the full research protocol ↗</a></section>
      <footer><span>WHEN ECOSYSTEM DISTURBANCES COMPOUND</span><span>Built by <a href="https://github.com/krlhsn">Kamrul Hassan</a> · <a href="https://orcid.org/0009-0008-2990-1036">ORCID</a></span></footer>
    </main>
  );
}
