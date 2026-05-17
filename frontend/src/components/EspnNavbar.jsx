/**
 * EspnNavbar — shared broadcast navbar used across all pages.
 * Props:
 *   right — ReactNode rendered on the far right (optional)
 */
import { Link } from 'react-router-dom'

export default function EspnNavbar({ right }) {
  return (
    <nav style={{ background: '#0d0d14', borderBottom: '1px solid #1a1a1a', position: 'sticky', top: 0, zIndex: 50 }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 20px', height: 56, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {/* Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}>
          <div style={{ width: 4, height: 36, background: '#e31837', borderRadius: 2, marginRight: 14 }} />
          <span style={{ fontSize: 20, fontFamily: 'Outfit, sans-serif', fontWeight: 900, color: '#fff', letterSpacing: '-0.5px' }}>
            🏏 CAPTAIN COOL
          </span>
          <span style={{ marginLeft: 12, background: '#e31837', color: '#fff', fontSize: 10, fontWeight: 800, letterSpacing: '0.08em', padding: '3px 9px', borderRadius: 4, textTransform: 'uppercase' }}>
            LIVE AI STRATEGIST
          </span>
        </Link>
        {/* Right slot */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {right ?? (
            <span style={{ fontSize: 11, color: '#555', fontWeight: 500, letterSpacing: '0.04em' }}>
              Powered by Gemini 2.5
            </span>
          )}
        </div>
      </div>
    </nav>
  )
}
