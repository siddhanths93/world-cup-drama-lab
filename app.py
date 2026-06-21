
"""
app.py - World Cup Drama Lab

Cleaned Matchday Magazine version.

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
from lib.calculate_standings import calculate_standings
from lib.tournament_pulse import build_tournament_pulse
from lib.ui_helpers import inject_global_css, escape_html, card_html
from views import what_happened_view, why_it_matters_view, what_could_happen_view


st.set_page_config(
    page_title="World Cup Drama Lab",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(inject_global_css(), unsafe_allow_html=True)


def _safe_html(html: str):
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


def _team_code(name):
    clean = "".join([c for c in name if c.isalpha()])
    return clean[:3].upper()


def _render_group_flow_sidebar(data):
    teams = data["team_by_id"]
    groups = data["groups"]
    matches_by_group = data["matches_by_group"]

    st.sidebar.markdown('<div class="wcdl-side-title">Group Flow</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="wcdl-side-note">One home for standings: points, goal difference, and finished scores.</div>',
        unsafe_allow_html=True,
    )

    group_options = [g["id"] for g in groups]
    selected_groups = st.sidebar.multiselect(
        "Groups to show",
        group_options,
        default=group_options[:4],
    )
    show_matches = st.sidebar.checkbox("Show finished match scores", value=True)

    for gid in selected_groups:
        group = data["group_by_id"][gid]
        group_matches = matches_by_group.get(gid, [])
        standings = calculate_standings(group["teamIds"], group_matches)
        completed = [m for m in group_matches if m["status"] == "completed"]

        html = (
            f'<div class="wcdl-side-group">'
            f'<div class="wcdl-side-group-head">'
            f'<h4>Group {gid}</h4>'
            f'<span class="wcdl-side-group-chip">{len(completed)} finished</span>'
            f'</div>'
        )
        html += '<table class="wcdl-side-table"><thead><tr><th>#</th><th>Team</th><th>MP</th><th>GD</th><th>Pts</th></tr></thead><tbody>'

        max_pts = max([r["points"] for r in standings] + [1])
        for row in standings:
            name = teams[row["teamId"]]["name"]
            pct = int((row["points"] / max_pts) * 100) if max_pts else 0
            html += (
                f'<tr>'
                f'<td><span class="wcdl-rank-pill">{row["rank"]}</span></td>'
                f'<td><span class="wcdl-team-code">{_team_code(name)}</span>{escape_html(name)}'
                f'<div class="wcdl-pts-bar"><div class="wcdl-pts-fill" style="width:{pct}%;"></div></div></td>'
                f'<td>{row["played"]}</td>'
                f'<td>{row["goalDifference"]:+d}</td>'
                f'<td><strong>{row["points"]}</strong></td>'
                f'</tr>'
            )
        html += '</tbody></table>'

        if show_matches and completed:
            html += '<div class="wcdl-side-match-title">Finished matches</div>'
            for m in completed:
                home = teams[m["homeTeam"]]["name"]
                away = teams[m["awayTeam"]]["name"]
                html += (
                    f'<div class="wcdl-side-match">'
                    f'<span>{escape_html(home)} vs {escape_html(away)}</span>'
                    f'<span class="wcdl-side-score">{m["homeScore"]}-{m["awayScore"]}</span>'
                    f'</div>'
                )
        html += '</div>'
        st.sidebar.markdown(html, unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.caption("Hourly GitHub Action refreshes local JSON. Streamlit does not call the API directly.")


def render_header(data):
    completed = [m for m in data["matches"] if m["status"] == "completed"]
    goals = sum((m["homeScore"] or 0) + (m["awayScore"] or 0) for m in completed)
    html = (
        '<div class="wcdl-compact-header">'
        '<div>'
        '<div class="wcdl-portfolio-kicker">Sid&apos;s AI Portfolio</div>'
        '<div class="wcdl-compact-title">World Cup Drama Lab</div>'
        '<div class="wcdl-compact-subtitle">Match recaps, beginner-friendly context, and group-stage survival scenarios.</div>'
        '</div>'
        f'<div class="wcdl-compact-meta"><strong>{len(completed)}</strong> matches played · <strong>{goals}</strong> goals · local JSON data</div>'
        '</div>'
    )
    _safe_html(html)


def render_pulse_strip(data):
    pulse = build_tournament_pulse(data)
    completed = [m for m in data["matches"] if m["status"] == "completed"]

    # Keep this as a small app-level snapshot, not a repeated feature surface.
    html = (
        '<div class="wcdl-pulse-strip">'
        f'<div><span>Matches played</span><strong>{len(completed)}</strong></div>'
        f'<div><span>Worth your time</span><strong>{escape_html(pulse["matchToWatchNext"]["title"])}</strong></div>'
        f'<div><span>Data refresh</span><strong>Hourly via GitHub Actions</strong></div>'
        '</div>'
    )
    _safe_html(html)


data = load_all()
_render_group_flow_sidebar(data)

render_header(data)
render_pulse_strip(data)

tab1, tab2, tab3 = st.tabs(["What Happened", "Explain Soccer", "What Could Happen"])

with tab1:
    what_happened_view.render(data)

with tab2:
    why_it_matters_view.render(data)

with tab3:
    what_could_happen_view.render(data)

st.write("")
st.markdown(
    """
    <div class="wcdl-note-compact">
      <strong>Data note</strong>
      Free-data, copyright-safe MVP. No player photos, official crests, FIFA artwork, paid data, betting odds,
      or live event-level analytics. Data is read from local JSON and refreshed by the hourly sync workflow.
    </div>
    """,
    unsafe_allow_html=True,
)
