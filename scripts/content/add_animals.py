"""Add 10 new animals + 4 missing ones that already have images."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List

from generate_content import (
    AnimalSeed,
    ASSETS_DIR,
    celebrity_original_from_photo,
    mask_from_alpha,
    silhouette_from_original,
    wikipedia_image_for_title,
    ensure_dirs,
)

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "src" / "data"

# 4 animals that already have images but are missing from JSON
EXISTING_MISSING = [
    AnimalSeed("Lion", "animals-lion", "Lion", "https://en.wikipedia.org/wiki/Lion", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Tiger", "animals-tiger", "Tiger", "https://en.wikipedia.org/wiki/Tiger", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Elephant", "animals-elephant", "Elephant", "https://en.wikipedia.org/wiki/Elephant", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Kangaroo", "animals-kangaroo", "Kangaroo", "https://en.wikipedia.org/wiki/Kangaroo", "CC BY-SA", "Wikimedia Commons"),
]

# 10 new animals to generate
NEW_ANIMALS: List[AnimalSeed] = [
    AnimalSeed("Rhinoceros", "animals-rhinoceros", "Rhinoceros", "https://en.wikipedia.org/wiki/Rhinoceros", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Hippopotamus", "animals-hippopotamus", "Hippopotamus", "https://en.wikipedia.org/wiki/Hippopotamus", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Polar Bear", "animals-polar-bear", "Polar_bear", "https://en.wikipedia.org/wiki/Polar_bear", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Toucan", "animals-toucan", "Toucan", "https://en.wikipedia.org/wiki/Toucan", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Iguana", "animals-iguana", "Iguana", "https://en.wikipedia.org/wiki/Iguana", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Jellyfish", "animals-jellyfish", "Jellyfish", "https://en.wikipedia.org/wiki/Jellyfish", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Hedgehog", "animals-hedgehog", "Hedgehog", "https://en.wikipedia.org/wiki/Hedgehog", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Peacock", "animals-peacock", "Peafowl", "https://en.wikipedia.org/wiki/Peafowl", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Sea Turtle", "animals-sea-turtle", "Sea_turtle", "https://en.wikipedia.org/wiki/Sea_turtle", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Bison", "animals-bison", "Bison", "https://en.wikipedia.org/wiki/Bison", "CC BY-SA", "Wikimedia Commons"),
]


def build_options(all_names: List[str], answer: str) -> List[str]:
    distractors = [n for n in all_names if n != answer][:3]
    return [answer, *distractors]


def main() -> None:
    ensure_dirs()

    # Load existing JSON
    animals_json_path = DATA_DIR / "animals.json"
    existing: list = json.loads(animals_json_path.read_text(encoding="utf-8"))
    existing_ids = {item["id"] for item in existing}

    # Collect all animal names for options
    all_names = [item["answer"] for item in existing]
    for seed in EXISTING_MISSING + NEW_ANIMALS:
        if seed.name not in all_names:
            all_names.append(seed.name)

    # Add the 4 missing ones that already have images
    for seed in EXISTING_MISSING:
        if seed.slug in existing_ids:
            continue
        print(f"Adding existing: {seed.name}")
        existing.append({
            "id": seed.slug,
            "category": "animals",
            "answer": seed.name,
            "options": build_options(all_names, seed.name),
            "silhouetteImage": f"/assets/animals/{seed.slug}-silhouette.png",
            "originalImage": f"/assets/animals/{seed.slug}-original.png",
            "hintMask": f"/assets/animals/{seed.slug}-mask.png",
            "sourceUrl": seed.source_url,
            "license": seed.license_name,
            "author": seed.author,
        })

    # Generate 10 new animals
    category_dir = ASSETS_DIR / "animals"
    for seed in NEW_ANIMALS:
        if seed.slug in existing_ids:
            print(f"Skipping (exists): {seed.name}")
            continue
        try:
            print(f"Generating: {seed.name}...")
            image_url = wikipedia_image_for_title(seed.page_title)
            original = celebrity_original_from_photo(image_url)
            silhouette = silhouette_from_original(original)
            hint_mask = mask_from_alpha(original, seed.slug)
            original.save(category_dir / f"{seed.slug}-original.png")
            silhouette.save(category_dir / f"{seed.slug}-silhouette.png")
            hint_mask.save(category_dir / f"{seed.slug}-mask.png")
            existing.append({
                "id": seed.slug,
                "category": "animals",
                "answer": seed.name,
                "options": build_options(all_names, seed.name),
                "silhouetteImage": f"/assets/animals/{seed.slug}-silhouette.png",
                "originalImage": f"/assets/animals/{seed.slug}-original.png",
                "hintMask": f"/assets/animals/{seed.slug}-mask.png",
                "sourceUrl": seed.source_url,
                "license": seed.license_name,
                "author": seed.author,
            })
            print(f"  Done: {seed.name}")
            time.sleep(0.5)
        except Exception as exc:
            print(f"  FAILED: {seed.name}: {exc}")

    animals_json_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    print(f"\nTotal animals in JSON: {len(existing)}")


if __name__ == "__main__":
    main()
