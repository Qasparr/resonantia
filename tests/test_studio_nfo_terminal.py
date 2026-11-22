# 93
# ---------------------------------------------------------------------
# test_studio_nfo_terminal.py -- The terminal NFO viewer, weighed
# pure.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XXII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: what is weighed here is the viewer's pure core with
# no terminal in the room: a synthetic CP437 .nfo (built through
# the ASCII engine's own encoder, the witness) rendering to the
# exact Unicode lines it was struck from; a synthetic SAUCE 00
# record (built byte by byte at the spec's offsets, an
# independent hand) landing its fields in the footer; the same
# body with and without its trailer rendering identically but
# for that footer; the EOF mark cutting what follows it; ANSI
# intent passing through in colour mode and vanishing whole in
# no-colour mode; the 80-column line surviving unwrapped; and
# the module's own self-checks standing green.
# ---------------------------------------------------------------------

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance.studio import ascii as asc
from resonance.studio import nfo_terminal as nfo


def synthetic_sauce(title="TWILIGHT QORE", author="QASPARR",
                    group="AXONEME", date="20261122", file_size=999,
                    comments=0):
    """A SAUCE 00 record built at spec offsets, plus its COMNT block.

    MECHANISM: an independent construction from the parser's --
    fields padded with spaces into a zeroed record, the comment
    block (COMNT + 64 bytes a line) built ahead of it where the
    count asks -- so the parser is judged against bytes it did
    not make.
    """
    record = bytearray(128)
    record[0:7] = b"SAUCE00"

    def put(offset, width, text):
        raw = text.encode("ascii")[:width]
        record[offset:offset + width] = raw + b" " * (width - len(raw))

    put(7, 35, title)
    put(42, 20, author)
    put(62, 20, group)
    put(82, 8, date)
    record[90:94] = file_size.to_bytes(4, "little")
    record[94] = 1
    record[95] = 1
    record[104] = comments
    block = b""
    if comments:
        block = b"COMNT" + b"a comment line".ljust(64, b" ") * comments
    return block + bytes(record)


class RenderTests(unittest.TestCase):
    """The render: CP437 in, the same art out as Unicode lines."""

    def test_synthetic_cp437_nfo_renders_to_expected_unicode(self):
        art = ["╔══════╗", "║ █▓▒░ ║", "║ ▄▀▌▐ ║",
               "╚══════╝", "└─┤ ├─┘"]
        data = asc.encode_cp437(art)
        self.assertEqual(nfo.render_nfo(data, color=False), art)

    def test_block_and_shade_glyphs_at_their_points(self):
        # The bytes are seated by hand here (0xDB full block,
        # 0xB2/0xB1/0xB0 the shades) so the decode is judged
        # against the raw scene bytes, not the encoder.
        data = bytes([0xDB, 0xB2, 0xB1, 0xB0]) + b"\r\n"
        self.assertEqual(nfo.render_nfo(data, color=False),
                         ["█▓▒░"])

    def test_eighty_column_line_is_preserved_unwrapped(self):
        line = "█" * 40 + "─" * 40
        (rendered,) = nfo.render_nfo(asc.encode_cp437([line]),
                                     color=False)
        self.assertEqual(rendered, line)
        self.assertEqual(len(rendered), 80)

    def test_eof_mark_cuts_everything_after_it(self):
        data = asc.encode_cp437(["shown"]) + b"\x1a" \
            + asc.encode_cp437(["never shown"])
        self.assertEqual(nfo.render_nfo(data, color=False),
                         ["shown"])

    def test_unseated_byte_is_refused_by_name(self):
        with self.assertRaises(ValueError) as caught:
            nfo.render_nfo(b"bad \x03 byte\r\n", color=False)
        self.assertIn("0x03", str(caught.exception))

    def test_bad_sauce_position_is_refused(self):
        with self.assertRaises(ValueError):
            nfo.render_nfo(b"x\r\n", sauce_position="middle")


class SauceTests(unittest.TestCase):
    """The trailer: parsed at its offsets, shown as one line."""

    def setUp(self):
        self.body_lines = ["the body stands", "as it was written"]
        self.body = asc.encode_cp437(self.body_lines)

    def test_sauce_fields_land_in_the_footer(self):
        data = self.body + synthetic_sauce()
        lines = nfo.render_nfo(data, color=False)
        self.assertEqual(lines[:2], self.body_lines)
        footer = lines[-1]
        for field in ("TWILIGHT QORE", "QASPARR", "AXONEME",
                      "2026-11-22"):
            self.assertIn(field, footer)

    def test_no_sauce_renders_identically_minus_footer(self):
        plain = nfo.render_nfo(self.body, color=False)
        sauced = nfo.render_nfo(self.body + synthetic_sauce(),
                                color=False)
        self.assertEqual(plain, self.body_lines)
        self.assertEqual(sauced[:-1], plain)
        self.assertEqual(len(sauced), len(plain) + 1)

    def test_sauce_can_stand_as_header(self):
        data = self.body + synthetic_sauce()
        lines = nfo.render_nfo(data, color=False,
                               sauce_position="header")
        self.assertIn("TWILIGHT QORE", lines[0])
        self.assertEqual(lines[1:], self.body_lines)

    def test_sauce_can_be_hidden(self):
        data = self.body + synthetic_sauce()
        self.assertEqual(
            nfo.render_nfo(data, color=False, show_sauce=False),
            self.body_lines)

    def test_parse_reads_the_spec_fields(self):
        sauce = nfo.parse_sauce(self.body + synthetic_sauce(
            file_size=4242))
        self.assertIsNotNone(sauce)
        self.assertEqual(sauce.title, "TWILIGHT QORE")
        self.assertEqual(sauce.author, "QASPARR")
        self.assertEqual(sauce.group, "AXONEME")
        self.assertEqual(sauce.date, "20261122")
        self.assertEqual(sauce.date_iso, "2026-11-22")
        self.assertEqual(sauce.file_size, 4242)
        self.assertEqual(sauce.comments, 0)

    def test_comment_block_is_lifted_with_the_record(self):
        data = self.body + synthetic_sauce(comments=2)
        body, sauce = nfo.split_sauce(data)
        self.assertIsNotNone(sauce)
        self.assertEqual(body, self.body)
        self.assertEqual(nfo.render_nfo(data, color=False)[:-1],
                         self.body_lines)

    def test_no_sauce_is_none_not_an_error(self):
        self.assertIsNone(nfo.parse_sauce(self.body))
        body, sauce = nfo.split_sauce(self.body)
        self.assertEqual(body, self.body)
        self.assertIsNone(sauce)


class AnsiTests(unittest.TestCase):
    """The intent: SGR through in colour, gone in no-colour."""

    def _ansi_nfo(self):
        text = "plain ".encode("ascii")
        sgr = b"\x1b[1;31m"
        red = "█▓".encode("cp437")
        return text + sgr + red + b"\r\n"

    def test_sgr_passes_through_and_the_line_is_reset(self):
        (line,) = nfo.render_nfo(self._ansi_nfo(), color=True)
        self.assertIn("\x1b[1;31m", line)
        self.assertIn("█▓", line)
        self.assertTrue(line.endswith("\x1b[0m"))

    def test_no_color_output_contains_no_escape_bytes(self):
        (line,) = nfo.render_nfo(self._ansi_nfo(), color=False)
        self.assertNotIn("\x1b", line)
        self.assertEqual(line, "plain █▓")

    def test_non_sgr_sequences_are_dropped_in_both_modes(self):
        data = b"\x1b[2J\x1b[1;1H" + "art".encode("ascii") + b"\r\n"
        for color in (True, False):
            (line,) = nfo.render_nfo(data, color=color)
            self.assertEqual(line, "art")

    def test_cli_no_color_flag_prints_no_escapes(self):
        import tempfile
        with tempfile.NamedTemporaryFile(
                "wb", suffix=".nfo", delete=False) as handle:
            handle.write(self._ansi_nfo())
            path = handle.name
        out = io.StringIO()
        with redirect_stdout(out):
            rc = nfo.main(["view", path, "--no-color"])
        self.assertEqual(rc, 0)
        self.assertNotIn("\x1b", out.getvalue())
        self.assertIn("plain █▓", out.getvalue())


class PagingTests(unittest.TestCase):
    """The pages: pure slices, 1-based, nothing invented."""

    def test_pages_slice_in_order(self):
        lines = [f"line {i}" for i in range(10)]
        self.assertEqual(nfo.page_lines(lines, 1, 4), lines[0:4])
        self.assertEqual(nfo.page_lines(lines, 3, 4), lines[8:10])
        self.assertEqual(nfo.page_count(lines, 4), 3)

    def test_a_page_past_the_end_is_empty(self):
        self.assertEqual(nfo.page_lines(["a"], 5, 4), [])

    def test_lawless_pages_are_refused(self):
        with self.assertRaises(ValueError):
            nfo.page_lines(["a"], 0, 4)
        with self.assertRaises(ValueError):
            nfo.page_lines(["a"], 1, 0)


class ModuleChecksTests(unittest.TestCase):
    """The self-checks: the module judged by its own witnesses."""

    def test_module_checks_all_pass(self):
        results = nfo.module_checks()
        self.assertTrue(results)
        for name, passed, got in results:
            self.assertTrue(passed, f"{name}: {got}")


if __name__ == "__main__":
    unittest.main()
