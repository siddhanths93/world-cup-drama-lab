"""
team_strength.py

Transparent, rule-based team strength and score realism helpers. This is
not a forecasting model. It exists to keep user-entered predictions from
feeling arbitrary.
"""
import math

FORM_WIN = 4
FORM_DRAW = 1
FORM_LOSS = -2
GD_MULTIPLIER = 1.5
ATTACK_MULTIPLIER = 1.2
DEFENSE_MULTIPLIER = 1.2

WIN_PROB_DIVISOR = 18
GOAL_MARGIN_DIVISOR = 14
AGGRESSIVE_GOAL_BUFFER = 2.5


def _team_completed_matches(team_id, matches):
    return [
        m for m in matches
        if m["status"] == "completed" and team_id in (m["homeTeam"], m["awayTeam"])
    ]


def calculate_team_strength(team_id, team_by_id, matches):
    team = team_by_id[team_id]
    base = team["baseStrength"]

    played = _team_completed_matches(team_id, matches)
    if not played:
        return {
            "teamId": team_id,
            "baseStrength": base,
            "formBonus": 0,
            "goalDifferenceBonus": 0,
            "attackBonus": 0,
            "defensiveWeaknessPenalty": 0,
            "teamStrength": round(base, 1),
            "matchesConsidered": 0,
        }

    form_total, gf_total, ga_total = 0, 0, 0
    for m in played:
        is_home = m["homeTeam"] == team_id
        gf = m["homeScore"] if is_home else m["awayScore"]
        ga = m["awayScore"] if is_home else m["homeScore"]
        gf_total += gf
        ga_total += ga
        if gf > ga:
            form_total += FORM_WIN
        elif gf == ga:
            form_total += FORM_DRAW
        else:
            form_total += FORM_LOSS

    n = len(played)
    form_bonus = form_total / n
    gd_bonus = ((gf_total - ga_total) / n) * GD_MULTIPLIER
    attack_bonus = (gf_total / n) * ATTACK_MULTIPLIER
    defense_penalty = (ga_total / n) * DEFENSE_MULTIPLIER
    strength = base + form_bonus + gd_bonus + attack_bonus - defense_penalty

    return {
        "teamId": team_id,
        "baseStrength": base,
        "formBonus": round(form_bonus, 1),
        "goalDifferenceBonus": round(gd_bonus, 1),
        "attackBonus": round(attack_bonus, 1),
        "defensiveWeaknessPenalty": round(defense_penalty, 1),
        "teamStrength": round(strength, 1),
        "matchesConsidered": n,
    }


def _strength_band(abs_gap):
    if abs_gap < 4:
        return "Coin flip"
    if abs_gap < 12:
        return "Slight edge"
    if abs_gap < 25:
        return "Clear favorite"
    return "Heavy favorite"


def predict_match_outcome(team_a_id, team_b_id, team_by_id, matches):
    sa = calculate_team_strength(team_a_id, team_by_id, matches)
    sb = calculate_team_strength(team_b_id, team_by_id, matches)
    gap = sa["teamStrength"] - sb["teamStrength"]

    # Internal probability-like signals only. UI should show labels, not exact percentages.
    win_a = 1 / (1 + math.pow(10, -gap / WIN_PROB_DIVISOR))
    draw_peak = 0.30
    draw_prob = draw_peak * math.exp(-(gap ** 2) / (2 * (WIN_PROB_DIVISOR * 1.8) ** 2))
    win_a_adj = win_a * (1 - draw_prob)
    win_b_adj = (1 - win_a) * (1 - draw_prob)

    favorite = team_a_id if gap > 0 else (team_b_id if gap < 0 else None)
    abs_gap = abs(gap)

    if abs_gap < 4:
        upset_risk = "Coin flip"
    elif abs_gap < 12:
        upset_risk = "Real chance"
    elif abs_gap < 25:
        upset_risk = "Would be a surprise"
    else:
        upset_risk = "Would be a shock"

    expected_margin = abs_gap / GOAL_MARGIN_DIVISOR
    likely_range = _likely_score_range(expected_margin)

    return {
        "teamA": team_a_id,
        "teamB": team_b_id,
        "strengthA": sa["teamStrength"],
        "strengthB": sb["teamStrength"],
        "strengthGap": round(gap, 1),
        "favorite": favorite,
        "confidenceLabel": _strength_band(abs_gap),
        "winProbA": round(win_a_adj, 3),
        "winProbB": round(win_b_adj, 3),
        "drawProb": round(draw_prob, 3),
        "expectedMargin": round(expected_margin, 1),
        "likelyScoreRange": likely_range,
        "upsetRisk": upset_risk,
    }


def _likely_score_range(expected_margin):
    if expected_margin < 0.5:
        return "1-1, 1-0, or 0-0"
    if expected_margin < 1.2:
        return "1-0, 2-1, or 1-1"
    if expected_margin < 2.2:
        return "2-0, 2-1, or 3-1"
    if expected_margin < 3.2:
        return "3-0, 3-1, or 4-1"
    return "4-0 or wider"


def realism_check(team_a_id, team_b_id, predicted_home, predicted_away, team_by_id, matches):
    outcome = predict_match_outcome(team_a_id, team_b_id, team_by_id, matches)
    predicted_margin = abs(predicted_home - predicted_away)
    total_goals = predicted_home + predicted_away
    expected = outcome["expectedMargin"]
    threshold = expected + AGGRESSIVE_GOAL_BUFFER

    if predicted_margin <= threshold and total_goals <= 5:
        return {
            "label": "Realistic",
            "isAggressive": False,
            "message": f"Realistic range. Similar outcomes include {outcome['likelyScoreRange']}.",
            "suggestedRange": outcome["likelyScoreRange"],
        }

    if predicted_margin <= threshold and total_goals > 5:
        return {
            "label": "Aggressive",
            "isAggressive": True,
            "message": f"High-scoring but not impossible. A calmer range would be {outcome['likelyScoreRange']}.",
            "suggestedRange": outcome["likelyScoreRange"],
        }

    if predicted_margin <= threshold + 2:
        return {
            "label": "Chaos Prediction",
            "isAggressive": True,
            "message": f"Possible, but it needs a chaotic game script. A more realistic range is {outcome['likelyScoreRange']}.",
            "suggestedRange": outcome["likelyScoreRange"],
        }

    return {
        "label": "Extremely Spicy",
        "isAggressive": True,
        "message": f"Very aggressive. Based on team strength and current form, {outcome['likelyScoreRange']} is more grounded.",
        "suggestedRange": outcome["likelyScoreRange"],
    }
