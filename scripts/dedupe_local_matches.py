"""
One-time local data cleanup.

Run this after pulling the cleanup release if your deployed app still shows
teams with too many matches played. It removes duplicate group fixtures from
data/matches.json using the same fixture-first logic as the sync script.
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MATCHES_PATH = PROJECT_ROOT / "data" / "matches.json"


def is_group_value(value):
    return str(value or "").strip().upper() in set("ABCDEFGHIJKL")


def key_for(m):
    group = str(m.get("group", "")).strip().upper()
    home = m.get("homeTeam")
    away = m.get("awayTeam")

    if is_group_value(group) and home and away:
        teams = tuple(sorted([home, away]))
        return ("group_fixture", group, teams[0], teams[1])

    if m.get("externalId"):
        return ("external", str(m["externalId"]))

    return ("fixture", group, home, away)


def quality(m):
    return (
        1 if m.get("status") == "completed" else 0,
        1 if m.get("homeScore") is not None and m.get("awayScore") is not None else 0,
        1 if m.get("externalId") else 0,
        1 if m.get("source") == "football-data.org-sync" else 0,
        str(m.get("date", "")),
    )


def dedupe(matches):
    deduped = {}
    removed = []

    for m in matches:
        key = key_for(m)
        if key not in deduped:
            deduped[key] = m
            continue

        current = deduped[key]
        preferred, other = (m, current) if quality(m) >= quality(current) else (current, m)
        removed.append(other)

        merged = dict(other)
        merged.update({k: v for k, v in preferred.items() if v is not None})

        if key[0] == "group_fixture":
            _, group, t1, t2 = key
            merged["id"] = f"{t1}-{t2}-group-{group.lower()}"

        deduped[key] = merged

    cleaned = sorted(
        deduped.values(),
        key=lambda m: (str(m.get("date", "")), str(m.get("group", "")), str(m.get("id", ""))),
    )
    return cleaned, removed


def main():
    matches = json.loads(MATCHES_PATH.read_text(encoding="utf-8"))
    cleaned, removed = dedupe(matches)

    MATCHES_PATH.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Before: {len(matches)} matches")
    print(f"After:  {len(cleaned)} matches")
    print(f"Removed duplicates: {len(removed)}")

    for m in removed:
        print(f"- {m.get('group')} | {m.get('homeTeam')} vs {m.get('awayTeam')} | {m.get('date')} | {m.get('homeScore')}-{m.get('awayScore')}")


if __name__ == "__main__":
    main()
