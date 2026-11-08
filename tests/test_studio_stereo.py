# 93
# ---------------------------------------------------------------------
# test_studio_stereo.py -- the Stereo Law, weighed on its own scales.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VIII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: what is weighed here is the law's whole promise, in its
# three parts: a synthetic mono bed through the widener must lose
# its correlation (below 0.90) while its sub-180 Hz band stays mono
# (above 0.99) and its mid survives sample-for-sample; the spine's
# role pans must move no onset in time (the panned render's onsets
# sit exactly where the flat render's sit); and the spec contract
# must default the width the way the law prescribes -- on for spine
# productions, off on the Proof No. 1 road, refused by name outside
# 0..1. No rendering, no bridge: scales only.
# ---------------------------------------------------------------------

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance import grid  # noqa: E402
from resonance.studio import pipeline, spine  # noqa: E402

SR = 48000
BPM = 103


def _band_corr_time_domain(x, sr, lo_hz, hi_hz):
    """Channel correlation in a band, measured the pedestrian way.

    MECHANISM: brick-wall FFT mask, inverse transform, Pearson on
    the reconstructed time series -- deliberately NOT the
    pipeline's Parseval shortcut, so the widener is weighed on an
    independent scale.
    """
    n = x.shape[1]
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    band = (freqs >= lo_hz) & (freqs < hi_hz)
    chans = []
    for ch in x:
        spec = np.fft.rfft(ch)
        chans.append(np.fft.irfft(np.where(band, spec, 0.0), n=n))
    a = chans[0] - chans[0].mean()
    b = chans[1] - chans[1].mean()
    return float(np.dot(a, b) / np.sqrt(np.dot(a, a) * np.dot(b, b)))


def _tone_mix(sr=SR, seconds=2.0):
    """A mono test bed: one tone in the lows, two in the widened air."""
    n = int(sr * seconds)  # whole cycles at df=0.5 Hz: no leakage
    t = np.arange(n) / sr
    mono = (0.40 * np.sin(2 * np.pi * 100.0 * t)
            + 0.30 * np.sin(2 * np.pi * 1000.0 * t)
            + 0.30 * np.sin(2 * np.pi * 4000.0 * t))
    return np.stack([mono, mono])


class WidenerTests(unittest.TestCase):
    def test_mono_bed_decorrelates_but_lows_stay_mono(self):
        bed = _tone_mix()
        self.assertAlmostEqual(pipeline.channel_correlation(bed), 1.0,
                               places=9)  # the patient, as admitted
        out = pipeline.widen_bed(bed, SR, 1.0)
        self.assertEqual(out.shape, bed.shape)  # no onset can move
        full = pipeline.channel_correlation(out)
        self.assertLess(full, 0.90,
                        f"widened correlation {full:.3f} still mono")
        low = _band_corr_time_domain(out, SR, 20.0,
                                     pipeline.STEREO_LOW_CUT_HZ)
        self.assertGreater(low, 0.99,
                           f"low band correlation {low:.4f} broke mono")

    def test_mid_is_preserved_exactly(self):
        bed = _tone_mix()
        out = pipeline.widen_bed(bed, SR, 1.0)
        mid_before = 0.5 * (bed[0] + bed[1])
        mid_after = 0.5 * (out[0] + out[1])
        # The mono fold-down is the original signal: the widening
        # lives entirely in the side, where fold-down cannot hear it.
        self.assertLess(float(np.max(np.abs(mid_after - mid_before))),
                        1e-9)

    def test_zero_width_is_identity(self):
        bed = _tone_mix()
        out = pipeline.widen_bed(bed, SR, 0.0)
        np.testing.assert_array_equal(out, bed)

    def test_bad_width_refused(self):
        with self.assertRaises(ValueError) as ctx:
            pipeline.widen_bed(_tone_mix(), SR, 1.5)
        self.assertIn("width", str(ctx.exception))


class StereoSpecTests(unittest.TestCase):
    def _spec(self, **over):
        spec = {"prompt_base": "a test tone poem",
                "sections": [{"seconds": 10}],
                "out_dir": "/tmp/never-built"}
        spec.update(over)
        return pipeline.validate_spec(spec)

    def test_default_off_without_spine(self):
        self.assertEqual(self._spec()["stereo"]["width"], 0.0)

    def test_default_on_with_spine(self):
        spec = self._spec(spine={"bpm": 103, "sections": [
            {"name": "hook", "bars": 8, "density": "full"}]})
        self.assertEqual(spec["stereo"]["width"], 1.0)

    def test_explicit_width_outranks_default(self):
        spec = self._spec(
            stereo={"width": 0.25},
            spine={"bpm": 103, "sections": [
                {"name": "hook", "bars": 8, "density": "full"}]})
        self.assertEqual(spec["stereo"]["width"], 0.25)

    def test_bad_width_refused_by_name(self):
        with self.assertRaises(ValueError) as ctx:
            self._spec(stereo={"width": 1.5})
        self.assertIn("stereo.width", str(ctx.exception))


class SpinePanTests(unittest.TestCase):
    def _spine(self, sections, **over):
        raw = {"bpm": BPM, "swing": 0.0, "root_midi": 29,
               "sections": sections}
        raw.update(over)
        return spine.normalize_spine_spec(raw)

    def test_role_pans_obey_the_law(self):
        self.assertEqual(spine.role_pan("kick", 0), 0.0)
        self.assertEqual(spine.role_pan("kick", 7), 0.0)
        for pos in range(16):
            self.assertLessEqual(abs(spine.role_pan("snare", pos)),
                                 0.15)
            self.assertLessEqual(abs(spine.role_pan("clap", pos)),
                                 0.15)
        hats = [spine.role_pan("closed_hat", p) for p in range(4)]
        self.assertTrue(all(0.4 <= abs(p) <= 0.7 for p in hats))
        self.assertLess(hats[0] * hats[1], 0.0)  # alternation
        rims = [spine.role_pan("rimshot", p) for p in range(4)]
        self.assertTrue(all(0.4 <= abs(p) <= 0.7 for p in rims))
        self.assertLess(rims[0] * rims[1], 0.0)

    def test_flat_render_is_the_pre_law_dual_mono(self):
        sp = self._spine([{"name": "intro", "bars": 4,
                           "density": "sparse"}])
        flat = spine.render_spine(sp, SR, pan_fn=lambda v, s: 0.0)
        np.testing.assert_array_equal(flat[0], flat[1])

    def test_panning_moves_no_onset(self):
        # Sparse bar 0 strikes at steps 0 and 8 (kick+hat+bass, then
        # hat). The panned render must put its onset energy peaks on
        # exactly the samples the flat render does -- the pan scales
        # channels; it is not allowed to touch time.
        sp = self._spine([{"name": "intro", "bars": 4,
                           "density": "sparse"}])
        panned = spine.render_spine(sp, SR)
        flat = spine.render_spine(sp, SR, pan_fn=lambda v, s: 0.0)
        self.assertEqual(panned.shape, flat.shape)
        self.assertFalse(np.array_equal(panned[0], panned[1]),
                         "the law did not take: still dual-mono")
        step_float = grid.samples_per_beat(BPM, SR) / 4.0
        for step in (0, 8):
            at = int(round(step * step_float))
            win = slice(max(0, at - 64), at + 1024)
            pk_pan = int(np.argmax(np.abs(panned[0][win])
                                   + np.abs(panned[1][win])))
            pk_flat = int(np.argmax(np.abs(flat[0][win])
                                    + np.abs(flat[1][win])))
            self.assertEqual(pk_pan, pk_flat,
                             f"onset at step {step} moved under pan")


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
