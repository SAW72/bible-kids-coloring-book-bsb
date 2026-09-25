#!/usr/bin/env python3
"""Compose the Nativity coloring story book from line-art sources.

Outputs US Letter PNGs (2550×3300, 300 dpi, two gray levels) and Letter / A4 PDFs.
Verse captions are exact Berean Standard Bible wording. See CAPTIONS.md.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import img2pdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ART = Path(__file__).resolve().parent / "art"
FONTS = Path(__file__).resolve().parent / "fonts"
PAGES = ROOT / "pages" / "nativity"
PDF_DIR = ROOT / "pdf"
CAPTIONS_MD = Path(__file__).resolve().parent / "CAPTIONS.md"

W, H = 2550, 3300
DPI = 300

# Footer matches the Vol 1 / Vol 2 pages: centered, just above the bottom edge.
FOOTER = "STEWARDOFTHEKING · BSB"
FOOTER_INK_TOP = 3206
# White pixels required between the ink of one text line and the next, and above the footer.
MIN_LINE_GAP = 48

FRED_BOLD = str(FONTS / "Fredoka-Bold.ttf")
NUNITO = str(FONTS / "Nunito-Regular.ttf")
NUNITO_BOLD = str(FONTS / "Nunito-Bold.ttf")
NUNITO_XB = str(FONTS / "Nunito-ExtraBold.ttf")
ANDIKA = str(FONTS / "Andika-Regular.ttf")
ANDIKA_BOLD = str(FONTS / "Andika-Bold.ttf")

# Exact BSB spans copied from Bible Hub. Footnote letters that Bible Hub inserts
# (Luke 2:1 “a”, Matthew 1:21 “d”) are not part of the translation and are omitted.
# https://biblehub.com/bsb/luke/1.htm
# https://biblehub.com/bsb/luke/2.htm
# https://biblehub.com/bsb/matthew/1.htm
SCENES = [
    {
        "file": "02-gabriel-mary.png",
        "art": "02-gabriel-mary.png",
        "title": "Gabriel appears to Mary",
        "reference": "Luke 1:30",
        "caption": "So the angel told her, \u201cDo not be afraid, Mary, for you have found favor with God.",
        "source_verse": "Luke 1:30",
        "source_url": "https://biblehub.com/bsb/luke/1.htm",
        "source_note": "The whole verse, as printed on Bible Hub. The angel’s words continue into verse 31, so this verse has an opening quotation mark and no closing mark.",
    },
    {
        "file": "03-mary-says-yes.png",
        "art": "03-mary-says-yes.png",
        "title": "Mary says yes",
        "reference": "Luke 1:38",
        "caption": "\u201cI am the Lord\u2019s servant,\u201d Mary answered. \u201cMay it happen to me according to your word.\u201d Then the angel left her.",
        "source_verse": "Luke 1:38",
        "source_url": "https://biblehub.com/bsb/luke/1.htm",
        "source_note": "The whole verse.",
    },
    {
        "file": "04-mary-visits-elizabeth.png",
        "art": "04-mary-visits-elizabeth.png",
        "title": "Mary visits Elizabeth",
        "reference": "Luke 1:42",
        "caption": "In a loud voice she exclaimed, \u201cBlessed are you among women, and blessed is the fruit of your womb!",
        "source_verse": "Luke 1:42",
        "source_url": "https://biblehub.com/bsb/luke/1.htm",
        "source_note": "The whole verse. Elizabeth’s words continue into verse 43, so the quotation is still open at the end of this verse.",
    },
    {
        "file": "05-joseph-dream.png",
        "art": "05-joseph-dream.png",
        "title": "An angel speaks to Joseph in a dream",
        "reference": "Matthew 1:21",
        "caption": "She will give birth to a Son, and you are to give Him the name Jesus, because He will save His people from their sins.\u201d",
        "source_verse": "Matthew 1:21",
        "source_url": "https://biblehub.com/bsb/matthew/1.htm",
        "source_note": "The whole verse. Bible Hub prints a footnote letter after “Jesus”; that letter is not part of the BSB text and is omitted. The closing quotation mark belongs to the angel’s speech, which opened in Matthew 1:20.",
    },
    {
        "file": "06-caesars-decree.png",
        "art": "06-caesars-decree.png",
        "title": "Caesar’s decree",
        "reference": "Luke 2:1",
        "caption": "Now in those days a decree went out from Caesar Augustus that a census should be taken of the whole empire.",
        "source_verse": "Luke 2:1",
        "source_url": "https://biblehub.com/bsb/luke/2.htm",
        "source_note": "The whole verse. Bible Hub prints a footnote letter after the sentence; that letter is not part of the BSB text and is omitted.",
    },
    {
        "file": "07-journey-to-bethlehem.png",
        "art": "07-journey-to-bethlehem.png",
        "title": "The journey to Bethlehem",
        "reference": "Luke 2:5",
        "caption": "He went there to register with Mary, who was pledged to him in marriage and was expecting a child.",
        "source_verse": "Luke 2:5",
        "source_url": "https://biblehub.com/bsb/luke/2.htm",
        "source_note": "The whole verse.",
    },
    {
        "file": "08-no-room-at-the-inn.png",
        "art": "08-no-room-at-the-inn.png",
        "title": "No room at the inn",
        "reference": "Luke 2:7",
        "caption": "because there was no room for them in the inn.",
        "source_verse": "Luke 2:7",
        "source_url": "https://biblehub.com/bsb/luke/2.htm",
        "source_note": "The closing clause of Luke 2:7, copied with its original lowercase. The birth and manger clauses of the same verse are the caption on the next page.",
    },
    {
        "file": "09-baby-in-the-manger.png",
        "art": "09-baby-in-the-manger.png",
        "title": "Jesus born and laid in a manger",
        "reference": "Luke 2:7",
        "caption": "And she gave birth to her firstborn, a Son. She wrapped Him in swaddling cloths and laid Him in a manger",
        "source_verse": "Luke 2:7",
        "source_url": "https://biblehub.com/bsb/luke/2.htm",
        "source_note": "The opening of Luke 2:7, through the word “manger,” stopping before the comma that joins the “no room” clause printed on the previous page.",
    },
    {
        "file": "10-angels-and-shepherds.png",
        "art": "10-angels-and-shepherds.png",
        "title": "Angels appear to the shepherds",
        "reference": "Luke 2:11",
        "caption": "Today in the city of David a Savior has been born to you. He is Christ the Lord!",
        "source_verse": "Luke 2:11",
        "source_url": "https://biblehub.com/bsb/luke/2.htm",
        "source_note": "The whole verse. The quotation opened in verse 10 and closes in verse 12, so verse 11 itself has no quotation marks.",
    },
    {
        "file": "11-shepherds-visit.png",
        "art": "11-shepherds-visit.png",
        "title": "The shepherds visit",
        "reference": "Luke 2:16",
        "caption": "So they hurried off and found Mary and Joseph and the Baby, who was lying in the manger.",
        "source_verse": "Luke 2:16",
        "source_url": "https://biblehub.com/bsb/luke/2.htm",
        "source_note": "The whole verse.",
    },
    {
        "file": "12-shepherds-tell-everyone.png",
        "art": "12-shepherds-tell-everyone.png",
        "title": "The shepherds tell everyone",
        "reference": "Luke 2:17",
        "caption": "After they had seen the Child, they spread the message they had received about Him.",
        "source_verse": "Luke 2:17",
        "source_url": "https://biblehub.com/bsb/luke/2.htm",
        "source_note": "The whole verse.",
    },
    {
        "file": "13-mary-treasures.png",
        "art": "13-mary-treasures.png",
        "title": "Mary treasures these things",
        "reference": "Luke 2:19",
        "caption": "But Mary treasured up all these things and pondered them in her heart.",
        "source_verse": "Luke 2:19",
        "source_url": "https://biblehub.com/bsb/luke/2.htm",
        "source_note": "The whole verse.",
    },
]


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text_size(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, stroke: int = 0):
    box = draw.textbbox((0, 0), text, font=face, stroke_width=stroke)
    return box[2] - box[0], box[3] - box[1], box


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = word if not cur else f"{cur} {word}"
        width, _, _ = text_size(draw, trial, face)
        if width <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    face: ImageFont.FreeTypeFont,
    fill: int = 0,
    stroke: int = 0,
) -> int:
    """Draw text whose ink starts at y. Returns the ink height."""
    width, height, box = text_size(draw, text, face, stroke)
    x = (W - width) / 2 - box[0]
    draw.text((x, y - box[1]), text, font=face, fill=fill, stroke_width=stroke, stroke_fill=0)
    return height


def draw_left_ink(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    ink_top: int,
    face: ImageFont.FreeTypeFont,
) -> int:
    """Draw text whose ink starts at ink_top. Returns the y of the ink bottom."""
    box = draw.textbbox((0, 0), text, font=face)
    draw.text((x - box[0], ink_top - box[1]), text, font=face, fill=0)
    return ink_top + (box[3] - box[1])


def draw_footer(draw: ImageDraw.ImageDraw) -> None:
    face = font(NUNITO_BOLD, 42)
    width, _, box = text_size(draw, FOOTER, face)
    x = (W - width) / 2 - box[0]
    y = FOOTER_INK_TOP - box[1]
    draw.text((x, y), FOOTER, font=face, fill=0)


def to_two_levels(page: Image.Image) -> Image.Image:
    """Force pure black and white. Grays are only anti-aliased edges."""
    return page.point(lambda p: 0 if p < 180 else 255)


def lineart(path: Path, max_w: int, max_h: int) -> Image.Image:
    im = Image.open(path).convert("L")
    scale = min(max_w / im.width, max_h / im.height)
    size = (max(1, int(round(im.width * scale))), max(1, int(round(im.height * scale))))
    im = im.resize(size, Image.Resampling.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(radius=0.7))
    # Keep the dark outline and the anti-aliased edge; drop light gray shading.
    bw = im.point(lambda p: 0 if p < 196 else 255)
    return bw


def save_page(page: Image.Image, path: Path) -> None:
    page = to_two_levels(page)
    path.parent.mkdir(parents=True, exist_ok=True)
    page.save(path, format="PNG", dpi=(DPI, DPI), optimize=True)


def compose_scene(scene: dict) -> Path:
    page = Image.new("L", (W, H), 255)
    draw = ImageDraw.Draw(page)
    cap_face = font(ANDIKA_BOLD, 78)
    ref_face = font(ANDIKA_BOLD, 64)
    max_w = W - 280
    lines = wrap(draw, scene["caption"], cap_face, max_w)
    line_h = 100
    ref_gap = 26
    _, ref_h, _ = text_size(draw, scene["reference"], ref_face)
    block_h = len(lines) * line_h + ref_gap + ref_h
    block_bottom = FOOTER_INK_TOP - 48
    block_top = block_bottom - block_h
    rule_y = block_top - 36

    art_box = (70, 56, W - 70, rule_y - 28)
    art = lineart(ART / scene["art"], art_box[2] - art_box[0], art_box[3] - art_box[1])
    ax = art_box[0] + (art_box[2] - art_box[0] - art.width) // 2
    ay = art_box[1] + (art_box[3] - art_box[1] - art.height) // 2
    page.paste(art, (ax, ay))

    draw.rectangle([160, rule_y, W - 160, rule_y + 7], fill=0)
    y = block_top
    for line in lines:
        draw_centered(draw, line, y, cap_face)
        y += line_h
    y += ref_gap - 10
    draw_centered(draw, scene["reference"], y, ref_face)
    draw_footer(draw)

    out = PAGES / scene["file"]
    save_page(page, out)
    print(f"{scene['file']}: {len(lines)} caption line(s)")
    return out


def fit_title_size(draw: ImageDraw.ImageDraw, text: str, max_w: int, start: int) -> tuple[ImageFont.FreeTypeFont, int]:
    size = start
    while size > 80:
        face = font(FRED_BOLD, size)
        stroke = max(12, size // 16)
        width, _, _ = text_size(draw, text, face, stroke)
        if width <= max_w:
            return face, stroke
        size -= 4
    face = font(FRED_BOLD, 80)
    return face, 12


def compose_cover() -> Path:
    page = Image.new("L", (W, H), 255)
    draw = ImageDraw.Draw(page)
    y = 80
    title_face, stroke = fit_title_size(draw, "The Nativity", W - 220, 210)
    y += draw_centered(draw, "The Nativity", y, title_face, fill=255, stroke=stroke)
    y += MIN_LINE_GAP
    sub = font(FRED_BOLD, 84)
    y += draw_centered(draw, "A Coloring Story Book", y, sub)
    y += MIN_LINE_GAP
    brand = font(NUNITO_XB, 54)
    y += draw_centered(draw, "Steward of the King", y, brand)
    y += MIN_LINE_GAP
    small = font(NUNITO, 36)
    y += draw_centered(draw, "Stories inspired by the Berean Standard Bible", y, small)

    art_top = y + MIN_LINE_GAP
    art_bottom = FOOTER_INK_TOP - MIN_LINE_GAP
    art = lineart(ART / "cover.png", W - 120, art_bottom - art_top)
    ax = (W - art.width) // 2
    ay = art_top + max(0, (art_bottom - art_top - art.height) // 2)
    page.paste(art, (ax, ay))
    draw_footer(draw)
    out = PAGES / "01-cover.png"
    save_page(page, out)
    return out


def compose_parent_note() -> Path:
    page = Image.new("L", (W, H), 255)
    draw = ImageDraw.Draw(page)
    # Same rounded frame as the volume parent notes, clear of the footer.
    frame_bottom = 3164
    draw.rounded_rectangle([70, 70, 2479, frame_bottom], radius=46, outline=0, width=8)

    left = 140
    right = 2410
    width = right - left
    # Single spacing, matching the volume notes (not a 48px gap between body lines).
    line_gap = 22

    def paragraph(text: str, face: ImageFont.FreeTypeFont, ink_top: int) -> int:
        for line in wrap(draw, text, face, width):
            ink_top = draw_left_ink(draw, line, left, ink_top, face) + line_gap
        return ink_top

    def heading(text: str, ink_top: int) -> int:
        face = font(NUNITO_XB, 52)
        return draw_left_ink(draw, text, left, ink_top + 10, face) + line_gap

    # Outlined bubble title, centered, same size as the volume notes.
    bubble = font(FRED_BOLD, 150)
    stroke = 12
    ink = 103
    ink += draw_centered(draw, "For Parents", ink, bubble, fill=255, stroke=stroke)
    ink += 32
    ink += draw_centered(draw, "& Sunday School", ink, bubble, fill=255, stroke=stroke)
    # At least 40px of white under the title descenders, then the centered subtitle.
    ink += 48
    subtitle = font(NUNITO_XB, 64)
    ink += draw_centered(draw, "The Nativity", ink, subtitle)
    ink += 28

    body = font(NUNITO, 40)
    ink = paragraph(
        "Twelve pictures tell the story of Jesus\u2019 birth, from the angel\u2019s visit to Mary to the night the shepherds came. Color them in order at home or in Sunday school. The pictures are gentle on purpose.",
        body,
        ink,
    )

    ink = heading("How to use this book", ink)
    ink = paragraph(
        "Read the Bible line under each picture aloud, then color. A beginning reader can try the short line. Little kids color the big shapes. Older kids can add the small flowers, stars, wings, and robes.",
        body,
        ink,
    )

    ink = heading("The story in this book", ink)
    stories = [
        "1. Gabriel appears to Mary \u2014 the angel brings good news.",
        "2. Mary says yes \u2014 she calls herself the Lord\u2019s servant.",
        "3. Mary visits Elizabeth \u2014 two mothers meet with joy.",
        "4. An angel speaks to Joseph \u2014 in a dream he is told the child\u2019s name.",
        "5. Caesar\u2019s decree \u2014 everyone goes to be registered.",
        "6. The journey to Bethlehem \u2014 Mary and Joseph travel to the city of David.",
        "7. No room at the inn \u2014 there was no room for them in the inn.",
        "8. Jesus is born \u2014 the baby is laid in a manger.",
        "9. Angels and the shepherds \u2014 good news in the fields at night.",
        "10. The shepherds visit \u2014 they find the baby in the manger.",
        "11. The shepherds tell everyone \u2014 the people are amazed.",
        "12. Mary treasures these things \u2014 she keeps them in her heart.",
    ]
    for item in stories:
        ink = paragraph(item, body, ink)

    ink = heading("Talk together", ink)
    prompts = [
        "\u2022 What did the angel tell Mary?",
        "\u2022 How did Mary answer?",
        "\u2022 Why did Mary and Joseph go to Bethlehem?",
        "\u2022 Who came to see the baby?",
        "\u2022 What did Mary keep in her heart?",
    ]
    for item in prompts:
        ink = paragraph(item, body, ink)

    ink = heading("Print & color", ink)
    ink = paragraph(
        "US Letter, portrait, actual size (100%). These files are 2550 \u00d7 3300 pixels at 300 dpi. Bold lines are for little crayons; small flowers and robes give older kids something extra to color. Ages about 3\u201312.",
        body,
        ink,
    )

    ink = heading("Personal use", ink)
    ink = paragraph(
        "Print these for your home, classroom, or Sunday school. Please don\u2019t resell the files or the prints.",
        body,
        ink,
    )
    ink = paragraph(
        "Stories inspired by the Berean Standard Bible (public domain). Kid-safe pictures: a gentle birth story, no scary violence.",
        body,
        ink,
    )

    text_bottom = ink - line_gap
    if text_bottom > frame_bottom - 24:
        raise SystemExit(f"Parent note text reaches y={text_bottom}, frame ends at {frame_bottom}")
    if FOOTER_INK_TOP - text_bottom < 40:
        raise SystemExit(f"Parent note text is {FOOTER_INK_TOP - text_bottom}px from the footer")

    draw_footer(draw)
    out = PAGES / "14-parent-note.png"
    save_page(page, out)
    print(f"parent note text bottom y={text_bottom}")
    return out


def write_captions() -> None:
    lines = [
        "# Nativity captions",
        "",
        "Exact Berean Standard Bible wording for each scene page. The BSB is public domain.",
        "Text was copied from the Bible Hub BSB pages linked below (the verse block at the top of each chapter, not the commentary).",
        "Footnote letters that Bible Hub inserts inside a verse are not part of the translation and are not printed.",
        "",
        "Quotation marks, apostrophes, and capitalization are copied as printed. Where a quotation runs across several verses, a caption that is one whole verse keeps only the marks that belong to that verse.",
        "",
        "| Page | File | Scene | Reference | Caption | Source |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for index, scene in enumerate(SCENES, start=2):
        caption = scene["caption"].replace("|", "\\|")
        lines.append(
            f"| {index} | `pages/nativity/{scene['file']}` | {scene['title']} | {scene['reference']} | {caption} | [{scene['source_verse']}]({scene['source_url']}) |"
        )
    lines.append("")
    lines.append("## Source notes")
    lines.append("")
    for scene in SCENES:
        lines.append(f"### {scene['file']}")
        lines.append("")
        lines.append(f"- Scene: {scene['title']}")
        lines.append(f"- Printed reference: {scene['reference']}")
        lines.append(f"- Printed caption: {scene['caption']}")
        lines.append(f"- Source: {scene['source_url']}")
        lines.append(f"- Note: {scene['source_note']}")
        lines.append("")
    lines.append("Pages 1 and 14 have no verse caption.")
    lines.append("")
    lines.append("- `pages/nativity/01-cover.png` — cover title only.")
    lines.append("- `pages/nativity/14-parent-note.png` — how to use the book, personal-use terms, and the BSB credit. It does not quote a verse.")
    lines.append("")
    CAPTIONS_MD.write_text("\n".join(lines), encoding="utf-8")


def build_pdfs(paths: list[Path]) -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    letter = (img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11))
    a4 = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
    letter_layout = img2pdf.get_layout_fun(pagesize=letter, fit=img2pdf.FitMode.into, auto_orient=False)
    a4_layout = img2pdf.get_layout_fun(pagesize=a4, fit=img2pdf.FitMode.into, auto_orient=False)
    files = [str(p) for p in paths]
    meta = dict(title="Steward of the King", author="Steward of the King")
    letter_pdf = PDF_DIR / "nativity-letter.pdf"
    a4_pdf = PDF_DIR / "nativity-a4.pdf"
    letter_pdf.write_bytes(img2pdf.convert(*files, layout_fun=letter_layout, **meta))
    a4_pdf.write_bytes(img2pdf.convert(*files, layout_fun=a4_layout, **meta))
    print(letter_pdf, letter_pdf.stat().st_size)
    print(a4_pdf, a4_pdf.stat().st_size)


def ink_bands(path: Path, y0: int, y1: int, x0: int = 160, x1: int = 2400, join: int = 12) -> list[tuple[int, int]]:
    """Rows of ink, joined when a gap is only a dot or a comma, not a new line."""
    im = Image.open(path).convert("L")
    px = im.load()
    rows = [
        y
        for y in range(y0, y1)
        if sum(1 for x in range(x0, x1, 3) if px[x, y] < 128) > 8
    ]
    if not rows:
        return []
    bands: list[tuple[int, int]] = []
    start = prev = rows[0]
    for y in rows[1:]:
        if y > prev + join:
            bands.append((start, prev))
            start = y
        prev = y
    bands.append((start, prev))
    return bands


def assert_gaps(bands: list[tuple[int, int]], label: str) -> None:
    gaps = []
    short = []
    for (_, bottom), (next_top, _) in zip(bands, bands[1:]):
        gap = next_top - bottom - 1
        gaps.append(gap)
        if gap < 40:
            short.append(f"y {bottom} to {next_top} is {gap}px")
    print(f"{label} gaps: {gaps}")
    if short:
        raise SystemExit(f"{label} is closer than 40px: {short}")


def assert_cover_spacing(path: Path) -> None:
    bands = ink_bands(path, 40, H)
    if len(bands) < 5:
        raise SystemExit(f"cover has only {len(bands)} ink bands")
    # The first four bands are the title, subtitle, publisher, and Bible line.
    assert_gaps(bands[:4], "cover title lines")
    gap_to_art = bands[4][0] - bands[3][1] - 1
    print(f"cover title-to-art gap: {gap_to_art}")
    if gap_to_art < 40:
        raise SystemExit(f"cover art is {gap_to_art}px under the title block")
    assert_gaps(bands[-2:], "cover above footer")


def assert_parent_spacing(path: Path) -> None:
    bands = ink_bands(path, 40, H)
    # Top rule, "For Parents", "& Sunday School", then "The Nativity".
    if len(bands) < 5:
        raise SystemExit(f"parent note has only {len(bands)} ink bands")
    title_gap = bands[3][0] - bands[2][1] - 1
    footer_gap = bands[-1][0] - bands[-2][1] - 1
    print(f"parent note title-to-subtitle gap: {title_gap}; footer gap: {footer_gap}")
    if title_gap < 40:
        raise SystemExit(f"subtitle is {title_gap}px under the title descenders")
    if footer_gap < 40:
        raise SystemExit(f"footer gap is {footer_gap}px")


def verify(paths: list[Path]) -> None:
    assert_cover_spacing(PAGES / "01-cover.png")
    assert_parent_spacing(PAGES / "14-parent-note.png")
    if len(paths) != 14:
        raise SystemExit(f"expected 14 pages, got {len(paths)}")
    for path in paths:
        im = Image.open(path)
        if im.size != (W, H):
            raise SystemExit(f"{path.name} size {im.size}")
        if im.mode != "L":
            raise SystemExit(f"{path.name} mode {im.mode}")
        colors = im.getcolors(maxcolors=4)
        if colors is None or sorted(v for _, v in colors) != [0, 255]:
            raise SystemExit(f"{path.name} colors {colors}")
        dpi = im.info.get("dpi")
        if not dpi or abs(dpi[0] - 300) > 0.1 or abs(dpi[1] - 300) > 0.1:
            raise SystemExit(f"{path.name} dpi {dpi}")
    if shutil.which("tesseract") is None:
        print("tesseract not installed; skipped caption OCR check")
        print("verify ok", len(paths), "pages")
        return
    # OCR the caption band of each scene and require the reference plus a few words.
    for scene in SCENES:
        path = PAGES / scene["file"]
        im = Image.open(path)
        band = im.crop((80, 2550, W - 80, 3180))
        band.save("/tmp/caption-band.png")
        text = subprocess.check_output(
            ["tesseract", "/tmp/caption-band.png", "stdout"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        ref = scene["reference"].replace(":", " ")
        # Tesseract often drops the colon or curly quotes. Check distinctive words.
        words = [w.strip(".,;:\"“”‘’!").lower() for w in scene["caption"].split() if len(w) > 4]
        sample = words[:4]
        hay = text.lower().replace(":", " ")
        missing = [w for w in sample if w not in hay]
        if scene["reference"].split()[0].lower() not in hay or missing:
            raise SystemExit(
                f"OCR mismatch on {scene['file']}\nexpected sample {sample} ref {scene['reference']}\n---\n{text}"
            )
        print(f"ocr ok {scene['file']}: {text.strip().splitlines()[-2:]}")
    print("verify ok", len(paths), "pages")


def main() -> None:
    PAGES.mkdir(parents=True, exist_ok=True)
    paths = [compose_cover()]
    for scene in SCENES:
        paths.append(compose_scene(scene))
    paths.append(compose_parent_note())
    write_captions()
    verify(paths)
    build_pdfs(paths)


if __name__ == "__main__":
    main()
