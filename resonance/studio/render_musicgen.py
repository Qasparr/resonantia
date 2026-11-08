# 93
# ---------------------------------------------------------------------
# render_musicgen.py -- the venv-side hands of the studio pipeline.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: this script is the ONLY part of the studio that imports
# torch/transformers/soundfile, and it is never imported by the system
# interpreter -- pipeline.py executes it BY PATH with the MusicGen
# venv's python (/home/hatch/workspace/musicgen-venv/bin/python),
# because the system python carries no torch. The two interpreters
# exchange JSON only: a job file in, one JSON result line on stdout,
# all progress chatter on stderr. Two job kinds:
#   {"segments": [{index, prompt, seconds, seed, file}], "out_dir": …}
#       Load facebook/musicgen-small ONCE, render each segment in
#       order (seeded per segment), write segNN.wav at the model's
#       native 32 kHz, PCM_16. Encodec runs at 50 tokens per second,
#       so seconds*50 max_new_tokens; guidance_scale 3.0 -- the exact
#       recipe proven by ~/workspace/musicgen/render_first.py.
#   {"finalize": [{"npy": path, "out": path, "subtype": "PCM_24"}]}
#       Load each float32 (frames, channels) .npy and write it as a
#       real WAV via soundfile -- the system interpreter has no
#       soundfile, and 24-bit PCM deserves a proper writer.
# DOCTRINE: the bridge is a wall with two small doors, both JSON.
# Nothing reaches across it except numbers and filenames, so either
# side can be rebuilt without the other's consent.
# ---------------------------------------------------------------------

import json
import os
import sys
import time

import numpy as np
import soundfile as sf
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

MODEL_ID = "facebook/musicgen-small"
TOKENS_PER_SECOND = 50  # Encodec frame rate -- the codec's own clock.
GUIDANCE_SCALE = 3.0     # The proven render_first.py recipe, unchanged.

# Threading (desk tuning, 2026-11-07): the first proof segment
# rendered at ~1.0 s/token on ~1.3 effective cores -- autoregressive
# decode leaves cores idle unless torch is told to use them. The
# count is env-driven (STUDIO_TORCH_THREADS) so the mill can be tuned
# to its machine without a code change; default is every core.
_THREADS = int(os.environ.get("STUDIO_TORCH_THREADS", "0")) \
    or (os.cpu_count() or 1)
torch.set_num_threads(_THREADS)
try:
    torch.set_num_interop_threads(max(1, _THREADS // 2))
except RuntimeError:
    pass  # already set for this process; the intraop count is the lever


def _log(msg):
    """Progress goes to stderr; stdout is reserved for the result."""
    print(f"[render_musicgen] {msg}", file=sys.stderr, flush=True)


def _render_segments(job):
    """Render every segment in the job with one model load.

    MECHANISM: the model is loaded once and kept resident across the
    whole job -- on CPU the load is a meaningful fraction of a short
    job's life, and per-segment seeds (torch.manual_seed before each
    generate) keep every segment independently reproducible anyway.
    """
    out_dir = job["out_dir"]
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    model = MusicgenForConditionalGeneration.from_pretrained(MODEL_ID)
    model.eval()
    _log(f"model loaded in {time.time() - t0:.0f}s")
    sample_rate = int(model.config.audio_encoder.sampling_rate)
    results = []
    for seg in job["segments"]:
        seed = int(seg["seed"])
        torch.manual_seed(seed)
        tokens = int(round(float(seg["seconds"]) * TOKENS_PER_SECOND))
        inputs = processor(text=[seg["prompt"]], padding=True,
                           return_tensors="pt")
        t1 = time.time()
        with torch.no_grad():
            audio = model.generate(**inputs, max_new_tokens=tokens,
                                   guidance_scale=GUIDANCE_SCALE)
        # audio: (batch, channels, samples); musicgen-small is mono.
        wav = audio[0].cpu().numpy()
        if wav.ndim == 2:      # (channels, samples) -> keep channel axis
            data = wav.T       # soundfile wants (frames, channels)
        else:
            data = wav
        path = os.path.join(out_dir, seg["file"])
        sf.write(path, data, sample_rate, subtype="PCM_16")
        wall = time.time() - t1
        _log(f"segment {seg['index']}: {seg['seconds']}s rendered "
             f"in {wall:.0f}s -> {path}")
        results.append({
            "index": int(seg["index"]),
            "file": seg["file"],
            "path": path,
            "seed": seed,
            "prompt": seg["prompt"],
            "seconds": float(seg["seconds"]),
            "sample_rate": sample_rate,
            "frames": int(data.shape[0]),
            "channels": int(data.shape[1]) if data.ndim == 2 else 1,
            "wall_seconds": round(wall, 2),
        })
    return {"ok": True, "kind": "segments", "model": MODEL_ID,
            "segments": results,
            "wall_seconds": round(time.time() - t0, 2)}


def _finalize(job):
    """Write mastered float arrays as real WAV files via soundfile.

    MECHANISM: pipeline.py masters in float and saves (frames,
    channels) float32 .npy; this side is the only place a 24-bit PCM
    WAV is struck, because soundfile lives here and not system-side.
    """
    written = []
    for item in job["finalize"]:
        arr = np.load(item["npy"])
        sf.write(item["out"], arr, int(item.get("sample_rate", 48000)),
                 subtype=item.get("subtype", "PCM_24"))
        written.append({"out": item["out"],
                        "bytes": os.path.getsize(item["out"])})
        _log(f"finalized {item['out']} ({written[-1]['bytes']} bytes)")
    return {"ok": True, "kind": "finalize", "written": written}


def main(argv):
    if len(argv) != 2:
        print(json.dumps({"ok": False,
                          "error": "usage: render_musicgen.py JOB.json"}))
        return 2
    with open(argv[1], "r", encoding="utf-8") as fh:
        job = json.load(fh)
    try:
        if "segments" in job:
            result = _render_segments(job)
        elif "finalize" in job:
            result = _finalize(job)
        else:
            result = {"ok": False,
                      "error": "job has neither 'segments' nor 'finalize'"}
            print(json.dumps(result))
            return 2
    except Exception as exc:  # surface, never swallow: the desk must see it
        print(json.dumps({"ok": False,
                          "error": f"{type(exc).__name__}: {exc}"}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# 93 -- Live, Love, and let Love, Live.
