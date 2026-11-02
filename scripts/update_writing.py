"""Refreshes the latest dev.to articles between the WRITING markers of both READMEs.

Usage: python3 scripts/update_writing.py
"""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEVTO_USER = "brandoniscoding-dev"
LIMIT = 4
START, END = "<!-- WRITING:START -->", "<!-- WRITING:END -->"
READMES = {"README.md": "min read", "README.fr.md": "min de lecture"}

# Decorative emoji at either end of a title, kept out for a sober list.
EDGE_SYMBOLS = re.compile(r"^[^\w«\"']+|[^\w»\"'?!.)]+$")


def articles():
    req = urllib.request.Request(
        f"https://dev.to/api/articles?username={DEVTO_USER}&per_page={LIMIT}",
        headers={"User-Agent": "profile-readme"},
    )
    with urllib.request.urlopen(req) as res:
        return json.load(res)


def render(items, unit):
    lines = [f'- [{EDGE_SYMBOLS.sub("", a["title"]).strip()}]({a["url"]}) <sub>· {a["reading_time_minutes"]} {unit}</sub>'
             for a in items]
    return "\n".join([START, *lines, END])


items = articles()
for name, unit in READMES.items():
    path = ROOT / name
    text = path.read_text(encoding="utf-8")
    block = re.compile(re.escape(START) + ".*?" + re.escape(END), re.S)
    path.write_text(block.sub(lambda _: render(items, unit), text), encoding="utf-8")
print("ok")
