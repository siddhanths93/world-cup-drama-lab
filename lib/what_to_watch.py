"""
what_to_watch.py

Ranks upcoming matches by watchability using free-data-safe inputs.
"""
from lib.team_strength import predict_match_outcome
from lib.group_chaos import calculate_group_chaos


def rank_upcoming_matches(data):
    teams = data["team_by_id"]
    matches = [m for m in data["matches"] if m["status"] == "scheduled"]
    results = []

    chaos_by_group = {g["id"]: calculate_group_chaos(g["id"], data) for g in data["groups"]}

    for m in matches:
        home = teams[m["homeTeam"]]
        away = teams[m["awayTeam"]]
        outcome = predict_match_outcome(m["homeTeam"], m["awayTeam"], teams, data["matches"])
        group_chaos = chaos_by_group[m["group"]]["score"]
        popularity = (home.get("popularity", 50) + away.get("popularity", 50)) / 2
        close_bonus = 18 if abs(outcome["strengthGap"]) < 8 else (10 if abs(outcome["strengthGap"]) < 18 else 4)
        upset_bonus = 14 if outcome["upsetRisk"] in ("Real chance", "Coin flip") else 6

        score = round(group_chaos * 0.45 + popularity * 0.25 + close_bonus + upset_bonus)
        score = max(0, min(100, score))
        results.append({
            "match": m,
            "score": score,
            "label": _label(score),
            "why": _why(home["name"], away["name"], group_chaos, outcome),
        })

    return sorted(results, key=lambda x: (-x["score"], x["match"]["date"]))


def _label(score):
    if score >= 80:
        return "Must Watch"
    if score >= 65:
        return "Worth Your Time"
    if score >= 45:
        return "Situational Watch"
    return "Only If You Care"


def _why(home_name, away_name, group_chaos, outcome):
    if group_chaos >= 75:
        group_text = "the group is already messy"
    elif group_chaos >= 55:
        group_text = "the group still has several open paths"
    else:
        group_text = "the group picture is starting to settle"

    if outcome["confidenceLabel"] in ("Coin flip", "Slight edge"):
        matchup_text = "the matchup looks close on the strength model"
    else:
        favorite = home_name if outcome["favorite"] == outcome["teamA"] else away_name
        matchup_text = f"{favorite} has the edge, but pressure can change the mood quickly"

    return f"{home_name} vs {away_name}: {group_text}, and {matchup_text}."
