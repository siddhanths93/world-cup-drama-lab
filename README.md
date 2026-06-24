# World Cup Drama Lab — Phase 1 Polished Final

Phase 1 cleanup version focused on the match-led flow:

**Team/group search → group match board → selected story → Why It Matters → Scenario Lab**

## What changed

- Expanded the app canvas for a wider dashboard layout.
- Removed the left sidebar / Quick Desk entirely.
- Added a compact Tournament Snapshot card in the header.
- Removed top KPI boxes like Matches Played / Worth Your Time / Flow.
- Replaced Streamlit tabs with app navigation buttons so CTA buttons can move the user between views.
- Match board now shows one selected group only.
- Group composition is informational only.
- Match cards are light editorial cards, not black buttons.
- Match cards use two lines: score/fixture + story sentence.
- Removed Result/Upcoming prefixes.
- Removed bottom Tournament Snapshot expander.
- Made the current group table always visible under the selected story.
- Fixed status labels to a trimmed set: Safe, In Control, Bubble Watch, Needs Help, Eliminated.
- Renamed scenario language from Current Status/Projected Fate to Current Position/Scenario Outcome.
- Fixed the Tell Your Friend card to show the actual one-sentence summary.

## Run locally

```cmd
py -m streamlit run app.py
```

## Notes

No player photos, official crests, FIFA artwork, betting odds, paid data, xG, or event-level claims.
