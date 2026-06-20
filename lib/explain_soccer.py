"""
explain_soccer.py

Plain-English explanations for group and team context.
"""

STATUS_PHRASES_BEGINNER = {
    "Safe": "is through to the next round in this scenario",
    "In Control": "is in a strong spot, but still has work left",
    "Danger Zone": "is in the qualifying picture, but one bad result can change things",
    "Calculator Mode": "needs its own result and help from other scorelines",
    "Needs a Miracle": "is in real trouble and needs a lot to go right",
    "Eliminated": "is out of the running",
}

STATUS_PHRASES_SPORTS_FAN = {
    "Safe": "has effectively clinched a playoff spot in this setup",
    "In Control": "controls its own destiny",
    "Danger Zone": "is on the bubble but still alive",
    "Calculator Mode": "is scoreboard watching like a wild-card team",
    "Needs a Miracle": "needs win-out-and-get-help energy",
    "Eliminated": "has been knocked out of the race",
}


def _group_translation(rows, team_by_id, style):
    top_two = rows[:2]
    third = rows[2] if len(rows) > 2 else None
    top_names = " and ".join(team_by_id[r["teamId"]]["name"] for r in top_two)
    if style == "sports_fan":
        if third:
            third_name = team_by_id[third["teamId"]]["name"]
            return f"{top_names} are in the playoff spots. {third_name} is the bubble team. Goal difference is point differential."
        return f"{top_names} are in the playoff spots."
    if third:
        third_name = team_by_id[third["teamId"]]["name"]
        return f"{top_names} are above the line. {third_name} is where the math starts."
    return f"{top_names} are above the line."


def explain_group(group_id, rows, team_by_id, style="complete_beginner"):
    phrases = STATUS_PHRASES_SPORTS_FAN if style == "sports_fan" else STATUS_PHRASES_BEGINNER

    why_lines = []
    want_lines = []
    for row in rows:
        name = team_by_id[row["teamId"]]["name"]
        label = row["qualification"]["label"]
        why_lines.append(f"{name} {phrases[label]}.")
        if label == "Safe":
            want_lines.append(f"{name} wants to manage risk and stay sharp.")
        elif label in ("In Control", "Danger Zone"):
            want_lines.append(f"{name} wants a clean result that removes the math.")
        elif label == "Calculator Mode":
            want_lines.append(f"{name} wants a win and friendly results elsewhere.")
        elif label == "Needs a Miracle":
            want_lines.append(f"{name} needs a win and a lot of help.")
        else:
            want_lines.append(f"{name} is mostly playing for pride or spoiler value.")

    if style == "sports_fan":
        watch_for = "Watch the line between 2nd and 3rd. That is the playoff cut line; goal difference is the point differential tiebreak."
    else:
        watch_for = "Watch the gap between 2nd and 3rd. That tells you who is safe, who is sweating, and who needs help."

    translation = _group_translation(rows, team_by_id, style)
    tell_friend = f"Group {group_id}, one sentence version: {translation}"

    return {
        "whyThisMatters": " ".join(why_lines),
        "whatEachTeamWants": " ".join(want_lines),
        "whatToWatchFor": watch_for,
        "translation": translation,
        "tellYourFriend": tell_friend,
    }


def explain_team(team_id, row, team_by_id, style="complete_beginner"):
    team = team_by_id[team_id]
    label = row["qualification"]["label"]
    note = row["qualification"]["note"]
    phrases = STATUS_PHRASES_SPORTS_FAN if style == "sports_fan" else STATUS_PHRASES_BEGINNER

    why = f"{team['name']} {phrases[label]}. Record so far: {row['won']}W-{row['drawn']}D-{row['lost']}L, goal difference {row['goalDifference']:+d}."
    wants = {
        "Safe": "to keep momentum and avoid unnecessary damage.",
        "In Control": "one more clean result to avoid late group-stage drama.",
        "Danger Zone": "a result that prevents calculator mode.",
        "Calculator Mode": "a win, plus help from another scoreline.",
        "Needs a Miracle": "a win, probably a big one, plus outside help.",
        "Eliminated": "pride and spoiler value.",
    }[label]

    if style == "sports_fan":
        watch_for = f"Goal difference is the point differential. {team['name']} is currently {row['goalDifference']:+d}."
    else:
        watch_for = f"Keep an eye on goal difference ({row['goalDifference']:+d}). It can decide who survives when points are tied."

    translation = f"{team['name']}: {note}"
    tell_friend = f"{team['name']} in one line: {translation}"

    return {
        "whyThisMatters": why,
        "whatEachTeamWants": f"{team['name']} wants {wants}",
        "whatToWatchFor": watch_for,
        "translation": translation,
        "tellYourFriend": tell_friend,
    }
