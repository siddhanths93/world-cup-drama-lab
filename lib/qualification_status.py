"""
calculate_qualification_status.py

Assigns one of six labels to a team based on its current group position
and how many matches it has left. This is deliberately approximate where
the 2026 format genuinely requires cross-group comparison (the third-place
bubble) - see the note returned alongside "Calculator Mode" rather than a
false-precision rank number.

Labels: Safe / In Control / Danger Zone / Calculator Mode /
        Needs a Miracle / Eliminated
"""

IN_CONTROL_GAP_THRESHOLD = 4  # points clear of 3rd place to count as "In Control"


def calculate_qualification_status(row, standings, remaining_matches, third_place_context=None):
    rank = row["rank"]
    points = row["points"]

    by_rank = {r["rank"]: r for r in standings}
    rank3_points = by_rank.get(3, {}).get("points", 0)
    rank2_points = by_rank.get(2, {}).get("points", 0)

    if rank in (1, 2):
        # remaining matches for whoever currently sits 3rd (rough estimate:
        # assume same remaining count as this team's group stage, since all
        # teams in a 3-team-remaining group play the same number of total
        # matches - fine approximation for MVP)
        max_possible_3rd = rank3_points + 3 * remaining_matches
        if points > max_possible_3rd:
            return {"label": "Safe", "note": "Mathematically through - 3rd place can no longer catch up on points."}
        if remaining_matches == 0:
            return {"label": "Safe", "note": "Group stage complete - locked into the top two."}
        gap = points - rank3_points
        if gap >= IN_CONTROL_GAP_THRESHOLD:
            return {"label": "In Control", "note": f"{gap} points clear of 3rd with {remaining_matches} match(es) left."}
        return {"label": "Danger Zone", "note": f"Only {gap} point(s) clear of 3rd - this is not settled yet."}

    if rank == 3:
        note = (third_place_context or
                "Top-two finish is unlikely from here - fate now depends on "
                "being one of the 8 best third-place teams across all 12 groups.")
        return {"label": "Calculator Mode", "note": note}

    # rank 4
    if remaining_matches == 0:
        return {"label": "Eliminated", "note": "Group stage complete - finished bottom of the group."}
    max_possible_points = points + 3 * remaining_matches
    if max_possible_points <= rank3_points:
        return {"label": "Eliminated", "note": "Can no longer catch the current 3rd-place team on points."}
    return {"label": "Needs a Miracle", "note": f"Mathematically alive with {remaining_matches} match(es) left, but needs help."}
