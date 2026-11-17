# 93
# ---------------------------------------------------------------------
# test_studio_visualize.py -- The In-House Media Visualizer,
# weighed pure.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: what is weighed here is the visualizer's pure core
# with no ffmpeg, no font, and no file in the room: the seat
# geometry on its logarithmic axis (edges exact, mapping
# monotonic, pairs sharing a tone sharing a column), the frame
# arithmetic (counts and centres exact by construction), the
# band weighing (a tone hears its own band, silence weighs
# zero), the gain mapping (bounded, guarded, gamma-lifted), the
# lamp smoothing (convex, directional), and the waveform
# reduction (true silhouettes, silence past the end). The live
# render -- decode, draw, encode -- is weighed by the demo run
# record, not here.
# ---------------------------------------------------------------------

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance.studio import visualize as viz


class SeatGeometryTests(unittest.TestCase):
    """The axis: log-true, edge-exact, monotonic."""

    def test_axis_edges_are_exact(self):
        self.assertEqual(viz.seat_x(100.0, 10, 1010), 10)
        self.assertEqual(viz.seat_x(1000.0, 10, 1010), 1010)

    def test_axis_is_monotonic_in_tone(self):
        xs = [viz.seat_x(h, 0, 900) for h in (100, 128, 192, 500, 1000)]
        self.assertEqual(xs, sorted(xs))
        self.assertTrue(all(b > a for a, b in zip(xs, xs[1:])))

    def test_axis_midpoint_is_the_geometric_mean(self):
        # On a log axis the middle of [100, 1000) is sqrt(100*1000).
        mid = viz.seat_x((100.0 * 1000.0) ** 0.5, 0, 800)
        self.assertAlmostEqual(mid, 400.0, places=6)

    def test_columns_group_pairs_sharing_a_tone(self):
        seats = [{"pair": "AA", "hz": 128.0}, {"pair": "BB", "hz": 128.0},
                 {"pair": "OO", "hz": 120.0}, {"pair": "CC", "hz": 192.0}]
        seats.sort(key=lambda s: (s["hz"], s["pair"]))
        cols = viz.layout_columns(seats)
        self.assertEqual([c["hz"] for c in cols], [120.0, 128.0, 192.0])
        self.assertEqual(cols[1]["pairs"], ["AA", "BB"])
        self.assertEqual(sum(len(c["pairs"]) for c in cols), 4)

    def test_the_real_dial_has_26_pairs_in_13_columns(self):
        seats = viz.load_seats(viz.dial_path())
        self.assertEqual(len(seats), 26)
        cols = viz.layout_columns(seats)
        self.assertEqual(len(cols), 13)
        self.assertEqual(max(len(c["pairs"]) for c in cols), 5)
        tones = [s["hz"] for s in seats]
        self.assertEqual(min(tones), 100.0)
        self.assertEqual(max(tones), 192.0)


class FrameArithmeticTests(unittest.TestCase):
    """Frame counts and centres, exact by construction."""

    def test_frame_count_rounds_to_nearest(self):
        self.assertEqual(viz.frame_count(13.385, 30), 402)
        self.assertEqual(viz.frame_count(10.0, 30), 300)

    def test_frame_count_never_below_one(self):
        self.assertEqual(viz.frame_count(0.001, 30), 1)

    def test_frame_centre_is_the_cell_midpoint(self):
        self.assertAlmostEqual(viz.frame_centre(0, 30), 0.5 / 30)
        self.assertAlmostEqual(viz.frame_centre(29, 30), 29.5 / 30)


class BandWeighingTests(unittest.TestCase):
    """A seat hears its own band; silence weighs zero."""

    def setUp(self):
        self.freqs = np.fft.rfftfreq(8192, d=1.0 / 44100)

    def test_energy_peaks_at_the_tone(self):
        mags = np.zeros_like(self.freqs)
        idx = int(np.argmin(np.abs(self.freqs - 144.0)))
        mags[idx] = 10.0
        near = viz.band_energy(mags, self.freqs, 144.0)
        far = viz.band_energy(mags, self.freqs, 800.0)
        self.assertGreater(near, 0.0)
        self.assertEqual(far, 0.0)

    def test_silence_weighs_zero(self):
        mags = np.zeros_like(self.freqs)
        self.assertEqual(viz.band_energy(mags, self.freqs, 128.0), 0.0)

    def test_band_edges_span_a_semitone_either_side(self):
        lo, hi = viz.band_edges(200.0)
        self.assertAlmostEqual(hi / 200.0, 2.0 ** (1.0 / 12.0), places=9)
        self.assertAlmostEqual(200.0 / lo, 2.0 ** (1.0 / 12.0), places=9)


class GainMappingTests(unittest.TestCase):
    """The lamp mapping: bounded, guarded, directional."""

    def test_zero_and_silent_reference_map_to_dark(self):
        self.assertEqual(viz.gain_from_energy(0.0, 5.0), 0.0)
        self.assertEqual(viz.gain_from_energy(5.0, 0.0), 0.0)

    def test_reference_energy_maps_to_full_light(self):
        self.assertEqual(viz.gain_from_energy(7.0, 7.0), 1.0)

    def test_gamma_lift_quarter_peak_is_half_light(self):
        self.assertAlmostEqual(viz.gain_from_energy(1.0, 4.0), 0.5)

    def test_gain_never_exceeds_one(self):
        self.assertEqual(viz.gain_from_energy(9.0, 4.0), 1.0)

    def test_smoothing_rises_faster_than_it_falls(self):
        up = viz.smooth_gain(0.0, 1.0)
        down = viz.smooth_gain(1.0, 0.0)
        self.assertGreater(up, 1.0 - down)
        self.assertTrue(0.0 <= up <= 1.0 and 0.0 <= down <= 1.0)

    def test_smoothing_holds_a_steady_gain(self):
        self.assertAlmostEqual(viz.smooth_gain(0.4, 0.4), 0.4)


class WaveformTests(unittest.TestCase):
    """The silhouette is the signal's own, silence past the end."""

    def test_peaks_track_a_sines_excursion(self):
        t = np.linspace(0, 1, 4410, endpoint=False)
        samples = np.sin(2 * np.pi * 10 * t).astype(np.float32)
        mins, maxs = viz.waveform_peaks(samples, 10)
        self.assertAlmostEqual(float(maxs.max()), 1.0, places=2)
        self.assertAlmostEqual(float(mins.min()), -1.0, places=2)

    def test_empty_body_reads_silence(self):
        mins, maxs = viz.waveform_peaks(np.zeros(0, dtype=np.float32), 8)
        self.assertTrue((mins == 0).all() and (maxs == 0).all())


class AnalyseTests(unittest.TestCase):
    """The whole weighing on synthetic sound, still pure."""

    def test_a_pure_tone_lights_its_own_seat(self):
        sr = 44100
        t = np.arange(sr) / sr  # one second
        samples = (0.8 * np.sin(2 * np.pi * 144.0 * t)).astype(np.float32)
        seats = [{"pair": "RR", "hz": 144.0}, {"pair": "YY", "hz": 100.0}]
        gains, reference = viz.analyse(samples, sr, 10, seats)
        self.assertEqual(gains.shape, (10, 2))
        self.assertGreater(reference, 0.0)
        # The 144 Hz seat (RR/II's column tone) ends near full light;
        # the 100 Hz seat hears only leakage, far less.
        self.assertGreater(gains[-1, 0], 0.8)
        self.assertLess(gains[-1, 1], gains[-1, 0])

    def test_silence_gains_nothing(self):
        samples = np.zeros(4410, dtype=np.float32)
        seats = [{"pair": "AA", "hz": 128.0}]
        gains, reference = viz.analyse(samples, 44100, 10, seats)
        self.assertEqual(reference, 0.0)
        self.assertTrue((gains == 0).all())


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
