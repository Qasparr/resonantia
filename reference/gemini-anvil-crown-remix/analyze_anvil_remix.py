#!/usr/bin/env python3
# =====================================================================
# 93
#
# Epigraph: "The method of science, the aim of religion." — the house
# rule under which this bench works: every number below was MEASURED
# from the audio, and every interpretation is MARKED as interpretation.
# Nothing in this script invents a note, a chord, or a lyric.
#
# analyze_anvil_remix.py — INTAKE MEASUREMENT + TRANSCRIPTION-
# ANALYSIS, phase 1 (analysis only) for "HONEY AND HAMMER"
# (THE ANVIL AND CROWN — REMIX), the founder's Gemini (Lyria)
# strike taken into the house 2026-11-10 under the adoption
# ruling. This one answers a FILED BRIEF (studio-runs/
# gemini-anvil-crown-remix/prompt.txt): exactly 93 bars at
# 144 BPM in the counted duet form — intro 4 / hook 8 / Verse I
# (Qasparr) 16 / hook 8 / Verse I (Qveen Bee) 16 / hook (half) 4
# / Verse II (Qasparr) 12 / Verse II (Qveen Bee) 12 / tag-team
# verse 12 / outro 1 — a Detroit bounce trap anthem in A major;
# Qveen Bee (soprano signature) singing every hook; Paganini
# arpeggios ordered INSIDE the performance (hi-hats, guitar on
# solfeggio tones); a binaural Sigma layer ordered EMBEDDED,
# sweeping 13-31 Hz. The bench is the Sovereign intake bench
# carried over whole, with its three added instruments re-seated
# for this brief:
#   * THE 93-BAR AUDIT — the measured segment map is laid against
#     the brief's form in bar coordinates; disagreements are
#     reported as coordinates, never verdicts. The three hook
#     seats are tested directly, as the refrain's seat was.
#   * THE SIGMA SWEEP PROBE — the fixed-seat probe of the Sphinx
#     intake, PLUS a sweep search: windowed narrowband line
#     tracking in each channel across 80-500 Hz, and the
#     interaural difference trajectory |fR - fL|(t). Thresholds
#     are stated in that block's header BEFORE it looks.
#   * THE ARPEGGIO ASSESSMENT — bed pitch-track pattern evidence
#     (density, interval census, broken-chord pattern score),
#     with its confidence stated as honestly as its result.
# It produces the measured skeleton on which a later engraving
# pass may build. It is NOT a finished transcription and
# fabricates nothing.
#
# Date: X day of November, Dies Martis, Sol in Scorpio,
#       Anno V:xii e.n. (2026 e.v.)
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice).
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# MECHANISM (what the machine does, step by step):
#   1. Decode the MP3 to stereo float; split mid/side.
#   2. Measure the tempo with the house studio estimator and lay
#      its grid under the file; estimate the downbeat phase from
#      the onset envelope, so bar lines sit on the music, not on
#      the file edge. (The PROVISIONAL constants below are replaced
#      by the measured grid before any bar is laid.)
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
import re

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HERE, "honey_and_hammer_23_k99j.mp3")
# PROVISIONAL grid only: the measured grid replaces these values in
# the TEMPO BLOCK below (after load, before first use). No bar is
# ever laid on the provisional numbers.
BPM = 100.0
BEAT = 60.0 / BPM
BAR = 4.0 * BEAT

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
# bass); side carries width. What the correlation says about THIS
# file is measured in the STEREO block below, not inherited.
# ---------------------------------------------------------------------
x, sr = sf.read(AUDIO)
if x.ndim == 1:
    x = np.column_stack([x, x])
L, R = x[:, 0], x[:, 1]
mid = 0.5 * (L + R)
side = 0.5 * (L - R)
dur = len(mid) / sr

# =====================================================================
# MEASUREMENT FRONT-END (the intake pass proper).
# TEMPO: the house studio estimator (onset-envelope autocorrelation
# with its stated log-Gaussian prior) on the mid channel -- the same
# instrument that weighed every studio run, so these numbers stand
# comparable with theirs. The desk's first-pass instrument (RMS-
# block envelope, the one whose 132.5 mis-reading the Sphinx intake
# exposed) is REPRODUCED by its own instrument below and carried in
# the record beside the house reading: the zero point between the
# two instruments is reported, never smoothed. This brief, unlike
# the earlier ones, NAMES its clock (144 BPM), and the flux raw
# autocorrelation is read at that point in the open.
# LOUDNESS: house K-weighted ungated LUFS + true peak (pipeline
# scales, 48 kHz set -- the signal is resampled for the weighing
# only), cross-checked against ffmpeg's gated BS.1770 (ebur128).
# STEREO: correlation + side RMS, global and per 30 s window.
# SIGMA PROBE: a discrete binaural layer at the doctrine pair
# (200 Hz L / 213 Hz R) would stand as a persistent narrowband line
# in nearly every 2 s window. The probe states its certification
# threshold BEFORE it looks: median line-to-shoulder ratio >= 10 dB
# AND persistence (ratio > 6 dB) in >= 90% of windows, at the exact
# doctrine frequencies in the correct channels. Anything less is
# NOT CERTIFIABLE, with the numbers printed either way.
# =====================================================================
import subprocess
import sys as _sys
_sys.path.insert(0, "/home/hatch/workspace/resonance")
from resonance.studio import performance as _perf
from resonance.studio import pipeline as _pipe
from scipy.signal import resample_poly as _resample_poly

_env, _env_rate = _perf.onset_envelope(mid, sr)
_tempo_global = _perf.tempo_from_envelope(_env, _env_rate)
_tempo_windows = _perf.window_tempos(_env, _env_rate, dur)
_wb = [w["bpm"] for w in _tempo_windows if w["bpm"] is not None]
# raw flux-envelope autocorrelation at the contested points
_e = _env - _env.mean()
_nf = 1 << int(np.ceil(np.log2(2 * len(_e))))
_sp = np.fft.rfft(_e, n=_nf)
_ac = np.fft.irfft(_sp * np.conj(_sp), n=_nf)[:len(_e)]
_ac = _ac / _ac[0]
def _ac_at(bpm):
    lag = _env_rate * 60.0 / bpm
    k = int(round(lag))
    f = lag - k
    return round(float(_ac[k] * (1 - f) + _ac[min(k + 1, len(_ac) - 1)] * f), 4)
_flux_points = {str(b): _ac_at(b) for b in
                (144.0, round(float(_tempo_global["bpm"]), 2),
                 round(float(_tempo_global["dominant_periodicity_bpm"]), 2),
                 72.0)}
# the desk's first-pass instrument, reproduced exactly: RMS blocks
# of 512 samples, positive differences, plain autocorrelation
_hopb = 512
_nb = len(mid) // _hopb
_rmsb = np.sqrt(np.mean(mid[:_nb * _hopb].reshape(_nb, _hopb) ** 2, axis=1))
_renv = np.maximum(0.0, np.diff(_rmsb))
_renv = _renv - _renv.mean()
_nf2 = 1 << int(np.ceil(np.log2(2 * len(_renv))))
_sp2 = np.fft.rfft(_renv, n=_nf2)
_rac = np.fft.irfft(_sp2 * np.conj(_sp2), n=_nf2)[:len(_renv)]
_rac = _rac / _rac[0]
_fps = sr / _hopb
_lags = np.arange(int(_fps * 60 / 200), int(_fps * 60 / 50))
_first_dominant = float(60 * _fps / _lags[int(np.argmax(_rac[_lags]))])
_first_strength = float(np.max(_rac[_lags]))
_l144 = int(round(_fps * 60 / 144.0))
TEMPO_BLOCK = {
    "house_estimator": {"global": _tempo_global, "windows": _tempo_windows,
                        "window_bpm_min": min(_wb), "window_bpm_max": max(_wb),
                        "window_bpm_spread": round(max(_wb) - min(_wb), 2)},
    "flux_raw_ac_at_points": _flux_points,
    "first_pass_instrument_reproduced": {
        "dominant_periodicity_bpm": round(_first_dominant, 2),
        "strength": round(_first_strength, 4),
        "ac_at_144_bpm": round(float(_rac[_l144]), 4)},
}
# THE GRID: the house estimator's headline. Its window series is the
# flattest clock in the file; the FORM-MAP carries the alternatives.
BPM = float(_tempo_global["bpm"])
BEAT = 60.0 / BPM
BAR = 4.0 * BEAT
# GRID OVERRIDE (audit instrument): ANVIL_GRID_BPM forces the
# grid to a named alternative so the brief audit can be re-weighed
# on a second clock without touching the bench of record. The
# override is recorded in TEMPO_BLOCK wherever it is used.
import os as _os
if _os.environ.get("ANVIL_GRID_BPM"):
    BPM = float(_os.environ["ANVIL_GRID_BPM"])
    BEAT = 60.0 / BPM
    BAR = 4.0 * BEAT
    TEMPO_BLOCK["grid_override_bpm"] = BPM

# loudness of the SOURCE as struck (48 kHz weighing copy)
_x48 = np.stack([_resample_poly(x[:, 0], 160, 147),
                 _resample_poly(x[:, 1], 160, 147)])
_src_lufs = _pipe.measure_loudness_lufs(_x48, 48000)
_src_tp = _pipe.true_peak_dbtp(_x48, 48000)
_src_spk = float(np.max(np.abs(x)))
_eb = subprocess.run(["ffmpeg", "-v", "info", "-i", AUDIO, "-af",
                      "ebur128=peak=true", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
_mI = re.search(r"Integrated loudness:\s*\n\s*I:\s*(-?[\d.]+) LUFS", _eb)
_mP = re.search(r"True peak:\s*\n\s*Peak:\s*(-?[\d.]+) dBFS", _eb)
LOUDNESS_BLOCK = {
    "house_ungated_lufs": round(_src_lufs, 2),
    "house_true_peak_dbtp": round(_src_tp, 2),
    "sample_peak_dbfs": round(20.0 * np.log10(_src_spk), 2),
    "ffmpeg_ebur128_gated_lufs": float(_mI.group(1)) if _mI else None,
    "ffmpeg_ebur128_true_peak_dbfs": float(_mP.group(1)) if _mP else None,
    "note": "house loudness is K-weighted integrated, UNGATED (the "
            "studio pipeline's stated simplification); the ffmpeg "
            "figure is the gated BS.1770-4 read, carried as a "
            "second witness, not a replacement.",
}

def _corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])
_stereo_windows = []
for _w0 in range(0, int(dur), 30):
    _w1 = min(dur, _w0 + 30)
    _m = slice(int(_w0 * sr), int(_w1 * sr))
    _sd = 0.5 * (x[_m, 0] - x[_m, 1])
    _stereo_windows.append({
        "start_s": _w0, "end_s": round(_w1, 2),
        "corr": round(_corr(x[_m, 0], x[_m, 1]), 4),
        "side_rms_dbfs": round(float(db(np.sqrt(np.mean(_sd ** 2) + 1e-15))), 2)})
STEREO_BLOCK = {
    "corr_global": round(_corr(L, R), 4),
    "side_rms_dbfs": round(float(db(np.sqrt(np.mean(side ** 2) + 1e-15))), 2),
    "mid_rms_dbfs": round(float(db(np.sqrt(np.mean(mid ** 2) + 1e-15))), 2),
    "windows": _stereo_windows,
}

# SIGMA PROBE (threshold stated in the header above, before looking)
def _probe(ch, f0):
    win_s = 2.0
    nw = int(dur // win_s)
    W = int(win_s * sr)
    ratios = []
    for i in range(nw):
        segx = ch[i * W:(i + 1) * W] * np.hanning(W)
        S = np.abs(np.fft.rfft(segx))
        fr = np.fft.rfftfreq(W, 1.0 / sr)
        k0 = int(np.argmin(np.abs(fr - f0)))
        line = S[max(0, k0 - 1):k0 + 2].max()
        sh = np.concatenate([S[(fr > f0 - 30) & (fr < f0 - 6)],
                             S[(fr > f0 + 6) & (fr < f0 + 30)]])
        ratios.append(20.0 * np.log10(line / (np.median(sh) + 1e-12)))
    ratios = np.array(ratios)
    return {"freq_hz": f0, "median_ratio_db": round(float(np.median(ratios)), 2),
            "p90_ratio_db": round(float(np.percentile(ratios, 90)), 2),
            "persistence_gt_6db": round(float(np.mean(ratios > 6.0)), 3),
            "n_windows": int(nw)}
_pL = _probe(L, 200.0)
_pR = _probe(R, 213.0)
_cert = (_pL["median_ratio_db"] >= 10.0 and _pR["median_ratio_db"] >= 10.0
         and _pL["persistence_gt_6db"] >= 0.9 and _pR["persistence_gt_6db"] >= 0.9)
SIGMA_BLOCK = {
    "doctrine_pair": {"left_hz": 200.0, "right_hz": 213.0},
    "probe_left_200hz": _pL, "probe_right_213hz": _pR,
    "certification_threshold": "median ratio >= 10 dB AND persistence "
                               "(> 6 dB) >= 0.90 in BOTH channels at the "
                               "exact doctrine frequencies",
    "certified": bool(_cert),
    "verdict": "CERTIFIED" if _cert else
               "NOT CERTIFIABLE -- no persistent narrowband line stands "
               "at the doctrine pair at mastering depth; whatever "
               "energy lives at 200/213 Hz belongs to the programme "
               "(bass and voice), not to a discrete binaural layer.",
}

# =====================================================================
# SIGMA SWEEP PROBE (this strike's addition — thresholds BEFORE looking)
# The brief ordered not the fixed doctrine pair but a pair SWEEPING
# 13-31 Hz. A sweeping binaural layer is a pair of narrowband lines,
# one per channel, whose FREQUENCY DIFFERENCE |fR - fL| travels
# inside 13-31 Hz over time. The probe tracks, in 2 s windows at a
# 1 s hop, the strongest peak-picked narrowband line in each channel
# inside 80-500 Hz (line = local maximum standing above its ±(6-30) Hz
# shoulder median). A PAIR WINDOW is one where BOTH channels hold a
# line with ratio > 6 dB. CERTIFICATION requires, all at once:
#   * pair persistence >= 0.90 of programme windows,
#   * median line ratio >= 10 dB in BOTH channels (the house bar),
#   * median |fR - fL| inside [13, 31] Hz,
#   * sweep evidence: the |fR - fL| trajectory's interquartile
#     range >= 4 Hz (a frozen offset is a detune, not a sweep).
# The known confound is stated in the open: programme bass is mostly
# centred, so it presents the SAME line in both channels (|df| ~ 0)
# and fails the beat test by construction; a genuinely independent
# per-channel tone is what the probe can see. Anything short of the
# full certificate is NOT CERTIFIABLE, with the trajectory printed.
# =====================================================================
def _track_line(ch, band_lo=80.0, band_hi=500.0):
    win_s, hop_s = 2.0, 1.0
    W, H = int(win_s * sr), int(hop_s * sr)
    out = []
    t = 0.0
    while t + win_s <= dur + 1e-9:
        i0 = int(t * sr)
        segx = ch[i0:i0 + W] * np.hanning(W)
        S = np.abs(np.fft.rfft(segx))
        fr = np.fft.rfftfreq(W, 1.0 / sr)
        band = (fr >= band_lo) & (fr <= band_hi)
        Sb = np.where(band, S, 0.0)
        k = int(np.argmax(Sb))
        sh = np.concatenate([S[(fr > fr[k] - 30) & (fr < fr[k] - 6)],
                             S[(fr > fr[k] + 6) & (fr < fr[k] + 30)]])
        ratio = 20.0 * np.log10(S[k] / (np.median(sh) + 1e-12)) if len(sh) else 0.0
        out.append({"t": round(t, 1), "freq_hz": round(float(fr[k]), 2),
                    "ratio_db": round(float(ratio), 2)})
        t += hop_s
    return out

_trL = _track_line(L)
_trR = _track_line(R)
_pairs = []
for a, b in zip(_trL, _trR):
    if a["ratio_db"] > 6.0 and b["ratio_db"] > 6.0:
        _pairs.append({"t": a["t"], "fL": a["freq_hz"], "fR": b["freq_hz"],
                       "df_hz": round(abs(b["freq_hz"] - a["freq_hz"]), 2),
                       "ratio_L": a["ratio_db"], "ratio_R": b["ratio_db"]})
_n_win = min(len(_trL), len(_trR))
_pair_persistence = len(_pairs) / max(_n_win, 1)
if _pairs:
    _dfs = np.array([p["df_hz"] for p in _pairs])
    _med_df = float(np.median(_dfs))
    _iqr_df = float(np.percentile(_dfs, 75) - np.percentile(_dfs, 25))
    _med_rL = float(np.median([p["ratio_L"] for p in _pairs]))
    _med_rR = float(np.median([p["ratio_R"] for p in _pairs]))
    _frac_in_band = float(np.mean((_dfs >= 13.0) & (_dfs <= 31.0)))
else:
    _med_df = _iqr_df = _med_rL = _med_rR = _frac_in_band = 0.0
_sweep_cert = (_pair_persistence >= 0.90 and _med_rL >= 10.0 and _med_rR >= 10.0
               and 13.0 <= _med_df <= 31.0 and _iqr_df >= 4.0)
SIGMA_SWEEP_BLOCK = {
    "method": "2 s windows, 1 s hop; strongest peak-picked narrowband "
              "line per channel in 80-500 Hz; pair window = both "
              "channels hold a line with line-to-shoulder ratio > 6 dB",
    "certification_threshold": "pair persistence >= 0.90 AND median "
                               "ratio >= 10 dB in BOTH channels AND "
                               "median |fR-fL| in [13,31] Hz AND |df| "
                               "IQR >= 4 Hz (sweep, not detune)",
    "n_windows": int(_n_win),
    "pair_windows": len(_pairs),
    "pair_persistence": round(float(_pair_persistence), 3),
    "median_ratio_L_db": round(_med_rL, 2),
    "median_ratio_R_db": round(_med_rR, 2),
    "median_abs_df_hz": round(_med_df, 2),
    "abs_df_iqr_hz": round(_iqr_df, 2),
    "frac_pair_windows_df_in_13_31": round(_frac_in_band, 3),
    "trajectory": _pairs,
    "certified": bool(_sweep_cert),
    "verdict": "CERTIFIED -- a sweeping binaural pair stands in the "
               "render at the ordered depth" if _sweep_cert else
               "NOT CERTIFIABLE -- no persistent per-channel line pair "
               "with a 13-31 Hz interaural difference stands in the "
               "render at the stated thresholds; the trajectory is "
               "printed in full so the finding can be re-weighed.",
}

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
# energy wins. The search VERIFIES the phase rather than assuming
# it; no phase is inherited from any earlier file's shape.
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
# PROGRAMME / FADE (RMS contour instrument, labelled wherever used —
# the segmenter sleeps on a dying signal, per the Sphinx intake's
# method note 4). 0.5 s windows on the mid channel; the programme
# end is read at three thresholds so the fade's shape is a curve,
# not a point invented by one cut.
# ---------------------------------------------------------------------
_pw = int(0.5 * sr)
_pn = len(mid) // _pw
_prms = np.sqrt(np.mean(mid[:_pn * _pw].reshape(_pn, _pw) ** 2, axis=1) + 1e-15)
_pdb = db(_prms)
_pt = (np.arange(_pn) + 0.5) * 0.5
def _last_above(thr):
    idx = np.where(_pdb > thr)[0]
    return round(float(_pt[idx[-1]]), 2) if len(idx) else 0.0
PROGRAMME_BLOCK = {
    "duration_s": round(dur, 3),
    "last_window_above_-40dbfs_s": _last_above(-40.0),
    "last_window_above_-50dbfs_s": _last_above(-50.0),
    "last_window_above_-60dbfs_s": _last_above(-60.0),
    "final_window_dbfs": round(float(_pdb[-1]), 1),
}

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

# =====================================================================
# THE 93-BAR AUDIT (this strike's commission — coordinates, not
# verdicts). The brief's form, in bar numbers: intro 1-4, hook
# 5-12, Verse I (Qasparr) 13-28, hook 29-36, Verse I (Qveen Bee)
# 37-52, hook (half) 53-56, Verse II (Qasparr) 57-68, Verse II
# (Qveen Bee) 69-80, tag-team verse 81-92, outro 93; 93 bars
# total. Each ordered interior boundary (the starts of bars 5,
# 13, 29, 37, 53, 57, 69, 81 and 93) is laid on the measured
# grid and the NEAREST measured segment boundary is reported
# with its distance in seconds and in bars. The three hook
# seats are tested directly: which measured segment covers
# each seat, its level rank among segments, its recurrence
# twin, and whether the seat lies whole inside one segment —
# a performed hook should declare itself by returning.
# =====================================================================
_BRIEF_FORM = [
    {"section": "intro", "bars": [1, 4]},
    {"section": "hook", "bars": [5, 12]},
    {"section": "verse_I_qasparr", "bars": [13, 28]},
    {"section": "hook", "bars": [29, 36]},
    {"section": "verse_I_qveen_bee", "bars": [37, 52]},
    {"section": "hook_half", "bars": [53, 56]},
    {"section": "verse_II_qasparr", "bars": [57, 68]},
    {"section": "verse_II_qveen_bee", "bars": [69, 80]},
    {"section": "tag_team_verse", "bars": [81, 92]},
    {"section": "outro", "bars": [93, 93]},
]
_measured_bounds_s = sorted({round(float(s["t0"]), 3) for s in segments} |
                            {round(float(segments[-1]["t1"]), 3)})
_audit_rows = []
for _b in (5, 13, 29, 37, 53, 57, 69, 81, 93):
    _exp_s = PHASE + (_b - 1) * BAR
    _near = min(_measured_bounds_s, key=lambda v: abs(v - _exp_s))
    _audit_rows.append({
        "ordered_boundary": f"start of bar {_b}",
        "expected_s": round(float(_exp_s), 2),
        "nearest_measured_boundary_s": _near,
        "distance_s": round(abs(_near - _exp_s), 2),
        "distance_bars": round(abs(_near - _exp_s) / BAR, 2)})
_levels_sorted = sorted((o["mean_db"] for o in segments), reverse=True)
_hook_seats = []
for _seat in ((5, 12), (29, 36), (53, 56)):
    _hit = None
    for _i, _s in enumerate(segments):
        if _s["bar0"] + 1 <= _seat[0] <= _s["bar0"] + _s["n_bars"]:
            _hit = {"segment_index": _i,
                    "segment_bars": [_s["bar0"] + 1, _s["bar0"] + _s["n_bars"]],
                    "t0": _s["t0"], "t1": _s["t1"],
                    "mean_db": _s["mean_db"],
                    "level_rank_of_segments": _levels_sorted.index(_s["mean_db"]) + 1,
                    "recurrence_sim": _s["recurrence_sim"],
                    "recurrence_with": _s["recurrence_with"],
                    "seat_lies_whole_in_segment":
                        bool(_s["bar0"] + _s["n_bars"] >= _seat[1])}
            break
    _hook_seats.append({"seat_bars": list(_seat), "covering_segment": _hit})
_prog_end = PROGRAMME_BLOCK["last_window_above_-40dbfs_s"]
BRIEF_AUDIT = {
    "brief": "studio-runs/gemini-anvil-crown-remix/prompt.txt",
    "ordered_form": _BRIEF_FORM,
    "ordered_total_bars": 93,
    "ordered_bpm": 144.0,
    "expected_span_at_ordered_144bpm_s": 155.0,
    "grid_bars_in_file": int(N_BARS),
    "grid_bar_s": round(BAR, 4),
    "expected_file_span_for_93_bars_s": round(PHASE + 93 * BAR, 2),
    "programme_bars_at_-40dbfs": int((_prog_end - PHASE) // BAR) + 1,
    "boundary_distances": _audit_rows,
    "hook_seats": _hook_seats,
    "measured_segments_bars": [[s["bar0"] + 1, s["bar0"] + s["n_bars"]]
                               for s in segments],
}

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

# =====================================================================
# ARPEGGIO ASSESSMENT (this strike's commission). The brief ordered
# Paganini arpeggios INSIDE the performance — hi-hats at 144 and
# guitar playing arpeggios on solfeggio tones. The bench cannot hear
# intent; it can weigh pattern evidence in the bed. The vocal sketch
# above is gated to the centred voice; this pass re-quantises the
# SAME f0 track WITHOUT the vocal-likelihood gate (energy + voicing
# only) into "bed notes" and asks three questions of them:
#   1. DENSITY — notes per second inside the verse spans.
#   2. INTERVAL CENSUS — the distribution of successive intervals;
#      broken chords spend their motion on chord steps (3, 4, 5, 7
#      semitones), not on the semitone slides of speech.
#   3. PATTERN SCORE — over sliding 4-note windows, the fraction
#      whose pitch-class set fits inside ONE major/minor triad and
#      whose contour is monotone or single-turn (up-down/down-up):
#      the shape an arpeggio draws.
# THRESHOLDS stated before the numbers are read into prose:
# presence requires bed coverage >= 0.05 of frames, density >= 1.5
# notes/s in verse spans, chord-step share >= 0.45, pattern score
# >= 0.35. If coverage < 0.05 the bed cannot be held by this
# tracker and the honest verdict is UNREADABLE. Anything between
# is reported as the numbers stand, tiered LOW.
# =====================================================================
_bed_midi = np.where(voiced & np.isfinite(f0),
                     69.0 + 12.0 * np.log2(np.maximum(f0, 1.0) / 440.0), np.nan)
_bed_med = np.copy(_bed_midi)
for i in range(n_pf):
    lo, hi = max(0, i - 2), min(n_pf, i + 3)
    wsel = _bed_midi[lo:hi]
    wsel = wsel[np.isfinite(wsel)]
    _bed_med[i] = np.median(wsel) if len(wsel) >= 3 else np.nan
_bed_notes = []
i = 0
while i < n_pf:
    if not np.isfinite(_bed_med[i]):
        i += 1
        continue
    centre = _bed_med[i]
    j, gap = i, 0
    while j + 1 < n_pf:
        nxt = _bed_med[j + 1]
        if np.isfinite(nxt) and abs(nxt - centre) <= 0.5:
            j += 1
            gap = 0
            centre = 0.9 * centre + 0.1 * nxt
        elif not np.isfinite(nxt) and gap < int(0.070 / hop_s):
            j += 1
            gap += 1
        else:
            break
    if (j - i + 1) * hop_s >= 0.060:
        _bed_notes.append({"onset_s": round(float(pitch_t[i]), 3),
                           "midi": int(round(float(np.nanmedian(_bed_med[i:j + 1]))))})
    i = j + 1
_bed_cov = float(np.mean(voiced))
_verse_span_s = [ (s["t0"], s["t1"]) for s in segments ]
_bed_in_verses = [n for n in _bed_notes
                  if any(t0 <= n["onset_s"] < t1 for t0, t1 in _verse_span_s)]
_dens = (len(_bed_in_verses) /
         max(sum(t1 - t0 for t0, t1 in _verse_span_s), 1.0))
_ivs = [abs(b["midi"] - a["midi"]) for a, b in zip(_bed_notes, _bed_notes[1:])]
_chord_steps = float(np.mean([iv in (3, 4, 5, 7) for iv in _ivs])) if _ivs else 0.0
_TRIADS = []
for _r in range(12):
    _TRIADS.append({_r, (_r + 4) % 12, (_r + 7) % 12})
    _TRIADS.append({_r, (_r + 3) % 12, (_r + 7) % 12})
_pat_ok = _pat_tot = 0
for k in range(len(_bed_notes) - 3):
    w = _bed_notes[k:k + 4]
    pcs = {n["midi"] % 12 for n in w}
    if not any(pcs <= t for t in _TRIADS):
        continue
    ds = [b["midi"] - a["midi"] for a, b in zip(w, w[1:])]
    signs = [1 if d > 0 else (-1 if d < 0 else 0) for d in ds]
    turns = sum(1 for a, b in zip(signs, signs[1:]) if a and b and a != b)
    _pat_tot += 1
    if turns <= 1:
        _pat_ok += 1
_pat_score = (_pat_ok / _pat_tot) if _pat_tot else 0.0
_pc_census = {NOTE_NAMES[p]: int(sum(1 for n in _bed_notes if n["midi"] % 12 == p))
              for p in range(12)}
if _bed_cov < 0.05:
    _arp_verdict = ("UNREADABLE -- the autocorrelation bed track holds "
                    "too little of this mix for pattern evidence to stand")
elif _dens >= 1.5 and _chord_steps >= 0.45 and _pat_score >= 0.35:
    _arp_verdict = ("PRESENT at bench strength -- dense, chord-stepping, "
                    "triad-shaped note motion stands in the bed track")
else:
    _arp_verdict = ("NOT ESTABLISHED -- the bed track's note motion does "
                    "not meet the stated arpeggio thresholds; the numbers "
                    "stand below for re-weighing")
ARPEGGIO_BLOCK = {
    "bed_coverage_frames": round(_bed_cov, 3),
    "bed_notes_total": len(_bed_notes),
    "density_notes_per_s_all_segments": round(_dens, 2),
    "interval_census_abs_semitones": {str(k): int(v) for k, v in
                                      sorted({iv: _ivs.count(iv) for iv in set(_ivs)}.items())},
    "chord_step_share_3_4_5_7": round(_chord_steps, 3),
    "pattern_windows_triad_shaped": _pat_tot,
    "pattern_score_monotone_or_single_turn": round(_pat_score, 3),
    "bed_pitch_class_census": _pc_census,
    "thresholds": "presence: coverage >= 0.05 AND density >= 1.5/s AND "
                  "chord-step share >= 0.45 AND pattern score >= 0.35; "
                  "coverage < 0.05 -> UNREADABLE",
    "verdict": _arp_verdict,
    "confound_stated": "the bed track is the mid channel without the "
                       "vocal gate: where the rap rides, the 'bed' notes "
                       "ARE the voice's intonation. Pattern evidence is "
                       "therefore strongest where the tracker leaves the "
                       "voice (intros, dips) and weakest inside the flow.",
}

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
stats.update({"tempo": TEMPO_BLOCK, "loudness_source": LOUDNESS_BLOCK,
              "stereo": STEREO_BLOCK, "sigma_probe": SIGMA_BLOCK,
              "sigma_sweep_probe": SIGMA_SWEEP_BLOCK,
              "programme": PROGRAMME_BLOCK, "brief_audit": BRIEF_AUDIT,
              "arpeggio": ARPEGGIO_BLOCK,
              "grid": {"bpm": BPM, "beat_s": round(BEAT, 6),
                       "bar_s": round(BAR, 6)}})

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
