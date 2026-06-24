"""
tournament_pulse.py

Builds the top-of-app summary cards.
"""
from lib.match_story import generate_match_story
from lib.group_chaos import rank_group_chaos
from lib.survival_card import build_survival_card
from lib.what_to_watch import rank_upcoming_matches


def build_tournament_pulse(data):
    teams = data["team_by_id"]
    matches = data["matches"]
    completed = [m for m in matches if m["status"] == "completed"]

    stories = [generate_match_story(m, teams, matches) for m in completed]
    story_pairs = list(zip(completed, stories))

    most_entertaining = max(story_pairs, key=lambda ms: ms[1]["entertainmentMeter"]["score"], default=None)
    chaos = rank_group_chaos(data)
    most_chaotic = chaos[0] if chaos else {"group": "N/A", "score": 0, "label": "Settled", "reasons": []}

    survival_cards = [build_survival_card(t["id"], data) for t in data["teams"]]
    pressure_order = {"Needs Help": 5, "Bubble Watch": 4, "In Control": 2, "Safe": 1, "Eliminated": 0}
    pressure = sorted(
        survival_cards,
        key=lambda c: (pressure_order.get(c["status"], 0), -c["points"]),
        reverse=True,
    )
    team_pressure = pressure[0] if pressure else None

    upcoming = rank_upcoming_matches(data)
    next_watch = upcoming[0] if upcoming else None

    return {
        "mostChaoticGroup": {
            "title": f"Group {most_chaotic['group']} — {most_chaotic['label']}",
            "subtitle": f"Chaos score {most_chaotic['score']}/100. " + "; ".join(most_chaotic.get("reasons", [])[:2]),
        },
        "teamUnderPressure": {
            "title": f"{team_pressure['teamName']} — {team_pressure['status']}" if team_pressure else "No pressure read yet",
            "subtitle": team_pressure["fanTranslation"] if team_pressure else "More data needed.",
        },
        "mostEntertainingMatch": _match_card(most_entertaining),
        "matchToWatchNext": _watch_card(next_watch, teams),
    }


def _match_card(match_story_pair):
    if not match_story_pair:
        return {"title": "No completed matches yet", "subtitle": "Check back after the first result."}
    match, story = match_story_pair
    return {
        "title": f"{story['homeTeam']} {story['score']} {story['awayTeam']}",
        "subtitle": f"{story['entertainmentMeter']['score']}/100 entertainment. {story['oneLiner']}",
    }


def _watch_card(watch, teams):
    if not watch:
        return {"title": "No upcoming matches in data", "subtitle": "Refresh the local JSON when new fixtures are available."}
    m = watch["match"]
    return {
        "title": f"{teams[m['homeTeam']]['name']} vs {teams[m['awayTeam']]['name']}",
        "subtitle": f"{watch['label']} — {watch['why']}",
    }
