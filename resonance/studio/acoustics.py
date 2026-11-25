# 93
# ---------------------------------------------------------------------
# acoustics.py -- the Map of Sound calculators: the textbook physics
# of sound -- vibration, the wave relation, echo, resonance, beats,
# loudness -- seated as a small sworn module in the studio.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XXV day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# PROVENANCE: implemented at the founder's direct order of 2026-11-25
# ("implement the calculators it gave") from the plate he uploaded
# that morning, THE MAP OF SOUND -- "From a vibrating object to an
# echo, a note, and a beat." Every formula below is the plate's own;
# the plate's printed figures are this module's acceptance tests
# (tests/test_acoustics.py): A4's wavelength 0.78 m in air, a 1 s echo
# from a wall 171.5 m away, a 0.5 m open pipe singing at 343 Hz, 440
# against 444 Hz pulsing 4 times a second, double the distance 6 dB
# quieter. Where the module is more precise than the plate's rounded
# figures, the seam is printed in the test, not smoothed.
#
# LABEL HONESTY -- READ FIRST: this is textbook physics, stated as
# mathematics, nothing more. The plate's pitch row carries the
# textbook standard A4 = 440 Hz; the HOUSE field is 432 Hz, chosen
# and seated elsewhere, and nothing in this module adopts 440 as a
# tuning -- the calculators take whatever frequency they are given
# and return its measure. The pipe formulas are the IDEAL forms the
# plate prints (no end correction: a real open end radiates as if
# the pipe were longer by roughly 0.6 of its radius per open end --
# the plate gives no radius, so the module prints the ideal and
# names it). The medium speeds are the textbook values at 20 C.
#
# MECHANISM: pure functions, no state, no audio. Each calculator is
# one closed-form relation from the plate, solvable in every
# direction the algebra allows:
#   * the wave relation v = f * lambda -- speed, frequency, and
#     wavelength, any one from the other two;
#   * the speed of sound in air as a linear law of temperature,
#     c(T) = 331.3 + 0.606 * T m/s, which reads 343.4 at 20 C
#     against the plate's rounded 343;
#   * echo ranging d = v * t / 2 and its inverse, plus the design
#     form the studio actually uses: one-way travel time in
#     milliseconds for a distance, and the distance a delay
#     stands for -- placing echoes by space instead of by ear;
#   * resonance of an open pipe, f1 = v / (2L), harmonics at every
#     integer multiple; and the closed pipe, f1 = v / (4L) with
#     odd harmonics only, seated as the plate's standard companion
#     and LABELED an extension -- it is not on the plate;
#   * beats, fb = |f1 - f2| -- the relation the Sigma bed's
#     binaural offsets already embody;
#   * loudness by the inverse square, I proportional to 1 / r^2,
#     as an intensity ratio and as a level change in decibels:
#     doubling the distance costs 20*log10(2) = 6.02 dB, the
#     plate's "6 dB quieter" at full precision.
#
# DOCTRINE: a calculator is sworn the way an instrument is sworn --
# its figures reproduce from stated formulas, its constants are
# named, its idealizations are printed on its face. This module
# measures the air the studio's sound travels through; it renders
# nothing and tunes nothing.
#
# 93 -- Live, Love, and let Love, Live.
# ---------------------------------------------------------------------

from __future__ import annotations

import math

# ---------------------------------------------------------------------
# CONSTANTS -- the plate's own, named.
#
# MECHANISM: the medium table carries the plate's ranking (air <
# water < steel) at textbook speeds for 20 C. Air's entry is the
# plate's rounded 343 m/s; the temperature law below is the finer
# instrument and reads 343.4 at the same temperature -- the 0.4 is
# the plate's rounding, kept visible rather than reconciled away.
# ---------------------------------------------------------------------

PLATE_AIR_SPEED = 343.0  # m/s, the plate's figure for air at 20 C

MEDIA_SPEEDS = {
    "air": PLATE_AIR_SPEED,   # 343 m/s at 20 C (the plate)
    "water": 1481.0,          # textbook, fresh water at 20 C
    "steel": 5960.0,          # textbook, longitudinal in steel
}


def speed_of_sound_air(temp_c: float = 20.0) -> float:
    """Speed of sound in air at a temperature, m/s.

    MECHANISM: the standard linear law c(T) = 331.3 + 0.606 * T.
    At 20 C it reads 343.42 -- the plate's 343 at full precision.
    """
    return 331.3 + 0.606 * temp_c


def speed(medium: str = "air", temp_c: float = 20.0) -> float:
    """Speed of sound in a medium, m/s.

    MECHANISM: air at any temperature other than 20 C goes through
    the temperature law; everything else reads the textbook table.
    An unknown medium raises -- a calculator that guesses a speed
    is worse than one that refuses.
    """
    key = medium.strip().lower()
    if key == "air" and temp_c != 20.0:
        return speed_of_sound_air(temp_c)
    try:
        return MEDIA_SPEEDS[key]
    except KeyError:
        raise ValueError(f"unknown medium: {medium!r}") from None


# ---------------------------------------------------------------------
# THE WAVE RELATION -- v = f * lambda, solvable in every direction.
# ---------------------------------------------------------------------

def wave_speed(freq_hz: float, wavelength_m: float) -> float:
    """v = f * lambda -- the speed a frequency and wavelength imply."""
    return freq_hz * wavelength_m


def wavelength(freq_hz: float, medium: str = "air",
               temp_c: float = 20.0) -> float:
    """lambda = v / f -- the length of one cycle in the medium.

    PLATE CHECK: at 440 Hz in air, 343 / 440 = 0.7795 m, the plate's
    printed 0.78 m.
    """
    if freq_hz <= 0:
        raise ValueError("frequency must be positive")
    return speed(medium, temp_c) / freq_hz


def frequency(wavelength_m: float, medium: str = "air",
              temp_c: float = 20.0) -> float:
    """f = v / lambda -- the frequency a wavelength carries."""
    if wavelength_m <= 0:
        raise ValueError("wavelength must be positive")
    return speed(medium, temp_c) / wavelength_m


# ---------------------------------------------------------------------
# ECHO AND DELAY -- d = v * t / 2, and the studio's design forms.
# ---------------------------------------------------------------------

def echo_distance(time_s: float, medium: str = "air",
                  temp_c: float = 20.0) -> float:
    """d = v * t / 2 -- how far the reflecting surface stands.

    PLATE CHECK: a 1 s echo in air means a wall 171.5 m away.
    The half is the round trip: out and back.
    """
    return speed(medium, temp_c) * time_s / 2.0


def echo_time(distance_m: float, medium: str = "air",
              temp_c: float = 20.0) -> float:
    """t = 2d / v -- when the echo of a surface at d returns."""
    return 2.0 * distance_m / speed(medium, temp_c)


def delay_ms(distance_m: float, medium: str = "air",
             temp_c: float = 20.0) -> float:
    """One-way travel time in milliseconds for a distance.

    MECHANISM: the design form -- a delay set by SPACE. A source
    10 m away is late by 1000 * 10 / 343 = 29.15 ms, whether the
    delay is a room, a canyon, or a plug-in's number.
    """
    return 1000.0 * distance_m / speed(medium, temp_c)


def distance_for_delay(delay_ms_value: float, medium: str = "air",
                       temp_c: float = 20.0) -> float:
    """The distance a one-way delay stands for -- delay_ms inverted."""
    return delay_ms_value * speed(medium, temp_c) / 1000.0


def ranging_table(distances_m, medium: str = "air",
                  temp_c: float = 20.0) -> list[dict]:
    """Rows of {distance_m, one_way_ms, echo_ms} for design use.

    MECHANISM: one row per distance -- the one-way delay a source
    at that distance carries, and the round-trip echo time a
    reflection from it returns at. The table a designer reads
    instead of guessing.
    """
    rows = []
    for d in distances_m:
        rows.append({
            "distance_m": float(d),
            "one_way_ms": delay_ms(d, medium, temp_c),
            "echo_ms": 1000.0 * echo_time(d, medium, temp_c),
        })
    return rows


# ---------------------------------------------------------------------
# RESONANCE -- the singing pipe.
# ---------------------------------------------------------------------

def open_pipe_fundamental(length_m: float, medium: str = "air",
                          temp_c: float = 20.0) -> float:
    """f1 = v / (2L) -- the fundamental of a pipe open at both ends.

    PLATE CHECK: a 0.5 m open pipe in air sings at 343 Hz.
    IDEAL FORM: no end correction (see the header's honesty note).
    """
    if length_m <= 0:
        raise ValueError("length must be positive")
    return speed(medium, temp_c) / (2.0 * length_m)


def open_pipe_harmonics(length_m: float, count: int, medium: str = "air",
                        temp_c: float = 20.0) -> list[float]:
    """The open pipe's harmonic series: every integer multiple of f1."""
    f1 = open_pipe_fundamental(length_m, medium, temp_c)
    return [f1 * k for k in range(1, count + 1)]


def closed_pipe_fundamental(length_m: float, medium: str = "air",
                            temp_c: float = 20.0) -> float:
    """f1 = v / (4L) -- the fundamental of a pipe closed at one end.

    EXTENSION, LABELED: this companion is standard physics but is
    NOT on the founder's plate; it is seated beside the plate's
    open pipe so the pair can be told apart, and it claims no
    plate authority.
    """
    if length_m <= 0:
        raise ValueError("length must be positive")
    return speed(medium, temp_c) / (4.0 * length_m)


def closed_pipe_harmonics(length_m: float, count: int, medium: str = "air",
                          temp_c: float = 20.0) -> list[float]:
    """The closed pipe's series: ODD multiples of f1 only."""
    f1 = closed_pipe_fundamental(length_m, medium, temp_c)
    return [f1 * (2 * k - 1) for k in range(1, count + 1)]


def pipe_length_for(freq_hz: float, medium: str = "air",
                    temp_c: float = 20.0, closed: bool = False) -> float:
    """L from a wanted fundamental -- the resonance relation inverted.

    MECHANISM: open, L = v / (2f); closed, L = v / (4f). The form
    a builder uses: name the note, get the pipe.
    """
    if freq_hz <= 0:
        raise ValueError("frequency must be positive")
    return speed(medium, temp_c) / ((4.0 if closed else 2.0) * freq_hz)


# ---------------------------------------------------------------------
# BEATS -- fb = |f1 - f2|.
# ---------------------------------------------------------------------

def beats(freq_a: float, freq_b: float) -> float:
    """fb = |f1 - f2| -- the pulse rate of two near tones.

    PLATE CHECK: 440 and 444 Hz pulse 4 times a second. The same
    relation, heard between the ears instead of in the air, is
    the Sigma bed's binaural offset.
    """
    return abs(freq_a - freq_b)


# ---------------------------------------------------------------------
# LOUDNESS -- the inverse square.
# ---------------------------------------------------------------------

def intensity_ratio(distance_from: float, distance_to: float) -> float:
    """I2 / I1 = (d1 / d2)^2 -- intensity kept across a move.

    MECHANISM: intensity falls with the SQUARE of the distance;
    doubling the distance keeps a quarter of the intensity.
    """
    if distance_from <= 0 or distance_to <= 0:
        raise ValueError("distances must be positive")
    return (distance_from / distance_to) ** 2


def level_change_db(distance_from: float, distance_to: float) -> float:
    """The level change in decibels across a move, -20*log10(d2/d1).

    PLATE CHECK: double the distance reads -6.02 dB -- the plate's
    "6 dB quieter" at full precision.
    """
    if distance_from <= 0 or distance_to <= 0:
        raise ValueError("distances must be positive")
    return -20.0 * math.log10(distance_to / distance_from)
