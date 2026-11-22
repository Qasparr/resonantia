#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — tests/test_studio_eqvillibbrrivmm.py — the
# EQVILLIBBRRIVMM studio mirrors, judged against the C++ of record
#
# 93.
# Date: 22 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM: the Python mirrors in studio/eqvillibbrrivmm.py
# are judged the way the house judges everything — by the same
# behaviours the founder's own C++ harness asserted in
# eqvillibbrrivmm/test_fluid_voice.cpp (the DOOD table's seat and
# wrap, the cube's count and closed gate, the pitch roundtrip, the
# rail's pass and cushion), plus the one behaviour the harness had
# no Python counterpart to prove: the convolution equalizer's
# direction on real samples, measured by probe before it was sworn
# here (200 Hz passes at 0.997 RMS, 6,000 Hz falls to 0.345, pole
# at the Full Key G9). A mirror that cannot be re-derived against
# the C++ is not a mirror; it is a rumor with a file name.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""Tests for resonance/studio/eqvillibbrrivmm.py, against the C++."""

import math
import unittest

import numpy as np

from resonance.studio import eqvillibbrrivmm as eq


class TestDoodTable(unittest.TestCase):
    """The DOOD table: 24 steps seated, wrap by modulo, Block4 at 22."""

    def test_table_seats_24_steps(self):
        # MECHANISM: the C++ table is a fixed std::array<PatternStep, 24>
        # (fluid_voice.cpp:68); the mirror's tuple must seat the same 24,
        # in order, indices sworn.
        self.assertEqual(len(eq.DOOD_TABLE), 24)
        for i, step in enumerate(eq.DOOD_TABLE):
            self.assertEqual(step.step_index, i)

    def test_step_at_wraps_by_modulo(self):
        # MECHANISM: stepAt indexes by % 24 (fluid_voice.cpp:106-109), and
        # the C++ harness asserted stepAt(24) is step 0. The mirror holds
        # the same wrap, one full turn and beyond.
        self.assertEqual(eq.dood_step_at(24).step_index, 0)
        self.assertEqual(eq.dood_step_at(48).step_index, 0)
        self.assertEqual(eq.dood_step_at(25).step_index, 1)

    def test_block4_at_step_22(self):
        # MECHANISM: the DD-Block4 line seats Block4 at steps 22-23 with
        # gate weight 1.25 (fluid_voice.cpp:102-103); the harness asserted
        # step 22's glyph. Motif and symbol ride with it.
        step22 = eq.dood_step_at(22)
        self.assertEqual(step22.glyph, "Block4")
        self.assertEqual(step22.symbol, "■4")
        self.assertEqual(step22.gate_weight, 1.25)
        self.assertEqual(eq.dood_step_at(23).glyph, "Block4")
        self.assertEqual(eq.dood_step_at(0).motif, "DOOD")
        self.assertEqual(eq.dood_step_at(0).gate_weight, 1.00)


class TestCube48(unittest.TestCase):
    """The 48^3 cube: 110,592 cells, 48 Hz anchor, gate closes."""

    def test_cells_and_anchor(self):
        # MECHANISM: 48 x 48 x 48 = 110,592 (fluid_voice.cpp:41-42),
        # held as a static_assert in the harness; here as arithmetic.
        self.assertEqual(eq.CUBE48_CELLS, 110592)
        self.assertEqual(eq.CUBE48_CELLS, 48 ** 3)
        metrics = eq.cube48_evaluate(3, 0.25, 1.0)
        self.assertEqual(metrics.total_cells, 110592)
        self.assertEqual(metrics.anchor_hz, 48.0)

    def test_energy_in_unit_interval(self):
        # MECHANISM: energy is clamped to [0, 1] in the founder's code
        # (fluid_voice.cpp:132); sweep frames and times to prove the
        # clamp holds across the lattice walk, not at one point.
        for frame in range(0, 96, 7):
            for elapsed in (0.0, 0.25, 1.7):
                energy = eq.cube48_evaluate(frame, elapsed, 1.0).energy
                self.assertGreaterEqual(energy, 0.0)
                self.assertLessEqual(energy, 1.0)

    def test_zero_gate_closes_the_cube(self):
        # MECHANISM: raw energy is multiplied by the DOOD gate weight
        # (fluid_voice.cpp:131), so a zero gate gives exactly zero —
        # the harness asserted the same identity.
        self.assertEqual(eq.cube48_evaluate(3, 0.25, 0.0).energy, 0.0)


class TestAutotune(unittest.TestCase):
    """The fluid voice: pitch roundtrip, correction sane, clamps hold."""

    def test_pitch_roundtrip_a4(self):
        # MECHANISM: 12-TET about A4 = 440 Hz = MIDI 69
        # (fluid_voice.cpp:171-177); the harness held 440 <-> 69 and
        # the 528 roundtrip. The mirror holds them tighter (double
        # width), asserted at 1e-9.
        self.assertAlmostEqual(eq.freq_to_midi(440.0), 69.0, places=9)
        self.assertAlmostEqual(eq.midi_to_freq(69.0), 440.0, places=9)
        self.assertAlmostEqual(
            eq.midi_to_freq(eq.freq_to_midi(528.0)), 528.0, places=6)

    def test_target_selection(self):
        # MECHANISM: candidates are the Solfeggio note at 0.5x, 1x, and
        # 1.5x — or the Full Key G9 in the third seat when the lock
        # index exceeds 0.65 (fluid_voice.cpp:184-186). Nearest in
        # MIDI distance wins.
        self.assertEqual(eq.select_autotune_target(528.0, 528.0, 0.0), 528.0)
        self.assertEqual(eq.select_autotune_target(264.0, 528.0, 0.0), 264.0)
        self.assertEqual(
            eq.select_autotune_target(1200.0, 528.0, 0.9), eq.FULL_KEY_G9_HZ)

    def test_frames_finite_and_formants_clamped(self):
        # MECHANISM: the harness ran four frames back to back so the
        # glide state is exercised, asserting fftSize finite samples,
        # lock in [0, 1], F1 in [250, 1200], F2 in [900, 3200]
        # (fluid_voice.cpp:237-238). The mirror is held to the same.
        engine = eq.FluidVoiceAutotune()
        cube = eq.cube48_evaluate(3, 0.25, 1.0)
        for frame in range(4):
            synth = engine.synthesize_frame(frame, 512, 528.0, 1.0,
                                            cube.energy, 0.0)
            self.assertEqual(synth.voice_samples.shape, (512,))
            self.assertTrue(np.all(np.isfinite(synth.voice_samples)))
            self.assertGreater(synth.autotuned_pitch_hz, 0.0)
            self.assertGreaterEqual(synth.lock_index, 0.0)
            self.assertLessEqual(synth.lock_index, 1.0)
            self.assertGreaterEqual(synth.formant_f1_hz, 250.0)
            self.assertLessEqual(synth.formant_f1_hz, 1200.0)
            self.assertGreaterEqual(synth.formant_f2_hz, 900.0)
            self.assertLessEqual(synth.formant_f2_hz, 3200.0)

    def test_correction_sign_and_magnitude_sane(self):
        # MECHANISM: the engine's own raw pitch sweeps 196-306 Hz
        # (fluid_voice.cpp:213) while the 528 Hz Solfeggio target
        # pulls the snap upward by strength 0.85; the sounding pitch
        # glides after it, so the correction (sounding minus raw, in
        # cents) is positive and bounded — the harness's frame-3
        # print showed +52.97 cents at lock 0.989. Asserted here as
        # direction and sane magnitude, not a copied figure: the
        # mirror's double-width glide lands near, not on, the C++'s
        # float32 print.
        engine = eq.FluidVoiceAutotune()
        cube = eq.cube48_evaluate(3, 0.25, 1.0)
        synth = None
        for frame in range(4):
            synth = engine.synthesize_frame(frame, 512, 528.0, 1.0,
                                            cube.energy, 0.0)
        self.assertGreaterEqual(synth.raw_pitch_hz, 196.0)
        self.assertLessEqual(synth.raw_pitch_hz, 306.0)
        self.assertGreater(synth.correction_cents, 0.0)
        self.assertLess(synth.correction_cents, 200.0)
        self.assertGreater(synth.autotuned_pitch_hz, synth.raw_pitch_hz)
        self.assertGreater(synth.lock_index, 0.9)


class TestRail13_5(unittest.TestCase):
    """The 13/5 rail: pass in-rail, cushion over-rail, center key railed."""

    def test_in_rail_passes_untouched(self):
        # MECHANISM: |x| <= 2.6 returns x itself, unengaged
        # (fluid_voice.cpp:460-462) — the harness asserted value and
        # flag for 1.0; the rail's own edge is in-rail too.
        result = eq.cushion_13_5(1.0)
        self.assertFalse(result.engaged)
        self.assertEqual(result.value, 1.0)
        edge = eq.cushion_13_5(eq.GUARDRAIL_RATIO_13_5)
        self.assertFalse(edge.engaged)
        self.assertEqual(edge.value, eq.GUARDRAIL_RATIO_13_5)

    def test_over_rail_cushions_engaged(self):
        # MECHANISM: beyond the rail, sign * (2.6 - 0.15*tanh(excess))
        # — engaged, sign preserved, pulled back INSIDE the bound
        # (fluid_voice.cpp:463-467); both directions, as the harness
        # asserted for +10 and -10.
        for raw, sign in ((10.0, 1.0), (-10.0, -1.0)):
            result = eq.cushion_13_5(raw)
            self.assertTrue(result.engaged)
            self.assertEqual(math.copysign(1.0, result.value), sign)
            self.assertLessEqual(abs(result.value), eq.GUARDRAIL_RATIO_13_5)
            self.assertGreater(abs(result.value),
                               eq.GUARDRAIL_RATIO_13_5 - 0.15)

    def test_center_key_railed_at_any_time(self):
        # MECHANISM: the center-key position passes through the rail
        # by construction (fluid_voice.cpp:469-473), so |position|
        # never exceeds 13/5 — asserted across a time sweep, as the
        # manifold's own assert holds it per-frame.
        for t in (0.0, 0.37, 1.234, 5.0, 93.0):
            self.assertLessEqual(abs(eq.center_key_position(t)),
                                 eq.GUARDRAIL_RATIO_13_5 + 1e-9)


class TestConvolutionEq(unittest.TestCase):
    """The equalizer: the Laplace bus's kernel at work on samples."""

    @staticmethod
    def _rms_ratio(freq_hz, pole_hz, seconds=0.5, sr=48000):
        # MECHANISM: a half-amplitude sine's steady-state RMS after
        # the EQ, over its RMS before, skipping the kernel's attack
        # (first 100 samples) — the probe's own measure.
        t = np.arange(int(sr * seconds), dtype=np.float64) / sr
        x = 0.5 * np.sin(2.0 * np.pi * freq_hz * t)
        y = eq.apply_eq(x, pole_hz)
        return (np.sqrt(np.mean(y[100:] ** 2))
                / np.sqrt(np.mean(x[100:] ** 2)))

    def test_convolve_identity_and_clamp(self):
        # MECHANISM: a unit impulse kernel returns the input
        # (manifold.cpp:259-277), and the output clamps to [-1, 1]
        # however hot the accumulation runs.
        x = np.array([0.25, -0.5, 0.75, 0.0])
        np.testing.assert_allclose(
            eq.convolve_time_domain(x, np.array([1.0])), x)
        hot = eq.convolve_time_domain(
            np.array([0.9, 0.9]), np.array([2.0, 2.0]))
        self.assertTrue(np.all(np.abs(hot) <= 1.0))

    def test_eq_attenuates_high_band_relative_to_low(self):
        # MECHANISM: the 16-tap kernel exp(-0.28k)*cos(0.35k*|Re H|)
        # is a decaying, lowpass-leaning FIR (manifold.cpp:301-313).
        # Probed before swearing: at the G9 pole, 200 Hz passes at
        # 0.997 RMS and 6,000 Hz falls to 0.345. Asserted as the
        # direction and a wide magnitude bound — the mirror's
        # double-width figures land near the probe, not on it.
        low = self._rms_ratio(200.0, eq.FULL_KEY_G9_HZ)
        high = self._rms_ratio(6000.0, eq.FULL_KEY_G9_HZ)
        self.assertGreater(low, 0.9)
        self.assertLess(high, 0.6)
        self.assertLess(high, low)

    def test_transfer_magnitude_clamped(self):
        # MECHANISM: transfer_magnitude is |H(s)| clamped to
        # [0.05, 3.0] (manifold.cpp:322); at the manifold's own
        # operating point the unclamped |H| sits inside, and the
        # s-plane product is finite.
        x = np.zeros(512)
        x[0] = 1.0
        result = eq.evaluate_laplace_domain(x, 0.25, 2.0 * np.pi * 629.342,
                                            eq.FULL_KEY_G9_HZ)
        self.assertGreaterEqual(result.transfer_magnitude, 0.05)
        self.assertLessEqual(result.transfer_magnitude, 3.0)
        self.assertTrue(np.isfinite(result.s_plane_product.real))
        self.assertEqual(result.time_domain_convolved.shape, (512,))


class TestModuleChecks(unittest.TestCase):
    """The module's own re-derivation, on the cubes.py pattern."""

    def test_eqvillibbrrivmm_checks_all_pass(self):
        # MECHANISM: eqvillibbrrivmm_checks() re-derives every sworn
        # figure from its base; a single drifted constant fails by
        # name, as cubes_checks() judges the parallel record.
        results = eq.eqvillibbrrivmm_checks()
        self.assertTrue(results)
        for name, passed, got in results:
            self.assertTrue(passed, f"{name}: got {got}")


if __name__ == "__main__":
    unittest.main()


# =============================================================================
# Closing motto: "Live, Love, and let Love, Live."
# 93 — Live, Love, and let Love, Live.
# =============================================================================
