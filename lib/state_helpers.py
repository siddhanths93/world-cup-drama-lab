"""
state_helpers.py

Shared navigation state for World Cup Drama Lab.
Phase 1 goal: one selected match/team/group follows the user across
Match Desk -> Why It Matters -> Scenario Lab.
"""
import streamlit as st


def _match_sort_key(match):
    # date strings are ISO-like in current data; id tiebreaker keeps stable order.
    return (match.get("date", ""), match.get("id", ""))


def latest_active_group(data):
    """Pick the group from the latest live/completed match, falling back to first group."""
    live = [m for m in data["matches"] if m.get("status") == "live"]
    if live:
        return sorted(live, key=_match_sort_key, reverse=True)[0]["group"]

    completed = [m for m in data["matches"] if m.get("status") == "completed"]
    if completed:
        return sorted(completed, key=_match_sort_key, reverse=True)[0]["group"]

    return data["groups"][0]["id"] if data.get("groups") else None


def latest_match_for_group(data, group_id):
    """Return latest live/completed match in a group, else nearest upcoming, else None."""
    matches = data["matches_by_group"].get(group_id, [])
    live = [m for m in matches if m.get("status") == "live"]
    if live:
        return sorted(live, key=_match_sort_key, reverse=True)[0]

    completed = [m for m in matches if m.get("status") == "completed"]
    if completed:
        return sorted(completed, key=_match_sort_key, reverse=True)[0]

    scheduled = [m for m in matches if m.get("status") == "scheduled"]
    if scheduled:
        return sorted(scheduled, key=_match_sort_key)[0]

    return None


def latest_match_for_team(data, team_id):
    """Return latest live/completed match involving a team, else nearest upcoming."""
    matches = [
        m for m in data["matches"]
        if m.get("homeTeam") == team_id or m.get("awayTeam") == team_id
    ]
    live = [m for m in matches if m.get("status") == "live"]
    if live:
        return sorted(live, key=_match_sort_key, reverse=True)[0]

    completed = [m for m in matches if m.get("status") == "completed"]
    if completed:
        return sorted(completed, key=_match_sort_key, reverse=True)[0]

    scheduled = [m for m in matches if m.get("status") == "scheduled"]
    if scheduled:
        return sorted(scheduled, key=_match_sort_key)[0]

    return None


def default_team_for_group(data, group_id):
    ids = data["group_by_id"].get(group_id, {}).get("teamIds", [])
    return ids[0] if ids else None


def ensure_selection_state(data):
    """Initialize shared navigation state safely."""
    group_ids = [g["id"] for g in data.get("groups", [])]
    team_ids = [t["id"] for t in data.get("teams", [])]

    if not group_ids or not team_ids:
        return

    if st.session_state.get("selected_group") not in group_ids:
        st.session_state["selected_group"] = latest_active_group(data) or group_ids[0]

    group_id = st.session_state["selected_group"]
    group_team_ids = data["group_by_id"].get(group_id, {}).get("teamIds", [])

    if st.session_state.get("selected_team") not in team_ids:
        st.session_state["selected_team"] = default_team_for_group(data, group_id)

    if st.session_state.get("selected_team") not in group_team_ids:
        st.session_state["selected_team"] = default_team_for_group(data, group_id)

    selected_match_id = st.session_state.get("selected_match_id")
    match_ids = {m["id"] for m in data.get("matches", [])}
    if selected_match_id not in match_ids:
        preferred = latest_match_for_team(data, st.session_state.get("selected_team"))
        if preferred is None:
            preferred = latest_match_for_group(data, group_id)
        if preferred:
            st.session_state["selected_match_id"] = preferred["id"]


def set_selected_group(data, group_id):
    """Update group and keep team/match coherent."""
    st.session_state["selected_group"] = group_id
    group_team_ids = data["group_by_id"].get(group_id, {}).get("teamIds", [])
    if st.session_state.get("selected_team") not in group_team_ids:
        st.session_state["selected_team"] = group_team_ids[0] if group_team_ids else None
    match = latest_match_for_team(data, st.session_state.get("selected_team"))
    if match is None or match.get("group") != group_id:
        match = latest_match_for_group(data, group_id)
    if match:
        st.session_state["selected_match_id"] = match["id"]


def set_selected_team(data, team_id):
    """Update team, then infer group and preferred match."""
    team = data["team_by_id"].get(team_id)
    if not team:
        return
    st.session_state["selected_team"] = team_id
    st.session_state["selected_group"] = team["group"]
    match = latest_match_for_team(data, team_id) or latest_match_for_group(data, team["group"])
    if match:
        st.session_state["selected_match_id"] = match["id"]


def set_selected_match(data, match_id):
    """Update selected match and sync group/team context."""
    match = next((m for m in data["matches"] if m["id"] == match_id), None)
    if not match:
        return
    st.session_state["selected_match_id"] = match_id
    st.session_state["selected_group"] = match["group"]
    # Prefer the current selected team if it is in the match; else home team.
    current_team = st.session_state.get("selected_team")
    if current_team not in (match.get("homeTeam"), match.get("awayTeam")):
        st.session_state["selected_team"] = match.get("homeTeam")


def selected_match(data):
    ensure_selection_state(data)
    mid = st.session_state.get("selected_match_id")
    return next((m for m in data["matches"] if m["id"] == mid), None)
