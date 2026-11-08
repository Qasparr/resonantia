#!/usr/bin/env python3
# =====================================================================
# 93
#
# Epigraph: "The method of science, the aim of religion." — the stop
# rule runs on NUMBERS, not on hope: bleed down, beat intact, or we
# stop and say so.
#
# measure.py — per-pass metrics for the ANVIL AND CROWN instrumental
# production: the BLEED indicator (vocal-band residual, vocal-dense
# vs vocal-sparse frames) and the BEAT-PRESERVATION indicator
# (accompaniment energy vs the previous pass and vs the original).
#
# Date: VIII day of November, Dies Solis, Sol in Scorpio,
#       Anno V:xii e.n. (2026 e.v.)
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice).
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# MECHANISM:
#   Frames of 1.0 s on the mono sum. Vocal band = 300-3400 Hz via
#   FFT band energy. Dense/sparse masks come from the PASS-1 vocal
#   stem's band RMS (dense >= -25 dBFS; sparse <= -45 dBFS) and are
#   FIXED for every pass, so passes are comparable.
#   BLEED(pass) = bandRMS(accomp, dense) - bandRMS(accomp, sparse) dB.
#   BEAT(pass)  = full-band RMS + 4 spectral band energies of accomp,
#   reported vs prev pass and vs original, in body frames (12-146 s)
#   and in sparse frames.
#   Also: per-second vocal-band RMS profile of the original and of
#   the pass-1 vocal stem around the head/tail (announcer bounds).
# =====================================================================
import sys, json
import numpy as np
import soundfile as sf

W = "/home/hatch/workspace/resonance/reference/anvil-crown-instrumental/work/"
SR = 44100
BANDS = {"sub 20-120": (20, 120), "low 120-300": (120, 300),
         "vocal 300-3400": (300, 3400), "high 3400-16000": (3400, 16000)}


def load(p):
    x, sr = sf.read(p, always_2d=True)
    assert sr == SR, (p, sr)
    return x


def frames_mono(x):
    n = len(x) // SR
    return x[: n * SR].mean(axis=1).reshape(n, SR)


def band_db(frame_mat, lo, hi):
    F = np.abs(np.fft.rfft(frame_mat * np.hanning(SR), axis=1))
    freqs = np.fft.rfftfreq(SR, 1 / SR)
    m = (freqs >= lo) & (freqs < hi)
    e = (F[:, m] ** 2).sum(axis=1)
    return 10 * np.log10(e / SR + 1e-20)  # relative dB per frame


def rms_db(frame_mat):
    return 10 * np.log10((frame_mat ** 2).mean(axis=1) + 1e-20)


def main():
    orig = frames_mono(load(W + "original.wav"))
    voc1 = frames_mono(load(W + "p1_vocals.wav"))
    voc_band = band_db(voc1, 300, 3400)
    dense = voc_band >= -25.0
    sparse = voc_band <= -45.0
    body = np.zeros(len(orig), bool); body[12:146] = True
    out = {"n_frames": int(len(orig)),
           "dense_frames": [int(i) for i in np.where(dense)[0]],
           "sparse_frames": [int(i) for i in np.where(sparse)[0]],
           "passes": {}}
    # original reference
    ob = band_db(orig, 300, 3400)
    out["original"] = {
        "bleed_db": float(ob[dense].mean() - ob[sparse].mean()),
        "full_rms_db_body": float(rms_db(orig[body]).mean()),
        "band_rms_db_body": {k: float(band_db(orig[body], *v).mean()) for k, v in BANDS.items()},
    }
    prev = None
    for tag in ("p1", "p2", "p3"):
        try:
            acc = frames_mono(load(W + ("accomp1.wav" if tag == "p1" else f"{tag}_accomp.wav")))
        except Exception:
            continue
        ab = band_db(acc, 300, 3400)
        full_body = float(rms_db(acc[body]).mean())
        bands_body = {k: float(band_db(acc[body], *v).mean()) for k, v in BANDS.items()}
        rec = {"bleed_db": float(ab[dense].mean() - ab[sparse].mean()),
               "band_db_dense": float(ab[dense].mean()),
               "band_db_sparse": float(ab[sparse].mean()),
               "full_rms_db_body": full_body,
               "band_rms_db_body": bands_body,
               "full_rms_db_sparse": float(rms_db(acc[sparse]).mean()),
               "peak_dbfs": float(20 * np.log10(np.abs(load(W + ("accomp1.wav" if tag == "p1" else f"{tag}_accomp.wav"))).max() + 1e-12))}
        if prev is not None:
            rec["vs_prev"] = {
                "bleed_improve_db": prev["bleed_db"] - rec["bleed_db"],
                "full_cost_db": prev["full_rms_db_body"] - full_body,
                "sparse_cost_db": prev["full_rms_db_sparse"] - rec["full_rms_db_sparse"],
                "band_cost_db": {k: prev["band_rms_db_body"][k] - bands_body[k] for k in BANDS},
            }
        out["passes"][tag] = rec
        prev = rec
    # announcer evidence: vocal-band RMS per second, head and tail
    ob_full = band_db(orig, 300, 3400)
    out["head_profile"] = [{"t": i, "mix_vocalband_db": round(float(ob_full[i]), 1),
                            "voc1_band_db": round(float(voc_band[i]), 1)} for i in range(0, 26)]
    out["tail_profile"] = [{"t": i, "mix_vocalband_db": round(float(ob_full[i]), 1),
                            "voc1_band_db": round(float(voc_band[i]), 1)} for i in range(128, len(orig))]
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

# 93 — Live, Love, and let Love, Live.
