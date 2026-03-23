"""Generate 30 football player silhouettes with median filter."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List

from generate_content import (
    ASSETS_DIR,
    celebrity_original_from_photo,
    mask_from_alpha,
    silhouette_from_original,
    wikipedia_image_for_title,
    ensure_dirs,
)
from PIL import ImageFilter

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "src" / "data"


class PlayerSeed:
    def __init__(self, name: str, slug: str, page_title: str):
        self.name = name
        self.slug = slug
        self.page_title = page_title


# 25 well-known + 5 lesser-known
PLAYERS: List[PlayerSeed] = [
    # Legends & superstars (25)
    PlayerSeed("Pele", "football-pele", "Pelé"),
    PlayerSeed("Diego Maradona", "football-maradona", "Diego_Maradona"),
    PlayerSeed("Lionel Messi", "football-messi", "Lionel_Messi"),
    PlayerSeed("Cristiano Ronaldo", "football-ronaldo", "Cristiano_Ronaldo"),
    PlayerSeed("Zinedine Zidane", "football-zidane", "Zinedine_Zidane"),
    PlayerSeed("Ronaldinho", "football-ronaldinho", "Ronaldinho"),
    PlayerSeed("David Beckham", "football-beckham", "David_Beckham"),
    PlayerSeed("Thierry Henry", "football-henry", "Thierry_Henry"),
    PlayerSeed("Ronaldo Nazario", "football-ronaldo-nazario", "Ronaldo_(Brazilian_footballer)"),
    PlayerSeed("Neymar", "football-neymar", "Neymar"),
    PlayerSeed("Kylian Mbappe", "football-mbappe", "Kylian_Mbappé"),
    PlayerSeed("Erling Haaland", "football-haaland", "Erling_Haaland"),
    PlayerSeed("Zlatan Ibrahimovic", "football-ibrahimovic", "Zlatan_Ibrahimović"),
    PlayerSeed("Wayne Rooney", "football-rooney", "Wayne_Rooney"),
    PlayerSeed("Steven Gerrard", "football-gerrard", "Steven_Gerrard"),
    PlayerSeed("Franz Beckenbauer", "football-beckenbauer", "Franz_Beckenbauer"),
    PlayerSeed("Johan Cruyff", "football-cruyff", "Johan_Cruyff"),
    PlayerSeed("Michel Platini", "football-platini", "Michel_Platini"),
    PlayerSeed("Marco van Basten", "football-van-basten", "Marco_van_Basten"),
    PlayerSeed("George Best", "football-best", "George_Best"),
    PlayerSeed("Roberto Baggio", "football-baggio", "Roberto_Baggio"),
    PlayerSeed("Andres Iniesta", "football-iniesta", "Andrés_Iniesta"),
    PlayerSeed("Xavi", "football-xavi", "Xavi"),
    PlayerSeed("Gerd Muller", "football-muller", "Gerd_Müller"),
    PlayerSeed("Lev Yashin", "football-yashin", "Lev_Yashin"),
    # Lesser-known (5)
    PlayerSeed("Hristo Stoichkov", "football-stoichkov", "Hristo_Stoichkov"),
    PlayerSeed("Gheorghe Hagi", "football-hagi", "Gheorghe_Hagi"),
    PlayerSeed("Jay-Jay Okocha", "football-okocha", "Jay-Jay_Okocha"),
    PlayerSeed("Davor Suker", "football-suker", "Davor_Šuker"),
    PlayerSeed("Socrates", "football-socrates", "Sócrates"),
    # Extra backup
    PlayerSeed("Paolo Maldini", "football-maldini", "Paolo_Maldini"),
    PlayerSeed("Cafu", "football-cafu", "Cafu"),
    PlayerSeed("Dennis Bergkamp", "football-bergkamp", "Dennis_Bergkamp"),
    PlayerSeed("Didier Drogba", "football-drogba", "Didier_Drogba"),
    PlayerSeed("Samuel Eto'o", "football-etoo", "Samuel_Eto%27o"),
]


def build_options(all_names: List[str], answer: str) -> List[str]:
    distractors = [n for n in all_names if n != answer][:3]
    return [answer, *distractors]


def main() -> None:
    ensure_dirs()
    football_dir = ASSETS_DIR / "football"
    football_dir.mkdir(parents=True, exist_ok=True)

    all_names = [s.name for s in PLAYERS]
    football_out: list = []

    for seed in PLAYERS:
        if len(football_out) >= 30:
            break
        try:
            print(f"Generating: {seed.name}...")
            image_url = wikipedia_image_for_title(seed.page_title)
            # Get original with background removed
            original = celebrity_original_from_photo(image_url)

            # Silhouette = median-filtered version (blurred/abstracted, hard to recognise)
            median = original.copy().filter(ImageFilter.MedianFilter(size=11))
            # Apply a second pass for stronger effect
            median = median.filter(ImageFilter.MedianFilter(size=9))

            # Hint mask for partial reveal
            hint_mask = mask_from_alpha(original, seed.slug)

            # Save: silhouette = median filtered, original = clean (for hint)
            median.save(football_dir / f"{seed.slug}-silhouette.png")
            original.save(football_dir / f"{seed.slug}-original.png")
            hint_mask.save(football_dir / f"{seed.slug}-mask.png")

            football_out.append({
                "id": seed.slug,
                "category": "football",
                "answer": seed.name,
                "options": build_options(all_names, seed.name),
                "silhouetteImage": f"/assets/football/{seed.slug}-silhouette.png",
                "originalImage": f"/assets/football/{seed.slug}-original.png",
                "hintMask": f"/assets/football/{seed.slug}-mask.png",
                "sourceUrl": f"https://en.wikipedia.org/wiki/{seed.page_title}",
                "license": "CC BY-SA",
                "author": "Wikimedia Commons",
            })
            print(f"  Done: {seed.name} ({len(football_out)} total)")
            time.sleep(0.5)
        except Exception as exc:
            print(f"  FAILED: {seed.name}: {exc}")

    json_path = DATA_DIR / "football.json"
    json_path.write_text(json.dumps(football_out, indent=2), encoding="utf-8")
    print(f"\nTotal football players: {len(football_out)}")


if __name__ == "__main__":
    main()
