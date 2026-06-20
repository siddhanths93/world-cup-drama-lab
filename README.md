# World Cup Drama Lab

Matchday Magazine version.

This build fixes the hero rendering, makes tabs more visible, moves tournament pulse/top stories under **What Happened**, removes the realism-check clutter from the simulator, and improves the sidebar group-flow table.

## Main views

1. **What Happened** — tournament pulse, top stories, clickable recap board, detailed match recap.
2. **Explain Soccer** — group/team context explained for complete beginners and American sports fans.
3. **What Could Happen** — compact qualification simulator with survival cards, remaining match predictions, and projected fate.

## Copyright-safe visual approach

This version does **not** use:
- player photos
- team crests
- official FIFA branding
- official tournament artwork
- external visual assets

The design uses only typography, layout, colors, abstract CSS shapes, local data, and generated text.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

If `streamlit` is not recognized:

```bash
python -m streamlit run app.py
```

## Refresh data

The app reads from `data/matches.json`. To refresh completed scores from football-data.org free tier:

```cmd
set FOOTBALL_DATA_API_KEY=your_token_here
python scripts/sync_football_data.py
```

PowerShell:

```powershell
$env:FOOTBALL_DATA_API_KEY="your_token_here"
python scripts/sync_football_data.py
```
## Automated hourly refresh with GitHub Actions

This repo includes:

```text
.github/workflows/sync-worldcup-data.yml
scripts/sync_football_data.py
```

Set a GitHub secret named:

```text
FOOTBALL_DATA_API_KEY
```

Then the workflow runs once per hour and updates:

```text
data/matches.json
data/last_updated.json
```

The Streamlit app still reads from local JSON. Visitors never call football-data.org directly.
