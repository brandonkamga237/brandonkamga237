"""Generates the GitHub stats and top-languages cards (dark/light) from the GraphQL API.

Usage: GH_TOKEN=... GH_USER=brandonkamga237 python3 scripts/gen_stats.py <out_dir>
"""
import json
import os
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")
USER = os.environ.get("GH_USER", "brandonkamga237")
TOKEN = os.environ["GH_TOKEN"]

# Markup and build files skew the byte counts without saying much about the work.
IGNORED_LANGS = {"HTML", "CSS", "SCSS", "Dockerfile", "Makefile", "MDX", "Batchfile"}

THEMES = {
    "dark": dict(bg="#0d1117", border="#30363d", text="#e6edf3", muted="#8b949e", track="#21262d"),
    "light": dict(bg="#ffffff", border="#d0d7de", text="#1f2328", muted="#59636e", track="#eaeef2"),
}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    pullRequests { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as res:
        body = json.load(res)
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]["user"]


def fmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def card(t, title, inner, height=200):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="495" height="{height}" viewBox="0 0 495 {height}" role="img" aria-label="{escape(title)}">
  <style>text {{ font-family: {SANS}; }}</style>
  <rect x="0.5" y="0.5" width="494" height="{height - 1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
  <text x="28" y="40" font-size="15" font-weight="600" fill="{t["text"]}">{escape(title)}</text>
  {inner}
</svg>
'''


def stats_card(t, user):
    cc = user["contributionsCollection"]
    repos = user["repositories"]
    tiles = [
        (cc["contributionCalendar"]["totalContributions"], "Contributions, 12 mo"),
        (cc["totalCommitContributions"] + cc["restrictedContributionsCount"], "Commits, 12 mo"),
        (user["pullRequests"]["totalCount"], "Pull requests"),
        (sum(r["stargazerCount"] for r in repos["nodes"]), "Stars earned"),
        (repos["totalCount"], "Public repositories"),
        (user["followers"]["totalCount"], "Followers"),
    ]
    inner = []
    for i, (value, label) in enumerate(tiles):
        x = 28 + (i % 3) * 150
        y = 92 + (i // 3) * 62
        inner.append(
            f'<text x="{x}" y="{y}" font-size="28" font-weight="700" fill="{t["text"]}">{fmt(value)}</text>'
            f'<text x="{x}" y="{y + 22}" font-size="12" fill="{t["muted"]}">{escape(label)}</text>')
    return card(t, "GitHub activity", "\n  ".join(inner))


def langs_card(t, user):
    totals, colors = {}, {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name in IGNORED_LANGS:
                continue
            totals[name] = totals.get(name, 0) + edge["size"]
            colors[name] = edge["node"]["color"] or t["muted"]
    top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:6]
    total = sum(size for _, size in top) or 1

    inner = [f'<rect x="28" y="62" width="439" height="8" rx="4" fill="{t["track"]}"/>',
             '<clipPath id="bar"><rect x="28" y="62" width="439" height="8" rx="4"/></clipPath>',
             '<g clip-path="url(#bar)">']
    x = 28.0
    for name, size in top:
        w = 439 * size / total
        inner.append(f'<rect x="{x:.2f}" y="62" width="{w:.2f}" height="8" fill="{colors[name]}"/>')
        x += w
    inner.append("</g>")
    for i, (name, size) in enumerate(top):
        cx = 28 + (i % 2) * 220
        cy = 108 + (i // 2) * 30
        inner.append(
            f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{colors[name]}"/>'
            f'<text x="{cx + 18}" y="{cy}" font-size="13" fill="{t["text"]}">{escape(name)}</text>'
            f'<text x="{cx + 200}" y="{cy}" font-size="13" text-anchor="end" fill="{t["muted"]}">{100 * size / total:.1f}%</text>')
    return card(t, "Most used languages", "\n  ".join(inner))


user = fetch()
OUT.mkdir(parents=True, exist_ok=True)
for name, t in THEMES.items():
    (OUT / f"stats-{name}.svg").write_text(stats_card(t, user), encoding="utf-8")
    (OUT / f"langs-{name}.svg").write_text(langs_card(t, user), encoding="utf-8")
print("ok")
