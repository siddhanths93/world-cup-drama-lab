"""
simulate_group.py

Combines real completed matches with user-supplied predicted scores for
the remaining matches in a group, recomputes the table, and attaches a
qualification status to each team.
"""
from lib.calculate_standings import calculate_standings
from lib.qualification_status import calculate_qualification_status


def simulate_group(group_id, all_matches_in_group, predictions, team_ids,
                    third_place_context=None):
    """
    group_id: e.g. "A"
    all_matches_in_group: every match dict (completed + scheduled) for this group
    predictions: dict of {match_id: (predicted_home_score, predicted_away_score)}
                 for scheduled matches the user has set a prediction for.
                 Matches with no entry are simply left out of the simulation
                 (treated as "not yet decided" - they won't appear as
                 completed in the projected table).
    team_ids: the 4 team ids in this group
    third_place_context: optional, see calculate_qualification_status

    Returns: {
        "standings": [...],  # projected table
        "remainingUndecided": [match_id, ...],  # scheduled matches with no
                                                  # prediction supplied yet
    }
    """
    simulated_matches = []
    remaining_undecided = []

    for m in all_matches_in_group:
        if m["status"] == "completed":
            simulated_matches.append(m)
        elif m["status"] == "scheduled":
            pred = predictions.get(m["id"])
            if pred is not None:
                ph, pa = pred
                simulated_matches.append({
                    **m,
                    "status": "completed",  # treat as decided for table purposes
                    "homeScore": ph,
                    "awayScore": pa,
                    "isPrediction": True,
                })
            else:
                remaining_undecided.append(m["id"])

    standings = calculate_standings(team_ids, simulated_matches)

    remaining_for_team = {tid: 0 for tid in team_ids}
    for m in all_matches_in_group:
        if m["status"] == "scheduled" and predictions.get(m["id"]) is None:
            if m["homeTeam"] in remaining_for_team:
                remaining_for_team[m["homeTeam"]] += 1
            if m["awayTeam"] in remaining_for_team:
                remaining_for_team[m["awayTeam"]] += 1

    for row in standings:
        row["qualification"] = calculate_qualification_status(
            row, standings, remaining_for_team[row["teamId"]], third_place_context
        )

    return {
        "standings": standings,
        "remainingUndecided": remaining_undecided,
    }
