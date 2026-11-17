# 93
# ---------------------------------------------------------------------
# test_studio_ascii.py -- The ASCII Engine, weighed pure.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: what is weighed here is the engine's pure core with
# no file and no ffmpeg in the room: the CP437 table against the
# standard library's own codec (the witness), the encode/decode
# round trip and the refusal of unseated characters, the NFO
# writer's 80-column law on the composed artifact, the ramp's
# monotonicity and the half-blocks' earned seat, the aspect
# correction's arithmetic, and the dial frame's shape (26 pairs
# seated, darkness for silence, a hot pair in its own column).
# The live strikes -- the plate render, the Mugetsu .nfo, the
# peak-frame demo -- are weighed by the demo run report, not here.
# ---------------------------------------------------------------------

import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance.studio import ascii as asc
from resonance.studio import visualize as viz


class CP437TableTests(unittest.TestCase):
    """The table: named glyphs at their true code points, whole."""

    def test_named_glyphs_at_their_code_points(self):
        named = {"░": 0xB0, "▒": 0xB1, "▓": 0xB2, "█": 0xDB,
                 "▄": 0xDC, "▀": 0xDF, "▌": 0xDD, "▐": 0xDE,
                 "■": 0xFE, "─": 0xC4, "│": 0xB3, "═": 0xCD,
                 "║": 0xBA, "╔": 0xC9, "╗": 0xBB, "╚": 0xC8,
                 "╝": 0xBC, "┌": 0xDA, "┐": 0xBF, "└": 0xC0,
                 "┘": 0xD9, "·": 0xFA, "α": 0xE0, "π": 0xE3,
                 "Ω": 0xEA, "°": 0xF8}
        for glyph, point in named.items():
            self.assertEqual(asc.CP437_POINTS[glyph], point, glyph)

    def test_whole_table_against_the_stdlib_codec(self):
        # The codec is the witness: every seated glyph must encode
        # to its seated byte and decode back to itself.
        for glyph, byte in asc.CP437_POINTS.items():
            self.assertEqual(glyph.encode("cp437"), bytes([byte]),
                             glyph)
            self.assertEqual(bytes([byte]).decode("cp437"), glyph)

    def test_encode_decode_round_trip(self):
        lines = ["╔═══╗ ░▒▓█ ▄▀▌▐ · α π Σ Ω", "plain ASCII 123 !?"]
        self.assertEqual(asc.decode_cp437(asc.encode_cp437(lines)),
                         lines)

    def test_encode_uses_crlf_and_ends_with_it(self):
        data = asc.encode_cp437(["one", "two"])
        self.assertTrue(data.endswith(b"\r\n"))
        self.assertEqual(data.count(b"\r\n"), 2)
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))

    def test_unseated_character_is_refused_by_name(self):
        with self.assertRaises(ValueError) as caught:
            asc.encode_cp437(["the price is €5"])
        self.assertIn("€", str(caught.exception))

    def test_transliteration_folds_the_printed_list(self):
        self.assertEqual(asc.transliterate("a—b ‘c’ ΑΕΙΟ"),
                         "a-b 'c' AEIO")
        data = asc.encode_cp437(["a—b"])
        self.assertEqual(asc.decode_cp437(data), ["a-b"])


class NFOWriterTests(unittest.TestCase):
    """The writer: the scene's form under the 80-column law."""

    def test_eighty_column_law_on_a_full_nfo(self):
        lines = asc.build_nfo_lines(
            "A TITLE LONG ENOUGH TO NEED ITS OWN WRAPPING ROOM "
            "INSIDE THE FRAME",
            info=[("Title", "Something"), ("Engine", "ascii.py"),
                  ("Note", "a value with enough words in it to "
                           "wrap onto a second leader line or two")],
            body=["A body paragraph with enough words to wrap at "
                  "the box width and keep wrapping until it has "
                  "said everything it came to say, twice."])
        self.assertTrue(lines)
        for line in lines:
            self.assertLessEqual(len(line), asc.NFO_WIDTH, line)

    def test_frame_and_flagpole_stand_in_the_layout(self):
        lines = asc.build_nfo_lines("T")
        self.assertTrue(lines[0].startswith("╔"))
        self.assertTrue(lines[0].endswith("╗"))
        joined = "\n".join(lines)
        self.assertIn("Flagpole of Claim and Coinage", joined)
        self.assertIn("Johnathan 'Qasparr' Monroe", joined)

    def test_info_leaders_dot_to_the_column(self):
        lines = asc.build_nfo_lines("T", info=[("Title", "X")])
        info_line = next(l for l in lines if l.startswith("  Title"))
        # The dots run out to the leader column; the colon sits on it.
        self.assertEqual(info_line.index(":"), asc.LEADER_COLUMN)

    def test_a_lawless_word_is_refused(self):
        with self.assertRaises(ValueError):
            asc.build_nfo_lines("T", body=["x" * 90])

    def test_the_nfo_is_true_cp437_bytes(self):
        lines = asc.build_nfo_lines("MUGETSU", info=[("Seat", "YAMI")],
                                    body=["Sung from the score."])
        data = asc.encode_cp437(lines)
        # The witness decodes the artifact whole, back to the lines.
        self.assertEqual(asc.decode_cp437(data), lines)
        # And the box glyphs sit at their CP437 points in the bytes.
        self.assertIn(bytes([0xC9]), data)   # ╔
        self.assertIn(bytes([0xCD]), data)   # ═


class RampAndRendererTests(unittest.TestCase):
    """The ramp: monotone ink; the halves where they earn it."""

    def test_ramp_monotonicity_on_uniform_cells(self):
        coverages = []
        for step in range(21):
            v = step / 20.0
            glyph = asc.glyph_for_cell(v, v)
            self.assertIn(glyph, asc.RAMP)
            idx = asc.RAMP.index(glyph)
            coverages.append(asc.RAMP_COVERAGE[idx])
        self.assertEqual(coverages, sorted(coverages))
        self.assertEqual(coverages[0], 0.0)
        self.assertEqual(coverages[-1], 1.0)

    def test_half_blocks_earn_their_seat(self):
        self.assertEqual(asc.glyph_for_cell(1.0, 0.0), "▀")
        self.assertEqual(asc.glyph_for_cell(0.0, 1.0), "▄")
        self.assertEqual(asc.glyph_for_cell(0.0, 0.0), " ")
        self.assertEqual(asc.glyph_for_cell(1.0, 1.0), "█")

    def test_aspect_correction_arithmetic(self):
        # The plate's own proportions: 1920x1280 at 100 columns.
        self.assertEqual(asc.cell_rows_for(100, 1920, 1280), 33)
        # A square picture stands half as many rows as columns.
        self.assertEqual(asc.cell_rows_for(80, 100, 100), 40)
        with self.assertRaises(ValueError):
            asc.cell_rows_for(0, 100, 100)

    def test_render_grid_halves_and_shades(self):
        grid = np.array([[1.0, 0.0, 0.5],
                         [0.0, 1.0, 0.5]])
        (line,) = asc.render_grid(grid)
        self.assertEqual(line, "▀▄▒")

    def test_render_grid_refuses_odd_subrows(self):
        with self.assertRaises(ValueError):
            asc.render_grid(np.zeros((3, 4)))

    def test_luminance_grid_shape_and_range(self):
        image = Image.new("RGB", (200, 100), (128, 128, 128))
        grid = asc.luminance_grid(image, 50)
        self.assertEqual(grid.shape,
                         (2 * asc.cell_rows_for(50, 200, 100), 50))
        self.assertTrue(np.all(grid >= 0.0) and np.all(grid <= 1.0))
        self.assertTrue(np.allclose(grid, 128 / 255.0, atol=0.02))

    def test_a_split_picture_renders_its_halves(self):
        image = Image.new("L", (40, 40), 0)
        for x in range(20, 40):
            for y in range(40):
                image.putpixel((x, y), 255)
        lines = asc.render_image(image, 20)
        for line in lines:
            self.assertEqual(line[:10], " " * 10)
            self.assertEqual(line[10:], "█" * 10)


class DialFrameTests(unittest.TestCase):
    """The frame: 26 pairs seated; silence dark; heat in its column."""

    @classmethod
    def setUpClass(cls):
        cls.seats = viz.load_seats(viz.dial_path())

    def test_twenty_six_pairs_seated_in_unique_slots(self):
        slots = asc.dial_slots(self.seats)
        self.assertEqual(len(slots), 26)
        self.assertEqual(len(set(slots)), 26)
        self.assertTrue(all(0 <= s < 26 for s in slots))
        # Tone order is preserved left to right across the frame.
        pairs_by_slot = [pair for _, pair in sorted(
            zip(slots, [s["pair"] for s in self.seats]))]
        tones = {s["pair"]: s["hz"] for s in self.seats}
        ordered = [tones[p] for p in pairs_by_slot]
        self.assertEqual(ordered, sorted(ordered))

    def test_zero_gains_render_dark(self):
        lines = asc.dial_frame([0.0] * 26, self.seats, height=6)
        field = lines[:6]
        for line in field:
            for glyph in "░▒▓█":
                self.assertNotIn(glyph, line)

    def test_a_single_hot_pair_lights_its_own_column(self):
        hot = 7   # a seat in the crowded first octave
        gains = [0.0] * 26
        gains[hot] = 1.0
        slots = asc.dial_slots(self.seats)
        lines = asc.dial_frame(gains, self.seats, height=6)
        ink_columns = set()
        for line in lines[:6]:
            for col, ch in enumerate(line):
                if ch != " ":
                    ink_columns.add(col)
        expected = {slots[hot] * asc.SLOT_PITCH,
                    slots[hot] * asc.SLOT_PITCH + 1}
        self.assertEqual(ink_columns, expected)

    def test_every_pair_is_labelled(self):
        lines = asc.dial_frame([0.5] * 26, self.seats, height=4)
        label_row = lines[4 + 1]   # after the field and the axis rule
        for seat in self.seats:
            self.assertIn(seat["pair"], label_row)

    def test_the_axis_feet_name_the_seated_span(self):
        lines = asc.dial_frame([0.0] * 26, self.seats, height=2)
        feet = lines[-1]
        self.assertIn("100 Hz", feet)
        self.assertIn("192 Hz", feet)

    def test_mismatched_or_unfinite_gains_are_refused(self):
        with self.assertRaises(ValueError):
            asc.dial_frame([0.5] * 25, self.seats)
        with self.assertRaises(ValueError):
            asc.dial_frame([float("nan")] * 26, self.seats)


if __name__ == "__main__":
    unittest.main()
