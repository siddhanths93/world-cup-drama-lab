"""
Data loading layer for World Cup Drama Lab.

Loads the static JSON data (teams, groups, matches, rules) and builds
convenient lookup structures. Cached with Streamlit's cache so the JSON
is only parsed once per session.
"""
import json
import os
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_all():
    """Returns a dict with teams, groups, matches, rules, plus lookup maps."""
    teams = _load_json("teams.json")
    groups = _load_json("groups.json")
    matches = _load_json("matches.json")
    rules = _load_json("rules.json")

    team_by_id = {t["id"]: t for t in teams}
    group_by_id = {g["id"]: g for g in groups}

    matches_by_group = {}
    for m in matches:
        matches_by_group.setdefault(m["group"], []).append(m)

    return {
        "teams": teams,
        "groups": groups,
        "matches": matches,
        "rules": rules,
        "team_by_id": team_by_id,
        "group_by_id": group_by_id,
        "matches_by_group": matches_by_group,
    }


def team_name(team_by_id, team_id):
    t = team_by_id.get(team_id)
    return t["name"] if t else team_id


def completed_matches(matches):
    return [m for m in matches if m["status"] == "completed"]


def scheduled_matches(matches):
    return [m for m in matches if m["status"] == "scheduled"]
