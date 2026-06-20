"""
sync_football_data.py

Refreshes World Cup Drama Lab's local data from football-data.org.

Key design:
- The Streamlit app never calls the API on page load.
- This script runs on a schedule, updates data/matches.json, and exits.
- GitHub Actions can run this once per hour and commit updated JSON back to the repo.

Environment variables:
- FOOTBALL_DATA_API_KEY: required
- FOOTBALL_DATA_COMPETITION: optional, default WC
- FOOTBALL_DATA_SEASON: optional, default 2026
- SYNC_COOLDOWN_MINUTES: optional, default 10
- FORCE_SYNC: optional, set to "true" to bypass cooldown
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MATCHES_PATH = DATA_DIR / "matches.json"
LAST_UPDATED_PATH = DATA_DIR / "last_updated.json"

API_BASE = "https://api.football-data.org/v4"
DEFAULT_COMPETITION = os.getenv("FOOTBALL_DATA_COMPETITION", "WC")
DEFAULT_SEASON = os.getenv("FOOTBALL_DATA_SEASON", "2026")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_name(value: str | None) -> str:
    """Normalize external API team names safely.

    football-data.org can return null team names for not-yet-known knockout
    placeholders such as TBD. Returning an empty string lets the sync skip those
    rows instead of crashing.
    """
    if value is None:
        return ""

    return (
        str(value)
        .lower()
        .replace("&", "and")
        .replace(".", "")
        .replace("-", " ")
        .replace("’", "")
        .replace("'", "")
        .replace("  ", " ")
        .strip()
    )


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, payload):
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def recently_synced(min_minutes: int) -> bool:
    if os.getenv("FORCE_SYNC", "").lower() == "true":
        return False

    data = load_json(LAST_UPDATED_PATH, default={}) or {}
    last_synced = data.get("lastSyncedAt")
    if not last_synced:
        return False

    try:
        last_dt = datetime.fromisoformat(last_synced.replace("Z", "+00:00"))
    except ValueError:
        return False

    return datetime.now(timezone.utc) - last_dt < timedelta(minutes=min_minutes)


def api_get(path: str):
    token = os.getenv("FOOTBALL_DATA_API_KEY")
    if not token:
        raise RuntimeError("Missing FOOTBALL_DATA_API_KEY environment variable.")

    url = f"{API_BASE}{path}"
    req = Request(url, headers={"X-Auth-Token": token})

    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API error {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error: {exc}") from exc


def football_data_status_to_local(status: str) -> str:
    status = (status or "").upper()
    if status in {"FINISHED", "AWARDED"}:
        return "completed"
    if status in {"IN_PLAY", "PAUSED", "LIVE"}:
        return "live"
    return "scheduled"


def make_team_lookup(teams):
    lookup = {}
    for team in teams:
        tid = team["id"]
        name = team["name"]
        lookup[normalize_name(name)] = tid

    # Add common API/source aliases here as needed.
    lookup.update({
        "usa": "usa",
        "united states": "usa",
        "united states of america": "usa",
        "czech republic": "cze",
        "czechia": "cze",
        "korea republic": "kor",
        "south korea": "kor",
        "bosnia herzegovina": "bih",
        "bosnia and herzegovina": "bih",
        "curacao": "cuw",
        "curaçao": "cuw",
        "ivory coast": "civ",
        "cote divoire": "civ",
        "côte divoire": "civ",
        "dr congo": "cod",
        "congo dr": "cod",
        "democratic republic of the congo": "cod",
        "cape verde": "cpv",
        "saudi arabia": "ksa",
        "new zealand": "nzl",
    })
    return lookup


def find_existing_match(existing_matches, home_id, away_id, api_id=None, date_prefix=None):
    if api_id is not None:
        for idx, m in enumerate(existing_matches):
            if str(m.get("externalId", "")) == str(api_id):
                return idx

    for idx, m in enumerate(existing_matches):
        if m["homeTeam"] == home_id and m["awayTeam"] == away_id:
            if date_prefix is None or str(m.get("date", "")).startswith(date_prefix):
                return idx

    for idx, m in enumerate(existing_matches):
        if {m["homeTeam"], m["awayTeam"]} == {home_id, away_id}:
            if date_prefix is None or str(m.get("date", "")).startswith(date_prefix):
                return idx

    return None


def update_matches_from_api(existing, api_matches, team_lookup):
    updated_count = 0
    added_count = 0
    skipped = []

    for item in api_matches:
        home_name = (item.get("homeTeam") or {}).get("name")
        away_name = (item.get("awayTeam") or {}).get("name")

        if not home_name or not away_name:
            skipped.append(f"Skipped TBD/unassigned fixture: {home_name} vs {away_name}")
            continue

        home_id = team_lookup.get(normalize_name(home_name))
        away_id = team_lookup.get(normalize_name(away_name))

        if not home_id or not away_id:
            skipped.append(f"Could not map team(s): {home_name} vs {away_name}")
            continue

        utc_date = item.get("utcDate", "")
        date_prefix = utc_date[:10] if utc_date else None
        api_id = item.get("id")
        idx = find_existing_match(existing, home_id, away_id, api_id=api_id, date_prefix=date_prefix)

        score = item.get("score", {}).get("fullTime", {}) or {}
        home_score = score.get("home")
        away_score = score.get("away")
        status = football_data_status_to_local(item.get("status"))

        group_raw = item.get("group") or item.get("stage") or "TBD"
        group = str(group_raw).replace("GROUP_", "").replace("Group ", "").replace("GROUP ", "")

        if idx is None:
            match_id = f"{home_id}-{away_id}-{date_prefix or api_id or 'match'}"
            existing.append({
                "id": match_id,
                "externalId": api_id,
                "group": group,
                "homeTeam": home_id,
                "awayTeam": away_id,
                "homeScore": home_score,
                "awayScore": away_score,
                "status": status,
                "date": date_prefix or utc_date,
                "events": [],
                "source": "football-data.org-sync",
            })
            added_count += 1
            continue

        m = existing[idx]
        before = dict(m)

        m["externalId"] = api_id
        m["source"] = "football-data.org-sync"

        if group and group != "TBD":
            m["group"] = group

        if status:
            m["status"] = status

        if date_prefix:
            m["date"] = date_prefix

        if home_score is not None:
            m["homeScore"] = home_score

        if away_score is not None:
            m["awayScore"] = away_score

        if m != before:
            updated_count += 1

    return updated_count, added_count, skipped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Fetch and compare but do not write files.")
    parser.add_argument("--force", action="store_true", help="Bypass cooldown.")
    args = parser.parse_args()

    cooldown = int(os.getenv("SYNC_COOLDOWN_MINUTES", "10"))
    if not args.force and recently_synced(cooldown):
        print(f"Skipped sync: last successful sync was less than {cooldown} minutes ago.")
        return

    teams = load_json(DATA_DIR / "teams.json", default=[])
    existing = load_json(MATCHES_PATH, default=[])
    team_lookup = make_team_lookup(teams)

    print(f"Fetching {DEFAULT_COMPETITION} {DEFAULT_SEASON} matches from football-data.org...")
    payload = api_get(f"/competitions/{DEFAULT_COMPETITION}/matches?season={DEFAULT_SEASON}")
    api_matches = payload.get("matches", [])

    updated_count, added_count, skipped = update_matches_from_api(existing, api_matches, team_lookup)

    summary = {
        "lastSyncedAt": utc_now_iso(),
        "source": "football-data.org",
        "competition": DEFAULT_COMPETITION,
        "season": DEFAULT_SEASON,
        "matchesReturned": len(api_matches),
        "matchesUpdated": updated_count,
        "matchesAdded": added_count,
        "skipped": skipped[:50],
        "notes": "Free-tier scores/schedules may be delayed. Public app reads from local JSON.",
    }

    print(json.dumps(summary, indent=2))

    if args.dry_run:
        print("Dry run complete. No files written.")
        return

    save_json(MATCHES_PATH, existing)
    save_json(LAST_UPDATED_PATH, summary)
    print("Local JSON updated.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Sync failed: {exc}", file=sys.stderr)
        sys.exit(1)
