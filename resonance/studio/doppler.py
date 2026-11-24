#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — studio/doppler.py — the DOPPLER seat: the geometry
# of the Doppler effect seated in the Python studio — the observed
# frequency and the front/back wavelengths of a moving source, the
# Mach number, the Mach cone's half-angle, the plate's three
# regimes, a constant-velocity shift render, and a straight-line
# pass-by render whose pitch glides by the pass's own geometry.
#
# Epigraph: "When source speed exceeds wave speed (M > 1),
# overlapping wavefronts form a conical shock wave."
# — the plate the founder brought to the desk (XXIV Nov 2026),
#   "The geometry of the Doppler effect": how source motion
#   compresses wavefronts into frequency shifts and Mach cones.
#
# 93.
# Date: 24 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
#   Hypothesis: that wavefront compression — the same ratio
#     arithmetic the UPSCALE seat already swears by, read as
#     motion instead of evaluation — gains its true seat as ONE
#     named instrument: the plate's formula, the plate's three
#     regimes, and two renders (constant shift, pass-by glide)
#     whose pitch is proven by measurement on the house's sworn
#     frequency instrument, studio/fourier.py, never asserted
#     from the construction.
#   Method: the classical (non-relativistic) Doppler law in
#     units where the wave speed is the caller's — v_sound
#     defaults to 1.0 and air's 343 m/s is a caller's choice,
#     never baked in. The renders evaluate the handed waveform
#     at Doppler-warped positions by a Kaiser-windowed sinc
#     (β = 10.0, half-width 10 source samples — the upscale
#     seat's own sworn window and seam span), the shift at a
#     constant ratio, the pass-by at the cumulative phase of
#     its instantaneous ratio. Every singularity is refused by
#     name, with its regime named in the refusal: at M = 1 the
#     plate's pile-up, above it the cone that replaces the
#     frequency as the right instrument.
#   Observation: on the sworn signals the seat is exact where
#     the mathematics is exact. observed_frequency at M = 0.5
#     returns 2·f0 and, receding, f0/1.5; the plate's
#     wavelengths at M = 0.5 are 0.5λ0 and 1.5λ0 exactly;
#     sin(mach_angle) at the plate's M = 1.6 returns 0.625.
#     The shift render, measured on the Fourier seat: a
#     whole-cycle 1 kHz tone at M = 0.5 approach reads exactly
#     2000.0 Hz at magnitude 0.500000, its steady whole-cycle
#     centre floored at the house floor, −120.0 dB above
#     3 kHz; receding it reads 666.6759 Hz against the
#     analytic 666.6667 — inside one output bin (0.6667 Hz),
#     the record holding exactly 1,000 cycles — at magnitude
#     0.499845, and a constant signal renders flat to
#     ±3.5e-6. The pass-by's ratio anchors are exact (→ 2.0
#     and → 2/3 at the far ends, exactly 1 at the tangent
#     point), and its STFT-measured glide holds every frame
#     within 11.67 Hz — half a bin — of the analytic
#     instantaneous frequency across the sounded span. One
#     coordinate at full size: the cumulative phase consumes
#     source time faster than the file on the approach half,
#     so a finite source is exhausted before the render ends
#     — in the sworn geometry (4 s tone, v_source = 0.5,
#     distance 0.25, v_sound = 1) τ reaches the source's
#     4.0 s at t = +0.7742 s, the last sounded sample stands
#     at exactly that instant, and the render is exactly
#     silent after it; the exhaustion instant is computable
#     from τ before a sample is rendered, and the tests
#     swear it rather than hide it. The full battery stands
#     in tests/test_studio_doppler.py.
#   Result: this module. Nothing else in the studio was
#     touched: no pipeline wiring, no call site adopted — the
#     seat stands on the bench, deliberately unwired, ready
#     for the work that calls it.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""The Doppler effect, seated as a named studio instrument.

DOCTRINE — THE PLATE'S GEOMETRY, STATED PLAINLY:
  A source that moves while it sounds lays its wavefronts down
unevenly: compressed ahead of the motion, stretched behind it.
The observer's frequency is the wave speed read against that
uneven spacing, and the plate's one formula carries the whole
doctrine:

    f_obs = f0 · (v + v_observer) / (v − v_source)

with v the wave speed in the medium and both velocities signed
by the seat's convention (below). Ahead of an approaching
source the wavelength is λ′ = λ0(1 − M) and behind it
λ″ = λ0(1 + M), M = v_source/v the Mach number. The plate's
three regimes bound the seat:

  * SUBSONIC (M < 1): wavefronts nest; the shift is a smooth
    ratio and this seat's formulae are the whole story.
  * SONIC (M = 1): every forward crest piles up at one tangent
    point — the plate's "infinite constructive pile-up at
    nose." The shifted frequency diverges; a frequency is the
    wrong instrument at the wall, and the seat refuses there
    by name rather than return an infinity dressed as a
    number.
  * SUPERSONIC (M > 1): the source outruns its own wave and
    the fronts' envelope is a cone, half-angle θ_M with
    sin θ_M = v/v_source = 1/M. Ahead of the cone no wave has
    arrived; the cone, not a frequency, is the answer there —
    so the seat refuses a shift and seats mach_angle instead.

SIGN LAW (the convention every function here keeps):
  Velocities are signed by CLOSING. A positive v_source is a
source moving toward the observer; a positive v_observer is
an observer moving toward the source; negative values recede.
The medium is still (no wind term is seated). The law is the
classical one — exact for sound in a still medium at the
speeds a studio renders; the relativistic form is a different
seat with a different name, and is not approximated here.

MEDIUM LAW: the seat is medium-agnostic. v_sound defaults to
1.0, so velocities may be handed in as fractions of the wave
speed itself (v_source = 0.5 is M = 0.5 in any medium). Air's
343 m/s, water's, a string's — the caller names the medium by
naming v_sound; nothing about air is baked into the seat.

MECHANISM — THE RENDERS:
  shift() renders a constant radial velocity: the observed
waveform is the source waveform read at positions p = r·n,
where r = v_sound/(v_sound − v_source) is the same ratio
observed_frequency returns divided by f0. The output holds
floor((N−1)/r) + 1 samples — the same cycles in 1/r the
duration, which is the physics of a wave train arriving
compressed or stretched, stated as a count, not hidden.

  passby() renders a straight-line pass: the source travels
at v_source past a stationary observer whose closest-approach
distance is `distance`, t = 0 at the tangent point, seated at
the CENTRE of the handed signal (hand a signal whose middle
is the pass's middle). The instantaneous ratio is
r(t) = v_sound/(v_sound + v_r(t)) with the radial (range-rate)
velocity v_r(t) = v_source·x(t)/sqrt(x(t)² + distance²),
x(t) = v_source·t — negative while the range closes, zero at
the tangent point, positive as it opens. The render reads the
source at the CUMULATIVE PHASE τ(t) = ∫ r dt of that ratio:
pitch crosses f0 exactly at closest approach and glides from
the approach ratio to the recession ratio as the pass runs.
PITCH GEOMETRY ONLY: no 1/R amplitude law is applied — how
loud a pass is, is a mix decision, not wave geometry, and
this seat does not smuggle it in. The render returns the
handed signal's own sample count; on the approach half the
cumulative phase consumes the source faster than real time,
and what it reads past the source's end is the silence
outside a finite file (the seam law, below).

MECHANISM — THE EVALUATION (the upscale seat's window):
  Both renders evaluate the waveform between its samples by
a Kaiser-windowed sinc: β = 10.0, half-width 10 source
samples — the window the upscale seat measured to a −109.7 dB
image floor and swears at −90 dB. A Doppler render is that
same evaluation read along a warped path; it inherits the
window, and its proofs are MEASURED on the Fourier seat, so
the render argues with no second yardstick.

THE SEAM — WHERE THE EVALUATION IS NOT THE INTERIOR:
  The kernel is finite (10 source samples to each side). At
the first and last 10 source samples of a render the kernel
runs out of program and reconstructs against the silence
outside the file — the truth of a finite file, but a
different truth from the interior's. The proofs therefore
measure steady segments and whole-cycle tones, and any
coordinate the seam moves is printed in the tests' and the
module's numbers at full size, never smoothed.

SHAPE LAW (refusals by name, the house's law):
  * Every scalar is one finite number; booleans, non-numbers,
    and non-finite values are refused by name. v_sound must
    be positive; f0 and lambda0 must be positive.
  * A signal is a real, finite, 1-D array of at least 2
    samples — the Fourier seat's own shape law, kept so the
    seats agree about what a signal is. Complex input is
    refused before conversion; channels are handed one at a
    time.
  * A closing source at v_source ≥ v_sound is refused by
    name, its regime named (sonic pile-up at equality,
    supersonic cone above it). An observer receding at
    v_observer ≤ −v_sound is refused by name: the wave train
    never catches that observer, and a negative frequency
    would be a fiction. mach_angle below M = 1 is refused:
    no cone exists subsonically, and the refusal IS the
    boundary coordinate. A pass at distance ≤ 0 is refused
    (the line runs through the observer; the radial geometry
    is singular there), as is a pass at v_source ≤ 0 (no
    pass) or v_source ≥ v_sound (a cone problem, not a
    glide).
"""

import math
from typing import Tuple, Union

import numpy as np

__all__ = [
    "DopplerError",
    "KAISER_BETA",
    "KERNEL_HALF_WIDTH",
    "observed_frequency",
    "wavelength_front_back",
    "mach_number",
    "mach_angle",
    "mach_angle_rad",
    "regime",
    "passby_radial_velocity",
    "passby_ratio",
    "shift",
    "passby",
]


class DopplerError(ValueError):
    """A velocity, frequency, or signal refused by name.

    Subclasses ValueError so existing house code that catches
    ValueError around numeric work catches this too; the tests
    assert DopplerError itself, so a refusal can never pass
    silently as some other error — and a singularity can never
    pass as a number.
    """


# The Kaiser window's beta and the kernel's half-width in
# source samples — the upscale seat's sworn pair (β = 10.0
# measured −109.7 dB of image floor there; half-width 10 is
# its seam span), kept here so the two evaluation seats argue
# with one window, not two.
KAISER_BETA = 10.0
KERNEL_HALF_WIDTH = 10


def _as_number(value, name: str) -> float:
    """MECHANISM: bring a caller's scalar under the shape law.

    One finite number; booleans are refused as what they are
    (a flag, not a velocity), non-numbers and non-finite
    values by name — an axis built on them is fiction.
    """
    if isinstance(value, bool) or \
            not isinstance(value, (int, float, np.integer,
                                  np.floating)):
        raise DopplerError(f"{name}: not a number; got "
                           f"{type(value).__name__}")
    number = float(value)
    if not np.isfinite(number):
        raise DopplerError(f"{name}: must be finite; got "
                           f"{number}")
    return number


def _as_sound_speed(v_sound) -> float:
    """MECHANISM: the wave speed is one positive number.

    A medium whose wave speed is zero or negative carries no
    wavefronts to compress; refused by name before any ratio
    is seated on it.
    """
    v = _as_number(v_sound, "v_sound")
    if v <= 0.0:
        raise DopplerError(f"v_sound: the wave speed must be "
                           f"positive; got {v}")
    return v


def _as_signal(samples, name: str = "signal") -> np.ndarray:
    """MECHANISM: bring a caller's signal under the shape law.

    The Fourier seat's law, kept verbatim in substance: a
    real, finite, 1-D array of at least 2 samples. Complex
    input is refused before conversion (an imaginary part is
    never silently dropped), as are empty, non-finite,
    non-numeric, and multi-channel arrays.
    """
    if np.iscomplexobj(samples):
        raise DopplerError(f"{name}: complex signals are "
                           "refused — this seat renders real "
                           "waveforms; hand the real channel")
    try:
        arr = np.asarray(samples, dtype=float)
    except (TypeError, ValueError) as exc:
        raise DopplerError(f"{name}: not a real numeric array "
                           f"({exc})") from exc
    if arr.ndim != 1:
        raise DopplerError(f"{name}: a signal is 1-D; got "
                           f"{arr.ndim}-D — hand one channel "
                           "at a time")
    if arr.size < 2:
        raise DopplerError(f"{name}: {arr.size} sample(s); a "
                           "render needs at least 2")
    if not np.all(np.isfinite(arr)):
        raise DopplerError(f"{name}: non-finite samples are "
                           "refused — every rendered sample "
                           "would inherit the fiction")
    return arr


def _as_rate(sample_rate, name: str = "sr") -> float:
    """MECHANISM: a sample rate is one positive, finite number."""
    rate = _as_number(sample_rate, name)
    if rate <= 0.0:
        raise DopplerError(f"{name}: must be positive; got "
                           f"{rate}")
    return rate


def _refuse_closing_singularity(v_source: float, v_sound: float,
                                seat: str) -> None:
    """MECHANISM: the closing singularity, refused with its regime.

    At v_source = v_sound the denominator of the plate's
    formula is the sonic wall: every forward crest arrives at
    once and the shifted frequency diverges — the plate's
    pile-up. Above it the source outruns its own wave and the
    cone is the answer. Both are refused by name here, the
    regime named in the message, so no caller can mistake the
    boundary for a number.
    """
    if v_source == v_sound:
        raise DopplerError(
            f"{seat}: v_source == v_sound (M = 1, the sonic "
            "regime) — every forward wavefront piles up at the "
            "nose at once and the shifted frequency diverges; "
            "a frequency is the wrong instrument at the wall")
    if v_source > v_sound:
        raise DopplerError(
            f"{seat}: v_source = {v_source} exceeds v_sound = "
            f"{v_sound} (M = {v_source / v_sound:g}, the "
            "supersonic regime) — the source outruns its own "
            "wave; ahead of the Mach cone no wave has arrived, "
            "and the cone (mach_angle) is the answer there, "
            "not a frequency")


def observed_frequency(f0, v_source, v_observer=0.0,
                       v_sound=1.0) -> float:
    """The plate's formula: f0 · (v + v_observer)/(v − v_source).

    SIGN LAW: positive velocities close. A source approaching
    at half the wave speed (v_source = 0.5·v_sound) doubles
    the frequency exactly; receding at the same speed
    (v_source = −0.5·v_sound) gives f0/1.5. An approaching
    observer raises the reading by the numerator alone.

    REFUSALS: a closing source at or above the wave speed is
    refused with its regime named (the sonic pile-up at
    equality, the supersonic cone above); an observer
    receding at or beyond the wave speed is refused — the
    wave train never catches that observer.
    """
    f = _as_number(f0, "f0")
    if f <= 0.0:
        raise DopplerError(f"f0: a sounded frequency must be "
                           f"positive; got {f}")
    vs = _as_number(v_source, "v_source")
    vo = _as_number(v_observer, "v_observer")
    v = _as_sound_speed(v_sound)
    _refuse_closing_singularity(vs, v, "observed_frequency")
    if vo <= -v:
        raise DopplerError(
            f"observed_frequency: v_observer = {vo} recedes "
            f"at or beyond the wave speed ({v}) — the wave "
            "train never catches that observer, and the "
            "formula's negative frequency would be a fiction")
    return f * (v + vo) / (v - vs)


def wavelength_front_back(lambda0, v_source, v_sound=1.0
                          ) -> Tuple[float, float]:
    """(λ_front, λ_back) = (λ0(1 − M), λ0(1 + M)), M = v_source/v.

    The plate's λ′ and λ″: ahead of the motion the fronts are
    laid down closer together, behind it farther apart. Front
    is the side toward which the source moves — the closing
    side under the sign law, so a receding source (negative
    v_source) reads its stretched side as the front, which is
    the geometry and is stated rather than hidden.

    REFUSALS: a closing source at or above the wave speed is
    refused with its regime named (the front wavelength
    would be zero at the wall, negative past it); a source
    receding at or beyond the wave speed is refused likewise
    (the back wavelength would be zero or negative — the
    fronts behind it are not a spacing but a wake).
    """
    lam = _as_number(lambda0, "lambda0")
    if lam <= 0.0:
        raise DopplerError(f"lambda0: a wavelength must be "
                           f"positive; got {lam}")
    vs = _as_number(v_source, "v_source")
    v = _as_sound_speed(v_sound)
    _refuse_closing_singularity(vs, v, "wavelength_front_back")
    if vs <= -v:
        raise DopplerError(
            f"wavelength_front_back: v_source = {vs} recedes "
            f"at or beyond the wave speed ({v}) — the back "
            "wavelength λ0(1 + M) would be zero or negative; "
            "past the wave speed the spacing behind is a "
            "wake, not a wavelength")
    m = vs / v
    return lam * (1.0 - m), lam * (1.0 + m)


def mach_number(v_source, v_sound=1.0) -> float:
    """M = v_source / v_sound — the closing Mach, signed.

    Positive closes, negative recedes (the sign law); the
    plate's regimes are read off its magnitude by regime().
    """
    vs = _as_number(v_source, "v_source")
    v = _as_sound_speed(v_sound)
    return vs / v


def mach_angle_rad(v_source, v_sound=1.0) -> float:
    """The Mach cone's half-angle in radians: asin(1/|M|).

    MECHANISM: the plate's sin θ_M = v/v_s = 1/M, read off
    the source's SPEED — a cone trails motion in either
    direction, so the angle is seated on |v_source|.

    REFUSAL: below the wave speed there is no cone — the
    fronts nest and outrun the source in every direction —
    and the refusal is the boundary coordinate, named. At
    exactly the wave speed the angle is π/2: the cone
    flattened to the plate's shock wall at the nose.
    """
    vs = _as_number(v_source, "v_source")
    v = _as_sound_speed(v_sound)
    speed = abs(vs)
    if speed < v:
        raise DopplerError(
            f"mach_angle: |v_source| = {speed} is below "
            f"v_sound = {v} (M = {speed / v:g}, the subsonic "
            "regime) — no cone exists; the wavefronts nest "
            "and outrun the source in every direction")
    return math.asin(v / speed)


def mach_angle(v_source, v_sound=1.0) -> float:
    """The Mach cone's half-angle in DEGREES.

    The same seat as mach_angle_rad, read in the plate's own
    unit (its supersonic panel prints θ_M in degrees);
    mach_angle_rad is the radians access. Refusals identical.
    """
    return math.degrees(mach_angle_rad(v_source, v_sound))


def regime(v_source, v_sound=1.0) -> str:
    """The plate's three regimes, off the source's speed.

    "subsonic" below the wave speed, "sonic" at exact
    equality, "supersonic" above it — speed, so a receding
    source is classified by |v_source| as the plate's panels
    are (its axis is how fast the source moves, and the cone
    trails either direction of travel). The sonic case is
    exact equality, never a tolerance: the wall is a
    coordinate, not a neighbourhood.
    """
    vs = _as_number(v_source, "v_source")
    v = _as_sound_speed(v_sound)
    speed = abs(vs)
    if speed < v:
        return "subsonic"
    if speed == v:
        return "sonic"
    return "supersonic"


def _evaluate_at(x: np.ndarray, positions: np.ndarray
                 ) -> np.ndarray:
    """MECHANISM: the waveform evaluated at fractional positions.

    Kaiser-windowed sinc interpolation — the upscale seat's
    window (β = 10.0) at its seam span (half-width 10 source
    samples). Positions outside [0, N−1] reconstruct against
    the silence outside the file: taps that fall outside
    contribute zero, which is the seam law stated in the
    module docstring, executed rather than described.
    """
    n = x.size
    half = KERNEL_HALF_WIDTH
    base = np.floor(positions).astype(np.int64)
    # Tap offsets −half..+half around each position's floor:
    # 2·half + 1 taps, the kernel's full seated width.
    offsets = np.arange(-half, half + 1, dtype=np.int64)
    idx = base[:, None] + offsets[None, :]          # (M, 2H+1)
    u = positions[:, None] - idx                    # p − k
    # The Kaiser window on its support |u| ≤ half, zero past
    # it; np.i0 is the modified Bessel function of the first
    # kind the window is defined by.
    scaled = u / half
    window = np.where(
        np.abs(u) <= half,
        np.i0(KAISER_BETA * np.sqrt(np.clip(1.0 - scaled ** 2,
                                            0.0, None)))
        / np.i0(KAISER_BETA),
        0.0)
    weights = np.sinc(u) * window
    inside = (idx >= 0) & (idx < n)
    taps = np.where(inside, x[np.clip(idx, 0, n - 1)], 0.0)
    return np.sum(taps * weights, axis=1)


def shift(signal, sr, v_source, v_sound=1.0) -> np.ndarray:
    """Render a constant radial velocity: the waveform at r·n.

    Positive v_source approaches (the sign law) and the
    render is the source read at positions p = r·n with
    r = v_sound/(v_sound − v_source) — time compressed by
    exactly the ratio observed_frequency swears, so a tone
    at f0 renders at r·f0. The output holds
    floor((N−1)/r) + 1 samples: the same cycles in 1/r the
    duration. Recession (negative v_source) stretches by the
    same law. Pitch only — the render applies no gain.

    REFUSALS: the closing singularity, with its regime named,
    exactly as observed_frequency refuses it; the signal and
    rate under the shape law.
    """
    x = _as_signal(signal)
    rate = _as_rate(sr)
    vs = _as_number(v_source, "v_source")
    v = _as_sound_speed(v_sound)
    _refuse_closing_singularity(vs, v, "shift")
    r = v / (v - vs)
    count = int(math.floor((x.size - 1) / r)) + 1
    positions = r * np.arange(count, dtype=float)
    return _evaluate_at(x, positions)


def passby_radial_velocity(t, v_source, distance, v_sound=1.0):
    """v_r(t) = v_source·x(t)/sqrt(x(t)² + distance²), x = v_source·t.

    The pass's radial (range-rate) velocity under the
    passby() geometry: the source travels a straight line at
    v_source, the observer stands `distance` off the line,
    t = 0 at the tangent point. v_r is the rate the range
    OPENS: negative while the source closes (t < 0), exactly
    zero at closest approach, positive as it recedes;
    v_r → −v_source in the far past (full closing) and
    +v_source in the far future (full recession). v_sound is validated and
    carried for the family's one signature; the velocity
    itself is pure geometry and does not use it.

    Accepts a scalar t (returns a float) or an array of times
    (returns an ndarray of the same shape).
    """
    vs = _as_number(v_source, "v_source")
    d = _as_number(distance, "distance")
    _as_sound_speed(v_sound)
    times = np.asarray(t, dtype=float)
    if not np.all(np.isfinite(times)):
        raise DopplerError("t: times must be finite")
    x = vs * times
    v_r = vs * x / np.sqrt(x ** 2 + d ** 2)
    if np.ndim(t) == 0:
        return float(v_r)
    return v_r


def passby_ratio(t, v_source, distance, v_sound=1.0):
    """r(t) = v_sound/(v_sound + v_r(t)) — the pass's pitch ratio.

    The instantaneous ratio the passby() render integrates:
    the plate's formula read at the pass's own radial
    velocity. Its anchors are exact: r → v/(v − v_source)
    (the full approach ratio) as t → −∞, r = 1 exactly at
    t = 0 (the radial velocity vanishes at the tangent
    point, so pitch crosses f0 at closest approach), and
    r → v/(v + v_source) (the recession ratio) as t → +∞.

    Accepts a scalar t or an array, as passby_radial_velocity
    does. The pass's own refusals are passby()'s; this seat
    validates its scalars and lets the geometry speak.
    """
    v = _as_sound_speed(v_sound)
    v_r = passby_radial_velocity(t, v_source, distance, v)
    if isinstance(v_r, float):
        return v / (v + v_r)
    return v / (v + v_r)


def passby(signal, sr, v_source, distance, v_sound=1.0
           ) -> np.ndarray:
    """Render a straight-line pass-by: pitch gliding by geometry.

    GEOMETRY (stated once, exactly): the source travels a
    straight line at speed v_source; the observer is
    stationary, `distance` from the line; t = 0 is closest
    approach, seated at the CENTRE of the handed signal —
    hand a signal whose middle is the pass's middle. The
    render reads the source at the cumulative phase
    τ(t) = ∫₀ᵗ r(s) ds of the instantaneous ratio
    passby_ratio (trapezoid on the sample grid), evaluated
    by the module's windowed sinc. The output holds the
    handed signal's own sample count; positions the phase
    runs past the source's end read the silence outside the
    file (the seam law). One consequence, stated as a
    coordinate: because the ratio exceeds 1 on the whole
    approach half, the phase consumes MORE source time than
    the file holds real time (in the tests' sworn geometry,
    4.837 s of source over a 4 s file), so a finite source
    is exhausted before the render ends — at the instant τ
    reaches the source's duration, computable from
    passby_ratio before a sample is rendered — and the
    render's tail is that silence, exactly.

    PITCH GEOMETRY ONLY: no 1/R amplitude law is applied.
    The pass renders as loud at its far ends as at its
    closest approach, because loudness over a pass is a mix
    decision, not wave geometry, and this seat does not
    smuggle it in.

    REFUSALS: v_source ≤ 0 (no pass is seated), v_source ≥
    v_sound (the pass becomes a cone problem — refused with
    its regime named), distance ≤ 0 (the line runs through
    the observer and the radial geometry is singular), and
    the shape law on signal and rate.
    """
    x = _as_signal(signal)
    rate = _as_rate(sr)
    vs = _as_number(v_source, "v_source")
    d = _as_number(distance, "distance")
    v = _as_sound_speed(v_sound)
    if vs <= 0.0:
        raise DopplerError(
            f"passby: v_source = {vs} seats no pass — a pass "
            "is a source in motion past the observer; give a "
            "positive travel speed (direction is geometry's, "
            "not the sign's: the pass approaches, then "
            "recedes, by construction)")
    _refuse_closing_singularity(vs, v, "passby")
    if d <= 0.0:
        raise DopplerError(
            f"passby: distance = {d} — the source's line "
            "would run through the observer and the radial "
            "geometry is singular there; a pass stands off "
            "the line by a positive distance")
    n = x.size
    # Times centred on the signal's middle: t = 0 (closest
    # approach) at the centre sample, the seat stated in the
    # docstring, executed here as an axis.
    t = (np.arange(n, dtype=float) - (n - 1) / 2.0) / rate
    ratio = passby_ratio(t, vs, d, v)
    # The cumulative phase: τ(t) = ∫ r dt from the render's
    # start, trapezoid on the sample grid — the grid is fine
    # (the ratio's own timescale is distance/v_source, a
    # multitude of samples at any studio rate), so the
    # integral's error sits far under the kernel's ripple.
    tau = np.zeros(n)
    if n > 1:
        steps = 0.5 * (ratio[1:] + ratio[:-1]) / rate
        tau[1:] = np.cumsum(steps)
    positions = tau * rate  # source time → source samples
    return _evaluate_at(x, positions)
