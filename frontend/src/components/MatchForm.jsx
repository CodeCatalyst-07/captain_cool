/**
 * MatchForm — ESPN broadcast style input form.
 * Three labelled sections: MATCH STATE / TEAMS & PLAYERS / CONDITIONS
 * All field logic and prop interface unchanged.
 */
export default function MatchForm({ form, setForm }) {
  const set = (key) => (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm((prev) => ({ ...prev, [key]: val }))
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>

      {/* ── MATCH STATE ──────────────────────────────────────────────────── */}
      <div>
        <div className="espn-section-header">
          <span className="espn-section-title">Match State</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 16 }}>

          <div>
            <label className="espn-label" htmlFor="innings">Innings</label>
            <select id="innings" value={form.innings} onChange={set('innings')} className="espn-input">
              <option value={1}>1st Innings</option>
              <option value={2}>2nd Innings (Chase)</option>
            </select>
          </div>

          <div>
            <label className="espn-label" htmlFor="over">Current Over</label>
            <input id="over" type="number" min={0} max={20} value={form.over}
              onChange={set('over')} className="espn-input" placeholder="e.g. 14" />
          </div>

          <div>
            <label className="espn-label" htmlFor="score">Score</label>
            <input id="score" type="text" value={form.score}
              onChange={set('score')} className="espn-input" placeholder="e.g. 134/4" />
          </div>

          <div>
            <label className="espn-label" htmlFor="target">Target</label>
            <input id="target" type="number" min={0} value={form.target}
              onChange={set('target')} className="espn-input" placeholder="0 if 1st innings" />
          </div>

          <div>
            <label className="espn-label" htmlFor="pitch_type">Pitch Type</label>
            <select id="pitch_type" value={form.pitch_type} onChange={set('pitch_type')} className="espn-input">
              <option value="Flat">Flat</option>
              <option value="Sticky">Sticky</option>
              <option value="Dusty">Dusty</option>
              <option value="Green">Green</option>
            </select>
          </div>

          <div>
            <label className="espn-label" htmlFor="venue">Venue</label>
            <input id="venue" type="text" value={form.venue}
              onChange={set('venue')} className="espn-input" placeholder="e.g. Wankhede Stadium Mumbai" />
          </div>

        </div>
      </div>

      {/* ── TEAMS & PLAYERS ──────────────────────────────────────────────── */}
      <div>
        <div className="espn-section-header">
          <span className="espn-section-title">Teams &amp; Players</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 16 }}>

          <div>
            <label className="espn-label" htmlFor="batting_team">Batting Team</label>
            <input id="batting_team" type="text" value={form.batting_team}
              onChange={set('batting_team')} className="espn-input" placeholder="e.g. MI" />
          </div>

          <div>
            <label className="espn-label" htmlFor="bowling_team">Bowling Team</label>
            <input id="bowling_team" type="text" value={form.bowling_team}
              onChange={set('bowling_team')} className="espn-input" placeholder="e.g. CSK" />
          </div>

          <div>
            <label className="espn-label" htmlFor="striker">Striker</label>
            <input id="striker" type="text" value={form.striker}
              onChange={set('striker')} className="espn-input" placeholder="Batsman on strike" />
          </div>

          <div>
            <label className="espn-label" htmlFor="non_striker">Non-Striker</label>
            <input id="non_striker" type="text" value={form.non_striker}
              onChange={set('non_striker')} className="espn-input" placeholder="Other end" />
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <label className="espn-label" htmlFor="bowlers_remaining">Bowlers Remaining (name:overs)</label>
            <input id="bowlers_remaining" type="text" value={form.bowlers_remaining}
              onChange={set('bowlers_remaining')} className="espn-input" placeholder="Bumrah:2,Chahar:3" />
          </div>

          <div>
            <label className="espn-label" htmlFor="cricbuzz_url">Cricbuzz URL (optional)</label>
            <input id="cricbuzz_url" type="text" value={form.cricbuzz_url}
              onChange={set('cricbuzz_url')} className="espn-input" placeholder="https://cricbuzz.com/..." />
          </div>

        </div>
      </div>

      {/* ── CONDITIONS ───────────────────────────────────────────────────── */}
      <div>
        <div className="espn-section-header">
          <span className="espn-section-title">Conditions</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 16 }}>

          {/* Dew Factor toggle */}
          <div>
            <span className="espn-label">Dew Factor</span>
            <label htmlFor="dew_factor" style={{
              display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer',
              background: '#1a1a2e', border: '1px solid #2a2a3e', borderRadius: 4,
              padding: '10px 14px',
            }}>
              <input id="dew_factor" type="checkbox" checked={form.dew_factor}
                onChange={set('dew_factor')} className="sr-only" />
              <div className="espn-toggle-track"
                style={{ background: form.dew_factor ? '#e31837' : '#2a2a3e' }}>
                <div className="espn-toggle-thumb"
                  style={{ transform: form.dew_factor ? 'translateX(20px)' : 'translateX(0)' }} />
              </div>
              <span style={{ fontSize: 12, color: form.dew_factor ? '#ff6b6b' : '#555', fontWeight: 600 }}>
                {form.dew_factor ? 'Dew expected — HIGH RISK' : 'No significant dew'}
              </span>
            </label>
          </div>

          {/* Impact Player toggle */}
          <div>
            <span className="espn-label">Impact Player</span>
            <label htmlFor="impact_player" style={{
              display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer',
              background: '#1a1a2e', border: '1px solid #2a2a3e', borderRadius: 4,
              padding: '10px 14px',
            }}>
              <input id="impact_player" type="checkbox" checked={form.impact_player_available}
                onChange={set('impact_player_available')} className="sr-only" />
              <div className="espn-toggle-track"
                style={{ background: form.impact_player_available ? '#f59e0b' : '#2a2a3e' }}>
                <div className="espn-toggle-thumb"
                  style={{ transform: form.impact_player_available ? 'translateX(20px)' : 'translateX(0)' }} />
              </div>
              <span style={{ fontSize: 12, color: form.impact_player_available ? '#fbbf24' : '#555', fontWeight: 600 }}>
                {form.impact_player_available ? 'Substitution available' : 'Already used'}
              </span>
            </label>
          </div>

        </div>
      </div>
    </div>
  )
}
