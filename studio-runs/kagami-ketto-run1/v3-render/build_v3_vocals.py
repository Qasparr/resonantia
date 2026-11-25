# 93
# ---------------------------------------------------------------------
# build_v3_vocals.py -- KAGAMI KETTOU, v3: the track re-rendered
# as its OWN track, on the Mugetsu-proven road, with no remnant
# of Mugetsu in it.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR, All Rights Reserved, Without Prejudice.
# Written XXV day of November, Anno V:xii e.n. (2026 e.v.), under
# the Method of Science, Aim of Religion -- Scientific Illuminism.
#
# THE COMMISSION (the founder's direct order, 2026-11-25 08:00
# EST): "return to the mugetsu version then rerender the 2nd
# Japanese track as its own track no reminence of Mugetsu in it."
#
# THE DEFECT IT ANSWERS (the founder's ear, 2026-11-25 07:39 EST,
# on FILO v2, which had raised the v1 stem +17.93 dB into the
# front): the voices could be heard, "but they are way offkey
# and pitch and tempo." The v1 stem had never been ear-passed at
# level -- buried some 20 dB in v1, exposed in v2. And the v1
# stem carried a Mugetsu remnant in its very timing: its
# calibration factors {'VV': 1.1054, 'A': 1.1141, 'E': 1.1158,
# 'I': 1.1203, 'O': 1.1114} were trained by the two MUGETSU HOOK
# proofs (pow-7a6472d2..., pow-de96414a...) -- factors learned
# from another song's phrases, applied to this one's 47 lines.
# (The v1 walls already showed the strain: Shion's s03 overhung
# its slot by 0.124 s, s04 by 0.542 s, even with those factors.)
#
# THE ROAD RETURNED TO -- "THE MUGETSU VERSION", AS COORDINATES:
#   * Engine: resonance.studio.diffsinger.render() -- the house
#     DiffSinger plug; bridge resonance/studio/render_diffsinger.py
#     executed in the lab venv (diffsinger-lab/venv), ONNX stages
#     dsdur (linguistic + duration_lem_26v) -> dsvariance
#     (pitch_variance_lem_25) -> acoustic_lem_25 -> NSF-HiFiGAN
#     vocoder (pc_nsf_hifigan_44.1k_hop512_128bin_2025.02).
#   * Bank: Lem the Shapeshifter DS 2.5 (named per its TOS),
#     44.1 kHz, hop 512, 86.1328 frames/s. Speakers from the
#     filed score: Civet (Kurogane AND his Mirror -- the same
#     voice turned, the desk's seated reading) and Phascogale
#     (Shion).
#   * The calibration loop: resonance.studio.proofs -- per-seat
#     (the Nine's vowel seats, acoustic register only) asked-vs-
#     realized duration totals carried by vocal proofs; factor
#     = asked/realized clamped to [0.5, 2.0]; at sequence build
#     the plug scales each mora's frame budget by its seat's
#     factor. The score's note durations NEVER move.
#   * The Mugetsu precedent, circuit 1: run 1 struck with NO
#     calibration (the genesis) -> factors trained on run 1
#     ALONE -> run 2 struck with them: total realization moved
#     90.38% -> 99.52% of the filed score.
#
# MECHANISM -- THE FOUR STAGES OF THIS BUILD:
#   pass1  The filed spec's 47 lines (spec.json, byte-carried;
#          notes and lyrics UNCHANGED) rendered with NO
#          calibration -- Kagami's genesis, the Mugetsu run-1
#          condition. Its vocal proof is appended to a LOCAL
#          ledger (ledger-v3.jsonl, in this folder): the loop's
#          own machinery, a Kagami-only chain. The house ledger
#          is not touched, and no Mugetsu-trained factor can
#          enter, because the local ledger holds nothing else.
#   train  proofs.rebuild_calibration over the local ledger:
#          factors derived by the loop's own functions from
#          Kagami pass 1 ALONE. Provenance is asserted in code:
#          every training ID must resolve inside the local
#          ledger, to the pass-1 stem's own proof.
#   pass2  The same 47 lines re-rendered WITH Kagami's own
#          factors; its proof chained to pass 1's in the local
#          ledger. The pass-2 assembly is the v3 stem.
#   gate   THE STEP WHOSE ABSENCE CAUSED THE REPAIR. Before
#          anything is mixed, the new stem is weighed by the
#          Vocal Exam's own judges (resonance.studio.vocal_exam)
#          plus the plug's realized .ds:
#            (a) ONSETS vs the 144 BPM grid -- judge_onsets on
#                each line's own WAV (audio read, partial
#                coverage where lines are legato), and the
#                realized-.ds note-onset drift (full coverage;
#                the plug's stated reconstruction: per-line
#                totals exact, within-line split proportional
#                to the asked budgets), and per-line rendered
#                vs slot durations.
#            (b) PITCH vs the written notes -- judge_pitch on
#                each line's WAV: cents per note, aggregated
#                per section; every note past 200 cents named.
#            (c) LANGUAGE -- judge_language on the stem.
#          The identical gate is run on the v1 stem and lines,
#          so the receipt prints before/after on one scale.
#          If a gate measure passes beyond its stated tolerance,
#          this build STOPS: no mix is struck from a failing
#          stem, and nothing is buried to hide it.
#
# GATE TOLERANCES (stated here, before the fact, from the
# house's own scales):
#   durations  total realization within [97, 103]%; every
#              section within [95, 105]% (Mugetsu circuit 1
#              landed 99.52% total, lines 96.83--103.10).
#   onsets     per section: audio mean |error| <= 50 ms and
#              max |error| <= 120 ms over measured onsets (an
#              eighth at 144 BPM is 208.3 ms); .ds drift mean
#              |drift| <= 60 ms, max <= 150 ms.
#   pitch      per section: median |cents| <= 50; notes past
#              100 cents <= 10% of the section's measured notes.
#
# DOCTRINE: a calibration is a correction of budgets, never of
# the score; a gate is a measurement, never a hope. This build
# changes the stem's TRAINING and nothing else -- the score,
# the lyrics, the speakers stand as filed.
#
# 93 -- Live, Love, and let Love, Live.
# ---------------------------------------------------------------------

import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
REPO = PKG.parents[1]
sys.path.insert(0, str(REPO))

from resonance.studio import diffsinger as ds       # noqa: E402
from resonance.studio import proofs                 # noqa: E402
from resonance.studio import vocal_exam             # noqa: E402

LEDGER_V3 = HERE / "ledger-v3.jsonl"
FILED_SPEC = PKG / "spec.json"

SECTIONS = ("verse_a", "verse_b", "shion", "close")


def section_of(line_id):
    """A line's section, from its filed id's first letter:
    a -> Verse A, b -> Verse B, s -> Shion, c/f -> the close."""
    head = line_id.split("-")[0][0]
    return {"a": "verse_a", "b": "verse_b", "s": "shion",
            "c": "close", "f": "close"}[head]


def filed_lines():
    """The filed spec's lines, byte-carried: the score and the
    lyrics are the record, and this build retypes neither."""
    spec = json.loads(FILED_SPEC.read_text(encoding="utf-8"))
    return spec["lines"], int(spec.get("threads", 4))


# ---------------------------------------------------------------------
# STAGE pass1 -- Kagami's genesis: the filed lines, no calibration.
# ---------------------------------------------------------------------

def stage_pass1():
    lines, threads = filed_lines()
    spec = {
        "title": "KAGAMI KETTOU -- v3 pass 1 (Kagami's own "
                 "genesis: NO calibration; KUROGANE + MIRROR "
                 "seat: Civet; SHION seat: Phascogale)",
        "lines": lines,
        "assembly_file": "vocal-stem.wav",
        "threads": threads,
        "proof": {"ledger": str(LEDGER_V3)},
    }
    out = HERE / "pass1"
    manifest = ds.render(spec, out, log=lambda m: print(m, flush=True))
    rec = {"stage": "pass1",
           "proof_id": manifest["proof"]["id"],
           "calibration": manifest["calibration"],
           "seat_totals": manifest["seat_totals"],
           "assembly": manifest["assembly"]["measured"],
           "lines": [{"id": r["id"], "asked_s": r["asked_s"],
                      "rendered_s": r["rendered_s"]}
                     for r in manifest["lines"]],
           "walls": manifest["walls"]}
    (HERE / "pass1-record.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(json.dumps({"pass1_proof": rec["proof_id"],
                      "seat_totals": rec["seat_totals"]}, indent=2))
    return rec


# ---------------------------------------------------------------------
# STAGE train -- the loop's own math over the local ledger alone.
# ---------------------------------------------------------------------

def stage_train():
    pass1 = json.loads((HERE / "pass1-record.json").read_text(
        encoding="utf-8"))
    store = proofs.rebuild_calibration(ledger_path=LEDGER_V3)
    factors = proofs.calibration_factors(store)
    trained_by = proofs.calibration_trained_by(store)
    # PROVENANCE, ASSERTED: every training ID resolves inside
    # the LOCAL ledger, and the only record there is pass 1's
    # own proof of the Kagami stem. No Mugetsu proof can train
    # this render, because no Mugetsu record stands in the chain.
    local = {r["id"]: r for r in proofs.read_ledger(LEDGER_V3)}
    assert trained_by, "no training records in the local ledger"
    for pid in trained_by:
        assert pid in local, f"training id {pid} not in local ledger"
        art = local[pid]["artifact"]["path"]
        assert "v3-render/pass1" in art, f"foreign artifact: {art}"
    assert trained_by == [pass1["proof_id"]], (
        f"trained_by {trained_by} != pass 1 proof {pass1['proof_id']}")
    chain = proofs.verify_ledger(LEDGER_V3)
    rec = {"stage": "train",
           "factors": factors,
           "trained_by": trained_by,
           "store": store,
           "chain_verification": chain,
           "pass1_realization_pct": round(
               100.0 * sum(r["rendered_s"] for r in pass1["lines"])
               / sum(r["asked_s"] for r in pass1["lines"]), 4)}
    (HERE / "calibration-v3-record.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(json.dumps({"factors": factors,
                      "trained_by": trained_by,
                      "pass1_realization_pct":
                          rec["pass1_realization_pct"]}, indent=2))
    return rec


# ---------------------------------------------------------------------
# STAGE pass2 -- the same lines, Kagami's own factors applied.
# ---------------------------------------------------------------------

def stage_pass2():
    lines, threads = filed_lines()
    train = json.loads((HERE / "calibration-v3-record.json")
                       .read_text(encoding="utf-8"))
    pass1 = json.loads((HERE / "pass1-record.json").read_text(
        encoding="utf-8"))
    spec = {
        "title": "KAGAMI KETTOU -- v3 pass 2 (calibration trained "
                 "on Kagami pass 1 alone; KUROGANE + MIRROR seat: "
                 "Civet; SHION seat: Phascogale)",
        "lines": lines,
        "assembly_file": "vocal-stem.wav",
        "threads": threads,
        "calibration": {"factors": train["factors"],
                        "trained_by": train["trained_by"]},
        "proof": {"ledger": str(LEDGER_V3),
                  "parents": [pass1["proof_id"]]},
    }
    out = HERE / "pass2"
    manifest = ds.render(spec, out, log=lambda m: print(m, flush=True))
    rec = {"stage": "pass2",
           "proof_id": manifest["proof"]["id"],
           "calibration": manifest["calibration"],
           "seat_totals": manifest["seat_totals"],
           "assembly": manifest["assembly"]["measured"],
           "lines": [{"id": r["id"], "asked_s": r["asked_s"],
                      "rendered_s": r["rendered_s"]}
                     for r in manifest["lines"]],
           "walls": manifest["walls"],
           "realization_pct": round(
               100.0 * sum(r["rendered_s"] for r in manifest["lines"])
               / sum(r["asked_s"] for r in manifest["lines"]), 4)}
    (HERE / "pass2-record.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2),
        encoding="utf-8")
    # The v3 stem, under its own name, beside the passes.
    import shutil
    shutil.copyfile(out / "vocal-stem.wav", HERE / "vocal-stem-v3.wav")
    print(json.dumps({"pass2_proof": rec["proof_id"],
                      "realization_pct": rec["realization_pct"],
                      "walls": rec["walls"]}, indent=2))
    return rec


# ---------------------------------------------------------------------
# THE GATE. One scale for both stems: v1 (the filed run) and v3
# pass 2 are weighed by the identical judges, so the receipt's
# before/after argues with no second yardstick.
# ---------------------------------------------------------------------

def _notes_with_starts(line):
    """The line's notes as the pitch judge takes them: each
    note's start is the cumulative sum of the written durations
    before it, within the line."""
    out, t = [], 0.0
    for n in line["notes"]:
        out.append({"start_s": t, "dur_s": n["dur"],
                    "midi": n["midi"]})
        t += n["dur"]
    return out


def _ds_note_drifts(ds_path):
    """Per-note onset drift from a realized .ds: a note's
    realized onset is the sum of the realized phoneme durations
    of the notes before it (grouped by ph_num); its asked onset
    is the sum of the written note_dur before it. The plug's
    reconstruction caveat rides with these numbers: per-line
    totals are the model's own; the within-line split is the
    asked proportion. Segments come back as a LIST in built
    order -- five of the close's unison lines share their text
    with a partner, so text is not a key; the caller aligns by
    index and asserts each segment's offset against the filed
    spec's, so a misalignment cannot pass in silence."""
    segs = json.loads(Path(ds_path).read_text(encoding="utf-8"))
    per_line = []
    for seg in segs:
        ph_dur = [float(x) for x in seg["ph_dur"].split()]
        ph_num = [int(x) for x in seg["ph_num"].split()]
        note_dur = [float(x) for x in seg["note_dur"].split()]
        drifts, ra, aa, idx = [], 0.0, 0.0, 0
        for k, cnt in enumerate(ph_num):
            drifts.append((ra - aa) * 1000.0)
            ra += sum(ph_dur[idx:idx + cnt])
            idx += cnt
            aa += note_dur[k]
        per_line.append({"offset": float(seg["offset"]),
                         "drifts_ms": drifts})
    return per_line


def gate_one(label, lines_dir, stem_path, ds_path, spec_lines,
             manifest_lines):
    """Weigh one stem end to end; return its gate record."""
    spec_by_id = {l["id"]: l for l in spec_lines}
    man_by_id = {r["id"]: r for r in manifest_lines}
    # (a1) durations, per section and total (the exam's judge).
    durations = {}
    for sec in SECTIONS:
        ids = [l["id"] for l in spec_lines
               if section_of(l["id"]) == sec]
        durations[sec] = vocal_exam.judge_durations(
            [man_by_id[i]["asked_s"] for i in ids],
            [man_by_id[i]["rendered_s"] for i in ids])
    durations["total"] = vocal_exam.judge_durations(
        [r["asked_s"] for r in manifest_lines],
        [r["rendered_s"] for r in manifest_lines])
    # (a2) audio onsets + (b) pitch, per line file.
    onsets, pitch = {}, {}
    drifts_aligned = _ds_note_drifts(ds_path)
    assert len(drifts_aligned) == len(spec_lines), (
        f"{ds_path}: {len(drifts_aligned)} segments against "
        f"{len(spec_lines)} filed lines")
    drift_sections = {sec: [] for sec in SECTIONS}
    for pos, line in enumerate(spec_lines):
        lid = line["id"]
        sec = section_of(lid)
        assert abs(drifts_aligned[pos]["offset"]
                   - line["offset"]) < 0.01, (
            f"{lid}: .ds segment {pos} offset "
            f"{drifts_aligned[pos]['offset']} != filed "
            f"{line['offset']} -- alignment refused")
        wav, sr = sf.read(str(Path(lines_dir) / f"{lid}.wav"))
        notes = _notes_with_starts(line)
        onsets[lid] = vocal_exam.judge_onsets(
            wav, sr, [n["start_s"] for n in notes])
        pitch[lid] = vocal_exam.judge_pitch(wav, sr, notes)
        drift_sections[sec].extend(drifts_aligned[pos]["drifts_ms"])
    onset_sec, pitch_sec = {}, {}
    for sec in SECTIONS:
        ids = [l["id"] for l in spec_lines
               if section_of(l["id"]) == sec]
        errs = [o["error_ms"] for i in ids
                for o in onsets[i]["per_onset"] if "error_ms" in o]
        n_exp = sum(len(onsets[i]["per_onset"]) for i in ids)
        onset_sec[sec] = {
            "n_expected": n_exp, "n_measured": len(errs),
            "mean_error_ms": round(
                sum(errs) / len(errs), 2) if errs else None,
            "mean_abs_error_ms": round(
                sum(abs(e) for e in errs) / len(errs), 2)
            if errs else None,
            "max_abs_error_ms": round(
                max(abs(e) for e in errs), 2) if errs else None}
        cents = [abs(n["cents"]) for i in ids
                 for n in pitch[i]["per_note"] if "cents" in n]
        signed = [n["cents"] for i in ids
                  for n in pitch[i]["per_note"] if "cents" in n]
        worst = sorted(
            ({"line": i, "midi": n["midi"],
              "target_hz": n["target_hz"],
              "measured_hz": n.get("measured_hz"),
              "cents": n["cents"]}
             for i in ids for n in pitch[i]["per_note"]
             if "cents" in n),
            key=lambda w: -abs(w["cents"]))[:5]
        pitch_sec[sec] = {
            "n_notes": sum(len(pitch[i]["per_note"]) for i in ids),
            "n_measured": len(cents),
            "median_abs_cents": round(
                sorted(cents)[len(cents) // 2], 2) if cents else None,
            "mean_cents": round(
                sum(signed) / len(signed), 2) if signed else None,
            "max_abs_cents": round(max(cents), 2) if cents else None,
            "n_over_100": sum(1 for c in cents if c > 100),
            "n_over_200": sum(1 for c in cents if c > 200),
            "worst": worst}
        d = drift_sections[sec]
        onset_sec[sec]["ds_drift"] = {
            "n_notes": len(d),
            "mean_abs_ms": round(
                sum(abs(x) for x in d) / len(d), 2) if d else None,
            "max_abs_ms": round(
                max(abs(x) for x in d), 2) if d else None}
    # (c) language, on the assembled stem.
    language = vocal_exam.judge_language(stem_path, "ja")
    return {"label": label, "durations": durations,
            "onsets_per_section": onset_sec,
            "pitch_per_section": pitch_sec,
            "onsets_per_line": onsets, "pitch_per_line": pitch,
            "language": language}


# The gate's tolerances, stated in the header before the fact.
TOL = {"dur_total": (97.0, 103.0), "dur_section": (95.0, 105.0),
       "onset_mean_abs_ms": 50.0, "onset_max_abs_ms": 120.0,
       "drift_mean_abs_ms": 60.0, "drift_max_abs_ms": 150.0,
       "pitch_median_abs_cents": 50.0, "pitch_over_100_share": 0.10}


def gate_verdict(g):
    """PASS/FAIL per measure, from the stated tolerances. A
    section whose onsets are too few to read is named
    LOW-COVERAGE and its onset verdict rests on the .ds drift
    and the line totals -- printed, never passed in silence."""
    checks = []

    def add(name, ok, detail):
        # ok is True / False / None -- None is the LOW-COVERAGE
        # state, a named non-verdict, never a silent pass and
        # never counted among the failures.
        checks.append({"check": name,
                       "ok": None if ok is None else bool(ok),
                       "detail": detail})

    tot = g["durations"]["total"]["accuracy_pct"]
    add("durations: total", TOL["dur_total"][0] <= tot
        <= TOL["dur_total"][1], f"{tot}% vs [97, 103]")
    for sec in SECTIONS:
        acc = g["durations"][sec]["accuracy_pct"]
        add(f"durations: {sec}", TOL["dur_section"][0] <= acc
            <= TOL["dur_section"][1], f"{acc}% vs [95, 105]")
        o = g["onsets_per_section"][sec]
        if o["n_measured"] >= max(4, 0.2 * o["n_expected"]):
            add(f"onsets (audio): {sec}",
                o["mean_abs_error_ms"] <= TOL["onset_mean_abs_ms"]
                and o["max_abs_error_ms"] <= TOL["onset_max_abs_ms"],
                f"mean|err| {o['mean_abs_error_ms']} ms, max "
                f"{o['max_abs_error_ms']} ms over "
                f"{o['n_measured']}/{o['n_expected']} onsets")
        else:
            add(f"onsets (audio): {sec} LOW-COVERAGE", None,
                f"only {o['n_measured']}/{o['n_expected']} onsets "
                "readable -- verdict rests on .ds drift + totals")
        d = o["ds_drift"]
        add(f"onsets (.ds drift): {sec}",
            d["mean_abs_ms"] <= TOL["drift_mean_abs_ms"]
            and d["max_abs_ms"] <= TOL["drift_max_abs_ms"],
            f"mean|drift| {d['mean_abs_ms']} ms, max "
            f"{d['max_abs_ms']} ms over {d['n_notes']} notes")
        p = g["pitch_per_section"][sec]
        share = (p["n_over_100"] / p["n_measured"]
                 if p["n_measured"] else 1.0)
        add(f"pitch: {sec}",
            p["median_abs_cents"] <= TOL["pitch_median_abs_cents"]
            and share <= TOL["pitch_over_100_share"],
            f"median| cents| {p['median_abs_cents']}, "
            f"{p['n_over_100']}/{p['n_measured']} notes past "
            f"100 cents ({share:.1%}), max {p['max_abs_cents']}")
    lang = g["language"]
    add("language: ja", lang.get("match") is True,
        f"detected {lang.get('detected')} p="
        f"{lang.get('probability')}")
    failed = [c for c in checks if c["ok"] is False]
    return {"checks": checks,
            "verdict": "FAIL" if failed else "PASS",
            "failed": failed}


def stage_gate():
    spec_lines, _t = filed_lines()
    # v1, on the same scale: its per-line asked/rendered are
    # re-measured from its own line WAVs (its ds manifest was
    # overwritten by its build's summary manifest; the WAVs and
    # the render.log are its record).
    v1_manifest_lines = []
    for line in spec_lines:
        m = ds.measure_wav(PKG / "lines" / f"{line['id']}.wav")
        v1_manifest_lines.append({
            "id": line["id"],
            "asked_s": round(sum(n["dur"] for n in line["notes"]), 4),
            "rendered_s": m["duration_s"]})
    g_v1 = gate_one("v1 (Mugetsu-trained factors)", PKG / "lines",
                    PKG / "vocal-stem.wav",
                    PKG / "sequence-realized.ds",
                    spec_lines, v1_manifest_lines)
    p2 = json.loads((HERE / "pass2-record.json").read_text(
        encoding="utf-8"))
    g_v3 = gate_one("v3 pass 2 (Kagami-trained factors)",
                    HERE / "pass2" / "lines",
                    HERE / "pass2" / "vocal-stem.wav",
                    HERE / "pass2" / "sequence-realized.ds",
                    spec_lines, p2["lines"])
    verdict = gate_verdict(g_v3)
    rec = {"stage": "gate", "tolerances": TOL,
           "v1": g_v1, "v3": g_v3, "v3_verdict": verdict,
           "v1_verdict_for_the_record": gate_verdict(g_v1)}
    (HERE / "gate-record-v3.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(json.dumps({"v3_verdict": verdict["verdict"],
                      "failed": verdict["failed"]}, indent=2))
    return rec


# ---------------------------------------------------------------------
# STAGE gatepitch -- the pitch question re-asked with a sound
# instrument. The gate's first strike read pitch through
# judge_pitch (fourier.dominant_frequency: the strongest peak,
# which on these voices is a harmonic, not the fundamental --
# it returned octave medians on lines a YIN read of the same
# windows reads at 0 +/- 4 cents). This stage runs the YIN
# read (yin_pitch_read.py, in the lab venv) over BOTH stems'
# lines, aggregates per section under the gate's stated pitch
# tolerances, names every note past 200 cents, and issues the
# FINAL gate verdict: the first gate's checks with its pitch
# checks replaced by these. Both records stand; the first is
# marked refuted-on-pitch, never erased.
# ---------------------------------------------------------------------

def _yin_pitch_section(read, spec_lines):
    per_section = {}
    for sec in SECTIONS:
        ids = [l["id"] for l in spec_lines
               if section_of(l["id"]) == sec]
        cents, named = [], []
        n_notes = 0
        for lid in ids:
            for pos, n in enumerate(read[lid]["per_note"]):
                n_notes += 1
                if "cents" in n:
                    cents.append(abs(n["cents"]))
                    if abs(n["cents"]) > 200:
                        named.append({"line": lid, "note": pos,
                                      "midi": n["midi"],
                                      "target_hz": n["target_hz"],
                                      "measured_hz":
                                          n.get("measured_hz"),
                                      "cents": n["cents"]})
        per_section[sec] = {
            "n_notes": n_notes, "n_measured": len(cents),
            "median_abs_cents": round(
                sorted(cents)[len(cents) // 2], 2) if cents else None,
            "max_abs_cents": round(max(cents), 2) if cents else None,
            "n_over_100": sum(1 for c in cents if c > 100),
            "n_over_200": sum(1 for c in cents if c > 200),
            "named_over_200": sorted(
                named, key=lambda w: -abs(w["cents"]))}
    return per_section


def stage_gatepitch():
    import subprocess
    spec_lines, _t = filed_lines()
    helper = HERE / "yin_pitch_read.py"
    reads = {}
    for label, lines_dir in (("v1", PKG / "lines"),
                             ("v3", HERE / "pass2" / "lines")):
        out = HERE / f"yin-pitch-{label}.json"
        subprocess.run(
            [ds.LAB_PYTHON, str(helper), str(lines_dir),
             str(FILED_SPEC), str(out)], check=True)
        reads[label] = json.loads(out.read_text(encoding="utf-8"))
    sections = {label: _yin_pitch_section(reads[label], spec_lines)
                for label in ("v1", "v3")}
    # The final verdict: the first gate's checks, its pitch
    # checks struck and replaced by the YIN pitch checks.
    gate = json.loads((HERE / "gate-record-v3.json").read_text(
        encoding="utf-8"))
    checks = [c for c in gate["v3_verdict"]["checks"]
              if not c["check"].startswith("pitch:")]
    for sec in SECTIONS:
        p = sections["v3"][sec]
        share = (p["n_over_100"] / p["n_measured"]
                 if p["n_measured"] else 1.0)
        checks.append({
            "check": f"pitch (YIN): {sec}",
            "ok": bool(p["median_abs_cents"]
                       <= TOL["pitch_median_abs_cents"]
                       and share <= TOL["pitch_over_100_share"]),
            "detail": f"median|cents| {p['median_abs_cents']}, "
                      f"{p['n_over_100']}/{p['n_measured']} notes "
                      f"past 100 cents ({share:.1%}), max "
                      f"{p['max_abs_cents']}, "
                      f"{p['n_over_200']} named past 200"})
    failed = [c for c in checks if c["ok"] is False]
    final = {"checks": checks,
             "verdict": "FAIL" if failed else "PASS",
             "failed": failed}
    rec = {"stage": "gatepitch",
           "instrument": "librosa.yin (autocorrelation), lab "
                         "venv, steady-centre medians",
           "refuted_instrument": "vocal_exam.judge_pitch via "
                                 "fourier.dominant_frequency -- "
                                 "reads the strongest spectral "
                                 "peak (a harmonic/formant on "
                                 "these voices), not the "
                                 "fundamental; its pitch checks "
                                 "in gate-record-v3.json stand "
                                 "marked refuted, not erased",
           "v1_sections": sections["v1"],
           "v3_sections": sections["v3"],
           "final_gate_verdict": final}
    (HERE / "gate-pitch-record-v3.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(json.dumps({"final_gate_verdict": final["verdict"],
                      "failed": failed,
                      "v3_pitch": {s: sections["v3"][s][
                          "median_abs_cents"] for s in SECTIONS},
                      "v1_pitch": {s: sections["v1"][s][
                          "median_abs_cents"] for s in SECTIONS}},
                     indent=2))
    return rec


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "pass1":
        stage_pass1()
    elif stage == "train":
        stage_train()
    elif stage == "pass2":
        stage_pass2()
    elif stage == "gate":
        rec = stage_gate()
        sys.exit(0 if rec["v3_verdict"]["verdict"] == "PASS" else 1)
    elif stage == "gatepitch":
        rec = stage_gatepitch()
        sys.exit(0 if rec["final_gate_verdict"]["verdict"] == "PASS"
                 else 1)
    else:
        raise SystemExit(f"unknown stage {stage!r}: "
                         "pass1 | train | pass2 | gate | gatepitch")

# 93 -- Live, Love, and let Love, Live.
