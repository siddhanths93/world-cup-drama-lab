"""
match_story.py

One call returns the match recap package used by the What Happened view.
"""
from lib.team_strength import predict_match_outcome
from lib.drama_meter import calculate_drama_meter, calculate_entertainment_meter
from lib.scoreline_verdict import calculate_scoreline_verdict
from lib.momentum import calculate_momentum_movie

CHAOS_GOAL_THRESHOLD = 5
BIG_GAP_THRESHOLD = 15
BUSINESS_TRIP_GAP_THRESHOLD = 10


def calculate_match_type(match, team_by_id, all_matches, heartbreak=False, calculator_mode=False):
    if heartbreak:
        return "Heartbreak Mode"
    if calculator_mode:
        return "Calculator Mode Activated"

    home, away = match["homeTeam"], match["awayTeam"]
    hs, as_ = match["homeScore"], match["awayScore"]
    total_goals = hs + as_
    margin = abs(hs - as_)
    is_draw = hs == as_

    outcome = predict_match_outcome(home, away, team_by_id, all_matches)
    favorite = outcome["favorite"]
    gap = abs(outcome["strengthGap"])
    favorite_lost = (favorite == home and hs < as_) or (favorite == away and as_ < hs)
    favorite_won = (favorite == home and hs > as_) or (favorite == away and as_ > hs)

    if total_goals >= CHAOS_GOAL_THRESHOLD:
        return "Chaos Ball"
    if favorite_lost and gap >= BIG_GAP_THRESHOLD:
        return "Upset Energy"
    if is_draw and gap >= BIG_GAP_THRESHOLD:
        return "Giant Sweating"
    if favorite_won and margin >= 2 and gap >= BUSINESS_TRIP_GAP_THRESHOLD:
        return "Business Trip"
    if (favorite_won and margin == 1) or (is_draw and gap < BIG_GAP_THRESHOLD and total_goals > 0):
        return "Nervy Grind"
    if total_goals <= 1 and gap < BUSINESS_TRIP_GAP_THRESHOLD:
        return "Group Stage Tax"
    return "Nervy Grind"


def generate_match_story(match, team_by_id, all_matches, heartbreak=False, calculator_mode=False,
                         qualification_stakes=False):
    home_name = team_by_id[match["homeTeam"]]["name"]
    away_name = team_by_id[match["awayTeam"]]["name"]
    hs, as_ = match["homeScore"], match["awayScore"]

    verdict = calculate_scoreline_verdict(match, team_by_id, all_matches)
    drama = calculate_drama_meter(match, strength_gap=verdict["strengthGap"], qualification_stakes=qualification_stakes)
    entertainment = calculate_entertainment_meter(match)
    momentum = calculate_momentum_movie(match, team_by_id)
    match_type = calculate_match_type(match, team_by_id, all_matches, heartbreak=heartbreak, calculator_mode=calculator_mode)

    if hs == as_:
        takeaway = f"{home_name} and {away_name} split the points. The bigger story is what that did to the group math."
    elif hs > as_:
        takeaway = f"{home_name} beat {away_name}. The result matters more when you read it through the group table."
    else:
        takeaway = f"{away_name} beat {home_name}. The result changes the pressure picture around both teams."

    one_liner = _one_line_takeaway(home_name, away_name, hs, as_, match_type, verdict["verdict"])

    return {
        "homeTeam": home_name,
        "awayTeam": away_name,
        "score": f"{hs}-{as_}",
        "scorelineVerdict": verdict,
        "dramaMeter": drama,
        "entertainmentMeter": entertainment,
        "momentumMovie": momentum,
        "matchType": match_type,
        "takeaway": takeaway,
        "oneLiner": one_liner,
    }


def _one_line_takeaway(home_name, away_name, hs, as_, match_type, verdict):
    if hs == as_:
        return f"Shared points, unfinished business, and more group-stage math for {home_name} and {away_name}."
    winner = home_name if hs > as_ else away_name
    loser = away_name if hs > as_ else home_name
    if match_type == "Business Trip":
        return f"{winner} handled the assignment; {loser} leaves with more pressure."
    if match_type == "Giant Sweating":
        return f"The stronger side got pulled into a harder match than expected."
    if verdict in ("Scoreline Shock", "Upset Signal"):
        return f"This is the kind of result that makes the group table worth refreshing."
    return f"{winner} got the result; {loser} now has less room for error."
