"""Generates the GitHub overview and 3D contributions cards (dark/light x en/fr) from the GraphQL API.

Usage: GH_TOKEN=... GH_USER=brandonkamga237 python3 scripts/gen_stats.py <out_dir>
"""
import json
import math
import os
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")
USER = os.environ.get("GH_USER", "brandonkamga237")
TOKEN = os.environ["GH_TOKEN"]

# Markup and build files skew the byte counts without saying much about the work.
IGNORED_LANGS = {"HTML", "CSS", "SCSS", "Dockerfile", "Makefile", "MDX", "Batchfile"}

THEMES = {
    "dark": dict(bg="#0d1117", border="#30363d", text="#e6edf3", muted="#8b949e", track="#21262d",
                 empty="#161b22", levels=["#3d444d", "#6e7681", "#b1bac4", "#f0f6fc"]),
    "light": dict(bg="#ffffff", border="#d0d7de", text="#1f2328", muted="#59636e", track="#eaeef2",
                  empty="#ebedf0", levels=["#afb8c1", "#6e7781", "#424a53", "#1f2328"]),
}

COPY = {
    "en": dict(activity="GitHub activity", langs="Most used languages", contrib="Contributions",
               tiles=["Contributions, 12 mo", "Commits, 12 mo", "Pull requests", "Stars earned",
                      "Public repositories", "Followers"],
               last_year="in the last 12 months", current="Current streak", longest="Longest streak",
               best="Best day", total="All time", days="days", day="day", sep=",",
               months=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]),
    "fr": dict(activity="Activité GitHub", langs="Langages les plus utilisés", contrib="Contributions",
               tiles=["Contributions, 12 mois", "Commits, 12 mois", "Pull requests", "Étoiles reçues",
                      "Dépôts publics", "Abonnés"],
               last_year="sur les 12 derniers mois", current="Série en cours", longest="Plus longue série",
               best="Meilleur jour", total="Depuis le début", days="jours", day="jour", sep="\u202f",
               months=["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]),
}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
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

YEAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""


def graphql(query, **variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": USER, **variables}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as res:
        body = json.load(res)
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]["user"]


def all_days(created_at):
    """Every contribution day since the account was created, oldest first."""
    days = {}
    now = datetime.now(timezone.utc)
    for year in range(created_at.year, now.year + 1):
        start = max(created_at, datetime(year, 1, 1, tzinfo=timezone.utc))
        end = min(now, datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
        data = graphql(YEAR_QUERY, **{"from": start.isoformat(), "to": end.isoformat()})
        for week in data["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in week["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    return sorted(days.items())


def streaks(days):
    longest = run = 0
    for _, count in days:
        run = run + 1 if count else 0
        longest = max(longest, run)
    current = 0
    # Today without a contribution yet does not break the streak.
    tail = days[:-1] if days and days[-1][1] == 0 else days
    for _, count in reversed(tail):
        if not count:
            break
        current += 1
    return current, longest


def fmt(n, c):
    return f"{n:,}".replace(",", c["sep"])


def fmt_date(iso, c):
    d = date.fromisoformat(iso)
    return f"{d.day} {c['months'][d.month - 1]} {d.year}"


def shade(hex_color, factor):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#{:02x}{:02x}{:02x}".format(*(int(v * factor) for v in (r, g, b)))


def frame(t, width, height, label, inner):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
  <style>text {{ font-family: {SANS}; }}</style>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="16" fill="{t["bg"]}" stroke="{t["border"]}"/>
  {inner}
</svg>
'''


def overview_card(t, c, user):
    cc = user["contributionsCollection"]
    repos = user["repositories"]
    values = [
        cc["contributionCalendar"]["totalContributions"],
        cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        user["pullRequests"]["totalCount"],
        sum(r["stargazerCount"] for r in repos["nodes"]),
        repos["totalCount"],
        user["followers"]["totalCount"],
    ]
    inner = [f'<text x="48" y="52" font-size="18" font-weight="600" fill="{t["text"]}">{escape(c["activity"])}</text>']
    for i, (value, label) in enumerate(zip(values, c["tiles"])):
        x = 48 + (i % 3) * 180
        y = 118 + (i // 3) * 82
        inner.append(
            f'<text x="{x}" y="{y}" font-size="36" font-weight="700" letter-spacing="-1" fill="{t["text"]}">{fmt(value, c)}</text>'
            f'<text x="{x}" y="{y + 26}" font-size="13" fill="{t["muted"]}">{escape(label)}</text>')

    inner.append(f'<line x1="620" y1="40" x2="620" y2="240" stroke="{t["border"]}"/>')

    totals, colors = {}, {}
    for repo in repos["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name in IGNORED_LANGS:
                continue
            totals[name] = totals.get(name, 0) + edge["size"]
            colors[name] = edge["node"]["color"] or t["muted"]
    top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:6]
    total = sum(size for _, size in top) or 1

    left, width = 668, 484
    inner += [f'<text x="{left}" y="52" font-size="18" font-weight="600" fill="{t["text"]}">{escape(c["langs"])}</text>',
              f'<rect x="{left}" y="82" width="{width}" height="10" rx="5" fill="{t["track"]}"/>',
              f'<clipPath id="bar"><rect x="{left}" y="82" width="{width}" height="10" rx="5"/></clipPath>',
              '<g clip-path="url(#bar)">']
    x = float(left)
    for name, size in top:
        w = width * size / total
        inner.append(f'<rect x="{x:.2f}" y="82" width="{w:.2f}" height="10" fill="{colors[name]}"/>')
        x += w
    inner.append("</g>")
    for i, (name, size) in enumerate(top):
        cx = left + (i % 2) * 254
        cy = 140 + (i // 2) * 38
        inner.append(
            f'<circle cx="{cx + 6}" cy="{cy - 5}" r="6" fill="{colors[name]}"/>'
            f'<text x="{cx + 22}" y="{cy}" font-size="15" fill="{t["text"]}">{escape(name)}</text>'
            f'<text x="{cx + 226}" y="{cy}" font-size="15" text-anchor="end" fill="{t["muted"]}">{100 * size / total:.1f}%</text>')
    return frame(t, 1200, 280, c["activity"], "\n  ".join(inner))


def contrib_card(t, c, user, history):
    calendar = user["contributionsCollection"]["contributionCalendar"]
    weeks = calendar["weeks"]
    counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
    peak = max(counts) or 1
    nonzero = sorted(n for n in counts if n)

    def level(n):
        if not n:
            return -1
        rank = sum(1 for v in nonzero if v <= n) / len(nonzero)
        return min(3, int(rank * 4 - 1e-9))

    # Isometric grid: weeks run down-right, weekdays run down-left.
    w, h = 9.5, 4.75
    ox, oy, max_h = 1150 - 53 * w, 92, 56
    inner = []
    cells = [(wi, d["weekday"], d["contributionCount"]) for wi, week in enumerate(weeks) for d in week["contributionDays"]]
    for col, row, n in sorted(cells, key=lambda cell: (cell[0] + cell[1], cell[0])):
        px, py = ox + (col - row) * w, oy + (col + row) * h
        # Log scale, so one outlier day does not flatten the rest.
        height = 2 if not n else 5 + (max_h - 5) * math.log1p(n) / math.log1p(peak)
        lv = level(n)
        top = t["empty"] if lv < 0 else t["levels"][lv]
        s = 0.86  # gap between cells
        tw, th = w * s, h * s
        tx, ty = px, py + h - height  # centre of the top face
        T, R, B, L = (tx, ty - th), (tx + tw, ty), (tx, ty + th), (tx - tw, ty)
        B0, R0, L0 = (B[0], B[1] + height), (R[0], R[1] + height), (L[0], L[1] + height)

        def pts(*ps):
            return " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)

        inner.append(f'<polygon points="{pts(L, B, B0, L0)}" fill="{shade(top, 0.78)}"/>'
                     f'<polygon points="{pts(B, R, R0, B0)}" fill="{shade(top, 0.62)}"/>'
                     f'<polygon points="{pts(T, R, B, L)}" fill="{top}"/>')

    current, longest = streaks(history)
    best_date, best = max(history, key=lambda kv: kv[1])
    all_time = sum(n for _, n in history)
    plural = lambda n: f'{n} {c["day"] if n == 1 else c["days"]}'

    side = [
        f'<text x="48" y="52" font-size="18" font-weight="600" fill="{t["text"]}">{escape(c["contrib"])}</text>',
        f'<text x="48" y="128" font-size="56" font-weight="700" letter-spacing="-2" fill="{t["text"]}">{fmt(calendar["totalContributions"], c)}</text>',
        f'<text x="48" y="156" font-size="14" fill="{t["muted"]}">{escape(c["last_year"])}</text>',
    ]
    facts = [(c["current"], plural(current)), (c["longest"], plural(longest)),
             (c["best"], f"{best} · {fmt_date(best_date, c)}"), (c["total"], fmt(all_time, c))]
    for i, (label, value) in enumerate(facts):
        x = 48 + (i % 2) * 220
        y = 222 + (i // 2) * 64
        side.append(f'<text x="{x}" y="{y}" font-size="13" fill="{t["muted"]}">{escape(label)}</text>'
                    f'<text x="{x}" y="{y + 26}" font-size="19" font-weight="600" fill="{t["text"]}">{escape(value)}</text>')
    return frame(t, 1200, 400, c["contrib"], "\n  ".join(side + inner))


user = graphql(QUERY)
history = all_days(datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00")))
OUT.mkdir(parents=True, exist_ok=True)
for lang, c in COPY.items():
    for name, t in THEMES.items():
        (OUT / f"overview-{lang}-{name}.svg").write_text(overview_card(t, c, user), encoding="utf-8")
        (OUT / f"contrib-{lang}-{name}.svg").write_text(contrib_card(t, c, user, history), encoding="utf-8")
print("ok")
