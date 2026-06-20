
"""
What Happened view

Completed-match recaps with:
- tournament pulse
- top stories
- clickable recap board
- detailed recap
"""
import streamlit as st

from lib.match_story import generate_match_story
from lib.tournament_pulse import build_tournament_pulse
from lib.group_chaos import rank_group_chaos
from lib.ui_helpers import (
    card_html,
    stat_card_html,
    progress_html,
    badge_html,
    escape_html,
    DRAMA_COLORS,
    ENTERTAINMENT_COLORS,
    VERDICT_COLORS,
    MATCH_TYPE_COLORS,
    PULSE_COLORS,
)


def _label_for(m, teams):
    h, a = teams[m["homeTeam"]]["name"], teams[m["awayTeam"]]["name"]
    return f"Group {m['group']} · {m['date']} · {h} {m['homeScore']}-{m['awayScore']} {a}"


def _rank_stories(stories, sort_mode):
    def key(item):
        match, story = item
        if sort_mode == "Most entertaining":
            return story["entertainmentMeter"]["score"]
        if sort_mode == "Most dramatic":
            return story["dramaMeter"]["score"]
        if sort_mode == "Most misleading scoreline":
            return abs(story["scorelineVerdict"]["actualMargin"] - story["scorelineVerdict"]["expectedMargin"])
        if sort_mode == "Biggest margin":
            return abs(match["homeScore"] - match["awayScore"])
        return match["date"]

    return sorted(stories, key=key, reverse=True)


def _render_tournament_pulse(data):
    pulse = build_tournament_pulse(data)

    st.markdown(
        """
        <div class="wcdl-section-title">
          <h3>Tournament pulse</h3>
          <div class="wcdl-section-note">The quick read before you open a match.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns([1, 1, 1, 0.85])
    with col1:
        title = pulse["mostChaoticGroup"]["title"].split(" — ")[0]
        st.markdown(
            stat_card_html(
                "Most chaotic group",
                title,
                pulse["mostChaoticGroup"]["subtitle"],
                accent="#BE123C",
                badge="Group Chaos",
                badge_color_map=PULSE_COLORS,
            ),
            unsafe_allow_html=True,
        )
    with col2:
        title = pulse["teamUnderPressure"]["title"].split(" — ")[0]
        status = pulse["teamUnderPressure"]["title"].split(" — ")[-1]
        st.markdown(
            stat_card_html(
                "Team under pressure",
                title,
                status,
                accent="#B45309",
                badge=status,
                badge_color_map={status: "#B45309"},
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            stat_card_html(
                "What to watch next",
                pulse["matchToWatchNext"]["title"],
                pulse["matchToWatchNext"]["subtitle"],
                accent="#1D4ED8",
                badge="High Stakes",
                badge_color_map={"High Stakes": "#1D4ED8"},
            ),
            unsafe_allow_html=True,
        )
    with col4:
        completed = [m for m in data["matches"] if m["status"] == "completed"]
        goals = sum((m["homeScore"] or 0) + (m["awayScore"] or 0) for m in completed)
        avg = goals / len(completed) if completed else 0
        st.markdown(
            card_html(
                label="Quick snapshot",
                body=(
                    f'<div style="display:grid;grid-template-columns:54px 1fr;row-gap:8px;align-items:center;">'
                    f'<div style="font-size:1.55rem;font-weight:950;">48</div><div>Teams</div>'
                    f'<div style="font-size:1.55rem;font-weight:950;">12</div><div>Groups</div>'
                    f'<div style="font-size:1.55rem;font-weight:950;">{len(completed)}</div><div>Matches Played</div>'
                    f'<div style="font-size:1.55rem;font-weight:950;">{goals}</div><div>Goals Scored<br><span style="color:#94A3B8;">({avg:.2f} per match)</span></div>'
                    f'</div>'
                ),
                accent="#0F172A",
                variant="dark",
            ),
            unsafe_allow_html=True,
        )


def _render_top_stories(data, stories):
    chaos = rank_group_chaos(data)[0]
    statement_match, statement_story = max(stories, key=lambda ms: ms[1]["entertainmentMeter"]["score"])
    drama_match, drama_story = max(stories, key=lambda ms: ms[1]["dramaMeter"]["score"])

    story_cards = [
        (
            "01",
            f"{statement_story['homeTeam']} {statement_story['score']} {statement_story['awayTeam']} made a loud statement",
            statement_story["oneLiner"],
            f"{statement_story['entertainmentMeter']['score']}/100 entertainment",
            "#BE123C",
        ),
        (
            "02",
            f"Group {chaos['group']} is where the math gets interesting",
            "; ".join(chaos["reasons"][:2]),
            f"{chaos['score']}/100 chaos",
            "#D6A84F",
        ),
        (
            "03",
            f"{drama_story['homeTeam']} {drama_story['score']} {drama_story['awayTeam']} carried the strongest tension signal",
            drama_story["oneLiner"],
            f"{drama_story['dramaMeter']['score']}/100 drama",
            "#1D4ED8",
        ),
    ]

    st.markdown(
        """
        <div class="wcdl-section-title">
          <h3>Top stories so far</h3>
          <div class="wcdl-section-note">Generated from scores, standings context, and team strength inputs.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for col, (num, title, body, footer, accent) in zip(cols, story_cards):
        with col:
            st.markdown(
                card_html(
                    label=num,
                    title=title,
                    body=escape_html(body),
                    footer=footer,
                    accent=accent,
                    large=True,
                ),
                unsafe_allow_html=True,
            )


def _render_clickable_recap_board(stories):
    st.markdown(
        """
        <div class="wcdl-section-title">
          <h3>Match recap board</h3>
          <div class="wcdl-section-note">Pick a match and the detailed recap below will update.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sort_mode = st.selectbox(
        "Sort completed matches by",
        ["Most entertaining", "Most dramatic", "Most misleading scoreline", "Biggest margin", "Latest first"],
    )
    ranked = _rank_stories(stories, sort_mode)[:8]

    if "selected_match_id" not in st.session_state:
        st.session_state["selected_match_id"] = ranked[0][0]["id"]

    cols = st.columns(4)
    for i, (match, story) in enumerate(ranked):
        with cols[i % 4]:
            selected = st.session_state.get("selected_match_id") == match["id"]
            border = "#BE123C" if selected else "rgba(15,23,42,0.14)"
            bg = "#FFF7ED" if selected else "rgba(255,255,255,0.72)"
            st.markdown(
                f"""
                <div style="
                    background:{bg};
                    border:1px solid {border};
                    border-radius:10px;
                    padding:12px 12px 10px 12px;
                    min-height:112px;
                    margin-bottom:8px;
                    box-shadow:0 8px 18px rgba(15,23,42,0.06);
                ">
                  <div style="font-size:.72rem;text-transform:uppercase;color:#64748B;font-weight:850;">
                    Group {match['group']} · {match['date']}
                  </div>
                  <div style="font-weight:900;color:#0F172A;line-height:1.2;margin-top:7px;">
                    {escape_html(story['homeTeam'])} {escape_html(story['score'])} {escape_html(story['awayTeam'])}
                  </div>
                  <div style="margin-top:8px;">{badge_html(story['matchType'], MATCH_TYPE_COLORS)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open recap", key=f"open_{match['id']}", use_container_width=True):
                st.session_state["selected_match_id"] = match["id"]
                st.rerun()


def render(data):
    teams = data["team_by_id"]
    matches = data["matches"]
    completed = [m for m in matches if m["status"] == "completed"]
    completed.sort(key=lambda m: m["date"])
    stories = [(m, generate_match_story(m, teams, matches)) for m in completed]


    if not stories:
        st.info("No completed matches are available in the local dataset yet.")
        return

    _render_tournament_pulse(data)
    _render_top_stories(data, stories)
    _render_clickable_recap_board(stories)

    story_by_id = {m["id"]: (m, s) for m, s in stories}
    selected_id = st.session_state.get("selected_match_id")
    if selected_id not in story_by_id:
        selected_id = stories[0][0]["id"]
        st.session_state["selected_match_id"] = selected_id

    match, story = story_by_id[selected_id]

    st.markdown(
        """
        <div class="wcdl-section-title">
          <h3>Detailed recap</h3>
          <div class="wcdl-section-note">The short version, verdict, mood, and what it means.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        card_html(
            label=f"Group {match['group']} · {match['date']}",
            title=f"{story['homeTeam']} {story['score']} {story['awayTeam']}",
            body=(
                f'<div style="font-size:1.05rem;color:#0F172A;font-weight:850;margin-bottom:10px;">'
                f'{escape_html(story["oneLiner"])}</div>'
                f'<div>{escape_html(story["takeaway"])}</div>'
            ),
            accent="#BE123C",
            large=True,
        ),
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    verdict = story["scorelineVerdict"]
    with col1:
        st.markdown(
            card_html(
                label="Expected result",
                title=verdict["verdict"],
                body=badge_html(verdict["verdict"], VERDICT_COLORS),
                footer=verdict["reason"],
                accent=VERDICT_COLORS.get(verdict["verdict"], "#64748B"),
            ),
            unsafe_allow_html=True,
        )

    drama = story["dramaMeter"]
    drama_color = DRAMA_COLORS.get(drama["label"], "#1D4ED8")
    with col2:
        st.markdown(
            card_html(
                label="Drama",
                title=drama["label"],
                body=progress_html(drama["score"], drama_color),
                footer=f"{drama['score']}/100 tension",
                accent=drama_color,
            ),
            unsafe_allow_html=True,
        )

    entertainment = story["entertainmentMeter"]
    entertainment_color = ENTERTAINMENT_COLORS.get(entertainment["label"], "#15803D")
    with col3:
        st.markdown(
            card_html(
                label="Entertainment",
                title=entertainment["label"],
                body=progress_html(entertainment["score"], entertainment_color),
                footer=f"{entertainment['score']}/100 spectacle",
                accent=entertainment_color,
            ),
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            card_html(
                label="Match type",
                title=story["matchType"],
                body=badge_html(story["matchType"], MATCH_TYPE_COLORS),
                footer="A simple match personality label.",
                accent=MATCH_TYPE_COLORS.get(story["matchType"], "#64748B"),
            ),
            unsafe_allow_html=True,
        )

    col_a, col_b = st.columns([1.2, 1])
    with col_a:
        st.markdown(
            card_html(
                label="What this means",
                title="Tournament impact",
                body=(
                    f'{escape_html(story["takeaway"])} '
                    f'The result matters most when read through the group table in the sidebar.'
                ),
                accent="#BE123C",
            ),
            unsafe_allow_html=True,
        )

    with col_b:
        momentum = story["momentumMovie"]
        st.markdown(
            card_html(
                label="Momentum movie",
                title="The match in three beats",
                body=(
                    f'<strong>Opening:</strong> {escape_html(momentum["early"])}<br>'
                    f'<strong>Middle:</strong> {escape_html(momentum["middle"])}<br>'
                    f'<strong>Final:</strong> {escape_html(momentum["late"])}'
                ),
                footer=momentum["disclaimer"],
                accent="#D6A84F",
            ),
            unsafe_allow_html=True,
        )

    st.markdown(
        card_html(
            label="Method note",
            title="How these ratings are calculated",
            body=(
                "Drama is driven by tension, closeness, upset context, and qualification stakes. "
                "Entertainment is driven more by goals and spectacle. "
                "The scoreline verdict does not use xG or shot data in this free-data MVP."
            ),
            accent="#0F172A",
        ),
        unsafe_allow_html=True,
    )
