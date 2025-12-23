import Head from 'next/head'
import { useState } from 'react'

export default function Home() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  async function handlePredict() {
    if (!text.trim()) return
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

  const setSample = (val) => {
    setText(val)
    setResult(null)
  }

  return (
    <div className="container">
      <Head>
        <title>Fake News Detector — AI Analysis</title>
        <meta name="description" content="Validate news snippets using our AI-powered fake news detector." />
      </Head>

      <header className="header">
        <h1>Fake News Detector</h1>
        <p>Harness AI to distinguish between reliable reporting and deceptive content.</p>
      </header>

      <main className="card">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste news headline or content snippet here to analyze..."
        />

        <div className="button-group">
          <button
            className="btn-primary"
            onClick={handlePredict}
            disabled={loading || !text.trim()}
          >
            {loading ? 'Analyzing...' : 'Analyze Content'}
          </button>

          <button
            className="btn-outline"
            onClick={() => setSample('Shocking secret! This one weird trick cure for diabetes docs hate!')}
          >
            Try Fake Sample
          </button>

          <button
            className="btn-outline"
            onClick={() => setSample('The local city council approved a new budget for public parks and infrastructure, officials said Tuesday.')}
          >
            Try Real Sample
          </button>
        </div>

        {result && result.error && (
          <div className="error-box">
            <strong>Internal Error:</strong> {result.error}
          </div>
        )}

        {result && !result.error && (
          <div className={`result-container`}>
            <div className={`result-box ${result.label === 'FAKE' ? 'fake' : 'real'}`}>
              <div className="result-label">
                <span>{result.label === 'FAKE' ? '🚩 Predicted as FAKE' : '✅ Predicted as REAL'}</span>
              </div>
              <div className="result-score">
                Confidence: {(result.score * 100).toFixed(1)}%
              </div>
            </div>
            <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center' }}>
              Disclaimer: This AI analysis is a prediction based on learned patterns and may not always be accurate.
            </p>
          </div>
        )}
      </main>

      <footer>
        <p>&copy; {new Date().getFullYear()} Fake News Detection MVP. Built with Next.js and Scikit-Learn.</p>
      </footer>
    </div>
  )
}
