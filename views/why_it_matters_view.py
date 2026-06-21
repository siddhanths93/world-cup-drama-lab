
"""
Explain Soccer view

Plain-English group/team context with a more editorial layout.
"""
import streamlit as st

from lib.calculate_standings import calculate_standings
from lib.qualification_status import calculate_qualification_status
from lib.explain_soccer import explain_group, explain_team
from lib.group_chaos import calculate_group_chaos, rank_group_chaos
from lib.ui_helpers import (
    card_html,
    stat_card_html,
    progress_html,
    badge_html,
    escape_html,
    QUALIFICATION_COLORS,
    CHAOS_COLORS,
    PULSE_COLORS,
)


def _standings_with_qualification(group_id, data):
    group = data["group_by_id"][group_id]
    matches = data["matches_by_group"].get(group_id, [])
    rows = calculate_standings(group["teamIds"], matches)

    remaining = {tid: 0 for tid in group["teamIds"]}
    for m in matches:
        if m["status"] == "scheduled":
            if m["homeTeam"] in remaining:
                remaining[m["homeTeam"]] += 1
            if m["awayTeam"] in remaining:
                remaining[m["awayTeam"]] += 1

    for row in rows:
        row["qualification"] = calculate_qualification_status(row, rows, remaining[row["teamId"]])
    return rows


def _render_group_table(rows, teams):
    html = '<table class="wcdl-small-table"><thead><tr><th>#</th><th>Team</th><th>P</th><th>GD</th><th>Pts</th><th>Status</th></tr></thead><tbody>'
    for i, row in enumerate(rows, start=1):
        status = row["qualification"]["label"]
        html += (
            f'<tr>'
            f'<td>{i}</td>'
            f'<td>{escape_html(teams[row["teamId"]]["name"])}</td>'
            f'<td>{row["played"]}</td>'
            f'<td>{row["goalDifference"]:+d}</td>'
            f'<td><strong>{row["points"]}</strong></td>'
            f'<td>{badge_html(status, QUALIFICATION_COLORS)}</td>'
            f'</tr>'
        )
    html += "</tbody></table>"
    return html


def _render_survival_card(card):
    body = (
        f'<div style="font-size:1.05rem;color:#F8FAFC;font-weight:800;margin-bottom:10px;">'
        f'{escape_html(card["fanTranslation"])}</div>'
        f'<div><strong>Mood:</strong> {escape_html(card["mood"])}</div>'
        f'<div><strong>Controls fate:</strong> {escape_html(card["controlsFate"])}</div>'
        f'<div><strong>Best path:</strong> {escape_html(card["bestPath"])}</div>'
        f'<div><strong>Danger path:</strong> {escape_html(card["dangerPath"])}</div>'
    )
    st.markdown(
        card_html(
            label="Team survival card",
            title=f"{card['teamName']} — {card['status']}",
            body=body,
            badge=card["status"],
            badge_color_map=QUALIFICATION_COLORS,
            footer=card["note"],
            accent=QUALIFICATION_COLORS.get(card["status"], "#60A5FA"),
            large=True,
        ),
        unsafe_allow_html=True,
    )


def render(data):
    teams = data["team_by_id"]
    groups = data["groups"]

    chaos_rank = rank_group_chaos(data)[:4]
    st.markdown(
        """
        <div class="wcdl-section-title">
          <h3>Group chaos meter</h3>
          <div class="wcdl-section-note">Which groups are still open, messy, or close to settled.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    chaos_cols = st.columns(4)
    for col, chaos in zip(chaos_cols, chaos_rank):
        color = CHAOS_COLORS.get(chaos["label"], "#60A5FA")
        with col:
            st.markdown(
                stat_card_html(
                    f"Group {chaos['group']}",
                    chaos["label"],
                    "; ".join(chaos["reasons"][:2]),
                    accent=color,
                    badge=f"{chaos['score']}/100",
                    badge_color_map={f"{chaos['score']}/100": color},
                ),
                unsafe_allow_html=True,
            )

    st.divider()

    col_target, col_style = st.columns([2, 1])
    with col_target:
        target_kind = st.radio("Choose what to explain", ["Group", "Team"], horizontal=True)
    with col_style:
        style_label = st.selectbox("Explain it for", ["Complete Beginner", "American Sports Fan"])
        style = "sports_fan" if style_label == "American Sports Fan" else "complete_beginner"

    if target_kind == "Group":
        group_id = st.selectbox("Group", [g["id"] for g in groups], format_func=lambda g: f"Group {g}")
        rows = _standings_with_qualification(group_id, data)
        chaos = calculate_group_chaos(group_id, data)
        chaos_color = CHAOS_COLORS.get(chaos["label"], "#60A5FA")

        explanation = explain_group(group_id, rows, teams, style=style)

        st.markdown(
            card_html(
                label="Plain English version",
                title=f"Group {group_id}: {chaos['label']}",
                body=(
                    f'<div>{escape_html(explanation["translation"])}</div>'
                    f'{progress_html(chaos["score"], chaos_color)}'
                    f'<div style="color:#64748B;">{"; ".join(escape_html(r) for r in chaos["reasons"])}</div>'
                    f'<div style="margin-top:10px;color:#64748B;font-size:.9rem;">Use the sidebar for the full standings table.</div>'
                ),
                badge="Group Chaos",
                badge_color_map=PULSE_COLORS,
                accent=chaos_color,
                large=True,
            ),
            unsafe_allow_html=True,
        )

    else:
        team_id = st.selectbox(
            "Team",
            [t["id"] for t in data["teams"]],
            format_func=lambda tid: teams[tid]["name"],
        )
        team = teams[team_id]
        rows = _standings_with_qualification(team["group"], data)
        row = next(r for r in rows if r["teamId"] == team_id)

        explanation = explain_team(team_id, row, teams, style=style)
        st.markdown(
            card_html(
                label="Team context",
                title=f"{team['name']} in plain English",
                body=(
                    f"{escape_html(explanation['translation'])} "
                    "For the full survival card and scenario testing, use the What Could Happen tab."
                ),
                accent="#1D4ED8",
                large=True,
            ),
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            card_html(
                label="Why this matters",
                title="The plain-English version",
                body=escape_html(explanation["whyThisMatters"]),
                accent="#F59E0B",
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            card_html(
                label="What to watch next",
                title="The thing that changes the story",
                body=escape_html(explanation["whatToWatchFor"]),
                accent="#60A5FA",
            ),
            unsafe_allow_html=True,
        )

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(
            card_html(
                label="What they want",
                title="The group-stage objective",
                body=escape_html(explanation["whatEachTeamWants"]),
                accent="#22C55E",
            ),
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            card_html(
                label="Tell your friend",
                title="One sentence version",
                body=f'<div style="font-size:1.1rem;color:#F8FAFC;font-weight:800;">{escape_html(explanation["tellYourFriend"])}</div>',
                accent="#A78BFA",
            ),
            unsafe_allow_html=True,
        )
