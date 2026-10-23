import { useState } from 'react'
import { Activity, AlertTriangle, Building2, CloudSun, FileText, HardHat, LayoutDashboard, MessageSquareText, Ruler, ShieldCheck, Upload, Wallet, LoaderCircle, CheckCircle2 } from 'lucide-react'

const API = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const nav = [
  ['overview', 'Overview', LayoutDashboard],
  ['safety', 'Site safety', ShieldCheck],
  ['cracks', 'Crack analysis', AlertTriangle],
  ['planning', 'Planning & costs', Ruler],
  ['valuation', 'Property valuation', Building2],
  ['assistant', 'Site assistant', MessageSquareText],
]
const money = n => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n)

function Result({ data }) {
  if (!data) return null
  return <div className="result"><div className="result-head"><CheckCircle2 size={18}/><b>Analysis result</b><span className="mode">{data.mode || 'calculated'}</span></div>
    {data.summary && <p>{data.summary}</p>}
    {data.answer && <p className="answer">{data.answer}</p>}
    {data.findings && <div className="findings">{data.findings.map((f,i)=><div className="finding" key={i}><div className="finding-top"><b>{f.title}</b><span className={'severity '+f.severity}>{f.severity}</span></div><p>{f.explanation}</p><p><b>Action:</b> {f.recommended_action}</p></div>)}</div>}
    {data.observation && <p>{data.observation}</p>}
    {data.possible_patterns && <div><h4>Possible patterns</h4><ul>{data.possible_patterns.map((x,i)=><li key={i}>{x}</li>)}</ul></div>}
    {data.recommended_next_steps && <div><h4>Recommended next steps</h4><ul>{data.recommended_next_steps.map((x,i)=><li key={i}>{x}</li>)}</ul></div>}
    {data.total_area_sqft !== undefined && <div className="metric-grid"><div><small>Total built-up area</small><strong>{data.total_area_sqft.toLocaleString()} sq ft</strong></div><div><small>Cement (rough)</small><strong>{data.estimated_cement_bags.toLocaleString()} bags</strong></div><div><small>Steel (rough)</small><strong>{data.estimated_steel_kg.toLocaleString()} kg</strong></div><div><small>Indicative cost range</small><strong>{money(data.indicative_cost_low_inr)} – {money(data.indicative_cost_high_inr)}</strong></div></div>}
    {data.estimated_value_inr !== undefined && <div className="valuation"><small>Indicative value</small><strong>{money(data.estimated_value_inr)}</strong><span>Adjustment: {data.adjustment_percent}%</span></div>}
    {data.assumptions && <><h4>Assumptions</h4><ul>{data.assumptions.map((x,i)=><li key={i}>{x}</li>)}</ul></>}
    {data.disclaimer && <p className="disclaimer">{data.disclaimer}</p>}
  </div>
}

export default function App() {
  const [page, setPage] = useState('overview')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [description, setDescription] = useState('Worker near an unprotected edge without a harness')
  const [weather, setWeather] = useState('Clear')
  const [site, setSite] = useState('Second-floor construction work')
  const [image, setImage] = useState(null)
  const [crackDescription, setCrackDescription] = useState('')
  const [area, setArea] = useState('1200')
  const [floors, setFloors] = useState('1')
  const [finish, setFinish] = useState('standard')
  const [location, setLocation] = useState('Indore')
  const [rate, setRate] = useState('4000')
  const [age, setAge] = useState('5')
  const [condition, setCondition] = useState('good')
  const [question, setQuestion] = useState('What should I check before starting work at height?')

  async function request(path, options) {
    setBusy(true); setError(''); setResult(null)
    try {
      const response = await fetch(`${API}${path}`, options)
      const body = await response.json()
      if (!response.ok) throw new Error(body.detail || `Request failed (${response.status})`)
      setResult(body)
    } catch (e) {
      setError(`${e.message}. Confirm the FastAPI server is running at ${API}.`)
    } finally { setBusy(false) }
  }
  const json = body => ({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  function runSafety(e) { e.preventDefault(); request('/api/analyze/safety', json({ description, weather, site_context: site })) }
  function runCracks(e) {
    e.preventDefault()
    if (!image) { setError('Choose a JPG, PNG or WEBP image first.'); return }
    const form = new FormData(); form.append('image', image); form.append('description', crackDescription)
    request('/api/analyze/cracks', { method: 'POST', body: form })
  }
  function runPlanning(e) { e.preventDefault(); request('/api/planning/estimate', json({ area_sqft: Number(area), floors: Number(floors), finish_level: finish, location })) }
  function runValuation(e) { e.preventDefault(); request('/api/valuation/estimate', json({ area_sqft: Number(area), rate_per_sqft_inr: Number(rate), age_years: Number(age), condition })) }
  function runAssistant(e) { e.preventDefault(); request('/api/assistant', json({ question, site_context: site, weather })) }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><HardHat size={22}/></div><div><b>BuildSight</b><small>CONSTRUCTION INTELLIGENCE</small></div></div>
      <div className="workspace-label">WORKSPACE</div>
      {nav.map(([id,label,Icon])=><button key={id} className={`nav-item ${page===id?'active':''}`} onClick={()=>{setPage(id);setResult(null);setError('')}}><Icon size={18}/><span>{label}</span></button>)}
      <div className="sidebar-bottom"><div className="status-dot"></div><div><b>Local demo environment</b><small>AI provider is configured on backend</small></div></div>
    </aside>
    <main className="main">
      <header className="topbar"><div><span className="crumb">Projects</span><span className="slash">/</span><b>Multimodal Construction Intelligence</b></div><div className="top-actions"><span className="status-pill"><span className="green-dot"></span> API workspace</span><div className="avatar">BS</div></div></header>
      <div className="content">
        <div className="page-heading"><div><div className="eyebrow">CONSTRUCTION OPERATIONS / AI ASSISTANT</div><h1>{nav.find(n=>n[0]===page)?.[1] || 'Overview'}</h1><p>Turn site observations into structured, reviewable insights.</p></div><div className="date-chip"><Activity size={16}/> MVP workspace</div></div>
        {page==='overview' && <><div className="hero"><div className="hero-copy"><span className="hero-tag"><Activity size={14}/> MULTIMODAL PROJECT HUB</span><h2>Make every site decision<br/>more <em>informed.</em></h2><p>Review safety observations, record crack evidence, estimate project quantities and organize construction knowledge in one place.</p><button className="primary-btn" onClick={()=>setPage('safety')}>Start site review <span>→</span></button></div><div className="hero-art"><div className="art-circle"></div><div className="blueprint"><div className="blueprint-label">SITE / 01</div><div className="building"><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div><div className="blueprint-line"></div><div className="blueprint-caption">PLAN · REVIEW · BUILD</div></div><div className="floating-card"><span className="float-icon"><ShieldCheck size={18}/></span><div><b>Safety first</b><small>Structured observations</small></div><span className="float-check">✓</span></div></div></div>
          <div className="section-title"><div><h3>Project modules</h3><p>Choose a workflow to begin.</p></div><span className="tiny-note">6 WORKFLOWS</span></div>
          <div className="module-grid">{nav.slice(1).map(([id,label,Icon],i)=><button className="module-card" key={id} onClick={()=>setPage(id)}><div className={`module-icon color-${i}`}><Icon size={21}/></div><div className="module-arrow">↗</div><h4>{label}</h4><p>{['Identify potential site hazards and practical controls.','Record image evidence and recommended inspection steps.','Estimate quantities and an indicative project cost range.','Calculate an indicative value from area and local rate.','Ask practical questions about construction workflows.'][i]}</p><span className="module-link">Open workflow <span>→</span></span></button>)}</div>
          <div className="notice"><AlertTriangle size={18}/><div><b>Professional review required</b><p>Outputs are advisory. Never use this MVP to certify a structure, replace a risk assessment, or make a final valuation.</p></div></div>
        </>}
        {page==='safety' && <div className="panel"><div className="panel-intro"><div className="panel-icon"><ShieldCheck/></div><div><h3>Site safety screening</h3><p>Describe the task, hazard or observation. The result is a preliminary checklist, not a safety certification.</p></div></div><form onSubmit={runSafety} className="form-grid"><label className="wide">Site observation<textarea value={description} onChange={e=>setDescription(e.target.value)} required minLength="3" /></label><label>Weather conditions<input value={weather} onChange={e=>setWeather(e.target.value)}/></label><label>Site context<input value={site} onChange={e=>setSite(e.target.value)}/></label><div className="wide form-footer"><span>Include what happened, where, and what controls are present.</span><button className="primary-btn" disabled={busy}>{busy?<LoaderCircle className="spin" size={17}/>:<ShieldCheck size={17}/>} Analyze observation</button></div></form></div>}
        {page==='cracks' && <div className="panel"><div className="panel-intro"><div className="panel-icon warning"><AlertTriangle/></div><div><h3>Crack observation & analysis</h3><p>Upload a site photo and record context. Demo mode validates the upload but does not inspect pixels.</p></div></div><form onSubmit={runCracks} className="form-grid"><label className="wide upload-zone"><Upload size={28}/><b>{image?image.name:'Choose a site image'}</b><span>JPG, PNG or WEBP · max 8 MB</span><input type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>setImage(e.target.files?.[0]||null)}/></label>{image&&<div className="wide image-preview"><img src={URL.createObjectURL(image)} alt="Selected site evidence"/><span>Selected evidence · review before submitting</span></div>}<label className="wide">Observation notes<textarea value={crackDescription} onChange={e=>setCrackDescription(e.target.value)} placeholder="Where is the crack? When was it noticed? Is it changing?"/></label><div className="wide form-footer"><span>AI observations must be checked by a structural engineer.</span><button className="primary-btn" disabled={busy}>{busy?<LoaderCircle className="spin" size={17}/>:<Upload size={17}/>} Review image</button></div></form></div>}
        {page==='planning' && <div className="panel"><div className="panel-intro"><div className="panel-icon purple"><Ruler/></div><div><h3>Planning & quantity estimator</h3><p>Generate rough quantities and a cost range from basic project inputs.</p></div></div><form onSubmit={runPlanning} className="form-grid"><label>Area per floor (sq ft)<input type="number" min="1" max="1000000" value={area} onChange={e=>setArea(e.target.value)} required/></label><label>Number of floors<input type="number" min="1" max="100" value={floors} onChange={e=>setFloors(e.target.value)} required/></label><label>Finish level<select value={finish} onChange={e=>setFinish(e.target.value)}><option value="basic">Basic</option><option value="standard">Standard</option><option value="premium">Premium</option></select></label><label>Location<input value={location} onChange={e=>setLocation(e.target.value)}/></label><div className="wide form-footer"><span>Illustrative estimates only; not a bill of quantities.</span><button className="primary-btn" disabled={busy}>{busy?<LoaderCircle className="spin" size={17}/>:<Ruler size={17}/>} Estimate project</button></div></form></div>}
        {page==='valuation' && <div className="panel"><div className="panel-intro"><div className="panel-icon green"><Wallet/></div><div><h3>Indicative property valuation</h3><p>Uses your local rate input and a simple age/condition adjustment.</p></div></div><form onSubmit={runValuation} className="form-grid"><label>Property area (sq ft)<input type="number" min="1" value={area} onChange={e=>setArea(e.target.value)} required/></label><label>Local rate (₹ / sq ft)<input type="number" min="1" value={rate} onChange={e=>setRate(e.target.value)} required/></label><label>Property age (years)<input type="number" min="0" max="200" value={age} onChange={e=>setAge(e.target.value)} required/></label><label>Condition<select value={condition} onChange={e=>setCondition(e.target.value)}><option value="poor">Poor</option><option value="fair">Fair</option><option value="good">Good</option><option value="excellent">Excellent</option></select></label><div className="wide form-footer"><span>Not a formal market appraisal.</span><button className="primary-btn" disabled={busy}>{busy?<LoaderCircle className="spin" size={17}/>:<Building2 size={17}/>} Estimate value</button></div></form></div>}
        {page==='assistant' && <div className="panel"><div className="panel-intro"><div className="panel-icon blue"><MessageSquareText/></div><div><h3>Construction knowledge assistant</h3><p>Ask a practical question about materials, safety or site workflows.</p></div></div><form onSubmit={runAssistant} className="form-grid"><label className="wide">Your question<textarea value={question} onChange={e=>setQuestion(e.target.value)} required minLength="3"/></label><label>Weather context<input value={weather} onChange={e=>setWeather(e.target.value)}/></label><label>Site context<input value={site} onChange={e=>setSite(e.target.value)}/></label><div className="wide form-footer"><span>Responses may be incomplete; verify against project specifications.</span><button className="primary-btn" disabled={busy}>{busy?<LoaderCircle className="spin" size={17}/>:<MessageSquareText size={17}/>} Ask assistant</button></div></form></div>}
        {busy && <div className="loading"><LoaderCircle className="spin" size={18}/> Processing request…</div>}
        {error && <div className="error-box"><AlertTriangle size={18}/><span>{error}</span></div>}
        {result && <Result data={result}/>}
        <footer className="footer"><span>BuildSight · Construction Intelligence MVP</span><span><FileText size={14}/> Review every recommendation</span></footer>
      </div>
    </main>
  </div>
}
