#!/usr/bin/env python3
"""Binaural finalize: measure the raw sofalizer render, apply one
constant gain so it lands on the house loudness (-14.0 LUFS) without
breaching the -1.0 dBTP ceiling, TPDF-dither to 24-bit, strike the
final file, export the 320K MP3, and read everything back."""
import json, pathlib, subprocess, sys
import numpy as np
import soundfile as sf
sys.path.insert(0, str(pathlib.Path.home() / "workspace/resonance"))
from resonance.studio import four_powers as fp
from resonance.studio import pipeline

RUN3 = pathlib.Path(__file__).resolve().parent
from scipy import signal as sig
x, sr = sf.read(RUN3 / "binaural_raw.wav", always_2d=True)
x = x.T.astype(np.float64)
RAW_SR = sr  # the KEMAR SOFA set's native rate; sofalizer struck at it
if sr != 48000:
    x = np.vstack([sig.resample_poly(c, 160, 147) for c in x])
    sr = 48000
lufs0 = pipeline.measure_loudness_lufs(x, sr)
tp0 = pipeline.true_peak_dbtp(x, sr)
gain = -14.0 - lufs0
# ceiling guard: never let the gain push true peak past -1.05 dBTP
gain = min(gain, -1.05 - tp0)
y = x * 10 ** (gain / 20)
d = fp.tpdf_dither(y, seed=32017)
out = RUN3 / "honey-and-hammer-explicit-remix-binaural.wav"
sf.write(out, d.T, sr, subtype="PCM_24")
back, bsr = sf.read(out, always_2d=True)
back = back.T.astype(np.float64)
res = {"raw_lufs": round(lufs0, 2), "raw_dbtp": round(tp0, 2),
       "gain_applied_db": round(float(gain), 2), "sofa_native_sr": RAW_SR,
       "file": out.name, "sr": bsr,
       "duration_s": round(back.shape[1] / bsr, 3),
       "lufs_integrated": round(pipeline.measure_loudness_lufs(back, bsr), 2),
       "true_peak_dbtp": round(pipeline.true_peak_dbtp(back, bsr), 2)}
mp3 = RUN3 / "honey-and-hammer-explicit-remix-binaural-320k.mp3"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out),
                "-codec:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
                str(mp3)], check=True)
probe = json.loads(subprocess.run(
    ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of",
     "json", str(mp3)], capture_output=True, text=True, check=True).stdout)
astream = next(s for s in probe["streams"] if s["codec_type"] == "audio")
mb, msr = sf.read(mp3, always_2d=True)
mb = mb.T.astype(np.float64)
res["mp3"] = {"file": mp3.name,
              "bit_rate_bps": int(astream.get("bit_rate", probe["format"]["bit_rate"])),
              "sample_rate": int(astream["sample_rate"]),
              "size_bytes": int(probe["format"]["size"]),
              "lufs_integrated": round(pipeline.measure_loudness_lufs(mb, msr), 2),
              "true_peak_dbtp": round(pipeline.true_peak_dbtp(mb, msr), 2)}
data = json.loads((RUN3 / "run_data.json").read_text())
data["binaural"] = res
(RUN3 / "run_data.json").write_text(json.dumps(data, indent=2))
print(json.dumps(res, indent=2))
print("BINAURAL DONE")
