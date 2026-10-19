# Slide catalog

What a post file can use. `validate.py` enforces it and `render.py` refuses slides whose
text spills outside the safe area. See `examples/decode-job-description.json` for a full post.

## Post level

```json
{ "slug": "...", "theme": "blueprint", "seed": 4127, "alt_text": "...", "caption": "...",
  "search_terms": ["...", "..."], "slides": [ ... ] }
```

- **6 to 12 slides.** Cover first, CTA last. Pick the count from the content, not a habit.
- **theme**: `midnight` · `editorial` · `blueprint` · `terminal` · `aurora` · `riso` (moods in `slides/theme.py`)
- **seed**: any integer. It picks the generative art and any layout you don't set. Same seed, same pixels.
- At least **half the middle slides need a visual**.
- At most **3 slides with `"animate": true`**. Each becomes an 8s looping video; its still is the fallback.

## Slide

```json
{ "kind": "content", "headline": "FIND THE MUST-HAVES", "body": "optional, max 25 words",
  "kicker": "optional small label", "visual": { "type": "checklist", ... },
  "layout": "optional", "art": "optional", "surface": "optional", "animate": false }
```

| kind | job | headline |
|---|---|---|
| `cover` | the hook | max 6 words, CAPS |
| `stake` | second cover, why it matters | optional |
| `content` | one idea per slide, auto-numbered 01, 02 … | 2–8 words |
| `recap` | the screenshot slide: `items` list or a visual | yes |
| `cta` | one ask | e.g. SAVE THIS |

**layout** (random from the seed if unset): cover `left`/`center`/`poster` · content `stack`/`visual-first`/`number`/`center` · stake and cta `left`/`center`
**art** (random from the theme if unset): `glow` `waves` `rings` `dots` `rules` `grid` `scan` `rain` `shapes` `none`
**surface** overrides the theme for one slide: `night` `paper` `ink` `blue` `console` `gradient` `card`

## Visuals

| type | fields | best for | animates as |
|---|---|---|---|
| `chips` | `items`, `strike` (bool) | buzzwords, tools, myths to cross out | chips rise, strike-through draws |
| `steps` | `items` | ordered process | rows rise one by one |
| `checklist` | `items`, `done` (n ticked) | criteria, prep lists | ticks pop in |
| `stat` | `value`, `prefix`, `suffix`, `label`, `note` | one striking number (illustrative, say so in `note`) | number counts up |
| `bars` | `items`: [[label, value]], `suffix` | comparisons, rankings | bars grow |
| `donut` | `value` 0–100, `label`, `note` | a share or a score | ring fills |
| `compare` | `left`/`right`: {`title`, `lines`}, `stack` | wrong vs right, before vs after | sides rise |
| `code` | `lines`, `highlight` (line indexes) | SQL, Excel formulas, Python, regex | lines type out |
| `terminal` | `lines`: [[tag, text, tone ok/bad/info]] | logs, outputs, ATS scans | lines print, cursor blinks |
| `flow` | `items`: [label] or [[label, icon]] | pipelines, cause → effect | arrows march |
| `timeline` | `items`: [[when, what]] | 30-60-90 plans, interview day | points rise |
| `decode` | `rows`: [[they say, they mean]], `left_title`, `right_title` | jargon, JDs, feedback, offer letters | rows rise |
| `quote` | `text`, `who` | a line worth saying in an interview | text rises |
| `matrix` | `cols`, `rows`, `filled` | coverage grids, skill maps | cells pop |
| `search` | `query`, `results` | "anyone can google it" | query types |
| `icons` | `items`: [[icon, label]], `cols` | 3–6 parallel ideas | cards pop |
| `image` | `src` (file under `assets/`), `caption`, `shape` (`circle`/`tilt`), `alt` | real photos the user supplied | static |
| `svg` | `markup`: inline `<svg>` | original illustration drawn for the post | static |

**Icons:** briefcase bolt bulb calendar chart chat check clock code cross eye link linkedin lock
mail mic money resume rocket search shield star target team user warning

**svg art rules:** plain shapes and text only, `viewBox` around 840 wide, use `var(--accent)`,
`var(--accent2)`, `var(--fg)` and `var(--muted)` for colour so it follows the theme. No
`<script>`, event handlers, `<image>`, `<foreignObject>` or external links (rejected).
