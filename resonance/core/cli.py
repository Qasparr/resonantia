# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# SPDX-License-Identifier: AGPL-3.0-only
"""
resonance/core/cli.py -- the `resonance-edit` executable.

Hypothesis: the editing primitives deserve a zero-argument executable:
  with no input file, synthesize a short demo tone and run it through
  the default chain (fade-in, fade-out, normalize) so the tool always
  demonstrates its own machinery on a real buffer. Beside it, a `cut`
  subcommand serves the ringtone workflow: slice [start, start+length)
  out of any ffmpeg-readable file with tight click-free fades.
Method:     flat flags (no subcommand) keep the legacy chain: trim,
  gain, fade-in, fade-out, soft limiter, normalize, each logged to
  stdout; output written with core.io.write_wav. `cut` reads WAV
  natively and anything else through resonance.convert.decode_to_pcm
  (loud when ffmpeg is absent), then trim -> tight fades -> normalize
  -> write. Both paths exit 0/2/1 (ok / bad args / failure).
Observation: `resonance-edit --help` exits 0 and names the tool;
  `resonance-edit -o out.wav` writes a processed WAV;
  `resonance-edit cut -i song.mp3 --start 30 -o ring.wav` slices a
  30 s ringtone.
Result:     the [project.scripts] `resonance-edit` entry point.

Exit codes: 0 on success, 2 on bad arguments, 1 on read/process/write
failure. Only 16-bit PCM WAV input is supported by the flat chain
(the core.io contract) -- anything else is a loud error, never a
silent guess.
"""
import argparse
import sys
from pathlib import Path


def _demo_tone(sr):
    """The zero-argument input: 3 s of 440 Hz, honest and boring.

    A generated tone -- not claimed to be anyone's recording -- so the
    tool's chain is exercisable without a file on disk.
    """
    import numpy as np

    t = np.arange(3 * sr, dtype=np.float64) / float(sr)
    return (0.5 * np.sin(2.0 * np.pi * 440.0 * t)).astype(np.float32)


def build_parser():
    """The argparse contract: works with zero arguments; `cut` slices."""
    p = argparse.ArgumentParser(
        prog="resonance-edit",
        description="Apply waveform edits (trim/gain/fades/limiter/"
                    "normalize) to a WAV file, or `cut` a ringtone slice "
                    "out of any audio file.",
    )
    # Legacy flat chain -- unchanged, still zero-argument friendly.
    p.add_argument("-i", "--input", default=None,
                   help="input WAV path (default: a 3 s 440 Hz demo tone)")
    p.add_argument("--trim-start", type=float, default=0.0,
                   help="trim start in seconds (default: 0.0)")
    p.add_argument("--trim-end", type=float, default=None,
                   help="trim end in seconds (default: end of buffer)")
    p.add_argument("--gain-db", type=float, default=0.0,
                   help="gain in dB (default: 0.0)")
    p.add_argument("--fade-in", type=float, default=0.5,
                   help="fade-in length in seconds (default: 0.5)")
    p.add_argument("--fade-out", type=float, default=0.5,
                   help="fade-out length in seconds (default: 0.5)")
    p.add_argument("--limiter", action="store_true",
                   help="apply the soft limiter (default: off)")
    p.add_argument("--normalize", type=float, default=0.95,
                   help="peak-normalize target; 0 disables (default: 0.95)")
    p.add_argument("-o", "--output", default="edited.wav",
                   help="output WAV path (default: edited.wav)")

    sub = p.add_subparsers(dest="command")
    cut = sub.add_parser(
        "cut",
        help="slice a ringtone-length section out of an audio file",
        description=(
            "The cutter: take [start, start+length) out of any "
            "ffmpeg-readable audio file, with tight click-free fades "
            "and peak normalization -- the ringtone workflow. WAV is "
            "read natively; anything else (MP3/OGG/M4A/...) decodes "
            "through ffmpeg, loudly when ffmpeg is absent."),
    )
    cut.add_argument("-i", "--input", required=True,
                     help="input audio path (WAV native; others via ffmpeg)")
    cut.add_argument("--start", type=float, default=0.0,
                     help="slice start in seconds (default: 0.0)")
    span = cut.add_mutually_exclusive_group()
    span.add_argument("--duration", type=float, default=30.0,
                      help="slice length in seconds (default: 30.0, the "
                           "classic ringtone length)")
    span.add_argument("--end", type=float, default=None,
                      help="slice end in seconds (alternative to --duration)")
    cut.add_argument("--fade-in", type=float, default=0.1,
                     help="fade-in seconds; short and tight so the slice "
                          "starts clean (default: 0.1)")
    cut.add_argument("--fade-out", type=float, default=0.1,
                     help="fade-out seconds (default: 0.1)")
    cut.add_argument("--normalize", type=float, default=0.95,
                     help="peak-normalize target; 0 disables (default: 0.95)")
    cut.add_argument("--mono", action="store_true",
                     help="mix stereo down to mono (ringtones are mono)")
    cut.add_argument("-o", "--output", default=None,
                     help="output WAV path (default: <input-stem>_cut.wav)")
    return p


def cmd_process(args):
    """The legacy flat chain: trim -> gain -> fades -> limiter -> normalize.

    Kept byte-for-byte from the original main() -- the zero-argument
    contract (demo tone when no -i) is unchanged.
    """
    from resonance.core import edit
    from resonance.core.io import read_wav, write_wav

    if args.input is None:
        sr = 44100
        audio = _demo_tone(sr)
        print("resonance-edit: no input -- using the 3 s 440 Hz demo tone")
    else:
        audio, sr = read_wav(args.input)
        print(f"resonance-edit: read {args.input} ({audio.shape}, "
              f"{sr} Hz)")

    # Fixed chain order; every applied step is logged, so the tool
    # teaches while it works.
    n = audio.shape[-1]
    start = max(0, int(round(args.trim_start * sr)))
    end = n if args.trim_end is None else min(n, int(round(args.trim_end * sr)))
    if (start, end) != (0, n):
        audio = edit.trim(audio, start, end)
        print(f"resonance-edit: trim -> {start}:{end} samples")
    if args.gain_db:
        audio = edit.gain(audio, args.gain_db, unit="db")
        print(f"resonance-edit: gain {args.gain_db:+.1f} dB")
    if args.fade_in > 0:
        audio = edit.fade_in(audio, int(round(args.fade_in * sr)))
        print(f"resonance-edit: fade-in {args.fade_in} s")
    if args.fade_out > 0:
        audio = edit.fade_out(audio, int(round(args.fade_out * sr)))
        print(f"resonance-edit: fade-out {args.fade_out} s")
    if args.limiter:
        audio = edit.soft_limiter(audio)
        print("resonance-edit: soft limiter")
    if args.normalize > 0:
        audio = edit.normalize(audio, target=args.normalize)
        print(f"resonance-edit: normalized to {args.normalize}")

    write_wav(args.output, audio, sr)
    print(f"resonance-edit: wrote {args.output} "
          f"({audio.shape[-1]} frames @ {sr} Hz)")
    return 0


def cmd_cut(args):
    """The cutter: slice [start, start+length) for ringtones and clips.

    Hypothesis: a ringtone is a slice with manners -- it starts and
      ends clean (tight fades, no clicks), sits at a sane level
      (normalized), and is mono more often than not.
    Method:     WAV reads natively; anything else decodes through
      resonance.convert.decode_to_pcm (ffmpeg -- loud when absent).
      The selection is clamped to the file; an empty selection is a
      loud ValueError, never a silent 0-byte file. Then: trim ->
      fade-in -> fade-out -> optional mono mixdown -> normalize ->
      write 16-bit WAV.
    Observation: every step logs to stdout; the output name defaults
      to <input-stem>_cut.wav beside the input.
    Result:    0 on success; exceptions propagate to main()'s handler.
    """
    import numpy as np

    from resonance.core import edit
    from resonance.core.io import read_wav, write_wav

    src = Path(args.input)
    if src.suffix.lower() == ".wav":
        audio, sr = read_wav(args.input)
        print(f"resonance-edit cut: read {args.input} ({audio.shape}, "
              f"{sr} Hz)")
    else:
        # DOCTRINE: non-WAV input decodes through the real converter.
        # No ffmpeg on PATH means a loud, actionable error -- never a
        # guessed decode.
        from resonance.convert.convert import decode_to_pcm
        audio, sr = decode_to_pcm(args.input)
        print(f"resonance-edit cut: decoded {args.input} via ffmpeg "
              f"({audio.shape}, {sr} Hz)")

    # MECHANISM: work in seconds for the human, samples for the engine;
    # clamp to the file so over-long requests degrade to "to the end".
    n = audio.shape[-1]
    total_s = n / sr
    start_s = max(0.0, float(args.start))
    if args.end is not None:
        end_s = min(total_s, float(args.end))
    else:
        end_s = min(total_s, start_s + float(args.duration))
    if end_s <= start_s:
        raise ValueError(
            f"resonance-edit cut: empty selection "
            f"(start={start_s:.2f}s, end={end_s:.2f}s, file is "
            f"{total_s:.2f}s) -- refusing to write a silent file.")
    start, end = int(round(start_s * sr)), int(round(end_s * sr))
    audio = edit.trim(audio, start, end)
    print(f"resonance-edit cut: slice [{start_s:.2f}s -> {end_s:.2f}s] "
          f"({end - start} samples)")

    if args.fade_in > 0:
        audio = edit.fade_in(audio, int(round(args.fade_in * sr)))
        print(f"resonance-edit cut: fade-in {args.fade_in} s")
    if args.fade_out > 0:
        audio = edit.fade_out(audio, int(round(args.fade_out * sr)))
        print(f"resonance-edit cut: fade-out {args.fade_out} s")
    if args.mono and audio.ndim == 2:
        # Equal mixdown; the peak step below re-levels it.
        audio = audio.mean(axis=0).astype(np.float32)
        print("resonance-edit cut: mixed to mono")
    if args.normalize > 0:
        audio = edit.normalize(audio, target=args.normalize)
        print(f"resonance-edit cut: normalized to {args.normalize}")

    out = args.output or str(src.with_name(f"{src.stem}_cut.wav"))
    write_wav(out, audio, sr)
    print(f"resonance-edit cut: wrote {out} "
          f"({audio.shape[-1]} frames @ {sr} Hz, "
          f"{audio.shape[-1] / sr:.1f} s)")
    return 0


def main(argv=None):
    """Entry point. Returns the process exit code."""
    args = build_parser().parse_args(argv)

    try:
        if args.command == "cut":
            return cmd_cut(args)
        return cmd_process(args)
    except Exception as exc:
        print(f"resonance-edit: error: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
