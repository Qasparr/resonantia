#!/usr/bin/env python3
# =====================================================================
# 93
#
# Epigraph: "The method of science, the aim of religion." — the house
# rule under which this bench works: every number below was MEASURED
# from the audio, and every interpretation is MARKED as interpretation.
# Nothing in this script invents a note, a chord, or a lyric.
#
# analyze_anvil_crown.py — TRANSCRIPTION-ANALYSIS, phase 1 (analysis
# only) for "THE ANVIL AND CROWN", the founder's Gemini-only track.
# It produces the measured skeleton (form map features, per-bar chord
# labels, a coarse melody sketch) on which a later engraving pass may
# build. It is NOT a finished transcription and fabricates nothing.
#
# Date: VIII day of November, Dies Solis, Sol in Scorpio,
#       Anno V:xii e.n. (2026 e.v.)
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice).
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# MECHANISM (what the machine does, step by step):
#   1. Decode the MP3 to stereo float; split mid/side.
#   2. Lay the measured 69.8 BPM pulse (bench: REFERENCE-ANVIL-CROWN)
#      under the file and estimate the downbeat phase from the onset
#      envelope, so bar lines sit on the music, not on the file edge.
#   3. FORM: novelty = spectral flux + chroma change; peak-pick with a
#      minimum spacing; snap candidates to the bar grid; describe every
#      resulting segment by measured features (level, slope, centroid,
#      chroma stability, voiced density, recurrence vs other segments).
#   4. KEY/CHORDS: chromagram (FFT bins -> pitch classes); key by
#      Krumhansl-Schmuckler profile correlation; per-bar chord by
#      triad-template correlation, with the winning margin carried as
#      the confidence so a thin bar reads as a thin bar.
#   5. MELODY SKETCH: normalized-autocorrelation pitch track on the
#      mid channel, gated by a vocal-likelihood heuristic (centred,
#      speech-band energy); frames quantised to MIDI and grouped into
#      notes. Suspect octaves are FLAGGED, never silently rewritten —
#      dispositions are marked, never vanished.
# Runtime: numpy + soundfile only.
# =====================================================================

import json
import math
import os

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = "/home/hatch/workspace/resonance/reference/the-anvil-crown.mp3"
BPM = 69.8                      # bench-measured, flat across windows
BEAT = 60.0 / BPM               # seconds per beat  = 0.859599
BAR = 4.0 * BEAT                # 4/4 assumed        = 3.438397

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# ---------------------------------------------------------------------
# Framing helper: slice a 1-D signal into overlapping frames.
# DOCTRINE: one framer for every stage keeps all clocks comparable.
# ---------------------------------------------------------------------
def frame_signal(x, win, hop):
    n_frames = 1 + (len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n_frames)[:, None]
    return x[idx], n_frames


def db(x):
    return 20.0 * np.log10(np.maximum(x, 1e-12))


# ---------------------------------------------------------------------
# Load + mid/side split.
# MECHANISM: mid carries the centred programme (lead vocal, kick,
# bass); side carries width. Correlation 0.9293 (bench) says the vocal
# is centred but the mix is genuinely wide.
# ---------------------------------------------------------------------
x, sr = sf.read(AUDIO)
if x.ndim == 1:
    x = np.column_stack([x, x])
L, R = x[:, 0], x[:, 1]
mid = 0.5 * (L + R)
side = 0.5 * (L - R)
dur = len(mid) / sr

# ---------------------------------------------------------------------
# STFT of the mid channel (Hann, 4096 @ 44.1 kHz ~ 93 ms, hop 1024).
# ---------------------------------------------------------------------
NFFT, HOP = 4096, 1024
win = np.hanning(NFFT)
frames, n_fr = frame_signal(mid, NFFT, HOP)
SPEC = np.abs(np.fft.rfft(frames * win, axis=1))          # (frames, bins)
freqs = np.fft.rfftfreq(NFFT, 1.0 / sr)
frame_t = (np.arange(n_fr) * HOP + NFFT / 2) / sr         # frame centres

# ---------------------------------------------------------------------
# Onset envelope (spectral flux on log magnitude) + downbeat phase.
# MECHANISM: for each candidate phase in [0, beat), sum the flux at
# the beat positions; the phase whose beats land on the most onset
# energy wins. The file length is 46.0 bars at 69.8 BPM, so a phase
# near zero is expected — the search VERIFIES rather than assumes it.
# ---------------------------------------------------------------------
logmag = np.log1p(50.0 * SPEC)
flux = np.maximum(0.0, np.diff(logmag, axis=0)).sum(axis=1)
flux_t = frame_t[1:]
flux_env = flux / (flux.max() + 1e-12)

best_phase, best_score = 0.0, -1.0
for ph in np.arange(0.0, BEAT, 0.005):
    pos = np.arange(ph, dur, BEAT)
    idx = np.searchsorted(flux_t, pos)
    idx = idx[(idx >= 0) & (idx < len(flux_env))]
    score = flux_env[idx].sum()
    if score > best_score:
        best_score, best_phase = score, float(ph)
PHASE = best_phase  # downbeats at PHASE + k*BAR (first full bar start)


def bar_bounds():
    """Bar start times on the phase-corrected grid."""
    starts = []
    t = PHASE
    while t < dur - 0.05:
        starts.append(t)
        t += BAR
    return np.array(starts)


BARS = bar_bounds()
N_BARS = len(BARS)

# ---------------------------------------------------------------------
# RMS contour (50 ms windows, 25 ms hop) in dBFS on the stereo sum,
# plus per-frame spectral centroid.
# ---------------------------------------------------------------------
rwin, rhop = int(0.050 * sr), int(0.025 * sr)
rframes, n_rf = frame_signal(mid, rwin, rhop)
rms = np.sqrt(np.mean(rframes ** 2, axis=1) + 1e-15)
rms_db = db(rms)
rms_t = (np.arange(n_rf) * rhop + rwin / 2) / sr

centroid = (SPEC * freqs[None, :]).sum(axis=1) / (SPEC.sum(axis=1) + 1e-12)

# ---------------------------------------------------------------------
# Chromagram, v2 — PEAK-PICKED bins only, 80-2500 Hz.
# MECHANISM / post-mortem of v1: summing log-magnitudes over ALL bins
# let the broadband floor (drums, cymbals, master-bus noise) vote in
# every pitch class at once; the chroma came out near-uniform, every
# bar failed its confidence gate (corr ~0.54, margin ~0.01), and the
# Krumhansl read tilted to an unreliable D minor that the melody
# sketch's sharp-heavy pitch census (C#, F#, G#, D#) contradicts.
# The fix is the classic one: only local spectral maxima vote — a
# partial must stand above its neighbours to count as harmony — and
# the band stops below the cymbal shelf. Magnitudes vote linearly.
# ---------------------------------------------------------------------
band = (freqs >= 80.0) & (freqs <= 2500.0)
midi_of_bin = 69.0 + 12.0 * np.log2(np.maximum(freqs, 1.0) / 440.0)
pc_of_bin = np.round(midi_of_bin).astype(int) % 12
is_peak = np.zeros_like(SPEC, dtype=bool)
is_peak[:, 1:-1] = (SPEC[:, 1:-1] > SPEC[:, :-2]) & (SPEC[:, 1:-1] >= SPEC[:, 2:])
mag_c = np.where(is_peak & band[None, :], SPEC, 0.0)
CH = np.zeros((n_fr, 12))
pcs = pc_of_bin
for pc in range(12):
    CH[:, pc] = mag_c[:, pcs == pc].sum(axis=1)
CH = CH / (np.linalg.norm(CH, axis=1, keepdims=True) + 1e-12)

# ---------------------------------------------------------------------
# FORM: novelty from flux + chroma change at a 1 s lag.
# MECHANISM: a section boundary is where the harmony AND the texture
# both move; either alone is usually just a fill or a chord change.
# ---------------------------------------------------------------------
lag = int(round(1.0 * sr / HOP))
chroma_now = CH[lag:]
chroma_prev = CH[:-lag]
cos = (chroma_now * chroma_prev).sum(axis=1) / (
    np.linalg.norm(chroma_now, axis=1) * np.linalg.norm(chroma_prev, axis=1) + 1e-12)
nov_chroma = np.zeros(n_fr)
nov_chroma[lag:] = 1.0 - cos
nov_flux_full = np.zeros(n_fr)
nov_flux_full[1:] = flux / (np.percentile(flux, 99) + 1e-12)
novelty = 0.5 * np.clip(nov_flux_full, 0, 1) + 0.5 * np.clip(nov_chroma, 0, 1)
# smooth over ~0.5 s
k = 21
nov_s = np.convolve(novelty, np.ones(k) / k, mode="same")

# Peak-pick: local maxima above the 88th percentile, >= 6.8 s apart
# (v1's 3.5 s spacing caught every bar-level fill — 23 fragments for
# a 46-bar song; a SECTION boundary must clear two bars of ground).
# Greedy by height so the strongest boundaries claim their ground.
cand = []
order = np.argsort(nov_s)[::-1]
thr = np.percentile(nov_s, 88)
for i in order:
    if nov_s[i] < thr:
        break
    t = frame_t[i]
    if t < 2.0 or t > dur - 2.0:
        continue
    if all(abs(t - c[0]) >= 6.8 for c in cand):
        prom = nov_s[i] / (thr + 1e-12)
        cand.append((float(t), float(nov_s[i]), float(prom)))
cand.sort()

# Snap EVERY candidate to the nearest bar line: an engraving skeleton
# lives on the grid. The raw peak time and the snap distance stay in
# bound_detail — the forcing is disclosed, never hidden.
boundaries = [0.0]
bound_detail = []
for t, h, prom in cand:
    rel = (t - PHASE) / BAR
    snapped = float(PHASE + round(rel) * BAR)
    if snapped <= boundaries[-1] + 0.5:
        continue
    conf = 0.75 if prom <= 1.6 else 0.9
    boundaries.append(snapped)
    bound_detail.append({"t_raw": round(t, 3), "t_used": snapped,
                         "snap_distance_s": round(abs(snapped - t), 3),
                         "novelty": round(h, 4),
                         "prominence_ratio": round(prom, 2), "confidence": conf})
boundaries.append(dur)
boundaries = np.array(boundaries)

# ---------------------------------------------------------------------
# Pitch track (needed for segment voiced-density + the melody sketch).
# MECHANISM: normalised autocorrelation per 46 ms frame on the mid
# channel; voicing = correlation peak >= 0.55 with in-band energy.
# Vocal-likelihood gate: mid louder than side AND >= 45% of mid energy
# inside 250-4000 Hz (the speech band).
# ---------------------------------------------------------------------
PWIN, PHOP = 2048, 512
pframes, n_pf = frame_signal(mid, PWIN, PHOP)
pwin = np.hanning(PWIN)
pf = pframes * pwin
# band energy share via a small FFT of the same frames
PS = np.abs(np.fft.rfft(pf, axis=1)) ** 2
pfreqs = np.fft.rfftfreq(PWIN, 1.0 / sr)
speech_band = (pfreqs >= 250) & (pfreqs <= 4000)
band_share = PS[:, speech_band].sum(axis=1) / (PS.sum(axis=1) + 1e-15)
sframes, _ = frame_signal(side, PWIN, PHOP)
mid_rms_f = np.sqrt(np.mean(pf ** 2, axis=1) + 1e-15)
side_rms_f = np.sqrt(np.mean((sframes * pwin) ** 2, axis=1) + 1e-15)
vocal_gate = (band_share >= 0.45) & (mid_rms_f > side_rms_f)

FMIN, FMAX = 65.0, 500.0
lag_min, lag_max = int(sr / FMAX), int(sr / FMIN)
f0 = np.full(n_pf, np.nan)
f0_conf = np.zeros(n_pf)
pf_big = np.concatenate([pf, np.zeros_like(pf)], axis=1)
AC = np.fft.irfft(np.abs(np.fft.rfft(pf_big, axis=1)) ** 2, axis=1)[:, :PWIN]
AC = AC / (AC[:, [0]] + 1e-15)
seg = AC[:, lag_min:lag_max]
pk = np.argmax(seg, axis=1)
pk_val = seg[np.arange(n_pf), pk]
voiced = (pk_val >= 0.55) & (mid_rms_f > 0.008)
lag_best = pk + lag_min
f0[voiced] = sr / lag_best[voiced]
f0_conf = pk_val
pitch_t = (np.arange(n_pf) * PHOP + PWIN / 2) / sr

# ---------------------------------------------------------------------
# Segment feature table (the evidence the FORM-MAP is authored from).
# ---------------------------------------------------------------------
def seg_features(t0, t1):
    m = (rms_t >= t0) & (rms_t < t1)
    cf = (frame_t >= t0) & (frame_t < t1)
    pf_m = (pitch_t >= t0) & (pitch_t < t1)
    lev = float(rms_db[m].mean()) if m.any() else float("nan")
    tt = rms_t[m]
    slope = float(np.polyfit(tt - t0, rms_db[m], 1)[0]) if m.sum() > 4 else 0.0
    cents = float(centroid[cf].mean()) if cf.any() else float("nan")
    chs = CH[cf]
    lagf = int(round(1.0 * sr / HOP))  # stability read at a 1 s lag:
    if len(chs) > lagf + 2:            # frame-to-frame cosine is ~1 by
        a, b = chs[lagf:], chs[:-lagf]  # construction (75% STFT overlap)
        sims = (a * b).sum(axis=1) / (np.linalg.norm(a, axis=1)
                                      * np.linalg.norm(b, axis=1) + 1e-12)
        stab = float(np.clip(sims.mean(), 0, 1))
    else:
        stab = float("nan")
    vd = float((voiced & vocal_gate)[pf_m].mean()) if pf_m.any() else 0.0
    # per-bar chroma fingerprint for recurrence testing
    bars_here = [CH[(frame_t >= b) & (frame_t < b + BAR)].mean(axis=0).tolist()
                 for b in BARS if t0 - 0.01 <= b < t1 - 0.01]
    return {"t0": t0, "t1": t1, "dur": t1 - t0,
            "bar0": int(round((t0 - PHASE) / BAR)),
            "n_bars": int(round((t1 - t0) / BAR)),
            "mean_db": lev, "slope_db_s": slope, "centroid_hz": cents,
            "chroma_stability": stab, "voiced_density": vd,
            "_bar_chroma": bars_here}


segments = []
for t0, t1 in zip(boundaries[:-1], boundaries[1:]):
    segments.append(seg_features(float(t0), float(t1)))


def pearson(a, b):
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    n = min(len(a), len(b))
    if n < 4:
        return 0.0
    a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


# Merge pass: dissolve an interior boundary when the two sides are
# the same room — level within 1.2 dB AND bar-chroma fingerprints
# Pearson-correlated above 0.90. Weakest-novelty boundary goes first.
# MECHANISM: novelty finds candidate seams; this pass asks whether
# anything actually changed across the seam. Dissolved boundaries are
# recorded in MERGED_AWAY, marked — never vanished.
MERGED_AWAY = []
while len(segments) > 2:
    best_i, best_nov = -1, None
    for i in range(len(segments) - 1):
        if abs(segments[i]["mean_db"] - segments[i + 1]["mean_db"]) >= 1.2:
            continue
        if pearson(segments[i]["_bar_chroma"], segments[i + 1]["_bar_chroma"]) <= 0.90:
            continue
        nov = bound_detail[i]["novelty"] if i < len(bound_detail) else 0.0
        if best_nov is None or nov < best_nov:
            best_i, best_nov = i, nov
    if best_i < 0:
        break
    t0, t1 = segments[best_i]["t0"], segments[best_i + 1]["t1"]
    MERGED_AWAY.append({"boundary_s": segments[best_i + 1]["t0"],
                        "novelty": best_nov})
    segments[best_i:best_i + 2] = [seg_features(t0, t1)]
    if best_i < len(bound_detail):
        bound_detail.pop(best_i)

# Recurrence: Pearson correlation of per-bar chroma fingerprints
# (v1 used raw cosine on non-negative vectors, which is ~1 between
# ANY two segments and so measured nothing; centring fixes it).
for i, s in enumerate(segments):
    best, best_j = -1.0, -1
    for j, o in enumerate(segments):
        if i == j or not s["_bar_chroma"] or not o["_bar_chroma"]:
            continue
        sim = pearson(s["_bar_chroma"], o["_bar_chroma"])
        if sim > best:
            best, best_j = sim, j
    s["recurrence_sim"] = round(best, 3)
    s["recurrence_with"] = best_j
for s in segments:
    s.pop("_bar_chroma")

# ---------------------------------------------------------------------
# KEY: Krumhansl-Schmuckler profiles vs duration-weighted mean chroma.
# ---------------------------------------------------------------------
KS_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KS_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
w = SPEC.sum(axis=1)
global_chroma = (CH * w[:, None]).sum(axis=0)
global_chroma = global_chroma / global_chroma.sum()
key_scores = []
for root in range(12):
    for name, prof in (("major", KS_MAJ), ("minor", KS_MIN)):
        p = np.roll(prof, root)
        c = np.corrcoef(global_chroma, p)[0, 1]
        key_scores.append((float(c), root, name))
key_scores.sort(reverse=True)
KEY_TOP = [{"key": f"{NOTE_NAMES[r]} {n}", "corr": round(c, 3)} for c, r, n in key_scores[:3]]
key_margin = key_scores[0][0] - key_scores[1][0]

# ---------------------------------------------------------------------
# CHORDS per bar: mean bar chroma vs triad templates.
# Templates: major, minor, power (root+fifth). Confidence rides on
# the margin between the winner and the runner-up; a bar where the
# vocal/bass evidence is thin is labelled UNCLEAR, in the open.
# ---------------------------------------------------------------------
def template(root, kind):
    v = np.zeros(12)
    if kind == "maj":
        v[[root, (root + 4) % 12, (root + 7) % 12]] = [1.0, 0.9, 0.9]
    elif kind == "min":
        v[[root, (root + 3) % 12, (root + 7) % 12]] = [1.0, 0.9, 0.9]
    else:  # "5"
        v[[root, (root + 7) % 12]] = [1.0, 0.9]
    return v / np.linalg.norm(v)


TEMPLATES = [(r, k, template(r, k)) for r in range(12) for k in ("maj", "min", "5")]
chord_rows = []
for bi, b0 in enumerate(BARS):
    b1 = b0 + BAR
    m = (frame_t >= b0) & (frame_t < b1)
    if m.sum() < 3:
        chord_rows.append({"bar": bi + 1, "t0": b0, "t1": b1, "chord": "UNCLEAR",
                           "corr": 0.0, "margin": 0.0, "confidence": "none",
                           "bar_db": -120.0})
        continue
    bc = CH[m].mean(axis=0)
    bc = bc / (np.linalg.norm(bc) + 1e-12)
    scored = sorted(((float(bc @ tv), r, k) for r, k, tv in TEMPLATES), reverse=True)
    (c1, r1, k1), (c2, _, _) = scored[0], scored[1]
    bar_db = float(rms_db[(rms_t >= b0) & (rms_t < b1)].mean())
    margin = c1 - c2
    if c1 < 0.55 or margin < 0.02:
        label, conf = "UNCLEAR", "low"
    else:
        suffix = {"maj": "", "min": "m", "5": "5"}[k1]
        label = f"{NOTE_NAMES[r1]}{suffix}"
        conf = "high" if margin >= 0.08 else ("medium" if margin >= 0.04 else "low")
    chord_rows.append({"bar": bi + 1, "t0": round(float(b0), 3), "t1": round(float(b1), 3),
                       "chord": label, "corr": round(c1, 3), "margin": round(margin, 3),
                       "confidence": conf, "bar_db": round(bar_db, 1)})

# ---------------------------------------------------------------------
# MELODY SKETCH: quantise the gated, voiced f0 track to notes.
# MECHANISM: median-of-5 smoothing; a note is a run of frames within
# half a semitone, >= 90 ms, gaps <= 70 ms bridged. Octave suspects
# (note > 15 semitones from both neighbours and < 150 ms) are flagged.
# ---------------------------------------------------------------------
midi_f = np.where(voiced & vocal_gate & np.isfinite(f0),
                  69.0 + 12.0 * np.log2(np.maximum(f0, 1.0) / 440.0), np.nan)
med = np.copy(midi_f)
for i in range(n_pf):
    lo, hi = max(0, i - 2), min(n_pf, i + 3)
    wsel = midi_f[lo:hi]
    wsel = wsel[np.isfinite(wsel)]
    med[i] = np.median(wsel) if len(wsel) >= 3 else np.nan

notes = []
i = 0
hop_s = PHOP / sr
while i < n_pf:
    if not np.isfinite(med[i]):
        i += 1
        continue
    centre = med[i]
    j, gap = i, 0
    while j + 1 < n_pf:
        nxt = med[j + 1]
        if np.isfinite(nxt) and abs(nxt - centre) <= 0.5:
            j += 1
            gap = 0
            centre = 0.9 * centre + 0.1 * nxt
        elif not np.isfinite(nxt) and gap < int(0.070 / hop_s):
            j += 1
            gap += 1
        else:
            break
    dur_n = (j - i + 1) * hop_s
    if dur_n >= 0.090:
        sel = slice(i, j + 1)
        fq = f0[sel][np.isfinite(f0[sel])]
        notes.append({
            "onset_s": round(float(pitch_t[i]), 3),
            "dur_s": round(float(dur_n), 3),
            "midi": int(round(float(np.nanmedian(med[sel])))),
            "note": NOTE_NAMES[int(round(float(np.nanmedian(med[sel])))) % 12]
                    + str(int(round(float(np.nanmedian(med[sel])))) // 12 - 1),
            "mean_hz": round(float(np.median(fq)), 1) if len(fq) else None,
            "conf": round(float(np.mean(f0_conf[sel])), 3),
            "octave_suspect": False,
        })
    i = j + 1

for a, b_, c in zip([None] + notes[:-1], notes, notes[1:] + [None]):
    near = [n for n in (a, c) if n is not None]
    if near and all(abs(b_["midi"] - n["midi"]) >= 15 for n in near) and b_["dur_s"] < 0.150:
        b_["octave_suspect"] = True

# ---------------------------------------------------------------------
# Write the machine outputs. The FORM-MAP document is authored by the
# desk from these numbers; nothing here writes prose conclusions.
# ---------------------------------------------------------------------
with open(os.path.join(HERE, "chords.csv"), "w") as fh:
    fh.write("bar,start_s,end_s,chord,template_corr,margin,confidence,bar_mean_dbfs\n")
    for r in chord_rows:
        fh.write(f"{r['bar']},{r['t0']},{r['t1']},{r['chord']},{r['corr']},"
                 f"{r['margin']},{r['confidence']},{r['bar_db']}\n")

stats = {
    "audio": AUDIO, "sr": sr, "duration_s": round(dur, 3),
    "bpm_measured_bench": BPM, "beat_s": round(BEAT, 6), "bar_s": round(BAR, 6),
    "downbeat_phase_s": round(PHASE, 3), "n_bars": int(N_BARS),
    "boundaries": bound_detail,
    "boundaries_merged_away": MERGED_AWAY,
    "chord_distribution": {c: sum(1 for r in chord_rows if r["chord"] == c)
                           for c in sorted(set(r["chord"] for r in chord_rows))},
    "segments": [{k: (round(v, 3) if isinstance(v, float) else v)
                  for k, v in s.items()} for s in segments],
    "key_top3": KEY_TOP, "key_margin": round(float(key_margin), 3),
    "global_chroma": [round(float(v), 4) for v in global_chroma],
    "n_notes_sketch": len(notes),
    "sketch_coverage": round(float(np.mean(voiced & vocal_gate)), 3),
}
with open(os.path.join(HERE, "analysis-stats.json"), "w") as fh:
    json.dump(stats, fh, indent=1)

sketch = {
    "document": "TRANSCRIPTION-ANALYSIS — MELODY SKETCH (phase 1, machine sketch)",
    "honesty_header": {
        "status": "SKETCH — a measured pitch-track reduction for a later engraving "
                  "pass. NOT a finished transcription. Do not engrave from this "
                  "file without the desk's audit against the audio.",
        "method": "Normalised-autocorrelation f0 on the mid channel (46 ms "
                  "frames, 11.6 ms hop), gated by a vocal-likelihood heuristic "
                  "(centred mid>side, >=45% of energy in 250-4000 Hz), "
                  "median-smoothed and grouped into notes >= 90 ms.",
        "known_failure_modes": [
            "Octave errors survive the gate; suspects are flagged, not fixed.",
            "Rapped/spoken passages have continuous intonation — notes there "
            "are the tracker's quantisation of speech, marked by low conf.",
            "Dense hook stacks (doubled vocals + ad-libs) can pull the track "
            "to a harmony line instead of the lead.",
            "Onsets are frame-quantised (+/- 12 ms) before any rhythmic "
            "quantisation an engraver later applies.",
        ],
        "tempo_grid": f"{BPM} BPM bench-measured; bar = {BAR:.4f} s; "
                      f"downbeat phase est. {PHASE:.3f} s.",
    },
    "notes": notes,
}
with open(os.path.join(HERE, "melody-sketch.json"), "w") as fh:
    json.dump(sketch, fh, indent=1)

print(json.dumps({"phase_s": round(PHASE, 3), "n_bars": int(N_BARS),
                  "n_segments": len(segments), "key_top": KEY_TOP,
                  "key_margin": round(float(key_margin), 3),
                  "n_notes": len(notes),
                  "coverage": stats["sketch_coverage"]}, indent=1))
print("segments:")
for s in segments:
    print(f"  {s['t0']:7.2f}-{s['t1']:7.2f}  bars {s['bar0']+1:>2}-{s['bar0']+s['n_bars']:>2}"
          f"  {s['mean_db']:6.1f} dB  slope {s['slope_db_s']:+.2f}  cent {s['centroid_hz']:6.0f}"
          f"  stab {s['chroma_stability']:.3f}  voice {s['voiced_density']:.2f}"
          f"  recur {s['recurrence_sim']:+.3f} (seg {s['recurrence_with']})")

# 93 — Live, Love, and let Love, Live.
