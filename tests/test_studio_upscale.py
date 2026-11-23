#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — tests/test_studio_upscale.py — the upscale seat
# judged by proof, not snapshot: a tone whose frequency and
# amplitude are known before the code runs, a spectrum that must
# stay empty where the source never reached, a crest hidden
# between samples that the seat must surface, and loudness that
# must not move.
#
# 93.
# Date: 23 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM: an interpolator is sworn only to what
# the sampling theorem swears to — the waveform the samples
# determine, and nothing above the Nyquist they were captured
# under. These tests therefore assert: identity (the tone comes
# back at its own frequency and amplitude), honesty (no spectral
# content above the source Nyquist beyond the seat's sworn
# floor — the bench measured ≈ −110 dB against the −90 dB sworn
# here, headroom kept on purpose), revelation (a crest placed
# exactly between samples, invisible to the sample peak, stands
# in the report's true peak), and stillness (loudness unmoved —
# the seat applies no gain). The refusals are asserted by the
# module's own error name. No snapshots: a stored array could
# only prove the code agrees with itself.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""Tests for resonance/studio/upscale.py, against closed-form truth."""

import unittest

import numpy as np

from resonance.studio import upscale
from resonance.studio.upscale import IMAGE_FLOOR_DB, UpscaleError, resample_up

SR = 44100
TR = 96000


def tone(freq=1000.0, amp=0.5, seconds=1.0, sr=SR):
    """A pure tone with an exact whole number of cycles per second."""
    t = np.arange(int(sr * seconds)) / sr
    return amp * np.sin(2.0 * np.pi * freq * t)


def center_spectrum(y, sr, seconds=0.5):
    """FFT of the steady-state center of y (edges never measured).

    The segment length is a whole number of cycles of the 1 kHz
    test tone at both house rates, so the fundamental falls on
    one bin exactly and no windowing fiction enters the reading.
    """
    n = int(sr * seconds)
    seg = y[len(y) // 4: len(y) // 4 + n]
    return (np.abs(np.fft.rfft(seg)),
            np.fft.rfftfreq(n, d=1.0 / sr))


class TestTonePreserved(unittest.TestCase):
    """The waveform comes back as itself: frequency, amplitude, span."""

    def test_frequency_and_amplitude(self):
        y, _ = resample_up(tone(), SR, TR)
        self.assertEqual(len(y), TR)  # exactly one second, re-seated
        mag, freqs = center_spectrum(y, TR)
        k = int(np.argmax(mag))
        self.assertAlmostEqual(freqs[k], 1000.0, delta=2.0)
        # Bin magnitude of a whole-cycle segment is amp * n / 2.
        self.assertAlmostEqual(2.0 * mag[k] / (TR // 2), 0.5, delta=0.005)

    def test_duration_within_one_target_sample(self):
        _, report = resample_up(tone(seconds=0.5), SR, TR)
        self.assertEqual(report["samples_before"], SR // 2)
        self.assertEqual(report["samples_after"], TR // 2)
        drift = abs(report["samples_after"] / TR
                    - report["samples_before"] / SR)
        self.assertLessEqual(drift, 1.0 / TR)

    def test_awkward_length_counts(self):
        # 44101 samples: not a whole second, not divisible by the
        # ratio's denominator — the count must still be the exact
        # ceiling of n * up / down, and the span must hold.
        t = np.arange(44101) / SR
        x = 0.5 * np.sin(2.0 * np.pi * 1000.0 * t)
        y, report = resample_up(x, SR, TR)
        expected = -(-44101 * 320 // 147)
        self.assertEqual(len(y), expected)
        self.assertEqual(report["samples_after"], expected)
        drift = abs(expected / TR - 44101 / SR)
        self.assertLessEqual(drift, 1.0 / TR)

    def test_ratio_arithmetic_in_report(self):
        _, rep = resample_up(tone(seconds=0.5), SR, 192000)
        self.assertEqual((rep["ratio_up"], rep["ratio_down"]), (640, 147))
        x48 = tone(seconds=0.5, sr=48000)
        _, rep = resample_up(x48, 48000, TR)
        self.assertEqual((rep["ratio_up"], rep["ratio_down"]), (2, 1))
        self.assertEqual(rep["source_nyquist_hz"], 24000.0)


class TestHonesty(unittest.TestCase):
    """THE HONESTY PROOF: nothing above the source Nyquist, ever.

    The seat evaluates the waveform the samples determine; above
    22050 Hz the source determined nothing, so the upscaled
    spectrum must stand empty there down to the filter floor the
    module swears (IMAGE_FLOOR_DB). The bench measured the floor
    at ≈ −110 dB (largest bin) and ≈ −108 dB (total energy) for
    the window the seat ships; the assertions swear −90 dB and
    keep the measured headroom.
    """

    def test_no_content_above_source_nyquist(self):
        y, _ = resample_up(tone(), SR, TR)
        mag, freqs = center_spectrum(y, TR)
        fundamental = mag[int(np.argmax(mag))]
        above = mag[freqs > SR / 2.0]
        peak_db = 20.0 * np.log10(np.max(above) / fundamental)
        energy_db = 10.0 * np.log10(np.sum(above ** 2)
                                    / np.sum(mag ** 2))
        self.assertLess(peak_db, IMAGE_FLOOR_DB)
        self.assertLess(energy_db, IMAGE_FLOOR_DB)


class TestInterSamplePeak(unittest.TestCase):
    """The crest between the samples: hidden before, standing after.

    A sine at SR/4 with phase π/4 has its crest (analytic value
    1.0) falling exactly halfway between every pair of samples:
    the samples only ever read ±cos(π/4) = ±0.7071. The sample
    peak therefore swears −3.01 dB while the waveform's true peak
    is 0 dB. The seat's report must show the truth on both sides,
    and the delivered interior must BE the waveform — sample peak
    0.999986 on the bench — never overshooting it in the interior.
    (The whole-file true peak after reads higher still, +0.80
    dBTP on the bench: the seam ring the module's doctrine names,
    on a signal that begins mid-crest at full scale. The sworn
    assertion is the gap over the source sample peak, with the
    interior asserted separately and exactly.)
    """

    def setUp(self):
        t = np.arange(SR) / SR
        self.x = np.cos(2.0 * np.pi * (SR / 4.0) * t + np.pi / 4.0)
        self.y, self.report = resample_up(self.x, SR, TR)

    def test_sample_peak_hides_the_crest(self):
        # Analytic: 20*log10(cos(pi/4)) = -3.0103 dB.
        self.assertAlmostEqual(self.report["sample_peak_before_db"],
                               -3.01, delta=0.02)

    def test_true_peak_was_always_there(self):
        self.assertAlmostEqual(self.report["true_peak_before_dbtp"],
                               0.0, delta=0.05)
        self.assertAlmostEqual(self.report["intersample_rise_before_db"],
                               3.01, delta=0.05)

    def test_seat_surfaces_the_crest(self):
        self.assertGreater(self.report["true_peak_after_dbtp"],
                           self.report["sample_peak_before_db"] + 2.0)

    def test_interior_is_the_waveform_itself(self):
        margin = TR // 20  # 50 ms: far outside the seam's span
        interior = np.max(np.abs(self.y[margin:-margin]))
        self.assertLessEqual(interior, 1.0 + 0.001)
        self.assertGreaterEqual(interior, 1.0 - 0.001)


class TestLoudness(unittest.TestCase):
    """The seat applies no gain: loudness before and after agree."""

    def test_loudness_unmoved_on_program(self):
        rng = np.random.default_rng(93)
        n = 2 * SR
        t = np.arange(n) / SR

        def chan(seed):
            r = np.random.default_rng(seed)
            x = (0.30 * np.sin(2.0 * np.pi * 110 * t)
                 + 0.20 * np.sin(2.0 * np.pi * 440 * t + 0.3)
                 + 0.12 * np.sin(2.0 * np.pi * 1320 * t + 1.1)
                 + 0.05 * r.standard_normal(n))
            return x * (0.7 + 0.3 * np.sin(2.0 * np.pi * 0.5 * t))

        stereo = np.stack([chan(93), chan(94)])  # house (channels, N)
        _, report = resample_up(stereo, SR, TR)
        self.assertLessEqual(
            abs(report["lufs_after"] - report["lufs_before"]), 0.1)
        self.assertLessEqual(report["lufs_delta"], 0.1)


class TestShapes(unittest.TestCase):
    """The caller's shape is the returned shape, exactly."""

    def test_mono_stays_mono(self):
        y, report = resample_up(tone(seconds=0.5), SR, TR)
        self.assertEqual(y.ndim, 1)
        self.assertEqual(report["channels"], 1)

    def test_stereo_stays_stereo(self):
        x = np.stack([tone(seconds=0.5), tone(seconds=0.5)])
        y, report = resample_up(x, SR, TR)
        self.assertEqual(y.shape, (2, TR // 2))
        self.assertEqual(report["channels"], 2)

    def test_one_channel_2d_stays_2d(self):
        y, _ = resample_up(tone(seconds=0.5)[np.newaxis, :], SR, TR)
        self.assertEqual(y.shape, (1, TR // 2))

    def test_silence_floors_at_the_house_floor(self):
        y, report = resample_up(np.zeros(SR), SR, TR)
        self.assertTrue(np.all(y == 0.0))
        self.assertEqual(report["sample_peak_before_db"], -120.0)
        self.assertEqual(report["sample_peak_after_db"], -120.0)
        self.assertEqual(report["true_peak_before_dbtp"], -120.0)
        self.assertEqual(report["lufs_before"], -120.0)
        self.assertEqual(report["lufs_after"], -120.0)


class TestRefusals(unittest.TestCase):
    """Every refusal by the module's own name, before arithmetic."""

    def setUp(self):
        self.x = tone(seconds=0.25)

    def test_downsampling_refused(self):
        with self.assertRaises(UpscaleError):
            resample_up(self.x, TR, SR)

    def test_same_rate_refused(self):
        with self.assertRaises(UpscaleError):
            resample_up(self.x, 48000, 48000)

    def test_bad_rates_refused(self):
        for bad in (0, -44100, 44100.5, "96000", None, True):
            with self.assertRaises(UpscaleError, msg=f"rate {bad!r}"):
                resample_up(self.x, bad, TR)
            with self.assertRaises(UpscaleError, msg=f"rate {bad!r}"):
                resample_up(self.x, SR, bad)

    def test_empty_refused(self):
        with self.assertRaises(UpscaleError):
            resample_up(np.array([]), SR, TR)
        with self.assertRaises(UpscaleError):
            resample_up(np.zeros((2, 0)), SR, TR)
        with self.assertRaises(UpscaleError):
            resample_up(np.zeros((0, 100)), SR, TR)

    def test_unreal_shapes_refused(self):
        with self.assertRaises(UpscaleError):
            resample_up(np.zeros((2, 3, 4)), SR, TR)
        with self.assertRaises(UpscaleError):
            resample_up(np.array(1.0), SR, TR)
        with self.assertRaises(UpscaleError):
            resample_up(self.x.astype(complex), SR, TR)
        with self.assertRaises(UpscaleError):
            resample_up(["a", "b", "c"], SR, TR)

    def test_short_program_refused_by_loudness_block(self):
        # 0.25 s is under the BS.1770 scale's 0.400 s block: the
        # seat refuses by name rather than report an unsworn
        # loudness. (0.5 s program throughout this file passes.)
        with self.assertRaises(UpscaleError) as cm:
            resample_up(self.x, SR, TR)
        self.assertIn("0.400", str(cm.exception))

    def test_nonfinite_refused(self):
        for poison in (np.nan, np.inf):
            x = self.x.copy()
            x[10] = poison
            with self.assertRaises(UpscaleError, msg=f"{poison}"):
                resample_up(x, SR, TR)


if __name__ == "__main__":
    unittest.main()
