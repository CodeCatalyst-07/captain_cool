import { useState } from 'react'
import { Link } from 'react-router-dom'
import EspnNavbar from '../components/EspnNavbar'
import MatchForm from '../components/MatchForm'
import LoadingSpinner from '../components/LoadingSpinner'
import ResultCards from '../components/ResultCards'
import WinProbBar from '../components/WinProbBar'

const INITIAL_FORM = {
  innings: 1,
  over: 14,
  score: '134/4',
  batting_team: 'MI',
  bowling_team: 'CSK',
  striker: 'Hardik Pandya',
  non_striker: 'Tilak Varma',
  bowlers_remaining: 'Bumrah:2,Chahar:3',
  pitch_type: 'Flat',
  dew_factor: true,
  venue: 'Wankhede Stadium Mumbai',
  target: 0,
  impact_player_available: true,
  cricbuzz_url: '',
}

const TICKER_TEXT = 'MULTI-AGENT AI SYSTEM  •  GOOGLE GEMINI 2.5 FLASH  •  REAL-TIME IPL STRATEGY  •  ADK POWERED  •  '

export default function AnalyzePage() {
  const [form, setForm] = useState(INITIAL_FORM)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const baseUrl = import.meta.env.VITE_API_URL || ''
      const res = await fetch(`${baseUrl}/api/strategy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          innings: Number(form.innings),
          over: Number(form.over),
          target: Number(form.target),
        }),
      })
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}))
        throw new Error(errBody.detail || errBody.traceback || `Server error ${res.status}`)
      }
      setResult(await res.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const ticker = TICKER_TEXT + TICKER_TEXT

  const navRight = (
    <Link to="/" style={{ fontSize: 12, color: '#555', textDecoration: 'none', fontWeight: 600, letterSpacing: '0.06em', display: 'flex', alignItems: 'center', gap: 6 }}>
      ← BACK TO HOME
    </Link>
  )

  return (
    <div style={{ background: '#0a0a0f', minHeight: '100vh' }}>
      <EspnNavbar right={navRight} />

      {/* Ticker */}
      <div className="ticker-wrap" style={{ padding: '8px 0' }}>
        <div className="ticker-track">
          {[...Array(6)].map((_, i) => (
            <span key={i} style={{ marginRight: 60 }}>
              {ticker.split('  •  ').filter(Boolean).map((seg, j, arr) => (
                <span key={j}>
                  <span style={{ color: '#e31837', fontWeight: 700, fontSize: 11, letterSpacing: '0.1em' }}>{seg.trim()}</span>
                  {j < arr.length - 1 && <span style={{ color: '#444', margin: '0 18px', fontSize: 11 }}>•</span>}
                </span>
              ))}
            </span>
          ))}
        </div>
      </div>

      <main style={{ maxWidth: 1100, margin: '0 auto', padding: '28px 20px', display: 'flex', flexDirection: 'column', gap: 28 }}>
        {/* Breadcrumb */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Link to="/" style={{ fontSize: 11, color: '#555', textDecoration: 'none', letterSpacing: '0.06em' }}>HOME</Link>
          <span style={{ color: '#333', fontSize: 11 }}>/</span>
          <span style={{ fontSize: 11, color: '#e31837', fontWeight: 700, letterSpacing: '0.06em' }}>ANALYZE MATCH</span>
        </div>

        {/* Form panel */}
        <section style={{ background: '#0d0d14', border: '1px solid #1a1a1a', borderRadius: 8, overflow: 'hidden' }}>
          <div style={{ borderBottom: '1px solid #1a1a1a', padding: '14px 24px', display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 3, height: 20, background: '#e31837', borderRadius: 2 }} />
            <span style={{ fontSize: 13, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#fff' }}>
              Match Situation
            </span>
          </div>
          <form onSubmit={handleSubmit} style={{ padding: '24px' }}>
            <MatchForm form={form} setForm={setForm} loading={loading} />
            <div style={{ marginTop: 28 }}>
              <button
                type="submit"
                disabled={loading}
                className={loading ? 'btn-analyzing' : ''}
                style={{
                  width: '100%', padding: '14px', borderRadius: 4, border: 'none',
                  background: loading ? '#9b1228' : '#e31837',
                  color: '#fff', fontWeight: 800, fontSize: 13,
                  letterSpacing: '0.1em', textTransform: 'uppercase',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
                  transition: 'background 0.2s',
                }}
              >
                {loading ? (
                  <>
                    <span style={{ width: 14, height: 14, border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid #fff', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.8s linear infinite' }} />
                    ANALYZING...
                  </>
                ) : "🧠 GET CAPTAIN'S DECISION"}
              </button>
            </div>
          </form>
        </section>

        {loading && <LoadingSpinner />}

        {error && (
          <div style={{ background: '#1a0a0a', border: '1px solid #e31837', borderRadius: 8, padding: 20, display: 'flex', gap: 14 }}>
            <span style={{ fontSize: 20 }}>⚠️</span>
            <div>
              <p style={{ color: '#e31837', fontWeight: 700, marginBottom: 6, fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Analysis Failed</p>
              <p style={{ color: '#aaa', fontSize: 13, lineHeight: 1.6, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{error}</p>
            </div>
          </div>
        )}

        {result && (
          <section style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 3, height: 24, background: '#e31837', borderRadius: 2 }} />
              <span style={{ fontSize: 14, fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#fff' }}>DEBATE ANALYSIS</span>
              <div style={{ flex: 1, height: 1, background: '#1a1a1a' }} />
              <span style={{ fontSize: 10, color: '#e31837', fontWeight: 700, letterSpacing: '0.1em' }}>5 ROUNDS COMPLETE</span>
            </div>
            <WinProbBar before={result.win_probability_before} after={result.win_probability_after} battingTeam={form.batting_team} bowlingTeam={form.bowling_team} />
            <ResultCards result={result} />
          </section>
        )}
      </main>

      <footer style={{ borderTop: '1px solid #1a1a1a', padding: '16px 24px', textAlign: 'center' }}>
        <span style={{ fontSize: 11, color: '#333', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          Captain Cool · Google Gemini 2.5 Flash · ADK Multi-Agent System
        </span>
      </footer>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
