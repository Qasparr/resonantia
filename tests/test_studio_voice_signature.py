#!/usr/bin/env python3
# =============================================================================
# RESONANTIA -- tests/test_studio_voice_signature.py -- the
# voice-signature plug judged at its gates: the registry
# round-trips whole; enrollment holds the founder's boundary
# shut IN CODE (a recording, a clone, a sampled real voice --
# refused by name, for every holder; the founder's seat takes
# an imagined synthetic generation and the filed spec, or
# nothing); a render is the named signature through the named
# backend or it does not happen (an absent backend, an
# unseated backend, a reference-less clone -- each refused,
# never substituted); and a struck render is measured and
# written into the trail before it is returned.
#
# 93.
# Date: 24 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR -- All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM: the boundary is asserted where it
# binds -- at the enroll() gate, with the refusal's own error
# name -- not where it is merely described. The render trail
# is asserted from the log file the render actually wrote.
# Backends in these tests are stubs that strike a one-second
# tone: what is sworn here is the plug's law (gates, seating,
# logging, measurement), not any engine's voice; the engines
# are proven on the bench, in the open, by their own runs.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""Tests for resonance/studio/voice_signature.py, at its gates."""

import json
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from resonance.studio import voice_signature as vs
from resonance.studio.voice_signature import (
    BackendUnavailable, BoundaryError, SignaturePlug,
    VoiceSignatureError)


def make_wav(path, seconds=1.0, rate=48000, freq=220.0, amp=0.3):
    """A small honest tone, 16-bit PCM, whole cycles not needed."""
    n = int(seconds * rate)
    t = np.arange(n) / rate
    x = (amp * np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(x.tobytes())
    return Path(path)


GENERATED_PROV = {
    "kind": "GENERATED",
    "engine": "test-synth (in-test stub generation)",
    "date": "2026-11-24",
    "source_line": "a short line, generated for the gate tests",
    "subject": "synthetic persona voice",
}


class StubCloneBackend:
    """A cloning seat that strikes a tone and tells the truth."""

    name = "stub_clone"
    supports_clone = True
    supports_named_voice = False

    def __init__(self, ok=True):
        self._ok = ok
        self.calls = []

    def available(self):
        return (True, "stub_clone: seated") if self._ok else \
            (False, "stub_clone: deliberately unseated for the test")

    def render_clone(self, reference_wav, reference_text, text,
                     out_path):
        self.calls.append((str(reference_wav), reference_text, text))
        make_wav(out_path, seconds=1.0)
        return None


class StubVoiceBackend:
    """A named-voice seat, on the ZONOS road's shape."""

    name = "stub_voice"
    supports_clone = False
    supports_named_voice = True

    def available(self):
        return True, "stub_voice: seated"

    def render_voice(self, voice, text, out_path):
        make_wav(out_path, seconds=1.0)
        return None


class RegistryShapeTests(unittest.TestCase):
    """The seated registry loads whole and round-trips whole."""

    def test_seed_registry_loads_with_filed_holders(self):
        ids = vs.list_signatures()
        for expected in ("qasparr", "qveen-bee", "lady-lilith",
                         "banshee", "sol-rey", "yami", "shion"):
            self.assertIn(expected, ids)
        founder = vs.get_signature("qasparr")
        self.assertEqual(founder["holder_kind"], "founder")
        # The founder's spec in the registry IS the filed spec.
        self.assertEqual(founder["spec"]["register"],
                         vs.FILED_FOUNDER_SPEC["register"])
        qveen = vs.get_signature("qveen-bee")
        self.assertIn("SOPRANO", qveen["spec"]["register"])

    def test_registry_round_trip(self):
        data = vs.load_registry()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "signatures.json"
            vs.save_registry(data, path)
            again = vs.load_registry(path)
        self.assertEqual(again, data)

    def test_unknown_signature_refused_by_name(self):
        with self.assertRaises(VoiceSignatureError):
            vs.get_signature("no-such-voice")


class EnrollGateTests(unittest.TestCase):
    """The boundary, held at the gate, in code."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.reg = Path(self._td.name) / "signatures.json"
        self.ref = make_wav(Path(self._td.name) / "ref.wav", 1.0)

    def tearDown(self):
        self._td.cleanup()

    def test_persona_enroll_with_generated_reference(self):
        rec = vs.enroll(
            "test-persona", self.ref, holder="TEST PERSONA",
            provenance=dict(GENERATED_PROV), registry_path=self.reg)
        self.assertEqual(rec["reference"]["duration_s"], 1.0)
        self.assertEqual(rec["reference"]["sample_rate"], 48000)
        self.assertEqual(len(rec["reference"]["sha256"]), 64)
        # The registry is self-contained: the copy is seated.
        copied = Path(self.reg).parent / rec["reference"]["file"]
        self.assertTrue(copied.exists())
        # A reference seats the cloning backend by default.
        self.assertEqual(rec["backends"]["fish_s2"]["mode"], "clone")

    def test_founder_recording_refused(self):
        prov = {"kind": "RECORDING", "engine": "a microphone",
                "subject": "the founder, recorded at home"}
        with self.assertRaises(BoundaryError):
            vs.enroll("qasparr", self.ref, provenance=prov,
                      registry_path=self.reg)

    def test_founder_clone_refused(self):
        prov = {"kind": "CLONE", "engine": "some suite",
                "subject": "the founder"}
        with self.assertRaises(BoundaryError):
            vs.enroll("qasparr", self.ref, provenance=prov,
                      registry_path=self.reg)

    def test_persona_clone_of_a_person_refused(self):
        prov = {"kind": "CLONE", "engine": "some suite",
                "subject": "a real singer"}
        with self.assertRaises(BoundaryError):
            vs.enroll("test-persona", self.ref,
                      holder="TEST PERSONA", provenance=prov,
                      registry_path=self.reg)

    def test_generated_without_engine_refused(self):
        prov = {"kind": "GENERATED", "engine": "",
                "subject": "synthetic persona voice"}
        with self.assertRaises(BoundaryError):
            vs.enroll("test-persona", self.ref,
                      holder="TEST PERSONA", provenance=prov,
                      registry_path=self.reg)

    def test_founder_generated_imagined_enrolls(self):
        prov = dict(GENERATED_PROV)
        prov["subject"] = "imagined-synthetic"
        rec = vs.enroll("qasparr", self.ref, provenance=prov,
                        registry_path=self.reg)
        self.assertEqual(rec["spec"], vs.FILED_FOUNDER_SPEC)
        self.assertEqual(
            rec["reference"]["provenance"]["kind"], "GENERATED")

    def test_founder_spec_is_filed_not_written(self):
        parting = {"register": "a deep bass, recorded from life",
                   "summary": "his real voice, sampled"}
        with self.assertRaises(BoundaryError):
            vs.enroll("qasparr", spec=parting,
                      registry_path=self.reg)

    def test_missing_and_unreadable_references_refused(self):
        with self.assertRaises(VoiceSignatureError):
            vs.enroll("test-persona", Path(self._td.name) / "no.wav",
                      holder="TEST PERSONA",
                      provenance=dict(GENERATED_PROV),
                      registry_path=self.reg)
        not_wav = Path(self._td.name) / "not.wav"
        not_wav.write_text("this is not a wav", encoding="utf-8")
        with self.assertRaises(VoiceSignatureError):
            vs.enroll("test-persona", not_wav,
                      holder="TEST PERSONA",
                      provenance=dict(GENERATED_PROV),
                      registry_path=self.reg)

    def test_too_short_reference_refused(self):
        short = make_wav(Path(self._td.name) / "short.wav", 0.2)
        with self.assertRaises(VoiceSignatureError):
            vs.enroll("test-persona", short, holder="TEST PERSONA",
                      provenance=dict(GENERATED_PROV),
                      registry_path=self.reg)


class RenderGateTests(unittest.TestCase):
    """A render is the named signature/backend, or it is not."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.reg = Path(self._td.name) / "signatures.json"
        self.ref = make_wav(Path(self._td.name) / "ref.wav", 1.0)
        vs.enroll("test-persona", self.ref, holder="TEST PERSONA",
                  provenance=dict(GENERATED_PROV),
                  backends={"stub_clone": {"mode": "clone"},
                            "stub_voice": {"voice": "Stub_F_1"}},
                  registry_path=self.reg)

    def tearDown(self):
        self._td.cleanup()

    def _plug(self, backends):
        return SignaturePlug(registry_path=self.reg, backends=backends)

    def test_clone_render_measures_and_logs(self):
        stub = StubCloneBackend()
        plug = self._plug({"stub_clone": stub})
        out = Path(self._td.name) / "out.wav"
        rec = plug.render("test-persona", "say it plain",
                          backend="stub_clone", out_path=out)
        self.assertTrue(out.exists())
        self.assertEqual(rec["signature_id"], "test-persona")
        self.assertEqual(rec["backend"], "stub_clone")
        self.assertEqual(rec["mode"], "clone")
        self.assertAlmostEqual(rec["duration_s"], 1.0, delta=0.05)
        self.assertEqual(rec["sample_rate"], 48000)
        self.assertIsNotNone(rec["dbtp"])
        # The trail holds exactly this render, with its numbers.
        log = Path(self._td.name) / "render_log.jsonl"
        lines = log.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 1)
        logged = json.loads(lines[0])
        self.assertEqual(logged["signature_id"], "test-persona")
        self.assertEqual(logged["backend"], "stub_clone")
        self.assertEqual(logged["text"], "say it plain")

    def test_named_voice_render(self):
        plug = self._plug({"stub_voice": StubVoiceBackend()})
        rec = plug.render("test-persona", "say it plain",
                          backend="stub_voice",
                          out_path=Path(self._td.name) / "o.wav")
        self.assertEqual(rec["mode"], "named-voice")

    def test_absent_backend_raises_unavailable(self):
        plug = self._plug({"stub_clone": StubCloneBackend(ok=False)})
        with self.assertRaises(BackendUnavailable):
            plug.render("test-persona", "say it plain",
                        backend="stub_clone",
                        out_path=Path(self._td.name) / "o.wav")

    def test_unknown_backend_raises_unavailable(self):
        plug = self._plug({"stub_clone": StubCloneBackend()})
        with self.assertRaises(BackendUnavailable):
            plug.render("test-persona", "say it plain",
                        backend="no_such_backend",
                        out_path=Path(self._td.name) / "o.wav")

    def test_unseated_backend_raises_unavailable(self):
        # The signature seats stub_clone only; stub_voice exists
        # on the plug but not on her record -- no substitution.
        plug = self._plug({"stub_clone": StubCloneBackend(),
                           "zonos_like": StubVoiceBackend()})
        vs.enroll("solo-clone", self.ref, holder="SOLO CLONE",
                  provenance=dict(GENERATED_PROV),
                  backends={"stub_clone": {"mode": "clone"}},
                  registry_path=self.reg)
        with self.assertRaises(BackendUnavailable):
            plug.render("solo-clone", "say it plain",
                        backend="zonos_like",
                        out_path=Path(self._td.name) / "o.wav")

    def test_clone_without_reference_refused(self):
        vs.enroll("no-ref", holder="NO REF", registry_path=self.reg)
        data = vs.load_registry(self.reg)
        for rec in data["signatures"]:
            if rec["id"] == "no-ref":
                rec["backends"]["stub_clone"] = {"mode": "clone"}
        vs.save_registry(data, self.reg)
        plug = self._plug({"stub_clone": StubCloneBackend()})
        with self.assertRaises(VoiceSignatureError):
            plug.render("no-ref", "say it plain",
                        backend="stub_clone",
                        out_path=Path(self._td.name) / "o.wav")

    def test_real_fish_backend_reports_its_seat(self):
        # The seat's own word about itself, whatever the bench
        # holds: available() must answer, and a lab that does
        # not exist must answer False with its reason.
        empty = vs.FishS2Backend(lab_dir=Path(self._td.name) / "void")
        ok, reason = empty.available()
        self.assertFalse(ok)
        self.assertIn("fish_s2", reason)


if __name__ == "__main__":
    unittest.main()
