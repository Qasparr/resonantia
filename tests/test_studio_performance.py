# 93
# ---------------------------------------------------------------------
# test_studio_performance.py -- Proof No. 4's road, under test.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VIII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: the performance mode's contract, pinned: the validator
# synthesizes takes from ONE invariant prompt and refuses every
# impurity the founder's ruling names (a spine, per-section
# prompts); the tempo estimator reads synthetic click trains at
# their struck tempi; the join weigher finds a planted jump; the
# dancer's schedule keeps the arc and sums to the performance's
# own bars; the dry run plans without rendering. No test here
# touches the MusicGen bridge -- the render itself is weighed by
# the run's manifest, as the house weighs every claim.
# ---------------------------------------------------------------------

import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

from resonance.studio import performance as perf
from resonance.studio import pipeline


def _perf_spec(**over):
    spec = {
        "title": "SINGLE PASS",
        "prompt_base": "detroit bounce, f minor, one performance",
        "performance": {"takes": 7, "take_seconds": 30,
                        "continue_seconds": 5.0},
        "out_dir": "studio-runs/test-performance",
    }
    spec.update(over)
    return spec


class TestValidatePerformance(unittest.TestCase):
    def test_normalizes_and_synthesizes_takes(self):
        out = pipeline.validate_spec(_perf_spec())
        self.assertEqual(out["performance"]["takes"], 7)
        self.assertEqual(len(out["sections"]), 7)
        self.assertTrue(all(
            s["prompt_suffix"] == "" for s in out["sections"]))
        self.assertTrue(all(
            s["seconds"] == 30.0 for s in out["sections"]))
        # One invariant prompt: every take speaks the same words.
        prompts = {pipeline._full_prompt(out, s)
                   for s in out["sections"]}
        self.assertEqual(len(prompts), 1)

    def test_sections_not_required(self):
        out = pipeline.validate_spec(_perf_spec())
        self.assertNotIn("spine", out)

    def test_spine_refused(self):
        spec = _perf_spec(spine={
            "bpm": 120, "sections": [
                {"name": "a", "bars": 4, "density": "full"}]})
        with self.assertRaises(ValueError) as cm:
            pipeline.validate_spec(spec)
        self.assertIn("performance", str(cm.exception))

    def test_section_suffix_refused(self):
        spec = _perf_spec(sections=[
            {"name": "x", "prompt_suffix": "add strings",
             "seconds": 30}])
        with self.assertRaises(ValueError) as cm:
            pipeline.validate_spec(spec)
        self.assertIn("invariant", str(cm.exception))

    def test_takes_range_refused(self):
        spec = _perf_spec()
        spec["performance"] = {"takes": 1}
        with self.assertRaises(ValueError) as cm:
            pipeline.validate_spec(spec)
        self.assertIn("performance.takes", str(cm.exception))

    def test_take_seconds_range_refused(self):
        spec = _perf_spec()
        spec["performance"] = {"take_seconds": 45}
        with self.assertRaises(ValueError) as cm:
            pipeline.validate_spec(spec)
        self.assertIn("performance.take_seconds", str(cm.exception))

    def test_arpeggio_allowed_with_performance(self):
        out = pipeline.validate_spec(_perf_spec(arpeggio={}))
        self.assertIn("arpeggio", out)
        # ...and the Stereo Law defaults on, as on a spine run.
        self.assertEqual(out["stereo"]["width"], 1.0)

    def test_arpeggio_still_refused_alone(self):
        spec = {
            "title": "x", "prompt_base": "y",
            "sections": [{"name": "a", "seconds": 10}],
            "arpeggio": {}, "out_dir": "studio-runs/test-x",
        }
        with self.assertRaises(ValueError):
            pipeline.validate_spec(spec)


def _click_train(bpm, seconds=24.0, sr=48000):
    """A struck clock: decaying low pings on the beats, accented 4s."""
    x = np.zeros(int(seconds * sr))
    beat = 60.0 / bpm
    t = np.arange(int(0.09 * sr)) / sr
    ping = np.sin(2 * np.pi * 110.0 * t) * np.exp(-t * 45.0)
    n_beats = int(seconds / beat)
    for b in range(n_beats):
        at = int(b * beat * sr)
        amp = 1.0 if b % 4 == 0 else 0.7
        x[at:at + ping.shape[0]] += amp * ping
    return x


class TestTempoEstimator(unittest.TestCase):
    def _estimate(self, bpm):
        x = _click_train(bpm)
        env, rate = perf.onset_envelope(x, 48000)
        return perf.tempo_from_envelope(env, rate)

    def test_reads_120(self):
        t = self._estimate(120.0)
        self.assertIsNotNone(t)
        self.assertAlmostEqual(t["bpm"], 120.0, delta=4.0)

    def test_reads_70(self):
        t = self._estimate(70.0)
        self.assertIsNotNone(t)
        self.assertAlmostEqual(t["bpm"], 70.0, delta=3.0)

    def test_silence_reads_nothing(self):
        env, rate = perf.onset_envelope(np.zeros(48000 * 12), 48000)
        self.assertIsNone(perf.tempo_from_envelope(env, rate))

    def test_windows_hold_the_tempo(self):
        x = _click_train(96.0, seconds=64.0)
        env, rate = perf.onset_envelope(x, 48000)
        wins = perf.window_tempos(env, rate, 64.0)
        bpms = [w["bpm"] for w in wins if w["bpm"] is not None]
        self.assertGreaterEqual(len(bpms), 2)
        for b in bpms:
            self.assertAlmostEqual(b, 96.0, delta=5.0)


class TestMeasureJoins(unittest.TestCase):
    def test_planted_jump_found(self):
        sr = 32000
        rng = np.random.default_rng(7)
        a = 0.001 * rng.standard_normal(sr)
        b = 0.001 * rng.standard_normal(sr)
        b[0] += 0.5  # the planted discontinuity
        x = np.concatenate([a, b])
        joins, summary = perf.measure_joins(x, sr, [sr])
        self.assertEqual(len(joins), 1)
        self.assertGreater(joins[0]["waveform_jump"], 0.4)
        self.assertGreater(joins[0]["jump_vs_median_internal"], 50)
        self.assertEqual(summary["count"], 1)

    def test_clean_splice_reads_small(self):
        sr = 32000
        t = np.arange(2 * sr) / sr
        x = 0.2 * np.sin(2 * np.pi * 100.0 * t)
        joins, _ = perf.measure_joins(x, sr, [sr])
        # A continuous sine crosses its own splice like any sample.
        self.assertLess(joins[0]["waveform_jump"], 0.01)


class TestSchedule(unittest.TestCase):
    def test_bars_sum_and_modes(self):
        sched = perf.build_arp_schedule(210.0, 70.0)
        total = sum(s["bars"] for s in sched["sections"])
        sec_per_bar = 4 * 60.0 / 70.0
        self.assertEqual(total, int(210.0 // sec_per_bar))
        from resonance.studio import arpeggio
        _, modes = arpeggio.compose_events(
            sched["sections"], {})
        self.assertIn("bariolage16", modes)      # the verse3 chair
        self.assertIn("statement_fade", modes)   # the outro
        self.assertIn("runs", modes)             # the lifts
        self.assertEqual(sched["swing"], 0.0)

    def test_unmeasured_tempo_refused(self):
        with self.assertRaises(ValueError):
            perf.build_arp_schedule(210.0, None)


class TestDryRun(unittest.TestCase):
    def test_dry_run_plans_the_performance(self):
        with tempfile.TemporaryDirectory() as td:
            spec = _perf_spec(out_dir=str(Path(td) / "run"),
                              arpeggio={})
            manifest = pipeline.produce(spec, dry_run=True)
            self.assertTrue(manifest["dry_run"])
            plan = manifest["planned"]["performance"]
            self.assertEqual(plan["takes"], 7)
            self.assertEqual(plan["planned_program_seconds"], 210.0)
            self.assertEqual(plan["joins"], 6)
            self.assertFalse((Path(td) / "run" / "master.wav")
                             .exists())


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
