#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — tests/test_studio_doppler.py — the Doppler seat
# judged analytically: the plate's formula at its exact seats,
# the plate's own numbers (λ′/λ″ at M = 0.5, sin θ_M = 0.625 at
# M = 1.6), the singularity refusals with their regimes named,
# and the two renders judged by MEASUREMENT on the house's
# sworn frequency instrument, studio/fourier.py — never by the
# construction that rendered them.
#
# 93.
# Date: 24 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM: a Doppler seat is sworn only to what
# the geometry guarantees. The formula's seats are asserted
# exactly where the arithmetic is exact (M = 0.5 doubles the
# frequency to the last bit); the renders are asserted where
# the Fourier seat can measure them — a whole-cycle tone reads
# its shifted frequency on one bin exactly, a record holding a
# whole number of cycles reads within one bin of the analytic
# frequency, and the pass-by glide is asserted frame by frame
# against the analytic instantaneous frequency with the bin
# width as the stated tolerance. The one coordinate the
# construction cannot hide — the cumulative phase exhausting
# a finite source before the render ends — is asserted at its
# predicted instant, not smoothed over. The shape law's
# refusals are asserted by the module's own error name.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""Tests for resonance/studio/doppler.py, against the plate's geometry."""

import unittest

import numpy as np

from resonance.studio import doppler, fourier
from resonance.studio.doppler import DopplerError

SR = 48000


def whole_cycle_tone(freq=1000.0, amp=0.5, seconds=1.0, sr=SR):
    """A sine with an exact whole number of cycles in the record.

    Whole cycles are the sworn class for measurement: the
    tone's energy falls on one Fourier bin exactly, so a
    rendered frequency can be asserted to the bin, not to a
    leakage tolerance.
    """
    t = np.arange(int(sr * seconds)) / sr
    return amp * np.sin(2.0 * np.pi * freq * t)


class TestFormulaExactness(unittest.TestCase):
    """The plate's formula at the seats where it is exact."""

    def test_approach_half_sound_speed_doubles(self):
        # M = 0.5 closing: f′ = f0 · 1/(1 − 0.5) = 2·f0, and
        # in floats the division is exact — asserted equal.
        self.assertEqual(doppler.observed_frequency(1000.0, 0.5),
                         2000.0)

    def test_recession_half_sound_speed(self):
        # M = 0.5 receding: f′ = f0/1.5.
        self.assertAlmostEqual(
            doppler.observed_frequency(1000.0, -0.5),
            1000.0 / 1.5, delta=1e-9)

    def test_observer_motion_numerator(self):
        # A closing observer alone: f′ = f0·(1 + 0.5) — the
        # plate's numerator read by itself.
        self.assertEqual(
            doppler.observed_frequency(1000.0, 0.0,
                                       v_observer=0.5),
            1500.0)
        # Both moving: (1 + 0.25)/(1 − 0.5) = 2.5.
        self.assertEqual(
            doppler.observed_frequency(1000.0, 0.5,
                                       v_observer=0.25),
            2500.0)

    def test_medium_is_callers_choice(self):
        # The same M = 0.5 in air's units (343 m/s): the seat
        # bakes no medium in, so the ratio is identical.
        self.assertEqual(
            doppler.observed_frequency(440.0, 171.5,
                                       v_sound=343.0),
            880.0)

    def test_wavelengths_at_half_sound_speed(self):
        # The plate's own numbers: λ′ = 0.5λ0, λ″ = 1.5λ0.
        front, back = doppler.wavelength_front_back(1.0, 0.5)
        self.assertEqual(front, 0.5)
        self.assertEqual(back, 1.5)
        front, back = doppler.wavelength_front_back(2.0, 0.5)
        self.assertEqual((front, back), (1.0, 3.0))

    def test_mach_number_signed(self):
        self.assertEqual(doppler.mach_number(0.5), 0.5)
        self.assertEqual(doppler.mach_number(-0.5), -0.5)
        self.assertEqual(doppler.mach_number(171.5, 343.0), 0.5)

    def test_mach_angle_plate_example(self):
        # The plate's supersonic panel: v_s = 1.6·v, so
        # sin θ_M = 1/1.6 = 0.625 — asserted to float
        # precision on the radians seat, and in degrees on
        # the plate's own unit.
        self.assertAlmostEqual(
            np.sin(doppler.mach_angle_rad(1.6)), 0.625,
            delta=1e-12)
        self.assertAlmostEqual(doppler.mach_angle(1.6),
                               38.68218745348943, delta=1e-9)

    def test_mach_angle_at_the_wall_is_ninety(self):
        # M = 1: the cone flattened to the shock wall, θ = 90°.
        self.assertEqual(doppler.mach_angle(1.0), 90.0)

    def test_regime_boundaries_exact(self):
        self.assertEqual(doppler.regime(0.5), "subsonic")
        self.assertEqual(doppler.regime(0.999999), "subsonic")
        self.assertEqual(doppler.regime(1.0), "sonic")
        self.assertEqual(doppler.regime(1.6), "supersonic")
        # Speed, not direction: recession is classified by
        # |v_source|, the plate's own axis.
        self.assertEqual(doppler.regime(-0.5), "subsonic")
        self.assertEqual(doppler.regime(-1.0), "sonic")
        self.assertEqual(doppler.regime(-2.0), "supersonic")


class TestRefusals(unittest.TestCase):
    """The singularities and the shape law, refused by name."""

    def test_sonic_pileup_refused_and_named(self):
        with self.assertRaises(DopplerError) as cm:
            doppler.observed_frequency(1000.0, 1.0)
        self.assertIn("sonic", str(cm.exception))
        self.assertIn("pile", str(cm.exception))

    def test_supersonic_shift_refused_and_named(self):
        with self.assertRaises(DopplerError) as cm:
            doppler.observed_frequency(1000.0, 1.5)
        self.assertIn("supersonic", str(cm.exception))
        with self.assertRaises(DopplerError):
            doppler.shift(whole_cycle_tone(), SR, 2.0)
        with self.assertRaises(DopplerError):
            doppler.shift(whole_cycle_tone(), SR, 1.0)

    def test_observer_outrunning_the_wave_refused(self):
        with self.assertRaises(DopplerError):
            doppler.observed_frequency(1000.0, 0.0,
                                       v_observer=-1.0)

    def test_no_cone_below_the_wave_speed(self):
        # The refusal IS the boundary coordinate: subsonic,
        # the fronts nest and there is no angle to return.
        with self.assertRaises(DopplerError) as cm:
            doppler.mach_angle(0.5)
        self.assertIn("subsonic", str(cm.exception))
        with self.assertRaises(DopplerError):
            doppler.mach_angle_rad(0.999)

    def test_wavelength_singularities_refused(self):
        with self.assertRaises(DopplerError):
            doppler.wavelength_front_back(1.0, 1.0)
        with self.assertRaises(DopplerError):
            doppler.wavelength_front_back(1.0, -1.0)

    def test_passby_refusals(self):
        tone = whole_cycle_tone(seconds=0.1)
        with self.assertRaises(DopplerError):
            doppler.passby(tone, SR, 1.0, 0.25)     # sonic
        with self.assertRaises(DopplerError):
            doppler.passby(tone, SR, 1.5, 0.25)     # supersonic
        with self.assertRaises(DopplerError):
            doppler.passby(tone, SR, 0.0, 0.25)     # no pass
        with self.assertRaises(DopplerError):
            doppler.passby(tone, SR, 0.5, 0.0)      # through
        with self.assertRaises(DopplerError):
            doppler.passby(tone, SR, 0.5, -0.25)    # the line

    def test_shape_law(self):
        with self.assertRaises(DopplerError):
            doppler.observed_frequency(0.0, 0.5)    # no tone
        with self.assertRaises(DopplerError):
            doppler.observed_frequency(1000.0, 0.5,
                                       v_sound=0.0)
        with self.assertRaises(DopplerError):
            doppler.observed_frequency(1000.0, True)  # a flag
        with self.assertRaises(DopplerError):
            doppler.mach_number(float("nan"))
        with self.assertRaises(DopplerError):
            doppler.shift(np.array([1.0 + 1.0j, 2.0]), SR, 0.5)
        with self.assertRaises(DopplerError):
            doppler.shift(np.zeros((2, 100)), SR, 0.5)
        with self.assertRaises(DopplerError):
            doppler.shift(np.array([0.5]), SR, 0.5)
        with self.assertRaises(DopplerError):
            doppler.shift(whole_cycle_tone(), 0, 0.5)


class TestShiftRender(unittest.TestCase):
    """The constant-velocity render, measured on the Fourier seat."""

    def test_approach_measures_double(self):
        y = doppler.shift(whole_cycle_tone(), SR, 0.5)
        # The duration law: the same 1,000 cycles in 1/r the
        # samples — r = 2, so exactly 24,000.
        self.assertEqual(y.size, 24000)
        hz, mag = fourier.dominant_frequency(y, SR)
        self.assertEqual(hz, 2000.0)
        self.assertAlmostEqual(mag, 0.5, delta=1e-3)

    def test_approach_floor_is_the_house_floor(self):
        # A steady whole-cycle centre segment (12,000 samples
        # = exactly 50 cycles at 2 kHz) carries nothing above
        # 3 kHz above the seat's sworn −90 dB; the bench read
        # the house floor itself, −120.0 dB.
        y = doppler.shift(whole_cycle_tone(), SR, 0.5)
        floor = fourier.floor_above(y[6000:18000], SR, 3000.0)
        self.assertLessEqual(floor, -90.0)

    def test_recession_measures_two_thirds(self):
        y = doppler.shift(whole_cycle_tone(), SR, -0.5)
        hz, mag = fourier.dominant_frequency(y, SR)
        # The record holds exactly 1,000 cycles, so the tone
        # sits on the record's own cycle grid: the reading is
        # asserted within one output bin of the analytic
        # f0/1.5, the bin width stated, not hidden.
        bin_hz = SR / y.size
        self.assertLessEqual(abs(hz - 1000.0 / 1.5), bin_hz)
        self.assertAlmostEqual(mag, 0.5, delta=1e-3)
        # And nothing above the tone beyond the sworn floor:
        # a 36,000-sample steady segment (exactly 500 cycles)
        # above 1 kHz.
        floor = fourier.floor_above(y[10000:46000], SR, 1000.0)
        self.assertLessEqual(floor, -90.0)

    def test_rest_is_identity(self):
        # v_source = 0: r = 1, positions are the integers, and
        # the windowed sinc at integer positions is the sample
        # itself — the render at rest is the handed waveform.
        x = whole_cycle_tone()
        y = doppler.shift(x, SR, 0.0)
        self.assertEqual(y.size, x.size)
        self.assertLess(np.max(np.abs(y - x)), 1e-9)

    def test_constant_signal_renders_flat(self):
        # The kernel's DC honesty: a constant evaluates to
        # itself in the interior (bench: ±3.5e-6; sworn here
        # at 1e-4, the difference kept as headroom).
        y = doppler.shift(np.ones(SR), SR, 0.3)
        interior = y[100:-100]
        self.assertLess(np.max(np.abs(interior - 1.0)), 1e-4)


class TestPassby(unittest.TestCase):
    """The pass: exact anchors, a measured glide, a sworn seam."""

    VS, D = 0.5, 0.25   # the sworn geometry, v_sound = 1

    def test_ratio_anchors_exact(self):
        # t → −∞: the full approach ratio 2.0; t = 0: exactly
        # 1 (the radial velocity vanishes at the tangent
        # point, so pitch crosses f0 at closest approach);
        # t → +∞: the recession ratio 2/3.
        self.assertAlmostEqual(
            doppler.passby_ratio(-1e7, self.VS, self.D), 2.0,
            delta=1e-9)
        self.assertEqual(
            doppler.passby_ratio(0.0, self.VS, self.D), 1.0)
        self.assertAlmostEqual(
            doppler.passby_ratio(1e7, self.VS, self.D), 2.0 / 3.0,
            delta=1e-9)

    def test_radial_velocity_anchors(self):
        self.assertEqual(
            doppler.passby_radial_velocity(0.0, self.VS, self.D),
            0.0)
        self.assertAlmostEqual(
            doppler.passby_radial_velocity(-1e7, self.VS, self.D),
            -0.5, delta=1e-9)
        self.assertAlmostEqual(
            doppler.passby_radial_velocity(1e7, self.VS, self.D),
            0.5, delta=1e-9)

    def test_glide_measured_frame_by_frame(self):
        # The end-to-end proof: a 4 s whole-cycle tone through
        # the pass, read by the Fourier seat's STFT. Every
        # frame in the sounded span is asserted within ONE
        # BIN (23.4375 Hz at frame 2048) of the analytic
        # instantaneous frequency f0·r(t) at its centre — the
        # bench's worst frame stood at 11.67 Hz, half a bin.
        src = whole_cycle_tone(seconds=4.0)
        out = doppler.passby(src, SR, self.VS, self.D)
        self.assertEqual(out.size, src.size)
        times, freqs, mag = fourier.stft(out, SR, 2048, 1024)
        dom = freqs[np.argmax(mag, axis=1)]
        centre = (src.size - 1) / 2.0 / SR
        bin_hz = SR / 2048
        seen = {"first": None, "centre": None, "last": None}
        for i, tc in enumerate(times):
            rel = tc - centre
            if -1.9 <= rel <= 0.6:
                analytic = 1000.0 * doppler.passby_ratio(
                    rel, self.VS, self.D)
                self.assertLessEqual(
                    abs(dom[i] - analytic), bin_hz,
                    f"frame at t={rel:+.3f} s: measured "
                    f"{dom[i]:.2f} Hz, analytic {analytic:.2f}")
                if seen["first"] is None:
                    seen["first"] = dom[i]
                if abs(rel) < 0.03:
                    seen["centre"] = dom[i]
                seen["last"] = dom[i]
        # The glide's shape, coarsely: approach above, the
        # crossing at f0, recession below — in that order.
        self.assertGreater(seen["first"], 1800.0)
        self.assertLess(abs(seen["centre"] - 1000.0), 2 * bin_hz)
        self.assertLess(seen["last"], 800.0)
        self.assertGreater(seen["first"], seen["centre"])
        self.assertGreater(seen["centre"], seen["last"])

    def test_exhaustion_coordinate_sworn(self):
        # The construction's one hard coordinate, asserted at
        # its predicted instant: the cumulative phase consumes
        # the 4 s source at τ = 4.0 s, which the ratio's own
        # trapezoid places at t = +0.7742 s; the render is
        # sounded before it and EXACTLY silent 5 ms after it.
        src = whole_cycle_tone(seconds=4.0)
        out = doppler.passby(src, SR, self.VS, self.D)
        t = (np.arange(out.size) - (out.size - 1) / 2.0) / SR
        ratio = doppler.passby_ratio(t, self.VS, self.D)
        tau = np.concatenate(
            [[0.0], np.cumsum(0.5 * (ratio[1:] + ratio[:-1])
                              / SR)])
        k = int(np.searchsorted(tau, 4.0))
        self.assertAlmostEqual(t[k], 0.7742, delta=0.001)
        # Sounded in the 100 ms before the predicted instant…
        self.assertGreater(
            np.max(np.abs(out[k - 4800:k])), 0.1)
        # …and exactly silent 5 ms after it, to the file's end.
        self.assertEqual(np.max(np.abs(out[k + 240:])), 0.0)


if __name__ == "__main__":
    unittest.main()
