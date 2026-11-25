"""Render the 25 November 2026 world-news front page as a 1024x1024 PNG.

Own implementation: builds the page from a small set of drawing helpers
(font loading, greedy word wrapping measured with textbbox, a paragraph
renderer, and simple geometric scene painters for the skyline, smoke and
flame). Stories are the verified 25 November 2026 items:
lead — second Hamas security chief Mohammad Abu al-Ouf killed in Gaza;
Kyiv strikes two refineries in Samara; Pakistan's first astronaut boards
Tiangong; Australia signs a security treaty with Solomon Islands; the AI
sell-off hits Nvidia and the Nikkei; bottom strip — Trump awards Giuliani
the Medal of Freedom and an unclassified CIA system is breached.
"""
import os

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
MARGIN = 24
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/noto"
SERIF_BOLD = os.path.join(FONT_DIR, "NotoSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "NotoSerif-Regular.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "NotoSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "NotoSans-Regular.ttf")

INK = (13, 32, 61)
CRIMSON = (178, 34, 34)
EMBER = (230, 126, 34)
GILT = (212, 175, 55)
SEA = (14, 90, 100)
STONE = (90, 90, 90)
PAPER = (240, 242, 245)
BORDER = (200, 205, 210)
BODY_INK = (20, 20, 20)
BODY_GREY = (60, 60, 60)


def load(path, size):
    """Load a TTF face at the requested point size."""
    return ImageFont.truetype(path, size)


def fit_words(canvas, text, face, max_w):
    """Greedy word wrap: pack as many words per line as fit in max_w."""
    lines = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if canvas.textlength(trial, font=face) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paragraph(canvas, x, y, lines, face, colour, gap):
    """Paint stacked lines and return the y coordinate just below them."""
    for line in lines:
        canvas.text((x, y), line, font=face, fill=colour)
        y += gap
    return y


def draw_skyline(canvas, left, right, base_y, towers):
    """Paint a row of dark towers with lit windows above base_y.

    towers is a list of (x_offset, width, height) triples.
    """
    for off, wide, tall in towers:
        bx = left + off
        canvas.rectangle([bx, base_y - tall, bx + wide, base_y], fill=(28, 10, 10))
        wy = base_y - tall + 14
        while wy < base_y - 10:
            wx = bx + 12
            while wx < bx + wide - 10:
                canvas.rectangle([wx, wy, wx + 8, wy + 8], fill=(255, 210, 63))
                wx += 22
            wy += 22


def draw_smoke(canvas, puffs, colour=(140, 135, 130)):
    """Paint a cluster of overlapping smoke discs."""
    for cx, cy, radius in puffs:
        canvas.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius], fill=colour
        )


def draw_flame(canvas, tip_x, base_y, height, width):
    """Paint a two-tone flame triangle rising from base_y."""
    canvas.polygon(
        [
            (tip_x - width // 2, base_y),
            (tip_x, base_y - height),
            (tip_x + width // 2, base_y),
        ],
        fill=EMBER,
    )
    canvas.polygon(
        [
            (tip_x - width // 4, base_y),
            (tip_x, base_y - int(height * 0.62)),
            (tip_x + width // 4, base_y),
        ],
        fill=(255, 210, 63),
    )


def build_page():
    page = Image.new("RGB", (PAGE, PAGE), "white")
    c = ImageDraw.Draw(page)

    # ---------- masthead ----------
    c.rectangle([0, 0, PAGE, 118], fill=INK)
    c.text((36, 18), "THE WORLD IN ONE DAY", font=load(SERIF_BOLD, 58), fill="white")
    c.text(
        (36, 82),
        "WEDNESDAY  25  NOVEMBER  2026",
        font=load(SANS_BOLD, 26),
        fill=GILT,
    )
    c.text(
        (PAGE - 36, 82),
        "WORLD NEWS",
        font=load(SANS_BOLD, 26),
        fill="white",
        anchor="ra",
    )

    # ---------- lead story: Gaza ----------
    lead_top, lead_bottom = 136, 470
    c.rectangle([MARGIN, lead_top, PAGE - MARGIN, lead_bottom], fill=(74, 28, 28))
    skyline_top = 330
    c.rectangle([MARGIN, skyline_top, PAGE - MARGIN, lead_bottom], fill=(48, 18, 18))
    draw_skyline(
        c,
        MARGIN,
        PAGE - MARGIN,
        lead_bottom,
        [
            (56, 90, 90),
            (176, 70, 130),
            (276, 110, 80),
            (416, 80, 120),
            (536, 100, 85),
            (676, 70, 140),
            (776, 120, 95),
        ],
    )
    # smoke kept low, clear of the headline; flame rises from a tower
    draw_smoke(c, [(240, 306, 26), (264, 278, 30), (738, 302, 28), (762, 274, 22)])
    draw_flame(c, 725, skyline_top, 62, 50)

    c.text((48, 158), "GAZA  •  LEAD STORY", font=load(SANS_BOLD, 24), fill=GILT)
    headline_face = load(SERIF_BOLD, 44)
    headline = fit_words(
        c,
        "SECOND HAMAS SECURITY CHIEF KILLED IN GAZA IN 24 HOURS",
        headline_face,
        PAGE - 96,
    )
    paragraph(c, 48, 192, headline, headline_face, "white", 54)
    # caption band over the skyline base so the text never sits on windows
    c.rectangle([MARGIN, 428, PAGE - MARGIN, lead_bottom], fill=(48, 18, 18))
    c.text(
        (48, 436),
        "Mohammad Abu al-Ouf dies with his wife and two daughters in a strike on Gaza City.",
        font=load(SANS, 22),
        fill=(220, 225, 235),
    )

    # ---------- 2x2 story grid ----------
    cards = [
        (
            "UKRAINE",
            CRIMSON,
            "KYIV HITS TWO RUSSIAN OIL REFINERIES IN SAMARA",
            "Fires at the Syzran and Kuibyshev plants, 800 km from the border; Putin vows retaliation.",
        ),
        (
            "SPACE",
            SEA,
            "PAKISTAN'S FIRST ASTRONAUT BOARDS CHINA'S STATION",
            "Shenzhou-24 docks at Tiangong; Zeeshan Ali is the first foreign guest aboard the station.",
        ),
        (
            "PACIFIC",
            (90, 70, 130),
            "AUSTRALIA SIGNS SECURITY TREATY WITH SOLOMON ISLANDS",
            "The pact bars foreign military bases in the Solomons and deepens Canberra's Pacific role.",
        ),
        (
            "MARKETS",
            (30, 90, 40),
            "AI SELL-OFF HITS STOCKS AS NVIDIA SLIDES",
            "Nvidia falls about 7% and Japan's Nikkei drops 2.76% as doubts over the AI boom grow.",
        ),
    ]
    card_w, card_h, gap = 488, 196, 8
    grid_x, grid_y = MARGIN, 490
    for idx, (kicker, accent, head, body) in enumerate(cards):
        x = grid_x + (idx % 2) * (card_w + gap)
        y = grid_y + (idx // 2) * (card_h + gap)
        c.rectangle([x, y, x + card_w, y + card_h], fill=PAPER, outline=BORDER, width=2)
        c.rectangle([x, y, x + card_w, y + 44], fill=accent)
        c.text((x + 16, y + 8), kicker, font=load(SANS_BOLD, 22), fill="white")
        head_face = load(SERIF_BOLD, 26)
        head_lines = fit_words(c, head, head_face, card_w - 32)
        after_head = paragraph(c, x + 16, y + 54, head_lines, head_face, BODY_INK, 31)
        body_face = load(SANS, 19)
        body_lines = fit_words(c, body, body_face, card_w - 32)[:2]
        paragraph(c, x + 16, after_head + 4, body_lines, body_face, BODY_GREY, 24)

    # ---------- bottom strip: United States ----------
    c.rectangle([MARGIN, 906, PAGE - MARGIN, 1000], fill=INK)
    c.text((48, 918), "UNITED STATES", font=load(SANS_BOLD, 22), fill=GILT)
    c.text(
        (48, 946),
        "Trump awards Giuliani the Medal of Freedom; unclassified CIA system breached.",
        font=load(SANS, 20),
        fill="white",
    )

    page.save(OUT, optimize=True)
    print(f"saved {OUT}")


if __name__ == "__main__":
    build_page()
