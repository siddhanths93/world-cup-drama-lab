"""
survival_card.py

Builds a concise team survival card: current mood, what they need, danger path,
and friend-friendly translation.
"""
from lib.calculate_standings import calculate_standings
from lib.qualification_status import calculate_qualification_status


def _remaining_for_team(group_team_ids, matches):
    remaining = {tid: 0 for tid in group_team_ids}
    remaining_matches = []
    for m in matches:
        if m["status"] == "scheduled":
            remaining_matches.append(m)
            if m["homeTeam"] in remaining:
                remaining[m["homeTeam"]] += 1
            if m["awayTeam"] in remaining:
                remaining[m["awayTeam"]] += 1
    return remaining, remaining_matches


def build_survival_card(team_id, data, simulated_standings=None, simulated_remaining=None):
    teams = data["team_by_id"]
    team = teams[team_id]
    group = data["group_by_id"][team["group"]]
    matches = data["matches_by_group"].get(team["group"], [])

    if simulated_standings is None:
        standings = calculate_standings(group["teamIds"], matches)
        remaining, remaining_matches = _remaining_for_team(group["teamIds"], matches)
    else:
        standings = simulated_standings
        remaining = simulated_remaining or {tid: 0 for tid in group["teamIds"]}
        remaining_matches = [m for m in matches if m["status"] == "scheduled"]

    row = next(r for r in standings if r["teamId"] == team_id)
    qualification = calculate_qualification_status(row, standings, remaining.get(team_id, 0))
    label = qualification["label"]

    next_match = next((m for m in remaining_matches if team_id in (m["homeTeam"], m["awayTeam"])), None)
    opponent = None
    if next_match:
        opponent_id = next_match["awayTeam"] if next_match["homeTeam"] == team_id else next_match["homeTeam"]
        opponent = teams[opponent_id]["name"]

    return {
        "teamId": team_id,
        "teamName": team["name"],
        "group": team["group"],
        "status": label,
        "mood": _mood(label),
        "controlsFate": _controls_fate(label, row["rank"], remaining.get(team_id, 0)),
        "currentRecord": f"{row['won']}W-{row['drawn']}D-{row['lost']}L",
        "points": row["points"],
        "goalDifference": row["goalDifference"],
        "nextOpponent": opponent,
        "bestPath": _best_path(label, opponent),
        "dangerPath": _danger_path(label, opponent),
        "fanTranslation": _fan_translation(label, team["name"], opponent),
        "note": qualification["note"],
    }


def _mood(label):
    return {
        "Safe": "calm",
        "In Control": "comfortable but not done",
        "Bubble Watch": "sweating",
        "Needs Help": "scoreboard watching",
        "Eliminated": "playing for pride",
    }.get(label, "unclear")


def _controls_fate(label, rank, remaining):
    if label in ("Safe", "In Control"):
        return "Mostly yes"
    if label == "Bubble Watch":
        return "Partially"
    if label == "Needs Help":
        return "Not fully"
    if remaining == 0:
        return "No"
    return "Barely"


def _best_path(label, opponent):
    if label == "Safe":
        return "Manage the final group situation and avoid unnecessary damage."
    if opponent:
        return f"Beat {opponent} and keep goal difference healthy."
    if label == "In Control":
        return "Avoid a bad final result and protect the current table position."
    if label == "Bubble Watch":
        return "Win or draw well enough to stay above the line."
    if label == "Needs Help":
        return "Win, then hope the teams around them drop points or lose goal difference."
    return "The group path is no longer available."


def _danger_path(label, opponent):
    if label == "Safe":
        return "The main danger is losing rhythm before the knockout rounds."
    if label == "In Control":
        return "A loss can turn comfort into calculator mode quickly."
    if label == "Bubble Watch":
        return "A draw may not be enough if the closest rival wins."
    if label == "Needs Help":
        return "Even a decent result might not be enough if other results break badly."
    return "Only spoiler role remains."


def _fan_translation(label, team_name, opponent):
    if label == "Safe":
        return f"{team_name} can breathe. The math is no longer the problem."
    if label == "In Control":
        return f"{team_name} is in a good place. Do the job and avoid drama."
    if label == "Bubble Watch":
        return f"{team_name} is alive, but one bad result can turn this into a spreadsheet exercise."
    if label == "Needs Help":
        return f"{team_name} needs their own result and help from elsewhere. This is scoreboard-watching territory."
    return f"{team_name} is out of the group race."
