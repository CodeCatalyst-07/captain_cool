/**
 * ResultCards — ESPN broadcast panel cards.
 * All JSON parsing (StatsBody) and markdown rendering (renderMarkdown) logic
 * preserved exactly — only the visual structure has changed.
 */

// ─── JSON helpers (unchanged logic) ──────────────────────────────────────────

function tryParseJson(raw) {
  if (!raw || typeof raw !== 'string') return null
  let cleaned = raw.trim()
  cleaned = cleaned.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '').trim()
  if (!cleaned.startsWith('{') && !cleaned.startsWith('[')) return null
  try { return JSON.parse(cleaned) } catch { return null }
}

function formatValue(val) {
  if (val === null || val === undefined) return '—'
  if (typeof val === 'boolean') return val ? 'Yes' : 'No'
  if (typeof val === 'number') return String(val)
  if (typeof val === 'string') return val || '—'
  if (Array.isArray(val)) {
    if (val.length === 0) return '—'
    return val.map((v) => (typeof v === 'string' ? v : JSON.stringify(v))).join(' · ')
  }
  if (typeof val === 'object') {
    return Object.entries(val).map(([k, v]) => `${k}: ${v}`).join(', ') || '—'
  }
  return String(val)
}

function toLabel(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function rowAccent(key) {
  if (key === 'phase')           return '#60a5fa'
  if (key.includes('dew'))      return '#22d3ee'
  if (key.includes('depth'))    return '#f59e0b'
  if (key.includes('run_rate')) return '#22c55e'
  if (key.includes('matchup'))  return '#a78bfa'
  if (key.includes('weather'))  return '#38bdf8'
  if (key.includes('bowler'))   return '#fb923c'
  return '#d1d5db'
}

// ─── Markdown renderer (unchanged logic) ─────────────────────────────────────

function renderMarkdown(text) {
  if (!text) return null
  const boldParts = text.split(/(\*\*[^*]+\*\*)/g)
  return boldParts.map((segment, i) => {
    if (segment.startsWith('**') && segment.endsWith('**')) {
      return <strong key={i} style={{ fontWeight: 700, color: '#fff' }}>{segment.slice(2, -2)}</strong>
    }
    const italicParts = segment.split(/(\*[^*]+\*)/g)
    if (italicParts.length === 1) return segment
    return italicParts.map((s, j) => {
      if (s.startsWith('*') && s.endsWith('*')) {
        return <em key={`${i}-${j}`}>{s.slice(1, -1)}</em>
      }
      return s
    })
  })
}

// ─── Stats body (unchanged logic, new visual) ─────────────────────────────────

function StatsBody({ content }) {
  const data = tryParseJson(content)

  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    return (
      <pre style={{
        fontSize: 12, color: '#9ca3af', fontFamily: 'monospace',
        whiteSpace: 'pre-wrap', wordBreak: 'break-word', lineHeight: 1.6,
        margin: 0, maxHeight: 320, overflowY: 'auto',
      }}>
        {content}
      </pre>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
      {Object.entries(data).map(([key, val], idx, arr) => {
        const isArray = Array.isArray(val)
        return (
          <div key={key} style={{
            display: 'flex', gap: 16, padding: '10px 0',
            borderBottom: idx < arr.length - 1 ? '1px solid #1a1a1a' : 'none',
            alignItems: isArray ? 'flex-start' : 'center',
          }}>
            <span style={{
              fontSize: 10, fontWeight: 700, letterSpacing: '0.08em',
              textTransform: 'uppercase', color: '#555',
              width: 130, flexShrink: 0, paddingTop: isArray ? 2 : 0,
            }}>
              {toLabel(key)}
            </span>
            {isArray && val.length > 0 ? (
              <ul style={{ flex: 1, margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 4 }}>
                {val.map((item, i) => (
                  <li key={i} style={{ fontSize: 12, color: rowAccent(key), lineHeight: 1.5 }}>
                    <span style={{ color: '#e31837', marginRight: 6 }}>▸</span>
                    {typeof item === 'string' ? item : JSON.stringify(item)}
                  </li>
                ))}
              </ul>
            ) : (
              <span style={{ fontSize: 13, fontWeight: 600, color: rowAccent(key) }}>
                {formatValue(val)}
              </span>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── Card config ──────────────────────────────────────────────────────────────

const CARDS = [
  {
    key: 'stats_summary',
    icon: '📊',
    label: 'ROUND 1',
    title: 'Stats Summary',
    role: 'StatsAnalyst · Data Engine',
    accentColor: '#3b82f6',
    stats: true,
  },
  {
    key: 'initial_proposal',
    icon: '🏏',
    label: 'ROUND 2',
    title: 'Strategist\'s Proposal',
    role: 'Strategist · Virtual Captain',
    accentColor: '#22c55e',
  },
  {
    key: 'devils_challenge',
    icon: '😈',
    label: 'ROUND 3',
    title: 'Devil\'s Challenge',
    role: 'DevilsAdvocate · Data Analyst',
    accentColor: '#e31837',
  },
  {
    key: 'final_decision',
    icon: '🏆',
    label: 'ROUND 4',
    title: 'Final Decision',
    role: 'Strategist · Revised & Decisive',
    accentColor: '#f59e0b',
    gold: true,
    large: true,
  },
  {
    key: 'commentary',
    icon: '🎙️',
    label: 'ROUND 5',
    title: 'Live Commentary',
    role: 'Commentator · Harsha × Shastri',
    accentColor: '#7c3aed',
    purple: true,
    italic: true,
  },
]

// ─── Main component ────────────────────────────────────────────────────────────

export default function ResultCards({ result }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {CARDS.map((card) => {
        const content = result[card.key] ?? '—'

        const cardBg   = card.gold ? '#1a1200' : card.purple ? '#0f0a1a' : '#0d0d14'
        const borderL  = card.accentColor

        return (
          <div
            key={card.key}
            className="broadcast-card"
            style={{
              background: cardBg,
              border: '1px solid #1a1a1a',
              borderLeftColor: borderL,
              borderRadius: 8,
              overflow: 'hidden',
            }}
          >
            {/* Card header */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '12px 20px', borderBottom: '1px solid #1a1a1a',
              background: 'rgba(0,0,0,0.3)',
            }}>
              <span style={{ fontSize: 20 }}>{card.icon}</span>
              <div style={{ flex: 1 }}>
                <p style={{
                  margin: 0, fontSize: card.large ? 15 : 13,
                  fontWeight: 800, color: '#fff', letterSpacing: '0.02em',
                }}>
                  {card.title}
                </p>
                <p style={{ margin: 0, fontSize: 10, color: '#555',
                  letterSpacing: '0.06em', textTransform: 'uppercase', marginTop: 2 }}>
                  {card.role}
                </p>
              </div>
              {/* Round badge */}
              <span style={{
                background: card.accentColor + '22',
                color: card.accentColor,
                border: `1px solid ${card.accentColor}44`,
                fontSize: 10, fontWeight: 800, padding: '3px 10px',
                borderRadius: 4, letterSpacing: '0.08em',
                flexShrink: 0,
              }}>
                {card.label}
              </span>
            </div>

            {/* Card body */}
            <div style={{ padding: '18px 20px' }}>
              {card.stats ? (
                <StatsBody content={content} />
              ) : card.purple ? (
                /* Commentary — broadcast quote style */
                <div style={{
                  borderLeft: '3px solid #7c3aed', paddingLeft: 16,
                }}>
                  <p style={{
                    margin: 0, fontSize: 15, lineHeight: 1.8,
                    color: '#d1c4e9', fontStyle: 'italic',
                    fontFamily: 'Georgia, serif',
                  }}>
                    {renderMarkdown(content)}
                  </p>
                </div>
              ) : (
                <p style={{
                  margin: 0,
                  fontSize: card.large ? 14 : 13,
                  lineHeight: 1.8,
                  color: card.gold ? '#fef3c7' : '#d1d5db',
                  whiteSpace: 'pre-wrap',
                  fontWeight: card.large ? 500 : 400,
                }}>
                  {renderMarkdown(content)}
                </p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
