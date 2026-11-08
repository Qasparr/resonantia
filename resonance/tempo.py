# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# SPDX-License-Identifier: AGPL-3.0-only
# =============================================================================
# "Move the sound in time, and say by which road you moved it."
#
# 93.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
#
# DOCTRINE: there are two honest roads for time in this engine and
# they are not interchangeable. WSOLA walks the waveform itself and
# keeps transients standing; the phase vocoder walks the spectrum
# and keeps tones pure. The caller names the road, or accepts the
# documented heuristic and its name in the bargain.
# Method of Science, Aim of Religion — Scientific Illuminism.
# =============================================================================
"""resonance/tempo.py -- time-stretch and tempo-held pitch shift.

HYPOTHESIS
    Changing tempo without changing pitch (or pitch without tempo)
    is surgery on one axis of sound while holding the other still,
    and each material has a road that suits it. WSOLA (Waveform
    OverLap-Add with Similarity search) cuts the waveform into
    grains and re-lays them at the new spacing, searching near each
    expected position for the grain whose overlap best matches what
    is already laid -- transients and speech survive because the
    waveform itself is preserved, never resynthesized. The phase
    vocoder (resonance.pitch.shift.phase_vocoder, the house engine)
    resynthesizes from the spectrum -- sustained tones stay pure,
    but transients smear. Neither is "better"; they are different
    instruments, and this module keeps both under one small API.

METHOD
    wsola(x, rate, window=1024, hop=None, tolerance=None):
        Synthesis hop Hs = window//4; analysis hop Ha = Hs/rate.
        For each synthesis frame, candidate input positions within
        +/- tolerance of the expected position are scored by
        normalized cross-correlation against the already-synthesized
        overlap tail; the best grain is Hann-windowed and added.
        rate > 1 = longer (slower), rate < 1 = shorter (faster).
    time_stretch(x, sr, rate, method='wsola'|'vocoder'|'auto'):
        'auto' measures mean spectral flux; flux-heavy (transient)
        material takes WSOLA, steady material takes the vocoder.
        The heuristic is documented as a heuristic, not an oracle.
    shift_pitch(x, sr, semitones, method='wsola'|'vocoder'):
        Pitch shift with duration (tempo) held: varispeed resample
        by r = 2**(st/12) -- duration D/r, pitch * r -- then
        time-stretch by r on the named road to restore duration.
        The 'vocoder' road delegates to the house
        resonance.pitch.pitch_shift outright; the 'wsola' road is
        this module's own composition and is the transient-friendlier
        of the two. NEITHER road preserves formants (that is
        resonance.vocal's office); both smear or double something at
        large shifts, and say so here rather than hiding it.
    Stereo (2, N) is processed per channel, as in the pitch wing.

OBSERVATION
    On synthetic material: WSOLA doubles a sine burst's duration
    with its dominant frequency held within a few Hz; the vocoder
    holds tone purity on sustained sines to the same tolerance.
    On real speech WSOLA keeps consonant attacks legible where the
    vocoder turns them to water -- the expected, documented split.

RESULT
    wsola / time_stretch / shift_pitch over numpy arrays, sr
    explicit. rate <= 0 raises ValueError. Empty input returns
    empty output. numpy only.

No medical or therapeutic claims are made about anything stretched here.
"""

import numpy as np

from resonance.pitch.shift import phase_vocoder, pitch_shift

__all__ = ["wsola", "time_stretch", "shift_pitch"]


def _resample_linear(x, factor):
    """Resample by `factor` (linear interp; factor>1 = longer).

    MECHANISM: matches the pitch wing's own resampler so the two
    shift roads differ only in their stretch engine, not in their
    varispeed step -- the comparison between roads stays honest.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0 or factor == 1.0:
        return x.copy()
    n_out = max(1, int(round(len(x) * factor)))
    return np.interp(np.linspace(0, len(x) - 1, n_out),
                     np.arange(len(x)), x)


def _wsola_mono(x, rate, window=1024, hop=None, tolerance=None):
    """WSOLA on one channel. rate>1 lengthens. See module docstring."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    if n == 0:
        return x.copy()
    hop_s = int(hop) if hop else max(1, window // 4)
    tol = int(tolerance) if tolerance is not None else window // 4
    hop_a = hop_s / float(rate)
    win = np.hanning(window)
    overlap = window - hop_s
    # Pad so every candidate grain is a full window.
    xp = np.concatenate([x, np.zeros(window)])
    target_len = int(round(n * rate))
    n_frames = max(1, int(np.ceil(target_len / hop_s)))
    out = np.zeros(n_frames * hop_s + window)
    wsum = np.zeros_like(out)
    for i in range(n_frames):
        nominal = i * hop_a
        center = int(round(nominal))
        lo = max(0, center - tol)
        hi = min(len(xp) - window, center + tol)
        if hi < lo:
            hi = lo
        pos = lo
        if i > 0 and overlap > 0 and hi > lo:
            # MECHANISM: score each candidate grain by how its head
            # (the overlap region) continues what is already laid.
            # The reference is the running normalized output tail.
            s0 = i * hop_s
            ref = out[s0:s0 + overlap].copy()
            nz = wsum[s0:s0 + overlap] > 1e-8
            ref[nz] /= wsum[s0:s0 + overlap][nz]
            cand = np.stack([xp[p:p + overlap] for p in range(lo, hi + 1)])
            num = cand @ ref
            den = (np.linalg.norm(cand, axis=1) * np.linalg.norm(ref))
            den[den == 0] = 1.0
            pos = lo + int(np.argmax(num / den))
        grain = xp[pos:pos + window] * win
        s0 = i * hop_s
        out[s0:s0 + window] += grain
        wsum[s0:s0 + window] += win
    nz = wsum > 1e-8
    out[nz] /= wsum[nz]
    return out[:target_len]


def wsola(x, rate, window=1024, hop=None, tolerance=None):
    """Time-stretch by `rate` with pitch held, the waveform road.

    rate > 1 = longer/slower, rate < 1 = shorter/faster. Stereo
    (2, N) is processed per channel. rate <= 0 raises ValueError.
    """
    if rate <= 0:
        raise ValueError(f"tempo.wsola: rate must be positive, got {rate}")
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0:
        return x.copy()
    if x.ndim == 2:
        return np.stack([_wsola_mono(ch, rate, window, hop, tolerance)
                         for ch in x])
    return _wsola_mono(x, rate, window, hop, tolerance)


def _spectral_flux_mean(x, n_fft=1024, hop=512):
    """Mean per-frame spectral flux -- the 'auto' road's only witness.

    DOCTRINE: a heuristic is allowed to decide, but it is not allowed
    to pretend it measured more than it did. High mean flux = energy
    keeps arriving in new places = transient-rich material.
    """
    x = np.asarray(x, dtype=np.float64)
    if len(x) < n_fft:
        return 0.0
    win = np.hanning(n_fft)
    frames = [np.abs(np.fft.rfft(x[i:i + n_fft] * win))
              for i in range(0, len(x) - n_fft + 1, hop)]
    if len(frames) < 2:
        return 0.0
    mags = np.stack(frames)
    scale = np.maximum(mags.max(), 1e-12)
    diffs = np.diff(mags / scale, axis=0)
    return float(np.mean(np.sqrt(np.sum(diffs ** 2, axis=1))))


def time_stretch(x, sr, rate, method="wsola"):
    """Stretch `x` by `rate` with pitch held, on the named road.

    method: 'wsola' (waveform road), 'vocoder' (the house phase
    vocoder), or 'auto' (spectral-flux heuristic: flux mean above
    0.35 -> WSOLA, else vocoder; the threshold is a documented
    heuristic, tuned on speech-vs-pad intuition, not a law).
    """
    if rate <= 0:
        raise ValueError(
            f"tempo.time_stretch: rate must be positive, got {rate}")
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0:
        return x.copy()
    if method == "auto":
        mono = x[0] if x.ndim == 2 else x
        method = "wsola" if _spectral_flux_mean(mono) > 0.35 else "vocoder"
    if method == "wsola":
        return wsola(x, rate)
    if method == "vocoder":
        if x.ndim == 2:
            return np.stack([phase_vocoder(ch, rate) for ch in x])
        return phase_vocoder(x, rate)
    raise ValueError(f"tempo.time_stretch: unknown method {method!r}")


def shift_pitch(x, sr, semitones, method="wsola"):
    """Shift pitch by `semitones` with duration (tempo) held.

    MECHANISM: varispeed resample by r (duration -> D/r, pitch ->
    pitch*r), then time-stretch by r on the chosen road (duration
    restored, pitch kept). The 'vocoder' road is the house
    resonance.pitch.pitch_shift itself. Output length equals input
    length exactly (the stretch product is trimmed/padded to it).

    Honest limit: no formant preservation on either road -- the
    spectral envelope rides with the pitch. Formant re-seating is
    resonance.vocal.formant_preserving_shift's office.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0 or semitones == 0:
        return x.copy()
    if method == "vocoder":
        return pitch_shift(x, sr, semitones)
    if method != "wsola":
        raise ValueError(f"tempo.shift_pitch: unknown method {method!r}")
    ratio = 2.0 ** (semitones / 12.0)

    def _shift_mono(mono):
        sped = _resample_linear(mono, 1.0 / ratio)   # pitch * ratio
        out = _wsola_mono(sped, ratio)               # duration restored
        n = len(mono)
        if len(out) < n:
            out = np.concatenate([out, np.zeros(n - len(out))])
        return out[:n]

    if x.ndim == 2:
        return np.stack([_shift_mono(ch) for ch in x])
    return _shift_mono(x)


# 93 — Live, Love, and let Love, Live.
