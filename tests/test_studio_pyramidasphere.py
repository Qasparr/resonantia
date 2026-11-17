# 93
# ---------------------------------------------------------------------
# test_studio_pyramidasphere.py -- The Pyramidasphere scene,
# weighed pure.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: what is weighed here is the scene's pure core with
# no ffmpeg and no font in the room: the pyramid frame (exactly
# 31 nodes, in the instrument's square tiers, centred, descending,
# joined), the three seats in pyramid order with the folds
# climbing, the star's geometry (24 vertices, first point up,
# radii alternating), and the fold weighing (the bands partition
# the field, the mean law holds, silence renders dark, a tone
# lights its own fold, gains stay bounded). The sphere tile's
# cache is weighed as a rim object (no font is loaded by it).
# The live render -- decode, draw, encode -- is weighed by the
# demo run record, not here.
# ---------------------------------------------------------------------

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance.studio import pyramidasphere as pyr
from resonance.studio import visualize as viz

W, H = 1280, 720


class PyramidFrameTests(unittest.TestCase):
    """The frame: 31 nodes, square tiers, centred, joined."""

    def test_node_count_is_exactly_31(self):
        self.assertEqual(len(pyr.pyramid_nodes(W, H)), 31)

    def test_tiers_are_the_square_frame(self):
        rows = pyr.pyramid_rows(W, H)
        self.assertEqual([len(r) for r in rows], [1, 1, 4, 9, 16])
        self.assertEqual(1 ** 2 + 2 ** 2 + 3 ** 2 + 4 ** 2 + 1, 31)

    def test_rows_are_centred_on_the_axis(self):
        for row in pyr.pyramid_rows(W, H):
            mean_x = sum(x for x, _ in row) / len(row)
            self.assertAlmostEqual(mean_x, W / 2.0, places=6)

    def test_rows_descend_and_nodes_stay_in_the_field(self):
        rows = pyr.pyramid_rows(W, H)
        ys = [row[0][1] for row in rows]
        self.assertTrue(all(b > a for a, b in zip(ys, ys[1:])))
        for x, y in pyr.pyramid_nodes(W, H):
            self.assertTrue(0 < x < W)
            self.assertTrue(0 < y < H)

    def test_constant_pitch_within_a_tier(self):
        row = pyr.pyramid_rows(W, H)[-1]      # the 16 tier
        gaps = [b[0] - a[0] for a, b in zip(row, row[1:])]
        self.assertTrue(all(abs(g - gaps[0]) < 1e-9 for g in gaps))

    def test_edges_join_only_nodes(self):
        rows = pyr.pyramid_rows(W, H)
        nodes = set(pyr.pyramid_nodes(W, H))
        edges = pyr.node_edges(rows)
        within = sum(len(r) - 1 for r in rows)
        self.assertGreaterEqual(len(edges), within + 1 + 4 + 9 + 16)
        for a, b in edges:
            self.assertIn(a, nodes)
            self.assertIn(b, nodes)


class SphereSeatTests(unittest.TestCase):
    """The seats: pyramid order, the folds climbing."""

    def test_three_seats_apex_first(self):
        seats = pyr.sphere_seats(W, H)
        self.assertEqual(len(seats), 3)
        apex, base_left, base_right = seats
        self.assertLess(apex["cy"], base_left["cy"])
        self.assertEqual(base_left["cy"], base_right["cy"])
        self.assertLess(base_left["cx"], apex["cx"])
        self.assertLess(apex["cx"], base_right["cx"])

    def test_folds_climb_the_pyramid(self):
        seats = pyr.sphere_seats(W, H)
        self.assertEqual([s["fold"] for s in seats],
                         ["HIGH", "LOW", "MID"])
        self.assertEqual({s["fold"] for s in seats},
                         set(pyr.FOLD_NAMES))


class StarTests(unittest.TestCase):
    """The star: 24 vertices, first point up, radii alternating."""

    def test_star_vertices(self):
        pts = pyr.star_points(100.0, 100.0, 40.0, 18.0)
        self.assertEqual(len(pts), 24)
        self.assertAlmostEqual(pts[0][0], 100.0, places=9)
        self.assertAlmostEqual(pts[0][1], 60.0, places=9)
        dists = [((x - 100.0) ** 2 + (y - 100.0) ** 2) ** 0.5
                 for x, y in pts]
        self.assertAlmostEqual(dists[0], 40.0, places=9)
        self.assertAlmostEqual(dists[1], 18.0, places=9)
        self.assertAlmostEqual(dists[2], 40.0, places=9)


class FoldWeighingTests(unittest.TestCase):
    """The weighing: partition, mean law, darkness, ordering."""

    def test_bands_partition_the_field(self):
        bands = pyr.FOLD_BANDS
        self.assertEqual(len(bands), 3)
        for (lo, hi), (next_lo, _) in zip(bands, bands[1:]):
            self.assertLess(lo, hi)
            self.assertEqual(hi, next_lo)
        self.assertLess(bands[-1][1], viz.ANALYSIS_SR / 2.0)
        self.assertEqual(pyr.PROGRAM_BAND,
                         (bands[0][0], bands[-1][1]))

    def test_fold_energy_is_a_mean_not_a_sum(self):
        freqs = np.fft.rfftfreq(viz.FFT_SIZE, d=1.0 / viz.ANALYSIS_SR)
        mags = np.zeros_like(freqs)
        mags[(freqs >= 30.0) & (freqs < 240.0)] = 2.0
        self.assertAlmostEqual(pyr.fold_energy(mags, freqs, 30.0, 240.0),
                               2.0, places=9)
        self.assertEqual(pyr.fold_energy(mags, freqs, 240.0, 1920.0), 0.0)
        # A band past the analysis Nyquist is empty and weighs 0.
        self.assertEqual(pyr.fold_energy(mags, freqs, 23000.0, 24000.0),
                         0.0)

    def _tone(self, hz, seconds=2.0):
        t = np.arange(int(viz.ANALYSIS_SR * seconds)) / viz.ANALYSIS_SR
        return (0.8 * np.sin(2.0 * np.pi * hz * t)).astype(np.float32)

    def test_silence_renders_dark_folds(self):
        samples = np.zeros(viz.ANALYSIS_SR, dtype=np.float32)
        folds, program, ref, prog_ref = pyr.analyse_folds(
            samples, viz.ANALYSIS_SR, 10)
        self.assertEqual(ref, 0.0)
        self.assertEqual(prog_ref, 0.0)
        self.assertTrue(np.all(folds == 0.0))
        self.assertTrue(np.all(program == 0.0))

    def test_low_tone_lights_the_low_fold(self):
        folds, _, _, _ = pyr.analyse_folds(
            self._tone(120.0), viz.ANALYSIS_SR, 10)
        low, mid, high = (float(folds[-1, j]) for j in range(3))
        self.assertGreater(low, 0.8)
        self.assertGreater(low, mid + 0.3)
        self.assertLess(high, 0.2)

    def test_high_tone_lights_the_high_fold(self):
        folds, _, _, _ = pyr.analyse_folds(
            self._tone(6000.0), viz.ANALYSIS_SR, 10)
        low, mid, high = (float(folds[-1, j]) for j in range(3))
        self.assertGreater(high, 0.8)
        self.assertGreater(high, low + 0.3)

    def test_gains_stay_bounded(self):
        rng = np.random.default_rng(93)
        samples = (0.5 * rng.standard_normal(viz.ANALYSIS_SR * 2)
                   ).astype(np.float32)
        folds, program, _, _ = pyr.analyse_folds(
            samples, viz.ANALYSIS_SR, 10)
        self.assertTrue(np.all(folds >= 0.0) and np.all(folds <= 1.0))
        self.assertTrue(np.all(program >= 0.0)
                        and np.all(program <= 1.0))


class SphereTileTests(unittest.TestCase):
    """The rim: the tile's shape and the brightness cache."""

    def test_tile_is_square_at_the_seat_diameter(self):
        tile = pyr.sphere_tile(60)
        self.assertEqual(tile.size, (120, 120))

    def test_brightness_cache_reuses_its_tiles(self):
        painter = pyr.ScenePainter()
        first = painter.tile(60, 0.5)
        second = painter.tile(60, 0.5)
        self.assertIs(first, second)
        brighter = painter.tile(60, 0.9)
        self.assertIsNot(first, brighter)


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
