"""Checks a post file against the carousel rules before anything renders."""

from pathlib import Path

from slides.theme import THEMES
from slides.visuals import VISUALS, render_visual

ROOT = Path(__file__).resolve().parent
MIN_SLIDES = 6
MAX_SLIDES = 12
MAX_ANIMATED = 3
COVER_MAX_WORDS = 6
HEADLINE_MIN_WORDS = 2
HEADLINE_MAX_WORDS = 8
BODY_MAX_WORDS = 25
CAPTION_MAX_CHARS = 2200
CAPTION_MAX_HASHTAGS = 5
KINDS = {"cover", "stake", "content", "step", "recap", "cta"}
MIDDLE_KINDS = {"stake", "content", "step"}


def _words(text: str) -> int:
    return len(text.split())


def _check_visual(label: str, visual: dict) -> list[str]:
    kind = visual.get("type")
    if kind not in VISUALS:
        return [f"{label}: unknown visual {kind!r}. Use one of: {', '.join(sorted(VISUALS))}"]
    if kind == "image":
        src = ROOT / visual.get("src", "")
        if not str(visual.get("src", "")).startswith("assets/") or not src.is_file():
            return [f"{label}: image src must be an existing file under assets/"]
    try:
        render_visual(visual)
    except (KeyError, TypeError, ValueError, IndexError) as err:
        return [f"{label}: {kind} visual is missing or has a bad field ({err})"]
    return []


def _check_slide(index: int, slide: dict) -> list[str]:
    label = f"slide {index + 1}"
    kind = slide.get("kind")
    if kind not in KINDS:
        return [f"{label}: unknown kind {kind!r}"]

    errors = []
    headline = slide.get("headline", "")
    body = slide.get("body", "")

    if kind == "cover":
        if not headline:
            errors.append(f"{label}: cover needs a headline")
        elif _words(headline) > COVER_MAX_WORDS:
            errors.append(f"{label}: cover is {_words(headline)} words, max {COVER_MAX_WORDS}")
    if kind in ("step", "content") and not HEADLINE_MIN_WORDS <= _words(headline) <= HEADLINE_MAX_WORDS:
        errors.append(
            f"{label}: headline is {_words(headline)} words, want {HEADLINE_MIN_WORDS}-{HEADLINE_MAX_WORDS}"
        )
    if _words(body) > BODY_MAX_WORDS:
        errors.append(f"{label}: body is {_words(body)} words, max {BODY_MAX_WORDS}. Split it")
    if kind == "recap" and not (slide.get("items") or slide.get("visual")):
        errors.append(f"{label}: recap needs items or a visual")
    if slide.get("visual"):
        errors.extend(_check_visual(label, slide["visual"]))
    return errors


def validate_post(post: dict) -> list[str]:
    """Return a list of human-readable problems. Empty means the post is good to render."""
    slides = post.get("slides", [])
    errors = []

    if not MIN_SLIDES <= len(slides) <= MAX_SLIDES:
        errors.append(f"{len(slides)} slides, want {MIN_SLIDES}-{MAX_SLIDES}")
    if slides and slides[0].get("kind") != "cover":
        errors.append("first slide must be the cover")
    if slides and slides[-1].get("kind") != "cta":
        errors.append("last slide must be the CTA")
    if post.get("theme", "midnight") not in THEMES:
        errors.append(f"unknown theme {post.get('theme')!r}. Use one of: {', '.join(THEMES)}")
    animated = sum(1 for s in slides if s.get("animate"))
    if animated > MAX_ANIMATED:
        errors.append(f"{animated} animated slides, max {MAX_ANIMATED}")

    if post.get("theme"):
        middle = [s for s in slides if s.get("kind") in MIDDLE_KINDS]
        with_visual = sum(1 for s in middle if s.get("visual"))
        if middle and with_visual * 2 < len(middle):
            errors.append(f"only {with_visual} of {len(middle)} middle slides have a visual, want at least half")

    for index, slide in enumerate(slides):
        errors.extend(_check_slide(index, slide))

    caption = post.get("caption", "")
    if not caption:
        errors.append("caption is empty")
    if len(caption) > CAPTION_MAX_CHARS:
        errors.append(f"caption is {len(caption)} chars, max {CAPTION_MAX_CHARS}")
    hashtags = [w for w in caption.split() if w.startswith("#")]
    if len(hashtags) > CAPTION_MAX_HASHTAGS:
        errors.append(f"{len(hashtags)} hashtags, max {CAPTION_MAX_HASHTAGS}")
    if not post.get("alt_text"):
        errors.append("alt_text is missing for the cover")
    return errors
