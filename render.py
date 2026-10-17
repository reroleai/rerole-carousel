"""Render a carousel post file to 1080x1350 JPEGs with headless Chrome.

  python3 render.py posts/2026-10-14-communication-skills.json
  python3 render.py posts/2026-10-14-communication-skills.json --html-only
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from templates import render_slide
from validate import validate_post

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
WIDTH, HEIGHT = 1080, 1350
FONT_WAIT_MS = 4000
CHROME_TIMEOUT_S = 60
JPEG_QUALITY = 92
CHROME_CANDIDATES = (
    os.environ.get("CHROME_PATH", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
)


def find_chrome() -> str:
    for candidate in CHROME_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    raise SystemExit("Chrome not found. Install it or set CHROME_PATH.")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise SystemExit(f"Could not read {path}: {err}") from err


def write_html(post: dict, brand: dict, html_dir: Path) -> list[Path]:
    html_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / brand["logo"], html_dir / Path(brand["logo"]).name)

    slides = post["slides"]
    pages = []
    step_number = 0
    for position, slide in enumerate(slides, start=1):
        if slide["kind"] == "step":
            step_number += 1
        page = html_dir / f"{position:02d}.html"
        page.write_text(render_slide(slide, brand, position, len(slides), step_number), encoding="utf-8")
        pages.append(page)
    return pages


def screenshot(chrome: str, page: Path, png: Path) -> None:
    cmd = [
        chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", f"--window-size={WIDTH},{HEIGHT}",
        f"--virtual-time-budget={FONT_WAIT_MS}", f"--screenshot={png}", page.as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=CHROME_TIMEOUT_S)
    if result.returncode != 0 or not png.exists():
        raise SystemExit(f"Chrome failed on {page.name}:\n{result.stderr[-800:]}")


def to_jpeg(png: Path) -> Path:
    """The Instagram publishing API only accepts JPEG, so convert and drop the PNG."""
    jpg = png.with_suffix(".jpg")
    if shutil.which("sips"):
        cmd = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(JPEG_QUALITY), str(png), "--out", str(jpg)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=CHROME_TIMEOUT_S)
        if result.returncode != 0:
            raise SystemExit(f"JPEG conversion failed on {png.name}:\n{result.stderr[-800:]}")
    else:
        try:
            from PIL import Image
        except ImportError as err:
            raise SystemExit("Need sips (macOS) or Pillow (pip install pillow) to write JPEGs.") from err
        with Image.open(png) as image:
            image.convert("RGB").save(jpg, "JPEG", quality=JPEG_QUALITY)
    png.unlink()
    return jpg


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("post", type=Path)
    parser.add_argument("--brand", type=Path, default=ROOT / "brand.json")
    parser.add_argument("--html-only", action="store_true", help="write the HTML, skip the images")
    args = parser.parse_args()

    brand = load_json(args.brand)
    post = load_json(args.post)
    problems = validate_post(post)
    if problems:
        print("Post failed validation:", *problems, sep="\n  - ", file=sys.stderr)
        raise SystemExit(1)

    post_dir = OUT / post["slug"]
    pages = write_html(post, brand, post_dir / "html")
    (post_dir / "caption.txt").write_text(post["caption"], encoding="utf-8")
    (post_dir / "alt_text.txt").write_text(post["alt_text"], encoding="utf-8")

    if args.html_only:
        print(f"HTML written to {post_dir / 'html'}")
        return

    chrome = find_chrome()
    for page in pages:
        png = post_dir / f"{page.stem}.png"
        screenshot(chrome, page, png)
        jpg = to_jpeg(png)
        print(f"  {jpg.relative_to(ROOT)}")
    print(f"{len(pages)} slides rendered to {post_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
