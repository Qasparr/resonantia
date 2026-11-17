# 93
# ---------------------------------------------------------------------
# test_studio_proofs.py -- Render-as-Proof, weighed pure.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: what is weighed here is the proof law with no render
# in the room: the hash chain's integrity and its tamper alarms,
# the Proof of Mastering gate's fail-closed verdicts (an in-law
# body seals; loud, hot, mis-bitrated, and UNMEASURED bodies all
# fail, each by name), the calibration store's arithmetic (the
# Nine as training axes: factors are asked/realized, clamped,
# provenance kept), the stamp's round-trip through the CLI, and
# the plug's application of a learned factor at sequence build.
# The live chain -- genesis, run 2, the master -- is weighed by
# the run record, not here.
# ---------------------------------------------------------------------

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resonance.studio import diffsinger as ds  # noqa: E402
from resonance.studio import proofs  # noqa: E402


def _artifact(tmp, name="art.wav", body=b"RIFF-fake-but-hashed"):
    p = Path(tmp) / name
    p.write_bytes(body)
    return p


class TestChain(unittest.TestCase):
    """The ledger: chained, append-only, tamper-evident."""

    def test_chain_integrity_and_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            art = _artifact(tmp)
            r1 = proofs.append_proof(
                "lyrics", art, {"n": 1}, ledger_path=ledger,
                ts="2026-11-16T00:00:00+00:00")
            r2 = proofs.append_proof(
                "vocal", art, {"n": 2}, parents=[r1["id"]],
                ledger_path=ledger, ts="2026-11-16T00:01:00+00:00")
            r3 = proofs.append_proof(
                "score", art, {"n": 3}, parents=[r2["id"]],
                ledger_path=ledger, ts="2026-11-16T00:02:00+00:00")
            self.assertEqual(r1["prev"], proofs.GENESIS_PREV)
            self.assertEqual(r2["prev"], r1["id"])
            self.assertEqual(r3["prev"], r2["id"])
            self.assertTrue(r1["id"].startswith("pow-"))
            self.assertIn("Flagpole of Claim and Coinage",
                          r1["flagpole"])
            verdict = proofs.verify_ledger(ledger)
            self.assertTrue(verdict["ok"], verdict["breaks"])
            self.assertEqual(verdict["records"], 3)

    def test_tampered_record_breaks(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            art = _artifact(tmp)
            proofs.append_proof("lyrics", art, {"n": 1},
                                ledger_path=ledger)
            lines = ledger.read_text(encoding="utf-8").splitlines()
            rec = json.loads(lines[0])
            rec["manifest"] = {"n": 999}     # a later hand edits
            lines[0] = json.dumps(rec, ensure_ascii=False)
            ledger.write_text("\n".join(lines) + "\n",
                              encoding="utf-8")
            verdict = proofs.verify_ledger(ledger)
            self.assertFalse(verdict["ok"])
            self.assertTrue(any("TAMPERED RECORD" in b["problem"]
                                for b in verdict["breaks"]))

    def test_tampered_artifact_breaks(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            art = _artifact(tmp)
            proofs.append_proof("vocal", art, {}, ledger_path=ledger)
            art.write_bytes(b"a different body entirely")
            verdict = proofs.verify_ledger(ledger)
            self.assertFalse(verdict["ok"])
            self.assertTrue(any("TAMPERED ARTIFACT" in b["problem"]
                                for b in verdict["breaks"]))

    def test_missing_artifact_is_reported_not_passed(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            art = _artifact(tmp)
            proofs.append_proof("vocal", art, {}, ledger_path=ledger)
            art.unlink()
            verdict = proofs.verify_ledger(ledger)
            self.assertFalse(verdict["ok"])
            self.assertTrue(any("ARTIFACT MISSING" in b["problem"]
                                for b in verdict["breaks"]))

    def test_bad_kind_refused_by_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            art = _artifact(tmp)
            with self.assertRaises(ValueError):
                proofs.append_proof("mixtape", art, {},
                                    ledger_path=Path(tmp) / "l.jsonl")


class TestMasteringGate(unittest.TestCase):
    """Proof of Mastering: fail-closed, every check printed."""

    def _in_law(self):
        return {"lufs_integrated": -14.1, "true_peak_dbtp": -1.2,
                "bitrate_bps": 320000,
                "sworn_bitrate_bps": 320000}

    def test_in_law_body_seals(self):
        gate = proofs.check_mastering(self._in_law())
        self.assertTrue(gate["sealed"], gate)
        self.assertEqual(gate["failures"], [])

    def test_loud_body_fails_by_name(self):
        body = self._in_law()
        body["lufs_integrated"] = -11.0
        gate = proofs.check_mastering(body)
        self.assertFalse(gate["sealed"])
        self.assertIn("integrated loudness", gate["failures"])

    def test_hot_body_fails_by_name(self):
        body = self._in_law()
        body["true_peak_dbtp"] = -0.4
        gate = proofs.check_mastering(body)
        self.assertFalse(gate["sealed"])
        self.assertIn("decoded true peak", gate["failures"])

    def test_wrong_bitrate_fails_by_name(self):
        body = self._in_law()
        body["bitrate_bps"] = 256000
        gate = proofs.check_mastering(body)
        self.assertFalse(gate["sealed"])
        self.assertIn("bitrate (sworn)", gate["failures"])

    def test_unmeasured_body_cannot_seal(self):
        gate = proofs.check_mastering({})
        self.assertFalse(gate["sealed"])
        self.assertIn("integrated loudness", gate["failures"])
        self.assertIn("decoded true peak", gate["failures"])

    def test_sigma_checked_only_when_sworn(self):
        body = self._in_law()
        body["sigma_sworn"] = True
        body["sigma_band_dbfs"] = -28.0
        gate = proofs.check_mastering(body)
        self.assertFalse(gate["sealed"])
        self.assertIn("sigma band (sworn)", gate["failures"])
        body["sigma_band_dbfs"] = -30.13
        self.assertTrue(proofs.check_mastering(body)["sealed"])

    def test_failed_master_still_gets_its_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            art = _artifact(tmp, "master.mp3")
            body = self._in_law()
            body["lufs_integrated"] = -9.0
            rec = proofs.append_master_proof(
                art, {"title": "LOUD"}, body, ledger_path=ledger)
            self.assertEqual(rec["status"], "FAILED")
            self.assertFalse(rec["gate"]["sealed"])
            self.assertTrue(proofs.verify_ledger(ledger)["ok"])


class TestCalibration(unittest.TestCase):
    """The Nine as training axes: accumulate, factor, clamp."""

    def _vocal(self, tmp, ledger, totals, ts):
        art = _artifact(tmp, f"v-{ts}.wav")
        return proofs.append_proof(
            "vocal", art, {"seat_totals": totals},
            ledger_path=ledger, ts=ts)

    def test_factor_is_asked_over_realized(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            self._vocal(tmp, ledger,
                        {"Α": {"asked_s": 2.0, "realized_s": 1.8,
                               "phonemes": 10}},
                        "2026-11-16T00:00:00+00:00")
            store = proofs.rebuild_calibration(ledger)
            factors = proofs.calibration_factors(store)
            self.assertAlmostEqual(factors["Α"], 2.0 / 1.8, 3)

    def test_accumulates_across_proofs_with_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            r1 = self._vocal(tmp, ledger,
                             {"VV": {"asked_s": 1.0,
                                     "realized_s": 0.9,
                                     "phonemes": 5}},
                             "2026-11-16T00:00:00+00:00")
            r2 = self._vocal(tmp, ledger,
                             {"VV": {"asked_s": 1.0,
                                     "realized_s": 0.9,
                                     "phonemes": 5}},
                             "2026-11-16T00:01:00+00:00")
            store = proofs.rebuild_calibration(ledger)
            acc = store["seats"]["VV"]
            self.assertEqual(acc["trained_by"], [r1["id"], r2["id"]])
            self.assertAlmostEqual(acc["asked_s"], 2.0)
            self.assertAlmostEqual(acc["realized_s"], 1.8)
            self.assertEqual(
                proofs.calibration_trained_by(store),
                [r1["id"], r2["id"]])

    def test_factor_clamped_to_the_stated_span(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            self._vocal(tmp, ledger,
                        {"Ο": {"asked_s": 10.0, "realized_s": 1.0,
                               "phonemes": 3}},
                        "2026-11-16T00:00:00+00:00")
            factors = proofs.calibration_factors(
                proofs.rebuild_calibration(ledger))
            self.assertEqual(factors["Ο"], proofs.FACTOR_MAX)

    def test_unseen_seat_has_no_factor(self):
        store = proofs.accumulate_calibration([])
        self.assertEqual(proofs.calibration_factors(store), {})

    def test_non_vocal_proofs_do_not_train(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            art = _artifact(tmp)
            proofs.append_proof(
                "score", art,
                {"seat_totals": {"Α": {"asked_s": 5.0,
                                       "realized_s": 1.0,
                                       "phonemes": 9}}},
                ledger_path=ledger)
            store = proofs.rebuild_calibration(ledger)
            self.assertEqual(store["seats"], {})


class TestStamp(unittest.TestCase):
    """The toolkit's door: stamp, read back, master refused."""

    def test_stamp_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            art = _artifact(tmp, "sheet.pdf")
            rec = proofs.stamp("score", art, {"pages": 3},
                               ledger_path=ledger)
            back = proofs.read_ledger(ledger)
            self.assertEqual(back[0]["id"], rec["id"])
            self.assertEqual(back[0]["artifact"]["sha256"],
                             proofs.sha256_file(art))
            self.assertTrue(proofs.verify_ledger(ledger)["ok"])

    def test_stamp_master_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            art = _artifact(tmp, "m.mp3")
            with self.assertRaises(ValueError):
                proofs.stamp("master", art, {},
                             ledger_path=Path(tmp) / "l.jsonl")

    def test_cli_stamp_and_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = str(Path(tmp) / "ledger.jsonl")
            art = _artifact(tmp, "lyric.txt")
            out = io.StringIO()
            with redirect_stdout(out):
                rc = proofs.main(["stamp", "--kind", "lyrics",
                                  "--file", str(art),
                                  "--ledger", ledger])
            self.assertEqual(rc, 0)
            rec = json.loads(out.getvalue())
            self.assertEqual(rec["kind"], "lyrics")
            out = io.StringIO()
            with redirect_stdout(out):
                rc = proofs.main(["verify", "--ledger", ledger])
            self.assertEqual(rc, 0)
            self.assertTrue(json.loads(out.getvalue())["ok"])


class TestPlugApplication(unittest.TestCase):
    """The plug pre-corrects mora budgets by the learned factors."""

    def _bank(self, tmp):
        bank = Path(tmp)
        ph = {"SP": 0, "AP": 1, "ja/a": 2, "ja/u": 3, "ja/k": 4}
        langs = {"ja": 2}
        (bank / "phonemes.json").write_text(json.dumps(ph))
        (bank / "languages.json").write_text(json.dumps(langs))
        return ph, langs

    def _line(self):
        return {"id": "t1", "lang": "ja", "speaker": "X",
                "text": "カウ", "offset": 0.0,
                "morae": [["k", "a"], ["u"]],
                "notes": [{"midi": 60, "dur": 1.0},
                          {"midi": 62, "dur": 1.0}]}

    def test_factor_scales_only_its_seats_morae(self):
        with tempfile.TemporaryDirectory() as tmp:
            ph, langs = self._bank(tmp)
            plain = ds.build_line(self._line(), ph, langs)
            corr = ds.build_line(self._line(), ph, langs,
                                 seat_factors={"Α": 2.0})
            # The a-mora (Α seat) doubles; the u-mora (VV seat,
            # untrained here) stands; the score's asked seconds
            # never move.
            self.assertEqual(corr["word_dur"][0],
                             plain["word_dur"][0] * 2)
            self.assertEqual(corr["word_dur"][1],
                             plain["word_dur"][1])
            self.assertEqual(corr["asked_s"], plain["asked_s"])
            self.assertEqual(
                corr["calibration_applied"]["Α"]["morae"], 1)

    def test_seat_durations_aggregate_by_station(self):
        with tempfile.TemporaryDirectory() as tmp:
            ph, langs = self._bank(tmp)
            built = ds.build_line(self._line(), ph, langs)
            total_frames = sum(built["word_dur"])
            rows = ds.seat_durations(
                [built], [{"id": "t1", "frames": total_frames}])
            totals = rows["totals"]
            self.assertIn("Α", totals)
            self.assertIn("VV", totals)
            # At full realization, asked == realized per seat.
            for seat in ("Α", "VV"):
                self.assertAlmostEqual(totals[seat]["asked_s"],
                                       totals[seat]["realized_s"],
                                       places=3)


if __name__ == "__main__":
    unittest.main()

# 93 -- Live, Love, and let Love, Live.
