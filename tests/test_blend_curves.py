# 93
# ---------------------------------------------------------------------
# test_blend_curves.py -- the sworn tests of resonance/studio/
# blend_curves.py. The figures are the Gamma-Hebdomad audit's own
# (claims M-01..M-03, recomputed there from the pdfs at 50 digits):
# the plate's three densities peak at 1.5 / 5.0 / 2.4576 at modes
# 0.5 / 1.0 / 0.2 and each integrates to 1. The crossfade road is
# sworn against the closed forms all three seats possess, so the
# continued fraction is proven exactly where the plate draws.
# ---------------------------------------------------------------------

import unittest

from resonance.studio.blend_curves import (
    EARLY_LEAN, LATE_SNAP, SYMMETRIC_BELL,
    bell_envelope, beta_pdf, blend, density_envelope,
    early_lean_blend, early_lean_envelope, late_snap_blend,
    late_snap_envelope, symmetric_blend,
)


class TestPlateDensities(unittest.TestCase):
    """The audit figures, M-01..M-03, as acceptance tests."""

    def test_bell_peak(self):
        self.assertAlmostEqual(beta_pdf(0.5, *SYMMETRIC_BELL), 1.5,
                               places=12)
        self.assertEqual(beta_pdf(0.0, *SYMMETRIC_BELL), 0.0)
        self.assertEqual(beta_pdf(1.0, *SYMMETRIC_BELL), 0.0)

    def test_late_snap_endpoint(self):
        self.assertAlmostEqual(beta_pdf(1.0, *LATE_SNAP), 5.0,
                               places=12)
        self.assertEqual(beta_pdf(0.0, *LATE_SNAP), 0.0)

    def test_early_lean_peak(self):
        self.assertAlmostEqual(beta_pdf(0.2, *EARLY_LEAN), 2.4576,
                               places=10)

    def test_densities_integrate_to_one(self):
        # Simpson on a fine grid: a density must carry unit mass.
        for seat in (SYMMETRIC_BELL, LATE_SNAP, EARLY_LEAN):
            n = 4000
            h = 1.0 / n
            total = 0.0
            for i in range(n + 1):
                w = 1 if i in (0, n) else (4 if i % 2 else 2)
                total += w * beta_pdf(i * h, *seat)
            self.assertAlmostEqual(total * h / 3.0, 1.0, places=4)


class TestEnvelopes(unittest.TestCase):
    def test_envelopes_top_at_one(self):
        self.assertAlmostEqual(bell_envelope(0.5), 1.0, places=12)
        self.assertAlmostEqual(late_snap_envelope(1.0), 1.0, places=12)
        self.assertAlmostEqual(early_lean_envelope(0.2), 1.0, places=10)

    def test_envelope_shapes(self):
        # The bell swells and falls; the snap is late; the lean early.
        self.assertLess(bell_envelope(0.1), bell_envelope(0.5))
        self.assertLess(bell_envelope(0.9), bell_envelope(0.5))
        # The snap at the midpoint is exactly 0.5^4 of its height.
        self.assertAlmostEqual(late_snap_envelope(0.5), 0.0625,
                               places=12)
        self.assertGreater(early_lean_envelope(0.2),
                           early_lean_envelope(0.8))

    def test_envelope_matches_density_ratio(self):
        # Envelope = density / peak, checked against the raw density.
        peak = beta_pdf(0.5, *SYMMETRIC_BELL)
        self.assertAlmostEqual(
            density_envelope(0.25, *SYMMETRIC_BELL),
            beta_pdf(0.25, *SYMMETRIC_BELL) / peak, places=12)


class TestBlends(unittest.TestCase):
    def test_endpoints(self):
        for fn in (symmetric_blend, late_snap_blend, early_lean_blend):
            self.assertEqual(fn(0.0), 0.0)
            self.assertEqual(fn(1.0), 1.0)

    def test_closed_forms(self):
        # The general road sworn against each seat's closed form.
        for t in (0.1, 0.25, 0.5, 0.75, 0.9):
            self.assertAlmostEqual(symmetric_blend(t),
                                   3 * t * t - 2 * t ** 3, places=10)
            self.assertAlmostEqual(late_snap_blend(t), t ** 5,
                                   places=10)
            self.assertAlmostEqual(early_lean_blend(t),
                                   1 - (1 - t) ** 5 * (1 + 5 * t),
                                   places=10)

    def test_symmetric_midpoint(self):
        self.assertAlmostEqual(symmetric_blend(0.5), 0.5, places=12)

    def test_shape_ordering(self):
        # At any interior mix point the lean has crossed furthest,
        # the snap least -- the names are the shapes.
        for t in (0.2, 0.4, 0.6, 0.8):
            self.assertGreater(early_lean_blend(t), symmetric_blend(t))
            self.assertGreater(symmetric_blend(t), late_snap_blend(t))

    def test_monotone(self):
        for fn in (symmetric_blend, late_snap_blend, early_lean_blend):
            prev = -1.0
            for i in range(101):
                v = fn(i / 100.0)
                self.assertGreaterEqual(v, prev)
                prev = v

    def test_generic_blend_agrees_with_presets(self):
        self.assertAlmostEqual(blend(0.3, 2.0, 2.0),
                               symmetric_blend(0.3), places=12)

    def test_clamping(self):
        self.assertEqual(symmetric_blend(-0.5), 0.0)
        self.assertEqual(symmetric_blend(1.5), 1.0)
        self.assertEqual(bell_envelope(-1.0), 0.0)


if __name__ == "__main__":
    unittest.main()
