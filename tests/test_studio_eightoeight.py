# 93
# ---------------------------------------------------------------------
# test_studio_eightoeight.py -- the 808 Synthesizer Toolbox,
# weighed by measurement.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: nothing here listens. The kick's pitch track is read
# by autocorrelation at both ends (attack inside its sweep band,
# tail on its fundamental within tolerance); the decay law is
# weighed at its own constant (env(tau) == e^-1); the hat's energy
# is weighed where the recipe puts it (above the high-pass); the
# cowbell's two squares are found in the spectrum at their seats;
# the clap's burst train is counted in its envelope; the dial
# placement rule is weighed seat by seat against the dial's own
# data. Measurements, not vibes -- a voice that misses its recipe
# fails here before it ever reaches an ear.
# ---------------------------------------------------------------------

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance.studio import eightoeight as e8  # noqa: E402


def _band_energy(buf, sr, lo, hi):
    """Fraction of a buffer's spectral energy inside [lo, hi) Hz."""
    spec = np.abs(np.fft.rfft(buf)) ** 2
    freqs = np.fft.rfftfreq(len(buf), 1.0 / sr)
    total = spec.sum()
    if total == 0:
        return 0.0
    return float(spec[(freqs >= lo) & (freqs < hi)].sum() / total)


class TestDecayLaw(unittest.TestCase):
    """The envelope is a stated exponential, weighed at its tau."""

    def test_env_at_tau_is_e_inverse(self):
        import math
        self.assertAlmostEqual(float(e8.exp_decay(0.137, 0.137)),
                               math.exp(-1.0), places=12)

    def test_env_at_zero_is_one(self):
        self.assertEqual(float(e8.exp_decay(0.0, 0.05)), 1.0)


class TestKickTrack(unittest.TestCase):
    """The kick: struck sharp, settling to its fundamental."""

    def test_attack_inside_sweep_band_tail_on_fundamental(self):
        buf = e8.kick(fundamental=50.0, sweep_start=160.0, click=0.0,
                      drive=0.0)
        track = e8.kick_track(buf)
        attack = track["attack_hz_window_20ms"]
        tail = track["tail_hz_last_250ms"]
        self.assertIsNotNone(attack)
        self.assertIsNotNone(tail)
        # The attack window averages the sweep: well above the
        # fundamental, below the struck pitch.
        self.assertGreater(attack, 50.0 + 0.30 * (160.0 - 50.0))
        self.assertLess(attack, 160.0)
        # The tail has settled: on the fundamental, +-3 Hz.
        self.assertAlmostEqual(tail, 50.0, delta=3.0)

    def test_tail_follows_the_fundamental_argument(self):
        buf = e8.kick(fundamental=64.0, sweep_start=180.0, click=0.0,
                      drive=0.0)
        tail = e8.kick_track(buf)["tail_hz_last_250ms"]
        self.assertAlmostEqual(tail, 64.0, delta=3.0)

    def test_kick_decays(self):
        buf = e8.kick(click=0.0, drive=0.0)
        sr = e8.SR
        head = float(np.sqrt(np.mean(buf[:sr // 10] ** 2)))
        tail = float(np.sqrt(np.mean(buf[-sr // 10:] ** 2)))
        self.assertGreater(head, 3.0 * tail)


class TestDialPlacement(unittest.TestCase):
    """The placement rule, seat by seat."""

    def test_rule_cases(self):
        # (seat, placed, shifts): drops negative, lifts positive.
        self.assertEqual(e8.place_seat(176.0), (44.0, -2))   # VV
        self.assertEqual(e8.place_seat(120.0), (60.0, -1))   # OO
        self.assertEqual(e8.place_seat(192.0), (48.0, -2))   # LL
        self.assertEqual(e8.place_seat(60.0), (60.0, 0))
        self.assertEqual(e8.place_seat(45.0), (45.0, 0))
        self.assertEqual(e8.place_seat(25.0), (50.0, 1))
        self.assertEqual(e8.place_seat(432.0), (54.0, -3))

    def test_every_dial_seat_places_into_the_band(self):
        for pair in ("AA", "EE", "II", "OO", "VV", "XX", "ZZ"):
            d = e8.fundamental_for_pair(pair)
            self.assertGreaterEqual(d["placed_hz"], 30.0)
            self.assertLessEqual(d["placed_hz"], 60.0)
            self.assertEqual(d["pair"], pair)

    def test_vv_derivation_is_the_founders_seat(self):
        d = e8.fundamental_for_pair("VV")
        self.assertEqual(d["seat_hz"], 176.0)
        self.assertEqual(d["placed_hz"], 44.0)
        self.assertEqual(d["ordinal"], 44)

    def test_dial_tuned_kick_tail_lands_on_the_seat(self):
        buf = e8.kick(tune="VV", click=0.0, drive=0.0)
        tail = e8.kick_track(buf)["tail_hz_last_250ms"]
        self.assertAlmostEqual(tail, 44.0, delta=3.0)


class TestMetallicVoices(unittest.TestCase):
    """Hat and cowbell: the energy lives where the recipe puts it."""

    def test_closed_hat_energy_above_the_highpass(self):
        buf = e8.hihat(open_=False)
        frac = _band_energy(buf, e8.SR, 6000.0, 20000.0)
        self.assertGreater(frac, 0.75)

    def test_open_hat_rings_longer_than_closed(self):
        sr = e8.SR
        closed = e8.hihat(open_=False, seconds=1.2)
        opened = e8.hihat(open_=True, seconds=1.2)
        late = slice(int(0.5 * sr), int(0.7 * sr))
        rms_c = float(np.sqrt(np.mean(closed[late] ** 2)))
        rms_o = float(np.sqrt(np.mean(opened[late] ** 2)))
        self.assertGreater(rms_o, 5.0 * rms_c)

    def test_cowbell_squares_at_their_seats(self):
        buf = e8.cowbell()
        head = buf[:int(0.05 * e8.SR)]
        spec = np.abs(np.fft.rfft(head))
        freqs = np.fft.rfftfreq(len(head), 1.0 / e8.SR)
        for seat in (540.0, 845.0):
            band = (freqs > seat - 40) & (freqs < seat + 40)
            local = float(spec[band].max())
            self.assertGreater(local, 0.25 * float(spec.max()))


class TestNoiseVoices(unittest.TestCase):
    """Snare and clap: two bodies, and a counted burst train."""

    def test_snare_has_tone_and_noise(self):
        buf = e8.snare()
        # Tone: energy near 190 Hz in the first 30 ms.
        head = buf[:int(0.03 * e8.SR)]
        self.assertGreater(
            _band_energy(head, e8.SR, 150.0, 240.0), 0.05)
        # Noise: the snap body, weighed where the recipe puts it
        # -- the band-pass sits at 1800 Hz, so the noise's energy
        # concentrates in 1.2-9 kHz (measured 0.196 of the whole).
        self.assertGreater(
            _band_energy(buf, e8.SR, 1200.0, 9000.0), 0.15)

    def test_clap_envelope_counts_its_bursts(self):
        buf = e8.clap()
        sr = e8.SR
        # A coarse envelope: windowed peak amplitude, 2 ms windows.
        win = sr // 500
        n = (len(buf) // win) * win
        env = np.abs(buf[:n]).reshape(-1, win).max(axis=1)
        head = env[:int(0.060 * sr) // win]
        peaks = sum(1 for i in range(1, len(head) - 1)
                    if head[i] > head[i - 1] and head[i] >= head[i + 1]
                    and head[i] > 0.2 * head.max())
        self.assertGreaterEqual(peaks, 3)


class TestRegistryAndDeterminism(unittest.TestCase):
    """Every registered voice strikes; a seed re-strikes identically."""

    def test_all_voices_render_finite_and_audible(self):
        for name in e8.VOICES:
            buf, _ = e8.render_voice(name)
            self.assertTrue(np.all(np.isfinite(buf)), name)
            self.assertGreater(float(np.max(np.abs(buf))), 0.05, name)

    def test_seeded_noise_is_reproducible(self):
        a, _ = e8.render_voice("snare")
        b, _ = e8.render_voice("snare")
        self.assertTrue(np.array_equal(a, b))

    def test_tom_seats_rise(self):
        tails = []
        for seat in ("low", "mid", "high"):
            buf = e8.tom(seat=seat)
            est = e8.estimate_fundamental(
                buf, e8.SR, 0.15, 0.45, fmin=50.0, fmax=400.0)
            tails.append(est)
        self.assertLess(tails[0], tails[1])
        self.assertLess(tails[1], tails[2])


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
