"""
calculate_standings.py

Builds a group table from a list of completed matches. Sort order:
points -> goal difference -> goals for. Head-to-head and disciplinary
tiebreaks are intentionally NOT implemented for MVP accuracy reasons
(see rules.json notes) - any case decided only by those criteria is
flagged as "too close to call" rather than silently guessed.
"""

POINTS_WIN = 3
POINTS_DRAW = 1
POINTS_LOSS = 0


def calculate_standings(team_ids, matches):
    """
    team_ids: list of team id strings in the group (any order)
    matches: list of match dicts with status == 'completed' belonging to
             this group (homeTeam, awayTeam, homeScore, awayScore)

    Returns: list of row dicts sorted best-to-worst, each with:
        teamId, played, won, drawn, lost, goalsFor, goalsAgainst,
        goalDifference, points, tiebreakNote
    """
    table = {
        tid: {
            "teamId": tid, "played": 0, "won": 0, "drawn": 0, "lost": 0,
            "goalsFor": 0, "goalsAgainst": 0, "goalDifference": 0, "points": 0,
        }
        for tid in team_ids
    }

    for m in matches:
        if m["status"] != "completed":
            continue
        home, away = m["homeTeam"], m["awayTeam"]
        if home not in table or away not in table:
            continue
        hs, as_ = m["homeScore"], m["awayScore"]

        for tid, gf, ga in ((home, hs, as_), (away, as_, hs)):
            row = table[tid]
            row["played"] += 1
            row["goalsFor"] += gf
            row["goalsAgainst"] += ga

        if hs > as_:
            table[home]["won"] += 1
            table[home]["points"] += POINTS_WIN
            table[away]["lost"] += 1
            table[away]["points"] += POINTS_LOSS
        elif hs < as_:
            table[away]["won"] += 1
            table[away]["points"] += POINTS_WIN
            table[home]["lost"] += 1
            table[home]["points"] += POINTS_LOSS
        else:
            table[home]["drawn"] += 1
            table[home]["points"] += POINTS_DRAW
            table[away]["drawn"] += 1
            table[away]["points"] += POINTS_DRAW

    for row in table.values():
        row["goalDifference"] = row["goalsFor"] - row["goalsAgainst"]

    rows = list(table.values())
    rows.sort(key=lambda r: (-r["points"], -r["goalDifference"], -r["goalsFor"]))

    # Flag genuine ties on points/GD/GF that this MVP can't break safely
    for i, row in enumerate(rows):
        row["tiebreakNote"] = None
        if i > 0:
            prev = rows[i - 1]
            if (row["points"], row["goalDifference"], row["goalsFor"]) == \
               (prev["points"], prev["goalDifference"], prev["goalsFor"]):
                row["tiebreakNote"] = "too close to call (head-to-head not modeled)"

    for i, row in enumerate(rows):
        row["rank"] = i + 1

    return rows
