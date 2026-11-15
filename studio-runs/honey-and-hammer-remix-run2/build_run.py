#!/usr/bin/env python3
"""
HONEY AND HAMMER — THE EXPLICIT REMIX: run 2, backing, mix, the Four
Powers master, and the BOVNCE 320K MP3 export. House tools only:

  * drums  — the studio's STRUCK KIT (v4-proof-3 one-shots), placed on
             the grid. Rendered audio, never note-synthesis.
  * bass   — spine.bass808, the studio's own 808 voice, on the loop
             roots (G1 · Eb1 · Bb1 · F1).
  * pad    — numpy/scipy synthesis (no soundfont, no fluidsynth on
             this box; confessed in the run report, as in run 1).
  * vocal  — the DiffSinger lines from render_vocal.py, resampled
             44.1k -> 48k, one line per bar.
  * master — resonance.studio.four_powers over pipeline.master_signal:
             Scire -> Velle -> Vapour (off, confessed) -> Audere
             (-14 LUFS / -1 dBTP law) -> Tacere TPDF dither, 24-bit.
  * export — ffmpeg/libmp3lame at 320 kbps CBR (the BOVNCE 320K spec);
             the bitrate is read back from the struck file (ffprobe).

Spec (Resonantia variables): G minor, 96 BPM, 4/4, swung 16ths
(swing 0.14, run 1's start point), chord loop Gm-Eb-Bb-F per bar.
70 bars: hook 8, five 12-line sections, outro 2.

RUN-1 LESSONS APPLIED:
  * duration calibration x1.15 lives in render_vocal.py (CAL); this
    script measures the landed ratio from the manifest.
  * cooler staging: vocal bus at -20.5 dBFS RMS (run 1 staged -18 and
    the premix peaked +3.18 dBFS); if the premix still peaks over
    +0.5 dBFS a uniform trim is applied and recorded, not hidden.
"""
import json
import pathlib
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy import signal as sig

sys.path.insert(0, str(pathlib.Path.home() / "workspace/resonance"))
from resonance.studio import four_powers as fp          # noqa: E402
from resonance.studio import pipeline                   # noqa: E402
from resonance.studio.spine import bass808              # noqa: E402

RUN = pathlib.Path(__file__).resolve().parent
KIT = pathlib.Path.home() / ("workspace/resonance/studio-runs/"
                             "v4-proof-3/kit")
SR = 48000
BPM = 96.0
BAR_S = 4 * 60.0 / BPM              # 2.5 s
STEP_S = BAR_S / 16
SWING = 0.14
N_BARS = 70
LOOP = ["Gm", "Eb", "Bb", "F"]
ROOT = {"Gm": 31, "Eb": 27, "Bb": 34, "F": 29}   # G1, Eb1, Bb1, F1
PAD = {"Gm": [55, 58, 62], "Eb": [55, 58, 63],
       "Bb": [53, 58, 62], "F": [53, 57, 60]}
OUTRO_BAR = 68


def chord_of(bar):
    return LOOP[bar % 4]


def bar_start(bar):
    return int(round(bar * BAR_S * SR))


def step_at(bar, step):
    off = SWING * STEP_S if step % 2 == 1 else 0.0
    return bar_start(bar) + int(round((step * STEP_S + off) * SR))


TOTAL = bar_start(N_BARS) + int(0.5 * SR)     # half-second tail


def load_mono(path):
    x, sr = sf.read(path, always_2d=False)
    assert sr == SR, f"{path}: {sr} != {SR}"
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x.astype(np.float64)


def pan_gains(pan):
    a = (pan + 1.0) * np.pi / 4.0
    return np.cos(a), np.sin(a)


def place(buf, x, at, gain=1.0, pan=0.0):
    if at >= buf.shape[1]:
        return
    n = min(len(x), buf.shape[1] - at)
    gl, gr = pan_gains(pan)
    buf[0, at:at + n] += x[:n] * gain * gl
    buf[1, at:at + n] += x[:n] * gain * gr


# ---------------------------------------------------------------------
# Pad: detuned saw stack through a lowpass, slow envelope. Synthesis —
# the confessed synth layer (no soundfont exists on this box).
# ---------------------------------------------------------------------
def pad_chord(midis, dur_s, sr=SR):
    n = int(round(dur_s * sr))
    t = np.arange(n) / sr
    out = np.zeros(n)
    for m in midis:
        f0 = 440.0 * 2 ** ((m - 69) / 12)
        for det in (-4.0, 4.0):
            f = f0 * 2 ** (det / 1200.0)
            tone = np.zeros(n)
            for k in range(1, 13):
                tone += np.sin(2 * np.pi * f * k * t) / k
            out += tone * 0.5
        out += 0.6 * np.sin(2 * np.pi * f0 * t)      # triangle-ish core
    b, a = sig.butter(2, 1100.0, fs=sr)
    out = sig.lfilter(b, a, out)
    atk = int(0.35 * sr); rel = int(0.6 * sr)
    env = np.ones(n)
    env[:atk] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, atk))
    env[-rel:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, rel))
    return out * env * 0.045


def pluck(midi, dur_s, sr=SR):
    """One decaying note — the outro's single piano-ish strike
    (synthesised; no piano exists on this box — run-1 wall, standing)."""
    n = int(round(dur_s * sr))
    t = np.arange(n) / sr
    f0 = 440.0 * 2 ** ((midi - 69) / 12)
    out = np.zeros(n)
    for k, amp in ((1, 1.0), (2, 0.55), (3, 0.30), (4, 0.16), (5, 0.08)):
        out += amp * np.sin(2 * np.pi * f0 * k * t) * np.exp(-t * (1.1 + 0.5 * k))
    return out * 0.22


# ---------------------------------------------------------------------
# Backing
# ---------------------------------------------------------------------
def build_backing():
    buf = np.zeros((2, TOTAL))
    kit = {v: load_mono(KIT / f"{v}.wav") for v in
           ("kick", "snare", "clap", "closed_hat", "open_hat", "rimshot")}
    hat_vel = [0.85, 0.45, 0.65, 0.45] * 4
    for bar in range(N_BARS):
        ch = chord_of(bar)
        if bar >= OUTRO_BAR:
            section = "outro"
        elif bar < 8:
            section = "hook"
        else:
            section = "verse"
        fade = 1.0 if section != "outro" else (0.7 if bar == OUTRO_BAR
                                              else 0.45)
        place(buf, pad_chord(PAD[ch], BAR_S + 0.3), bar_start(bar),
              gain=fade)
        if section == "outro":
            # the sheet: the 808 drops out; one kick, one note, gone.
            if bar == OUTRO_BAR:
                place(buf, kit["kick"], step_at(bar, 0), gain=0.9)
                place(buf, pluck(55, 2.5), bar_start(bar), gain=1.0)
            continue
        for st, v in ((0, 1.0), (8, 0.95), (10, 0.8)):
            place(buf, kit["kick"], step_at(bar, st), gain=v * fade)
        if section == "verse":
            place(buf, kit["kick"], step_at(bar, 14), gain=0.45)
        for st in (4, 12):
            place(buf, kit["snare"], step_at(bar, st), gain=1.0)
        place(buf, kit["clap"], step_at(bar, 4), gain=0.5)
        place(buf, kit["clap"], step_at(bar, 12), gain=0.7)
        for st in range(16):
            place(buf, kit["closed_hat"], step_at(bar, st),
                  gain=hat_vel[st])
        place(buf, kit["open_hat"], step_at(bar, 14), gain=0.75)
        for st, v in ((3, 0.3), (11, 0.35)):
            place(buf, kit["rimshot"], step_at(bar, st), gain=v)
        if section == "verse":
            place(buf, kit["rimshot"], step_at(bar, 7), gain=0.25)
        # 808 line on the bar root
        for st, ln, v in ((0, 6, 1.0), (8, 3.5, 0.9), (11, 2.5, 0.85)):
            place(buf, bass808(ROOT[ch], ln * STEP_S, sr=SR),
                  step_at(bar, st), gain=v)
    return buf


# ---------------------------------------------------------------------
# Vocal assembly. (line id, speaker, bar, gain, pan)
# ---------------------------------------------------------------------
PLACEMENT = []
for _i, _spk in ((1, "Quoll"), (3, "Quoll"), (5, "Quoll"), (7, "Quoll")):
    PLACEMENT.append((f"hook{_i}", _spk, _i - 1, 1.0, -0.1))
for _i in (2, 4):
    PLACEMENT.append((f"hook{_i}", "Phascogale", _i - 1, 1.0, 0.1))
for _i in (6, 8):
    PLACEMENT.append((f"hook{_i}", "Quoll", _i - 1, 0.9, -0.15))
    PLACEMENT.append((f"hook{_i}", "Phascogale", _i - 1, 0.9, 0.15))
for _p, _base_bar in (("sol", 8), ("ari", 20), ("qas", 32),
                      ("sage", 44), ("qveen", 56)):
    _spk = {"sol": "Civet", "ari": "Civet", "qas": "Phascogale",
            "sage": "Phascogale", "qveen": "Quoll"}[_p]
    for _i in range(12):
        PLACEMENT.append((f"{_p}{_i+1}", _spk, _base_bar + _i, 1.0, 0.0))
for _i in (1, 2):
    PLACEMENT.append((f"out{_i}", "Quoll", OUTRO_BAR + _i - 1, 0.85, -0.1))
    PLACEMENT.append((f"out{_i}", "Civet", OUTRO_BAR + _i - 1, 0.85, 0.1))
# the sheet's outro texture: the hook chant at half volume underneath
PLACEMENT.append(("hook1", "Quoll", OUTRO_BAR, 0.45, -0.1))
PLACEMENT.append(("hook2", "Phascogale", OUTRO_BAR + 1, 0.45, 0.1))


def build_vocal():
    man = json.loads((RUN / "lines_manifest.json").read_text())
    by = {(m["id"], m["speaker"]): m for m in man}
    buf = np.zeros((2, TOTAL))
    notes = {"missing": [], "overhang_s": {}}
    for lid, spk, bar, gain, pan in PLACEMENT:
        m = by.get((lid, spk))
        if m is None:
            notes["missing"].append(f"{lid}/{spk}")
            continue
        x, sr = sf.read(RUN / "lines" / m["file"])
        assert sr == 44100
        x48 = sig.resample_poly(x, 160, 147).astype(np.float64)
        place(buf, x48, bar_start(bar), gain=gain, pan=pan)
        over = (len(x48) / SR) - BAR_S
        if over > 0.01:
            notes["overhang_s"][f"{lid}/{spk}@bar{bar}"] = round(over, 3)
    # duration calibration measurement, straight from the manifest
    tot_r = sum(m["frames"] for m in man)
    tot_h = sum(m["handed_frames"] for m in man)
    tot_n = sum(m["nominal_frames"] for m in man)
    notes["duration"] = {
        "renders": len(man),
        "rendered_frames": tot_r, "handed_frames_cal": tot_h,
        "nominal_frames_uncal": tot_n,
        "ratio_vs_handed_cal": round(tot_r / tot_h, 4),
        "ratio_vs_nominal_uncal": round(tot_r / tot_n, 4),
        "bar_frames_at_44k": round(BAR_S * 44100 / 512 * 512 / 512, 2)}
    return buf, notes, man


def rms_db(x):
    return float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12))


def main():
    data = {"spec": {"key": "G minor", "bpm": BPM, "bars": N_BARS,
                     "loop": LOOP, "swing": SWING,
                     "duration_cal": 1.15}}
    backing = build_backing()
    vocal, vnotes, man = build_vocal()
    data["vocal_notes"] = vnotes
    data["lines_rendered"] = len(man)

    # gain staging (run-1 lesson: cooler vocal): backing bed
    # -21 dBFS RMS, vocal -20.5 dBFS RMS; premix peak guard recorded.
    b_gain = 10 ** ((-21.0 - rms_db(backing)) / 20)
    v_gain = 10 ** ((-20.5 - rms_db(vocal)) / 20)
    backing *= b_gain; vocal *= v_gain
    data["staging"] = {"backing_gain_db": round(20 * np.log10(b_gain), 2),
                       "vocal_gain_db": round(20 * np.log10(v_gain), 2),
                       "backing_rms_dbfs": round(rms_db(backing), 2),
                       "vocal_rms_dbfs": round(rms_db(vocal), 2)}
    data["stem_print_gain_db"] = {}
    for name, stem in (("backing-stem.wav", backing),
                       ("vocal-stem.wav", vocal)):
        pk = 20 * np.log10(np.max(np.abs(stem)))
        pg = min(0.0, -1.0 - pk)
        data["stem_print_gain_db"][name] = round(float(pg), 2)
        sf.write(RUN / name, (stem * 10 ** (pg / 20)).T, SR,
                 subtype="PCM_24")

    premix = backing + vocal
    pk = 20 * np.log10(np.max(np.abs(premix)))
    trim = min(0.0, 0.5 - pk) if pk > 0.5 else 0.0
    if trim:
        premix = premix * 10 ** (trim / 20)
    data["premix"] = {"rms_dbfs": round(rms_db(premix), 2),
                      "peak_dbfs_before_trim": round(float(pk), 2),
                      "trim_db": round(float(trim), 2),
                      "peak_dbfs": round(20 * np.log10(
                          np.max(np.abs(premix))), 2)}

    # ---- the Four Powers chain ---------------------------------------
    scire = fp.scire_measure(premix, SR, pipeline.measure_loudness_lufs,
                             pipeline.true_peak_dbtp)
    velle = fp.normalize_velle({
        "eq": [{"type": "peak", "freq_hz": 3000.0, "gain_db": 1.5,
                "q": 1.0},
               {"type": "highshelf", "freq_hz": 8000.0, "gain_db": 1.0}],
        "comp": {"threshold_db": -18.0, "ratio": 2.0, "knee_db": 6.0,
                 "attack_ms": 10.0, "release_ms": 120.0,
                 "makeup_db": 0.0}})
    y, velle_rep = fp.velle_stage(premix, SR, velle)
    y, vapour_rep = fp.vapour_stage(y, fp.normalize_vapour(None))
    mastered, master_rep = pipeline.master_signal(y, SR, -14.0, -1.0)
    dithered = fp.tpdf_dither(mastered, seed=32015)
    tacere = fp.tacere_report(master_rep, True)
    section = fp.assemble(scire, velle_rep, vapour_rep, master_rep,
                          tacere)
    data["four_powers"] = section

    out_path = RUN / "honey-and-hammer-explicit-remix-resonantia.wav"
    sf.write(out_path, dithered.T, SR, subtype="PCM_24")

    back, sr = sf.read(out_path, always_2d=True)
    back = back.T.astype(np.float64)
    data["final"] = {
        "file": out_path.name, "sr": sr,
        "duration_s": round(back.shape[1] / sr, 3),
        "lufs_integrated": round(
            pipeline.measure_loudness_lufs(back, sr), 2),
        "true_peak_dbtp": round(pipeline.true_peak_dbtp(back, sr), 2),
        "sample_peak_dbfs": round(20 * np.log10(np.max(np.abs(back))), 2),
        "bits": 24}

    # ---- BOVNCE 320K: the MP3 export, bitrate read back --------------
    mp3_path = RUN / "honey-and-hammer-explicit-remix-320k.mp3"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out_path),
                    "-codec:a", "libmp3lame", "-b:a", "320k",
                    "-ar", "48000", str(mp3_path)], check=True)
    probe = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams",
         "-of", "json", str(mp3_path)],
        capture_output=True, text=True, check=True).stdout)
    astream = next(s for s in probe["streams"]
                   if s["codec_type"] == "audio")
    data["mp3"] = {
        "file": mp3_path.name, "codec": astream["codec_name"],
        "sample_rate": int(astream["sample_rate"]),
        "bit_rate_bps": int(astream.get("bit_rate",
                                        probe["format"]["bit_rate"])),
        "duration_s": round(float(probe["format"]["duration"]), 3),
        "size_bytes": int(probe["format"]["size"])}
    mp3_back, msr = sf.read(mp3_path, always_2d=True)
    mp3_back = mp3_back.T.astype(np.float64)
    data["mp3"]["lufs_integrated"] = round(
        pipeline.measure_loudness_lufs(mp3_back, msr), 2)
    data["mp3"]["true_peak_dbtp"] = round(
        pipeline.true_peak_dbtp(mp3_back, msr), 2)

    for name, stem in (("vocal-stem.wav", vocal),
                       ("backing-stem.wav", backing)):
        data[name] = {"duration_s": round(stem.shape[1] / SR, 3),
                      "rms_dbfs": round(rms_db(stem), 2),
                      "peak_dbfs": round(20 * np.log10(
                          np.max(np.abs(stem))), 2)}
    (RUN / "run_data.json").write_text(json.dumps(data, indent=2))
    print(json.dumps(data["final"], indent=2), flush=True)
    print(json.dumps(data["mp3"], indent=2), flush=True)
    print("BUILD DONE", flush=True)


if __name__ == "__main__":
    main()
