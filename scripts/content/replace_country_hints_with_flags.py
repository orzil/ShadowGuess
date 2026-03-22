"""Replace country hint original images with flags clipped to the country shape.

For each country:
1. Load the silhouette PNG (has alpha channel defining the country shape)
2. Download the country's flag
3. Resize the flag to cover the country's bounding box
4. Clip the flag to the country shape using the silhouette alpha
5. Save as -original.png

Result: hint reveals flag colors filling the country outline.
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


def flag_clipped_to_shape(flag: Image.Image, silhouette: Image.Image) -> Image.Image:
    """Fill the country shape with the flag image."""
    # Get the country shape from the silhouette alpha channel
    alpha = silhouette.split()[-1]
    bbox = alpha.getbbox()
    if bbox is None:
        return silhouette

    x1, y1, x2, y2 = bbox
    shape_w = x2 - x1
    shape_h = y2 - y1

    # Resize flag to cover the country bounding box (cover, not contain)
    flag_ratio = flag.width / flag.height
    shape_ratio = shape_w / shape_h

    if flag_ratio > shape_ratio:
        # Flag is wider — fit height, crop width
        new_h = shape_h
        new_w = int(new_h * flag_ratio)
    else:
        # Flag is taller — fit width, crop height
        new_w = shape_w
        new_h = int(new_w / flag_ratio)

    resized_flag = flag.resize((new_w, new_h), Image.LANCZOS)

    # Center the flag over the country bounding box
    flag_x = x1 + (shape_w - new_w) // 2
    flag_y = y1 + (shape_h - new_h) // 2

    # Paste the flag onto a full-size canvas
    canvas = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    canvas.paste(resized_flag, (flag_x, flag_y))

    # Apply the country shape as alpha mask — flag only visible inside the country
    canvas.putalpha(alpha)
    return canvas


def main() -> None:
    success = 0
    for slug, iso2 in COUNTRY_FLAGS.items():
        sil_path = ASSETS_DIR / f"{slug}-silhouette.png"
        out_path = ASSETS_DIR / f"{slug}-original.png"
        try:
            print(f"Processing {slug} ({iso2})...")
            silhouette = Image.open(sil_path).convert("RGBA")
            flag = download_flag(iso2)
            result = flag_clipped_to_shape(flag, silhouette)
            result.save(out_path)
            print(f"  OK: {out_path.name}")
            success += 1
            time.sleep(0.3)
        except Exception as exc:
            print(f"  FAILED: {slug}: {exc}")

    print(f"\nDone: {success}/{len(COUNTRY_FLAGS)} flags clipped to country shapes.")


if __name__ == "__main__":
    main()
