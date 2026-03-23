"""Re-process football silhouettes: Canny edges with colored lines on dark fill."""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ASSETS = Path(__file__).resolve().parents[2] / "public" / "assets" / "football"


def canny_silhouette(original: Image.Image) -> Image.Image:
    """Create a colored-edge silhouette: dark filled shape with bright edge lines."""
    arr = np.array(original)
    alpha = arr[:, :, 3]

    # Convert RGB to grayscale for edge detection
    gray = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2GRAY)

    # Canny edge detection
    edges = cv2.Canny(gray, 40, 120)

    # Dilate edges so they're clearly visible
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    # Build output: dark silhouette fill + bright cyan edge lines
    out = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)

    # Dark fill where original has alpha (the body shape)
    body_mask = alpha > 30
    out[body_mask, 0] = 20   # R
    out[body_mask, 1] = 30   # G
    out[body_mask, 2] = 50   # B
    out[body_mask, 3] = 220  # A

    # Bright cyan edges on top
    edge_mask = (edges > 0) & (alpha > 30)
    out[edge_mask, 0] = 100  # R
    out[edge_mask, 1] = 220  # G
    out[edge_mask, 2] = 255  # B
    out[edge_mask, 3] = 255  # A

    return Image.fromarray(out, "RGBA")


def main() -> None:
    originals = sorted(ASSETS.glob("*-original.png"))
    count = 0
    for orig_path in originals:
        slug = orig_path.name.replace("-original.png", "")
        sil_path = ASSETS / f"{slug}-silhouette.png"
        try:
            original = Image.open(orig_path).convert("RGBA")
            sil = canny_silhouette(original)
            sil.save(sil_path)
            print(f"OK: {slug}")
            count += 1
        except Exception as exc:
            print(f"FAILED: {slug}: {exc}")

    print(f"\nDone: {count} silhouettes updated.")


if __name__ == "__main__":
    main()
