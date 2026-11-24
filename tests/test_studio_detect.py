#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — tests/test_studio_detect.py — the Detection Seat
# judged on KNOWN house renders: the ZONOS3-Mini English
# narration of THE PIRATE ESSAY (its script stands beside it)
# and the DiffSinger DETROIT MUGETSU hook (Japanese, its sheet
# in the Vocal Exam corpus). The reads asserted here are the
# reads measured on this bench on 24 November 2026; where the
# instrument disagrees with the known content — the sung
# hook's forced-Japanese transcript is kana in shape but not
# the sheet's words — the test asserts the honest shape of
# the read, never a tuned agreement.
#
# 93.
# Date: 24 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""Tests for resonance/studio/detect.py and the exam's two
additive judges, by measurement on artifacts of record."""

import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

from resonance.studio import detect
from resonance.studio import vocal_exam as exam

ROOT = Path(__file__).resolve().parents[1]
EN_MASTER = (ROOT / "studio-runs" / "pirate-essay-audiobook-run1"
             / "master.wav")
JA_HOOK = (ROOT / "studio-runs" / "mugetsu-hook-engine-run2"
           / "mugetsu-hook.wav")

SEAT = detect.seat_status()
WHISPER_UP = SEAT["whisper_cli_present"] and SEAT["whisper_model_present"]


def _trim(src, dst, seconds):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(src),
         "-t", str(seconds), str(dst)],
        check=True, capture_output=True)
    return dst


class TestSeatStatus(unittest.TestCase):
    """The seat reports its own standing, piece by piece."""

    def test_status_names_every_piece(self):
        for key in ("whisper_cli_present", "whisper_model_present",
                    "whisper_model_bytes", "silero_model_present",
                    "onnxruntime_present", "vad_engine_available"):
            self.assertIn(key, SEAT)
        self.assertIn(SEAT["vad_engine_available"],
                      ("silero-onnx", "energy-decile"))


@unittest.skipUnless(WHISPER_UP, "whisper seat not built on this box")
class TestLanguageDetection(unittest.TestCase):
    """Identification on known content, EN and JA."""

    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        cls.en_clip = _trim(EN_MASTER,
                            Path(cls._td.name) / "en-15s.wav", 15)

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def test_english_narration_reads_english(self):
        # Measured on this bench: en, p = 0.9972 (20 s read).
        read = detect.detect_language(self.en_clip)
        self.assertEqual(read["language"], "en")
        self.assertGreater(read["probability"], 0.9)
        self.assertEqual(read["model"], "ggml-base")

    def test_japanese_hook_reads_japanese(self):
        # Measured on this bench: ja, p = 0.8241 — the sung
        # hook, read by the dedicated detection pass.
        read = detect.detect_language(JA_HOOK)
        self.assertEqual(read["language"], "ja")
        self.assertGreater(read["probability"], 0.5)


@unittest.skipUnless(WHISPER_UP, "whisper seat not built on this box")
class TestTranscription(unittest.TestCase):
    """Transcription smoke: spoken words against their script;
    sung words asserted only for the shape of the read."""

    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        cls.en_clip = _trim(EN_MASTER,
                            Path(cls._td.name) / "en-15s.wav", 15)
        cls.en = detect.transcribe(cls.en_clip)
        cls.ja = detect.transcribe(JA_HOOK)

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def test_english_transcript_meets_its_script(self):
        # The script of record opens "The Pirate Essay. The
        # Seventy-Seven Trinities..." — the machine listener's
        # words must carry its load-bearing nouns.
        self.assertEqual(self.en["language"], "en")
        self.assertIn("Pirate", self.en["text"])
        self.assertIn("Trinities", self.en["text"])
        self.assertIn("authorship", self.en["text"])

    def test_segments_are_timed_and_ordered(self):
        segs = self.en["segments"]
        self.assertGreaterEqual(len(segs), 2)
        for s in segs:
            self.assertLessEqual(s["start_s"], s["end_s"])
        starts = [s["start_s"] for s in segs]
        self.assertEqual(starts, sorted(starts))
        self.assertLessEqual(segs[-1]["end_s"], 15.5)

    def test_japanese_hook_transcribes_as_japanese_shape(self):
        # The two-pass law: detection says ja (p = 0.8241), so
        # the decode is Japanese-forced and yields kana. The
        # words are NOT the sheet's — sung soprano at base
        # model size — and this test asserts the shape of the
        # read (language, kana present, segments timed), never
        # a lyric agreement the instrument did not earn.
        self.assertEqual(self.ja["language"], "ja")
        self.assertGreaterEqual(len(self.ja["segments"]), 3)
        kana = [c for c in self.ja["text"]
                if "ぁ" <= c <= "ヶ"]
        self.assertGreater(len(kana), 20)


class TestVoiceSegments(unittest.TestCase):
    """VAD: silence reads empty; narration reads covered."""

    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        td = Path(cls._td.name)
        cls.en_clip = _trim(EN_MASTER, td / "en-15s.wav", 15)
        # A known silence: two seconds of digital zeros,
        # written with the stdlib wave module.
        import wave
        with wave.open(str(td / "silence.wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(np.zeros(32000, dtype=np.int16).tobytes())
        cls.silence = td / "silence.wav"

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def test_silence_has_no_voice(self):
        read = detect.voice_segments(self.silence)
        self.assertEqual(read["segments"], [])
        self.assertEqual(read["coverage"], 0.0)
        self.assertEqual(read["speech_s"], 0.0)

    def test_narration_is_covered(self):
        # Silero's frame read on this narration: 85.6% of
        # frames over threshold; segment coverage stands in
        # the same country. Either engine must clear 0.5.
        read = detect.voice_segments(self.en_clip)
        self.assertIn(read["engine"],
                      ("silero-onnx", "energy-decile"))
        self.assertGreater(read["coverage"], 0.5)
        self.assertLess(read["coverage"], 1.0)
        self.assertGreaterEqual(len(read["segments"]), 1)
        for s in read["segments"]:
            self.assertLess(s["start_s"], s["end_s"])

    def test_energy_engine_obeys_its_name(self):
        read = detect.voice_segments(self.en_clip,
                                     engine="energy-decile")
        self.assertEqual(read["engine"], "energy-decile")
        self.assertGreater(read["coverage"], 0.3)

    def test_unseated_engine_name_refused(self):
        with self.assertRaises(detect.DetectError):
            detect.voice_segments(self.en_clip, engine="magic")


@unittest.skipUnless(WHISPER_UP, "whisper seat not built on this box")
class TestLyricTimingDraft(unittest.TestCase):
    """The draft artifact: marked DRAFT, timed, worded."""

    def test_draft_written_and_marked(self):
        with tempfile.TemporaryDirectory() as td:
            clip = _trim(EN_MASTER, Path(td) / "en-15s.wav", 15)
            abc = Path(td) / "draft.abc"
            out = detect.lyric_timing_draft(clip, abc,
                                            title="Pirate (test)")
            text = abc.read_text(encoding="utf-8")
            self.assertIn("DRAFT", text)
            self.assertIn("w: ", text)
            self.assertIn("Pirate", text)
            import json
            side = json.loads(
                Path(out["timing_path"]).read_text(
                    encoding="utf-8"))
            self.assertEqual(len(side["segments"]),
                             len(out["segments"]))
            self.assertEqual(side["language"], "en")


@unittest.skipUnless(WHISPER_UP, "whisper seat not built on this box")
class TestExamJudges(unittest.TestCase):
    """The exam's additive judges, on the artifacts of record."""

    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        cls.en_clip = _trim(EN_MASTER,
                            Path(cls._td.name) / "en-15s.wav", 15)

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def test_language_judge_matches_known_english(self):
        read = exam.judge_language(self.en_clip, expected_lang="en")
        self.assertEqual(read["detected"], "en")
        self.assertTrue(read["match"])

    def test_language_judge_on_the_hook_of_record(self):
        read = exam.judge_language(JA_HOOK, expected_lang="ja")
        self.assertEqual(read["detected"], "ja")
        self.assertTrue(read["match"])
        self.assertGreater(read["probability"], 0.5)

    def test_coverage_judge_on_narration(self):
        read = exam.judge_coverage(self.en_clip)
        self.assertEqual(read["judge"], "coverage")
        self.assertGreater(read["coverage"], 0.5)
        self.assertGreaterEqual(read["n_segments"], 1)


if __name__ == "__main__":
    unittest.main()
