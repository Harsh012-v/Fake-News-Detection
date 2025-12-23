// Lightweight Vercel serverless function.
// Behavior:
// - If environment variable PYTHON_BACKEND_URL is set, proxy the request to that URL
//   (useful when you host the Python Flask model elsewhere). The request body
//   is forwarded and the response returned to the client.
// - If PYTHON_BACKEND_URL is not set, use a local JS rule-based predictor (same
//   logic as the original MVP) so the function works out-of-the-box on Vercel.

async function proxyToPython(url, body) {
  const fetch = globalThis.fetch || (await import('node-fetch')).default
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    // small timeout not enforced here; Vercel has function timeouts per plan
  })
  const data = await resp.json()
  return { status: resp.status, data }
}

export default async function handler(req, res) {
  try {
    if (req.method !== 'POST') {
      res.setHeader('Allow', 'POST')
      return res.status(405).json({ error: 'Method not allowed, use POST' })
    }

    const body = req.body
    const data = typeof body === 'string' ? JSON.parse(body || '{}') : (body || {})
    const text = data.text
    if (!text || typeof text !== 'string') {
      return res.status(400).json({ error: "missing required field 'text'" })
    }

    const pythonUrl = process.env.PYTHON_BACKEND_URL
    if (pythonUrl) {
      // Proxy to python backend (expecting the python backend to accept same JSON shape)
      try {
        const { status, data: pData } = await proxyToPython(pythonUrl, { text })
        return res.status(status).json(pData)
      } catch (err) {
        // fall through to local predictor on proxy failure
        console.error('Proxy to Python backend failed:', String(err))
      }
    }

    // Local JS rule-based predictor (fallback)
    const normalize = (t) => t.toLowerCase().replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim()
    const clean = normalize(text)
    const tokens = clean.split(' ').filter(Boolean)

    const keywords_fake = ['miracle', 'click', 'shocking', 'cure', 'weird', 'video', 'aliens']
    const keywords_real = ['report', 'said', 'confirmed', 'approves', 'signed', 'president', 'scientist']

    const fake_hits = keywords_fake.reduce((acc, k) => acc + (tokens.includes(k) ? 1 : 0), 0)
    const real_hits = keywords_real.reduce((acc, k) => acc + (tokens.includes(k) ? 1 : 0), 0)

    let label = 'REAL'
    let score = 0.5
    if (fake_hits === real_hits) {
      label = 'REAL'
      score = 0.5
    } else if (fake_hits > real_hits) {
      label = 'FAKE'
      score = Math.min(0.99, 0.5 + Math.abs(fake_hits - real_hits) * 0.25)
    } else {
      label = 'REAL'
      score = Math.min(0.99, 0.5 + Math.abs(fake_hits - real_hits) * 0.25)
    }

    return res.status(200).json({ label, score })
  } catch (err) {
    console.error(err)
    return res.status(500).json({ error: 'internal error', detail: String(err) })
  }
}
