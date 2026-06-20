"""
group_chaos.py

Scores how messy a group is using standings and remaining fixtures.
"""
from lib.calculate_standings import calculate_standings
from lib.qualification_status import calculate_qualification_status


def _label(score):
    if score < 30:
        return "Settled"
    if score < 55:
        return "Still Open"
    if score < 78:
        return "Calculator Mode Brewing"
    return "Pure Chaos"


def calculate_group_chaos(group_id, data):
    group = data["group_by_id"][group_id]
    teams = data["team_by_id"]
    matches = data["matches_by_group"].get(group_id, [])
    rows = calculate_standings(group["teamIds"], matches)

    remaining_matches = [m for m in matches if m["status"] == "scheduled"]
    points = [r["points"] for r in rows]
    gd = [r["goalDifference"] for r in rows]

    score = 10
    reasons = []

    points_spread = max(points) - min(points) if points else 0
    if points_spread <= 3:
        score += 28
        reasons.append("the points gap is tight")
    elif points_spread <= 5:
        score += 18
        reasons.append("several teams are still close on points")
    else:
        score += 6

    gd_spread = max(gd) - min(gd) if gd else 0
    if gd_spread <= 3:
        score += 18
        reasons.append("goal difference is still close")
    elif gd_spread <= 6:
        score += 10

    if remaining_matches:
        score += min(len(remaining_matches) * 8, 24)
        reasons.append(f"{len(remaining_matches)} match(es) still need to be played")

    # Teams not mathematically done add chaos.
    remaining_for_team = {tid: 0 for tid in group["teamIds"]}
    for m in remaining_matches:
        remaining_for_team[m["homeTeam"]] += 1
        remaining_for_team[m["awayTeam"]] += 1

    labels = []
    for row in rows:
        q = calculate_qualification_status(row, rows, remaining_for_team[row["teamId"]])
        labels.append(q["label"])
    unresolved = sum(1 for x in labels if x not in ("Safe", "Eliminated"))
    score += unresolved * 6
    if unresolved >= 3:
        reasons.append("most of the group still has something to play for")

    # 2nd/3rd tension matters most.
    if len(rows) >= 3:
        gap_2_3 = rows[1]["points"] - rows[2]["points"]
        if gap_2_3 <= 1:
            score += 15
            reasons.append("the 2nd/3rd place line is thin")
        elif gap_2_3 <= 3:
            score += 8

    score = max(0, min(100, round(score)))
    if not reasons:
        reasons = ["the table is starting to separate"]

    return {
        "group": group_id,
        "score": score,
        "label": _label(score),
        "reasons": reasons[:4],
        "standings": rows,
    }


def rank_group_chaos(data):
    groups = data["groups"]
    results = [calculate_group_chaos(g["id"], data) for g in groups]
    return sorted(results, key=lambda x: x["score"], reverse=True)
