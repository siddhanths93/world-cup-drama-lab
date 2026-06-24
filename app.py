"""
app.py - World Cup Drama Lab

Phase 1 clean editorial version.

Design rules:
- no official FIFA logos or team crests
- no player photos
- no external images
- no paid APIs
- no betting odds
- no xG/event-level claims
"""
import streamlit as st

from lib.data_loader import load_all
from lib.ui_helpers import inject_global_css, escape_html
from lib.state_helpers import ensure_selection_state, selected_match, set_selected_match
from views import what_happened_view, why_it_matters_view, what_could_happen_view


st.set_page_config(
    page_title="World Cup Drama Lab",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(inject_global_css(), unsafe_allow_html=True)


def _safe_html(html: str):
    # Use markdown rather than st.html to avoid stray component labels/rendering artifacts.
    st.markdown(html, unsafe_allow_html=True)


def _sync_query_params(data):
    """Allow match cards to be real clickable links without Streamlit button styling."""
    try:
        params = st.query_params
        match_id = params.get("match_id")
        if isinstance(match_id, list):
            match_id = match_id[0] if match_id else None
        if match_id:
            valid = any(m["id"] == match_id for m in data.get("matches", []))
            if valid and st.session_state.get("selected_match_id") != match_id:
                set_selected_match(data, match_id)
            try:
                st.query_params.clear()
            except Exception:
                pass
    except Exception:
        return


def _headline_for_match(data):
    teams = data["team_by_id"]
    match = selected_match(data)
    if not match:
        return "Every result changes the group-stage story.", "Select a team or group. Every section follows the same story."

    home = teams[match["homeTeam"]]["name"]
    away = teams[match["awayTeam"]]["name"]
    if match["status"] == "completed":
        hs, as_ = match["homeScore"], match["awayScore"]
        if hs == as_:
            title = f"{home} and {away} left Group {match['group']} unresolved."
        else:
            winner = home if hs > as_ else away
            loser = away if hs > as_ else home
            margin = abs(hs - as_)
            if margin >= 3:
                title = f"{winner} made a statement. {loser} is under pressure."
            elif margin == 1:
                title = f"{winner} survived a narrow one. Group {match['group']} stays tense."
            else:
                title = f"{winner} took control of the Group {match['group']} story."
        return title, "Select a team or group. Every section follows the same story."

    return f"{home} vs {away} is next on the Group {match['group']} board.", "Select a team or group. Every section follows the same story."


def render_header(data):
    title, subtitle = _headline_for_match(data)
    completed = [m for m in data["matches"] if m["status"] == "completed"]
    live = [m for m in data["matches"] if m["status"] == "live"]
    scheduled = [m for m in data["matches"] if m["status"] == "scheduled"]
    goals = sum((m.get("homeScore") or 0) + (m.get("awayScore") or 0) for m in completed)
    html = (
        '<div class="wcdl-header">'
        '<div>'
        "<div class=\"wcdl-header-kicker\">Sid's Portfolio - World Cup Drama Lab</div>"
        f'<div class="wcdl-header-title">{escape_html(title)}</div>'
        f'<div class="wcdl-header-subtitle">{escape_html(subtitle)}</div>'
        '</div>'
        '<div class="wcdl-snapshot">'
        '<div class="wcdl-snapshot-title">Tournament snapshot</div>'
        f'<div class="wcdl-snapshot-row"><span>Completed</span><strong>{len(completed)}</strong></div>'
        f'<div class="wcdl-snapshot-row"><span>Live</span><strong>{len(live)}</strong></div>'
        f'<div class="wcdl-snapshot-row"><span>Goals</span><strong>{goals}</strong></div>'
        f'<div class="wcdl-snapshot-row"><span>Upcoming</span><strong>{len(scheduled)}</strong></div>'
        '<div class="wcdl-snapshot-row"><span>Source</span><strong>Local JSON</strong></div>'
        '</div>'
        '</div>'
    )
    _safe_html(html)


def _nav_button(label, view_key, key):
    active = st.session_state.get("active_view", "match") == view_key
    button_label = f"{'✓ ' if active else ''}{label}"
    if st.button(button_label, key=key, use_container_width=True):
        st.session_state["active_view"] = view_key
        st.rerun()


def render_navigation():
    st.session_state.setdefault("active_view", "match")
    c1, c2, c3, spacer = st.columns([1, 1.15, 1, 5])
    with c1:
        _nav_button("Match Desk", "match", "nav_match")
    with c2:
        _nav_button("Why It Matters", "why", "nav_why")
    with c3:
        _nav_button("Scenario Lab", "scenario", "nav_scenario")
    st.markdown('<div class="wcdl-nav-spacer"></div>', unsafe_allow_html=True)


data = load_all()
ensure_selection_state(data)
_sync_query_params(data)

render_header(data)
render_navigation()

active_view = st.session_state.get("active_view", "match")
if active_view == "why":
    why_it_matters_view.render(data)
elif active_view == "scenario":
    what_could_happen_view.render(data)
else:
    what_happened_view.render(data)

st.write("")
st.markdown(
    """
    <div class="wcdl-data-note">
      Free-data, copyright-safe MVP. No player photos, official crests, FIFA artwork, paid data, betting odds,
      or live event-level analytics. Data is read from local JSON and refreshed by the hourly sync workflow.
    </div>
    """,
    unsafe_allow_html=True,
)
