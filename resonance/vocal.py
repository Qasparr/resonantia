# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# SPDX-License-Identifier: AGPL-3.0-only
# =============================================================================
# "Take the machine out of the voice. The slang, the accent, the
#  soul -- those are the artist, and no tool here touches them."
#
# 93.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
#
# DOCTRINE: this module's charter is narrow and it is stated in the
# spec it was built from -- NOT slang, NOT accent, NOT the words.
# Only the voicing tells: the artifacts by which a listener knows a
# machine sang it. Anything beyond that charter is another wing's
# business (recognition + resynthesis), and this module does not
# pretend to it. Method of Science, Aim of Religion.
# =============================================================================
"""resonance/vocal.py -- removing the machine's tells from a voice.

HYPOTHESIS
    A synthesized or over-processed vocal betrays itself in four
    measurable ways, none of them the words: (1) its pitch contour
    is inhumanly steady -- quantized flat lines where a throat would
    drift, scoop, and vibrate; (2) its formants ride with its pitch
    under naive shifting -- the chipmunk/mask tell; (3) its cycle-
    to-cycle jitter and shimmer sit outside the human band (usually
    at exactly zero, which no throat achieves); (4) its harmonic
    stack is over-even and buzzy, with no air around it. Each tell
    has a counter-tool, and the counter-tools work from the voice's
    OWN statistics -- the module imposes no foreign idea of how this
    singer should sound; it removes what no singer does.

METHOD
    track_f0_autocorr(x, sr, ...): the simple autocorrelation
        tracker the spec ordered -- per-frame normalized
        autocorrelation peak in the [fmin, fmax] lag band, parabolic
        refinement, voicing gated on peak strength and frame RMS.
        DOCUMENTED LIMITS, plainly: autocorrelation octave-errors on
        harmonic-rich voices (it will sometimes report f/2 or 2f),
        dissolves on breathy and polyphonic material, and its frame
        rate (hop 512) cannot see true cycle jitter. The corrective-
        grade tracker in this engine is YIN
        (resonance.pitch.track_f0); this one is the bench tracker --
        fast, transparent, and honest about its ceiling.
    measure_jitter_shimmer(f0, amps=None): frame-rate APPROXIMATIONS
        of the clinical cycle measures (successive-period and
        successive-amplitude relative variation). Labeled
        approximations wherever returned: a 512-sample hop smooths
        what a cycle counter would catch.
    humanize_contour(f0, hop_s, strength, seed): works in cents
        against the contour's own median. Adds (a) micro-drift: a
        low-passed random walk whose amplitude is the contour's own
        residual variation, floored at 12 cents and capped at 30 --
        a machine-flat contour gets the floor, a living one is not
        exaggerated past the cap; (b) vibrato on sustained voiced
        runs, rate/depth measured from the contour's own detrended
        spectrum when present (4-7.5 Hz band), else the human
        defaults 5.5 Hz / ~20 cents, with a 120 ms onset ramp
        because throats do not vibrate from the first cycle;
        (c) attack scoops at voiced onsets, approaching the note
        from up to ~70 cents below over ~90 ms -- the singer's
        approach, chosen and documented (some styles approach from
        above; below is the common case and this module's rule).
        Unvoiced frames stay unvoiced. Deterministic per seed.
    normalize_jitter_shimmer_contour(f0, amount): blends the log-f0
        contour toward its binomial-smoothed self by `amount`,
        pulling successive-period variation toward the human band.
        (A median filter was the first design and was rejected on
        measurement: median-3 phase-flips period-2 alternation
        instead of removing it, and cycle-rate wobble IS period-2
        alternation. A [1,2,1]/4 low-pass is the correct counter;
        it costs a little step sharpness, which the blend bounds.)
    psola_resynthesize(x, sr, f0_src, f0_dst, hop): a simplified
        TD-PSOLA grain engine -- the application path that turns a
        corrected contour back into sound. Pitch marks step by the
        source period (peak-aligned within half a period), grains
        are two-period Hann windows, re-laid at the target contour's
        spacing; unvoiced spans pass through as fixed-step grains.
        DOCUMENTED LIMITS: monophonic voiced material only; no
        peak-picking sophistication, no unvoiced/voiced boundary
        surgery; sibilance and breaths survive approximately, not
        perfectly. Bench grade, stated as such.
    humanize(x, sr, ...): track -> humanize_contour -> psola.
    formant_preserving_shift(x, sr, semitones): house pitch_shift
        first (envelope rides along -- the tell), then cepstral
        envelope re-seating: per STFT frame, the shifted signal's
        liftered log-envelope is pulled toward the ORIGINAL frame's
        envelope at the SAME frequencies (formants stay home while
        harmonics move). The pull is PARTIAL by default
        (correction=0.85) under a +/-36 dB safety clip -- both
        choices measured, not guessed: full replacement is exact on
        paper and unusable in practice, because the shifted
        signal's envelope valleys hold vocoder noise that a +40 dB
        correction faithfully amplifies into audibility. The lifter
        is 4 ms of quefrency: 1 ms (the first build) provably
        flattens two formants into one hill. Approximate -- real
        formant tracking is a roadmap item in the pitch wing too --
        but the chipmunk geometry is directly countered, and tests
        measure the peak coming home.
    debuzz(x, sr, amount): geometric blend of each STFT frame's
        magnitude toward its frequency-smoothed self; softens the
        over-even ripple of synthetic harmonic stacks AT THE
        SMOOTHING SCALE (~200 Hz at the default 9-bin width --
        finer comb structure is the analysis window's, not the
        voice's, and is not claimed). Phase kept.
    add_presence(x, sr, level_db=-42, seed): a deterministic breath
        layer -- band-limited noise (4-9 kHz) shaped by the
        signal's own amplitude envelope, mixed at level_db relative
        to signal RMS. Air, at the level of a quiet room, not an
        effect.

OBSERVATION
    On synthetic machine-voice stand-ins (perfectly steady harmonic
    stacks), the wing measures its own claims: humanized contours
    gain cents-variation in the human range with the mean unmoved;
    jitter falls toward the band under normalization; formant peaks
    of a shifted synthetic vowel stay near home while the naive
    shift drags them up by the full ratio. On real throats the
    tools are corrective, not creative -- a living contour is
    already inside every band this module enforces, and passes
    nearly untouched. That is the design: the module's silence on
    human material is its correctness.

RESULT
    Contour tools over numpy arrays (NaN = unvoiced); audio tools
    over numpy arrays, sr explicit, stereo per channel. numpy only,
    composing the house pitch engines where they exist.

No medical or therapeutic claims are made about anything voiced here.
"""

import numpy as np

from resonance.pitch.shift import _istft, _stft, pitch_shift

__all__ = [
    "track_f0_autocorr",
    "measure_jitter_shimmer",
    "humanize_contour",
    "normalize_jitter_shimmer_contour",
    "psola_resynthesize",
    "humanize",
    "formant_preserving_shift",
    "debuzz",
    "add_presence",
]


# ---------------------------------------------------------------- F0

def track_f0_autocorr(x, sr, fmin=60.0, fmax=450.0, frame_size=2048,
                      hop=512, voicing_threshold=0.55, rms_floor=1e-4):
    """Autocorrelation F0 track; returns (f0_hz, voiced) arrays.

    f0_hz is NaN where unvoiced. See the module docstring for this
    tracker's documented limits (octave errors, breath, polyphony)
    and for the corrective-grade YIN alternative in resonance.pitch.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        x = x[0]
    if len(x) < frame_size:
        return np.array([]), np.array([], dtype=bool)
    min_lag = max(1, int(sr / fmax))
    max_lag = min(frame_size // 2, int(sr / fmin))
    n_frames = 1 + (len(x) - frame_size) // hop
    f0 = np.full(n_frames, np.nan)
    voiced = np.zeros(n_frames, dtype=bool)
    win = np.hanning(frame_size)
    for i in range(n_frames):
        frame = x[i * hop:i * hop + frame_size] * win
        if np.sqrt(np.mean(frame ** 2)) < rms_floor:
            continue
        # Normalized autocorrelation via FFT.
        size = 1
        while size < 2 * frame_size:
            size *= 2
        spec = np.fft.rfft(frame, size)
        ac = np.fft.irfft(spec * np.conj(spec), size)[:max_lag + 1]
        if ac[0] <= 0:
            continue
        acn = ac / ac[0]
        seg = acn[min_lag:max_lag + 1]
        lag = int(np.argmax(seg)) + min_lag
        if acn[lag] < voicing_threshold:
            continue
        # Parabolic refinement around the peak.
        if 0 < lag < max_lag:
            a, b, c = acn[lag - 1], acn[lag], acn[lag + 1]
            denom = a - 2 * b + c
            if denom != 0:
                lag = lag + float(np.clip(0.5 * (a - c) / denom, -1, 1))
        f0[i] = sr / lag
        voiced[i] = True
    return f0, voiced


def _cents(f0, ref):
    return 1200.0 * np.log2(f0 / ref)


def measure_jitter_shimmer(f0, amps=None):
    """Frame-rate jitter/shimmer approximations from a contour.

    jitter_pct: mean |T_i - T_{i-1}| / mean(T) over voiced runs, in
    percent (T = 1/f0). shimmer_pct: the same construction over the
    per-frame amplitude contour, when given. Both are labeled
    approximations -- a hop-sampled contour smooths true cycle
    variation, so these read LOW against clinical cycle measures.
    NaN-safe: unvoiced frames break runs rather than polluting them.
    """
    f0 = np.asarray(f0, dtype=np.float64)
    out = {"jitter_pct": float("nan"), "shimmer_pct": float("nan")}

    def _variation(values):
        vals = []
        run = []
        for v in values:
            if np.isfinite(v) and v > 0:
                run.append(v)
            else:
                if len(run) > 2:
                    r = np.asarray(run)
                    vals.append(np.mean(np.abs(np.diff(r))) / np.mean(r))
                run = []
        if len(run) > 2:
            r = np.asarray(run)
            vals.append(np.mean(np.abs(np.diff(r))) / np.mean(r))
        return float(100.0 * np.mean(vals)) if vals else float("nan")

    periods = np.where(np.isfinite(f0) & (f0 > 0), 1.0 / np.where(
        np.isfinite(f0) & (f0 > 0), f0, 1.0), np.nan)
    out["jitter_pct"] = _variation(periods)
    if amps is not None:
        out["shimmer_pct"] = _variation(np.asarray(amps, dtype=np.float64))
    return out


# ------------------------------------------------------- humanization

def _voiced_runs(voiced):
    """Yield (start, end) half-open runs of True in a bool array."""
    runs = []
    i = 0
    n = len(voiced)
    while i < n:
        if voiced[i]:
            j = i
            while j < n and voiced[j]:
                j += 1
            runs.append((i, j))
            i = j
        else:
            i += 1
    return runs


def humanize_contour(f0, hop_s, strength=1.0, seed=0):
    """Return a humanized copy of an F0 contour (NaN = unvoiced).

    Adds micro-drift, vibrato, and attack scoops in the cents
    domain, sized from the contour's own statistics and clamped to
    human ranges; see the module docstring for the exact rules.
    Deterministic for a given seed. Melody (the contour's own large
    motion) is preserved: only the fine structure is the tool's.
    """
    f0 = np.asarray(f0, dtype=np.float64)
    out = f0.copy()
    voiced = np.isfinite(f0) & (f0 > 0)
    if voiced.sum() < 8:
        return out
    ref = float(np.median(f0[voiced]))
    cents = np.where(voiced, _cents(np.where(voiced, f0, ref), ref), 0.0)
    rng = np.random.RandomState(seed)
    n = len(f0)
    # Residual variation: detrend each run lightly (subtract a wide
    # moving average) so melody doesn't inflate the drift budget.
    resid = cents.copy()
    k = max(3, int(round(0.25 / hop_s)) | 1)  # ~250 ms window, odd
    kernel = np.ones(k) / k
    smooth = np.convolve(cents, kernel, mode="same")
    resid[voiced] = (cents - smooth)[voiced]
    own_std = float(np.std(resid[voiced])) if voiced.any() else 0.0
    drift_amp = float(np.clip(own_std, 12.0, 30.0)) * strength
    # Micro-drift: low-passed random walk, normalized to drift_amp.
    walk = np.cumsum(rng.randn(n))
    walk = np.convolve(walk, kernel, mode="same")
    wstd = float(np.std(walk)) or 1.0
    drift = walk / wstd * drift_amp
    # MECHANISM: de-mean the drift over the voiced frames. Micro-
    # drift redistributes pitch around the melody; it must never
    # transpose it -- a random walk's local mean is not zero, so
    # the mean is removed explicitly rather than trusted away.
    drift = drift - float(np.mean(drift[voiced]))
    new_cents = cents + drift * voiced
    # Vibrato + scoops, per sustained voiced run.
    for s, e in _voiced_runs(voiced):
        dur = (e - s) * hop_s
        if dur < 0.35:
            continue
        seg = cents[s:e] - np.mean(cents[s:e])
        # Existing vibrato: strongest spectral peak in 4-7.5 Hz.
        spec = np.abs(np.fft.rfft(seg * np.hanning(e - s)))
        freqs = np.fft.rfftfreq(e - s, hop_s)
        band = (freqs >= 4.0) & (freqs <= 7.5)
        depth = 0.0
        rate = 5.5
        if band.any() and spec[band].max() > 0:
            peak = int(np.argmax(spec[band]))
            rate = float(freqs[band][peak])
            depth = float(2.0 * spec[band][peak] / max(1, (e - s) / 2))
        target_depth = float(np.clip(max(depth, 20.0), 0.0, 45.0))
        target_depth *= strength
        t = np.arange(e - s) * hop_s
        ramp = np.clip(t / 0.12, 0.0, 1.0)  # 120 ms vibrato onset
        vib = target_depth * np.sin(2 * np.pi * rate * t) * ramp
        # Attack scoop: approach from below, ~90 ms recovery.
        scoop = -70.0 * strength * np.exp(-t / 0.03)
        new_cents[s:e] += vib + scoop
    out[voiced] = ref * 2.0 ** (new_cents[voiced] / 1200.0)
    return out


def normalize_jitter_shimmer_contour(f0, amount=0.7):
    """Blend log-f0 toward its binomial-smoothed self by `amount`.

    Per voiced run, the target is the [1,2,1]/4 low-pass of the log
    contour (edges held); blending in the log domain moves pitch
    ratios, not pitch differences. amount=1 applies two passes,
    lesser amounts one -- alternation amplitude roughly halves per
    pass while phrase-scale melody (many frames wide) passes
    nearly untouched. amount=0 returns the input. See
    measure_jitter_shimmer to read the before/after.
    """
    if not 0.0 <= amount <= 1.0:
        raise ValueError(
            f"vocal: amount must be in [0, 1], got {amount}")
    f0 = np.asarray(f0, dtype=np.float64)
    out = f0.copy()
    voiced = np.isfinite(f0) & (f0 > 0)
    passes = 2 if amount >= 0.99 else 1
    for s, e in _voiced_runs(voiced):
        if e - s < 3:
            continue
        logf = np.log(f0[s:e])
        for _ in range(passes):
            sm = logf.copy()
            sm[1:-1] = (logf[:-2] + 2.0 * logf[1:-1] + logf[2:]) / 4.0
            logf = logf * (1.0 - amount) + sm * amount
        out[s:e] = np.exp(logf)
    return out


# ------------------------------------------------------------- PSOLA

def psola_resynthesize(x, sr, f0_src, f0_dst, hop=512):
    """Simplified TD-PSOLA: re-lay `x`'s grains on f0_dst's spacing.

    f0_src / f0_dst are per-frame contours (hop samples apart, NaN =
    unvoiced), e.g. from track_f0_autocorr and humanize_contour.
    Limits are documented in the module docstring -- bench grade,
    monophonic voiced material.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        x = x[0]
    n = len(x)
    if n == 0 or len(f0_src) == 0:
        return x.copy()

    def _f0_at(contour, pos):
        i = int(pos // hop)
        if i < 0 or i >= len(contour):
            return np.nan
        return contour[i]

    # Source marks: step by the source period through voiced spans
    # (peak-aligned within half a period); fixed hop steps elsewhere.
    marks = []          # (position, voiced_flag)
    pos = float(hop)
    while pos < n - hop:
        f = _f0_at(f0_src, pos)
        if np.isfinite(f) and f > 0:
            period = sr / f
            lo = max(0, int(pos - period / 2))
            hi = min(n, int(pos + period / 2))
            if hi > lo:
                pos = float(lo + int(np.argmax(np.abs(x[lo:hi]))))
            marks.append((pos, True))
            pos += period
        else:
            marks.append((pos, False))
            pos += hop
    if not marks:
        return x.copy()
    out = np.zeros(n + sr)  # slack; trimmed at the end
    wsum = np.zeros_like(out)
    tpos = marks[0][0]
    for k, (mpos, was_voiced) in enumerate(marks):
        f_src = _f0_at(f0_src, mpos)
        period = sr / f_src if (was_voiced and np.isfinite(f_src)
                                and f_src > 0) else float(hop)
        half = int(period)
        lo = max(0, int(mpos) - half)
        hi = min(n, int(mpos) + half)
        grain = x[lo:hi] * np.hanning(hi - lo)
        o = int(round(tpos)) - half
        if o + len(grain) > len(out):
            break
        if o >= 0:
            out[o:o + len(grain)] += grain
            wsum[o:o + len(grain)] += np.hanning(hi - lo)
        # Advance the target clock by the TARGET period at this time.
        f_dst = _f0_at(f0_dst, mpos)
        if was_voiced and np.isfinite(f_dst) and f_dst > 0:
            tpos += sr / f_dst
        else:
            tpos += period
        if tpos > n:
            break
    # Gain staging: divide by the window sum where grains actually
    # landed (two-period Hann grains at one-period spacing sum to
    # ~1 in steady material, so this is near-unity there and only
    # rescues the sparse edges). Trim/pad to the input length.
    nz = wsum > 1e-8
    out[nz] /= wsum[nz]
    if len(out) < n:
        out = np.concatenate([out, np.zeros(n - len(out))])
    return out[:n]


def humanize(x, sr, strength=1.0, seed=0):
    """Track, humanize the contour, and resynthesize. See docstrings.

    Returns the corrected audio, same length as the input. Stereo
    is processed per channel with the SAME contour decisions per
    channel (channels are tracked independently -- documented).
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        return np.stack([humanize(ch, sr, strength, seed) for ch in x])
    f0, _ = track_f0_autocorr(x, sr)
    if len(f0) == 0 or not np.isfinite(f0).any():
        return x.copy()
    hop_s = 512 / float(sr)
    dst = humanize_contour(f0, hop_s, strength=strength, seed=seed)
    return psola_resynthesize(x, sr, f0, dst, hop=512)


# ----------------------------------------------------------- formants

def _cepstral_envelope(mag, lifter):
    """Log spectral envelope via cepstral liftering of one frame."""
    logmag = np.log(np.maximum(mag, 1e-12))
    cep = np.fft.irfft(logmag)
    cep[lifter:-lifter] = 0.0
    return np.fft.rfft(cep).real


def formant_preserving_shift(x, sr, semitones, lifter_ms=4.0,
                             correction=0.85, max_gain_db=36.0):
    """Pitch-shift with formants re-seated at their home frequencies.

    MECHANISM: house pitch_shift moves everything (the tell). Then,
    per STFT frame, the shifted spectrum's cepstral envelope is
    pulled toward the ORIGINAL frame's envelope at the same
    frequencies by `correction` (0..1 in the log domain), under a
    +/- max_gain_db safety clip -- harmonics move, the vocal
    tract's resonances stay home. Stereo per channel. Approximate
    by design, and partial by MEASURED necessity (see the module
    docstring on valley-noise amplification at full correction).
    """
    if not 0.0 <= correction <= 1.0:
        raise ValueError(
            f"vocal: correction must be in [0, 1], got {correction}")
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        return np.stack([formant_preserving_shift(
            ch, sr, semitones, lifter_ms, correction, max_gain_db)
            for ch in x])
    if x.size == 0 or semitones == 0:
        return x.copy()
    shifted = pitch_shift(x, sr, semitones)
    n_fft, hop = 2048, 512
    spec_o = _stft(x, n_fft, hop)
    spec_s = _stft(shifted, n_fft, hop)
    frames = min(spec_o.shape[1], spec_s.shape[1])
    if frames == 0:
        return shifted
    lifter = max(2, int(sr * lifter_ms / 1000.0))
    cap = max_gain_db / 20.0 * np.log(10.0)
    out = spec_s[:, :frames].copy()
    for i in range(frames):
        env_o = _cepstral_envelope(np.abs(spec_o[:, i]), lifter)
        env_s = _cepstral_envelope(np.abs(spec_s[:, i]), lifter)
        gain = np.exp(np.clip(correction * (env_o - env_s), -cap, cap))
        out[:, i] = spec_s[:, i] * gain
    return _istft(out, n_fft, hop, length=len(x))


# --------------------------------------------------- de-buzz / air

def debuzz(x, sr, amount=0.5, smooth_bins=9):
    """Soften over-even synthetic harmonic ripple in the spectrum.

    MECHANISM: per STFT frame, magnitude is geometrically blended
    toward a frequency-smoothed copy of itself by `amount`; phase
    untouched. Real formant structure (broad) survives the
    smoothing width; sample-to-sample spectral evenness (the buzz)
    does not. amount in [0, 1]; 0 returns the input.
    """
    if not 0.0 <= amount <= 1.0:
        raise ValueError(f"vocal.debuzz: amount in [0,1], got {amount}")
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        return np.stack([debuzz(ch, sr, amount, smooth_bins) for ch in x])
    if x.size == 0 or amount == 0.0:
        return x.copy()
    n_fft, hop = 2048, 512
    spec = _stft(x, n_fft, hop)
    if spec.shape[1] == 0:
        return x.copy()
    mag = np.abs(spec)
    kernel = np.ones(smooth_bins) / smooth_bins
    smooth = np.apply_along_axis(
        lambda c: np.convolve(c, kernel, mode="same"), 0, mag)
    new_mag = mag ** (1.0 - amount) * np.maximum(smooth, 1e-12) ** amount
    out = new_mag * np.exp(1j * np.angle(spec))
    return _istft(out, n_fft, hop, length=len(x))


def add_presence(x, sr, level_db=-42.0, seed=0):
    """Add a deterministic low-level breath/air layer. See docstring.

    MECHANISM: seeded white noise, band-shaped to 4-9 kHz by an FFT
    mask, amplitude-followed to the signal's own smoothed envelope
    (so the air breathes WITH the phrase, not over the silences),
    and mixed at level_db relative to the signal's RMS.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        return np.stack([add_presence(ch, sr, level_db, seed)
                         for ch in x])
    if x.size == 0:
        return x.copy()
    rng = np.random.RandomState(seed)
    noise = rng.randn(len(x))
    spec = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(len(x), 1.0 / sr)
    mask = (freqs >= 4000.0) & (freqs <= 9000.0)
    noise = np.fft.irfft(spec * mask, len(x))
    # Envelope following: smoothed |x|, normalized to its own peak.
    k = max(3, int(sr * 0.01) | 1)
    env = np.convolve(np.abs(x), np.ones(k) / k, mode="same")
    peak = env.max() or 1.0
    env = env / peak
    layer = noise * env
    lrms = np.sqrt(np.mean(layer ** 2)) or 1.0
    xrms = np.sqrt(np.mean(x ** 2))
    gain = (10.0 ** (level_db / 20.0)) * xrms / lrms
    return x + gain * layer


# 93 — Live, Love, and let Love, Live.
