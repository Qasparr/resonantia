#!/usr/bin/env python3
"""
HONEY AND HAMMER — THE EXPLICIT REMIX: RUN 3 — the stereo re-mix.

Founder's ear verdict on run 2: "Something's off — make it full stereo
and Dolby rendered." Diagnosis first (RUN-REPORT.md has the numbers):
run 2's backing stem measures correlation +1.0000 with 0.00% side
energy — every element was placed at pan 0.0; it is dual-mono. The
vocal stem is +0.9962 (verses all at pan 0.0; only the hook's +/-0.1
pans differ at all). The master is +0.9985. A mono record in a stereo
container is what was off.

This run changes ONLY the stage picture. Same lines (run 2's 74
renders, untouched), same kit, same 808, same pad synthesis, same
Four Powers chain and settings, same staging targets, same house law
(-14 LUFS / -1 dBTP). What moves:

  * backing — kick and 808 stay centred (the low end is mono by law);
    snare centred; clap split into a +/-5..7 ms pair at pan -/+0.30;
    closed hats walk a pan pattern; open hat +0.55; rimshots -/+0.45;
    the pad is rendered as two independently-detuned stacks, one per
    ear, over a quieter centre core.
  * vocal — hook call-and-response widened to -/+0.35, the "(both)"
    doubles split to -/+0.55; verses stay centred dry but every
    section gets a stereo room tail: a synthetic stereo impulse
    (decorrelated noise decay, one per ear) convolved as a send —
    verses -13 dB, hook -15 dB, outro -11 dB (the outro is layered
    wide: Quoll -0.5 / Civet +0.5 over the hook chant at -/+0.3).
  * binaural — rendered separately (see RUN-REPORT.md): ffmpeg
    sofalizer + the MIT KEMAR SOFA set on this box. It is a binaural
    headphone render, NOT Dolby/Atmos; no file here carries that name.
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

RUN3 = pathlib.Path(__file__).resolve().parent
RUN2 = RUN3.parent / "honey-and-hammer-remix-run2"
KIT = pathlib.Path.home() / ("workspace/resonance/studio-runs/"
                             "v4-proof-3/kit")
SR = 48000
BPM = 96.0
BAR_S = 4 * 60.0 / BPM
STEP_S = BAR_S / 16
SWING = 0.14
N_BARS = 70
LOOP = ["Gm", "Eb", "Bb", "F"]
ROOT = {"Gm": 31, "Eb": 27, "Bb": 34, "F": 29}
PAD = {"Gm": [55, 58, 62], "Eb": [55, 58, 63],
       "Bb": [53, 58, 62], "F": [53, 57, 60]}
OUTRO_BAR = 68
TOTAL = int(round(N_BARS * BAR_S * SR)) + int(0.5 * SR)


def chord_of(bar):
    return LOOP[bar % 4]


def bar_start(bar):
    return int(round(bar * BAR_S * SR))


def step_at(bar, step):
    off = SWING * STEP_S if step % 2 == 1 else 0.0
    return bar_start(bar) + int(round((step * STEP_S + off) * SR))


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


def place_stereo(buf, x2, at, gain=1.0):
    n = min(x2.shape[1], buf.shape[1] - at)
    buf[:, at:at + n] += x2[:, :n] * gain


# ---------------------------------------------------------------------
# Pad, stereo: two independently detuned harmonic stacks (one per ear)
# over a quiet centre core. Synthesis — run 2's confessed layer,
# unchanged in kind, widened in placement.
# ---------------------------------------------------------------------
def _pad_stack(midis, dur_s, detunes, cutoff, sr=SR):
    n = int(round(dur_s * sr))
    t = np.arange(n) / sr
    out = np.zeros(n)
    for m in midis:
        f0 = 440.0 * 2 ** ((m - 69) / 12)
        for det in detunes:
            f = f0 * 2 ** (det / 1200.0)
            tone = np.zeros(n)
            for k in range(1, 13):
                tone += np.sin(2 * np.pi * f * k * t) / k
            out += tone * 0.5
        out += 0.6 * np.sin(2 * np.pi * f0 * t)
    b, a = sig.butter(2, cutoff, fs=sr)
    out = sig.lfilter(b, a, out)
    atk = int(0.35 * sr); rel = int(0.6 * sr)
    env = np.ones(n)
    env[:atk] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, atk))
    env[-rel:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, rel))
    return out * env


def pad_chord_stereo(midis, dur_s):
    left = _pad_stack(midis, dur_s, (-5.0, 3.0), 1000.0)
    right = _pad_stack(midis, dur_s, (-3.0, 5.0), 1200.0)
    core = _pad_stack(midis, dur_s, (-4.0, 4.0), 1100.0)
    return np.vstack([left * 0.058 + core * 0.013,
                      right * 0.058 + core * 0.013])


def pluck(midi, dur_s, sr=SR):
    n = int(round(dur_s * sr))
    t = np.arange(n) / sr
    f0 = 440.0 * 2 ** ((midi - 69) / 12)
    out = np.zeros(n)
    for k, amp in ((1, 1.0), (2, 0.55), (3, 0.30), (4, 0.16), (5, 0.08)):
        out += amp * np.sin(2 * np.pi * f0 * k * t) * np.exp(-t * (1.1 + 0.5 * k))
    return out * 0.22


# ---------------------------------------------------------------------
# Stereo room: one synthetic impulse per ear (decorrelated decaying
# noise through a lowpass), used as a convolution send.
# ---------------------------------------------------------------------
def stereo_ir(dur_s=1.3, seed_l=101, seed_r=202, sr=SR):
    n = int(dur_s * sr)
    irs = []
    for seed in (seed_l, seed_r):
        rng = np.random.default_rng(seed)
        noise = rng.standard_normal(n)
        decay = np.exp(-np.arange(n) / (0.26 * sr))
        b, a = sig.butter(2, 4200.0, fs=sr)
        h = sig.lfilter(b, a, noise * decay)
        pre = int(0.02 * sr)
        h = np.concatenate([np.zeros(pre), h])[:n]
        irs.append(h / (np.sqrt(np.mean(h ** 2)) + 1e-12))
    return np.vstack(irs)


def apply_room(mono, ir, send_db):
    g = 10 ** (send_db / 20)
    wet = np.vstack([
        sig.fftconvolve(mono, ir[0])[:len(mono)],
        sig.fftconvolve(mono, ir[1])[:len(mono)]])
    return wet * g


# ---------------------------------------------------------------------
# Backing — run 2's pattern, new stage picture.
# ---------------------------------------------------------------------
HAT_PAN = [-0.45, 0.35, -0.30, 0.50]


def build_backing():
    buf = np.zeros((2, TOTAL))
    kit = {v: load_mono(KIT / f"{v}.wav") for v in
           ("kick", "snare", "clap", "closed_hat", "open_hat", "rimshot")}
    hat_vel = [0.85, 0.45, 0.65, 0.45] * 4
    ms = SR // 1000
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
        place_stereo(buf, pad_chord_stereo(PAD[ch], BAR_S + 0.3),
                     bar_start(bar), gain=fade)
        if section == "outro":
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
        # clap as a split pair, +/- ms around the step, -/+0.30
        for st, v in ((4, 0.5), (12, 0.7)):
            at = step_at(bar, st)
            place(buf, kit["clap"], at - 5 * ms, gain=v * 0.62, pan=-0.40)
            place(buf, kit["clap"], at + 7 * ms, gain=v * 0.62, pan=0.40)
        for st in range(16):
            place(buf, kit["closed_hat"], step_at(bar, st),
                  gain=hat_vel[st], pan=HAT_PAN[st % 4])
        place(buf, kit["open_hat"], step_at(bar, 14), gain=0.75, pan=0.60)
        place(buf, kit["rimshot"], step_at(bar, 3), gain=0.3, pan=-0.50)
        place(buf, kit["rimshot"], step_at(bar, 11), gain=0.35, pan=0.50)
        if section == "verse":
            place(buf, kit["rimshot"], step_at(bar, 7), gain=0.25, pan=-0.30)
        for st, ln, v in ((0, 6, 1.0), (8, 3.5, 0.9), (11, 2.5, 0.85)):
            place(buf, bass808(ROOT[ch], ln * STEP_S, sr=SR),
                  step_at(bar, st), gain=v)
    return buf


# ---------------------------------------------------------------------
# Vocal — run 2's lines, new placement + stereo room sends.
# (line id, speaker, bar, gain, pan, bus)  bus: hook / verse / outro
# ---------------------------------------------------------------------
PLACEMENT = []
for _i in (1, 3, 5, 7):
    PLACEMENT.append((f"hook{_i}", "Quoll", _i - 1, 1.0, -0.35, "hook"))
for _i in (2, 4):
    PLACEMENT.append((f"hook{_i}", "Phascogale", _i - 1, 1.0, 0.35, "hook"))
for _i in (6, 8):
    PLACEMENT.append((f"hook{_i}", "Quoll", _i - 1, 0.9, -0.55, "hook"))
    PLACEMENT.append((f"hook{_i}", "Phascogale", _i - 1, 0.9, 0.55, "hook"))
for _p, _base_bar in (("sol", 8), ("ari", 20), ("qas", 32),
                      ("sage", 44), ("qveen", 56)):
    _spk = {"sol": "Civet", "ari": "Civet", "qas": "Phascogale",
            "sage": "Phascogale", "qveen": "Quoll"}[_p]
    for _i in range(12):
        PLACEMENT.append((f"{_p}{_i+1}", _spk, _base_bar + _i, 1.0, 0.0,
                          "verse"))
for _i in (1, 2):
    PLACEMENT.append((f"out{_i}", "Quoll", OUTRO_BAR + _i - 1, 0.85, -0.5,
                      "outro"))
    PLACEMENT.append((f"out{_i}", "Civet", OUTRO_BAR + _i - 1, 0.85, 0.5,
                      "outro"))
PLACEMENT.append(("hook1", "Quoll", OUTRO_BAR, 0.45, -0.3, "outro"))
PLACEMENT.append(("hook2", "Phascogale", OUTRO_BAR + 1, 0.45, 0.3, "outro"))

ROOM_SEND_DB = {"hook": -15.0, "verse": -13.0, "outro": -11.0}


def build_vocal(ir):
    man = json.loads((RUN2 / "lines_manifest.json").read_text())
    by = {(m["id"], m["speaker"]): m for m in man}
    buses = {b: np.zeros((2, TOTAL)) for b in ROOM_SEND_DB}
    notes = {"missing": []}
    for lid, spk, bar, gain, pan, bus in PLACEMENT:
        m = by.get((lid, spk))
        if m is None:
            notes["missing"].append(f"{lid}/{spk}")
            continue
        x, sr = sf.read(RUN2 / "lines" / m["file"])
        assert sr == 44100
        x48 = sig.resample_poly(x, 160, 147).astype(np.float64)
        place(buses[bus], x48, bar_start(bar), gain=gain, pan=pan)
    vocal = np.zeros((2, TOTAL))
    for bus, buf in buses.items():
        vocal += buf
        mono = buf.mean(axis=0)
        vocal += apply_room(mono, ir, ROOM_SEND_DB[bus])
    return vocal, notes


# ---------------------------------------------------------------------
# Stereo image measurement (the report's before/after).
# ---------------------------------------------------------------------
def image_stats(x):
    L, R = x[0], x[1]
    M, S = (L + R) / 2, (L - R) / 2
    def db(v):
        return float(20 * np.log10(np.sqrt(np.mean(v ** 2)) + 1e-12))
    return {
        "corr": round(float(np.corrcoef(L, R)[0, 1]), 4),
        "rms_l_dbfs": round(db(L), 2), "rms_r_dbfs": round(db(R), 2),
        "side_minus_mid_db": round(db(S) - db(M), 2),
        "side_energy_pct": round(float(
            100 * np.mean(S ** 2) / (np.mean(M ** 2) + np.mean(S ** 2))), 2)}


def rms_db(x):
    return float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12))


def main():
    data = {"run": 3, "change": "stereo stage picture only; lines, kit, "
            "808, pad synthesis, chain settings and staging as run 2"}
    # before: run 2's struck files, measured on the same ruler
    data["before"] = {}
    for key, fn in (("master", "honey-and-hammer-explicit-remix-resonantia.wav"),
                    ("vocal_stem", "vocal-stem.wav"),
                    ("backing_stem", "backing-stem.wav")):
        x, _ = sf.read(RUN2 / fn, always_2d=True)
        data["before"][key] = image_stats(x.T.astype(np.float64))

    ir = stereo_ir()
    backing = build_backing()
    vocal, vnotes = build_vocal(ir)
    data["vocal_notes"] = vnotes
    data["backing_image_pre_stage"] = image_stats(backing)
    data["vocal_image_pre_stage"] = image_stats(vocal)

    b_gain = 10 ** ((-21.0 - rms_db(backing)) / 20)
    v_gain = 10 ** ((-20.5 - rms_db(vocal)) / 20)
    backing *= b_gain; vocal *= v_gain
    data["staging"] = {"backing_gain_db": round(20 * np.log10(b_gain), 2),
                       "vocal_gain_db": round(20 * np.log10(v_gain), 2),
                       "backing_rms_dbfs": round(rms_db(backing), 2),
                       "vocal_rms_dbfs": round(rms_db(vocal), 2)}
    for name, stem in (("backing-stem-stereo.wav", backing),
                       ("vocal-stem-stereo.wav", vocal)):
        pk = 20 * np.log10(np.max(np.abs(stem)))
        pg = min(0.0, -1.0 - pk)
        sf.write(RUN3 / name, (stem * 10 ** (pg / 20)).T, SR,
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

    # ---- the Four Powers chain, run 2's settings verbatim ------------
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
    dithered = fp.tpdf_dither(mastered, seed=32016)
    tacere = fp.tacere_report(master_rep, True)
    section = fp.assemble(scire, velle_rep, vapour_rep, master_rep,
                          tacere)
    data["four_powers"] = section

    out_path = RUN3 / "honey-and-hammer-explicit-remix-stereo-resonantia.wav"
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
        "bits": 24, **image_stats(back)}

    mp3_path = RUN3 / "honey-and-hammer-explicit-remix-stereo-320k.mp3"
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
    data["mp3"].update(image_stats(mp3_back))

    (RUN3 / "run_data.json").write_text(json.dumps(data, indent=2))
    print(json.dumps(data["before"], indent=2), flush=True)
    print(json.dumps(data["final"], indent=2), flush=True)
    print(json.dumps(data["mp3"], indent=2), flush=True)
    print("BUILD DONE", flush=True)


if __name__ == "__main__":
    main()
