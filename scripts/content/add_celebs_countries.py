"""Add 10 new celebrities + 4 missing, and 10 new countries."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List

from generate_content import (
    CelebritySeed,
    CountrySeed,
    ASSETS_DIR,
    celebrity_original_from_photo,
    country_original_from_geojson,
    mask_from_alpha,
    silhouette_from_original,
    wikipedia_image_for_title,
    ensure_dirs,
    SIZE,
)

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "src" / "data"

# 4 celebs with images but missing from JSON
EXISTING_MISSING_CELEBS = [
    CelebritySeed("Albert Einstein", "celebrities-albert-einstein", "Albert_Einstein", "https://en.wikipedia.org/wiki/Albert_Einstein", "Public domain", "Wikimedia Commons"),
    CelebritySeed("Charlie Chaplin", "celebrities-charlie-chaplin", "Charlie_Chaplin", "https://en.wikipedia.org/wiki/Charlie_Chaplin", "Public domain", "Wikimedia Commons"),
    CelebritySeed("Mahatma Gandhi", "celebrities-mahatma-gandhi", "Mahatma_Gandhi", "https://en.wikipedia.org/wiki/Mahatma_Gandhi", "Public domain", "Wikimedia Commons"),
    CelebritySeed("Usain Bolt", "celebrities-usain-bolt", "Usain_Bolt", "https://en.wikipedia.org/wiki/Usain_Bolt", "CC BY-SA", "Wikimedia Commons"),
]

# 10 new celebrities
NEW_CELEBS: List[CelebritySeed] = [
    CelebritySeed("Bob Marley", "celebrities-bob-marley", "Bob_Marley", "https://en.wikipedia.org/wiki/Bob_Marley", "CC BY-SA", "Wikimedia Commons"),
    CelebritySeed("Oprah Winfrey", "celebrities-oprah-winfrey", "Oprah_Winfrey", "https://en.wikipedia.org/wiki/Oprah_Winfrey", "CC BY-SA", "Wikimedia Commons"),
    CelebritySeed("David Bowie", "celebrities-david-bowie", "David_Bowie", "https://en.wikipedia.org/wiki/David_Bowie", "CC BY-SA", "Wikimedia Commons"),
    CelebritySeed("Madonna", "celebrities-madonna", "Madonna_(entertainer)", "https://en.wikipedia.org/wiki/Madonna_(entertainer)", "CC BY-SA", "Wikimedia Commons"),
    CelebritySeed("Arnold Schwarzenegger", "celebrities-arnold-schwarzenegger", "Arnold_Schwarzenegger", "https://en.wikipedia.org/wiki/Arnold_Schwarzenegger", "CC BY-SA", "Wikimedia Commons"),
    CelebritySeed("Beyonce", "celebrities-beyonce", "Beyonc%C3%A9", "https://en.wikipedia.org/wiki/Beyonc%C3%A9", "CC BY-SA", "Wikimedia Commons"),
    CelebritySeed("Jackie Chan", "celebrities-jackie-chan", "Jackie_Chan", "https://en.wikipedia.org/wiki/Jackie_Chan", "CC BY-SA", "Wikimedia Commons"),
    CelebritySeed("Clint Eastwood", "celebrities-clint-eastwood", "Clint_Eastwood", "https://en.wikipedia.org/wiki/Clint_Eastwood", "CC BY-SA", "Wikimedia Commons"),
    CelebritySeed("Roger Federer", "celebrities-roger-federer", "Roger_Federer", "https://en.wikipedia.org/wiki/Roger_Federer", "CC BY-SA", "Wikimedia Commons"),
    CelebritySeed("Freddie Mercury", "celebrities-freddie-mercury", "Freddie_Mercury", "https://en.wikipedia.org/wiki/Freddie_Mercury", "CC BY-SA", "Wikimedia Commons"),
]

# 10 new countries
NEW_COUNTRIES: List[CountrySeed] = [
    CountrySeed("Germany", "countries-germany", "DEU"),
    CountrySeed("Russia", "countries-russia", "RUS"),
    CountrySeed("Turkey", "countries-turkey", "TUR"),
    CountrySeed("Thailand", "countries-thailand", "THA"),
    CountrySeed("Greece", "countries-greece", "GRC"),
    CountrySeed("Sweden", "countries-sweden", "SWE"),
    CountrySeed("Colombia", "countries-colombia", "COL"),
    CountrySeed("Indonesia", "countries-indonesia", "IDN"),
    CountrySeed("Nigeria", "countries-nigeria", "NGA"),
    CountrySeed("New Zealand", "countries-new-zealand", "NZL"),
]


def build_options(all_names: List[str], answer: str) -> List[str]:
    distractors = [n for n in all_names if n != answer][:3]
    return [answer, *distractors]


def main() -> None:
    ensure_dirs()

    # --- CELEBRITIES ---
    celebs_path = DATA_DIR / "celebrities.json"
    celebs: list = json.loads(celebs_path.read_text(encoding="utf-8"))
    celeb_ids = {item["id"] for item in celebs}
    celeb_names = [item["answer"] for item in celebs]
    for seed in EXISTING_MISSING_CELEBS + NEW_CELEBS:
        if seed.name not in celeb_names:
            celeb_names.append(seed.name)

    # Add missing ones that already have images
    for seed in EXISTING_MISSING_CELEBS:
        if seed.slug in celeb_ids:
            continue
        print(f"Adding existing celeb: {seed.name}")
        celebs.append({
            "id": seed.slug,
            "category": "celebrities",
            "answer": seed.name,
            "options": build_options(celeb_names, seed.name),
            "silhouetteImage": f"/assets/celebrities/{seed.slug}-silhouette.png",
            "originalImage": f"/assets/celebrities/{seed.slug}-original.png",
            "hintMask": f"/assets/celebrities/{seed.slug}-mask.png",
            "sourceUrl": seed.source_url,
            "license": seed.license_name,
            "author": seed.author,
        })
        celeb_ids.add(seed.slug)

    # Generate new celebs
    celeb_dir = ASSETS_DIR / "celebrities"
    for seed in NEW_CELEBS:
        if seed.slug in celeb_ids:
            print(f"Skipping celeb (exists): {seed.name}")
            continue
        try:
            print(f"Generating celeb: {seed.name}...")
            image_url = wikipedia_image_for_title(seed.page_title)
            original = celebrity_original_from_photo(image_url)
            silhouette = silhouette_from_original(original)
            hint_mask = mask_from_alpha(original, seed.slug)
            original.save(celeb_dir / f"{seed.slug}-original.png")
            silhouette.save(celeb_dir / f"{seed.slug}-silhouette.png")
            hint_mask.save(celeb_dir / f"{seed.slug}-mask.png")
            celebs.append({
                "id": seed.slug,
                "category": "celebrities",
                "answer": seed.name,
                "options": build_options(celeb_names, seed.name),
                "silhouetteImage": f"/assets/celebrities/{seed.slug}-silhouette.png",
                "originalImage": f"/assets/celebrities/{seed.slug}-original.png",
                "hintMask": f"/assets/celebrities/{seed.slug}-mask.png",
                "sourceUrl": seed.source_url,
                "license": seed.license_name,
                "author": seed.author,
            })
            print(f"  Done: {seed.name}")
            time.sleep(0.6)
        except Exception as exc:
            print(f"  FAILED: {seed.name}: {exc}")

    celebs_path.write_text(json.dumps(celebs, indent=2), encoding="utf-8")
    print(f"\nTotal celebrities: {len(celebs)}")

    # --- COUNTRIES ---
    countries_path = DATA_DIR / "countries.json"
    countries: list = json.loads(countries_path.read_text(encoding="utf-8"))
    country_ids = {item["id"] for item in countries}
    country_names = [item["answer"] for item in countries]
    for seed in NEW_COUNTRIES:
        if seed.name not in country_names:
            country_names.append(seed.name)

    country_dir = ASSETS_DIR / "countries"
    for seed in NEW_COUNTRIES:
        if seed.slug in country_ids:
            print(f"Skipping country (exists): {seed.name}")
            continue
        try:
            print(f"Generating country: {seed.name}...")
            original = country_original_from_geojson(seed.iso3)
            silhouette = silhouette_from_original(original)
            hint_mask = mask_from_alpha(original, seed.slug)
            original.save(country_dir / f"{seed.slug}-original.png")
            silhouette.save(country_dir / f"{seed.slug}-silhouette.png")
            hint_mask.save(country_dir / f"{seed.slug}-mask.png")
            countries.append({
                "id": seed.slug,
                "category": "countries",
                "answer": seed.name,
                "options": build_options(country_names, seed.name),
                "silhouetteImage": f"/assets/countries/{seed.slug}-silhouette.png",
                "originalImage": f"/assets/countries/{seed.slug}-original.png",
                "hintMask": f"/assets/countries/{seed.slug}-mask.png",
                "sourceUrl": f"https://raw.githubusercontent.com/johan/world.geo.json/master/countries/{seed.iso3}.geo.json",
                "license": "Open source dataset",
                "author": "johan/world.geo.json contributors",
            })
            print(f"  Done: {seed.name}")
            time.sleep(0.3)
        except Exception as exc:
            print(f"  FAILED: {seed.name}: {exc}")

    countries_path.write_text(json.dumps(countries, indent=2), encoding="utf-8")
    print(f"Total countries: {len(countries)}")


if __name__ == "__main__":
    main()
