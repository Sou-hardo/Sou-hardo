"""Render the profile README's SVG cards in sou-hardo.com's design language.

Black page, white ink, warm-grey muted text, hairline dividers, one violet
accent, Helvetica for text and JetBrains Mono for small labels.

    python3 scripts/build_svgs.py            # static cards + "now" (needs GH_TOKEN for live data)
"""

import json
import os
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
USER = "Sou-hardo"

BG, FG, MUTED, LINE, SURFACE, ACCENT = "#0a0a0a", "#ffffff", "#aaa59e", "#3b3936", "#242321", "#897aff"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono',ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

EASE = "cubic-bezier(.22,1,.36,1)"  # one curve everywhere: quick out, long settle

STYLE = f"""<style>
.s{{font-family:{SANS}}}.m{{font-family:{MONO}}}
.tb{{transform-box:fill-box;transform-origin:center}}
@keyframes fade{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
@keyframes pulse{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
@keyframes draw{{from{{stroke-dashoffset:1200}}to{{stroke-dashoffset:0}}}}
@keyframes wipe{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
@keyframes shadow{{0%,100%{{transform:scaleX(1);opacity:.5}}50%{{transform:scaleX(.78);opacity:.25}}}}
@keyframes ripple{{from{{transform:scale(1);opacity:.7}}to{{transform:scale(3.2);opacity:0}}}}
@keyframes wave{{0%,70%,100%{{opacity:.35;transform:scale(1)}}12%{{opacity:1;transform:scale(1.9)}}}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
@keyframes bob{{0%,100%{{transform:scaleY(1)}}50%{{transform:scaleY(.82)}}}}
.f{{animation:fade 1s {EASE} both}}
.p{{animation:pulse 3.6s ease-in-out infinite}}
.b{{animation:blink 1.1s step-end infinite}}
.dr{{stroke-dasharray:1200;animation:draw 2.6s {EASE} both}}
.w{{transform-box:fill-box;transform-origin:left;animation:wipe 1.4s {EASE} both}}
.fl{{animation:float 4.8s ease-in-out infinite}}
.sh{{transform-box:fill-box;transform-origin:center;animation:shadow 4.8s ease-in-out infinite}}
.rp{{transform-box:fill-box;transform-origin:center;animation:ripple 2.4s {EASE} infinite}}
.wv{{transform-box:fill-box;transform-origin:center;animation:wave 6s ease-in-out infinite}}
.g{{transform-box:fill-box;transform-origin:bottom;animation:grow 1.2s {EASE} both,bob 5s ease-in-out 1.4s infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""

MASCOT = "data:image/gif;base64," + __import__("base64").b64encode((OUT / "mascot.gif").read_bytes()).decode()


def mascot(x, y, size, shadow=True):
    """The site's cat favicon, floating, with a ground shadow that breathes opposite."""
    sh = f'<ellipse class="sh" cx="{x + size / 2}" cy="{y + size * .97}" rx="{size * .3}" ry="{size * .05}" fill="{ACCENT}" opacity=".4"/>' if shadow else ""
    return f'{sh}<g class="fl"><image href="{MASCOT}" x="{x}" y="{y}" width="{size}" height="{size}"/></g>'


def t(s):
    return escape(str(s), quote=True)


def svg(w, h, body, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{t(label)}">{STYLE}'
        f'<rect width="{w}" height="{h}" rx="14" fill="{BG}"/>'
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="13.5" fill="none" stroke="{LINE}"/>'
        f"{body}</svg>\n"
    )


def wrap(text, size, width):
    """Greedy word wrap using an average Helvetica glyph width."""
    max_chars = int(width / (size * 0.53))
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + ([cur] if cur else [])


def para(x, y, text, size=15, width=500, fill=MUTED, lh=1.5, cls="s", delay=0):
    out = []
    for i, line in enumerate(wrap(text, size, width)):
        out.append(f'<text class="{cls}" x="{x}" y="{y + i * size * lh:.1f}" font-size="{size}" fill="{fill}">{t(line)}</text>')
    return f'<g class="f" style="animation-delay:{delay}s">{"".join(out)}</g>', y + len(out) * size * lh


def label(x, y, text, fill=MUTED, anchor="start"):
    return f'<text class="m" x="{x}" y="{y}" font-size="15" letter-spacing="1.4" fill="{fill}" text-anchor="{anchor}">{t(text.upper())}</text>'


def square(x, y, fill=MUTED, s=5):
    return f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{fill}"/>'


# --- cards --------------------------------------------------------------------


def header():
    w, h = 1200, 450
    cx, cy = 930, 210  # mascot centre; the dot wave radiates from here
    dots = []
    for r in range(14):
        for c in range(24):
            x, y = 690 + c * 20, 40 + r * 26
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** .5
            if d < 118:
                continue  # clear a halo around the cat
            accent = (r * 7 + c * 3) % 13 == 0
            fill, size = (ACCENT, 3) if accent else (LINE, 2)
            dots.append(f'<rect class="wv" style="animation-delay:{d / 160:.2f}s" x="{x}" y="{y}" width="{size}" height="{size}" fill="{fill}"/>')
    roles = [
        ("Software Developer, AI & DevOps", "Ledgercross"),
        ("Co-founder & Operations Director", "Arché Intelligence Lab"),
        ("Advisor", "FrithX"),
        ("B.Sc. CSE, CGPA 4.00", "AIUB, Dhaka"),
    ]
    rows = []
    for i, (role, org) in enumerate(roles):
        y = 268 + i * 36
        rows.append(
            f'<g class="f" style="animation-delay:{1.3 + i * .14:.2f}s">{square(64, y - 11, ACCENT if i == 0 else MUTED, 7)}'
            f'<text class="s" x="84" y="{y}" font-size="21" fill="{FG}">{t(role)}'
            f'<tspan fill="{MUTED}">  ·  {t(org)}</tspan></text></g>'
        )
    tagline = "AI researcher and AI engineer."
    tw = len(tagline) * 26 * .455
    body = (
        
        f'<g>{"".join(dots)}</g>'
        + f'<circle class="rp" cx="{cx}" cy="{cy}" r="46" fill="none" stroke="{ACCENT}" stroke-opacity=".5"/>'
        + f'<circle class="rp" style="animation-delay:1.2s" cx="{cx}" cy="{cy}" r="46" fill="none" stroke="{ACCENT}" stroke-opacity=".5"/>'
        + mascot(cx - 80, cy - 86, 160)
        + f'<g class="f">{label(64, 74, "Dhaka, Bangladesh")}</g>'
        + f'<defs><clipPath id="nm"><rect class="w" style="animation-delay:.15s" x="56" y="90" width="430" height="80"/></clipPath>'
        f'<clipPath id="tg"><rect class="w" style="animation-delay:.8s;animation-timing-function:steps(30)" x="64" y="164" width="{tw + 6:.0f}" height="34"/></clipPath></defs>'
        + f'<text class="s" clip-path="url(#nm)" x="60" y="150" font-size="64" font-weight="700" fill="{FG}" letter-spacing="-1.5">@sou-hardo</text>'
        + f'<text class="s" clip-path="url(#tg)" x="64" y="192" font-size="26" fill="{MUTED}">{t(tagline)}</text>'
        + f'<rect class="b" x="{70 + tw:.0f}" y="170" width="2" height="26" fill="{ACCENT}"/>'
        + f'<line class="w" style="animation-delay:1.1s" x1="64" y1="224" x2="640" y2="224" stroke="{LINE}"/>'
        + "".join(rows)
        + f'<text class="m" x="1136" y="416" font-size="16" fill="{MUTED}" text-anchor="end">sou-hardo.com</text>'
    )
    return svg(w, h, body, "Souhardo Rahman, @sou-hardo. AI researcher and AI engineer.")


def available():
    w, h = 1200, 130
    tracks = ["AI/ML engineering", "Full stack", "Research"]
    pills, x = [], 64
    for i, tr in enumerate(tracks):
        pw = len(tr) * 17 * .56 + 36
        pills.append(
            f'<g class="f" style="animation-delay:{.3 + i * .12:.2f}s">'
            f'<rect x="{x:.0f}" y="70" width="{pw:.0f}" height="36" rx="18" fill="none" stroke="{ACCENT}"/>'
            f'<text class="s" x="{x + pw / 2:.0f}" y="94" font-size="17" fill="{FG}" text-anchor="middle">{t(tr)}</text></g>'
        )
        x += pw + 12
    body = (
        f'<circle cx="70" cy="45" r="5" fill="#3fb950"/><circle class="rp" cx="70" cy="45" r="5" fill="#3fb950"/>'
        f'<g class="f"><text class="s" x="86" y="51" font-size="20" font-weight="700" fill="{FG}">Open to collaborations and hire</text></g>'
        + "".join(pills)
        + f'<g class="f" style="animation-delay:.6s"><text class="m" x="{w - 64}" y="51" font-size="17" fill="{ACCENT}" text-anchor="end">dev.souhardo@gmail.com</text>'
        + label(w - 64, 94, "Email me", anchor="end") + '</g>'
    )
    return svg(w, h, body, "Open to collaborations and hire: AI/ML engineering, full stack, research")


def stats():
    w, h = 1200, 170
    items = [("4.00", "CGPA at AIUB"), ("11", "Published research works"), ("34", "Citations · h-index 3"), ("13", "Co-authored papers at Arché")]
    col = (w - 64 * 2) / len(items)
    out = []
    for i, (num, cap) in enumerate(items):
        x = 64 + i * col
        if i:
            out.append(f'<line x1="{x - 24:.0f}" y1="40" x2="{x - 24:.0f}" y2="120" stroke="{LINE}"/>')
        out.append(
            f'<g class="f" style="animation-delay:{i * .12:.2f}s">'
            f'<text class="s" x="{x:.0f}" y="84" font-size="48" font-weight="700" fill="{FG}" letter-spacing="-1">{t(num)}</text>'
            f'<text class="s" x="{x:.0f}" y="114" font-size="18" fill="{MUTED}">{t(cap)}</text></g>'
            f'<line class="w" style="animation-delay:{.4 + i * .12:.2f}s" x1="{x:.0f}" y1="134" x2="{x + 32:.0f}" y2="134" stroke="{ACCENT}" stroke-width="2"/>'
        )
    return svg(w, h, "".join(out), "4.00 CGPA, 11 published research works, 34 citations, 13 co-authored papers at Arché")


def role(company, title, dates, bullets, url):
    w = 1200
    body = [
        label(48, 56, dates),
        f'<text class="s" x="48" y="100" font-size="34" font-weight="700" fill="{FG}">{t(company)}</text>',
        f'<text class="s" x="48" y="130" font-size="20" fill="{MUTED}">{t(title)}</text>',
        f'<line class="w" x1="48" y1="156" x2="{w - 48}" y2="156" stroke="{LINE}"/>',
        f'<line class="w" style="animation-delay:.2s" x1="48" y1="156" x2="128" y2="156" stroke="{ACCENT}" stroke-width="2"/>',
        f'<text class="m" x="{w - 48}" y="56" font-size="17" fill="{ACCENT}" text-anchor="end">{t(url)} ↗</text>',
    ]
    y = 196
    for i, b in enumerate(bullets):
        head, _, rest = b.partition(": ")
        if len(head) > 12:  # only short project names get the bold lead-in column
            head, rest = b, ""
        body.append(square(50, y - 12, ACCENT if rest else MUTED, 7))
        if rest:  # "Project: what it is" gets a bold lead-in column
            body.append(f'<text class="s f" style="animation-delay:{.1 + i * .1:.2f}s" x="70" y="{y}" font-size="20" font-weight="700" fill="{FG}">{t(head)}</text>')
            p, y = para(200, y, rest, size=20, width=w - 260, fill=FG, lh=1.45, delay=.1 + i * .1)
        else:
            p, y = para(70, y, b, size=20, width=w - 130, fill=FG, lh=1.45, delay=.1 + i * .1)
        body.append(p)
        y += 14
    h = int(y + 24)
    return svg(w, h, "".join(body), f"{title} at {company}")


def icon_uri(name):
    return "data:image/svg+xml;base64," + __import__("base64").b64encode((OUT / f"icon-{name}.svg").read_bytes()).decode()


def project(name, tag, desc, stack, meta, motif, icon):
    w = 590
    p, end = para(32, 98, desc, size=19, width=w - 190, lh=1.45)
    h = 266  # fixed so cards in a row line up
    body = (
        
        motif
        + f'<image class="f" href="{icon_uri(icon)}" x="32" y="34" width="34" height="34"/>'
        + f'<text class="s" x="76" y="60" font-size="30" font-weight="700" fill="{FG}">{t(name)}</text>'
        + p
        + f'<line class="w" style="animation-delay:.3s" x1="32" y1="{h - 58}" x2="{w - 32}" y2="{h - 58}" stroke="{LINE}"/>'
        + f'<text class="m" x="32" y="{h - 24}" font-size="15" fill="{MUTED}">{t(stack)}</text>'
        + f'<text class="m" x="{w - 32}" y="{h - 24}" font-size="15" fill="{ACCENT}" text-anchor="end">{t(meta)}</text>'
    )
    return svg(w, h, body, f"{name}: {desc}")


def motif_idcard():  # veritas: an ID card, a scan line sweeps the portrait, then a match tick
    return (
        f'<g transform="translate(436 36)">'
        f'<rect width="122" height="80" rx="6" fill="{SURFACE}" stroke="{LINE}"/>'
        f'<rect x="10" y="12" width="36" height="46" rx="3" fill="none" stroke="#5b5750"/>'
        f'<circle cx="28" cy="29" r="8" fill="#5b5750"/><path d="M14 56 q14 -16 28 0" fill="#5b5750"/>'
        f'<rect class="w" style="animation-delay:.4s" x="56" y="16" width="52" height="4" fill="{MUTED}"/>'
        f'<rect class="w" style="animation-delay:.6s" x="56" y="28" width="40" height="4" fill="{LINE}"/>'
        f'<rect class="w" style="animation-delay:.8s" x="56" y="40" width="46" height="4" fill="{LINE}"/>'
        f'<rect x="8" y="12" width="40" height="2" fill="{ACCENT}"><animate attributeName="y" values="12;56;12" dur="2.8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/></rect>'
        f'<path class="dr" style="animation-delay:1.2s" d="M58 62 l8 7 l16 -16" fill="none" stroke="{ACCENT}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></g>'
    )


def motif_negotiate():  # apron: supplier quote steps down toward the target price, then holds for approval
    pts = [(0, 6), (24, 6), (24, 26), (50, 26), (50, 40), (78, 40), (78, 50), (122, 50)]
    d = "M" + " L".join(f"{436 + x} {40 + y}" for x, y in pts)
    return (
        f'<line x1="436" y1="96" x2="558" y2="96" stroke="{ACCENT}" stroke-dasharray="3 4"/>'
        f'<text class="m" x="558" y="112" font-size="13" fill="{ACCENT}" text-anchor="end">TARGET</text>'
        f'<path class="dr" d="{d}" fill="none" stroke="{FG}" stroke-width="1.8"/>'
        f'<circle class="rp" cx="558" cy="90" r="5" fill="none" stroke="{ACCENT}"/><rect x="554" y="86" width="8" height="8" fill="{ACCENT}"/>'
    )


def motif_invoice():  # keptcash: an overdue invoice, the recovered bar fills up
    return (
        f'<g transform="translate(450 30)">'
        f'<path d="M0 0 h96 v92 l-12 -6 l-12 6 l-12 -6 l-12 6 l-12 -6 l-12 6 l-12 -6 l-12 6 z" fill="{SURFACE}" stroke="{LINE}"/>'
        f'<text class="m" x="12" y="22" font-size="13" font-weight="700" fill="{FG}">$</text>'
        f'<rect x="28" y="12" width="56" height="4" fill="{MUTED}"/><rect x="28" y="22" width="40" height="4" fill="{LINE}"/>'
        f'<rect x="12" y="40" width="72" height="6" fill="{LINE}"/>'
        f'<rect class="w" style="animation-delay:.6s;animation-duration:2.4s" x="12" y="40" width="72" height="6" fill="{ACCENT}"/>'
        f'<rect x="12" y="56" width="50" height="4" fill="{LINE}"/>'
        f'<text class="m p" x="84" y="74" font-size="13" fill="{ACCENT}" text-anchor="end">KEPT</text></g>'
    )


def motif_signal():  # wifirank: packets travel the arc between you and the edge
    arc = "M436 96 Q498 10 558 84"
    pk = "".join(
        f'<rect x="-3" y="-3" width="6" height="6" fill="{ACCENT}"><animateMotion dur="2.4s" begin="{i * .8}s" repeatCount="indefinite" path="{arc}" keyPoints="0;1" keyTimes="0;1" calcMode="spline" keySplines=".45 0 .55 1"/></rect>'
        for i in range(3)
    )
    return (
        f'<path class="dr" d="{arc}" fill="none" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="3 5"/>{pk}'
        f'<rect x="431" y="91" width="10" height="10" fill="{FG}"/>'
        f'<circle class="rp" cx="558" cy="84" r="6" fill="none" stroke="{ACCENT}"/><rect x="553" y="79" width="10" height="10" fill="{ACCENT}"/>'
    )


PUBS = [
    ("2026", "OpthaNet: attention-integrated ophthalmic image classification", "Wiley HTL"),
    ("2025", "T3SSLNet: triple self-supervised learning for brain tumor MRI", "IEEE Access"),
    ("2025", "KbFL-XAI: explainable federated learning for eye disease", "Elsevier BEA"),
    ("2025", "MIME: multi-strategy imbalance mitigation for skin cancer", "TCCE · Springer"),
    ("2025", "SSChNet: self-supervised network for child speech recognition", "IEEE NCIM"),
    ("2024", "Brain MRI ND-5 Dataset", "IEEE DataPort"),
    ("Review", "Hi-TGNet: hierarchical tumor guidance network (thesis)", "Sci. Reports"),
]


def publications():
    w = 1200
    h = 80 + len(PUBS) * 56 + 30
    body = [label(64, 50, "Selected research"), label(w - 64, 50, "34 citations · h-index 3", anchor="end")]
    for i, (yr, title, venue) in enumerate(PUBS):
        y = 112 + i * 56
        col = ACCENT if yr == "Review" else MUTED
        body.append(
            f'<g class="f" style="animation-delay:{i * .08:.2f}s">'
            f'<text class="m" x="64" y="{y}" font-size="16" fill="{col}">{t(yr)}</text>'
            f'<text class="s" x="160" y="{y}" font-size="20" fill="{FG}">{t(title)}</text>'
            f'<text class="s" x="{w - 64}" y="{y}" font-size="18" fill="{MUTED}" text-anchor="end">{t(venue)}</text>'
            f'<line class="w" style="animation-delay:{.2 + i * .08:.2f}s" x1="64" y1="{y + 24}" x2="{w - 64}" y2="{y + 24}" stroke="{LINE}"/></g>'
        )
    return svg(w, h, "".join(body), "Selected research publications")


def footer():
    w, h = 1200, 170
    body = (
        f'<line class="w" x1="64" y1="132" x2="{w - 64}" y2="132" stroke="{LINE}"/>'
        + mascot(w / 2 - 44, 40, 88, shadow=False)
        + f'<g class="f" style="animation-delay:.4s">{label(64, 116, "Thanks for stopping by")}'
        f'<text class="m" x="{w - 64}" y="116" font-size="17" fill="{ACCENT}" text-anchor="end">dev.souhardo@gmail.com</text></g>'
        + f'<text class="m" x="{w / 2}" y="158" font-size="16" fill="{MUTED}" text-anchor="middle">sou-hardo.com</text>'
    )
    return svg(w, h, body, "Thanks for stopping by. sou-hardo.com")


# --- activity (live) ----------------------------------------------------------

LEVELS = ["#161514", "#2e2a4d", "#4a3f99", "#6b5ce0", ACCENT]  # empty → busiest, violet ramp


def activity_data():
    data = gql(
        "{viewer{followers{totalCount} "
        "repositories(first:100,ownerAffiliations:[OWNER,COLLABORATOR,ORGANIZATION_MEMBER],isFork:false){nodes{stargazerCount owner{login} "
        "languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}} "
        "contributionsCollection{totalCommitContributions totalPullRequestContributions totalIssueContributions "
        "totalPullRequestReviewContributions restrictedContributionsCount "
        "contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"
    )
    if not data:
        return None
    v = data["viewer"]
    c = v["contributionsCollection"]
    days = [d for w in c["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    longest = cur = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    for d in reversed(days):
        if d["contributionCount"]:
            cur += 1
        elif cur or d is not days[-1]:
            break  # today may still be empty without breaking the streak
    langs = {}
    for r in v["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or MUTED])[0] += e["size"]
    total = sum(x[0] for x in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:8]
    best = max(days, key=lambda d: d["contributionCount"])
    return {
        "total": c["contributionCalendar"]["totalContributions"],
        "week": sum(d["contributionCount"] for d in days[-7:]),
        "best": best["contributionCount"],
        "best_date": best["date"],
        "longest": longest,
        "current": cur,
        "stars": sum(r["stargazerCount"] for r in v["repositories"]["nodes"] if r["owner"]["login"] == USER),
        "followers": v["followers"]["totalCount"],
        "prs": c["totalPullRequestContributions"],
        "issues": c["totalIssueContributions"],
        "reviews": c["totalPullRequestReviewContributions"],
        "commits": c["totalCommitContributions"] + c["restrictedContributionsCount"],
        "langs": [(n, sz / total, col) for n, (sz, col) in top],
        "days": days,
    }


def fmt_date(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%b %-d")


def overview(a):
    w, h = 590, 330
    cx, cy, r = 128, 170, 76
    circ = 2 * 3.14159 * r
    stats = [(f'{a["commits"]:,}', "Commits"), (str(a["prs"]), "Pull requests"), (str(a["issues"]), "Issues"), (str(a["followers"]), "Followers")]
    cells = []
    for i, (num, cap) in enumerate(stats):
        x, y = 262 + (i % 2) * 160, 132 + (i // 2) * 80
        cells.append(
            f'<g class="f" style="animation-delay:{.3 + i * .1:.2f}s">'
            f'<text class="s" x="{x}" y="{y}" font-size="36" font-weight="700" fill="{FG}" letter-spacing="-.5">{t(num)}</text>'
            f'{label(x, y + 26, cap)}</g>'
        )
    body = (
        
        f'<text class="s" x="32" y="46" font-size="21" font-weight="700" fill="{FG}">GitHub, last 12 months</text>'
        + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{SURFACE}" stroke-width="8"/>'
        + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ACCENT}" stroke-width="8" stroke-linecap="round" '
        f'transform="rotate(-90 {cx} {cy})" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}">'
        f'<animate attributeName="stroke-dashoffset" from="{circ:.1f}" to="{circ * .12:.1f}" dur="1.8s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".22 1 .36 1"/></circle>'
        + f'<circle class="p" cx="{cx}" cy="{cy - r}" r="3" fill="{FG}"/>'
        + f'<text class="s f" x="{cx}" y="{cy + 6}" font-size="30" font-weight="700" fill="{FG}" text-anchor="middle">{a["total"]:,}</text>'
        + f'<text class="s" x="{cx}" y="{cy + 30}" font-size="16" fill="{MUTED}" text-anchor="middle">contributions</text>'
        + "".join(cells)
        + f'<line class="w" x1="32" y1="{h - 46}" x2="{w - 32}" y2="{h - 46}" stroke="{LINE}"/>'
        + label(32, h - 22, f'Streak {a["current"]}d · longest {a["longest"]}d · best day {a["best"]}')
    )
    return svg(w, h, body, f'{a["total"]} contributions in the last year')


def languages(a):
    w, h = 590, 330
    x0, bw = 32, w - 64
    bar, x = [], x0
    for i, (n, frac, col) in enumerate(a["langs"]):
        seg = bw * frac / sum(f for _, f, _ in a["langs"])
        bar.append(f'<rect class="w" style="animation-delay:{.2 + i * .08:.2f}s" x="{x:.1f}" y="72" width="{max(seg - 2, 1):.1f}" height="10" fill="{col}"/>')
        x += seg
    rows = []
    for i, (n, frac, col) in enumerate(a["langs"]):
        cx, y = x0 + (i % 2) * 270, 130 + (i // 2) * 48
        rows.append(
            f'<g class="f" style="animation-delay:{.4 + i * .06:.2f}s">{square(cx, y - 12, col, 10)}'
            f'<text class="s" x="{cx + 20}" y="{y}" font-size="19" font-weight="700" fill="{FG}">{t(n)}</text>'
            f'<text class="m" x="{cx + 250}" y="{y}" font-size="16" fill="{MUTED}" text-anchor="end">{frac * 100:.1f}%</text>'
            f'<line x1="{cx}" y1="{y + 12}" x2="{cx + 250}" y2="{y + 12}" stroke="{LINE}"/></g>'
        )
    body = (
        
        f'<text class="s" x="32" y="46" font-size="21" font-weight="700" fill="{FG}">Languages across my repos</text>'
        + "".join(bar) + "".join(rows)
    )
    return svg(w, h, body, "Languages across repositories")


def contrib_iso(a):
    """Isometric year of contributions: colour = GitHub's level, height = log-softened count."""
    import math
    w, h = 1200, 580
    days = a["days"]
    lvl = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    sx, sy = 11.5, 6.6  # half-width / half-height of one tile
    ox, oy = 260, 150
    cells, months, last_m = [], [], None
    for i, d in enumerate(days):
        wk, dow = divmod(i, 7)
        x = ox + (wk - dow) * sx
        y = oy + (wk + dow) * sy
        n, L = d["contributionCount"], lvl[d["contributionLevel"]]
        hgt = 2 + (math.log1p(n) * 16 if n else 0)
        top = LEVELS[L]
        left = "#0d0c0c" if not L else LEVELS[max(L - 1, 0)]
        right = "#121110" if not L else "#1f1b3a"
        delay = .2 + wk * .025
        g = (
            f'<g class="g" style="animation-delay:{delay:.2f}s,{2 + (wk % 9) * .4:.1f}s">'
            f'<path d="M{x:.1f} {y:.1f} l{sx} {sy} v-{hgt:.1f} l-{sx} -{sy} z" fill="{left}"/>'
            f'<path d="M{x + sx:.1f} {y + sy:.1f} l{sx} -{sy} v-{hgt:.1f} l-{sx} {sy} z" fill="{right}"/>'
            f'<path d="M{x:.1f} {y - hgt:.1f} l{sx} -{sy} l{sx} {sy} l-{sx} {sy} z" fill="{top}"/></g>'
        ) if n else (
            f'<path d="M{x:.1f} {y:.1f} l{sx} -{sy} l{sx} {sy} l-{sx} {sy} z" fill="{LEVELS[0]}" stroke="#000" stroke-width=".4"/>'
        )
        cells.append(g)
        m = d["date"][5:7]
        if dow == 0 and m != last_m:
            first = last_m is None
            last_m = m
            if first:
                continue  # the partial first month would crowd the next label
            months.append(label(x - 30, y + 40, datetime.strptime(d["date"], "%Y-%m-%d").strftime("%b")))
    boxes = [(f'{a["total"]:,}', "Total"), (str(a["week"]), "This week"), (str(a["best"]), f'Best day · {fmt_date(a["best_date"])}')]
    stat = []
    for i, (num, cap) in enumerate(boxes):
        x = 730 + i * 140
        stat.append(
            f'<g class="f" style="animation-delay:{.4 + i * .1:.2f}s"><text class="s" x="{x}" y="98" font-size="36" font-weight="700" fill="{ACCENT if i == 0 else FG}">{t(num)}</text>'
            f'{label(x, 124, cap)}</g>'
        )
    streak = (
        f'<g class="f" style="animation-delay:1s"><text class="s" x="64" y="{h - 80}" font-size="36" font-weight="700" fill="{FG}">{a["longest"]}<tspan font-size="18" fill="{MUTED}"> days</tspan></text>'
        f'{label(64, h - 54, "Longest streak")}'
        f'<text class="s" x="240" y="{h - 80}" font-size="36" font-weight="700" fill="{FG}">{a["current"]}<tspan font-size="18" fill="{MUTED}"> days</tspan></text>'
        f'{label(240, h - 54, "Current streak")}</g>'
    )
    legend = "".join(f'<rect x="{1036 + i * 16}" y="{h - 44}" width="12" height="12" fill="{c}"/>' for i, c in enumerate(LEVELS))
    body = (
        
        f'<text class="s" x="64" y="56" font-size="21" font-weight="700" fill="{FG}">Contributions, last 12 months</text>'
        + f'<line x1="706" y1="40" x2="706" y2="132" stroke="{LINE}"/>'
        + "".join(cells) + "".join(months) + "".join(stat) + streak
        + label(1026, h - 32, "Less", anchor="end") + legend + label(1136, h - 31, "More")
    )
    return svg(w, h, body, f'Isometric contribution chart, {a["total"]} contributions')


def contrib_grid(a):
    """Flat year grid; the mascot strolls along the top edge, a light follows below."""
    w, h = 1200, 270
    days = a["days"]
    lvl = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    s, gap, ox, oy = 11, 3, 64, 112
    weeks = (len(days) + 6) // 7
    cells = []
    for i, d in enumerate(days):
        wk, dow = divmod(i, 7)
        L = lvl[d["contributionLevel"]]
        cls = f' class="p" style="animation-delay:{(wk * 7 + dow) % 23 * .17:.2f}s"' if L == 4 else ""
        cells.append(f'<rect{cls} x="{ox + wk * (s + gap)}" y="{oy + dow * (s + gap)}" width="{s}" height="{s}" rx="2" fill="{LEVELS[L]}"/>')
    gw = weeks * (s + gap)
    # activity mix, after GitHub's overview: commits / PRs / issues / reviews
    mix = [("Commits", a["commits"]), ("Pull requests", a["prs"]), ("Issues", a["issues"]), ("Code review", a["reviews"])]
    tot = sum(v for _, v in mix) or 1
    mx = []
    for i, (n, v) in enumerate(mix):
        y = 124 + i * 34
        frac = v / tot
        mx.append(
            f'<text class="s" x="{ox + gw + 48}" y="{y}" font-size="18" fill="{FG}">{t(n)}</text>'
            f'<text class="m" x="{w - 64}" y="{y}" font-size="16" fill="{MUTED}" text-anchor="end">{frac * 100:.0f}%</text>'
            f'<rect x="{ox + gw + 48}" y="{y + 9}" width="{w - 64 - ox - gw - 48}" height="4" fill="{SURFACE}"/>'
            f'<rect class="w" style="animation-delay:{.5 + i * .1:.2f}s" x="{ox + gw + 48}" y="{y + 9}" width="{max((w - 64 - ox - gw - 48) * frac, 1):.1f}" height="4" fill="{ACCENT}"/>'
        )
    walk = f'<animateTransform attributeName="transform" type="translate" values="0 0;{gw - 30} 0;0 0" keyTimes="0;.5;1" dur="26s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
    flip = f'<animateTransform attributeName="transform" type="scale" values="1 1;1 1;-1 1;-1 1" keyTimes="0;.499;.5;1" dur="26s" repeatCount="indefinite" calcMode="discrete"/>'
    cat = (
        f'<g>{walk}<rect x="{ox}" y="{oy - 4}" width="30" height="2" fill="{ACCENT}" opacity=".7"/>'
        f'<g transform="translate({ox + 15} 0)"><g>{flip}<image href="{MASCOT}" x="-17" y="{oy - 40}" width="34" height="34"/></g></g></g>'
    )
    body = (
        
        f'<text class="s" x="64" y="46" font-size="21" font-weight="700" fill="{FG}">Every day of the year</text>'
        + f'<text class="s" x="{ox + gw + 48}" y="46" font-size="21" font-weight="700" fill="{FG}">Activity mix</text>'
        + "".join(cells) + cat + "".join(mx)
    )
    return svg(w, h, body, "Contribution grid with the mascot walking across it, and activity mix")


# --- live "now" card ----------------------------------------------------------


def gql(query):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def rest(path):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={"Authorization": f"bearer {token}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError:
        return None


def recent_repos(limit=6):
    """Repos I pushed to most recently, private ones included, with my latest commit in each."""
    if not (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")):
        return None
    repos = rest("user/repos?per_page=40&sort=pushed&affiliation=owner,collaborator,organization_member") or []
    rows = []
    for r in repos:
        if r["full_name"] in (f"{USER}/{USER}", f"{USER}/github-readme"):
            continue  # bot-updated stats repos would always top the list
        commits = rest(f'repos/{r["full_name"]}/commits?author={USER}&per_page=1')
        if not commits:
            continue  # pushed by someone else
        c = commits[0]["commit"]
        rows.append((r["full_name"], c["author"]["date"][:10], r["language"] or "", c["message"].splitlines()[0], r["private"]))
        if len(rows) == limit:
            break
    return sorted(rows, key=lambda x: x[1], reverse=True)


def now(rows):
    w = 1200
    h = 80 + len(rows) * 64 + 24
    stamp = datetime.now(timezone.utc).strftime("%d %b %Y")
    body = [
        f'<circle class="rp" cx="68" cy="44" r="4" fill="none" stroke="{ACCENT}"/><rect x="64" y="40" width="8" height="8" fill="{ACCENT}"/>',
        label(82, 49, "Recently pushed"),
        label(w - 64, 49, f"updated {stamp}", anchor="end"),
    ]
    for i, (repo, date, lang, msg, private) in enumerate(rows):
        y = 116 + i * 64
        msg = msg[:20] + "-" * min(max(len(msg) - 20, 0), 8)  # first 20 chars; dashes hide the rest
        owner, name = repo.split("/")
        owner = owner if len(owner) <= 12 else owner[:11] + "…"
        body.append(
            f'<g class="f" style="animation-delay:{i * .1:.2f}s">'
            f'<text class="s" x="64" y="{y}" font-size="22" fill="{MUTED}">{t(owner)}/<tspan font-weight="700" fill="{FG}">{t(name)}</tspan></text>'
            + (f'<text class="m" x="{74 + len(owner + name) * 12.2:.0f}" y="{y}" font-size="13" fill="{ACCENT}">PRIVATE</text>' if private else "")
            + f''
            f'<text class="m" x="600" y="{y}" font-size="16" fill="{MUTED}">{t(msg)}</text>'
            f'<text class="m" x="{w - 64}" y="{y}" font-size="16" fill="{MUTED}" text-anchor="end">{t(f"{lang}  ·  {date}" if lang else date)}</text>'
            f'<line class="w" style="animation-delay:{.2 + i * .1:.2f}s" x1="64" y1="{y + 28}" x2="{w - 64}" y2="{y + 28}" stroke="{LINE}"/></g>'
        )
    return svg(w, h, "".join(body), "Recently pushed repositories")


def bust_cache():
    """Version every image link so browsers and GitHub's image cache fetch fresh cards."""
    import re
    readme = OUT.parent / "README.md"
    v = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    text = re.sub(r'(assets/[\w-]+\.svg)(\?v=\w+)?', rf"\1?v={v}", readme.read_text())
    readme.write_text(text)


def main():
    OUT.mkdir(exist_ok=True)
    cards = {
        "header.svg": header(),
        "stats.svg": stats(),
        "available.svg": available(),
        "publications.svg": publications(),
        "footer.svg": footer(),
        "role-ledgercross.svg": role(
            "Ledgercross", "Software Developer (AI & DevOps)", "Feb 2026 – Now",
            [
                "Veritas: KYC-as-a-service rebuilt on scale-to-zero GCP. Google OCR, InsightFace face match and liveness, hosted links and webhooks.",
                "ODIN: real-time deepfake detection on YouTube, TikTok and X. MV3 extension, FastAPI orchestrator and Gemini agent on Cloud Run.",
                "APRON: AI procurement negotiator. AI proposes, deterministic code verifies, policy decides, humans approve.",
                "ACROA: contract risk agent with deterministic renewal math and a deny-by-default policy gate.",
                "Keptcash: AI accounts-receivable employee that diagnoses unpaid invoices and drafts the follow-up.",
            ],
            "ledgercross.com",
        ),
        "role-arche.svg": role(
            "Arché Intelligence Lab", "Co-founder & Operations Director", "May 2024 – Now",
            [
                "Co-founded a non-profit, student-led AI research lab with collaborators across four countries.",
                "Supervise the Computer Vision & Medical-AI track: brain MRI, ophthalmic imaging, skin lesions, federated and explainable diagnosis.",
                "Mentor student researchers from first idea to peer-reviewed paper.",
                "Assisted on 24 of the lab's peer-reviewed publications, 13 of which I co-authored, across medical imaging, explainable AI and Bengali NLP.",
            ],
            "archelab.org",
        ),
        "project-veritas.svg": project(
            "Veritas", "Ledgercross · Identity",
            "KYC-as-a-service: document OCR, face match with liveness, operator dashboard and webhooks on serverless GCP.",
            "FastAPI · InsightFace · Cloud Run · Postgres", "private", motif_idcard(), "ledgercross",
        ),
        "project-apron.svg": project(
            "APRON", "Ledgercross · Procurement",
            "AI procurement negotiator with an evidence-backed ledger of quotes, contracts and savings. Humans approve high-impact moves.",
            "Python · React · Postgres RLS · Doppler", "private", motif_negotiate(), "ledgercross",
        ),
        "project-keptcash.svg": project(
            "Keptcash", "Ledgercross · Receivables",
            "The AI accounts-receivable employee: finds why each invoice is unpaid, drafts the email, tracks promises, reports dollars recovered.",
            "FastAPI · Next.js · QuickBooks · Gmail", "private", motif_invoice(), "ledgercross",
        ),
        "project-wifirank.svg": project(
            "WifiRank", "Personal · Live",
            "Crowdsourced speed tests and reviews for Dhaka ISPs, run on a live map and ranked per neighbourhood.",
            "Astro · React · Neon · MapLibre", "wifirank.site", motif_signal(), "wifirank",
        ),
    }
    act = activity_data()
    if act:
        cards.update({
            "activity-overview.svg": overview(act),
            "activity-languages.svg": languages(act),
            "activity-iso.svg": contrib_iso(act),
            "activity-grid.svg": contrib_grid(act),
        })
    rows = recent_repos()
    if rows:
        cards["now.svg"] = now(rows)
    elif not (OUT / "now.svg").exists():
        cards["now.svg"] = now([("Sou-hardo/wifirank", "", "TypeScript", "set GH_TOKEN to load live data", False)])
    for name, content in cards.items():
        (OUT / name).write_text(content)
    bust_cache()
    print("wrote", ", ".join(cards))


if __name__ == "__main__":
    main()
