# 93
# ---------------------------------------------------------------------
# test_studio_kit.py -- the rendered kit and the sampled spine.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
#
# DOCTRINE under test (Proof No. 3, the founder's verdict law):
#   * one-shot takes are selected by MEASUREMENT (single onset,
#     clean decay, no tonal residue, the 808 in pitch) -- the
#     scales in resonance.studio.kit, weighed here on synthetic
#     fixtures whose truth is known by construction;
#   * a spine spec that names samples renders SAMPLES ONLY -- a
#     hole in the kit is a refusal, never a fallback to synthesis;
#   * the grid closes at the production's own numbers: 140 BPM,
#     96 bars, exact samples.
# ---------------------------------------------------------------------

import math
import os
import tempfile
import unittest
import wave

import numpy as np

from resonance import grid
from resonance.studio import kit as kit_mod
from resonance.studio import spine

SR32 = 32000
SR48 = 48000


def _noise_burst(sr, dur_s, tau=0.08, seed=7):
    rng = np.random.default_rng(seed)
    n = int(dur_s * sr)
    t = np.arange(n) / sr
    return rng.standard_normal(n) * np.exp(-t / tau) * 0.9


def _place(take, hit, at_s, sr):
    at = int(at_s * sr)
    end = min(take.size, at + hit.size)
    take[at:end] += hit[:end - at]
    return take


def _write_wav16(path, arr, sr):
    pcm = np.clip(np.asarray(arr) * 32767, -32768, 32767) \
        .astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


class MeasureTakeTests(unittest.TestCase):
    def test_clean_noise_hit_measures_clean(self):
        take = np.zeros(3 * SR32)
        _place(take, _noise_burst(SR32, 0.6), 0.3, SR32)
        m = kit_mod.measure_take(take, SR32, "kick")
        self.assertEqual(m["hit_regions"], 1)
        self.assertTrue(m["clean_single"], m)
        self.assertLessEqual(m["tail_rms_db_rel_peak"], -32.0)

    def test_two_hits_are_not_a_single_but_are_trimmable(self):
        take = np.zeros(3 * SR32)
        hit = _noise_burst(SR32, 0.6)
        _place(take, hit, 0.3, SR32)
        _place(take, hit, 1.8, SR32)
        m = kit_mod.measure_take(take, SR32, "kick")
        self.assertEqual(m["hit_regions"], 2)
        self.assertFalse(m["clean_single"])
        self.assertTrue(m["trimmable"])

    def test_sustained_tonal_tail_convicts_the_take(self):
        take = np.zeros(3 * SR32)
        _place(take, _noise_burst(SR32, 0.6), 0.3, SR32)
        t = np.arange(3 * SR32) / SR32
        take += 0.15 * np.sin(2 * np.pi * 440.0 * t) \
            * (t >= 0.3)
        m = kit_mod.measure_take(take, SR32, "snare")
        self.assertFalse(m["clean_single"], m)

    def test_short_hat_still_gets_a_tonality(self):
        take = np.zeros(3 * SR32)
        _place(take, _noise_burst(SR32, 0.25, tau=0.02), 0.2, SR32)
        m = kit_mod.measure_take(take, SR32, "closed_hat")
        self.assertIsNotNone(m["tonality"])
        self.assertTrue(m["clean_single"], m)

    def test_bass_pitch_measured_against_the_root(self):
        from resonance.core.notes import midi_to_freq
        for cents_true, expect_clean in ((0.0, True),
                                         (200.0, False)):
            f = midi_to_freq(29) * 2 ** (cents_true / 1200.0)
            n = 4 * SR32
            t = np.arange(n) / SR32
            take = np.zeros(n)
            hit = np.sin(2 * np.pi * f * t[:2 * SR32]) \
                * np.exp(-t[:2 * SR32] / 0.5) * 0.9
            _place(take, hit, 0.2, SR32)
            m = kit_mod.measure_take(take, SR32, "bass808",
                                     target_midi=29)
            self.assertAlmostEqual(m["cents_from_target"],
                                   cents_true, delta=25.0)
            self.assertEqual(m["clean_single"], expect_clean, m)


    def test_never_decaying_wash_is_not_clean(self):
        # The first build's hole: a take that is one unbroken
        # texture has one region and no tail to measure, and the
        # old gates called it clean. It never decays -- convict it.
        rng = np.random.default_rng(3)
        take = rng.standard_normal(3 * SR32) * 0.5
        m = kit_mod.measure_take(take, SR32, "clap")
        self.assertEqual(m["hit_regions"], 1)
        self.assertFalse(m["decayed_within_take"], m)
        self.assertGreater(m["sustain_db"], -20.0, m)
        self.assertFalse(m["clean_single"], m)

    def test_loop_cut_flag_and_cut_holds_one_hit(self):
        take = np.zeros(3 * SR32)
        hit = _noise_burst(SR32, 0.6)
        _place(take, hit, 0.3, SR32)
        _place(take, hit, 1.6, SR32)
        m = kit_mod.measure_take(take, SR32, "kick")
        self.assertTrue(m["loop_cut"], m)
        # Hand the cutter a decay that would overrun the next
        # onset: the cut must stop short of the second strike.
        m2 = dict(m)
        m2["decay_end_s"] = m["next_onset_s"] - 0.02
        cut = kit_mod.cut_hit(take, SR32, m2)
        self.assertLess(cut.size / SR32,
                        m["next_onset_s"] - 0.29)
        tail = cut[int(1.0 * SR32):]
        self.assertLess(float(np.sqrt(np.mean(tail ** 2))), 0.02)


class BassDerivationTests(unittest.TestCase):
    def _rec(self, file, hz, tail, regions=1, decayed=True):
        return {"file": file, "seed": 1, "prompt": "x",
                "metrics": {"fundamental_hz": hz,
                            "hit_regions": regions,
                            "decayed_within_take": decayed,
                            "tail_rms_db_rel_peak": tail}}

    def test_source_is_the_best_measured_take_not_the_prompt(self):
        all_metrics = {
            "bass29": [self._rec("bass29_t3.wav", 39.23, -120.0,
                                 decayed=False)],
            "bass37": [self._rec("bass37_t2.wav", 44.55, -57.61),
                       self._rec("bass37_t3.wav", 61.36, -63.56)],
            "bass39": [self._rec("bass39_t2.wav", 49.12, -120.0,
                                 decayed=False)],
        }
        src = kit_mod.pick_bass_source(all_metrics)
        self.assertEqual(src["file"], "bass37_t2.wav")
        self.assertAlmostEqual(src["exact_midi"], 29.0, delta=0.6)

    def test_exact_shift_lands_the_root_on_pitch(self):
        from resonance.core.notes import midi_to_freq
        sr = SR32
        t = np.arange(3 * sr) / sr
        hit = np.sin(2 * np.pi * 44.55 * t) \
            * np.exp(-t / 1.0) * 0.9
        exact = kit_mod.exact_midi_of_hz(44.55)
        for target in (29, 32, 37, 39):
            shifted = kit_mod._rate_shift(hit, target - exact)
            hz, cents = kit_mod._fundamental_cents(
                shifted, sr, target)
            self.assertAlmostEqual(hz, midi_to_freq(target),
                                   delta=1.5)
            self.assertLess(abs(cents), 25.0)


class ScoreAndUsabilityTests(unittest.TestCase):
    def _drum_metrics(self, tail, sustain, tonality):
        return {"clean_single": False, "trimmable": False,
                "loop_cut": False, "hit_regions": 1,
                "tail_rms_db_rel_peak": tail,
                "sustain_db": sustain, "tonality": tonality,
                "cents_from_target": None, "hit_length_s": 2.9,
                "decayed_within_take": False}

    def test_drum_shape_outranks_tonality(self):
        # The open-hat lesson: a decaying strike with a slightly
        # worse spectrum beats a never-falling swell.
        swell = self._drum_metrics(-15.0, -6.0, 0.15)
        strike = self._drum_metrics(-30.0, -25.0, 0.22)
        self.assertLess(kit_mod._take_score(strike),
                        kit_mod._take_score(swell))

    def test_usability_bar(self):
        clean = dict(self._drum_metrics(-60.0, -40.0, 0.2),
                     clean_single=True)
        self.assertTrue(kit_mod._voice_usable(clean))
        loop = dict(self._drum_metrics(-30.0, -30.0, 0.2),
                    loop_cut=True)
        self.assertTrue(kit_mod._voice_usable(loop))
        swell = self._drum_metrics(-11.0, -13.0, 0.68)
        self.assertFalse(kit_mod._voice_usable(swell))
        self.assertFalse(kit_mod._voice_usable(None))


class SelectionTests(unittest.TestCase):
    def test_clean_take_beats_looped_take(self):
        with tempfile.TemporaryDirectory() as td:
            clean = np.zeros(3 * SR32)
            _place(clean, _noise_burst(SR32, 0.6), 0.3, SR32)
            looped = np.zeros(3 * SR32)
            hit = _noise_burst(SR32, 0.6)
            _place(looped, hit, 0.3, SR32)
            _place(looped, hit, 1.8, SR32)
            _write_wav16(os.path.join(td, "kick_t0.wav"), looped,
                         SR32)
            _write_wav16(os.path.join(td, "kick_t1.wav"), clean,
                         SR32)
            plan = [
                {"voice": "kick", "file": "kick_t0.wav", "seed": 1,
                 "prompt": "x", "target_midi": None},
                {"voice": "kick", "file": "kick_t1.wav", "seed": 2,
                 "prompt": "x", "target_midi": None},
            ]
            selection, _ = kit_mod.select_kit(td, plan)
            self.assertEqual(selection["kick"]["file"],
                             "kick_t1.wav")
            self.assertEqual(selection["kick"]["basis"],
                             "clean single hit")


def _tiny_kit(sr=SR48, marker_len=64):
    """An in-memory kit of marker impulses: content known exactly."""
    def mark(value):
        arr = np.zeros(marker_len)
        arr[0] = value
        return arr
    voices = {name: mark(0.3) for name in spine.KIT_VOICES}
    voices["kick"] = mark(0.6)
    bass = {midi: mark(0.15) for midi in (29, 32, 37, 39)}
    return {"voices": voices, "bass": bass}


def _spec(sections, samples=None, bpm=140.0):
    raw = {"bpm": bpm, "swing": 0.0, "root_midi": 29,
           "sections": sections}
    if samples is not None:
        raw["samples"] = samples
    return spine.normalize_spine_spec(raw)


class SampledSpineTests(unittest.TestCase):
    def test_samples_land_on_the_grid_unsynthesized(self):
        samples = {v: f"{v}.wav" for v in spine.KIT_VOICES}
        samples["bass808"] = {str(m): f"b{m}.wav"
                              for m in (29, 32, 37, 39)}
        sp = _spec([{"name": "intro", "bars": 2,
                     "density": "sparse"}], samples=samples)
        # Normalization records the paths; rendering from an
        # in-memory kit loads no files and synthesizes nothing.
        arr = spine.render_spine(sp, SR48, pan_fn=lambda v, p: 0.0,
                                 kit=_tiny_kit())
        n = spine.spine_samples(sp, SR48)
        self.assertEqual(arr.shape, (2, n))
        # Sparse bar 1: kick (vel .95) + closed hat (vel .45) on
        # step 0, bass marker under both -- all centered. (Marker
        # values keep the stack under 1.0, so the spine's peak
        # normalization stays out of this weighing.)
        self.assertAlmostEqual(arr[0, 0], 0.95 * 0.6 + 0.45 * 0.3
                               + 0.15, places=6)

    def test_incomplete_kit_refuses_never_falls_back(self):
        sp = _spec([{"name": "x", "bars": 1, "density": "sparse"}])
        broken = _tiny_kit()
        del broken["voices"]["rimshot"]
        with self.assertRaises(ValueError) as ctx:
            spine.render_spine(sp, SR48, kit=broken)
        self.assertIn("rimshot", str(ctx.exception))

    def test_synth_voices_are_never_consulted_in_sampled_mode(self):
        sp = _spec([{"name": "x", "bars": 1, "density": "full"}])
        saved = spine.VOICES
        try:
            spine.VOICES = {}
            arr = spine.render_spine(sp, SR48, kit=_tiny_kit())
            self.assertEqual(arr.shape[1],
                             spine.spine_samples(sp, SR48))
            with self.assertRaises(Exception):
                spine.render_spine(sp, SR48)  # no kit: synth road
        finally:
            spine.VOICES = saved

    def test_missing_voice_path_refused_at_validation(self):
        samples = {v: f"{v}.wav" for v in spine.KIT_VOICES}
        del samples["snare"]
        samples["bass808"] = {str(m): f"b{m}.wav"
                              for m in (29, 32, 37, 39)}
        with self.assertRaises(ValueError) as ctx:
            _spec([{"name": "x", "bars": 1, "density": "sparse"}],
                  samples=samples)
        self.assertIn("spine.samples.snare", str(ctx.exception))

    def test_missing_chord_root_refused_at_validation(self):
        samples = {v: f"{v}.wav" for v in spine.KIT_VOICES}
        samples["bass808"] = {str(m): f"b{m}.wav"
                              for m in (29, 32, 39)}  # 37 missing
        with self.assertRaises(ValueError) as ctx:
            _spec([{"name": "x", "bars": 1, "density": "sparse"}],
                  samples=samples)
        self.assertIn("37", str(ctx.exception))

    def test_load_kit_roundtrip_and_rate_refusal(self):
        with tempfile.TemporaryDirectory() as td:
            samples = {}
            for v in spine.KIT_VOICES:
                p = os.path.join(td, f"{v}.wav")
                _write_wav16(p, _noise_burst(SR48, 0.2), SR48)
                samples[v] = p
            samples["bass808"] = {}
            for midi in (29, 32, 37, 39):
                p = os.path.join(td, f"bass{midi}.wav")
                _write_wav16(p, _noise_burst(SR48, 0.4), SR48)
                samples["bass808"][str(midi)] = p
            kit = spine.load_kit(samples, SR48)
            self.assertEqual(set(kit["bass"]), {29, 32, 37, 39})
            self.assertTrue(all(kit["voices"][v].size > 0
                                for v in spine.KIT_VOICES))
            bad = dict(samples)
            p = os.path.join(td, "wrong_rate.wav")
            _write_wav16(p, _noise_burst(22050, 0.2), 22050)
            bad["kick"] = p
            with self.assertRaises(ValueError) as ctx:
                spine.load_kit(bad, SR48)
            self.assertIn("spine.samples.kick", str(ctx.exception))
            gone = dict(samples)
            gone["snare"] = os.path.join(td, "not_there.wav")
            with self.assertRaises(ValueError):
                spine.load_kit(gone, SR48)


class GridCloseTests(unittest.TestCase):
    SECTIONS = [
        {"name": "intro", "bars": 8, "density": "sparse"},
        {"name": "hook", "bars": 8, "density": "full"},
        {"name": "verse1", "bars": 16, "density": "driving"},
        {"name": "hook", "bars": 8, "density": "full"},
        {"name": "feature", "bars": 16, "density": "open"},
        {"name": "hook", "bars": 8, "density": "full"},
        {"name": "verse2", "bars": 16, "density": "driving"},
        {"name": "hook_out", "bars": 8, "density": "full"},
        {"name": "outro", "bars": 8, "density": "sparse"},
    ]

    def test_grid_closes_at_140_bpm_96_bars(self):
        sp = _spec(self.SECTIONS)
        self.assertEqual(spine.total_bars(sp), 96)
        exact = grid.bars_to_samples(96, 140.0, SR48, 4)
        self.assertEqual(spine.spine_samples(sp, SR48), exact)
        arr = spine.render_spine(sp, SR48, kit=_tiny_kit())
        self.assertEqual(arr.shape, (2, exact))
        self.assertAlmostEqual(exact / SR48, 96 * 4 * 60 / 140,
                               delta=1.0 / SR48)


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
