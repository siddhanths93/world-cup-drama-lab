"""
scoreline_verdict.py

Free-data-safe scoreline verdicts. These labels are based on final score,
team strength, and group context. They do not claim to know shot quality,
xG, possession, or match control.
"""
from lib.team_strength import predict_match_outcome

BIG_STRENGTH_GAP = 12
SHOCK_DIFF_THRESHOLD = 3.0
NERVOUS_MARGIN = 1


def calculate_scoreline_verdict(match, team_by_id, all_matches):
    home, away = match["homeTeam"], match["awayTeam"]
    hs, away_score = match["homeScore"], match["awayScore"]

    outcome = predict_match_outcome(home, away, team_by_id, all_matches)
    favorite = outcome["favorite"]
    gap = outcome["strengthGap"]
    abs_gap = abs(gap)
    margin = hs - away_score
    abs_margin = abs(margin)
    is_draw = hs == away_score

    favorite_lost = (
        (favorite == home and hs < away_score) or
        (favorite == away and away_score < hs)
    )
    favorite_won = (
        (favorite == home and hs > away_score) or
        (favorite == away and away_score > hs)
    )

    if favorite is not None and abs_gap >= BIG_STRENGTH_GAP and favorite_lost:
        verdict = "Scoreline Shock"
        reason = "The result went against the strength gap. With free data, call this a scoreline shock rather than a full performance verdict."
    elif favorite is not None and abs_gap >= BIG_STRENGTH_GAP and is_draw:
        verdict = "Upset Signal"
        reason = "The underdog took points from a stronger team. That is enough to flag upset energy, even without shot-level data."
    elif favorite_won and abs_gap >= BIG_STRENGTH_GAP and abs_margin <= NERVOUS_MARGIN:
        verdict = "Nervier Than It Looks"
        reason = "The favorite got the result, but the margin was thin enough to keep the group story interesting."
    elif abs_margin >= 4 and abs_gap < BIG_STRENGTH_GAP:
        verdict = "Scoreline Shock"
        reason = "The final margin was much wider than the team-strength gap suggested."
    elif abs_margin <= 1:
        verdict = "Hard to Judge"
        reason = "The scoreline was tight. Without xG or shot data, this app avoids pretending it knows who truly controlled the match."
    else:
        verdict = "Expected Result"
        reason = "The result broadly matches the team-strength and scoreline context available in the free dataset."

    expected_margin = outcome.get("expectedMargin", 0)
    if favorite == away:
        expected_margin = -expected_margin
    elif favorite is None:
        expected_margin = 0

    return {
        "verdict": verdict,
        "reason": reason,
        "strengthGap": gap,
        "expectedMargin": round(expected_margin, 1),
        "actualMargin": margin,
    }
