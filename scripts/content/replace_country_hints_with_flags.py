"""Replace country hint original images with their national flags.

Downloads flags from flagcdn.com, resizes to 1024x1024 canvas,
and overwrites the -original.png for each country.
The silhouette and mask stay unchanged.
"""
from __future__ import annotations

import io
import time
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = ROOT / "public" / "assets" / "countries"
SIZE = (1024, 1024)

# slug -> ISO 3166-1 alpha-2 code
COUNTRY_FLAGS = {
    "countries-japan": "jp",
    "countries-italy": "it",
    "countries-chile": "cl",
    "countries-india": "in",
    "countries-brazil": "br",
    "countries-australia": "au",
    "countries-egypt": "eg",
    "countries-canada": "ca",
    "countries-united-states": "us",
    "countries-mexico": "mx",
    "countries-argentina": "ar",
    "countries-south-africa": "za",
    "countries-united-kingdom": "gb",
    "countries-spain": "es",
    "countries-france": "fr",
    "countries-china": "cn",
    "countries-norway": "no",
    "countries-saudi-arabia": "sa",
    "countries-germany": "de",
    "countries-russia": "ru",
    "countries-turkey": "tr",
    "countries-thailand": "th",
    "countries-greece": "gr",
    "countries-sweden": "se",
    "countries-colombia": "co",
    "countries-indonesia": "id",
    "countries-nigeria": "ng",
    "countries-new-zealand": "nz",
}


def download_flag(iso2: str) -> Image.Image:
    url = f"https://flagcdn.com/w1280/{iso2}.png"
    headers = {"User-Agent": "ShadowGuessContentBot/1.0 (educational game)"}
    resp = requests.get(url, timeout=30, headers=headers)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGBA")


def flag_on_canvas(flag: Image.Image) -> Image.Image:
    """Place the flag centered on a 1024x1024 transparent canvas, scaled to ~900px wide."""
    canvas = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    target_w = 900
    ratio = target_w / flag.width
    new_h = int(flag.height * ratio)
    resized = flag.resize((target_w, new_h), Image.LANCZOS)
    x = (SIZE[0] - target_w) // 2
    y = (SIZE[1] - new_h) // 2
    canvas.paste(resized, (x, y))
    return canvas


def main() -> None:
    success = 0
    for slug, iso2 in COUNTRY_FLAGS.items():
        out_path = ASSETS_DIR / f"{slug}-original.png"
        try:
            print(f"Downloading flag for {slug} ({iso2})...")
            flag = download_flag(iso2)
            img = flag_on_canvas(flag)
            img.save(out_path)
            print(f"  Saved: {out_path.name}")
            success += 1
            time.sleep(0.3)
        except Exception as exc:
            print(f"  FAILED: {slug}: {exc}")

    print(f"\nDone: {success}/{len(COUNTRY_FLAGS)} flags replaced.")


if __name__ == "__main__":
    main()
