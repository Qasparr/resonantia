# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# SPDX-License-Identifier: AGPL-3.0-only
# =============================================================================
# "The arithmetic must close: a loop that claims four bars IS four bars,
#  to the sample."
#
# 93.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
#
# DOCTRINE: this module is the counting-house of RESONANTIA's Tools
# Wing. It owns no sound of its own; it owns the NUMBERS every other
# tool must answer to — samples per beat, samples per bar, and the
# measured drift of real audio against the grid it claims to live on.
# Method of Science, Aim of Religion — Scientific Illuminism.
# =============================================================================
"""resonance/grid.py -- sample-exact beat/bar arithmetic.

HYPOTHESIS
    Tempo math done in seconds drifts. 60/93 s per beat is not a
    whole number of samples at any common sample rate, so a loop
    trimmed "to 8.000 seconds" is NOT an 8-second loop of bars --
    it is a loop that creeps against the metronome a few samples
    further every pass, and the creep is audible within a minute.
    The fix is accounting, not magic: carry the fractional beat
    length as a float, but always ROUND ONCE, AT THE TOTAL. A loop
    of N bars is round(N * beats_per_bar * 60 * sr / bpm) samples --
    one rounding, at the end, so the loop closes exactly and the
    next loop starts on the same grid line.

METHOD
    samples_per_beat(bpm, sr)  -> float, 60*sr/bpm, unrounded.
    samples_per_bar(bpm, sr, beats_per_bar=4) -> float.
    bars_to_samples(n_bars, ...) -> int: the single-rounding rule
        applied to the total; this is the only length a loop that
        claims n_bars is allowed to have.
    fit_loop_to_bars(x, bpm, sr, beats_per_bar=4, mode):
        'trim'    -> cut to the largest whole-bar length <= len(x)
        'pad'     -> zero-pad to the smallest whole-bar length >= len(x)
        'nearest' -> whichever whole-bar length is closer
        Returns a NEW array; the input is never mutated. An input
        shorter than one bar trims to empty under 'trim' -- reported
        by length, not hidden.
    measure_drift(n_samples, bpm, sr, beats_per_bar=4) -> dict:
        the signed distance from a real length to its nearest
        whole-bar length, in samples, milliseconds, and beats, plus
        the whole-bar count it rounds to. Drift is MEASURED here,
        never silently corrected -- correction is the caller's act.
    beat_positions(n_samples, bpm, sr, beats_per_bar=4) -> the
        sample index of every beat line inside the span, each
        rounded from the same unrounded accumulator, so beat lines
        do not accumulate rounding error either.

OBSERVATION
    At 93 BPM and 48 kHz one beat is 30967.741... samples. Rounding
    per beat gives a 4-bar loop of 495,484 samples; the single-
    rounding rule gives 495,484 (they agree here) -- but at other
    tempos they diverge by a sample or two per loop, which is
    exactly the creep this module exists to refuse.

RESULT
    Pure functions over ints and numpy arrays; no audio is altered
    except by fit_loop_to_bars' documented trim/pad. bpm <= 0 or
    sr <= 0 raises ValueError. numpy only.

No medical or therapeutic claims are made about anything counted here.
"""

import numpy as np

__all__ = [
    "samples_per_beat",
    "samples_per_bar",
    "bars_to_samples",
    "fit_loop_to_bars",
    "measure_drift",
    "beat_positions",
]


def _validate(bpm, sr):
    # MECHANISM: one gate for the whole module. A non-positive tempo
    # or sample rate is not a slow tempo; it is a nonsense question,
    # and the counting-house refuses nonsense loudly (fail-closed).
    if bpm <= 0:
        raise ValueError(f"grid: bpm must be positive, got {bpm}")
    if sr <= 0:
        raise ValueError(f"grid: sr must be positive, got {sr}")


def samples_per_beat(bpm, sr):
    """Float samples in one beat: 60*sr/bpm. Deliberately unrounded.

    DOCTRINE: callers who round this number per beat and multiply
    re-introduce the creep this module exists to refuse. Keep the
    fraction; round totals, never rates.
    """
    _validate(bpm, sr)
    return 60.0 * float(sr) / float(bpm)


def samples_per_bar(bpm, sr, beats_per_bar=4):
    """Float samples in one bar of `beats_per_bar` beats."""
    if beats_per_bar <= 0:
        raise ValueError(
            f"grid: beats_per_bar must be positive, got {beats_per_bar}")
    return samples_per_beat(bpm, sr) * float(beats_per_bar)


def bars_to_samples(n_bars, bpm, sr, beats_per_bar=4):
    """Exact integer sample length of `n_bars` bars.

    MECHANISM: the single-rounding rule -- compute the full float
    length of the whole span, round once. This is the canonical
    length of any loop that claims to be `n_bars` bars long.
    """
    if n_bars < 0:
        raise ValueError(f"grid: n_bars must be >= 0, got {n_bars}")
    return int(round(n_bars * samples_per_bar(bpm, sr, beats_per_bar)))


def fit_loop_to_bars(x, bpm, sr, beats_per_bar=4, mode="nearest"):
    """Return a copy of `x` trimmed or zero-padded to whole bars.

    mode: 'trim' (largest whole-bar length <= len), 'pad' (smallest
    >= len), 'nearest'. Multi-channel arrays are fitted along the
    LAST axis. The input is never mutated.
    """
    if mode not in ("trim", "pad", "nearest"):
        raise ValueError(f"grid: unknown fit mode {mode!r}")
    x = np.asarray(x)
    n = x.shape[-1] if x.ndim else 0
    bar = samples_per_bar(bpm, sr, beats_per_bar)
    whole = n / bar
    if mode == "trim":
        n_bars = int(np.floor(whole))
    elif mode == "pad":
        n_bars = int(np.ceil(whole))
    else:
        n_bars = int(round(whole))
    target = bars_to_samples(n_bars, bpm, sr, beats_per_bar)
    if target == n:
        return x.copy()
    if target < n:
        return x[..., :target].copy()
    pad = target - n
    pad_width = [(0, 0)] * x.ndim
    pad_width[-1] = (0, pad)
    return np.pad(x, pad_width)


def measure_drift(n_samples, bpm, sr, beats_per_bar=4):
    """Measure how far a real length sits from the whole-bar grid.

    Returns a dict: n_bars (nearest whole-bar count), target_samples,
    drift_samples (signed: actual - target), drift_ms, drift_beats.
    Positive drift = the material runs LONG of the grid.
    """
    if n_samples < 0:
        raise ValueError(f"grid: n_samples must be >= 0, got {n_samples}")
    bar = samples_per_bar(bpm, sr, beats_per_bar)
    n_bars = int(round(n_samples / bar)) if bar > 0 else 0
    target = bars_to_samples(n_bars, bpm, sr, beats_per_bar)
    drift = int(n_samples) - target
    return {
        "n_bars": n_bars,
        "target_samples": target,
        "drift_samples": drift,
        "drift_ms": 1000.0 * drift / float(sr),
        "drift_beats": drift / samples_per_beat(bpm, sr),
    }


def beat_positions(n_samples, bpm, sr, beats_per_bar=4):
    """Sample index of every beat line in [0, n_samples).

    MECHANISM: positions are round(k * samples_per_beat) from the
    unrounded accumulator -- each line is rounded independently from
    the true float position, so error never accumulates line to
    line. Bar lines are every beats_per_bar-th entry.
    """
    spb = samples_per_beat(bpm, sr)
    n_beats = int(np.floor(n_samples / spb)) + 1 if n_samples > 0 else 0
    pos = np.round(spb * np.arange(n_beats)).astype(int)
    return pos[pos < n_samples] if n_samples > 0 else pos[:0]


# 93 — Live, Love, and let Love, Live.
