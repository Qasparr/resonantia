#!/usr/bin/env python3
# =====================================================================
# THE PIRATE ESSAY -- AUDIOBOOK RUN 1: ASSEMBLE, MASTER, SEAL, FILM
#
#   A Scientific Illuminist treatment of the house's first in-house
#   audiobook: the founder's stamped essay, narrated by the speech
#   seat (ZONOS3-Mini), mastered by the Four Powers path, sealed in
#   the Render-as-Proof ledger, and filmed as a static-cover video
#   edition.
#
#   Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
#   (Greek, -ARR, All Rights Reserved, Without Prejudice)
#   XVI day of November, Dies Lunae, Sol in Scorpio,
#   Anno V:xii e.n. (2026 e.v.)
#
#   Method of Science, Aim of Religion
#   Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR,
#   All Rights Reserved, Without Prejudice. Right of claim hereby
#   reserved and coined under the authority of the Living Man.
#
# MECHANISM, in the order the build runs:
#   1. ASSEMBLE -- the 21 rendered chunks (44.1 kHz mono, llama-tts)
#      are converted to the master's 48 kHz, joined in document
#      order with stated silences between them (1.2 s; 2.5 s before
#      the Annex and before the Colophon), and struck as a 24-bit
#      assembled WAV. No content is trimmed; joins are additions of
#      silence only.
#   2. MASTER -- the Four Powers path of mugetsu run 2, re-cut for
#      long-form: Scire measures (the pipeline's own LUFS scale on
#      the whole signal; true peak by the pipeline's own FFT
#      oversampling, computed in 120 s windows with 5 s overlaps --
#      intersample peaks are local, so the windowed maximum is the
#      whole-signal maximum), then master_signal's law applied
#      pointwise in blocks (gain to -14 LUFS, soft-limit, true-peak
#      trim -- gain and limiter are sample-local operations, so the
#      blocked application is the same arithmetic, not an
#      approximation of it), Tacere's TPDF dither at the 24-bit
#      strike (seeded per block from the house seed 93, the same
#      triangular law run 2 struck whole), and the delivered MP3 at
#      the sworn 320,000 bps.
#   3. PROOFS -- the narration render is stamped as a vocal proof
#      (manifest naming the speech engine and the source text's
#      hash); the master is appended through append_master_proof,
#      sealed or FAILED by the gate's measurement of the DELIVERED
#      MP3 decoded. The gate's scales (proofs.measure_master) run
#      in a subprocess so a memory failure there cannot take the
#      build down; if they cannot carry the long form, the measured
#      body is computed by the same scales in blocks and the
#      substitution is confessed in the manifest at full size.
#   4. VIDEO -- a static, honest visual: the bookshop front cover
#      on the doctrine purple, the title, and the TVRRIS VERITATIS
#      seal, 1920x1080; the audio is the sealed master, stream-
#      copied if the container allows, re-encoded at the same
#      bitrate only if it does not (and the manifest says which).
#
# DOCTRINE: the labels stay honest -- this is a SPOKEN-WORD
# audiobook master: one narrated stem, the founder's own text read
# by the house speech seat. It is not sung, not a mix, and no real
# person's voice is cloned or imitated: the voice is a predefined
# voice shipping inside the model's own release.
#
# CORRECTIO (appended during the run, the original plan above
# standing): the first master strike died silently at the
# whole-signal scales (the LUFS FFT the length of the signal;
# four_powers' RMS witness squaring the whole body into RAM).
# Scire and the loudness scales now run in their blocked,
# time-domain forms -- same coefficients, same reductions,
# validated at delta 0.0000 LU against the whole-signal scale on
# two slices of this program. The law did not change; the body
# carrying it did.
# =====================================================================

import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from resonance.studio import four_powers as fp      # noqa: E402
from resonance.studio import pipeline                # noqa: E402
from resonance.studio import proofs                  # noqa: E402

ESSAY_DIR = Path.home() / "workspace" / "your_files" / "pirate-essay"
SOURCE_MD = ESSAY_DIR / "THE-PIRATE-ESSAY.md"
MP3_OUT = ESSAY_DIR / "THE-PIRATE-ESSAY-AUDIOBOOK.mp3"
VIDEO_OUT = ESSAY_DIR / "THE-PIRATE-ESSAY-VIDEO.mp4"
COVER = (Path.home() / "workspace" / "bookshop" / "covers"
         / "FRONT-pirate-essay.png")
SEAL = Path.home() / "workspace" / "templates" / "doctrine-logo.png"
LEDGER = REPO / "proofs" / "ledger.jsonl"
SCRIPT_DIR = HERE / "script"
CHUNK_DIR = HERE / "chunks"
ASSEMBLED = HERE / "assembled.wav"
MASTER_WAV = HERE / "master.wav"
MANIFEST = HERE / "manifest.json"
SR = pipeline.TARGET_SR
SEED = 93
VOICE = "Imogen_en-British_F_1"
GAP_DEFAULT = 1.2
GAPS_BEFORE = {"18": 2.5, "21": 2.5}   # before the Annex, the Colophon


def _ffmpeg(args, what):
    proc = subprocess.run(["ffmpeg", "-y", "-v", "error", *args],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg ({what}) failed: "
                           f"{proc.stderr.strip()}")


def _probe_duration(path):
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True)
    return float(proc.stdout.strip())


def _write_wav24_mono(path, samples_f32):
    """Strike a 24-bit PCM mono WAV from a float32 signal."""
    import wave
    x = np.asarray(samples_f32, dtype=np.float64)
    ints = np.clip(np.round(x * (2 ** 23)), -(2 ** 23),
                   2 ** 23 - 1).astype(np.int32)
    raw = ints.view(np.uint8).reshape(-1, 4)[:, :3]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(np.ascontiguousarray(raw).tobytes())


# ---------------------------------------------------------------------
# True peak, the pipeline's own scale, computed in windows.
# ---------------------------------------------------------------------

def block_true_peak(samples, sr, block_s=120.0, overlap_s=5.0):
    """Whole-signal true peak via pipeline.true_peak_dbtp in windows.

    MECHANISM: true_peak_dbtp reconstructs the band-limited signal
    on a 4x grid; an intersample peak is a local event (the
    interpolation kernel's support is a handful of samples), so
    the maximum over 120 s windows overlapping by 5 s is the
    whole-signal maximum, computed at a memory the box can carry.
    """
    x = np.asarray(samples)
    if x.ndim == 1:
        n = x.shape[0]
    else:
        n = x.shape[1]
    block = int(block_s * sr)
    hop = int((block_s - overlap_s) * sr)
    peak_db = -120.0
    start = 0
    while start < n:
        end = min(n, start + block)
        seg = x[:, start:end] if x.ndim == 2 else x[start:end]
        peak_db = max(peak_db, pipeline.true_peak_dbtp(seg, sr))
        if end == n:
            break
        start += hop
    return peak_db


# ---------------------------------------------------------------------
# Long-form scales: the house scales, computed in blocks.
#
# WHY THESE EXIST (the record, at full size): the first master
# attempt died silently mid-chain -- process gone, no traceback, a
# 2.95 GB working array left on disk. The whole-signal scales
# cannot carry a 64-minute program on this box:
# measure_loudness_lufs takes an FFT the length of the signal per
# channel (~3 GB of complex spectrum), and four_powers' own RMS
# witness squares the whole (2, N) body into RAM. The scales below
# are the SAME scales, blocked: the loudness is the pipeline's own
# ungated K-weighted figure with the pipeline's own biquad
# coefficients, applied in the time domain block by block (energy
# is energy, in either domain -- validated against
# measure_loudness_lufs on two 90 s slices of this very program:
# delta 0.0000 LU on both), and Scire's plain witnesses are the
# same reductions accumulated over blocks.
# ---------------------------------------------------------------------

def streaming_lufs(samples, sr, block_s=60.0):
    """pipeline.measure_loudness_lufs, computed in blocks."""
    from scipy.signal import lfilter, lfilter_zi
    x = np.asarray(samples)
    if x.ndim == 1:
        x = x[np.newaxis, :]
    n = x.shape[1]
    step = int(block_s * sr)
    total = 0.0
    for ch in x:
        zi1 = lfilter_zi(pipeline._K_PRE_B, pipeline._K_PRE_A) * 0.0
        zi2 = lfilter_zi(pipeline._K_RLB_B, pipeline._K_RLB_A) * 0.0
        ss = 0.0
        for s in range(0, n, step):
            seg = np.asarray(ch[s:s + step], dtype=np.float64)
            y, zi1 = lfilter(pipeline._K_PRE_B, pipeline._K_PRE_A,
                             seg, zi=zi1)
            y, zi2 = lfilter(pipeline._K_RLB_B, pipeline._K_RLB_A,
                             y, zi=zi2)
            ss += float(np.sum(y * y))
        total += ss / n
    if total <= 0.0:
        return -120.0
    return float(-0.691 + 10.0 * math.log10(total))


def streaming_scire(work):
    """four_powers.scire_measure's report, accumulated in blocks.

    Same fields, same scales: BS.1770 loudness (streaming form,
    above), the pipeline's oversampled true peak in windows, and
    the plain peak/RMS/crest witnesses as whole-body reductions
    accumulated block-wise instead of materialized whole.
    """
    block = int(60 * SR)
    n = work.shape[1]
    peak = 0.0
    ss = 0.0
    count = 0
    for s, e in _block_windows(n, block):
        seg = np.asarray(work[:, s:e], dtype=np.float64)
        peak = max(peak, float(np.max(np.abs(seg))) if seg.size
                   else 0.0)
        ss += float(np.sum(seg * seg))
        count += seg.size
    rms = math.sqrt(ss / count) if count else 0.0
    peak_db = (20.0 * math.log10(peak) if peak > 0 else -120.0)
    rms_db = (20.0 * math.log10(rms) if rms > 0 else -120.0)
    return {
        "stage": "metering / measurement (BS.1770)",
        "lufs_integrated": round(streaming_lufs(work, SR), 2),
        "true_peak_dbtp": round(block_true_peak(work, SR), 2),
        "sample_peak_dbfs": round(peak_db, 2),
        "rms_dbfs": round(rms_db, 2),
        "crest_db": round(peak_db - rms_db, 2),
    }


def _wav_blocks(path, block_s=60.0):
    """Stream a PCM WAV as (2, M) float32 blocks (stdlib wave)."""
    import wave
    with wave.open(str(path), "rb") as w:
        ch = w.getnchannels()
        width = w.getsampwidth()
        sr = w.getframerate()
        step = int(block_s * sr)
        while True:
            raw = w.readframes(step)
            if not raw:
                break
            if width == 2:
                a = np.frombuffer(raw, dtype=np.int16).astype(
                    np.float32) / 32768.0
            elif width == 3:
                b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
                v = (b[:, 0].astype(np.int32)
                     | (b[:, 1].astype(np.int32) << 8)
                     | (b[:, 2].astype(np.int32) << 16))
                v = np.where(v >= 2 ** 23, v - 2 ** 24, v)
                a = v.astype(np.float32) / float(2 ** 23)
            else:
                raise ValueError(f"wav width {width} unsupported")
            a = a.reshape(-1, ch).T
            if a.shape[0] == 1:
                a = np.vstack([a, a])
            yield sr, a


def streaming_tp_wav(path):
    """pipeline.true_peak_dbtp over a WAV file, in 120 s windows
    with 5 s overlaps, read from disk -- never whole."""
    import wave
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        total = w.getnframes()
    win = int(120 * sr)
    hop = int(115 * sr)
    peak_db = -120.0
    start = 0
    while start < total:
        count = min(win, total - start)
        buf = []
        for _, blk in _wav_blocks_range(path, start, count):
            buf.append(blk)
        seg = np.concatenate(buf, axis=1) if buf else None
        if seg is not None and seg.shape[1]:
            peak_db = max(peak_db, pipeline.true_peak_dbtp(seg, sr))
        if start + count >= total:
            break
        start += hop
    return peak_db


def _wav_blocks_range(path, start, count):
    """Yield (sr, block) for frames [start, start+count) of a WAV."""
    import wave
    with wave.open(str(path), "rb") as w:
        ch = w.getnchannels()
        width = w.getsampwidth()
        sr = w.getframerate()
        w.setpos(start)
        remaining = count
        while remaining > 0:
            raw = w.readframes(min(remaining, int(30 * sr)))
            if not raw:
                break
            got = len(raw) // (width * ch)
            remaining -= got
            if width == 2:
                a = np.frombuffer(raw, dtype=np.int16).astype(
                    np.float32) / 32768.0
            elif width == 3:
                b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
                v = (b[:, 0].astype(np.int32)
                     | (b[:, 1].astype(np.int32) << 8)
                     | (b[:, 2].astype(np.int32) << 16))
                v = np.where(v >= 2 ** 23, v - 2 ** 24, v)
                a = v.astype(np.float32) / float(2 ** 23)
            else:
                raise ValueError(f"wav width {width} unsupported")
            a = a.reshape(-1, ch).T
            if a.shape[0] == 1:
                a = np.vstack([a, a])
            yield sr, a


def streaming_lufs_wav(path):
    """streaming_lufs over a WAV file, block by block from disk."""
    from scipy.signal import lfilter, lfilter_zi
    states = {}
    sums = {}
    n_total = 0
    sr_seen = None
    for sr, blk in _wav_blocks(path):
        sr_seen = sr
        n_total += blk.shape[1]
        for ci in range(blk.shape[0]):
            if ci not in states:
                states[ci] = [
                    lfilter_zi(pipeline._K_PRE_B,
                               pipeline._K_PRE_A) * 0.0,
                    lfilter_zi(pipeline._K_RLB_B,
                               pipeline._K_RLB_A) * 0.0]
                sums[ci] = 0.0
            seg = blk[ci].astype(np.float64)
            y, states[ci][0] = lfilter(
                pipeline._K_PRE_B, pipeline._K_PRE_A, seg,
                zi=states[ci][0])
            y, states[ci][1] = lfilter(
                pipeline._K_RLB_B, pipeline._K_RLB_A, y,
                zi=states[ci][1])
            sums[ci] += float(np.sum(y * y))
    if sr_seen != SR:
        raise ValueError(f"decoded WAV at {sr_seen}, not {SR}")
    total = sum(s / n_total for s in sums.values())
    if total <= 0.0:
        return -120.0
    return float(-0.691 + 10.0 * math.log10(total))


# ---------------------------------------------------------------------
# 1. ASSEMBLE
# ---------------------------------------------------------------------

def assemble():
    script_files = sorted(SCRIPT_DIR.glob("*.txt"))
    if len(script_files) != 21:
        raise ValueError(f"expected 21 script chunks, found "
                         f"{len(script_files)}")
    parts = []
    chunks_meta = []
    total = 0
    for i, sf in enumerate(script_files):
        name = sf.stem
        raw_wav = CHUNK_DIR / f"{name}.wav"
        if not raw_wav.exists():
            raise FileNotFoundError(f"rendered chunk missing: {raw_wav}")
        conv = HERE / f".conv-{name}.wav"
        _ffmpeg(["-i", str(raw_wav), "-ar", str(SR), "-ac", "1",
                 str(conv)], f"chunk {name} to 48k")
        x, sr = pipeline.read_wav_pcm(conv)
        conv.unlink()
        if sr != SR:
            raise ValueError(f"chunk {name} at {sr}, not {SR}")
        x = np.asarray(x, dtype=np.float32).ravel()
        gap = 0.0
        if i > 0:
            gap = GAPS_BEFORE.get(name[:2], GAP_DEFAULT)
            parts.append(np.zeros(int(gap * SR), dtype=np.float32))
            total += int(gap * SR)
        parts.append(x)
        total += x.shape[0]
        chunks_meta.append({
            "chunk": name,
            "script_file": sf.name,
            "words": len(sf.read_text(encoding="utf-8").split()),
            "rendered_seconds": round(_probe_duration(raw_wav), 3),
            "assembled_seconds": round(x.shape[0] / SR, 3),
            "gap_before_seconds": gap,
        })
        print(f"assemble: {name} {x.shape[0] / SR:.2f}s "
              f"(gap {gap:.1f}s)")
    program = np.concatenate(parts) if parts else np.zeros(0, np.float32)
    _write_wav24_mono(ASSEMBLED, program)
    meta = {"chunks": chunks_meta,
            "total_seconds": round(total / SR, 3),
            "sample_rate": SR}
    MANIFEST.write_text(json.dumps(
        {"assemble": meta}, indent=2) + "\n", encoding="utf-8")
    print(f"assemble: program {total / SR:.2f}s -> {ASSEMBLED}")
    return meta


# ---------------------------------------------------------------------
# 2. MASTER (master_signal's law, applied in blocks for long-form)
# ---------------------------------------------------------------------

def _block_windows(n, block):
    start = 0
    while start < n:
        end = min(n, start + block)
        yield start, end
        start = end


def master():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    x32, sr = pipeline.read_wav_pcm(ASSEMBLED)
    if sr != SR:
        raise ValueError(f"assembled at {sr}, not {SR}")
    mono = np.asarray(x32, dtype=np.float64).ravel()
    n = mono.shape[0]
    del x32
    # The working stereo body lives on disk (dual mono), so the
    # chain's float64 arithmetic never has to fit in RAM whole.
    work_path = HERE / ".master-work.npy"
    work = np.lib.format.open_memmap(work_path, mode="w+",
                                     dtype=np.float64, shape=(2, n))
    block = int(60 * SR)
    for s, e in _block_windows(n, block):
        work[0, s:e] = mono[s:e]
        work[1, s:e] = mono[s:e]
    del mono
    # Head and tail fades, as run 2 struck them: 5 ms in, 2.0 s out.
    head = int(pipeline.HEAD_FADE_S * SR)
    tail = int(pipeline.END_FADE_S * SR)
    for ch in (0, 1):
        work[ch, :head] *= np.linspace(0.0, 1.0, head)
        work[ch, -tail:] *= np.linspace(1.0, 0.0, tail)
    work.flush()
    scire = streaming_scire(work)
    print(f"master: scire {scire}")
    # ATTEMPT 2 STEERING (the calibration loop, run honestly):
    # attempt 1 was measured by the gate at decoded TP -0.88 dBTP
    # against the WAV's -1.02 -- the MP3 decode overshoots the
    # steered peak by +0.14 dB, and the gate (rightly) FAILED it
    # (proof pow-875cbecb..., standing in the ledger). Attempt 2
    # budgets the overshoot: the limiter and trim steer to
    # -1.30 dBTP, and the gain pre-compensates +0.38 dB for the
    # lower ceiling's extra limiting cost (attempt 1's transfer:
    # limiting + trim cost 0.34 LU at the -1.0 ceiling), aiming
    # post-limit loudness at the middle of the gate's band.
    STEER_DBTP = proofs.CEILING_DBTP - 0.30
    GAIN_PRECOMP_DB = 0.38
    gain_db = (proofs.TARGET_LUFS + GAIN_PRECOMP_DB
               - scire["lufs_integrated"])
    gain = 10.0 ** (gain_db / 20.0)
    for s, e in _block_windows(n, block):
        seg = np.asarray(work[:, s:e]) * gain
        work[:, s:e] = pipeline.soft_limit(seg, STEER_DBTP)
    work.flush()
    tp = block_true_peak(work, SR)
    trim_db = 0.0
    if tp > STEER_DBTP:
        trim_db = STEER_DBTP - tp - 0.02
        factor = 10.0 ** (trim_db / 20.0)
        for s, e in _block_windows(n, block):
            work[:, s:e] = np.asarray(work[:, s:e]) * factor
        work.flush()
        tp = block_true_peak(work, SR)
    lufs_after = streaming_lufs(work, SR)
    sample_peak = 0.0
    for s, e in _block_windows(n, block):
        sample_peak = max(sample_peak,
                          float(np.max(np.abs(np.asarray(work[:, s:e])))))
    report = {
        "lufs_before": scire["lufs_integrated"],
        "gain_applied_db": round(gain_db, 2),
        "trim_db": round(trim_db, 2),
        "lufs_after": round(lufs_after, 2),
        "sample_peak_db": round(20.0 * math.log10(sample_peak), 2)
        if sample_peak > 0 else -120.0,
        "true_peak_dbtp": round(tp, 2),
        "ceiling_overrode_loudness": bool(trim_db < 0.0),
        "target_lufs": proofs.TARGET_LUFS,
        "ceiling_dbtp": proofs.CEILING_DBTP,
        "attempt": 2,
        "steering_ceiling_dbtp": STEER_DBTP,
        "decode_overshoot_budget_db": 0.30,
        "gain_precompensation_db": GAIN_PRECOMP_DB,
        "prior_attempt": "master proof pow-875cbecbf6a46800a2ec84"
                          "e4ee69200607ff96224a5c5eedb7772824c63c"
                          "966d FAILED at the gate: decoded true "
                          "peak -0.88 dBTP vs the WAV's steered "
                          "-1.02 (MP3 decode overshoot +0.14 dB); "
                          "loudness and bitrate passed. That "
                          "record stands; this attempt answers it.",
        "longform_note": "master_signal's law applied in blocks: "
                         "gain and soft-limit are sample-local; "
                         "loudness on the pipeline's own scale "
                         "(its ungated K-weighted figure, its own "
                         "biquad coefficients) computed in the time "
                         "domain in blocks -- the whole-signal FFT "
                         "form and four_powers' whole-body RMS "
                         "witness OOM-kill on the 64-minute form in "
                         "this box, and the blocked form was "
                         "validated against the whole-signal scale "
                         "at delta 0.0000 LU on two 90 s slices of "
                         "this program; true peak by the pipeline's "
                         "oversampling in 120 s windows with 5 s "
                         "overlaps.",
    }
    print(f"master: report {report}")
    # Tacere: TPDF dither at the 24-bit strike, per block, seeded
    # from the house seed -- the same triangular law, blocked.
    import wave
    lsb = 2.0 ** (-(fp.EXPORT_BITS - 1))
    with wave.open(str(MASTER_WAV), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(SR)
        for bi, (s, e) in enumerate(_block_windows(n, block)):
            rng = np.random.default_rng(SEED * 100000 + bi)
            seg = np.asarray(work[:, s:e], dtype=np.float64)
            noise = (rng.random(seg.shape) + rng.random(seg.shape)
                     - 1.0) * lsb
            ints = np.clip(np.round((seg + noise) * (2 ** 23)),
                           -(2 ** 23), 2 ** 23 - 1).astype(np.int32)
            frames = ints.T.copy()
            raw = frames.view(np.uint8).reshape(-1, 2, 4)[:, :, :3]
            w.writeframes(np.ascontiguousarray(raw).tobytes())
    del work
    work_path.unlink()
    tacere = fp.tacere_report(report, True)
    four = fp.assemble(
        scire,
        {"engaged": False, "eq": [], "comp": None,
         "rms_delta_db": 0.0, "peak_delta_db": 0.0},
        {"engaged": False, "drive_db": 0.0,
         "crest_before_db": scire["crest_db"],
         "crest_after_db": scire["crest_db"], "rms_delta_db": 0.0},
        report, tacere)
    _ffmpeg(["-i", str(MASTER_WAV), "-codec:a", "libmp3lame",
             "-b:a", "320k", str(MP3_OUT)], "audiobook mp3")
    print(f"master: -> {MASTER_WAV} + {MP3_OUT}")
    manifest["master"] = {"report": report, "four_powers": four,
                          "scire": scire}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n",
                        encoding="utf-8")
    return report, four


# ---------------------------------------------------------------------
# 3. PROOFS
# ---------------------------------------------------------------------

def _measure_master_subprocess():
    """proofs.measure_master in a subprocess (memory isolation)."""
    code = (
        "import json, sys\n"
        "sys.path.insert(0, {repo!r})\n"
        "from resonance.studio import proofs\n"
        "m = proofs.measure_master({mp3!r}, {wav!r})\n"
        "print(json.dumps(m))\n"
    ).format(repo=str(REPO), mp3=str(MP3_OUT), wav=str(MASTER_WAV))
    proc = subprocess.run([sys.executable, "-c", code],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return None, proc.stderr.strip()[-500:]
    return json.loads(proc.stdout.strip().splitlines()[-1]), ""


def _measure_master_blocked():
    """The gate's scales in blocks, if the whole-signal scales
    cannot carry the long form (confessed wherever used)."""
    decoded = HERE / ".decoded-master.wav"
    _ffmpeg(["-i", str(MP3_OUT), "-ar", str(SR), str(decoded)],
            "decode delivered mp3")
    lufs = streaming_lufs_wav(decoded)
    tp = streaming_tp_wav(decoded)
    sr = SR
    body = {"bitrate_bps": proofs._ffprobe_bitrate_bps(MP3_OUT),
            "sworn_bitrate_bps": proofs.SWORN_BITRATE_BPS,
            "lufs_integrated": round(lufs, 2),
            "true_peak_dbtp": round(tp, 2),
            "measurement_note": "proofs.measure_master could not "
                                "carry the long form in this box's "
                                "memory; the measured body was "
                                "computed by the same scales in "
                                "blocks (the pipeline's ungated "
                                "K-weighted loudness, its own "
                                "biquad coefficients, applied in "
                                "the time domain over the decoded "
                                "MP3 -- validated at delta 0.0000 "
                                "LU against the whole-signal scale; "
                                "the pipeline's oversampled true "
                                "peak in 120 s windows, 5 s "
                                "overlaps).",
            "files": {"delivered_mp3": {
                "path": str(MP3_OUT), "decoded_sr": sr,
                "lufs_integrated": round(lufs, 2),
                "true_peak_dbtp": round(tp, 2),
                "bitrate_bps": proofs._ffprobe_bitrate_bps(MP3_OUT)}}}
    decoded.unlink()
    return body


def seal():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    asm = manifest["assemble"]
    vocal_manifest = {
        "title": "THE PIRATE ESSAY -- audiobook narration render",
        "label": "spoken narration render: the founder's stamped "
                 "essay read by the house speech seat; speech, "
                 "not sung performance",
        "engine": "ZONOS3-Mini via llama.cpp llama-tts b12438 "
                  "(ggml-org pair: ZONOS3-Mini-Q8_0.gguf + "
                  "mmproj-ZONOS3-Mini-F32.gguf), CPU on this box",
        "voice": VOICE + " (predefined voice shipping inside the "
                         "model's own release; no cloned voice)",
        "source_text": {
            "path": str(SOURCE_MD),
            "sha256": proofs.sha256_file(SOURCE_MD)},
        "narration_script": {
            "files": [c["script_file"] for c in asm["chunks"]],
            "words_total": sum(c["words"] for c in asm["chunks"]),
            "sha256": proofs.sha256_file(HERE / "NARRATION-SCRIPT.md")
            if (HERE / "NARRATION-SCRIPT.md").exists() else None},
        "chunks": asm["chunks"],
        "total_seconds": asm["total_seconds"],
        "assembled_sample_rate": SR,
        "render_sample_rate": 44100,
    }
    # The narration render does not change between master
    # attempts: if a vocal proof already stands in the ledger for
    # this exact assembled artifact (same SHA-256), it is reused
    # as the parent rather than re-stamped as a duplicate.
    asm_sha = proofs.sha256_file(ASSEMBLED)
    vocal = None
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if (rec.get("kind") == "vocal"
                    and rec.get("artifact", {}).get("sha256")
                    == asm_sha):
                vocal = rec
    if vocal is not None:
        print(f"proof of work (vocal): {vocal['id']} "
              f"({vocal['status']}) -- standing record reused; "
              f"the narration was not re-rendered")
    else:
        vocal = proofs.append_proof("vocal", ASSEMBLED,
                                    vocal_manifest, parents=(),
                                    ledger_path=LEDGER)
        print(f"proof of work (vocal): {vocal['id']} "
              f"({vocal['status']})")
    measured, err = _measure_master_subprocess()
    measure_path = "proofs.measure_master (subprocess)"
    if measured is None:
        print(f"measure_master subprocess failed: {err}")
        measured = _measure_master_blocked()
        measure_path = "blocked scales (confessed in manifest)"
    body = {"title": "THE PIRATE ESSAY -- audiobook "
                     "(SPOKEN-WORD master)",
            "label": "spoken-word audiobook master: one narrated "
                     "stem (ZONOS3-Mini speech seat) mastered to "
                     "house law; narration, not a sung performance, "
                     "no backing, no mix",
            "four_powers": manifest["master"]["four_powers"],
            "master_report": manifest["master"]["report"],
            "measurement_path": measure_path}
    rec = proofs.append_master_proof(MP3_OUT, body, measured,
                                     parents=[vocal["id"]],
                                     ledger_path=LEDGER)
    print(f"proof of mastering: {rec['id']} ({rec['status']})")
    verdict = proofs.verify_ledger(LEDGER)
    print(f"ledger verify: {json.dumps(verdict)}")
    manifest["proofs"] = {
        "vocal_proof_id": vocal["id"],
        "master_proof_id": rec["id"],
        "master_status": rec["status"],
        "master_gate": rec.get("gate"),
        "measured": measured,
        "measurement_path": measure_path,
        "ledger_verify": verdict}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n",
                        encoding="utf-8")
    return vocal, rec, verdict


# ---------------------------------------------------------------------
# 4. VIDEO
# ---------------------------------------------------------------------

def video():
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1920, 1080
    purple = (0x4B, 0x00, 0x82)
    gold = (0xFF, 0xD7, 0x00)
    frame = Image.new("RGB", (W, H), purple)
    cover = Image.open(COVER).convert("RGB")
    ch = 880
    cw = int(cover.width * ch / cover.height)
    cover = cover.resize((cw, ch))
    cx, cy = 150, (H - ch) // 2
    frame.paste(cover, (cx, cy))
    seal = Image.open(SEAL).convert("RGB")
    ss = 300
    seal = seal.resize((ss, ss))
    tx = cx + cw + 110
    frame.paste(seal, (tx, 90))
    draw = ImageDraw.Draw(frame)
    fdir = "/usr/share/fonts/truetype/liberation"
    f_title = ImageFont.truetype(f"{fdir}/LiberationSans-Bold.ttf", 92)
    f_sub = ImageFont.truetype(f"{fdir}/LiberationSans-Regular.ttf", 52)
    f_line = ImageFont.truetype(f"{fdir}/LiberationSans-Regular.ttf", 40)
    f_small = ImageFont.truetype(f"{fdir}/LiberationSans-Regular.ttf", 34)
    y = 450
    draw.text((tx, y), "THE PIRATE ESSAY", font=f_title, fill=gold)
    y += 120
    draw.text((tx, y), "The Seventy-Seven Trinities", font=f_sub,
              fill=(255, 255, 255))
    y += 110
    draw.text((tx, y), "AUDIOBOOK", font=f_sub, fill=gold)
    y += 80
    draw.text((tx, y), "Narrated in house by the speech seat\n"
                       "of RESONANTIA (ZONOS3-Mini)", font=f_line,
              fill=(255, 255, 255))
    y += 130
    draw.text((tx, y), "Johnathan 'Qasparr' Monroe", font=f_small,
              fill=(230, 230, 230))
    frame_path = HERE / "video-frame.png"
    frame.save(frame_path)
    audio_note = "stream-copied from the sealed master"
    proc = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate",
         "30", "-i", str(frame_path), "-i", str(MP3_OUT),
         "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt",
         "yuv420p", "-c:a", "copy", "-shortest", str(VIDEO_OUT)],
        capture_output=True, text=True)
    if proc.returncode != 0:
        audio_note = ("RE-ENCODED as AAC at 320 kbps (the MP3 "
                      "stream could not be copied into the MP4 "
                      "container on this ffmpeg); the video is an "
                      "edition of the master, not a new master")
        _ffmpeg(["-loop", "1", "-framerate", "30", "-i",
                 str(frame_path), "-i", str(MP3_OUT), "-c:v",
                 "libx264", "-tune", "stillimage", "-pix_fmt",
                 "yuv420p", "-c:a", "aac", "-b:a", "320k",
                 "-shortest", str(VIDEO_OUT)], "video edition (aac)")
    dur_mp3 = _probe_duration(MP3_OUT)
    dur_mp4 = _probe_duration(VIDEO_OUT)
    info = {"video": str(VIDEO_OUT),
            "bytes": VIDEO_OUT.stat().st_size,
            "duration_seconds": round(dur_mp4, 3),
            "master_duration_seconds": round(dur_mp3, 3),
            "duration_delta_seconds": round(abs(dur_mp4 - dur_mp3), 3),
            "audio": audio_note,
            "frame": "1920x1080: bookshop front cover on doctrine "
                     "purple #4B0082, TVRRIS VERITATIS seal, title"}
    print(f"video: {json.dumps(info)}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["video"] = info
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n",
                        encoding="utf-8")
    return info


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    t0 = time.time()
    if phase in ("assemble", "all"):
        assemble()
    if phase in ("master", "all"):
        master()
    if phase in ("proofs", "all"):
        seal()
    if phase in ("video", "all"):
        video()
    print(f"phase {phase} done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()

# 93 -- Live, Love, and let Love, Live.
