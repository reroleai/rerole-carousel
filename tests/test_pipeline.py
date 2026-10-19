import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import publish  # noqa: E402
from templates import render_slide  # noqa: E402
from validate import validate_post  # noqa: E402

POST = json.loads((ROOT / "posts" / "2026-10-14-communication-skills.json").read_text())
BRAND = json.loads((ROOT / "brand.json").read_text())
EXAMPLE = json.loads((ROOT / "examples" / "decode-job-description.json").read_text())


def with_slide(index, **changes):
    post = copy.deepcopy(POST)
    post["slides"][index] = {**post["slides"][index], **changes}
    return post


class ValidateTest(unittest.TestCase):
    def test_shipped_post_passes(self):
        self.assertEqual(validate_post(POST), [])

    def test_rejects_long_cover(self):
        post = with_slide(0, headline="one two three four five six seven")
        self.assertTrue(any("cover is 7 words" in e for e in validate_post(post)))

    def test_rejects_paragraph_body(self):
        post = with_slide(2, body="word " * 26)
        self.assertTrue(any("Split it" in e for e in validate_post(post)))

    def test_rejects_too_few_slides(self):
        post = {**POST, "slides": POST["slides"][:3]}
        self.assertTrue(any("3 slides" in e for e in validate_post(post)))

    def test_requires_cover_first_and_cta_last(self):
        post = {**POST, "slides": list(reversed(POST["slides"]))}
        errors = validate_post(post)
        self.assertIn("first slide must be the cover", errors)
        self.assertIn("last slide must be the CTA", errors)

    def test_rejects_too_many_hashtags(self):
        post = {**POST, "caption": POST["caption"] + " #a #b #c"}
        self.assertTrue(any("6 hashtags" in e for e in validate_post(post)))

    def test_does_not_mutate_input(self):
        before = copy.deepcopy(POST)
        validate_post(POST)
        self.assertEqual(POST, before)


class VisualPostTest(unittest.TestCase):
    def test_example_post_passes(self):
        self.assertEqual(validate_post(EXAMPLE), [])

    def test_rejects_unknown_visual(self):
        post = copy.deepcopy(EXAMPLE)
        post["slides"][2]["visual"] = {"type": "hologram"}
        self.assertTrue(any("unknown visual" in e for e in validate_post(post)))

    def test_rejects_visual_missing_fields(self):
        post = copy.deepcopy(EXAMPLE)
        post["slides"][2]["visual"] = {"type": "bars"}
        self.assertTrue(any("bars visual" in e for e in validate_post(post)))

    def test_rejects_unsafe_svg(self):
        post = copy.deepcopy(EXAMPLE)
        post["slides"][2]["visual"] = {"type": "svg", "markup": "<svg><script>alert(1)</script></svg>"}
        self.assertTrue(any("svg visual" in e for e in validate_post(post)))

    def test_rejects_image_outside_assets(self):
        post = copy.deepcopy(EXAMPLE)
        post["slides"][2]["visual"] = {"type": "image", "src": "/etc/hosts"}
        self.assertTrue(any("under assets/" in e for e in validate_post(post)))

    def test_limits_animated_slides(self):
        post = copy.deepcopy(EXAMPLE)
        for slide in post["slides"]:
            slide["animate"] = True
        self.assertTrue(any("animated slides" in e for e in validate_post(post)))

    def test_requires_visuals_on_half_the_middle(self):
        post = copy.deepcopy(EXAMPLE)
        for slide in post["slides"][1:-2]:
            slide.pop("visual", None)
        self.assertTrue(any("middle slides have a visual" in e for e in validate_post(post)))

    def test_allows_twelve_slides(self):
        post = copy.deepcopy(EXAMPLE)
        extra = copy.deepcopy(post["slides"][4])
        post["slides"][-2:-2] = [extra, extra, extra]
        self.assertEqual(len(post["slides"]), 12)
        self.assertEqual(validate_post(post), [])

    def test_same_seed_same_render(self):
        slide = EXAMPLE["slides"][2]
        first = render_slide(slide, BRAND, 3, 9, 2, "riso", 7)
        self.assertEqual(first, render_slide(slide, BRAND, 3, 9, 2, "riso", 7))
        self.assertNotEqual(first, render_slide(slide, BRAND, 3, 9, 2, "riso", 8))

    def test_frames_stack_one_section_per_time(self):
        html = render_slide(EXAMPLE["slides"][0], BRAND, 1, 9, 0, "terminal", 1, times=[0, .5, 1])
        self.assertEqual(html.count('<section class="slide'), 3)
        self.assertIn("--t:0.500", html)

    def test_long_word_shrinks_headline(self):
        from slides.compose import _headline_size
        self.assertLess(_headline_size("PARAMETERISATION", "content", "stack"),
                        _headline_size("SAY IT", "content", "stack"))


class TemplateTest(unittest.TestCase):
    def test_escapes_copy(self):
        slide = {"kind": "step", "headline": "<script>x</script> here now", "body": "a & b"}
        html = render_slide(slide, BRAND, 3, 9, 1)
        self.assertNotIn("<script>x", html)
        self.assertIn("a &amp; b", html)

    def test_every_slide_has_handle_and_position(self):
        total = len(POST["slides"])
        for position, slide in enumerate(POST["slides"], start=1):
            html = render_slide(slide, BRAND, position, total, 1)
            self.assertIn(BRAND["handle"], html)
            self.assertIn(f"{position}/{total}", html)


class PublishTest(unittest.TestCase):
    def test_image_urls_are_numbered(self):
        urls = publish.image_urls(POST, "https://cdn.example.com/p")
        self.assertEqual(urls[0], "https://cdn.example.com/p/01.jpg")
        self.assertEqual(len(urls), len(POST["slides"]))

    def test_image_urls_fill_in_slug(self):
        urls = publish.image_urls(POST, "https://raw.example.com/repo/out/{slug}")
        self.assertEqual(urls[0], "https://raw.example.com/repo/out/communication-skills/01.jpg")

    def test_queue_skips_published_and_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "published.json"
            with mock.patch.object(publish, "LEDGER", ledger), \
                    mock.patch.object(publish, "is_rendered", return_value=True):
                first = publish.next_post_path()
                self.assertIsNotNone(first)
                slug = json.loads(first.read_text())["slug"]
                publish.record(slug, "123")
                self.assertEqual(publish.read_ledger()[0]["media_id"], "123")
                self.assertNotEqual(publish.next_post_path(), first)

    def test_video_base_switches_raw_to_jsdelivr(self):
        base = "https://raw.githubusercontent.com/me/repo/abc123/out/{slug}"
        self.assertEqual(publish.video_base(base), "https://cdn.jsdelivr.net/gh/me/repo@abc123/out/{slug}")
        self.assertEqual(publish.video_base("https://cdn.example.com/x"), "https://cdn.example.com/x")

    def test_media_items_use_video_only_when_rendered(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "out" / POST["slug"]
            folder.mkdir(parents=True)
            (folder / "02.mp4").write_bytes(b"x")
            with mock.patch.object(publish, "ROOT", Path(tmp)):
                items = publish.media_items(POST, "https://i.example/{slug}", "https://v.example/{slug}")
        self.assertIsNone(items[0]["video"])
        self.assertEqual(items[1]["video"], f"https://v.example/{POST['slug']}/02.mp4")
        self.assertEqual(items[1]["image"], f"https://i.example/{POST['slug']}/02.jpg")

    def test_config_requires_env(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit):
                publish.read_config()

    def test_config_rejects_http_image_host(self):
        env = {"IG_USER_ID": "1", "IG_ACCESS_TOKEN": "t", "IMAGE_BASE_URL": "http://x.com"}
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(SystemExit):
                publish.read_config()


if __name__ == "__main__":
    unittest.main()


class CreativeBriefTest(unittest.TestCase):
    def test_brief_is_in_range_and_avoids_last_theme(self):
        import random
        import creative_brief
        from slides.visuals import VISUALS
        with mock.patch.object(creative_brief, "last_theme", return_value="blueprint"):
            for seed in range(40):
                brief = creative_brief.roll(random.Random(seed))
                self.assertNotEqual(brief["theme"], "blueprint")
                self.assertTrue(6 <= brief["slides"] <= 12)
                self.assertTrue(1 <= brief["animated_slides"] <= 3)
                self.assertTrue(set(brief["feature_visuals"]) <= set(VISUALS))
