# 93
# ---------------------------------------------------------------------
# ascii.py -- The ASCII Engine: a rendering engine in the DAMN NFO
# viewer lineage -- CP437 text, struck and shown.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# DOCTRINE -- THIS ENGINE RENDERS; IT DOES NOT WEIGH. The house's
# engine audit (XVI Nov 2026) found no ASCII engine and reported the
# house's own standing research beside the absence: "ASCII seats
# addresses; it does not weigh" (pontifex, MACHINE-FORM-AND-CIPHER-
# BREAKDOWN §II). The founder's answer the same night (XVII Nov
# 2026, 00:14 EST) -- "Yhe Damnnfo viewer ascii engine", read: "The
# DAMN NFO viewer -- ascii engine" -- reframes the seat without
# moving the doctrine: pontifex is untouched, ASCII becomes no
# weighing bank, and the ASCII ENGINE is a RENDERING engine in the
# lineage of the DAMN NFO Viewer, the classic utility of the
# release-scene era (the founder's own XDCC/IRC years) that showed
# .nfo files as they were written to be seen: in CP437, the IBM PC
# character set, blocks and box-drawing at their true code points.
# What the DAMN viewer showed, this engine strikes.
#
# MECHANISM -- THREE INSTRUMENTS, ONE CHARACTER SET:
#   (1) THE NFO WRITER: house text in, a scene-form .nfo out --
#       CP437-encoded bytes, the classic layout (a framed header
#       block, ruled sections, dotted-leader release info, the
#       Flagpole at the foot), the scene's 80-column law enforced,
#       DOS line endings (CRLF) as the scene wrote them.
#   (2) THE IMAGE RENDERER: a still image in, ASCII art out --
#       luminance weighed through the CP437 shade ramp with the
#       half-blocks seated where the image's own halves differ,
#       aspect-corrected for the terminal cell.
#   (3) THE DIAL FRAME: one frame of the Double-Letter Dial as
#       ASCII -- the visualizer's per-seat gains (resonance/studio/
#       visualize.py) drawn as lamps of block characters, the seat
#       geometry imported from the visualizer, never forked.
#
# MECHANISM -- THE BYTES ARE THE DOCTRINE: CP437 here is a table,
# not a hope. Every glyph this engine can emit carries its code
# point in CP437_POINTS below, and every entry in that table was
# verified against the standard library's cp437 codec before it
# was seated (the tests re-verify the whole table, glyph by glyph).
# A character with no seat is REFUSED BY NAME -- never replaced by
# a Unicode lookalike pasted into a UTF-8 file and called CP437.
# The one stated exception is TRANSLITERATION, the scene's own
# practice: a short, printed list of typographic characters (the
# em dash, the curly quote, the Greek capitals that are Latin
# homoglyphs) is folded to its seated form before encoding, in the
# open, in the table below -- and anything outside even that list
# still refuses.
#
# MECHANISM -- THE CONTROL-PICTURE SEAT IS NOT TAKEN: classic
# CP437 also pictures glyphs at bytes 0x01-0x1E (the card suits,
# the smiling faces the DAMN viewer drew). Those bytes are control
# codes to every text codec, this host's included, so a file
# carrying them cannot be verified byte-for-glyph by the codec
# that witnesses the rest of the table. This engine seats only the
# printable range (0x20 and above), where the witness holds; the
# unseated range is named here rather than silently used.
#
# INPUTS / PROCESSES / OUTPUTS / TOLERANCES (the four elements):
#   Inputs:    text (title, info pairs, body) for the writer; a
#              PIL image or image path for the renderer; a gains
#              vector in the visualizer's seat order, with the
#              seats themselves, for the dial frame.
#   Processes: transliterate -> seat (CP437 table) -> lay out
#              (80-column law, box and rule geometry) -> encode
#              (CRLF, CP437 bytes). For images: luminance -> sub-
#              cell grid (aspect-corrected) -> nearest-coverage
#              glyph per cell. For the dial: seat_x geometry ->
#              character slots -> lamp fills by gain.
#   Outputs:   .nfo files and ASCII-art files as true CP437 bytes,
#              each with a plain-text (Unicode) preview spelling of
#              the same lines for modern readers; JSON run
#              summaries on stdout from the CLI.
#   Tolerances: no NFO line exceeds 80 characters, ever -- the
#              writer raises rather than overflow. The renderer's
#              glyph choice is nearest-coverage by squared error,
#              deterministic, ties to the earlier candidate. The
#              dial frame's slots are unique per pair by
#              construction (collision probing, stated below).
# ---------------------------------------------------------------------

import argparse
import json
import math
import sys
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image

from . import visualize
from .proofs import AUTHORSHIP, FLAGPOLE

# ---------------------------------------------------------------------
# The CP437 table -- every glyph this engine may emit, at its true
# code point. The printable ASCII range seats itself (0x20-0x7E map
# to themselves, as they do in CP437); the extended glyphs below
# were each verified against the stdlib cp437 codec before seating.
# ---------------------------------------------------------------------

CP437_POINTS = {chr(c): c for c in range(0x20, 0x7F)}
CP437_POINTS.update({
    # The shade ramp and the blocks -- the renderer's alphabet.
    "░": 0xB0, "▒": 0xB1, "▓": 0xB2,
    "█": 0xDB, "▄": 0xDC, "▀": 0xDF, "▌": 0xDD, "▐": 0xDE,
    "■": 0xFE,
    # Single rule and box-drawing -- the writer's rules.
    "─": 0xC4, "│": 0xB3, "┌": 0xDA, "┐": 0xBF, "└": 0xC0, "┘": 0xD9,
    "├": 0xC3, "┤": 0xB4, "┬": 0xC2, "┴": 0xC1, "┼": 0xC5,
    # Double rule and box-drawing -- the writer's frame.
    "═": 0xCD, "║": 0xBA, "╔": 0xC9, "╗": 0xBB, "╚": 0xC8, "╝": 0xBC,
    "╠": 0xCC, "╣": 0xB9, "╦": 0xCB, "╩": 0xCA, "╬": 0xCE,
    # The middle dot, the scene's separator.
    "·": 0xFA,
    # The Greek small letters and signs CP437 itself seats -- the
    # house weighs in Greek elsewhere; here they are only letters.
    "α": 0xE0, "π": 0xE3, "Σ": 0xE4, "σ": 0xE5, "µ": 0xE6,
    "τ": 0xE7, "Φ": 0xE8, "Θ": 0xE9, "Ω": 0xEA, "δ": 0xEB,
    "∞": 0xEC, "φ": 0xED, "ε": 0xEE,
    "±": 0xF1, "≥": 0xF2, "≤": 0xF3, "÷": 0xF6, "≈": 0xF7,
    "°": 0xF8, "√": 0xFB, "²": 0xFD,
})
CP437_CHARS = {byte: glyph for glyph, byte in CP437_POINTS.items()}

# TRANSLITERATION -- the scene folded what its character set could
# not hold, and said so. These folds happen BEFORE seating, in the
# open; anything not seated after folding is refused by name.
TRANSLITERATION = {
    "—": "-",    # em dash -> hyphen (the scene's own dash)
    "–": "-",    # en dash -> hyphen
    "‘": "'", "’": "'",   # curly single quotes -> straight
    "“": '"', "”": '"',   # curly double quotes -> straight
    "…": "...",  # ellipsis -> three dots
    "•": "·",    # bullet -> the seated middle dot
    " ": " ",    # non-breaking space -> space
    # The Greek capitals that are Latin homoglyphs fold to their
    # Latin twins, so a seat name spelled in Greek capitals (the
    # Divine Nine's Α Ε Ι Ο) survives the crossing letter for
    # letter -- the shape is the same; only the name of the
    # alphabet changes, and the fold is printed here.
    "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I",
    "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P", "Τ": "T",
    "Χ": "X",
}

EOL = "\r\n"   # the scene wrote DOS text; the .nfo keeps the law


def transliterate(text):
    """Fold the printed list of unseated characters to seated forms.

    MECHANISM: a per-character substitution over TRANSLITERATION;
    every other character passes untouched. Pure.
    """
    return "".join(TRANSLITERATION.get(ch, ch) for ch in text)


def encode_cp437(lines):
    """Lines of text -> true CP437 bytes, CRLF-ended. Fail-closed.

    MECHANISM: each line is transliterated, then every character
    is seated through CP437_POINTS; a character with no seat
    raises ValueError naming the character and its code point --
    the engine refuses rather than approximate. Lines are joined
    with CRLF and the file ends with a final CRLF, the DOS form.
    """
    out = bytearray()
    for line in lines:
        for ch in transliterate(line):
            byte = CP437_POINTS.get(ch)
            if byte is None:
                raise ValueError(
                    f"no CP437 seat for {ch!r} (U+{ord(ch):04X}); "
                    "the engine refuses to approximate it")
            out.append(byte)
        out += EOL.encode("ascii")
    return bytes(out)


def decode_cp437(data):
    """CP437 bytes -> lines of text, the encode's inverse witness.

    MECHANISM: the stream is split into lines at the BYTE level
    first (CRLF and LF endings both split), because the ending
    bytes are structure, not glyphs; then every byte of every line
    is read through CP437_CHARS (a byte with no seated glyph
    raises, naming the byte). A single trailing empty line from
    the file's final EOL is dropped, so decode(encode(lines)) ==
    lines for any lines the encoder seated.
    """
    raw_lines = data.replace(b"\r\n", b"\n").split(b"\n")
    if raw_lines and raw_lines[-1] == b"":
        raw_lines.pop()
    lines = []
    for raw in raw_lines:
        chars = []
        for byte in raw:
            glyph = CP437_CHARS.get(byte)
            if glyph is None:
                raise ValueError(
                    f"byte 0x{byte:02X} carries no seated CP437 glyph")
            chars.append(glyph)
        lines.append("".join(chars))
    return lines


def preview_text(lines):
    """The same lines as a plain-text (Unicode) preview spelling."""
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------
# The shade ramp -- the renderer's alphabet, weighed by coverage.
# ---------------------------------------------------------------------

# The ramp in ink order: each glyph's share of its cell covered in
# ink. A terminal shows ink as light, so coverage tracks luminance:
# the brighter the picture, the fuller the glyph.
RAMP = (" ", "░", "▒", "▓", "█")
RAMP_COVERAGE = (0.0, 0.25, 0.5, 0.75, 1.0)

# The half-blocks and their (upper, lower) coverage pairs. A cell
# whose upper half is lit and lower dark is not a shade at all --
# it is a half, and the half-blocks earn their seat exactly there.
HALF_TOP = "▀"        # coverage (1, 0): the upper half in ink
HALF_BOTTOM = "▄"     # coverage (0, 1): the lower half in ink

# Every glyph a rendered cell may take, with its (upper, lower)
# coverage, in tie-break order: shades first, then the halves --
# on an exact tie the shade speaks, the half only wins outright.
CELL_CANDIDATES = tuple(
    [(glyph, (cov, cov)) for glyph, cov in zip(RAMP, RAMP_COVERAGE)]
    + [(HALF_TOP, (1.0, 0.0)), (HALF_BOTTOM, (0.0, 1.0))])

# The aspect law: a terminal character cell is about twice as tall
# as it is wide, so a picture rendered one character per pixel
# would stand twice too tall. The correction factor is the cell's
# width-to-height ratio, 0.5: the row count is the column count
# scaled by the picture's own aspect and then by this factor.
CELL_ASPECT = 0.5


def cell_rows_for(cols, img_w, img_h, aspect=CELL_ASPECT):
    """How many character rows a picture earns at `cols` wide. Pure.

    MECHANISM: rows = cols * (img_h / img_w) * aspect, rounded,
    never fewer than one -- the picture's proportions carried into
    a grid whose cells are themselves twice tall as wide.
    """
    if cols <= 0 or img_w <= 0 or img_h <= 0:
        raise ValueError("columns and image dimensions must be positive")
    return max(1, int(round(cols * (img_h / img_w) * aspect)))


def luminance_grid(image, cols, aspect=CELL_ASPECT):
    """A picture -> a luminance grid at double vertical resolution.

    MECHANISM: the image is reduced to greyscale and resized to
    (cols, 2 * rows) -- two sub-rows per character row, because
    the half-blocks read the cell's upper and lower halves
    separately. Returns a float64 array of shape (2 * rows, cols)
    with values in [0, 1] (PIL's L band, 0-255, rescaled).
    """
    rows = cell_rows_for(cols, image.width, image.height, aspect)
    small = image.convert("L").resize((cols, 2 * rows), Image.LANCZOS)
    return np.asarray(small, dtype=np.float64) / 255.0


def glyph_for_cell(upper, lower):
    """The glyph whose coverage sits nearest a cell's two halves.

    MECHANISM: squared error over CELL_CANDIDATES against the
    (upper, lower) luminance pair; the first candidate at the
    minimum wins, so the choice is deterministic and shades take
    ties over halves. A uniform cell therefore always takes a
    shade (the halves' best uniform error is 0.5, the shades'
    worst is 0.03125) -- halves earn their seat only where the
    halves genuinely differ. Pure.
    """
    best_glyph, best_err = None, None
    for glyph, (cov_up, cov_lo) in CELL_CANDIDATES:
        err = (upper - cov_up) ** 2 + (lower - cov_lo) ** 2
        if best_err is None or err < best_err:
            best_glyph, best_err = glyph, err
    return best_glyph


def render_grid(grid):
    """A double-resolution luminance grid -> ASCII art lines. Pure.

    MECHANISM: consecutive sub-row pairs (upper, lower) become one
    character row through glyph_for_cell, cell by cell. The grid's
    row count must be even -- it is double resolution by
    construction; an odd count is refused, not silently halved.
    """
    grid = np.asarray(grid, dtype=np.float64)
    if grid.ndim != 2 or grid.shape[0] % 2 != 0:
        raise ValueError("the luminance grid must be 2-D with an "
                         "even number of sub-rows")
    lines = []
    for r in range(0, grid.shape[0], 2):
        lines.append("".join(
            glyph_for_cell(float(grid[r, c]), float(grid[r + 1, c]))
            for c in range(grid.shape[1])))
    return lines


def render_image(image, cols, aspect=CELL_ASPECT):
    """A PIL image -> ASCII art lines at `cols` characters wide."""
    return render_grid(luminance_grid(image, cols, aspect))


def image_to_ascii(path, cols, aspect=CELL_ASPECT):
    """An image file -> (art lines, measured facts about the strike).

    The facts name the source's true dimensions and the grid the
    render used, so the run summary reports the strike as made.
    """
    with Image.open(path) as image:
        facts = {"source": str(path), "source_px": [image.width,
                                                   image.height],
                 "cols": cols, "aspect": aspect}
        lines = render_image(image, cols, aspect)
    facts["rows"] = len(lines)
    return lines, facts


# ---------------------------------------------------------------------
# The NFO writer -- house text in, a scene-form .nfo out.
# ---------------------------------------------------------------------

NFO_WIDTH = 80        # the scene's law: no line over 80 columns
BOX_WIDTH = 78        # the frame's width, inside the law's margin
LEADER_COLUMN = 16    # info labels dot out to this column

_SHADE_RULE = "░▒▓█▓▒░"   # the header's gradient, rising and falling


def _shade_rule(width):
    """The header's decorative rule at an exact width. Pure."""
    repeats = _SHADE_RULE * (width // len(_SHADE_RULE) + 1)
    return repeats[:width]


def _wrap(text, width):
    """Word-wrap one paragraph to `width`, refusing a lawless word.

    MECHANISM: textwrap does the wrapping with long words left
    whole; any single word longer than the width can never be
    seated lawfully, so it is refused by name rather than split
    or overflowed. Pure.
    """
    for word in text.split():
        if len(word) > width:
            raise ValueError(
                f"the word {word!r} ({len(word)} chars) exceeds the "
                f"{width}-column wrap; the writer refuses to break it")
    return textwrap.wrap(text, width=width, break_long_words=False,
                         break_on_hyphens=False)


def _section_rule(label, width=BOX_WIDTH):
    """A ruled section heading: two dashes, the label, dashes out."""
    head = f"── {label} "
    return head + "─" * (width - len(head))


def _info_lines(info):
    """Release-info pairs in the scene's dotted-leader form. Pure.

    MECHANISM: two spaces, the label, dot leaders out to
    LEADER_COLUMN, ': ', then the value word-wrapped in the room
    remaining, continuation lines hanging at the value's column.
    """
    lines = []
    for label, value in info:
        prefix = f"  {label}"
        if len(prefix) >= LEADER_COLUMN:
            raise ValueError(
                f"info label {label!r} reaches past the leader column")
        head = prefix + "." * (LEADER_COLUMN - len(prefix)) + ": "
        wrapped = _wrap(str(value), BOX_WIDTH - len(head))
        if not wrapped:
            lines.append(head.rstrip())
            continue
        lines.append(head + wrapped[0])
        lines.extend(" " * len(head) + part for part in wrapped[1:])
    return lines


def build_nfo_lines(title, info=(), body=(), subtitle=None,
                    extra_sections=(), footer=True):
    """Compose a scene-form .nfo as lines of text. Pure.

    MECHANISM -- THE LAYOUT, top to foot: a double-ruled frame
    (╔ ═ ╗ ║ ╚ ╝) carrying the shade rule, the centred title (and
    subtitle where given), and the shade rule again; a RELEASE
    INFO section of dotted-leader pairs where info is given; a
    NOTES section of wrapped paragraphs where body is given; any
    extra sections verbatim under their own rules (the caller's
    lines, width-checked like everything else); and at the foot,
    under a full double rule, the house lines -- the authorship
    and the Flagpole, imported from proofs.py so the words have
    one source of truth in the house. The writer takes a title, a
    body, and the house lines; it invents no content of its own --
    every word on the page was handed to it.
    TOLERANCE: the composed lines are validated whole at the end:
    any line over NFO_WIDTH raises, naming the line. The law is
    enforced on the artifact, not merely intended by the layout.
    """
    inner = BOX_WIDTH - 2
    lines = ["╔" + "═" * inner + "╗",
             "║" + _shade_rule(inner) + "║"]
    for text in [title] + ([subtitle] if subtitle else []):
        for part in _wrap(text, inner - 4):
            lines.append("║" + part.center(inner) + "║")
    lines += ["║" + _shade_rule(inner) + "║",
              "╚" + "═" * inner + "╝", ""]
    if info:
        lines.append(_section_rule("RELEASE INFO"))
        lines.extend(_info_lines(info))
    if body:
        if info:
            lines.append("")
        lines.append(_section_rule("NOTES"))
        for i, paragraph in enumerate(body):
            if i:
                lines.append("")
            lines.extend(_wrap(paragraph, BOX_WIDTH))
    for label, section_lines in extra_sections:
        lines.append("")
        lines.append(_section_rule(label))
        lines.extend(section_lines)
    if footer:
        lines += ["", "═" * BOX_WIDTH]
        for text in (AUTHORSHIP, FLAGPOLE):
            lines.extend(_wrap(text, BOX_WIDTH))
    for line in lines:
        if len(line) > NFO_WIDTH:
            raise ValueError(
                f"an .nfo line exceeds the {NFO_WIDTH}-column law "
                f"({len(line)} chars): {line!r}")
    return lines


def write_nfo(path, title, info=(), body=(), subtitle=None,
              extra_sections=(), footer=True):
    """Compose and strike an .nfo file as true CP437 bytes.

    Returns the measured facts of the strike: the path, the byte
    count, the line count, and the widest line as written.
    """
    lines = build_nfo_lines(title, info=info, body=body,
                            subtitle=subtitle,
                            extra_sections=extra_sections,
                            footer=footer)
    data = encode_cp437(lines)
    Path(path).write_bytes(data)
    return {"out": str(path), "bytes": len(data), "lines": len(lines),
            "max_width": max(len(line) for line in lines)}


# ---------------------------------------------------------------------
# The dial frame -- one frame of the Double-Letter Dial as ASCII.
# ---------------------------------------------------------------------

SLOT_PITCH = 3        # each pair's slot: 2 glyph columns + 1 space
FRAME_HEIGHT = 10     # the lamp field's default height, in rows


def dial_slots(seats, n_slots=None):
    """Seat the pairs in character slots along the dial's axis. Pure.

    MECHANISM: the visualizer's own seat_x maps each pair's tone
    onto the slot range [0, n_slots) on the sworn logarithmic
    axis -- the geometry is imported, never forked. Pairs sharing
    a tone (13 distinct tones carry 26 pairs) ask for the same
    slot; collisions resolve by deterministic probing -- +1, -1,
    +2, -2, ... -- to the nearest free slot, so every pair owns a
    column and the seating is a pure function of the seat list.
    Returns the slot index per seat, in seat order.
    """
    if n_slots is None:
        n_slots = len(seats)
    if n_slots < len(seats):
        raise ValueError("fewer slots than seats: a pair would be "
                         "left standing without a column")
    taken = set()
    slots = []
    for seat in seats:
        want = int(round(visualize.seat_x(seat["hz"], 0, n_slots - 1)))
        slot, step = want, 0
        while slot in taken:
            step += 1
            for candidate in (want + step, want - step):
                if 0 <= candidate < n_slots and candidate not in taken:
                    slot = candidate
                    break
            else:
                continue
            break
        taken.add(slot)
        slots.append(slot)
    return slots


def _shade_for(fill):
    """The ramp glyph nearest a fill fraction in [0, 1]. Pure.

    MECHANISM: nearest RAMP_COVERAGE wins, the first at the
    minimum -- fill 0 is the space exactly, so a dark lamp is
    truly dark, with no shade dust at its foot.
    """
    best = min(range(len(RAMP)),
               key=lambda i: (abs(fill - RAMP_COVERAGE[i]), i))
    return RAMP[best]


def dial_frame(gains, seats, height=FRAME_HEIGHT, caption=None):
    """One dial frame as ASCII lines: lamps of blocks over an axis.

    MECHANISM: each pair's lamp is a 2-character column in its
    slot (dial_slots over the visualizer's geometry); the lamp's
    height in cells is gain * height, and each cell's glyph is
    the shade nearest its fill (the fraction of that cell the
    lamp's height covers), so a half-lit lamp tops out in shade,
    not in a false full block. Beneath the field: the axis rule,
    the pair labels in their slots, and the seated tones' true
    span named at the axis's feet.
    DOCTRINE -- THE AXIS IS ORDINAL, AND SAYS SO: on the sworn
    logarithmic band the 26 tones crowd into the first octave
    (100-192 Hz of [100, 1000)), so a metric character axis would
    crush every pair into its first few columns. The probing in
    dial_slots therefore spreads the cluster across the frame:
    position on this axis is the dial's ORDER, tone rising left
    to right, and the feet name the seated span honestly (the
    lowest and highest tones actually seated) rather than dress
    the frame in the full band's edges. The band's open upper sky
    -- no pair seated above 192 Hz -- is a fact of the dial,
    recorded in its own document; the lamp HEIGHTS are the
    measurement here, and they are drawn true.
    Gains are clamped to [0, 1] after validation -- a gain vector
    that does not match the seat list, or carries a non-finite
    value, is refused by name; the lamp is a display of a
    measurement made elsewhere, and this function invents none
    of it. Returns the frame as lines of text.
    """
    gains = [float(g) for g in gains]
    if len(gains) != len(seats):
        raise ValueError(
            f"{len(gains)} gains against {len(seats)} seats: the "
            "vector must speak for every seat, in seat order")
    if any(not math.isfinite(g) for g in gains):
        raise ValueError("a gain is not finite; the frame refuses "
                         "to draw an unmeasured lamp")
    gains = [min(1.0, max(0.0, g)) for g in gains]
    slots = dial_slots(seats)
    width = len(seats) * SLOT_PITCH - 1
    field = []
    for row in range(height):
        level = height - 1 - row          # this row's height from 0
        cells = [" "] * width
        for gain, slot in zip(gains, slots):
            fill = min(1.0, max(0.0, gain * height - level))
            glyph = _shade_for(fill)
            cells[slot * SLOT_PITCH] = glyph
            cells[slot * SLOT_PITCH + 1] = glyph
        field.append("".join(cells).rstrip())
    labels = [" "] * width
    for seat, slot in zip(seats, slots):
        labels[slot * SLOT_PITCH] = seat["pair"][0]
        labels[slot * SLOT_PITCH + 1] = seat["pair"][1]
    lo = f"{int(min(s['hz'] for s in seats))} Hz"
    hi = f"{int(max(s['hz'] for s in seats))} Hz"
    band = lo + " " * (width - len(lo) - len(hi)) + hi
    lines = []
    if caption:
        lines.append(caption)
    lines.extend(field)
    lines.append("─" * width)
    lines.append("".join(labels).rstrip())
    lines.append(band)
    return lines


def gains_from_audio(audio_path, seats, fps=30):
    """Strike an honest gains analysis of an audio file. The rim.

    MECHANISM: the visualizer's own doors are used and no other --
    decode_audio weighs the file, analyse returns the per-frame
    gain matrix and its reference. This helper only chooses the
    frame the demo strikes: the PEAK frame, the one whose gains
    sum highest, named by index and centre time in the result.
    Returns (gains vector, facts) with the frame's coordinates.
    """
    samples = visualize.decode_audio(audio_path)
    gains, reference = visualize.analyse(
        samples, visualize.ANALYSIS_SR, fps, seats)
    totals = gains.sum(axis=1)
    peak = int(totals.argmax())
    facts = {"source": str(audio_path), "frames": int(gains.shape[0]),
             "fps": fps, "reference": reference,
             "peak_frame": peak,
             "peak_time_s": visualize.frame_centre(peak, fps)}
    return [float(g) for g in gains[peak]], facts


# ---------------------------------------------------------------------
# The CLI -- the studio's idiom: subcommands, JSON whole on stdout.
# ---------------------------------------------------------------------

def _strike(lines, out_path, preview_path=None):
    """Write art lines as CP437 bytes (+ a Unicode preview if asked).

    Returns the measured facts of the strike.
    """
    data = encode_cp437(lines)
    Path(out_path).write_bytes(data)
    facts = {"out": str(out_path), "bytes": len(data),
             "lines": len(lines),
             "max_width": max((len(line) for line in lines), default=0)}
    if preview_path:
        Path(preview_path).write_text(preview_text(lines),
                                      encoding="utf-8")
        facts["preview"] = str(preview_path)
    return facts


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="resonance.studio.ascii",
        description="The ASCII Engine: CP437 rendering in the "
                    "DAMN NFO viewer lineage. It renders; it does "
                    "not weigh.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_nfo = sub.add_parser("nfo", help="strike a scene-form .nfo")
    p_nfo.add_argument("--title", required=True)
    p_nfo.add_argument("--subtitle")
    p_nfo.add_argument("--info", action="append", default=[],
                       metavar="LABEL=VALUE",
                       help="a release-info pair (repeatable)")
    p_nfo.add_argument("--body-file",
                       help="a text file whose paragraphs (blank-line "
                            "separated) become the NOTES section")
    p_nfo.add_argument("--out", required=True)

    p_render = sub.add_parser("render",
                              help="render an image as ASCII art")
    p_render.add_argument("image")
    p_render.add_argument("--width", type=int, default=100,
                          help="the art's width in characters")
    p_render.add_argument("--out", required=True)
    p_render.add_argument("--preview",
                          help="also write a Unicode preview file")

    p_frame = sub.add_parser("frame",
                             help="strike one dial frame as ASCII")
    p_frame.add_argument("--audio",
                         help="an audio file to weigh through the "
                              "visualizer's core (peak frame struck)")
    p_frame.add_argument("--gains",
                         help="a JSON file: a gains vector in seat "
                              "order, or an object carrying 'gains'")
    p_frame.add_argument("--height", type=int, default=FRAME_HEIGHT)
    p_frame.add_argument("--dial", help="the dial table to seat from")
    p_frame.add_argument("--out", required=True)
    p_frame.add_argument("--preview",
                         help="also write a Unicode preview file")

    args = parser.parse_args(argv)

    if args.command == "nfo":
        info = []
        for pair in args.info:
            label, sep, value = pair.partition("=")
            if not sep:
                parser.error(f"--info wants LABEL=VALUE, got {pair!r}")
            info.append((label, value))
        body = []
        if args.body_file:
            text = Path(args.body_file).read_text(encoding="utf-8")
            body = [p.replace("\n", " ").strip()
                    for p in text.split("\n\n") if p.strip()]
        facts = write_nfo(args.out, args.title, info=info, body=body,
                          subtitle=args.subtitle)
        print(json.dumps(facts, indent=2))
        return 0

    if args.command == "render":
        lines, facts = image_to_ascii(args.image, args.width)
        facts.update(_strike(lines, args.out, args.preview))
        print(json.dumps(facts, indent=2))
        return 0

    if args.command == "frame":
        seats = visualize.load_seats(visualize.dial_path(args.dial))
        if args.gains:
            raw = json.loads(Path(args.gains).read_text(
                encoding="utf-8"))
            gains = raw["gains"] if isinstance(raw, dict) else raw
            facts = {"source": f"gains file {args.gains}"}
            caption = "THE DOUBLE-LETTER DIAL -- ASCII FRAME"
        elif args.audio:
            gains, facts = gains_from_audio(args.audio, seats)
            caption = (f"THE DOUBLE-LETTER DIAL -- ASCII FRAME - "
                       f"frame {facts['peak_frame']} of "
                       f"{facts['frames']}, "
                       f"t = {facts['peak_time_s']:.2f} s")
        else:
            parser.error("frame wants --audio or --gains")
        lines = dial_frame(gains, seats, height=args.height,
                           caption=caption)
        facts.update(_strike(lines, args.out, args.preview))
        facts["seats"] = len(seats)
        print(json.dumps(facts, indent=2))
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
