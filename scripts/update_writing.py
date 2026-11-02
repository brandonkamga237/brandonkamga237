"""Refreshes the latest LesCracks blog articles between the WRITING markers of both READMEs.

Usage: python3 scripts/update_writing.py
"""
import json
import re
import urllib.request
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://lescracks.com"
LIMIT = 4
START, END = "<!-- WRITING:START -->", "<!-- WRITING:END -->"
READMES = {
    "README.md": dict(unit="min read",
                      months=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]),
    "README.fr.md": dict(unit="min de lecture",
                         months=["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]),
}


def articles():
    req = urllib.request.Request(f"{SITE}/api/resources?size={LIMIT}", headers={"User-Agent": "profile-readme"})
    with urllib.request.urlopen(req) as res:
        return json.load(res)["content"]


def cell(a, lang):
    url = f'{SITE}/blog/{a["slug"]}'
    d = date.fromisoformat(a["publishedAt"][:10])
    meta = f'{a["categoryName"]} · {a["readingMinutes"]} {lang["unit"]} · {d.day} {lang["months"][d.month - 1]} {d.year}'
    cover = f'<a href="{url}"><img alt="" src="{SITE}{a["coverImage"]}" width="100%"></a><br>' if a.get("coverImage") else ""
    return (f'    <td width="50%" valign="top">\n      {cover}\n'
            f'      <b><a href="{url}">{escape(a["title"])}</a></b><br>\n'
            f'      <sub>{escape(meta)}</sub>\n    </td>')


def render(items, lang):
    rows = ["  <tr>\n" + "\n".join(cell(a, lang) for a in items[i:i + 2]) + "\n  </tr>" for i in range(0, len(items), 2)]
    return "\n".join([START, "<table>", *rows, "</table>", END])


items = articles()
for name, lang in READMES.items():
    path = ROOT / name
    text = path.read_text(encoding="utf-8")
    block = re.compile(re.escape(START) + ".*?" + re.escape(END), re.S)
    path.write_text(block.sub(lambda _: render(items, lang), text), encoding="utf-8")
print("ok")
