/**
 * LoadingSpinner — ESPN broadcast "ANALYZING..." overlay.
 * Radar pulse rings in red, uppercase status text with dot animation.
 */

const ROUNDS = [
  { icon: '📊', label: 'STATS ANALYST', sub: 'Fetching live match data' },
  { icon: '🏏', label: 'STRATEGIST',    sub: 'Crafting tactical decision' },
  { icon: '😈', label: 'DEVIL\'S ADVOCATE', sub: 'Stress-testing the plan' },
  { icon: '✅', label: 'STRATEGIST',    sub: 'Defending under fire' },
  { icon: '🎙️', label: 'COMMENTATOR',  sub: 'Building the narrative' },
]

export default function LoadingSpinner() {
  return (
    <div style={{
      background: '#0d0d14', border: '1px solid #1a1a1a',
      borderLeft: '3px solid #e31837', borderRadius: 8,
      padding: '36px 24px', display: 'flex', flexDirection: 'column',
      alignItems: 'center', gap: 32,
    }}>

      {/* Radar pulse */}
      <div style={{ position: 'relative', width: 80, height: 80 }}>
        <div className="radar-ring" />
        <div className="radar-ring" />
        <div className="radar-ring" />
        {/* Centre dot */}
        <div style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%,-50%)',
          width: 16, height: 16, borderRadius: '50%',
          background: '#e31837',
          boxShadow: '0 0 12px #e31837',
        }} />
      </div>

      {/* Status text */}
      <div style={{ textAlign: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginBottom: 8 }}>
          <span style={{ fontSize: 18, fontWeight: 900, letterSpacing: '0.14em', color: '#fff' }}>
            AGENTS DEBATING
          </span>
          <span className="dot-1" style={{ width: 5, height: 5, borderRadius: '50%', background: '#e31837', display: 'inline-block' }} />
          <span className="dot-2" style={{ width: 5, height: 5, borderRadius: '50%', background: '#e31837', display: 'inline-block' }} />
          <span className="dot-3" style={{ width: 5, height: 5, borderRadius: '50%', background: '#e31837', display: 'inline-block' }} />
        </div>
        <p style={{ color: '#555', fontSize: 12, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          Typically 30–90 seconds
        </p>
      </div>

      {/* Round indicators */}
      <div style={{ width: '100%', maxWidth: 380, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {ROUNDS.map((r, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            background: '#111', borderRadius: 4, padding: '10px 14px',
            borderLeft: '2px solid #1a1a1a',
            animation: `slide-up 0.4s ease forwards`,
            animationDelay: `${i * 0.15}s`,
            opacity: 0,
          }}>
            <span style={{ fontSize: 16 }}>{r.icon}</span>
            <div style={{ flex: 1 }}>
              <p style={{ margin: 0, fontSize: 11, fontWeight: 800, letterSpacing: '0.08em', color: '#e31837' }}>{r.label}</p>
              <p style={{ margin: 0, fontSize: 11, color: '#444', marginTop: 2 }}>{r.sub}</p>
            </div>
            <div style={{ display: 'flex', gap: 3 }}>
              {[0,1,2].map(j => (
                <span key={j} style={{
                  width: 4, height: 4, borderRadius: '50%', background: '#222',
                  display: 'block',
                  animation: `dot-pulse 1.4s ease-in-out infinite`,
                  animationDelay: `${i * 0.2 + j * 0.15}s`,
                }} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
