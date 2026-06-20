
"""
sync_football_data.py

Optional refresh script for World Cup Drama Lab.

Purpose:
- Pull latest delayed fixtures/scores from football-data.org free tier.
- Update data/matches.json.
- Keep the public app reading from local JSON only.

Setup:
1. Create a free football-data.org account.
2. Set your API token:
   Windows PowerShell:
      $env:FOOTBALL_DATA_API_KEY="your_token_here"

   macOS/Linux:
      export FOOTBALL_DATA_API_KEY="your_token_here"

3. Run from the project root:
      python scripts/sync_football_data.py

Notes:
- Free tier is delayed and rate-limited.
- This script does not run on every page load.
- It does not add xG, lineups, cards, or live event data.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
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


def normalize_name(value: str) -> str:
    return (
        value.lower()
        .replace("&", "and")
        .replace(".", "")
        .replace("-", " ")
        .replace("  ", " ")
        .strip()
    )


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, payload):
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def api_get(path: str):
    token = os.getenv("FOOTBALL_DATA_API_KEY")
    if not token:
        raise RuntimeError(
            "Missing FOOTBALL_DATA_API_KEY. Set it first, then rerun this script."
        )

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


def make_team_lookup(existing_matches):
    # We infer team names from the existing local file. If the external API uses a
    # slightly different name, add an alias below.
    names = set()
    for m in existing_matches:
        names.add(m["homeTeam"])
        names.add(m["awayTeam"])

    aliases = {
        "usa": "usa",
        "united states": "usa",
        "united states of america": "usa",
        "czech republic": "cze",
        "czechia": "cze",
        "korea republic": "kor",
        "south korea": "kor",
        "dr congo": "cod",
        "congo dr": "cod",
        "curacao": "cuw",
        "curaçao": "cuw",
        "ivory coast": "civ",
        "côte d’ivoire": "civ",
        "cote divoire": "civ",
    }
    return aliases


def find_existing_match(existing_matches, home_id, away_id, date_prefix=None):
    # Prefer exact home/away match.
    for idx, m in enumerate(existing_matches):
        if m["homeTeam"] == home_id and m["awayTeam"] == away_id:
            return idx

    # Some APIs may reverse home/away. Match by pair if needed.
    for idx, m in enumerate(existing_matches):
        if {m["homeTeam"], m["awayTeam"]} == {home_id, away_id}:
            if date_prefix is None or str(m.get("date", "")).startswith(date_prefix):
                return idx

    return None


def main():
    existing = load_json(MATCHES_PATH)
    aliases = make_team_lookup(existing)

    print(f"Fetching {DEFAULT_COMPETITION} {DEFAULT_SEASON} matches from football-data.org...")
    payload = api_get(f"/competitions/{DEFAULT_COMPETITION}/matches?season={DEFAULT_SEASON}")

    api_matches = payload.get("matches", [])
    updated_count = 0
    skipped = []

    for item in api_matches:
        home_name = item.get("homeTeam", {}).get("name", "")
        away_name = item.get("awayTeam", {}).get("name", "")

        home_id = aliases.get(normalize_name(home_name))
        away_id = aliases.get(normalize_name(away_name))

        if not home_id or not away_id:
            skipped.append(f"Could not map: {home_name} vs {away_name}")
            continue

        utc_date = item.get("utcDate", "")
        date_prefix = utc_date[:10] if utc_date else None
        idx = find_existing_match(existing, home_id, away_id, date_prefix)

        score = item.get("score", {}).get("fullTime", {})
        home_score = score.get("home")
        away_score = score.get("away")

        status = football_data_status_to_local(item.get("status"))

        if idx is None:
            group = item.get("group") or "TBD"
            match_id = f"{home_id}-{away_id}-{date_prefix or item.get('id', 'match')}"
            existing.append({
                "id": match_id,
                "group": str(group).replace("GROUP_", "").replace("Group ", ""),
                "homeTeam": home_id,
                "awayTeam": away_id,
                "homeScore": home_score,
                "awayScore": away_score,
                "status": status,
                "date": date_prefix or utc_date,
                "events": [],
                "source": "football-data.org-sync"
            })
            updated_count += 1
        else:
            m = existing[idx]
            changed = False

            if status:
                changed = changed or m.get("status") != status
                m["status"] = status

            if date_prefix:
                changed = changed or m.get("date") != date_prefix
                m["date"] = date_prefix

            if home_score is not None:
                changed = changed or m.get("homeScore") != home_score
                m["homeScore"] = home_score

            if away_score is not None:
                changed = changed or m.get("awayScore") != away_score
                m["awayScore"] = away_score

            m["source"] = "football-data.org-sync"

            if changed:
                updated_count += 1

    save_json(MATCHES_PATH, existing)
    save_json(LAST_UPDATED_PATH, {
        "lastSyncedAt": datetime.now(timezone.utc).isoformat(),
        "source": "football-data.org",
        "competition": DEFAULT_COMPETITION,
        "season": DEFAULT_SEASON,
        "matchesReturned": len(api_matches),
        "matchesUpdatedOrAdded": updated_count,
        "skipped": skipped[:25],
        "notes": "Free-tier scores/schedules may be delayed. Public app still reads from local JSON."
    })

    print(f"Done. Updated or added {updated_count} matches.")
    if skipped:
        print("Skipped mappings:")
        for s in skipped[:10]:
            print(f"- {s}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Sync failed: {exc}", file=sys.stderr)
        sys.exit(1)
