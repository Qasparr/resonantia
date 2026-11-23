#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — studio/upscale.py — the UPSCALE seat: a master weighed
# at one sample rate, evaluated at a higher one. Polyphase
# resampling upward only, with the report that proves nothing was
# invented on the way.
#
# Epigraph: "The samples determine the waveform — all of it,
# everywhere between them." — the interpolation theorem, stated as
# this seat's working law (Whittaker–Shannon): a band-limited
# signal sampled above its Nyquist rate is not suggested by its
# samples but FIXED by them, so a higher rate is the same waveform
# read at more points, and no original beyond the samples is
# needed — or exists — for the reading.
#
# 93.
# Date: 23 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
#   Hypothesis (the founder's doctrine, stated XXIII Nov 2026):
#     that upscaling needs only the samples in hand — "you just
#     need the resonate values to upscale just as easy as down" —
#     because down and up are one resampling operation read in two
#     directions, and that NOTHING above the source Nyquist can be
#     recovered by it, since nothing above it was ever captured.
#   Method: scipy.signal.resample_poly under an exact rational
#     ratio (target/source reduced by gcd: 44100→96000 is 320/147,
#     44100→192000 is 640/147, 48000→96000 is 2/1), its Kaiser
#     window raised from scipy's default β=5.0 to β=10.0, every
#     result weighed on the house's own scales — true peak by
#     pipeline.true_peak_dbtp, the FFT-oversampled scale the
#     mastering chain itself swears by — and loudness by
#     pyloudnorm, whose coefficients follow the rate (the
#     pipeline's sworn LUFS scale carries the 48 kHz coefficient
#     set and refuses other rates by name, so it cannot weigh a
#     seat whose whole purpose is to leave one rate for another).
#   Observation (bench probes, XXIII Nov 2026, before this file
#     was written): the default Kaiser β=5.0 leaves spectral
#     images above the source Nyquist at −76.3 dB relative to a
#     1 kHz fundamental — not quiet enough to swear by. β=10.0
#     measures −109.7 dB (largest single bin) and −107.5 dB
#     (total energy) on the same tone; the seat therefore swears
#     a floor of −90 dB and keeps ~20 dB of headroom under the
#     measurement. Loudness across 44100→96000 moved 0.021 LU on
#     a stereo program signal (seeded sines + noise, 3 s) and
#     0.021 LU mono — the seat applies no gain. The hidden-crest
#     case (sine at source_rate/4, phase π/4, analytic crest 1.0
#     falling exactly between samples): source sample peak
#     0.707107 (−3.01 dB), house true peak of the source −0.000
#     dBTP, upscaled interior sample peak 0.999986 — the waveform
#     itself, evaluated. Duration (engine probe): 1000 samples at
#     44100 became 2177 at 96000, a duration error of 0.129 target
#     samples. One coordinate the seat's own tests then struck:
#     pyloudnorm's BS.1770 block is 0.400 s, and it refuses
#     program shorter than its block — so the seat refuses it
#     first, by name, rather than report a loudness it cannot
#     swear to (the pipeline's own scale refuses by the same law,
#     on rate).
#   Result: this module. A bench seat, wired into nothing:
#     pipeline.py and every existing module untouched.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""The upscale seat: the same waveform, evaluated at more points.

DOCTRINE — THE FOUNDER'S, STATED PLAINLY:
  Upscaling a recording needs nothing but the recording. A signal
captured cleanly above its Nyquist rate is determined by its
samples — every point between them included — so raising the rate
is evaluating that same waveform at more points, with a polyphase
filter doing the evaluating. Down and up are the same operation:
downsampling reads the waveform at fewer points behind an
anti-alias filter, upsampling at more points behind an
anti-imaging filter. Neither direction needs an "original" beyond
the samples in hand; a gate that claims otherwise is a product
gate, not mathematics.

THE BOUNDARY — WHAT THIS SEAT CANNOT DO, AND DOES NOT PRETEND TO:
  Nothing above the source Nyquist (source_rate / 2) was ever
captured, so nothing above it can be recovered, and this seat
recovers none and synthesizes none. Its filter's stopband stands
where the source's spectrum ends: the upscaled signal carries no
content above the source Nyquist beyond the filter floor sworn
below (IMAGE_FLOOR_DB, −90 dB, proven by test on a pure tone —
the bench measured ≈ −110 dB). Tools that paint plausible
content above the source Nyquist are doing SYNTHESIS — invention,
however beautiful — and synthesis is a different seat with a
different name. This seat's whole oath is the narrower one: the
values between the samples were always implied by the samples;
the seat evaluates them, it does not invent them.

MECHANISM — THE ENGINE:
  scipy.signal.resample_poly with the ratio reduced to exact
integers by gcd (44100→96000 = 320/147; 44100→192000 = 640/147;
48000→96000 = 2/1), windowed with a Kaiser window at β=10.0.
scipy's default β=5.0 was measured on this bench leaving images
at −76.3 dB above the source Nyquist — audible arithmetic, not a
floor a house seat can swear to — so the window is raised and
named here, and the tests swear to −90 dB against the raised
window, never to the default. The seat applies NO gain and NO
shaping: loudness before and after agrees to measurement
tolerance (0.021 LU on the bench's program probe; the tests
swear 0.1 LU), and every peak the report shows is the waveform's
own.

MECHANISM — THE SCALES (no second yardstick):
  * TRUE PEAK: pipeline.true_peak_dbtp — the house's own scale,
    the FFT-domain 4x-oversampled measurement the mastering
    chain masters by and the proof gate weighs deliveries with.
    The founder's master law swears by decoded true peaks, and
    this seat's reason to exist is the gap between a sample peak
    and the truth between samples, so the report carries BOTH:
    sample peak and true peak, before and after, and the rise of
    the true peak above the sample peak on each side.
  * LOUDNESS: pyloudnorm's integrated loudness (BS.1770), the
    scale the house's own run-scripts master by. The pipeline's
    measure_loudness_lufs is NOT used, by its own design: it
    carries the published 48 kHz coefficient set and refuses any
    other rate rather than mis-weigh — and an upscale crosses
    rates by definition, so a scale whose coefficients follow
    the rate is the honest one here. Silence and any non-finite
    reading are floored at −120.0, the pipeline's own floor.

THE SEAM — THE ONE PLACE THE EVALUATION IS NOT THE INTERIOR:
  The polyphase kernel is a finite window (half-length 10 *
max(up, down) taps at the upsampled rate — 10 source samples at
any upward ratio). Inside the file it always has program on both
sides and the evaluation is exact to the filter's ripple. At the
first and last seam_span_source_samples of the file the kernel
runs out of program and reconstructs against the silence that
actually stands outside a finite file — which is the truth of a
file, but a different truth from the interior's: material that
begins or ends mid-crest can ring there. On the bench's worst
case (the hidden-crest sine, full-scale at the seam) the ring
measured +0.52 dB of sample peak at the third output sample and
a whole-file true peak of +0.80 dBTP against the interior's
0.00 — while the interior sample peak stood at 0.999986 against
the analytic crest 1.0. The report's figures are WHOLE-FILE
figures, seams included, because a delivered master must answer
for its seams; the seam's width is printed in the report
(seam_span_source_samples) so the coordinate is a number, not
a vibe.

SHAPE LAW (refusals by name, the house's law):
  * Audio is the house's own shape: a 1-D mono array, or a 2-D
    array in (channels, frames) orientation — the shape
    pipeline.master_signal masters and core.io writes. The
    returned array keeps the caller's shape exactly: 1-D in,
    1-D out; (C, N) in, (C, ceil(N * up / down)) out. Samples are
    read on the house's float scale (full scale = 1.0); every dB
    figure is relative to it.
  * Rates are whole positive numbers of hertz. Fractional,
    non-numeric, zero, or negative rates are refused by name.
  * target_rate < source_rate is refused: downsampling is a
    different seat, not a failure of this one. target_rate ==
    source_rate is refused: the identity is not an upscale.
  * Empty input (no frames, or no channels), complex samples,
    non-numeric samples, arrays of dimension other than 1 or 2,
    and non-finite samples (NaN / infinity) are refused by name,
    each as UpscaleError, before any arithmetic runs.
  * Program of 0.400 s or shorter is refused by name: the
    loudness scale's BS.1770 block is 0.400 s and it cannot weigh
    less than a block, so the seat refuses rather than report a
    loudness it cannot swear to. (Duration is one number on both
    sides of the seat, so the source side's check covers both.)
"""

import math
from math import gcd
from typing import Dict, Tuple, Union

import numpy as np
import pyloudnorm as pyln
from scipy.signal import resample_poly

from resonance.studio.pipeline import true_peak_dbtp

__all__ = ["UpscaleError", "resample_up", "KAISER_BETA", "IMAGE_FLOOR_DB"]


class UpscaleError(ValueError):
    """A rate, a direction, or a signal refused by name.

    Subclasses ValueError so existing house code that catches
    ValueError around numeric work catches this too; the tests
    assert UpscaleError itself, so a refusal can never pass
    silently as some other error.
    """


# The Kaiser window's beta, raised from scipy's default 5.0: the
# default measured −76.3 dB of image energy above the source
# Nyquist on this bench; β=10.0 measured −109.7 dB. The seat
# swears IMAGE_FLOOR_DB and keeps the difference as headroom.
KAISER_BETA = 10.0

# The sworn floor: in the upscaled signal, no spectral content
# above the source Nyquist stands above this level (decibels
# relative to the program's own fundamental, proven by test on a
# pure tone; total energy above Nyquist measured lower still).
IMAGE_FLOOR_DB = -90.0

# The house's silence floor, the same −120.0 pipeline.py floors
# its own zero readings at: a peak or a loudness that is not a
# number is reported at the floor, never invented above it.
_FLOOR_DB = -120.0


def _as_rate(value, name: str) -> int:
    """MECHANISM: bring a caller's rate under the rate law.

    A rate is a whole positive number of hertz. Booleans,
    fractional numbers, non-numeric values, zero, and negatives
    are refused by name — a rate that is not a count of cycles
    per second cannot seat a ratio.
    """
    if isinstance(value, bool):
        raise UpscaleError(f"{name}: a sample rate is a whole positive "
                           f"number of hertz; got {value!r}")
    if isinstance(value, (int, np.integer)):
        rate = int(value)
    elif isinstance(value, float) and float(value).is_integer():
        # An integral float (44100.0) IS a whole number of hertz;
        # only the fractional kind is refused.
        rate = int(value)
    else:
        raise UpscaleError(f"{name}: a sample rate is a whole positive "
                           f"number of hertz; got {value!r}")
    if rate <= 0:
        raise UpscaleError(f"{name}: a sample rate must be positive; "
                           f"got {rate}")
    return rate


def _as_audio(samples) -> Tuple[np.ndarray, bool]:
    """MECHANISM: bring a caller's samples under the shape law.

    Returns ((channels, frames) float64 array, was_mono). Complex
    input is refused before conversion — float() would silently
    drop the imaginary part, and a dropped part is a smoothed
    refusal; the house refuses whole or not at all.
    """
    if np.iscomplexobj(samples):
        raise UpscaleError("samples: complex audio is refused — the "
                           "seat is seated over real samples only")
    try:
        arr = np.asarray(samples, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise UpscaleError(f"samples: not a real numeric array "
                           f"({exc})") from exc
    if arr.ndim == 1:
        mono, x = True, arr[np.newaxis, :]
    elif arr.ndim == 2:
        mono, x = False, arr
    else:
        raise UpscaleError(f"samples: audio is a 1-D mono array or a "
                           f"2-D (channels, frames) array; got "
                           f"{arr.ndim}-D")
    channels, frames = x.shape
    if frames == 0:
        raise UpscaleError("samples: empty input — no frames to "
                           "evaluate")
    if channels == 0:
        raise UpscaleError("samples: empty input — no channels")
    if not np.all(np.isfinite(x)):
        raise UpscaleError("samples: non-finite samples (NaN or "
                           "infinity) are refused — a peak that is "
                           "not a number cannot be sworn to")
    return x, mono


def _sample_peak_db(x: np.ndarray) -> float:
    """Sample peak in dB relative to full scale 1.0, floored.

    MECHANISM: the largest |sample| actually present — the number
    that HIDES the inter-sample crests, carried in the report
    beside the true peak so the hiding is measured, not asserted.
    """
    peak = float(np.max(np.abs(x))) if x.size else 0.0
    return 20.0 * math.log10(peak) if peak > 0.0 else _FLOOR_DB


def _loudness_lufs(x: np.ndarray, rate: int) -> float:
    """Integrated loudness (LUFS) by pyloudnorm, rate-correct.

    MECHANISM: pyloudnorm's Meter computes its BS.1770 K-weighting
    for the rate it is handed, which is what a cross-rate seat
    needs (see the module's scales doctrine). pyloudnorm speaks
    (frames, channels); the house speaks (channels, frames); the
    transpose at this boundary is the whole translation. Silence
    reads −inf from the meter and is floored at the house's
    −120.0, as is any non-finite reading.
    """
    if not np.any(x):
        return _FLOOR_DB
    data = x[0] if x.shape[0] == 1 else np.ascontiguousarray(x.T)
    # The caller (resample_up) has already refused program of
    # 0.400 s or shorter, so the meter's block always seats here.
    value = float(pyln.Meter(rate).integrated_loudness(data))
    return value if math.isfinite(value) else _FLOOR_DB


def resample_up(samples, source_rate, target_rate
                ) -> Tuple[np.ndarray, Dict[str, Union[int, float, str]]]:
    """Evaluate `samples` from source_rate at target_rate, upward only.

    Returns (new_samples, report): the resampled array in the
    caller's own shape (1-D mono stays 1-D; (channels, frames)
    stays (channels, frames)), and the report — a plain dict in
    the house style of pipeline.master_signal's report — carrying
    the ratio arithmetic, the counts and durations, loudness and
    both peaks on both sides, the inter-sample rises, the seam's
    width, and the note that reads them. The seat applies no
    gain: what changes is the number of points the waveform is
    evaluated at, and nothing else.
    """
    sr = _as_rate(source_rate, "source_rate")
    tr = _as_rate(target_rate, "target_rate")
    # The direction law: this seat evaluates upward, only. A lower
    # target is not an error in the caller's arithmetic — it is a
    # different seat's work, and is refused as such, by name.
    if tr < sr:
        raise UpscaleError(
            f"target_rate {tr} < source_rate {sr}: downsampling is "
            "a different seat — this seat only evaluates upward")
    if tr == sr:
        raise UpscaleError(
            f"target_rate == source_rate ({sr}): the identity is "
            "not an upscale — there is nothing to evaluate")
    x, mono = _as_audio(samples)

    # The loudness block law: BS.1770 weighs in 0.400 s blocks
    # and pyloudnorm refuses program not longer than one block.
    # The seat refuses first, by name and before any arithmetic,
    # rather than strike the resample and then fail at the scale.
    # Exact integer form: frames/sr <= 2/5 s  <=>  5*frames <= 2*sr.
    # Duration is the same on both sides of the seat, so this one
    # check covers the target side's block as well.
    if 5 * x.shape[1] <= 2 * sr:
        raise UpscaleError(
            f"samples: {x.shape[1]} frames at {sr} Hz is "
            f"{x.shape[1] / sr:.3f} s — the loudness scale (BS.1770 "
            "via pyloudnorm) weighs in 0.400 s blocks and cannot "
            "weigh program not longer than one block; the seat "
            "refuses rather than report a loudness it cannot "
            "swear to")

    # The exact rational ratio: the only arithmetic the seat is
    # allowed to be casual about is none — 44100→96000 is 320/147,
    # and the report prints the reduced pair so the ratio can be
    # checked by hand.
    divisor = gcd(sr, tr)
    up, down = tr // divisor, sr // divisor

    y = np.asarray(
        resample_poly(x, up, down, axis=-1,
                      window=("kaiser", KAISER_BETA)),
        dtype=np.float64)

    channels, n_before = x.shape
    n_after = y.shape[1]

    lufs_before = _loudness_lufs(x, sr)
    lufs_after = _loudness_lufs(y, tr)
    spk_before = _sample_peak_db(x)
    spk_after = _sample_peak_db(y)
    # The house's own true-peak scale, 4x FFT oversampling — the
    # measurement that sees between the samples, run on both
    # sides so the seat's effect on the hidden crests is a pair
    # of numbers, not a claim.
    tp_before = float(true_peak_dbtp(x, sr))
    tp_after = float(true_peak_dbtp(y, tr))
    rise_before = tp_before - spk_before
    rise_after = tp_after - spk_after

    # The seam's width in source samples: the kernel's half-length
    # (10 * max(up, down) taps at the upsampled rate) expressed in
    # the source's own samples — 10 at any upward ratio, computed
    # here from the construction rather than asserted.
    seam = -(-(10 * max(up, down)) // up)

    report: Dict[str, Union[int, float, str]] = {
        "source_rate": sr,
        "target_rate": tr,
        "ratio_up": up,
        "ratio_down": down,
        "ratio": round(tr / sr, 6),
        "channels": channels,
        "samples_before": n_before,
        "samples_after": n_after,
        "duration_before_s": round(n_before / sr, 6),
        "duration_after_s": round(n_after / tr, 6),
        "lufs_before": round(lufs_before, 2),
        "lufs_after": round(lufs_after, 2),
        "lufs_delta": round(abs(lufs_after - lufs_before), 2),
        "sample_peak_before_db": round(spk_before, 2),
        "sample_peak_after_db": round(spk_after, 2),
        "true_peak_before_dbtp": round(tp_before, 2),
        "true_peak_after_dbtp": round(tp_after, 2),
        "intersample_rise_before_db": round(rise_before, 2),
        "intersample_rise_after_db": round(rise_after, 2),
        "source_nyquist_hz": sr / 2.0,
        "filter": f"polyphase FIR (scipy.signal.resample_poly), "
                  f"Kaiser window, beta {KAISER_BETA}",
        "image_floor_db": IMAGE_FLOOR_DB,
        "seam_span_source_samples": seam,
        "intersample_note": (
            f"true peak stands {rise_before:.2f} dB above the sample "
            f"peak before and {rise_after:.2f} dB above it after: "
            "the crests were always there, between the samples — "
            "this seat evaluates them, it does not invent them. "
            f"Whole-file figures include the seams (the first and "
            f"last {seam} source samples), where the kernel runs "
            "out of program and reconstructs against the silence "
            "outside the file."),
    }
    return (y[0] if mono else y), report
