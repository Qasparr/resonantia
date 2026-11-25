# 93
# ---------------------------------------------------------------------
# yin_pitch_read.py -- the corrected pitch instrument for the
# Kagami v3 gate: per-note F0 by YIN autocorrelation, read in
# the lab venv (the house's DiffSinger seat, where librosa
# lives), over the same steady-centre windows the Vocal Exam's
# pitch judge uses.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR, All Rights Reserved, Without Prejudice.
# Written XXV day of November, Anno V:xii e.n. (2026 e.v.), under
# the Method of Science, Aim of Religion -- Scientific Illuminism.
#
# WHY THIS INSTRUMENT EXISTS: the gate's first strike read
# pitch through vocal_exam.judge_pitch, whose instrument is
# fourier.dominant_frequency -- the strongest spectral peak in
# the note's centre window. On these voices that peak is a
# harmonic or a formant, not the fundamental: it returned
# medians near +1200 cents (an octave) on lines where a YIN
# read of the SAME windows returns 0 +/- 4 cents. A gate may
# not rest on a refuted instrument, so the pitch question is
# re-asked here with an autocorrelation tracker, and both
# reads stand in the record -- the first is marked, not erased.
#
# MECHANISM: for each filed line, librosa.yin over the line's
# WAV (fmin 50 Hz, fmax 1000 Hz, frame 2048, hop 512 at the
# bank's native 44.1 kHz); each written note's pitch is the
# MEDIAN YIN value over its steady centre (the middle 50% of
# its span, the exam judge's own window law), compared with
# the written pitch as 1200*log2(measured/target). A note
# whose centre is under 30 ms, or carries no voiced YIN
# frames, is UNMEASURABLE -- counted, never interpolated.
#
# USAGE: <lab python> yin_pitch_read.py <lines_dir> <spec.json>
#        <out.json>
#
# 93 -- Live, Love, and let Love, Live.
# ---------------------------------------------------------------------

import json
import math
import sys
from pathlib import Path

import librosa
import numpy as np

SR = 44100


def midi_hz(midi):
    return 440.0 * 2.0 ** ((float(midi) - 69.0) / 12.0)


def main(argv):
    lines_dir, spec_path, out_path = (Path(argv[1]), Path(argv[2]),
                                      Path(argv[3]))
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    result = {}
    for line in spec["lines"]:
        lid = line["id"]
        y, sr = librosa.load(str(lines_dir / f"{lid}.wav"),
                             sr=SR, mono=True)
        f0 = librosa.yin(y, fmin=50.0, fmax=1000.0, sr=sr,
                         frame_length=2048, hop_length=512)
        times = librosa.times_like(f0, sr=sr, hop_length=512)
        per_note, t = [], 0.0
        for note in line["notes"]:
            dur = float(note["dur"])
            c0, c1 = t + 0.25 * dur, t + 0.75 * dur
            target = midi_hz(note["midi"])
            if dur * 0.5 < 0.03:
                per_note.append({"midi": note["midi"],
                                 "target_hz": round(target, 4),
                                 "state": "UNMEASURABLE",
                                 "reason": "steady centre under "
                                           "30 ms"})
                t += dur
                continue
            sel = f0[(times >= c0) & (times < c1)]
            sel = sel[sel > 0]
            if len(sel) == 0:
                per_note.append({"midi": note["midi"],
                                 "target_hz": round(target, 4),
                                 "state": "UNMEASURABLE",
                                 "reason": "no voiced YIN frames "
                                           "in the centre"})
                t += dur
                continue
            med = float(np.median(sel))
            per_note.append({
                "midi": note["midi"],
                "target_hz": round(target, 4),
                "measured_hz": round(med, 4),
                "cents": round(1200.0 * math.log2(med / target), 2)})
            t += dur
        result[lid] = {"speaker": line["speaker"],
                       "per_note": per_note}
    out_path.write_text(json.dumps(result, ensure_ascii=False,
                                   indent=2), encoding="utf-8")
    print(f"yin pitch read: {len(result)} lines -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# 93 -- Live, Love, and let Love, Live.
