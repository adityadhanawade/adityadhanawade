#!/usr/bin/env python3
"""Generate every SVG used by the profile README.

Concept: the profile is a transit network. Build work runs on one line (orange),
design work on another (cream). Projects are stations. Where a project needed both
(The Leverage Report) the lines meet at an interchange.

Usage:
    python scripts/build_assets.py                 # all assets
    python scripts/build_assets.py --activity-only # just the contribution timetable

The activity chart reads real public contribution data through the GitHub CLI
(`gh api graphql`). If that call fails, the existing SVG is left untouched.
"""
import json
import subprocess
import sys
from datetime import date
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
USER = "adityadhanawade"

INK = "#0F1216"
PANEL = "#171B21"
HAIR = "#2A313A"
TEXT = "#ECE8E0"
SOFT = "#C9C5BD"
MUTED = "#8F98A3"
BUILD = "#FF7A1A"   # the single accent
DESIGN = "#ECE8E0"

SANS = "'Segoe UI', -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, Menlo, monospace"


def svg(w, h, title, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-labelledby="t">'
        f'<title id="t">{escape(title)}</title>{body}</svg>\n'
    )


def t(x, y, s, size, fill=TEXT, weight=400, family=SANS, anchor="start", extra=""):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
        f'font-family="{family}" fill="{fill}" text-anchor="{anchor}" {extra}>{escape(s)}</text>'
    )


def station(x, y, color, r=11):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}" stroke="{color}" stroke-width="5"/>'


def fits(s, size, width, factor=0.56):
    assert len(s) * size * factor <= width, f"text too long for its box: {s!r}"


# ---------------------------------------------------------------- hero
def hero():
    w, h = 1000, 440
    by, dy = 322, 372  # build / design line y
    b = [f'<rect width="{w}" height="{h}" rx="20" fill="{INK}"/>']
    b.append(t(56, 118, "Aditya Dhanawade", 82, TEXT, 800, extra='letter-spacing="-2"'))
    b.append(t(56, 176, "I design it, then I build it.", 38, BUILD, 600))
    b.append(t(56, 222, "Full-stack developer and UI/UX designer, Pune", 22, MUTED, 400, MONO))
    # lines
    b.append(f'<line x1="150" y1="{by}" x2="950" y2="{by}" stroke="{BUILD}" stroke-width="8" stroke-linecap="round"/>')
    b.append(f'<line x1="150" y1="{dy}" x2="860" y2="{dy}" stroke="{DESIGN}" stroke-width="8" stroke-linecap="round"/>')
    # interchange link
    b.append(f'<line x1="390" y1="{by}" x2="390" y2="{dy}" stroke="{TEXT}" stroke-width="5"/>')
    build = [(190, "Vehicle App"), (390, "Leverage Report"), (580, "AI Data Analyst"), (740, "CivicFix"), (900, "NagarNetra")]
    design = [(190, "Thiranex"), (600, "Caregiver"), (790, "Vanguard Audio")]
    for x, name in build:
        b.append(station(x, by, BUILD))
        b.append(t(x, by - 26, name, 20, SOFT, 500, anchor="middle"))
    b.append(station(390, dy, DESIGN))
    for x, name in design:
        b.append(station(x, dy, DESIGN))
        b.append(t(x, dy + 46, name, 20, SOFT, 500, anchor="middle"))
    b.append(t(56, by + 5, "BUILD", 15, BUILD, 700, MONO, extra='letter-spacing="3"'))
    b.append(t(56, dy + 5, "DESIGN", 15, DESIGN, 700, MONO, extra='letter-spacing="3"'))
    return svg(w, h, "Aditya Dhanawade. Full-stack developer and UI/UX designer. A transit map with a build line and a design line meeting at The Leverage Report.", "".join(b))


# ---------------------------------------------------------------- cards
CARDS = [
    ("nagarnetra", "NagarNetra", "Live demo, in development", BUILD,
     ["Buses as moving city sensors. A phone on the dash", "detects road damage (YOLOv8) for a fleet dashboard."],
     "React / Vite / FastAPI / YOLOv8 / Supabase"),
    ("ai-data-analyst-agent", "AI Data Analyst Agent", "Live demo", BUILD,
     ["Ask a dataset questions in plain English. The agent", "writes pandas code, runs it, fixes its own errors."],
     "Python / TypeScript / Strands Agents / Gemini"),
    ("leverage-report", "The Leverage Report", "Live", BUILD,
     ["A free AI-money toolkit with four interactive tools,", "designed and built solo, research to deployment."],
     "Next.js / TypeScript / Tailwind CSS"),
    ("civicfix", "CivicFix", "Smart India Hackathon 2026", BUILD,
     ["A complaint closes only with proof: the after-photo", "must match the report GPS. I led the team of six."],
     "Team Hex Coders / JSPM University, Pune"),
    ("caregiver", "The Caregiver Is Invisible", "Zuntra 2026 entry", DESIGN,
     ["A case study on designing for the adult child who", "coordinates a parent's care from far away."],
     "Figma / 5 interviews / 12 screens / 2 test rounds"),
    ("vanguard", "Vanguard Audio", "48-hour design marathon", DESIGN,
     ["Brand identity and launch campaign for a fictional", "audio brand, done solo for IIT Bhubaneswar."],
     "Brand identity / campaign / art direction"),
]


def card(slug, name, status, color, lines, footer):
    w, h = 800, 196
    for ln in lines:
        fits(ln, 24, 690, 0.54)
    fits(footer, 19, 690, 0.62)
    fits(name, 31, 490, 0.58)
    b = [f'<rect width="{w}" height="{h}" rx="16" fill="{INK}"/>']
    b.append(f'<line x1="44" y1="48" x2="44" y2="{h - 28}" stroke="{color}" stroke-width="8" stroke-linecap="round"/>')
    b.append(station(44, 48, color, 12))
    b.append(t(84, 58, name, 31, TEXT, 700))
    b.append(t(w - 36, 56, status, 17, color, 600, MONO, "end"))
    b.append(t(84, 104, lines[0], 24, SOFT))
    b.append(t(84, 136, lines[1], 24, SOFT))
    b.append(f'<line x1="84" y1="152" x2="{w - 36}" y2="152" stroke="{HAIR}" stroke-width="2"/>')
    b.append(t(84, 178, footer, 19, MUTED, 400, MONO))
    return svg(w, h, f"{name}. {' '.join(lines)} {footer}.", "".join(b))


# ---------------------------------------------------------------- stack lines
def stack():
    w, h = 700, 560
    build = ["TypeScript", "React and Next.js", "Tailwind CSS", "Python and FastAPI", "Kotlin and Java", "Firebase and Supabase"]
    design = ["Figma", "Design systems", "User research", "Prototyping", "Usability testing", "Heuristic evaluation"]
    b = [f'<rect width="{w}" height="{h}" rx="20" fill="{INK}"/>']
    xs = (60, 390)
    top, step = 120, 60
    for x, color, head, items in ((xs[0], BUILD, "BUILD LINE", build), (xs[1], DESIGN, "DESIGN LINE", design)):
        b.append(t(x - 14, 64, head, 18, color, 700, MONO, extra='letter-spacing="3"'))
        last = top + step * (len(items) - 1)
        b.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{last + 70}" stroke="{color}" stroke-width="8" stroke-linecap="round"/>')
        for i, name in enumerate(items):
            y = top + step * i
            b.append(station(x, y, color))
            b.append(t(x + 28, y + 8, name, 24, TEXT, 500))
    ey = top + step * 5 + 70
    # both lines run into one terminal
    b.append(f'<path d="M {xs[0]} {ey - 20} V {ey} H {xs[1]}" fill="none" stroke="{BUILD}" stroke-width="8" stroke-linecap="round"/>')
    b.append(f'<line x1="{xs[1]}" y1="{ey - 20}" x2="{xs[1]}" y2="{ey}" stroke="{DESIGN}" stroke-width="8" stroke-linecap="round"/>')
    b.append(f'<rect x="{xs[1] - 14}" y="{ey - 14}" width="28" height="28" rx="6" fill="{TEXT}"/>')
    b.append(t(xs[1] + 32, ey + 8, "One product, end to end", 22, SOFT, 500))
    return svg(w, h, "Toolkit as two transit lines. Build line: TypeScript, React and Next.js, Tailwind CSS, Python and FastAPI, Kotlin and Java, Firebase and Supabase. Design line: Figma, design systems, user research, prototyping, usability testing, heuristic evaluation.", "".join(b))


# ---------------------------------------------------------------- divider / footer
def divider():
    b = (f'<line x1="40" y1="14" x2="1000" y2="14" stroke="#8B949E" stroke-opacity=".45" stroke-width="3" stroke-linecap="round"/>'
         f'<circle cx="16" cy="14" r="8" fill="none" stroke="{BUILD}" stroke-width="4"/>')
    return svg(1000, 28, "Section divider", b).replace('role="img"', 'role="presentation" aria-hidden="true"')


def footer():
    w, h = 1000, 150
    b = [f'<rect width="{w}" height="{h}" rx="20" fill="{INK}"/>']
    b.append(f'<line x1="0" y1="75" x2="820" y2="75" stroke="{BUILD}" stroke-width="8"/>')
    b.append(f'<rect x="820" y="40" width="22" height="70" rx="6" fill="{TEXT}"/>')
    b.append(t(56, 56, "End of the line", 30, TEXT, 700))
    b.append(t(56, 118, "Open to internships in full-stack and UI/UX.", 22, SOFT, 400))
    return svg(w, h, "End of the line. Open to internships in full-stack and UI/UX.", "".join(b))


# ---------------------------------------------------------------- activity
def fetch_activity():
    q = ('{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions '
         'weeks{contributionDays{date contributionCount}}}}}}' % USER)
    r = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def activity():
    cal = fetch_activity()
    weeks = cal["weeks"]
    days = [d for wk in weeks for d in wk["contributionDays"]]
    total = cal["totalContributions"]
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
            return "#1D232B", 1
        lvl = 1 + sum(n > c for c in q)
        return BUILD, (0.28, 0.5, 0.75, 1.0)[lvl - 1]

    w, h = 1000, 330
    b = [f'<rect width="{w}" height="{h}" rx="20" fill="{INK}"/>']
    b.append(t(40, 56, "Activity, past 12 months", 26, TEXT, 700))
    x0, y0, step, size = 40, 100, 17.4, 14
    last_month = None
    for i, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            dt = date.fromisoformat(d["date"])
            col, op = shade(d["contributionCount"])
            y = y0 + (dt.isoweekday() % 7) * step
            b.append(f'<rect x="{x0 + i * step:.1f}" y="{y:.1f}" width="{size}" height="{size}" rx="3" fill="{col}" fill-opacity="{op}"/>')
        m = date.fromisoformat(wk["contributionDays"][0]["date"]).month
        if m != last_month:
            last_month = m
            b.append(t(x0 + i * step, y0 - 12, date(2000, m, 1).strftime("%b"), 13, MUTED, 400, MONO))
    sy = 270
    stats = [(str(total), "contributions"), (str(active), "active days"), (str(streak), "longest streak, days"),
             (str(best["contributionCount"]), "busiest day, " + date.fromisoformat(best["date"]).strftime("%b %d").replace(" 0", " "))]
    for i, (num, label) in enumerate(stats):
        x = 40 + i * 235
        b.append(t(x, sy, num, 38, BUILD, 700, MONO))
        b.append(t(x, sy + 26, label, 15, MUTED, 400, MONO))
    b.append(t(w - 40, 56, "refreshed " + date.today().isoformat(), 14, MUTED, 400, MONO, "end"))
    return svg(w, h, f"Contribution calendar for the past 12 months: {total} public contributions on {active} days, longest streak {streak} days.", "".join(b))


def write(name, content):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")
    print("wrote", name, len(content), "bytes")


if __name__ == "__main__":
    if "--activity-only" not in sys.argv:
        write("hero.svg", hero())
        for c in CARDS:
            write(f"card-{c[0]}.svg", card(*c))
        write("stack.svg", stack())
        write("divider.svg", divider())
        write("footer.svg", footer())
    try:
        write("activity.svg", activity())
    except Exception as e:  # keep the last good chart
        print("activity not refreshed:", e)
        if "--activity-only" in sys.argv:
            sys.exit(0)
