
"""
ui_helpers.py

Shared UI helpers for World Cup Drama Lab.

Light "Matchday Magazine" visual system.
No external images, official logos, team crests, or copyrighted visual assets.
All decoration is CSS: typography, layout, abstract curves, lines, dots.
"""

DRAMA_COLORS = {
    "Low Drama": "#475569",
    "Decent Watch": "#2563EB",
    "Proper World Cup Tension": "#B45309",
    "Chaos Match": "#BE123C",
    "Football Heritage Moment": "#7C3AED",
}

ENTERTAINMENT_COLORS = {
    "Low Event": "#475569",
    "Respectable Watch": "#2563EB",
    "Goal Fest": "#B45309",
    "Pure Entertainment": "#15803D",
}

VERDICT_COLORS = {
    "Expected Result": "#15803D",
    "Nervier Than It Looks": "#B45309",
    "Upset Signal": "#7C3AED",
    "Scoreline Shock": "#BE123C",
    "Hard to Judge": "#475569",
}

QUALIFICATION_COLORS = {
    "Safe": "#15803D",
    "In Control": "#0F766E",
    "Danger Zone": "#B45309",
    "Calculator Mode": "#2563EB",
    "Needs a Miracle": "#C2410C",
    "Eliminated": "#64748B",
}

MATCH_TYPE_COLORS = {
    "Business Trip": "#2563EB",
    "Nervy Grind": "#B45309",
    "Chaos Ball": "#BE123C",
    "Upset Energy": "#7C3AED",
    "Giant Sweating": "#C2410C",
    "Group Stage Tax": "#475569",
    "Heartbreak Mode": "#991B1B",
    "Calculator Mode Activated": "#2563EB",
}

PULSE_COLORS = {
    "Group Chaos": "#BE123C",
    "Pressure": "#B45309",
    "Entertainment": "#7C3AED",
    "Next Match": "#2563EB",
    "Survival": "#0F766E",
    "Scenario": "#475569",
}

REALISM_COLORS = {
    "Realistic": "#15803D",
    "Aggressive": "#B45309",
    "Chaos Prediction": "#BE123C",
    "Extremely Spicy": "#7C3AED",
}

CHAOS_COLORS = {
    "Settled": "#15803D",
    "Still Open": "#2563EB",
    "Calculator Mode Brewing": "#B45309",
    "Pure Chaos": "#BE123C",
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


def progress_html(score, color="#BE123C"):
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
    footer_html = f'<div class="wcdl-card-footer">{footer}</div>' if footer else ""
    accent_style = f'--card-accent:{accent};' if accent else ""
    size_class = " wcdl-card-large" if large else ""
    variant_class = f" wcdl-card-{variant}"
    return (
        f'<div class="wcdl-card{size_class}{variant_class}" style="{accent_style}">'
        f'{label_html}{title_html}{meta_html}{badge_html_block}{body_html}{footer_html}'
        f'</div>'
    )


def stat_card_html(label, value, subtitle="", accent="#BE123C", badge=None, badge_color_map=None):
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
  --wcdl-paper: #F7F1E6;
  --wcdl-paper-2: #FFFDF7;
  --wcdl-ink: #0F172A;
  --wcdl-muted: #64748B;
  --wcdl-line: rgba(15, 23, 42, 0.16);
  --wcdl-red: #BE123C;
  --wcdl-blue: #1D4ED8;
  --wcdl-gold: #D6A84F;
}

.stApp {
  background:
    radial-gradient(circle at 82% 12%, rgba(190,18,60,0.12), transparent 26%),
    radial-gradient(circle at 10% 4%, rgba(214,168,79,0.14), transparent 22%),
    linear-gradient(135deg, #F7F1E6 0%, #FFFDF7 46%, #F4EBD9 100%);
  color: var(--wcdl-ink);
}

.block-container {
  padding-top: 1.2rem !important;
  padding-bottom: 3rem !important;
  max-width: 1320px !important;
}

h1, h2, h3, h4, h5 {
  color: var(--wcdl-ink) !important;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
  letter-spacing: -0.04em;
}

p, li, div, span, label {
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

[data-testid="stCaptionContainer"], .stCaption, small {
  color: var(--wcdl-muted) !important;
}

hr {
  border-color: rgba(15,23,42,0.16) !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Sidebar */
[data-testid="stSidebar"] {
  background: #FFFFFF !important;
  border-right: 1px solid rgba(15,23,42,0.12);
}
[data-testid="stSidebar"] * {
  color: #0F172A;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
  color: #64748B !important;
}

/* Inputs */
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input,
.stTextInput input {
  background: #FFFFFF !important;
  border: 1px solid rgba(15,23,42,0.18) !important;
  color: #0F172A !important;
  border-radius: 10px !important;
}
.stNumberInput label, .stSelectbox label, .stRadio label {
  color: #334155 !important;
  font-weight: 650 !important;
}
.stButton > button {
  background: #0F172A !important;
  border: 1px solid #0F172A !important;
  color: #FFFFFF !important;
  border-radius: 10px !important;
  padding: 0.55rem 0.9rem !important;
  transition: all .15s ease;
}
.stButton > button:hover {
  background: #BE123C !important;
  border-color: #BE123C !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 0;
  border-bottom: 1px solid rgba(15,23,42,0.16);
  margin: 8px 0 22px 0;
}
.stTabs [data-baseweb="tab"] {
  color: #0F172A;
  padding: 16px 28px;
  border-radius: 0;
  border-bottom: 4px solid transparent;
  background: transparent;
  font-weight: 900;
  font-size: 1.02rem;
  text-transform: uppercase;
  letter-spacing: .02em;
}
.stTabs [aria-selected="true"] {
  color: #BE123C !important;
  border-bottom: 4px solid #BE123C !important;
  background: rgba(190,18,60,0.04) !important;
}

/* Hero */
.wcdl-hero {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(15,23,42,0.12);
  background:
    radial-gradient(circle at 72% 18%, rgba(214,168,79,0.18), transparent 28%),
    linear-gradient(135deg, rgba(255,253,247,0.98), rgba(247,241,230,0.94));
  border-radius: 0;
  padding: 38px 42px 36px 42px;
  margin: 0 0 24px 0;
  box-shadow: 0 16px 45px rgba(15,23,42,0.08);
  min-height: 300px;
}
.wcdl-hero::before {
  content:"";
  position:absolute;
  right:-110px;
  top:-70px;
  width:560px;
  height:560px;
  border:42px solid rgba(214,168,79,0.20);
  border-radius:50%;
}
.wcdl-hero::after {
  content:"";
  position:absolute;
  right:-80px;
  bottom:-115px;
  width:430px;
  height:430px;
  background:
    linear-gradient(135deg, rgba(190,18,60,0.92) 0%, rgba(190,18,60,0.92) 45%, rgba(15,23,42,0.95) 46%, rgba(15,23,42,0.95) 100%);
  transform: rotate(-12deg);
  border-radius: 22px;
  opacity: .95;
}
.wcdl-hero-content {
  position:relative;
  z-index:2;
  max-width: 650px;
}
.wcdl-portfolio-kicker {
  text-transform: uppercase;
  letter-spacing: .16em;
  color: #64748B;
  font-size: .76rem;
  font-weight: 950;
  margin-bottom: 10px;
}
.wcdl-brand {
  font-size: clamp(1.8rem, 3.4vw, 3.1rem);
  line-height: .92;
  font-weight: 1000;
  letter-spacing: -.055em;
  color:#0F172A;
  text-transform: uppercase;
}
.wcdl-brand span {
  color:#BE123C;
  display:block;
}
.wcdl-tagline {
  margin-top: 12px;
  color:#334155;
  font-weight:600;
  max-width:360px;
}
.wcdl-kicker {
  margin-top: 34px;
  text-transform: uppercase;
  letter-spacing: .1em;
  font-size: .75rem;
  font-weight: 900;
  color: #BE123C;
}
.wcdl-title {
  margin-top: 8px;
  border-left: 4px solid #BE123C;
  padding-left: 18px;
  font-size: clamp(2rem, 4vw, 3.8rem);
  font-weight: 950;
  line-height: .98;
  color: #0F172A;
  max-width: 640px;
}
.wcdl-subtitle {
  color:#334155;
  font-size: 1.02rem;
  line-height: 1.65;
  max-width: 510px;
  margin-top: 14px;
}

/* Section headers */
.wcdl-section-title {
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:16px;
  margin: 30px 0 12px 0;
  border-bottom: 1px solid rgba(15,23,42,0.15);
  padding-bottom: 6px;
}
.wcdl-section-title h3 {
  margin:0 !important;
  font-size:1.18rem !important;
  text-transform: uppercase;
  letter-spacing: -.02em;
}
.wcdl-section-note {
  color:#64748B;
  font-size:.88rem;
}

/* Cards */
.wcdl-card, .wcdl-stat-card {
  position: relative;
  background: rgba(255,255,255,0.70);
  border: 1px solid rgba(15,23,42,0.14);
  border-radius: 12px;
  padding: 18px 18px;
  margin-bottom: 16px;
  box-shadow: 0 12px 26px rgba(15,23,42,0.07);
  overflow: hidden;
}
.wcdl-card::after, .wcdl-stat-card::after {
  content:"";
  position:absolute;
  right:-55px; bottom:-75px;
  width:180px; height:180px;
  border: 28px solid color-mix(in srgb, var(--card-accent, #BE123C) 12%, transparent);
  border-radius:50%;
}
.wcdl-card-large {
  min-height: 170px;
  padding: 24px;
}
.wcdl-card-default {}
.wcdl-card-dark {
  background: #0F172A;
  color:#F8FAFC;
}
.wcdl-card-dark .wcdl-card-title,
.wcdl-card-dark .wcdl-stat-value {
  color:#F8FAFC;
}
.wcdl-card-dark .wcdl-card-body,
.wcdl-card-dark .wcdl-stat-subtitle {
  color:#CBD5E1;
}
.wcdl-card-label {
  text-transform: uppercase;
  letter-spacing:.09em;
  color:#334155;
  font-size:.72rem;
  font-weight:900;
  margin-bottom:8px;
}
.wcdl-card-title {
  color:#0F172A;
  font-weight:900;
  line-height:1.12;
  font-size:1.2rem;
  margin-bottom:8px;
}
.wcdl-card-meta {
  color:#64748B;
  font-size:.86rem;
  margin-bottom:10px;
}
.wcdl-card-body {
  color:#334155;
  line-height:1.55;
  font-size:.95rem;
}
.wcdl-card-footer {
  color:#64748B;
  border-top:1px solid rgba(15,23,42,0.12);
  margin-top:14px;
  padding-top:12px;
  font-size:.86rem;
}
.wcdl-stat-value {
  color:#0F172A;
  font-weight:950;
  font-size:1.65rem;
  line-height:1.1;
}
.wcdl-stat-subtitle {
  color:#64748B;
  font-size:.86rem;
  line-height:1.45;
  margin-top:7px;
}
.wcdl-badge {
  display:inline-flex;
  align-items:center;
  color: var(--badge-color);
  background: color-mix(in srgb, var(--badge-color) 11%, #FFFFFF);
  border: 1px solid color-mix(in srgb, var(--badge-color) 40%, #FFFFFF);
  border-radius: 7px;
  padding: 4px 9px;
  font-size: .77rem;
  font-weight: 850;
  white-space: nowrap;
}
.wcdl-card-badge-row {
  margin: 8px 0 10px 0;
}
.wcdl-progress {
  width:100%;
  height:8px;
  background: rgba(15,23,42,0.10);
  border-radius:999px;
  overflow:hidden;
  margin: 10px 0 8px 0;
}
.wcdl-progress-fill {
  height:100%;
  border-radius:999px;
}

/* Story list */
.wcdl-story-list {
  display:grid;
  grid-template-columns: repeat(3, 1fr);
  gap:0;
}
.wcdl-story-row {
  display:grid;
  grid-template-columns: 48px 1fr;
  gap:12px;
  padding: 16px 18px;
  border-right:1px solid rgba(15,23,42,0.16);
}
.wcdl-story-row:last-child { border-right:none; }
.wcdl-story-number {
  font-size:2rem;
  font-weight:1000;
  color:#BE123C;
  line-height:1;
}
.wcdl-story-headline {
  color:#0F172A;
  font-weight:900;
  line-height:1.22;
}
.wcdl-story-sub {
  color:#475569;
  font-size:.9rem;
  margin-top:8px;
  line-height:1.45;
}
.wcdl-story-tag {
  margin-top:12px;
}


/* Clickable recap cards */
.wcdl-recap-card-link {
  display: block;
  text-decoration: none !important;
  color: inherit !important;
}
.wcdl-recap-card {
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(15,23,42,0.14);
  border-radius: 10px;
  padding: 14px 16px 14px 16px;
  min-height: 125px;
  margin-bottom: 18px;
  box-shadow: 0 8px 18px rgba(15,23,42,0.06);
  transition: transform .14s ease, border-color .14s ease, box-shadow .14s ease, background .14s ease;
  cursor: pointer;
}
.wcdl-recap-card:hover {
  transform: translateY(-2px);
  border-color: #BE123C;
  box-shadow: 0 14px 28px rgba(15,23,42,0.10);
  background: #FFF7ED;
}
.wcdl-recap-card-selected {
  border-color: #BE123C;
  background: #FFF7ED;
}
.wcdl-recap-card-meta {
  font-size: .72rem;
  text-transform: uppercase;
  color: #64748B;
  font-weight: 900;
  letter-spacing: .03em;
}
.wcdl-recap-card-title {
  font-weight: 950;
  color: #0F172A;
  line-height: 1.2;
  margin-top: 9px;
  font-size: 1.05rem;
}
.wcdl-recap-card-hint {
  color: #64748B;
  margin-top: 9px;
  font-size: .78rem;
  font-weight: 750;
}

/* Tables */
.wcdl-small-table {
  width:100%;
  border-collapse: collapse;
  color:#0F172A;
  font-size:.9rem;
}
.wcdl-small-table th {
  color:#64748B;
  text-transform:uppercase;
  font-size:.68rem;
  letter-spacing:.08em;
  text-align:left;
  padding:7px 6px;
  border-bottom:1px solid rgba(15,23,42,0.16);
}
.wcdl-small-table td {
  padding:8px 6px;
  border-bottom:1px solid rgba(15,23,42,0.10);
}

/* Sidebar group flow */
.wcdl-side-title {
  font-size:1.05rem;
  font-weight:1000;
  color:#0F172A;
  margin: 8px 0 4px 0;
  text-transform: uppercase;
  letter-spacing: -.02em;
}
.wcdl-side-note {
  font-size:.82rem;
  color:#64748B;
  line-height:1.35;
  margin-bottom: 12px;
}
.wcdl-side-group {
  background: linear-gradient(135deg, rgba(255,255,255,.96), rgba(247,241,230,.78));
  border:1px solid rgba(15,23,42,0.12);
  border-left:4px solid #BE123C;
  border-radius:12px;
  padding:12px 12px 10px 12px;
  margin: 12px 0 16px 0;
  box-shadow:0 8px 18px rgba(15,23,42,.06);
}
.wcdl-side-group-head {
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:8px;
}
.wcdl-side-group h4 {
  margin: 0 !important;
  font-size:1rem !important;
  letter-spacing:-.02em !important;
  color:#0F172A !important;
}
.wcdl-side-group-chip {
  background:#0F172A;
  color:#FFFFFF;
  border-radius:999px;
  padding:3px 8px;
  font-size:.68rem;
  font-weight:900;
}
.wcdl-side-table {
  width:100%;
  border-collapse:separate;
  border-spacing:0 4px;
  font-size:.78rem;
}
.wcdl-side-table th {
  color:#64748B;
  font-size:.62rem;
  text-transform:uppercase;
  padding:3px 2px;
  font-weight:900;
}
.wcdl-side-table td {
  padding:5px 3px;
  color:#0F172A;
  background: rgba(255,255,255,.64);
}
.wcdl-side-table tr td:first-child {
  border-radius:8px 0 0 8px;
}
.wcdl-side-table tr td:last-child {
  border-radius:0 8px 8px 0;
}
.wcdl-rank-pill {
  display:inline-flex;
  width:20px;
  height:20px;
  align-items:center;
  justify-content:center;
  background:#BE123C;
  color:#FFFFFF;
  border-radius:999px;
  font-size:.66rem;
  font-weight:950;
}
.wcdl-team-code {
  display:inline-flex;
  width:28px;
  height:20px;
  align-items:center;
  justify-content:center;
  background:#F1F5F9;
  border:1px solid rgba(15,23,42,0.12);
  border-radius:5px;
  font-size:.63rem;
  font-weight:950;
  margin-right:5px;
  color:#334155;
}
.wcdl-pts-bar {
  height:4px;
  width:100%;
  background:rgba(15,23,42,.08);
  border-radius:999px;
  margin-top:3px;
  overflow:hidden;
}
.wcdl-pts-fill {
  height:100%;
  background:#BE123C;
  border-radius:999px;
}
.wcdl-side-match-title {
  margin-top:10px;
  font-size:.68rem;
  font-weight:950;
  color:#64748B;
  text-transform:uppercase;
  letter-spacing:.08em;
}
.wcdl-side-match {
  font-size:.75rem;
  color:#334155;
  padding:6px 7px;
  margin-top:5px;
  border:1px solid rgba(15,23,42,.09);
  background:rgba(255,255,255,.66);
  border-radius:8px;
  display:flex;
  justify-content:space-between;
  gap:8px;
}
.wcdl-side-score {
  font-weight:950;
  color:#BE123C;
  white-space:nowrap;
}

.wcdl-source-note {
  border: 1px solid rgba(15,23,42,0.12);
  background: rgba(255,255,255,0.70);
  border-radius: 12px;
  padding: 14px 16px;
  color: #475569;
  font-size: .9rem;
  line-height: 1.55;
}


/* Compact method/source notes */
.wcdl-note-compact {
  background: rgba(255,255,255,0.58);
  border: 1px solid rgba(15,23,42,0.10);
  border-left: 4px solid rgba(15,23,42,0.28);
  border-radius: 10px;
  padding: 10px 13px;
  margin: 10px 0 14px 0;
  color: #64748B;
  font-size: .82rem;
  line-height: 1.42;
  box-shadow: none;
}
.wcdl-note-compact strong {
  color: #334155;
  font-size: .72rem;
  text-transform: uppercase;
  letter-spacing: .09em;
  margin-right: 6px;
}


/* Cleanup release: compact top system */
.wcdl-compact-header {
  display:flex;
  justify-content:space-between;
  align-items:flex-end;
  gap:18px;
  padding: 18px 0 14px 0;
  border-bottom: 1px solid rgba(15,23,42,0.14);
  margin-bottom: 10px;
}
.wcdl-compact-title {
  color:#0F172A;
  font-size: clamp(1.65rem, 3vw, 2.45rem);
  font-weight: 1000;
  letter-spacing: -.055em;
  text-transform: uppercase;
  line-height: .95;
}
.wcdl-compact-subtitle {
  margin-top: 7px;
  color:#475569;
  font-size:.96rem;
  line-height:1.45;
}
.wcdl-compact-meta {
  color:#64748B;
  font-size:.86rem;
  white-space:nowrap;
  padding-bottom:3px;
}
.wcdl-compact-meta strong {
  color:#BE123C;
}
.wcdl-pulse-strip {
  display:grid;
  grid-template-columns: .8fr 1.5fr 1fr;
  gap: 10px;
  margin: 12px 0 16px 0;
}
.wcdl-pulse-strip > div {
  background:rgba(255,255,255,.70);
  border:1px solid rgba(15,23,42,.11);
  border-radius:10px;
  padding:10px 12px;
  box-shadow:0 8px 18px rgba(15,23,42,.04);
}
.wcdl-pulse-strip span {
  display:block;
  color:#64748B;
  text-transform:uppercase;
  letter-spacing:.08em;
  font-size:.68rem;
  font-weight:950;
  margin-bottom:4px;
}
.wcdl-pulse-strip strong {
  color:#0F172A;
  font-size:.95rem;
}

@media (max-width: 900px) {
  .wcdl-story-list { grid-template-columns: 1fr; }
  .wcdl-story-row { border-right:none; border-bottom:1px solid rgba(15,23,42,0.12); }
  .wcdl-hero { padding: 28px 24px; min-height: 420px; }
  .wcdl-hero::after { opacity:.35; }
}
</style>
"""
