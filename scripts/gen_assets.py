"""Generates the static profile SVGs (header and toolbox, dark/light x en/fr) into assets/.

Usage: python3 scripts/gen_assets.py [out_dir]
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": dict(bg="#0d1117", panel="#161b22", border="#30363d", text="#e6edf3",
                 muted="#8b949e", dot="#484f58", grid="#161b22", chip="#161b22"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", border="#d0d7de", text="#1f2328",
                  muted="#59636e", dot="#d0d7de", grid="#f3f4f6", chip="#f6f8fa"),
}

COPY = {
    "en": dict(
        eyebrow="SOFTWARE ENGINEER  ·  YAOUNDÉ, CAMEROON",
        role="Backend, Platform &amp; DevOps",
        tag=["I design and ship production systems end to end,",
             "from the domain model to the infrastructure."],
        term=[("whoami", "brandon: builds systems that ship"),
              ("focus --now", "distributed backends · platforms · infra"),
              ("stack --core", "java · spring · go · typescript · postgres")],
        toolbox="Toolbox",
        groups=["Languages", "Backend", "Frontend", "Data", "Platform", "Practices"],
    ),
    "fr": dict(
        eyebrow="INGÉNIEUR LOGICIEL  ·  YAOUNDÉ, CAMEROUN",
        role="Backend, Plateforme &amp; DevOps",
        tag=["Je conçois et livre des systèmes en production,",
             "du modèle métier jusqu'à l'infrastructure."],
        term=[("whoami", "brandon : des systèmes qui tournent en prod"),
              ("focus --now", "backends distribués · plateformes · infra"),
              ("stack --core", "java · spring · go · typescript · postgres")],
        toolbox="Boîte à outils",
        groups=["Langages", "Backend", "Frontend", "Données", "Plateforme", "Pratiques"],
    ),
}

TOOLBOX = [
    ["Java", "Go", "TypeScript", "JavaScript", "Python", "SQL"],
    ["Spring Boot", "FastAPI", "JPA / Hibernate", "Flyway", "JobRunr", "Keycloak"],
    ["React", "Next.js", "Vite", "Tailwind CSS", "TanStack Query", "next-intl"],
    ["PostgreSQL", "MinIO / S3"],
    ["Docker", "Docker Compose", "Linux", "GitHub Actions", "Playwright"],
    ["Hexagonal architecture", "DDD", "REST", "OAuth2 / JWT", "i18n"],
]

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

# Terminal typing animation, in seconds.
CHAR_W = 9.05
TYPE_SPEED = 0.07
START = 0.5
OUTPUT_PAUSE = 0.25
NEXT_PAUSE = 0.55


def header(t, c):
    lines, keyframes = [], []
    y, clock = 110, START
    for i, (cmd, out) in enumerate(c["term"]):
        typing = len(cmd) * TYPE_SPEED
        lines.append(
            f'<text x="712" y="{y}" class="mono fade" style="animation-delay:{clock:.2f}s">'
            f'<tspan fill="{t["muted"]}">$</tspan><tspan dx="10" fill="{t["text"]}">{escape(cmd)}</tspan></text>')
        # A panel-coloured cover slides right one character at a time to reveal the command.
        keyframes.append(f"@keyframes type{i} {{ to {{ transform: translateX({len(cmd) * CHAR_W:.1f}px); }} }}")
        lines.append(
            f'<rect class="cover" x="730" y="{y - 15}" width="{len(cmd) * CHAR_W + 4:.1f}" height="20" fill="{t["panel"]}" '
            f'style="animation: type{i} {typing:.2f}s steps({len(cmd)}, end) {clock:.2f}s both"/>')
        clock += typing + OUTPUT_PAUSE
        y += 22
        lines.append(
            f'<text x="712" y="{y}" class="mono fade" fill="{t["muted"]}" style="animation-delay:{clock:.2f}s">{escape(out)}</text>')
        clock += NEXT_PAUSE
        y += 30
    lines.append(f'<text x="712" y="{y}" class="mono fade" fill="{t["muted"]}" style="animation-delay:{clock:.2f}s">$</text>')
    lines.append(
        f'<rect class="cursor" x="730" y="{y - 14}" width="9" height="18" fill="{t["text"]}" '
        f'style="animation: appear 0.01s {clock:.2f}s both, blink 1.1s steps(1) {clock:.2f}s infinite"/>')

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
      .fade {{ animation: appear 0.01s both; }}
      @keyframes appear {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
      {" ".join(keyframes)}
      @media (prefers-reduced-motion: reduce) {{
        .fade, .cursor {{ animation: none !important; }}
        .cover {{ display: none; }}
      }}
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
  {"".join(lines)}
</svg>
'''


def toolbox(t, c):
    rows, y = [], 104
    for label, items in zip(c["groups"], TOOLBOX):
        rows.append(f'<text x="48" y="{y + 5}" class="sans" font-size="12" font-weight="600" letter-spacing="1.5" fill="{t["muted"]}">{escape(label.upper())}</text>')
        x = 240
        for item in items:
            w = len(item) * 7.6 + 28
            rows.append(
                f'<rect x="{x}" y="{y - 16}" width="{w:.0f}" height="32" rx="16" fill="{t["chip"]}" stroke="{t["border"]}"/>'
                f'<text x="{x + w / 2:.0f}" y="{y + 5}" text-anchor="middle" class="sans" font-size="14" fill="{t["text"]}">{escape(item)}</text>')
            x += w + 10
        y += 48
    height = y + 8
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-label="{escape(c["toolbox"])}">
  <style>.sans {{ font-family: {SANS}; }}</style>
  <rect x="0.5" y="0.5" width="1199" height="{height - 1}" rx="16" fill="{t["bg"]}" stroke="{t["border"]}"/>
  <text x="48" y="52" class="sans" font-size="18" font-weight="600" fill="{t["text"]}">{escape(c["toolbox"])}</text>
  {"".join(rows)}
</svg>
'''


OUT.mkdir(parents=True, exist_ok=True)
for lang, c in COPY.items():
    for name, t in THEMES.items():
        (OUT / f"header-{lang}-{name}.svg").write_text(header(t, c), encoding="utf-8")
        (OUT / f"toolbox-{lang}-{name}.svg").write_text(toolbox(t, c), encoding="utf-8")
print("ok")
