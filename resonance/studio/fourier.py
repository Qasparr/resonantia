#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — studio/fourier.py — the Fourier transform seated as
# a named instrument in the Python studio: transform and inverse
# on the real-signal road, an amplitude-true spectrum, dominant
# frequency, band energy, the honesty floor above a cutoff, and
# the Hann-windowed short-time transform.
#
# Epigraph: "Fourier Transform: From Signals to Frequencies."
# — the plate the founder brought to the desk (XXIII Nov 2026):
#   Joseph Fourier · 1822 — "Revealing the hidden frequencies
#   inside complex signals."
#
# 93.
# Date: 23 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
#   Hypothesis: that Fourier, which the house already uses
#     everywhere as scattered hand-rolled calls, gains its true
#     seat as ONE named instrument with ONE scaling law and ONE
#     floor law, judged only against signals whose spectra are
#     known in closed form before any code runs — the seat
#     studio/nabla.py now holds for ∇, held here for the
#     transform.
#   Method: numpy's rFFT road under the house's own validation
#     (real finite 1-D signals, positive finite rates, every
#     refusal by name), a single-sided amplitude scaling under
#     which a sine of amplitude A reads A at its bin (window
#     coherent gain divided out when windowed), and the upscale
#     seat's own measurement scale for the floor: the unwindowed,
#     unpadded transform of exactly the samples handed in.
#   Observation: on the sworn signals the seat is exact where
#     the mathematics is exact. The round trip over an odd
#     length (4,095 samples, seeded tones + noise) returns the
#     signal with worst error 4.4e-16; Parseval's energies agree
#     to a relative 4.1e-16. A whole-cycle 1 kHz sine of
#     amplitude 0.5 at 48 kHz reads exactly 1000.0 Hz and
#     exactly 0.5 at its bin, unwindowed AND Hann-windowed with
#     the coherent gain divided out. A 5-sample delay leaves
#     the magnitude spectrum unmoved (worst 4.2e-17) and rotates
#     the tone bin's phase by exactly the delay law's angle.
#     The floor above 5 kHz of a pure 1 kHz tone stands at the
#     house floor, −120.0 dB; seat a component at −40 dB above
#     the cutoff and the floor reads −40.0000000000002 dB.
#     Band energies match their closed-form shares to ~1e-13.
#     A 300→1500 Hz chirp tracked through the STFT holds its
#     per-frame dominant bin within half a bin of the chirp's
#     instantaneous frequency, rising monotonically. The full
#     battery stands in tests/test_studio_fourier.py.
#   Result: this module. No existing module was touched: the
#     hand-rolled call sites named in the docstring keep their
#     own roads until a separate order adopts this seat.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""The Fourier transform, seated as a named studio instrument.

DOCTRINE — WHAT THE TRANSFORM IS, AND WHERE IT ALREADY SERVES:
  The Fourier transform re-reads a signal in the frequency
domain: the same waveform, weighed as a sum of sinusoids, each
with a frequency, an amplitude, and a phase. Joseph Fourier's
claim of 1822 — that any signal separates into frequency
components — is the load-bearing fact under half the house's
instruments, and until this seat it stood in the house as
scattered hand-rolled calls, each with its own scaling habit:

  * resonance/binaural/adaptive.py — a Hann-windowed rFFT read
    for spectral flux;
  * resonance/synth/voices.py — FFT-mask bandpass and highpass
    filters;
  * resonance/diagnostics/verify.py — FFT verification of the
    binaural renders, and resonance/binaural/generator.py,
    built FFT-verifiable by design;
  * the pipeline's true_peak_dbtp (studio/pipeline.py) — true
    peaks by 4x FFT oversampling, the master law's own scale;
  * studio/upscale.py — the spectral honesty floor above the
    source Nyquist, the measurement this seat's floor_above
    generalizes;
  * on the device, the C++ upscale.hpp carries a private FFT /
    IFFT with a Bluestein road, struck for the APK's one job.

  Those are the existing roads, and this module does not
replace them: adoption of this seat by any call site is a
separate order, taken site by site. What this module is, is
the SWORN INSTRUMENT — one scaling law, one floor law, one
validation law, judged analytically — that any of those roads,
and any new work (the visualizer's time-frequency pictures
among it), can be weighed against.

MECHANISM — THE SCALING LAW (one law, sworn everywhere here):
  transform() returns the raw rFFT coefficients beside their
frequency axis in Hz, the record's length, and its rate;
inverse() applies the inverse rFFT at that recorded length,
so the round trip is exact to floating-point rounding,
odd lengths included. spectrum() reads AMPLITUDE: the
single-sided scaling under which a sine of amplitude A reads
exactly A at its bin — interior bins doubled, the DC and
Nyquist bins not — and when a window is applied its COHERENT
GAIN (the window's mean) is divided out, so a whole-cycle tone
reads its true amplitude windowed or not. The Hann window
seated here is the PERIODIC Hann, w[n] = 1/2 − 1/2·cos(2πn/N),
whose coherent gain is exactly 1/2. Energy obeys Parseval
under this law: the single-sided power sum of the raw
coefficients, divided by N, is the time-domain energy.

MECHANISM — THE FLOOR LAW (the upscale seat's scale, kept):
  floor_above() measures on exactly the samples handed in —
the steady segment, as the upscale test hands the steady
centre of its render — UNWINDOWED and UNPADDED, so a
whole-cycle tone falls on one bin exactly and no windowing
fiction enters the reading. The reading is the strongest bin
above the cutoff, in dB against the signal's dominant bin.
Readings are floored at −120.0 dB, the house's silence floor
(the number pipeline.py floors at): a level is reported at
the floor, never invented above it.

MECHANISM — THE SHAPE LAW (refusals by name, the house's law):
  * A signal is a real, finite, 1-D array of at least 2
    samples. Complex input is refused before conversion (an
    imaginary part is never silently dropped), as are empty,
    non-finite, non-numeric, and multi-channel arrays — a
    caller with channels hands one channel at a time.
  * A sample rate is a positive, finite number. Zero,
    negative, non-finite, and non-numeric rates are refused
    by name.
  * Bands and cutoffs must sit inside (0, Nyquist]; a band's
    low edge must lie below its high edge. Violations are
    refused by name, never clipped into compliance.
  * The STFT seats complete frames only — no padding fiction
    at the edges; a signal shorter than one frame is refused
    by name.

AXIS LAW: frequencies come back in Hz, ascending, on the rFFT
axis (DC first, Nyquist last for even lengths). Phases are in
radians, as numpy.angle reads them.
"""

from typing import NamedTuple, Optional, Tuple

import numpy as np

__all__ = [
    "FourierError",
    "FourierTransform",
    "FLOOR_DB",
    "transform",
    "inverse",
    "spectrum",
    "dominant_frequency",
    "band_energy_db",
    "floor_above",
    "stft",
]


class FourierError(ValueError):
    """A signal, rate, or band refused by the shape law, by name.

    Subclasses ValueError so existing house code that catches
    ValueError around numeric work catches this too; the tests
    assert FourierError itself, so a refusal can never pass
    silently as some other error.
    """


# The house's silence floor: readings at or below it are
# reported AT it, never invented above it — the number
# pipeline.py floors at, kept here so the seat argues with
# no second yardstick.
FLOOR_DB = -120.0


class FourierTransform(NamedTuple):
    """One transform record: the axis, the coefficients, the span.

    frequencies — the rFFT axis in Hz, ascending.
    coefficients — the raw (unnormalized) rFFT coefficients;
        inverse() of this record is the exact round trip.
    n_samples — the time-domain length the coefficients came
        from; the inverse needs it because an odd length cannot
        be inferred from the coefficient count.
    sample_rate — the rate in Hz the axis was built from.
    """

    frequencies: np.ndarray
    coefficients: np.ndarray
    n_samples: int
    sample_rate: float


def _as_signal(samples, name: str = "samples") -> np.ndarray:
    """MECHANISM: bring a caller's signal under the shape law.

    Converts to a float ndarray and refuses, by name: complex
    input (before conversion, so nothing is silently dropped),
    non-numeric input, anything not 1-D, fewer than 2 samples,
    and any non-finite sample — a NaN in the time domain is a
    fiction in every bin.
    """
    if np.iscomplexobj(samples):
        raise FourierError(f"{name}: complex signals are refused — "
                           "this seat is the real-signal road; hand "
                           "the real channel you mean to weigh")
    try:
        arr = np.asarray(samples, dtype=float)
    except (TypeError, ValueError) as exc:
        raise FourierError(f"{name}: not a real numeric array "
                           f"({exc})") from exc
    if arr.ndim != 1:
        raise FourierError(f"{name}: a signal is 1-D; got "
                           f"{arr.ndim}-D — hand one channel at "
                           "a time")
    if arr.size < 2:
        raise FourierError(f"{name}: {arr.size} sample(s); a "
                           "transform needs at least 2")
    if not np.all(np.isfinite(arr)):
        raise FourierError(f"{name}: non-finite samples are "
                           "refused — every bin would inherit "
                           "the fiction")
    return arr


def _as_rate(sample_rate, name: str = "sample_rate") -> float:
    """MECHANISM: a rate is one positive, finite number.

    Booleans are refused as what they are (a flag, not a rate);
    zero, negative, non-finite, and non-numeric rates are
    refused by name — an axis built on them is fiction.
    """
    if isinstance(sample_rate, bool) or \
            not isinstance(sample_rate, (int, float, np.integer,
                                        np.floating)):
        raise FourierError(f"{name}: not a number; got "
                           f"{type(sample_rate).__name__}")
    rate = float(sample_rate)
    if not np.isfinite(rate) or rate <= 0.0:
        raise FourierError(f"{name}: must be positive and "
                           f"finite; got {rate}")
    return rate


def _hann_periodic(n: int) -> np.ndarray:
    """MECHANISM: the periodic Hann window of length n.

    w[k] = 1/2 − 1/2·cos(2πk/n) — the DFT-even form seated for
    spectral work, whose coherent gain (its mean) is exactly
    1/2 at every length, so the amplitude law's correction is
    a number, not an approximation.
    """
    k = np.arange(n)
    return 0.5 - 0.5 * np.cos(2.0 * np.pi * k / n)


def _window(window, n: int, name: str = "window") -> np.ndarray:
    """MECHANISM: resolve the window argument to an array.

    None seats the rectangular window (ones — no window);
    "hann" seats the periodic Hann. Any other name is refused
    by name: a window the seat has not sworn to is not quietly
    approximated.
    """
    if window is None:
        return np.ones(n)
    if isinstance(window, str) and window.lower() == "hann":
        return _hann_periodic(n)
    raise FourierError(f"{name}: {window!r} is not a seated "
                       "window; give \"hann\" or None")


def _amplitude_spectrum(coefficients: np.ndarray, n: int,
                        coherent_gain: float) -> np.ndarray:
    """MECHANISM: raw rFFT bins under the amplitude law.

    Interior bins are doubled (their mirror energy lives in
    the negative frequencies the rFFT folds away); the DC bin
    and — for even n — the Nyquist bin are not, having no
    mirror. The whole is divided by n and by the window's
    coherent gain, so a sine of amplitude A reads A at its bin.
    """
    mag = np.abs(coefficients) / (n * coherent_gain)
    if mag.size > 1:
        mag[1:] *= 2.0
        if n % 2 == 0:
            mag[-1] /= 2.0  # the Nyquist bin has no mirror
    return mag


def transform(samples, sample_rate) -> FourierTransform:
    """The forward transform: samples → (axis, coefficients).

    MECHANISM: numpy.fft.rfft under the shape law, the axis
    from numpy.fft.rfftfreq at the caller's rate. The
    coefficients are the RAW rFFT output — the scaling law
    lives in spectrum() and in inverse(), so this record is
    the lossless seat: inverse(transform(x)) is x itself, to
    floating-point rounding, at any length.
    """
    x = _as_signal(samples)
    rate = _as_rate(sample_rate)
    coefficients = np.fft.rfft(x)
    frequencies = np.fft.rfftfreq(x.size, d=1.0 / rate)
    return FourierTransform(frequencies=frequencies,
                            coefficients=coefficients,
                            n_samples=int(x.size),
                            sample_rate=rate)


def inverse(spectrum_record, n_samples: Optional[int] = None
            ) -> np.ndarray:
    """The inverse transform: a transform record → its samples.

    MECHANISM: numpy.fft.irfft at the record's own length —
    the exact round trip of transform(). A bare coefficient
    array is also accepted, but then n_samples must be given:
    an odd time-domain length cannot be inferred from the
    coefficient count, and a guessed length is a fiction the
    seat refuses by name.
    """
    if isinstance(spectrum_record, FourierTransform):
        coefficients = spectrum_record.coefficients
        n = spectrum_record.n_samples if n_samples is None \
            else n_samples
    else:
        coefficients = np.asarray(spectrum_record)
        if coefficients.dtype.kind != "c":
            raise FourierError("inverse: coefficients must be "
                               "complex — hand the record "
                               "transform() returned")
        if n_samples is None:
            raise FourierError("inverse: a bare coefficient "
                               "array needs n_samples — an odd "
                               "length cannot be inferred, and "
                               "the seat does not guess")
        n = n_samples
    if coefficients.ndim != 1 or coefficients.size == 0:
        raise FourierError("inverse: coefficients are a "
                           "non-empty 1-D array")
    if not np.all(np.isfinite(coefficients)):
        raise FourierError("inverse: non-finite coefficients "
                           "are refused")
    if not isinstance(n, (int, np.integer)) or n < 2:
        raise FourierError(f"inverse: n_samples must be an "
                           f"integer of at least 2; got {n!r}")
    return np.fft.irfft(coefficients, n=int(n))


def spectrum(samples, sample_rate, window: Optional[str] = "hann"
             ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(frequencies, magnitude, phase) under the amplitude law.

    MECHANISM: the signal is windowed (periodic Hann by
    default; None for the rectangular road), transformed, and
    read under the scaling law — magnitude in the signal's own
    amplitude units, phase in radians from the windowed
    coefficients. A whole-cycle sine of amplitude A reads A at
    its bin on either road, the window's coherent gain divided
    out on the Hann road.
    """
    x = _as_signal(samples)
    rate = _as_rate(sample_rate)
    w = _window(window, x.size)
    coefficients = np.fft.rfft(x * w)
    frequencies = np.fft.rfftfreq(x.size, d=1.0 / rate)
    magnitude = _amplitude_spectrum(coefficients, x.size,
                                    float(np.mean(w)))
    phase = np.angle(coefficients)
    return frequencies, magnitude, phase


def dominant_frequency(samples, sample_rate) -> Tuple[float, float]:
    """(hz, magnitude) of the strongest component, unwindowed.

    MECHANISM: the argmax of the unwindowed amplitude
    spectrum — the seat a caller asks "what is this signal,
    mostly?" of. The magnitude is under the amplitude law, so
    it reads in the signal's own units.
    """
    frequencies, magnitude, _ = spectrum(samples, sample_rate,
                                         window=None)
    k = int(np.argmax(magnitude))
    return float(frequencies[k]), float(magnitude[k])


def band_energy_db(samples, sample_rate, low_hz, high_hz,
                   reference: str = "total") -> float:
    """The energy inside [low_hz, high_hz], in dB of the total.

    MECHANISM: the unwindowed rFFT's single-sided power
    (Parseval's weights) summed over the bins whose frequency
    lies inside the band, against the total power over all
    bins. reference="total" is the seated reference; any other
    is refused by name. An empty band — or a silent signal —
    reads at the house floor, FLOOR_DB, never above invention.
    """
    x = _as_signal(samples)
    rate = _as_rate(sample_rate)
    if reference != "total":
        raise FourierError(f"reference: {reference!r} is not a "
                           "seated reference; give \"total\"")
    nyquist = rate / 2.0
    for name, edge in (("low_hz", low_hz), ("high_hz", high_hz)):
        if isinstance(edge, bool) or not isinstance(
                edge, (int, float, np.integer, np.floating)) \
                or not np.isfinite(float(edge)):
            raise FourierError(f"{name}: not a finite number; "
                               f"got {edge!r}")
    low, high = float(low_hz), float(high_hz)
    if low < 0.0 or high > nyquist:
        raise FourierError(f"band: [{low}, {high}] Hz must sit "
                           f"inside [0, {nyquist}] Hz at this "
                           "rate")
    if low >= high:
        raise FourierError(f"band: low_hz ({low}) must lie "
                           f"below high_hz ({high})")
    coefficients = np.fft.rfft(x)
    frequencies = np.fft.rfftfreq(x.size, d=1.0 / rate)
    power = np.abs(coefficients) ** 2
    if power.size > 1:
        power[1:] *= 2.0
        if x.size % 2 == 0:
            power[-1] /= 2.0  # Nyquist bin: no mirror
    total = float(np.sum(power))
    if total <= 0.0:
        return FLOOR_DB
    in_band = (frequencies >= low) & (frequencies <= high)
    band = float(np.sum(power[in_band]))
    if band <= 0.0:
        return FLOOR_DB
    return max(10.0 * np.log10(band / total), FLOOR_DB)


def floor_above(samples, sample_rate, cutoff_hz) -> float:
    """The strongest level above cutoff_hz, dB vs the dominant.

    MECHANISM: the upscale seat's honesty measurement,
    generalized — the unwindowed, unpadded rFFT of exactly
    the samples handed in (the steady segment, as the
    upscale test hands the steady centre of its render), the
    strongest bin strictly above the cutoff weighed against
    the signal's dominant bin, 20·log10 of the ratio, floored
    at the house floor. Nothing above the cutoff reads at
    FLOOR_DB — reported at the floor, never invented above it.
    """
    x = _as_signal(samples)
    rate = _as_rate(sample_rate)
    if isinstance(cutoff_hz, bool) or not isinstance(
            cutoff_hz, (int, float, np.integer, np.floating)) \
            or not np.isfinite(float(cutoff_hz)):
        raise FourierError(f"cutoff_hz: not a finite number; "
                           f"got {cutoff_hz!r}")
    cutoff = float(cutoff_hz)
    nyquist = rate / 2.0
    if cutoff <= 0.0 or cutoff > nyquist:
        raise FourierError(f"cutoff_hz: {cutoff} must sit "
                           f"inside (0, {nyquist}] Hz at this "
                           "rate")
    magnitudes = np.abs(np.fft.rfft(x))
    frequencies = np.fft.rfftfreq(x.size, d=1.0 / rate)
    dominant = float(np.max(magnitudes))
    if dominant <= 0.0:
        return FLOOR_DB
    above = magnitudes[frequencies > cutoff]
    if above.size == 0:
        return FLOOR_DB
    strongest = float(np.max(above))
    if strongest <= 0.0:
        return FLOOR_DB
    return max(20.0 * np.log10(strongest / dominant), FLOOR_DB)


def stft(samples, sample_rate, frame_size, hop
         ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(times, frequencies, magnitude) — the time-frequency seat.

    MECHANISM: complete frames only, seated every hop samples
    from the signal's start, each framed by the periodic Hann
    and read under the amplitude law — so a steady tone reads
    its own amplitude in every frame that holds it, and a
    frame's dominant bin is that frame's pitch. Times are the
    frame CENTRES in seconds. A signal shorter than one frame
    is refused by name; no frame is ever padded into being.
    """
    x = _as_signal(samples)
    rate = _as_rate(sample_rate)
    for name, value in (("frame_size", frame_size), ("hop", hop)):
        if isinstance(value, bool) or not isinstance(
                value, (int, np.integer)):
            raise FourierError(f"{name}: must be an integer; "
                               f"got {value!r}")
    frame_size, hop = int(frame_size), int(hop)
    if frame_size < 2:
        raise FourierError(f"frame_size: at least 2; got "
                           f"{frame_size}")
    if hop < 1:
        raise FourierError(f"hop: at least 1; got {hop}")
    if x.size < frame_size:
        raise FourierError(f"stft: {x.size} sample(s) cannot "
                           f"fill one frame of {frame_size}; "
                           "the seat pads nothing")
    w = _hann_periodic(frame_size)
    gain = float(np.mean(w))
    frequencies = np.fft.rfftfreq(frame_size, d=1.0 / rate)
    starts = range(0, x.size - frame_size + 1, hop)
    magnitude = np.empty((len(starts), frequencies.size))
    for i, start in enumerate(starts):
        frame = x[start:start + frame_size] * w
        coefficients = np.fft.rfft(frame)
        magnitude[i] = _amplitude_spectrum(coefficients,
                                           frame_size, gain)
    times = (np.array(list(starts), dtype=float)
             + frame_size / 2.0) / rate
    return times, frequencies, magnitude
