#!/usr/bin/env python3
# =====================================================================
# PRODUCE_NO_ARPEGGIO.PY -- the v5b A/B variant builder (desk tool)
#
# 93. Do what thou wilt shall be the whole of the Law.
#
# Authorship attributed exclusively to
# Johnathan 'Qasparr' Monroe (Greek, -ARR, All Rights Reserved,
# Without Prejudice). Scientific Illuminism: the Method of Science,
# the Aim of Religion.
#
# MECHANISM: rebuild Studio Proof No. 4 ("SINGLE PASS", v5) from
# its own on-disk performance with EXACTLY ONE change -- the
# composed arpeggio layer is never added to the mix. Every other
# stage is the pipeline's own machinery, called in the order
# resonance.studio.performance.produce_performance calls it:
# read performance_48k.wav (the one performance, already rendered
# and resampled in v5; NO MusicGen is invoked here) -> measure the
# realized tempo from the bed's mid channel -> Stereo Law bed
# widening -> [validation only: the arpeggio, scheduled on the
# measured tempo and mixed at its law] -> head/tail fades ->
# master_signal (loudness, then the -1 dBTP ceiling law).
#
# DOCTRINE (the A/B guarantee, the v4b protocol): before the
# variant is struck, this script rebuilds v5 WITH its arpeggio
# layer through the identical code path and masters it; the
# reconstruction is compared sample-by-sample against v5's
# shipped master.wav. Only if the reconstruction matches
# (<= 2 LSB at 24-bit, corr/side/LUFS/TP to the digit) does the
# script proceed -- proof that the performance under both mixes
# is the same performance, and that the variant differs by the
# arpeggio layer and nothing else.
#
# WHY THIS VARIANT EXISTS: the founder's ear on v5 -- hats
# better, but a "weird wind instrument sound" persists. The
# desk's spectral analysis convicts the arpeggio as the source
# candidate: solfeggio-band energy in v5's master runs +9 to
# +27 dB above the raw performance at the ladder frequencies
# (396/417/528/639/741/852 Hz) -- sustained pure-tone ridges the
# performance does not contain. This script therefore also
# weighs those bands in both masters (and in the raw
# performance) across three windows, and the manifest carries
# the table: in v5b the ridges should be gone.
#
# The variant manifest states the single difference on its
# face: arpeggio: ABSENT. The desk re-measures the struck
# master.wav from disk (seconds, correlation, side RMS, LUFS,
# true peak) and those numbers -- not the mastering report's --
# are what the manifest confesses.
#
# Love is the law, love under will.
# 93 -- Live, Love, and let Love, Live.
# =====================================================================

import json
import math
import shutil
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/hatch/workspace/resonance")
sys.path.insert(0, str(ROOT))

from resonance.studio import pipeline as P  # noqa: E402
from resonance.studio import performance as performance_mod  # noqa: E402
from resonance.studio import arpeggio as arpeggio_mod  # noqa: E402

V5 = ROOT / "studio-runs" / "v5-proof-4"
OUT = ROOT / "studio-runs" / "v5b-no-arpeggio"
SR = P.TARGET_SR

LADDER_HZ = [396.0, 417.0, 528.0, 639.0, 741.0, 852.0]
BAND_WINDOWS = [(40.0, 55.0), (100.0, 115.0), (160.0, 175.0)]
BAND_HALF_WIDTH_HZ = 2.0


def log(msg):
    print(f"[v5b] {msg}", flush=True)


def rms(x):
    return float(np.sqrt(np.mean(np.asarray(x, dtype=np.float64) ** 2)))


def band_levels(path):
    """Solfeggio-band levels of one struck file, per desk window.

    MECHANISM: for each window, each channel is Hann-windowed and
    FFT'd; the one-sided power inside +/-2 Hz of each ladder
    frequency is summed, Parseval-normalized (window power
    corrected), and averaged across channels. Reported per
    frequency: the band level in dBFS and the band level relative
    to the window's own broadband RMS -- the ridge height, which
    is the quantity the desk's conviction was about.
    """
    x, sr = P.read_wav_pcm(path)
    assert sr == SR
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x])
    out = {}
    for a, b in BAND_WINDOWS:
        seg = x[:, int(a * SR):int(b * SR)]
        n = seg.shape[1]
        w = np.hanning(n)
        w2 = float(np.mean(w ** 2))
        freqs = np.fft.rfftfreq(n, 1.0 / SR)
        broadband_dbfs = round(20.0 * math.log10(rms(seg)), 2)
        bands = {}
        for f0 in LADDER_HZ:
            mask = ((freqs >= f0 - BAND_HALF_WIDTH_HZ)
                    & (freqs <= f0 + BAND_HALF_WIDTH_HZ))
            acc = 0.0
            for ch in range(seg.shape[0]):
                spectrum = np.fft.rfft(seg[ch] * w)
                acc += 2.0 * float(np.sum(np.abs(spectrum[mask]) ** 2))
            mean_square = acc / seg.shape[0] / (n * n * w2)
            level = round(10.0 * math.log10(mean_square), 2)
            bands[str(int(f0))] = {
                "band_dbfs": level,
                "above_broadband_db": round(level - broadband_dbfs, 2),
            }
        out[f"{a:.0f}-{b:.0f}s"] = {
            "broadband_rms_dbfs": broadband_dbfs,
            "bands": bands,
        }
    return out


def main():
    t_start = time.time()
    OUT.mkdir(parents=True, exist_ok=True)

    # -- the spec: v5's, with the title changed and nothing else ---
    spec = P.validate_spec(json.loads((V5 / "spec.json").read_text(
        encoding="utf-8")))
    assert Path(spec["out_dir"]).resolve() == V5
    spec["out_dir"] = str(OUT)
    spec["title"] = ("SINGLE PASS — Studio Proof No. 4 — "
                     "VARIANT v5b: NO ARPEGGIO (A/B)")

    # -- resume law: the performance is already rendered truth -----
    perf_src = V5 / "performance_48k.wav"
    perf_dst = OUT / "performance_48k.wav"
    if not perf_dst.exists():
        shutil.copy2(perf_src, perf_dst)
    log("performance_48k.wav resumed from v5-proof-4 on disk; "
        "no MusicGen rendering in this run")

    # -- (c) the bed: the one performance at 48 kHz ----------------
    bed, sr = P.read_wav_pcm(perf_dst)
    assert sr == SR
    if bed.ndim == 1:  # MusicGen-small is mono: dual it, honestly.
        bed = np.stack([bed, bed])
    bed = np.asarray(bed, dtype=np.float64)
    total_seconds = bed.shape[1] / SR

    # -- (d) the tempo is the performance's own: measure it --------
    mid = 0.5 * (bed[0] + bed[1])
    env, env_rate = performance_mod.onset_envelope(mid, SR)
    tempo_global = performance_mod.tempo_from_envelope(env, env_rate)
    global_bpm = (tempo_global or {}).get("bpm")
    assert global_bpm is not None, "tempo could not be measured"
    log(f"realized tempo re-measured from the bed: {global_bpm} BPM "
        f"(v5 manifest: 106.24)")

    # -- (e) the Stereo Law, part 2: the bed takes its width -------
    stereo_width = spec["stereo"]["width"]
    stereo_report = {
        "bed_width": stereo_width,
        "spine_panned_by_role": False,
        "low_cut_hz": P.STEREO_LOW_CUT_HZ,
    }
    corr_before = P.channel_correlation(bed)
    bed = P.widen_bed(bed, SR, stereo_width)
    stereo_report.update({
        "bed_correlation_before": round(corr_before, 4),
        "bed_correlation_after": round(P.channel_correlation(bed), 4),
        "bed_low_band_correlation_after": round(
            P.band_correlation(bed, SR, 20.0, P.STEREO_LOW_CUT_HZ), 4),
    })

    head = int(P.HEAD_FADE_S * SR)
    tail = int(P.END_FADE_S * SR)

    def fades(m):
        m = m.copy()
        m[:, :head] *= np.linspace(0.0, 1.0, head)
        m[:, -tail:] *= np.linspace(1.0, 0.0, tail)
        return m

    # -- (f) the arpeggio, rendered for the VALIDATION mix only ----
    schedule = performance_mod.build_arp_schedule(total_seconds,
                                                  global_bpm)
    layer, arp_rep = arpeggio_mod.render_arpeggio(
        spec["arpeggio"], schedule, SR)
    rendered = layer.shape[1]
    target = bed.shape[1]
    if rendered > target:
        layer = layer[:, :target]
        fit = "sliced to the program"
    elif rendered < target:
        layer = np.pad(layer, ((0, 0), (0, target - rendered)))
        fit = "zero-padded to the program"
    else:
        fit = "exact"
    layer_rms = rms(layer)
    ref_rms = rms(bed)
    gain = (ref_rms * 10 ** (spec["arpeggio"]["level_db"] / 20.0)
            / layer_rms)
    arp_rep["mixed_layer_rms_dbfs"] = round(
        20.0 * math.log10(layer_rms * gain), 2)
    schedule_block = {
        "bpm": schedule["bpm"],
        "bpm_source": "measured from the performance itself "
                      "(onset-envelope autocorrelation)",
        "swing": schedule["swing"],
        "total_bars": sum(s["bars"] for s in schedule["sections"]),
        "sections": schedule["sections"],
        "layer_rendered_samples": rendered,
        "program_samples": target,
        "layer_fit": fit,
    }

    # -- VALIDATION: rebuild v5 whole, compare against its master --
    mix_v5 = fades(bed + layer * gain)
    del layer
    mastered_v5, master_rep_v5 = P.master_signal(
        mix_v5, SR, spec["master"]["target_lufs"],
        spec["master"]["ceiling_dbtp"])
    del mix_v5
    v5_master, sr5 = P.read_wav_pcm(V5 / "master.wav")
    assert sr5 == SR and v5_master.shape == mastered_v5.shape
    diff = np.abs(np.asarray(mastered_v5, dtype=np.float32)
                  - np.asarray(v5_master, dtype=np.float32))
    max_diff = float(diff.max())
    lsb = 1.0 / 2 ** 23
    validation = {
        "reconstruction": "v5 rebuilt through the identical code "
                          "path WITH its arpeggio layer and "
                          "mastered; compared against the shipped "
                          "master.wav",
        "max_abs_sample_diff": max_diff,
        "max_abs_sample_diff_lsb24": round(max_diff / lsb, 3),
        "corr_reconstructed": round(P.channel_correlation(mastered_v5), 4),
        "side_reconstructed_dbfs": round(P.side_rms_dbfs(mastered_v5), 2),
        "lufs_reconstructed": master_rep_v5["lufs_after"],
        "true_peak_reconstructed_dbtp": master_rep_v5["true_peak_dbtp"],
        "v5_manifest": {"corr": 0.8995, "side_dbfs": -26.90,
                        "lufs": -14.00, "true_peak_dbtp": -1.79},
    }
    log(f"validation reconstruction: max diff "
        f"{validation['max_abs_sample_diff_lsb24']} LSB, corr "
        f"{validation['corr_reconstructed']}, side "
        f"{validation['side_reconstructed_dbfs']} dBFS, LUFS "
        f"{validation['lufs_reconstructed']}, TP "
        f"{validation['true_peak_reconstructed_dbtp']} dBTP")
    del mastered_v5, v5_master, diff
    if max_diff > 2 * lsb:
        raise SystemExit(
            "VALIDATION FAILED: the rebuilt performance does not "
            "reproduce v5's master; refusing to strike a variant "
            "whose one-change guarantee cannot be proven.")

    # -- THE VARIANT: the same performance, widened, NO ARPEGGIO ---
    mix = fades(bed)
    del bed
    mastered, master_report = P.master_signal(
        mix, SR, spec["master"]["target_lufs"],
        spec["master"]["ceiling_dbtp"])
    del mix
    stereo_report.update({
        "master_correlation": round(P.channel_correlation(mastered), 4),
        "master_side_rms_dbfs": round(P.side_rms_dbfs(mastered), 2),
    })

    # -- strike the files: the pipeline's own finalize bridge ------
    mastered32 = np.asarray(mastered, dtype=np.float32)
    master_npy = OUT / "_master_float.npy"
    np.save(master_npy, mastered32.T.copy())
    master_wav = OUT / "master.wav"
    P._run_bridge({"finalize": [
        {"npy": str(master_npy), "out": str(master_wav),
         "sample_rate": SR, "subtype": "PCM_24"},
    ]}, OUT, log)
    master_npy.unlink()
    preview = OUT / "preview.mp3"
    P._ffmpeg(["-i", str(master_wav), "-codec:a", "libmp3lame",
               "-b:a", "320k", str(preview)], "preview mp3")
    del mastered, mastered32

    # -- desk re-measurement: the struck file, weighed from disk ---
    struck, sr_s = P.read_wav_pcm(master_wav)
    assert sr_s == SR
    remeasure = {
        "seconds": round(struck.shape[1] / SR, 3),
        "samples": int(struck.shape[1]),
        "correlation": round(P.channel_correlation(struck), 4),
        "side_rms_dbfs": round(P.side_rms_dbfs(struck), 2),
        "lufs": round(P.measure_loudness_lufs(
            np.asarray(struck, dtype=np.float64), SR), 2),
        "true_peak_dbtp": round(P.true_peak_dbtp(
            np.asarray(struck, dtype=np.float64), SR), 2),
    }
    del struck
    log(f"variant struck: corr {remeasure['correlation']}, side "
        f"{remeasure['side_rms_dbfs']} dBFS, LUFS {remeasure['lufs']}, "
        f"TP {remeasure['true_peak_dbtp']} dBTP")

    # -- the solfeggio-band check: the ridges, weighed -------------
    log("weighing the solfeggio bands in both masters and the "
        "raw performance...")
    band_check = {
        "method": "per window (the desk's three: 40-55 s, "
                  "100-115 s, 160-175 s): Hann-windowed FFT of "
                  "each channel; one-sided power summed inside "
                  "+/-2 Hz of each ladder frequency, Parseval-"
                  "normalized, averaged across channels. "
                  "band_dbfs is the band's absolute level; "
                  "above_broadband_db is the ridge height against "
                  "the window's own broadband RMS.",
        "ladder_hz": [int(f) for f in LADDER_HZ],
        "v5_master": band_levels(V5 / "master.wav"),
        "v5b_master_no_arpeggio": band_levels(master_wav),
        "raw_performance_48k": band_levels(perf_dst),
    }
    (OUT / "band-check.json").write_text(
        json.dumps(band_check, indent=2), encoding="utf-8")

    # -- provenance carried from v5's manifest ----------------------
    v5_manifest = json.loads((V5 / "manifest.json").read_text(
        encoding="utf-8"))
    v5_arp = v5_manifest["arpeggio"]

    # -- the manifest: v5's shape, the difference on its face ------
    spec_for_manifest = json.loads(json.dumps(spec))
    spec_for_manifest["arpeggio"] = {
        "absent": True,
        "note": "the composed arpeggio layer is OMITTED from this "
                "variant's mix at the desk's A/B order "
                "(2026-11-09) -- the founder heard a 'weird wind "
                "instrument sound' in v5 and the spectral evidence "
                "points at this layer. v5's arpeggio values are "
                "recorded here so the one change is fully "
                "described, not merely named.",
        "v5_values": {"level_db": v5_arp["level_db"],
                      "orbit_hz": v5_arp["orbit_hz"],
                      "strength": v5_arp["strength"],
                      "seed": v5_arp["seed"],
                      "total_notes": v5_arp["total_notes"],
                      "mixed_layer_rms_dbfs":
                          v5_arp["mixed_layer_rms_dbfs"]},
    }
    manifest = {
        "title": spec["title"],
        "title_status": "working title",
        "variant": {
            "of": "studio-runs/v5-proof-4 — SINGLE PASS "
                  "(Studio Proof No. 4)",
            "single_difference": "arpeggio: absent — the composed "
                                 "solfeggio arpeggio layer (1,064 "
                                 "notes, level −9 dB, orbit "
                                 "0.03 Hz, seed 777, on a schedule "
                                 "derived from the measured tempo "
                                 "in v5) is not present in this "
                                 "mix. Everything else is "
                                 "identical: the same performance "
                                 "(performance_48k.wav resumed "
                                 "from v5-proof-4 on disk — no "
                                 "new MusicGen generation), the "
                                 "same Stereo Law widening, the "
                                 "same fades, the same mastering "
                                 "law (−14 LUFS target, −1 dBTP "
                                 "ceiling). Sigma remains absent, "
                                 "as in v5, by design.",
            "validation": validation,
        },
        "dry_run": False,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pipeline": "resonance.studio v1 (proof-of-concept build) — "
                    "variant struck by produce_no_arpeggio.py "
                    "driving the pipeline's own stages",
        "spec": spec_for_manifest,
        "performance": {
            "source_run": "studio-runs/v5-proof-4 (the performance "
                          "is v5's, byte-identical: "
                          "performance_48k.wav copied whole)",
            "method": v5_manifest["performance"]["method"],
            "realized_tempo": v5_manifest["performance"]
                              ["realized_tempo"],
            "tempo_remeasured_this_run_bpm": global_bpm,
            "joins": v5_manifest["performance"]["joins"],
            "join_summary": v5_manifest["performance"]
                            ["join_summary"],
        },
        "render": {"model": "facebook/musicgen-small",
                   "wall_seconds_this_run": 0.0,
                   "note": "no MusicGen rendering in this run — "
                           "the performance was resumed from "
                           "v5-proof-4 on disk"},
        "program": {"seconds": round(total_seconds, 3),
                    "sample_rate": SR, "channels": 2, "bit_depth": 24},
        "arpeggio": {
            "status": "ABSENT",
            "note": "no arpeggio was rendered or mixed; the "
                    "layer's v5 figures stand in the spec block "
                    "above (v5_values) and in the variant block. "
                    "The notation in composition.abc is v5's "
                    "sheet, carried over and marked: every "
                    "notated passage is a passage this mix does "
                    "not contain.",
            "validation_render": arp_rep,
            "validation_schedule": schedule_block,
        },
        "stereo": stereo_report,
        "sigma": v5_manifest["sigma"],
        "master": master_report,
        "desk_remeasure": remeasure,
        "solfeggio_band_check": band_check,
        "files": {
            "master_wav": {"path": str(master_wav),
                           "bytes": master_wav.stat().st_size},
            "preview_mp3": {"path": str(preview),
                            "bytes": preview.stat().st_size},
            "performance_48k_wav": {"path": str(perf_dst),
                                    "bytes": perf_dst.stat().st_size},
            "band_check_json": str(OUT / "band-check.json"),
            "composition_abc": str(OUT / "composition.abc"),
            "spec_json": str(OUT / "spec.json"),
        },
        "wall_seconds_total": round(time.time() - t_start, 2),
        "notes": [
            "VARIANT of v5-proof-4: the single difference is the "
            "ABSENT arpeggio layer; the validation block proves "
            "the performance under this mix is the performance "
            "under v5's, sample for sample.",
            "loudness is K-weighted integrated, UNGATED (BS.1770 "
            "gating omitted in the proof build, stated not hidden).",
            "2 s tail fade + 5 ms head fade applied before "
            "mastering, as in v5.",
            "stereo law: the bed is widened by quadrature side "
            "synthesis above 180 Hz with the mid preserved "
            "exactly and the lows left fully mono — identical "
            "in both mixes; the correlation tick between v5 and "
            "v5b is the arpeggio's own decorrelated orbit "
            "leaving the sum, nothing else.",
            "the solfeggio-band check stands in its own block "
            "and in band-check.json: in v5b the ladder-frequency "
            "ridges the desk measured in v5 should be gone, "
            "back to the raw performance's own levels.",
        ],
    }
    (OUT / "spec.json").write_text(
        json.dumps(spec_for_manifest, indent=2), encoding="utf-8")
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    log(f"done in {manifest['wall_seconds_total']}s -> {master_wav}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
