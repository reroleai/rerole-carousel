"""Publish a rendered carousel to Instagram through the official Graph API.

Dry run by default: it prints exactly what it would send and posts nothing.
Add --publish to post for real.

Needs, in the environment (never in this file):
  IG_USER_ID        the Instagram professional account id
  IG_ACCESS_TOKEN   a long-lived token with instagram_content_publish
  IMAGE_BASE_URL    public https folder where out/<slug>/01.jpg ... are hosted.
                    May contain {slug}, e.g. https://raw.githubusercontent.com/me/repo/main/out/{slug}
Optional:
  GRAPH_HOST        default graph.facebook.com (graph.instagram.com for Instagram Login tokens)
  GRAPH_VERSION     default v23.0

  python3 publish.py posts/2026-10-14-communication-skills.json
  python3 publish.py posts/2026-10-14-communication-skills.json --publish
  python3 publish.py --next --publish     oldest post not yet in published.json
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POSTS = ROOT / "posts"
LEDGER = ROOT / "published.json"
REQUIRED_ENV = ("IG_USER_ID", "IG_ACCESS_TOKEN", "IMAGE_BASE_URL")
POLL_INTERVAL_S = 3
POLL_ATTEMPTS = 40
HTTP_TIMEOUT_S = 60


def read_config() -> dict:
    missing = [name for name in REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        raise SystemExit(f"Missing environment variables: {', '.join(missing)}")
    base_url = os.environ["IMAGE_BASE_URL"].rstrip("/")
    if not base_url.startswith("https://"):
        raise SystemExit("IMAGE_BASE_URL must be a public https URL. Instagram fetches the images itself.")
    host = os.environ.get("GRAPH_HOST", "graph.facebook.com")
    version = os.environ.get("GRAPH_VERSION", "v23.0")
    return {
        "user_id": os.environ["IG_USER_ID"],
        "token": os.environ["IG_ACCESS_TOKEN"],
        "image_base": base_url,
        "api": f"https://{host}/{version}",
    }


def graph(method: str, url: str, params: dict) -> dict:
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        request = urllib.request.Request(f"{url}?{data.decode()}")
    else:
        request = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_S) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as err:
        detail = err.read().decode(errors="replace")
        raise SystemExit(f"Graph API {err.code} on {url.split('?')[0]}: {detail}") from err
    except urllib.error.URLError as err:
        raise SystemExit(f"Network error calling the Graph API: {err.reason}") from err


def wait_until_ready(config: dict, container_id: str) -> None:
    for _ in range(POLL_ATTEMPTS):
        status = graph("GET", f"{config['api']}/{container_id}",
                       {"fields": "status_code", "access_token": config["token"]})
        code = status.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise SystemExit(f"Container {container_id} failed with status {code}")
        time.sleep(POLL_INTERVAL_S)
    raise SystemExit(f"Container {container_id} was not ready after {POLL_ATTEMPTS * POLL_INTERVAL_S}s")


def image_urls(post: dict, base: str) -> list[str]:
    folder = base.replace("{slug}", post["slug"]).rstrip("/")
    return [f"{folder}/{index:02d}.jpg" for index in range(1, len(post["slides"]) + 1)]


def read_ledger() -> list[dict]:
    if not LEDGER.exists():
        return []
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def record(slug: str, media_id: str) -> None:
    entry = {"slug": slug, "media_id": media_id, "published_at": datetime.now(timezone.utc).isoformat()}
    LEDGER.write_text(json.dumps([*read_ledger(), entry], indent=2) + "\n", encoding="utf-8")


def is_rendered(post: dict) -> bool:
    folder = ROOT / "out" / post["slug"]
    return all((folder / f"{i:02d}.jpg").exists() for i in range(1, len(post["slides"]) + 1))


def next_post_path() -> Path | None:
    """Oldest rendered post (by file name) that is not in the ledger yet."""
    done = {entry["slug"] for entry in read_ledger()}
    for path in sorted(POSTS.glob("*.json")):
        post = json.loads(path.read_text(encoding="utf-8"))
        if post["slug"] not in done and is_rendered(post):
            return path
    return None


def publish(post: dict, config: dict) -> str:
    media_url = f"{config['api']}/{config['user_id']}/media"
    children = []
    for url in image_urls(post, config["image_base"]):
        item = graph("POST", media_url, {
            "image_url": url, "is_carousel_item": "true", "access_token": config["token"],
        })
        wait_until_ready(config, item["id"])
        children.append(item["id"])
        print(f"  uploaded {url.rsplit('/', 1)[-1]}")

    carousel = graph("POST", media_url, {
        "media_type": "CAROUSEL", "children": ",".join(children),
        "caption": post["caption"], "access_token": config["token"],
    })
    wait_until_ready(config, carousel["id"])
    result = graph("POST", f"{config['api']}/{config['user_id']}/media_publish", {
        "creation_id": carousel["id"], "access_token": config["token"],
    })
    return result["id"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("post", type=Path, nargs="?")
    parser.add_argument("--next", action="store_true", help="pick the oldest unpublished post")
    parser.add_argument("--publish", action="store_true", help="actually post. Without it, dry run")
    args = parser.parse_args()

    path = next_post_path() if args.next else args.post
    if path is None:
        if args.next:
            print("Queue is empty: every rendered post is already in published.json.")
            return
        parser.error("give a post file or --next")

    post = json.loads(path.read_text(encoding="utf-8"))
    if not is_rendered(post):
        raise SystemExit(f"Render first: python3 render.py {path}")
    if post["slug"] in {entry["slug"] for entry in read_ledger()}:
        raise SystemExit(f"{post['slug']} is already in published.json. Remove it there to post again.")

    if not args.publish:
        base = os.environ.get("IMAGE_BASE_URL", "<IMAGE_BASE_URL>")
        print(f"DRY RUN for {post['slug']}, nothing will be posted. Add --publish to post.\n")
        print("Images:", *image_urls(post, base), sep="\n  ")
        print(f"\nCaption ({len(post['caption'])} chars):\n{post['caption']}")
        print(f"\nAlt text (add in the app, Advanced settings): {post['alt_text']}")
        return

    config = read_config()
    media_id = publish(post, config)
    record(post["slug"], media_id)
    print(f"Published {post['slug']}. Media id {media_id}")
    print(f"Add alt text in the app if your API version does not set it: {post['alt_text']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
