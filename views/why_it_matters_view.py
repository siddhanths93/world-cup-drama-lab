
"""
Why It Matters view

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
        f'<div style="font-size:1.05rem;color:#07122B;font-weight:850;margin-bottom:10px;">'
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
    from lib.state_helpers import ensure_selection_state
    ensure_selection_state(data)
    teams = data["team_by_id"]
    groups = data["groups"]

    st.markdown(
        """
        <div class="wcdl-section-title">
          <h3>Why this group matters</h3>
          <div class="wcdl-section-note">This view inherits the match/team/group selected in Match Desk.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_group_for_view = st.session_state.get("selected_group", groups[0]["id"])
    if st.session_state.get("_why_synced_group") != selected_group_for_view:
        st.session_state["why_group_context"] = selected_group_for_view
        st.session_state["_why_synced_group"] = selected_group_for_view

    c1, c2 = st.columns([1, 1])
    with c1:
        group_id = st.selectbox(
            "Group context",
            [g["id"] for g in groups],
            index=[g["id"] for g in groups].index(st.session_state.get("selected_group", groups[0]["id"])),
            format_func=lambda g: f"Group {g}",
            key="why_group_context",
        )
        if group_id != st.session_state.get("selected_group"):
            st.session_state["selected_group"] = group_id
            group_team_ids = data["group_by_id"][group_id]["teamIds"]
            if st.session_state.get("selected_team") not in group_team_ids:
                st.session_state["selected_team"] = group_team_ids[0]
    with c2:
        style_label = st.selectbox("Explain it for", ["Complete Beginner", "American Sports Fan"])
        style = "sports_fan" if style_label == "American Sports Fan" else "complete_beginner"

    target_kind = "Group"
    if target_kind == "Group":
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
                    f'<div style="margin-top:10px;color:#64748B;font-size:.9rem;">The selected group table appears below.</div>'
                ),
                badge="Group Chaos",
                badge_color_map=PULSE_COLORS,
                accent=chaos_color,
                large=True,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            card_html(
                label="Selected group table",
                title=f"Group {group_id}",
                body=_render_group_table(rows, teams),
                accent="#0F172A",
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
                title=explanation["tellYourFriend"],
                body="Use this as the quick one-sentence explanation for someone casually watching the group.",
                accent="#2563EB",
            ),
            unsafe_allow_html=True,
        )
