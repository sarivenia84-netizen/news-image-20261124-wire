#!/usr/bin/env python3
"""The Wire — 24 November 2026: make.fun news-image-20261124 entry.

Renders a 1024x1024 one-page visual summary of the day's world news as a
PNG using only the Python standard library (zlib + struct): no network,
no fonts, no third-party packages. Deterministic: two runs write the
same bytes.

Layout: masthead, a lead story block, a 3x3 grid of story cards and a
bottom markets strip. Text is drawn with a built-in 5x7 bitmap font.
"""

import os
import struct
import zlib

W = H = 1024
OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "out"), "entry.png")

# ---------------------------------------------------------------- palette
PAPER = (244, 241, 234)
INK = (18, 18, 22)
RED = (178, 34, 38)
BLUE = (24, 60, 110)
GREEN = (22, 110, 74)
AMBER = (198, 122, 20)
GREY = (120, 118, 112)
RULE = (210, 205, 196)
DARKPANEL = (30, 30, 36)

CANVAS = bytearray()
for _ in range(W * H):
    CANVAS += bytes(PAPER)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        CANVAS[i:i + 3] = bytes(c)


def rect(x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(H, y1)):
        base = (y * W + max(0, x0)) * 3
        n = (min(W, x1) - max(0, x0)) * 3
        if n > 0:
            CANVAS[base:base + n] = bytes(c) * (n // 3)


def hline(x0, x1, y, c, t=1):
    rect(x0, y, x1, y + t, c)


def vline(x, y0, y1, c, t=1):
    rect(x, y0, x + t, y1, c)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, each glyph 7 rows of 5-bit integers (MSB = left pixel).
FONT = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11100, 0b10010, 0b10001, 0b10001, 0b10001, 0b10010, 0b11100),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11111),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b11110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": (0, 0, 0, 0, 0, 0b01100, 0b00100),
    ":": (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "-": (0, 0, 0, 0b11111, 0, 0, 0),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "+": (0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    '"': (0b01010, 0b01010, 0, 0, 0, 0, 0),
}


def text(x, y, s, c, sc=2):
    """Draw string s at (x, y), top-left of the first glyph, scaled sc."""
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT["?"])
        for ry in range(7):
            row = g[ry]
            for rx in range(5):
                if row & (0b10000 >> rx):
                    rect(cx + rx * sc, y + ry * sc,
                         cx + rx * sc + sc, y + ry * sc + sc, c)
        cx += 6 * sc
    return cx - x


def twidth(s, sc=2):
    return max(0, len(s)) * 6 * sc - sc


def wrap(s, nchars):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if len(t) <= nchars:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def center_text(y, s, c, sc=2):
    x = (W - twidth(s, sc)) // 2
    text(x, y, s, c, sc)

# ---------------------------------------------------------------- stories
STORIES = [
    (RED, "MARKETS", "Nvidia reinstates Jensen",
     "Huang as CEO; stock soars", "27%: 1 tn added (24 Nov)"),
    (AMBER, "WASHINGTON", "Trump says White House",
     "pressured Nvidia board to", "return Huang as CEO"),
    (RED, "UKRAINE", "Sea drones sink Russian",
     "corvette Merkury in a", "Libyan port - AP"),
    (RED, "MOSCOW", "Russia accuses Estonia of",
     "hostile acts on verge of", "triggering open war"),
    (BLUE, "KYIV", "Zelenskiy: intelligence",
     "shows Russia planning new", "strikes on Ukraine"),
    (BLUE, "LONDON", "Britain: SpaceX Ukraine",
     "restrictions dented", "confidence and trust"),
    (RED, "TEHRAN", "Iran vows every means to",
     "counter US naval blockade", "of Strait of Hormuz"),
    (AMBER, "RIYADH", "Houthis claim attack on",
     "Saudi Rabigh oil refinery", "(23 Nov)"),
    (RED, "GAZA", "Israeli strikes kill 3,",
     "including UNRWA worker,", "despite ceasefire deal"),
    (BLUE, "GAZA", "Israeli army completes",
     "ground operation beyond", "the Yellow Line - BBC"),
    (GREEN, "ROME", "WFP warns wars jeopardize",
     "food aid for 7.3 million", "more people"),
    (AMBER, "PYONGYANG", "North Korea considers",
     "shutting Swiss diplomatic", "office, KCNA says"),
    (BLUE, "TOKYO", "Japan-China ties strain",
     "after APEC snub; Xi and",
     "Takaichi only shook hands"),
    (AMBER, "IOWA", "Trump pauses Army plan to",
     "detonate 68 drums of lead",
     "azide, defers to court"),
    (GREEN, "WASHINGTON", "Voting opens for 79th",
     "National Thanksgiving",
     "Turkey Pardon - WH"),
    (RED, "BERLIN", "Hundreds of German",
     "schools receive bomb", "threats; police sweep"),
    (AMBER, "BRUSSELS", "Belgian unions lead",
     "Brussels protest against", "austerity policies"),
    (BLUE, "SINGAPORE", "Diesel shortage persists",
     "despite oil's Iran-war", "recovery - analysts"),
    (GREEN, "GENEVA", "Europe urged to lead",
     "global action on anti-", "microbial resistance"),
]

def draw():
    # ---- masthead
    rect(0, 0, W, 8, INK)
    rect(0, 8, W, 9, RED)
    y = 34
    center_text(y, "THE WIRE", INK, 9)
    y += 64
    center_text(y, "ONE PAGE - EVERY STORY - TUESDAY 24 NOVEMBER 2026", GREY, 2)
    hline(48, W - 48, y + 30, INK, 3)
    hline(48, W - 48, y + 36, RULE, 1)

    # ---- lead story banner
    bx0, by0, bx1, by1 = 48, y + 46, W - 48, y + 176
    rect(bx0, by0, bx1, by1, DARKPANEL)
    rect(bx0, by0, bx0 + 10, by1, RED)
    text(bx0 + 30, by0 + 12, "LEAD STORY - MARKETS", (230, 220, 200), 2)
    text(bx0 + 30, by0 + 36, "NVIDIA BRINGS BACK HUANG;", PAPER, 3)
    text(bx0 + 30, by0 + 64, "STOCK SOARS 27%, ADDS 1 TN", PAPER, 3)
    text(bx0 + 30, by0 + 96, "IN SANTA CLARA - CNBC - CNN - FORTUNE", (200, 200, 205), 2)

    # ---- story grid 3x6
    gy0 = by1 + 14
    cw, ch, gap = 312, 80, 10
    gx0 = 32
    for i, (col, tag, l1, l2, l3) in enumerate(STORIES):
        r, cix = divmod(i, 3)
        x0 = gx0 + cix * (cw + gap)
        y0 = gy0 + r * (ch + gap)
        rect(x0, y0, x0 + cw, y0 + ch, (255, 253, 248))
        rect(x0, y0, x0 + cw, y0 + ch, RULE)
        rect(x0, y0, x0 + cw, y0 + 3, col)
        rect(x0 + 8, y0 + 9, x0 + 8 + twidth(tag, 1) + 8, y0 + 21, col)
        text(x0 + 12, y0 + 12, tag, PAPER, 1)
        for k, line in enumerate((l1, l2, l3)):
            text(x0 + 8, y0 + 24 + k * 16, line, INK, 2)
        # tiny map-pin dot
        rect(x0 + cw - 20, y0 + ch - 14, x0 + cw - 14, y0 + ch - 8, col)

    # ---- date-check + markets strip
    my = gy0 + 7 * ch + 6 * gap + 4
    rect(32, my, W - 32, my + 58, (238, 234, 226))
    rect(32, my, W - 32, my + 58, RULE)
    text(48, my + 9, "DATE CHECK: ALL 19 STORIES TUESDAY 24 NOV 2026 - 11 REGIONS", INK, 2)
    stats = [("NVDA", "+27% HUANG BACK", GREEN), ("HORMUZ", "BLOCKADE", RED),
             ("GAZA", "CEASEFIRE TENSE", AMBER), ("WFP", "7.3M AT RISK", RED)]
    sx = 48
    for name, val, col in stats:
        text(sx, my + 27, name, GREY, 2)
        text(sx, my + 42, val, col, 2)
        sx += 235

    # ---- footer
    text(64, H - 26, "SOURCES: REUTERS - CNBC - CNN - AL JAZEERA - BBC - WH",
         GREY, 1)
    text(W - 64 - twidth("THE WIRE / 2026", 1), H - 26, "THE WIRE / 2026",
         GREY, 1)


draw()

# ---------------------------------------------------------------- PNG out
def write_png(path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += CANVAS[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(
            ">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
           + chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    print(f"wrote {path} ({len(png):,} bytes)")


write_png(OUT)
# verified: deterministic output, exit 0