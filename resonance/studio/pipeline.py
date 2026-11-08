# 93
# ---------------------------------------------------------------------
# pipeline.py -- the proven road, paved: compose, voice, ground, master.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: produce(spec) walks the architecture the house proved by
# ear and by FFT (2026-10-26 / 2026-11-02): RESONANTIA composes and
# grounds (the Sigma binaural layer, struck by resonance.binaural),
# local MusicGen voices the bed (rendered by the venv bridge,
# render_musicgen.py -- the system interpreter has no torch), and a
# mastering chain finishes: K-weighted loudness to target, then a
# true-peak ceiling that outranks the loudness when the two fight.
# Everything the run claims, the manifest measures: durations, peaks,
# loudness before/after, and the Sigma separation as found by FFT on
# the sigma-only render -- never as merely intended.
#
# DOCTRINE: a claim you cannot measure is a wish. This module's whole
# shape -- spec in, manifest out, every number weighed -- exists so
# the words "studio grade" are a measurement, not a mood. The Stereo
# Law (VIII day of November) rides the same doctrine: MusicGen's bed
# is born mono, so width is MANUFACTURED honestly -- spine panned by
# role, bed widened by band with the lows kept mono and the mid
# preserved exactly, Sigma untouched -- and the correlations are
# measured into the manifest, never asserted.
# ---------------------------------------------------------------------

import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from resonance import grid
from resonance.binaural.generator import binaural_beat
from resonance.studio import spine as spine_mod

TARGET_SR = 48000            # The master's sample rate, full stop.
CROSSFADE_S = 2.0            # Equal-power overlap between sections.
END_FADE_S = 2.0             # A record ends; it does not stop.
HEAD_FADE_S = 0.005          # 5 ms: no click at the needle drop.
VENV_PYTHON = os.environ.get(
    "RESONANTIA_MUSICGEN_PYTHON",
    "/home/hatch/workspace/musicgen-venv/bin/python")
RENDER_SCRIPT = str(Path(__file__).with_name("render_musicgen.py"))

# BS.1770 K-weighting, the standard 48 kHz coefficient set (stage 1:
# the shelf "pre-filter"; stage 2: the RLB high-pass). These constants
# are the published 48 kHz values; the loudness function refuses other
# sample rates rather than quietly mis-weigh at them.
_K_PRE_B = (1.53512485958697, -2.69169618940638, 1.19839281085285)
_K_PRE_A = (1.0, -1.69065929318241, 0.73248077421585)
_K_RLB_B = (1.0, -2.0, 1.0)
_K_RLB_A = (1.0, -1.99004745483398, 0.99007225036621)

DEFAULTS = {
    "title": "Untitled",
    "seed": 93,
    "sigma": {"left_hz": 200.0, "right_hz": 213.0, "gain_db": -28.0},
    "master": {"target_lufs": -14.0, "ceiling_dbtp": -1.0},
}

# The Stereo Law's bed constants (part 2; part 1 is the spine's
# pans, part 3 is Sigma left untouched). Below STEREO_LOW_CUT_HZ the
# bed stays fully mono -- lows are summed by every club system on
# earth and the 808's throne is not negotiable. The synthesized
# side's ratio to the mid ramps up in log-frequency and reaches
# STEREO_MAX_SIDE at STEREO_RAMP_END_HZ, holding above it.
STEREO_LOW_CUT_HZ = 180.0
STEREO_RAMP_END_HZ = 2000.0
STEREO_MAX_SIDE = 0.75


# ---------------------------------------------------------------------
# Spec: the contract an operator -- or an agent -- speaks to the mill.
# ---------------------------------------------------------------------

def validate_spec(spec):
    """Validate a produce() spec and return a normalized copy.

    MECHANISM: every field is checked against the range where the
    machinery stays honest (a section is 3-30 s because MusicGen's
    token budget and attention stay musical there; the Sigma pair
    must ascend and sit well under Nyquist; the ceiling must be a
    ceiling). Defaults fill what the spec leaves open. Raises
    ValueError with the offending field named -- an agent reading the
    error must be able to fix the spec without asking a human.
    """
    if not isinstance(spec, dict):
        raise ValueError("spec: must be a JSON object (dict)")
    out = dict(spec)
    out["title"] = str(spec.get("title", DEFAULTS["title"]))
    base = spec.get("prompt_base")
    if not isinstance(base, str) or not base.strip():
        raise ValueError("prompt_base: required, a non-empty string")
    out["prompt_base"] = base.strip()
    sections = spec.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValueError("sections: required, a non-empty list")
    norm_sections = []
    for i, sec in enumerate(sections):
        if not isinstance(sec, dict):
            raise ValueError(f"sections[{i}]: must be an object")
        seconds = float(sec.get("seconds", 30))
        if not 3.0 <= seconds <= 30.0:
            raise ValueError(
                f"sections[{i}].seconds: {seconds} outside 3..30")
        norm_sections.append({
            "name": str(sec.get("name", f"section{i + 1}")),
            "prompt_suffix": str(sec.get("prompt_suffix", "")),
            "seconds": seconds,
        })
    out["sections"] = norm_sections
    out["seed"] = int(spec.get("seed", DEFAULTS["seed"]))
    sigma = dict(DEFAULTS["sigma"])
    sigma.update(spec.get("sigma") or {})
    left, right = float(sigma["left_hz"]), float(sigma["right_hz"])
    if not (20.0 <= left < right <= 1000.0):
        raise ValueError(
            f"sigma: need 20 <= left_hz < right_hz <= 1000, "
            f"got {left}/{right}")
    if not -60.0 <= float(sigma["gain_db"]) <= 0.0:
        raise ValueError(f"sigma.gain_db: {sigma['gain_db']} outside -60..0")
    sigma.update(left_hz=left, right_hz=right,
                 gain_db=float(sigma["gain_db"]))
    out["sigma"] = sigma
    master = dict(DEFAULTS["master"])
    master.update(spec.get("master") or {})
    if not -30.0 <= float(master["target_lufs"]) <= -6.0:
        raise ValueError(
            f"master.target_lufs: {master['target_lufs']} outside -30..-6")
    if not -3.0 <= float(master["ceiling_dbtp"]) <= -0.1:
        raise ValueError(
            f"master.ceiling_dbtp: {master['ceiling_dbtp']} outside -3..-0.1")
    master.update(target_lufs=float(master["target_lufs"]),
                  ceiling_dbtp=float(master["ceiling_dbtp"]))
    out["master"] = master
    # The optional rhythmic spine: absent is the Proof No. 1 road,
    # unchanged. Present, it is normalized by its own validator,
    # whose refusals name their fields the same way.
    if spec.get("spine") is not None:
        out["spine"] = spine_mod.normalize_spine_spec(spec["spine"])
    else:
        out.pop("spine", None)
    # The Stereo Law's width: how far the mono bed is widened
    # (widen_bed). The law defaults ON for spine productions -- a
    # spined record ships stereo or says why not -- and OFF on the
    # Proof No. 1 road, whose dual-mono bed stays as it was proved.
    # An explicit "stereo": {"width": w} always outranks the default.
    stereo_raw = spec.get("stereo")
    if stereo_raw is None:
        width = 1.0 if out.get("spine") else 0.0
    else:
        if not isinstance(stereo_raw, dict):
            raise ValueError("stereo: must be an object")
        width = float(stereo_raw.get(
            "width", 1.0 if out.get("spine") else 0.0))
    if not 0.0 <= width <= 1.0:
        raise ValueError(f"stereo.width: {width} outside 0..1")
    out["stereo"] = {"width": width}
    if not spec.get("out_dir"):
        raise ValueError("out_dir: required")
    out["out_dir"] = str(spec["out_dir"])
    return out


def _full_prompt(spec, section):
    """prompt_base + section suffix: one voice, many arrangements."""
    suffix = section["prompt_suffix"].strip()
    return f"{spec['prompt_base']}, {suffix}" if suffix else spec["prompt_base"]


# ---------------------------------------------------------------------
# WAV I/O on the system side: stdlib wave + numpy, PCM int only.
# (The float masters cross to the venv for their final 24-bit write;
#  ffmpeg strikes the preview. Each tool does the job it is best at.)
# ---------------------------------------------------------------------

def read_wav_pcm(path):
    """Read a PCM WAV (16/24/32-bit int) -> (float32 (2, N) or (N,), sr).

    MECHANISM: the stdlib wave module frames the file; numpy unpacks.
    24-bit needs the manual sign extension below -- a 3-byte little-
    endian sample whose top bit is the sign, extended to int32 before
    scaling. Float WAVs are refused: on this side of the bridge, WAV
    means PCM, and a surprise should be loud, not silent.
    """
    import wave
    with wave.open(str(path), "rb") as w:
        channels, width, sr, frames = (w.getnchannels(), w.getsampwidth(),
                                       w.getframerate(), w.getnframes())
        raw = w.readframes(frames)
    if width == 2:
        data = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    elif width == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        vals = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        vals = np.where(vals >= 1 << 23, vals - (1 << 24), vals)
        data = vals.astype(np.float32) / 8388608.0
    elif width == 4:
        data = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
    elif width == 1:
        data = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
                - 128.0) / 128.0
    else:
        raise ValueError(f"{path}: unsupported sample width {width}")
    data = data.reshape(-1, channels).T
    return (data if channels == 2 else data[0]), sr


# ---------------------------------------------------------------------
# Measurement: K-weighted loudness and true peak -- the scales.
# ---------------------------------------------------------------------

def _biquad_response(b, a, freqs, sr):
    """|H(e^jw)| of a biquad at the given frequencies (exact, analytic).

    MECHANISM: filtering for a *measurement* is done in the frequency
    domain -- multiply the signal's spectrum by H and take the mean
    square from Parseval -- because a pure-Python time-domain biquad
    loop over twelve million samples would take minutes to weigh one
    song. The response itself is the textbook z-transform ratio.
    """
    w = 2j * np.pi * freqs / sr
    z = np.exp(w)
    num = b[0] + b[1] * z ** -1 + b[2] * z ** -2
    den = a[0] + a[1] * z ** -1 + a[2] * z ** -2
    return num / den


def _fast_len(n):
    """Smallest m >= n whose prime factors are all in {2, 3, 5, 7}.

    MECHANISM: pocketfft is fast and lean on smooth lengths, but a
    length with a large prime factor (the 10,066,019-sample spine
    grid of Pipeline Proof No. 2 is 23 x 437653) falls back to
    Bluestein's algorithm -- multiple half-gigabyte chirp buffers
    and minutes of compute, which on a shared box reads as a hang
    and ends as an OOM kill. Zero-padding a measurement transform
    up to the next smooth length changes none of the physics (the
    padded spectrum is the same spectrum, interpolated); it only
    changes which algorithm carries it. Every measurement FFT in
    this module therefore runs at a fast length.
    """
    m = int(n)
    while True:
        r = m
        for p in (2, 3, 5, 7):
            while r % p == 0:
                r //= p
        if r == 1:
            return m
        m += 1


def measure_loudness_lufs(samples, sr):
    """K-weighted integrated loudness (LUFS), ungated, stereo or mono.

    MECHANISM: BS.1770's two K-weighting stages are applied per
    channel in the frequency domain; the loudness is
    -0.691 + 10*log10(sum of channel mean-squares), L/R weighted 1.0.
    The published coefficients are the 48 kHz set, so other sample
    rates are refused rather than mis-weighed. Gating (the -70 LUFS
    absolute / -10 LU relative gates of BS.1770-4) is NOT applied --
    a stated simplification, recorded in every manifest: for program
    material at album loudness the gates move the number by tenths
    at most, and an honest ungated figure beats a gated fiction.
    """
    if sr != TARGET_SR:
        raise ValueError(
            f"measure_loudness_lufs: coefficients are the 48 kHz set, "
            f"got sr={sr}")
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim == 1:
        x = x[np.newaxis, :]
    n = x.shape[1]
    # The transform runs at the next fast length (see _fast_len):
    # zero-padding interpolates the same spectrum onto a grid the
    # FFT can carry cheaply. Parseval bookkeeping follows the pad:
    # sum|H*X_pad|^2 / (n_pad * n) is the filtered mean square over
    # the original n samples. The K-weight response is evaluated in
    # blocks so no full-length complex temporaries ever exist.
    n_pad = _fast_len(n)
    n_bins = n_pad // 2 + 1
    weight = np.empty(n_bins, dtype=np.float64)
    block = 1 << 18
    for lo in range(0, n_bins, block):
        hi = min(n_bins, lo + block)
        freqs = np.fft.rfftfreq(n_pad, d=1.0 / sr)[lo:hi]
        h = (_biquad_response(_K_PRE_B, _K_PRE_A, freqs, sr)
             * _biquad_response(_K_RLB_B, _K_RLB_A, freqs, sr))
        weight[lo:hi] = np.abs(h) ** 2
    total = 0.0
    for ch in x:
        spectrum = np.fft.rfft(ch, n=n_pad)
        # Parseval: mean square of the filtered signal from its spectrum.
        ms = np.sum(weight * np.abs(spectrum) ** 2) / (n_pad * n)
        # rfft folds negative frequencies; restore their energy.
        ms *= 2.0  # endpoints negligible at song scale
        total += ms
        del spectrum
    if total <= 0.0:
        return -120.0
    return float(-0.691 + 10.0 * math.log10(total))


def true_peak_dbtp(samples, sr, oversample=4):
    """True peak (dBTP) via FFT-domain oversampling, per channel max.

    MECHANISM: intersample peaks hide between samples; zero-padding
    the spectrum by `oversample` reconstructs the band-limited signal
    on the finer grid, where the honest peak shows itself. float32
    keeps a 4x oversample of a full song inside this machine's RAM.
    """
    x = np.asarray(samples, dtype=np.float32)
    if x.ndim == 1:
        x = x[np.newaxis, :]
    peak = 0.0
    for ch in x:
        n = ch.shape[0]
        spectrum = np.fft.rfft(ch)
        # The oversampled reconstruction runs at the next fast
        # length at or beyond n * oversample (see _fast_len): the
        # interpolation is the same band-limited one, carried by
        # radix FFTs instead of Bluestein buffers. The amplitude
        # scale of an irfft over a zero-padded spectrum is the
        # length ratio, generalized here from `oversample`.
        up_len = _fast_len(n * oversample)
        padded = np.zeros(up_len // 2 + 1, dtype=spectrum.dtype)
        padded[:spectrum.shape[0]] = spectrum
        up = np.fft.irfft(padded, n=up_len) * (up_len / n)
        peak = max(peak, float(np.max(np.abs(up))) if up.size else 0.0)
        del spectrum, padded, up
    return 20.0 * math.log10(peak) if peak > 0.0 else -120.0


def soft_limit(samples, ceiling_dbtp):
    """Soft limiter: linear below the knee, tanh approach to ceiling.

    MECHANISM: below T = 0.85 * ceiling the signal passes untouched --
    a limiter that works on quiet samples is a distortion box. Above
    T, a tanh curve bends the excess toward the ceiling value
    asymptotically, so the limiter alone can never quite reach it;
    the caller's true-peak trim then takes the last fraction of a dB
    with pure gain, which no waveform can argue with.
    """
    ceiling = 10.0 ** (ceiling_dbtp / 20.0)
    knee = 0.85 * ceiling
    x = np.asarray(samples, dtype=np.float64)
    ax = np.abs(x)
    over = ax > knee
    if not np.any(over):
        return x
    bent = knee + (ceiling - knee) * np.tanh((ax[over] - knee)
                                             / (ceiling - knee))
    y = x.copy()
    y[over] = np.sign(x[over]) * bent
    return y


def master_signal(samples, sr, target_lufs, ceiling_dbtp):
    """Master a stereo (2, N) float signal. Returns (mastered, report).

    MECHANISM, in the order the law prescribes: measure loudness,
    gain to target (loudness first -- the song's intended weight),
    soft-limit, then measure the TRUE peak; if the ceiling would
    break, trim by pure gain until it holds (the ceiling is law --
    a clipped master is a broken promise at any loudness). The
    report carries every measured figure, including whether the
    ceiling overrode the loudness, so the manifest never has to lie.
    """
    x = np.asarray(samples, dtype=np.float64)
    lufs_before = measure_loudness_lufs(x, sr)
    gain_db = target_lufs - lufs_before
    y = x * (10.0 ** (gain_db / 20.0))
    y = soft_limit(y, ceiling_dbtp)
    tp = true_peak_dbtp(y, sr)
    trim_db = 0.0
    if tp > ceiling_dbtp:
        trim_db = ceiling_dbtp - tp - 0.02  # a hair under, for safety
        y = y * (10.0 ** (trim_db / 20.0))
        tp = true_peak_dbtp(y, sr)
    sample_peak = float(np.max(np.abs(y))) if y.size else 0.0
    report = {
        "lufs_before": round(lufs_before, 2),
        "gain_applied_db": round(gain_db, 2),
        "trim_db": round(trim_db, 2),
        "lufs_after": round(measure_loudness_lufs(y, sr), 2),
        "sample_peak_db": round(20.0 * math.log10(sample_peak), 2)
        if sample_peak > 0 else -120.0,
        "true_peak_dbtp": round(tp, 2),
        "ceiling_overrode_loudness": bool(trim_db < 0.0),
        "target_lufs": target_lufs,
        "ceiling_dbtp": ceiling_dbtp,
    }
    return y, report


# ---------------------------------------------------------------------
# The Sigma layer: resonance.binaural strikes the carriers; FFT judges.
# ---------------------------------------------------------------------

def sigma_layer(spec, seconds, sr=TARGET_SR):
    """The Sigma binaural ground for `seconds`, from the house engine.

    MECHANISM: resonance.binaural's binaural_beat takes (carrier,
    beat); the spec speaks (left, right), so carrier is their mean
    and beat their difference -- the same pair, in the engine's own
    tongue. Generated at unit working amplitude; the caller scales
    it against the bed's RMS, because "under the bed" is a relation,
    not an absolute.
    """
    left = spec["sigma"]["left_hz"]
    right = spec["sigma"]["right_hz"]
    layer = binaural_beat(beat_hz=right - left,
                          carrier=(left + right) / 2.0,
                          duration=seconds, sample_rate=sr,
                          amplitude=0.5)
    return np.asarray(layer, dtype=np.float64)


def measure_carrier(samples_1d, sr, lo_hz, hi_hz):
    """FFT peak-pick: the dominant frequency inside [lo_hz, hi_hz].

    MECHANISM: the whole channel, one rfft, the largest magnitude in
    the band that brackets the intended carrier. For a pure tone
    running minutes long the peak bin sits within a fraction of a
    hertz of the truth -- this is the Nov 2 proof standard: report
    the measured separation, never the intended one.
    """
    x = np.asarray(samples_1d, dtype=np.float64)
    n_pad = _fast_len(x.shape[0])
    spectrum = np.abs(np.fft.rfft(x, n=n_pad))
    freqs = np.fft.rfftfreq(n_pad, d=1.0 / sr)
    band = (freqs >= lo_hz) & (freqs <= hi_hz)
    idx = np.argmax(np.where(band, spectrum, 0.0))
    return float(freqs[idx])


# ---------------------------------------------------------------------
# The Stereo Law, part 2: the bed takes its width by band.
# (Part 1 is the spine's role pans in spine.py; part 3 is that the
#  Sigma layer is never passed through any of this.)
# ---------------------------------------------------------------------

def channel_correlation(samples):
    """Pearson correlation between the channels of a (2, N) signal.

    MECHANISM: the forensic number itself -- Proof No. 2's master
    read 0.9984, which is a mono record in a stereo coat. Mono or
    single-channel input reads 1.0 by definition.
    """
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim == 1 or x.shape[0] < 2:
        return 1.0
    a = x[0] - float(np.mean(x[0]))
    b = x[1] - float(np.mean(x[1]))
    den = float(np.sqrt(np.dot(a, a) * np.dot(b, b)))
    return float(np.dot(a, b) / den) if den > 0.0 else 1.0


def band_correlation(samples, sr, lo_hz, hi_hz):
    """Channel correlation inside [lo_hz, hi_hz) only.

    MECHANISM: by Parseval, the correlation of the band-limited
    channels is Re sum(A * conj(B)) / sqrt(sum|A|^2 * sum|B|^2)
    over the band's rfft bins -- the same number a brick-wall
    filter and a stopwatch would give, without the filter. The
    transform runs at a fast length (see _fast_len).
    """
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim == 1 or x.shape[0] < 2:
        return 1.0
    n = x.shape[1]
    n_pad = _fast_len(n)
    freqs = np.fft.rfftfreq(n_pad, d=1.0 / sr)
    band = (freqs >= lo_hz) & (freqs < hi_hz)
    if not np.any(band):
        return 1.0
    a = np.fft.rfft(x[0], n=n_pad)[band]
    b = np.fft.rfft(x[1], n=n_pad)[band]
    num = float(np.real(np.sum(a * np.conj(b))))
    den = float(np.sqrt(np.sum(np.abs(a) ** 2)
                        * np.sum(np.abs(b) ** 2)))
    return num / den if den > 0.0 else 1.0


def side_rms_dbfs(samples):
    """RMS of the stereo side (L-R)/2, in dBFS.

    MECHANISM: the width you can weigh. Proof No. 2's master read
    -46.5 dBFS against a -15.5 dBFS mid -- 31 dB of width missing.
    """
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim == 1 or x.shape[0] < 2:
        return -120.0
    side = 0.5 * (x[0] - x[1])
    rms = float(np.sqrt(np.mean(side ** 2))) if side.size else 0.0
    return 20.0 * math.log10(rms) if rms > 0.0 else -120.0


def stereo_side_ratio(freqs, width):
    """The synthesized side's ratio to the mid, per frequency.

    MECHANISM: 0 below STEREO_LOW_CUT_HZ (lows stay fully mono),
    then a smoothstep in log-frequency up to width *
    STEREO_MAX_SIDE at STEREO_RAMP_END_HZ, holding flat above.
    Smooth, monotone, deterministic -- no per-bin randomness, so a
    render is reproducible and the correlation bound is provable:
    at ratio k with a quadrature side, a band's channel correlation
    is (1 - k^2) / (1 + k^2).
    """
    f = np.asarray(freqs, dtype=np.float64)
    k = np.zeros(f.shape, dtype=np.float64)
    lo, hi = math.log(STEREO_LOW_CUT_HZ), math.log(STEREO_RAMP_END_HZ)
    ramp = (f >= STEREO_LOW_CUT_HZ) & (f < STEREO_RAMP_END_HZ)
    if np.any(ramp):
        t = (np.log(f[ramp]) - lo) / (hi - lo)
        k[ramp] = t * t * (3.0 - 2.0 * t)
    k[f >= STEREO_RAMP_END_HZ] = 1.0
    return k * (float(width) * STEREO_MAX_SIDE)


def widen_bed(bed, sr, width):
    """Widen a (2, N) bed per the Stereo Law; returns a new array.

    MECHANISM: mid/side surgery. The mid (L+R)/2 is preserved
    EXACTLY -- the mono fold-down of the widened bed is the
    original signal, sample for sample, so nothing the bed was
    proved on changes. The side keeps whatever it honestly had
    (zero, for MusicGen's dual-mono) and gains a synthesized side:
    the mid's own quadrature -- every widened frequency rotated
    +90 degrees -- scaled by stereo_side_ratio. A quadrature side
    decorrelates without combing any single channel (each channel
    keeps the mid's per-band energy profile, plus the side's), and
    below 180 Hz the ratio is 0, so the lows come out L == R,
    fully mono, untouched. The transform runs at a fast length
    (see _fast_len) and the result is cut back to the bed's exact
    length: widening moves no onset in time either.
    """
    x = np.asarray(bed, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x])
    if not 0.0 <= float(width) <= 1.0:
        raise ValueError(f"widen_bed width: {width} outside 0..1")
    if width == 0.0:
        return x.copy()
    mid = 0.5 * (x[0] + x[1])
    side = 0.5 * (x[0] - x[1])
    n = mid.shape[0]
    n_pad = _fast_len(n)
    spectrum = np.fft.rfft(mid, n=n_pad)
    freqs = np.fft.rfftfreq(n_pad, d=1.0 / sr)
    k = stereo_side_ratio(freqs, width)
    synth = np.fft.irfft(spectrum * (k * 1j), n=n_pad)[:n]
    side = side + synth
    return np.stack([mid + side, mid - side])


# ---------------------------------------------------------------------
# The venv bridge: two small JSON doors in a necessary wall.
# ---------------------------------------------------------------------

def _run_bridge(job, out_dir, log):
    """Execute render_musicgen.py in the venv; return its result dict."""
    job_path = Path(out_dir) / "bridge_job.json"
    job_path.write_text(json.dumps(job, indent=2), encoding="utf-8")
    env = dict(os.environ, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
               OMP_NUM_THREADS=str(os.cpu_count() or 1),
               MKL_NUM_THREADS=str(os.cpu_count() or 1))
    log_path = Path(out_dir) / "render.log"
    with open(log_path, "a", encoding="utf-8") as log_fh:
        proc = subprocess.run(
            [VENV_PYTHON, RENDER_SCRIPT, str(job_path)],
            stdout=subprocess.PIPE, stderr=log_fh, env=env, text=True)
    lines = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()]
    if not lines:
        raise RuntimeError(
            f"venv bridge produced no result (see {log_path})")
    result = json.loads(lines[-1])
    if not result.get("ok"):
        raise RuntimeError(f"venv bridge failed: {result.get('error')}")
    return result


def _ffmpeg(args, what):
    """Run ffmpeg, loudly. A failed encode is a failed run."""
    proc = subprocess.run(["ffmpeg", "-y", "-v", "error", *args],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg ({what}) failed: {proc.stderr.strip()}")


def _segment_file_ok(path, seconds):
    """True when a previously rendered segment file is whole.

    MECHANISM: this machine restarts under load, and a render can
    die mid-write; a survivor segment counts as landed only if its
    WAV header parses, its rate is MusicGen's native 32 kHz, and its
    frame count matches the brief within 2%. A truncated survivor is
    re-rendered, never trusted -- resume is a recovery, not a hope.
    """
    import wave
    try:
        with wave.open(str(path), "rb") as w:
            frames, sr = w.getnframes(), w.getframerate()
    except Exception:
        return False
    return sr == 32000 and abs(frames / sr - seconds) <= 0.02 * seconds


# ---------------------------------------------------------------------
# produce(): the road itself.
# ---------------------------------------------------------------------

def _dry_run_manifest(spec):
    """The manifest skeleton for --dry-run: the plan, weighed, unbuilt."""
    total_render = sum(s["seconds"] for s in spec["sections"])
    overlaps = CROSSFADE_S * max(0, len(spec["sections"]) - 1)
    planned = {
        "sections": [
            {"name": s["name"], "prompt": _full_prompt(spec, s),
             "seed": spec["seed"] + i, "seconds": s["seconds"]}
            for i, s in enumerate(spec["sections"])],
        "rendered_seconds_total": total_render,
        "program_seconds_after_crossfades": total_render - overlaps,
        "sample_rate": TARGET_SR,
        "sigma": spec["sigma"],
        "master": spec["master"],
    }
    if spec.get("spine"):
        sp = spec["spine"]
        planned["spine"] = {
            "bpm": sp["bpm"],
            "total_bars": spine_mod.total_bars(sp),
            "exact_samples": spine_mod.spine_samples(sp, TARGET_SR),
            "sections": sp["sections"],
        }
    if spec["stereo"]["width"] > 0.0 or spec.get("spine"):
        planned["stereo"] = {
            "bed_width": spec["stereo"]["width"],
            "spine_panned_by_role": bool(spec.get("spine")),
            "low_cut_hz": STEREO_LOW_CUT_HZ,
        }
    return {
        "title": spec["title"],
        "title_status": "working title",
        "dry_run": True,
        "spec": spec,
        "planned": planned,
        "files": {},
        "notes": ["dry run: spec validated, nothing rendered"],
    }


def produce(spec, dry_run=False, log=None):
    """Run the full pipeline for `spec`; return the manifest dict.

    MECHANISM: render (venv bridge) -> resample (ffmpeg) -> stitch
    (equal-power crossfades, per-section RMS matched to the median so
    nine separate dreams sit at one table) -> Sigma ground (house
    binaural engine, scaled to gain_db under the bed's RMS) -> fade
    the ends -> master (loudness, then ceiling) -> strike (24-bit
    master + sigma-only via the venv's soundfile; MP3 via ffmpeg)
    -> manifest (everything measured, nothing merely claimed).
    """
    log = log or (lambda msg: print(f"[studio] {msg}", file=sys.stderr,
                                    flush=True))
    spec = validate_spec(spec)
    out_dir = Path(spec["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "spec.json").write_text(json.dumps(spec, indent=2),
                                       encoding="utf-8")
    if dry_run:
        manifest = _dry_run_manifest(spec)
        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest

    t_start = time.time()
    sections = spec["sections"]

    # -- (a) render the bed, one model load for the whole song --------
    # Resume law: whole segments already on disk (see _segment_file_ok)
    # are not re-rendered -- a restarted run picks the song up where
    # the machine dropped it, and the manifest marks every resumed
    # segment as resumed. Nothing is silently inherited.
    import wave as _wave
    render_by_index = {}
    todo = []
    for i, s in enumerate(sections):
        seg_file = out_dir / f"seg{i:02d}.wav"
        if seg_file.exists() and _segment_file_ok(seg_file, s["seconds"]):
            with _wave.open(str(seg_file), "rb") as w:
                native_sr = w.getframerate()
            render_by_index[i] = {
                "index": i, "file": seg_file.name,
                "sample_rate": native_sr, "wall_seconds": None,
                "resumed": True}
            log(f"section {i} ({s['name']}) already rendered -- "
                f"resuming past it")
        else:
            todo.append(i)
    render_model = "facebook/musicgen-small"
    render_wall = 0.0
    if todo:
        job = {"out_dir": str(out_dir), "segments": [
            {"index": i, "prompt": _full_prompt(spec, sections[i]),
             "seconds": sections[i]["seconds"],
             "seed": spec["seed"] + i, "file": f"seg{i:02d}.wav"}
            for i in todo]}
        log(f"rendering {len(todo)} sections via the venv bridge...")
        render = _run_bridge(job, out_dir, log)
        render_model = render["model"]
        render_wall = render["wall_seconds"]
        for r in render["segments"]:
            render_by_index[r["index"]] = {**r, "resumed": False}

    # -- (b) resample to 48 kHz and stitch ----------------------------
    log("resampling and stitching...")
    bed = None
    seg_reports = []
    seg_rms = []
    arrays = []
    for i, s in enumerate(sections):
        src = out_dir / f"seg{i:02d}.wav"
        dst = out_dir / f"seg{i:02d}_48k.wav"
        _ffmpeg(["-i", str(src), "-ar", str(TARGET_SR), "-ac", "2",
                 "-c:a", "pcm_s24le", str(dst)], f"resample seg{i:02d}")
        arr, sr = read_wav_pcm(dst)
        assert sr == TARGET_SR
        if arr.ndim == 1:  # MusicGen-small is mono: dual it, honestly.
            arr = np.stack([arr, arr])
        arrays.append(np.asarray(arr, dtype=np.float64))
        seg_rms.append(float(np.sqrt(np.mean(arrays[-1] ** 2))))
    median_rms = float(np.median(seg_rms))
    for i, arr in enumerate(arrays):
        if seg_rms[i] > 0:
            gain = median_rms / seg_rms[i]
            gain = min(max(gain, 10 ** (-6 / 20)), 10 ** (6 / 20))
            arrays[i] = arr * gain  # +/-6 dB at most: match, don't force
    fade = int(CROSSFADE_S * TARGET_SR)
    bed = arrays[0]
    for nxt in arrays[1:]:
        t = np.linspace(0.0, 1.0, fade, dtype=np.float64)
        out_w = np.cos(t * np.pi / 2.0)
        in_w = np.sin(t * np.pi / 2.0)
        overlap = (bed[:, -fade:] * out_w + nxt[:, :fade] * in_w)
        bed = np.concatenate([bed[:, :-fade], overlap, nxt[:, fade:]],
                             axis=1)
    total_seconds = bed.shape[1] / TARGET_SR

    # -- (b1) the Stereo Law, part 2: the bed takes its width ---------
    # The stitched bed is dual-mono (MusicGen has no stereo to give).
    # Widening happens HERE -- after the stitch, before the spine --
    # so the spine's own pans and the Sigma ground are never passed
    # through it (parts 1 and 3 of the law). The correlations are
    # measured on the bed itself, before and after, and the low
    # band is weighed separately: it must come out still mono.
    stereo_width = spec["stereo"]["width"]
    stereo_report = None
    if stereo_width > 0.0 or spec.get("spine"):
        stereo_report = {
            "bed_width": stereo_width,
            "spine_panned_by_role": bool(spec.get("spine")),
            "low_cut_hz": STEREO_LOW_CUT_HZ,
        }
    if stereo_width > 0.0:
        corr_before = channel_correlation(bed)
        log(f"widening the bed (Stereo Law, width "
            f"{stereo_width:.2f})...")
        bed = widen_bed(bed, TARGET_SR, stereo_width)
        stereo_report.update({
            "bed_correlation_before": round(corr_before, 4),
            "bed_correlation_after": round(channel_correlation(bed), 4),
            "bed_low_band_correlation_after": round(
                band_correlation(bed, TARGET_SR, 20.0,
                                 STEREO_LOW_CUT_HZ), 4),
        })
    for i, s in enumerate(sections):
        r = render_by_index[i]
        seg_reports.append({
            "name": s["name"], "prompt": _full_prompt(spec, s),
            "seed": spec["seed"] + i, "seconds": s["seconds"],
            "native_sample_rate": r["sample_rate"],
            "file": r["file"], "wall_seconds": r["wall_seconds"],
            "resumed_from_disk": bool(r.get("resumed")),
            "rms_matched_from": round(seg_rms[i], 5),
        })

    # -- (b2) the rhythmic spine: the house engine owns the clock -----
    # When the spec carries a spine, the program is trimmed DOWN to
    # the spine's exact whole-bar length (never stretched, never
    # tempo-shifted -- a length trim, not surgery) and the spine is
    # mixed under the bed RMS-matched, so the drums the founder can
    # hold to a number are OURS, struck on the grid of resonance.grid.
    spine_report = None
    if spec.get("spine"):
        sp = spec["spine"]
        bar_float = grid.samples_per_bar(sp["bpm"], TARGET_SR,
                                         sp["beats_per_bar"])
        bars_wanted = spine_mod.total_bars(sp)
        bars_fit = int(bed.shape[1] // bar_float)
        bars_used = min(bars_wanted, bars_fit)
        if bars_used < 1:
            raise RuntimeError(
                "spine: the stitched bed is shorter than one bar at "
                f"{sp['bpm']} BPM -- cannot lay a spine on it")
        if bars_used < bars_wanted:
            sp = spine_mod.trim_spine_spec(sp, bars_used)
            log(f"spine: bed holds only {bars_used} whole bars; "
                f"schedule trimmed from {bars_wanted}")
        spine_len = spine_mod.spine_samples(sp, TARGET_SR)
        bed_trimmed = bed.shape[1] > spine_len
        if bed_trimmed:
            bed = bed[:, :spine_len]
        total_seconds = bed.shape[1] / TARGET_SR
        log(f"laying the spine: {bars_used} bars at {sp['bpm']} BPM, "
            f"{spine_len} samples exactly...")
        spine_arr = spine_mod.render_spine(sp, TARGET_SR)
        assert spine_arr.shape[1] == bed.shape[1]
        spine_rms = float(np.sqrt(np.mean(spine_arr ** 2)))
        if spine_rms > 0:
            b_rms = float(np.sqrt(np.mean(bed ** 2)))
            bed = bed + spine_arr * (b_rms / spine_rms)
        spine_report = {
            "bpm": sp["bpm"], "swing": sp["swing"],
            "root_midi": sp["root_midi"],
            "bars_scheduled": bars_wanted, "bars_used": bars_used,
            "exact_samples": spine_len,
            "bed_trimmed_to_grid": bool(bed_trimmed),
            "sections": sp["sections"],
            "engine": "resonance.studio.spine (resonance.synth "
                      "voices + grid arithmetic)",
        }

    # -- (c)+(d) the Sigma ground, laid under the bed ------------------
    log("laying the Sigma ground...")
    sigma = sigma_layer(spec, total_seconds)
    if sigma.shape[1] != bed.shape[1]:
        # Float round-trip through seconds can drift a frame; the bed
        # is the program, so the ground is cut (or padded) to fit it.
        if sigma.shape[1] > bed.shape[1]:
            sigma = sigma[:, :bed.shape[1]]
        else:
            sigma = np.pad(sigma, ((0, 0), (0, bed.shape[1]
                                            - sigma.shape[1])))
    bed_rms = float(np.sqrt(np.mean(bed ** 2)))
    sigma_rms = float(np.sqrt(np.mean(sigma ** 2)))
    scale = (bed_rms * 10 ** (spec["sigma"]["gain_db"] / 20.0)) / sigma_rms
    mix = bed + sigma * scale
    measured_left = measure_carrier(
        sigma[0], TARGET_SR,
        spec["sigma"]["left_hz"] - 30.0, spec["sigma"]["left_hz"] + 30.0)
    measured_right = measure_carrier(
        sigma[1], TARGET_SR,
        spec["sigma"]["right_hz"] - 30.0, spec["sigma"]["right_hz"] + 30.0)

    # -- fades: a record ends; it does not stop ------------------------
    head = int(HEAD_FADE_S * TARGET_SR)
    tail = int(END_FADE_S * TARGET_SR)
    mix[:, :head] *= np.linspace(0.0, 1.0, head)
    mix[:, -tail:] *= np.linspace(1.0, 0.0, tail)

    # -- (e) master: loudness first, ceiling is law --------------------
    log("mastering...")
    mastered, master_report = master_signal(
        mix, TARGET_SR, spec["master"]["target_lufs"],
        spec["master"]["ceiling_dbtp"])
    if stereo_report is not None:
        stereo_report.update({
            "master_correlation": round(channel_correlation(mastered), 4),
            "master_side_rms_dbfs": round(side_rms_dbfs(mastered), 2),
        })
    mastered32 = np.asarray(mastered, dtype=np.float32)
    sigma32 = np.asarray(sigma * scale, dtype=np.float32)

    # -- (f) strike the files ------------------------------------------
    master_npy = out_dir / "_master_float.npy"
    sigma_npy = out_dir / "_sigma_float.npy"
    np.save(master_npy, mastered32.T.copy())   # (frames, channels)
    np.save(sigma_npy, sigma32.T.copy())
    master_wav = out_dir / "master.wav"
    sigma_wav = out_dir / "sigma.wav"
    fin = _run_bridge({"finalize": [
        {"npy": str(master_npy), "out": str(master_wav),
         "sample_rate": TARGET_SR, "subtype": "PCM_24"},
        {"npy": str(sigma_npy), "out": str(sigma_wav),
         "sample_rate": TARGET_SR, "subtype": "PCM_24"},
    ]}, out_dir, log)
    master_npy.unlink()
    sigma_npy.unlink()
    preview = out_dir / "preview.mp3"
    _ffmpeg(["-i", str(master_wav), "-codec:a", "libmp3lame",
             "-b:a", "320k", str(preview)], "preview mp3")

    manifest = {
        "title": spec["title"],
        "title_status": "working title",
        "dry_run": False,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "pipeline": "resonance.studio v1 (proof-of-concept build)",
        "spec": spec,
        "sections": seg_reports,
        "render": {"model": render_model,
                   "wall_seconds_this_run": render_wall,
                   "resumed_segments":
                   [i for i in range(len(sections))
                    if render_by_index[i].get("resumed")],
                   "rendered_seconds_total":
                   sum(s["seconds"] for s in sections)},
        "program": {"seconds": round(total_seconds, 3),
                    "sample_rate": TARGET_SR, "channels": 2,
                    "bit_depth": 24},
        "spine": spine_report,
        "stereo": stereo_report,
        "sigma": {
            "intended_left_hz": spec["sigma"]["left_hz"],
            "intended_right_hz": spec["sigma"]["right_hz"],
            "measured_left_hz": round(measured_left, 2),
            "measured_right_hz": round(measured_right, 2),
            "measured_separation_hz":
                round(abs(measured_right - measured_left), 2),
            "gain_db": spec["sigma"]["gain_db"],
            "gain_reference": "relative to the bed's RMS level",
            "engine": "resonance.binaural.generator.binaural_beat",
        },
        "master": master_report,
        "files": {
            "master_wav": {"path": str(master_wav),
                           "bytes": master_wav.stat().st_size},
            "preview_mp3": {"path": str(preview),
                            "bytes": preview.stat().st_size},
            "sigma_wav": {"path": str(sigma_wav),
                          "bytes": sigma_wav.stat().st_size},
            "spec_json": str(out_dir / "spec.json"),
            "render_log": str(out_dir / "render.log"),
        },
        "wall_seconds_total": round(time.time() - t_start, 2),
        "notes": [
            "loudness is K-weighted integrated, UNGATED (BS.1770 "
            "gating omitted in the proof build, stated not hidden).",
            "section levels RMS-matched to the median section, "
            "clamped to +/-6 dB, before crossfading.",
            "2 s tail fade + 5 ms head fade applied before mastering.",
        ] + ([
            "musicgen-small renders mono; the bed is dual-mono by "
            "construction -- the stereo field is carried by the Sigma "
            "layer in this proof.",
        ] if stereo_report is None else [
            "stereo law: musicgen-small renders mono, and the "
            "stitched bed starts dual-mono; the Stereo Law answers "
            "in three parts -- the spine is panned by role (kick "
            "and 808 centered, hats and rim wide), the bed is "
            "widened by quadrature side synthesis above 180 Hz with "
            "the mid preserved exactly and the lows left fully "
            "mono, and the Sigma layer is never processed. The "
            "widths are measured in the stereo block, not claimed.",
        ]) + ([
            "spine: the rhythmic spine is RESONANTIA's own synthesis "
            "on the resonance.grid arithmetic -- whole bars, exact "
            "samples; the bed was trimmed in LENGTH to that grid, "
            "never tempo-shifted.",
        ] if spine_report else []),
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    log(f"done in {manifest['wall_seconds_total']}s -> {master_wav}")
    return manifest

# 93 -- Live, Love, and let Love, Live.
