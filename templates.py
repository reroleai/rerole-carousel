"""HTML for each slide kind. Every slide is a standalone 1080x1350 page."""

from html import escape

STEP_LABELS = ("01", "02", "03", "04", "05", "06", "07", "08")


def _css(brand: dict) -> str:
    c = brand["colors"]
    font = brand["font"]
    return f"""
:root {{
  --navy: {c['navy']}; --ink: {c['ink']}; --muted: {c['muted']}; --paper: {c['paper']};
  --sky: {c['sky']}; --sky-light: {c['sky_light']};
  --emerald: {c['emerald']}; --emerald-light: {c['emerald_light']};
  --brand-gradient: linear-gradient(100deg, var(--sky-light) 0%, var(--emerald-light) 100%);
  --brand-gradient-deep: linear-gradient(100deg, var(--sky) 0%, var(--emerald) 100%);
  --safe: 120px;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1350px; overflow: hidden; }}
body {{
  font-family: '{font}', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased; letter-spacing: -0.02em;
}}
.slide {{ position: relative; width: 1080px; height: 1350px; padding: var(--safe);
  display: flex; flex-direction: column; overflow: hidden; }}
.dark {{ background: var(--navy); color: #fff; }}
.light {{ background: var(--paper); color: var(--ink); }}
.glow::before {{ content: ''; position: absolute; width: 1100px; height: 1100px; right: -520px; top: -380px;
  border-radius: 50%; background: radial-gradient(circle, rgba(56,189,248,.28), rgba(52,211,153,.10) 45%, transparent 70%); }}
.glow::after {{ content: ''; position: absolute; width: 900px; height: 900px; left: -480px; bottom: -520px;
  border-radius: 50%; background: radial-gradient(circle, rgba(52,211,153,.22), transparent 65%); }}
.brand {{ position: relative; z-index: 1; display: flex; align-items: center; gap: 18px; font-weight: 700; font-size: 34px; }}
.brand img {{ width: 64px; height: 64px; border-radius: 50%; }}
.foot {{ position: absolute; left: var(--safe); right: var(--safe); bottom: 64px; z-index: 1;
  display: flex; justify-content: space-between; font-size: 32px; font-weight: 600; opacity: .72; }}
.grad {{ background: var(--brand-gradient); -webkit-background-clip: text; background-clip: text; color: transparent; }}
.light .grad {{ background-image: var(--brand-gradient-deep); }}
.content {{ position: relative; z-index: 1; flex: 1; display: flex; flex-direction: column; justify-content: center; }}
h1 {{ font-size: 150px; line-height: .92; font-weight: 900; letter-spacing: -0.025em; }}
h2 {{ font-size: 92px; line-height: 1; font-weight: 800; letter-spacing: -0.015em; }}
.sub {{ font-size: 46px; line-height: 1.3; font-weight: 500; margin-top: 56px; max-width: 780px; color: #cbd5e1; }}
.body {{ font-size: 46px; line-height: 1.35; font-weight: 500; margin-top: 52px; color: var(--muted); }}
.num {{ font-size: 220px; line-height: 1; font-weight: 900; letter-spacing: -0.035em; margin-bottom: 40px; }}
.bar {{ width: 140px; height: 14px; border-radius: 7px; background: var(--brand-gradient-deep); margin-bottom: 64px; }}
.stake {{ font-size: 86px; line-height: 1.1; font-weight: 800; letter-spacing: -0.035em; }}
.swipe {{ position: absolute; right: var(--safe); bottom: 150px; z-index: 1; font-size: 34px; font-weight: 700;
  padding: 22px 36px; border-radius: 999px; border: 3px solid rgba(255,255,255,.35); }}
.recap {{ list-style: none; margin-top: 64px; }}
.recap li {{ display: flex; align-items: center; gap: 36px; font-size: 52px; font-weight: 700;
  padding: 30px 0; border-bottom: 2px solid rgba(255,255,255,.12); }}
.recap li span {{ flex: none; width: 86px; height: 86px; border-radius: 22px; background: var(--brand-gradient-deep);
  display: grid; place-items: center; font-size: 40px; font-weight: 900; color: #fff; }}
.cta {{ background: linear-gradient(150deg, var(--sky) 0%, #0e7490 50%, var(--emerald) 100%); color: #fff; }}
.cta .sub {{ color: rgba(255,255,255,.9); }}
.bookmark {{ width: 132px; height: 168px; margin-bottom: 72px; }}
.site {{ margin-top: 72px; font-size: 40px; font-weight: 800; display: inline-block;
  padding: 24px 44px; border-radius: 999px; background: #fff; color: var(--navy); align-self: flex-start; }}
"""


def _gradient_last_word(text: str) -> str:
    """Put the brand gradient on the final word, the way the site does on its h1."""
    head, _, last = text.rpartition(" ")
    if not head:
        return f'<span class="grad">{escape(text)}</span>'
    return f'{escape(head)} <span class="grad">{escape(last)}</span>'


def _brand_mark(brand: dict) -> str:
    return f'<div class="brand"><img src="{escape(brand["logo"])}" alt="">{escape(brand["name"])}</div>'


def _footer(brand: dict, position: int, total: int) -> str:
    return f'<div class="foot"><span>{escape(brand["handle"])}</span><span>{position}/{total}</span></div>'


def _cover(slide: dict, brand: dict) -> tuple[str, str]:
    inner = f"""{_brand_mark(brand)}
<div class="content"><h1>{_gradient_last_word(slide['headline'])}</h1>
<p class="sub">{escape(slide.get('body', ''))}</p></div>
<div class="swipe">Swipe &rarr;</div>"""
    return "dark glow", inner


def _stake(slide: dict, brand: dict) -> tuple[str, str]:
    inner = f'<div class="content"><div class="bar"></div><p class="stake">{escape(slide["body"])}</p></div>'
    return "light", inner


def _step(slide: dict, brand: dict, step_number: int) -> tuple[str, str]:
    label = STEP_LABELS[step_number - 1] if step_number <= len(STEP_LABELS) else str(step_number)
    inner = f"""<div class="content"><div class="num grad">{label}</div>
<h2>{escape(slide['headline'])}</h2><p class="body">{escape(slide['body'])}</p></div>"""
    return "light", inner


def _recap(slide: dict, brand: dict) -> tuple[str, str]:
    items = "".join(
        f"<li><span>{i}</span>{escape(item)}</li>" for i, item in enumerate(slide["items"], start=1)
    )
    inner = f"""<div class="content"><h2>{_gradient_last_word(slide['headline'])}</h2>
<ul class="recap">{items}</ul></div>"""
    return "dark glow", inner


def _cta(slide: dict, brand: dict) -> tuple[str, str]:
    bookmark = (
        '<svg class="bookmark" viewBox="0 0 22 28" fill="none" stroke="#fff" stroke-width="2.4" '
        'stroke-linejoin="round"><path d="M2 3a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v23l-9-6-9 6z"/></svg>'
    )
    inner = f"""{_brand_mark(brand)}
<div class="content">{bookmark}<h1>{escape(slide['headline'])}</h1>
<p class="sub">{escape(slide.get('body', ''))}</p>
<span class="site">{escape(brand['site'])}</span></div>"""
    return "cta", inner


def render_slide(slide: dict, brand: dict, position: int, total: int, step_number: int) -> str:
    """Return a full HTML document for one slide. position is 1-based."""
    kind = slide["kind"]
    if kind == "step":
        classes, inner = _step(slide, brand, step_number)
    else:
        builder = {"cover": _cover, "stake": _stake, "recap": _recap, "cta": _cta}[kind]
        classes, inner = builder(slide, brand)

    font_query = brand["font"].replace(" ", "+")
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family={font_query}:wght@500;600;700;800;900&display=block" rel="stylesheet">
<style>{_css(brand)}</style></head>
<body><section class="slide {classes}">{inner}{_footer(brand, position, total)}</section></body></html>"""
