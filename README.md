# World Cup Drama Lab

Cleaned portfolio MVP.

## What changed in this cleanup release

- Fixed project hygiene: ignores `.venv/`, `.venv1/`, `.idea/workspace.xml`, caches, and local secret files.
- Fixed sync identity logic so football-data.org date shifts do not create duplicate matches.
- Added dedupe protection before saving synced match data.
- Simplified the app structure:
  - Compact header instead of large hero.
  - One small app-level pulse strip.
  - **What Happened** now focuses on Recap Board + Detailed Recap.
  - **Explain Soccer** owns Group Chaos.
  - **What Could Happen** owns Survival Card + Simulator.
  - Standings live in the sidebar only.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

If needed on Windows:

```cmd
.venv\Scripts\python.exe -m streamlit run app.py
```

## Sync data locally

```cmd
set FOOTBALL_DATA_API_KEY=your_token_here
.venv\Scripts\python.exe scripts\sync_football_data.py --force
```

## Automated refresh

GitHub Actions runs `.github/workflows/sync-worldcup-data.yml` hourly. It uses the GitHub repository secret:

```text
FOOTBALL_DATA_API_KEY
```

The deployed Streamlit app does not call football-data.org directly. It reads local JSON committed by the workflow.


## If standings show duplicate matches

Run:

```cmd
python scripts\dedupe_local_matches.py
```

Then commit `data/matches.json` and push.
