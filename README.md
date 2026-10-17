# ReRole carousel pipeline

One JSON file per post → branded 1080x1350 JPEG slides → GitHub → posted to @rerole.ai.

```
posts/<date>-<slug>.json        copy: slides, caption, alt text   (write with /ig-carousel)
brand.json                      ReRole colours, font, handle, logo (from rerole.ai)
render.py                       validates the copy, renders out/<slug>/01.jpg ... with headless Chrome
publish.py                      posts a carousel through the Instagram API (dry run by default)
published.json                  what has already been posted, so nothing posts twice
.github/workflows/publish.yml   runs publish.py on GitHub, on a button press or a schedule
```

**First-time setup (Meta app, GitHub repo, secrets): see [SETUP.md](SETUP.md).**

## Make a post

```bash
python3 render.py posts/2026-10-14-communication-skills.json
python3 publish.py posts/2026-10-14-communication-skills.json   # dry run, posts nothing
git add posts out && git commit -m "feat: add communication skills carousel" && git push
```

GitHub then posts it, either when you press **Run workflow** or at the next scheduled time.

`render.py` refuses copy that breaks the carousel rules: 6-10 slides, cover ≤ 6 words,
slide bodies ≤ 25 words, ≤ 5 hashtags, and alt text present.

## Tests

```bash
python3 -m unittest discover -s tests
```
