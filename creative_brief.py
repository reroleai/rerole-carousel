"""Roll a random creative brief for the next carousel, so no two posts look alike.

  python3 creative_brief.py            # random
  python3 creative_brief.py --seed 7   # reproducible

Avoids the theme used by the most recent post, picks a slide count, a seed for the
generative art, the visuals the post must feature, and how many slides animate.
"""

import argparse
import json
import random
from pathlib import Path

from slides.theme import THEMES
from slides.visuals import VISUALS

ROOT = Path(__file__).resolve().parent
SLIDE_COUNTS = [6, 7, 8, 8, 9, 9, 10, 10, 11, 12]
FEATURED = 3
WILDCARDS = [
    "Draw one original inline-SVG illustration for a slide (an `svg` visual): a scene, a metaphor or a diagram, not clip art.",
    "Make the stake slide a single giant `stat` or `quote`, no body text.",
    "Give one content slide a different surface from the rest, using the `surface` field, for a visual jolt mid-deck.",
    "Use the `number` layout for every content slide, editorial style.",
    "Use a `decode` slide to translate jargon the audience hears.",
    "End the middle section with a `matrix` or `checklist` the reader can self-score against.",
    "Put a `terminal` or `code` visual on the cover instead of plain text.",
    "If the user has supplied a photo in assets/, build one slide around it with an `image` visual.",
]


def last_theme() -> str | None:
    posts = sorted((ROOT / "posts").glob("*.json"))
    for path in reversed(posts):
        theme = json.loads(path.read_text(encoding="utf-8")).get("theme")
        if theme:
            return theme
    return None


def roll(rng: random.Random) -> dict:
    previous = last_theme()
    themes = [name for name in THEMES if name != previous]
    visual_pool = [name for name in VISUALS if name not in ("image", "svg")]
    return {
        "theme": rng.choice(themes),
        "theme_mood": None,
        "seed": rng.randint(1, 99999),
        "slides": rng.choice(SLIDE_COUNTS),
        "feature_visuals": rng.sample(visual_pool, FEATURED),
        "animated_slides": rng.choice([1, 2, 2, 3]),
        "wildcard": rng.choice(WILDCARDS),
        "avoid_theme": previous,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    brief = roll(random.Random(args.seed))
    brief["theme_mood"] = THEMES[brief["theme"]]["mood"]
    print(json.dumps(brief, indent=2))


if __name__ == "__main__":
    main()
