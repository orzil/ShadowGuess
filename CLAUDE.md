# ShadowGuess

Silhouette guessing game built with Next.js 16 + React 19 + TypeScript (strict mode).

## Quick commands

- `npm run dev` — start dev server
- `npm run build` — production build
- `npm run lint` — ESLint (flat config)
- `npm run content:generate` — regenerate image assets and data JSON via Python script

## Project structure

```
app/
  layout.tsx          — root layout (dark theme, metadata)
  page.tsx            — entry point, renders GameBoard
  globals.css         — minimal global styles (dark radial gradient)
src/
  components/
    GameBoard.tsx     — main game UI (category selection, timer, choices, hint, scoring)
  lib/
    gameEngine.ts     — question picking, shuffling, score/XP calculation (30s rounds)
    progression.ts    — XP/level system, localStorage profile persistence, category unlocks
  types/
    game.ts           — core types: CategoryId, ChoiceQuestion, PlayerProfile, RoundView
  data/
    countries.json    — generated question data for countries
    celebrities.json  — generated question data for celebrities
    animals.json      — generated question data for animals
public/assets/
  countries/          — country silhouettes (from GeoJSON outlines)
  celebrities/        — celebrity silhouettes (Wikipedia photos + rembg)
  animals/            — animal silhouettes (Wikipedia photos + rembg)
scripts/content/
  generate_content.py — Python content pipeline (Pillow, rembg, requests)
  requirements.txt    — Python deps: Pillow, requests, rembg, onnxruntime
docs/                 — content-list.md, validation-report.md
```

## Architecture notes

- Single-page app: everything runs client-side in `GameBoard.tsx`
- No API routes or server-side data fetching
- Player profile (XP, level, unlocks, best score/streak) persisted in `localStorage` under key `shadowguess.profile.v1`
- Path alias: `@/*` maps to `./src/*`
- Three active categories: `countries`, `celebrities`, `animals`
- Two future/locked categories: `landmarks`, `objects` (unlock at levels 2 and 3)
- Each question has 3 image variants: `original`, `silhouette`, `hintMask` (CSS mask-image for partial reveal)
- Content is pre-generated — JSON data files reference static assets in `/public/assets/`

## Game mechanics

- 30 seconds per round, 4 multiple-choice options
- 1 hint per round (reveals part of original image through mask)
- Wrong answer or timeout ends the run
- Score: `(100 + remainingSeconds * 4) * (1 + min(streak, 10) * 0.1)`
- XP: `40 + remainingSeconds * 2`
- Level threshold: `250 + (level - 1) * 150` XP

## Content pipeline

The Python script `scripts/content/generate_content.py` generates all game assets:
- Countries: GeoJSON outlines rendered to PNG via Pillow
- Celebrities/Animals: Wikipedia page images, background removed with `rembg`, normalized to 1024x1024
- Outputs: `{slug}-original.png`, `{slug}-silhouette.png`, `{slug}-mask.png` + JSON data files
- Run: `pip install -r scripts/content/requirements.txt` then `npm run content:generate`

## Conventions

- TypeScript strict mode, no `allowJs`
- Inline styles (no CSS modules or Tailwind)
- ESLint flat config with `eslint-config-next`
- No test framework configured yet
