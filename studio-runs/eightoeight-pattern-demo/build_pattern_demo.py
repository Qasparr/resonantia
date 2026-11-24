#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — studio-runs/eightoeight-pattern-demo/
# build_pattern_demo.py — THE 808 PATTERN DEMO: the toolbox's
# voices seated on the KRS foundation grid (144 BPM, 13/8 Sigma
# Mega), struck as a two-bar pattern, mastered to the master
# law, and seated with its drum sheet — sheets ship with all
# tracks, drum parts included.
#
# 93.
# Date: 24 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
#   Hypothesis: that the 808 Synthesizer Toolbox, already a
#     parametric instrument, closes its Phase-2 seat when its
#     voices hold a filed grid together — the KRS foundation
#     (144 BPM, 13/8 Sigma Mega, docs/KRS-BLUEPRINT-MASTERING-
#     PROCESS.md) — and the struck pattern passes the master
#     law on the house's own scales with its sheet beside it.
#   Method: the pattern is stated as step seats (eighth-note
#     steps, 13 to the bar, two bars); each voice is rendered
#     by resonance/studio/eightoeight.py at its recipe (the
#     kick tuned by the dial to VV, the founder's seat, placed
#     44 Hz); voices are summed into a stereo mix at 48 kHz,
#     mastered by pipeline.master_signal to −14 LUFS under a
#     −1.0 dBTP ceiling, encoded 320k by the pipeline's own
#     ffmpeg road, and the delivered MP3 is weighed by the
#     Vocal Exam's master-law judge at the sworn 320,000 bps.
#   Observation: stands in this run's manifest.json and
#     RUN-REPORT.md, measured from the struck files.
#   Result: pattern.wav (the mastered WAV), master-320k.mp3,
#     sheet.abc (the drum sheet), manifest.json.
#
# LABEL HONESTY: "808" names the TR-808 sound family; every
# voice here is synthesized in-house (see eightoeight.py's
# header). Nothing samples Roland's machine.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""Strike the 808 pattern demo: grid, voices, master, sheet."""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from resonance.studio import eightoeight as e8          # noqa: E402
from resonance.studio import pipeline as pipe           # noqa: E402
from resonance.studio import vocal_exam as exam         # noqa: E402

HERE = Path(__file__).resolve().parent
SR = e8.SR                       # 48000, the studio rate
BPM = 144                        # the KRS foundation tempo
STEPS_PER_BAR = 13               # 13/8 Sigma Mega: 13 eighths
BARS = 2
STEP_S = 60.0 / BPM / 2.0        # one eighth at 144 BPM

# The pattern, as step seats within one bar (0..12). The kick
# bounces (0, 3, 6, 10); the snare answers at 4 and 11; hats
# tick the odd steps, the open hat closing the bar at 12.
PATTERN = {
    "kick": [0, 3, 6, 10],
    "snare": [4, 11],
    "hihat_closed": [1, 3, 5, 7, 9, 11],
    "hihat_open": [12],
}
GAINS = {"kick": 0.95, "snare": 0.55,
         "hihat_closed": 0.30, "hihat_open": 0.32}
VOICE_FN = {
    "kick": lambda: e8.kick(tune="VV"),
    "snare": lambda: e8.snare(),
    "hihat_closed": lambda: e8.hihat(open_=False),
    "hihat_open": lambda: e8.hihat(open_=True),
}


def build_mix():
    """Sum the pattern into a mono float64 buffer at SR.

    MECHANISM: each voice renders once (its recipe is
    step-independent); a step seat places the voice's buffer
    at step * STEP_S across both bars. The kick's tail is
    allowed to ring across steps — that ring IS the bounce.
    """
    total_s = BARS * STEPS_PER_BAR * STEP_S + 1.0  # tail room
    mix = np.zeros(int(total_s * SR))
    placed = []
    for name, steps in PATTERN.items():
        buf = VOICE_FN[name]() * GAINS[name]
        for bar in range(BARS):
            for step in steps:
                at = int((bar * STEPS_PER_BAR + step) * STEP_S * SR)
                end = min(len(mix), at + len(buf))
                mix[at:end] += buf[:end - at]
                placed.append({"voice": name, "bar": bar + 1,
                               "step": step,
                               "at_s": round((bar * STEPS_PER_BAR
                                              + step) * STEP_S, 4)})
    return mix, placed


def write_sheet(path, placed):
    """The drum sheet, in ABC — the house's notation layer.

    MECHANISM: M:13/8, L:1/8, Q:1/4=144 — the filed grid
    itself. Two voices: V:1 the kick (staff seat C,), V:2 the
    snare (c) and hats (g). A step with no voice is a rest z.
    The mapping is declared in the header, so the sheet reads
    as what it is: seats on a staff, named in the legend —
    the same honesty the toolbox's label carries.
    """
    def bar_voice(voice_names, seat_note):
        bars = []
        for bar in range(BARS):
            cells = []
            for step in range(STEPS_PER_BAR):
                hit = any(p["voice"] in voice_names
                          and p["bar"] == bar + 1
                          and p["step"] == step
                          for p in placed)
                cells.append(seat_note if hit else "z")
            bars.append(" ".join(cells))
        return " | ".join(bars) + " |"

    kick_line = bar_voice({"kick"}, "C,")
    # V:2 carries two voices on one staff line: snare seat c,
    # hat seat g. A step holding both is written as an ABC
    # chord [cg] — the notation's own way to seat two voices
    # at one instant (the filed pattern seats snare + closed
    # hat together at step 11 of each bar).
    SEAT = {"snare": "c", "hihat_closed": "g", "hihat_open": "g"}

    def bar_top():
        bars = []
        for bar in range(BARS):
            cells = []
            for step in range(STEPS_PER_BAR):
                hits = [p["voice"] for p in placed
                        if p["bar"] == bar + 1 and p["step"] == step
                        and p["voice"] != "kick"]
                if not hits:
                    cells.append("z")
                elif len(hits) == 1:
                    cells.append(SEAT[hits[0]])
                else:
                    cells.append("[" + "".join(
                        SEAT[h] for h in hits) + "]")
            bars.append(" ".join(cells))
        return " | ".join(bars) + " |"

    lines = [
        "X:1",
        "T:808 Pattern Demo — the KRS Foundation Grid (drum sheet)",
        "% Struck with the pattern it notates, 24 November 2026.",
        "% Grid: 144 BPM, 13/8 Sigma Mega (the KRS foundation).",
        "% Legend: V:1 C, = the 808 kick, dial-tuned to VV "
        "(placed 44 Hz).",
        "% V:2 c = snare; g = hi-hat (closed; the bar-final g "
        "of each bar",
        "% is the open hat, per the pattern record in "
        "manifest.json).",
        "% '808' names the TR-808 sound family; every voice is "
        "synthesized",
        "% in-house by resonance/studio/eightoeight.py.",
        "M:13/8",
        "L:1/8",
        "Q:1/4=144",
        "K:C",
        "V:1 clef=bass",
        kick_line,
        "V:2",
        bar_top(),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    mix, placed = build_mix()
    stereo = np.stack([mix, mix])
    mastered, report = pipe.master_signal(stereo, SR, -14.0, -1.0)

    wav_path = HERE / "pattern.wav"
    # The master is written by soundfile at 24-bit — the
    # pipeline's own WAV road for masters. eightoeight's
    # write_wav is NOT used here: it peak-sets its buffer to
    # the kit's seat, which would rescale a finished master
    # and break the law the master was just weighed under.
    import soundfile as sf
    sf.write(str(wav_path), mastered.T, SR, subtype="PCM_24")

    mp3_path = HERE / "master-320k.mp3"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(wav_path),
         "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3_path)],
        check=True, capture_output=True)

    sheet_path = HERE / "sheet.abc"
    write_sheet(sheet_path, placed)

    law = exam.judge_masterlaw(mp3_path, sworn_bps=320000)
    deriv = e8.fundamental_for_pair("VV")
    manifest = {
        "run": "eightoeight-pattern-demo",
        "date": "24 November 2026",
        "grid": {"bpm": BPM, "meter": "13/8 Sigma Mega",
                 "steps_per_bar": STEPS_PER_BAR, "bars": BARS,
                 "step_s": round(STEP_S, 6)},
        "pattern": PATTERN,
        "kick_tuning": deriv,
        "placed_hits": placed,
        "mastering_report": report,
        "master_law_mp3": law,
        "files": {"wav": wav_path.name, "mp3": mp3_path.name,
                  "sheet": sheet_path.name},
    }
    (HERE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(json.dumps({"master_law_compliant": law["compliant"],
                      "lufs_after": report["lufs_after"],
                      "true_peak_after": report.get("true_peak_dbtp"),
                      "files": manifest["files"]}, indent=2))
    return 0 if law["compliant"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
