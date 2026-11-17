# 93
# ---------------------------------------------------------------------
# build_run.py -- MUGETSU HOOK, ENGINE RUN 2: the calibration
# loop's first circuit, and the proof chain's first three links.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: this driver walks the whole doctrine of
# docs/PROOF-OF-WORK.md in one pass, in order:
#   1. GENESIS -- run 1 (studio-runs/mugetsu-hook-engine-run1/,
#      struck before the ledger existed) is stamped as the
#      ledger's first proof: its artifact hashed, its per-seat
#      asked-vs-realized totals recomputed from its own spec and
#      manifest by the plug's seat_durations -- the same scales
#      that will weigh run 2, so the comparison argues with no
#      second yardstick.
#   2. TRAINING -- the calibration store is rebuilt from the
#      ledger (resonance.studio.proofs): per-seat factors
#      asked/realized, provenance = the genesis proof's ID.
#   3. RUN 2 -- the SAME filed score, the SAME filed lyrics
#      (byte-exact, extracted and cross-checked by run 1's driver
#      of record, imported below -- the tables are not retyped),
#      the SAME bank (Lem the Shapeshifter DS 2.5, named per its
#      TOS), rendered through the plug WITH the calibration
#      applied and WITH proof emission ordered (parent: genesis).
#   4. MASTERING -- the run-2 vocal is mastered through the Four
#      Powers chain (Scire measures; Audere's law via
#      pipeline.master_signal at -14 LUFS / -1.0 dBTP; Tacere
#      dithers the 24-bit strike), struck as master.wav + a
#      delivered master.mp3 at the sworn 320k, and appended as a
#      Proof of Mastering (parent: the run-2 vocal proof) whose
#      seal the gate decides on the DECODED MP3's measurements.
#   5. THE COMPARISON -- run2-summary.json carries the per-line
#      and total duration realization of both runs against the
#      filed score's asked seconds, printed whatever it says.
#
# DOCTRINE: the labels stay honest -- the master is a VOCAL
# master (one sung stem, no backing, no mix), the alignment of
# morae under notes is the grouping law (CONSTRUCTED, labeled in
# run 1's report and unchanged here), and the calibration is a
# correction of BUDGETS, never of the score: the notes run 2 is
# weighed against are run 1's notes, byte for byte.
# ---------------------------------------------------------------------

import importlib.util
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from resonance.studio import diffsinger as ds  # noqa: E402
from resonance.studio import four_powers as fp  # noqa: E402
from resonance.studio import pipeline  # noqa: E402
from resonance.studio import proofs  # noqa: E402

RUN1 = REPO / "studio-runs" / "mugetsu-hook-engine-run1"
PKG = REPO / "studio-runs" / "gemini-mugetsu-japanese"
LEDGER = proofs.default_ledger_path()
SEED = 93


def _load_run1_driver():
    """Run 1's driver as a module: its filed tables, imported.

    The mora tables and the extraction law are run 1's record;
    importing them (rather than retyping 127 morae) is what
    'the same filed lyrics' means mechanically -- one source,
    two runs, no transcription seam between them.
    """
    path = RUN1 / "build_run.py"
    spec = importlib.util.spec_from_file_location("run1_driver",
                                                  path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stamp_genesis():
    """Run 1 -> the ledger's genesis vocal proof (idempotent).

    If a record already attests run 1's assembly by path, it is
    the genesis and is returned untouched -- the ledger is
    append-only, and a second genesis would be a fork, not a
    correction.
    """
    target = "studio-runs/mugetsu-hook-engine-run1/mugetsu-hook.wav"
    for rec in proofs.read_ledger(LEDGER):
        if rec["artifact"]["path"] == target:
            print(f"genesis already stands: {rec['id']}")
            return rec
    spec1 = json.loads((RUN1 / "spec.json").read_text(
        encoding="utf-8"))
    man1 = json.loads((RUN1 / "manifest.json").read_text(
        encoding="utf-8"))
    ph, langs = ds._load_bank_tables(ds.BANK)
    built = [ds.build_line(line, ph, langs)
             for line in spec1["lines"]]
    rows = [{"id": r["id"], "frames": r["frames"]}
            for r in man1["lines"]]
    seats = ds.seat_durations(built, rows)
    body = {
        "title": man1["title"],
        "engine": man1["engine"],
        "bank": ds.BANK_NAME,
        "seat_totals": seats["totals"],
        "nine": man1["nine"],
        "lines": [{"id": r["id"], "asked_s": r["asked_s"],
                   "rendered_s": r["rendered_s"]}
                  for r in man1["lines"]],
        "assembly": {
            "file": man1["assembly"]["file"],
            "duration_s": man1["assembly"]["measured"]["duration_s"],
            "peak_dbfs": man1["assembly"]["measured"]["peak_dbfs"],
            "rms_dbfs": man1["assembly"]["measured"]["rms_dbfs"]},
        "calibration": {"applied": False, "factors": {},
                        "trained_by": []},
        "genesis": True,
        "stamped_from": "studio-runs/mugetsu-hook-engine-run1/"
                        "manifest.json (run 1 predates the "
                        "ledger; stamped at the loop's founding "
                        "from its manifest of record, its seat "
                        "totals recomputed by the plug's own "
                        "scales)",
    }
    rec = proofs.append_proof(
        "vocal", RUN1 / "mugetsu-hook.wav", body, parents=[],
        ledger_path=LEDGER)
    print(f"genesis stamped: {rec['id']}")
    return rec


def build_spec(run1, genesis_id, factors, trained_by):
    """Run 2's spec: run 1's sources, the loop's corrections."""
    texts = run1.extract_hook_lines()
    for i, (table, reading) in enumerate(
            zip(run1.MORAE, run1.READINGS), 1):
        if run1.split_morae(reading) != [k for k, _ in table]:
            raise ValueError(f"line {i}: mora cross-check failed")
    melody = ds.melody_from_midi(run1.SCORE_MID, "Hook melody",
                                 bpm=run1.BPM)
    notes = melody["notes"]
    bars = []
    for b in range(8):
        lo, hi = b * run1.BAR_S, (b + 1) * run1.BAR_S
        bars.append([n for n in notes
                     if lo - 1e-9 <= n["start"] < hi])
    if [len(b) for b in bars] != [7, 6, 7, 7, 7, 7, 7, 6]:
        raise ValueError("bar note counts differ from run 1")
    lines = []
    for i, (text, table, bar) in enumerate(
            zip(texts, run1.MORAE, bars), 1):
        lines.append({
            "id": f"hook-l{i}", "lang": "ja",
            "speaker": run1.SPEAKER, "text": text,
            "morae": [ph for _, ph in table],
            "notes": [{"midi": n["midi"], "dur": n["dur"]}
                      for n in bar],
            "offset": (i - 1) * run1.BAR_S})
    return {
        "title": "DETROIT MUGETSU -- hook, engine run 2 "
                 "(calibration circuit 1; YAMI seat: Civet)",
        "lines": lines, "assembly_file": "mugetsu-hook.wav",
        "threads": 4,
        "calibration": {"factors": factors,
                        "trained_by": trained_by},
        "proof": {"parents": [genesis_id]},
    }


def _ffmpeg(args, what):
    proc = subprocess.run(["ffmpeg", "-y", "-v", "error", *args],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg ({what}) failed: "
                           f"{proc.stderr.strip()}")


def _write_wav24(path, samples):
    """Strike a 24-bit PCM WAV from a (2, N) float signal."""
    x = np.asarray(samples, dtype=np.float64)
    ints = np.clip(np.round(x * (2 ** 23)), -(2 ** 23),
                   2 ** 23 - 1).astype(np.int32)
    frames = ints.T.copy()                      # (N, 2)
    raw = frames.view(np.uint8).reshape(-1, 2, 4)[:, :, :3]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(pipeline.TARGET_SR)
        w.writeframes(np.ascontiguousarray(raw).tobytes())


def master_vocal(vocal_wav, vocal_proof_id):
    """Master the run-2 vocal; append its Proof of Mastering."""
    src48 = HERE / "master-src-48k.wav"
    _ffmpeg(["-i", str(vocal_wav), "-ar", "48000", "-ac", "2",
             str(src48)], "vocal to 48k stereo")
    x, sr = pipeline.read_wav_pcm(src48)
    if sr != pipeline.TARGET_SR:
        raise ValueError(f"mastering source at {sr}, not 48000")
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.vstack([x, x])
    scire = fp.scire_measure(x, pipeline.TARGET_SR,
                             pipeline.measure_loudness_lufs,
                             pipeline.true_peak_dbtp)
    head = int(pipeline.HEAD_FADE_S * pipeline.TARGET_SR)
    tail = int(pipeline.END_FADE_S * pipeline.TARGET_SR)
    x[:, :head] *= np.linspace(0.0, 1.0, head)
    x[:, -tail:] *= np.linspace(1.0, 0.0, tail)
    mastered, report = pipeline.master_signal(
        x, pipeline.TARGET_SR, proofs.TARGET_LUFS,
        proofs.CEILING_DBTP)
    mastered = fp.tpdf_dither(mastered, SEED)
    tacere = fp.tacere_report(report, True)
    four = fp.assemble(scire, {"engaged": False, "eq": [],
                               "comp": None, "rms_delta_db": 0.0,
                               "peak_delta_db": 0.0},
                       {"engaged": False, "drive_db": 0.0,
                        "crest_before_db": scire["crest_db"],
                        "crest_after_db": scire["crest_db"],
                        "rms_delta_db": 0.0},
                       report, tacere)
    master_wav = HERE / "master.wav"
    master_mp3 = HERE / "master.mp3"
    _write_wav24(master_wav, mastered)
    _ffmpeg(["-i", str(master_wav), "-codec:a", "libmp3lame",
             "-b:a", "320k", str(master_mp3)], "master mp3")
    measured = proofs.measure_master(master_mp3, master_wav)
    body = {"title": "DETROIT MUGETSU -- hook, engine run 2 "
                     "(VOCAL master)",
            "label": "vocal master: one sung stem mastered to "
                     "house law; no backing, no mix",
            "four_powers": four, "master_report": report}
    rec = proofs.append_master_proof(
        master_mp3, body, measured, parents=[vocal_proof_id],
        ledger_path=LEDGER)
    print(f"proof of mastering: {rec['id']} ({rec['status']})")
    return rec, measured, four


def main():
    run1 = _load_run1_driver()
    genesis = stamp_genesis()
    store = proofs.rebuild_calibration(LEDGER)
    factors = proofs.calibration_factors(store)
    trained_by = proofs.calibration_trained_by(store)
    print(f"calibration factors: {factors}")
    print(f"trained by: {trained_by}")

    spec = build_spec(run1, genesis["id"], factors, trained_by)
    (HERE / "spec.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2),
        encoding="utf-8")
    manifest = ds.render(spec, HERE,
                         log=lambda m: print(m, flush=True))
    vocal_proof_id = manifest["proof"]["id"]

    master_rec, measured, four = master_vocal(
        HERE / "mugetsu-hook.wav", vocal_proof_id)

    man1 = json.loads((RUN1 / "manifest.json").read_text(
        encoding="utf-8"))
    comparison = []
    tot1 = tot2 = asked_tot = 0.0
    for r1, r2 in zip(man1["lines"], manifest["lines"]):
        asked = r1["asked_s"]
        comparison.append({
            "id": r1["id"], "asked_s": asked,
            "run1_rendered_s": r1["rendered_s"],
            "run1_realization_pct": round(
                100.0 * r1["rendered_s"] / asked, 2),
            "run2_rendered_s": r2["rendered_s"],
            "run2_realization_pct": round(
                100.0 * r2["rendered_s"] / asked, 2)})
        tot1 += r1["rendered_s"]
        tot2 += r2["rendered_s"]
        asked_tot += asked
    summary = {
        "genesis_proof": genesis["id"],
        "run2_vocal_proof": vocal_proof_id,
        "master_proof": master_rec["id"],
        "master_status": master_rec["status"],
        "master_gate": master_rec["gate"],
        "master_measured": measured,
        "calibration_factors": factors,
        "calibration_trained_by": trained_by,
        "run2_seat_totals": manifest["seat_totals"],
        "comparison": comparison,
        "totals": {
            "asked_s": round(asked_tot, 4),
            "run1_rendered_s": round(tot1, 4),
            "run1_realization_pct": round(100.0 * tot1 / asked_tot,
                                          2),
            "run2_rendered_s": round(tot2, 4),
            "run2_realization_pct": round(100.0 * tot2 / asked_tot,
                                          2)},
        "run2_assembly": manifest["assembly"]["measured"],
        "run2_walls": manifest["walls"],
    }
    (HERE / "run2-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(json.dumps(summary["totals"], indent=2))
    print(f"master: {master_rec['status']} "
          f"{master_rec['gate']['failures']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 93 -- Live, Love, and let Love, Live.
