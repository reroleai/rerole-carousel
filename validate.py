"""Checks a post file against the ig-carousel slide rules before anything renders."""

MIN_SLIDES = 6
MAX_SLIDES = 10
COVER_MAX_WORDS = 6
HEADLINE_MIN_WORDS = 3
HEADLINE_MAX_WORDS = 7
BODY_MAX_WORDS = 25
CAPTION_MAX_CHARS = 2200
CAPTION_MAX_HASHTAGS = 5
KINDS = {"cover", "stake", "step", "recap", "cta"}


def _words(text: str) -> int:
    return len(text.split())


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
    if kind == "step" and not HEADLINE_MIN_WORDS <= _words(headline) <= HEADLINE_MAX_WORDS:
        errors.append(
            f"{label}: headline is {_words(headline)} words, want "
            f"{HEADLINE_MIN_WORDS}-{HEADLINE_MAX_WORDS}"
        )
    if _words(body) > BODY_MAX_WORDS:
        errors.append(f"{label}: body is {_words(body)} words, max {BODY_MAX_WORDS}. Split it")
    if kind == "recap" and not slide.get("items"):
        errors.append(f"{label}: recap needs items")
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
