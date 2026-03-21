from __future__ import annotations

import io
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import requests
from PIL import Image, ImageDraw
from rembg import remove

ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = ROOT / "public" / "assets"
DATA_DIR = ROOT / "src" / "data"
SIZE = (1024, 1024)


@dataclass
class CountrySeed:
    name: str
    slug: str
    iso3: str


@dataclass
class CelebritySeed:
    name: str
    slug: str
    page_title: str
    source_url: str
    license_name: str
    author: str


@dataclass
class AnimalSeed:
    name: str
    slug: str
    page_title: str
    source_url: str
    license_name: str
    author: str


COUNTRY_SEEDS: List[CountrySeed] = [
    CountrySeed("Japan", "countries-japan", "JPN"),
    CountrySeed("Italy", "countries-italy", "ITA"),
    CountrySeed("Chile", "countries-chile", "CHL"),
    CountrySeed("India", "countries-india", "IND"),
    CountrySeed("Brazil", "countries-brazil", "BRA"),
    CountrySeed("Australia", "countries-australia", "AUS"),
    CountrySeed("Egypt", "countries-egypt", "EGY"),
    CountrySeed("Canada", "countries-canada", "CAN"),
    CountrySeed("United States", "countries-united-states", "USA"),
    CountrySeed("Mexico", "countries-mexico", "MEX"),
    CountrySeed("Argentina", "countries-argentina", "ARG"),
    CountrySeed("South Africa", "countries-south-africa", "ZAF"),
    CountrySeed("United Kingdom", "countries-united-kingdom", "GBR"),
    CountrySeed("Spain", "countries-spain", "ESP"),
    CountrySeed("France", "countries-france", "FRA"),
    CountrySeed("China", "countries-china", "CHN"),
    CountrySeed("Norway", "countries-norway", "NOR"),
    CountrySeed("Saudi Arabia", "countries-saudi-arabia", "SAU"),
]

CELEBRITY_SEEDS: List[CelebritySeed] = [
    CelebritySeed(
        "Charlie Chaplin",
        "celebrities-charlie-chaplin",
        "Charlie_Chaplin",
        "https://en.wikipedia.org/wiki/Charlie_Chaplin",
        "Public domain",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Marilyn Monroe",
        "celebrities-marilyn-monroe",
        "Marilyn_Monroe",
        "https://en.wikipedia.org/wiki/Marilyn_Monroe",
        "Public domain",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Michael Jackson",
        "celebrities-michael-jackson",
        "Michael_Jackson",
        "https://en.wikipedia.org/wiki/Michael_Jackson",
        "CC BY-SA 3.0",
        "Zoran Veselinovic",
    ),
    CelebritySeed(
        "Elvis Presley",
        "celebrities-elvis-presley",
        "Elvis_Presley",
        "https://en.wikipedia.org/wiki/Elvis_Presley",
        "Public domain",
        "MGM studio",
    ),
    CelebritySeed(
        "Albert Einstein",
        "celebrities-albert-einstein",
        "Albert_Einstein",
        "https://en.wikipedia.org/wiki/Albert_Einstein",
        "Public domain",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Audrey Hepburn",
        "celebrities-audrey-hepburn",
        "Audrey_Hepburn",
        "https://en.wikipedia.org/wiki/Audrey_Hepburn",
        "Public domain",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Bruce Lee",
        "celebrities-bruce-lee",
        "Bruce_Lee",
        "https://en.wikipedia.org/wiki/Bruce_Lee",
        "Fair use style source",
        "Press photo",
    ),
    CelebritySeed(
        "Frida Kahlo",
        "celebrities-frida-kahlo",
        "Frida_Kahlo",
        "https://en.wikipedia.org/wiki/Frida_Kahlo",
        "Public domain",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Muhammad Ali",
        "celebrities-muhammad-ali",
        "Muhammad_Ali",
        "https://en.wikipedia.org/wiki/Muhammad_Ali",
        "Public domain",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Princess Diana",
        "celebrities-princess-diana",
        "Diana,_Princess_of_Wales",
        "https://en.wikipedia.org/wiki/Diana,_Princess_of_Wales",
        "Public domain",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Nelson Mandela",
        "celebrities-nelson-mandela",
        "Nelson_Mandela",
        "https://en.wikipedia.org/wiki/Nelson_Mandela",
        "Public domain",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Mahatma Gandhi",
        "celebrities-mahatma-gandhi",
        "Mahatma_Gandhi",
        "https://en.wikipedia.org/wiki/Mahatma_Gandhi",
        "Public domain",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Usain Bolt",
        "celebrities-usain-bolt",
        "Usain_Bolt",
        "https://en.wikipedia.org/wiki/Usain_Bolt",
        "CC BY-SA",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Cristiano Ronaldo",
        "celebrities-cristiano-ronaldo",
        "Cristiano_Ronaldo",
        "https://en.wikipedia.org/wiki/Cristiano_Ronaldo",
        "CC BY-SA",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Lionel Messi",
        "celebrities-lionel-messi",
        "Lionel_Messi",
        "https://en.wikipedia.org/wiki/Lionel_Messi",
        "CC BY-SA",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Serena Williams",
        "celebrities-serena-williams",
        "Serena_Williams",
        "https://en.wikipedia.org/wiki/Serena_Williams",
        "CC BY-SA",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Taylor Swift",
        "celebrities-taylor-swift",
        "Taylor_Swift",
        "https://en.wikipedia.org/wiki/Taylor_Swift",
        "CC BY-SA",
        "Wikimedia Commons",
    ),
    CelebritySeed(
        "Dwayne Johnson",
        "celebrities-dwayne-johnson",
        "Dwayne_Johnson",
        "https://en.wikipedia.org/wiki/Dwayne_Johnson",
        "CC BY-SA",
        "Wikimedia Commons",
    ),
]

ANIMAL_SEEDS: List[AnimalSeed] = [
    AnimalSeed("Lion", "animals-lion", "Lion", "https://en.wikipedia.org/wiki/Lion", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Tiger", "animals-tiger", "Tiger", "https://en.wikipedia.org/wiki/Tiger", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Elephant", "animals-elephant", "Elephant", "https://en.wikipedia.org/wiki/Elephant", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Giraffe", "animals-giraffe", "Giraffe", "https://en.wikipedia.org/wiki/Giraffe", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Zebra", "animals-zebra", "Zebra", "https://en.wikipedia.org/wiki/Zebra", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Panda", "animals-panda", "Giant_panda", "https://en.wikipedia.org/wiki/Giant_panda", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Kangaroo", "animals-kangaroo", "Kangaroo", "https://en.wikipedia.org/wiki/Kangaroo", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Penguin", "animals-penguin", "Penguin", "https://en.wikipedia.org/wiki/Penguin", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Dolphin", "animals-dolphin", "Dolphin", "https://en.wikipedia.org/wiki/Dolphin", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Shark", "animals-shark", "Shark", "https://en.wikipedia.org/wiki/Shark", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Eagle", "animals-eagle", "Eagle", "https://en.wikipedia.org/wiki/Eagle", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Owl", "animals-owl", "Owl", "https://en.wikipedia.org/wiki/Owl", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Wolf", "animals-wolf", "Wolf", "https://en.wikipedia.org/wiki/Wolf", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Fox", "animals-fox", "Fox", "https://en.wikipedia.org/wiki/Fox", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Bear", "animals-bear", "Bear", "https://en.wikipedia.org/wiki/Bear", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Rabbit", "animals-rabbit", "Rabbit", "https://en.wikipedia.org/wiki/Rabbit", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Horse", "animals-horse", "Horse", "https://en.wikipedia.org/wiki/Horse", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Cat", "animals-cat", "Cat", "https://en.wikipedia.org/wiki/Cat", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Dog", "animals-dog", "Dog", "https://en.wikipedia.org/wiki/Dog", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Koala", "animals-koala", "Koala", "https://en.wikipedia.org/wiki/Koala", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Cheetah", "animals-cheetah", "Cheetah", "https://en.wikipedia.org/wiki/Cheetah", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Leopard", "animals-leopard", "Leopard", "https://en.wikipedia.org/wiki/Leopard", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Camel", "animals-camel", "Camel", "https://en.wikipedia.org/wiki/Camel", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Deer", "animals-deer", "Deer", "https://en.wikipedia.org/wiki/Deer", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Monkey", "animals-monkey", "Monkey", "https://en.wikipedia.org/wiki/Monkey", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Gorilla", "animals-gorilla", "Gorilla", "https://en.wikipedia.org/wiki/Gorilla", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Crocodile", "animals-crocodile", "Crocodile", "https://en.wikipedia.org/wiki/Crocodile", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Octopus", "animals-octopus", "Octopus", "https://en.wikipedia.org/wiki/Octopus", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Parrot", "animals-parrot", "Parrot", "https://en.wikipedia.org/wiki/Parrot", "CC BY-SA", "Wikimedia Commons"),
    AnimalSeed("Flamingo", "animals-flamingo", "Flamingo", "https://en.wikipedia.org/wiki/Flamingo", "CC BY-SA", "Wikimedia Commons"),
]


def ensure_dirs() -> None:
    for category in ("countries", "celebrities", "animals"):
        (ASSETS_DIR / category).mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_image(url: str) -> Image.Image:
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            response = requests.get(
                url,
                timeout=45,
                headers={"User-Agent": "ShadowGuessContentBot/1.0 (educational game dataset builder)"},
            )
            if response.status_code in (429, 503):
                time.sleep(2 + attempt * 1.5)
                continue
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content)).convert("RGBA")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(1 + attempt)
    if last_error:
        raise last_error
    raise RuntimeError(f"Failed to download image from {url}")


def normalize_canvas(img: Image.Image) -> Image.Image:
    canvas = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    src = img.copy()
    src.thumbnail((920, 920))
    x = (SIZE[0] - src.width) // 2
    y = (SIZE[1] - src.height) // 2
    canvas.alpha_composite(src, (x, y))
    return canvas


def country_original_from_geojson(iso3: str) -> Image.Image:
    url = f"https://raw.githubusercontent.com/johan/world.geo.json/master/countries/{iso3}.geo.json"
    response = requests.get(url, timeout=45)
    response.raise_for_status()
    geo = response.json()

    rings: List[List[Tuple[float, float]]] = []
    for feature in geo["features"]:
        geom = feature["geometry"]
        if geom["type"] == "Polygon":
            rings.extend(geom["coordinates"])
        elif geom["type"] == "MultiPolygon":
            for poly in geom["coordinates"]:
                rings.extend(poly)

    all_pts = [(pt[0], pt[1]) for ring in rings for pt in ring]
    min_x = min(p[0] for p in all_pts)
    max_x = max(p[0] for p in all_pts)
    min_y = min(p[1] for p in all_pts)
    max_y = max(p[1] for p in all_pts)
    width = max(max_x - min_x, 1e-6)
    height = max(max_y - min_y, 1e-6)
    scale = min(820 / width, 820 / height)
    pad_x, pad_y = 102, 102

    img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for ring in rings:
        mapped = [
            (pad_x + (lon - min_x) * scale, pad_y + (max_y - lat) * scale)
            for lon, lat in ring
        ]
        if len(mapped) >= 3:
            draw.polygon(mapped, fill=(220, 220, 220, 255))
    return img


def celebrity_original_from_photo(url: str) -> Image.Image:
    raw = download_image(url)
    # rembg creates alpha foreground from real photo
    fg = remove(raw)
    return normalize_canvas(fg)


def wikipedia_image_for_title(page_title: str) -> str:
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": page_title,
        "prop": "pageimages",
        "piprop": "original",
        "format": "json",
    }
    response = requests.get(api_url, params=params, timeout=45, headers={"User-Agent": "ShadowGuessContentBot/1.0"})
    response.raise_for_status()
    pages = response.json()["query"]["pages"]
    page = next(iter(pages.values()))
    original = page.get("original")
    if not original or "source" not in original:
        raise RuntimeError(f"No page image found for {page_title}")
    return original["source"]


def silhouette_from_original(original: Image.Image) -> Image.Image:
    alpha = original.split()[-1]
    sil = Image.new("RGBA", original.size, (0, 0, 0, 255))
    sil.putalpha(alpha)
    return sil


def mask_from_alpha(original: Image.Image, unique_key: str) -> Image.Image:
    alpha = original.split()[-1]
    bbox = alpha.getbbox()
    mask = Image.new("L", original.size, 0)
    if bbox is None:
        return mask
    x1, y1, x2, y2 = bbox
    key = sum(ord(ch) for ch in unique_key)
    w = x2 - x1
    h = y2 - y1
    # Spread hint centers so masks are not duplicated across items.
    offset_x = int(((key % 7) - 3) * max(18, w * 0.05))
    offset_y = int((((key // 7) % 7) - 3) * max(18, h * 0.05))
    cx = (x1 + x2) // 2 + offset_x
    cy = (y1 + y2) // 2 + offset_y
    rx = max(88, int(w * (0.18 + (key % 5) * 0.03)))
    ry = max(88, int(h * (0.18 + ((key // 5) % 5) * 0.03)))
    draw = ImageDraw.Draw(mask)
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    if key % 2 == 0:
        cx2 = min(x2, max(x1, cx + int(w * 0.16)))
        cy2 = min(y2, max(y1, cy - int(h * 0.14)))
        draw.ellipse((cx2 - rx // 2, cy2 - ry // 2, cx2 + rx // 2, cy2 + ry // 2), fill=255)
    return mask


def build_options(pool: List[str], answer: str) -> List[str]:
    distractors = [name for name in pool if name != answer][:3]
    return [answer, *distractors]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    countries_out = []
    celebs_out = []
    animals_out = []

    country_names = [c.name for c in COUNTRY_SEEDS]
    celeb_names = [c.name for c in CELEBRITY_SEEDS]
    animal_names = [a.name for a in ANIMAL_SEEDS]

    for seed in COUNTRY_SEEDS:
        original = country_original_from_geojson(seed.iso3)
        silhouette = silhouette_from_original(original)
        hint_mask = mask_from_alpha(original, seed.slug)
        category_dir = ASSETS_DIR / "countries"
        original.save(category_dir / f"{seed.slug}-original.png")
        silhouette.save(category_dir / f"{seed.slug}-silhouette.png")
        hint_mask.save(category_dir / f"{seed.slug}-mask.png")
        countries_out.append(
            {
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
            }
        )

    for seed in CELEBRITY_SEEDS:
        try:
            image_url = wikipedia_image_for_title(seed.page_title)
            original = celebrity_original_from_photo(image_url)
            silhouette = silhouette_from_original(original)
            hint_mask = mask_from_alpha(original, seed.slug)
            category_dir = ASSETS_DIR / "celebrities"
            original.save(category_dir / f"{seed.slug}-original.png")
            silhouette.save(category_dir / f"{seed.slug}-silhouette.png")
            hint_mask.save(category_dir / f"{seed.slug}-mask.png")
            celebs_out.append(
                {
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
                }
            )
            time.sleep(0.6)
        except Exception as exc:  # noqa: BLE001
            print(f"Skipping celebrity '{seed.name}': {exc}")

    for seed in ANIMAL_SEEDS:
        try:
            image_url = wikipedia_image_for_title(seed.page_title)
            original = celebrity_original_from_photo(image_url)
            silhouette = silhouette_from_original(original)
            hint_mask = mask_from_alpha(original, seed.slug)
            category_dir = ASSETS_DIR / "animals"
            original.save(category_dir / f"{seed.slug}-original.png")
            silhouette.save(category_dir / f"{seed.slug}-silhouette.png")
            hint_mask.save(category_dir / f"{seed.slug}-mask.png")
            animals_out.append(
                {
                    "id": seed.slug,
                    "category": "animals",
                    "answer": seed.name,
                    "options": build_options(animal_names, seed.name),
                    "silhouetteImage": f"/assets/animals/{seed.slug}-silhouette.png",
                    "originalImage": f"/assets/animals/{seed.slug}-original.png",
                    "hintMask": f"/assets/animals/{seed.slug}-mask.png",
                    "sourceUrl": seed.source_url,
                    "license": seed.license_name,
                    "author": seed.author,
                }
            )
            time.sleep(0.35)
        except Exception as exc:  # noqa: BLE001
            print(f"Skipping animal '{seed.name}': {exc}")

    write_json(DATA_DIR / "countries.json", countries_out)
    write_json(DATA_DIR / "celebrities.json", celebs_out)
    write_json(DATA_DIR / "animals.json", animals_out)
    print("Generated real-data countries, celebrities, and animals datasets.")


if __name__ == "__main__":
    main()
