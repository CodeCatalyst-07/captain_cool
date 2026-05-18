import { useNavigate } from 'react-router-dom'
import EspnNavbar from '../components/EspnNavbar'

const STEPS = [
  { label: 'YOU INPUT MATCH STATE',                     detail: 'Fill in the live situation via the form', color: '#6b7280' },
  { label: 'STATS ANALYST',                             detail: 'Fetches live data + venue weather',        color: '#3b82f6' },
  { label: 'STRATEGIST',                                detail: 'Proposes tactical decision',               color: '#22c55e' },
  { label: "DEVIL'S ADVOCATE",                          detail: 'Raises 2 objections',                      color: '#e31837' },
  { label: 'STRATEGIST DEFENDS',                        detail: 'Revises or holds the decision',            color: '#22c55e' },
  { label: 'COMMENTATOR',                               detail: 'Narrates the final call',                  color: '#7c3aed' },
  { label: "YOU GET THE CAPTAIN'S DECISION",            detail: 'Full debate + commentary delivered',        color: '#f59e0b' },
]

const TECH = [
  { icon: '✨', name: 'Google Gemini 2.0 Flash', desc: 'State-of-the-art multimodal LLM powering all four agents with real-time reasoning and tool use.', badge: 'GOOGLE OFFICIAL', badgeColor: '#3b82f6' },
  { icon: '🤖', name: 'Agent Development Kit (ADK)', desc: 'Google\'s open-source framework for building multi-agent systems with session management and async runners.', badge: 'GOOGLE OFFICIAL', badgeColor: '#22c55e' },
  { icon: '⚡', name: 'FastAPI + React', desc: 'High-performance async Python backend with a Vite-powered React frontend for a real-time broadcast experience.', badge: 'OPEN SOURCE', badgeColor: '#f59e0b' },
]

export default function HowItWorksPage() {
  const navigate = useNavigate()

  const navRight = (
    <button onClick={() => navigate('/analyze')} style={{ background: '#e31837', color: '#fff', border: 'none', borderRadius: 4, padding: '8px 18px', fontSize: 11, fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', cursor: 'pointer' }}>
      ANALYZE MATCH →
    </button>
  )

  return (
    <div style={{ background: '#0a0a0f', minHeight: '100vh' }}>
      <EspnNavbar right={navRight} />

      <main style={{ maxWidth: 900, margin: '0 auto', padding: '48px 24px 80px', display: 'flex', flexDirection: 'column', gap: 64 }}>

        {/* Page heading */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 4, height: 28, background: '#e31837', borderRadius: 2 }} />
          <h1 style={{ margin: 0, fontSize: 'clamp(20px,3vw,28px)', fontWeight: 900, color: '#fff', fontFamily: 'Outfit, sans-serif', letterSpacing: '-0.5px', textTransform: 'uppercase' }}>
            HOW CAPTAIN COOL WORKS
          </h1>
        </div>

        {/* ── SECTION 1: Architecture Flow ─────────────────────────────── */}
        <section>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 32 }}>
            <div style={{ width: 3, height: 20, background: '#e31837', borderRadius: 2 }} />
            <span style={{ fontSize: 12, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#e31837' }}>Architecture Flow</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0 }}>
            {STEPS.map((step, i) => (
              <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', maxWidth: 520 }}>
                {/* Box */}
                <div style={{
                  width: '100%', background: '#0d0d14',
                  border: `1px solid ${step.color}44`,
                  borderLeft: `4px solid ${step.color}`,
                  borderRadius: 6, padding: '16px 20px',
                  display: 'flex', alignItems: 'center', gap: 16,
                }}>
                  <div style={{ width: 10, height: 10, borderRadius: '50%', background: step.color, flexShrink: 0 }} />
                  <div>
                    <p style={{ margin: 0, fontSize: 12, fontWeight: 800, color: '#fff', letterSpacing: '0.06em' }}>{step.label}</p>
                    <p style={{ margin: '3px 0 0', fontSize: 11, color: '#555' }}>{step.detail}</p>
                  </div>
                </div>

                {/* Arrow connector (not on last item) */}
                {i < STEPS.length - 1 && (
                  <div style={{ height: 36, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 3 }}>
                    <div style={{ width: 1, flex: 1, borderLeft: '2px dashed #e31837', opacity: 0.5, animation: 'flow-dash 1.5s linear infinite' }} />
                    <div style={{ width: 0, height: 0, borderLeft: '5px solid transparent', borderRight: '5px solid transparent', borderTop: '8px solid #e31837', opacity: 0.7 }} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* ── SECTION 2: Tech Stack ─────────────────────────────────────── */}
        <section>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 24 }}>
            <div style={{ width: 3, height: 20, background: '#e31837', borderRadius: 2 }} />
            <span style={{ fontSize: 12, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#e31837' }}>Tech Stack</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 16 }}>
            {TECH.map((t) => (
              <div key={t.name} style={{ background: '#0d0d14', border: '1px solid #1a1a1a', borderRadius: 8, padding: 24, display: 'flex', flexDirection: 'column', gap: 14 }}>
                <span style={{ fontSize: 32 }}>{t.icon}</span>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
                    <p style={{ margin: 0, fontSize: 13, fontWeight: 800, color: '#fff' }}>{t.name}</p>
                    <span style={{ background: t.badgeColor + '22', color: t.badgeColor, border: `1px solid ${t.badgeColor}44`, fontSize: 9, fontWeight: 800, padding: '2px 7px', borderRadius: 3, letterSpacing: '0.08em', flexShrink: 0 }}>
                      {t.badge}
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: 12, color: '#6b7280', lineHeight: 1.65 }}>{t.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── SECTION 3: CTA ────────────────────────────────────────────── */}
        <section style={{ textAlign: 'center', padding: '40px 0' }}>
          <h2 style={{ margin: '0 0 8px', fontSize: 'clamp(22px,3vw,32px)', fontWeight: 900, color: '#fff', fontFamily: 'Outfit, sans-serif', textTransform: 'uppercase' }}>
            READY TO STRATEGIZE?
          </h2>
          <p style={{ margin: '0 0 36px', fontSize: 14, color: '#555' }}>
            Input a live match state and let 4 AI agents debate the best call.
          </p>
          <button
            onClick={() => navigate('/analyze')}
            style={{ background: '#e31837', color: '#fff', border: 'none', borderRadius: 4, padding: '18px 48px', fontSize: 14, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', cursor: 'pointer' }}
          >
            ANALYZE A MATCH NOW →
          </button>
        </section>
      </main>

      <style>{`
        @keyframes flow-dash {
          0%   { background-position: 0 0; }
          100% { background-position: 0 20px; }
        }
      `}</style>
    </div>
  )
}
