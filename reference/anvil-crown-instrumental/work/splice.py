#!/usr/bin/env python3
# =====================================================================
# 93
#
# Epigraph: "The method of science, the aim of religion." — the
# splice points below were MEASURED off the stems, not guessed:
# head corr 0.625->0.32 (p1 leak rides the announcer), tail corr
# -0.22 (no leakage rides the outro), arrangement turns at 14.3 s
# and 131.2 s (transcription form map).
#
# splice.py — final assembly for the ANVIL AND CROWN instrumental.
#
# Date: VIII day of November, Dies Solis, Sol in Scorpio,
#       Anno V:xii e.n. (2026 e.v.)
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice).
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# MECHANISM (sample-exact, stereo, float32 throughout):
#   out = original        for t < 13.575 s
#         equal-power xfade 13.575-14.325 s  (0.75 s, centred 13.95)
#         p2 accomp       for 14.325 <= t < 130.85 s
#         equal-power xfade 130.85-131.60 s (0.75 s, centred 131.225)
#         original        for t >= 131.60 s
#   Then ONE plain gain of +2.57 dB over the whole file (the cleaned
#   body measured 2.57 dB under the original's body RMS; a uniform
#   gain keeps the announcer windows' relative level honest).
#   Peak after gain: +0.32 dBFS source peak + 2.57 dB = +2.89 dBFS in
#   float — the WAV stays float32 (no clipping); the 320k MP3 render
#   is soft-limited to -0.3 dBFS, CONFESSED in the report.
# DOCTRINE: no EQ, no reverb fill, no creative moves. Splice + gain
# + preview limiter, all on the record.
# =====================================================================
import numpy as np
import soundfile as sf

W = "/home/hatch/workspace/resonance/reference/anvil-crown-instrumental/work/"
D = "/home/hatch/workspace/resonance/reference/anvil-crown-instrumental/"
SR = 44100
GAIN_DB = 2.57
XFADE = 0.75


def ep_xfade(dst, src_a, src_b, centre_s):
    """Equal-power crossfade from src_a to src_b centred at centre_s,
    written into dst (all arrays share sample indexing)."""
    c = int(round(centre_s * SR)); h = int(round(XFADE * SR / 2))
    i0, i1 = c - h, c + h
    t = np.linspace(0.0, np.pi / 2, i1 - i0)[:, None]
    dst[i0:i1] = src_a[i0:i1] * np.cos(t) + src_b[i0:i1] * np.sin(t)
    return dst


def main():
    orig, sr = sf.read(W + "original.wav", always_2d=True)
    acc, sr2 = sf.read(W + "p2_accomp.wav", always_2d=True)
    assert sr == sr2 == SR and len(orig) == len(acc)
    out = acc.copy()
    h_end = int(round(13.575 * SR))       # original rules before this
    t_start = int(round(131.60 * SR))     # original rules after this
    out[:h_end] = orig[:h_end]
    out[t_start:] = orig[t_start:]
    out = ep_xfade(out, orig, acc, 13.95)
    out = ep_xfade(out, acc, orig, 131.225)
    out = out * (10 ** (GAIN_DB / 20))
    sf.write(D + "instrumental.wav", out, SR, subtype="FLOAT")
    peak = 20 * np.log10(np.abs(out).max())
    rms = 20 * np.log10(np.sqrt((out ** 2).mean()))
    print(f"instrumental.wav written: {len(out)} samples, peak {peak:.2f} dBFS, RMS {rms:.2f} dBFS")


if __name__ == "__main__":
    main()

# 93 — Live, Love, and let Love, Live.
