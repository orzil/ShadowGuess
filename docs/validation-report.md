# ShadowGuess Vertical-Slice Validation

## Automated checks
- `npm run content:generate`: passed
- `npm run lint`: passed (2 non-blocking image optimization warnings in game UI)
- `npm run build`: passed

## Dataset checks (countries + celebrities)
- Every item has:
  - `silhouetteImage`
  - `originalImage`
  - `hintMask`
  - source attribution metadata
- Current count:
  - countries: 2 items
  - celebrities: 2 items

## Gameplay checks
- One hint per round is enforced.
- Wrong answer ends the run.
- Timer reaches 0 and ends the run.
- Correct answers add score and XP.
- Profile persistence is enabled via local storage.

## Expansion gate decision
Vertical slice is functionally complete and ready to expand data volume in the same two categories, then unlock additional categories once silhouette quality is manually reviewed.
