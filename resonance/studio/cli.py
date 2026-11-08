# 93
# ---------------------------------------------------------------------
# cli.py -- the studio's mouth: one door for humans, one for agents.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: argparse with two subcommands. `produce` builds a spec
# from --spec FILE, or from the flag form (--prompt/--seconds/--seed/
# --title/--out-dir; --seconds is split into <=30 s sections because
# the mill renders in sections), and runs pipeline.produce. With
# --json, stdout carries EXACTLY one JSON object -- the manifest, or
# {"error": ...} on failure -- and every progress line goes to
# stderr; that is the contract AGENT.md promises machine readers.
# `check` weighs an existing WAV: duration, rate, channels, peak,
# RMS, and -- when a channel is dominated by one pure tone -- the
# measured carrier frequency of each ear.
# Exit codes are honest: 0 success, 1 failure (with the error named),
# 2 usage. Nothing here prints a success it did not earn.
# ---------------------------------------------------------------------

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

from resonance.studio import pipeline


def _spec_from_flags(args):
    """Flag form -> spec dict. Long briefs split into <=30 s sections.

    MECHANISM: the pipeline renders in sections; a single --seconds
    request is one arrangement spoken plainly, so it is cut into
    30 s movements (last one shorter) with empty suffixes -- the
    prompt carries the whole intent in every movement.
    """
    seconds = float(args.seconds)
    sections = []
    remaining = seconds
    idx = 1
    while remaining > 0:
        take = min(30.0, remaining)
        sections.append({"name": f"movement{idx}", "prompt_suffix": "",
                         "seconds": take})
        remaining -= take
        idx += 1
    return {
        "title": args.title,
        "prompt_base": args.prompt,
        "sections": sections,
        "seed": args.seed,
        "out_dir": args.out_dir,
    }


def _cmd_produce(args):
    if args.spec:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    else:
        spec = _spec_from_flags(args)
    manifest = pipeline.produce(spec, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(manifest, indent=2))
    else:
        prog = manifest.get("program", {})
        planned = manifest.get("planned", {})
        print(f"title:    {manifest['title']} (working title)")
        if manifest.get("dry_run"):
            print(f"dry run:  {planned['rendered_seconds_total']}s of "
                  f"sections planned, nothing rendered")
        else:
            print(f"program:  {prog['seconds']}s @ {prog['sample_rate']} Hz, "
                  f"{prog['bit_depth']}-bit")
            print(f"sigma:    measured "
                  f"{manifest['sigma']['measured_left_hz']} / "
                  f"{manifest['sigma']['measured_right_hz']} Hz "
                  f"(separation "
                  f"{manifest['sigma']['measured_separation_hz']} Hz)")
            print(f"master:   {manifest['master']['lufs_after']} LUFS, "
                  f"true peak {manifest['master']['true_peak_dbtp']} dBTP")
            print(f"master.wav: {manifest['files']['master_wav']['path']}")
            print(f"preview:    {manifest['files']['preview_mp3']['path']}")
    return 0


def _dominant_carrier(samples_1d, sr):
    """The channel's dominant pure tone, or None if none dominates.

    MECHANISM: FFT the middle of the file; a carrier is declared
    when the peak bin (50-1000 Hz) stands at least 12 dB above the
    band's median magnitude -- a tone that merely exists is not a
    carrier, and `check` refuses to call it one.
    """
    x = np.asarray(samples_1d, dtype=np.float64)
    take = min(x.shape[0], sr * 20)
    start = max(0, (x.shape[0] - take) // 2)
    seg = x[start:start + take] * np.hanning(take)
    spectrum = np.abs(np.fft.rfft(seg))
    freqs = np.fft.rfftfreq(take, d=1.0 / sr)
    band = (freqs >= 50.0) & (freqs <= 1000.0)
    if not np.any(band):
        return None
    mags = spectrum[band]
    peak_i = int(np.argmax(mags))
    median = float(np.median(mags)) or 1e-12
    if 20.0 * math.log10((mags[peak_i] or 1e-12) / median) < 12.0:
        return None
    return round(float(freqs[band][peak_i]), 2)


def _cmd_check(args):
    data, sr = pipeline.read_wav_pcm(args.wav)
    if data.ndim == 1:
        channels = [data]
    else:
        channels = [data[0], data[1]]
    frames = channels[0].shape[0]
    peak = max(float(np.max(np.abs(ch))) if ch.size else 0.0
               for ch in channels)
    rms = math.sqrt(float(np.mean(np.concatenate(channels) ** 2)))
    info = {
        "path": str(args.wav),
        "duration_seconds": round(frames / sr, 3),
        "sample_rate": sr,
        "channels": len(channels),
        "peak_dbfs": round(20.0 * math.log10(peak), 2) if peak else -120.0,
        "rms_dbfs": round(20.0 * math.log10(rms), 2) if rms else -120.0,
    }
    carriers = []
    for ch in channels:
        carriers.append(_dominant_carrier(ch, sr))
    if any(c is not None for c in carriers):
        info["carriers_hz"] = carriers
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        for key, val in info.items():
            print(f"{key}: {val}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="resonance.studio",
        description="RESONANTIA studio pipeline: compose, voice, "
                    "ground, master. See resonance/studio/AGENT.md.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("produce", help="produce a mastered track")
    p.add_argument("--spec", help="path to a spec JSON file")
    p.add_argument("--prompt", help="prompt_base (flag form)")
    p.add_argument("--seconds", type=float, default=30.0,
                   help="total seconds (flag form; split into sections)")
    p.add_argument("--seed", type=int, default=93)
    p.add_argument("--title", default="Untitled")
    p.add_argument("--out-dir", default="studio-runs/run")
    p.add_argument("--dry-run", action="store_true",
                   help="validate + plan only; renders nothing")
    p.add_argument("--json", action="store_true",
                   help="stdout = exactly one JSON object (the manifest)")

    c = sub.add_parser("check", help="weigh an existing WAV")
    c.add_argument("wav")
    c.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "produce":
            if not args.spec and not args.prompt:
                parser.error("produce needs --spec FILE or --prompt TEXT")
            return _cmd_produce(args)
        return _cmd_check(args)
    except Exception as exc:
        if getattr(args, "json", False):
            print(json.dumps({"error": f"{type(exc).__name__}: {exc}"}))
        else:
            print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

# 93 -- Live, Love, and let Love, Live.
