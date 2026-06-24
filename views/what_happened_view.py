"""
Match Desk view

Phase 1 clean editorial flow:
- user can search/select a team or select a group
- selected group shows composition chips only as information
- board shows only that group's games
- latest results first, upcoming games second
- clicking a match drives recap/context/scenario state through query params
"""
import streamlit as st

from lib.calculate_standings import calculate_standings
from lib.match_story import generate_match_story
from lib.state_helpers import (
    ensure_selection_state,
    latest_match_for_group,
    set_selected_group,
    set_selected_team,
    set_selected_match,
    selected_match,
)
from lib.ui_helpers import (
    card_html,
    badge_html,
    escape_html,
    MATCH_TYPE_COLORS,
    QUALIFICATION_COLORS,
)
from lib.qualification_status import calculate_qualification_status


def _format_match_line(match, teams):
    home = teams[match["homeTeam"]]["name"]
    away = teams[match["awayTeam"]]["name"]
    if match["status"] == "completed":
        return f"{home} {match['homeScore']}–{match['awayScore']} {away}"
    if match["status"] == "live":
        return f"{home} {match.get('homeScore') or 0}–{match.get('awayScore') or 0} {away}"
    return f"{home} vs {away}"


def _match_sort_key(match):
    return (match.get("date", ""), match.get("id", ""))


def _group_match_sections(group_matches):
    live = sorted([m for m in group_matches if m["status"] == "live"], key=_match_sort_key, reverse=True)
    completed = sorted([m for m in group_matches if m["status"] == "completed"], key=_match_sort_key, reverse=True)
    scheduled = sorted([m for m in group_matches if m["status"] == "scheduled"], key=_match_sort_key)
    return live, completed, scheduled


def _standings_with_status(data, group_id):
    teams = data["team_by_id"]
    group = data["group_by_id"][group_id]
    group_matches = data["matches_by_group"].get(group_id, [])
    rows = calculate_standings(group["teamIds"], group_matches)

    remaining = {tid: 0 for tid in group["teamIds"]}
    for m in group_matches:
        if m["status"] == "scheduled":
            remaining[m["homeTeam"]] += 1
            remaining[m["awayTeam"]] += 1

    html = '<table class="wcdl-small-table"><thead><tr><th>#</th><th>Team</th><th>P</th><th>GD</th><th>Pts</th><th>Status</th></tr></thead><tbody>'
    for row in rows:
        q = calculate_qualification_status(row, rows, remaining[row["teamId"]])
        html += (
            f'<tr>'
            f'<td>{row["rank"]}</td>'
            f'<td>{escape_html(teams[row["teamId"]]["name"])}</td>'
            f'<td>{row["played"]}</td>'
            f'<td>{row["goalDifference"]:+d}</td>'
            f'<td><strong>{row["points"]}</strong></td>'
            f'<td>{badge_html(q["label"], QUALIFICATION_COLORS)}</td>'
            f'</tr>'
        )
    html += '</tbody></table>'
    return html


def _group_chips_html(data, group_id):
    teams = data["team_by_id"]
    group_team_ids = data["group_by_id"][group_id]["teamIds"]
    chips = [f'<span class="wcdl-team-chip">{escape_html(teams[tid]["name"])}</span>' for tid in group_team_ids]
    return ''.join(chips)


def _sync_team_selector(data):
    set_selected_team(data, st.session_state["wcdl_team_selector"])


def _sync_group_selector(data):
    set_selected_group(data, st.session_state["wcdl_group_selector"])


def _render_team_group_controls(data):
    ensure_selection_state(data)
    teams = data["team_by_id"]
    groups = data["groups"]
    group_ids = [g["id"] for g in groups]
    all_team_ids = [t["id"] for t in sorted(data["teams"], key=lambda x: x["name"])]

    selected_group = st.session_state["selected_group"]
    selected_team = st.session_state["selected_team"]

    st.session_state.setdefault("wcdl_team_selector", selected_team)
    st.session_state.setdefault("wcdl_group_selector", selected_group)
    if st.session_state["wcdl_team_selector"] != selected_team:
        st.session_state["wcdl_team_selector"] = selected_team
    if st.session_state["wcdl_group_selector"] != selected_group:
        st.session_state["wcdl_group_selector"] = selected_group

    st.markdown(
        """
        <div class="wcdl-finder-header">
          <h3>Find your team or group</h3>
          <p>Search by team if you do not know the group. The board will auto-focus on that group.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_team, c_group = st.columns([1.4, 0.8])
    with c_team:
        st.selectbox(
            "Team search",
            all_team_ids,
            format_func=lambda tid: teams[tid]["name"],
            key="wcdl_team_selector",
            on_change=_sync_team_selector,
            args=(data,),
        )
    with c_group:
        st.selectbox(
            "Group filter",
            group_ids,
            format_func=lambda gid: f"Group {gid}",
            key="wcdl_group_selector",
            on_change=_sync_group_selector,
            args=(data,),
        )


def _render_group_header(data, group_id):
    chips = _group_chips_html(data, group_id)
    st.markdown(
        f"""
        <div class="wcdl-group-context-panel">
          <div class="wcdl-card-label">Group {escape_html(group_id)} composition</div>
          <div class="wcdl-team-chip-row">{chips}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _scheduled_match_type(match, selected_team):
    if selected_team in (match.get("homeTeam"), match.get("awayTeam")):
        return "Survival Match"
    return "Pressure Match"


def _scheduled_description(match, teams, selected_team):
    home = teams[match["homeTeam"]]["name"]
    away = teams[match["awayTeam"]]["name"]
    if selected_team == match.get("homeTeam"):
        return f"{home} needs a result and help elsewhere."
    if selected_team == match.get("awayTeam"):
        return f"{away} needs a result and help elsewhere."
    return "Final matchday leverage."


def _render_match_link(match, story, teams, selected_id, selected_team=None, data=None):
    title = _format_match_line(match, teams)
    selected = selected_id == match["id"]

    if match["status"] == "completed" and story:
        match_type = story["matchType"]
        desc = story["oneLiner"]
    elif match["status"] == "live":
        match_type = "Live"
        desc = "Live match. This story is still moving."
    else:
        match_type = _scheduled_match_type(match, selected_team)
        desc = _scheduled_description(match, teams, selected_team)

    badge = badge_html(match_type, MATCH_TYPE_COLORS)
    active_class = " wcdl-match-card-active" if selected else ""
    href = f"?match_id={escape_html(match['id'])}"
    st.markdown(
        f'<a class="wcdl-match-link" href="{href}">'
        f'<div class="wcdl-match-card{active_class}">'
        f'<div class="wcdl-match-copy">'
        f'<div class="wcdl-match-title">{escape_html(title)}</div>'
        f'<div class="wcdl-match-desc">{escape_html(desc)}</div>'
        f'</div>'
        f'<div class="wcdl-match-type">{badge}</div>'
        f'</div>'
        f'</a>',
        unsafe_allow_html=True,
    )


def _render_group_match_board(data, group_id):
    teams = data["team_by_id"]
    matches = data["matches"]
    selected_id = st.session_state.get("selected_match_id")
    selected_team = st.session_state.get("selected_team")
    group_matches = data["matches_by_group"].get(group_id, [])
    live, completed, scheduled = _group_match_sections(group_matches)

    if not selected_id or not any(m["id"] == selected_id for m in group_matches):
        preferred = latest_match_for_group(data, group_id)
        if preferred:
            st.session_state["selected_match_id"] = preferred["id"]
            selected_id = preferred["id"]

    st.markdown(
        """
        <div class="wcdl-section-title">
          <h3>Match board</h3>
          <div class="wcdl-section-note">Only this group's games. Latest results first, upcoming fixtures below.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if live:
        st.markdown('<div class="wcdl-board-subhead">Live now</div>', unsafe_allow_html=True)
        for m in live:
            _render_match_link(m, None, teams, selected_id, selected_team, data)

    st.markdown('<div class="wcdl-board-subhead">Latest results</div>', unsafe_allow_html=True)
    if not completed:
        st.info("No completed matches in this group yet.")
    for m in completed:
        story = generate_match_story(m, teams, matches)
        _render_match_link(m, story, teams, selected_id, selected_team, data)

    st.markdown('<div class="wcdl-board-subhead">Coming up</div>', unsafe_allow_html=True)
    if not scheduled:
        st.caption("No upcoming fixtures in this group in the current dataset.")
    for m in scheduled:
        _render_match_link(m, None, teams, selected_id, selected_team, data)


def _render_selected_story(data):
    teams = data["team_by_id"]
    matches = data["matches"]
    match = selected_match(data)
    if not match:
        st.info("Pick a match from the board to open the story.")
        return

    home = teams[match["homeTeam"]]["name"]
    away = teams[match["awayTeam"]]["name"]

    if match["status"] == "completed":
        story = generate_match_story(match, teams, matches)
        title = f"{story['homeTeam']} {story['score'].replace('-', '–')} {story['awayTeam']}"
        body = (
            f'<div style="font-size:1.12rem;color:#07122B;font-weight:900;margin-bottom:12px;line-height:1.35;">'
            f'{escape_html(story["oneLiner"])}</div>'
            f'<div>{escape_html(story["takeaway"])} This story now carries into Why It Matters and Scenario Lab.</div>'
        )
        badge = story["matchType"]
        badge_map = MATCH_TYPE_COLORS
    else:
        title = f"{home} vs {away}"
        body = (
            f'<div style="font-size:1.12rem;color:#07122B;font-weight:900;margin-bottom:12px;line-height:1.35;">'
            f'This is the next Group {match["group"]} fixture to watch.</div>'
            f'<div>Use Scenario Lab to test how this result could change the group table.</div>'
        )
        badge = _scheduled_match_type(match, st.session_state.get("selected_team"))
        badge_map = MATCH_TYPE_COLORS

    st.markdown(
        card_html(
            label=f"Selected story · Group {match['group']}",
            title=title,
            body=body,
            badge=badge,
            badge_color_map=badge_map,
            accent="#2563EB",
            large=True,
        ),
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            card_html(
                label="Why this matters",
                title=f"Group {match['group']} context is now open.",
                body="Why It Matters explains this group without making you hunt through every table.",
                accent="#F59E0B",
            ),
            unsafe_allow_html=True,
        )
        if st.button("Open Why It Matters →", key="go_why_from_match", use_container_width=True):
            st.session_state["active_view"] = "why"
            st.rerun()
    with c2:
        st.markdown(
            card_html(
                label="Next step",
                title="Use Scenario Lab for this same group.",
                body="Scenario controls default to the selected group and team from this board.",
                accent="#2563EB",
            ),
            unsafe_allow_html=True,
        )
        if st.button("Open Scenario Lab →", key="go_scenario_from_match", use_container_width=True):
            st.session_state["active_view"] = "scenario"
            st.rerun()

    st.markdown(
        card_html(
            label="Current group table",
            title=f"Group {match['group']} table and status",
            body=_standings_with_status(data, match["group"]),
            accent="#2563EB",
            large=True,
        ),
        unsafe_allow_html=True,
    )


def render(data):
    ensure_selection_state(data)
    _render_team_group_controls(data)
    group_id = st.session_state["selected_group"]
    _render_group_header(data, group_id)

    left, right = st.columns([1, 1.08])
    with left:
        _render_group_match_board(data, group_id)
    with right:
        _render_selected_story(data)
