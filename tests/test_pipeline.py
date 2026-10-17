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
