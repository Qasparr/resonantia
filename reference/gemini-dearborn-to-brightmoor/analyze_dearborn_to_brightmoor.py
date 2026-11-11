#!/usr/bin/env python3
# =====================================================================
# 93
#
# Epigraph: "The method of science, the aim of religion." — the
# house rule for every intake: state the threshold BEFORE looking,
# print the numbers either way, and crown nothing the bench cannot
# carry.
#
# analyze_dearborn_to_brightmoor.py — the intake bench for
# "DEARBORN TO BRIGHTMOOR", the founder's Gemini (Lyria) strike
# from the Album I (CROWN FIRE SEASON) prompt pack, Track 5
# "DEARBORN TO BRIGHTMOOR" (writing seat ARI SPARKZ; Qasparr
# lead feature; Sage Archer sings the hook),
# taken in under the adoption ruling of 2026-11-10 (Gemini
# strikes; the desk measures, masters, notates, records).
#
# Date: X day of November, Dies Martis, Sol in Scorpio,
#       Anno V:xii e.n. (2026 e.v.)
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice).
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# MECHANISM (what the machine does, step by step):
#   1. Decode the struck MP3; split mid/side. Duration, programme
#      end profile (0.5 s RMS windows read at three thresholds, so
#      the fade's shape is a curve, not a point).
#   2. TEMPO: the house studio estimator (onset-envelope
#      autocorrelation with its log-Gaussian prior) on the mid
#      channel — the same instrument that weighed every prior
#      intake, so the numbers stand comparable. The raw flux
#      autocorrelation is read in the open at the ordered 144 BPM,
#      the headline, the dominant periodicity, and 46 (the ordered
#      clock's half). The desk's first-pass RMS instrument is
#      reproduced beside it. NO clock is crowned unless a single
#      rung stands clean; the zero point between candidates is
#      reported, never smoothed.
#   3. LOUDNESS: house K-weighted UNGATED LUFS + true peak
#      (pipeline scales, 48 kHz weighing copy), cross-checked
#      against ffmpeg's gated BS.1770 (ebur128) as second witness.
#   4. STEREO: L/R correlation + side/mid RMS, global and per
#      30 s window.
#   5. KEY: peak-picked chromagram (80–2500 Hz, local maxima only)
#      vs Krumhansl–Schmuckler profiles, duration-weighted; top
#      three candidates + margin printed. The brief ordered
#      A major; the bench reads what it reads.
#   6. SIGMA PROBES (thresholds stated BEFORE looking, identical
#      to the prior intakes):
#      a. FIXED PAIR at the doctrine seats (200 Hz L / 213 Hz R):
#         certified iff median line-to-shoulder ratio >= 10 dB AND
#         persistence (ratio > 6 dB) >= 0.90 in BOTH channels.
#      b. SWEEP/PAIR probe: 2 s windows, 1 s hop; strongest
#         peak-picked narrowband line per channel in 80–500 Hz;
#         a pair window needs both channels holding a line with
#         ratio > 6 dB. Precedent certification (written for a
#         13–31 Hz SWEEP): pair persistence >= 0.90 AND median
#         ratios >= 10 dB both channels AND median |fR-fL| in
#         [13,31] Hz AND |df| IQR >= 4 Hz. THIS brief ordered
#         exactly that sweep (13–31 Hz, Album I pack), so the
#         bar applies as written, with no caveat; the measured
#         separation and its spread are reported as coordinates
#         beside the verdict either way.
# Runtime: numpy + scipy + soundfile + the house studio pipeline.
# Output: analysis-stats.json beside this file.
# =====================================================================

import json
import os
import re
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

sys.path.insert(0, "/home/hatch/workspace/resonance")
from resonance.studio import performance as _perf
from resonance.studio import pipeline as _pipe

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HERE, "dearborn_to_brightmoor_26_b6wq.mp3")
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ORDERED_BPM = 144.0
ORDERED_BARS = 72  # intro 4 + V1 (Ari) 16 + hook 8 (Sage, sung) + Q feature verse 16 + hook 8 + V2 (Ari) 8 + final hook 8 + outro 4


def frame_signal(x, win, hop):
    n_frames = 1 + (len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n_frames)[:, None]
    return x[idx], n_frames


def db(x):
    return 20.0 * np.log10(np.maximum(x, 1e-12))


def _corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])


# ---------------------------------------------------------------------
# Load + mid/side split.
# ---------------------------------------------------------------------
x, sr = sf.read(AUDIO)
if x.ndim == 1:
    x = np.column_stack([x, x])
L, R = x[:, 0], x[:, 1]
mid = 0.5 * (L + R)
side = 0.5 * (L - R)
dur = len(mid) / sr

stats = {"audio": AUDIO, "sr": int(sr), "duration_s": round(dur, 3)}

# ---------------------------------------------------------------------
# Programme end profile (0.5 s windows, three thresholds).
# ---------------------------------------------------------------------
_pw = int(0.5 * sr)
_pn = len(mid) // _pw
_prms = np.sqrt(np.mean(mid[:_pn * _pw].reshape(_pn, _pw) ** 2, axis=1) + 1e-15)
_pdb = db(_prms)
_pt = (np.arange(_pn) + 0.5) * 0.5


def _last_above(thr):
    idx = np.where(_pdb > thr)[0]
    return round(float(_pt[idx[-1]]), 2) if len(idx) else 0.0


# exact digital silence census (the Sovereign strike's failure species)
_sil = np.all(x == 0.0, axis=1)
stats["programme"] = {
    "duration_s": round(dur, 3),
    "last_window_above_-40dbfs_s": _last_above(-40.0),
    "last_window_above_-50dbfs_s": _last_above(-50.0),
    "last_window_above_-60dbfs_s": _last_above(-60.0),
    "final_window_dbfs": round(float(_pdb[-1]), 1),
    "exact_zero_samples": int(_sil.sum()),
    "exact_zero_seconds": round(float(_sil.sum()) / sr, 3),
}

# ---------------------------------------------------------------------
# TEMPO — house estimator + raw flux reads + first-pass instrument.
# ---------------------------------------------------------------------
_env, _env_rate = _perf.onset_envelope(mid, sr)
_tempo_global = _perf.tempo_from_envelope(_env, _env_rate)
_tempo_windows = _perf.window_tempos(_env, _env_rate, dur)
_wb = [w["bpm"] for w in _tempo_windows if w["bpm"] is not None]
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
                (ORDERED_BPM, round(float(_tempo_global["bpm"]), 2),
                 round(float(_tempo_global["dominant_periodicity_bpm"]), 2),
                 72.0)}
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
_l92 = int(round(_fps * 60 / ORDERED_BPM))
stats["tempo"] = {
    "house_estimator": {"global": _tempo_global, "windows": _tempo_windows,
                        "window_bpm_min": min(_wb), "window_bpm_max": max(_wb),
                        "window_bpm_spread": round(max(_wb) - min(_wb), 2)},
    "flux_raw_ac_at_points": _flux_points,
    "first_pass_instrument_reproduced": {
        "dominant_periodicity_bpm": round(_first_dominant, 2),
        "strength": round(_first_strength, 4),
        "ac_at_144_bpm": round(float(_rac[_l92]), 4)},
}
BPM = float(_tempo_global["bpm"])
BAR = 4.0 * 60.0 / BPM
stats["bpm_measured_bench"] = round(BPM, 2)
stats["bar_s"] = round(BAR, 6)
stats["n_bars_on_bench_grid"] = int(dur // BAR)
stats["brief_audit"] = {
    "brief": "studio-runs/gemini-collabo-cycle/ALBUM-1-PROMPTS.md, Track 5",
    "ordered_bpm": ORDERED_BPM,
    "ordered_total_bars": ORDERED_BARS,
    "expected_span_at_ordered_144bpm_s": round(ORDERED_BARS * 240.0 / ORDERED_BPM, 2),
    "grid_bars_in_file": int(dur // BAR),
    "grid_bar_s": round(BAR, 4),
}

# ---------------------------------------------------------------------
# LOUDNESS of the source as struck (48 kHz weighing copy) + witness.
# ---------------------------------------------------------------------
_x48 = np.stack([resample_poly(x[:, 0], 160, 147),
                 resample_poly(x[:, 1], 160, 147)])
_src_lufs = _pipe.measure_loudness_lufs(_x48, 48000)
_src_tp = _pipe.true_peak_dbtp(_x48, 48000)
_src_spk = float(np.max(np.abs(x)))
_eb = subprocess.run(["ffmpeg", "-v", "info", "-i", AUDIO, "-af",
                      "ebur128=peak=true", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
_mI = re.search(r"Integrated loudness:\s*\n\s*I:\s*(-?[\d.]+) LUFS", _eb)
_mP = re.search(r"True peak:\s*\n\s*Peak:\s*(-?[\d.]+) dBFS", _eb)
stats["loudness_source"] = {
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

# ---------------------------------------------------------------------
# STEREO — global + per 30 s window.
# ---------------------------------------------------------------------
_stereo_windows = []
for _w0 in range(0, int(dur), 30):
    _w1 = min(dur, _w0 + 30)
    _m = slice(int(_w0 * sr), int(_w1 * sr))
    _sd = 0.5 * (x[_m, 0] - x[_m, 1])
    _stereo_windows.append({
        "start_s": _w0, "end_s": round(_w1, 2),
        "corr": round(_corr(x[_m, 0], x[_m, 1]), 4),
        "side_rms_dbfs": round(float(db(np.sqrt(np.mean(_sd ** 2) + 1e-15))), 2)})
stats["stereo"] = {
    "corr_global": round(_corr(L, R), 4),
    "side_rms_dbfs": round(float(db(np.sqrt(np.mean(side ** 2) + 1e-15))), 2),
    "mid_rms_dbfs": round(float(db(np.sqrt(np.mean(mid ** 2) + 1e-15))), 2),
    "windows": _stereo_windows,
}

# ---------------------------------------------------------------------
# SIGMA PROBE A — fixed doctrine pair (threshold stated in header).
# ---------------------------------------------------------------------
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
stats["sigma_probe"] = {
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

# ---------------------------------------------------------------------
# SIGMA PROBE B — pair/sweep tracker (precedent instrument, verbatim
# thresholds; see header for the constant-beat caveat).
# ---------------------------------------------------------------------
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
    _frac_at_ordered = float(np.mean((_dfs >= 11.0) & (_dfs <= 15.0)))
else:
    _med_df = _iqr_df = _med_rL = _med_rR = _frac_in_band = _frac_at_ordered = 0.0
_sweep_cert = (_pair_persistence >= 0.90 and _med_rL >= 10.0 and _med_rR >= 10.0
               and 13.0 <= _med_df <= 31.0 and _iqr_df >= 4.0)
stats["sigma_sweep_probe"] = {
    "method": "2 s windows, 1 s hop; strongest peak-picked narrowband "
              "line per channel in 80-500 Hz; pair window = both "
              "channels hold a line with line-to-shoulder ratio > 6 dB",
    "certification_threshold": "pair persistence >= 0.90 AND median "
                               "ratio >= 10 dB in BOTH channels AND "
                               "median |fR-fL| in [13,31] Hz AND |df| "
                               "IQR >= 4 Hz (sweep, not detune)",
    "ordered_layer": "a binaural Sigma layer SWEEPING slowly "
                       "between 13 and 31 Hz (Album I prompt pack, "
                       "Track 5) -- the precedent sweep bar above "
                       "applies as written; the measured separation "
                       "and its spread are reported below as "
                       "coordinates beside the verdict",
    "n_windows": int(_n_win),
    "pair_windows": len(_pairs),
    "pair_persistence": round(float(_pair_persistence), 3),
    "median_ratio_L_db": round(_med_rL, 2),
    "median_ratio_R_db": round(_med_rR, 2),
    "median_abs_df_hz": round(_med_df, 2),
    "abs_df_iqr_hz": round(_iqr_df, 2),
    "frac_pair_windows_df_in_13_31": round(_frac_in_band, 3),
    "frac_pair_windows_df_within_13_plusminus_2": round(_frac_at_ordered, 3),
    "trajectory": _pairs,
    "certified": bool(_sweep_cert),
    "verdict": "CERTIFIED -- a sweeping binaural pair stands in the "
               "render at the ordered depth" if _sweep_cert else
               "NOT CERTIFIABLE under the precedent sweep bar -- the "
               "trajectory and the measured separation are printed in "
               "full so the finding can be re-weighed.",
}

# ---------------------------------------------------------------------
# KEY — peak-picked chromagram vs Krumhansl-Schmuckler profiles.
# ---------------------------------------------------------------------
NFFT, HOP = 4096, 1024
win = np.hanning(NFFT)
frames, n_fr = frame_signal(mid, NFFT, HOP)
SPEC = np.abs(np.fft.rfft(frames * win, axis=1))
freqs = np.fft.rfftfreq(NFFT, 1.0 / sr)
band = (freqs >= 80.0) & (freqs <= 2500.0)
midi_of_bin = 69.0 + 12.0 * np.log2(np.maximum(freqs, 1.0) / 440.0)
pc_of_bin = np.round(midi_of_bin).astype(int) % 12
is_peak = np.zeros_like(SPEC, dtype=bool)
is_peak[:, 1:-1] = (SPEC[:, 1:-1] > SPEC[:, :-2]) & (SPEC[:, 1:-1] >= SPEC[:, 2:])
mag_c = np.where(is_peak & band[None, :], SPEC, 0.0)
CH = np.zeros((n_fr, 12))
for pc in range(12):
    CH[:, pc] = mag_c[:, pc_of_bin == pc].sum(axis=1)
CH = CH / (np.linalg.norm(CH, axis=1, keepdims=True) + 1e-12)
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
stats["key"] = {
    "top3": [{"key": f"{NOTE_NAMES[r]} {n}", "corr": round(c, 3)}
             for c, r, n in key_scores[:3]],
    "margin": round(key_scores[0][0] - key_scores[1][0], 3),
    "global_chroma": {NOTE_NAMES[i]: round(float(global_chroma[i]), 4)
                      for i in range(12)},
    "ordered": "A major",
}

with open(os.path.join(HERE, "analysis-stats.json"), "w") as fh:
    json.dump(stats, fh, indent=1)
print(json.dumps({k: v for k, v in stats.items() if k != "tempo"}, indent=1)[:200])
print("tempo headline:", stats["tempo"]["house_estimator"]["global"])
print("WROTE analysis-stats.json")

# 93 — Live, Love, and let Love, Live.
