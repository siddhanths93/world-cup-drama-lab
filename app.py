
"""
app.py - World Cup Drama Lab

Matchday Magazine version.

Copyright-safe/free-data constraints:
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
from lib.ui_helpers import inject_global_css, escape_html, card_html


st.set_page_config(
    page_title="World Cup Drama Lab",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(inject_global_css(), unsafe_allow_html=True)


def _safe_html(html: str):
    """Use Streamlit's HTML renderer when available to avoid markdown showing raw HTML."""
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
        '<div class="wcdl-side-note">Live-feeling tournament context from local JSON: standings, points, goal difference, and finished scores.</div>',
        unsafe_allow_html=True,
    )

    group_options = [g["id"] for g in groups]
    default_groups = group_options[:4]
    selected_groups = st.sidebar.multiselect(
        "Groups to show",
        group_options,
        default=default_groups,
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
    st.sidebar.caption("Use the sync script to refresh completed scores from a free API. The app itself reads local JSON only.")


def render_hero():
    # Keep this compact and unindented so Streamlit never renders it as code.
    html = (
        '<section class="wcdl-hero">'
        '<div class="wcdl-hero-content">'
        '<div class="wcdl-portfolio-kicker">Sid\'s AI Portfolio</div>'
        '<div class="wcdl-brand">World Cup<span>Drama Lab</span></div>'
        '<div class="wcdl-tagline">The simple way to follow the tournament.</div>'
        '<div class="wcdl-kicker">Today\'s tournament mood</div>'
        '<div class="wcdl-title">The drama is building.</div>'
        '<div class="wcdl-subtitle">'
        'Follow what happened, understand why it matters, and simulate what could happen next. '
        'Built with local public-style match data, generated stories, and no copyrighted visuals.'
        '</div>'
        '</div>'
        '</section>'
    )
    _safe_html(html)


from views import what_happened_view, why_it_matters_view, what_could_happen_view

data = load_all()
_render_group_flow_sidebar(data)

render_hero()

tab1, tab2, tab3 = st.tabs(["What Happened", "Explain Soccer", "What Could Happen"])

with tab1:
    what_happened_view.render(data)

with tab2:
    why_it_matters_view.render(data)

with tab3:
    what_could_happen_view.render(data)

st.write("")
st.markdown(
    card_html(
        label="Data and method notes",
        title="Free-data, copyright-safe MVP",
        body=(
            "No player photos, official team crests, official FIFA artwork, or external visual assets are used. "
            "The app reads from local JSON and can be refreshed with the included sync script. "
            "This is not a betting model, official FIFA analysis, or live event-level analytics."
        ),
        accent="#0F172A",
    ),
    unsafe_allow_html=True,
)

st.caption("Local-data MVP. No official branding, photos, paid data, betting odds, or event-level analytics claims.")
