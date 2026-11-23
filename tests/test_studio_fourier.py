#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — tests/test_studio_fourier.py — the Fourier seat
# judged analytically: every signal below is chosen because its
# spectrum is known in closed form before the code runs.
#
# 93.
# Date: 23 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM: a transform is sworn only to what the
# mathematics guarantees. On whole-cycle tones the rFFT is
# exact — one bin carries the tone, at its true amplitude under
# the module's scaling law — so these tests assert tightly
# there; the round trip and Parseval are asserted to rounding;
# the floor is asserted at the house floor the module swears,
# and at the exact level of a component seated by hand. The
# shape law's refusals are asserted by the module's own error
# name. No snapshots: a stored spectrum could only prove the
# code agrees with itself.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""Tests for resonance/studio/fourier.py, against closed-form spectra."""

import unittest

import numpy as np

from resonance.studio import fourier
from resonance.studio.fourier import FLOOR_DB, FourierError

SR = 48000


def whole_cycle_tone(freq=1000.0, amp=0.5, seconds=1.0, sr=SR,
                     phase=0.0):
    """A sine with an exact whole number of cycles in the record.

    Whole cycles are the sworn class: the tone's energy falls
    on ONE bin exactly, so amplitude and frequency can be
    asserted to rounding, not to a leakage tolerance.
    """
    t = np.arange(int(sr * seconds)) / sr
    return amp * np.sin(2.0 * np.pi * freq * t + phase)


class TestSpectrumAmplitude(unittest.TestCase):
    """A sine of amplitude A reads A at exactly its bin."""

    def test_unwindowed_tone_exact(self):
        freqs, mag, _ = fourier.spectrum(whole_cycle_tone(), SR,
                                         window=None)
        k = int(np.argmax(mag))
        self.assertEqual(freqs[k], 1000.0)
        self.assertAlmostEqual(mag[k], 0.5, delta=1e-9)

    def test_hann_tone_exact_after_coherent_gain(self):
        # The periodic Hann's coherent gain is exactly 1/2 and
        # the module divides it out, so the windowed reading of
        # a whole-cycle tone is the same exact number.
        freqs, mag, _ = fourier.spectrum(whole_cycle_tone(), SR,
                                         window="hann")
        k = int(np.argmax(mag))
        self.assertEqual(freqs[k], 1000.0)
        self.assertAlmostEqual(mag[k], 0.5, delta=1e-9)

    def test_dominant_frequency(self):
        hz, mag = fourier.dominant_frequency(whole_cycle_tone(),
                                             SR)
        self.assertEqual(hz, 1000.0)
        self.assertAlmostEqual(mag, 0.5, delta=1e-9)


class TestRoundTripAndParseval(unittest.TestCase):
    """The lossless seat, and energy conserved across domains."""

    def _signal(self, n=4095):
        # Odd length on purpose: the inverse cannot infer it
        # from the coefficient count, so this also swears the
        # record carries its own length home.
        rng = np.random.default_rng(93)
        t = np.arange(n)
        return (0.4 * np.sin(2.0 * np.pi * 7 * t / n)
                + 0.2 * np.cos(2.0 * np.pi * 123 * t / n + 0.5)
                + 0.05 * rng.standard_normal(n))

    def test_round_trip_exact(self):
        x = self._signal()
        back = fourier.inverse(fourier.transform(x, SR))
        self.assertLess(np.max(np.abs(back - x)), 1e-10)

    def test_round_trip_even_length(self):
        x = self._signal(4096)
        back = fourier.inverse(fourier.transform(x, SR))
        self.assertLess(np.max(np.abs(back - x)), 1e-10)

    def test_parseval(self):
        # Time energy Σx² equals the single-sided power sum of
        # the raw coefficients divided by N — the module's own
        # scaling law, sworn numerically.
        x = self._signal()
        record = fourier.transform(x, SR)
        power = np.abs(record.coefficients) ** 2
        power[1:] *= 2.0
        if record.n_samples % 2 == 0:
            power[-1] /= 2.0
        e_freq = np.sum(power) / record.n_samples
        e_time = np.sum(x ** 2)
        self.assertAlmostEqual(e_freq / e_time, 1.0, delta=1e-12)


class TestDelay(unittest.TestCase):
    """A delay rotates phase and leaves magnitude standing."""

    def test_delay_law(self):
        n, sr, k_bin, shift = 4096, 16384, 64, 5
        t = np.arange(n)
        x = 0.7 * np.sin(2.0 * np.pi * k_bin * t / n + 0.3)
        y = np.roll(x, shift)
        _, mag_x, phase_x = fourier.spectrum(x, sr, window=None)
        _, mag_y, phase_y = fourier.spectrum(y, sr, window=None)
        np.testing.assert_allclose(mag_y, mag_x, rtol=0,
                                   atol=1e-12)
        rotated = np.angle(np.exp(1j * (phase_y[k_bin]
                                        - phase_x[k_bin])))
        expected = -2.0 * np.pi * k_bin * shift / n
        self.assertAlmostEqual(rotated, expected, delta=1e-9)


class TestFloorAbove(unittest.TestCase):
    """The honesty measurement, generalized and sworn."""

    def test_pure_tone_floors_deep(self):
        # A whole-cycle tone below the cutoff: above the cutoff
        # stands only rounding, reported at the house floor —
        # in any case far under the −90 dB the seat swears.
        reading = fourier.floor_above(whole_cycle_tone(), SR,
                                      5000.0)
        self.assertLess(reading, -90.0)
        self.assertEqual(reading, FLOOR_DB)

    def test_seated_component_reads_its_level(self):
        # A component seated by hand at −40 dB (amplitude ratio
        # 0.01) above the cutoff must read −40 dB: the floor is
        # a measurement, not a mood.
        x = whole_cycle_tone() + whole_cycle_tone(freq=8000.0,
                                                  amp=0.005)
        reading = fourier.floor_above(x, SR, 5000.0)
        self.assertAlmostEqual(reading, -40.0, delta=0.5)

    def test_silence_reads_the_floor(self):
        reading = fourier.floor_above(np.zeros(4096), SR, 5000.0)
        self.assertEqual(reading, FLOOR_DB)


class TestBandEnergy(unittest.TestCase):
    """Band shares against their closed-form energy fractions."""

    def setUp(self):
        # Amplitudes 0.5 and 0.25 → energies in ratio 4:1, so
        # the shares are exactly 0.8 and 0.2 of the total.
        self.mix = whole_cycle_tone() + whole_cycle_tone(
            freq=3000.0, amp=0.25)

    def test_band_shares(self):
        self.assertAlmostEqual(
            fourier.band_energy_db(self.mix, SR, 900, 1100),
            10.0 * np.log10(0.8), delta=0.01)
        self.assertAlmostEqual(
            fourier.band_energy_db(self.mix, SR, 2900, 3100),
            10.0 * np.log10(0.2), delta=0.01)

    def test_empty_band_reads_the_floor(self):
        self.assertEqual(
            fourier.band_energy_db(self.mix, SR, 5000, 6000),
            FLOOR_DB)


class TestStft(unittest.TestCase):
    """The time-frequency seat against a chirp of known law."""

    def test_chirp_tracked(self):
        sr, seconds, f0, f1 = 16000, 2.0, 300.0, 1500.0
        t = np.arange(int(sr * seconds)) / sr
        phase = 2.0 * np.pi * (f0 * t
                               + (f1 - f0) * t ** 2 / (2.0 * seconds))
        chirp = 0.6 * np.sin(phase)
        frame, hop = 1024, 512
        times, freqs, mag = fourier.stft(chirp, sr, frame, hop)
        resolution = sr / frame
        dominant = freqs[np.argmax(mag, axis=1)]
        instantaneous = f0 + (f1 - f0) * times / seconds
        # Every frame's dominant bin tracks the chirp's
        # instantaneous frequency at the frame centre to within
        # one bin, endpoints included in the same assertion.
        self.assertTrue(np.all(np.abs(dominant - instantaneous)
                               <= resolution))
        # And the track rises monotonically, one bin of slack
        # for the seating of a swept tone in a finite frame.
        self.assertTrue(np.all(np.diff(dominant)
                               >= -resolution))


class TestRefusals(unittest.TestCase):
    """The shape law, by the module's own error name."""

    def test_signal_refusals(self):
        with self.assertRaises(FourierError):
            fourier.transform([], SR)                      # empty
        with self.assertRaises(FourierError):
            fourier.transform([1.0], SR)                   # 1 sample
        with self.assertRaises(FourierError):
            fourier.transform([1.0, np.nan, 3.0], SR)      # non-finite
        with self.assertRaises(FourierError):
            fourier.transform(np.array([1.0 + 1.0j, 2.0]), SR)  # complex
        with self.assertRaises(FourierError):
            fourier.transform(np.zeros((2, 100)), SR)      # 2-D
        with self.assertRaises(FourierError):
            fourier.transform(["a", "b"], SR)              # text

    def test_rate_refusals(self):
        x = whole_cycle_tone(seconds=0.01)
        for bad in (0, -48000, np.inf, "48000", True):
            with self.assertRaises(FourierError):
                fourier.transform(x, bad)

    def test_window_refusal(self):
        with self.assertRaises(FourierError):
            fourier.spectrum(whole_cycle_tone(seconds=0.01), SR,
                             window="blackman")

    def test_band_refusals(self):
        x = whole_cycle_tone(seconds=0.01)
        with self.assertRaises(FourierError):
            fourier.band_energy_db(x, SR, 3000, 1000)   # low ≥ high
        with self.assertRaises(FourierError):
            fourier.band_energy_db(x, SR, 1000, 30000)  # past Nyquist
        with self.assertRaises(FourierError):
            fourier.band_energy_db(x, SR, 1000, 2000,
                                   reference="peak")    # unseated ref

    def test_cutoff_refusals(self):
        x = whole_cycle_tone(seconds=0.01)
        with self.assertRaises(FourierError):
            fourier.floor_above(x, SR, 0.0)
        with self.assertRaises(FourierError):
            fourier.floor_above(x, SR, 30000.0)         # past Nyquist

    def test_stft_refusals(self):
        x = whole_cycle_tone(seconds=0.01)
        with self.assertRaises(FourierError):
            fourier.stft(x, SR, 8192, 512)              # frame > signal
        with self.assertRaises(FourierError):
            fourier.stft(x, SR, 1024, 0)                # hop of nothing
        with self.assertRaises(FourierError):
            fourier.stft(x, SR, 1024.5, 512)            # fractional frame

    def test_inverse_refusals(self):
        x = whole_cycle_tone(seconds=0.01)
        record = fourier.transform(x, SR)
        with self.assertRaises(FourierError):
            # A bare array without its length: the seat does
            # not guess an odd length back into being.
            fourier.inverse(record.coefficients)
        with self.assertRaises(FourierError):
            fourier.inverse(np.array([1.0, 2.0, 3.0]),
                            n_samples=480)             # not complex
        # And the bare road WITH its length sworn works.
        back = fourier.inverse(record.coefficients,
                               n_samples=record.n_samples)
        np.testing.assert_allclose(back, x, rtol=0, atol=1e-10)


if __name__ == "__main__":
    unittest.main()
