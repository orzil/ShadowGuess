"""Generate 30 landmark silhouettes."""
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

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "src" / "data"


class LandmarkSeed:
    def __init__(self, name: str, slug: str, page_title: str, source_url: str):
        self.name = name
        self.slug = slug
        self.page_title = page_title
        self.source_url = source_url


LANDMARKS: List[LandmarkSeed] = [
    LandmarkSeed("Eiffel Tower", "landmarks-eiffel-tower", "Eiffel_Tower", "https://en.wikipedia.org/wiki/Eiffel_Tower"),
    LandmarkSeed("Statue of Liberty", "landmarks-statue-of-liberty", "Statue_of_Liberty", "https://en.wikipedia.org/wiki/Statue_of_Liberty"),
    LandmarkSeed("Taj Mahal", "landmarks-taj-mahal", "Taj_Mahal", "https://en.wikipedia.org/wiki/Taj_Mahal"),
    LandmarkSeed("Colosseum", "landmarks-colosseum", "Colosseum", "https://en.wikipedia.org/wiki/Colosseum"),
    LandmarkSeed("Big Ben", "landmarks-big-ben", "Big_Ben", "https://en.wikipedia.org/wiki/Big_Ben"),
    LandmarkSeed("Great Wall of China", "landmarks-great-wall", "Great_Wall_of_China", "https://en.wikipedia.org/wiki/Great_Wall_of_China"),
    LandmarkSeed("Sydney Opera House", "landmarks-sydney-opera", "Sydney_Opera_House", "https://en.wikipedia.org/wiki/Sydney_Opera_House"),
    LandmarkSeed("Christ the Redeemer", "landmarks-christ-redeemer", "Christ_the_Redeemer_(statue)", "https://en.wikipedia.org/wiki/Christ_the_Redeemer_(statue)"),
    LandmarkSeed("Pyramids of Giza", "landmarks-pyramids-giza", "Great_Pyramid_of_Giza", "https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza"),
    LandmarkSeed("Leaning Tower of Pisa", "landmarks-tower-pisa", "Leaning_Tower_of_Pisa", "https://en.wikipedia.org/wiki/Leaning_Tower_of_Pisa"),
    LandmarkSeed("Machu Picchu", "landmarks-machu-picchu", "Machu_Picchu", "https://en.wikipedia.org/wiki/Machu_Picchu"),
    LandmarkSeed("Stonehenge", "landmarks-stonehenge", "Stonehenge", "https://en.wikipedia.org/wiki/Stonehenge"),
    LandmarkSeed("Mount Rushmore", "landmarks-mount-rushmore", "Mount_Rushmore", "https://en.wikipedia.org/wiki/Mount_Rushmore"),
    LandmarkSeed("Golden Gate Bridge", "landmarks-golden-gate", "Golden_Gate_Bridge", "https://en.wikipedia.org/wiki/Golden_Gate_Bridge"),
    LandmarkSeed("Burj Khalifa", "landmarks-burj-khalifa", "Burj_Khalifa", "https://en.wikipedia.org/wiki/Burj_Khalifa"),
    LandmarkSeed("Sagrada Familia", "landmarks-sagrada-familia", "Sagrada_Fam%C3%ADlia", "https://en.wikipedia.org/wiki/Sagrada_Fam%C3%ADlia"),
    LandmarkSeed("Parthenon", "landmarks-parthenon", "Parthenon", "https://en.wikipedia.org/wiki/Parthenon"),
    LandmarkSeed("Angkor Wat", "landmarks-angkor-wat", "Angkor_Wat", "https://en.wikipedia.org/wiki/Angkor_Wat"),
    LandmarkSeed("Tower Bridge", "landmarks-tower-bridge", "Tower_Bridge", "https://en.wikipedia.org/wiki/Tower_Bridge"),
    LandmarkSeed("Arc de Triomphe", "landmarks-arc-triomphe", "Arc_de_Triomphe", "https://en.wikipedia.org/wiki/Arc_de_Triomphe"),
    LandmarkSeed("Hagia Sophia", "landmarks-hagia-sophia", "Hagia_Sophia", "https://en.wikipedia.org/wiki/Hagia_Sophia"),
    LandmarkSeed("Petra", "landmarks-petra", "Petra", "https://en.wikipedia.org/wiki/Petra"),
    LandmarkSeed("Notre-Dame", "landmarks-notre-dame", "Notre-Dame_de_Paris", "https://en.wikipedia.org/wiki/Notre-Dame_de_Paris"),
    LandmarkSeed("Empire State Building", "landmarks-empire-state", "Empire_State_Building", "https://en.wikipedia.org/wiki/Empire_State_Building"),
    LandmarkSeed("Brandenburg Gate", "landmarks-brandenburg-gate", "Brandenburg_Gate", "https://en.wikipedia.org/wiki/Brandenburg_Gate"),
    LandmarkSeed("Chichen Itza", "landmarks-chichen-itza", "Chichen_Itza", "https://en.wikipedia.org/wiki/Chichen_Itza"),
    LandmarkSeed("Sphinx", "landmarks-sphinx", "Great_Sphinx_of_Giza", "https://en.wikipedia.org/wiki/Great_Sphinx_of_Giza"),
    LandmarkSeed("Mount Fuji", "landmarks-mount-fuji", "Mount_Fuji", "https://en.wikipedia.org/wiki/Mount_Fuji"),
    LandmarkSeed("Moai", "landmarks-moai", "Moai", "https://en.wikipedia.org/wiki/Moai"),
    LandmarkSeed("Space Needle", "landmarks-space-needle", "Space_Needle", "https://en.wikipedia.org/wiki/Space_Needle"),
    LandmarkSeed("CN Tower", "landmarks-cn-tower", "CN_Tower", "https://en.wikipedia.org/wiki/CN_Tower"),
    LandmarkSeed("St. Basil's Cathedral", "landmarks-st-basils", "Saint_Basil%27s_Cathedral", "https://en.wikipedia.org/wiki/Saint_Basil%27s_Cathedral"),
    LandmarkSeed("Opera House Vienna", "landmarks-vienna-opera", "Vienna_State_Opera", "https://en.wikipedia.org/wiki/Vienna_State_Opera"),
    LandmarkSeed("Forbidden City", "landmarks-forbidden-city", "Forbidden_City", "https://en.wikipedia.org/wiki/Forbidden_City"),
    LandmarkSeed("Liberty Bell", "landmarks-liberty-bell", "Liberty_Bell", "https://en.wikipedia.org/wiki/Liberty_Bell"),
]


def build_options(all_names: List[str], answer: str) -> List[str]:
    distractors = [n for n in all_names if n != answer][:3]
    return [answer, *distractors]


def main() -> None:
    ensure_dirs()
    (ASSETS_DIR / "landmarks").mkdir(parents=True, exist_ok=True)

    all_names = [s.name for s in LANDMARKS]
    landmarks_out: list = []
    landmark_dir = ASSETS_DIR / "landmarks"

    for seed in LANDMARKS:
        try:
            print(f"Generating: {seed.name}...")
            image_url = wikipedia_image_for_title(seed.page_title)
            original = celebrity_original_from_photo(image_url)
            silhouette = silhouette_from_original(original)
            hint_mask = mask_from_alpha(original, seed.slug)
            original.save(landmark_dir / f"{seed.slug}-original.png")
            silhouette.save(landmark_dir / f"{seed.slug}-silhouette.png")
            hint_mask.save(landmark_dir / f"{seed.slug}-mask.png")
            landmarks_out.append({
                "id": seed.slug,
                "category": "landmarks",
                "answer": seed.name,
                "options": build_options(all_names, seed.name),
                "silhouetteImage": f"/assets/landmarks/{seed.slug}-silhouette.png",
                "originalImage": f"/assets/landmarks/{seed.slug}-original.png",
                "hintMask": f"/assets/landmarks/{seed.slug}-mask.png",
                "sourceUrl": seed.source_url,
                "license": "CC BY-SA",
                "author": "Wikimedia Commons",
            })
            print(f"  Done: {seed.name}")
            time.sleep(0.5)
        except Exception as exc:
            print(f"  FAILED: {seed.name}: {exc}")

    json_path = DATA_DIR / "landmarks.json"
    json_path.write_text(json.dumps(landmarks_out, indent=2), encoding="utf-8")
    print(f"\nTotal landmarks: {len(landmarks_out)}")


if __name__ == "__main__":
    main()
