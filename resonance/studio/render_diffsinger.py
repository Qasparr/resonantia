# 93
# ---------------------------------------------------------------------
# render_diffsinger.py -- the lab-side hands of the DiffSinger plug.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: this script is the ONLY part of the DiffSinger plug that
# imports onnxruntime/torch/soundfile, and it is never imported by the
# system interpreter -- resonance/studio/diffsinger.py executes it BY
# PATH with the diffsinger-lab venv's python, because the system
# python carries no onnxruntime and no torch. The two interpreters
# exchange JSON only: a job file in, one JSON result line on stdout,
# all progress chatter on stderr. The job carries BUILT sequences
# (phoneme token ids, language ids, per-phoneme score pitches,
# per-word phoneme divisions and frame budgets) -- the sequence law
# lives system-side in diffsinger.py; this side only sings what it
# is handed, through the five proven stages, stage-batched across
# lines exactly as the first self-sufficient run drove them
# (studio-runs/spear-and-magickal-helm-run1/render_vocal.py):
#   stage 1+2  duration model  (dsdur linguistic + duration ONNX)
#              -> per-phoneme frame counts
#   stage 3    variance model  (dsvariance linguistic + pitch
#              variance ONNX, 20 steps) -> voicing + tension curves
#   stage 4    acoustic model  (acoustic ONNX, 30 steps, depth 0.6)
#              -> mel spectrogram
#   stage 5    PC-NSF-HiFiGAN vocoder (torch, the lab's DiffSinger
#              checkpoint) -> waveform at 44.1 kHz
# Per-line WAVs are written PCM_16 into out_dir/lines/, then the
# lines are ASSEMBLED onto one canvas at the job's per-line offsets
# (float sum; overlaps, if the duration model ever returns a line
# longer than its slot, would sum -- the result reports each line's
# rendered seconds so the system side can name any overhang).
# Print gain: if a struck file's float peak would exceed -1 dBFS,
# the file is printed at exactly the gain that lands the peak on
# -1 dBFS and the gain is REPORTED in the result (the Spear vocal
# stem's print-gain precedent) -- never applied silently, never
# applied when the peak already sits under the ceiling.
#
# DOCTRINE: the bridge is a wall with two small doors, both JSON --
# the same wall the MusicGen bridge keeps. This side knows nothing
# of the Divine Nine, of scores, or of lyrics; it knows tokens and
# frames. The canon law lives on the system side, where it can be
# unit-tested without a neural network in the room.
# ---------------------------------------------------------------------

import gc
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
import soundfile as sf

SR = 44100                 # The bank and vocoder's native rate.
HOP = 512                  # Vocoder hop; FPS below is its clock.
FPS = SR / HOP             # 86.1328 frames per second.
PRINT_CEILING = 0.8913     # -1.0 dBFS: the house print ceiling.


def _log(msg):
    """Progress goes to stderr; stdout is reserved for the result."""
    print(f"[render_diffsinger] {msg}", file=sys.stderr, flush=True)


def _print_gain(peak):
    """The gain that prints a peak on the ceiling; 1.0 if unneeded.

    MECHANISM: pure ratio, no taste in it -- if the float peak is
    already at or under PRINT_CEILING the file prints raw (gain
    exactly 1.0); otherwise the gain is ceiling/peak, and the
    caller records it beside the file it struck.
    """
    if peak <= 0.0 or peak <= PRINT_CEILING:
        return 1.0
    return PRINT_CEILING / peak


def _write_printed(path, wav):
    """Write one mono float waveform as PCM_16, print gain applied.

    Returns (peak_before, gain) so the result line can confess both.
    """
    peak = float(np.max(np.abs(wav))) if len(wav) else 0.0
    gain = _print_gain(peak)
    sf.write(path, wav * gain, SR, subtype="PCM_16")
    return peak, gain


def _run_job(job):
    bank = job["bank_dir"]
    out_dir = job["out_dir"]
    lines_dir = os.path.join(out_dir, "lines")
    os.makedirs(lines_dir, exist_ok=True)
    t0 = time.time()

    opts = ort.SessionOptions()
    opts.intra_op_num_threads = int(job.get("threads", 4))

    def sess(path):
        return ort.InferenceSession(
            str(path), sess_options=opts,
            providers=["CPUExecutionProvider"])

    lines = job["lines"]
    spk_emb = {}
    for spk in sorted({ln["speaker"] for ln in lines}):
        spk_emb[spk] = np.fromfile(
            os.path.join(bank, f"{spk}.emb"),
            dtype=np.float32).reshape(1, 1, 256)
    _log(f"{len(lines)} lines, speakers {sorted(spk_emb)}")

    # ---- Stage 1+2: duration model, all lines ---------------------
    s_ling = sess(os.path.join(bank, "dsdur", "linguistic.onnx"))
    s_dur = sess(os.path.join(
        bank, "dsdur", "duration_lem_26v.dur.onnx"))
    for ln in lines:
        tokens = np.array([ln["tokens"]], dtype=np.int64)
        enc, xmask = s_ling.run(None, {
            "tokens": tokens,
            "languages": np.array([ln["languages"]], dtype=np.int64),
            "word_div": np.array([ln["word_div"]], dtype=np.int64),
            "word_dur": np.array([ln["word_dur"]], dtype=np.int64)})
        spk_tok = np.repeat(spk_emb[ln["speaker"]],
                            tokens.shape[1], axis=1)
        pred = s_dur.run(None, {
            "encoder_out": enc, "x_masks": xmask,
            "ph_midi": np.array([ln["ph_midi"]], dtype=np.int64),
            "spk_embed": spk_tok})[0]
        frames = np.maximum(
            1, np.round(pred.reshape(-1)).astype(np.int64))
        ln["_frames"] = frames
        ln["_T"] = int(frames.sum())
        _log(f"[dur] {ln['id']}: {ln['_T']} frames "
             f"({ln['_T'] / FPS:.2f}s)")
    del s_ling, s_dur
    gc.collect()

    # ---- Stage 3: variance model, all lines -----------------------
    s_ling = sess(os.path.join(bank, "dsvariance", "linguistic.onnx"))
    s_var = sess(os.path.join(
        bank, "dsvariance", "pitch_variance_lem_25.variance.onnx"))
    for ln in lines:
        frames = ln["_frames"]
        T = ln["_T"]
        enc2, _ = s_ling.run(None, {
            "tokens": np.array([ln["tokens"]], dtype=np.int64),
            "languages": np.array([ln["languages"]], dtype=np.int64),
            "ph_dur": frames.reshape(1, -1)})
        midi_frames = np.repeat(
            np.array(ln["ph_midi"], dtype=np.float32), frames)
        nz = np.where(midi_frames > 0)[0]
        filled = midi_frames.copy()
        last = midi_frames[nz[0]] if len(nz) else 0.0
        for i in range(T):
            if filled[i] > 0:
                last = filled[i]
            else:
                filled[i] = last
        ln["_f0"] = np.where(
            midi_frames > 0,
            440.0 * 2 ** ((midi_frames - 69) / 12), 0.0)
        spk_fr = np.repeat(spk_emb[ln["speaker"]], T, axis=1)
        ln["_spk_fr"] = spk_fr
        voicing, tension = s_var.run(None, {
            "encoder_out": enc2, "ph_dur": frames.reshape(1, -1),
            "pitch": filled.reshape(1, -1).astype(np.float32),
            "voicing": np.zeros((1, T), dtype=np.float32),
            "tension": np.zeros((1, T), dtype=np.float32),
            "retake": np.ones((1, T, 2), dtype=bool),
            "spk_embed": spk_fr,
            "steps": np.array(20, dtype=np.int64)})
        ln["_voicing"] = voicing.astype(np.float32)
        ln["_tension"] = tension.astype(np.float32)
        _log(f"[var] {ln['id']}: voicing mean {voicing.mean():.2f} "
             f"tension mean {tension.mean():.2f}")
    del s_ling, s_var
    gc.collect()

    # ---- Stage 4: acoustic model, all lines -----------------------
    s_ac = sess(os.path.join(bank, "acoustic_lem_25.onnx"))
    for ln in lines:
        T = ln["_T"]
        mel = s_ac.run(None, {
            "tokens": np.array([ln["tokens"]], dtype=np.int64),
            "languages": np.array([ln["languages"]], dtype=np.int64),
            "durations": ln["_frames"].reshape(1, -1),
            "f0": ln["_f0"].reshape(1, -1).astype(np.float32),
            "voicing": ln["_voicing"], "tension": ln["_tension"],
            "gender": np.zeros((1, T), dtype=np.float32),
            "velocity": np.ones((1, T), dtype=np.float32),
            "spk_embed": ln["_spk_fr"],
            "depth": np.array(0.6, dtype=np.float32),
            "steps": np.array(30, dtype=np.int64)})[0]
        ln["_mel"] = mel
        _log(f"[acoustic] {ln['id']}: mel {mel.shape}")
    del s_ac
    gc.collect()

    # ---- Stage 5: vocoder, all lines ------------------------------
    sys.path.insert(0, job["lab_dir"])
    import torch
    from modules.nsf_hifigan.models import load_model
    # load_model calls model_path.with_name('config.json'): it
    # takes a pathlib.Path, NOT a str -- the proven Spear call
    # passed a Path. (First engine run died here on exactly this:
    # a str path raised AttributeError at the vocoder door, after
    # all four ONNX stages had already sung. Named, not hidden.)
    model, _h = load_model(Path(job["vocoder_dir"]) / "model.ckpt")
    model.eval()
    results = []
    wavs = {}
    for ln in lines:
        with torch.no_grad():
            c = torch.from_numpy(ln["_mel"]).transpose(1, 2)
            f0t = torch.from_numpy(
                ln["_f0"].reshape(1, -1).astype(np.float32))
            wav = model(c, f0t).view(-1).cpu().numpy()
        name = f"{ln['id']}.wav"
        peak, gain = _write_printed(os.path.join(lines_dir, name), wav)
        wavs[ln["id"]] = wav * gain
        results.append({
            "id": ln["id"], "file": f"lines/{name}",
            "frames": ln["_T"], "samples": int(len(wav)),
            "seconds": round(len(wav) / SR, 4),
            "float_peak": round(peak, 4),
            "print_gain": round(gain, 4)})
        _log(f"[vocoder] {name}: {len(wav)} samples "
             f"(peak {peak:.3f}, gain {gain:.3f})")
        for key in ("_mel", "_spk_fr", "_voicing", "_tension"):
            del ln[key]
        gc.collect()
    del model
    gc.collect()

    # ---- Assembly: the lines on one canvas, at their offsets ------
    # The canvas is sized to the job's total OR to the longest
    # line's true end, whichever reaches further: a line that
    # renders long overlaps its neighbour (summed, and named by
    # the system side from the reported seconds) -- it is never
    # clipped at the canvas edge to fit the plan.
    asm = job["assembly"]
    total = int(round(float(asm["total_s"]) * SR))
    for ln in lines:
        off = int(round(float(asm["offsets_s"][ln["id"]]) * SR))
        total = max(total, off + len(wavs[ln["id"]]))
    canvas = np.zeros(total, dtype=np.float32)
    for ln in lines:
        off = int(round(float(asm["offsets_s"][ln["id"]]) * SR))
        wav = wavs[ln["id"]]
        canvas[off:off + len(wav)] += wav
    peak, gain = _write_printed(
        os.path.join(out_dir, asm["file"]), canvas)
    assembly = {"file": asm["file"], "samples": total,
                "seconds": round(total / SR, 4),
                "float_peak": round(peak, 4),
                "print_gain": round(gain, 4)}
    _log(f"[assembly] {asm['file']}: {total} samples "
         f"(peak {peak:.3f}, gain {gain:.3f})")
    return {"ok": True, "kind": "diffsinger",
            "lines": results, "assembly": assembly,
            "wall_seconds": round(time.time() - t0, 2)}


def main(argv):
    if len(argv) != 2:
        print(json.dumps({"ok": False,
                          "error": "usage: render_diffsinger.py "
                                   "JOB.json"}))
        return 2
    with open(argv[1], "r", encoding="utf-8") as fh:
        job = json.load(fh)
    try:
        result = _run_job(job)
    except Exception as exc:  # surface, never swallow
        print(json.dumps({"ok": False,
                          "error": f"{type(exc).__name__}: {exc}"}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# 93 -- Live, Love, and let Love, Live.
