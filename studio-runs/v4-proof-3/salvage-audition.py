# 93
# salvage-audition.py -- weigh v3's master for FX worth lifting.
#
# MECHANISM: every 0.25 s hop over the v3 master, compute the
# spectral centroid (25 ms frames) and the 6-12 kHz band share;
# then for each structural joint of the v3 grid, and for the
# strongest windows anywhere, report (a) centroid slope + fit R^2
# (a sweep is a ramp that holds its line), (b) HF sparkle share,
# (c) RMS. Distinctiveness is judged against the track-wide
# distribution of the same numbers -- a fragment earns salvage by
# standing out of ITS OWN record, not by an agent's adjectives.
#
# Authorship: Johnathan 'Qasparr' Monroe, ARR. Proof No. 3 desk work.
# ---------------------------------------------------------------------

import json
import math
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/resonance")
from resonance.studio.pipeline import read_wav_pcm  # noqa: E402

MASTER = "/home/hatch/workspace/resonance/studio-runs/" \
         "brightmoor-rachets-v3/master.wav"
BPM = 137.0
JOINT_BARS = (8, 16, 32, 40, 56, 64, 80, 88, 104, 112)


def frame_stats(mono, sr, hop_s=0.25, frame_s=0.05):
    hop = int(hop_s * sr)
    frame = int(frame_s * sr)
    times, cents, hf_share, rms = [], [], [], []
    for at in range(0, mono.size - frame, hop):
        x = mono[at:at + frame] * np.hanning(frame)
        spec = np.abs(np.fft.rfft(x))
        freqs = np.fft.rfftfreq(frame, d=1.0 / sr)
        total = float(spec.sum()) or 1.0
        cents.append(float((spec * freqs).sum() / total))
        hf = (freqs >= 6000) & (freqs <= 12000)
        hf_share.append(float(spec[hf].sum() / total))
        rms.append(float(np.sqrt(np.mean(mono[at:at + frame] ** 2))))
        times.append(at / sr)
    return (np.array(times), np.array(cents), np.array(hf_share),
            np.array(rms))


def window_report(times, cents, hf, rms, t0, t1):
    m = (times >= t0) & (times < t1)
    if m.sum() < 4:
        return None
    t, c = times[m], cents[m]
    slope, icept = np.polyfit(t - t0, c, 1)
    fit = slope * (t - t0) + icept
    ss_res = float(np.sum((c - fit) ** 2))
    ss_tot = float(np.sum((c - c.mean()) ** 2)) or 1.0
    return {
        "t0": round(t0, 2), "t1": round(t1, 2),
        "centroid_slope_hz_s": round(float(slope), 1),
        "centroid_fit_r2": round(1.0 - ss_res / ss_tot, 3),
        "centroid_start_hz": round(float(c[0]), 0),
        "centroid_end_hz": round(float(c[-1]), 0),
        "hf_share_mean": round(float(hf[m].mean()), 4),
        "hf_share_max": round(float(hf[m].max()), 4),
        "rms_dbfs": round(20 * math.log10(float(rms[m].mean())
                                          + 1e-12), 2),
    }


def main():
    arr, sr = read_wav_pcm(MASTER)
    mono = np.asarray(arr, dtype=np.float64).mean(axis=0)
    times, cents, hf, rms = frame_stats(mono, sr)
    bar_s = 240.0 / BPM
    # Distribution yardstick: every non-overlapping 1.75 s window.
    allw = []
    t = 0.0
    while t + 1.75 < mono.size / sr:
        r = window_report(times, cents, hf, rms, t, t + 1.75)
        if r:
            allw.append(r)
        t += 1.75
    slopes = np.array([abs(w["centroid_slope_hz_s"]) for w in allw])
    hfs = np.array([w["hf_share_mean"] for w in allw])
    print(f"track-wide |centroid slope|: median "
          f"{np.median(slopes):.0f}, p90 {np.percentile(slopes, 90):.0f}"
          f", max {slopes.max():.0f} Hz/s")
    print(f"track-wide HF share: median {np.median(hfs):.4f}, "
          f"p90 {np.percentile(hfs, 90):.4f}, max {hfs.max():.4f}")
    print("\nJOINT WINDOWS (2 s ending at each v3 joint):")
    joints = []
    for bar in JOINT_BARS:
        jt = bar * bar_s
        r = window_report(times, cents, hf, rms, jt - 2.0, jt)
        r["joint_bar"] = bar
        r["joint_s"] = round(jt, 2)
        joints.append(r)
        print(f"  bar {bar:>3} ({jt:6.1f}s): slope "
              f"{r['centroid_slope_hz_s']:+7.0f} Hz/s R2 "
              f"{r['centroid_fit_r2']:.2f}  centroid "
              f"{r['centroid_start_hz']:.0f}->{r['centroid_end_hz']:.0f}"
              f"  HF {r['hf_share_mean']:.4f}  RMS "
              f"{r['rms_dbfs']:.1f}")
    print("\nTOP SWEEP WINDOWS ANYWHERE (|slope|, R2 >= 0.5):")
    cand = [w for w in allw if abs(w["centroid_slope_hz_s"]) > 500
            and w["centroid_fit_r2"] >= 0.5]
    cand.sort(key=lambda w: -abs(w["centroid_slope_hz_s"]))
    for w in cand[:8]:
        print(f"  {w['t0']:6.1f}-{w['t1']:6.1f}s: slope "
              f"{w['centroid_slope_hz_s']:+7.0f} Hz/s R2 "
              f"{w['centroid_fit_r2']:.2f}  centroid "
              f"{w['centroid_start_hz']:.0f}->{w['centroid_end_hz']:.0f}"
              f"  HF {w['hf_share_mean']:.4f}")
    print("\nTOP HF-SPARKLE WINDOWS (hf_share_mean):")
    sp = sorted(allw, key=lambda w: -w["hf_share_mean"])[:8]
    for w in sp:
        print(f"  {w['t0']:6.1f}-{w['t1']:6.1f}s: HF "
              f"{w['hf_share_mean']:.4f} (max {w['hf_share_max']:.4f})"
              f"  slope {w['centroid_slope_hz_s']:+7.0f}  RMS "
              f"{w['rms_dbfs']:.1f}")
    out = {"yardstick": {
               "slope_p90": float(np.percentile(slopes, 90)),
               "slope_max": float(slopes.max()),
               "hf_p90": float(np.percentile(hfs, 90)),
               "hf_max": float(hfs.max())},
           "joints": joints, "top_sweeps": cand[:8],
           "top_sparkle": sp}
    with open("/home/hatch/workspace/resonance/studio-runs/"
              "v4-proof-3/salvage-audition.json", "w") as fh:
        json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()

# 93 -- Live, Love, and let Love, Live.
