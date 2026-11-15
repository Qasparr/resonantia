# 93
# ---------------------------------------------------------------------
# test_studio_four_powers.py -- the Four Powers chain, weighed.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XV day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: each power is tested at its own claim. Scire only
# measures (its numbers must match the pipeline's scales on the
# same signal). Velle's EQ must move the band it names and leave
# the others standing; its compressor must reduce what stands
# above the threshold and touch nothing below it. Vapour must
# lower the crest while never raising the peak past full scale,
# and drive 0 must be a perfect pass-through. Tacere's dither
# must be bounded by the 24-bit LSB, deterministic per seed, and
# its headroom must be the ceiling minus the delivered peak.
# The RGBA8888 map must stay inside its bytes. And the spec
# contract must refuse bad orders by naming their fields, while
# an unordered spec stays exactly as flat as it always was.
# ---------------------------------------------------------------------

import math
import unittest

import numpy as np

from resonance.studio import four_powers as fp
from resonance.studio import pipeline

SR = 48000


def _sine(freq, seconds=1.0, amp=0.5):
    t = np.arange(int(SR * seconds)) / SR
    x = amp * np.sin(2.0 * np.pi * freq * t)
    return np.stack([x, x])


class TestNormalize(unittest.TestCase):
    def test_velle_refusals_name_fields(self):
        with self.assertRaises(ValueError) as ctx:
            fp.normalize_velle({"eq": [{"type": "peak", "freq_hz": 1000,
                                        "gain_db": 20.0}]})
        self.assertIn("velle.eq[0].gain_db", str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            fp.normalize_velle({"comp": {"ratio": 40.0}})
        self.assertIn("velle.comp.ratio", str(ctx.exception))
        with self.assertRaises(ValueError):
            fp.normalize_velle({})

    def test_vapour_and_tuning_ranges(self):
        self.assertEqual(fp.normalize_vapour(None), {"drive_db": 0.0})
        with self.assertRaises(ValueError) as ctx:
            fp.normalize_vapour({"drive_db": 30.0})
        self.assertIn("vapour.drive_db", str(ctx.exception))
        self.assertEqual(fp.normalize_tuning_hz(None), 440.0)
        self.assertEqual(fp.normalize_tuning_hz(432), 432.0)
        with self.assertRaises(ValueError) as ctx:
            fp.normalize_tuning_hz(200)
        self.assertIn("tuning_hz", str(ctx.exception))


class TestScire(unittest.TestCase):
    def test_scire_matches_pipeline_scales(self):
        x = _sine(440.0, amp=0.25)
        rep = fp.scire_measure(x, SR, pipeline.measure_loudness_lufs,
                               pipeline.true_peak_dbtp)
        self.assertAlmostEqual(
            rep["lufs_integrated"],
            round(pipeline.measure_loudness_lufs(x, SR), 2), places=1)
        # A steady sine's crest is 3.01 dB.
        self.assertAlmostEqual(rep["crest_db"], 3.01, delta=0.1)


class TestVelleEQ(unittest.TestCase):
    def test_peak_band_moves_its_own_band_only(self):
        velle = fp.normalize_velle(
            {"eq": [{"type": "peak", "freq_hz": 1000.0,
                     "gain_db": 6.0, "q": 1.0}]})
        hot = _sine(1000.0, amp=0.25)
        y, rep = fp.velle_stage(hot, SR, velle)
        self.assertTrue(rep["engaged"])
        self.assertAlmostEqual(rep["rms_delta_db"], 6.0, delta=0.6)
        low = _sine(100.0, amp=0.25)
        _, rep_low = fp.velle_stage(low, SR, velle)
        self.assertLess(abs(rep_low["rms_delta_db"]), 1.5)

    def test_unordered_velle_is_flat_and_confessed(self):
        x = _sine(440.0)
        y, rep = fp.velle_stage(x, SR, None)
        self.assertFalse(rep["engaged"])
        np.testing.assert_array_equal(y, x)


class TestVelleComp(unittest.TestCase):
    def test_comp_reduces_above_threshold_only(self):
        comp = fp.normalize_velle({"comp": {
            "threshold_db": -20.0, "ratio": 4.0, "knee_db": 0.0,
            "attack_ms": 5.0, "release_ms": 100.0,
            "makeup_db": 0.0}})
        loud = _sine(220.0, seconds=2.0, amp=0.9)   # peak ~ -0.9 dBFS
        y, rep = fp.velle_stage(loud, SR, comp)
        self.assertGreater(rep["comp"]["max_gain_reduction_db"], 5.0)
        self.assertLess(float(np.sqrt(np.mean(y ** 2))),
                        float(np.sqrt(np.mean(loud ** 2))))
        quiet = _sine(220.0, seconds=1.0, amp=0.01)  # peak -40 dBFS
        yq, repq = fp.velle_stage(quiet, SR, comp)
        self.assertAlmostEqual(
            repq["comp"]["max_gain_reduction_db"], 0.0, places=2)
        np.testing.assert_allclose(yq, quiet, atol=1e-9)


class TestVapour(unittest.TestCase):
    def test_drive_zero_is_identity(self):
        x = _sine(330.0)
        y, rep = fp.vapour_stage(x, {"drive_db": 0.0})
        self.assertFalse(rep["engaged"])
        np.testing.assert_array_equal(y, x)

    def test_saturation_lowers_crest_never_raises_peak(self):
        x = _sine(330.0, amp=0.9)
        y, rep = fp.vapour_stage(x, {"drive_db": 12.0})
        self.assertTrue(rep["engaged"])
        self.assertLess(rep["crest_after_db"], rep["crest_before_db"])
        self.assertLessEqual(float(np.max(np.abs(y))), 1.0)


class TestTacere(unittest.TestCase):
    def test_dither_bounded_and_deterministic(self):
        x = _sine(440.0, amp=0.1)
        a = fp.tpdf_dither(x, seed=93)
        b = fp.tpdf_dither(x, seed=93)
        np.testing.assert_array_equal(a, b)
        lsb = 2.0 ** -23
        self.assertLessEqual(float(np.max(np.abs(a - x))), lsb * 1.01)
        self.assertAlmostEqual(float(np.mean(a - x)), 0.0, delta=lsb)

    def test_headroom_is_ceiling_minus_peak(self):
        master = {"ceiling_dbtp": -1.0, "true_peak_dbtp": -1.13,
                  "target_lufs": -14.0, "gain_applied_db": 3.0,
                  "trim_db": -0.5, "lufs_after": -14.2,
                  "ceiling_overrode_loudness": True}
        tac = fp.tacere_report(master, True)
        self.assertAlmostEqual(tac["headroom_dbtp"], 0.13, places=2)
        self.assertTrue(tac["dither"]["applied"])


class TestRGBA(unittest.TestCase):
    def test_map_stays_in_bytes_and_hex(self):
        scire = {"lufs_integrated": -14.0, "crest_db": 9.0}
        master = {"true_peak_dbtp": -1.0}
        tac = {"headroom_dbtp": 0.13}
        m = fp.rgba8888_map(scire, master, tac)
        for key in ("R_know_scire", "G_dare_audere", "B_will_velle",
                    "A_silent_vapour_tacere"):
            self.assertTrue(0 <= m[key] <= 255)
        self.assertEqual(len(m["hex"]), 9)
        self.assertTrue(m["hex"].startswith("#"))


class TestSpecIntegration(unittest.TestCase):
    BASE = {"prompt_base": "dark boom bap instrumental",
            "sections": [{"name": "a", "seconds": 5}],
            "out_dir": "studio-runs/four-powers-test"}

    def test_defaults_keep_the_old_spec_flat(self):
        spec = pipeline.validate_spec(dict(self.BASE))
        self.assertNotIn("velle", spec)
        self.assertEqual(spec["vapour"], {"drive_db": 0.0})
        self.assertEqual(spec["tuning_hz"], 440.0)
        self.assertTrue(spec["master"]["dither"])

    def test_full_order_normalizes(self):
        raw = dict(self.BASE)
        raw["velle"] = {"eq": [{"type": "lowshelf", "freq_hz": 120.0,
                                "gain_db": 2.0}],
                        "comp": {"threshold_db": -16.0, "ratio": 3.0}}
        raw["vapour"] = {"drive_db": 6.0}
        raw["tuning_hz"] = 432.0
        raw["master"] = {"dither": False}
        spec = pipeline.validate_spec(raw)
        self.assertEqual(spec["velle"]["comp"]["ratio"], 3.0)
        self.assertEqual(spec["vapour"]["drive_db"], 6.0)
        self.assertEqual(spec["tuning_hz"], 432.0)
        self.assertFalse(spec["master"]["dither"])

    def test_dry_run_manifest_carries_the_plan(self):
        raw = dict(self.BASE)
        raw["vapour"] = {"drive_db": 3.0}
        manifest = pipeline.produce(raw, dry_run=True)
        planned = manifest["planned"]
        self.assertEqual(planned["four_powers"]["vapour_drive_db"], 3.0)
        self.assertEqual(planned["tuning_hz"], 440.0)


class TestArpeggioTuning(unittest.TestCase):
    def _render(self, tuning):
        from resonance.studio import arpeggio as arp
        from resonance.studio import spine as spine_mod
        sp = spine_mod.normalize_spine_spec({
            "bpm": 93, "root_midi": 29,
            "sections": [{"name": "hook", "bars": 2,
                          "density": "full"}]})
        a = arp.normalize_arpeggio_spec({}, default_seed=93,
                                        tuning_hz=tuning)
        layer, rep = arp.render_arpeggio(a, sp, SR)
        return layer, rep

    def test_432_flattens_the_dancer(self):
        l440, r440 = self._render(440.0)
        l432, r432 = self._render(432.0)
        self.assertEqual(r440["tuning_cents"], 0.0)
        self.assertAlmostEqual(r432["tuning_cents"], -31.8, delta=0.2)
        self.assertFalse(np.allclose(l440, l432))

    def test_440_is_the_standing_render(self):
        from resonance.studio import arpeggio as arp
        a = arp.normalize_arpeggio_spec({}, default_seed=93)
        self.assertEqual(a["tuning_hz"], 440.0)
        self.assertEqual(a["tuning_cents"], 0.0)


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
