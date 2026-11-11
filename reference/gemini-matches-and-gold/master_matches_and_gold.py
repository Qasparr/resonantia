#!/usr/bin/env python3
# =====================================================================
# 93
#
# Epigraph: "The method of science, the aim of religion." — the
# house rule: loudness first, the ceiling is law, and the manifest
# confesses whichever one wins.
#
# master_matches_and_gold.py — the house-law master build sheet
# for "MATCHES AND GOLD", the founder's Gemini (Lyria) strike
# from the Album I (CROWN FIRE SEASON) prompt pack, Track 1
# "SEASON OPENER", taken in under the adoption ruling of
# 2026-11-10 (Gemini strikes; the desk measures, masters,
# notates, records). The bench of record is
# analyze_matches_and_gold.py / analysis-stats.json beside
# this file.
#
# Date: X day of November, Dies Martis, Sol in Scorpio,
#       Anno V:xii e.n. (2026 e.v.)
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice).
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# MECHANISM (what the machine does, step by step):
#   1. Decode the struck MP3 (44.1 kHz) and resample to the house
#      program rate, 48 kHz (the K-weighting coefficients are the
#      published 48 kHz set; the pipeline refuses other rates
#      rather than mis-weigh).
#   2. resonance.studio.pipeline.master_signal applies the law in
#      its own order: K-weighted loudness gained to the -14 LUFS
#      target, soft limiting, then a true-peak trim by pure gain
#      if the -1 dBTP ceiling would break. Its report — including
#      ceiling_overrode_loudness — belongs in the manifest
#      VERBATIM.
#   3. THE SIGMA RIDE. The brief ordered a binaural Sigma layer
#      embedded in the performance (sweeping slowly between 13
#      and 31 Hz). Both intake probes read the strike's own layer
#      NOT CERTIFIABLE (analysis-stats.json: fixed seats far
#      under the bar; pair tracker pair persistence 0.828,
#      median interaural difference 1.5 Hz, 1.3 % of pair
#      windows inside 13-31 Hz — the tracked lines are the
#      programme's own wandering tones, not a binaural pair).
#      Under the founder's embedded-Sigma standing order
#      and the closed Fixtures A/B law (ear verdict 2026-11-10:
#      a house Sigma pair may ride a Gemini master), the house
#      Proven Road pair rides under the master: 200 Hz left /
#      213 Hz right sine, amplitude = mastered-bed RMS x
#      10^(-28/20). It is the Proven Road fixture, confessed in
#      the manifest as such. No trim follows the ride unless the
#      ride itself moves the loudness off the -14.0 target at the
#      manifest's 0.01 LU resolution; the build prints the
#      after-ride loudness so the manifest states what happened.
#   4. Strike matches-and-gold-resonantia.wav (48 kHz, 24-bit) and
#      matches-and-gold-resonantia.mp3 (ffmpeg, libmp3lame 320k). The
#      "-resonantia" suffix is the founder's naming ruling of
#      2026-11-10: the house master is never mistaken for the raw
#      strike, which keeps its uploaded filename.
#   5. VERIFY BY THE RESIDUAL (the fixtures method): final minus
#      pre-ride master is the Sigma layer alone, sample-aligned.
#      Its per-window FFT peaks in 180-230 Hz must read ~200 Hz
#      (L) and ~213 Hz (R), separation ~13.0 Hz. Peak-picking the
#      MIX would find the programme's own tones; the residual is
#      the honest instrument. Then re-read the struck WAV from
#      disk and re-measure it, so verification describes the file
#      that exists, not the array that was intended.
#
# WHAT IS NOT DONE, BY ORDER AND BY LAW:
#   - NO arrangement surgery, no EQ, no fades, no trims beyond
#     the pipeline's own ceiling trim: the waveform is the
#     performance as struck, gained, ceilinged, and ridden only.
#   - NO width work: the strike's image is left as struck; no
#     stems exist, and any widening available to this desk moves
#     the vocal image with the bed. In doubt, leave width as
#     struck, and confess the doubt in the manifest.
# Runtime: numpy + scipy + soundfile + the house studio pipeline.
# =====================================================================

import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

sys.path.insert(0, "/home/hatch/workspace/resonance")
from resonance.studio import pipeline as pipe

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "matches_and_gold__2__25_ajgz.mp3")
MASTER_WAV = os.path.join(HERE, "matches-and-gold-resonantia.wav")
PREVIEW = os.path.join(HERE, "matches-and-gold-resonantia.mp3")
TARGET_LUFS = -14.0
CEILING_DBTP = -1.0
PROGRAM_SR = 48000
SIGMA_LEFT_HZ = 200.0
SIGMA_RIGHT_HZ = 213.0
SIGMA_GAIN_DB = -28.0  # relative to the mastered bed's RMS


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])


def db(x):
    return 20.0 * np.log10(np.maximum(x, 1e-12))


# --- 1. decode + resample to the program rate ------------------------
x, sr = sf.read(SOURCE)
assert sr == 44100 and x.ndim == 2, f"source shape {x.shape} @ {sr}"
corr_before = corr(x[:, 0], x[:, 1])
side_before = 0.5 * (x[:, 0] - x[:, 1])
side_rms_before = float(db(np.sqrt(np.mean(side_before ** 2) + 1e-15)))
x48 = np.stack([resample_poly(x[:, 0], 160, 147),
                resample_poly(x[:, 1], 160, 147)])  # (2, N) @ 48 kHz

# --- 2. the law, applied by the house's own hand ----------------------
y, report = pipe.master_signal(x48, PROGRAM_SR, TARGET_LUFS, CEILING_DBTP)

# --- 3. the Sigma ride (house fixture; confessed in the manifest) -----
bed_rms = float(np.sqrt(np.mean(y**2)))
amp = bed_rms * 10 ** (SIGMA_GAIN_DB / 20.0)
t = np.arange(y.shape[1]) / PROGRAM_SR
sigma = np.stack([amp * np.sin(2 * np.pi * SIGMA_LEFT_HZ * t),
                  amp * np.sin(2 * np.pi * SIGMA_RIGHT_HZ * t)])
y_ridden = y + sigma
lufs_after_ride = pipe.measure_loudness_lufs(y_ridden, PROGRAM_SR)

# --- 4. strike the files ----------------------------------------------
sf.write(MASTER_WAV, y_ridden.T, PROGRAM_SR, subtype="PCM_24")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", MASTER_WAV,
                "-codec:a", "libmp3lame", "-b:a", "320k", PREVIEW],
               check=True)

# --- 5a. verify the pair by the residual (fixtures method) ------------
resid = y_ridden - y  # the Sigma layer alone, sample-aligned
win = 16384
pl_list, pr_list, diffs = [], [], []
for start in range(0, y.shape[1] - win, PROGRAM_SR * 2):
    seg = resid[:, start:start + win].T * np.hanning(win)[:, None]
    spec = np.abs(np.fft.rfft(seg, axis=0))
    freqs = np.fft.rfftfreq(win, 1 / PROGRAM_SR)
    band = (freqs >= 180) & (freqs <= 230)
    f = freqs[band]
    s = spec[band, :]

    def peak_freq(col):
        k = int(np.argmax(col))
        if 0 < k < len(col) - 1:
            d = 0.5 * (np.log(col[k - 1] + 1e-12)
                       - np.log(col[k + 1] + 1e-12)) / (
                np.log(col[k - 1] + 1e-12)
                - 2 * np.log(col[k] + 1e-12)
                + np.log(col[k + 1] + 1e-12) + 1e-12)
            return float(f[k] + d * (f[1] - f[0]))
        return float(f[k])

    pl, pr = peak_freq(s[:, 0]), peak_freq(s[:, 1])
    pl_list.append(pl)
    pr_list.append(pr)
    diffs.append(abs(pr - pl))
within_L = float(np.mean([abs(v - SIGMA_LEFT_HZ) <= 1.0 for v in pl_list]))
within_R = float(np.mean([abs(v - SIGMA_RIGHT_HZ) <= 1.0 for v in pr_list]))
residual_probe = {
    "windows": len(diffs),
    "median_L_hz": round(float(np.median(pl_list)), 2),
    "median_R_hz": round(float(np.median(pr_list)), 2),
    "median_separation_hz": round(float(np.median(diffs)), 2),
    "windows_within_1hz_of_seat": {"left_200hz": within_L,
                                   "right_213hz": within_R},
    "residual_rms_per_channel": round(float(np.sqrt(np.mean(resid[0] ** 2))), 6),
    "implied_pair_amplitude": round(amp, 5),
}
assert abs(residual_probe["median_L_hz"] - SIGMA_LEFT_HZ) < 1.0
assert abs(residual_probe["median_R_hz"] - SIGMA_RIGHT_HZ) < 1.0
assert abs(residual_probe["median_separation_hz"] - 13.0) < 1.0

# --- 5b. verify the file that exists ----------------------------------
z, zsr = sf.read(MASTER_WAV)
z48 = np.stack([z[:, 0], z[:, 1]])
zside = 0.5 * (z[:, 0] - z[:, 1])
zmid = 0.5 * (z[:, 0] + z[:, 1])
verify = {
    "sample_rate": zsr,
    "frames": int(len(z)),
    "duration_s": round(len(z) / zsr, 3),
    "lufs": round(pipe.measure_loudness_lufs(z48, PROGRAM_SR), 2),
    "true_peak_dbtp": round(pipe.true_peak_dbtp(z48, PROGRAM_SR), 2),
    "sample_peak_dbfs": round(float(db(np.max(np.abs(z)))), 2),
    "corr": round(corr(z[:, 0], z[:, 1]), 4),
    "side_rms_dbfs": round(float(db(np.sqrt(np.mean(zside ** 2) + 1e-15))), 2),
    "mid_rms_dbfs": round(float(db(np.sqrt(np.mean(zmid ** 2) + 1e-15))), 2),
}

print(json.dumps({"master": report,
                  "sigma": {"bed_rms": round(bed_rms, 4),
                            "amp": round(amp, 5),
                            "lufs_after_ride": round(lufs_after_ride, 2),
                            "residual_probe": residual_probe},
                  "verification": verify,
                  "width": {"corr_source": round(corr_before, 4),
                            "side_rms_dbfs_source": round(side_rms_before, 2),
                            "corr_master": verify["corr"],
                            "side_rms_dbfs_master": verify["side_rms_dbfs"]}},
                 indent=1))

# 93 — Live, Love, and let Love, Live.
