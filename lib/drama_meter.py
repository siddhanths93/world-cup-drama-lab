"""
drama_meter.py

Two separate scores:
- Drama Meter measures tension: closeness, stakes, and upset pressure.
- Entertainment Meter measures spectacle: goals and unusual scorelines.

This avoids calling a 7-1 blowout "dramatic" just because it had goals.
"""

DRAMA_BASELINE = 12
ENTERTAINMENT_BASELINE = 8

DRAMA_BANDS = [
    (0, 30, "Low Drama"),
    (31, 55, "Decent Watch"),
    (56, 75, "Proper World Cup Tension"),
    (76, 90, "Chaos Match"),
    (91, 100, "Football Heritage Moment"),
]

ENTERTAINMENT_BANDS = [
    (0, 30, "Low Event"),
    (31, 55, "Respectable Watch"),
    (56, 80, "Goal Fest"),
    (81, 100, "Pure Entertainment"),
]


def _band_label(score, bands):
    for lo, hi, label in bands:
        if lo <= score <= hi:
            return label
    return bands[-1][2]


def calculate_drama_meter(match, strength_gap=None, qualification_stakes=False):
    hs, as_ = match["homeScore"], match["awayScore"]
    total_goals = hs + as_
    margin = abs(hs - as_)

    score = DRAMA_BASELINE
    closeness = 0
    if margin == 0:
        closeness = 26
    elif margin == 1:
        closeness = 22
    elif margin == 2:
        closeness = 8
    else:
        closeness = -8
    score += closeness

    goal_tension = min(total_goals * 4, 16)
    if margin >= 3:
        goal_tension = max(0, goal_tension - 10)
    score += goal_tension

    upset = 0
    if strength_gap is not None and abs(strength_gap) >= 12 and margin <= 1:
        upset = 18
        score += upset

    stakes = 12 if qualification_stakes else 0
    score += stakes

    score = max(0, min(100, round(score)))
    return {
        "score": score,
        "label": _band_label(score, DRAMA_BANDS),
        "breakdown": {
            "baseline": DRAMA_BASELINE,
            "closeness": closeness,
            "goalTension": goal_tension,
            "upsetPressure": upset,
            "qualificationStakes": stakes,
        },
    }


def calculate_entertainment_meter(match):
    hs, as_ = match["homeScore"], match["awayScore"]
    total_goals = hs + as_
    margin = abs(hs - as_)

    score = ENTERTAINMENT_BASELINE
    goals = min(total_goals * 11, 70)
    score += goals

    weird_scoreline = 0
    if total_goals >= 5:
        weird_scoreline += 12
    if margin >= 4:
        weird_scoreline += 8
    if hs == as_ and total_goals >= 4:
        weird_scoreline += 10
    score += weird_scoreline

    score = max(0, min(100, round(score)))
    return {
        "score": score,
        "label": _band_label(score, ENTERTAINMENT_BANDS),
        "breakdown": {
            "baseline": ENTERTAINMENT_BASELINE,
            "goals": goals,
            "scorelineShape": weird_scoreline,
        },
    }
