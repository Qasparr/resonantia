# 93
# ---------------------------------------------------------------------
# four_powers.py -- the Four Powers mastering chain, named and built.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XV day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: the founder's night work of 2026-11-14 named the house
# mastering chain by the Four Powers of the Sphinx, and his order of
# 2026-11-15 separated the mapping into this studio:
#
#   SCIRE  (Know)   -- metering / measurement: the BS.1770 K-weighted
#                      loudness and true peak the pipeline already
#                      weighs, now NAMED as the first power and
#                      recorded before anything touches the signal.
#   VELLE  (Will)   -- EQ + compression: the dynamic intent vector.
#                      This module builds it: a zero-phase FFT EQ
#                      (smooth analytic shelf/peak curves) and a
#                      block-based feedforward compressor, numpy
#                      only, conservative ranges, every refusal
#                      naming its field. Engaged only when a spec
#                      orders it; an unordered run is flat, and the
#                      manifest says flat.
#   AUDERE (Dare)   -- limiting: the existing master_signal law --
#                      loudness gained to target, soft limiting,
#                      then the true-peak ceiling enforced by trim.
#                      The ceiling outranks the loudness. This
#                      module does not re-implement it; it NAMES
#                      it and carries its measured report.
#   TACERE (Silent) -- headroom + dither: the ceiling/headroom
#                      accounting after Audere (headroom = ceiling
#                      minus delivered true peak, measured) and a
#                      TPDF dither at the 24-bit export word, so
#                      the silence at the bottom of the master is
#                      shaped noise, not truncation.
#
# Beside the four stands VAPOUR -- the founder's audio vapour,
# saturation: an optional tanh saturation stage, drive ordered in
# the spec and confessed in the manifest, OFF unless ordered.
#
# The module also carries the RGBA8888 metering map (R = Know,
# G = Dare, B = Will, A = Silent/Vapour) as manifest metadata for
# persona/metering displays: a documented display convention over
# measured values, never a measurement claim of its own.
#
# DOCTRINE: a stage that is not measured is not a stage, it is a
# rumor. Every function here returns its report beside its signal,
# and the manifest's four_powers section prints each power's
# measured values -- including "not engaged" when a power was not
# ordered, because an honest zero is worth more than a silent one.
# ---------------------------------------------------------------------

import math

import numpy as np

# The export word: masters strike as 24-bit PCM (see pipeline's
# finalize step), so the dither's least significant bit is 2^-23.
EXPORT_BITS = 24

# The house tuning reference as it stands: A4 = 440 Hz (resonance.
# core.notes is built on it). A spec may order another reference
# (the founder's 432 Hz lock) -- see pipeline.validate_spec's
# "tuning_hz" and arpeggio's render, the one synthesis path that
# consumes a reference today. Existing masters are never retuned.
HOUSE_TUNING_HZ = 440.0

EQ_BAND_TYPES = ("lowshelf", "peak", "highshelf")
_COMP_BLOCK = 256          # compressor gain blocks, in samples:
                           # ~5.3 ms at 48 kHz -- fine enough to
                           # ride a transient, coarse enough that
                           # the gain curve itself never becomes
                           # a waveform (no zipper, no pumping
                           # artifacts from the arithmetic).


# ---------------------------------------------------------------------
# Spec handling: the same contract style as the rest of the studio --
# every refusal names its field.
# ---------------------------------------------------------------------

def normalize_velle(raw):
    """Validate a spec's "velle" block; return the normal form.

    MECHANISM: Velle is EQ + compression, ordered as data: a list
    of EQ bands (type / freq_hz / gain_db, plus q for peaks) and
    an optional compressor (threshold / ratio / knee / attack /
    release / makeup). Ranges are conservative by design -- this
    is a mastering stage, not a sound-design box: EQ gains stop
    at +/-12 dB, ratios at 10:1, and a band that asks for more is
    refused by name rather than clipped into compliance. Absent
    (None), Velle is not engaged and the manifest records flat.
    """
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("velle: must be an object")
    bands = []
    raw_bands = raw.get("eq") or []
    if not isinstance(raw_bands, list) or len(raw_bands) > 8:
        raise ValueError("velle.eq: must be a list of at most 8 bands")
    for i, b in enumerate(raw_bands):
        if not isinstance(b, dict):
            raise ValueError(f"velle.eq[{i}]: must be an object")
        btype = b.get("type")
        if btype not in EQ_BAND_TYPES:
            raise ValueError(
                f"velle.eq[{i}].type: {btype!r} must be one of "
                f"{EQ_BAND_TYPES}")
        freq = float(b.get("freq_hz", 1000.0))
        if not 20.0 <= freq <= 18000.0:
            raise ValueError(
                f"velle.eq[{i}].freq_hz: {freq} outside 20..18000")
        gain = float(b.get("gain_db", 0.0))
        if not -12.0 <= gain <= 12.0:
            raise ValueError(
                f"velle.eq[{i}].gain_db: {gain} outside -12..12 "
                f"(a mastering stage, not a sound-design box)")
        q = float(b.get("q", 1.0))
        if not 0.3 <= q <= 6.0:
            raise ValueError(
                f"velle.eq[{i}].q: {q} outside 0.3..6")
        bands.append({"type": btype, "freq_hz": freq,
                      "gain_db": gain, "q": q})
    comp = None
    raw_comp = raw.get("comp")
    if raw_comp is not None:
        if not isinstance(raw_comp, dict):
            raise ValueError("velle.comp: must be an object")
        thr = float(raw_comp.get("threshold_db", -18.0))
        if not -48.0 <= thr <= 0.0:
            raise ValueError(
                f"velle.comp.threshold_db: {thr} outside -48..0")
        ratio = float(raw_comp.get("ratio", 2.0))
        if not 1.0 <= ratio <= 10.0:
            raise ValueError(
                f"velle.comp.ratio: {ratio} outside 1..10")
        knee = float(raw_comp.get("knee_db", 6.0))
        if not 0.0 <= knee <= 24.0:
            raise ValueError(
                f"velle.comp.knee_db: {knee} outside 0..24")
        attack = float(raw_comp.get("attack_ms", 10.0))
        if not 0.1 <= attack <= 250.0:
            raise ValueError(
                f"velle.comp.attack_ms: {attack} outside 0.1..250")
        release = float(raw_comp.get("release_ms", 120.0))
        if not 10.0 <= release <= 1000.0:
            raise ValueError(
                f"velle.comp.release_ms: {release} outside 10..1000")
        makeup = float(raw_comp.get("makeup_db", 0.0))
        if not 0.0 <= makeup <= 12.0:
            raise ValueError(
                f"velle.comp.makeup_db: {makeup} outside 0..12")
        comp = {"threshold_db": thr, "ratio": ratio, "knee_db": knee,
                "attack_ms": attack, "release_ms": release,
                "makeup_db": makeup}
    if not bands and comp is None:
        raise ValueError(
            "velle: an empty Velle orders nothing -- give it eq "
            "bands and/or a comp, or omit the block")
    return {"eq": bands, "comp": comp}


def normalize_vapour(raw):
    """Validate a spec's "vapour" block; return the normal form.

    MECHANISM: one number with a name -- drive_db, how hard the
    signal is pushed into the tanh curve. 0 (or an absent block)
    is OFF: the stage is not engaged and the signal passes
    untouched, because saturation the founder did not order is
    distortion with good PR. The ceiling of 24 dB keeps the stage
    a vapour, not a fuzz box.
    """
    if raw is None:
        return {"drive_db": 0.0}
    if not isinstance(raw, dict):
        raise ValueError("vapour: must be an object")
    drive = float(raw.get("drive_db", 0.0))
    if not 0.0 <= drive <= 24.0:
        raise ValueError(
            f"vapour.drive_db: {drive} outside 0..24")
    return {"drive_db": drive}


def normalize_tuning_hz(raw):
    """Validate a spec's "tuning_hz"; return the reference in Hz.

    MECHANISM: the tuning reference for the synthesis paths that
    consume one (today: the arpeggio's staff realization). The
    default is the house's standing practice, 440.0 -- a spec that
    does not mention tuning gets exactly the masters the house has
    always made. The range 400..480 covers the founder's 432 lock
    and every sane concert pitch; outside it, the field is named
    and refused. A tuning order never reaches backward: shipped
    masters and their manifests are not retuned, ever.
    """
    if raw is None:
        return HOUSE_TUNING_HZ
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise ValueError(f"tuning_hz: {raw!r} must be a number")
    value = float(raw)
    if not 400.0 <= value <= 480.0:
        raise ValueError(
            f"tuning_hz: {value} outside 400..480")
    return value


# ---------------------------------------------------------------------
# Small measures, shared by the stages' reports.
# ---------------------------------------------------------------------

def _rms_dbfs(x):
    """RMS of a (C, N) or (N,) signal, in dBFS (-120 for silence)."""
    a = np.asarray(x, dtype=np.float64)
    rms = float(np.sqrt(np.mean(a ** 2))) if a.size else 0.0
    return 20.0 * math.log10(rms) if rms > 0.0 else -120.0


def _peak_dbfs(x):
    """Sample peak of a signal, in dBFS (-120 for silence)."""
    a = np.asarray(x, dtype=np.float64)
    peak = float(np.max(np.abs(a))) if a.size else 0.0
    return 20.0 * math.log10(peak) if peak > 0.0 else -120.0


def _crest_db(x):
    """Crest factor: peak over RMS, in dB -- the dynamics' height."""
    return _peak_dbfs(x) - _rms_dbfs(x)


# ---------------------------------------------------------------------
# SCIRE -- Know: the measurement, taken before anything is touched.
# ---------------------------------------------------------------------

def scire_measure(samples, sr, measure_lufs, measure_tp):
    """Measure the pre-master signal; return Scire's report.

    MECHANISM: the pipeline's own scales are passed in (BS.1770
    K-weighted loudness and FFT-oversampled true peak -- this
    module names the power, it does not forge a second set of
    scales). Beside them stand the plain witnesses: sample peak,
    RMS, and the crest factor Velle's compressor will be judged
    against. Measured on the signal AS IT ARRIVES at the chain --
    post-mix, pre-EQ, pre-everything the chain does.
    """
    x = np.asarray(samples, dtype=np.float64)
    return {
        "stage": "metering / measurement (BS.1770)",
        "lufs_integrated": round(measure_lufs(x, sr), 2),
        "true_peak_dbtp": round(measure_tp(x, sr), 2),
        "sample_peak_dbfs": round(_peak_dbfs(x), 2),
        "rms_dbfs": round(_rms_dbfs(x), 2),
        "crest_db": round(_crest_db(x), 2),
    }


# ---------------------------------------------------------------------
# VELLE -- Will: EQ + compression, the dynamic intent vector.
# ---------------------------------------------------------------------

def _eq_response_db(freqs, bands):
    """The summed EQ magnitude curve, in dB, at the given freqs.

    MECHANISM: three smooth analytic shapes, summed in dB --
    lowshelf weight 1/(1+(f/fc)^2) (unity deep below fc, half at
    fc, gone above), highshelf its mirror, and a peak as a
    Gaussian in log2-frequency whose width the band's q sets
    (weight exp(-0.5 * (q * log2(f/fc))^2): half an octave out at
    q=2 the bump has fallen to ~0.61 of its height). Smooth
    everywhere, so the zero-phase FFT application below rings
    nowhere; conservative, so a mastering EQ cannot saw a mix in
    half. The DC bin takes the shelves' own limits by hand
    (log2(0) is not a frequency).
    """
    f = np.asarray(freqs, dtype=np.float64)
    total = np.zeros(f.shape, dtype=np.float64)
    safe = np.maximum(f, 1e-9)
    for band in bands:
        fc = band["freq_hz"]
        g = band["gain_db"]
        if band["type"] == "lowshelf":
            w = 1.0 / (1.0 + (safe / fc) ** 2)
        elif band["type"] == "highshelf":
            w = (safe / fc) ** 2 / (1.0 + (safe / fc) ** 2)
        else:  # peak
            w = np.exp(-0.5 * (band["q"]
                               * np.log2(safe / fc)) ** 2)
        total += g * w
    if f.size and f[0] == 0.0:
        dc = 0.0
        for band in bands:
            if band["type"] == "lowshelf":
                dc += band["gain_db"]
        total[0] = dc
    return total


def _apply_eq(samples, sr, bands):
    """Apply the EQ curve, zero-phase, per channel, via rfft.

    MECHANISM: the magnitude curve multiplies each channel's
    spectrum; phase is untouched (a mastering EQ on an offline
    render owes no latency and takes no phase liberties). The
    transform runs at the signal's own length; the result is cut
    back to the exact input length.
    """
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim == 1:
        x = x[np.newaxis, :]
    n = x.shape[1]
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    mag = 10.0 ** (_eq_response_db(freqs, bands) / 20.0)
    out = np.empty_like(x)
    for ch in range(x.shape[0]):
        out[ch] = np.fft.irfft(np.fft.rfft(x[ch]) * mag, n=n)
    return out


def _comp_gain_reduction_db(level_db, comp):
    """Static soft-knee gain reduction for one block level (dB).

    MECHANISM: the textbook curve -- no reduction below the knee's
    foot, full ratio above its head, a quadratic blend between:
    GR = (1/R - 1) * (x - T + K/2)^2 / (2K) inside the knee, and
    (1/R - 1) * (x - T) above it, where x is the block's level.
    Returns a non-positive number (a reduction), 0.0 at unity.
    """
    thr, ratio, knee = (comp["threshold_db"], comp["ratio"],
                        comp["knee_db"])
    over = level_db - thr
    if knee > 0.0 and over > -knee / 2.0 and over < knee / 2.0:
        return (1.0 / ratio - 1.0) * (over + knee / 2.0) ** 2 \
            / (2.0 * knee)
    if over >= knee / 2.0:
        return (1.0 / ratio - 1.0) * over
    return 0.0


def _apply_comp(samples, sr, comp):
    """Apply the compressor; return (signal, measured GR report).

    MECHANISM: stereo-linked and block-based. The signal is cut
    into _COMP_BLOCK-sample blocks; each block's level is the
    linked peak (max over channels) in dBFS; the static curve
    gives the block's target reduction; attack/release one-pole
    smoothing over blocks (time constants converted at the block
    rate) keeps the gain curve a curve, never a waveform; the
    per-sample gain is the linear interpolation of the block
    gains, so no sample ever hears a step. Makeup gain, when
    ordered, is plain gain applied after. The report's max/mean
    reduction are measured from the gain curve actually applied.
    """
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim == 1:
        x = x[np.newaxis, :]
    n = x.shape[1]
    n_blocks = int(math.ceil(n / _COMP_BLOCK))
    block_rate = sr / _COMP_BLOCK
    atk = math.exp(-1.0 / (comp["attack_ms"] / 1000.0 * block_rate))
    rel = math.exp(-1.0 / (comp["release_ms"] / 1000.0 * block_rate))
    targets = np.empty(n_blocks, dtype=np.float64)
    for b in range(n_blocks):
        seg = x[:, b * _COMP_BLOCK:(b + 1) * _COMP_BLOCK]
        peak = float(np.max(np.abs(seg))) if seg.size else 0.0
        level = 20.0 * math.log10(peak) if peak > 0.0 else -120.0
        targets[b] = _comp_gain_reduction_db(level, comp)
    smoothed = np.empty(n_blocks, dtype=np.float64)
    g = 0.0
    for b in range(n_blocks):
        coef = atk if targets[b] < g else rel
        g = coef * g + (1.0 - coef) * targets[b]
        smoothed[b] = g
    block_index = np.arange(n_blocks, dtype=np.float64)
    sample_pos = np.arange(n, dtype=np.float64) / _COMP_BLOCK
    gain_db = np.interp(sample_pos, block_index, smoothed)
    y = x * (10.0 ** (gain_db / 20.0))[np.newaxis, :]
    if comp["makeup_db"]:
        y = y * (10.0 ** (comp["makeup_db"] / 20.0))
    report = {
        **comp,
        "max_gain_reduction_db": round(float(-np.min(smoothed)), 2)
        if n_blocks else 0.0,
        "mean_gain_reduction_db": round(float(-np.mean(smoothed)), 2)
        if n_blocks else 0.0,
    }
    return y, report


def velle_stage(samples, sr, velle):
    """Run Velle (EQ, then compression); return (signal, report).

    MECHANISM: EQ before compression -- the will shapes the tone,
    then the dynamics are judged on the shaped signal, the order
    every mastering chain in the record books uses. A spec that
    ordered no Velle gets its signal back untouched with the
    report saying "not engaged" -- the power's absence is printed,
    never implied away. Deltas are measured across the whole
    stage so the manifest can weigh what the Will actually did.
    """
    x = np.asarray(samples, dtype=np.float64)
    if velle is None:
        return x.copy(), {"engaged": False, "eq": [], "comp": None,
                          "rms_delta_db": 0.0, "peak_delta_db": 0.0}
    y = x
    if velle["eq"]:
        y = _apply_eq(y, sr, velle["eq"])
    comp_report = None
    if velle["comp"] is not None:
        y, comp_report = _apply_comp(y, sr, velle["comp"])
    return y, {
        "engaged": True,
        "eq": velle["eq"],
        "comp": comp_report,
        "rms_delta_db": round(_rms_dbfs(y) - _rms_dbfs(x), 2),
        "peak_delta_db": round(_peak_dbfs(y) - _peak_dbfs(x), 2),
    }


# ---------------------------------------------------------------------
# VAPOUR -- saturation: the audio vapour, driven and confessed.
# ---------------------------------------------------------------------

def vapour_stage(samples, vapour):
    """Run the saturation stage; return (signal, report).

    MECHANISM: a tanh curve, the oldest soft clip in the book --
    y = tanh(g*x) / tanh(g), with g the linear drive. The
    normalization holds a full-scale sample at full scale, so the
    stage adds harmonics and density without ever handing Audere
    a hotter peak than it was given. Drive 0 (or no order) is
    OFF: the signal returns untouched and the report confesses
    the stage stood idle. Crest before/after is measured -- the
    vapour's whole audible claim is that the crest falls as the
    body rises, and the manifest prints both numbers.
    """
    x = np.asarray(samples, dtype=np.float64)
    drive = float(vapour["drive_db"]) if vapour else 0.0
    if drive <= 0.0:
        return x.copy(), {"engaged": False, "drive_db": 0.0,
                          "crest_before_db": round(_crest_db(x), 2),
                          "crest_after_db": round(_crest_db(x), 2),
                          "rms_delta_db": 0.0}
    g = 10.0 ** (drive / 20.0)
    y = np.tanh(g * x) / math.tanh(g)
    return y, {"engaged": True, "drive_db": drive,
               "crest_before_db": round(_crest_db(x), 2),
               "crest_after_db": round(_crest_db(y), 2),
               "rms_delta_db": round(_rms_dbfs(y) - _rms_dbfs(x), 2)}


# ---------------------------------------------------------------------
# TACERE -- Silent: headroom accounting + dither on export.
# ---------------------------------------------------------------------

def tpdf_dither(samples, seed, bits=EXPORT_BITS):
    """Add TPDF dither at the export word's LSB; return the signal.

    MECHANISM: triangular-probability-density noise -- the sum of
    two uniform draws, scaled to one LSB peak-to-peak at the
    export word (2^-(bits-1) full-scale step) -- added in the
    float domain just before the 24-bit strike, so the strike's
    rounding decorrelates from the signal instead of quantizing
    it. Seeded from the spec's seed: the same spec dithers the
    same way twice, because a master you cannot reproduce is a
    master you cannot audit.
    """
    rng = np.random.default_rng(int(seed))
    x = np.asarray(samples, dtype=np.float64)
    lsb = 2.0 ** (-(bits - 1))
    noise = (rng.random(x.shape) + rng.random(x.shape) - 1.0) * lsb
    return x + noise


def tacere_report(master_report, dither_applied):
    """Tacere's accounting, from Audere's measured master report.

    MECHANISM: headroom is what the ceiling still holds after the
    master is struck -- ceiling minus delivered true peak,
    measured, never assumed (the trim in master_signal buys at
    least a hair under the ceiling by construction; this prints
    the actual figure). The dither line confesses whether the
    export was dithered and at what word.
    """
    headroom = round(float(master_report["ceiling_dbtp"])
                     - float(master_report["true_peak_dbtp"]), 2)
    return {
        "stage": "headroom accounting + dither on export",
        "ceiling_dbtp": master_report["ceiling_dbtp"],
        "delivered_true_peak_dbtp": master_report["true_peak_dbtp"],
        "headroom_dbtp": headroom,
        "dither": {"applied": bool(dither_applied),
                   "type": "TPDF" if dither_applied else None,
                   "bits": EXPORT_BITS if dither_applied else None},
    }


# ---------------------------------------------------------------------
# The RGBA8888 metering map: measured values, displayed as colour.
# ---------------------------------------------------------------------

def _byte(value, lo, hi):
    """Clamp a measured value's linear map into a 0..255 byte."""
    if hi <= lo:
        return 0
    frac = (float(value) - lo) / (hi - lo)
    return int(round(255.0 * min(1.0, max(0.0, frac))))


def rgba8888_map(scire, master_report, tacere):
    """The RGBA8888 metering map over the chain's measured values.

    MECHANISM: the founder's channel map -- R = Know (Scire),
    G = Dare (Audere), B = Will (Velle's dynamics, read here as
    the pre-master crest Scire measured), A = Silent/Vapour
    (Tacere's headroom, the silence held in reserve). Each byte
    is a documented linear map of ONE measured number:
      R: integrated LUFS,        -48..0    -> 0..255
      G: delivered true peak,    -24..0    -> 0..255
      B: crest factor dB,          0..24   -> 0..255
      A: headroom dBTP,            0..12   -> 0..255
    A display convention for persona/metering faces -- it carries
    the measurements, it is not itself a measurement.
    """
    r = _byte(scire["lufs_integrated"], -48.0, 0.0)
    g = _byte(master_report["true_peak_dbtp"], -24.0, 0.0)
    b = _byte(scire["crest_db"], 0.0, 24.0)
    a = _byte(tacere["headroom_dbtp"], 0.0, 12.0)
    return {
        "R_know_scire": r, "G_dare_audere": g,
        "B_will_velle": b, "A_silent_vapour_tacere": a,
        "hex": f"#{r:02X}{g:02X}{b:02X}{a:02X}",
        "mapping": "R = integrated LUFS (-48..0), G = delivered "
                   "true peak dBTP (-24..0), B = crest dB (0..24), "
                   "A = headroom dBTP (0..12); linear, clamped -- "
                   "a display convention over measured values",
    }


# ---------------------------------------------------------------------
# Assembly: the manifest's four_powers section, all four named.
# ---------------------------------------------------------------------

def assemble(scire, velle_report, vapour_report, master_report,
             tacere):
    """Assemble the manifest's four_powers section from the reports.

    MECHANISM: Audere's numbers are read out of the pipeline's
    master report (the limiting law itself lives in
    pipeline.master_signal; this section NAMES it and prints its
    measured trim and ceiling verdict beside the other powers, so
    one block of the manifest tells the whole chain's story).
    """
    return {
        "scire": scire,
        "velle": velle_report,
        "audere": {
            "stage": "limiting (soft limit + true-peak ceiling "
                     "trim; the ceiling outranks the loudness)",
            "target_lufs": master_report["target_lufs"],
            "ceiling_dbtp": master_report["ceiling_dbtp"],
            "gain_applied_db": master_report["gain_applied_db"],
            "trim_db": master_report["trim_db"],
            "lufs_after": master_report["lufs_after"],
            "true_peak_dbtp": master_report["true_peak_dbtp"],
            "ceiling_overrode_loudness":
                master_report["ceiling_overrode_loudness"],
        },
        "tacere": tacere,
        "vapour": vapour_report,
        "rgba8888": rgba8888_map(scire, master_report, tacere),
    }


__all__ = [
    "EXPORT_BITS",
    "HOUSE_TUNING_HZ",
    "assemble",
    "normalize_tuning_hz",
    "normalize_vapour",
    "normalize_velle",
    "rgba8888_map",
    "scire_measure",
    "tacere_report",
    "tpdf_dither",
    "vapour_stage",
    "velle_stage",
]

# 93 -- Live, Love, and let Love, Live.
