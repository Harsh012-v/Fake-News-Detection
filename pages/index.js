import Head from 'next/head'
import { useState } from 'react'

export default function Home() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  async function predict() {
    setLoading(true)
    setResult(null)
    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Request failed')
      setResult(data)
    } catch (err) {
      setResult({ error: err.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 760, margin: '2rem auto', fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial' }}>
      <Head>
        <title>Fake News Detector — MVP</title>
      </Head>

      <h1>Fake News Detector — MVP</h1>
      <p style={{ color: '#555' }}>Paste a headline or snippet and click "Predict". The API is at <code>/api/predict</code>.</p>

      <textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Enter the news text or headline..." style={{ width: '100%', height: 140, padding: '.6rem', fontSize: '1rem' }} />
      <div style={{ marginTop: '.5rem' }}>
        <button onClick={predict} disabled={loading} style={{ padding: '.6rem 1rem', fontSize: '1rem' }}>{loading ? 'Predicting...' : 'Predict'}</button>
        <button onClick={() => setText('This one weird trick doctors hate — cure for diabetes!')} style={{ marginLeft: '.5rem' }}>Sample fake</button>
        <button onClick={() => setText('Council approves funding for new park, officials said')} style={{ marginLeft: '.5rem' }}>Sample real</button>
      </div>

      <div style={{ marginTop: '1rem' }}>
        {result && result.error && <div style={{ background: '#fff0f0', border: '1px solid #ff8a8a', color: '#a00', padding: '1rem', borderRadius: 6 }}>Error: {result.error}</div>}
        {result && !result.error && (
          <div style={{ padding: '1rem', borderRadius: 6, background: result.label === 'FAKE' ? '#fff0f0' : '#f0fff6', border: result.label === 'FAKE' ? '1px solid #ff8a8a' : '1px solid #8affb3' }}>
            <strong>{result.label}</strong> — score: {Number(result.score).toFixed(2)}
          </div>
        )}
      </div>

      <footer style={{ marginTop: '3rem', color: '#666' }}>
        Running on Vercel? Deploy this repo and the site will be available at the root and the API at /api/predict.
      </footer>
    </div>
  )
}
