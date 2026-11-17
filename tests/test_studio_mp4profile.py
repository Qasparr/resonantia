# 93
# ---------------------------------------------------------------------
# test_studio_mp4profile.py -- The house MP4 profile, weighed pure.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: the profile is pure argument-building, so it is
# weighed with no ffmpeg in the room: the geometry (fit within
# the sworn frame, never upscale, even dimensions), the audio
# ladder (a master's copy first, AAC the one fallback; a
# non-master straight to AAC), and the encode tail (the codec
# law, the faststart flag, the caller's tune admitted and an
# unknown mode refused by name).
# ---------------------------------------------------------------------

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance.studio import mp4profile as prof  # noqa: E402


class TestFitWithin(unittest.TestCase):
    def test_sworn_frame_is_itself(self):
        self.assertEqual(prof.fit_within(1920, 1080), (1920, 1080))

    def test_oversize_scales_to_the_frame(self):
        self.assertEqual(prof.fit_within(3840, 2160), (1920, 1080))
        self.assertEqual(prof.fit_within(2560, 1080), (1920, 810))

    def test_never_upscales(self):
        self.assertEqual(prof.fit_within(1280, 720), (1280, 720))
        self.assertEqual(prof.fit_within(640, 360), (640, 360))

    def test_dimensions_are_even(self):
        w, h = prof.fit_within(1000, 563)
        self.assertEqual((w % 2, h % 2), (0, 0))
        self.assertLessEqual(w, 1000)
        self.assertLessEqual(h, 563)

    def test_portrait_fits_by_height(self):
        w, h = prof.fit_within(1080, 1920)
        self.assertEqual(h, 1080)
        self.assertLessEqual(w, 1920)

    def test_nonpositive_is_refused(self):
        with self.assertRaises(ValueError):
            prof.fit_within(0, 720)


class TestAudioLadder(unittest.TestCase):
    def test_master_copies_first_aac_fallback(self):
        ladder = prof.audio_ladder(True)
        self.assertEqual([m for m, _ in ladder],
                         ["copy", "aac-320k"])
        self.assertEqual(ladder[0][1], ["-c:a", "copy"])
        self.assertIn("320k", ladder[1][1])

    def test_non_master_goes_straight_to_aac(self):
        ladder = prof.audio_ladder(False)
        self.assertEqual([m for m, _ in ladder], ["aac-320k"])


class TestOutputArgs(unittest.TestCase):
    def test_the_codec_law_and_faststart(self):
        args = prof.output_args("copy")
        for needle in ("libx264", "yuv420p", "+faststart"):
            self.assertIn(needle, args)
        self.assertEqual(args[args.index("-c:a") + 1], "copy")

    def test_tune_is_the_callers_to_name(self):
        args = prof.output_args("aac-320k", tune="stillimage")
        self.assertEqual(args[args.index("-tune") + 1],
                         "stillimage")
        self.assertNotIn("-tune", prof.output_args("copy"))

    def test_unknown_mode_refused_by_name(self):
        with self.assertRaises(ValueError):
            prof.output_args("opus-510k")

    def test_build_command_assembles_the_whole(self):
        cmd = prof.build_command(
            ["-i", "in.wav", "-i", "frame.png"], "out.mp4",
            audio_mode="copy")
        self.assertEqual(cmd[:4], ["ffmpeg", "-v", "error", "-y"])
        self.assertEqual(cmd[-1], "out.mp4")
        self.assertIn("+faststart", cmd)


if __name__ == "__main__":
    unittest.main()
