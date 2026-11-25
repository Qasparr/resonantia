# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# SPDX-License-Identifier: AGPL-3.0-only
"""
tests/test_acoustics.py -- unittest tests for resonance.studio.acoustics.

Run:  python3 -m unittest tests.test_acoustics   (from the repo root)
   or python3 -m unittest discover -s tests

The acceptance figures are THE PLATE'S OWN: the founder's uploaded
Map of Sound (2026-11-25) prints A4's wavelength as 0.78 m in air, a
1 s echo as a wall 171.5 m away, a 0.5 m open pipe at 343 Hz, 440
against 444 Hz as 4 pulses a second, and double the distance as 6 dB
quieter. Each test asserts the plate's figure within the plate's own
rounding, and prints the seam where the module's precision and the
plate's rounding differ -- the seam is a finding, not a failure.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resonance.studio import acoustics as ac


class TestWaveRelation(unittest.TestCase):
    def test_air_speed_plate(self):
        # The plate: 343 m/s in air at 20 C.
        self.assertEqual(ac.speed("air"), 343.0)

    def test_air_speed_temperature_law(self):
        # The finer law reads 343.42 at 20 C -- the plate's rounding.
        self.assertAlmostEqual(ac.speed_of_sound_air(20.0), 343.42, places=2)
        self.assertLess(ac.speed_of_sound_air(0.0), ac.speed_of_sound_air(20.0))

    def test_wavelength_plate(self):
        # The plate: note A4 (440 Hz), wavelength 0.78 m in air.
        self.assertAlmostEqual(ac.wavelength(440.0), 0.78, delta=0.01)

    def test_frequency_inverts_wavelength(self):
        lam = ac.wavelength(440.0)
        self.assertAlmostEqual(ac.frequency(lam), 440.0, places=6)

    def test_wave_speed(self):
        self.assertAlmostEqual(ac.wave_speed(440.0, 343.0 / 440.0), 343.0,
                               places=6)

    def test_medium_order_plate(self):
        # The plate's ranking: air < water < steel.
        self.assertLess(ac.speed("air"), ac.speed("water"))
        self.assertLess(ac.speed("water"), ac.speed("steel"))

    def test_unknown_medium_refuses(self):
        with self.assertRaises(ValueError):
            ac.speed("moonrock")


class TestEchoAndDelay(unittest.TestCase):
    def test_echo_distance_plate(self):
        # The plate: a 1 s echo means a wall 171.5 m away.
        self.assertAlmostEqual(ac.echo_distance(1.0), 171.5, places=6)

    def test_echo_time_inverts(self):
        self.assertAlmostEqual(ac.echo_time(171.5), 1.0, places=6)

    def test_delay_round_trip(self):
        d = 10.0
        self.assertAlmostEqual(ac.distance_for_delay(ac.delay_ms(d)), d,
                               places=9)

    def test_delay_value(self):
        # 10 m in air: 1000 * 10 / 343 = 29.1545... ms.
        self.assertAlmostEqual(ac.delay_ms(10.0), 29.1545, delta=0.001)

    def test_ranging_table(self):
        rows = ac.ranging_table([1.0, 10.0])
        self.assertEqual(len(rows), 2)
        # Echo is the round trip: exactly twice the one-way delay.
        for row in rows:
            self.assertAlmostEqual(row["echo_ms"], 2.0 * row["one_way_ms"],
                                   places=9)


class TestResonance(unittest.TestCase):
    def test_open_pipe_plate(self):
        # The plate: a 0.5 m open pipe sings at 343 Hz.
        self.assertAlmostEqual(ac.open_pipe_fundamental(0.5), 343.0, places=6)

    def test_open_pipe_harmonics_all_integers(self):
        series = ac.open_pipe_harmonics(0.5, 3)
        self.assertEqual(len(series), 3)
        for got, want in zip(series, [343.0, 686.0, 1029.0]):
            self.assertAlmostEqual(got, want, places=6)

    def test_closed_pipe_extension(self):
        # LABELED EXTENSION (not on the plate): f1 = v / 4L, odd series.
        self.assertAlmostEqual(ac.closed_pipe_fundamental(0.5), 171.5,
                               places=6)
        series = ac.closed_pipe_harmonics(0.5, 3)
        for got, want in zip(series, [171.5, 514.5, 857.5]):
            self.assertAlmostEqual(got, want, places=6)

    def test_pipe_length_inverts(self):
        length = ac.pipe_length_for(343.0)
        self.assertAlmostEqual(length, 0.5, places=6)
        self.assertAlmostEqual(
            ac.open_pipe_fundamental(ac.pipe_length_for(220.0)), 220.0,
            places=6)


class TestBeatsAndLoudness(unittest.TestCase):
    def test_beats_plate(self):
        # The plate: 440 and 444 Hz pulse 4 times a second.
        self.assertEqual(ac.beats(440.0, 444.0), 4.0)
        self.assertEqual(ac.beats(444.0, 440.0), 4.0)

    def test_intensity_quarter_at_double_distance(self):
        self.assertAlmostEqual(ac.intensity_ratio(1.0, 2.0), 0.25, places=12)

    def test_level_change_plate(self):
        # The plate: double the distance, 6 dB quieter (full precision 6.02).
        self.assertAlmostEqual(ac.level_change_db(1.0, 2.0), -6.0206,
                               delta=0.001)
        # Halving the distance is the same figure, positive.
        self.assertAlmostEqual(ac.level_change_db(2.0, 1.0), 6.0206,
                               delta=0.001)


if __name__ == "__main__":
    unittest.main()
