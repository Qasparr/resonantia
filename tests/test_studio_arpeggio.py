# 93
# ---------------------------------------------------------------------
# test_studio_arpeggio.py -- the dancer, weighed; the motif, checked.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VIII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: what is weighed here: the composed layer is
# DETERMINISTIC (same spec, same render, to the bit); its notes are
# ONLY the documented solfeggio staff approximations; the layer is
# exactly as long as the grid it dances on, at the founder's new
# tempo (137 BPM, 120 bars closed by resonance.grid's arithmetic);
# the humanized contour bends without transposing; the motif rides
# verbatim in every prompt the mill would speak; and the contract
# refuses its nonsense by name (arpeggio without a spine, a level
# above parity, a fractional crossfade). The bridge is never
# touched: composition and scales only.
# ---------------------------------------------------------------------

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance import grid  # noqa: E402
from resonance.studio import arpeggio, pipeline, spine  # noqa: E402

SR = 48000
MOTIF = ("the same repeating four-note F minor piano motif "
         "(F, A-flat, C, A-flat)")
LADDER_MIDIS = {67, 68, 72, 75, 78, 80}


def _small_spine(bpm=137.0):
    return spine.normalize_spine_spec({
        "bpm": bpm, "swing": 0.12, "root_midi": 29,
        "sections": [
            {"name": "intro", "bars": 2, "density": "sparse"},
            {"name": "hook", "bars": 2, "density": "full"},
            {"name": "verse1", "bars": 2, "density": "driving"},
            {"name": "verse3", "bars": 2, "density": "driving"},
            {"name": "outro", "bars": 2, "density": "sparse"},
        ]})


class FigureTests(unittest.TestCase):
    def test_cell_is_the_proven_road_figure(self):
        # The 20 notes of the Proven Road sheet, as ladder indices:
        # G | ^G | c _e | ^f ^g G | ^G c _e ^f ^g | G ^G c _e ^f ^g G ^G
        self.assertEqual(
            arpeggio.figure_cell(),
            [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5,
             0, 1, 2, 3, 4, 5, 0, 1])
        self.assertEqual(arpeggio.FIBONACCI_PHRASES, (1, 1, 2, 3, 5, 8))

    def test_ladder_offsets_documented(self):
        inv = {r["syllable"]: r for r in arpeggio.ladder_inventory()}
        self.assertEqual(inv["UT"]["carrier_hz"], 396.0)
        self.assertAlmostEqual(inv["UT"]["cents_offset"], 17.6, delta=0.6)
        # FA is the ladder's wide step: ~+46 cents from Eb5.
        self.assertAlmostEqual(inv["FA"]["cents_offset"], 46.0, delta=1.0)
        self.assertEqual(inv["SOL"]["midi"], 78)


class CompositionTests(unittest.TestCase):
    def test_notes_stay_on_the_ladder(self):
        events, modes = arpeggio.compose_events(_small_spine()["sections"])
        self.assertTrue(events)
        self.assertEqual({e["midi"] for e in events} - LADDER_MIDIS,
                         set())
        self.assertEqual(modes, ["statement", "runs", "bariolage",
                                 "bariolage16", "statement_fade"])

    def test_third_verse_takes_the_dense_bariolage(self):
        _, modes = arpeggio.compose_events(_small_spine()["sections"])
        self.assertEqual(modes[3], "bariolage16")

    def test_mode_override_outranks_the_map(self):
        events, modes = arpeggio.compose_events(
            _small_spine()["sections"], overrides={1: "mute"})
        self.assertEqual(modes[1], "mute")
        self.assertFalse([e for e in events if e["section"] == 1])


class RenderTests(unittest.TestCase):
    def test_deterministic_and_grid_long(self):
        sp = _small_spine()
        arp = arpeggio.normalize_arpeggio_spec({}, default_seed=93)
        layer1, rep1 = arpeggio.render_arpeggio(arp, sp, SR)
        layer2, _ = arpeggio.render_arpeggio(arp, sp, SR)
        self.assertTrue(np.array_equal(layer1, layer2))
        self.assertEqual(layer1.shape,
                         (2, spine.spine_samples(sp, SR)))
        self.assertGreater(rep1["total_notes"], 100)
        self.assertTrue(np.all(np.isfinite(layer1)))
        self.assertGreater(float(np.max(np.abs(layer1))), 0.05)

    def test_grid_closes_at_137_for_120_bars(self):
        # The v3 schedule's arithmetic: 120 bars at 137 BPM, one
        # rounding at the total, and the layer would be that long.
        self.assertEqual(grid.bars_to_samples(120, 137.0, SR),
                         int(round(120 * 4 * 60 * SR / 137.0)))
        sp = spine.normalize_spine_spec({
            "bpm": 137.0, "sections": [
                {"name": n, "bars": b, "density": d} for n, b, d in [
                    ("intro", 8, "sparse"), ("hook", 8, "full"),
                    ("verse1", 16, "driving"), ("hook", 8, "full"),
                    ("feature", 16, "open"), ("hook", 8, "full"),
                    ("verse2", 16, "driving"), ("hook", 8, "full"),
                    ("verse3", 16, "driving"), ("hook_out", 8, "full"),
                    ("outro", 8, "sparse")]]})
        self.assertEqual(spine.total_bars(sp), 120)
        self.assertEqual(spine.spine_samples(sp, SR),
                         grid.bars_to_samples(120, 137.0, SR))

    def test_humanizer_bends_without_transposing(self):
        # A flat contour through humanize_contour gains fine
        # structure but keeps its median pitch (vocal.py's law:
        # drift redistributes, never transposes).
        from resonance.vocal import humanize_contour
        f0 = np.full(400, 440.0)
        out = humanize_contour(f0, 256 / SR, strength=1.0, seed=93)
        cents = 1200 * np.log2(out / 440.0)
        self.assertGreater(float(np.std(cents)), 1.0)
        self.assertLess(abs(float(np.median(cents))), 6.0)


class ContractTests(unittest.TestCase):
    def _spec(self, **extra):
        spec = {
            "title": "T", "prompt_base": "base",
            "sections": [{"name": "a", "seconds": 10},
                         {"name": "b", "seconds": 10}],
            "spine": {"bpm": 137.0, "sections": [
                {"name": "hook", "bars": 8, "density": "full"}]},
            "out_dir": "/tmp/studio-arpeggio-test",
        }
        spec.update(extra)
        return spec

    def test_motif_rides_every_prompt(self):
        spec = pipeline.validate_spec(self._spec(motif=MOTIF))
        for sec in spec["sections"]:
            self.assertIn(MOTIF, pipeline._full_prompt(spec, sec))
        manifest = pipeline.produce(spec, dry_run=True)
        for planned in manifest["planned"]["sections"]:
            self.assertIn(MOTIF, planned["prompt"])

    def test_no_motif_keeps_legacy_prompts(self):
        spec = pipeline.validate_spec(self._spec())
        self.assertEqual(pipeline._full_prompt(spec, spec["sections"][0]),
                         "base")

    def test_arpeggio_requires_spine(self):
        spec = self._spec(arpeggio={"level_db": -9.0})
        del spec["spine"]
        with self.assertRaises(ValueError) as ctx:
            pipeline.validate_spec(spec)
        self.assertIn("arpeggio", str(ctx.exception))

    def test_arpeggio_level_refused_above_parity(self):
        with self.assertRaises(ValueError) as ctx:
            pipeline.validate_spec(self._spec(arpeggio={"level_db": 2.0}))
        self.assertIn("arpeggio.level_db", str(ctx.exception))

    def test_crossfade_bars_closes_on_the_grid(self):
        spec = pipeline.validate_spec(self._spec(crossfade_bars=2))
        self.assertEqual(
            pipeline._crossfade_samples(spec),
            grid.bars_to_samples(2, 137.0, SR))
        plain = pipeline.validate_spec(self._spec())
        self.assertEqual(pipeline._crossfade_samples(plain),
                         int(pipeline.CROSSFADE_S * SR))

    def test_fractional_crossfade_refused(self):
        with self.assertRaises(ValueError) as ctx:
            pipeline.validate_spec(self._spec(crossfade_bars=1.5))
        self.assertIn("crossfade_bars", str(ctx.exception))

    def test_chained_normalizes_and_plans(self):
        spec = pipeline.validate_spec(
            self._spec(chained=True, continue_seconds=5.0))
        self.assertTrue(spec["chained"])
        self.assertEqual(spec["continue_seconds"], 5.0)
        manifest = pipeline.produce(spec, dry_run=True)
        self.assertTrue(manifest["planned"]["chained"])
        self.assertEqual(manifest["planned"]["continue_seconds"], 5.0)

    def test_chained_defaults_five_seconds(self):
        spec = pipeline.validate_spec(self._spec(chained=True))
        self.assertEqual(spec["continue_seconds"], 5.0)

    def test_continue_seconds_range_refused(self):
        with self.assertRaises(ValueError) as ctx:
            pipeline.validate_spec(
                self._spec(chained=True, continue_seconds=30.0))
        self.assertIn("continue_seconds", str(ctx.exception))

    def test_unchained_spec_carries_no_chain(self):
        spec = pipeline.validate_spec(self._spec())
        self.assertNotIn("chained", spec)
        manifest = pipeline.produce(spec, dry_run=True)
        self.assertFalse(manifest["planned"]["chained"])


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
