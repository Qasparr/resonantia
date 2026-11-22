# 93
# ---------------------------------------------------------------------
# nfo_terminal.py -- The DAMN NFO viewer, expanded into the
# terminal: scene .nfo files read as they were written to be seen,
# and shown on the terminal the reader is actually sitting at.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XXII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# Epigraph: "it expanded the ascii/ansi damn nfo viewer into the
# terminal" -- the founder's own description of this step, spoken
# of the Meta AI session's undelivered build (XXII Nov 2026). The
# expansion is built here instead, in the house, on the house's
# own ASCII engine.
#
# DOCTRINE -- A SIBLING, NOT A FORK: this viewer stands beside
# resonance/studio/ascii.py the way pyramidasphere.py stands
# beside the visualizer. The CP437 discipline is the engine's --
# its seated table (CP437_CHARS), its refusal of unseated bytes by
# name -- IMPORTED, never forked: there is one CP437 table in the
# house and this module reads through it. What ascii.py strikes
# (the writer, the renderer, the dial frame), this module SHOWS:
# the reading half of the DAMN lineage. Like the engine, it
# renders; it does not weigh.
#
# MECHANISM -- THE READING, BYTE TO TERMINAL:
#   (1) THE TRAILER IS LIFTED FIRST: a SAUCE 00 record, where the
#       file carries one, sits in the last 128 bytes (with its
#       COMNT comment block ahead of it where the comment count
#       says so). It is parsed into its fields -- title, author,
#       group, date, file size, data and file types -- and lifted
#       off the body, to be shown as a header or footer line. A
#       file without SAUCE renders without complaint.
#   (2) THE EOF MARK IS HONOURED: the classic 0x1A byte ends the
#       text, as it ended it on DOS -- the body is cut at the
#       first 0x1A and everything past it is not content.
#   (3) THE BODY IS READ THROUGH THE TABLE: lines split at the
#       byte level (CRLF and LF), tabs expanded to the 8-column
#       stops the scene's editors used, every other byte read
#       through ascii.CP437_CHARS -- a byte with no seat is
#       REFUSED BY NAME, never approximated, the engine's law.
#   (4) ANSI INTENT IS PASSED THROUGH SANELY: ANSI art carries
#       its colour as embedded ESC sequences. SGR sequences (the
#       colour and weight intent) are parsed out of the byte
#       stream and, in colour mode, re-emitted around the text
#       they governed, with a reset closed at the line's end so
#       colour never bleeds past its own line. In --no-color
#       mode they are dropped whole: the output carries no escape
#       byte at all. Non-SGR sequences (cursor addressing and its
#       kin) are dropped in both modes -- a line renderer has no
#       cursor to address, and says so below rather than pretend.
#
# MECHANISM -- THE WIDTH LAW: the scene wrote to 80 columns and
# DAMN-style viewers do not wrap art. Neither does this one: a
# line renders at its true width, whole, whether that is 80 or
# another number the author chose. Wrapping NFO art would break
# the picture to save the frame; the frame yields.
#
# MECHANISM -- PAGING WITHOUT A TTY: every render is a list of
# lines first and a print second, so tests weigh the viewer with
# no terminal in the room. Paging is a pure slice -- page_lines
# takes a 1-based page and a page size and returns that page's
# lines; the CLI prints one page when --page is named and the
# whole file otherwise. Deterministic, and driven by arguments,
# never by keystrokes the tests cannot send.
#
# BOUNDARIES -- WHAT THE CLASSIC DAMN VIEWER DOES THAT THIS ONE
# DELIBERATELY DOES NOT REPRODUCE, NAMED IN THE OPEN:
#   * Interactive scroll keys and keyboard navigation. The DAMN
#     viewer pages by keypress at a live terminal; this viewer
#     pages by argument (--page N), so its whole behaviour is
#     testable without a TTY.
#   * Its file browser, menu shell, and built-in editor. This is
#     a viewer: one file in, its lines out. It edits nothing.
#   * The CP437 control pictures at bytes 0x01-0x1E (the card
#     suits and faces the old viewers drew). ascii.py seats only
#     the printable range, where the stdlib codec witnesses the
#     table; a body byte in the unseated range is refused by
#     name, following the engine's doctrine, rather than
#     silently pictured here.
#   * Charset guessing. Some modern viewers sniff UTF-8. This
#     one takes CP437 by law -- an .nfo is a CP437 artifact --
#     and a file that is not CP437 fails by name at the byte
#     that has no seat, instead of being misread politely.
#
# INPUTS / PROCESSES / OUTPUTS / TOLERANCES (the four elements):
#   Inputs:    the raw bytes of an .nfo / .diz / .txt file (from
#              render_nfo's caller, or a path for render_file and
#              the CLI); the colour and SAUCE switches; a page
#              number and size where paging is wanted.
#   Processes: lift SAUCE -> cut at 0x1A -> split lines at the
#              byte level -> per line: scan out ANSI sequences,
#              expand tabs, seat every byte through the CP437
#              table -> re-emit SGR intent in colour mode ->
#              attach the SAUCE line as footer or header -> slice
#              the requested page.
#   Outputs:   lists of rendered lines (Unicode text, ANSI SGR
#              embedded in colour mode); the CLI prints them.
#              module_checks() returns [(name, passed, got)] on
#              the cubes pattern.
#   Tolerances: a rendered text line's character count equals
#              its source line's byte count exactly (one byte,
#              one glyph -- tabs and ANSI sequences excepted, and
#              both are structure, not glyphs). No line is wrapped
#              or truncated, ever. SAUCE fields are read at their
#              spec offsets and nowhere else.
# ---------------------------------------------------------------------

import argparse
import json
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

from . import ascii as asc

EOF_BYTE = 0x1A       # the DOS end-of-file mark the scene honoured
TAB_STOP = 8          # the scene's editors tabbed to 8-column stops

# ---------------------------------------------------------------------
# SAUCE -- the Standard Architecture for Universal Comment
# Extensions record: 128 bytes at the file's tail, the scene's
# own metadata trailer. Offsets per the SAUCE 00 spec.
# ---------------------------------------------------------------------

SAUCE_SIZE = 128
SAUCE_ID = b"SAUCE"
SAUCE_VERSION = b"00"
_COMMENT_ID = b"COMNT"
_COMMENT_LINE = 64    # each SAUCE comment line is 64 bytes


@dataclass(frozen=True)
class SauceRecord:
    """One parsed SAUCE 00 record: the trailer's fields, seated.

    MECHANISM: the text fields are stored stripped of their
    space/NUL padding, as the spec writes them; the date is kept
    raw (CCYYMMDD) with date_iso as its reading form. file_size
    is the size the record claims for the file before the trailer
    was appended -- reported, never enforced.
    """

    title: str
    author: str
    group: str
    date: str           # raw, CCYYMMDD as written
    file_size: int
    data_type: int
    file_type: int
    comments: int

    @property
    def date_iso(self):
        """The date read as YYYY-MM-DD, where it is 8 digits."""
        if len(self.date) == 8 and self.date.isdigit():
            return f"{self.date[0:4]}-{self.date[4:6]}-{self.date[6:8]}"
        return self.date

    def line(self):
        """The record as one footer/header line. Pure.

        MECHANISM: the non-empty fields in spec order -- title,
        author, group, date -- joined under the SAUCE name, so
        the line identifies its own source. A record with no
        readable field still names itself: "[SAUCE]".
        """
        parts = [p for p in (self.title, self.author, self.group,
                             self.date_iso) if p]
        return "[SAUCE] " + " | ".join(parts) if parts else "[SAUCE]"


def _sauce_text(raw):
    """A SAUCE text field's bytes -> its reading form. Pure.

    MECHANISM: trailing NUL and space padding is stripped, then
    the bytes are read through the standard library's cp437
    codec -- the same witness ascii.py verifies its whole table
    against before seating a glyph.
    """
    return raw.rstrip(b"\x00 ").decode("cp437")


def parse_sauce(data):
    """The SAUCE 00 record at the data's tail, or None. Pure.

    MECHANISM: the record is exactly the last SAUCE_SIZE bytes;
    it is a SAUCE record only when its first five bytes are the
    SAUCE id and its version bytes are "00". Fields are read at
    their spec offsets and nowhere else. Anything else -- a
    shorter file, a different trailer -- is not SAUCE, and the
    function says so by returning None, not by guessing.
    """
    if len(data) < SAUCE_SIZE:
        return None
    record = data[-SAUCE_SIZE:]
    if record[0:5] != SAUCE_ID or record[5:7] != SAUCE_VERSION:
        return None
    return SauceRecord(
        title=_sauce_text(record[7:42]),
        author=_sauce_text(record[42:62]),
        group=_sauce_text(record[62:82]),
        date=_sauce_text(record[82:90]),
        file_size=struct.unpack_from("<I", record, 90)[0],
        data_type=record[94],
        file_type=record[95],
        comments=record[104],
    )


def split_sauce(data):
    """(body bytes, SauceRecord | None): the trailer lifted. Pure.

    MECHANISM: where parse_sauce finds a record, the record's
    128 bytes are lifted off the tail; where its comment count
    is non-zero, the comment block ahead of it -- the COMNT id
    plus 64 bytes per comment line -- is lifted too, but only
    when the COMNT id actually stands where the count says it
    should: the count is a claim, the id is the witness. A file
    without SAUCE returns itself whole, with None.
    """
    sauce = parse_sauce(data)
    if sauce is None:
        return data, None
    end = len(data) - SAUCE_SIZE
    if sauce.comments:
        block = len(_COMMENT_ID) + _COMMENT_LINE * sauce.comments
        start = end - block
        if start >= 0 and data[start:start + len(_COMMENT_ID)] \
                == _COMMENT_ID:
            end = start
    return data[:end], sauce


def strip_eof(data):
    """The body cut at the first EOF byte (0x1A). Pure.

    MECHANISM: on DOS the byte ended the file whatever followed
    it, and the scene's files still carry it -- often just ahead
    of the SAUCE trailer. Everything from the first 0x1A on is
    not content and is cut; a body with no 0x1A passes whole.
    """
    cut = data.find(bytes([EOF_BYTE]))
    return data if cut < 0 else data[:cut]


# ---------------------------------------------------------------------
# The line scan -- ANSI sequences out, tabs expanded, bytes seated.
# ---------------------------------------------------------------------

_CSI = re.compile(rb"\x1b\[([0-9;]*)([A-Za-z])")


def _line_segments(raw):
    """One raw line's bytes -> segments: ("text", str) | ("sgr", str).

    MECHANISM: a left-to-right byte scan. An ESC[...m sequence
    closes the current text run and seats an SGR segment with
    its parameter string (an empty parameter list reads as "0",
    the reset it means). Any other CSI sequence is structure
    this viewer does not honour (see the header's boundaries)
    and is dropped; a lone ESC byte is dropped with it. A tab
    expands to the next TAB_STOP column of the text so far --
    SGR segments are zero-width and do not move the column.
    Every remaining byte is seated through asc.CP437_CHARS; a
    byte with no seat raises ValueError naming the byte, the
    engine's refusal carried into the viewer whole.
    """
    segments = []
    chars = []
    column = 0
    i = 0
    while i < len(raw):
        byte = raw[i]
        if byte == 0x1B:
            match = _CSI.match(raw, i)
            if match is not None:
                if match.group(2) == b"m":
                    if chars:
                        segments.append(("text", "".join(chars)))
                        chars = []
                    params = match.group(1).decode("ascii")
                    segments.append(("sgr", params or "0"))
                i = match.end()
            else:
                i += 1
            continue
        if byte == 0x09:
            spaces = TAB_STOP - (column % TAB_STOP)
            chars.append(" " * spaces)
            column += spaces
            i += 1
            continue
        glyph = asc.CP437_CHARS.get(byte)
        if glyph is None:
            raise ValueError(
                f"byte 0x{byte:02X} carries no seated CP437 glyph; "
                "the viewer refuses to approximate it")
        chars.append(glyph)
        column += 1
        i += 1
    if chars:
        segments.append(("text", "".join(chars)))
    return segments


def _render_segments(segments, color):
    """Segments -> one terminal line. Pure.

    MECHANISM: text passes as read. In colour mode each SGR
    segment is re-emitted as its escape, and where any escape
    was emitted the line is closed with a reset, so the colour
    an author opened on a line never bleeds into the next line
    or the reader's prompt. In no-colour mode SGR segments are
    dropped whole -- the line carries no escape byte at all.
    """
    out = []
    coloured = False
    for kind, value in segments:
        if kind == "sgr":
            if color:
                out.append(f"\x1b[{value}m")
                coloured = True
        else:
            out.append(value)
    line = "".join(out)
    if coloured:
        line += "\x1b[0m"
    return line


# ---------------------------------------------------------------------
# The render -- bytes in, terminal lines out.
# ---------------------------------------------------------------------

def render_nfo(data, color=True, show_sauce=True,
               sauce_position="footer"):
    """Raw .nfo bytes -> the terminal lines that show them. Pure.

    MECHANISM: the pipeline of the header, in its order --
    split_sauce lifts the trailer, strip_eof cuts the body at
    0x1A, the body splits into lines at the byte level (CRLF
    and LF both split; one trailing empty line from the file's
    final ending is dropped, the decode's own convention in
    ascii.py), and each line is scanned and rendered. Where a
    SAUCE record was lifted and show_sauce stands, its line is
    attached at the foot (sauce_position "footer", the default)
    or the head ("header"); any other position is refused by
    name. Lines are never wrapped and never truncated.
    """
    if sauce_position not in ("footer", "header"):
        raise ValueError(
            f"sauce_position must be 'footer' or 'header', got "
            f"{sauce_position!r}")
    body, sauce = split_sauce(data)
    body = strip_eof(body)
    raw_lines = body.replace(b"\r\n", b"\n").split(b"\n")
    if raw_lines and raw_lines[-1] == b"":
        raw_lines.pop()
    lines = [_render_segments(_line_segments(raw), color)
             for raw in raw_lines]
    if sauce is not None and show_sauce:
        if sauce_position == "header":
            lines.insert(0, sauce.line())
        else:
            lines.append(sauce.line())
    return lines


def render_file(path, color=True, show_sauce=True,
                sauce_position="footer"):
    """An .nfo file at `path` -> its rendered terminal lines."""
    return render_nfo(Path(path).read_bytes(), color=color,
                      show_sauce=show_sauce,
                      sauce_position=sauce_position)


# ---------------------------------------------------------------------
# Paging -- the viewer's pages as pure slices.
# ---------------------------------------------------------------------

def page_count(lines, page_size):
    """How many pages `lines` makes at `page_size` to a page. Pure."""
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    return (len(lines) + page_size - 1) // page_size


def page_lines(lines, page, page_size):
    """One 1-based page of `lines`. Pure.

    MECHANISM: a plain slice -- page 1 is the first page_size
    lines, and so on. A page past the end returns an empty list
    (the reader has walked off the file's foot; there is nothing
    to show and nothing to invent). page and page_size below 1
    are refused by name.
    """
    if page <= 0:
        raise ValueError("page is 1-based and must be positive")
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    start = (page - 1) * page_size
    return list(lines[start:start + page_size])


# ---------------------------------------------------------------------
# Self-checks -- on the cubes pattern: [(name, passed, got)].
# ---------------------------------------------------------------------

def _synthetic_sauce(title="TWILIGHT QORE", author="QASPARR",
                     group="AXONEME", date="20261122",
                     file_size=12345):
    """A synthetic SAUCE 00 record with known fields, for checks.

    MECHANISM: the fields are written at their spec offsets into
    a zeroed 128-byte record, space-padded as the spec writes
    them, so the parser is judged against bytes built by an
    independent hand -- the test's, not its own.
    """
    record = bytearray(SAUCE_SIZE)
    record[0:7] = SAUCE_ID + SAUCE_VERSION

    def put(offset, width, text):
        raw = text.encode("ascii")[:width]
        record[offset:offset + width] = raw + b" " * (width - len(raw))

    put(7, 35, title)
    put(42, 20, author)
    put(62, 20, group)
    put(82, 8, date)
    struct.pack_into("<I", record, 90, file_size)
    record[94] = 1
    record[95] = 1
    return bytes(record)


def module_checks():
    """Self-checks for the terminal viewer.

    MECHANISM: each check builds its witness independently of
    the code it judges -- the block glyphs round-trip through
    ascii.py's own encoder, the SAUCE record is synthetic bytes
    at spec offsets, the EOF cut and the 80-column law are
    measured on the rendered lines themselves. Returns
    [(name, passed, got)] on the cubes pattern.
    """
    checks = []

    glyphs = "█▓▒░ ▄▀▌▐ │─┌┐└┘ ═║╔╗╚╝"
    data = asc.encode_cp437([glyphs])
    rendered = render_nfo(data, color=False, show_sauce=False)
    checks.append(("CP437 round-trip: the block and box glyphs "
                   "render back whole through the engine's table",
                   rendered == [glyphs], rendered))

    body = asc.encode_cp437(["a body that carries a trailer"])
    record = _synthetic_sauce()
    sauce = parse_sauce(body + record)
    ok = (sauce is not None and sauce.title == "TWILIGHT QORE"
          and sauce.author == "QASPARR" and sauce.group == "AXONEME"
          and sauce.date_iso == "2026-11-22"
          and sauce.file_size == 12345)
    checks.append(("SAUCE parse: a synthetic record's fields land "
                   "at their spec offsets", ok,
                   None if sauce is None else sauce.line()))
    stripped, _ = split_sauce(body + record)
    checks.append(("SAUCE strip: the trailer is lifted off the "
                   "body whole", stripped == body,
                   len(stripped)))

    eof_data = asc.encode_cp437(["before the mark"]) \
        + bytes([EOF_BYTE]) + b"after the mark is not content"
    rendered = render_nfo(eof_data, color=False, show_sauce=False)
    checks.append(("EOF cut: nothing past the 0x1A mark renders",
                   rendered == ["before the mark"], rendered))

    line80 = "█" * 80
    rendered = render_nfo(asc.encode_cp437([line80]), color=False,
                          show_sauce=False)
    checks.append(("the 80-column law: a full-width line renders "
                   "at exactly 80 characters, unwrapped",
                   len(rendered) == 1 and len(rendered[0]) == 80,
                   [len(line) for line in rendered]))
    return checks


# ---------------------------------------------------------------------
# The CLI -- the studio's idiom: subcommands, the view as text,
# the checks as JSON whole on stdout.
# ---------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="resonance.studio.nfo_terminal",
        description="The DAMN NFO viewer in the terminal: CP437 "
                    ".nfo files shown as they were written to be "
                    "seen. It renders; it does not weigh.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_view = sub.add_parser("view", help="show an .nfo in the terminal")
    p_view.add_argument("file")
    p_view.add_argument("--no-color", action="store_true",
                        help="drop all ANSI colour intent; the "
                             "output carries no escape bytes")
    p_view.add_argument("--no-sauce", action="store_true",
                        help="do not show the SAUCE line")
    p_view.add_argument("--sauce-position",
                        choices=("footer", "header"), default="footer")
    p_view.add_argument("--page", type=int,
                        help="print only this 1-based page")
    p_view.add_argument("--page-size", type=int, default=25,
                        help="lines per page when --page is named")

    sub.add_parser("check", help="run the viewer's self-checks")

    args = parser.parse_args(argv)

    if args.command == "view":
        lines = render_file(args.file, color=not args.no_color,
                            show_sauce=not args.no_sauce,
                            sauce_position=args.sauce_position)
        if args.page is not None:
            lines = page_lines(lines, args.page, args.page_size)
        sys.stdout.write("\n".join(lines) + "\n")
        return 0

    if args.command == "check":
        results = module_checks()
        facts = {"checks": [{"name": name, "passed": passed,
                             "got": got}
                            for name, passed, got in results],
                 "passed": sum(1 for _, p, _ in results if p),
                 "total": len(results)}
        print(json.dumps(facts, indent=2))
        return 0 if facts["passed"] == facts["total"] else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())


# ---------------------------------------------------------------------
# Closing motto: "Live, Love, and let Love, Live."
# 93 — Live, Love, and let Love, Live.
# ---------------------------------------------------------------------
