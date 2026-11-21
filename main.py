#!/usr/bin/env python3
"""makefun news-image-20261120 round 2 — "THE WORLD IN ONE DAY".

A deterministic, code-drawn newspaper front page for Friday 20 November 2026.
Everything (layout, text, all 13 illustrations, the schematic map) is drawn
with Pillow primitives from the data embedded below. No network, no random
numbers, no timestamps, no external assets — two runs produce byte-identical
output. Run:  python3 main.py   ->  entry.png  (1024x1024, RGB, <=1 MiB).
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

PAPER = (247, 243, 232)
INK = (18, 18, 18)
GREY = (96, 94, 88)
LIGHT = (214, 208, 194)
RED = (176, 30, 36)
BLUE = (28, 68, 118)
TEAL = (14, 96, 90)
GOLD = (176, 128, 28)
SKY = (174, 205, 226)
SEA = (196, 216, 228)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def wrap(d, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit inside width px."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, width, text, fnt, fill=INK, leading=None, max_lines=None):
    """Draw wrapped text; returns y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.22)
    lines = wrap(d, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def rule(d, x0, x1, y, fill=INK, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def tag(d, x, y, label, fill=RED):
    """Small red caps tag, e.g. CLAIM / FORECAST / REPORTED."""
    f = font(SANS_B, 9)
    tw = d.textlength(label, font=f)
    d.rectangle([x, y, x + tw + 10, y + 13], fill=fill)
    d.text((x + 5, y + 1), label, font=f, fill=(255, 255, 255))
    return x + tw + 14


# ---------------------------------------------------------------- data
STRIP = [
    ("515", "weapons fired at Kyiv overnight", "Reuters"),
    ("300,000+", "people evacuated for Cyclone Akvan", "IMD"),
    ("-6.2%", "Taiwan stocks, worst week since 1991", "AP"),
    ("2.3%", "Japan inflation, October", "Reuters"),
    ("118", "runs: Glenn Phillips v India", "ICC"),
    ("$3.8bn", "GTA VI day-one sales", "Reuters"),
]

REGIONS = [
    ("EUROPE", RED), ("MIDDLE EAST", (122, 74, 18)), ("ASIA", BLUE),
    ("AFRICA", (42, 110, 62)), ("AMERICAS", (96, 52, 120)),
    ("SPORT", (14, 96, 90)), ("MARKETS", (120, 40, 40)),
]

LEADS = [
    dict(n=1, kicker="KYIV  •  UKRAINE", head="Missiles strike Kyiv bridges in overnight barrage",
         body=("About 515 weapons — 27 ballistic and 84 cruise missiles plus 404 drones, "
               "Reuters reports — hit three bridges overnight. Eight to nine people were "
               "killed and power and water were cut across the capital."),
         src="Reuters  •  Kyiv Independent  •  BBC", tag="REPORTED"),
    dict(n=2, kicker="CYCLONE AKVAN  •  INDIA", head="Cyclone Akvan hits Odisha coast; 300,000 evacuated",
         body=("Akvan made landfall near Gopalpur around 08:00 with winds of 90–100 km/h, "
               "gusting to 110. More than 300,000 people were moved to safety, 423 rescue "
               "teams were deployed, and no deaths were reported."),
         src="IMD  •  Deccan Herald  •  PTI", tag=None),
    dict(n=3, kicker="AI SELL-OFF  •  MARKETS", head="AI sell-off sweeps Asia as Taiwan sinks 6.2%",
         body=("Taiwan fell 6.2% in its worst week since 1991; Seoul's KOSPI dropped 5.2% "
               "below 5,000 and Tokyo's Nikkei 5.1%. The Nasdaq lost 5.3% and the S&P 3.7%."),
         src="AP  •  Al Jazeera  •  Anadolu", tag=None),
]

FEATURES = [
    dict(n=4, kicker="COP31  •  ANTALYA", head="COP31 ends with no deal",
         body=("The final day closed without agreement: the draft omits fossil fuels, a "
               "$120bn finance gap remains, and the “35 by 35” target is unmet."),
         src="UN News • Reuters"),
    dict(n=5, kicker="UK–EU  •  LONDON", head="UK and EU strike first big post-Brexit “reset”",
         body=("A deal on food trade, youth visas and a carbon link — the largest reset of "
               "relations since Brexit."),
         src="Reuters"),
    dict(n=6, kicker="JAPAN  •  TOKYO", head="Japan inflation holds at 2.3% in October",
         body=("Core inflation was 2.2%, keeping the Bank of Japan in focus ahead of its "
               "next decision."),
         src="Reuters"),
    dict(n=7, kicker="KENYA  •  TURKANA", head="Kenya drills its first oil well",
         body=("Drilling begins in the Turkana basin; first oil is expected on 1 December."),
         src="allAfrica"),
    dict(n=8, kicker="EL SALVADOR", head="Bukele seeks a third term",
         body=("The president filed for a third term; voters decide on 28 February 2027."),
         src="AP"),
    dict(n=9, kicker="ITALY  •  ROME", head="General strike paralyses Italy over budget",
         body=("Workers and students marched nationwide in a 24-hour CGIL strike against "
               "the budget."),
         src="Reuters"),
    dict(n=10, kicker="CRICKET  •  WELLINGTON", head="Phillips hits 118 as NZ beat India",
         body=("Glenn Phillips reached hundreds in every format in Wellington."),
         src="ICC"),
    dict(n=11, kicker="SOUTH KOREA  •  SEOUL", head="Ruling party moves to impeach top judge",
         body=("The move follows a ruling that overturned a conviction, the Korea Herald "
               "reports."),
         src="Korea Herald"),
    dict(n=12, kicker="IRAQ", head="Iraqi troops enter militia stronghold",
         body=("Soldiers moved into the Jurf al-Sakhar fortress in a rare operation against "
               "the militia."),
         src="Reuters"),
    dict(n=13, kicker="POLAND", head="Russian cruise missile crashes in Poland",
         body=("The missile came down in a field; two airports paused operations."),
         src="Reuters"),
]

BRIEFS = [
    ("Lviv", "rail station strike kills two", "BBC"),
    ("Moscow", "Russia says Estonia border closed", "Reuters"),
    ("Berlin", "students strike against conscription", "Al Jazeera"),
    ("London", "general: UK runs cyber attacks abroad", "Sky News", "CLAIM"),
    ("Beijing", "China holds loan rates for 18th month", "Xinhua"),
    ("Tokyo", "SoftBank shares fall 14%+ in a day", "Al Jazeera"),
    ("Seoul", "KOSPI ends week 7.9% lower", "Anadolu"),
    ("Ganjam", "209 mm rain as Akvan crossed Odisha", "PTI"),
    ("Lebanon", "Israeli air strikes hit south and east", "Anadolu"),
    ("Yemen", "gunman fires on cargo ship off coast", "UKMTO"),
    ("Abuja", "court bars new evidence against Tinubu", "Channels TV"),
    ("Kampala", "police told to enforce Ebola ban on rallies", "allAfrica"),
    ("Malawi", "fuel crisis, overnight petrol queues", "Al Jazeera"),
    ("Africa", "AfDB: 22 nations in debt distress", "allAfrica"),
    ("Las Vegas", "Russell fastest in wet GP practice", "Autosport"),
    ("New York", "Nasdaq futures down 1.6% pre-bell", "24/7 Wall St", "FORECAST"),
    ("Washington", "Democrats question law firms' free work", "Al Jazeera"),
    ("Wellington", "Nicholls 175 in 216-run stand with Phillips", "ICC"),
    ("Sydney", "Australian shares fall 1.8%", "Reuters"),
    ("Antalya", "Panama asks COP31 to cap world oil output", "Anadolu"),
    ("Turin", "ATP backs plan to lift player pay above $350m", "Anadolu"),
    ("Peru", "6.7 quake near Carhuamayo, felt in Lima", "USGS"),
    ("Space", "BepiColombo reaches Mercury after 8-year trip", "ESA • BBC"),
    ("Brussels", "EU agrees €1bn military aid for Kyiv", "EU Council"),
    ("Hormuz", "46 ships wait; Brent nears $92.50", "Straits Times"),
]

DATE_CHECK = (
    "LEFT OUT ON PURPOSE — Thursday 19 Nov: the ICJ ruling on Myanmar; the Trump–Xi–Putin "
    "summit in Shenzhen; the APEC Shenzhen declaration; the second COP31 draft; the Riyadh tower "
    "attack; Colombia tax protests; Wall Street's 2% fall. Saturday 21 Nov: BepiColombo's Mercury "
    "orbit entry. Not yet published at press time: the COP31 final text and Asia's closing prices."
)


# ------------------------------------------------------- illustrations
# Each draws one distinct hand-drawn-style vector scene inside (x0,y0,x1,y1).
# Colours and shapes are fixed constants: fully deterministic.

def illo_kyiv(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(16, 22, 44))
    for sx, sy in [(0.12, 0.2), (0.3, 0.12), (0.55, 0.18), (0.78, 0.1), (0.9, 0.25)]:
        d.ellipse([x0 + sx * (x1 - x0) - 1, y0 + sy * (y1 - y0) - 1,
                   x0 + sx * (x1 - x0) + 1, y0 + sy * (y1 - y0) + 1], fill=(255, 255, 220))
    w, h = x1 - x0, y1 - y0
    # skyline
    base = y0 + h * 0.78
    for bx, bw, bh in [(0.02, 0.13, 0.42), (0.17, 0.1, 0.55), (0.29, 0.14, 0.36),
                       (0.45, 0.09, 0.62), (0.56, 0.13, 0.44), (0.71, 0.11, 0.58),
                       (0.84, 0.13, 0.4)]:
        d.rectangle([x0 + bx * w, base - bh * h, x0 + (bx + bw) * w, base], fill=(8, 10, 26))
        for wy in range(3):
            d.rectangle([x0 + (bx + 0.02) * w, base - bh * h + 6 + wy * 12,
                         x0 + (bx + 0.05) * w, base - bh * h + 12 + wy * 12], fill=(255, 214, 110))
    # bridge arc + fire
    d.arc([x0 + 0.05 * w, base - 6, x0 + 0.95 * w, base + h * 0.3], 180, 360, fill=(120, 130, 160), width=3)
    d.line([(x0 + 0.08 * w, base + 2), (x0 + 0.92 * w, base + 2)], fill=(120, 130, 160), width=3)
    for fx in (0.3, 0.62):
        d.polygon([(x0 + fx * w, base - 26), (x0 + (fx + 0.05) * w, base - 2),
                   (x0 + (fx - 0.02) * w, base - 2)], fill=(255, 120, 20))
        d.polygon([(x0 + (fx + 0.01) * w, base - 16), (x0 + (fx + 0.035) * w, base - 2),
                   (x0 + (fx - 0.005) * w, base - 2)], fill=(255, 210, 60))
    # missile trails
    for mx, my, ang in [(0.2, 0.62, -38), (0.55, 0.5, -52), (0.85, 0.58, -30)]:
        ex, ey = x0 + mx * w, y0 + my * h
        d.line([(ex, ey), (ex + 46, ey - 30)], fill=(255, 200, 90), width=2)
        d.ellipse([ex + 44, ey - 34, ex + 50, ey - 26], fill=(255, 240, 180))
    d.rectangle([x0, y1 - 14, x1, y1], fill=(8, 10, 26))


def illo_cyclone(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=SEA)
    w, h = x1 - x0, y1 - y0
    # Bay of Bengal coastline (stylised)
    d.polygon([(x0 + 0.08 * w, y0 + 0.05 * h), (x0 + 0.42 * w, y0 + 0.12 * h),
               (x0 + 0.55 * w, y0 + 0.4 * h), (x0 + 0.5 * w, y0 + 0.75 * h),
               (x0 + 0.3 * w, y0 + 0.95 * h), (x0 + 0.1 * w, y0 + 0.9 * h),
               (x0 + 0.02 * w, y0 + 0.5 * h)], fill=(222, 206, 164))
    d.polygon([(x0 + 0.6 * w, y0 + 0.3 * h), (x0 + 0.98 * w, y0 + 0.2 * h),
               (x0 + 0.98 * w, y0 + 0.9 * h), (x0 + 0.72 * w, y0 + 0.95 * h),
               (x0 + 0.62 * w, y0 + 0.6 * h)], fill=(206, 222, 190))
    # cyclone spiral
    cx, cy = x0 + 0.62 * w, y0 + 0.52 * h
    for r, col in [(52, (255, 255, 255)), (40, (210, 225, 240)), (28, (255, 255, 255)),
                   (16, (160, 190, 215))]:
        d.arc([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], 20, 300, fill=col, width=5)
    d.ellipse([cx - 7, cy - 6, cx + 7, cy + 6], fill=(255, 255, 255), outline=BLUE, width=2)
    d.text((cx - 35, cy - 22), "AKVAN", font=font(SANS_B, 10), fill=RED)
    d.text((x0 + 0.06 * w, y0 + 0.06 * h), "BAY OF BENGAL", font=font(SANS_B, 9), fill=BLUE)


def illo_chart_fall(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(255, 250, 244))
    w, h = x1 - x0, y1 - y0
    for i in range(5):
        gy = y0 + 12 + i * (h - 24) // 4
        d.line([(x0 + 8, gy), (x1 - 8, gy)], fill=(226, 220, 206), width=1)
    pts = [(0.06, 0.22), (0.2, 0.3), (0.34, 0.26), (0.48, 0.48), (0.62, 0.44),
           (0.74, 0.66), (0.86, 0.72), (0.96, 0.88)]
    xy = [(x0 + px * w, y0 + py * h) for px, py in pts]
    d.line(xy, fill=RED, width=4, joint="curve")
    for px, py in xy:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
    d.polygon([(xy[-1][0], xy[-1][1]), (xy[-1][0] - 16, xy[-1][1] - 2),
               (xy[-1][0] - 4, xy[-1][1] + 12)], fill=RED)
    d.text((x0 + 10, y0 + 8), "TAIWAN  −6.2%", font=font(SANS_B, 13), fill=RED)
    d.text((x0 + 10, y0 + h - 16), "KOSPI  −5.2%   NIKKEI  −5.1%", font=font(SANS_B, 10), fill=INK)


def illo_cop(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(226, 238, 226))
    w, h = x1 - x0, y1 - y0
    cx, cy, r = x0 + 0.36 * w, y0 + 0.52 * h, min(w, h) * 0.32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 150, 200), outline=BLUE, width=3)
    d.ellipse([cx - r * 0.55, cy - r * 0.7, cx + r * 0.15, cy - r * 0.1], fill=(110, 180, 110))
    d.ellipse([cx - r * 0.1, cy + r * 0.25, cx + r * 0.6, cy + r * 0.75], fill=(110, 180, 110))
    d.ellipse([cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8], outline=(255, 255, 255), width=2)
    # thermometer
    tx = x0 + 0.78 * w
    d.rounded_rectangle([tx - 7, y0 + 0.14 * h, tx + 7, y0 + 0.82 * h], radius=7, fill=(255, 255, 255), outline=RED, width=2)
    d.ellipse([tx - 13, y0 + 0.76 * h, tx + 13, y0 + 0.98 * h], fill=RED)
    d.rectangle([tx - 3, y0 + 0.3 * h, tx + 3, y0 + 0.82 * h], fill=RED)
    d.text((x0 + 0.06 * w, y0 + 0.05 * h), "COP31", font=font(SANS_B, 13), fill=TEAL)
    d.text((x0 + 0.06 * w, y0 + 0.2 * h), "ANTALYA", font=font(SANS_B, 10), fill=INK)


def illo_flags(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(240, 238, 230))
    w, h = x1 - x0, y1 - y0
    # Union Jack (stylised)
    ux, uy, uw, uh = x0 + 0.06 * w, y0 + 0.16 * h, 0.4 * w, 0.52 * h
    d.rectangle([ux, uy, ux + uw, uy + uh], fill=(28, 58, 120))
    d.polygon([(ux, uy), (ux + uw, uy + uh), (ux + uw, uy + uh - 8), (ux + 8, uy)], fill=(255, 255, 255))
    d.polygon([(ux + uw, uy), (ux, uy + uh), (ux, uy + uh - 8), (ux + uw - 8, uy)], fill=(255, 255, 255))
    d.line([(ux + uw / 2, uy), (ux + uw / 2, uy + uh)], fill=(255, 255, 255), width=10)
    d.line([(ux, uy + uh / 2), (ux + uw, uy + uh / 2)], fill=(255, 255, 255), width=10)
    d.line([(ux + uw / 2, uy), (ux + uw / 2, uy + uh)], fill=RED, width=5)
    d.line([(ux, uy + uh / 2), (ux + uw, uy + uh / 2)], fill=RED, width=5)
    # EU flag
    ex, ey, ew, eh = x0 + 0.54 * w, y0 + 0.16 * h, 0.4 * w, 0.52 * h
    d.rectangle([ex, ey, ex + ew, ey + eh], fill=(0, 51, 153))
    import math
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx, sy = ex + ew / 2 + math.cos(a) * ew * 0.3, ey + eh / 2 + math.sin(a) * eh * 0.32
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    d.text((x0 + 0.06 * w, y0 + 0.74 * h), "UK  ×  EU  RESET", font=font(SANS_B, 11), fill=INK)


def illo_bars_up(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(255, 250, 244))
    w, h = x1 - x0, y1 - y0
    vals = [0.3, 0.42, 0.38, 0.55, 0.62, 0.78]
    bw = w * 0.11
    for i, v in enumerate(vals):
        bx = x0 + 0.08 * w + i * w * 0.15
        by = y0 + h * 0.88 - v * h * 0.62
        col = RED if i == len(vals) - 1 else BLUE
        d.rectangle([bx, by, bx + bw, y0 + h * 0.88], fill=col)
    d.line([(x0 + 0.05 * w, y0 + h * 0.88), (x1 - 0.04 * w, y0 + h * 0.88)], fill=INK, width=2)
    d.text((x0 + 0.08 * w, y0 + 0.06 * h), "JAPAN  2.3%", font=font(SANS_B, 13), fill=RED)
    d.text((x0 + 0.08 * w, y0 + 0.24 * h), "core 2.2%", font=font(SANS_B, 10), fill=GREY)


def illo_rig(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(250, 196, 120))
    w, h = x1 - x0, y1 - y0
    d.ellipse([x0 + 0.68 * w, y0 + 0.1 * h, x0 + 0.9 * w, y0 + 0.32 * h], fill=(255, 214, 90))
    d.rectangle([x0, y0 + 0.72 * h, x1, y1], fill=(120, 84, 44))
    # derrick
    bx, by = x0 + 0.3 * w, y0 + 0.72 * h
    d.polygon([(bx, by - h * 0.55), (bx + w * 0.16, by - h * 0.55),
               (bx + w * 0.24, by), (bx - w * 0.08, by)], outline=INK, width=3)
    d.line([(bx, by - h * 0.55), (bx + w * 0.24, by)], fill=INK, width=2)
    d.line([(bx + w * 0.16, by - h * 0.55), (bx - w * 0.08, by)], fill=INK, width=2)
    d.line([(bx + w * 0.02, by - h * 0.4), (bx + w * 0.18, by - h * 0.28)], fill=INK, width=2)
    d.line([(bx + w * 0.02, by - h * 0.2), (bx + w * 0.2, by - h * 0.45)], fill=INK, width=2)
    # pumpjack
    d.line([(x0 + 0.62 * w, y0 + 0.72 * h), (x0 + 0.62 * w, y0 + 0.45 * h)], fill=INK, width=3)
    d.polygon([(x0 + 0.5 * w, y0 + 0.45 * h), (x0 + 0.86 * w, y0 + 0.52 * h),
               (x0 + 0.84 * w, y0 + 0.58 * h), (x0 + 0.52 * w, y0 + 0.52 * h)], fill=INK)
    d.text((x0 + 0.06 * w, y0 + 0.05 * h), "TURKANA", font=font(SANS_B, 11), fill=(90, 50, 10))


def illo_ballot(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(232, 236, 244))
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0 + 0.22 * w, y0 + 0.42 * h, x0 + 0.78 * w, y0 + 0.88 * h], fill=(255, 255, 255), outline=BLUE, width=3)
    d.rectangle([x0 + 0.42 * w, y0 + 0.42 * h, x0 + 0.58 * w, y0 + 0.5 * h], fill=INK)
    d.text((x0 + 0.28 * w, y0 + 0.58 * h), "✓", font=font(SANS_B, 22), fill=TEAL)
    d.text((x0 + 0.42 * w, y0 + 0.6 * h), "VOTE", font=font(SANS_B, 13), fill=INK)
    # ballot paper going in
    d.polygon([(x0 + 0.38 * w, y0 + 0.12 * h), (x0 + 0.62 * w, y0 + 0.12 * h),
               (x0 + 0.58 * w, y0 + 0.46 * h), (x0 + 0.42 * w, y0 + 0.46 * h)], fill=(255, 255, 255), outline=INK)
    d.line([(x0 + 0.44 * w, y0 + 0.22 * h), (x0 + 0.56 * w, y0 + 0.22 * h)], fill=GREY, width=2)
    d.line([(x0 + 0.44 * w, y0 + 0.3 * h), (x0 + 0.56 * w, y0 + 0.3 * h)], fill=GREY, width=2)
    d.text((x0 + 0.06 * w, y0 + 0.05 * h), "3rd TERM?", font=font(SANS_B, 11), fill=RED)


def illo_strike(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(245, 238, 220))
    w, h = x1 - x0, y1 - y0
    # crowd heads
    for i, hx in enumerate([0.14, 0.3, 0.46, 0.62, 0.78, 0.9]):
        d.ellipse([x0 + hx * w - 9, y0 + 0.78 * h, x0 + hx * w + 9, y0 + 0.78 * h + 18], fill=(60, 50, 44))
    # placard
    d.rectangle([x0 + 0.16 * w, y0 + 0.14 * h, x0 + 0.84 * w, y0 + 0.52 * h], fill=(255, 255, 255), outline=INK, width=2)
    d.text((x0 + 0.2 * w, y0 + 0.2 * h), "SCIOPERO", font=font(SANS_B, 16), fill=RED)
    d.text((x0 + 0.2 * w, y0 + 0.38 * h), "24 ORE • CGIL", font=font(SANS_B, 10), fill=INK)
    d.line([(x0 + 0.3 * w, y0 + 0.52 * h), (x0 + 0.3 * w, y0 + 0.78 * h)], fill=INK, width=3)
    d.line([(x0 + 0.7 * w, y0 + 0.52 * h), (x0 + 0.7 * w, y0 + 0.78 * h)], fill=INK, width=3)


def illo_cricket(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(210, 232, 190))
    w, h = x1 - x0, y1 - y0
    # pitch
    d.polygon([(x0 + 0.3 * w, y0 + 0.1 * h), (x0 + 0.7 * w, y0 + 0.1 * h),
               (x0 + 0.9 * w, y0 + 0.95 * h), (x0 + 0.1 * w, y0 + 0.95 * h)], fill=(222, 200, 150))
    # bat
    d.polygon([(x0 + 0.42 * w, y0 + 0.18 * h), (x0 + 0.56 * w, y0 + 0.22 * h),
               (x0 + 0.62 * w, y0 + 0.62 * h), (x0 + 0.5 * w, y0 + 0.66 * h)], fill=(210, 170, 110), outline=INK)
    d.line([(x0 + 0.5 * w, y0 + 0.2 * h), (x0 + 0.44 * w, y0 + 0.05 * h)], fill=INK, width=4)
    # ball + stumps
    d.ellipse([x0 + 0.68 * w, y0 + 0.55 * h, x0 + 0.68 * w + 14, y0 + 0.55 * h + 14], fill=RED, outline=(120, 0, 0))
    for sx in (0.3, 0.36, 0.42):
        d.line([(x0 + sx * w, y0 + 0.78 * h), (x0 + sx * w, y0 + 0.92 * h)], fill=(255, 220, 60), width=3)
    d.text((x0 + 0.06 * w, y0 + 0.05 * h), "118", font=font(SERIF_B, 22), fill=RED)
    d.text((x0 + 0.06 * w, y0 + 0.32 * h), "PHILLIPS", font=font(SANS_B, 10), fill=INK)


def illo_court(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(228, 232, 238))
    w, h = x1 - x0, y1 - y0
    # courthouse
    d.polygon([(x0 + 0.1 * w, y0 + 0.42 * h), (x0 + 0.5 * w, y0 + 0.16 * h),
               (x0 + 0.9 * w, y0 + 0.42 * h)], fill=(120, 130, 150))
    d.rectangle([x0 + 0.14 * w, y0 + 0.44 * h, x0 + 0.86 * w, y0 + 0.86 * h], fill=(200, 208, 218))
    for cx in (0.22, 0.38, 0.54, 0.7):
        d.rectangle([x0 + cx * w, y0 + 0.48 * h, x0 + (cx + 0.07) * w, y0 + 0.86 * h], fill=(240, 242, 245))
    # gavel
    d.line([(x0 + 0.62 * w, y0 + 0.06 * h), (x0 + 0.9 * w, y0 + 0.3 * h)], fill=(90, 60, 30), width=5)
    d.rounded_rectangle([x0 + 0.66 * w, y0 + 0.02 * h, x0 + 0.86 * w, y0 + 0.14 * h], radius=4, fill=(120, 80, 40))
    d.text((x0 + 0.06 * w, y0 + 0.06 * h), "SEOUL", font=font(SANS_B, 11), fill=BLUE)


def illo_tank(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(232, 222, 190))
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0 + 0.7 * h, x1, y1], fill=(190, 170, 120))
    # palm
    d.line([(x0 + 0.85 * w, y0 + 0.7 * h), (x0 + 0.85 * w, y0 + 0.3 * h)], fill=(90, 60, 30), width=4)
    for dx, dy in [(-0.12, -0.06), (-0.1, 0.04), (0.12, -0.06), (0.1, 0.04), (0, -0.12)]:
        d.line([(x0 + 0.85 * w, y0 + 0.3 * h), (x0 + (0.85 + dx) * w, y0 + (0.3 + dy) * h)], fill=(50, 120, 60), width=3)
    # tank
    d.rectangle([x0 + 0.1 * w, y0 + 0.52 * h, x0 + 0.52 * w, y0 + 0.68 * h], fill=(90, 100, 60))
    d.rectangle([x0 + 0.18 * w, y0 + 0.4 * h, x0 + 0.42 * w, y0 + 0.54 * h], fill=(70, 80, 48))
    d.line([(x0 + 0.42 * w, y0 + 0.46 * h), (x0 + 0.72 * w, y0 + 0.42 * h)], fill=INK, width=4)
    for tx in (0.14, 0.24, 0.34, 0.44):
        d.ellipse([x0 + tx * w, y0 + 0.64 * h, x0 + (tx + 0.06) * w, y0 + 0.72 * h], fill=INK)
    d.text((x0 + 0.06 * w, y0 + 0.05 * h), "JURF AL-SAKHAR", font=font(SANS_B, 10), fill=INK)


def illo_missile_field(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(200, 220, 240))
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0 + 0.62 * h, x1, y1], fill=(150, 180, 90))
    for fx in range(8):
        d.line([(x0 + fx * w / 8, y0 + 0.66 * h), (x0 + fx * w / 8 + 6, y0 + 0.95 * h)], fill=(120, 150, 60), width=2)
    # missile angled down into field
    d.line([(x0 + 0.15 * w, y0 + 0.12 * h), (x0 + 0.62 * w, y0 + 0.58 * h)], fill=(200, 200, 200), width=8)
    d.polygon([(x0 + 0.62 * w, y0 + 0.58 * h), (x0 + 0.58 * w, y0 + 0.5 * h),
               (x0 + 0.7 * w, y0 + 0.56 * h)], fill=RED)
    d.line([(x0 + 0.1 * w, y0 + 0.08 * h), (x0 + 0.16 * w, y0 + 0.14 * h)], fill=(255, 200, 90), width=3)
    # smoke + crater
    d.ellipse([x0 + 0.55 * w, y0 + 0.55 * h, x0 + 0.75 * w, y0 + 0.68 * h], fill=(90, 80, 70))
    d.ellipse([x0 + 0.6 * w, y0 + 0.5 * h, x0 + 0.68 * w, y0 + 0.58 * h], fill=(220, 220, 220))
    d.text((x0 + 0.06 * w, y0 + 0.05 * h), "POLAND", font=font(SANS_B, 11), fill=RED)


ILLOS = [illo_kyiv, illo_cyclone, illo_chart_fall, illo_cop, illo_flags,
         illo_bars_up, illo_rig, illo_ballot, illo_strike, illo_cricket,
         illo_court, illo_tank, illo_missile_field]


# ------------------------------------------------------------- layout
MX = 28  # side margin
RX = W - MX


def draw_map(d, x0, y0, x1, y1):
    """Schematic world map with numbered pins 1-13 for the illustrated stories."""
    d.rectangle([x0, y0, x1, y1], fill=SEA, outline=INK, width=1)
    w, h = x1 - x0, y1 - y0

    def px(lon, lat):
        return x0 + (lon + 180) / 360 * w, y0 + (90 - lat) / 180 * h

    def poly(coords, fill):
        d.polygon([px(lo, la) for lo, la in coords], fill=fill)

    # stylised continents (lon/lat, equirectangular)
    poly([(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 62),
          (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 20), (-97, 16),
          (-105, 20), (-117, 33), (-125, 49), (-150, 60), (-168, 66)], (222, 206, 164))
    poly([(-80, 10), (-60, 8), (-50, 0), (-40, -5), (-35, -8), (-48, -28),
          (-58, -35), (-65, -45), (-70, -55), (-73, -40), (-70, -20),
          (-77, -5), (-80, 10)], (206, 222, 190))
    poly([(-10, 36), (0, 43), (10, 44), (20, 45), (30, 46), (40, 44), (28, 36),
          (23, 40), (12, 38), (3, 37), (-9, 35), (-10, 36)], (222, 206, 164))
    poly([(-18, 35), (-10, 31), (-6, 30), (10, 30), (20, 32), (32, 31), (35, 28),
          (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (32, -29), (26, -34),
          (19, -35), (15, -27), (12, -18), (9, 4), (0, 5), (-8, 5), (-17, 15),
          (-18, 35)], (222, 206, 164))
    poly([(60, 70), (90, 75), (130, 72), (170, 66), (180, 65), (160, 60),
          (140, 60), (130, 45), (120, 40), (105, 20), (100, 8), (95, 16),
          (90, 22), (80, 8), (77, 8), (72, 20), (68, 23), (60, 25), (55, 26),
          (48, 30), (45, 38), (50, 45), (60, 55), (60, 70)], (222, 206, 164))
    poly([(113, -22), (122, -14), (130, -12), (137, -12), (142, -11), (147, -19),
          (153, -27), (150, -37), (140, -38), (130, -32), (122, -34), (115, -35),
          (113, -22)], (206, 222, 190))
    d.text((x0 + 6, y0 + 4), "WORLD MAP — STORIES 1–13", font=font(SANS_B, 9), fill=BLUE)
    pins = [(1, 31, 50), (2, 85, 19), (3, 121, 23), (4, 30, 37), (5, 0, 51),
            (6, 139, 35), (7, 36, 3), (8, -89, 14), (9, 12, 42), (10, 175, -41),
            (11, 127, 37), (12, 44, 33), (13, 19, 52)]
    f = font(SANS_B, 9)
    for n, lon, lat in pins:
        cx, cy = px(lon, lat)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED, outline=(255, 255, 255), width=1)
        tw = d.textlength(str(n), font=f)
        d.text((cx - tw / 2, cy - 6), str(n), font=f, fill=(255, 255, 255))


def lead_block(d, x, y, width, item, illo_h):
    illo = ILLOS[item["n"] - 1]
    d.rectangle([x, y, x + width, y + illo_h], outline=INK, width=1)
    illo(d, x + 1, y + 1, x + width - 1, y + illo_h - 1)
    yy = y + illo_h + 8
    d.text((x, yy), f"{item['n']}.  {item['kicker']}", font=font(SANS_B, 10), fill=RED)
    yy += 15
    yy = text_block(d, x, yy, width, item["head"], font(SERIF_B, 19), leading=21, max_lines=2)
    yy = text_block(d, x, yy + 2, width, item["body"], font(SERIF, 11), leading=13, max_lines=4)
    yy += 3
    d.text((x, yy), item["src"], font=font(SANS_I, 9), fill=GREY)
    if item.get("tag"):
        tag(d, x + width - 62, yy - 1, item["tag"])
    return yy


def feature_block(d, x, y, width, item, illo_h):
    illo = ILLOS[item["n"] - 1]
    d.rectangle([x, y, x + width, y + illo_h], outline=INK, width=1)
    illo(d, x + 1, y + 1, x + width - 1, y + illo_h - 1)
    yy = y + illo_h + 6
    d.text((x, yy), f"{item['n']}. {item['kicker']}", font=font(SANS_B, 8), fill=RED)
    yy += 12
    yy = text_block(d, x, yy, width, item["head"], font(SERIF_B, 13), leading=15, max_lines=2)
    yy = text_block(d, x, yy + 1, width, item["body"], font(SERIF, 10), leading=12, max_lines=2)
    yy += 2
    d.text((x, yy), item["src"], font=font(SANS_I, 8), fill=GREY)
    return yy


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead: kicker small, DATE giant, deck line
    d.text((MX, 10), "THE WORLD IN ONE DAY  •  ALL THE NEWS THAT FITS ON ONE PAGE",
           font=font(SANS_B, 11), fill=RED)
    rule(d, MX, RX, 28, width=2)
    d.text((MX, 34), "FRIDAY 20 NOVEMBER 2026", font=font(SERIF_B, 57), fill=INK)
    deck = ("Kyiv bridges hit in overnight barrage  •  Cyclone Akvan lands in Odisha  •  "
            "Taiwan −6.2% in AI rout  •  COP31 ends without a deal")
    d.text((MX, 100), deck, font=font(SERIF_I, 13), fill=INK)
    rule(d, MX, RX, 122, width=2)

    # ---- strip of 6 numbers, directly under the masthead
    colw = (RX - MX) / 6
    for i, (num, label, src) in enumerate(STRIP):
        cx = MX + i * colw
        d.text((cx + 6, 130), num, font=font(SERIF_B, 24), fill=RED)
        text_block(d, cx + 6, 158, colw - 12, label, font(SANS, 9), leading=11, max_lines=2)
        d.text((cx + 6, 180), "Source: " + src, font=font(SANS_I, 8), fill=GREY)
        if i:
            d.line([(cx, 130), (cx, 192)], fill=LIGHT, width=1)
    rule(d, MX, RX, 196, width=1)

    # ---- region bar
    y = 200
    seg = (RX - MX) / len(REGIONS)
    for i, (name, col) in enumerate(REGIONS):
        x0 = MX + i * seg
        d.rectangle([x0, y, x0 + seg - 2, y + 18], fill=col)
        f = font(SANS_B, 10)
        tw = d.textlength(name, font=f)
        d.text((x0 + (seg - 2 - tw) / 2, y + 3), name, font=f, fill=(255, 255, 255))

    # ---- 3 big leads
    y = 228
    lw = (RX - MX - 2 * 16) / 3
    for i, item in enumerate(LEADS):
        lead_block(d, MX + i * (lw + 16), y, lw, item, illo_h=138)
    rule(d, MX, RX, 470, width=1)

    # ---- 10 features: 5 columns x 2 rows
    fw = (RX - MX - 4 * 12) / 5
    for row in range(2):
        yy = 478 + row * 142
        for col in range(5):
            item = FEATURES[row * 5 + col]
            feature_block(d, MX + col * (fw + 12), yy, fw, item, illo_h=64)
    rule(d, MX, RX, 766, width=1)

    # ---- map (pins 1-13) + briefs
    y = 774
    map_w = 300
    draw_map(d, MX, y, MX + map_w, y + 148)
    bx = MX + map_w + 14
    bw = (RX - bx) / 2
    d.text((bx, y), "ALSO ON FRIDAY 20 NOVEMBER", font=font(SANS_B, 11), fill=INK)
    rule(d, bx, RX, y + 16, width=1)
    f_b = font(SERIF, 10)
    f_s = font(SANS, 9)
    half = (len(BRIEFS) + 1) // 2
    for ci in range(2):
        col_items = BRIEFS[ci * half:(ci + 1) * half]
        yy = y + 21
        for j, b in enumerate(col_items):
            city, txt, src = b[0], b[1], b[2]
            line = f"{city} — {txt} ({src})"
            lines = wrap(d, line, f_b, bw - 8)
            for ln in lines:
                d.text((bx + ci * bw, yy), ln, font=f_b, fill=INK)
                yy += 11
            if len(b) > 3:  # CLAIM / FORECAST tag
                tag(d, bx + ci * bw + bw - 62, yy - 12, b[3])
    rule(d, MX, RX, 940, width=1)

    # ---- DATE CHECK (specific exclusions)
    y = 946
    d.text((MX, y), "DATE CHECK — WHAT WE LEFT OUT, AND WHY", font=font(SANS_B, 11), fill=RED)
    text_block(d, MX, y + 16, RX - MX, DATE_CHECK, font(SERIF, 10), leading=13, max_lines=3)
    rule(d, MX, RX, 992, width=1)

    # ---- footer
    d.text((MX, 998),
           "All figures sourced as labelled; unconfirmed items are marked CLAIM or FORECAST. "
           "Prices are at press time.",
           font=font(SANS, 9), fill=GREY)
    d.text((MX, 1011), "THE WORLD IN ONE DAY  •  FRIDAY 20 NOVEMBER 2026  •  38 STORIES, 13 ILLUSTRATIONS",
           font=font(SANS_B, 9), fill=INK)
    return img


def main():
    img = build()
    img.save(OUT, format="PNG")
    h = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    print(f"{OUT}: {img.size} {img.mode} sha256={h}")


if __name__ == "__main__":
    main()
