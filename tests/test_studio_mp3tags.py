# 93
# ---------------------------------------------------------------------
# test_studio_mp3tags.py -- The proof stamp, weighed pure.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: the ID3 stamp writer/reader is weighed against
# synthetic MP3 bodies (the tagger treats audio as opaque bytes,
# so a plausible frame header repeated is a lawful fixture) and
# against hand-built v2.3 tags carrying foreign furniture -- a
# stranger's comment, an unknown frame, another tool's TXXX --
# that a stamp must preserve payload-for-payload. The guarded
# integration tests at the end put a real ffmpeg-encoded master
# through proofs.emit_produce_proof and weigh the whole seam:
# the record attests the twin, the delivered file carries the
# stamp, the chain verifies.
# ---------------------------------------------------------------------

import hashlib
import json
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance.studio import mp3tags, proofs  # noqa: E402


def _audio(n=4):
    """A synthetic MP3 body: plausible MPEG-1 Layer III frame
    headers over silence. The tagger never decodes audio, so the
    body only needs to be bytes that are not a tag."""
    frame = b"\xff\xfb\x90\x00" + b"\x00" * 413
    return frame * n


def _syncsafe(n):
    return bytes([(n >> 21) & 0x7F, (n >> 14) & 0x7F,
                  (n >> 7) & 0x7F, n & 0x7F])


def _v23_tag(frames):
    """Hand-build an ID3v2.3 tag from (frame_id, payload) pairs."""
    body = b""
    for frame_id, payload in frames:
        body += frame_id.encode("ascii") \
            + len(payload).to_bytes(4, "big") + b"\x00\x00" + payload
    return b"ID3" + bytes([3, 0, 0]) + _syncsafe(len(body)) + body


def _latin1_text(text):
    return b"\x00" + text.encode("latin-1")


def _foreign_mp3(tmp, name="song.mp3"):
    """An MP3 carrying another tool's tag furniture."""
    frames = [
        ("TIT2", _latin1_text("Old Title")),
        ("XABC", b"\x01\x02\x03binary-foreign\xff"),
        ("TXXX", b"\x00OTHER\x00keep me"),
        ("COMM", b"\x00engnote\x00a stranger's comment"),
    ]
    p = Path(tmp) / name
    p.write_bytes(_v23_tag(frames) + _audio())
    return p


class TestParse(unittest.TestCase):
    def test_tagless_file_is_all_audio(self):
        parsed = mp3tags.parse_tag(_audio())
        self.assertIsNone(parsed["version"])
        self.assertEqual(parsed["frames"], [])
        self.assertEqual(parsed["audio"], _audio())

    def test_v23_frames_parse(self):
        p = _foreign_mp3(self._tmp())
        parsed = mp3tags.parse_tag(p.read_bytes())
        self.assertEqual(parsed["version"], 3)
        ids = [f[0] for f in parsed["frames"]]
        self.assertEqual(ids, ["TIT2", "XABC", "TXXX", "COMM"])
        self.assertEqual(parsed["audio"], _audio())

    def test_refusals_are_named(self):
        # A v2.2 header, an extended header, unsynchronisation:
        # each refused by name, never silently mangled.
        for flags, major in ((0x00, 2), (0x40, 3), (0x80, 3)):
            data = b"ID3" + bytes([major, 0, flags]) \
                + _syncsafe(0) + _audio()
            with self.assertRaises(mp3tags.TagError):
                mp3tags.parse_tag(data)

    def _tmp(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        return tmp


class TestStamp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_sealed_stamp_round_trip(self):
        p = Path(self.tmp) / "bare.mp3"
        p.write_bytes(_audio())
        stamp = mp3tags.stamp_master_tags(
            p, proof_id="pow-abc123", status="SEALED",
            title="The Title")
        self.assertEqual(stamp["proof"], "pow-abc123")
        self.assertEqual(stamp["status"], "SEALED")
        self.assertEqual(stamp["title"], "The Title")
        self.assertEqual(stamp["authorship"], proofs.AUTHORSHIP)
        self.assertEqual(stamp["flagpole"], proofs.FLAGPOLE)
        self.assertNotIn("gate", stamp)

    def test_failed_stamp_prints_its_failure(self):
        p = Path(self.tmp) / "loud.mp3"
        p.write_bytes(_audio())
        gate = {"sealed": False, "checks": [
            {"check": "integrated loudness", "value": -9.5,
             "law": "-14.0 +/- 0.5 LUFS", "ok": False},
            {"check": "decoded true peak", "value": -2.0,
             "law": "<= -1.0 dBTP", "ok": True}],
            "failures": ["integrated loudness"]}
        stamp = mp3tags.stamp_master_tags(
            p, proof_id="pow-fail1", status="FAILED", gate=gate)
        self.assertEqual(stamp["status"], "FAILED")
        self.assertIn("integrated loudness", stamp["gate"])
        self.assertIn("-9.5", stamp["gate"])
        self.assertNotIn("true peak", stamp["gate"])

    def test_foreign_frames_survive_a_stamp(self):
        p = _foreign_mp3(self.tmp)
        mp3tags.stamp_master_tags(
            p, proof_id="pow-x", status="SEALED", title="New Title")
        parsed = mp3tags.parse_tag(p.read_bytes())
        by_id = {}
        for frame_id, _flags, payload in parsed["frames"]:
            by_id.setdefault(frame_id, []).append(payload)
        # The unknown frame rides byte for byte.
        self.assertEqual(by_id["XABC"],
                         [b"\x01\x02\x03binary-foreign\xff"])
        # The foreign TXXX and the stranger's comment survive.
        self.assertIn(b"\x00OTHER\x00keep me", by_id["TXXX"])
        self.assertEqual(len(by_id["COMM"]), 2)  # stranger + Flagpole
        # The stamp owns the title face: exactly one TIT2, the new.
        self.assertEqual(len(by_id["TIT2"]), 1)
        self.assertEqual(mp3tags.read_stamp(p)["title"], "New Title")
        # The audio body is untouched.
        self.assertEqual(parsed["audio"], _audio())

    def test_restamp_replaces_never_stacks(self):
        p = Path(self.tmp) / "twice.mp3"
        p.write_bytes(_audio())
        mp3tags.stamp_master_tags(p, proof_id="pow-first",
                                  status="SEALED")
        mp3tags.stamp_master_tags(p, proof_id="pow-second",
                                  status="SEALED")
        stamp = mp3tags.read_stamp(p)
        self.assertEqual(stamp["proof"], "pow-second")
        parsed = mp3tags.parse_tag(p.read_bytes())
        proofs_found = [pl for fid, _f, pl in parsed["frames"]
                        if fid == "TXXX"
                        and mp3tags._split_txxx(pl)[0]
                        == mp3tags.DESC_PROOF]
        self.assertEqual(len(proofs_found), 1)
        self.assertEqual(parsed["audio"], _audio())

    def test_unstamped_reads_empty(self):
        p = _foreign_mp3(self.tmp)
        self.assertEqual(mp3tags.read_stamp(p), {})


class TestAttestedTwin(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_preserve_creates_identical_twin(self):
        p = Path(self.tmp) / "preview.mp3"
        p.write_bytes(_audio())
        twin = mp3tags.preserve_attested_copy(p)
        self.assertEqual(twin.name, "preview.attested.mp3")
        self.assertEqual(twin.read_bytes(), _audio())
        # A second preservation of the same body is a no-op.
        self.assertEqual(mp3tags.preserve_attested_copy(p), twin)

    def test_stamped_file_is_refused_as_pristine(self):
        p = Path(self.tmp) / "stamped.mp3"
        p.write_bytes(_audio())
        mp3tags.stamp_master_tags(p, proof_id="pow-1",
                                  status="SEALED")
        with self.assertRaises(mp3tags.TagError):
            mp3tags.preserve_attested_copy(p)

    def test_twin_with_other_bytes_is_refused(self):
        p = Path(self.tmp) / "preview.mp3"
        p.write_bytes(_audio())
        twin = mp3tags.preserve_attested_copy(p)
        p.write_bytes(_audio(9))  # a new encode lands on the name
        with self.assertRaises(mp3tags.TagError):
            mp3tags.preserve_attested_copy(p)
        self.assertEqual(twin.read_bytes(), _audio())


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg not present")
class TestEmissionSeam(unittest.TestCase):
    """The whole seam on a real encode: proofs.emit_produce_proof
    attests the twin, stamps the delivery, and the chain verifies."""

    def _make_master(self, tmp):
        sr = 48000
        wav_path = Path(tmp) / "master.wav"
        with wave.open(str(wav_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            frames = b"".join(
                struct.pack("<h", int(0.4 * 32767
                                      * math.sin(2 * math.pi * 440
                                                 * i / sr)))
                for i in range(sr))
            w.writeframes(frames)
        mp3_path = Path(tmp) / "preview.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(wav_path),
             "-codec:a", "libmp3lame", "-b:a", "320k",
             str(mp3_path)], check=True)
        return wav_path, mp3_path

    def test_emit_stamps_delivery_and_chain_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            wav_path, mp3_path = self._make_master(tmp)
            pristine_audio = mp3tags.audio_bytes(mp3_path)
            ledger = Path(tmp) / "ledger.jsonl"
            manifest = {
                "title": "Seam Smoke",
                "pipeline": "test",
                "files": {
                    "preview_mp3": {"path": str(mp3_path)},
                    "master_wav": {"path": str(wav_path)},
                },
            }
            spec = {"proof": {"ledger": str(ledger)}}
            section = proofs.emit_produce_proof(
                manifest, tmp, spec, log=lambda *a: None)
            self.assertIn("id", section)
            # The delivered file carries the stamp, and the stamp
            # names this very proof and its verdict.
            stamp = mp3tags.read_stamp(mp3_path)
            self.assertEqual(stamp["proof"], section["id"])
            self.assertEqual(stamp["status"], section["status"])
            self.assertEqual(stamp["title"], "Seam Smoke")
            if section["status"] == "FAILED":
                self.assertIn("gate", stamp)
            # The attested twin stands pristine and unstamped,
            # and the record's hash is the twin's hash.
            twin = Path(tmp) / "preview.attested.mp3"
            self.assertTrue(twin.exists())
            self.assertEqual(mp3tags.read_stamp(twin), {})
            records = proofs.read_ledger(ledger)
            self.assertEqual(len(records), 1)
            self.assertEqual(
                records[0]["artifact"]["sha256"],
                hashlib.sha256(twin.read_bytes()).hexdigest())
            # The audio the listener receives is the attested
            # audio, byte for byte.
            self.assertEqual(mp3tags.audio_bytes(mp3_path),
                             pristine_audio)
            self.assertEqual(section["tags"]["audio_identical"],
                             True)
            # And the chain verifies whole.
            verdict = proofs.verify_ledger(ledger_path=ledger)
            self.assertTrue(verdict["ok"], verdict["breaks"])
            # ffprobe still parses the stamped file.
            proc = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries",
                 "format=duration", "-of", "json", str(mp3_path)],
                capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0)
            self.assertIn("duration", json.loads(proc.stdout)
                          ["format"])


if __name__ == "__main__":
    unittest.main()
