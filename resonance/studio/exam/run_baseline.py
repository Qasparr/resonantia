#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — studio/exam/run_baseline.py — the Vocal Exam's
# baseline run (Phase 1): score what exists on disk, append the
# records, sing nothing.
#
# 93.
# Date: 24 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# MECHANISM: loads the corpus (studio/exam/corpus.json), scores
# the two DETROIT MUGETSU engine runs of record against the
# hook item's sheet through studio/vocal_exam.py's judges,
# weighs run 2's delivered master against the master law
# (sworn at 320,000 bps by its gate of record), and appends
# one record per corpus item to studio/exam/results.jsonl —
# append-only, proof-ledger discipline. Items with no render
# on disk are recorded UNSUNG: a state, not a failure. Run it
# again and it appends a fresh dated set; history is never
# rewritten.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_ROOT))

from resonance.studio import vocal_exam as exam  # noqa: E402

RUNS = [
    ("studio-runs/mugetsu-hook-engine-run1",
     "DiffSinger (OpenVPI, bank: Lem the Shapeshifter DS 2.5) "
     "via resonance.studio.diffsinger — engine run 1 "
     "(proof pow-7a6472d2da0abf4b)"),
    ("studio-runs/mugetsu-hook-engine-run2",
     "DiffSinger (OpenVPI, bank: Lem the Shapeshifter DS 2.5) "
     "via resonance.studio.diffsinger — engine run 2, "
     "calibration circuit 1 (proof pow-de96414a282efe2f1)"),
]


def main():
    corpus = exam.load_corpus()
    ts = datetime.now(timezone.utc).isoformat()
    records = []
    scored_ids = set()
    for rel, label in RUNS:
        record = exam.score_hook_run(_ROOT / rel, corpus, label)
        record["ts"] = ts
        records.append(record)
        scored_ids.add(record["item_id"])
    master = exam.judge_masterlaw(
        _ROOT / "studio-runs/mugetsu-hook-engine-run2/master.mp3",
        sworn_bps=320000)
    master_wav = exam.judge_masterlaw(
        _ROOT / "studio-runs/mugetsu-hook-engine-run2/master.wav")
    records.append({
        "ts": ts, "item_id": "mugetsu-hook",
        "corpus_version": corpus["version"],
        "engine": RUNS[1][1], "state": "SCORED",
        "render": "studio-runs/mugetsu-hook-engine-run2/master.mp3",
        "judges": {"masterlaw_mp3": master,
                   "masterlaw_wav": master_wav},
    })
    for item in corpus["items"]:
        if item["id"] in scored_ids:
            continue
        records.append({
            "ts": ts, "item_id": item["id"],
            "corpus_version": corpus["version"],
            "engine": None, "state": "UNSUNG",
            "held_out": bool(item.get("held_out")),
            "note": "no render on disk — a state, not a "
                    "failure; singing it is the loop's work, "
                    "not Phase 1's",
            "prediction": exam.predict(item, corpus["version"]),
        })
    with open(exam.RESULTS_PATH, "a", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    for record in records:
        line = f"{record['item_id']}: {record['state']}"
        judges = record.get("judges") or {}
        if "durations" in judges:
            line += (f" | durations "
                     f"{judges['durations']['accuracy_pct']}%")
        if "pitch" in judges:
            line += (f" | pitch median "
                     f"{judges['pitch'].get('median_abs_cents')} "
                     f"cents ({judges['pitch']['n_measured']} "
                     f"notes)")
        print(line)
    print(f"appended {len(records)} records to "
          f"{exam.RESULTS_PATH}")


if __name__ == "__main__":
    main()
