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
#   {"segments": [{index, prompt, seconds, seed, file,
#                   continue_seconds?}], "out_dir": …}
#       Load the MusicGen model ONCE (MODEL_ID below; small by
#       default), render each segment in
#       order (seeded per segment), write segNN.wav at the model's
#       native 32 kHz, PCM_16. Encodec runs at 50 tokens per second,
#       so seconds*50 max_new_tokens; guidance_scale 3.0 -- the exact
#       recipe proven by ~/workspace/musicgen/render_first.py.
#       A segment with continue_seconds > 0 is CHAINED: it is
#       generated conditioned on the tail of its predecessor's audio
#       (the previous segment this job rendered, or segNN-1.wav read
#       back from out_dir -- the resume road), and the returned
#       audio's prompt span is sliced off, so the file holds only
#       the newly generated seconds. The mechanism was proven by the
#       desk's feasibility probe (2026-11-08): transformers 5.19's
#       processor accepts audio conditioning, the output is prompt +
#       continuation, and a direct splice at the joint measured a
#       SMALLER sample jump than 99% of the source's own internal
#       transitions.
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

# Model selection (desk, 2026-11-10, for the v9 strike): the model is
# env-driven so a run can change THE MODEL ONLY -- the founder's
# chained fallback after v8's ear verdict -- without touching the
# render recipe. Unset, the bridge is exactly what it was: small.
# _run_bridge passes os.environ through, so the choice travels with
# the produce invocation and the bridge's own result line reports
# the model that actually loaded into the manifest.
MODEL_ID = os.environ.get("STUDIO_MUSICGEN_MODEL",
                          "facebook/musicgen-small")
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


def _match_model_dtype(inputs, model):
    """Cast floating tensors in a processor batch to the model's
    dtype (desk fix, 2026-11-10, from the v9 strike's first death).

    MECHANISM: the processor hands the conditioning audio back as
    float32 whatever the model's residency; a bf16-resident model
    then feeds fp32 audio into bf16-biased linears on the
    continuation path and generate() dies on the type mismatch --
    plain takes never touch that path, which is why a strike can
    render its seed take and still die on its first continuation.
    Token ids and masks are not floating point and pass untouched.
    For the fp32 default this cast is a no-op.
    """
    dtype = next(model.parameters()).dtype
    for key, value in inputs.items():
        if torch.is_tensor(value) and value.is_floating_point():
            inputs[key] = value.to(dtype)
    return inputs


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
    prev_audio = None        # (frames,) mono float -- last struck audio
    prev_index = None
    for seg in job["segments"]:
        index = int(seg["index"])
        seed = int(seg["seed"])
        torch.manual_seed(seed)
        tokens = int(round(float(seg["seconds"]) * TOKENS_PER_SECOND))
        cont_s = float(seg.get("continue_seconds", 0.0) or 0.0)
        continued_from = None
        tail = None
        if cont_s > 0:
            # The conditioning source: this job's previous render if
            # it is the immediate predecessor, else the predecessor's
            # file on disk (the resume road). No source, no chain --
            # the segment renders plain and the result SAYS so.
            src = None
            if prev_audio is not None and prev_index == index - 1:
                src = prev_audio
            else:
                prior = os.path.join(out_dir, f"seg{index - 1:02d}.wav")
                if index > 0 and os.path.exists(prior):
                    arr, _sr = sf.read(prior, dtype="float32")
                    src = arr[:, 0] if arr.ndim == 2 else arr
            if src is not None and len(src) > sample_rate:
                n_tail = int(round(cont_s * sample_rate))
                # Whole codec frames only: 640 samples per token at
                # 32 kHz -- the slice arithmetic must be exact.
                frame = sample_rate // TOKENS_PER_SECOND
                n_tail = (n_tail // frame) * frame
                tail = np.ascontiguousarray(src[-n_tail:])
                continued_from = index - 1
        t1 = time.time()
        if tail is not None:
            inputs = processor(text=[seg["prompt"]], audio=tail,
                               sampling_rate=sample_rate,
                               return_tensors="pt", padding=True)
            _match_model_dtype(inputs, model)
            with torch.no_grad():
                audio = model.generate(**inputs, max_new_tokens=tokens,
                                       guidance_scale=GUIDANCE_SCALE)
        else:
            inputs = processor(text=[seg["prompt"]], padding=True,
                               return_tensors="pt")
            _match_model_dtype(inputs, model)
            with torch.no_grad():
                audio = model.generate(**inputs, max_new_tokens=tokens,
                                       guidance_scale=GUIDANCE_SCALE)
        # audio: (batch, channels, samples); musicgen-small is mono.
        # .float() first: a bf16-resident model (the medium strike's
        # road on this box) returns bf16 audio, which numpy refuses
        # outright; for the fp32 default the cast is a no-op.
        wav = audio[0].float().cpu().numpy()
        if wav.ndim == 2:      # (channels, samples) -> keep channel axis
            data = wav.T       # soundfile wants (frames, channels)
        else:
            data = wav
        if tail is not None:
            # The decoded stream opens with the prompt's own span
            # (the tail, re-decoded); only the continuation is the
            # segment. Slice exactly the tail's sample count.
            data = data[len(tail):]
        path = os.path.join(out_dir, seg["file"])
        sf.write(path, data, sample_rate, subtype="PCM_16")
        wall = time.time() - t1
        _log(f"segment {index}: {seg['seconds']}s rendered "
             f"in {wall:.0f}s -> {path}"
             + (f" (continued from {continued_from})"
                if continued_from is not None else ""))
        results.append({
            "index": index,
            "file": seg["file"],
            "path": path,
            "seed": seed,
            "prompt": seg["prompt"],
            "seconds": float(seg["seconds"]),
            "sample_rate": sample_rate,
            "frames": int(data.shape[0]),
            "channels": int(data.shape[1]) if data.ndim == 2 else 1,
            "wall_seconds": round(wall, 2),
            "continued_from": continued_from,
            "continue_seconds": cont_s if continued_from is not None
            else 0.0,
        })
        prev_audio = (data[:, 0] if data.ndim == 2 else data)
        prev_audio = np.ascontiguousarray(prev_audio, dtype=np.float32)
        prev_index = index
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
