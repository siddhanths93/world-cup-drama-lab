"""
momentum.py

Generates a 3-part narrative from final score and context only. The labels
avoid fake time blocks because the free data does not reliably include
minute-by-minute events.
"""


def calculate_momentum_movie(match, team_by_id):
    home_name = team_by_id[match["homeTeam"]]["name"]
    away_name = team_by_id[match["awayTeam"]]["name"]
    hs, as_ = match["homeScore"], match["awayScore"]
    margin = hs - as_
    total_goals = hs + as_

    if margin >= 3:
        winner, loser = home_name, away_name
        early = f"{winner} quickly turned this from a contest into a control game."
        middle = f"The scoreboard pressure kept building, and {loser} had little margin left."
        late = f"By the closing stretch, the main story was damage control rather than suspense."
    elif margin <= -3:
        winner, loser = away_name, home_name
        early = f"{winner} quickly turned this from a contest into a control game."
        middle = f"The scoreboard pressure kept building, and {loser} had little margin left."
        late = f"By the closing stretch, the main story was damage control rather than suspense."
    elif abs(margin) == 2:
        winner, loser = (home_name, away_name) if margin > 0 else (away_name, home_name)
        early = f"The match stayed open long enough to matter."
        middle = f"{winner} found enough separation to make the result feel manageable."
        late = f"{loser} needed a response, but the scoreboard never fully reopened."
    elif abs(margin) == 1:
        winner, loser = (home_name, away_name) if margin > 0 else (away_name, home_name)
        early = "The opening story was tension rather than control."
        middle = f"{winner} found the decisive edge, but never enough to make it feel completely safe."
        late = f"{loser} stayed close enough to keep the result uncomfortable."
    elif total_goals == 0:
        early = "The opening story was caution."
        middle = "Neither side created enough scoreboard separation to change the tone."
        late = "The match stayed stuck in a low-risk, low-reward pattern."
    else:
        early = f"{home_name} and {away_name} both had enough on the scoreboard to keep it alive."
        middle = "The middle story was balance: neither team fully solved the other."
        late = "The final story was shared points and unfinished business in the group."

    return {
        "early": early,
        "middle": middle,
        "late": late,
        "disclaimer": "Narrative recap based on final score and group context, not minute-by-minute event data.",
    }
