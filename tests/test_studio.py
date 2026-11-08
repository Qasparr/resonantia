# 93
# ---------------------------------------------------------------------
# test_studio.py -- the studio pipeline, weighed on its own scales.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: stdlib unittest, system python, NO rendering -- the
# MusicGen bridge is a wall these tests do not climb. What is weighed
# here is everything that must be true before a note is ever struck:
# the spec contract (bad specs refused, by name), the K-weighting
# scale (a sine whose loudness is computed by an independent formula
# path), the ceiling's supremacy (a hot, quiet-average signal whose
# loudness gain MUST be overridden by the true-peak law), and the
# agent contract (CLI --dry-run --json emits exactly one parseable
# JSON object). If any of these fail, the mill does not open.
# ---------------------------------------------------------------------

import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance.studio import pipeline  # noqa: E402

SR = 48000


def _biquad_gain_db(b, a, freq, sr):
    """|H| of a biquad at `freq`, by direct z-transform evaluation.

    The independent path: pipeline.measure_loudness_lufs reaches its
    number through FFTs and Parseval; this helper reaches the same
    truth through the transfer function alone. Agreement between two
    roads is what makes a scale a scale.
    """
    z = np.exp(2j * np.pi * freq / sr)
    num = b[0] + b[1] * z ** -1 + b[2] * z ** -2
    den = a[0] + a[1] * z ** -1 + a[2] * z ** -2
    return abs(num / den)


class SpecValidationTests(unittest.TestCase):
    def _minimal(self):
        return {"prompt_base": "a test tone poem",
                "sections": [{"seconds": 10}],
                "out_dir": "/tmp/never-built"}

    def test_minimal_spec_normalizes_with_defaults(self):
        spec = pipeline.validate_spec(self._minimal())
        self.assertEqual(spec["seed"], 93)
        self.assertEqual(spec["sigma"]["left_hz"], 200.0)
        self.assertEqual(spec["sigma"]["right_hz"], 213.0)
        self.assertEqual(spec["master"]["target_lufs"], -14.0)
        self.assertEqual(spec["sections"][0]["name"], "section1")

    def test_missing_prompt_base_refused(self):
        spec = self._minimal()
        del spec["prompt_base"]
        with self.assertRaises(ValueError) as ctx:
            pipeline.validate_spec(spec)
        self.assertIn("prompt_base", str(ctx.exception))

    def test_empty_sections_refused(self):
        spec = self._minimal()
        spec["sections"] = []
        with self.assertRaises(ValueError):
            pipeline.validate_spec(spec)

    def test_oversize_section_refused(self):
        spec = self._minimal()
        spec["sections"] = [{"seconds": 45}]
        with self.assertRaises(ValueError) as ctx:
            pipeline.validate_spec(spec)
        self.assertIn("seconds", str(ctx.exception))

    def test_descending_sigma_refused(self):
        spec = self._minimal()
        spec["sigma"] = {"left_hz": 213.0, "right_hz": 200.0}
        with self.assertRaises(ValueError) as ctx:
            pipeline.validate_spec(spec)
        self.assertIn("sigma", str(ctx.exception))

    def test_missing_out_dir_refused(self):
        spec = self._minimal()
        del spec["out_dir"]
        with self.assertRaises(ValueError):
            pipeline.validate_spec(spec)


class LoudnessScaleTests(unittest.TestCase):
    def test_sine_loudness_matches_independent_formula(self):
        freq, amp, seconds = 1000.0, 0.5, 2.0
        n = int(SR * seconds)  # exactly 2000 cycles: no leakage games
        t = np.arange(n) / SR
        sine = amp * np.sin(2 * np.pi * freq * t)
        stereo = np.stack([sine, sine])
        measured = pipeline.measure_loudness_lufs(stereo, SR)
        # Independent expectation: per-channel filtered mean square is
        # (A^2 / 2) * |H_pre * H_rlb|^2 at the sine's frequency; two
        # channels sum; the -0.691 is BS.1770's calibration offset.
        gain = (_biquad_gain_db(pipeline._K_PRE_B, pipeline._K_PRE_A,
                                freq, SR)
                * _biquad_gain_db(pipeline._K_RLB_B, pipeline._K_RLB_A,
                                  freq, SR))
        expected = -0.691 + 10 * math.log10(2 * (amp ** 2 / 2) * gain ** 2)
        self.assertAlmostEqual(measured, expected, delta=0.35)


class CeilingLawTests(unittest.TestCase):
    def test_ceiling_overrides_loudness_on_a_hot_quiet_signal(self):
        # A 100 ms full-scale burst in 2 s of near-silence: the
        # integrated loudness is low, so the loudness gain alone would
        # drive the burst far past the ceiling. The ceiling must win.
        n = 2 * SR
        x = np.zeros((2, n))
        burst = slice(SR // 2, SR // 2 + SR // 10)
        t = np.arange(SR // 10) / SR
        x[:, burst] = np.sin(2 * np.pi * 440.0 * t)
        mastered, report = pipeline.master_signal(
            x, SR, target_lufs=-8.0, ceiling_dbtp=-1.0)
        self.assertTrue(report["ceiling_overrode_loudness"])
        self.assertLessEqual(report["true_peak_dbtp"], -1.0 + 0.15)
        self.assertLessEqual(report["sample_peak_db"], -1.0 + 0.15)
        # And the mastered signal must still be the burst, not silence:
        self.assertGreater(float(np.max(np.abs(mastered))), 0.5)


class ResumeLawTests(unittest.TestCase):
    """_segment_file_ok: a survivor segment must be whole or nothing."""

    def _write_wav(self, path, seconds, sr=32000):
        import wave
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(b"\x00\x00" * int(sr * seconds))

    def test_whole_segment_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "seg00.wav"
            self._write_wav(p, 30)
            self.assertTrue(pipeline._segment_file_ok(p, 30))

    def test_truncated_segment_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "seg00.wav"
            self._write_wav(p, 12)  # died mid-write: 12s of a 30s brief
            self.assertFalse(pipeline._segment_file_ok(p, 30))

    def test_wrong_rate_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "seg00.wav"
            self._write_wav(p, 30, sr=44100)
            self.assertFalse(pipeline._segment_file_ok(p, 30))

    def test_garbage_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "seg00.wav"
            p.write_bytes(b"not a wav at all")
            self.assertFalse(pipeline._segment_file_ok(p, 30))


class DryRunContractTests(unittest.TestCase):
    def test_cli_dry_run_json_is_one_parseable_object(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, "-m", "resonance.studio", "produce",
                 "--prompt", "a dry wind over detroit", "--seconds", "45",
                 "--seed", "93", "--title", "DRY", "--out-dir", tmp,
                 "--dry-run", "--json"],
                cwd=repo, capture_output=True, text=True, timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        manifest = json.loads(proc.stdout)  # exactly one object, or this fails
        self.assertTrue(manifest["dry_run"])
        self.assertEqual(manifest["title"], "DRY")
        sections = manifest["planned"]["sections"]
        self.assertEqual(len(sections), 2)          # 45s -> 30 + 15
        self.assertEqual(sections[0]["seed"], 93)
        self.assertEqual(sections[1]["seed"], 94)
        self.assertEqual(
            manifest["planned"]["program_seconds_after_crossfades"], 43.0)

    def test_cli_bad_spec_json_errors_cleanly(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps({"sections": [{"seconds": 10}],
                                       "out_dir": tmp}))
            proc = subprocess.run(
                [sys.executable, "-m", "resonance.studio", "produce",
                 "--spec", str(bad), "--json"],
                cwd=repo, capture_output=True, text=True, timeout=120)
        self.assertNotEqual(proc.returncode, 0)
        err = json.loads(proc.stdout)
        self.assertIn("prompt_base", err["error"])


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
