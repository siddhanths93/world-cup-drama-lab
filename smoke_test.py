"""
Quick smoke test - not a full pytest suite, just enough to catch import
errors, type errors, and obviously-wrong output before wiring up the UI.
Run from the project root: python3 smoke_test.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# Streamlit's st.cache_data decorator needs a streamlit runtime context for
# some operations - import data_loader's raw json loader directly instead
# to keep this test runnable from plain python.
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_json(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


teams = load_json("teams.json")
groups = load_json("groups.json")
matches = load_json("matches.json")
team_by_id = {t["id"]: t for t in teams}

print(f"Loaded {len(teams)} teams, {len(groups)} groups, {len(matches)} matches")
assert len(teams) == 48
assert len(groups) == 12

from lib.calculate_standings import calculate_standings
from lib.team_strength import calculate_team_strength, predict_match_outcome, realism_check
from lib.qualification_status import calculate_qualification_status
from lib.simulate_group import simulate_group
from lib.drama_meter import calculate_drama_meter
from lib.scoreline_verdict import calculate_scoreline_verdict
from lib.momentum import calculate_momentum_movie
from lib.match_story import calculate_match_type, generate_match_story
from lib.explain_soccer import explain_group, explain_team

# --- standings ---
group_a_matches = [m for m in matches if m["group"] == "A"]
group_a_teams = [g["teamIds"] for g in groups if g["id"] == "A"][0]
standings_a = calculate_standings(group_a_teams, group_a_matches)
print("\nGroup A standings:")
for r in standings_a:
    print(f"  {r['rank']}. {team_by_id[r['teamId']]['name']:<16} "
          f"P{r['played']} W{r['won']} D{r['drawn']} L{r['lost']} "
          f"GD{r['goalDifference']:+d} Pts{r['points']}")
assert standings_a[0]["points"] >= standings_a[-1]["points"]

# --- team strength + prediction ---
strength_mex = calculate_team_strength("mex", team_by_id, matches)
print(f"\nMexico strength breakdown: {strength_mex}")

outcome = predict_match_outcome("bra", "hai", team_by_id, matches)
print(f"\nBrazil vs Haiti prediction: favorite={outcome['favorite']}, "
      f"winProbA={outcome['winProbA']}, likely={outcome['likelyScoreRange']}, "
      f"upsetRisk={outcome['upsetRisk']}")
assert outcome["favorite"] == "bra"

realism = realism_check("bra", "hai", 9, 0, team_by_id, matches)
print(f"Realism check for a predicted Brazil 9-0 Haiti: {realism}")
assert realism["isAggressive"] is True

realism1b = realism_check("kor", "cze", 6, 0, team_by_id, matches)
print(f"Realism check for a predicted South Korea 6-0 Czech Republic: {realism1b}")
assert realism1b["isAggressive"] is True

realism2 = realism_check("bra", "hai", 2, 0, team_by_id, matches)
print(f"Realism check for a predicted Brazil 2-0 Haiti: {realism2}")
assert realism2["isAggressive"] is False

# --- qualification status gets attached inside simulate_group, see below ---

# --- simulate_group: project Group A with a prediction for the remaining matches ---
scheduled_a = [m for m in group_a_matches if m["status"] == "scheduled"]
print(f"\nGroup A scheduled (to predict): {[m['id'] for m in scheduled_a]}")
predictions = {m["id"]: (1, 1) for m in scheduled_a}  # predict draws for the test
sim = simulate_group("A", group_a_matches, predictions, group_a_teams)
print("Simulated Group A standings with draws predicted:")
for r in sim["standings"]:
    print(f"  {r['rank']}. {team_by_id[r['teamId']]['name']:<16} Pts{r['points']} "
          f"-> {r['qualification']['label']} ({r['qualification']['note']})")

# --- drama meter / scoreline verdict / momentum / match type / full story ---
sample_match = next(m for m in matches if m["id"] == "ger-cuw-2026-06-14")  # 7-1 blowout
drama = calculate_drama_meter(sample_match, strength_gap=outcome["strengthGap"])
print(f"\nDrama meter for Germany 7-1 Curacao: {drama}")
assert drama["score"] >= 0 and drama["score"] <= 100

verdict = calculate_scoreline_verdict(sample_match, team_by_id, matches)
print(f"Scoreline verdict: {verdict}")

momentum = calculate_momentum_movie(sample_match, team_by_id)
print(f"Momentum movie: {momentum}")

mtype = calculate_match_type(sample_match, team_by_id, matches)
print(f"Match type: {mtype}")

story = generate_match_story(sample_match, team_by_id, matches)
print(f"\nFull match story takeaway: {story['takeaway']}")

# --- a genuinely close/upset-y match for contrast ---
close_match = next(m for m in matches if m["id"] == "qat-sui-2026-06-13")  # 1-1 draw
story2 = generate_match_story(close_match, team_by_id, matches)
print(f"Qatar vs Switzerland story: type={story2['matchType']}, "
      f"verdict={story2['scorelineVerdict']['verdict']}, drama={story2['dramaMeter']['score']} "
      f"({story2['dramaMeter']['label']})")

# --- explain soccer ---
explanation = explain_group("A", sim["standings"], team_by_id, style="complete_beginner")
print(f"\nExplain Group A (beginner): {explanation['translation']}")
print(f"Tell a friend: {explanation['tellYourFriend']}")

explanation_sf = explain_group("A", sim["standings"], team_by_id, style="sports_fan")
print(f"Explain Group A (sports fan): {explanation_sf['translation']}")

team_explanation = explain_team("mex", sim["standings"][0], team_by_id, style="complete_beginner")
print(f"\nExplain Mexico: {team_explanation['whyThisMatters']}")

print("\n✅ All smoke tests passed.")
