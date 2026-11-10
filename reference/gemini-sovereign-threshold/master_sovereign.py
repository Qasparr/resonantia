#!/usr/bin/env python3
# =====================================================================
# 93
#
# Epigraph: "The method of science, the aim of religion." — the
# house rule: loudness first, the ceiling is law, and the manifest
# confesses whichever one wins.
#
# master_sovereign.py — the house-law master of "SOVEREIGN AT THE
# THRESHOLD", the founder's second Gemini (Lyria) strike, struck by
# him from the desk's filed 49-bar brief (studio-runs/gemini-49-bars/
# prompt.txt) and taken in under the adoption ruling of 2026-11-10
# (Gemini strikes; the desk measures, masters, notates, records).
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
#      ceiling_overrode_loudness — is carried into the manifest
#      VERBATIM. The manifest never has to lie; neither does this.
#   3. Strike master.wav (48 kHz, 24-bit) and preview.mp3 (ffmpeg,
#      libmp3lame 320k — the studio chain's own preview settings).
#   4. Re-read the struck WAV from disk and re-measure it, so the
#      manifest's verification block describes the file that
#      exists, not the array that was intended.
#
# WHAT IS NOT DONE, BY ORDER AND BY LAW:
#   - NO Sigma layer is added. Whether Sigma rides a Gemini strike
#     is the founder's open call; the desk does not presume it.
#   - NO arrangement surgery, no EQ, no fades, no trims: the
#     waveform is the performance as struck, gained and ceilinged
#     only. (The performance chain's head/tail fades belong to
#     assembly of takes; there are no takes here.)
#   - NO width work unless the measured image leaves the vocal
#     plainly untouched by a conservative correction; the corr is
#     measured first and the decision confessed with its number.
#     There are no stems; any widening available to this desk
#     moves the vocal image with the bed wherever the vocal lives
#     in the side signal. In doubt, leave width as struck.
# Runtime: numpy + scipy + soundfile + the house studio pipeline.
# =====================================================================

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

sys.path.insert(0, "/home/hatch/workspace/resonance")
from resonance.studio import pipeline as pipe

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "sovereign_at_the_threshold__1__1_ygcl.mp3")
MASTER_WAV = os.path.join(HERE, "master.wav")
PREVIEW = os.path.join(HERE, "preview.mp3")
TARGET_LUFS = -14.0
CEILING_DBTP = -1.0
PROGRAM_SR = 48000


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])


# --- 1. decode + resample to the program rate ------------------------
x, sr = sf.read(SOURCE)
assert sr == 44100 and x.ndim == 2, f"source shape {x.shape} @ {sr}"
corr_before = corr(x[:, 0], x[:, 1])
x48 = np.stack([resample_poly(x[:, 0], 160, 147),
                resample_poly(x[:, 1], 160, 147)])  # (2, N) @ 48 kHz

# --- 2. the law, applied by the house's own hand ----------------------
y, report = pipe.master_signal(x48, PROGRAM_SR, TARGET_LUFS, CEILING_DBTP)

# --- 3. strike the files ----------------------------------------------
sf.write(MASTER_WAV, y.T, PROGRAM_SR, subtype="PCM_24")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", MASTER_WAV,
                "-codec:a", "libmp3lame", "-b:a", "320k", PREVIEW],
               check=True)

# --- 4. verify the file that exists ------------------------------------
z, zsr = sf.read(MASTER_WAV)
z48 = np.stack([z[:, 0], z[:, 1]])
verify = {
    "sample_rate": zsr,
    "duration_s": round(len(z) / zsr, 3),
    "lufs": round(pipe.measure_loudness_lufs(z48, PROGRAM_SR), 2),
    "true_peak_dbtp": round(pipe.true_peak_dbtp(z48, PROGRAM_SR), 2),
    "corr": round(corr(z[:, 0], z[:, 1]), 4),
}

manifest = {
    "title": "SOVEREIGN AT THE THRESHOLD — house master of the founder's Gemini strike",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "pipeline": "resonance.studio.pipeline.master_signal (intake pass, "
                "gemini-sovereign-threshold)",
    "provenance": {
        "source_file": "sovereign_at_the_threshold__1__1_ygcl.mp3",
        "source_sha256": sha256(SOURCE),
        "engine": "Gemini (Lyria), struck by the founder himself",
        "prompt": "the desk's filed 49-bar brief — studio-runs/"
                  "gemini-49-bars/prompt.txt (pushed faf3a3b): exactly "
                  "49 bars, intro 3 / Verse I 20 / refrain 3 / Verse II "
                  "20 / outro 3; Detroit bounce, F minor; solfeggio "
                  "arpeggio inside the performance; Sigma pair "
                  "sweeping 13-31 Hz in the pocket",
        "struck": "2026-11-10, uploaded by the founder the same day",
        "ruling": "adoption, 2026-11-10 — Gemini strikes; the desk "
                  "measures, masters, notates, records",
        "audio_custody": "local only — rented-engine reference audio "
                         "does not enter git (house rule)",
    },
    "spec": {"target_lufs": TARGET_LUFS, "ceiling_dbtp": CEILING_DBTP,
             "program_sample_rate": PROGRAM_SR, "bit_depth": 24},
    "master": report,
    "width": {
        "decision": "LEFT AS STRUCK",
        "corr_source": round(corr_before, 4),
        "corr_master": verify["corr"],
        "reason": "no stems exist; the vocal rides the mid and bleeds "
                  "into what side signal there is, so any widening "
                  "available to this desk would move the vocal image "
                  "with the bed. The conservative correction cannot "
                  "be shown to leave the vocal untouched — the doubt "
                  "is real, so width is left as struck, confessed.",
    },
    "sigma": {
        "added": False,
        "reason": "whether Sigma rides a Gemini strike is the "
                  "founder's open call, not the desk's; no layer "
                  "was presumed. What the strike itself carries is "
                  "weighed by both probes in analysis-stats.json "
                  "(sigma_probe at the doctrine seats; "
                  "sigma_sweep_probe for the ordered 13-31 Hz sweep).",
    },
    "verification": verify,
    "files": {
        "source_mp3": {"path": "reference/gemini-sovereign-threshold/"
                               "sovereign_at_the_threshold__1__1_ygcl.mp3",
                       "bytes": os.path.getsize(SOURCE),
                       "sha256": sha256(SOURCE)},
        "master_wav": {"path": "reference/gemini-sovereign-threshold/"
                               "master.wav",
                       "bytes": os.path.getsize(MASTER_WAV),
                       "sha256": sha256(MASTER_WAV)},
        "preview_mp3": {"path": "reference/gemini-sovereign-threshold/"
                                "preview.mp3",
                        "bytes": os.path.getsize(PREVIEW),
                        "sha256": sha256(PREVIEW)},
    },
    "notes": [
        "loudness is K-weighted integrated, UNGATED (BS.1770 gating "
        "omitted in the house scales, stated not hidden).",
        "the ceiling is law: had the true-peak trim taken the "
        "master below the loudness target, "
        "master.ceiling_overrode_loudness would say so in the "
        "open; the master block carries the gain, the trim and "
        "the flag as struck, and this prose adds nothing to them.",
        "no head or tail fades: those belong to the performance "
        "chain's assembly of takes; an intake master of a finished "
        "render leaves the waveform's edges as struck.",
        "nothing rides and nothing was removed: no Sigma, no EQ, "
        "no width process, no edit of any kind between decode and "
        "the loudness/ceiling law.",
    ],
}
with open(os.path.join(HERE, "manifest.json"), "w") as fh:
    json.dump(manifest, fh, indent=1)

print(json.dumps({"master": report, "verification": verify,
                  "width_corr_before": round(corr_before, 4)}, indent=1))

# 93 — Live, Love, and let Love, Live.
