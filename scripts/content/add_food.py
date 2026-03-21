"""Generate 30 food silhouettes."""
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


class FoodSeed:
    def __init__(self, name: str, slug: str, page_title: str):
        self.name = name
        self.slug = slug
        self.page_title = page_title


FOODS: List[FoodSeed] = [
    FoodSeed("Pizza", "food-pizza", "Pizza"),
    FoodSeed("Hamburger", "food-hamburger", "Hamburger"),
    FoodSeed("Sushi", "food-sushi", "Sushi"),
    FoodSeed("Croissant", "food-croissant", "Croissant"),
    FoodSeed("Taco", "food-taco", "Taco"),
    FoodSeed("Hot Dog", "food-hot-dog", "Hot_dog"),
    FoodSeed("Pretzel", "food-pretzel", "Pretzel"),
    FoodSeed("Donut", "food-donut", "Doughnut"),
    FoodSeed("Banana", "food-banana", "Banana"),
    FoodSeed("Apple", "food-apple", "Apple"),
    FoodSeed("Pineapple", "food-pineapple", "Pineapple"),
    FoodSeed("Watermelon", "food-watermelon", "Watermelon"),
    FoodSeed("Strawberry", "food-strawberry", "Strawberry"),
    FoodSeed("Grapes", "food-grapes", "Grape"),
    FoodSeed("Avocado", "food-avocado", "Avocado"),
    FoodSeed("Broccoli", "food-broccoli", "Broccoli"),
    FoodSeed("Carrot", "food-carrot", "Carrot"),
    FoodSeed("Corn", "food-corn", "Corn"),
    FoodSeed("Mushroom", "food-mushroom", "Mushroom"),
    FoodSeed("Onion", "food-onion", "Onion"),
    FoodSeed("Tomato", "food-tomato", "Tomato"),
    FoodSeed("Eggplant", "food-eggplant", "Eggplant"),
    FoodSeed("Lemon", "food-lemon", "Lemon"),
    FoodSeed("Orange", "food-orange", "Orange_(fruit)"),
    FoodSeed("Cherry", "food-cherry", "Cherry"),
    FoodSeed("Coconut", "food-coconut", "Coconut"),
    FoodSeed("Ice Cream", "food-ice-cream", "Ice_cream"),
    FoodSeed("Cupcake", "food-cupcake", "Cupcake"),
    FoodSeed("Popcorn", "food-popcorn", "Popcorn"),
    FoodSeed("Bread", "food-bread", "Bread"),
    FoodSeed("Cheese", "food-cheese", "Cheese"),
    FoodSeed("Waffle", "food-waffle", "Waffle"),
    FoodSeed("Pancake", "food-pancake", "Pancake"),
    FoodSeed("Mango", "food-mango", "Mango"),
    FoodSeed("Peach", "food-peach", "Peach"),
    FoodSeed("Pear", "food-pear", "Pear"),
    FoodSeed("Pomegranate", "food-pomegranate", "Pomegranate"),
    FoodSeed("Kiwi", "food-kiwi", "Kiwifruit"),
    FoodSeed("Garlic", "food-garlic", "Garlic"),
    FoodSeed("Pepper", "food-pepper", "Bell_pepper"),
]


def build_options(all_names: List[str], answer: str) -> List[str]:
    distractors = [n for n in all_names if n != answer][:3]
    return [answer, *distractors]


def main() -> None:
    ensure_dirs()
    food_dir = ASSETS_DIR / "food"
    food_dir.mkdir(parents=True, exist_ok=True)

    all_names = [s.name for s in FOODS]
    food_out: list = []

    for seed in FOODS:
        if len(food_out) >= 30:
            break
        try:
            print(f"Generating: {seed.name}...")
            image_url = wikipedia_image_for_title(seed.page_title)
            original = celebrity_original_from_photo(image_url)
            silhouette = silhouette_from_original(original)
            hint_mask = mask_from_alpha(original, seed.slug)
            original.save(food_dir / f"{seed.slug}-original.png")
            silhouette.save(food_dir / f"{seed.slug}-silhouette.png")
            hint_mask.save(food_dir / f"{seed.slug}-mask.png")
            food_out.append({
                "id": seed.slug,
                "category": "food",
                "answer": seed.name,
                "options": build_options(all_names, seed.name),
                "silhouetteImage": f"/assets/food/{seed.slug}-silhouette.png",
                "originalImage": f"/assets/food/{seed.slug}-original.png",
                "hintMask": f"/assets/food/{seed.slug}-mask.png",
                "sourceUrl": f"https://en.wikipedia.org/wiki/{seed.page_title}",
                "license": "CC BY-SA",
                "author": "Wikimedia Commons",
            })
            print(f"  Done: {seed.name} ({len(food_out)} total)")
            time.sleep(0.4)
        except Exception as exc:
            print(f"  FAILED: {seed.name}: {exc}")

    json_path = DATA_DIR / "food.json"
    json_path.write_text(json.dumps(food_out, indent=2), encoding="utf-8")
    print(f"\nTotal food items: {len(food_out)}")


if __name__ == "__main__":
    main()
