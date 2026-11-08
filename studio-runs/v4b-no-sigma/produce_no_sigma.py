#!/usr/bin/env python3
# =====================================================================
# PRODUCE_NO_SIGMA.PY -- the v4b A/B variant builder (desk tool)
#
# 93. Do what thou wilt shall be the whole of the Law.
#
# Authorship attributed exclusively to
# Johnathan 'Qasparr' Monroe (Greek, -ARR, All Rights Reserved,
# Without Prejudice). Scientific Illuminism: the Method of Science,
# the Aim of Religion.
#
# MECHANISM: rebuild Studio Proof No. 3 ("Velvet Hammer", v4) from
# its own on-disk segments with EXACTLY ONE change -- the Sigma
# binaural layer is never added to the mix. Every other stage is the
# pipeline's own machinery, called in the pipeline's own order:
# resample (ffmpeg) -> per-section RMS match to the median (+/-6 dB
# clamp) -> equal-power crossfade stitch (2 whole bars) -> Stereo
# Law bed widening -> sampled-kit spine placement -> composed
# arpeggio -> head/tail fades -> master_signal (loudness, then the
# -1 dBTP ceiling law). No MusicGen is invoked: the twelve segNN.wav
# files are copied from v4-proof-3 and consumed as rendered truth.
#
# DOCTRINE (the A/B guarantee): before the variant is struck, this
# script rebuilds v4 WITH its Sigma layer through the identical code
# path and masters it; the reconstruction is compared sample-by-
# sample against v4's shipped master.wav. Only if the reconstruction
# matches (<= 2 LSB at 24-bit) does the script proceed -- proof that
# the bed under both mixes is the same bed, and that the variant
# differs by the Sigma layer and nothing else.
#
# The variant manifest states the single difference on its face:
# sigma: ABSENT. The desk re-measures the struck master.wav from
# disk (correlation, side RMS, LUFS, true peak) and those numbers --
# not the mastering report's -- are what the manifest confesses.
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

from resonance import grid  # noqa: E402
from resonance.studio import pipeline as P  # noqa: E402
from resonance.studio import spine as spine_mod  # noqa: E402
from resonance.studio import arpeggio as arpeggio_mod  # noqa: E402

V4 = ROOT / "studio-runs" / "v4-proof-3"
OUT = ROOT / "studio-runs" / "v4b-no-sigma"
SR = P.TARGET_SR


def log(msg):
    print(f"[v4b] {msg}", flush=True)


def rms(x):
    return float(np.sqrt(np.mean(np.asarray(x, dtype=np.float64) ** 2)))


def main():
    t_start = time.time()
    OUT.mkdir(parents=True, exist_ok=True)

    # -- the spec: v4's, with two fields changed and no others --------
    spec = P.validate_spec(json.loads((V4 / "spec.json").read_text(
        encoding="utf-8")))
    assert spec["out_dir"] == str(V4)
    spec["out_dir"] = str(OUT)
    spec["title"] = ("VELVET HAMMER (Instrumental) — Studio Proof "
                     "No. 3 — VARIANT v4b: NO SIGMA (A/B)")

    # -- resume law: the segments are already rendered truth ---------
    sections = spec["sections"]
    for i in range(len(sections)):
        src = V4 / f"seg{i:02d}.wav"
        dst = OUT / f"seg{i:02d}.wav"
        if not dst.exists():
            shutil.copy2(src, dst)
        assert P._segment_file_ok(dst, sections[i]["seconds"]), \
            f"segment {i} failed the wholeness check"
    log("12 segments resumed from v4-proof-3 on disk; "
        "no MusicGen rendering in this run")

    # -- (b) resample + RMS match + stitch (produce(), mirrored) -----
    arrays, seg_rms = [], []
    for i, s in enumerate(sections):
        src = OUT / f"seg{i:02d}.wav"
        dst = OUT / f"seg{i:02d}_48k.wav"
        P._ffmpeg(["-i", str(src), "-ar", str(SR), "-ac", "2",
                   "-c:a", "pcm_s24le", str(dst)], f"resample seg{i:02d}")
        arr, sr = P.read_wav_pcm(dst)
        assert sr == SR
        if arr.ndim == 1:
            arr = np.stack([arr, arr])
        arrays.append(np.asarray(arr, dtype=np.float64))
        seg_rms.append(rms(arrays[-1]))
    median_rms = float(np.median(seg_rms))
    for i, arr in enumerate(arrays):
        if seg_rms[i] > 0:
            gain = median_rms / seg_rms[i]
            gain = min(max(gain, 10 ** (-6 / 20)), 10 ** (6 / 20))
            arrays[i] = arr * gain
    fade = P._crossfade_samples(spec)
    bed = arrays[0]
    for nxt in arrays[1:]:
        t = np.linspace(0.0, 1.0, fade, dtype=np.float64)
        out_w = np.cos(t * np.pi / 2.0)
        in_w = np.sin(t * np.pi / 2.0)
        overlap = (bed[:, -fade:] * out_w + nxt[:, :fade] * in_w)
        bed = np.concatenate([bed[:, :-fade], overlap, nxt[:, fade:]],
                             axis=1)
    del arrays
    total_seconds = bed.shape[1] / SR

    # -- (b1) Stereo Law, part 2: the bed takes its width ------------
    stereo_width = spec["stereo"]["width"]
    stereo_report = {
        "bed_width": stereo_width,
        "spine_panned_by_role": bool(spec.get("spine")),
        "low_cut_hz": P.STEREO_LOW_CUT_HZ,
    }
    if stereo_width > 0.0:
        corr_before = P.channel_correlation(bed)
        bed = P.widen_bed(bed, SR, stereo_width)
        stereo_report.update({
            "bed_correlation_before": round(corr_before, 4),
            "bed_correlation_after": round(P.channel_correlation(bed), 4),
            "bed_low_band_correlation_after": round(
                P.band_correlation(bed, SR, 20.0, P.STEREO_LOW_CUT_HZ), 4),
        })

    # -- (b2) the spine: sampled kit on the grid (produce, mirrored) -
    sp = spec["spine"]
    bar_float = grid.samples_per_bar(sp["bpm"], SR, sp["beats_per_bar"])
    bars_wanted = spine_mod.total_bars(sp)
    bars_fit = int(bed.shape[1] // bar_float)
    bars_used = min(bars_wanted, bars_fit)
    assert bars_used >= 1
    if bars_used < bars_wanted:
        sp = spine_mod.trim_spine_spec(sp, bars_used)
    spine_len = spine_mod.spine_samples(sp, SR)
    bed_trimmed = bed.shape[1] > spine_len
    if bed_trimmed:
        bed = bed[:, :spine_len]
    total_seconds = bed.shape[1] / SR
    spine_kit = spine_mod.load_kit(sp["samples"], SR)
    kit_manifest = None
    kman = Path(sp["samples"]["kick"]).parent / "kit_manifest.json"
    if kman.exists():
        kit_manifest = json.loads(kman.read_text(encoding="utf-8"))
    spine_arr = spine_mod.render_spine(sp, SR, kit=spine_kit)
    assert spine_arr.shape[1] == bed.shape[1]
    spine_rms = rms(spine_arr)
    if spine_rms > 0:
        b_rms = rms(bed)
        bed = bed + spine_arr * (b_rms / spine_rms)
    del spine_arr
    spine_report = {
        "bpm": sp["bpm"], "swing": sp["swing"],
        "root_midi": sp["root_midi"],
        "bars_scheduled": bars_wanted, "bars_used": bars_used,
        "exact_samples": spine_len,
        "bed_trimmed_to_grid": bool(bed_trimmed),
        "sections": sp["sections"],
        "engine": ("resonance.studio.spine as SAMPLER (rendered "
                   "one-shot kit + grid arithmetic; zero synthesis)"),
        "kit": {"samples": sp["samples"], "manifest": kit_manifest},
    }

    # -- (b3) the arpeggio layer (produce, mirrored) -----------------
    layer, arp_rep = arpeggio_mod.render_arpeggio(
        spec["arpeggio"], spec["spine"], SR)
    assert layer.shape[1] == bed.shape[1]
    layer_rms = rms(layer)
    mixed_dbfs = None
    if layer_rms > 0:
        ref_rms = rms(bed)
        gain = (ref_rms * 10 ** (spec["arpeggio"]["level_db"] / 20.0)
                / layer_rms)
        bed = bed + layer * gain
        mixed_dbfs = round(20.0 * math.log10(layer_rms * gain), 2)
    del layer
    arp_rep["mixed_layer_rms_dbfs"] = mixed_dbfs
    arpeggio_report = arp_rep

    # -- the Sigma layer, computed for the VALIDATION mix only -------
    sigma = P.sigma_layer(spec, total_seconds)
    if sigma.shape[1] != bed.shape[1]:
        if sigma.shape[1] > bed.shape[1]:
            sigma = sigma[:, :bed.shape[1]]
        else:
            sigma = np.pad(sigma, ((0, 0),
                                   (0, bed.shape[1] - sigma.shape[1])))
    bed_rms = rms(bed)
    sigma_rms = rms(sigma)
    scale = (bed_rms * 10 ** (spec["sigma"]["gain_db"] / 20.0)) / sigma_rms

    head = int(P.HEAD_FADE_S * SR)
    tail = int(P.END_FADE_S * SR)

    def fades(m):
        m = m.copy()
        m[:, :head] *= np.linspace(0.0, 1.0, head)
        m[:, -tail:] *= np.linspace(1.0, 0.0, tail)
        return m

    # -- VALIDATION: rebuild v4 whole, compare against its master ----
    mix_v4 = fades(bed + sigma * scale)
    mastered_v4, master_rep_v4 = P.master_signal(
        mix_v4, SR, spec["master"]["target_lufs"],
        spec["master"]["ceiling_dbtp"])
    del mix_v4
    v4_master, sr4 = P.read_wav_pcm(V4 / "master.wav")
    assert sr4 == SR and v4_master.shape == mastered_v4.shape
    diff = np.abs(np.asarray(mastered_v4, dtype=np.float32)
                  - np.asarray(v4_master, dtype=np.float32))
    max_diff = float(diff.max())
    lsb = 1.0 / 2 ** 23
    validation = {
        "reconstruction": "v4 rebuilt through the identical code "
                          "path WITH its Sigma layer and mastered; "
                          "compared against the shipped master.wav",
        "max_abs_sample_diff": max_diff,
        "max_abs_sample_diff_lsb24": round(max_diff / lsb, 3),
        "corr_reconstructed": round(P.channel_correlation(mastered_v4), 4),
        "side_reconstructed_dbfs": round(P.side_rms_dbfs(mastered_v4), 2),
        "lufs_reconstructed": master_rep_v4["lufs_after"],
        "true_peak_reconstructed_dbtp": master_rep_v4["true_peak_dbtp"],
        "v4_manifest": {"corr": 0.7089, "side_dbfs": -26.52,
                        "lufs": -15.49, "true_peak_dbtp": -1.02},
    }
    log(f"validation reconstruction: max diff "
        f"{validation['max_abs_sample_diff_lsb24']} LSB, corr "
        f"{validation['corr_reconstructed']}, side "
        f"{validation['side_reconstructed_dbfs']} dBFS, LUFS "
        f"{validation['lufs_reconstructed']}, TP "
        f"{validation['true_peak_reconstructed_dbtp']} dBTP")
    del mastered_v4, v4_master, diff
    if max_diff > 2 * lsb:
        raise SystemExit(
            "VALIDATION FAILED: the rebuilt bed does not reproduce "
            "v4's master; refusing to strike a variant whose one-"
            "change guarantee cannot be proven.")

    # -- THE VARIANT: the same bed, the same fades, NO SIGMA ---------
    mix = fades(bed)
    del bed, sigma
    mastered, master_report = P.master_signal(
        mix, SR, spec["master"]["target_lufs"],
        spec["master"]["ceiling_dbtp"])
    del mix
    stereo_report.update({
        "master_correlation": round(P.channel_correlation(mastered), 4),
        "master_side_rms_dbfs": round(P.side_rms_dbfs(mastered), 2),
    })

    # -- strike the files: the pipeline's own finalize bridge --------
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

    # -- desk re-measurement: the struck file, weighed from disk -----
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

    # -- section reports: provenance carried from v4's manifest ------
    v4_manifest = json.loads((V4 / "manifest.json").read_text(
        encoding="utf-8"))
    seg_reports = []
    for i, s in enumerate(sections):
        r = v4_manifest["sections"][i]
        seg_reports.append({
            "name": s["name"], "prompt": P._full_prompt(spec, s),
            "seed": spec["seed"] + i, "seconds": s["seconds"],
            "native_sample_rate": r["native_sample_rate"],
            "file": r["file"], "wall_seconds": None,
            "resumed_from_disk": True,
            "source_run": "studio-runs/v4-proof-3 (segments copied "
                          "byte-identical; no re-render)",
            "continued_from": r["continued_from"],
            "continue_seconds": r["continue_seconds"],
            "rms_matched_from": round(seg_rms[i], 5),
        })

    # -- the manifest: v4's shape, the difference on its face --------
    spec_for_manifest = json.loads(json.dumps(spec))
    spec_for_manifest["sigma"] = {
        "absent": True,
        "note": "the Sigma binaural layer is OMITTED from this "
                "variant's mix at the founder's order (the A/B "
                "experiment, 2026-11-08). v4's spec carried "
                "200.0/213.0 Hz at -28 dB under the bed; those "
                "values are recorded here so the one change is "
                "fully described, not merely named.",
        "v4_values": {"left_hz": 200.0, "right_hz": 213.0,
                      "gain_db": -28.0},
    }
    manifest = {
        "title": spec["title"],
        "title_status": "working title",
        "variant": {
            "of": "studio-runs/v4-proof-3 — VELVET HAMMER "
                  "(Studio Proof No. 3)",
            "single_difference": "sigma: absent — the Sigma "
                                 "binaural layer (200.0 Hz L / "
                                 "213.0 Hz R at −28 dB under the "
                                 "bed in v4) is not present in this "
                                 "mix. Every other layer, placement, "
                                 "and law is identical: same bed "
                                 "segments (resumed from disk), same "
                                 "RMS match and stitch, same Stereo "
                                 "Law, same sampled-kit spine, same "
                                 "arpeggio render, same fades, same "
                                 "mastering law (−14 LUFS target, "
                                 "−1 dBTP ceiling).",
            "validation": validation,
        },
        "dry_run": False,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pipeline": "resonance.studio v1 (proof-of-concept build) — "
                    "variant struck by produce_no_sigma.py driving "
                    "the pipeline's own stages",
        "spec": spec_for_manifest,
        "sections": seg_reports,
        "render": {"model": "facebook/musicgen-small",
                   "wall_seconds_this_run": 0.0,
                   "resumed_segments": list(range(len(sections))),
                   "rendered_seconds_total": 216.0,
                   "note": "no MusicGen rendering in this run — all "
                           "twelve segments resumed from v4-proof-3 "
                           "on disk under the resume law"},
        "program": {"seconds": round(total_seconds, 3),
                    "sample_rate": SR, "channels": 2, "bit_depth": 24},
        "spine": spine_report,
        "arpeggio": arpeggio_report,
        "stereo": stereo_report,
        "sigma": {
            "status": "ABSENT",
            "intended_left_hz": None,
            "intended_right_hz": None,
            "measured_left_hz": None,
            "measured_right_hz": None,
            "gain_db": None,
            "note": "no Sigma layer was generated or mixed; there "
                    "is no sigma.wav in this run directory, by "
                    "design. The founder's A/B question — what the "
                    "track is without the ground — is answered by "
                    "this file and no other change.",
        },
        "master": master_report,
        "desk_remeasure": remeasure,
        "files": {
            "master_wav": {"path": str(master_wav),
                           "bytes": master_wav.stat().st_size},
            "preview_mp3": {"path": str(preview),
                            "bytes": preview.stat().st_size},
            "sigma_wav": None,
            "spec_json": str(OUT / "spec.json"),
        },
        "wall_seconds_total": round(time.time() - t_start, 2),
        "notes": [
            "VARIANT of v4-proof-3: the single difference is the "
            "ABSENT Sigma layer; the validation block proves the "
            "bed under this mix is the bed under v4's, sample for "
            "sample.",
            "loudness is K-weighted integrated, UNGATED (BS.1770 "
            "gating omitted in the proof build, stated not hidden).",
            "section levels RMS-matched to the median section, "
            "clamped to +/-6 dB, before crossfading.",
            "2 s tail fade + 5 ms head fade applied before mastering.",
            "stereo law: the spine is panned by role, the bed is "
            "widened by quadrature side synthesis above 180 Hz with "
            "the mid preserved exactly and the lows left fully "
            "mono. In v4 the Sigma layer stood outside that law, "
            "never processed; in this variant there is no Sigma "
            "layer to exempt.",
            "spine: SAMPLED KIT — rendered one-shots placed by "
            "resonance.studio.spine, ZERO synthesis; provenance in "
            "the spine block's kit manifest (the kit itself lives "
            "in v4-proof-3 and is referenced, not copied).",
            "arpeggio: the house's composed violin layer, as v4; "
            "its notation stands in composition.abc.",
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
