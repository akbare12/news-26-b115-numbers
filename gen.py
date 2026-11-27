#!/usr/bin/env python3
"""Render entry.png for news-image-20261126, account b115, layout V111.
Masthead -> hero 1 full-width (art right) -> DATE CHECK -> heroes 2+3
two columns -> map full-width -> cards 5x2 -> ALSO 3 columns ->
timeline -> footer. 50 stories, 10 regions, Thursday 26 November 2026.
Run: python3 gen.py  (writes entry.png next to this file)
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

INK = (18, 18, 22)
PAPER = (250, 247, 238)
RED = (178, 34, 34)
BLUE = (24, 68, 128)
GOLD = (176, 128, 28)
TEAL = (14, 110, 110)
GREY = (96, 96, 96)
LIGHT = (233, 229, 218)
DARKGREY = (70, 70, 70)
SEA = (196, 216, 228)
LAND = (226, 214, 178)
LANDLINE = (150, 138, 100)

FD = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FDB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FDB if bold else FD, size)


def wrap(draw, text, fnt, maxw):
    """Greedy wrap; returns list of lines, every word kept."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, maxw, fill=INK, leading=None, max_lines=None):
    """Draw wrapped text inside a box; assert no word is dropped."""
    lines = wrap(draw, text, fnt, maxw)
    if max_lines is not None:
        assert len(lines) <= max_lines, "text needs %d lines, max %d: %r" % (
            len(lines), max_lines, text[:60])
    lh = leading if leading is not None else int(fnt.size * 1.25)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def point_in_polygon(px, py, poly):
    """Ray casting; True when the point lies inside the polygon."""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > py) != (yj > py):
            xinters = (xj - xi) * (py - yi) / (yj - yi) + xi
            if px < xinters:
                inside = not inside
        j = i
    return inside


# ---- simplified world map, lon/lat polygons -------------------------------
NORTH_AMERICA = [(-168, 66), (-155, 58), (-140, 60), (-130, 55), (-125, 48),
                 (-124, 40), (-120, 34), (-114, 29), (-110, 24), (-105, 20),
                 (-97, 16), (-92, 15), (-86, 12), (-82, 9), (-79, 9),
                 (-77, 7), (-75, 10), (-72, 12), (-68, 16), (-64, 18),
                 (-61, 15), (-60, 10), (-55, 6), (-52, 5), (-55, 9),
                 (-60, 12), (-62, 18), (-66, 19), (-70, 20), (-74, 22),
                 (-77, 25), (-80, 26), (-81, 30), (-76, 35), (-74, 39),
                 (-70, 42), (-66, 45), (-60, 47), (-55, 52), (-60, 55),
                 (-65, 58), (-68, 55), (-72, 58), (-78, 62), (-85, 66),
                 (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
                 (-155, 71), (-165, 68)]
SOUTH_AMERICA = [(-80, 10), (-77, 5), (-75, 2), (-72, 0), (-70, -5),
                 (-75, -12), (-78, -18), (-72, -22), (-70, -30), (-68, -38),
                 (-66, -45), (-68, -52), (-70, -55), (-74, -50), (-73, -40),
                 (-72, -30), (-70, -20), (-65, -15), (-60, -10), (-55, -8),
                 (-50, -5), (-45, -3), (-40, -5), (-35, -8), (-38, -15),
                 (-40, -22), (-45, -25), (-48, -28), (-52, -32), (-55, -35),
                 (-58, -38), (-62, -40), (-65, -45), (-68, -50), (-70, -55)]
EUROPE = [(-10, 36), (-9, 43), (-2, 48), (-1, 52), (2, 53), (7, 54),
          (8, 57), (12, 56), (18, 56), (21, 55), (24, 58), (28, 60),
          (31, 59), (33, 55), (31, 49), (28, 46), (24, 45), (20, 44),
          (16, 42), (14, 40), (10, 38), (4, 37), (0, 36), (-6, 36),
          (-10, 38)]
AFRICA = [(-17, 15), (-16, 20), (-12, 27), (-6, 32), (-1, 35), (5, 37),
          (10, 37), (15, 34), (20, 32), (25, 32), (30, 31), (33, 28),
          (36, 24), (38, 20), (40, 15), (44, 11), (48, 11), (51, 11),
          (50, 5), (46, 0), (42, -5), (40, -10), (38, -15), (36, -20),
          (34, -26), (32, -29), (28, -33), (24, -34), (20, -35), (17, -32),
          (15, -28), (13, -22), (12, -16), (11, -10), (9, -4), (9, 4),
          (4, 6), (-2, 5), (-8, 5), (-13, 8), (-16, 12)]
ASIA = [(30, 36), (34, 31), (37, 33), (42, 30), (44, 24), (43, 18),
        (46, 13), (52, 15), (57, 19), (56, 25), (60, 25), (65, 25),
        (70, 21), (75, 12), (78, 8), (80, 8), (84, 18), (88, 22),
        (92, 21), (95, 16), (99, 10), (103, 7), (106, 10), (109, 15),
        (110, 20), (114, 22), (118, 26), (121, 30), (124, 37), (127, 40),
        (130, 42), (134, 44), (138, 47), (141, 50), (142, 55), (140, 60),
        (136, 66), (130, 70), (122, 72), (112, 74), (102, 76), (92, 75),
        (82, 73), (72, 71), (64, 69), (56, 68), (48, 67), (42, 64),
        (38, 60), (34, 56), (30, 52), (28, 47), (30, 42)]
INDONESIA = [(95, 5), (98, 3), (100, -2), (104, -3), (106, -8), (110, -8.5),
             (114, -9), (118, -9.5), (120, -10), (122, -9), (125, -8),
             (128, -4), (130, -2), (131, 0), (128, 1), (125, 1), (120, 0),
             (115, 0), (110, 2), (105, 4), (100, 5)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (120, -34), (125, -33),
             (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
             (153, -27), (150, -22), (146, -19), (142, -11), (137, -12),
             (132, -11), (130, -13), (126, -14), (122, -17), (118, -20)]

CONTINENTS = [NORTH_AMERICA, SOUTH_AMERICA, EUROPE, AFRICA, ASIA,
              INDONESIA, AUSTRALIA]

# 10 map regions: (label, lon, lat, tag)
REGIONS = [
    ("NEW YORK", -74.0, 40.7, "1"),
    ("HORMUZ", 56.3, 26.2, "2"),
    ("RIYADH", 46.7, 24.6, "3"),
    ("GAZA", 34.6, 32.2, "4"),
    ("KYIV", 28.5, 50.5, "5"),
    ("BOGOR", 106.8, -6.6, "6"),
    ("LONDON", -0.1, 51.5, "7"),
    ("PYONGYANG", 125.8, 39.0, "8"),
    ("BANGKOK", 100.5, 13.75, "9"),
    ("BERLIN", 13.4, 52.5, "10"),
]

CARDS = [
    ("GAZA", "Israel kills Hamas education deputy", "Khaled Abu Nada and his wife killed in a Deir al-Balah strike; 9 dead overnight, third night of raids.", "9", "[C]"),
    ("KYIV", "Ballistic missiles hit Kyiv mall", "7 wounded, 2 serious, as Russia fires Iskander missiles and 113 drones; 18 hurt in Kryvyi Rih.", "7", "[C]"),
    ("BOGOR", "Flooded illegal gold mine", "13 dead, 13 missing about 100 m underground after heavy rain; rescue teams dig on.", "13", "[C]"),
    ("JERUSALEM", "Judge urges bribery charge dropped", "Netanyahu trial judge recommends prosecutors drop Case 4000, the only bribery count.", "4000", "[C]"),
    ("PYONGYANG", "Kim tours nuclear plant", "Kim Jong Un visits a nuclear-material factory and urges wider tactical nuclear deployment.", "1", "[C]"),
    ("SPACE", "FCC clears 1M SpaceX data satellites", "Starmind orbital compute modules approved 25 Nov; first US nod for space data centres.", "1M", "[C]"),
    ("LONDON", "UK net migration falls to 77,000", "Lowest since 1997 outside the pandemic, ONS data for the year to June 2026 show.", "77K", "[C]"),
    ("MOSCOW", "Record post-Soviet military budget", "Russia approves its largest military budget since the Soviet era.", "27", "[C]"),
    ("BANGKOK", "Oil depot blast injures 7", "Explosion at a Bangkok oil depot hurts 7 and triggers an evacuation alert; fire out in ~30 min.", "7", "[C]"),
    ("BERLIN", "2 Iraqis held over synagogue plot", "Suspects arrested in Cologne and Heidelberg over a planned March synagogue attack.", "2", "[C]"),
]

ALSO = [
    "Kuwait: Iranian drone kills 2 Italian technicians [C]",
    "Guinea-Bissau delays elections to Nov 2028 [C]",
    "Iraq shuts 2 Kurdistan border crossings [C]",
    "Kenya cult leader convicted of terror charges [C]",
    "Congo Ebola outbreak passes 12,000 cases [C]",
    "EU leaders open 2-day budget summit [C]",
    "Serbia sets presidential vote for 27 Dec [C]",
    "Trump asks Putin to 'pull back' in Europe [C]",
    "Thanksgiving storm cuts power to 800,000+ [C]",
    "UK signs \u00a38bn Babcock submarine deal [C]",
    "EU names Hernandez de Cos as ECB chief [C]",
    "Pakistan, Saudi, Turkey plan defence talks [C]",
    "Bangladesh garment workers tear-gassed [C]",
    "Brands shift $254m orders from Bangladesh [C]",
    "China factory profits grow fastest in 5 months [C]",
    "Canary Islands migrant arrivals hit record [C]",
    "US urges citizens to leave Iran [C]",
    "Myanmar rejects full ICJ genocide orders [C]",
    "India marks 77th Constitution Day [C]",
    "NY court upholds Mamdani rent freeze [C]",
    "S&P puts Nvidia rating on downgrade watch [C]",
    "US chip curbs threaten Chinese AI models [R]",
    "GAO: Pentagon stocks take years to rebuild [C]",
    "FinCEN confirms internal cyber breach [C]",
    "Eisenkot wins first Israel coalition deal [C]",
    "Merz warns Russia's aims go beyond Ukraine [C]",
    "UK on alert over drone threat to air bases [C]",
    "Norse Atlantic halts flights, warns of collapse [C]",
    "Poundland enters administration, 11,000 jobs at risk [C]",
    "Malaysia sues Google for $146m [C]",
    "Kenya court halts US-backed Ebola site [C]",
    "Belarus offers to fly Zelensky to Moscow [C]",
    "Kushner calls Putin 'grandmaster of politics' [C]",
    "Estonia decides to shut its border [C]",
    "Copernicus: longest stretch above 2\u00b0C [C]",
    "Nvidia halts AI server shipments to 4 countries [C]",
    "US Bitcoin funds hit record $4.94bn [C]",
]

TIMELINE = [
    ("DAWN", "Kyiv mall hit; 7 hurt"),
    ("OVERNIGHT", "Gaza strike kills Hamas deputy"),
    ("10:00", "NYC wind warning begins"),
    ("MIDDAY", "EU budget summit opens"),
    ("PM", "IRGC claims 2 tankers mined"),
    ("PM", "Markets rebound on tariff relief"),
    ("EVE", "Kuwait drone strike kills 2"),
]

# ---- layout geometry ------------------------------------------------------
# V111: masthead | hero1 full-width art-right | DATE CHECK | heroes 2+3
# two columns | map full-width | cards 5x2 | ALSO 3 columns | timeline | footer
Y_MAST, Y_HERO1, Y_DATE, Y_H23 = 0, 52, 182, 234
Y_MAP, Y_CARDS, Y_ALSO = 382, 500, 706
Y_TIME, Y_FOOT = 892, 962


def draw_masthead(d):
    d.rectangle([0, 0, W, 52], fill=INK)
    d.text((14, 10), "THE WORLD IN ONE PAGE", font=font(24, True), fill=(250, 247, 238))
    d.text((14, 38), "50 STORIES  \u00b7  10 REGIONS  \u00b7  ONE DAY", font=font(9), fill=(200, 195, 180))
    right = "THURSDAY 26 NOVEMBER 2026"
    d.text((W - 14 - text_w(d, right, font(15, True)), 12), right,
           font=font(15, True), fill=(250, 247, 238))
    sub = "make.fun  \u00b7  news-image-20261126"
    d.text((W - 14 - text_w(d, sub, font(9)), 36), sub, font=font(9), fill=(200, 195, 180))
    d.rectangle([0, 52, W, 55], fill=RED)


def draw_balloon_art(d, x0, y0, x1, y1):
    """Macy's balloon scene: sky, skyline, grounded balloons, ropes."""
    d.rectangle([x0, y0, x1, y1], fill=(168, 196, 222))
    d.rectangle([x0, y0, x1, y0 + 8], fill=(140, 175, 210))
    # skyline silhouettes
    for i, bh in enumerate([46, 62, 38, 70, 52, 44, 58, 36]):
        bx = x0 + 8 + i * 34
        d.rectangle([bx, y1 - bh, bx + 28, y1], fill=(90, 105, 130))
        for wy in range(y1 - bh + 6, y1 - 6, 10):
            for wx in range(bx + 5, bx + 24, 9):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(210, 205, 160))
    # street
    d.rectangle([x0, y1 - 14, x1, y1], fill=(70, 70, 72))
    for cx in range(x0 + 10, x1 - 10, 26):
        d.rectangle([cx, y1 - 8, cx + 12, y1 - 5], fill=(240, 200, 60))
    # two grounded balloons with netting + ropes
    d.ellipse([x0 + 30, y0 + 14, x0 + 120, y0 + 66], fill=(178, 34, 34))
    d.ellipse([x0 + 44, y0 + 22, x0 + 106, y0 + 58], fill=(210, 70, 60))
    d.ellipse([x0 + 150, y0 + 20, x0 + 226, y0 + 62], fill=(24, 68, 128))
    d.ellipse([x0 + 162, y0 + 26, x0 + 214, y0 + 56], fill=(70, 120, 180))
    for rx in (x0 + 40, x0 + 70, x0 + 100, x0 + 165, x0 + 195, x0 + 220):
        d.line([rx, y0 + 60, rx - 6, y1 - 14], fill=(60, 60, 60), width=1)
    # netting over balloons
    for nx in range(x0 + 30, x0 + 230, 14):
        d.line([nx, y0 + 16, nx + 10, y0 + 64], fill=(250, 247, 238), width=1)
    d.text((x0 + 8, y0 + 74), "BALLOONS GROUNDED  \u00b7  60 MPH GUSTS",
           font=font(9, True), fill=(18, 18, 22))


def draw_hero1(d):
    y0, y1 = Y_HERO1, Y_DATE
    d.rectangle([0, y0, W, y1], fill=PAPER)
    d.rectangle([8, y0 + 6, 54, y0 + 26], fill=RED)
    d.text((14, y0 + 10), "HERO 1", font=font(11, True), fill=(255, 255, 255))
    tx = 14
    d.text((tx, y0 + 32), "MACY'S 100TH PARADE POSTPONED",
           font=font(21, True), fill=INK)
    deck = ("Thanksgiving parade delayed by storm \u2014 first weather postponement in "
            "100 years; rescheduled Sat 28 Nov, 08:30 ET. Balloons grounded as gusts "
            "hit 60 mph; NYC high wind warning from 10:00 Thu. Philadelphia's parade "
            "also cancelled. [C]")
    draw_wrapped(d, tx, y0 + 60, deck, font(12), 640, leading=15, max_lines=4)
    d.text((tx, y1 - 26), "WHY IT MATTERS:", font=font(10, True), fill=RED)
    draw_wrapped(d, tx + 108, y1 - 26,
                 "America's most-watched Thanksgiving ritual stops for weather for the "
                 "first time \u2014 a nor'easter rewriting the holiday itself.",
                 font(10), 640 - 108, leading=12, max_lines=2)
    draw_balloon_art(d, 690, y0 + 6, 1010, y1 - 6)


def draw_datecheck(d):
    y0, y1 = Y_DATE, Y_H23
    d.rectangle([0, y0, W, y1], fill=(24, 68, 128))
    d.text((14, y0 + 6), "DATE CHECK \u2014 NOT 26 NOV, SO NOT IN TODAY'S COUNT:",
           font=font(11, True), fill=(255, 255, 255))
    l1 = ("COP31 failed 22 Nov  \u00b7  Shenzhou-24 launched 25 Nov  \u00b7  Cairo tanker fire, "
          "31 dead, 25 Nov  \u00b7  Cartagena hostages freed 25 Nov")
    l2 = ("Australia\u2013Solomon pact 25 Nov  \u00b7  UK energy prices +26% announced 25 Nov  "
          "\u00b7  Huawei verdict 24 Nov  \u2014  all 7 excluded on purpose.")
    d.text((14, y0 + 24), l1, font=font(10), fill=(235, 240, 248))
    d.text((14, y0 + 38), l2, font=font(10), fill=(235, 240, 248))
    assert text_w(d, l1, font(10)) <= W - 28, "datecheck line 1 too wide"
    assert text_w(d, l2, font(10)) <= W - 28, "datecheck line 2 too wide"


def hero_col(d, x, w, num, title, deck, why, badge, accent):
    y0, y1 = Y_H23, Y_MAP
    d.rectangle([x, y0, x + w, y1], outline=(180, 175, 160), width=1)
    d.rectangle([x, y0, x + w, y0 + 24], fill=accent)
    d.text((x + 10, y0 + 5), num, font=font(11, True), fill=(255, 255, 255))
    # badge number at top-right, beside the title line
    bw = text_w(d, badge, font(22, True)) + 16
    d.rectangle([x + w - bw - 8, y0 + 28, x + w - 8, y0 + 56], fill=accent)
    d.text((x + w - bw, y0 + 32), badge, font=font(22, True), fill=(255, 255, 255))
    tw = w - bw - 26
    draw_wrapped(d, x + 10, y0 + 30, title, font(15, True), tw, max_lines=1)
    draw_wrapped(d, x + 10, y0 + 58, deck, font(11), w - 20, leading=13, max_lines=3)
    d.text((x + 10, y0 + 104), "WHY IT MATTERS:", font=font(9, True), fill=RED)
    draw_wrapped(d, x + 10, y0 + 116, why, font(9), w - 20, leading=11, max_lines=2)


def draw_heroes23(d):
    hero_col(d, 8, 496, "HERO 2 \u2014 HORMUZ",
             "IRGC CLAIMS 2 TANKERS HIT BY MINES [CL]",
             "A supertanker carrying 2M barrels is among the vessels Tehran says "
             "were mined near Khasab; the claim is unverified. UKMTO confirms a "
             "projectile blast 50 nm west of Dubai; crew safe. [CL]",
             "The Iran war widens to the world's busiest oil chokepoint.",
             "2M", RED)
    hero_col(d, 520, 496, "HERO 3 \u2014 TARIFFS",
             "TRUMP TARIFFS: MARKETS REBOUND [C]",
             "STOXX 600 +1.6% and MSCI +0.4% as traders judge the 14-partner salvo "
             "\u2014 China 20%, EU 15% \u2014 not as bad as feared; levies would not "
             "stack on July rates. [C]",
             "Relief, not panic: the biggest trade salvo lands soft \u2014 for now.",
             "+1.6%", TEAL)


def draw_map(d):
    y0, y1 = Y_MAP, Y_CARDS
    d.rectangle([0, y0, W, y1], fill=SEA)
    mx0, mx1, my0, my1 = 8, 1016, y0 + 20, y1 - 4
    lon0, lon1, lat0, lat1 = -170.0, 190.0, 75.0, -58.0

    def proj(lon, lat):
        x = mx0 + (lon - lon0) / (lon1 - lon0) * (mx1 - mx0)
        y = my0 + (lat0 - lat) / (lat0 - lat1) * (my1 - my0)
        return (x, y)

    # polygons first, header AFTER polygons (so the header is never hidden)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LANDLINE)
    d.text((14, y0 + 3), "WHERE IT HAPPENED \u2014 10 REGIONS",
           font=font(11, True), fill=INK)
    # dots on land, labels >= 9px, no label overlap, no dot under any label
    # (a red dot must never cover a letter of another region's label)
    dots = []
    for label, lon, lat, tag in REGIONS:
        assert any(point_in_polygon(lon, lat, p) for p in CONTINENTS), \
            "dot %s (%.1f, %.1f) is not on land" % (label, lon, lat)
        dots.append((label,) + proj(lon, lat))
    placed = []
    label_boxes = []
    for label, lon, lat, tag in REGIONS:
        x, y = proj(lon, lat)
        placed.append((label, x, y))
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=RED, outline=(255, 255, 255))
        d.text((x - 2, y - 3), tag, font=font(6, True), fill=(255, 255, 255))
        lw = text_w(d, label, font(9, True))
        # try right, left, below, above; take the first slot with no overlap
        candidates = [(x + 8, y - 5), (x - 8 - lw, y - 5),
                      (x + 8, y + 7), (x - 8 - lw, y + 7),
                      (x + 8, y + 18), (x - 8 - lw, y + 18),
                      (x + 8, y - 16), (x - 8 - lw, y - 16),
                      (x - lw / 2, y - 17), (x - lw / 2, y + 14)]
        placed_box = None
        for lx, ly in candidates:
            if lx < mx0 or lx + lw > mx1 or ly < my0 or ly + 11 > my1:
                continue
            box = (lx, ly, lx + lw, ly + 11)
            clash = False
            for other in label_boxes:
                ox0, oy0, ox1, oy1 = other
                if not (box[2] < ox0 or box[0] > ox1 or box[3] < oy0 or box[1] > oy1):
                    clash = True
                    break
            if not clash:
                # no OTHER region's dot (radius 5) may sit under this label
                for olab, ox, oy in dots:
                    if olab == label:
                        continue
                    if (box[0] - 5 <= ox <= box[2] + 5
                            and box[1] - 5 <= oy <= box[3] + 5):
                        clash = True
                        break
            if not clash:
                placed_box = box
                break
        assert placed_box is not None, "no free label slot for %s" % label
        label_boxes.append(placed_box)
        d.text((placed_box[0], placed_box[1]), label, font=font(9, True), fill=INK)
    # final check: no label box covers any other region's dot
    for i, (lab, lx0, ly0, lx1, ly1) in enumerate(
            [(REGIONS[i][0],) + label_boxes[i] for i in range(len(label_boxes))]):
        for olab, ox, oy in dots:
            if olab == lab:
                continue
            assert not (lx0 - 5 <= ox <= lx1 + 5 and ly0 - 5 <= oy <= ly1 + 5), \
                "label %s covers dot %s" % (lab, olab)
    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            dx = placed[i][1] - placed[j][1]
            dy = placed[i][2] - placed[j][2]
            dist = math.hypot(dx, dy)
            assert dist >= 18, "map dots too close: %s vs %s (%.1f px)" % (
                placed[i][0], placed[j][0], dist)


def draw_cards(d):
    y0 = Y_CARDS
    cw, ch, gap = 198, 100, 5
    d.text((14, y0 + 2), "THE DAY'S TEN  \u2014  10 STORIES IN DEPTH",
           font=font(11, True), fill=INK)
    top = y0 + 20
    for idx, (region, title, deck, badge, tag) in enumerate(CARDS):
        row, col = divmod(idx, 5)
        x = 8 + col * (cw + gap)
        y = top + row * (ch + gap)
        d.rectangle([x, y, x + cw, y + ch], outline=(180, 175, 160), width=1)
        d.rectangle([x, y, x + cw, y + 16], fill=BLUE)
        d.text((x + 6, y + 3), region + "  " + tag, font=font(9, True),
               fill=(255, 255, 255))
        bw = text_w(d, badge, font(16, True)) + 10
        d.rectangle([x + cw - bw - 4, y + 20, x + cw - 4, y + 42], fill=GOLD)
        d.text((x + cw - bw + 1, y + 24), badge, font=font(16, True),
               fill=(255, 255, 255))
        tw = cw - 12 - (bw + 6 if len(badge) > 2 else 0)
        draw_wrapped(d, x + 6, y + 20, title, font(10, True), tw,
                     leading=12, max_lines=2)
        draw_wrapped(d, x + 6, y + 46, deck, font(9), cw - 12, leading=11,
                     max_lines=4)


def draw_also(d):
    y0 = Y_ALSO
    d.rectangle([0, y0, W, Y_TIME], fill=(242, 239, 230))
    d.text((14, y0 + 4), "ALSO TODAY \u2014 37 MORE STORIES",
           font=font(11, True), fill=INK)
    assert len(ALSO) == 37, "ALSO must hold 37 items, got %d" % len(ALSO)
    cols = [ALSO[0:13], ALSO[13:25], ALSO[25:37]]
    colw = 330
    for ci, items in enumerate(cols):
        x = 14 + ci * (colw + 6)
        y = y0 + 24
        for item in items:
            assert text_w(d, item, font(9)) <= colw, \
                "ALSO line too wide (%d px): %r" % (text_w(d, item, font(9)), item)
            d.text((x, y), "\u2022  " + item, font=font(9), fill=INK)
            y += 12
        assert y <= Y_TIME - 4, "ALSO column %d overflows" % ci


def draw_timeline(d):
    y0, y1 = Y_TIME, Y_FOOT
    d.rectangle([0, y0, W, y1], fill=PAPER)
    d.text((14, y0 + 4), "THE DAY, HOUR BY HOUR", font=font(11, True), fill=INK)
    n = len(TIMELINE)
    step = (W - 28) / n
    yline = y0 + 40
    d.line([14, yline, W - 14, yline], fill=RED, width=2)
    for i, (when, what) in enumerate(TIMELINE):
        cx = 14 + step * i + step / 2
        d.ellipse([cx - 4, yline - 4, cx + 4, yline + 4], fill=RED)
        d.text((cx - text_w(d, when, font(9, True)) / 2, yline - 20), when,
               font=font(9, True), fill=RED)
        lines = wrap(d, what, font(8), step - 10)
        assert len(lines) <= 2, "timeline item too long: %r" % what
        ly = yline + 8
        for line in lines:
            d.text((cx - text_w(d, line, font(8)) / 2, ly), line,
                   font=font(8), fill=INK)
            ly += 10
    assert yline + 30 <= y1, "timeline overflows"


def draw_footer(d):
    y0 = Y_FOOT
    d.rectangle([0, y0, W, H], fill=INK)
    d.text((14, y0 + 8), "Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 CNN \u00b7 UKMTO \u00b7 ONS \u00b7 KCNA \u00b7 FCC",
           font=font(9), fill=(200, 195, 180))
    d.text((14, y0 + 24), "Compiled 27 Nov 2026  \u00b7  50 stories  \u00b7  10 regions  \u00b7  "
           "Not affiliated with make.fun", font=font(9), fill=(200, 195, 180))
    right = "THE WORLD IN ONE PAGE"
    d.text((W - 14 - text_w(d, right, font(11, True)), y0 + 14), right,
           font=font(11, True), fill=(250, 247, 238))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_hero1(d)
    draw_datecheck(d)
    draw_heroes23(d)
    draw_map(d)
    draw_cards(d)
    draw_also(d)
    draw_timeline(d)
    draw_footer(d)
    img.save(OUT, "PNG", optimize=True)
    data = open(OUT, "rb").read()
    print("entry.png %d bytes %dx%d sha256=%s" % (
        len(data), W, H, hashlib.sha256(data).hexdigest()))
    assert len(data) <= 1024 * 1024, "entry.png over 1 MiB: %d" % len(data)
    assert 3 + 10 + 37 == 50, "story count must be 50"
    assert len(REGIONS) == 10, "region count must be 10"


if __name__ == "__main__":
    main()
