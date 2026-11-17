# 93
# ---------------------------------------------------------------------
# test_studio_diffsinger.py -- the DiffSinger plug, weighed pure.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: what is weighed here is the plug's pure law, with no
# neural network in the room: the Divine Nine's seating table
# (the founder's VV stamp and the vowels-only consonant ruling
# made mechanical), the grouping law that puts morae under notes,
# the sequence builder's arithmetic (word budgets, divisions,
# pitches), the .ds serialization's shape, the score reader's
# parsing of a synthetic MIDI, and the WAV measurement's math
# against a known sine. The bridge and the render are weighed by
# the run record, not here -- a unit test that needs a voicebank
# is not a unit test.
# ---------------------------------------------------------------------

import json
import math
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance.studio import diffsinger as ds  # noqa: E402

FPS = ds.FPS


def _fake_bank(tmp):
    """A two-language toy bank: just the JSON tables build_line
    reads, with ids small enough to check by hand."""
    bank = Path(tmp)
    ph = {"SP": 0, "AP": 1,
          "ja/a": 2, "ja/i": 3, "ja/u": 4, "ja/e": 5, "ja/o": 6,
          "ja/k": 7, "ja/N": 8,
          "en/aa": 9, "en/s": 10, "en/ih": 11}
    langs = {"ja": 2, "en": 1}
    (bank / "phonemes.json").write_text(json.dumps(ph))
    (bank / "languages.json").write_text(json.dumps(langs))
    return ph, langs


class TestNineSeating(unittest.TestCase):
    """The canon at the plug point: seats, offsets, and the pass."""

    def test_ja_four_exact_seats(self):
        for name, station in (("a", "Α"), ("i", "Ι"),
                              ("e", "Ε"), ("o", "Ο")):
            e = ds.seat_vowel("ja", name)
            self.assertEqual(e["station"], station)
            self.assertEqual(e["disposition"], ds.SEATED)

    def test_ja_u_seats_under_vv_by_the_founders_stamp(self):
        e = ds.seat_vowel("ja", "u")
        self.assertEqual(e["station"], "VV")
        self.assertEqual(e["disposition"], ds.SEATED)
        self.assertIn("unrounding", e["note"])

    def test_ja_long_vowels_hold_the_same_seats(self):
        for name, station in (("A", "Α"), ("I", "Ι"), ("U", "VV"),
                              ("E", "Ε"), ("O", "Ο")):
            e = ds.seat_vowel("ja", name)
            self.assertEqual(e["station"], station)
            self.assertEqual(e["disposition"], ds.SEATED)

    def test_en_seated_family(self):
        for name, station in (("aa", "Α"), ("iy", "Ι"),
                              ("eh", "Η"), ("ao", "Ω"),
                              ("uw", "VV")):
            e = ds.seat_vowel("en", name)
            self.assertEqual(e["station"], station)
            self.assertEqual(e["disposition"], ds.SEATED)

    def test_en_uh_is_vvs_nearest_offset(self):
        e = ds.seat_vowel("en", "uh")
        self.assertEqual(e["station"], "VV")
        self.assertEqual(e["disposition"], ds.NEAREST_OFFSET)

    def test_en_glides_are_half_seated_at_the_onset(self):
        for name, station in (("ey", "Ε"), ("ow", "Ο"),
                              ("ay", "Α"), ("aw", "Α"),
                              ("oy", "Ω")):
            e = ds.seat_vowel("en", name)
            self.assertEqual(e["station"], station)
            self.assertEqual(e["disposition"],
                             ds.HALF_SEATED_ONSET)

    def test_en_unseated_carry_coordinates_not_seats(self):
        for name in ("ih", "ae", "ah", "ax", "er"):
            e = ds.seat_vowel("en", name)
            self.assertIsNone(e["station"])
            self.assertEqual(e["disposition"], ds.UNSEATED)
            self.assertTrue(e["note"])  # coordinates, reported

    def test_consonants_pass_native_under_vowels_only(self):
        for lang, name in (("ja", "k"), ("ja", "N"),
                           ("ja", "sh"), ("en", "s"), ("en", "dh")):
            e = ds.seat_vowel(lang, name)
            self.assertIsNone(e["station"])
            self.assertEqual(e["disposition"], ds.PASS_NATIVE)

    def test_rests_are_rests(self):
        for name in ("SP", "AP"):
            self.assertEqual(ds.seat_vowel("ja", name)
                             ["disposition"], ds.REST)

    def test_vv_carries_no_isopsephy_weight(self):
        # The propriety audit's fence, made mechanical: VV is not
        # counted in the 1,779 and holds no Greek weight here.
        self.assertIsNone(ds.STATIONS["VV"]["weight"])
        greek = sum(s["weight"] for s in ds.STATIONS.values()
                    if s["weight"])
        self.assertEqual(greek, 1779)

    def test_ledger_totals_count_twice_weighed(self):
        led = [ds.seat_line("ja", ["k", "a", "N", "u"]),
               ds.seat_line("en", ["s", "ih", "uw"])]
        t = ds.ledger_totals(led)
        self.assertEqual(t["stations"], {"Α": 1, "VV": 2})
        self.assertEqual(t["dispositions"][ds.PASS_NATIVE], 3)
        self.assertEqual(t["dispositions"][ds.UNSEATED], 1)
        self.assertEqual(t["dispositions"][ds.SEATED], 3)


class TestGroupingLaw(unittest.TestCase):
    """Morae under notes: every mora sung, no note unsung."""

    def test_totals_preserved_and_floor_held(self):
        counts = ds.group_morae([0.2] * 6 + [0.4], 18)
        self.assertEqual(sum(counts), 18)
        self.assertTrue(all(c >= 1 for c in counts))
        self.assertEqual(len(counts), 7)

    def test_longer_notes_carry_more(self):
        counts = ds.group_morae([0.2, 0.4], 6)
        self.assertGreater(counts[1], counts[0])
        self.assertEqual(sum(counts), 6)

    def test_equal_notes_split_evenly(self):
        self.assertEqual(ds.group_morae([0.5, 0.5], 4), [2, 2])

    def test_refuses_when_a_note_would_go_unsung(self):
        with self.assertRaises(ValueError):
            ds.group_morae([0.2, 0.2, 0.2], 2)


class TestSequenceBuilding(unittest.TestCase):
    """The builder's arithmetic, against a toy bank."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ph, self.langs = _fake_bank(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _line(self, **over):
        line = {"id": "t1", "lang": "ja", "speaker": "Civet",
                "text": "kakaN",
                "morae": [["k", "a"], ["k", "a"], ["N"]],
                "notes": [{"midi": 68, "dur": 0.5},
                          {"midi": 71, "dur": 0.5}],
                "offset": 0.0}
        line.update(over)
        return line

    def test_tokens_divisions_and_pitches(self):
        b = ds.build_line(self._line(), self.ph, self.langs)
        # grouping: 3 morae over 2 equal notes -> [2, 1]
        self.assertEqual([n["morae"] for n in b["notes"]], [2, 1])
        self.assertEqual(b["word_div"], [2, 2, 1])
        self.assertEqual(b["tokens"],
                         [self.ph["ja/k"], self.ph["ja/a"],
                          self.ph["ja/k"], self.ph["ja/a"],
                          self.ph["ja/N"]])
        self.assertEqual(b["languages"], [2] * 5)
        self.assertEqual(b["ph_midi"], [68, 68, 68, 68, 71])
        # budgets: note 1 splits 0.5s over 2 morae, note 2 gives
        # its whole 0.5s to one mora -- whole frames, +-1 frame.
        self.assertAlmostEqual(b["word_dur"][0], round(0.25 * FPS))
        self.assertAlmostEqual(b["word_dur"][2], round(0.5 * FPS))
        self.assertAlmostEqual(b["asked_s"], 1.0)

    def test_rest_mora_carries_no_pitch(self):
        line = self._line(morae=[["SP"], ["k", "a"]],
                          notes=[{"midi": 68, "dur": 0.5},
                                 {"midi": 68, "dur": 0.5}])
        b = ds.build_line(line, self.ph, self.langs)
        self.assertEqual(b["tokens"][0], self.ph["SP"])
        self.assertEqual(b["ph_midi"][0], 0)
        self.assertEqual(b["ledger"][0]["disposition"], ds.REST)

    def test_unknown_phoneme_is_refused_by_name(self):
        line = self._line(morae=[["k", "a"], ["zz"], ["N"]])
        with self.assertRaises(ValueError) as cm:
            ds.build_line(line, self.ph, self.langs)
        self.assertIn("ja/zz", str(cm.exception))

    def test_unknown_language_is_refused_by_name(self):
        with self.assertRaises(ValueError):
            ds.build_line(self._line(lang="fr"),
                          self.ph, self.langs)


class TestDsSerialization(unittest.TestCase):
    """The .ds shape: segments the DiffSinger road recognizes."""

    def test_segment_shape_and_ph_num(self):
        with tempfile.TemporaryDirectory() as tmp:
            ph, langs = _fake_bank(tmp)
            line = {"id": "t1", "lang": "ja", "speaker": "Civet",
                    "text": "ka", "morae": [["k", "a"]],
                    "notes": [{"midi": 68, "dur": 0.5}],
                    "offset": 1.5}
            b = ds.build_line(line, ph, langs)
            segs = ds.write_ds([b], Path(tmp) / "s.ds")
            seg = segs[0]
            self.assertEqual(seg["offset"], 1.5)
            self.assertEqual(seg["text"], "ka")
            self.assertEqual(seg["ph_seq"], "ja/k ja/a")
            self.assertEqual(seg["note_seq"], "G#4")
            self.assertEqual(seg["ph_num"], "2")
            self.assertEqual(seg["note_slur"], "0")
            ph_dur = [float(x) for x in seg["ph_dur"].split()]
            self.assertEqual(len(ph_dur), 2)
            # whole-frame budgets: the sum holds the note's 0.5 s
            # to within one frame -- the module's stated tolerance.
            self.assertAlmostEqual(sum(ph_dur), 0.5, delta=1 / FPS)
            # the file on disk is the same JSON, utf-8 clean
            back = json.loads((Path(tmp) / "s.ds").read_text(
                encoding="utf-8"))
            self.assertEqual(back[0]["ph_seq"], "ja/k ja/a")

    def test_note_names(self):
        self.assertEqual(ds.note_name(60), "C4")
        self.assertEqual(ds.note_name(68), "G#4")
        self.assertEqual(ds.note_name(75), "D#5")
        self.assertEqual(ds.note_name(80), "G#5")


def _smf_bytes():
    """A minimal format-1 SMF: one named track, two notes, a tempo."""
    def vlq(v):
        out = [v & 0x7F]
        v >>= 7
        while v:
            out.append(0x80 | (v & 0x7F))
            v >>= 7
        return bytes(reversed(out))

    ev = b""
    ev += b"\x00\xff\x51\x03\x06\x1a\x80"          # tempo 400000 us
    name = b"V:1 Hook melody (YAMI)"
    ev += b"\x00\xff\x03" + vlq(len(name)) + name
    ev += b"\x00\x90\x44\x64"                     # on  68 @0
    ev += b"\x81\x70\x80\x44\x40"                 # off 68 @240
    ev += b"\x00\x90\x47\x64"                     # on  71 @240
    ev += b"\x83\x60\x80\x47\x40"                 # off 71 @480
    ev += b"\x00\xff\x2f\x00"
    trk = b"MTrk" + struct.pack(">I", len(ev)) + ev
    hdr = b"MThd" + struct.pack(">IHHH", 6, 1, 1, 480)
    return hdr + trk


class TestScoreReader(unittest.TestCase):
    """MIDI is the score: the reader takes notes, never sound."""

    def test_parse_notes_tempo_and_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "t.mid"
            p.write_bytes(_smf_bytes())
            got = ds.melody_from_midi(p, "Hook melody")
            self.assertEqual(got["track"], "V:1 Hook melody (YAMI)")
            self.assertAlmostEqual(got["bpm"], 150.0)
            self.assertEqual([n["midi"] for n in got["notes"]],
                             [68, 71])
            # 240 ticks at 480 tpq = half a quarter = 0.2 s at the
            # file's 400000 us tempo.
            self.assertAlmostEqual(got["notes"][0]["dur"], 0.2)
            self.assertAlmostEqual(got["notes"][1]["start"], 0.2)

    def test_missing_track_is_refused_by_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "t.mid"
            p.write_bytes(_smf_bytes())
            with self.assertRaises(ValueError):
                ds.melody_from_midi(p, "Piano riff")


class TestMeasurement(unittest.TestCase):
    """The manifest's math, against a sine whose truth is known."""

    def test_measure_known_sine(self):
        sr = 44100
        t = np.arange(sr // 2) / sr
        a = (0.5 * np.sin(2 * np.pi * 220 * t) * 32767
             ).astype("<i2")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "s.wav"
            with wave.open(str(p), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(a.tobytes())
            m = ds.measure_wav(p)
            self.assertEqual(m["sample_rate"], sr)
            self.assertAlmostEqual(m["duration_s"], 0.5, places=3)
            self.assertAlmostEqual(m["peak"], 0.5, delta=0.01)
            self.assertAlmostEqual(m["peak_dbfs"],
                                   20 * math.log10(0.5), delta=0.1)
            self.assertAlmostEqual(m["rms"], 0.5 / math.sqrt(2),
                                   delta=0.01)


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
