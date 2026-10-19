"""Art directions. Every theme stays inside the ReRole palette (navy, sky, emerald) and
type system (Inter, plus JetBrains Mono for code). They differ in surface, texture and mood.

A theme maps each slide role to a surface, and each surface is a set of CSS variables.
"""

THEMES = {
    "midnight": {
        "mood": "dark navy with soft sky/emerald glows; calm and premium",
        "roles": {"cover": "night", "stake": "paper", "content": "paper", "recap": "night", "cta": "gradient"},
        "art": {"night": ["glow", "waves", "rings"], "paper": ["dots", "none"], "gradient": ["waves", "rings"]},
        "headline": "heavy",
    },
    "editorial": {
        "mood": "magazine page: paper, ink, oversized numerals, thin rules",
        "roles": {"cover": "paper", "stake": "ink", "content": "paper", "recap": "paper", "cta": "ink"},
        "art": {"paper": ["dots", "rules", "none"], "ink": ["rings", "glow"]},
        "headline": "tight",
    },
    "blueprint": {
        "mood": "engineering drawing: blue grid, construction lines, mono labels",
        "roles": {"cover": "blue", "stake": "blue", "content": "blue", "recap": "blue", "cta": "gradient"},
        "art": {"blue": ["grid"], "gradient": ["grid", "rings"]},
        "headline": "heavy",
    },
    "terminal": {
        "mood": "hacker console: near-black, emerald phosphor, scanlines, mono type",
        "roles": {"cover": "console", "stake": "console", "content": "console", "recap": "console", "cta": "console"},
        "art": {"console": ["scan", "rain"]},
        "headline": "mono",
    },
    "aurora": {
        "mood": "full-bleed sky-to-emerald gradients with floating white cards",
        "roles": {"cover": "gradient", "stake": "gradient", "content": "card", "recap": "gradient", "cta": "night"},
        "art": {"gradient": ["waves", "rings"], "card": ["glow"], "night": ["glow"]},
        "headline": "heavy",
    },
    "riso": {
        "mood": "risograph print: paper grain, overlapping translucent shapes, bold ink",
        "roles": {"cover": "paper", "stake": "paper", "content": "paper", "recap": "paper", "cta": "gradient"},
        "art": {"paper": ["shapes", "shapes", "dots"], "gradient": ["shapes"]},
        "headline": "tight",
    },
}

DEFAULT_THEME = "midnight"


def surfaces(colors: dict) -> dict:
    c = colors
    return {
        "night": dict(bg=c["navy"], fg="#ffffff", muted="#cbd5e1", accent=c["sky_light"], accent2=c["emerald_light"],
                      panel="rgba(255,255,255,.06)", line="rgba(255,255,255,.14)", card="#ffffff", card_fg=c["navy"],
                      grad=f"linear-gradient(100deg,{c['sky_light']},{c['emerald_light']})"),
        "paper": dict(bg=c["paper"], fg=c["ink"], muted=c["muted"], accent=c["sky"], accent2=c["emerald"],
                      panel="#ffffff", line="#e2e8f0", card=c["navy"], card_fg="#ffffff",
                      grad=f"linear-gradient(100deg,{c['sky']},{c['emerald']})"),
        "ink": dict(bg="#0b1220", fg="#f8fafc", muted="#94a3b8", accent=c["sky_light"], accent2=c["emerald_light"],
                    panel="rgba(255,255,255,.05)", line="rgba(255,255,255,.12)", card="#f8fafc", card_fg=c["ink"],
                    grad=f"linear-gradient(100deg,{c['sky_light']},{c['emerald_light']})"),
        "blue": dict(bg="#0b2a4a", fg="#e0f2fe", muted="#93c5fd", accent=c["sky_light"], accent2=c["emerald_light"],
                     panel="rgba(186,230,253,.07)", line="rgba(186,230,253,.22)", card="#e0f2fe", card_fg="#0b2a4a",
                     grad=f"linear-gradient(100deg,#e0f2fe,{c['sky_light']})"),
        "console": dict(bg="#020617", fg="#d1fae5", muted="#6ee7b7", accent=c["emerald_light"], accent2=c["sky_light"],
                        panel="rgba(52,211,153,.06)", line="rgba(52,211,153,.25)", card="#022c22", card_fg="#d1fae5",
                        grad=f"linear-gradient(100deg,{c['emerald_light']},{c['sky_light']})"),
        "gradient": dict(bg=f"linear-gradient(150deg,{c['sky']} 0%,#0e7490 50%,{c['emerald']} 100%)", fg="#ffffff",
                         muted="rgba(255,255,255,.88)", accent="#ffffff", accent2="#d1fae5",
                         panel="rgba(255,255,255,.14)", line="rgba(255,255,255,.3)", card="#ffffff", card_fg=c["navy"],
                         grad="linear-gradient(100deg,#ffffff,#d1fae5)"),
        "card": dict(bg=f"linear-gradient(160deg,{c['sky']},{c['emerald']})", fg=c["ink"], muted=c["muted"],
                     accent=c["sky"], accent2=c["emerald"], panel=c["paper"], line="#e2e8f0", card=c["navy"],
                     card_fg="#ffffff", grad=f"linear-gradient(100deg,{c['sky']},{c['emerald']})"),
    }


def surface_css(name: str, colors: dict) -> str:
    v = surfaces(colors)[name]
    return (f"--bg:{v['bg']};--fg:{v['fg']};--muted:{v['muted']};--accent:{v['accent']};--accent2:{v['accent2']};"
            f"--panel:{v['panel']};--line:{v['line']};--card:{v['card']};--card-fg:{v['card_fg']};--grad:{v['grad']};")
