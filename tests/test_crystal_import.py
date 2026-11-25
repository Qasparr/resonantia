# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# SPDX-License-Identifier: AGPL-3.0-only
"""
tests/test_crystal_import.py -- unittest tests for
resonance.studio.crystal_import, the 5D Memory Crystal pattern
importer.

Run:  python3 -m unittest tests.test_crystal_import  (from repo root)
   or python3 -m unittest discover -s tests

The acceptance figures are THE SOURCE'S OWN: the pattern format,
the scales, the factory patterns, and the pitch walk were read out
of the page's script (see the module header for the extraction),
and the frequencies are asserted in BOTH tuning fields -- the
page's A4 = 440 and the house's A4 = 432 -- because the
re-grounding is the conversion's whole tuning act and it is
printed, never silent. The articulation-gate figures are the
transcription lab's measured floors (RECEIPT-FIX.md): violins
sustain 0.842 s, Salamander 0.130 s.
"""
import copy
import json
import math
import re
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resonance.abc.parser import parse_abc
from resonance.studio import crystal_import as ci


def _split_tunes(abc_text):
    blocks = re.split(r"(?m)^(X:.*)$", abc_text)
    it = iter(blocks[1:])
    return [head + body for head, body in zip(it, it)]


class TestFormatValidation(unittest.TestCase):
    def test_default_pattern_validates(self):
        data = copy.deepcopy(ci.DEFAULT_PATTERN)
        self.assertIs(ci.validate_pattern(data), data)

    def test_load_pattern_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "memory-crystal-pattern.json"
            p.write_text(json.dumps(ci.DEFAULT_PATTERN, indent=2))
            loaded = ci.load_pattern(p)
        self.assertEqual(loaded["tempo"], 72)
        self.assertEqual(loaded["scale"], "minor")
        self.assertEqual(len(loaded["tracks"]), 4)

    def test_fails_closed_missing_key(self):
        bad = copy.deepcopy(ci.DEFAULT_PATTERN)
        del bad["scale"]
        with self.assertRaises(ci.CrystalImportError) as cm:
            ci.validate_pattern(bad)
        self.assertIn("scale", str(cm.exception))

    def test_fails_closed_unknown_scale(self):
        bad = copy.deepcopy(ci.DEFAULT_PATTERN)
        bad["scale"] = "lydian"
        with self.assertRaises(ci.CrystalImportError):
            ci.validate_pattern(bad)

    def test_fails_closed_tempo_out_of_range(self):
        bad = copy.deepcopy(ci.DEFAULT_PATTERN)
        bad["tempo"] = 200
        with self.assertRaises(ci.CrystalImportError):
            ci.validate_pattern(bad)

    def test_fails_closed_step_not_binary(self):
        bad = copy.deepcopy(ci.DEFAULT_PATTERN)
        bad["tracks"][0]["pattern"][3] = 2
        with self.assertRaises(ci.CrystalImportError) as cm:
            ci.validate_pattern(bad)
        self.assertIn("strictly 0 or 1", str(cm.exception))

    def test_fails_closed_wrong_track_name(self):
        bad = copy.deepcopy(ci.DEFAULT_PATTERN)
        bad["tracks"][1]["name"] = "GLASS ORBITAL"
        with self.assertRaises(ci.CrystalImportError):
            ci.validate_pattern(bad)

    def test_fails_closed_wrong_track_count(self):
        bad = copy.deepcopy(ci.DEFAULT_PATTERN)
        bad["tracks"] = bad["tracks"][:3]
        with self.assertRaises(ci.CrystalImportError):
            ci.validate_pattern(bad)

    def test_load_pattern_missing_file_fails_closed(self):
        with self.assertRaises(ci.CrystalImportError):
            ci.load_pattern("/nonexistent/memory-crystal-pattern.json")


class TestPitchMath(unittest.TestCase):
    def test_step_seconds_is_a_sixteenth(self):
        # The source's tick: 60000/tempo/4 ms. At 72 BPM a step is
        # 0.2083 s; the beat (0.833 s) is four steps, not one.
        self.assertAlmostEqual(ci.step_seconds(72), 60.0 / 72 / 4)
        self.assertAlmostEqual(ci.step_seconds(72) * 4, 60.0 / 72)

    def test_degree_walk_matches_source_formula(self):
        # idx = step + track index; minor scale [0,2,3,5,7,9,10].
        # idx 0: k=0, n=0 (idx%3==0, no lift).
        self.assertEqual(ci.degree_walk("minor", 0), (0, 0))
        # idx 1: k=(2+0)%7=2, n=3, no lift (floor(1/7)=0).
        self.assertEqual(ci.degree_walk("minor", 1), (2, 3))
        # idx 7: k=(14+2)%7=2, n=3+12 (idx%3!=0, floor(7/7)=1).
        self.assertEqual(ci.degree_walk("minor", 7), (2, 15))

    def test_sub_horizon_first_note_both_fields(self):
        evs = ci.convert(ci.DEFAULT_PATTERN)
        e = evs[0]
        self.assertEqual(e.track_name, "SUB HORIZON")
        self.assertEqual(e.step, 0)
        self.assertEqual(e.midi, 21)                 # A0
        self.assertAlmostEqual(e.freq_page_hz, 27.5)         # 440/16
        self.assertAlmostEqual(e.freq_house_hz, 27.0)        # 432/16

    def test_every_event_carries_both_fields_in_ratio(self):
        for e in ci.convert(ci.DEFAULT_PATTERN):
            self.assertTrue(math.isclose(
                e.freq_page_hz / e.freq_house_hz, 440.0 / 432.0,
                rel_tol=1e-12))
            self.assertTrue(math.isclose(
                e.freq_house_hz,
                432.0 * 2 ** ((e.midi - 69) / 12), rel_tol=1e-12))

    def test_regrounding_bases_exact(self):
        self.assertEqual(
            ci.BASE_FREQS_432,
            [b * 432 // 440 if (b * 432) % 440 == 0 else b * 432 / 440
             for b in ci.BASE_FREQS_440])
        self.assertEqual(ci.BASE_FREQS_432, [54, 108, 216, 432])

    def test_regrounding_report_prints_both_fields(self):
        report = ci.regrounding_report(ci.DEFAULT_PATTERN)
        for name in ci.TRACK_NAMES:
            self.assertIn(name, report)
        self.assertIn("440", report)
        self.assertIn("432", report)
        self.assertIn("54", report)

    def test_velocity_preserves_page_balance(self):
        # Linear over the slider range: .34 -> 72, .055 -> 12.
        self.assertEqual(ci.velocity_of_level(0.34), 72)
        self.assertEqual(ci.velocity_of_level(0.055), 12)
        evs = ci.convert(ci.DEFAULT_PATTERN)
        vels = {e.track_name: e.velocity for e in evs}
        self.assertGreater(vels["SUB HORIZON"], vels["GLASS ORBIT"])
        self.assertGreater(vels["GLASS ORBIT"], vels["SIGNAL DUST"])


class TestSeatsAndGate(unittest.TestCase):
    def test_role_mapping_complete(self):
        evs = ci.convert(ci.DEFAULT_PATTERN)
        self.assertEqual({e.track_name for e in evs},
                         set(ci.TRACK_NAMES))
        self.assertEqual({e.role for e in evs},
                         {"sub", "glass", "choir", "dust"})
        for e in evs:
            self.assertEqual(e.seat, ci.SEATS[e.track_name]["seat"])

    def test_programs_per_seat(self):
        evs = ci.convert(ci.DEFAULT_PATTERN)
        prog = {}
        for e in evs:
            prog.setdefault(e.track_name, e.program)
        self.assertIsNone(prog["SUB HORIZON"])        # the house 808
        self.assertEqual(prog["GLASS ORBIT"], 39)     # glockenspiel
        self.assertEqual(prog["SIGNAL DUST"], 42)     # xylophone
        # Choir at 72 BPM: gated onto the Salamander (program 0).
        self.assertEqual(prog["PHANTOM CHOIR"], 0)

    def test_choir_gate_verdict_at_72_bpm(self):
        # A step at 72 BPM is 0.208 s: below the violins sustain
        # floor (0.842 s), above the Salamander floor (0.130 s).
        evs = [e for e in ci.convert(ci.DEFAULT_PATTERN)
               if e.track_name == "PHANTOM CHOIR"]
        self.assertTrue(evs)
        for e in evs:
            self.assertIsNotNone(e.gate)
            self.assertIn("Salamander seated", e.gate)
            self.assertIn("0.842", e.gate)

    def test_choir_gate_at_slowest_tempo_still_fails_strings(self):
        # Even at the page's slowest (40 BPM, step 0.375 s) no step
        # reaches the violins floor -- the gate is structural.
        p = copy.deepcopy(ci.DEFAULT_PATTERN)
        p["tempo"] = 40
        evs = [e for e in ci.convert(p)
               if e.track_name == "PHANTOM CHOIR"]
        for e in evs:
            self.assertEqual(e.program, 0)
            self.assertIn("Salamander seated", e.gate)


class TestABC(unittest.TestCase):
    def test_abc_round_trip_all_scales(self):
        for scale in ci.SCALES:
            p = copy.deepcopy(ci.DEFAULT_PATTERN)
            p["scale"] = scale
            evs = ci.convert(p)
            tunes = _split_tunes(ci.to_abc(evs, p))
            self.assertEqual(len(tunes), 4)
            for i, text in enumerate(tunes):
                tune = parse_abc(text)
                got = sorted((e.midi, e.start, e.dur)
                             for e in tune.events if e.kind == "note")
                want = sorted((e.midi, Fraction(e.step, 4),
                               Fraction(1, 4))
                              for e in evs if e.track_index == i)
                self.assertEqual(got, want, f"{scale} track {i}")
                # The grid is full: notes + rests span exactly 4 beats.
                total = sum(e.dur for e in tune.events)
                self.assertEqual(total, Fraction(4, 1))


class TestMIDI(unittest.TestCase):
    def test_midi_file_structure(self):
        evs = ci.convert(ci.DEFAULT_PATTERN)
        with tempfile.TemporaryDirectory() as d:
            path = ci.to_midi(evs, ci.DEFAULT_PATTERN,
                              Path(d) / "crystal.mid")
            data = path.read_bytes()
        self.assertEqual(data[:4], b"MThd")
        self.assertEqual(data.count(b"MTrk"), 5)   # tempo + 4 voices


if __name__ == "__main__":
    unittest.main()
