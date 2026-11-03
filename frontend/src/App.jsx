import { useEffect, useState } from 'react'
import axios from 'axios'
import './App.css'

const API_URL = 'http://127.0.0.1:8000/prediction/predict'
const RULES_URL = 'http://127.0.0.1:8000/prediction/rules'

// Dropdown options (taken from the training dataset)
const CHANNELS = [
  'foosdfpfkusacimwkcsosbicdxkicaua',
  'lmkebamcaaclubfxadlmueccxoimlema',
  'usilxuppasemubllopkaafesmlibmsdf',
  'ewpakwlliwisiwduibdlfmalxowmwpci',
  'sddiedcslfslkckwlfkdpoeeailfpeds',
  'epumfxlbckeskwekxbiuasklxalciiuu',
  'fixdbufsefwooaasfcxdxadsiekoceaa',
  'MISSING',
]
const ORIGINS = [
  'lxidpiddsbxsbosboudacockeimpuepw',
  'kamkkxfxxuwbdslkwifmmcsiusiuosws',
  'ldkssxwpmemidmecebumciepifcamkci',
  'usapbepcfoloekilkwsdiboslwaxobdp',
  'ewxeelcelemmiwuafmddpobolfuxioce',
  'MISSING',
]
const GAS = [
  { value: 'f', label: 'No (f)' },
  { value: 't', label: 'Yes (t)' },
]

// Field groups; every name matches the backend's PredictionInput schema
const GROUPS = [
  {
    title: 'Customer profile',
    fields: [
      { name: 'channel_sales', label: 'Sales channel', options: CHANNELS },
      { name: 'origin_up', label: 'Origin of contract', options: ORIGINS },
      { name: 'has_gas', label: 'Also a gas customer?', options: GAS },
      { name: 'nb_prod_act', label: 'Active products' },
      { name: 'num_years_antig', label: 'Years as customer' },
      { name: 'pow_max', label: 'Subscribed max power' },
    ],
  },
  {
    title: 'Consumption',
    fields: [
      { name: 'cons_12m', label: 'Electricity use, last 12 months' },
      { name: 'cons_gas_12m', label: 'Gas use, last 12 months' },
      { name: 'cons_last_month', label: 'Electricity use, last month' },
      { name: 'imp_cons', label: 'Current paid consumption' },
    ],
  },
  {
    title: 'Forecasts',
    fields: [
      { name: 'forecast_cons_12m', label: 'Forecast use, next 12 months' },
      { name: 'forecast_cons_year', label: 'Forecast use, calendar year' },
      { name: 'forecast_discount_energy', label: 'Forecast energy discount' },
      { name: 'forecast_meter_rent_12m', label: 'Forecast meter rent, 12 months' },
      { name: 'forecast_price_energy_off_peak', label: 'Forecast energy price, off-peak' },
      { name: 'forecast_price_energy_peak', label: 'Forecast energy price, peak' },
      { name: 'forecast_price_pow_off_peak', label: 'Forecast power price, off-peak' },
    ],
  },
  {
    title: 'Margins',
    fields: [
      { name: 'margin_gross_pow_ele', label: 'Gross margin on power subscription' },
      { name: 'margin_net_pow_ele', label: 'Net margin on power subscription' },
      { name: 'net_margin', label: 'Total net margin' },
    ],
  },
  {
    title: 'Contract dates',
    fields: [
      { name: 'activation_year', label: 'Activation year' },
      { name: 'activation_month', label: 'Activation month' },
      { name: 'end_year', label: 'Contract end year' },
      { name: 'renewal_year', label: 'Renewal year' },
      { name: 'tenure_days', label: 'Contract length (days)' },
    ],
  },
  {
    title: 'Average prices',
    fields: [
      { name: 'price_off_peak_var', label: 'Variable price, off-peak' },
      { name: 'price_peak_var', label: 'Variable price, peak' },
      { name: 'price_mid_peak_var', label: 'Variable price, mid-peak' },
      { name: 'price_off_peak_fix', label: 'Fixed price, off-peak' },
      { name: 'price_peak_fix', label: 'Fixed price, peak' },
      { name: 'price_mid_peak_fix', label: 'Fixed price, mid-peak' },
    ],
  },
]

// Example customers taken from the dataset, so you can try the app quickly
const TYPICAL = {
  channel_sales: 'foosdfpfkusacimwkcsosbicdxkicaua', origin_up: 'lxidpiddsbxsbosboudacockeimpuepw', has_gas: 'f',
  nb_prod_act: 1, num_years_antig: 5, pow_max: 13.856,
  cons_12m: 14115.5, cons_gas_12m: 0, cons_last_month: 792.5, imp_cons: 37.395,
  forecast_cons_12m: 1112.875, forecast_cons_year: 314, forecast_discount_energy: 0, forecast_meter_rent_12m: 18.795,
  forecast_price_energy_off_peak: 0.1432, forecast_price_energy_peak: 0.0841, forecast_price_pow_off_peak: 44.3114,
  margin_gross_pow_ele: 21.64, margin_net_pow_ele: 21.64, net_margin: 112.53,
  activation_year: 2011, activation_month: 7, end_year: 2016, renewal_year: 2015, tenure_days: 1828,
  price_off_peak_var: 0.1476, price_peak_var: 0.0845, price_mid_peak_var: 0,
  price_off_peak_fix: 44.2817, price_peak_fix: 0, price_mid_peak_fix: 0,
}
const CHURNED = {
  channel_sales: 'foosdfpfkusacimwkcsosbicdxkicaua', origin_up: 'lxidpiddsbxsbosboudacockeimpuepw', has_gas: 't',
  nb_prod_act: 2, num_years_antig: 3, pow_max: 43.648,
  cons_12m: 0, cons_gas_12m: 54946, cons_last_month: 0, imp_cons: 0,
  forecast_cons_12m: 0, forecast_cons_year: 0, forecast_discount_energy: 0, forecast_meter_rent_12m: 1.78,
  forecast_price_energy_off_peak: 0.114481, forecast_price_energy_peak: 0.098142, forecast_price_pow_off_peak: 40.606701,
  margin_gross_pow_ele: 25.44, margin_net_pow_ele: 25.44, net_margin: 678.99,
  activation_year: 2013, activation_month: 6, end_year: 2016, renewal_year: 2015, tenure_days: 1096,
  price_off_peak_var: 0.124787, price_peak_var: 0.100749, price_mid_peak_var: 0.06653,
  price_off_peak_fix: 40.942265, price_peak_fix: 22.35201, price_mid_peak_fix: 14.90134,
}

const TEXT_FIELDS = ['channel_sales', 'origin_up', 'has_gas']

function App() {
  const [form, setForm] = useState(() => Object.fromEntries(Object.entries(TYPICAL).map(([k, v]) => [k, String(v)])))
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [rules, setRules] = useState(null)

  useEffect(() => {
    axios.get(RULES_URL).then((res) => setRules(res.data)).catch(() => setRules(null))
  }, [])

  const load = (preset) => {
    setForm(Object.fromEntries(Object.entries(preset).map(([k, v]) => [k, String(v)])))
    setResult(null)
    setError('')
  }

  const change = (name, value) => setForm((f) => ({ ...f, [name]: value }))

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    // Text fields stay text; everything else is sent as a number
    const payload = Object.fromEntries(
      Object.entries(form).map(([k, v]) => [k, TEXT_FIELDS.includes(k) ? v : Number(v)])
    )
    try {
      const res = await axios.post(API_URL, payload)
      setResult(res.data)
    } catch (err) {
      if (err.response) {
        setError(`The server rejected the request (${err.response.status}). Check that every field is filled with a valid number.`)
      } else {
        setError('Could not reach the backend at http://127.0.0.1:8000. Is uvicorn running?')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page">
      <h1>Customer Churn Predictor</h1>
      <p className="sub">Enter a customer&apos;s details to estimate the chance they will leave.</p>

      <div className="presets">
        <button type="button" onClick={() => load(TYPICAL)}>Load typical customer</button>
        <button type="button" onClick={() => load(CHURNED)}>Load a customer who churned</button>
      </div>

      <form onSubmit={submit}>
        {GROUPS.map((group) => (
          <section className="group" key={group.title}>
            <h2>{group.title}</h2>
            <div className="grid">
              {group.fields.map((f) => (
                <div className="field" key={f.name}>
                  <label htmlFor={f.name}>{f.label}</label>
                  {f.options ? (
                    <select id={f.name} value={form[f.name]} onChange={(e) => change(f.name, e.target.value)}>
                      {f.options.map((o) =>
                        typeof o === 'string' ? (
                          <option key={o} value={o}>{o}</option>
                        ) : (
                          <option key={o.value} value={o.value}>{o.label}</option>
                        )
                      )}
                    </select>
                  ) : (
                    <input id={f.name} type="number" step="any" required value={form[f.name]}
                      onChange={(e) => change(f.name, e.target.value)} />
                  )}
                </div>
              ))}
            </div>
          </section>
        ))}

        <button className="submit" type="submit" disabled={loading}>
          {loading ? 'Predicting…' : 'Predict churn'}
        </button>
      </form>

      {error && <div className="error" role="alert">{error}</div>}

      {result && <Result result={result} />}

      <RulesTable rules={rules} />
    </main>
  )
}

function Result({ result }) {
  const level = result.risk_level.toLowerCase()
  const r = result.retention
  const factors = result.risk_factors || []

  return (
    <section className={`result ${level}`} aria-live="polite">
      <div className="top">
        <div>
          <div className="small">Risk score</div>
          <div className="pct">{result.churn_probability}<span className="of"> / 100</span></div>
        </div>
        <span className={`badge ${level}`}>{result.risk_level} risk</span>
      </div>
      <div className="bar"><div style={{ width: `${Math.min(100, result.churn_probability)}%` }} /></div>

      <div className="cols">
        <div>
          <h3>Factors behind the score</h3>
          {factors.length === 0 ? (
            <p className="hint">Factor details are only available when the saved model is XGBoost.</p>
          ) : (
            <ul className="factors">
              {factors.map((f) => (
                <li key={f.feature}>
                  <span className={`arrow ${f.effect}`}>{f.effect === 'raises' ? '▲' : '▼'}</span>
                  <span className="fname">
                    {f.label}
                    <span className="fval"> = {String(f.value).length > 14 ? String(f.value).slice(0, 8) + '…' : String(f.value)}</span>
                  </span>
                  <span className={`fimpact ${f.effect}`}>
                    {f.effect === 'raises' ? 'raises' : 'lowers'} risk · {f.impact}%
                  </span>
                </li>
              ))}
            </ul>
          )}
          <p className="hint">The % is each factor&apos;s share of the model&apos;s total push for this customer.</p>
        </div>

        <div>
          <h3>Suggested action</h3>
          <div className="action">
            <div className="action-title">{r.action}</div>
            <div className="rule">Rule: {r.rule}</div>
            <p>{r.explanation}</p>
            {r.also_applies.length > 0 && (
              <ul className="also">
                {r.also_applies.map((a) => (
                  <li key={a.rule}><strong>{a.action}</strong> ({a.rule})</li>
                ))}
              </ul>
            )}
          </div>
          <h3>Facts the rules checked</h3>
          <ul className="signals">
            {r.signals.map((s) => (
              <li key={s.key} className={s.met ? 'met' : ''}>
                <span className="mark">{s.met ? '✓' : '–'}</span>
                <span><strong>{s.label}</strong><br /><span className="hint">{s.detail}</span></span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <p className="note">
        This is a relative risk score, not a literal chance. In past data, customers scoring 50 or more
        left about 22% of the time versus about 10% overall. The suggestion comes from simple rules,
        shown below, and is a starting point for a person to judge, not an instruction.
      </p>
    </section>
  )
}

function RulesTable({ rules }) {
  if (!rules) return null
  const t = rules.thresholds
  return (
    <details className="rules">
      <summary>How the rules work</summary>
      <table>
        <thead><tr><th>Customer situation</th><th>Suggested action</th></tr></thead>
        <tbody>
          {rules.rules.map((r) => (
            <tr key={r.situation}><td>{r.situation}</td><td>{r.action}</td></tr>
          ))}
        </tbody>
      </table>
      <ul className="hint">
        <li>Rules are checked top to bottom; the first match is the main suggestion and any others are listed too.</li>
        <li>High risk: score of {Math.round(t.high_risk_at_or_above * 100)} or more. Medium risk: {Math.round(t.medium_risk_at_or_above * 100)} to {Math.round(t.high_risk_at_or_above * 100)}.</li>
        <li>High revenue: total net margin of {t.high_revenue_net_margin} or more (top quarter of customers).</li>
        <li>Paying above forecast price: average off-peak price at least {Math.round((t.price_above_forecast_ratio - 1) * 100)}% above the forecast price.</li>
        <li>Newer customer: {t.newer_customer_max_years} years or fewer as a customer.</li>
        <li>Declining engagement: last month&apos;s electricity use under {Math.round(t.declining_usage_ratio * 100)}% of the usual monthly average.</li>
        <li>These numbers live in <code>Backend/app/utils/retention.py</code> and can be edited there.</li>
      </ul>
    </details>
  )
}

export default App
