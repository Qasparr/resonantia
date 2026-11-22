# 93
# ---------------------------------------------------------------------
# test_studio_pipeline_cutins.py -- the two cut-ins of 2026-11-22,
# weighed: the EQVILLIBBRRIVMM bus on the section road's stems,
# and the Mastering Rule's seal on the sheets stage.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XXII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: a bridge of paper stands where pipeline._run_bridge
# stands (the pattern of test_studio_performance.py): tiny honest
# takes at MusicGen's native 32 kHz, and a finalize that strikes
# 16-bit WAVs from the float masters. The section road's takes are
# TWO-TONE probes -- 200 Hz and 6,000 Hz at equal amplitude -- so
# the bus's measured direction (lowpass lean, probed in
# test_studio_eqvillibbrrivmm.py before any of this was sworn) can
# be weighed on the struck master itself: with the pole ordered,
# the high band's share of the program must FALL against the same
# spec rendered without the key, while loudness is re-gained by
# the mastering law in both. Back-compat is weighed the same way
# the house weighs everything: the absent-key spec renders twice
# and must strike the identical master, byte for byte, with no eq
# block in its manifest and no eq key in its normalized spec.
# The Mastering Rule is weighed at the sheets stage, where it
# lives: both locks closed, the sheet is struck; either lock
# open, the run refuses and the refusal NAMES the lock; no rule
# declared, the road is the road as it always was.
# ---------------------------------------------------------------------

import tempfile
import unittest
import wave
from pathlib import Path
from unittest import mock

import numpy as np

from resonance.studio import pipeline

SR = 48000
G9 = 1254.3854  # the Full Key pole the bus was probed at


def _write_probe_take(path, seconds=3.0, sr=32000):
    """A two-tone take: 200 Hz and 6 kHz, equal amplitude, mono."""
    n = int(seconds * sr)
    t = np.arange(n) / sr
    data = 0.30 * np.sin(2 * np.pi * 200.0 * t) \
        + 0.30 * np.sin(2 * np.pi * 6000.0 * t)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((data * 32767).astype(np.int16).tobytes())


def _write_noise_take(path, seconds=3.0, sr=32000, seed=1):
    rng = np.random.default_rng(seed)
    data = 0.05 * rng.standard_normal(int(seconds * sr))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((data * 32767).astype(np.int16).tobytes())


def _fake_bridge(take_writer):
    """A bridge of paper: segments and finalize, honestly reported."""
    def fake(job, out_dir, log):
        if "finalize" in job:
            written = []
            for item in job["finalize"]:
                arr = np.load(item["npy"])
                pcm = np.clip(arr, -1.0, 1.0)
                pcm = (pcm * 32767).astype(np.int16)
                with wave.open(item["out"], "wb") as w:
                    w.setnchannels(pcm.shape[1])
                    w.setsampwidth(2)
                    w.setframerate(int(item.get(
                        "sample_rate", 48000)))
                    w.writeframes(pcm.tobytes())
                written.append({"out": item["out"], "bytes": 0})
            return {"ok": True, "kind": "finalize",
                    "written": written}
        segs = []
        for seg in job["segments"]:
            path = Path(out_dir) / seg["file"]
            take_writer(path, seconds=seg["seconds"])
            segs.append({
                "index": seg["index"], "file": seg["file"],
                "sample_rate": 32000,
                "frames": int(seg["seconds"] * 32000),
                "wall_seconds": 0.0,
                "continued_from": (seg["index"] - 1
                                   if seg["index"] > 0 else None),
                "continue_seconds":
                    seg.get("continue_seconds", 0.0)
                    if seg["index"] > 0 else 0.0})
        return {"ok": True, "kind": "segments", "model": "fake",
                "segments": segs, "wall_seconds": 0.0}
    return fake


def _section_spec(out_dir, **over):
    spec = {"title": "CUT-IN PROBE",
            "prompt_base": "two-tone probe, low and high",
            "sections": [{"name": "a", "seconds": 3},
                         {"name": "b", "seconds": 3}],
            "seed": 4242,
            "proof": {"emit": False},
            "out_dir": str(out_dir)}
    spec.update(over)
    return spec


def _perf_spec(out_dir, **over):
    spec = {"title": "RULE PROBE",
            "prompt_base": "detroit bounce, f minor, one "
                           "performance",
            "performance": {"takes": 2, "take_seconds": 3,
                            "continue_seconds": 2.0},
            "seed": 777,
            "out_dir": str(out_dir)}
    spec.update(over)
    return spec


def _band_ratio(master_wav):
    """HF/LF energy ratio of a struck master: [5.5k,6.5k]/[150,250]."""
    arr, sr = pipeline.read_wav_pcm(master_wav)
    x = np.asarray(arr, dtype=np.float64)
    if x.ndim == 1:
        x = x[np.newaxis, :]
    n = x.shape[1]
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    lf = (freqs >= 150.0) & (freqs <= 250.0)
    hf = (freqs >= 5500.0) & (freqs <= 6500.0)
    e_lf = e_hf = 0.0
    for ch in x:
        mag2 = np.abs(np.fft.rfft(ch)) ** 2
        e_lf += float(np.sum(mag2[lf]))
        e_hf += float(np.sum(mag2[hf]))
    return e_hf / e_lf if e_lf > 0 else float("inf")


class EqValidationTests(unittest.TestCase):
    def test_pole_normalizes(self):
        out = pipeline.validate_spec(
            _section_spec("/tmp/never-built", eq_pole_hz=G9))
        self.assertEqual(out["eq_pole_hz"], G9)

    def test_absent_pole_strikes_the_key(self):
        out = pipeline.validate_spec(_section_spec("/tmp/never"))
        self.assertNotIn("eq_pole_hz", out)

    def test_bad_poles_refused_by_name(self):
        for bad in (10.0, 20001.0, "high", True):
            with self.assertRaises(ValueError) as ctx:
                pipeline.validate_spec(
                    _section_spec("/tmp/never", eq_pole_hz=bad))
            self.assertIn("eq_pole_hz", str(ctx.exception))

    def test_pole_refused_on_the_performance_road(self):
        with self.assertRaises(ValueError) as ctx:
            pipeline.validate_spec(
                _perf_spec("/tmp/never", eq_pole_hz=G9))
        self.assertIn("eq_pole_hz", str(ctx.exception))


class EqRenderTests(unittest.TestCase):
    def _render(self, td, name, **over):
        out = Path(td) / name
        spec = _section_spec(out, **over)
        with mock.patch.object(pipeline, "_run_bridge",
                               _fake_bridge(_write_probe_take)):
            manifest = pipeline.produce(spec, log=lambda m: None)
        return out, manifest

    def test_absent_key_render_is_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            out1, man1 = self._render(td, "plain1")
            out2, man2 = self._render(td, "plain2")
            # Deterministic and identical: the road as it was.
            self.assertEqual((out1 / "master.wav").read_bytes(),
                             (out2 / "master.wav").read_bytes())
            self.assertNotIn("eq", man1)
            self.assertNotIn("eq_pole_hz", man1["spec"])
            dry = pipeline.produce(
                _section_spec(Path(td) / "dry"), dry_run=True,
                log=lambda m: None)
            self.assertNotIn("eq", dry["planned"])

    def test_present_key_eq_applied_and_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            plain_out, _ = self._render(td, "plain")
            eq_out, man = self._render(td, "eq", eq_pole_hz=G9)
            block = man["eq"]
            self.assertEqual(block["pole_hz"], G9)
            self.assertGreaterEqual(block["transfer_magnitude"],
                                    0.05)
            self.assertLessEqual(block["transfer_magnitude"], 3.0)
            self.assertEqual(len(block["stems"]), 2)
            for stem in block["stems"]:
                self.assertEqual(
                    len(stem["transfer_magnitude_per_channel"]), 2)
            # The audio moved, and in the measured direction: the
            # bus leans lowpass, so the high band's share falls.
            self.assertNotEqual(
                (plain_out / "master.wav").read_bytes(),
                (eq_out / "master.wav").read_bytes())
            ratio_plain = _band_ratio(plain_out / "master.wav")
            ratio_eq = _band_ratio(eq_out / "master.wav")
            self.assertLess(ratio_eq, 0.5 * ratio_plain)


class MasteringRuleValidationTests(unittest.TestCase):
    def test_rule_and_locks_normalize(self):
        out = pipeline.validate_spec(_perf_spec(
            "/tmp/never", mastering_rule="krs-blueprint",
            locks={"instrumental": True, "lyrics": True}))
        self.assertEqual(out["mastering_rule"], "krs-blueprint")
        self.assertEqual(out["locks"],
                         {"instrumental": True, "lyrics": True})

    def test_no_rule_strikes_both_keys(self):
        out = pipeline.validate_spec(_perf_spec("/tmp/never"))
        self.assertNotIn("mastering_rule", out)
        self.assertNotIn("locks", out)

    def test_unknown_rule_refused_by_name(self):
        with self.assertRaises(ValueError) as ctx:
            pipeline.validate_spec(_perf_spec(
                "/tmp/never", mastering_rule="some-other-rule"))
        self.assertIn("mastering_rule", str(ctx.exception))

    def test_unknown_lock_refused_by_name(self):
        with self.assertRaises(ValueError) as ctx:
            pipeline.validate_spec(_perf_spec(
                "/tmp/never", mastering_rule="krs-blueprint",
                locks={"chorus": True}))
        self.assertIn("locks.chorus", str(ctx.exception))

    def test_non_bool_lock_refused_by_name(self):
        with self.assertRaises(ValueError) as ctx:
            pipeline.validate_spec(_perf_spec(
                "/tmp/never", mastering_rule="krs-blueprint",
                locks={"instrumental": "yes"}))
        self.assertIn("locks.instrumental", str(ctx.exception))

    def test_missing_locks_normalize_open(self):
        out = pipeline.validate_spec(_perf_spec(
            "/tmp/never", mastering_rule="krs-blueprint"))
        self.assertEqual(out["locks"],
                         {"instrumental": False, "lyrics": False})

    def test_open_lock_weighed_in_the_rules_order(self):
        gate = pipeline.mastering_rule_open_lock
        self.assertIsNone(gate({}))
        self.assertIsNone(gate({"mastering_rule": "krs-blueprint",
                                "locks": {"instrumental": True,
                                          "lyrics": True}}))
        self.assertEqual(
            gate({"mastering_rule": "krs-blueprint",
                  "locks": {"instrumental": False,
                            "lyrics": False}}),
            "instrumental")
        self.assertEqual(
            gate({"mastering_rule": "krs-blueprint",
                  "locks": {"instrumental": True,
                            "lyrics": False}}),
            "lyrics")
        # Fail-closed however reached: no locks block at all.
        self.assertEqual(
            gate({"mastering_rule": "krs-blueprint"}),
            "instrumental")


class MasteringRuleSheetTests(unittest.TestCase):
    def _render(self, td, name, **over):
        out = Path(td) / name
        spec = _perf_spec(out, **over)
        with mock.patch.object(pipeline, "_run_bridge",
                               _fake_bridge(_write_noise_take)):
            return out, pipeline.produce(spec, log=lambda m: None)

    def test_both_locks_render_the_sheet(self):
        with tempfile.TemporaryDirectory() as td:
            out, _ = self._render(
                td, "sealed", mastering_rule="krs-blueprint",
                locks={"instrumental": True, "lyrics": True})
            self.assertTrue((out / "composition.abc").exists())
            self.assertTrue((out / "master.wav").exists())

    def test_missing_lyrics_refuses_and_names_it(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "open-lyrics"
            spec = _perf_spec(
                out, mastering_rule="krs-blueprint",
                locks={"instrumental": True, "lyrics": False})
            with mock.patch.object(
                    pipeline, "_run_bridge",
                    _fake_bridge(_write_noise_take)):
                with self.assertRaises(RuntimeError) as ctx:
                    pipeline.produce(spec, log=lambda m: None)
            self.assertIn("lyrics", str(ctx.exception))
            self.assertFalse((out / "composition.abc").exists())
            self.assertFalse((out / "master.wav").exists())

    def test_missing_instrumental_refuses_and_names_it(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "open-instrumental"
            spec = _perf_spec(
                out, mastering_rule="krs-blueprint",
                locks={"instrumental": False, "lyrics": True})
            with mock.patch.object(
                    pipeline, "_run_bridge",
                    _fake_bridge(_write_noise_take)):
                with self.assertRaises(RuntimeError) as ctx:
                    pipeline.produce(spec, log=lambda m: None)
            self.assertIn("instrumental", str(ctx.exception))
            self.assertFalse((out / "composition.abc").exists())

    def test_no_locks_at_all_refuses_at_the_first_lock(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "open-both"
            spec = _perf_spec(out, mastering_rule="krs-blueprint")
            with mock.patch.object(
                    pipeline, "_run_bridge",
                    _fake_bridge(_write_noise_take)):
                with self.assertRaises(RuntimeError) as ctx:
                    pipeline.produce(spec, log=lambda m: None)
            self.assertIn("instrumental", str(ctx.exception))
            self.assertFalse((out / "composition.abc").exists())

    def test_undeclared_spec_is_unaffected(self):
        with tempfile.TemporaryDirectory() as td:
            out, man = self._render(td, "plain")
            self.assertTrue((out / "composition.abc").exists())
            self.assertNotIn("mastering_rule", man["spec"])


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
