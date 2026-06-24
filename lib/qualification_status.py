"""
qualification_status.py

Simple, audience-friendly group status labels.

Final UI labels:
- Safe: mathematically or effectively through
- In Control: strong position, controls own path
- Bubble Watch: alive but vulnerable / table is tight
- Needs Help: low-control path or must rely on other results
- Eliminated: mathematically out

This is intentionally simpler than a full cross-group 3rd-place model.
"""


def calculate_qualification_status(row, standings, remaining_matches, third_place_context=None):
    rank = row["rank"]
    points = row["points"]
    gd = row.get("goalDifference", 0)

    by_rank = {r["rank"]: r for r in standings}
    rank2_points = by_rank.get(2, {}).get("points", 0)
    rank3_points = by_rank.get(3, {}).get("points", 0)
    rank4_points = by_rank.get(4, {}).get("points", 0)

    if remaining_matches == 0:
        if rank in (1, 2):
            return {"label": "Safe", "note": "Group stage complete — locked into a top-two place."}
        if rank == 3:
            return {
                "label": "Bubble Watch",
                "note": third_place_context or "Finished third — this depends on the best third-place comparison across groups.",
            }
        return {"label": "Eliminated", "note": "Group stage complete — finished outside the qualification picture."}

    # Top two: avoid overcalling danger when a team is actually in a strong position.
    if rank == 1:
        max_3rd = rank3_points + 3 * remaining_matches
        if points > max_3rd:
            return {"label": "Safe", "note": "Mathematically through — 3rd place can no longer catch them on points."}
        if points >= 4 and gd >= 0:
            return {"label": "In Control", "note": "Top of the group with a useful cushion. Do the job and avoid drama."}
        return {"label": "Bubble Watch", "note": "Top of the group, but the points gap is still thin."}

    if rank == 2:
        max_3rd = rank3_points + 3 * remaining_matches
        if points > max_3rd:
            return {"label": "Safe", "note": "Mathematically through — 3rd place can no longer catch them on points."}
        if points >= 4 and gd >= 0:
            return {"label": "In Control", "note": "In the top two and still controls the path."}
        return {"label": "Bubble Watch", "note": "Currently above the line, but one result can change the group."}

    if rank == 3:
        # If 3rd can still catch 2nd or be a best-third contender, keep it as bubble.
        max_possible = points + 3 * remaining_matches
        if max_possible < rank2_points:
            return {"label": "Needs Help", "note": "Top-two path is slipping; needs own result and help elsewhere."}
        return {
            "label": "Bubble Watch",
            "note": third_place_context or "Right on the line — top-two or best-third math is still alive.",
        }

    # rank 4
    max_possible = points + 3 * remaining_matches
    if max_possible < rank3_points:
        return {"label": "Eliminated", "note": "Cannot realistically catch the current bubble line on points."}
    return {"label": "Needs Help", "note": "Still alive, but needs a result and help from the rest of the group."}
