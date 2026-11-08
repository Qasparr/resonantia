#!/usr/bin/env python3
# =====================================================================
# SIGMA_AUDIT.PY -- the Sigma stem, weighed end to end (desk tool)
#
# 93. Do what thou wilt shall be the whole of the Law.
#
# Authorship attributed exclusively to
# Johnathan 'Qasparr' Monroe (Greek, -ARR, All Rights Reserved,
# Without Prejudice). Scientific Illuminism: the Method of Science,
# the Aim of Religion.
#
# MECHANISM: decode studio-runs/v4-proof-3/sigma.wav and walk it in
# 1-second windows: per-window RMS (dropouts/holes), per-window FFT
# peak per channel (carrier truth across the whole 164.571 s), and
# the maximum sample-to-sample delta per channel against the
# theoretical delta of a pure tone at the measured amplitude
# (clicks/discontinuities). Then decode v4's master.wav and weigh
# the Sigma band (190-220 Hz) against broadband energy, per channel,
# so the desk knows how audible the ground could be inside the mix.
#
# DOCTRINE: report what the numbers say, with timestamps for every
# anomaly -- or state plainly that the stem is clean and constant.
#
# Love is the law, love under will.
# 93 -- Live, Love, and let Love, Live.
# =====================================================================

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/home/hatch/workspace/resonance")
sys.path.insert(0, str(ROOT))
from resonance.studio import pipeline as P  # noqa: E402

V4 = ROOT / "studio-runs" / "v4-proof-3"
OUT = ROOT / "studio-runs" / "v4b-no-sigma"
SR = P.TARGET_SR
WIN = SR  # 1-second windows


def dbfs(rms_val):
    return round(20.0 * np.log10(rms_val), 2) if rms_val > 0 else -120.0


def audit_stem():
    sig, sr = P.read_wav_pcm(V4 / "sigma.wav")
    assert sr == SR and sig.shape[0] == 2
    x = np.asarray(sig, dtype=np.float64)
    n = x.shape[1]
    report = {"file": str(V4 / "sigma.wav"), "samples": int(n),
              "seconds": round(n / SR, 3), "channels": {}}
    anomalies = []

    for ch, name in ((0, "left"), (1, "right")):
        c = x[ch]
        peak = float(np.max(np.abs(c)))
        overall_rms = float(np.sqrt(np.mean(c ** 2)))
        # theoretical max step of a pure tone: A*2*sin(pi*f/sr),
        # evaluated at the channel's dominant carrier (found below
        # from the median window peak) -- first pass at spec values.
        deltas = np.abs(np.diff(c))
        dmax_i = int(np.argmax(deltas))
        longest_zero = 0
        run = 0
        for v in c:
            run = run + 1 if v == 0.0 else 0
            longest_zero = max(longest_zero, run)
        report["channels"][name] = {
            "rms_dbfs": dbfs(overall_rms),
            "peak_dbfs": dbfs(peak),
            "max_sample_delta": float(deltas[dmax_i]),
            "max_sample_delta_at_s": round(dmax_i / SR, 3),
            "longest_exact_zero_run_samples": int(longest_zero),
        }

    # 1-second windows
    nfull = n // WIN
    windows = []
    for w in range(nfull + 1):
        a, b = w * WIN, min((w + 1) * WIN, n)
        if b - a < WIN // 10:
            break
        seg = x[:, a:b]
        entry = {"window": w, "t0_s": round(a / SR, 2),
                 "t1_s": round(b / SR, 2),
                 "partial": bool(b - a < WIN)}
        for ch, name in ((0, "left"), (1, "right")):
            c = seg[ch]
            r = float(np.sqrt(np.mean(c ** 2)))
            spec = np.abs(np.fft.rfft(c))
            freqs = np.fft.rfftfreq(c.shape[0], d=1.0 / SR)
            pk = int(np.argmax(spec[1:]) + 1)
            entry[f"{name}_rms_dbfs"] = dbfs(r)
            entry[f"{name}_fft_peak_hz"] = round(float(freqs[pk]), 2)
        windows.append(entry)

    full = [w for w in windows if not w["partial"]]
    for name, intended in (("left", 200.0), ("right", 213.0)):
        rms_series = np.array([w[f"{name}_rms_dbfs"] for w in full])
        peak_series = np.array([w[f"{name}_fft_peak_hz"] for w in full])
        med_rms = float(np.median(rms_series))
        med_pk = float(np.median(peak_series))
        report["channels"][name].update({
            "intended_hz": intended,
            "window_rms_median_dbfs": round(med_rms, 2),
            "window_rms_min_dbfs": round(float(rms_series.min()), 2),
            "window_rms_max_dbfs": round(float(rms_series.max()), 2),
            "window_fft_peak_median_hz": med_pk,
            "window_fft_peak_min_hz": float(peak_series.min()),
            "window_fft_peak_max_hz": float(peak_series.max()),
        })
        for w in full:
            if abs(w[f"{name}_rms_dbfs"] - med_rms) > 1.0:
                anomalies.append(
                    f"{name} window {w['window']} "
                    f"({w['t0_s']}-{w['t1_s']} s): RMS "
                    f"{w[f'{name}_rms_dbfs']} dBFS deviates from the "
                    f"median {round(med_rms, 2)} by >1 dB")
            if abs(w[f"{name}_fft_peak_hz"] - med_pk) > 1.0:
                anomalies.append(
                    f"{name} window {w['window']} "
                    f"({w['t0_s']}-{w['t1_s']} s): FFT peak "
                    f"{w[f'{name}_fft_peak_hz']} Hz off the median "
                    f"carrier {med_pk} Hz")
        # continuity vs theory: pure-tone max step at peak amplitude
        peak_amp = 10 ** (report["channels"][name]["peak_dbfs"] / 20.0)
        theory = peak_amp * 2.0 * np.sin(np.pi * med_pk / SR)
        got = report["channels"][name]["max_sample_delta"]
        report["channels"][name].update({
            "pure_tone_max_delta_theory": float(theory),
            "delta_ratio_measured_over_theory": round(got / theory, 3),
        })
        if got > 1.5 * theory:
            anomalies.append(
                f"{name}: max sample delta {got:.6f} at "
                f"{report['channels'][name]['max_sample_delta_at_s']} s "
                f"is {round(got / theory, 2)}x the pure-tone bound "
                f"{theory:.6f} -- a click or discontinuity")
        if report["channels"][name]["longest_exact_zero_run_samples"] \
                > SR // 100:
            anomalies.append(
                f"{name}: exact-zero run of "
                f"{report['channels'][name]['longest_exact_zero_run_samples']} "
                f"samples (>10 ms) -- a hole in the stem")
    report["windows"] = windows
    report["anomalies"] = anomalies
    report["verdict"] = ("CLEAN AND CONSTANT — no dropout, hole, "
                         "click, or carrier drift found in any "
                         "1-second window of either channel"
                         if not anomalies else
                         f"{len(anomalies)} anomal"
                         f"{'y' if len(anomalies) == 1 else 'ies'} found")
    return report, x


def audit_in_master(stem):
    master, sr = P.read_wav_pcm(V4 / "master.wav")
    assert sr == SR
    m = np.asarray(master, dtype=np.float64)
    out = {"file": str(V4 / "master.wav"), "channels": {}}
    for ch, name in ((0, "left"), (1, "right")):
        for label, sig in (("master", m[ch]), ("sigma_stem", stem[ch])):
            spec = np.abs(np.fft.rfft(sig)) ** 2
            freqs = np.fft.rfftfreq(sig.shape[0], d=1.0 / SR)
            total = float(spec[1:].sum())
            band = float(spec[(freqs >= 190.0)
                              & (freqs <= 220.0)].sum())
            if label == "master":
                out["channels"].setdefault(name, {})[
                    "master_band_190_220hz_vs_broadband_db"] = round(
                        10.0 * np.log10(band / total), 2)
                out["channels"][name]["master_rms_dbfs"] = dbfs(
                    float(np.sqrt(np.mean(sig ** 2))))
            else:
                stem_band = band
                stem_total = total
        out["channels"][name].update({
            "sigma_stem_rms_vs_master_rms_db": round(
                dbfs(float(np.sqrt(np.mean(stem[ch] ** 2))))
                - out["channels"][name]["master_rms_dbfs"], 2),
            "sigma_stem_band_energy_vs_master_broadband_db": round(
                10.0 * np.log10(stem_band
                                / float((np.abs(np.fft.rfft(m[ch])) ** 2)
                                        [1:].sum())), 2),
            "sigma_stem_band_share_note": "the stem's 190-220 Hz "
            "energy weighed against the master's TOTAL energy; the "
            "master's own band ratio above includes the bed's "
            "low piano content in the same band",
            "_stem_band_frac_of_own_energy": round(
                10.0 * np.log10(stem_band / stem_total), 2),
        })
    return out


def main():
    stem_report, stem = audit_stem()
    mix_report = audit_in_master(stem)
    full = {"stem_audit": stem_report, "sigma_in_v4_master": mix_report}
    (OUT / "sigma-audit.json").write_text(
        json.dumps(full, indent=2), encoding="utf-8")
    print(json.dumps({"stem_verdict": stem_report["verdict"],
                      "anomalies": stem_report["anomalies"],
                      "channels": stem_report["channels"],
                      "sigma_in_v4_master": mix_report}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
