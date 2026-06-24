
"""
What Could Happen view

Interactive qualification simulator. Flow is compact:
team first, survival card second, score changes third, projected fate last.
No realism-check cards in v1 — the point is exploration, not forecasting.
"""
import streamlit as st

from lib.simulate_group import simulate_group
from lib.survival_card import build_survival_card
from lib.ui_helpers import (
    card_html,
    badge_html,
    escape_html,
    QUALIFICATION_COLORS,
)


def _pred_key(group_id, match_id, side):
    return f"pred_{group_id}_{match_id}_{side}"


def _set_prediction(group_id, match_id, home_score, away_score):
    st.session_state[_pred_key(group_id, match_id, "home")] = home_score
    st.session_state[_pred_key(group_id, match_id, "away")] = away_score


def _apply_optimistic_path(group_id, focus_team, scheduled):
    for m in scheduled:
        home, away = m["homeTeam"], m["awayTeam"]
        if focus_team == home:
            _set_prediction(group_id, m["id"], 2, 0)
        elif focus_team == away:
            _set_prediction(group_id, m["id"], 0, 2)
        else:
            _set_prediction(group_id, m["id"], 1, 1)


def _apply_nightmare_path(group_id, focus_team, scheduled):
    for m in scheduled:
        home, away = m["homeTeam"], m["awayTeam"]
        if focus_team == home:
            _set_prediction(group_id, m["id"], 0, 1)
        elif focus_team == away:
            _set_prediction(group_id, m["id"], 1, 0)
        else:
            _set_prediction(group_id, m["id"], 2, 1)


def _remaining_counts(group_team_ids, scheduled, predictions):
    remaining = {tid: 0 for tid in group_team_ids}
    for m in scheduled:
        if predictions.get(m["id"]) is None:
            remaining[m["homeTeam"]] += 1
            remaining[m["awayTeam"]] += 1
    return remaining


def _survival_body(card):
    return (
        f'<div style="font-size:1.05rem;color:#0F172A;font-weight:850;margin-bottom:10px;">'
        f'{escape_html(card["fanTranslation"])}</div>'
        f'<div><strong>Win path:</strong> {escape_html(card["bestPath"])}</div>'
        f'<div style="margin-top:8px;"><strong>Danger path:</strong> {escape_html(card["dangerPath"])}</div>'
        f'<div style="margin-top:8px;color:#64748B;">'
        f'Mood: {escape_html(card["mood"])} · Controls fate: {escape_html(card["controlsFate"])} · '
        f'{card["points"]} pts · GD {card["goalDifference"]:+d}</div>'
    )


def _projected_table_html(rows, teams):
    html = '<table class="wcdl-small-table"><thead><tr><th>#</th><th>Team</th><th>Pts</th><th>GD</th><th>Status</th></tr></thead><tbody>'
    for row in rows:
        status = row["qualification"]["label"]
        html += (
            f'<tr>'
            f'<td>{row["rank"]}</td>'
            f'<td>{escape_html(teams[row["teamId"]]["name"])}</td>'
            f'<td><strong>{row["points"]}</strong></td>'
            f'<td>{row["goalDifference"]:+d}</td>'
            f'<td>{badge_html(status, QUALIFICATION_COLORS)}</td>'
            f'</tr>'
        )
    html += "</tbody></table>"
    return html


def render(data):
    from lib.state_helpers import ensure_selection_state
    ensure_selection_state(data)
    teams = data["team_by_id"]
    groups = data["groups"]

    st.markdown(
        card_html(
            label="Scenario Lab",
            title="What happens next for the selected group?",
            body="This view inherits the group and team selected in Match Desk. Change remaining scores and see how the qualification story changes.",
            accent="#1D4ED8",
            large=True,
        ),
        unsafe_allow_html=True,
    )

    group_ids = [g["id"] for g in groups]
    default_group = st.session_state.get("selected_group", group_ids[0])
    if default_group not in group_ids:
        default_group = group_ids[0]

    if st.session_state.get("_scenario_synced_group") != default_group:
        st.session_state["wch_group"] = default_group
        st.session_state["_scenario_synced_group"] = default_group

    c_group, c_team = st.columns([1, 2])
    with c_group:
        group_id = st.selectbox(
            "Group",
            group_ids,
            index=group_ids.index(default_group),
            format_func=lambda g: f"Group {g}",
            key="wch_group",
        )
    if group_id != st.session_state.get("selected_group"):
        st.session_state["selected_group"] = group_id

    group_team_ids = data["group_by_id"][group_id]["teamIds"]
    group_matches = data["matches_by_group"].get(group_id, [])
    scheduled = [m for m in group_matches if m["status"] == "scheduled"]

    default_team = st.session_state.get("selected_team")
    if default_team not in group_team_ids:
        default_team = group_team_ids[0]
        st.session_state["selected_team"] = default_team

    if st.session_state.get("_scenario_synced_team") != default_team:
        st.session_state["wch_focus"] = default_team
        st.session_state["_scenario_synced_team"] = default_team

    with c_team:
        focus_team = st.selectbox(
            "Pick your team",
            group_team_ids,
            index=group_team_ids.index(default_team),
            format_func=lambda tid: teams[tid]["name"],
            key="wch_focus",
        )
    if focus_team != st.session_state.get("selected_team"):
        st.session_state["selected_team"] = focus_team

    current_card = build_survival_card(focus_team, data)

    left, right = st.columns([1, 1])
    with left:
        st.markdown(
            card_html(
                label="Current position",
                title=f"{current_card['teamName']} — {current_card['status']}",
                body=_survival_body(current_card),
                badge=current_card["status"],
                badge_color_map=QUALIFICATION_COLORS,
                footer=current_card["note"],
                accent=QUALIFICATION_COLORS.get(current_card["status"], "#1D4ED8"),
                large=True,
            ),
            unsafe_allow_html=True,
        )

    if not scheduled:
        with right:
            st.info("This group has no remaining scheduled matches in the local dataset.")
        return

    with right:
        st.markdown(
            card_html(
                label="Quick scenarios",
                title="Try a scenario",
                body="Current position uses the real table. Scenario outcome uses the scores you enter below.",
                accent="#D6A84F",
            ),
            unsafe_allow_html=True,
        )
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Optimistic", use_container_width=True):
                _apply_optimistic_path(group_id, focus_team, scheduled)
                st.rerun()
        with b2:
            if st.button("Nightmare", use_container_width=True):
                _apply_nightmare_path(group_id, focus_team, scheduled)
                st.rerun()
        with b3:
            if st.button("Reset", use_container_width=True):
                for m in scheduled:
                    st.session_state.pop(_pred_key(group_id, m["id"], "home"), None)
                    st.session_state.pop(_pred_key(group_id, m["id"], "away"), None)
                st.rerun()

    st.markdown(
        """
        <div class="wcdl-section-title">
          <h3>Remaining matches</h3>
          <div class="wcdl-section-note">Change the scores. The scenario outcome updates below.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    predictions = {}
    for m in scheduled:
        home_name, away_name = teams[m["homeTeam"]]["name"], teams[m["awayTeam"]]["name"]

        st.markdown(
            card_html(
                label=f"Group {group_id} · {m['date']}",
                title=f"{home_name} vs {away_name}",
                body="Enter a score for this remaining match.",
                accent="#1D4ED8",
            ),
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            hs = st.number_input(
                f"{home_name}",
                min_value=0,
                max_value=15,
                step=1,
                key=_pred_key(group_id, m["id"], "home"),
            )
        with c2:
            as_ = st.number_input(
                f"{away_name}",
                min_value=0,
                max_value=15,
                step=1,
                key=_pred_key(group_id, m["id"], "away"),
            )
        with c3:
            st.caption("Change this score to test the group path. No betting odds or probability claims are used.")

        predictions[m["id"]] = (hs, as_)

    sim = simulate_group(group_id, group_matches, predictions, group_team_ids)
    remaining_counts = _remaining_counts(group_team_ids, scheduled, predictions)
    projected_focus_card = build_survival_card(
        focus_team,
        data,
        simulated_standings=sim["standings"],
        simulated_remaining=remaining_counts,
    )

    st.markdown(
        """
        <div class="wcdl-section-title">
          <h3>Scenario outcome</h3>
          <div class="wcdl-section-note">Plain English first. Table second.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_result, c_table = st.columns([1.15, 1])
    with c_result:
        st.markdown(
            card_html(
                label="Scenario outcome",
                title=f"{projected_focus_card['teamName']} — {projected_focus_card['status']}",
                body=_survival_body(projected_focus_card),
                badge=projected_focus_card["status"],
                badge_color_map=QUALIFICATION_COLORS,
                footer=projected_focus_card["note"],
                accent=QUALIFICATION_COLORS.get(projected_focus_card["status"], "#1D4ED8"),
                large=True,
            ),
            unsafe_allow_html=True,
        )

    with c_table:
        st.markdown(
            card_html(
                label="Projected table",
                title=f"Group {group_id}",
                body=_projected_table_html(sim["standings"], teams),
                accent="#0F172A",
                large=True,
            ),
            unsafe_allow_html=True,
        )

    third_place_row = next((r for r in sim["standings"] if r["rank"] == 3), None)
    if third_place_row:
        st.markdown(
            card_html(
                label="Third-place bubble note",
                title=teams[third_place_row["teamId"]]["name"],
                body=third_place_row["qualification"]["note"],
                footer=(
                    "This MVP does not fully rank all 12 third-place teams against each other. "
                    "Treat Bubble Watch as an uncertainty label, not a final answer."
                ),
                accent="#B45309",
            ),
            unsafe_allow_html=True,
        )
