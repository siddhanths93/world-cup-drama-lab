"""
ui_helpers.py

Clean editorial visual system for World Cup Drama Lab.
No external images, official logos, team crests, or copyrighted visual assets.
"""

DRAMA_COLORS = {
    "Low Drama": "#64748B",
    "Decent Watch": "#2563EB",
    "Proper World Cup Tension": "#B45309",
    "Chaos Match": "#DC2626",
    "Football Heritage Moment": "#7C3AED",
}

ENTERTAINMENT_COLORS = {
    "Low Event": "#64748B",
    "Respectable Watch": "#2563EB",
    "Goal Fest": "#B45309",
    "Pure Entertainment": "#15803D",
}

VERDICT_COLORS = {
    "Expected Result": "#15803D",
    "Nervier Than It Looks": "#B45309",
    "Upset Signal": "#7C3AED",
    "Scoreline Shock": "#DC2626",
    "Hard to Judge": "#64748B",
}

QUALIFICATION_COLORS = {
    "Safe": "#15803D",
    "In Control": "#0F766E",
    "Bubble Watch": "#B45309",
    "Needs Help": "#DC2626",
    "Eliminated": "#64748B",
}

MATCH_TYPE_COLORS = {
    "Business Trip": "#2563EB",
    "Nervy Grind": "#B45309",
    "Chaos Ball": "#DC2626",
    "Upset Energy": "#7C3AED",
    "Giant Sweating": "#C2410C",
    "Group Stage Tax": "#64748B",
    "Heartbreak Mode": "#991B1B",
    "Calculator Mode Activated": "#2563EB",
    "Pressure Match": "#7C3AED",
    "Survival Match": "#0F766E",
}

PULSE_COLORS = {
    "Group Chaos": "#DC2626",
    "Pressure": "#B45309",
    "Entertainment": "#7C3AED",
    "Next Match": "#2563EB",
    "Survival": "#0F766E",
    "Scenario": "#64748B",
}

REALISM_COLORS = {
    "Realistic": "#15803D",
    "Aggressive": "#B45309",
    "Chaos Prediction": "#DC2626",
    "Extremely Spicy": "#7C3AED",
}

CHAOS_COLORS = {
    "Settled": "#15803D",
    "Still Open": "#2563EB",
    "Calculator Mode Brewing": "#B45309",
    "Pure Chaos": "#DC2626",
}


def escape_html(value):
    if value is None:
        return ""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def badge_html(label, color_map, default_color="#64748B"):
    raw_label = str(label)
    color = color_map.get(raw_label, default_color)
    return (
        f'<span class="wcdl-badge" style="--badge-color:{color};">'
        f'{escape_html(raw_label)}</span>'
    )


def progress_html(score, color="#2563EB"):
    score = max(0, min(100, int(round(score))))
    return (
        f'<div class="wcdl-progress">'
        f'<div class="wcdl-progress-fill" style="width:{score}%; background:{color};"></div>'
        f'</div>'
    )


def card_html(title=None, body=None, label=None, badge=None, badge_color_map=None, meta=None,
              accent=None, large=False, footer=None, variant="default"):
    title_html = f'<div class="wcdl-card-title">{escape_html(title)}</div>' if title else ""
    label_html = f'<div class="wcdl-card-label">{escape_html(label)}</div>' if label else ""
    meta_html = f'<div class="wcdl-card-meta">{escape_html(meta)}</div>' if meta else ""
    badge_part = badge_html(badge, badge_color_map or {}, accent or "#64748B") if badge else ""
    badge_html_block = f'<div class="wcdl-card-badge-row">{badge_part}</div>' if badge_part else ""
    body_html = f'<div class="wcdl-card-body">{body}</div>' if body else ""
    footer_html = f'<div class="wcdl-card-footer">{escape_html(footer)}</div>' if footer else ""
    accent_style = f'--card-accent:{accent};' if accent else ""
    size_class = " wcdl-card-large" if large else ""
    variant_class = f" wcdl-card-{variant}"
    return (
        f'<div class="wcdl-card{size_class}{variant_class}" style="{accent_style}">'
        f'{label_html}{title_html}{meta_html}{badge_html_block}{body_html}{footer_html}'
        f'</div>'
    )


def stat_card_html(label, value, subtitle="", accent="#2563EB", badge=None, badge_color_map=None):
    subtitle_html = f'<div class="wcdl-stat-subtitle">{escape_html(subtitle)}</div>' if subtitle else ""
    badge_part = badge_html(badge, badge_color_map or {}, accent) if badge else ""
    badge_block = f'<div style="margin-top:10px;">{badge_part}</div>' if badge_part else ""
    return (
        f'<div class="wcdl-stat-card" style="--card-accent:{accent};">'
        f'<div class="wcdl-card-label">{escape_html(label)}</div>'
        f'<div class="wcdl-stat-value">{escape_html(value)}</div>'
        f'{subtitle_html}{badge_block}'
        f'</div>'
    )


def inject_global_css():
    return """
<style>
:root {
  --wcdl-bg: #F6F7F2;
  --wcdl-card: #FFFFFF;
  --wcdl-card-soft: #F8FAFC;
  --wcdl-ink: #102033;
  --wcdl-muted: #64748B;
  --wcdl-line: #E2E8F0;
  --wcdl-blue: #2563EB;
  --wcdl-blue-soft: #EFF6FF;
  --wcdl-amber: #F59E0B;
  --wcdl-green: #16A34A;
  --wcdl-red: #DC2626;
}

.stApp {
  background:
    radial-gradient(circle at 92% 8%, rgba(37,99,235,0.08), transparent 26%),
    radial-gradient(circle at 8% 5%, rgba(245,158,11,0.10), transparent 22%),
    linear-gradient(135deg, #F6F7F2 0%, #FFFFFF 52%, #F3F6FB 100%);
  color: var(--wcdl-ink);
}

.block-container {
  padding-top: 1.35rem !important;
  padding-bottom: 3rem !important;
  max-width: 1680px !important;
}

/* Hide Streamlit chrome/sidebar; this app uses main-canvas navigation only. */
#MainMenu, footer, header {visibility: hidden;}
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display:none;}

h1, h2, h3, h4, h5, p, li, div, span, label {
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}
h1, h2, h3, h4, h5 { color: var(--wcdl-ink) !important; letter-spacing: -0.04em; }

[data-testid="stCaptionContainer"], .stCaption, small { color: var(--wcdl-muted) !important; }
hr { border-color: var(--wcdl-line) !important; }

/* Header */
.wcdl-header {
  display:grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap:28px;
  align-items:end;
  padding: 10px 0 18px 0;
  border-bottom: 1px solid var(--wcdl-line);
  margin-bottom: 8px;
}
.wcdl-snapshot {
  background:#FFFFFF;
  border:1px solid var(--wcdl-line);
  border-radius:16px;
  padding:16px 18px;
  box-shadow:0 10px 24px rgba(15,23,42,0.06);
}
.wcdl-snapshot-title {
  color:var(--wcdl-blue);
  text-transform:uppercase;
  letter-spacing:.12em;
  font-size:.72rem;
  font-weight:950;
  margin-bottom:10px;
}
.wcdl-snapshot-row {
  display:flex;
  justify-content:space-between;
  gap:14px;
  padding:7px 0;
  border-bottom:1px solid #EEF2F7;
  color:#475569;
  font-size:.9rem;
}
.wcdl-snapshot-row:last-child { border-bottom:0; }
.wcdl-snapshot-row strong { color:#07122B; }
.wcdl-header-kicker {
  color: var(--wcdl-blue);
  text-transform: uppercase;
  letter-spacing: .22em;
  font-weight: 950;
  font-size: .82rem;
  margin-bottom: 10px;
}
.wcdl-header-title {
  color: #07122B;
  text-transform: uppercase;
  font-weight: 1000;
  letter-spacing: -.065em;
  line-height: .92;
  font-size: clamp(2.5rem, 5.6vw, 5.1rem);
  max-width: 1120px;
}
.wcdl-header-subtitle {
  color: #334155;
  font-size: 1.06rem;
  margin-top: 14px;
  line-height: 1.55;
}

/* Inputs */
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input,
.stTextInput input {
  background: #FFFFFF !important;
  border: 1px solid #CBD5E1 !important;
  color: var(--wcdl-ink) !important;
  border-radius: 12px !important;
  min-height: 42px;
  box-shadow: none !important;
}
.stNumberInput label, .stSelectbox label, .stRadio label, .stTextInput label {
  color: #334155 !important;
  font-weight: 700 !important;
}

/* Buttons for scenario controls only */
.stButton > button {
  background: #FFFFFF !important;
  border: 1px solid #CBD5E1 !important;
  color: var(--wcdl-ink) !important;
  border-radius: 12px !important;
  padding: 0.55rem 0.9rem !important;
  font-weight: 850 !important;
  transition: all .15s ease;
}
.stButton > button:hover {
  background: var(--wcdl-blue-soft) !important;
  border-color: var(--wcdl-blue) !important;
  color: var(--wcdl-blue) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 28px;
  border-bottom: 0 !important;
  margin: 8px 0 22px 0;
}
.stTabs [data-baseweb="tab"] {
  color: #334155;
  padding: 14px 4px 9px 4px;
  border-radius: 0;
  border-bottom: 3px solid transparent;
  background: transparent;
  font-weight: 950;
  font-size: .98rem;
  text-transform: uppercase;
  letter-spacing: .06em;
}
.stTabs [aria-selected="true"] {
  color: var(--wcdl-blue) !important;
  border-bottom: 3px solid var(--wcdl-blue) !important;
  background: transparent !important;
}


/* App nav pills */
.wcdl-nav-spacer { margin: 4px 0 18px 0; }
div[data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"] { min-height: 42px; }
.wcdl-action-card {
  display:block;
  text-decoration:none !important;
}

/* Match board cards are rendered as anchors to avoid Streamlit button styling regressions. */

/* Section headers */
.wcdl-section-title {
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:16px;
  margin: 28px 0 12px 0;
  padding-bottom: 4px;
}
.wcdl-section-title h3 {
  margin:0 !important;
  font-size:1.12rem !important;
  text-transform: uppercase;
  letter-spacing: .03em;
}
.wcdl-section-note { color: var(--wcdl-muted); font-size:.88rem; }

/* Cards */
.wcdl-card, .wcdl-stat-card {
  position: relative;
  background: var(--wcdl-card);
  border: 1px solid var(--wcdl-line);
  border-radius: 14px;
  padding: 18px 18px;
  margin-bottom: 16px;
  box-shadow: 0 10px 24px rgba(15,23,42,0.06);
  overflow: hidden;
}
.wcdl-card-large { min-height: 150px; padding: 22px; }
.wcdl-card-label {
  text-transform: uppercase;
  letter-spacing:.11em;
  color: var(--wcdl-blue);
  font-size:.72rem;
  font-weight:950;
  margin-bottom:8px;
}
.wcdl-card-title {
  color: #07122B;
  font-weight:950;
  line-height:1.08;
  font-size:1.22rem;
  margin-bottom:8px;
}
.wcdl-card-meta { color: var(--wcdl-muted); font-size:.86rem; margin-bottom:10px; }
.wcdl-card-body { color:#334155; line-height:1.55; font-size:.95rem; }
.wcdl-card-footer {
  color:var(--wcdl-muted);
  border-top:1px solid var(--wcdl-line);
  margin-top:14px;
  padding-top:12px;
  font-size:.86rem;
}
.wcdl-stat-value { color:#07122B; font-weight:950; font-size:1.65rem; line-height:1.1; }
.wcdl-stat-subtitle { color:var(--wcdl-muted); font-size:.86rem; line-height:1.45; margin-top:7px; }
.wcdl-badge {
  display:inline-flex;
  align-items:center;
  color: var(--badge-color);
  background: color-mix(in srgb, var(--badge-color) 10%, #FFFFFF);
  border: 1px solid color-mix(in srgb, var(--badge-color) 28%, #FFFFFF);
  border-radius: 10px;
  padding: 5px 10px;
  font-size: .78rem;
  font-weight: 900;
  white-space: nowrap;
}
.wcdl-card-badge-row { margin: 8px 0 12px 0; }
.wcdl-progress {
  width:100%; height:7px; background:#E2E8F0; border-radius:999px; overflow:hidden; margin: 12px 0 9px 0;
}
.wcdl-progress-fill { height:100%; border-radius:999px; }

/* Team/group finder */
.wcdl-finder-header {
  background:#FFFFFF;
  border:1px solid var(--wcdl-line);
  border-radius:16px;
  padding:18px 20px;
  margin: 12px 0 12px 0;
  box-shadow:0 10px 24px rgba(15,23,42,0.05);
}
.wcdl-finder-header h3 {
  margin:0 0 6px 0 !important;
  font-size:1.08rem !important;
  text-transform:uppercase;
  letter-spacing:.04em;
}
.wcdl-finder-header p {
  margin:0;
  color:var(--wcdl-muted);
  font-size:.9rem;
  line-height:1.4;
}
.wcdl-group-context-panel {
  background:#FFFFFF;
  border:1px solid var(--wcdl-line);
  border-radius:16px;
  padding:18px;
  margin: 18px 0 18px 0;
  box-shadow:0 10px 24px rgba(15,23,42,0.05);
  display:flex;
  align-items:center;
  gap:18px;
  flex-wrap:wrap;
}
.wcdl-group-context-title {
  color:#07122B;
  font-size:1.05rem;
  font-weight:950;
  margin-top:2px;
}
.wcdl-team-chip-row { display:flex; gap:10px; flex-wrap:wrap; margin-top:10px; }
.wcdl-team-chip {
  display:inline-flex;
  border:1px solid #CBD5E1;
  background:#FFFFFF;
  color:#102033;
  border-radius:10px;
  padding:7px 12px;
  font-size:.86rem;
  font-weight:850;
}

/* Match board */
.wcdl-board-subhead {
  color: var(--wcdl-blue);
  text-transform: uppercase;
  letter-spacing: .08em;
  font-weight: 950;
  font-size: .88rem;
  margin: 14px 0 8px 0;
}
.wcdl-match-link {
  display:block;
  text-decoration:none !important;
  color:inherit !important;
}
.wcdl-match-card {
  display:grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items:center;
  gap:14px;
  background:#FFFFFF;
  border:1px solid var(--wcdl-line);
  border-radius:12px;
  padding:15px 18px;
  margin-bottom:10px;
  box-shadow:0 6px 15px rgba(15,23,42,0.04);
  transition:transform .12s ease, border-color .12s ease, background .12s ease, box-shadow .12s ease;
}
.wcdl-match-card:hover {
  transform:translateY(-1px);
  border-color:var(--wcdl-blue);
  background:#F8FBFF;
  box-shadow:0 12px 24px rgba(15,23,42,0.08);
}
.wcdl-match-card-active {
  border-color:var(--wcdl-blue);
  background:#F8FBFF;
  box-shadow:0 0 0 2px rgba(37,99,235,0.12), 0 12px 24px rgba(15,23,42,0.07);
}
.wcdl-match-title {
  color:#07122B;
  font-weight:950;
  font-size:1.06rem;
  line-height:1.18;
}
.wcdl-match-desc {
  color:#475569;
  font-size:.96rem;
  margin-top:4px;
  line-height:1.35;
}
.wcdl-match-type {
  justify-self:end;
  white-space:nowrap;
}

/* Tables */
.wcdl-small-table {
  width:100%; border-collapse: collapse; color:var(--wcdl-ink); font-size:.9rem;
}
.wcdl-small-table th {
  color:var(--wcdl-muted);
  text-transform:uppercase;
  font-size:.68rem;
  letter-spacing:.08em;
  text-align:left;
  padding:8px 7px;
  border-bottom:1px solid var(--wcdl-line);
}
.wcdl-small-table td {
  padding:10px 7px;
  border-bottom:1px solid #EEF2F7;
}

.wcdl-data-note {
  color:#64748B;
  font-size:.86rem;
  line-height:1.45;
  border-top:1px solid var(--wcdl-line);
  padding-top:16px;
  margin-top:20px;
}

@media (max-width: 900px) {
  .wcdl-header { grid-template-columns: 1fr; }
  .wcdl-match-card { grid-template-columns: 1fr; }
  .wcdl-match-type { justify-self:start; }
  .wcdl-header-title { font-size: 2.45rem; }
}
</style>
"""
