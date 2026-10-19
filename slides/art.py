"""Seeded generative background art. Same seed, same picture, so renders are reproducible.

Every generator returns SVG markup sized 1080x1350 that uses the surface's CSS variables,
so the art follows whichever theme surface it sits on. Elements with class "drift" or
"spin" move when the slide is animated (see motion.py).
"""

import math
import random

W, H = 1080, 1350


def _svg(body: str, defs: str = "") -> str:
    return (f'<svg class="art-svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" '
            f'xmlns="http://www.w3.org/2000/svg"><defs>{defs}</defs>{body}</svg>')


def glow(rng: random.Random) -> str:
    defs = ('<radialGradient id="g1"><stop offset="0" stop-color="var(--accent)" stop-opacity=".34"/>'
            '<stop offset="1" stop-color="var(--accent)" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="g2"><stop offset="0" stop-color="var(--accent2)" stop-opacity=".26"/>'
            '<stop offset="1" stop-color="var(--accent2)" stop-opacity="0"/></radialGradient>')
    body = "".join(
        f'<circle class="drift" style="--i:{i}" cx="{rng.randint(-100, W + 100)}" cy="{rng.randint(-100, H + 100)}" '
        f'r="{rng.randint(380, 720)}" fill="url(#g{1 + i % 2})"/>'
        for i in range(rng.randint(2, 3)))
    return _svg(body, defs)


def waves(rng: random.Random) -> str:
    """Flowing bands that echo the curves in the ReRole logo."""
    defs = ('<linearGradient id="wv" x1="0" x2="1"><stop offset="0" stop-color="var(--accent)"/>'
            '<stop offset="1" stop-color="var(--accent2)"/></linearGradient>')
    base = rng.randint(int(H * .76), int(H * .88))  # low, so the bands never run through copy
    amp, phase = rng.randint(50, 120), rng.random() * math.tau
    paths = []
    for i in range(rng.randint(5, 9)):
        y = base + i * 26
        points = " ".join(
            f"{x},{y + amp * math.sin(x / 210 + phase + i * .22):.0f}" for x in range(-40, W + 80, 40))
        paths.append(f'<polyline class="drift" style="--i:{i}" points="{points}" fill="none" stroke="url(#wv)" '
                     f'stroke-width="{rng.choice([3, 4, 6])}" stroke-opacity="{.75 - i * .06:.2f}"/>')
    return _svg("".join(paths), defs)


def rings(rng: random.Random) -> str:
    cx, cy = rng.choice([(W + 80, -60), (-80, H + 60), (W + 40, H * .7)])
    body = "".join(
        f'<circle class="spin" style="--i:{i}" cx="{cx}" cy="{cy}" r="{160 + i * 95}" fill="none" '
        f'stroke="var(--accent)" stroke-opacity="{.32 - i * .03:.2f}" stroke-width="2" '
        f'stroke-dasharray="{rng.choice(["0", "8 14", "2 10"])}"/>'
        for i in range(8))
    return _svg(body)


def dots(rng: random.Random) -> str:
    step = rng.choice([36, 44, 54])
    fx, fy = rng.randint(0, W), rng.randint(0, H)
    out = []
    for x in range(step // 2, W, step):
        for y in range(step // 2, H, step):
            fade = 1 - min(1, math.hypot(x - fx, y - fy) / 900)
            if fade > .05:
                out.append(f'<circle cx="{x}" cy="{y}" r="3" fill="var(--accent)" opacity="{fade * .45:.2f}"/>')
    return _svg("".join(out))


def rules(rng: random.Random) -> str:
    y = rng.randint(80, 140)
    lines = [f'<line x1="120" x2="{W - 120}" y1="{y}" y2="{y}" stroke="var(--fg)" stroke-opacity=".5" stroke-width="2"/>',
             f'<line x1="120" x2="{W - 120}" y1="{H - 130}" y2="{H - 130}" stroke="var(--fg)" stroke-opacity=".2"/>']
    return _svg("".join(lines))


def grid(rng: random.Random) -> str:
    minor = "".join(f'<line x1="{x}" x2="{x}" y1="0" y2="{H}"/>' for x in range(0, W, 45))
    minor += "".join(f'<line y1="{y}" y2="{y}" x1="0" x2="{W}"/>' for y in range(0, H, 45))
    major = "".join(f'<line x1="{x}" x2="{x}" y1="0" y2="{H}"/>' for x in range(0, W, 225))
    major += "".join(f'<line y1="{y}" y2="{y}" x1="0" x2="{W}"/>' for y in range(0, H, 225))
    cx, cy, r = rng.randint(650, 1000), rng.randint(150, 1200), rng.randint(140, 300)
    construct = (f'<circle class="spin" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="var(--accent)" '
                 f'stroke-opacity=".55" stroke-width="2" stroke-dasharray="10 10"/>'
                 f'<line x1="{cx - r - 60}" x2="{cx + r + 60}" y1="{cy}" y2="{cy}" stroke="var(--accent)" stroke-opacity=".4"/>'
                 f'<line y1="{cy - r - 60}" y2="{cy + r + 60}" x1="{cx}" x2="{cx}" stroke="var(--accent)" stroke-opacity=".4"/>')
    return _svg(f'<g stroke="var(--fg)" stroke-opacity=".06">{minor}</g>'
                f'<g stroke="var(--fg)" stroke-opacity=".13">{major}</g>{construct}')


def scan(rng: random.Random) -> str:
    lines = "".join(f'<rect y="{y}" width="{W}" height="2" fill="var(--accent)" opacity=".05"/>' for y in range(0, H, 6))
    sweep = (f'<rect class="drift" y="{rng.randint(100, 1100)}" width="{W}" height="140" '
             f'fill="var(--accent)" opacity=".05"/>')
    return _svg(lines + sweep)


def rain(rng: random.Random) -> str:
    cols = []
    for i, x in enumerate(range(30, W, 70)):
        if rng.random() < .45:
            continue
        glyphs = "".join(rng.choice("01{}<>/=;") for _ in range(rng.randint(6, 16)))
        y = rng.randint(-200, 900)
        chars = "".join(f'<tspan x="{x}" dy="44">{g}</tspan>' for g in glyphs)
        cols.append(f'<text class="drift" style="--i:{i % 5}" y="{y}" font-family="JetBrains Mono, monospace" '
                    f'font-size="30" fill="var(--accent)" opacity="{rng.uniform(.08, .22):.2f}">{chars}</text>')
    return _svg("".join(cols))


def shapes(rng: random.Random) -> str:
    """Risograph-style overlapping translucent shapes, plus grain."""
    defs = ('<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="'
            f'{rng.randint(1, 999)}"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .22 0"/></filter>')
    out = []
    for i in range(rng.randint(3, 5)):
        color = rng.choice(["var(--accent)", "var(--accent2)"])
        x, y, s = rng.randint(-150, W), rng.randint(-150, H), rng.randint(180, 420)
        kind = rng.choice(["circle", "rect", "tri"])
        attrs = f'class="drift" style="--i:{i};mix-blend-mode:multiply" fill="{color}" opacity=".16"'
        if kind == "circle":
            out.append(f'<circle {attrs} cx="{x}" cy="{y}" r="{s // 2}"/>')
        elif kind == "rect":
            out.append(f'<rect {attrs} x="{x}" y="{y}" width="{s}" height="{s * .7:.0f}" rx="40" '
                       f'transform="rotate({rng.randint(-25, 25)} {x} {y})"/>')
        else:
            out.append(f'<polygon {attrs} points="{x},{y} {x + s},{y + s // 3} {x + s // 4},{y + s}"/>')
    out.append(f'<rect width="{W}" height="{H}" filter="url(#grain)"/>')
    return _svg("".join(out), defs)


GENERATORS = {"glow": glow, "waves": waves, "rings": rings, "dots": dots, "rules": rules,
              "grid": grid, "scan": scan, "rain": rain, "shapes": shapes}


def art_layer(style: str, seed: int) -> str:
    if style == "none" or style not in GENERATORS:
        return ""
    return GENERATORS[style](random.Random(seed))
