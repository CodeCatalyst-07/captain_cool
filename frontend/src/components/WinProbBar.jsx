/**
 * WinProbBar — ESPN broadcast win-probability graphic.
 * Red/green color coding, team name labels, +% impact badge.
 * Props: before, after, battingTeam, bowlingTeam
 */
function pct(val) {
  return Math.min(100, Math.max(0, Math.round((val ?? 0) * 100)))
}

function barColor(p) {
  return p >= 50 ? '#22c55e' : '#e31837'
}

export default function WinProbBar({ before, after, battingTeam = 'Batting', bowlingTeam = 'Bowling' }) {
  const beforePct = pct(before?.win_probability)
  const afterPct  = pct(after?.win_probability)
  const delta     = afterPct - beforePct
  const deltaPos  = delta > 0

  return (
    <div style={{
      background: '#0d0d14', border: '1px solid #1a1a1a',
      borderLeft: '3px solid #e31837', borderRadius: 8, overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        padding: '12px 20px', borderBottom: '1px solid #1a1a1a',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: '0.1em',
            color: '#e31837', textTransform: 'uppercase' }}>Win Probability</span>
        </div>
        {delta !== 0 && (
          <span style={{
            background: deltaPos ? 'rgba(34,197,94,0.15)' : 'rgba(227,24,55,0.15)',
            color: deltaPos ? '#22c55e' : '#e31837',
            border: `1px solid ${deltaPos ? 'rgba(34,197,94,0.3)' : 'rgba(227,24,55,0.3)'}`,
            fontSize: 11, fontWeight: 800, padding: '3px 10px', borderRadius: 4,
            letterSpacing: '0.06em',
          }}>
            {deltaPos ? '+' : ''}{delta}% STRATEGY IMPACT
          </span>
        )}
      </div>

      {/* Bars */}
      <div style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: 20 }}>

        {/* Before */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <div>
              <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.08em',
                color: '#555', textTransform: 'uppercase' }}>Before Debate</span>
              <span style={{ marginLeft: 8, fontSize: 10, color: '#333',
                background: '#1a1a1a', padding: '2px 6px', borderRadius: 3 }}>
                {battingTeam}
              </span>
            </div>
            <span style={{ fontSize: 24, fontWeight: 900, color: barColor(beforePct),
              fontFamily: 'Outfit, sans-serif', lineHeight: 1 }}>
              {beforePct}%
            </span>
          </div>
          <div style={{ height: 8, background: '#1a1a1a', borderRadius: 4, overflow: 'hidden' }}>
            <div className="prob-bar" style={{ width: `${beforePct}%`, background: barColor(beforePct) }} />
          </div>
        </div>

        {/* Divider */}
        <div style={{ borderTop: '1px solid #1a1a1a' }} />

        {/* After */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <div>
              <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.08em',
                color: '#555', textTransform: 'uppercase' }}>After Debate</span>
              <span style={{ marginLeft: 8, fontSize: 10, color: '#333',
                background: '#1a1a1a', padding: '2px 6px', borderRadius: 3 }}>
                {battingTeam}
              </span>
            </div>
            <span style={{ fontSize: 24, fontWeight: 900, color: barColor(afterPct),
              fontFamily: 'Outfit, sans-serif', lineHeight: 1 }}>
              {afterPct}%
            </span>
          </div>
          <div style={{ height: 8, background: '#1a1a1a', borderRadius: 4, overflow: 'hidden' }}>
            <div className="prob-bar" style={{ width: `${afterPct}%`, background: barColor(afterPct) }} />
          </div>
        </div>

        {/* Context stats row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, marginTop: 4 }}>
          {[
            { label: 'RRR Before',   val: before?.required_run_rate?.toFixed(2) ?? '—' },
            { label: 'Balls (Before)', val: before?.balls_remaining ?? '—' },
            { label: 'RRR After',    val: after?.required_run_rate?.toFixed(2) ?? '—' },
            { label: 'Balls (After)',  val: after?.balls_remaining ?? '—' },
          ].map(({ label, val }) => (
            <div key={label} style={{
              background: '#111', borderRadius: 4, padding: '10px 8px', textAlign: 'center',
            }}>
              <p style={{ margin: 0, fontSize: 16, fontWeight: 900, color: '#fff',
                fontFamily: 'Outfit, sans-serif' }}>{val}</p>
              <p style={{ margin: '4px 0 0', fontSize: 9, color: '#444',
                letterSpacing: '0.06em', textTransform: 'uppercase' }}>{label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
