#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — studio/detect.py — THE DETECTION SEAT: voice
# activity, language identification, and transcription, fully
# offline, on the ggml family the bench already speaks.
#
# Epigraph: "Prove all things; hold fast that which is good."
# — 1 Thessalonians 5:21 (KJV), the house's standing text for
#   every instrument that claims to measure.
#
# 93.
# Date: 24 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
#   Hypothesis: that the studio's renders can be EXAMINED for
#     what they audibly are — which language came out, where the
#     voice is and is not, and what words a listener would write
#     down — by instruments that run on this machine, offline,
#     with no cloud seat and no subscription; and that the
#     founder's ear verdict on the DETROIT MUGETSU hook ("it
#     sounded weird but i heard a couple Japanese words in it")
#     is a measurement the bench should be able to state in
#     numbers beside the ear.
#   Method: whisper.cpp (the ggml sibling runtime of the
#     llama.cpp family the speech seat already rides) with the
#     multilingual base model, for language identification and
#     transcription; Silero VAD over ONNX Runtime for voice
#     activity, with a measured energy VAD as the standing
#     fallback; every read printed with its engine and model
#     named, and every disagreement with known content reported
#     as measured, never tuned away.
#   Observation (the bench's first reads, 24 November 2026):
#     the ZONOS3-Mini narration of THE PIRATE ESSAY identifies
#     as English at p = 0.9972 and transcribes recognizably
#     against its script; the DiffSinger DETROIT MUGETSU hook
#     identifies as Japanese at p = 0.8241 on the dedicated
#     detection pass — while the auto-decoding transcription
#     pass misfires to English on the same audio, and a
#     Japanese-forced decode yields kana that are Japanese in
#     shape but are NOT the sheet's words. The seat therefore
#     identifies LANGUAGE reliably at this model size and
#     transcribes SPOKEN words serviceably; lyric-accurate
#     transcription of a sung soprano is beyond the base model,
#     and this module prints that coordinate rather than
#     smoothing it.
#   Result: this module — detect_language, transcribe,
#     voice_segments, lyric_timing_draft — wired into the
#     Vocal Exam as two additive judges (language, coverage).
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""The Detection Seat — offline voice/language examination.

DOCTRINE — WHAT THIS SEAT IS, AND WHAT IT REFUSES TO BE:
  The studio renders; this seat LISTENS BACK, with instruments.
  It answers three questions about any audio file, offline:
  what language is this (Whisper's native identification),
  where is the voice (voice-activity segments), and what words
  does a machine listener hear (transcription with segment
  timestamps). It is an examination seat, kin to the Vocal
  Exam, not a production engine: it sings nothing, speaks
  nothing, and corrects nothing. A read that disagrees with
  what a render was supposed to be is reported as measured —
  the disagreement IS the finding (the Mugetsu hook's
  detection pass and decoding pass disagreeing with each
  other stands in this module's header, at full size).

  The seat is deliberately built on the ggml family: the
  house's speech seat is ZONOS3-Mini via llama.cpp's llama-tts
  (b12438, ~/workspace/lab/zonos3-mini), and whisper.cpp is
  that runtime's sibling — one family of local inference, no
  cloud seat, no account, no telemetry. The model seated is
  ggml-base (multilingual, 147,951,465 bytes on disk): the
  trade, printed — tiny (~75 MB) decodes faster on this
  1.5-CPU bench but its language identification is the weaker
  instrument, and identification is this seat's first duty;
  base reads a 20 s clip's language in ~5 s and transcribes
  it in ~13 s here, which the exam can afford. A larger model
  is a drop-in at the same seat (RESONANTIA_WHISPER_MODEL)
  whenever the bench grows.

MECHANISM — THE TWO-PASS TRANSCRIPTION LAW:
  transcribe() runs the dedicated detection pass FIRST
  (whisper-cli --detect-language) and then decodes with that
  language forced (-l <detected>). The reason is measured,
  not theoretical: left on auto, the decoder's own language
  guess on the sung Mugetsu hook lands on English and emits
  "(singing in foreign language)", while the dedicated pass
  reads the same audio as Japanese at p = 0.8241. Detection
  and decoding are different reads of the encoder; the seat
  takes the detection pass's word for the language and the
  decoder's word for the text, and prints both.

MECHANISM — VOICE ACTIVITY, TWO ENGINES, ONE RETURN:
  voice_segments() serves Silero VAD when its ONNX model and
  onnxruntime are present (engine "silero-onnx"): the v5
  model read statefully in 512-sample windows at 16 kHz,
  each window carrying the 64-sample context the model was
  trained with — omit the context and the same model reads
  clear narration at p <= 0.071, a coordinate measured on
  this bench and recorded here so no future hand has to
  rediscover it. Speech is p >= 0.5; runs are merged across
  gaps under 0.25 s and segments under 0.1 s are dropped.
  The fallback (engine "energy-decile") is a measured energy
  VAD in the house's own onset-judge idiom: 30 ms frame RMS
  in dB, the threshold standing on the quiet decile
  (10th percentile + 12 dB, floored at -55 dBFS), the same
  merge/drop law. Which engine served is printed in every
  return; the two are never blended silently.

MECHANISM — THE LYRIC TIMING DRAFT:
  lyric_timing_draft() turns a transcription into the first
  artifact of a transcription production (the founder's
  standing rule: a track with no notation gets a
  transcription production, never a fabricated sheet). The
  draft is an ABC file at Q:1/4=60 — one quarter note is one
  second, so note lengths read as seconds — one bar per
  segment, the segment's words on the w: line, its exact
  offsets in a %%text comment, and a JSON sidecar carrying
  the unrounded timings. It is marked DRAFT in its title and
  its header text, and it is never a finished sheet: the
  words are ASR output, unverified against any lyric of
  record, and the pitches are a neutral placeholder.

SEAT LAYOUT (local assets, never repo content — the
diffsinger-lab precedent; rebuild recipe in
docs/OFFLINE-PRODUCTION.md):
  tools/whisper.cpp/            the whisper.cpp clone + build
  tools/whisper.cpp/models/ggml-base.bin
  tools/silero/silero_vad.onnx  the Silero VAD model
Env overrides: RESONANTIA_WHISPER_CLI, RESONANTIA_WHISPER_MODEL,
RESONANTIA_SILERO_VAD.
"""

import json
import math
import os
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from resonance.studio import pipeline as _pipeline

__all__ = [
    "DetectError",
    "seat_status",
    "detect_language",
    "transcribe",
    "voice_segments",
    "lyric_timing_draft",
]

_REPO = Path(__file__).resolve().parents[2]
WHISPER_DIR = _REPO / "tools" / "whisper.cpp"
SILERO_PATH = _REPO / "tools" / "silero" / "silero_vad.onnx"

_MODEL_NAME = "ggml-base"
_VAD_THRESHOLD = 0.5          # Silero speech probability seat
_VAD_WINDOW = 512             # samples per Silero step at 16 kHz
_VAD_CONTEXT = 64             # the model's trained context carry
_MERGE_GAP_S = 0.25           # merge speech across gaps under this
_MIN_SEGMENT_S = 0.1          # drop segments under this
_ENERGY_FRAME_S = 0.030       # energy VAD frame
_ENERGY_MARGIN_DB = 12.0      # threshold = quiet decile + this
_ENERGY_FLOOR_DBFS = -55.0    # ... and never below this


class DetectError(Exception):
    """A refusal by name from the detection seat."""


# ---------------------------------------------------------------------
# Seat layout: where the binaries and models stand.
# ---------------------------------------------------------------------

def _whisper_cli():
    env = os.environ.get("RESONANTIA_WHISPER_CLI")
    return Path(env) if env else WHISPER_DIR / "build" / "bin" / "whisper-cli"


def _whisper_model():
    env = os.environ.get("RESONANTIA_WHISPER_MODEL")
    return Path(env) if env else WHISPER_DIR / "models" / "ggml-base.bin"


def _silero_model():
    env = os.environ.get("RESONANTIA_SILERO_VAD")
    return Path(env) if env else SILERO_PATH


def seat_status():
    """What of the seat stands on this machine, named piece by piece.

    MECHANISM: existence (and size, for models) of the whisper
    binary and model, the Silero model, and the onnxruntime
    import. The exam's language judge reads its UNMEASURABLE
    state from this; nothing here pretends a missing piece is
    present.
    """
    cli, model, silero = _whisper_cli(), _whisper_model(), _silero_model()
    try:
        import onnxruntime  # noqa: F401
        ort = True
    except ImportError:
        ort = False
    return {
        "whisper_cli": str(cli), "whisper_cli_present": cli.exists(),
        "whisper_model": str(model),
        "whisper_model_present": model.exists(),
        "whisper_model_bytes": model.stat().st_size
        if model.exists() else None,
        "whisper_model_name": _MODEL_NAME,
        "silero_model": str(silero),
        "silero_model_present": silero.exists(),
        "onnxruntime_present": ort,
        "vad_engine_available": "silero-onnx"
        if (silero.exists() and ort) else "energy-decile",
    }


def _require_whisper():
    cli, model = _whisper_cli(), _whisper_model()
    missing = [str(p) for p in (cli, model) if not p.exists()]
    if missing:
        raise DetectError(
            "detection seat incomplete: missing "
            + ", ".join(missing)
            + " — the rebuild recipe stands in "
              "docs/OFFLINE-PRODUCTION.md")
    return cli, model


# ---------------------------------------------------------------------
# Audio preparation: whisper and Silero both eat 16 kHz mono.
# ---------------------------------------------------------------------

def _prepare_16k(path):
    """(wav_path, cleanup) — a 16 kHz mono WAV view of the input.

    MECHANISM: a PCM WAV already at 16 kHz mono is used as it
    stands; anything else is converted by ffmpeg into a temp
    file the caller removes via cleanup(). The conversion is
    a view, never an edit: the source file is untouched.
    """
    path = Path(path)
    if not path.exists():
        raise DetectError(f"detect: no file at {path}")
    if path.suffix.lower() == ".wav":
        try:
            import wave
            with wave.open(str(path), "rb") as w:
                if w.getframerate() == 16000 and w.getnchannels() == 1:
                    return path, lambda: None
        except Exception:
            pass  # not a plain PCM WAV: fall through to ffmpeg
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    try:
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(path),
             "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
             tmp.name],
            check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        Path(tmp.name).unlink(missing_ok=True)
        raise DetectError(
            f"detect: ffmpeg cannot read {path}: "
            f"{e.stderr.decode(errors='replace')[:200]}")
    return Path(tmp.name), lambda: Path(tmp.name).unlink(missing_ok=True)


# ---------------------------------------------------------------------
# Language identification and transcription (whisper.cpp).
# ---------------------------------------------------------------------

_LANG_RE = re.compile(r"auto-detected language: (\w+) \(p = ([\d.]+)\)")


def _whisper_detect(wav16, cli, model):
    proc = subprocess.run(
        [str(cli), "-m", str(model), "-f", str(wav16),
         "--detect-language"],
        capture_output=True, text=True)
    m = _LANG_RE.search(proc.stderr + proc.stdout)
    if m is None:
        raise DetectError(
            "detect: whisper printed no language read "
            f"(exit {proc.returncode})")
    return m.group(1), float(m.group(2))


def detect_language(path):
    """Whisper's native language identification for one file.

    Returns {"language", "probability", "engine", "model"} —
    the code and the model's own probability, as printed by
    the dedicated detection pass (see the two-pass law in the
    module docstring for why this pass, not the decoder's
    guess, is the seat's word).
    """
    cli, model = _require_whisper()
    wav16, cleanup = _prepare_16k(path)
    try:
        lang, prob = _whisper_detect(wav16, cli, model)
    finally:
        cleanup()
    return {"language": lang, "probability": round(prob, 4),
            "engine": "whisper.cpp", "model": _MODEL_NAME}


def transcribe(path):
    """Transcribe one file: text + timed segments + language.

    MECHANISM: the two-pass law — detect first, then decode
    with the detected language forced. Segments carry the
    decoder's own offsets (whisper.cpp JSON, milliseconds
    home to seconds here), in order, text stripped. The
    return names the engine and model beside the words, so a
    transcript never circulates as an unattributed authority:
    these are a machine listener's words, measured as such.
    """
    cli, model = _require_whisper()
    wav16, cleanup = _prepare_16k(path)
    try:
        lang, prob = _whisper_detect(wav16, cli, model)
        with tempfile.TemporaryDirectory() as td:
            base = str(Path(td) / "transcript")
            proc = subprocess.run(
                [str(cli), "-m", str(model), "-f", str(wav16),
                 "-l", lang, "-ojf", "-of", base],
                capture_output=True, text=True)
            if proc.returncode != 0:
                raise DetectError(
                    f"transcribe: whisper exited {proc.returncode}: "
                    f"{proc.stderr[-200:]}")
            doc = json.loads(Path(base + ".json").read_text())
        segments = [{
            "start_s": round(s["offsets"]["from"] / 1000.0, 3),
            "end_s": round(s["offsets"]["to"] / 1000.0, 3),
            "text": s["text"].strip(),
        } for s in doc.get("transcription", [])]
    finally:
        cleanup()
    return {"language": lang, "language_probability": round(prob, 4),
            "text": " ".join(s["text"] for s in segments).strip(),
            "segments": segments,
            "engine": "whisper.cpp", "model": _MODEL_NAME}


# ---------------------------------------------------------------------
# Voice activity: Silero VAD over ONNX, energy fallback.
# ---------------------------------------------------------------------

def _merge_segments(raw, duration_s):
    """The merge/drop law both VAD engines share.

    MECHANISM: sort by start; merge across gaps under
    _MERGE_GAP_S; drop segments under _MIN_SEGMENT_S. The law
    is one because the return is one: a segment list must
    mean the same thing whichever engine served it.
    """
    merged = []
    for start, end in sorted(raw):
        if merged and start - merged[-1][1] < _MERGE_GAP_S:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [{"start_s": round(s, 3), "end_s": round(e, 3)}
            for s, e in merged
            if e - s >= _MIN_SEGMENT_S and s < duration_s]


def _silero_segments(wav16_path):
    """Speech runs from Silero VAD (ONNX), or None if unseated.

    MECHANISM: the v5 model, statefully — 512-sample windows,
    each prefixed with the last 64 samples of the previous
    window (the trained context; see the module docstring
    for the measured cost of omitting it), state carried
    across windows, sr handed in as the model asks. Speech
    frames at p >= _VAD_THRESHOLD become runs on the window
    grid (32 ms seats).
    """
    model = _silero_model()
    if not model.exists():
        return None
    try:
        import onnxruntime as ort
    except ImportError:
        return None
    data, sr = _pipeline.read_wav_pcm(wav16_path)
    x = np.asarray(data, dtype=np.float32)
    if x.ndim == 2:
        x = x.mean(axis=0)
    x = np.ascontiguousarray(x.reshape(-1), dtype=np.float32)
    sess = ort.InferenceSession(str(model),
                                providers=["CPUExecutionProvider"])
    state = np.zeros((2, 1, 128), dtype=np.float32)
    sr_in = np.array(16000, dtype=np.int64)
    context = np.zeros(_VAD_CONTEXT, dtype=np.float32)
    raw, t = [], 0.0
    step = _VAD_WINDOW / 16000.0
    for i in range(0, len(x) - _VAD_WINDOW + 1, _VAD_WINDOW):
        chunk = np.concatenate(
            [context, x[i:i + _VAD_WINDOW]]).reshape(1, -1)
        out, state = sess.run(
            None, {"input": chunk.astype(np.float32),
                   "state": state, "sr": sr_in})
        if float(out[0][0]) >= _VAD_THRESHOLD:
            raw.append((t, t + step))
        context = x[i + _VAD_WINDOW - _VAD_CONTEXT:i + _VAD_WINDOW]
        t += step
    return raw, len(x) / 16000.0


def _energy_segments(path):
    """Speech runs from the measured energy VAD (the fallback).

    MECHANISM: mono by the channel mean; 30 ms frames; frame
    RMS in dBFS; the threshold stands on the quiet decile —
    the 10th percentile of frame levels + _ENERGY_MARGIN_DB,
    floored at _ENERGY_FLOOR_DBFS — the onset judge's idiom:
    the file's own quiet sets the bar, so the law travels
    across masters of different loudness.
    """
    data, sr = _pipeline.read_wav_pcm(path)
    x = np.asarray(data, dtype=np.float64)
    if x.ndim == 2:
        x = x.mean(axis=0) if x.shape[0] <= x.shape[1] \
            else x.mean(axis=1)
    x = x.reshape(-1)
    frame = max(1, int(_ENERGY_FRAME_S * sr))
    n = len(x) // frame
    if n == 0:
        return [], len(x) / float(sr)
    frames = x[:n * frame].reshape(n, frame)
    rms = np.sqrt(np.mean(frames ** 2, axis=1))
    db = 20.0 * np.log10(rms + 1e-12)
    quiet = float(np.percentile(db, 10))
    thr = max(quiet + _ENERGY_MARGIN_DB, _ENERGY_FLOOR_DBFS)
    raw = [(i * _ENERGY_FRAME_S, (i + 1) * _ENERGY_FRAME_S)
           for i in range(n) if db[i] > thr]
    return raw, len(x) / float(sr)


def voice_segments(path, engine="auto"):
    """Timed speech regions of one file, and their coverage.

    Returns {"engine", "segments", "speech_s", "duration_s",
    "coverage", "longest_silence_s"}. engine="auto" seats
    Silero when present and the energy VAD otherwise; an
    explicit engine name is obeyed, and naming "silero-onnx"
    where the model or runtime is absent is a refusal, not a
    silent substitution — which engine served is part of the
    measurement.
    """
    if engine not in ("auto", "silero-onnx", "energy-decile"):
        raise DetectError(f"vad: {engine!r} is not a seated engine")
    served, got = None, None
    if engine in ("auto", "silero-onnx"):
        wav16, cleanup = _prepare_16k(path)
        try:
            got = _silero_segments(wav16)
        finally:
            cleanup()
        if got is not None:
            served = "silero-onnx"
        elif engine == "silero-onnx":
            raise DetectError(
                "vad: silero-onnx named but its model or "
                "onnxruntime is absent on this machine")
    if got is None:
        got = _energy_segments(path)
        served = "energy-decile"
    raw, duration_s = got
    segments = _merge_segments(raw, duration_s)
    speech_s = sum(s["end_s"] - s["start_s"] for s in segments)
    longest = 0.0
    cursor = 0.0
    for s in segments:
        longest = max(longest, s["start_s"] - cursor)
        cursor = max(cursor, s["end_s"])
    longest = max(longest, duration_s - cursor)
    return {"engine": served, "segments": segments,
            "speech_s": round(speech_s, 3),
            "duration_s": round(duration_s, 3),
            "coverage": round(speech_s / duration_s, 4)
            if duration_s > 0 else 0.0,
            "longest_silence_s": round(longest, 3)}


# ---------------------------------------------------------------------
# The lyric timing draft: transcription -> the sheets road.
# ---------------------------------------------------------------------

def _abc_stamp(seconds):
    m, s = divmod(seconds, 60.0)
    return f"{int(m):02d}:{s:05.2f}"


def lyric_timing_draft(path, abc_path, title=None):
    """Write the DRAFT sheet-sidecar for a render's transcription.

    MECHANISM: transcribe(); one ABC bar per segment at
    Q:1/4=60 (a quarter note is a second, so a segment of
    8.28 s stands as an 8-quarter placeholder note — lengths
    rounded to the whole second in the notation, exact in
    the %%text comment above the bar and in the JSON sidecar
    at <abc stem>.timing.json). The segment's words ride the
    w: line. Returns the transcription record plus the paths
    written. The artifact is a DRAFT by construction and by
    label; finishing it — verifying words against a lyric of
    record, seating real pitches — is the transcription
    production's human work, and this function does none of
    it silently.
    """
    abc_path = Path(abc_path)
    record = transcribe(path)
    title = title or Path(path).stem
    lines = [
        "X:1",
        f"T:{title} — LYRIC TIMING DRAFT",
        "% DRAFT — machine transcription by the Resonantia "
        "detection seat",
        "% (whisper.cpp, ggml-base, fully offline). NOT a "
        "finished sheet:",
        "% the words are ASR output, unverified against any "
        "lyric of record;",
        "% pitches are a neutral placeholder; note lengths "
        "are segment",
        "% durations rounded to the second at Q:1/4=60 (one "
        "quarter = 1 s);",
        "% exact offsets stand in the %%text line over each "
        "bar and in the",
        "% JSON sidecar. Language read: "
        f"{record['language']} (p = "
        f"{record['language_probability']}).",
        "M:4/4",
        "L:1/4",
        "Q:1/4=60",
        "K:C",
    ]
    for seg in record["segments"]:
        dur = max(1, int(round(seg["end_s"] - seg["start_s"])))
        lines.append(
            f"%%text [{_abc_stamp(seg['start_s'])} --> "
            f"{_abc_stamp(seg['end_s'])}]")
        lines.append(f"B{dur} |")
        words = seg["text"].replace("|", " ").strip()
        lines.append(f"w: {words}")
    abc_path.parent.mkdir(parents=True, exist_ok=True)
    abc_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sidecar = abc_path.with_suffix(".timing.json")
    sidecar.write_text(json.dumps(
        {"source": str(path), "draft": str(abc_path),
         "language": record["language"],
         "language_probability": record["language_probability"],
         "engine": record["engine"], "model": record["model"],
         "segments": record["segments"]},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return {**record, "abc_path": str(abc_path),
            "timing_path": str(sidecar)}


if __name__ == "__main__":
    print(json.dumps(seat_status(), indent=2))
