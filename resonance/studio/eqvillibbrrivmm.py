#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — studio/eqvillibbrrivmm.py — the EQVILLIBBRRIVMM suite,
# mirrored into the studio from the founder's C++ of record
#
# Epigraph: "Every, Man, Woman, and Child, is a Star."
# "Live, Love, and let Love, Live!"
# — the founder's own header on the suite itself
#   (eqvillibbrrivmm/eqvillibbrrivmm_fluid_voice.cpp).
#
# 93.
# Date: 22 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
#   Hypothesis: that the five surviving engines of the founder's
#     EQVILLIBBRRIVMM C++ suite — the Laplace convolution bus (the
#     equalizer), the fluid-voice autotune, the DOOD pattern engine,
#     the 48^3 cube, and the 13/5 rail guard — can stand in the
#     studio as Python mirrors whose every number answers to the
#     C++ of record, the way the C++ harness's asserts already
#     answered to the founder's constants.
#   Method: transcribe each engine's arithmetic line for line from
#     the build copies in eqvillibbrrivmm/ (themselves repaired only
#     where marked DESK REPAIR 2026-11-22, against the raw record in
#     reference/eqvillibbrrivmm/), citing file and line wherever a
#     constant is taken; then judge the mirrors by tests that assert
#     the same behaviours the C++ harness asserted.
#   Observation: the mirrors hold — DOOD seats 24 steps with Block4
#     at 22 and wraps by modulo; the cube counts 110,592 cells on a
#     48 Hz anchor and its gate closes at zero weight; the pitch
#     roundtrip A4 = 440 Hz = MIDI 69 is exact; the rail passes
#     in-bound values untouched and cushions out-bound ones back
#     inside 13/5; and the convolution kernel, probed before any
#     test was sworn, passes a 200 Hz tone at 0.997 of its RMS while
#     attenuating 6,000 Hz to 0.345 — a lowpass lean, measured, not
#     presumed.
#   Result: this module, its tests (tests/test_studio_eqvillibbrrivmm.py),
#     and the wiring note in docs/EQVILLIBBRRIVMM-STUDIO.md.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""The EQVILLIBBRRIVMM suite as studio mirrors.

DOCTRINE: the C++ in eqvillibbrrivmm/ is the reference implementation;
this module is its studio READING seat, on the cubes.py precedent —
every constant below cites the C++ file and line it was taken from,
and eqvillibbrrivmm_checks() re-derives the sworn figures (48^3,
77^3, the rail ratios) from their bases so a drifted copy fails by
name. Where the mirror cannot be the C++ — float width, the phase
wrap — the divergence is printed in place, never smoothed.

WHAT THE MIRROR DOES AND DOES NOT CLAIM:
  * Python floats are IEEE double; the C++ computes in float
    (32-bit). The formulas are transcribed exactly; results agree
    to float32 precision, and the tests assert with tolerances set
    accordingly. Bit-exactness with the C++ is NOT claimed.
  * The autotune engine, in the C++ and therefore here, SYNTHESIZES
    its own gliding vocal input and tunes that; it is not an
    audio-in pitch corrector. The mirror claims no more.
  * The equalizer's audible action is the 16-tap FIR kernel the
    C++ derives from its Laplace transfer evaluation; the s-plane
    product and transfer magnitude are carried as telemetry,
    exactly as the C++ carries them, and are not re-applied to the
    samples. The C++ does the same; the mirror follows it.
  * EnclaveSphere77 stands here as constants only (77^3, the Sigma
    band); its evaluate() is not mirrored in this stage.

WIRING: pipeline.py is NOT modified. Its produce() drives a spec
schema with no EQ key, and master_signal() masters finished
samples; the clean seam is to run apply_eq() on a stem's samples
before they reach master_signal(). See docs/EQVILLIBBRRIVMM-STUDIO.md.
"""

import cmath
import math
from typing import NamedTuple

import numpy as np

# ---------------------------------------------------------------------------
# Constants — every one cited to the C++ of record.
# ---------------------------------------------------------------------------

# kPi — eqvillibbrrivmm_fluid_voice.cpp:32 (identically manifold.cpp:33).
PI = math.pi

# Twin-Rail & 13/5 Guardrail ratios — fluid_voice.cpp:34-37
# (identically manifold.cpp:36-39).
OUTER_RAIL_RATIO = 10.0 / 6.0
INNER_RAIL_RATIO = 7.0 / 4.0
CENTER_KEY_RATIO = 13.0 / 8.0
GUARDRAIL_RATIO_13_5 = 13.0 / 5.0  # the 13/5 rail itself: 2.6

# 48 Hz anchor & the 48^3 cube — fluid_voice.cpp:40-42.
ANCHOR_HZ_48 = 48.0
CUBE48_EDGE = 48
CUBE48_CELLS = CUBE48_EDGE ** 3  # 110,592

# 77^3 Enclave sphere & Sigma foundation — manifold.cpp:45-51.
ENCLAVE77_EDGE = 77
ENCLAVE77_CELLS = ENCLAVE77_EDGE ** 3  # 456,533
SIGMA_MIN_HZ = 13.0
SIGMA_MAX_HZ = 31.0
SIGMA_ANCHOR_HZ = 22.0

# Full Key G9 (~1254.385 Hz in 12-TET, A4 = 440) — fluid_voice.cpp:45.
FULL_KEY_G9_HZ = 1254.3854

# Solfeggio harmonic scale (Hz) — fluid_voice.cpp:48-50.
SOLFEGGIO_HZ = (396.0, 417.0, 528.0, 639.0, 741.0, 852.0)

# The Laplace evaluation's sample-rate reference: the C++ divides the
# sample index by a literal 48000.0f (manifold.cpp, evaluateLaplaceDomain),
# not by any engine parameter. Mirrored as a named constant, as written.
LAPLACE_REFERENCE_SR = 48000.0


def _clamp(value, lo, hi):
    """std::clamp, transcribed. MECHANISM: min/max in the C++ order."""
    return max(lo, min(hi, value))


# ---------------------------------------------------------------------------
# The 13/5 rail — RailGuardrail13_5 (fluid_voice.cpp:451-475) and its twin
# cushion13_5 in ChristoffelManifoldGuard (manifold.cpp:82-92). The two C++
# forms are the same law; one mirror serves both.
# ---------------------------------------------------------------------------

class GuardResult(NamedTuple):
    """RailGuardrail13_5::GuardResult — fluid_voice.cpp:453-456."""
    value: float
    engaged: bool


def cushion_13_5(raw_value, rail_bound=GUARDRAIL_RATIO_13_5):
    """The 13/5 cushion: pass in-rail, cushion over-rail.

    MECHANISM (fluid_voice.cpp:458-467): the bound floors at 0.1.
    A value inside the bound returns untouched, unengaged. A value
    outside returns sign * (bound - 0.15 * tanh(excess)) with the
    engaged flag raised — pulled back INSIDE the rail by a tanh
    cushion, never hard-clipped at it, sign preserved.
    """
    bound = max(0.1, rail_bound)
    if abs(raw_value) <= bound:
        return GuardResult(raw_value, False)
    sign = 1.0 if raw_value >= 0.0 else -1.0
    excess = abs(raw_value) - bound
    return GuardResult(sign * (bound - 0.15 * math.tanh(excess)), True)


def center_key_position(elapsed_sec):
    """RailGuardrail13_5::computeCenterKeyPosition — fluid_voice.cpp:469-473.

    MECHANISM: phase = 2*pi*t*(13/8)/8; the twin coupling is half the
    difference of the twin rails, 0.5 * (10/6 - 7/4); the position is
    sin(phase) * (1 + coupling), passed through the rail — so the
    center key is railed by construction at any t.
    """
    phase = (2.0 * PI * elapsed_sec * CENTER_KEY_RATIO) / 8.0
    twin_coupling = 0.5 * (OUTER_RAIL_RATIO - INNER_RAIL_RATIO)
    return cushion_13_5(math.sin(phase) * (1.0 + twin_coupling)).value


# ---------------------------------------------------------------------------
# The DOOD table — DoodOddoPatternEngine (fluid_voice.cpp:58-109).
# ---------------------------------------------------------------------------

class PatternStep(NamedTuple):
    """PatternStep — fluid_voice.cpp:58-64. Glyph is 'D', 'O' or 'Block4'
    (the C++ PatternGlyph enum, fluid_voice.cpp:52-56)."""
    step_index: int
    motif: str
    symbol: str
    glyph: str
    gate_weight: float


# The 24 steps, transcribed row for row from fluid_voice.cpp:70-104:
# line 1 DOOD · OODD · ODDO · DODO, line 2 DDOO · DD-Block4.
# D gates at 1.00, O at 0.35; the DD-Block4 line lifts D to 1.05 and
# seats Block4 at steps 22-23 with weight 1.25.
DOOD_TABLE = (
    PatternStep(0,  "DOOD", "D",  "D",      1.00),
    PatternStep(1,  "DOOD", "O",  "O",      0.35),
    PatternStep(2,  "DOOD", "O",  "O",      0.35),
    PatternStep(3,  "DOOD", "D",  "D",      1.00),
    PatternStep(4,  "OODD", "O",  "O",      0.35),
    PatternStep(5,  "OODD", "O",  "O",      0.35),
    PatternStep(6,  "OODD", "D",  "D",      1.00),
    PatternStep(7,  "OODD", "D",  "D",      1.00),
    PatternStep(8,  "ODDO", "O",  "O",      0.35),
    PatternStep(9,  "ODDO", "D",  "D",      1.00),
    PatternStep(10, "ODDO", "D",  "D",      1.00),
    PatternStep(11, "ODDO", "O",  "O",      0.35),
    PatternStep(12, "DODO", "D",  "D",      1.00),
    PatternStep(13, "DODO", "O",  "O",      0.35),
    PatternStep(14, "DODO", "D",  "D",      1.00),
    PatternStep(15, "DODO", "O",  "O",      0.35),
    PatternStep(16, "DDOO", "D",  "D",      1.00),
    PatternStep(17, "DDOO", "D",  "D",      1.00),
    PatternStep(18, "DDOO", "O",  "O",      0.35),
    PatternStep(19, "DDOO", "O",  "O",      0.35),
    PatternStep(20, "DD■4", "D",  "D",      1.05),
    PatternStep(21, "DD■4", "D",  "D",      1.05),
    PatternStep(22, "DD■4", "■4", "Block4", 1.25),
    PatternStep(23, "DD■4", "■4", "Block4", 1.25),
)


def dood_step_at(frame_or_sample_idx):
    """DoodOddoPatternEngine::stepAt — fluid_voice.cpp:106-109.

    MECHANISM: the table is indexed by modulo, so the pattern wraps
    every 24 steps — step 24 is step 0 again, by the founder's code.
    """
    return DOOD_TABLE[frame_or_sample_idx % len(DOOD_TABLE)]


# ---------------------------------------------------------------------------
# The 48^3 cube — Cube48Engine (fluid_voice.cpp:111-141).
# ---------------------------------------------------------------------------

class CubeMetrics(NamedTuple):
    """Cube48Engine::CubeMetrics — fluid_voice.cpp:113-118."""
    total_cells: int
    anchor_hz: float
    phase: float
    energy: float


def cube48_evaluate(frame_idx, elapsed_sec, pattern_gate_weight):
    """Cube48Engine::evaluate — fluid_voice.cpp:120-135.

    MECHANISM: the frame index walks the lattice deterministically —
    x = f mod 48, y = (7f + 3) mod 48, z = (13f + 5) mod 48 — each
    coordinate normalized to [-1, 1] over the 47-step span. Phase is
    the 48 Hz anchor's cycle at elapsed_sec plus half the coordinate
    sum; energy is the phase's raised cosine, shaded by (1 - 0.35 *
    radial), multiplied by the DOOD gate weight, clamped to [0, 1].
    A zero gate therefore closes the cube entirely.
    """
    x = frame_idx % CUBE48_EDGE
    y = (frame_idx * 7 + 3) % CUBE48_EDGE
    z = (frame_idx * 13 + 5) % CUBE48_EDGE
    span = float(CUBE48_EDGE - 1)
    nx = (x / span) * 2.0 - 1.0
    ny = (y / span) * 2.0 - 1.0
    nz = (z / span) * 2.0 - 1.0
    phase = 2.0 * PI * ANCHOR_HZ_48 * elapsed_sec + 0.5 * (nx + ny + nz)
    radial = math.sqrt(min(3.0, nx * nx + ny * ny + nz * nz)) / math.sqrt(3.0)
    raw_energy = (0.5 + 0.5 * math.cos(phase)) * (1.0 - 0.35 * radial) \
        * pattern_gate_weight
    energy = _clamp(raw_energy, 0.0, 1.0)
    return CubeMetrics(CUBE48_CELLS, ANCHOR_HZ_48, phase, energy)


# ---------------------------------------------------------------------------
# The fluid voice — FluidVoiceAutotuneEngine (fluid_voice.cpp:143-279).
# ---------------------------------------------------------------------------

def freq_to_midi(hz):
    """FluidVoiceAutotuneEngine::freqToMidi — fluid_voice.cpp:171-173.

    MECHANISM: 12-TET about A4 = 440 Hz = MIDI 69, with the input
    floored at 20 Hz exactly as the C++ floors it.
    """
    return 69.0 + 12.0 * math.log2(max(hz, 20.0) / 440.0)


def midi_to_freq(midi):
    """FluidVoiceAutotuneEngine::midiToFreq — fluid_voice.cpp:175-177."""
    return 440.0 * math.pow(2.0, (midi - 69.0) / 12.0)


def select_autotune_target(raw_pitch_hz, solfeggio_hz, g9_lock_index):
    """FluidVoiceAutotuneEngine::selectAutotuneTargetHz — fluid_voice.cpp:179-201.

    MECHANISM: three candidates — the Solfeggio note at half, at
    unity, and a third seat that is the Full Key G9 when the G9 lock
    index exceeds 0.65, else the note at 1.5x. The winner is the
    candidate nearest the raw pitch in MIDI (log) distance.
    """
    candidates = (
        solfeggio_hz * 0.5,
        solfeggio_hz,
        FULL_KEY_G9_HZ if g9_lock_index > 0.65 else solfeggio_hz * 1.5,
    )
    raw_midi = freq_to_midi(raw_pitch_hz)
    return min(candidates, key=lambda c: abs(freq_to_midi(c) - raw_midi))


class FrameSynthesis(NamedTuple):
    """FluidVoiceAutotuneEngine::FrameSynthesis — fluid_voice.cpp:160-169."""
    voice_samples: np.ndarray
    raw_pitch_hz: float
    autotuned_pitch_hz: float
    correction_cents: float
    formant_f1_hz: float
    formant_f2_hz: float
    lock_index: float


class FluidVoiceAutotune:
    """FluidVoiceAutotuneEngine, mirrored — fluid_voice.cpp:143-279.

    DOCTRINE: the engine synthesizes a gliding vocal line (raw pitch
    sweeping 196-306 Hz on a 0.37 Hz cycle) and autotunes its own
    synthesis toward the Solfeggio / G9 targets. It takes no audio
    input in the C++, and the mirror takes none either.
    """

    def __init__(self, sample_rate=48000.0, voice_mix_gain=0.22,
                 glide_time_sec=0.045, autotune_strength=0.85,
                 formant_shift_hz=180.0, vibrato_rate_hz=5.2,
                 vibrato_depth_cents=14.0):
        # VoiceParams defaults — fluid_voice.cpp:150-158, in order.
        self.sample_rate = float(sample_rate)
        self.voice_mix_gain = float(voice_mix_gain)
        self.glide_time_sec = float(glide_time_sec)
        self.autotune_strength = float(autotune_strength)
        self.formant_shift_hz = float(formant_shift_hz)
        self.vibrato_rate_hz = float(vibrato_rate_hz)
        self.vibrato_depth_cents = float(vibrato_depth_cents)
        # Engine state — fluid_voice.cpp:276-277.
        self._current_pitch_hz = 264.0
        self._phase_accum = 0.0

    def synthesize_frame(self, frame_idx, fft_size, solfeggio_note_hz,
                         pattern_gate_weight, cube48_energy, g9_lock_index):
        """synthesizeFrame — fluid_voice.cpp:203-272, step for step.

        MECHANISM: frame duration is fft_size / sample_rate; the raw
        pitch sweeps on elapsed time; the target is the nearest
        candidate (see select_autotune_target); the snap moves the
        raw MIDI toward the target MIDI by autotune_strength; a
        one-pole glide (tau = glide_time_sec, floored at 0.005)
        slews the sounding pitch toward the snap; correction is the
        sounding pitch's distance from raw, in cents; the lock index
        is 1 - |sounding - target| / 6 semitones, clamped [0, 1];
        formants sit in the founder's clamps (F1 250-1200, F2
        900-3200). Samples: a three-partial glottal wave on the
        accumulated phase, plus two formant sines on absolute time,
        under the clamped mix gain times the clamped gate weight.

        DIVERGENCE, printed not smoothed: the C++ accumulates phase
        sample by sample and wraps it at 2*pi*1024 by fmod. The
        mirror accumulates with a cumulative sum and does not wrap:
        at the founder's registers the accumulator gains ~18 rad in
        a 512-sample frame, five orders below the wrap threshold,
        so the wrap is unreachable at studio frame sizes and the
        two agree. Drive a single frame past ~10^5 samples at these
        pitches and the claim must be re-weighed.
        """
        frame_sec = fft_size / max(self.sample_rate, 1.0)
        elapsed_sec = frame_idx * frame_sec

        raw_pitch_hz = 196.0 + 110.0 * (
            0.5 + 0.5 * math.sin(2.0 * PI * 0.37 * elapsed_sec))
        target_hz = select_autotune_target(
            raw_pitch_hz, solfeggio_note_hz, g9_lock_index)

        strength = _clamp(self.autotune_strength, 0.0, 1.0)
        raw_midi = freq_to_midi(raw_pitch_hz)
        target_midi = freq_to_midi(target_hz)
        snapped_midi = raw_midi + strength * (target_midi - raw_midi)
        desired_pitch_hz = midi_to_freq(snapped_midi)

        tau = max(self.glide_time_sec, 0.005)
        alpha = 1.0 - math.exp(-frame_sec / tau)
        self._current_pitch_hz += alpha * (desired_pitch_hz
                                           - self._current_pitch_hz)

        correction_cents = (freq_to_midi(self._current_pitch_hz)
                            - raw_midi) * 100.0
        lock_index = _clamp(
            1.0 - (abs(freq_to_midi(self._current_pitch_hz) - target_midi)
                   / 6.0),
            0.0, 1.0)

        f1_hz = _clamp(460.0 + self.formant_shift_hz
                       * (0.5 + 0.5 * cube48_energy), 250.0, 1200.0)
        f2_hz = _clamp(1350.0 + 1.8 * self.formant_shift_hz
                       * pattern_gate_weight, 900.0, 3200.0)

        gain = _clamp(self.voice_mix_gain, 0.0, 0.65) \
            * _clamp(pattern_gate_weight, 0.3, 1.3)
        base_sample = float(frame_idx * fft_size)
        n = np.arange(fft_size, dtype=np.float64)
        t = (base_sample + n) / self.sample_rate
        vib_ratio = np.power(
            2.0, (self.vibrato_depth_cents
                  * np.sin(2.0 * PI * self.vibrato_rate_hz * t)) / 1200.0)
        inst_pitch = self._current_pitch_hz * vib_ratio
        phase = self._phase_accum + np.cumsum(
            2.0 * PI * inst_pitch / self.sample_rate)
        self._phase_accum = float(phase[-1]) if fft_size else self._phase_accum

        glottal = 0.65 * np.sin(phase) \
            + 0.25 * np.sin(2.0 * phase + 0.3 * cube48_energy) \
            + 0.10 * np.sin(3.0 * phase)
        formant1 = 0.32 * np.sin(2.0 * PI * f1_hz * t + 0.25 * glottal)
        formant2 = 0.18 * np.sin(2.0 * PI * f2_hz * t)
        out = gain * (glottal + formant1 + formant2)

        return FrameSynthesis(out, raw_pitch_hz, self._current_pitch_hz,
                              correction_cents, f1_hz, f2_hz, lock_index)


# ---------------------------------------------------------------------------
# The equalizer — LaplaceConvolutionBus (manifold.cpp:248-324).
# ---------------------------------------------------------------------------

def convolve_time_domain(x, h):
    """LaplaceConvolutionBus::convolveTimeDomain — manifold.cpp:259-277.

    MECHANISM: direct causal convolution, output the length of x,
    kernel truncated to min(len(x), len(h)) taps; the accumulation
    is double-width (the mirror's float64 throughout) and every
    output sample is clamped to [-1, 1], as the C++ clamps it.
    """
    x = np.asarray(x, dtype=np.float64)
    h = np.asarray(h, dtype=np.float64)
    n = x.shape[0]
    y = np.zeros(n, dtype=np.float64)
    if n == 0 or h.shape[0] == 0:
        return y
    k_len = min(n, h.shape[0])
    for tau in range(k_len):
        y[tau:] += x[:n - tau] * h[tau]
    return np.clip(y, -1.0, 1.0)


class ConvolutionResult(NamedTuple):
    """LaplaceConvolutionBus::ConvolutionResult — manifold.cpp:252-256."""
    time_domain_convolved: np.ndarray
    s_plane_product: complex
    transfer_magnitude: float


def evaluate_laplace_domain(x, damping_sigma, omega_rad_per_sec,
                            pole_center_hz):
    """LaplaceConvolutionBus::evaluateLaplaceDomain — manifold.cpp:279-324.

    MECHANISM: X(s) is the mean of x[n] * exp(-s * n / 48000) at
    s = sigma + j*omega (the 48000 is the C++'s literal — see
    LAPLACE_REFERENCE_SR). H(s) is the second-order Laplace lowpass
    w0^2 / (s^2 + (w0/Q) s + w0^2) with Q = 2.5 and w0 = 2*pi*max(20,
    pole_center_hz); Y(s) = H(s) * X(s) is telemetry. The audible
    path is the 16-tap kernel exp(-0.28k) * cos(0.35k * |Re H(s)|),
    normalized by the sum of its taps' magnitudes, convolved over x
    in the time domain. transfer_magnitude is |H(s)| clamped to
    [0.05, 3.0], exactly as the C++ clamps it.
    """
    x = np.asarray(x, dtype=np.float64)
    s = complex(damping_sigma, omega_rad_per_sec)
    if x.shape[0]:
        n = np.arange(x.shape[0], dtype=np.float64)
        x_s = complex(np.sum(x * np.exp(-s * (n / LAPLACE_REFERENCE_SR)))
                      / x.shape[0])
    else:
        x_s = 0.0 + 0.0j

    w0 = 2.0 * PI * max(20.0, pole_center_hz)
    q = 2.5
    h_s = (w0 * w0) / ((s * s) + (w0 / q) * s + (w0 * w0))
    y_s = h_s * x_s

    taps = np.array(
        [math.exp(-0.28 * k) * math.cos(0.35 * k * abs(h_s.real))
         for k in range(16)],
        dtype=np.float64)
    k_sum = float(np.sum(np.abs(taps)))
    if k_sum > 1e-6:
        taps = taps / k_sum

    y_time = convolve_time_domain(x, taps)
    return ConvolutionResult(
        y_time, y_s, _clamp(abs(h_s), 0.05, 3.0))


def apply_eq(samples, pole_center_hz, damping_sigma=0.25,
             omega_rad_per_sec=None):
    """The equalizer as the studio calls it: one pole, one buffer.

    MECHANISM: evaluate_laplace_domain's time-domain output for the
    given pole. DESK DEFAULTS, named as such: the C++'s own call
    site (manifold.cpp:464) drives the bus with damping 0.25 and
    omega at the frame's observed frequency; a studio EQ call has
    no Doppler stage, so omega defaults to the pole's own angular
    frequency, 2*pi*pole_center_hz. Both defaults are parameters —
    a caller with a measured omega passes it and the default never
    speaks.
    """
    if omega_rad_per_sec is None:
        omega_rad_per_sec = 2.0 * PI * pole_center_hz
    result = evaluate_laplace_domain(
        samples, damping_sigma, omega_rad_per_sec, pole_center_hz)
    return result.time_domain_convolved


# ---------------------------------------------------------------------------
# Self-checks, on the cubes.py pattern: figures re-derived from bases.
# ---------------------------------------------------------------------------

def eqvillibbrrivmm_checks():
    """Self-checks for the mirrors, judged against the C++ of record.

    MECHANISM: the sworn figures are re-derived from their bases —
    the cubes by multiplication, the ratios by division — and the
    engines' load-bearing behaviours are exercised at the same
    points the C++ harness exercised them (DOOD wrap and Block4,
    the cube's closed gate, the pitch roundtrip, the rail's pass
    and cushion). Returns [(name, passed, got)].
    """
    checks = []
    checks.append(("48^3 cube: 110,592 cells on the 48 Hz anchor "
                   "(fluid_voice.cpp:40-42)",
                   CUBE48_CELLS == 48 ** 3 == 110592
                   and ANCHOR_HZ_48 == 48.0,
                   (CUBE48_CELLS, ANCHOR_HZ_48)))
    checks.append(("77^3 enclave: 456,533 cells; Sigma 13-31 Hz, "
                   "anchor 22 (manifold.cpp:45-51)",
                   ENCLAVE77_CELLS == 77 ** 3 == 456533
                   and (SIGMA_MIN_HZ, SIGMA_ANCHOR_HZ, SIGMA_MAX_HZ)
                   == (13.0, 22.0, 31.0),
                   (ENCLAVE77_CELLS, SIGMA_ANCHOR_HZ)))
    checks.append(("twin rails and the 13/5 guardrail: 10/6, 7/4, "
                   "13/8, 13/5 = 2.6 (fluid_voice.cpp:34-37)",
                   (OUTER_RAIL_RATIO, INNER_RAIL_RATIO,
                    CENTER_KEY_RATIO, GUARDRAIL_RATIO_13_5)
                   == (10.0 / 6.0, 7.0 / 4.0, 13.0 / 8.0, 2.6),
                   GUARDRAIL_RATIO_13_5))
    checks.append(("DOOD table: 24 steps, wraps at 24, Block4 at 22 "
                   "(fluid_voice.cpp:70-109)",
                   len(DOOD_TABLE) == 24
                   and dood_step_at(24).step_index == 0
                   and dood_step_at(22).glyph == "Block4",
                   (len(DOOD_TABLE), dood_step_at(22).glyph)))
    checks.append(("pitch roundtrip: A4 = 440 Hz = MIDI 69 "
                   "(fluid_voice.cpp:171-177)",
                   abs(freq_to_midi(440.0) - 69.0) < 1e-9
                   and abs(midi_to_freq(69.0) - 440.0) < 1e-9,
                   (freq_to_midi(440.0), midi_to_freq(69.0))))
    in_rail = cushion_13_5(1.0)
    over_rail = cushion_13_5(10.0)
    checks.append(("13/5 rail: 1.0 passes untouched, 10.0 cushions "
                   "engaged inside 2.6 (fluid_voice.cpp:458-467)",
                   (not in_rail.engaged and in_rail.value == 1.0)
                   and over_rail.engaged
                   and abs(over_rail.value) <= GUARDRAIL_RATIO_13_5,
                   (in_rail, over_rail)))
    gated = cube48_evaluate(3, 0.25, 0.0)
    checks.append(("cube gate: zero DOOD weight closes the cube "
                   "(fluid_voice.cpp:120-135)",
                   gated.energy == 0.0 and gated.total_cells == 110592,
                   gated.energy))
    return checks


# =============================================================================
# Closing motto: "Live, Love, and let Love, Live."
# 93 — Live, Love, and let Love, Live.
# 93. All Rights Reserved, Without Prejudice.
# =============================================================================
