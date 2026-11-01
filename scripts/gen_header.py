"""Generates the profile header SVGs (dark/light x en/fr) into assets/."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": dict(bg="#0d1117", panel="#161b22", border="#30363d", text="#e6edf3",
                 muted="#8b949e", dot="#484f58", grid="#161b22"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", border="#d0d7de", text="#1f2328",
                  muted="#59636e", dot="#d0d7de", grid="#f3f4f6"),
}

COPY = {
    "en": dict(
        eyebrow="SOFTWARE ENGINEER  ·  YAOUNDÉ, CAMEROON",
        role="Backend, Platform &amp; DevOps",
        tag=["I design and ship production systems end to end,",
             "from the domain model to the infrastructure."],
        term=[("$", "whoami"),
              ("", "brandon: builds systems that ship"),
              ("$", "focus --now"),
              ("", "distributed backends · platforms · infra"),
              ("$", "stack --core"),
              ("", "java · spring · go · typescript · postgres")],
    ),
    "fr": dict(
        eyebrow="INGÉNIEUR LOGICIEL  ·  YAOUNDÉ, CAMEROUN",
        role="Backend, Plateforme &amp; DevOps",
        tag=["Je conçois et livre des systèmes en production,",
             "du modèle métier jusqu'à l'infrastructure."],
        term=[("$", "whoami"),
              ("", "brandon : des systèmes qui tournent en prod"),
              ("$", "focus --now"),
              ("", "backends distribués · plateformes · infra"),
              ("$", "stack --core"),
              ("", "java · spring · go · typescript · postgres")],
    ),
}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"


def render(t, c):
    term_lines = []
    y = 110
    for prompt, text in c["term"]:
        if prompt:
            term_lines.append(
                f'<text x="712" y="{y}" class="mono"><tspan fill="{t["muted"]}">{prompt}</tspan>'
                f'<tspan dx="10" fill="{t["text"]}">{escape(text)}</tspan></text>')
            y += 22
        else:
            term_lines.append(f'<text x="712" y="{y}" class="mono" fill="{t["muted"]}">{escape(text)}</text>')
            y += 30
    term_lines.append(f'<text x="712" y="{y}" class="mono" fill="{t["muted"]}">$</text>')
    cursor_y = y - 14
    tag = "".join(
        f'<text x="64" y="{222 + i * 30}" class="sans" font-size="19" fill="{t["muted"]}">{escape(line)}</text>'
        for i, line in enumerate(c["tag"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="320" viewBox="0 0 1200 320" role="img" aria-label="Brandon Kamga, {c["role"]}">
  <defs>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="{t["grid"]}" stroke-width="1"/>
    </pattern>
    <clipPath id="card"><rect x="0.5" y="0.5" width="1199" height="319" rx="16"/></clipPath>
    <style>
      .sans {{ font-family: {SANS}; }}
      .mono {{ font-family: {MONO}; font-size: 15px; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
      .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    </style>
  </defs>
  <g clip-path="url(#card)">
    <rect width="1200" height="320" fill="{t["bg"]}"/>
    <rect width="1200" height="320" fill="url(#grid)"/>
  </g>
  <rect x="0.5" y="0.5" width="1199" height="319" rx="16" fill="none" stroke="{t["border"]}"/>

  <text x="64" y="84" class="sans" font-size="13" font-weight="600" letter-spacing="2" fill="{t["muted"]}">{escape(c["eyebrow"])}</text>
  <text x="62" y="146" class="sans" font-size="58" font-weight="700" letter-spacing="-1.5" fill="{t["text"]}">Brandon Kamga</text>
  <text x="64" y="184" class="sans" font-size="24" font-weight="500" fill="{t["text"]}">{c["role"]}</text>
  {tag}

  <rect x="680" y="36" width="456" height="248" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>
  <circle cx="704" cy="60" r="5.5" fill="{t["dot"]}"/><circle cx="723" cy="60" r="5.5" fill="{t["dot"]}"/><circle cx="742" cy="60" r="5.5" fill="{t["dot"]}"/>
  <text x="1112" y="65" text-anchor="end" class="mono" font-size="12" fill="{t["muted"]}">~/brandonkamga237</text>
  <line x1="680" y1="80" x2="1136" y2="80" stroke="{t["border"]}"/>
  {"".join(term_lines)}
  <rect class="cursor" x="730" y="{cursor_y}" width="9" height="18" fill="{t["text"]}"/>
</svg>
'''


OUT.mkdir(parents=True, exist_ok=True)
for lang, c in COPY.items():
    for name, t in THEMES.items():
        (OUT / f"header-{lang}-{name}.svg").write_text(render(t, c), encoding="utf-8")
print("ok")
