# ShadowGuess (v1 vertical slice)

ShadowGuess is a single-page silhouette guessing game built with Next.js.

Current playable categories:
- countries
- celebrities (full-body set in data contract)

## Game rules
- 30 seconds per round.
- 4 options, 1 correct.
- 1 hint per round.
- Wrong answer or timeout ends the run.

## Score and progression
- Score per correct answer: `base(100) + speed bonus + streak multiplier`.
- XP is awarded per correct answer.
- Levels and unlock placeholders are persisted in local storage.

## Run locally
```bash
npm install
npm run content:generate
npm run dev
```

## Content pipeline
Pipeline script:
- `scripts/content/generate_content.py`

It generates:
- images in `public/assets/<category>/`
- dataset JSON in `src/data/`

Dependencies:
```bash
python -m pip install -r scripts/content/requirements.txt
```

## Validation checklist before adding more categories
- Verify each item has `original`, `silhouette`, and `hintMask`.
- Play each category and ensure:
  - hint only works once per round,
  - timer ends run at 0,
  - wrong choice triggers game over,
  - score/xp update on correct answers.
- Confirm profile persists across refresh.
