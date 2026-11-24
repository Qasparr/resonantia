#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — tests/test_studio_vocal_exam.py — the Vocal Exam
# judged analytically: the corpus validated against its own
# law, the judges proven on synthetic renders whose truth is
# planted before any code runs, the predictor checked against
# the sheet's arithmetic, and the duration judge made to
# reproduce the recorded Mugetsu history (90.38% / 99.52%)
# from the artifacts of record.
#
# 93.
# Date: 24 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""Tests for resonance/studio/vocal_exam.py, by proof."""

import json
import math
import unittest
from pathlib import Path

import numpy as np

from resonance.studio import vocal_exam as exam

ROOT = Path(__file__).resolve().parents[1]
SR = 44100


def synth_tone(hz, dur_s, sr=SR, amp=0.5):
    t = np.arange(int(dur_s * sr)) / sr
    return amp * np.sin(2 * np.pi * hz * t)


def synth_vowel(f0, f1, f2, dur_s=0.5, sr=SR):
    """A formant vowel with planted truth: harmonic source
    through two resonators at (f1, f2)."""
    n = int(dur_s * sr)
    t = np.arange(n) / sr
    src = np.zeros(n)
    for k in range(1, 40):
        src += (1.0 / k) * np.sin(2 * np.pi * f0 * k * t)

    def res(x, f, bw=80.0):
        rr = np.exp(-np.pi * bw / sr)
        th = 2 * np.pi * f / sr
        b0 = 1 - rr
        a1 = 2 * rr * np.cos(th)
        a2 = -rr * rr
        y = np.zeros_like(x)
        for i in range(2, len(x)):
            y[i] = b0 * x[i] + a1 * y[i - 1] + a2 * y[i - 2]
        return y

    y = res(res(src, f1), f2)
    return y / np.max(np.abs(y)) * 0.7


class CorpusIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = exam.load_corpus()
        cls.items = exam.corpus_items(cls.corpus)

    def test_version_stamped(self):
        self.assertIsInstance(self.corpus["version"], int)
        self.assertGreaterEqual(self.corpus["version"], 1)

    def test_held_out_split_exists(self):
        held = [i for i in self.corpus["items"] if i["held_out"]]
        self.assertGreaterEqual(len(held), 1)
        self.assertIn("phrase-ja-tsuki",
                      {i["id"] for i in held})

    def test_thirteen_items(self):
        self.assertEqual(len(self.corpus["items"]), 13)

    def test_hook_sheet_totals(self):
        hook = self.items["mugetsu-hook"]
        self.assertEqual(len(hook["lines"]), 8)
        total = sum(l["asked_dur_s"] for l in hook["lines"])
        self.assertAlmostEqual(total, 13.3333, places=3)
        # The calibration heads ride in the sheet: the seated
        # stations of the runs of record.
        stations = {ph["station"] for l in hook["lines"]
                    for ph in l["phonemes"] if ph["station"]}
        self.assertEqual(stations, {"Α", "Ε", "Ι", "Ο", "VV"})

    def test_every_sheet_entry_lawful(self):
        for item in self.corpus["items"]:
            for note in exam.item_notes(item):
                self.assertTrue(0 <= note["midi"] <= 127)
                self.assertGreater(note["dur_s"], 0)
                self.assertGreater(note["hz"], 0)

    def test_broken_corpus_refused_by_name(self):
        bad = {"version": 1, "items": [
            {"id": "x", "kind": "vowel", "held_out": False,
             "segments": [{"midi": 57, "dur_s": 1.0}]}]}
        path = Path(self.corpus_path_tmp(bad))
        with self.assertRaises(exam.ExamError):
            exam.load_corpus(path)

    @staticmethod
    def corpus_path_tmp(obj):
        import tempfile
        fh = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False)
        json.dump(obj, fh)
        fh.close()
        return fh.name


class DurationJudge(unittest.TestCase):
    def test_exact_realization(self):
        out = exam.judge_durations([1.0, 2.0], [1.0, 2.0])
        self.assertEqual(out["accuracy_pct"], 100.0)

    def test_known_ratio(self):
        out = exam.judge_durations([2.0, 2.0], [1.8, 1.8])
        self.assertAlmostEqual(out["accuracy_pct"], 90.0)

    def test_overshoot_not_clamped(self):
        out = exam.judge_durations([1.0], [1.031])
        self.assertAlmostEqual(out["accuracy_pct"], 103.1)

    def test_shape_mismatch_refused(self):
        with self.assertRaises(exam.ExamError):
            exam.judge_durations([1.0], [1.0, 2.0])

    def test_history_reproduced_from_artifacts(self):
        corpus = exam.load_corpus()
        for run, want in (("mugetsu-hook-engine-run1", 90.38),
                          ("mugetsu-hook-engine-run2", 99.52)):
            rec = exam.score_hook_run(
                ROOT / "studio-runs" / run, corpus, "test")
            got = rec["judges"]["durations"]["accuracy_pct"]
            self.assertAlmostEqual(got, want, delta=0.05,
                                   msg=f"{run}: {got} vs {want}")


class PitchJudge(unittest.TestCase):
    def test_true_tone_scores_zero(self):
        sig = synth_tone(exam.midi_hz(69), 0.5)
        out = exam.judge_pitch(sig, SR,
                               [{"midi": 69, "start_s": 0.0,
                                 "dur_s": 0.5}])
        self.assertEqual(out["n_measured"], 1)
        self.assertAlmostEqual(out["per_note"][0]["cents"], 0.0,
                               delta=6.0)

    def test_detune_read_by_the_planted_amount(self):
        hz = exam.midi_hz(69) * 2 ** (50.0 / 1200.0)
        sig = synth_tone(hz, 0.5)
        out = exam.judge_pitch(sig, SR,
                               [{"midi": 69, "start_s": 0.0,
                                 "dur_s": 0.5}])
        self.assertAlmostEqual(out["per_note"][0]["cents"], 50.0,
                               delta=8.0)

    def test_short_note_unmeasurable(self):
        sig = synth_tone(440.0, 0.05)
        out = exam.judge_pitch(sig, SR,
                               [{"midi": 69, "start_s": 0.0,
                                 "dur_s": 0.04}])
        self.assertEqual(out["n_unmeasurable"], 1)
        self.assertEqual(out["per_note"][0]["state"],
                         "UNMEASURABLE")

    def test_time_stretch_drops_duration_by_prediction(self):
        asked = [0.5, 0.5]
        realized = [0.45, 0.45]  # a 0.9x stretch of the take
        out = exam.judge_durations(asked, realized)
        self.assertAlmostEqual(out["accuracy_pct"], 90.0)


class OnsetJudge(unittest.TestCase):
    def test_onset_at_the_mark(self):
        sig = np.zeros(int(1.0 * SR))
        sig[int(0.5 * SR):] = synth_tone(440.0, 0.5, amp=0.4)
        out = exam.judge_onsets(sig, SR, [0.5])
        self.assertEqual(out["n_measured"], 1)
        self.assertLess(abs(out["per_onset"][0]["error_ms"]), 25.0)

    def test_no_gap_is_unmeasurable(self):
        sig = synth_tone(440.0, 1.0, amp=0.4)  # sound throughout
        out = exam.judge_onsets(sig, SR, [0.5])
        self.assertEqual(out["n_unmeasurable"], 1)


class VowelJudge(unittest.TestCase):
    def test_planted_vowels_match_their_stations(self):
        for station, (f1, f2) in {
                "Α": (730, 1090), "Ε": (512, 1950),
                "Ι": (270, 2290), "Ο": (570, 840),
                "Η": (610, 1720), "Υ": (235, 2100),
                "VV": (300, 700)}.items():
            out = exam.judge_vowel(synth_vowel(180, f1, f2),
                                   SR, station)
            self.assertTrue(out.get("match"),
                            f"{station}: {out}")
            self.assertLessEqual(out["distance_octaves"],
                                 exam.VOWEL_MATCH_OCTAVES)

    def test_wrong_target_does_not_match(self):
        out = exam.judge_vowel(synth_vowel(180, 730, 1090),
                               SR, "Ι")
        self.assertFalse(out["match"])
        self.assertEqual(out["nearest_station"], "Α")

    def test_omega_omicron_crowding_is_a_coordinate(self):
        # The canon's finest step: a planted Ω reads within
        # tolerance of Ω, its nearest neighbour standing in
        # {Ο, Ω} — the read's resolution limit, asserted as
        # such rather than smoothed.
        out = exam.judge_vowel(synth_vowel(180, 590, 880),
                               SR, "Ω")
        self.assertLessEqual(out["distance_octaves"],
                             exam.VOWEL_MATCH_OCTAVES)
        self.assertIn(out["nearest_station"], {"Ο", "Ω"})

    def test_silence_and_short_segments_unmeasurable(self):
        self.assertEqual(
            exam.judge_vowel(np.zeros(22050), SR, "Α")["state"],
            "UNMEASURABLE")
        short = synth_vowel(180, 730, 1090, dur_s=0.03)
        self.assertEqual(
            exam.judge_vowel(short, SR, "Α")["state"],
            "UNMEASURABLE")

    def test_glide_target_refused_as_steady(self):
        out = exam.judge_vowel(synth_vowel(180, 512, 1950),
                               SR, "ΕΙ")
        self.assertEqual(out["state"], "UNMEASURABLE")

    def test_soprano_slice_unmeasurable_by_name(self):
        seg = synth_tone(620.0, 0.1, amp=0.3)
        out = exam.judge_vowel(seg, SR, "Α")
        self.assertEqual(out["state"], "UNMEASURABLE")
        self.assertIn("soprano comb", out["reason"])


class Predictor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = exam.corpus_items(exam.load_corpus())

    def test_hook_expectation(self):
        pred = exam.predict(self.items["mugetsu-hook"], 1)
        self.assertAlmostEqual(pred["total_dur_s"], 13.3333,
                               places=3)
        self.assertEqual(len(pred["notes"]), 54)
        self.assertEqual(
            pred["expected_perfect"]["duration_accuracy_pct"],
            100.0)
        self.assertEqual(set(pred["vowel_targets"]),
                         {"Α", "Ε", "Ι", "Ο", "VV"})

    def test_vowel_item_expectation(self):
        pred = exam.predict(self.items["vowel-Α"], 1)
        self.assertEqual(pred["notes"][0]["hz"],
                         round(exam.midi_hz(57), 4))
        self.assertEqual(pred["vowel_targets"]["Α"],
                         {"f1_hz": 730, "f2_hz": 1090})


class MasterlawJudge(unittest.TestCase):
    def test_run2_master_compliant_on_its_own_gate(self):
        out = exam.judge_masterlaw(
            ROOT / "studio-runs" / "mugetsu-hook-engine-run2"
            / "master.mp3", sworn_bps=320000)
        self.assertTrue(out["compliant"])
        checks = {c["check"]: c for c in out["checks"]}
        self.assertAlmostEqual(
            checks["integrated loudness"]["value"], -14.0,
            delta=0.1)
        self.assertEqual(checks["bitrate (sworn)"]["value"],
                         320000)

    def test_missing_file_refused(self):
        with self.assertRaises(exam.ExamError):
            exam.judge_masterlaw(ROOT / "no-such-master.mp3")


if __name__ == "__main__":
    unittest.main()
