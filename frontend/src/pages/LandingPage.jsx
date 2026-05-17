import { useNavigate } from 'react-router-dom'
import EspnNavbar from '../components/EspnNavbar'

const AGENTS = [
  { icon: '📊', name: 'STATS ANALYST',    role: 'Data Engine',       desc: 'Fetches live match data and builds the tactical picture.', round: 1, color: '#3b82f6' },
  { icon: '🏏', name: 'STRATEGIST',       role: 'Virtual Captain',   desc: 'Proposes the next decision like Dhoni, Rohit, and Hardik combined.', round: 2, color: '#22c55e' },
  { icon: '😈', name: "DEVIL'S ADVOCATE", role: 'Data Analyst',      desc: 'Challenges every proposal with 2 hard cricket-grounded objections.', round: 3, color: '#e31837' },
  { icon: '🎙️', name: 'COMMENTATOR',     role: 'Broadcast Narrator', desc: 'Narrates the final call in the voice of Harsha and Shastri.', round: 5, color: '#7c3aed' },
]

const TICKER = 'POWERED BY GOOGLE GEMINI 2.5 FLASH  •  AGENT DEVELOPMENT KIT  •  REAL-TIME IPL STRATEGY  •  '

export default function LandingPage() {
  const navigate = useNavigate()

  const navRight = (
    <button onClick={() => navigate('/analyze')} style={{ background: '#e31837', color: '#fff', border: 'none', borderRadius: 4, padding: '8px 18px', fontSize: 11, fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', cursor: 'pointer' }}>
      ANALYZE MATCH →
    </button>
  )

  return (
    <div style={{ background: '#0a0a0f', minHeight: '100vh', overflowX: 'hidden' }}>
      <EspnNavbar right={navRight} />

      {/* ── HERO ─────────────────────────────────────────────────────────── */}
      <section style={{ position: 'relative', minHeight: '92vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '60px 24px 80px', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse 70% 55% at 50% 60%, rgba(227,24,55,0.08) 0%, transparent 70%)', animation: 'hero-pulse 4s ease-in-out infinite' }} />

        <div style={{ position: 'relative', zIndex: 1, maxWidth: 760 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(227,24,55,0.12)', border: '1px solid rgba(227,24,55,0.3)', borderRadius: 4, padding: '6px 14px', marginBottom: 36 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#e31837', display: 'inline-block', animation: 'dot-pulse 1.4s ease-in-out infinite' }} />
            <span style={{ fontSize: 10, fontWeight: 800, letterSpacing: '0.14em', color: '#e31837', textTransform: 'uppercase' }}>LIVE AI SYSTEM</span>
          </div>

          <h1 style={{ margin: 0, fontFamily: 'Outfit, sans-serif', lineHeight: 1.05 }}>
            <span style={{ display: 'block', fontSize: 'clamp(48px, 8vw, 88px)', fontWeight: 900, color: '#fff', letterSpacing: '-2px' }}>YOUR AI IPL CAPTAIN</span>
            <span style={{ display: 'block', fontSize: 'clamp(48px, 8vw, 88px)', fontWeight: 900, color: '#e31837', letterSpacing: '-2px' }}>THINKS LIKE DHONI.</span>
          </h1>

          <p style={{ marginTop: 28, fontSize: 'clamp(15px,2vw,19px)', color: '#888', lineHeight: 1.7, maxWidth: 540, margin: '28px auto 0' }}>
            4 Gemini-powered agents debate every tactical decision in real time — stats, strategy, challenge, commentary.
          </p>

          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap', marginTop: 48 }}>
            <button onClick={() => navigate('/analyze')} style={{ background: '#e31837', color: '#fff', border: 'none', borderRadius: 4, padding: '16px 36px', fontSize: 13, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', cursor: 'pointer' }}>
              ANALYZE A MATCH
            </button>
            <button onClick={() => navigate('/how-it-works')} style={{ background: 'transparent', color: '#fff', border: '1px solid #333', borderRadius: 4, padding: '16px 36px', fontSize: 13, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', cursor: 'pointer' }}>
              HOW IT WORKS
            </button>
          </div>

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap', marginTop: 56 }}>
            {['4 AI AGENTS', 'REAL-TIME DEBATE', 'GEMINI 2.5 FLASH', 'ADK POWERED'].map((label) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#111', border: '1px solid #1a1a1a', borderRadius: 4, padding: '8px 16px' }}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#e31837', display: 'inline-block' }} />
                <span style={{ fontSize: 11, fontWeight: 800, color: '#fff', letterSpacing: '0.08em' }}>{label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── MEET THE AGENTS ───────────────────────────────────────────────── */}
      <section style={{ maxWidth: 1100, margin: '0 auto', padding: '60px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 36 }}>
          <div style={{ width: 3, height: 24, background: '#e31837', borderRadius: 2 }} />
          <span style={{ fontSize: 14, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#fff' }}>MEET YOUR TACTICAL TEAM</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 16 }}>
          {AGENTS.map((a) => (
            <div key={a.name} style={{ background: '#111827', borderRadius: 8, borderTop: `3px solid ${a.color}`, padding: 24, display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <span style={{ fontSize: 28 }}>{a.icon}</span>
                <span style={{ background: a.color + '22', color: a.color, border: `1px solid ${a.color}44`, fontSize: 9, fontWeight: 800, padding: '3px 8px', borderRadius: 3, letterSpacing: '0.08em' }}>
                  ROUND {a.round}
                </span>
              </div>
              <div>
                <p style={{ margin: 0, fontSize: 12, fontWeight: 800, color: '#fff', letterSpacing: '0.08em' }}>{a.name}</p>
                <p style={{ margin: '3px 0 0', fontSize: 10, color: '#555', letterSpacing: '0.06em', textTransform: 'uppercase' }}>{a.role}</p>
              </div>
              <p style={{ margin: 0, fontSize: 13, color: '#9ca3af', lineHeight: 1.6 }}>{a.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── BOTTOM TICKER ─────────────────────────────────────────────────── */}
      <div className="ticker-wrap" style={{ padding: '10px 0', marginTop: 20 }}>
        <div className="ticker-track">
          {[...Array(8)].map((_, i) => (
            <span key={i} style={{ marginRight: 80 }}>
              {TICKER.split('  •  ').filter(Boolean).map((seg, j, arr) => (
                <span key={j}>
                  <span style={{ color: '#e31837', fontWeight: 700, fontSize: 11, letterSpacing: '0.1em' }}>{seg.trim()}</span>
                  {j < arr.length - 1 && <span style={{ color: '#333', margin: '0 20px' }}>•</span>}
                </span>
              ))}
            </span>
          ))}
        </div>
      </div>

      <style>{`@keyframes hero-pulse { 0%,100%{opacity:.6} 50%{opacity:1} }`}</style>
    </div>
  )
}
