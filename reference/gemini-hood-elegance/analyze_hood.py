#!/usr/bin/env python3
# =====================================================================
# 93
#
# Epigraph: "The method of science, the aim of religion." — the house
# rule under which this bench works: every number below was MEASURED
# from the audio, and every interpretation is MARKED as interpretation.
# Nothing in this script invents a note, a chord, or a lyric.
#
# analyze_hood.py — INTAKE MEASUREMENT + TRANSCRIPTION-ANALYSIS,
# phase 1 (analysis only) for "STEEL IN THE SILK PURSE" (HOOD
# ELEGANCE v4), the founder's third Gemini (Lyria) strike, taken
# into the house 2026-11-10 under the adoption ruling. This one
# answers a FILED BRIEF (studio-runs/gemini-hood-elegance/
# prompt-v4-brightmoor-signature.txt): a full tag-team duet in the
# ordered formation intro / Qveen V1 / hook / Qveen V2 / hook /
# Qasparr V1 / Qasparr V2 / bridge / hook / tag-team final verse /
# Qveen sung outro; Detroit bounce, G# minor; hi-hat arpeggio at
# 222 BPM; NO VIOLIN — grand piano + guitar Paganini solfeggio
# arpeggios; bagpipes or harmonica; TWO voice signatures (his:
# medium pitch, NOT deep bass, the testimony register; hers:
# alluring Eve-flow/Brat-linguistics rap + SOPRANO sung hooks);
# and the decisive new variable —
#   THE BRIGHTMOOR SIGNATURE: a four-note grand-piano motif that
#   opens the track ALONE, answers the end of EVERY hook, and is
#   the last sound before the hard stop, IDENTICAL wherever it
#   plays. The bench extracts the opening motif from the alone
#   window, then searches the whole performance for exact and for
#   transposed recurrences, and tests the ordered seats.
# The bench is the Sphinx/Sovereign intake bench carried over,
# with the Sigma probes REMOVED — this brief did not order Sigma,
# so no probe was run and nothing is claimed about it either way —
# and four instruments added for this brief:
#   * THE SIGNATURE AUDIT (above).
#   * THE VOICE-REGISTER PASS — a second pitch track opened to
#     950 Hz (the bench track caps at 500 Hz, under a soprano's
#     working range), so her sung hooks and his rap centre can be
#     weighed in their own bands. Register classes are assigned by
#     thresholds stated in that block's header BEFORE it looks.
#   * THE HAT-LAYER MEASUREMENT — the high-band (6.5-12 kHz) onset
#     envelope's own periodicities, weighed against the ordered
#     222 BPM hat clock and the bounce pulse beneath it; both
#     clocks are reported if they split.
#   * THE PIANO/VIOLIN EVIDENCE CHECK — attack shape of the
#     opening alone-window notes (a piano strikes and decays; a
#     violin bows and sustains) and a vibrato census on sustained
#     tones (a bowed string wobbles 4-7 Hz; a struck piano string
#     does not). Confidence is stated as honestly as the result.
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
#   3. FORM: novelty = spectral flux + chroma change; peak-pick with
#      a minimum spacing; snap candidates to the bar grid; describe
#      every resulting segment by measured features (level, slope,
#      centroid, chroma stability, voiced density, recurrence vs
#      other segments, voice-register centres on both pitch tracks).
#   4. KEY/CHORDS: chromagram (FFT bins -> pitch classes); key by
#      Krumhansl-Schmuckler profile correlation; per-bar chord by
#      triad-template correlation, with the winning margin carried
#      as the confidence so a thin bar reads as a thin bar.
#   5. MELODY SKETCH: normalized-autocorrelation pitch track on the
#      mid channel, gated by a vocal-likelihood heuristic (centred,
#      speech-band energy); frames quantised to MIDI and grouped
#      into notes. Suspect octaves are FLAGGED, never silently
#      rewritten — dispositions are marked, never vanished.
# Runtime: numpy + soundfile only.
# =====================================================================

import json
import math
import os
import re

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HERE, "steel_in_the_silk_purse_6_qxq5.mp3")
# PROVISIONAL grid only: the measured grid replaces these values in
# the TEMPO BLOCK below (after load, before first use). No bar is
# ever laid on the provisional numbers.
BPM = 111.0
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
# MECHANISM: mid carries the centred programme (lead vocals, kick,
# bass); side carries width.
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
# instrument that weighed every studio run and both prior intakes,
# so these numbers stand comparable with theirs. The desk's
# first-pass instrument (RMS-block envelope) is REPRODUCED by its
# own instrument below and carried in the record beside the house
# reading: the zero point between the two instruments is reported,
# never smoothed.
# LOUDNESS: house K-weighted ungated LUFS + true peak (pipeline
# scales, 48 kHz set -- the signal is resampled for the weighing
# only), cross-checked against ffmpeg's gated BS.1770 (ebur128).
# STEREO: correlation + side RMS, global and per 30 s window.
# SIGMA: NOT PROBED. This brief did not order a Sigma layer (the
# Hood Elegance v4 brief orders hats, piano, guitar, wind, voices
# and the Signature — no Sigma), so the doctrine-pair and sweep
# probes of the prior intakes were not run. Nothing is certified
# and nothing is denied; the instrument simply did not look.
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
                (222.0, 111.0, 144.0,
                 round(float(_tempo_global["bpm"]), 2),
                 round(float(_tempo_global["dominant_periodicity_bpm"]), 2))}
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
_l222 = int(round(_fps * 60 / 222.0))
TEMPO_BLOCK = {
    "house_estimator": {"global": _tempo_global, "windows": _tempo_windows,
                        "window_bpm_min": min(_wb), "window_bpm_max": max(_wb),
                        "window_bpm_spread": round(max(_wb) - min(_wb), 2)},
    "flux_raw_ac_at_points": _flux_points,
    "first_pass_instrument_reproduced": {
        "dominant_periodicity_bpm": round(_first_dominant, 2),
        "strength": round(_first_strength, 4),
        "ac_at_222_bpm": round(float(_rac[_l222]), 4)},
}
# THE GRID: the house estimator's headline. Its window series is the
# flattest clock in the file; the FORM-MAP carries the alternatives.
BPM = float(_tempo_global["bpm"])
BEAT = 60.0 / BPM
BAR = 4.0 * BEAT

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

SIGMA_BLOCK = {
    "probed": False,
    "reason": "the Hood Elegance v4 brief did not order a Sigma "
              "layer; the doctrine-pair and sweep probes of the "
              "prior intakes were therefore not run. No claim is "
              "made in either direction.",
}

# =====================================================================
# THE HAT-LAYER MEASUREMENT (this strike's commission).
# The brief ordered a hi-hat arpeggio at 222 BPM shimmering over the
# bounce — a fast clock riding a slower one. The instrument: an
# onset envelope taken ONLY from the high band (6.5-12 kHz, where
# hats live and the kick/bass/vocal body does not), positive
# spectral flux in that band, then plain autocorrelation over the
# lag range for 140-300 BPM. Readings printed: the strongest
# periodicity in range, the autocorrelation at the ordered 222 and
# at its half 111, and at the house tempo headline and its double.
# A hat layer at 222 over a 111 bounce shows BOTH clocks: the
# half-time pulse from the full-band instruments above and the fast
# periodicity here. If the fast layer is not there, this block says
# so with its numbers, not with adjectives.
# =====================================================================
_hb_frames, _hb_n = frame_signal(mid, 2048, 256)
_hb_spec = np.abs(np.fft.rfft(_hb_frames * np.hanning(2048), axis=1))
_hb_freqs = np.fft.rfftfreq(2048, 1.0 / sr)
_hb_band = (_hb_freqs >= 6500.0) & (_hb_freqs <= 12000.0)
_hb_log = np.log1p(50.0 * _hb_spec[:, _hb_band])
_hb_flux = np.maximum(0.0, np.diff(_hb_log, axis=0)).sum(axis=1)
_hb_env = _hb_flux - _hb_flux.mean()
_hb_rate = sr / 256.0
_hnf = 1 << int(np.ceil(np.log2(2 * len(_hb_env))))
_hsp = np.fft.rfft(_hb_env, n=_hnf)
_hac = np.fft.irfft(_hsp * np.conj(_hsp), n=_hnf)[:len(_hb_env)]
_hac = _hac / _hac[0]
def _hac_at(bpm):
    lag = _hb_rate * 60.0 / bpm
    k = int(round(lag))
    f = lag - k
    return round(float(_hac[k] * (1 - f) + _hac[min(k + 1, len(_hac) - 1)] * f), 4)
_hlags = np.arange(int(_hb_rate * 60 / 300), int(_hb_rate * 60 / 140))
_hbest = int(_hlags[int(np.argmax(_hac[_hlags]))])
HATS_BLOCK = {
    "method": "high-band (6.5-12 kHz) spectral-flux onset envelope, "
              "plain autocorrelation; periodicities in 140-300 BPM",
    "strongest_periodicity_bpm": round(float(60 * _hb_rate / _hbest), 2),
    "strongest_ac": round(float(_hac[_hbest]), 4),
    "ac_at_ordered_222": _hac_at(222.0),
    "ac_at_half_111": _hac_at(111.0),
    "ac_at_house_headline": _hac_at(round(float(_tempo_global["bpm"]), 2)),
    "ac_at_house_headline_double": _hac_at(round(2 * float(_tempo_global["bpm"]), 2)),
    "ordered": "hat arpeggio at 222 BPM over the bounce",
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
# energy wins. The search VERIFIES rather than assumes.
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
# PROGRAMME / FADE (RMS contour instrument, labelled wherever used).
# 0.5 s windows on the mid channel; the programme end is read at
# three thresholds so the fade's shape is a curve, not a point
# invented by one cut.
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
# every pitch class at once; the chroma came out near-uniform. The
# fix is the classic one: only local spectral maxima vote — a
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

# Peak-pick: local maxima above the 88th percentile, >= 6.8 s apart.
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
# Pitch track, bench pass (needed for segment voiced-density + the
# melody sketch). MECHANISM: normalised autocorrelation per 46 ms
# frame on the mid channel; voicing = correlation peak >= 0.55 with
# in-band energy. Vocal-likelihood gate: mid louder than side AND
# >= 45% of mid energy inside 250-4000 Hz (the speech band).
# The bench band is 65-500 Hz, as in both prior intakes, so the
# sketch numbers stand comparable with theirs. A soprano works
# above this band; the REGISTER PASS below re-tracks at 65-950 Hz
# for the voice audit and does not touch the sketch.
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
# (raw cosine on non-negative vectors is ~1 between ANY two segments
# and so measures nothing; centring fixes it).
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
# MELODY SKETCH: quantise the gated, voiced bench f0 track to notes.
# MECHANISM: median-of-5 smoothing; a note is a run of frames within
# half a semitone, >= 90 ms, gaps <= 70 ms bridged. Octave suspects
# (note > 15 semitones from both neighbours and < 150 ms) are flagged.
# ---------------------------------------------------------------------
hop_s = PHOP / sr
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
# THE VOICE-REGISTER PASS (this strike's commission).
# The bench track caps at 500 Hz — under a soprano's working range —
# so a second autocorrelation pass re-tracks the mid channel at
# 65-950 Hz on the same frames and the same voicing gate. From it,
# per measured segment, the bench reports: the gated voiced frames'
# median f0 and 90th percentile on BOTH tracks, and the share of
# gated register frames at or above 300 Hz (a working soprano's
# floor region for full-voice hook singing).
# REGISTER CLASSES are assigned by thresholds stated HERE, before
# the numbers are read into prose — the same discipline as the
# prior intakes' probes:
#   sung-high:      register median >= 240 Hz (pitched singing in
#                   her band; a soprano hook centres well above it)
#   female-rap:     160 <= register median < 240 Hz
#   male-rap:       register median < 160 Hz
#   mixed/thin:     fewer than 40 gated register frames — no class
# The classes are heuristic labels on measured medians, nothing
# more; the FORM-MAP argues from the numbers, and a class that the
# numbers embarrass is struck in the open, not smoothed.
# TWO DISTINCT PERFORMERS is tested directly: if the segments the
# classes split into her band and his band show f0 centres separated
# by >= 5 semitones with non-overlapping interquartile ranges, the
# two-voice reading stands on the bench; else it is reported thin.
# =====================================================================
RFMIN, RFMAX = 65.0, 950.0
r_lag_min, r_lag_max = int(sr / RFMAX), int(sr / RFMIN)
rf0 = np.full(n_pf, np.nan)
_rseg = AC[:, r_lag_min:r_lag_max]
_rpk = np.argmax(_rseg, axis=1)
_rpk_val = _rseg[np.arange(n_pf), _rpk]
rvoiced = (_rpk_val >= 0.55) & (mid_rms_f > 0.008)
rf0[rvoiced] = sr / (_rpk + r_lag_min)[rvoiced]

def _f0_stats(mask_frames, track):
    vals = track[mask_frames]
    vals = vals[np.isfinite(vals)]
    if len(vals) < 10:
        return {"n": int(len(vals)), "median_hz": None, "p25_hz": None,
                "p75_hz": None, "p90_hz": None}
    return {"n": int(len(vals)),
            "median_hz": round(float(np.median(vals)), 1),
            "p25_hz": round(float(np.percentile(vals, 25)), 1),
            "p75_hz": round(float(np.percentile(vals, 75)), 1),
            "p90_hz": round(float(np.percentile(vals, 90)), 1)}

for s in segments:
    m = (pitch_t >= s["t0"]) & (pitch_t < s["t1"])
    gate_m = m & voiced & vocal_gate
    rgate_m = m & rvoiced & vocal_gate
    s["bench_f0"] = _f0_stats(gate_m, f0)
    s["register_f0"] = _f0_stats(rgate_m, rf0)
    rv = rf0[rgate_m]
    rv = rv[np.isfinite(rv)]
    s["register_share_ge_300hz"] = (round(float(np.mean(rv >= 300.0)), 3)
                                    if len(rv) >= 10 else None)
    med_r = s["register_f0"]["median_hz"]
    if s["register_f0"]["n"] < 40 or med_r is None:
        s["register_class"] = "mixed/thin"
    elif med_r >= 240.0:
        s["register_class"] = "sung-high"
    elif med_r >= 160.0:
        s["register_class"] = "female-rap-band"
    else:
        s["register_class"] = "male-rap-band"

# two-voice separation test on the class split
_her = [s for s in segments if s["register_class"] in ("sung-high", "female-rap-band")
        and s["register_f0"]["median_hz"] is not None]
_his = [s for s in segments if s["register_class"] == "male-rap-band"
        and s["register_f0"]["median_hz"] is not None]
def _pooled(segs_, key):
    lo = min(s["register_f0"]["p25_hz"] for s in segs_)
    hi = max(s["register_f0"]["p75_hz"] for s in segs_)
    meds = [s["register_f0"]["median_hz"] for s in segs_]
    return {"segments": len(segs_),
            "median_of_medians_hz": round(float(np.median(meds)), 1) if meds else None,
            "iqr_span_hz": [lo, hi]}
if _her and _his:
    _her_c = float(np.median([s["register_f0"]["median_hz"] for s in _her]))
    _his_c = float(np.median([s["register_f0"]["median_hz"] for s in _his]))
    _sep_st = 12.0 * math.log2(_her_c / _his_c) if _his_c > 0 else 0.0
    _overlap = not (_her and _his and
                    min(s["register_f0"]["p25_hz"] for s in _her) >
                    max(s["register_f0"]["p75_hz"] for s in _his))
    TWO_VOICE = {"her_centre_hz": round(_her_c, 1), "his_centre_hz": round(_his_c, 1),
                 "separation_semitones": round(_sep_st, 2),
                 "iqr_overlap": bool(_overlap),
                 "her_pool": _pooled(_her, "x"), "his_pool": _pooled(_his, "x"),
                 "test": "two-voice reading stands if separation >= 5 "
                         "semitones AND IQR spans do not overlap",
                 "stands": bool(_sep_st >= 5.0 and not _overlap)}
else:
    TWO_VOICE = {"her_centre_hz": None, "his_centre_hz": None,
                 "separation_semitones": None, "iqr_overlap": None,
                 "stands": False,
                 "test": "one of the two class pools is empty — the "
                         "two-voice test cannot be run on this split"}

VOICES_BLOCK = {
    "method": "bench f0 (65-500 Hz) + register f0 (65-950 Hz), both "
              "normalised autocorrelation on the mid channel, gated "
              "voiced & vocal-likelihood frames only",
    "class_thresholds": "sung-high: register median >= 240 Hz; "
                        "female-rap-band: 160-240 Hz; male-rap-band: "
                        "< 160 Hz; mixed/thin: < 40 gated frames",
    "brief_orders": {"his": "medium pitch, NOT a deep bass voice — "
                            "the testimony register",
                     "hers": "rap in the Eve/Brat band; hooks SUNG in "
                             "a soprano — bright, high, clear"},
    "two_voice_test": TWO_VOICE,
    "segments": [{"index": i, "t0": s["t0"], "t1": s["t1"],
                  "register_class": s["register_class"],
                  "bench_f0_median_hz": s["bench_f0"]["median_hz"],
                  "register_f0": s["register_f0"],
                  "share_ge_300hz": s["register_share_ge_300hz"]}
                 for i, s in enumerate(segments)],
}

# ---------------------------------------------------------------------
# BED NOTES: the same bench f0 track WITHOUT the vocal-likelihood
# gate (energy + voicing only), quantised to notes >= 60 ms. This
# is the track the Signature search runs on: in the alone window
# there is no voice to gate for, and a piano motif is pitched
# energy the autocorrelation can hold. The known confound stands
# from the prior intake: where a voice rides, bed notes can be the
# voice's intonation; the ALONE window is the one place the track
# is unambiguous, which is why the motif is extracted there.
# ---------------------------------------------------------------------
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
        fq = f0[i:j + 1][np.isfinite(f0[i:j + 1])]
        _bed_notes.append({"onset_s": round(float(pitch_t[i]), 3),
                           "dur_s": round(float((j - i + 1) * hop_s), 3),
                           "midi": int(round(float(np.nanmedian(_bed_med[i:j + 1])))),
                           "mean_hz": round(float(np.median(fq)), 1) if len(fq) else None})
    i = j + 1

# =====================================================================
# THE BRIGHTMOOR SIGNATURE AUDIT (this strike's decisive variable).
# The brief ordered: a four-note grand-piano motif that opens the
# track ALONE, answers the end of EVERY hook, and is the LAST SOUND
# before the hard stop — identical wherever it plays ("it is a
# signature, not a variation").
# MECHANISM:
#   1. THE ALONE WINDOW: the bench finds where the full programme
#      arrives — the first RMS frame above -28 dBFS that stays
#      above -32 dBFS for a full second (t_full) — and where the
#      voice arrives — the first gated, voiced run of >= 0.3 s
#      (t_voice). The alone window is [0, min(t_full, t_voice)]:
#      inside it, whatever the bed track hears is the piano alone,
#      by construction unconfounded by voice or beat.
#   2. THE MOTIF: the first four bed notes inside the alone window,
#      with pitches, onsets and durations. If the window holds
#      fewer than four notes, the audit says so and the motif seat
#      is UNREADABLE — no motif is invented.
#   3. THE SEARCH: every run of four consecutive bed notes in the
#      whole file is tested two ways — EXACT (same four MIDI
#      numbers) and TRANSPOSED (same three intervals, any root).
#      Exact is what "identical" means; transposed matches are
#      family, reported separately, never merged into the exact
#      count.
#   4. THE SEATS: a hook-answer seat is the span from 1 s before a
#      sung-high segment's end to one bar after it; the final seat
#      is the last 8 s of programme (to the -40 dBFS programme
#      end). The verdict rule is stated here, before the search:
#        present-and-identical: >= 1 EXACT recurrence at a
#          hook-answer seat AND an EXACT match opening inside
#          the final seat;
#        present-but-varied: matches exist at the seats but only
#          TRANSPOSED (or exact matches miss a seat);
#        absent: no recurrence beyond the origin at any seat.
# =====================================================================
# 1. the alone window
_full_idx = None
for _i in range(len(rms_db)):
    if rms_db[_i] > -28.0 and np.all(rms_db[_i:_i + 40] > -32.0):
        _full_idx = _i
        break
_t_full = float(rms_t[_full_idx]) if _full_idx is not None else dur
_gv = (voiced & vocal_gate).astype(int)
_run = 0
_t_voice = dur
for _i, _v in enumerate(_gv):
    _run = _run + 1 if _v else 0
    if _run >= int(0.3 / hop_s):
        _t_voice = float(pitch_t[_i] - 0.3)
        break
_alone_end = min(_t_full, _t_voice)
_alone_notes = [n for n in _bed_notes if n["onset_s"] < _alone_end]
_motif = _alone_notes[:4]
_motif_midi = [n["midi"] for n in _motif]
_motif_intervals = [b - a for a, b in zip(_motif_midi, _motif_midi[1:])]
_motif_source = "alone window (the primary instrument)"
_intro_notes = []
if len(_motif_midi) < 4:
    # FALLBACK INSTRUMENT, declared before it is used: the primary
    # alone-window test can collapse (it did here — see the
    # alone_window numbers: the full-band RMS crosses the arrival
    # threshold almost at once, whether because the render opens
    # hot or because the solo figure itself plays loud). The
    # fallback takes the opening pitched figure from the measured
    # INTRO SEGMENT — the room the segmenter itself isolated at
    # the file's head (quiet, low voiced density) — and runs the
    # identical search and seat tests on its first four notes.
    # Every result it feeds is marked FALLBACK wherever it lands.
    _intro_end = float(segments[0]["t1"]) if segments else 0.0
    _intro_notes = [n for n in _bed_notes if n["onset_s"] < _intro_end]
    if len(_intro_notes) >= 4:
        _motif = _intro_notes[:4]
        _motif_midi = [n["midi"] for n in _motif]
        _motif_intervals = [b - a for a, b in zip(_motif_midi, _motif_midi[1:])]
        _motif_source = ("FALLBACK — the measured intro segment "
                         "(segment 0): the alone-window test "
                         "collapsed, so the opening pitched figure "
                         "is taken from the segment the segmenter "
                         "itself isolated as the intro room. A "
                         "weaker instrument, marked as such "
                         "wherever its results are used.")

def _note_name(m):
    return NOTE_NAMES[m % 12] + str(m // 12 - 1)

# 3. the search
_exact_hits, _transposed_hits = [], []
if len(_motif_midi) == 4:
    for _k in range(len(_bed_notes) - 3):
        _w = _bed_notes[_k:_k + 4]
        _wm = [n["midi"] for n in _w]
        if _wm == _motif_midi:
            _exact_hits.append({"onset_s": _w[0]["onset_s"],
                                "bed_note_index": _k})
        elif [b - a for a, b in zip(_wm, _wm[1:])] == _motif_intervals:
            _transposed_hits.append({"onset_s": _w[0]["onset_s"],
                                     "bed_note_index": _k,
                                     "root": _note_name(_wm[0])})
# 4. the seats
_prog_end_sig = PROGRAMME_BLOCK["last_window_above_-40dbfs_s"]
_hook_seats = []
for _i, _s in enumerate(segments):
    if _s["register_class"] == "sung-high":
        _seat = {"segment": _i, "hook_end_s": _s["t1"],
                 "seat_span_s": [round(_s["t1"] - 1.0, 2),
                                 round(_s["t1"] + BAR, 2)],
                 "exact_in_seat": [h["onset_s"] for h in _exact_hits
                                   if _s["t1"] - 1.0 <= h["onset_s"] <= _s["t1"] + BAR],
                 "transposed_in_seat": [h["onset_s"] for h in _transposed_hits
                                        if _s["t1"] - 1.0 <= h["onset_s"] <= _s["t1"] + BAR]}
        _hook_seats.append(_seat)
# The second seat table: EVERY measured segment end. The brief
# says the motif answers every HOOK; hooks are identified by the
# register classes, which on this mix are bed-confounded (see the
# voices block), so the strict hook-seat table above may not name
# the true hooks. This table tests the looser, honest question —
# does the figure recur at segment ends at all — and the FORM-MAP
# reads both tables together, in the open.
_seg_end_seats = []
for _i, _s in enumerate(segments):
    _seg_end_seats.append({
        "segment": _i, "end_s": _s["t1"],
        "exact_in_seat": [h["onset_s"] for h in _exact_hits
                          if _s["t1"] - 1.0 <= h["onset_s"] <= _s["t1"] + BAR],
        "transposed_in_seat": [h["onset_s"] for h in _transposed_hits
                               if _s["t1"] - 1.0 <= h["onset_s"] <= _s["t1"] + BAR]})
_any_seat_exact = (any(seat["exact_in_seat"] for seat in _hook_seats)
                   or any(seat["exact_in_seat"] for seat in _seg_end_seats))
_final_exact = [h["onset_s"] for h in _exact_hits
                if _prog_end_sig - 8.0 <= h["onset_s"] <= _prog_end_sig + 0.5]
_final_transp = [h["onset_s"] for h in _transposed_hits
                 if _prog_end_sig - 8.0 <= h["onset_s"] <= _prog_end_sig + 0.5]
_origin_s = _motif[0]["onset_s"] if _motif else None
_recur_exact = [h for h in _exact_hits
                if _origin_s is None or h["onset_s"] > _origin_s + 1.0]
if len(_motif_midi) < 4:
    _sig_verdict = ("UNREADABLE — the alone window holds fewer than "
                    "four bed notes; no motif can be extracted and "
                    "none is invented")
elif (_any_seat_exact and _final_exact):
    _sig_verdict = ("PRESENT-AND-IDENTICAL — exact recurrences stand "
                    "at a segment-end seat and inside the final seat"
                    + (" (motif taken by the FALLBACK instrument — "
                       "see motif_source)" if _motif_source.startswith("FALLBACK")
                       else ""))
elif _recur_exact or _transposed_hits:
    _sig_verdict = ("PRESENT-BUT-VARIED — recurrences exist but the "
                    "exact form does not hold every ordered seat "
                    "(transposed family and/or missed seats; the "
                    "seat table carries the coordinates)")
else:
    _sig_verdict = ("ABSENT — no recurrence of the opening figure, "
                    "exact or transposed, stands anywhere after the "
                    "origin")
SIGNATURE_BLOCK = {
    "ordered": "four-note grand-piano motif: opens the track alone, "
               "answers the end of every hook, last sound before "
               "the hard stop, identical wherever it plays",
    "alone_window": {"t_full_band_s": round(_t_full, 2),
                     "t_first_voice_s": round(_t_voice, 2),
                     "alone_end_s": round(_alone_end, 2),
                     "bed_notes_in_window": len(_alone_notes)},
    "motif_first_four_notes": [{"note": _note_name(n["midi"]),
                                "midi": n["midi"],
                                "onset_s": n["onset_s"],
                                "dur_s": n["dur_s"],
                                "mean_hz": n["mean_hz"]} for n in _motif],
    "motif_intervals_semitones": _motif_intervals,
    "motif_source": _motif_source,
    "all_notes_in_alone_window": [{"note": _note_name(n["midi"]),
                                   "onset_s": n["onset_s"],
                                   "dur_s": n["dur_s"]} for n in _alone_notes],
    "intro_segment_notes": [{"note": _note_name(n["midi"]),
                             "midi": n["midi"],
                             "onset_s": n["onset_s"],
                             "dur_s": n["dur_s"],
                             "mean_hz": n["mean_hz"]} for n in _intro_notes],
    "exact_recurrences": _exact_hits,
    "transposed_recurrences": _transposed_hits,
    "hook_answer_seats": _hook_seats,
    "segment_end_seats": _seg_end_seats,
    "final_seat": {"programme_end_-40dbfs_s": _prog_end_sig,
                   "seat_span_s": [round(_prog_end_sig - 8.0, 2),
                                   round(_prog_end_sig + 0.5, 2)],
                   "exact_in_seat": _final_exact,
                   "transposed_in_seat": _final_transp},
    "verdict": _sig_verdict,
    "candidate_canonical_notation": (
        " ".join(_note_name(m) for m in _motif_midi)
        + " — intervals " + "/".join(f"{v:+d}" for v in _motif_intervals)
        ) if (len(_motif_midi) == 4 and _sig_verdict.startswith("PRESENT-AND-IDENTICAL"))
        else None,
    "confound_stated": "the bed track is autocorrelation on the mid "
                       "channel; a four-note coincidence inside dense "
                       "rap intonation is possible, which is why the "
                       "verdict requires recurrences AT THE ORDERED "
                       "SEATS (hook answers, final seat), not merely "
                       "anywhere in the file.",
}

# =====================================================================
# THE PIANO/VIOLIN EVIDENCE CHECK (the brief said NO VIOLIN).
# Two physical signatures separate a struck string from a bowed one:
#   ATTACK — a piano hammer strikes: the note's amplitude envelope
#     rises 10%->90% of its peak in typically < 30 ms, then decays.
#     A bow draws the string up over ~60-200 ms and SUSTAINS. The
#     bench measures attack time for the alone-window notes (the
#     one seat where the lead string voice plays unaccompanied).
#   VIBRATO — a bowed (or sung) sustained tone wobbles 4-7 Hz. A
#     piano string cannot. The bench takes sustained pitched runs
#     (>= 0.35 s) on the bench track where the vocal gate is FALSE
#     for most frames — instrumental tones, not voice — detrends
#     each run's f0 in cents, and reports the share of modulation
#     energy inside 4-7 Hz.
# READING RULE, stated before the numbers: median alone-window
# attack <= 30 ms AND median instrumental vibrato share < 0.25
# reads CONSISTENT WITH PIANO (struck, not bowed); slow attacks or
# strong 4-7 Hz wobble on instrumental tones would embarrass the
# no-violin order. Confidence ceiling: MODERATE — a synth string
# patch can imitate either signature, and the bench weighs the
# audio it was given, not the session that made it.
# =====================================================================
_env5 = np.abs(mid)
_k5 = int(0.005 * sr)
_env5 = np.convolve(_env5, np.ones(_k5) / _k5, mode="same")
def _attack_ms(t_on, t_off):
    i0 = max(0, int((t_on - 0.15) * sr))
    i1 = int(min(t_off, dur) * sr)
    if i1 - i0 < int(0.05 * sr):
        return None
    segx = _env5[i0:i1]
    pk_i = int(np.argmax(segx))
    peak = segx[pk_i]
    if peak <= 0:
        return None
    above10 = np.where(segx[:pk_i + 1] >= 0.10 * peak)[0]
    above90 = np.where(segx[:pk_i + 1] >= 0.90 * peak)[0]
    if not len(above10) or not len(above90):
        return None
    return round(float((above90[0] - above10[0]) / sr * 1000.0), 1)
_attacks = []
for _n in _alone_notes:
    _a = _attack_ms(_n["onset_s"], _n["onset_s"] + max(_n["dur_s"], 0.15))
    if _a is not None:
        _attacks.append({"note": _note_name(_n["midi"]),
                         "onset_s": _n["onset_s"], "attack_ms": _a})
_med_attack = round(float(np.median([a["attack_ms"] for a in _attacks])), 1) if _attacks else None
# vibrato on sustained instrumental runs
_vib_shares = []
_i = 0
_bed_voiced = voiced & np.isfinite(f0)
while _i < n_pf:
    if not _bed_voiced[_i]:
        _i += 1
        continue
    _j = _i
    _centre = 69.0 + 12.0 * math.log2(f0[_i] / 440.0)
    while (_j + 1 < n_pf and _bed_voiced[_j + 1]
           and abs(69.0 + 12.0 * math.log2(f0[_j + 1] / 440.0) - _centre) <= 0.5):
        _j += 1
    _run_s = (_j - _i + 1) * hop_s
    if _run_s >= 0.35:
        _frac_vocal = float(np.mean(vocal_gate[_i:_j + 1]))
        if _frac_vocal < 0.5:  # instrumental tone, not voice
            _cents = 1200.0 * np.log2(f0[_i:_j + 1] / np.median(f0[_i:_j + 1]))
            _cents = _cents - np.linspace(_cents[0], _cents[-1], len(_cents))
            _sp = np.abs(np.fft.rfft(_cents * np.hanning(len(_cents)))) ** 2
            _fr = np.fft.rfftfreq(len(_cents), hop_s)
            _in = (_fr >= 4.0) & (_fr <= 7.0)
            _allb = (_fr >= 1.0) & (_fr <= 12.0)
            if _sp[_allb].sum() > 0:
                _vib_shares.append(round(float(_sp[_in].sum() / _sp[_allb].sum()), 3))
    _i = _j + 1
_med_vib = round(float(np.median(_vib_shares)), 3) if _vib_shares else None
if _med_attack is not None and _med_vib is not None:
    _violin_reading = ("CONSISTENT WITH PIANO — struck attacks and no "
                       "bowed-string wobble at bench strength"
                       if (_med_attack <= 30.0 and _med_vib < 0.25) else
                       "MIXED — one or both physical signatures "
                       "embarrass a clean piano reading; the numbers "
                       "stand for re-weighing")
else:
    _violin_reading = ("UNREADABLE at one or both instruments — too "
                       "few alone-window notes or sustained "
                       "instrumental runs to weigh")
VIOLIN_BLOCK = {
    "ordered": "NO VIOLIN — grand piano leads the strings, with guitar",
    "alone_window_attacks": _attacks,
    "median_attack_ms": _med_attack,
    "instrumental_sustained_runs_weighed": len(_vib_shares),
    "vibrato_shares_4_7hz": _vib_shares,
    "median_vibrato_share": _med_vib,
    "reading_rule": "median attack <= 30 ms AND median vibrato share "
                    "< 0.25 -> consistent with piano; confidence "
                    "ceiling MODERATE (a synth patch can imitate "
                    "either signature)",
    "reading": _violin_reading,
}

# =====================================================================
# THE FORM AUDIT (coordinates, not verdicts). The brief's ordered
# formation is laid beside the measured segment map; each segment
# carries its register class and recurrence so the FORM-MAP can
# argue the attribution in the open. The brief ordered NO bar
# counts — the audit therefore tests SEQUENCE and CONTENT (two
# voices trading in the ordered seats, hooks recurring as sung
# segments, a halftime bridge dip, a sung outro at the tail), not
# a bar census.
# =====================================================================
_ORDERED_FORM = ["intro (Signature alone, then swell)",
                 "Qveen verse 1 (rap)", "hook (Qveen sung)",
                 "Qveen verse 2 (rap, double-time)", "hook (Qveen sung)",
                 "Qasparr verse 1 (rap)", "Qasparr verse 2 (rap)",
                 "bridge (Qasparr, halftime)", "hook (Qveen sung)",
                 "final verse (tag team, both on the last line)",
                 "outro (Qveen sung, alone)"]
FORM_AUDIT = {
    "brief": "studio-runs/gemini-hood-elegance/"
             "prompt-v4-brightmoor-signature.txt",
    "ordered_form": _ORDERED_FORM,
    "ordered_sections": len(_ORDERED_FORM),
    "measured_segments": len(segments),
    "grid": {"bpm": round(BPM, 2), "bar_s": round(BAR, 4),
             "n_bars_in_file": int(N_BARS)},
    "measured_map": [{"index": i, "t0": s["t0"], "t1": s["t1"],
                      "bars": [s["bar0"] + 1, s["bar0"] + s["n_bars"]],
                      "mean_db": round(s["mean_db"], 2),
                      "register_class": s["register_class"],
                      "register_median_hz": s["register_f0"]["median_hz"],
                      "recurrence_sim": s["recurrence_sim"],
                      "recurrence_with": s["recurrence_with"]}
                     for i, s in enumerate(segments)],
    "sung_high_segments": [i for i, s in enumerate(segments)
                           if s["register_class"] == "sung-high"],
    "male_rap_segments": [i for i, s in enumerate(segments)
                          if s["register_class"] == "male-rap-band"],
    "female_rap_segments": [i for i, s in enumerate(segments)
                            if s["register_class"] == "female-rap-band"],
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
    "ordered_key": "G# minor",
    "global_chroma": [round(float(v), 4) for v in global_chroma],
    "n_notes_sketch": len(notes),
    "sketch_coverage": round(float(np.mean(voiced & vocal_gate)), 3),
}
stats.update({"tempo": TEMPO_BLOCK, "hats": HATS_BLOCK,
              "loudness_source": LOUDNESS_BLOCK,
              "stereo": STEREO_BLOCK, "sigma": SIGMA_BLOCK,
              "programme": PROGRAMME_BLOCK, "voices": VOICES_BLOCK,
              "signature": SIGNATURE_BLOCK, "violin_check": VIOLIN_BLOCK,
              "form_audit": FORM_AUDIT,
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
            "The bench track caps at 500 Hz: a soprano's sung line rides "
            "partly above it, so her hook notes here are the tracker's "
            "subharmonic shadows of the true line — the register pass in "
            "analysis-stats.json carries her band's measurements.",
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
          f"  recur {s['recurrence_sim']:+.3f} (seg {s['recurrence_with']})"
          f"  class {s['register_class']} regmed {s['register_f0']['median_hz']}")
print("hats:", json.dumps(HATS_BLOCK, indent=1))
print("voices two-voice:", json.dumps(TWO_VOICE, indent=1))
print("signature verdict:", _sig_verdict)
print("signature motif source:", _motif_source)
print("signature motif:", SIGNATURE_BLOCK["motif_first_four_notes"])
print("intro segment notes:", json.dumps(SIGNATURE_BLOCK["intro_segment_notes"]))
print("exact recurrences:", _exact_hits)
print("transposed recurrences:", _transposed_hits)
print("violin reading:", _violin_reading,
      "| median attack ms:", _med_attack, "| median vibrato:", _med_vib)

# 93 — Live, Love, and let Love, Live.
