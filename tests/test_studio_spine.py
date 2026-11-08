# 93
# ---------------------------------------------------------------------
# test_studio_spine.py -- the spine, weighed on the grid it claims.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VIII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: what is weighed here is the spine's whole promise --
# that the house engine's drums live on resonance.grid's arithmetic
# exactly: the total length is bars_to_samples and not a sample more,
# kick onsets land on the computed step offsets, the 808 bass holds
# the F-minor root it was told to hold, and bad spine specs are
# refused by name. Plus the pipeline contract: a spec WITHOUT a
# spine validates exactly as it did before the spine existed.
# ---------------------------------------------------------------------

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance import grid  # noqa: E402
from resonance.studio import pipeline, spine  # noqa: E402

SR = 48000
BPM = 103


def _spine_spec(sections, **over):
    raw = {"bpm": BPM, "swing": 0.0, "root_midi": 29,
           "sections": sections}
    raw.update(over)
    return spine.normalize_spine_spec(raw)


class SpineSpecTests(unittest.TestCase):
    def test_minimal_spine_normalizes(self):
        sp = _spine_spec([{"name": "hook", "bars": 8, "density": "full"}])
        self.assertEqual(sp["bpm"], 103.0)
        self.assertEqual(sp["beats_per_bar"], 4)
        self.assertEqual(spine.total_bars(sp), 8)

    def test_bad_bpm_refused(self):
        with self.assertRaises(ValueError) as ctx:
            _spine_spec([{"bars": 4, "density": "full"}], bpm=0)
        self.assertIn("spine.bpm", str(ctx.exception))

    def test_unknown_density_refused(self):
        with self.assertRaises(ValueError) as ctx:
            _spine_spec([{"bars": 4, "density": "wild"}])
        self.assertIn("density", str(ctx.exception))

    def test_zero_bars_refused(self):
        with self.assertRaises(ValueError) as ctx:
            _spine_spec([{"bars": 0, "density": "full"}])
        self.assertIn("bars", str(ctx.exception))

    def test_empty_sections_refused(self):
        with self.assertRaises(ValueError):
            _spine_spec([])

    def test_pipeline_spec_without_spine_unchanged(self):
        spec = pipeline.validate_spec({
            "prompt_base": "a tone poem", "sections": [{"seconds": 10}],
            "out_dir": "/tmp/never-built"})
        self.assertNotIn("spine", spec)

    def test_pipeline_spec_with_spine_normalizes(self):
        spec = pipeline.validate_spec({
            "prompt_base": "a tone poem", "sections": [{"seconds": 10}],
            "out_dir": "/tmp/never-built",
            "spine": {"bpm": 103,
                      "sections": [{"name": "hook", "bars": 8,
                                    "density": "full"}]}})
        self.assertEqual(spec["spine"]["bpm"], 103.0)


class GridExactnessTests(unittest.TestCase):
    def test_total_length_is_bars_to_samples_at_103(self):
        sp = _spine_spec([{"name": "intro", "bars": 8,
                           "density": "sparse"}])
        arr = spine.render_spine(sp, SR)
        expected = grid.bars_to_samples(8, BPM, SR)
        self.assertEqual(expected, 894757)  # the number, pinned
        self.assertEqual(arr.shape, (2, expected))

    def test_multi_section_length_closes(self):
        sp = _spine_spec([
            {"name": "hook", "bars": 8, "density": "full"},
            {"name": "verse", "bars": 16, "density": "driving"},
            {"name": "feature", "bars": 16, "density": "open"},
        ])
        arr = spine.render_spine(sp, SR)
        self.assertEqual(arr.shape[1],
                         grid.bars_to_samples(40, BPM, SR))

    def test_trim_spine_spec_cuts_from_the_end(self):
        sp = _spine_spec([
            {"name": "a", "bars": 8, "density": "full"},
            {"name": "b", "bars": 16, "density": "driving"},
        ])
        cut = spine.trim_spine_spec(sp, 10)
        self.assertEqual(spine.total_bars(cut), 10)
        self.assertEqual(cut["sections"][1]["bars"], 2)
        self.assertEqual(spine.total_bars(sp), 24)  # original intact


class OnsetGridTests(unittest.TestCase):
    def test_kick_onsets_land_on_grid_steps(self):
        # Driving bar 0 strikes the kick at steps 0, 8, 10 -- with
        # swing 0 the onsets must sit on round(step * step_float).
        sp = _spine_spec([{"name": "verse", "bars": 4,
                           "density": "driving"}])
        arr = spine.render_spine(sp, SR)
        mono = np.abs(arr[0])
        step_float = grid.samples_per_beat(BPM, SR) / 4.0
        tol = 1024  # the kick's attack fade smears the rise a little
        for step in (0, 8, 10):
            at = int(round(step * step_float))
            window = mono[max(0, at - 64):at + tol]
            self.assertGreater(float(np.max(window)), 0.3,
                               f"no kick energy near step {step}")
        # A step where NOTHING in the pattern strikes hard (step 1 of
        # the driving bar carries only a quiet hat): its onset region
        # must be far quieter than a kick step's.
        at = int(round(1 * step_float))
        quiet = float(np.max(mono[at:at + 512]))
        kick_at = int(round(8 * step_float))
        loud = float(np.max(mono[kick_at:kick_at + 512]))
        self.assertLess(quiet, loud)

    def test_first_onset_is_the_first_sample(self):
        sp = _spine_spec([{"name": "intro", "bars": 4,
                           "density": "sparse"}])
        arr = spine.render_spine(sp, SR)
        self.assertGreater(float(np.max(np.abs(arr[:, :512]))), 0.3)


class BassTests(unittest.TestCase):
    def test_bass808_holds_the_root_pitch(self):
        # F1 = MIDI 29 = 43.65 Hz. After the 25 ms pitch drop the
        # tone must sit on the root: FFT the settled middle of a
        # half-second note and find the peak in the 30-60 Hz band.
        note = spine.bass808(29, 0.5, SR)
        seg = note[int(0.15 * SR):int(0.45 * SR)]
        spectrum = np.abs(np.fft.rfft(seg * np.hanning(seg.size)))
        freqs = np.fft.rfftfreq(seg.size, d=1.0 / SR)
        band = (freqs >= 30.0) & (freqs <= 60.0)
        peak = float(freqs[band][np.argmax(spectrum[band])])
        self.assertAlmostEqual(peak, 43.65, delta=3.0)

    def test_spine_bass_follows_the_chord_cycle(self):
        # Bar 2 of the cycle is Db over the root (+8 semitones):
        # F1 43.65 Hz -> Db2 69.30 Hz. Render 4 sparse bars, weigh
        # the bass band of bar index 1 the same way.
        sp = _spine_spec([{"name": "intro", "bars": 4,
                           "density": "sparse"}])
        arr = spine.render_spine(sp, SR)
        bar = grid.samples_per_bar(BPM, SR)
        start = int(round(1 * bar)) + int(0.3 * SR)
        seg = arr[0][start:start + int(0.4 * SR)]
        spectrum = np.abs(np.fft.rfft(seg * np.hanning(seg.size)))
        freqs = np.fft.rfftfreq(seg.size, d=1.0 / SR)
        band = (freqs >= 55.0) & (freqs <= 85.0)
        peak = float(freqs[band][np.argmax(spectrum[band])])
        self.assertAlmostEqual(peak, 69.30, delta=4.0)


class DryRunSpineTests(unittest.TestCase):
    def test_cli_dry_run_reports_spine_plan(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            spec = {
                "title": "SPINE DRY", "prompt_base": "bounce",
                "sections": [{"name": "x", "seconds": 10}],
                "out_dir": tmp,
                "spine": {"bpm": 103, "sections": [
                    {"name": "hook", "bars": 8, "density": "full"}]},
            }
            spec_path = Path(tmp) / "spec.json"
            spec_path.write_text(json.dumps(spec))
            proc = subprocess.run(
                [sys.executable, "-m", "resonance.studio", "produce",
                 "--spec", str(spec_path), "--dry-run", "--json"],
                cwd=repo, capture_output=True, text=True, timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        manifest = json.loads(proc.stdout)
        plan = manifest["planned"]["spine"]
        self.assertEqual(plan["total_bars"], 8)
        self.assertEqual(plan["exact_samples"],
                         grid.bars_to_samples(8, BPM, SR))


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
