"""Wait for the publish run triggered by a push, then confirm the post is in published.json.

  python3 watch_run.py --sha $(git rev-parse HEAD) --slug salary-negotiation

Uses the public GitHub API, so no login is needed (the repo is public).
Exit code 0 = posted, 1 = run failed or not recorded, 2 = timed out.
"""

import argparse
import base64
import json
import subprocess
import time

POLL_INTERVAL_S = 20
DEFAULT_TIMEOUT_S = 600
HTTP_TIMEOUT_S = 30


def repo_slug() -> str:
    url = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True).stdout
    path = url.strip().removesuffix(".git").split("github.com")[-1].lstrip(":/")
    return path


def get_json(url: str) -> dict:
    # curl rather than urllib: python.org builds on macOS often lack CA certificates.
    cmd = ["curl", "-sS", "--fail", "--max-time", str(HTTP_TIMEOUT_S),
           "-H", "Accept: application/vnd.github+json", url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"GitHub API request failed on {url}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def find_run(repo: str, sha: str) -> dict | None:
    runs = get_json(f"https://api.github.com/repos/{repo}/actions/runs?head_sha={sha}&per_page=5")
    publish_runs = [r for r in runs.get("workflow_runs", []) if r["name"] == "Publish to Instagram"]
    return publish_runs[0] if publish_runs else None


def published_slugs(repo: str) -> list[dict]:
    try:
        data = get_json(f"https://api.github.com/repos/{repo}/contents/published.json?ref=main")
    except SystemExit:
        return []
    return json.loads(base64.b64decode(data["content"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    args = parser.parse_args()

    repo = repo_slug()
    deadline = time.monotonic() + args.timeout
    run = None
    while time.monotonic() < deadline:
        run = find_run(repo, args.sha)
        if run and run["status"] == "completed":
            break
        print(f"waiting: {run['status'] if run else 'run not started yet'}", flush=True)
        time.sleep(POLL_INTERVAL_S)
    else:
        print(f"TIMEOUT after {args.timeout}s. Check https://github.com/{repo}/actions")
        return 2

    print(f"run #{run['run_number']} {run['conclusion']}: {run['html_url']}")
    if run["conclusion"] != "success":
        print("FAILED. Open the run, expand the Publish step and read the error line.")
        return 1

    # The workflow commits published.json right after posting; give it a moment to land.
    for _ in range(6):
        entry = next((e for e in published_slugs(repo) if e["slug"] == args.slug), None)
        if entry:
            print(f"POSTED {args.slug}: media id {entry['media_id']} at {entry['published_at']}")
            return 0
        time.sleep(10)
    print(f"Run succeeded but {args.slug} is not in published.json. It may have posted a different queued post.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
