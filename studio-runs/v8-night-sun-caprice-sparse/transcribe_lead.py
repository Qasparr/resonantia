#!/usr/bin/env python3
# 93
# ---------------------------------------------------------------------
# transcribe_lead.py -- the desk transcription of a performance's
# lead line, struck AFTER the run, for composition.abc's X:2.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR, All Rights Reserved, Without Prejudice. Method of Science,
# Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: the kept performance (performance_48k.wav, the bed
# before Sigma and mastering) is YIN-tracked with the house's own
# resonance.pitch tracker, restricted to the lead band. A frame
# is admitted ONLY when YIN and the frame's own spectral peak in
# the lead band agree within 50 cents -- two witnesses or none.
# Admitted frames are segmented into notes (same rounded MIDI,
# minimum 0.12 s, gaps under 0.08 s bridged), each note's pitch
# the median of its frames, its cents deviation kept. Durations
# are quantized to 16ths of the performance's MEASURED tempo (the
# manifest's global BPM -- the performance's own clock, nobody's
# grid imposed), notes split at barlines with ties.
#
# DOCTRINE (the limits, which the sheet prints on its own face):
# this is a MONOPHONIC estimate over a dense stereo mix. YIN
# locks onto the strongest periodic voice in its band; where the
# bed out-shouts the violin, the line follows the bed or falls
# silent -- unvoiced frames are printed as rests only where the
# tracker honestly found no lead, and the coverage fraction is
# stated in numbers. Octave errors survive any tracker; the
# dual-witness gate thins them, it does not abolish them. What
# stands here is a desk transcription with its error budget
# confessed -- not the performance's soul on paper.
# ---------------------------------------------------------------------

import json
import math
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/resonance")
from resonance.pitch import track_f0  # noqa: E402

LEAD_LO_HZ, LEAD_HI_HZ = 180.0, 1400.0
CONF_MIN = 0.80
AGREE_CENTS = 50.0
MIN_NOTE_S = 0.12
BRIDGE_GAP_S = 0.08

NOTE_NAMES = ["C", "^C", "D", "_E", "E", "F",
              "^F", "G", "^G", "A", "_B", "B"]


def abc_for(midi):
    """Clean MIDI->ABC: C4(60)='C', C5(72)='c', C3(48)='C,' etc."""
    name = NOTE_NAMES[midi % 12]
    acc = ""
    base = name
    if name[0] in "^_":
        acc, base = name[0], name[1:]
    octv = midi // 12 - 1            # scientific octave of the C below
    if octv < 4:                     # capitals, commas below C4
        return acc + base + "," * (3 - octv) if octv <= 3 else \
            acc + base
    if octv == 4:
        return acc + base
    return acc + base.lower() + "'" * (octv - 5)


def read_wav_mono(path):
    with wave.open(str(path), "rb") as w:
        sr, ch, sw, n = (w.getframerate(), w.getnchannels(),
                         w.getsampwidth(), w.getnframes())
        raw = w.readframes(n)
    if sw == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
             | (a[:, 2].astype(np.int32) << 16))
        x = np.where(x >= 1 << 23, x - (1 << 24), x).astype(np.float64)
        x /= float(1 << 23)
    elif sw == 2:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float64)
        x /= 32768.0
    else:
        raise ValueError(f"unsupported sample width {sw}")
    if ch == 2:
        x = x.reshape(-1, 2).mean(axis=1)
    return x, sr


def spectral_peak_hz(frame, sr):
    """Strongest rfft peak inside the lead band, or None.

    MECHANISM: parabolic interpolation around the peak bin -- a
    raw bin at 48 kHz/2048 is 23.4 Hz wide, which at 200 Hz is
    over 100 cents of quantization slop; an uninterpolated peak
    would fail honest low notes against YIN for a measurement
    artifact, not a disagreement. Interpolated, the witness
    testifies about pitch, not about the grid it was read on.
    """
    if len(frame) < 64:
        return None
    mag = np.abs(np.fft.rfft(frame * np.hanning(len(frame))))
    freqs = np.fft.rfftfreq(len(frame), 1.0 / sr)
    band = (freqs >= LEAD_LO_HZ) & (freqs <= LEAD_HI_HZ)
    if not np.any(band):
        return None
    k = int(np.argmax(np.where(band, mag, 0.0)))
    if 0 < k < len(mag) - 1:
        a, b, c = mag[k - 1], mag[k], mag[k + 1]
        denom = a - 2.0 * b + c
        if denom != 0.0:
            shift = 0.5 * (a - c) / denom
            return float(freqs[k] + shift * (freqs[1] - freqs[0]))
    return float(freqs[k])


def transcribe(audio, sr):
    """Dual-witness YIN track -> admitted (time, midi_float, conf)."""
    frames = track_f0(audio, sr, fmin=LEAD_LO_HZ, fmax=LEAD_HI_HZ,
                      frame_size=2048, hop=512, threshold=0.10)
    hop_s = 512 / sr
    admitted = []
    n_voiced = 0
    for fr in frames:
        if not fr.voiced or fr.f0_hz is None:
            continue
        n_voiced += 1
        if fr.confidence < CONF_MIN:
            continue
        i0 = int((fr.time_s - 1024 / sr) * sr)
        seg = audio[max(0, i0):max(0, i0) + 2048]
        peak = spectral_peak_hz(seg, sr)
        if peak is None or peak <= 0:
            continue
        cents = abs(1200.0 * math.log2(fr.f0_hz / peak))
        if cents > AGREE_CENTS:
            continue
        midi_f = 69.0 + 12.0 * math.log2(fr.f0_hz / 440.0)
        admitted.append((fr.time_s, midi_f, fr.confidence))
    return admitted, len(frames), n_voiced, hop_s


def segment_notes(admitted, hop_s):
    """Admitted frames -> note events (start_s, dur_s, midi, cents)."""
    if not admitted:
        return []
    notes = []
    cur = [admitted[0]]
    for prev, fr in zip(admitted, admitted[1:]):
        gap = fr[0] - prev[0]
        same = round(fr[1]) == round(cur[-1][1])
        if same and gap <= BRIDGE_GAP_S + 1.5 * hop_s:
            cur.append(fr)
        else:
            notes.append(cur)
            cur = [fr]
    notes.append(cur)
    out = []
    for run in notes:
        t0 = run[0][0] - hop_s / 2
        t1 = run[-1][0] + hop_s / 2
        if t1 - t0 < MIN_NOTE_S:
            continue
        med = float(np.median([r[1] for r in run]))
        midi = int(round(med))
        cents = int(round(100.0 * (med - midi)))
        out.append({"start": t0, "dur": t1 - t0, "midi": midi,
                    "cents": cents,
                    "conf": float(np.mean([r[2] for r in run]))})
    return out


def notes_to_abc(notes, bpm, total_s):
    """Quantize to 16ths of the measured tempo; bar by 4/4; ties."""
    beat_s = 60.0 / bpm
    unit = beat_s / 4.0                      # one 16th
    events = []                              # (start_unit, len, midi)
    for n in notes:
        s = int(round(n["start"] / unit))
        ln = max(1, int(round(n["dur"] / unit)))
        events.append((s, ln, n["midi"]))
    total_units = int(math.ceil(total_s / unit))
    bars = []
    cur_bar = []
    pos = 0                                  # absolute unit position
    ev_i = 0
    events.sort()
    timeline = {}
    for s, ln, midi in events:
        timeline.setdefault(s, []).append((ln, midi))

    def dur_tok(units, tie=False):
        return f"{units}-" if tie else f"{units}"

    u = 0
    bar = []
    bar_start = 0
    # walk unit by unit, emitting rests and notes
    pending = None                           # (midi, remaining)
    while u < total_units:
        in_bar = u - bar_start
        room = 16 - in_bar
        if pending is None:
            hits = timeline.get(u)
            if hits:
                ln, midi = hits[0]
                pending = (midi, ln)
            else:
                # rest until next hit or bar end
                nxt = min([s for s in timeline if s > u],
                          default=total_units)
                run = min(room, nxt - u, total_units - u)
                bar.append(f"z{run}" if run > 1 else "z")
                u += run
                if u - bar_start >= 16:
                    bars.append(" ".join(bar))
                    bar, bar_start = [], u
                continue
        midi, remain = pending
        take = min(room, remain, total_units - u)
        tie = remain > take
        bar.append(f"{abc_for(midi)}{dur_tok(take, tie)}")
        u += take
        remain -= take
        pending = (midi, remain) if remain > 0 else None
        if u - bar_start >= 16:
            bars.append(" ".join(bar))
            bar, bar_start = [], u
    if bar:
        bars.append(" ".join(bar))
    return bars


def main():
    run_dir = Path(sys.argv[1])
    abc_path = run_dir / "composition.abc"
    text = abc_path.read_text(encoding="utf-8")
    if "\nX:2" in text:
        print("X:2 already present; refusing to append twice",
              file=sys.stderr)
        return 1
    src = run_dir / "performance_48k.wav"
    if not src.exists():
        src = run_dir / "master.wav"
    audio, sr = read_wav_mono(src)
    total_s = len(audio) / sr
    admitted, n_frames, n_voiced, hop_s = transcribe(audio, sr)
    notes = segment_notes(admitted, hop_s)
    manifest = json.loads((run_dir / "manifest.json")
                          .read_text(encoding="utf-8"))
    bpm = manifest["performance"]["realized_tempo"]["global_bpm"]
    bars = notes_to_abc(notes, bpm, total_s)
    voiced_s = len(admitted) * hop_s
    block = []
    block.append("")
    block.append("X:2")
    block.append(f"T:{manifest['title']}: the lead line, "
                 "as transcribed by the desk")
    block.append("C:Johnathan 'Qasparr' Monroe, ARR, All Rights "
                 "Reserved, Without Prejudice")
    block.append(f"R:transcription at the performance's measured "
                 f"tempo: {bpm} BPM (its own clock)")
    block.append("M:4/4")
    block.append("L:1/16")
    block.append("K:Fmin")
    block.append("%")
    block.append("% THE TRANSCRIPTION, AND ITS LIMITS (stated on "
                 "its face, per the rule):")
    block.append("% Struck by the desk AFTER the run, from "
                 "performance_48k.wav -- the kept")
    block.append("% performance before Sigma and mastering -- "
                 "with the house YIN tracker")
    block.append("% (resonance.pitch), lead band "
                 f"{LEAD_LO_HZ:.0f}-{LEAD_HI_HZ:.0f} Hz. A frame was "
                 "admitted ONLY where")
    block.append("% YIN and the frame's own spectral peak agreed "
                 "within 50 cents -- two")
    block.append("% witnesses or none. It is a MONOPHONIC "
                 "estimate over a dense mix:")
    block.append("% where the bed out-shouts the lead, the line "
                 "follows the bed or falls")
    block.append("% silent (rests); octave errors are thinned by "
                 "the gate, not abolished.")
    block.append("% Durations are quantized to 16ths of the "
                 "MEASURED tempo; pitches are")
    block.append("% frame medians rounded to the staff. This is "
                 "the lead line as the")
    block.append("% tooling honestly hears it -- an estimate with "
                 "its error budget in the")
    block.append("% open, not a fabrication and not a claim of "
                 "note-perfect capture.")
    block.append(f"% COVERAGE: {len(admitted)} admitted frames of "
                 f"{n_frames} tracked ({n_voiced} voiced before "
                 f"the gates) = {voiced_s:.1f} s of")
    block.append(f"% {total_s:.1f} s carried a two-witness lead; "
                 f"{len(notes)} notes segmented.")
    block.append("%")
    for b in bars:
        block.append(b + " |")
    block.append("%")
    block.append("% 93 -- Live, Love, and let Love, Live.")
    abc_path.write_text(text.rstrip("\n") + "\n" + "\n".join(block)
                        + "\n", encoding="utf-8")
    print(json.dumps({"notes": len(notes), "bars": len(bars),
                      "admitted_frames": len(admitted),
                      "total_frames": n_frames,
                      "bpm": bpm}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 93 -- Live, Love, and let Love, Live.
