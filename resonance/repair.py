# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# SPDX-License-Identifier: AGPL-3.0-only
# =============================================================================
# "Rebuild the broken span from the signal's own testimony on both
#  sides of the wound -- invent nothing the waveform did not say."
#
# 93.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
#
# DOCTRINE: repair is interpolation under oath. Every filled sample
# in this module is derived from the surrounding real signal by a
# named method, and every repaired span is reported to the caller.
# Silent repair is falsification; this module does not practice it.
# Method of Science, Aim of Religion — Scientific Illuminism.
# =============================================================================
"""resonance/repair.py -- tears, pops, cracks: the repair bench.

HYPOTHESIS
    Most damage done to a recording after the fact is LOCAL: a click
    is a few samples, a tear is a fraction of a second, crackle is a
    sparse rain of tiny outliers, clipping flattens only the peaks.
    Local damage admits local repair, because the signal on both
    sides of the wound still testifies to what the signal was doing
    -- its spectrum, its momentum, its statistics. The repair family
    is solved, as the founder said: detect the outlier, excise it,
    and bridge the hole from the testimony of the edges.

METHOD
    remove_dc(x): subtract the mean (per channel). DC offset is the
        humblest defect and the first removed, because it poisons
        every detector downstream.
    detect_clicks(x, threshold=10.0): robust z-score of the first
        difference -- a click is a near-instantaneous jump, so it
        stands out in d(x) even when it hides in x. Sigma is the
        MAD-based robust estimate, so the clicks themselves cannot
        inflate the yardstick. Flagged samples are merged into
        spans (gaps of <= 8 samples merge) and padded by 2 samples
        on each side: the excision must take the whole wound.
    repair_gap(x, start, end): fill [start, end) by the method the
        gap length earns --
          <= 6 samples: cubic Hermite bridging on the edge values
            and edge slopes (the waveform's own momentum, continued).
          longer: AR interpolation in the Janssen family -- fit an
            autoregressive model by least squares on the context at
            BOTH edges (the right edge's model is fit on its
            reversal, so it predicts toward the gap), predict into
            the gap from both sides, and blend the two predictions
            with distance weights. DOCUMENTED SIMPLIFICATION: the
            full Janssen method iterates the fit with the filled gap
            included; this implementation is single-pass. On tonal
            and speech-like material the difference is small; on
            noise-like material AR fill is a plausible texture, not
            a recovery, and is labeled as such wherever it matters.
        A gap touching an array edge, or with too little context,
        falls back to linear bridging. Fallbacks are chosen by the
        function and visible in the code, never silent magic.
    declick(x, threshold): detect + repair every click span;
        returns (repaired, spans) -- the spans ARE the report.
    repair_tear(x, start, end, fade=...): the long-gap arm. AR fill
        with a wider context, then equal-power crossfades where the
        fill meets the real signal at both seams, so the mend
        introduces no step of its own.
    decrackle(x, strength=1.0, window=5): median-filter witness.
        The median of a small window tracks the programme and
        ignores sparse impulses; where the signal departs from its
        own median by more than a robust threshold, the departure
        is crackle and is pulled toward the median by `strength`.
    declip(x, level=None): runs of >= 2 samples pinned at the clip
        level are excised and rebuilt with repair_gap's AR bridge.
        level defaults to max|x|; pass it explicitly when the
        recording was clipped below its current peak.

OBSERVATION
    On synthetic wounds the bench measures what it claims: an
    injected click's peak deviation falls by orders of magnitude; a
    50 ms tear in a sine returns to within a few percent RMS of the
    unharmed signal; a hard-clipped sine recovers most of its lost
    crest. On real-world noise-like tears (cymbals, crowd), the fill
    is a statistical stand-in -- plausible, seamless, and NOT the
    original. The module restores continuity, never history.

RESULT
    Pure functions over numpy arrays; every repair reports its
    spans. Stereo (2, N) processed per channel where sensible.
    numpy only.

No medical or therapeutic claims are made about anything repaired here.
"""

import numpy as np

__all__ = [
    "remove_dc",
    "detect_clicks",
    "repair_gap",
    "declick",
    "repair_tear",
    "decrackle",
    "declip",
]


def remove_dc(x):
    """Subtract the mean (per channel for (2, N) input)."""
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0:
        return x.copy()
    return x - np.mean(x, axis=-1, keepdims=True)


def _robust_sigma(v):
    """MAD-based robust standard deviation estimate."""
    med = np.median(v)
    return 1.4826 * np.median(np.abs(v - med)) + 1e-20


def detect_clicks(x, threshold=10.0, merge_gap=8, pad=2):
    """Locate click spans in a mono signal.

    Returns a list of (start, end) half-open sample spans, sorted.
    MECHANISM: z-score of the first difference against a MAD-robust
    sigma; a click's attack is the loudest derivative in the room.
    A click also has a falling edge, so flagged indices merge into
    one span per click (merge_gap), and the span is padded so the
    excision takes the wound's full width.

    DOCTRINE / honest limit: a genuine programme transient (a drum
    hit's first sample) can trip a low threshold. threshold=10
    robust sigmas is conservative; de-clicking is for sparse
    defects, and the returned spans let the caller audit every
    excision before trusting it.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        x = x[0]
    if len(x) < 4:
        return []
    d = np.diff(x, prepend=x[0])
    z = np.abs(d) / _robust_sigma(d)
    flagged = np.nonzero(z > threshold)[0]
    if flagged.size == 0:
        return []
    spans = []
    start = prev = int(flagged[0])
    for idx in flagged[1:]:
        idx = int(idx)
        if idx - prev <= merge_gap:
            prev = idx
        else:
            spans.append((start, prev + 1))
            start = prev = idx
    spans.append((start, prev + 1))
    n = len(x)
    return [(max(0, s - pad), min(n, e + pad)) for s, e in spans]


def _cubic_bridge(x, start, end):
    """Cubic Hermite fill of [start, end) from edge values/slopes."""
    n = len(x)
    length = end - start
    y0 = x[start - 1] if start > 0 else x[end]
    y1 = x[end] if end < n else x[start - 1]
    # Edge slopes from the nearest honest differences available.
    m0 = (x[start - 1] - x[start - 3]) / 2.0 if start >= 3 else (
        x[start - 1] - x[start - 2] if start >= 2 else 0.0)
    m1 = (x[end + 2] - x[end]) / 2.0 if end + 2 < n else (
        x[end + 1] - x[end] if end + 1 < n else 0.0)
    t = (np.arange(length) + 1) / (length + 1)  # interior points only
    h00 = 2 * t ** 3 - 3 * t ** 2 + 1
    h10 = t ** 3 - 2 * t ** 2 + t
    h01 = -2 * t ** 3 + 3 * t ** 2
    h11 = t ** 3 - t ** 2
    span = float(length + 1)
    return h00 * y0 + h10 * span * m0 + h01 * y1 + h11 * span * m1


def _ar_fit(segment, order):
    """Least-squares AR coefficients predicting segment forward.

    Returns None when the segment cannot support the fit.
    """
    seg = np.asarray(segment, dtype=np.float64)
    if len(seg) <= order + 1:
        return None
    rows = np.stack([seg[order - 1 - k:len(seg) - 1 - k]
                     for k in range(order)], axis=1)
    target = seg[order:]
    rows = rows[:len(target)]
    if len(target) < order:
        return None
    coef, *_ = np.linalg.lstsq(rows, target, rcond=None)
    return coef


def _ar_predict(coef, history, steps):
    """Roll an AR model forward `steps` samples from `history`."""
    order = len(coef)
    buf = list(np.asarray(history, dtype=np.float64)[-order:])
    out = np.empty(steps)
    for i in range(steps):
        out[i] = float(np.dot(coef, buf[-order:][::-1]))
        buf.append(out[i])
    return out


def _ar_bridge(x, start, end, order=32, context=2048):
    """Janssen-family AR fill of [start, end); see module docstring.

    Single-pass simplification of Janssen: fit on the true context
    only (no iterate-with-fill), predict from both edges, blend by
    distance. Falls back to linear bridging when either edge lacks
    the context to testify.
    """
    n = len(x)
    length = end - start
    left = x[max(0, start - context):start]
    right = x[end:min(n, end + context)]
    order = int(min(order, max(2, min(len(left), len(right)) // 4)))
    coef_f = _ar_fit(left, order) if len(left) > order + 1 else None
    coef_b = _ar_fit(right[::-1], order) if len(right) > order + 1 else None
    if coef_f is None or coef_b is None:
        # One or both edges cannot testify: linear bridging is the
        # honest remainder (also the edge-of-array path).
        y0 = x[start - 1] if start > 0 else (x[end] if end < n else 0.0)
        y1 = x[end] if end < n else y0
        return np.linspace(y0, y1, length + 2)[1:-1]
    fwd = _ar_predict(coef_f, left, length)
    bwd = _ar_predict(coef_b, right[::-1], length)[::-1]
    # Distance weights: each prediction is trusted most near its own
    # edge (the Janssen weighting is quadratic; linear is the
    # documented simplification and behaves the same at the seams).
    w = (np.arange(length) + 1) / (length + 1)
    return (1.0 - w) * fwd + w * bwd


def repair_gap(x, start, end):
    """Return a copy of mono `x` with [start, end) rebuilt.

    Method by gap length: <= 6 samples cubic Hermite; longer, AR
    (Janssen-family). See module docstring for both, and for the
    single-pass simplification this implementation declares.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        x = x[0]
    out = x.copy()
    start = int(max(0, start))
    end = int(min(len(x), end))
    if end <= start or len(x) == 0:
        return out
    if end - start <= 6 and 0 < start and end < len(x):
        out[start:end] = _cubic_bridge(x, start, end)
    else:
        out[start:end] = _ar_bridge(x, start, end)
    return out


def declick(x, threshold=10.0):
    """Detect and repair all click spans; return (repaired, spans).

    The spans are the audit trail: every excision this function made,
    in sample coordinates, for the caller to inspect.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        chans = [declick(ch, threshold) for ch in x]
        return (np.stack([c[0] for c in chans]),
                [c[1] for c in chans])
    spans = detect_clicks(x, threshold=threshold)
    out = x.copy()
    for s, e in spans:
        out = repair_gap(out, s, e)
    return out, spans


def repair_tear(x, start, end, fade_samples=256):
    """Repair a long dropout [start, end) with seam crossfades.

    MECHANISM: AR bridge with a wide context (the tear's edges must
    testify at length), then seam anchoring over `fade_samples` at
    both edges: the fill's residual offset at each seam is removed
    under an equal-power decay, so the mend starts exactly on the
    real edge value and adds no step of its own. Where the gap is
    too short for the requested fade, the fade shrinks to the gap.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        x = x[0]
    out = x.copy()
    start = int(max(0, start))
    end = int(min(len(x), end))
    if end <= start or len(x) == 0:
        return out
    fill = _ar_bridge(x, start, end, order=48, context=8192)
    out[start:end] = fill
    fade = int(min(fade_samples, max(1, (end - start) // 2)))
    # MECHANISM: seam anchoring. The AR fill is statistically right
    # but need not pass exactly through the real edge samples, and
    # any residual offset at the seam is a step -- a new click,
    # manufactured by the repair itself. So measure the fill's
    # offset at each seam and remove it under an equal-power
    # (cos^2) decay across the fade: at the seam the correction is
    # total (the fill starts exactly on the real edge value), and
    # it dies to zero by the fade's end, leaving the fill's own
    # interior untouched. cos^2/sin^2 weights keep the correction's
    # power profile smooth -- no dip, no swell, no step.
    t = np.linspace(0.0, 1.0, fade, endpoint=False)
    decay = np.cos(t * np.pi / 2) ** 2
    if start > 0:
        offset = fill[0] - x[start - 1]
        out[start:start + fade] = fill[:fade] - offset * decay
    if end < len(x):
        offset = fill[-1] - x[end]
        out[end - fade:end] = fill[-fade:] - offset * decay[::-1]
    return out


def _median_filter(x, window):
    """Centered median filter (odd window), edge-padded."""
    if window % 2 == 0:
        window += 1
    half = window // 2
    padded = np.pad(x, half, mode="edge")
    view = np.lib.stride_tricks.sliding_window_view(padded, window)
    return np.median(view, axis=1)


def decrackle(x, strength=1.0, window=5, threshold=4.0):
    """Pull sparse impulsive crackle toward the signal's own median.

    MECHANISM: the median filter is the witness that ignores the
    crackle; the residual (signal - median) is crackle wherever it
    exceeds `threshold` robust sigmas of itself. Masked samples move
    toward the median by `strength` (1.0 = full replacement).
    Programme transients broader than the window survive: the
    median follows them, so they never enter the residual.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        return np.stack([decrackle(ch, strength, window, threshold)
                         for ch in x])
    if len(x) < window:
        return x.copy()
    med = _median_filter(x, window)
    res = x - med
    sigma = _robust_sigma(res)
    mask = np.abs(res) > threshold * sigma
    out = x.copy()
    out[mask] = x[mask] - strength * res[mask]
    return out


def declip(x, level=None, min_run=2):
    """Rebuild hard-clipped peaks; return (repaired, spans).

    MECHANISM: samples pinned at +/- level in runs of >= min_run
    are not peaks, they are plateaus -- the waveform's missing
    crest. Each plateau is excised and rebuilt by repair_gap's AR
    bridge from the unclipped slopes on both sides.
    DOCTRINE: a single sample AT the max is a peak and is left
    alone (min_run >= 2). If the recording's loudest moment merely
    touches the ceiling once, this function does nothing, and
    nothing is the honest answer.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        chans = [declip(ch, level, min_run) for ch in x]
        return (np.stack([c[0] for c in chans]),
                [c[1] for c in chans])
    if len(x) == 0:
        return x.copy(), []
    lvl = float(level) if level is not None else float(np.max(np.abs(x)))
    if lvl <= 0:
        return x.copy(), []
    pinned = np.abs(np.abs(x) - lvl) <= 1e-9 * max(1.0, lvl)
    spans = []
    i = 0
    while i < len(x):
        if pinned[i]:
            j = i
            while j < len(x) and pinned[j]:
                j += 1
            if j - i >= min_run:
                spans.append((i, j))
            i = j
        else:
            i += 1
    out = x.copy()
    for s, e in spans:
        out = repair_gap(out, s, e)
    return out, spans


# 93 — Live, Love, and let Love, Live.
