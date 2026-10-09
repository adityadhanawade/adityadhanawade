#!/usr/bin/env python3
"""Generate every SVG used by the profile README.

Concept: the profile is a transit network. Build work runs on one line (orange),
design work on another (cream). Projects are stations. Where a project needed both
(The Leverage Report) the lines meet at an interchange.

Text is converted to outlines with the fonts in scripts/fonts (SIL OFL), so every
graphic renders identically on every OS. GitHub shows SVGs through <img>, which cannot
load web fonts, and system fonts differ per device.

Usage:
    python scripts/build_assets.py                 # all assets
    python scripts/build_assets.py --activity-only # just the contribution chart

Requires: fonttools (pip install fonttools). The activity chart also needs the GitHub
CLI, authenticated (locally, or through GH_TOKEN in Actions). If the fetch fails the
existing activity.svg is left untouched.
"""
import json
import subprocess
import sys
from datetime import date
from html import escape
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONTS = Path(__file__).resolve().parent / "fonts"
USER = "adityadhanawade"

W = 600  # every graphic is drawn 600 units wide; GitHub shows them ~350px on a phone
INK = "#12161C"
EDGE = "#303741"   # panel border, keeps the panels visible on GitHub's dark theme
HAIR = "#2A313A"
TEXT = "#ECE8E0"
SOFT = "#C9C5BD"
MUTED = "#9AA3AE"
BUILD = "#FF7A1A"  # the single accent
DESIGN = "#ECE8E0"


class Face:
    def __init__(self, key, file):
        self.key = key
        self.font = TTFont(FONTS / file)
        self.upem = self.font["head"].unitsPerEm
        self.cmap = self.font.getBestCmap()
        self.gs = self.font.getGlyphSet()
        self.hmtx = self.font["hmtx"]

    def glyph(self, ch):
        return self.cmap.get(ord(ch)) or self.cmap[ord("?")]

    def width(self, s, size, ls=0.0):
        sc = size / self.upem
        return sum(self.hmtx[self.glyph(c)][0] * sc + ls for c in s) - (ls if s else 0)


SANS = Face("s5", "SpaceGrotesk-500.ttf")
SANSB = Face("s7", "SpaceGrotesk-700.ttf")
MONO = Face("m5", "JetBrainsMono-500.ttf")
MONOB = Face("m7", "JetBrainsMono-700.ttf")


class Canvas:
    def __init__(self, w, h, title, panel=True, r=20):
        self.w, self.h, self.title = w, h, title
        self.defs, self.body = {}, []
        if panel:
            self.body.append(f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="{INK}" stroke="{EDGE}" stroke-width="2"/>')

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, size, fill=TEXT, face=SANS, anchor="start", ls=0.0):
        sc = size / face.upem
        width = face.width(s, size, ls)
        x0 = x - width if anchor == "end" else x - width / 2 if anchor == "middle" else x
        uses, cur = [], 0.0
        for ch in s:
            g = face.glyph(ch)
            adv = face.hmtx[g][0]
            gid = f"{face.key}{g}"
            if gid not in self.defs:
                pen = SVGPathPen(face.gs, ntos=lambda v: str(int(round(v))))
                face.gs[g].draw(pen)
                self.defs[gid] = pen.getCommands()
            if self.defs[gid]:
                uses.append(f'<use href="#{gid}" x="{cur:.0f}"/>')
            cur += adv + ls / sc
        self.body.append(f'<g transform="translate({x0:.1f} {y}) scale({sc:.5f} {-sc:.5f})" fill="{fill}">{"".join(uses)}</g>')
        return width

    def wrap(self, s, size, maxw, face=SANS):
        lines, line = [], ""
        for word in s.split():
            trial = f"{line} {word}".strip()
            if face.width(trial, size) <= maxw:
                line = trial
            else:
                lines.append(line)
                line = word
        return lines + [line]

    def station(self, x, y, color, r=11, sw=5):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}" stroke="{color}" stroke-width="{sw}"/>')

    def line(self, x1, y1, x2, y2, color, sw=8):
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>')

    def render(self):
        defs = "".join(f'<path id="{k}" d="{v}"/>' for k, v in self.defs.items())
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
            f'role="img" aria-labelledby="t"><title id="t">{escape(self.title)}</title><defs>{defs}</defs>{"".join(self.body)}</svg>\n'
        )


def fit(s, size, maxw, face=SANS):
    w = face.width(s, size)
    assert w <= maxw, f"{s!r} is {w:.0f} wide, box is {maxw}"


# ---------------------------------------------------------------- hero
def hero():
    h = 392
    c = Canvas(W, h, "Aditya Dhanawade. Full-stack developer and UI/UX designer. A transit map with a build line and a design line meeting at The Leverage Report.")
    c.text(30, 84, "Aditya Dhanawade", 56, TEXT, SANSB, ls=-1)
    c.text(30, 132, "I design it, then I build it.", 28, BUILD, SANS)
    c.text(30, 170, "Full-stack developer and UI/UX designer, Pune", 18, MUTED, MONO)
    by, dy = 262, 316
    c.line(100, by, 572, by, BUILD)
    c.line(100, dy, 500, dy, DESIGN)
    c.line(190, by, 190, dy, TEXT, 5)
    c.text(30, by + 5, "BUILD", 14, BUILD, MONOB, ls=2)
    c.text(30, dy + 5, "DESIGN", 14, DESIGN, MONOB, ls=2)
    for x, name in ((190, "Leverage"), (320, "AI Analyst"), (430, "CivicFix"), (532, "NagarNetra")):
        c.station(x, by, BUILD)
        fit(name, 19, 110)
        c.text(x, by - 24, name, 19, SOFT, SANS, "middle")
    c.station(190, dy, DESIGN)
    for x, name in ((130, "Thiranex"), (340, "Caregiver"), (470, "Vanguard")):
        c.station(x, dy, DESIGN)
        c.text(x, dy + 42, name, 19, SOFT, SANS, "middle")
    return c.render()


# ---------------------------------------------------------------- cards
CARDS = [
    ("nagarnetra", "NagarNetra", "Live demo, in development", BUILD,
     "Buses become moving city sensors. A phone on the dash detects road damage with YOLOv8 and feeds a fleet dashboard.",
     "React / Vite / FastAPI / YOLOv8 / Supabase"),
    ("ai-data-analyst-agent", "AI Data Analyst Agent", "Live demo", BUILD,
     "Ask a dataset questions in plain English. The agent writes pandas code, runs it, and fixes its own errors.",
     "Python / TypeScript / Strands Agents / Gemini"),
    ("leverage-report", "The Leverage Report", "Live", BUILD,
     "A free AI-money toolkit with four interactive tools, designed and built solo from research to deployment.",
     "Next.js / TypeScript / Tailwind CSS"),
    ("civicfix", "CivicFix", "Smart India Hackathon 2026", BUILD,
     "A civic complaint closes only with proof: the after-photo must match the report's GPS location. I led the team of six.",
     "Team Hex Coders / JSPM University, Pune"),
    ("caregiver", "The Caregiver Is Invisible", "Zuntra Awards 2026 entry", DESIGN,
     "A case study on designing for the adult child who coordinates a parent's care from far away.",
     "Figma / 5 interviews / 12 screens / 2 test rounds"),
    ("vanguard", "Vanguard Audio", "48-hour design marathon", DESIGN,
     "Brand identity and launch campaign for a fictional audio brand, done solo for the IIT Bhubaneswar design marathon.",
     "Brand identity / campaign / art direction"),
]


def card(slug, name, status, color, desc, footer):
    tx = 66
    probe = Canvas(W, 10, "", panel=False)
    lines = probe.wrap(desc, 20, W - tx - 30)
    fy = 118 + 28 * (len(lines) - 1) + 38
    h = fy + 34
    c = Canvas(W, h, f"{name}. {status}. {desc} {footer}.", r=16)
    c.line(34, 46, 34, h - 30, color)
    c.station(34, 46, color, 12)
    fit(name, 26, W - tx - 24, SANSB)
    c.text(tx, 54, name, 26, TEXT, SANSB)
    c.text(tx, 82, status, 16, color, MONO)
    for i, ln in enumerate(lines):
        c.text(tx, 118 + 28 * i, ln, 20, SOFT, SANS)
    c.add(f'<line x1="{tx}" y1="{fy - 22}" x2="{W - 30}" y2="{fy - 22}" stroke="{HAIR}" stroke-width="2"/>')
    fit(footer, 16, W - tx - 24, MONO)
    c.text(tx, fy + 4, footer, 16, MUTED, MONO)
    return c.render()


# ---------------------------------------------------------------- stack lines
def stack():
    build = ["TypeScript", "React and Next.js", "Tailwind CSS", "Python and FastAPI", "Kotlin and Java", "Firebase and Supabase"]
    design = ["Figma", "Design systems", "User research", "Prototyping", "Usability testing", "Heuristic evaluation"]
    xs, top, step = (44, 338), 112, 54
    h = top + step * 5 + 130
    c = Canvas(W, h, "Toolkit as two transit lines. Build line: " + ", ".join(build) + ". Design line: " + ", ".join(design) + ".")
    for x, color, head, items in ((xs[0], BUILD, "BUILD LINE", build), (xs[1], DESIGN, "DESIGN LINE", design)):
        c.text(x - 11, 62, head, 15, color, MONOB, ls=2)
        c.line(x, top, x, top + step * 5 + 50, color)
        for i, name in enumerate(items):
            y = top + step * i
            c.station(x, y, color)
            fit(name, 20, 236 if x == xs[1] else 232)
            c.text(x + 26, y + 7, name, 20, TEXT, SANS)
    ey = top + step * 5 + 50
    c.add(f'<path d="M {xs[0]} {ey} H {xs[1]}" fill="none" stroke="{BUILD}" stroke-width="8" stroke-linecap="round"/>')
    c.line(xs[1], ey - 8, xs[1], ey, DESIGN)
    c.add(f'<rect x="{xs[1] - 14}" y="{ey - 14}" width="28" height="28" rx="6" fill="{TEXT}"/>')
    c.text(W / 2, ey + 56, "Both lines end at one product.", 20, SOFT, SANS, "middle")
    return c.render()


# ---------------------------------------------------------------- divider / footer
def divider():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 28" width="600" height="28" role="presentation" aria-hidden="true">'
        '<line x1="30" y1="14" x2="600" y2="14" stroke="#8B949E" stroke-opacity=".45" stroke-width="3" stroke-linecap="round"/>'
        f'<circle cx="12" cy="14" r="8" fill="none" stroke="{BUILD}" stroke-width="4"/></svg>\n'
    )


def footer():
    h = 130
    c = Canvas(W, h, "End of the line. Open to internships in full-stack and UI/UX.")
    c.line(30, 98, 530, 98, BUILD)
    c.add(f'<rect x="530" y="82" width="16" height="32" rx="5" fill="{TEXT}"/>')
    c.text(30, 48, "End of the line", 28, TEXT, SANSB)
    c.text(30, 76, "Open to internships in full-stack and UI/UX.", 18, SOFT, SANS)
    return c.render()


# ---------------------------------------------------------------- activity
def fetch_activity():
    q = ('{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions '
         'weeks{contributionDays{date contributionCount}}}}}}' % USER)
    r = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def activity():
    cal = fetch_activity()
    weeks = cal["weeks"]
    # Skip the empty stretch before the first contribution so the chart shows activity, not blank space.
    first = next((i for i, wk in enumerate(weeks) if any(d["contributionCount"] for d in wk["contributionDays"])), 0)
    weeks = weeks[min(first, len(weeks) - 12):]
    days = [d for wk in weeks for d in wk["contributionDays"]]
    total = sum(d["contributionCount"] for d in days)
    active = sum(1 for d in days if d["contributionCount"] > 0)
    best = max(days, key=lambda d: d["contributionCount"])
    streak = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] > 0 else 0
        streak = max(streak, cur)
    nz = sorted(d["contributionCount"] for d in days if d["contributionCount"] > 0)
    q = [nz[int(len(nz) * p)] for p in (0.25, 0.5, 0.75)] if nz else [1, 2, 3]

    def shade(n):
        if n == 0:
            return "#222932", 1
        lvl = 1 + sum(n > t for t in q)
        return BUILD, (0.3, 0.55, 0.78, 1.0)[lvl - 1]

    n = len(weeks)
    step = min(24, (W - 60) / n)
    gw = step * n
    y0 = 78
    sy = y0 + 7 * step + 44
    h = round(sy + 52)
    c = Canvas(W, h, f"Contribution calendar for the past {n} weeks: {total} public contributions on {active} days, longest streak {streak} days, busiest day {best['contributionCount']}.")
    c.text(30, 50, f"Activity, past {n} weeks", 22, TEXT, SANSB)
    x0 = (W - gw) / 2
    for i, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            dt = date.fromisoformat(d["date"])
            col, op = shade(d["contributionCount"])
            c.add(f'<rect x="{x0 + i * step:.1f}" y="{y0 + (dt.isoweekday() % 7) * step:.1f}" width="{step - 3:.1f}" height="{step - 3:.1f}" rx="3" fill="{col}" fill-opacity="{op}"/>')
    stats = [(str(total), "contributions"), (str(active), "active days"), (str(streak), "day streak"),
             (str(best["contributionCount"]), "busiest day")]
    for i, (num, label) in enumerate(stats):
        x = 30 + i * 140
        c.text(x, sy, num, 30, BUILD, MONOB)
        c.text(x, sy + 24, label, 13, MUTED, MONO)
    return c.render()


def write(name, content):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {name:34s} {len(content):>7,} bytes")


if __name__ == "__main__":
    only = "--activity-only" in sys.argv
    if not only:
        write("hero.svg", hero())
        for spec in CARDS:
            write(f"card-{spec[0]}.svg", card(*spec))
        write("stack.svg", stack())
        write("divider.svg", divider())
        write("footer.svg", footer())
    try:
        write("activity.svg", activity())
    except Exception as e:  # keep the last good chart
        print("activity not refreshed:", e)
        if not only:
            sys.exit(1)
