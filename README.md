# ReRole carousel pipeline

One JSON file per post → branded 1080x1350 JPEG slides → GitHub → posted to @rerole.ai.

```
posts/<date>-<slug>.json        copy: slides, caption, alt text   (write with /ig-carousel)
brand.json                      ReRole colours, font, handle, logo (from rerole.ai)
render.py                       validates the copy, renders out/<slug>/01.jpg ... with headless Chrome
publish.py                      posts a carousel through the Instagram API (dry run by default)
published.json                  what has already been posted, so nothing posts twice
watch_run.py                    waits for the GitHub run after a push and confirms the post
.github/workflows/publish.yml   runs publish.py on GitHub: on push to posts/, a button press or a schedule
```

**What a slide can contain (themes, generative art, 18 infographic types, animation): see [slides/CATALOG.md](slides/CATALOG.md).**

**First-time setup (Meta app, GitHub repo, secrets): see [SETUP.md](SETUP.md).**

## Make a post

```bash
python3 render.py posts/2026-10-14-communication-skills.json
python3 publish.py posts/2026-10-14-communication-skills.json   # dry run, posts nothing
git add posts out && git commit -m "feat: add communication skills carousel" && git push
```

**Pushing a new file in `posts/` to main publishes it.** Only push a post when it is ready.
`python3 watch_run.py --sha $(git rev-parse HEAD) --slug <slug>` waits and confirms it went live.

The easiest way to do all of this is the `/rerole-post` skill in Claude Code: it suggests
4 topics, and a background agent writes, renders, pushes and confirms the one you pick.

`render.py` refuses copy that breaks the carousel rules (6-12 slides, cover ≤ 6 words, bodies ≤ 25 words,
at least half the middle slides visual, ≤ 3 animated) and any slide whose text spills off the page.
Animated slides become 8s looping MP4s; Instagram gets the video, with the still as a fallback.
`python3 creative_brief.py` rolls a random theme, seed, slide count and visual mix for the next post.

## Tests

```bash
python3 -m unittest discover -s tests
```
