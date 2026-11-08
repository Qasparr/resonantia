#!/usr/bin/env python3
# =====================================================================
# 93
#
# Epigraph: "The method of science, the aim of religion." — every
# pass is MEASURED before the next is allowed; nothing is assumed.
#
# separate_pass.py — one Demucs separation pass for the ANVIL AND
# CROWN instrumental production. Loads the htdemucs bag ONCE and runs
# N sequential file->stems jobs in this single process (model reload
# per pass would waste the shared CPU budget).
#
# Date: VIII day of November, Dies Solis, Sol in Scorpio,
#       Anno V:xii e.n. (2026 e.v.)
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice).
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# MECHANISM:
#   args: jobs as  in.wav=outprefix  pairs.
#   For each job: separate -> save <outprefix>_vocals.wav and
#   <outprefix>_accomp.wav (the no_vocals stem), float32 WAV via
#   soundfile (NOT demucs.api.save_audio — that path is int16 and
#   rescale-clips; float keeps every later pass lossless).
#   Prints one JSON line per job with wall time, for the report.
# DOCTRINE: read-only toward the musicgen venv (torch borrowed via
# PYTHONPATH); writes only under this production's work/ directory.
# =====================================================================
import sys, json, time
from pathlib import Path

import torch
import soundfile as sf
from demucs.api import Separator

torch.set_num_threads(4)


def main() -> None:
    jobs = []
    for a in sys.argv[1:]:
        src, prefix = a.split("=", 1)
        jobs.append((Path(src), Path(prefix)))
    t0 = time.time()
    sep = Separator(model="htdemucs", device="cpu", shifts=1,
                    overlap=0.25, split=True, segment=None, progress=False)
    print(json.dumps({"event": "model_ready", "wall_s": round(time.time() - t0, 1),
                      "sources": list(sep._model.sources)}), flush=True)
    for src, prefix in jobs:
        t = time.time()
        origin, stems = sep.separate_audio_file(str(src))
        sr = sep.samplerate
        # demucs 4.1 Separator returns only the model's named sources;
        # the accompaniment (its two_stem target) is origin - vocals,
        # computed in float so no pass ever sees a quantised bounce.
        accomp = origin - stems["vocals"]
        for tag, tens in (("vocals", stems["vocals"]), ("accomp", accomp)):
            out = tens.detach().cpu().numpy().T  # (samples, ch)
            sf.write(str(prefix) + f"_{tag}.wav", out, sr, subtype="FLOAT")
        print(json.dumps({"event": "job_done", "src": str(src),
                          "prefix": str(prefix), "sr": sr,
                          "wall_s": round(time.time() - t, 1)}), flush=True)
    print(json.dumps({"event": "all_done", "total_wall_s": round(time.time() - t0, 1)}), flush=True)


if __name__ == "__main__":
    main()

# 93 — Live, Love, and let Love, Live.
