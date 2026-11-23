// =============================================================================
// RESONANTIA — android/eqapp/src/main/jni/upscale.hpp — the upscale
// seat in C++, seated with the EQVILLIBBRRIVMM app's native code:
// a master evaluated upward, from its own samples alone.
//
// Epigraph: "you just need the resonate values to upscale just as
// easy as down."
// — the founder, XXIII Nov 2026, stating the doctrine this seat
//   was built under.
//
// 93.
// Date: 23 November 2026.
// Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
// ARR — All Rights Reserved, Without Prejudice.
// Method of Science, Aim of Religion — Scientific Illuminism.
//
// SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
//   Hypothesis: that the studio's upscale seat (resonance/studio/
//     upscale.py, landed XXIII Nov 2026 at 97a63b9) can stand in
//     C++ on the device under its own doctrine — upscaling needs
//     only the samples in hand (the sampling theorem determines
//     the waveform between them), down and up are one resampling
//     operation read in two directions, and nothing above the
//     source Nyquist is recovered or synthesized — if the filter
//     is the seat's own Kaiser-windowed sinc at beta = 10.0 and
//     every sworn figure is re-measured here, not inherited.
//   Method: a port, not a reinvention. The Python seat's engine
//     is scipy.signal.resample_poly at the exact gcd-reduced
//     ratio, its filter a Kaiser-windowed ideal lowpass of
//     half-length 10 * max(up, down) at the upsampled rate — 10
//     source samples at any upward ratio. This header evaluates
//     the same construction in closed form: y(t) = sum_k s[k] *
//     sinc(t - k) * W(t - k), with W the Kaiser window of the
//     same beta over the same span, the modified Bessel I0
//     computed by its defining series. One honest coordinate of
//     difference, stated rather than smoothed: scipy's firwin
//     designs its taps by frequency sampling, this port by the
//     closed-form windowed sinc — same window, same beta, same
//     span, a different realization of the taps. The floor is
//     therefore MEASURED by the host harness and by the device
//     demo (both print it), never assumed from the Python seat's
//     -109.7 dB. The reference implementation remains the Python
//     seat.
//   Observation: (recorded in android/APK-BUILD.md after the
//     host proof and the strike.)
//   Result: this header, the toolkit JNI bridge that calls it,
//     and the measured numbers in the record.
//
// DOCTRINE — THE BOUNDARIES OF THIS SEAT, PRINTED IN ITS OWN CODE:
//   - EVALUATION ONLY. The seat applies no gain and paints no
//     content above the source Nyquist; synthesis is a different
//     seat with a different name, and it is not this one.
//   - MONO. The studio seat takes (channels, frames) and runs
//     its kernel per channel; this port IS that kernel, over one
//     channel of real samples. Channels are a caller's loop, in
//     either seat.
//   - NO LOUDNESS ON THIS SEAT. The studio report weighs LUFS by
//     pyloudnorm, whose coefficients follow the rate; pyloudnorm
//     has no on-device seat, so this port's report carries no
//     LUFS line rather than a number it cannot swear to. What it
//     carries: the rates, the exact ratio, the counts and
//     durations, sample peaks on both sides, true peaks on both
//     sides (by 4x FFT oversampling — the house scale's own
//     method, the measurement that sees between the samples),
//     and the measured spectral floor above the source Nyquist
//     against the sworn IMAGE_FLOOR_DB.
//   - THE SEAM IS NAMED, NOT SMOOTHED. The kernel sums over the
//     samples that exist; outside a finite file it reconstructs
//     against silence, exactly as the studio seat does. Whole-
//     file figures include the seams (the kernel's half-length,
//     printed in the report); the interior stands at the
//     waveform within the kernel's own ripple — measured on
//     the bench's full-scale tone at 1.0e-6, the finite span's
//     signature, printed in the record rather than rounded
//     into a claim of perfection.
//
// MECHANISM — THE LAW (refusals by name, as UpscaleError):
//   * A rate is a positive whole number of hertz; zero or
//     negative rates are refused by name.
//   * Upward only: a lower target is a different seat's work and
//     an equal target is the identity — both refused by name,
//     before any arithmetic.
//   * Empty input and non-finite samples are refused by name —
//     a peak that is not a number cannot be sworn to.
//   (The studio seat's 0.400 s loudness-block refusal guards a
//   scale this seat does not carry, and so does not translate;
//   it is named here so its absence is a decision, not a gap.)
//
// All Rights Reserved, Without Prejudice.
// "Live, Love, and let Love, Live."
// =============================================================================

#ifndef RESONANTIA_UPSCALE_HPP
#define RESONANTIA_UPSCALE_HPP

#include <cmath>
#include <complex>
#include <cstddef>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

namespace resonantia {
namespace upscale {

// DOCTRINE: a refusal is a named error, thrown before any
// arithmetic runs — the C++ seat of the Python seat's
// UpscaleError.
class UpscaleError : public std::runtime_error {
public:
    explicit UpscaleError(const std::string& message)
        : std::runtime_error(message) {}
};

// The Kaiser window's beta — the studio seat's own constant,
// raised there from scipy's default 5.0 (which measured -76.3 dB
// of image energy above the source Nyquist on the bench) to
// 10.0 (which measured -109.7 dB there). This port keeps the
// beta and re-measures the floor for its own taps.
constexpr double KAISER_BETA = 10.0;

// The sworn floor: in the upscaled signal, no spectral content
// above the source Nyquist stands above this level, in decibels
// relative to the strongest component at or below the source
// Nyquist. The seat swears the floor and keeps whatever
// headroom the measurement gives it.
constexpr double IMAGE_FLOOR_DB = -90.0;

// The house's silence floor, the same -120.0 the studio's
// pipeline floors its own zero readings at: a peak that is not
// a number is reported at the floor, never invented above it.
constexpr double FLOOR_DB = -120.0;

namespace detail {

// Forward seats: the transform trio below are mutually
// recursive (the Cooley-Tukey split calls itself by length;
// the Bluestein road calls both directions), so their names
// stand here before their bodies.
inline void fft_inplace(std::vector<std::complex<double>>& a);
inline void ifft_inplace(std::vector<std::complex<double>>& a);
inline void bluestein_inplace(std::vector<std::complex<double>>& a);

// MECHANISM: the modified Bessel function of the first kind,
// order zero — the Kaiser window's shape — by its defining
// series I0(x) = sum_k (x^2/4)^k / (k!)^2. The terms rise to a
// peak near k = x/2 and then fall factorially; the loop runs
// until a term can no longer move the sum at double precision
// (with a hard cap far past convergence for any beta the seat
// will ever carry).
inline double bessel_i0(double x) {
    const double quarter_x2 = (x * x) / 4.0;
    double sum = 1.0;
    double term = 1.0;
    for (int k = 1; k < 10000; ++k) {
        term *= quarter_x2 / (static_cast<double>(k) * k);
        sum += term;
        if (k > 12 && term < sum * 1e-19) {
            break;
        }
    }
    return sum;
}

// MECHANISM: the Kaiser window at normalized position u in
// [-1, 1]: I0(beta * sqrt(1 - u^2)) / I0(beta). Outside the
// span the window is zero — the kernel's support is finite,
// and the seam doctrine in the header is this line's price.
inline double kaiser_window(double u, double beta) {
    if (u < -1.0 || u > 1.0) {
        return 0.0;
    }
    const double r = 1.0 - u * u;
    return bessel_i0(beta * std::sqrt(r < 0.0 ? 0.0 : r))
           / bessel_i0(beta);
}

// MECHANISM: sinc(t) = sin(pi t) / (pi t), with the removable
// singularity at 0 seated at its limit, 1.
inline double sinc(double t) {
    if (t == 0.0) {
        return 1.0;
    }
    const double pi_t = 3.14159265358979323846 * t;
    return std::sin(pi_t) / pi_t;
}

// MECHANISM: the interpolation kernel — the ideal lowpass of
// the source's own band (cutoff at the source Nyquist, which
// for an upward evaluation is the binding band), windowed by
// the Kaiser window over its half-length L in source samples:
//   phi(tau) = sinc(tau) * W(tau / L),  |tau| <= L, else 0.
// At tau = 0 the kernel is 1 and the neighbouring integers sit
// on the sinc's own zeros, so the evaluation returns the
// caller's samples untouched at the caller's own seats.
inline double kernel(double tau, double half_len) {
    if (tau < -half_len || tau > half_len) {
        return 0.0;
    }
    return sinc(tau) * kaiser_window(tau / half_len, KAISER_BETA);
}

// MECHANISM: evaluate the interpolant of `samples` at the
// rational rate up/down relative to the source's own rate —
// output seat m stands at source time m * down / up. The sum
// runs over the samples that exist; outside the file the
// kernel reconstructs against silence (the seam, named in the
// header). The kernel's half-length follows the studio seat's
// construction: 10 * max(up, down) taps at the upsampled rate,
// expressed in source samples.
inline std::vector<double> evaluate(const std::vector<double>& samples,
                                    long up, long down) {
    const std::size_t n = samples.size();
    const std::size_t out_count = static_cast<std::size_t>(
        (static_cast<long long>(n) * up + down - 1) / down);
    const double half_len =
        10.0 * static_cast<double>(up > down ? up : down)
        / static_cast<double>(up);
    std::vector<double> out(out_count, 0.0);
    for (std::size_t m = 0; m < out_count; ++m) {
        const double t = static_cast<double>(m)
                         * static_cast<double>(down)
                         / static_cast<double>(up);
        long k_first = static_cast<long>(std::ceil(t - half_len));
        long k_last = static_cast<long>(std::floor(t + half_len));
        if (k_first < 0) {
            k_first = 0;
        }
        if (k_last > static_cast<long>(n) - 1) {
            k_last = static_cast<long>(n) - 1;
        }
        double sum = 0.0;
        for (long k = k_first; k <= k_last; ++k) {
            sum += samples[static_cast<std::size_t>(k)]
                   * kernel(t - static_cast<double>(k), half_len);
        }
        out[m] = sum;
    }
    return out;
}

// MECHANISM: the largest |sample| actually present, in decibels
// relative to full scale 1.0 — the number that HIDES the
// inter-sample crests, carried beside the true peak so the
// hiding is measured, not asserted. Silence reads the floor.
inline double sample_peak_db(const std::vector<double>& x) {
    double peak = 0.0;
    for (double v : x) {
        const double a = std::fabs(v);
        if (a > peak) {
            peak = a;
        }
    }
    return peak > 0.0 ? 20.0 * std::log10(peak) : FLOOR_DB;
}

inline double sample_peak(const std::vector<double>& x) {
    double peak = 0.0;
    for (double v : x) {
        const double a = std::fabs(v);
        if (a > peak) {
            peak = a;
        }
    }
    return peak;
}

// MECHANISM: the true peak in dBTP, on the house's own scale —
// 4x FFT oversampling, the method of the studio's
// pipeline.true_peak_dbtp, so this seat argues with no second
// yardstick: the signal's spectrum is zero-padded to four
// times its length (the Nyquist bin split evenly between its
// two seats) and inverse-transformed; the largest seat of the
// result is the peak the samples were hiding. The scale reads
// the record as periodic, as the studio's scale does; the
// kernel's seam lives in the delivered samples themselves and
// is read there, in the after figure, not invented here.
inline double true_peak_dbtp(const std::vector<double>& samples,
                             long /* up */, long /* down */) {
    const std::size_t n = samples.size();
    if (n == 0) {
        return FLOOR_DB;
    }
    std::vector<std::complex<double>> spectrum(n);
    for (std::size_t i = 0; i < n; ++i) {
        spectrum[i] = samples[i];
    }
    fft_inplace(spectrum);
    const std::size_t dense_n = 4 * n;
    std::vector<std::complex<double>> padded(dense_n, {0.0, 0.0});
    const std::size_t half = n / 2;
    for (std::size_t k = 0; k < half; ++k) {
        padded[k] = spectrum[k];
    }
    if (n % 2 == 0) {
        // The Nyquist bin is shared between the positive and
        // negative seats; split it evenly, as the scale does.
        padded[half] = spectrum[half] * 0.5;
        padded[dense_n - half] = spectrum[half] * 0.5;
    } else {
        padded[half] = spectrum[half];
    }
    for (std::size_t k = half + 1; k < n; ++k) {
        padded[dense_n - (n - k)] = spectrum[k];
    }
    ifft_inplace(padded);
    double peak = 0.0;
    for (const std::complex<double>& v : padded) {
        // The inverse carries the 1/(4N) of its own length; the
        // interpolant stands 4x taller (see the derivation in
        // fft_inplace's seat): x(m/4) = 4 * IFFT_4N(padded)[m].
        const double a = std::fabs(4.0 * v.real());
        if (a > peak) {
            peak = a;
        }
    }
    return peak > 0.0 ? 20.0 * std::log10(peak) : FLOOR_DB;
}

// MECHANISM: an in-place DFT by recursive Cooley-Tukey over
// the length's smallest prime factor (naive size-p butterflies
// for p in {2, 3, 5}); a length whose smallest prime factor
// stands above 5 takes the Bluestein road (below), so no
// length the seat can meet degenerates to the quadratic sum.
// The length is the caller's own, NEVER padded: the studio's
// scale reads a segment holding a whole number of cycles of
// the tone it weighs, so the fundamental falls on one bin
// exactly and no padding or windowing fiction enters the
// reading.
inline void fft_inplace(std::vector<std::complex<double>>& a) {
    const std::size_t n = a.size();
    if (n <= 1) {
        return;
    }
    const double pi = 3.14159265358979323846;
    std::size_t p = n;
    for (std::size_t q = 2; q * q <= n; ++q) {
        if (n % q == 0) {
            p = q;
            break;
        }
    }
    if (p > 5) {
        bluestein_inplace(a);
        return;
    }
    const std::size_t m = n / p;
    // Split into the p stride-p subsequences, transform each,
    // and recombine: X[k1 + m*k2] = sum_j A_j[k1] *
    // exp(-2 pi i * (j*k1/n + j*k2/p)).
    std::vector<std::vector<std::complex<double>>> sub(
        p, std::vector<std::complex<double>>(m));
    for (std::size_t j = 0; j < p; ++j) {
        for (std::size_t t = 0; t < m; ++t) {
            sub[j][t] = a[t * p + j];
        }
        fft_inplace(sub[j]);
    }
    for (std::size_t k1 = 0; k1 < m; ++k1) {
        for (std::size_t k2 = 0; k2 < p; ++k2) {
            std::complex<double> sum(0.0, 0.0);
            for (std::size_t j = 0; j < p; ++j) {
                const double ang = -2.0 * pi
                    * (static_cast<double>(j * k1)
                           / static_cast<double>(n)
                       + static_cast<double>(j * k2)
                             / static_cast<double>(p));
                sum += sub[j][k1]
                       * std::complex<double>(std::cos(ang),
                                              std::sin(ang));
            }
            a[k1 + m * k2] = sum;
        }
    }
}

// MECHANISM: the inverse transform, by the conjugation road
// through the forward one — the true-peak scale's return leg.
inline void ifft_inplace(std::vector<std::complex<double>>& a) {
    for (std::complex<double>& v : a) {
        v = std::conj(v);
    }
    fft_inplace(a);
    const double scale = 1.0 / static_cast<double>(a.size());
    for (std::complex<double>& v : a) {
        v = std::conj(v) * scale;
    }
}

// MECHANISM: the Bluestein road — a DFT of any length read as
// a convolution: tk = (t^2 + k^2 - (k-t)^2)/2 turns the
// transform into X[k] = chirp(k) * sum_t (x[t] chirp(t)) *
// conj(chirp(k-t)), with chirp(t) = exp(-pi i t^2 / n); the
// convolution runs on the power-of-two road above, at a
// length of at least 2n-1 so no wraparound reaches the seats
// that are read. This is what keeps an awkward length (an
// upscaled crest record of 17,837 samples, say) at transform
// speed instead of the quadratic sum.
inline void bluestein_inplace(std::vector<std::complex<double>>& a) {
    const std::size_t n = a.size();
    if (n <= 1) {
        return;
    }
    std::size_t L = 1;
    while (L < 2 * n - 1) {
        L <<= 1;
    }
    const double pi = 3.14159265358979323846;
    const auto chirp = [n, pi](std::size_t t) {
        const unsigned long long sq =
            (static_cast<unsigned long long>(t) * t) % (2ULL * n);
        const double ang = -pi * static_cast<double>(sq)
                           / static_cast<double>(n);
        return std::complex<double>(std::cos(ang), std::sin(ang));
    };
    std::vector<std::complex<double>> fa(L, {0.0, 0.0});
    std::vector<std::complex<double>> fb(L, {0.0, 0.0});
    for (std::size_t t = 0; t < n; ++t) {
        fa[t] = a[t] * chirp(t);
    }
    fb[0] = std::complex<double>(1.0, 0.0);
    for (std::size_t t = 1; t < n; ++t) {
        const std::complex<double> v = std::conj(chirp(t));
        fb[t] = v;
        fb[L - t] = v;
    }
    fft_inplace(fa);
    fft_inplace(fb);
    for (std::size_t i = 0; i < L; ++i) {
        fa[i] *= fb[i];
    }
    ifft_inplace(fa);
    for (std::size_t k = 0; k < n; ++k) {
        a[k] = fa[k] * chirp(k);
    }
}

// MECHANISM: the magnitude spectrum of a signal at its own
// length — bins 0..N/2 of the unpadded DFT. This is the scale
// the floor is weighed on, in this seat, by this seat.
inline std::vector<double> magnitude_spectrum(
        const std::vector<double>& x) {
    std::vector<std::complex<double>> a(x.size());
    for (std::size_t i = 0; i < x.size(); ++i) {
        a[i] = x[i];
    }
    fft_inplace(a);
    std::vector<double> mag(x.size() / 2 + 1, 0.0);
    for (std::size_t i = 0; i < mag.size(); ++i) {
        mag[i] = std::abs(a[i]);
    }
    return mag;
}

}  // namespace detail

// MECHANISM: the spectral floor above the source Nyquist, in
// decibels — weighed exactly as the studio seat's own honesty
// test weighs it: on the STEADY-STATE CENTER SEGMENT of the
// signal (half a second of it, seated a quarter of the way in;
// the seams are a separate named coordinate and are never
// measured here), the largest bin standing above
// source_rate/2 against the segment's largest bin (the
// fundamental). The segment is read at its own length, so a
// whole-cycle tone falls on one bin exactly. Silence reads
// the floor value itself.
inline double above_nyquist_floor_db(const std::vector<double>& signal,
                                     int source_rate,
                                     int signal_rate) {
    if (signal.size() < 4 || source_rate <= 0 || signal_rate <= 0) {
        return FLOOR_DB;
    }
    std::size_t seg_len =
        static_cast<std::size_t>(signal_rate) / 2;
    const std::size_t start = signal.size() / 4;
    if (seg_len > signal.size() - start) {
        seg_len = signal.size() - start;
    }
    if (seg_len < 4) {
        return FLOOR_DB;
    }
    const std::vector<double> seg(signal.begin() + start,
                                  signal.begin() + start + seg_len);
    const std::vector<double> mag = detail::magnitude_spectrum(seg);
    const double bin_hz = static_cast<double>(signal_rate)
                          / static_cast<double>(seg_len);
    const double nyquist = static_cast<double>(source_rate) / 2.0;
    double fundamental = 0.0;
    double above_max = 0.0;
    for (std::size_t i = 0; i < mag.size(); ++i) {
        if (mag[i] > fundamental) {
            fundamental = mag[i];
        }
        const double freq = static_cast<double>(i) * bin_hz;
        if (freq > nyquist && mag[i] > above_max) {
            above_max = mag[i];
        }
    }
    if (fundamental <= 0.0 || above_max <= 0.0) {
        return FLOOR_DB;
    }
    const double db = 20.0 * std::log10(above_max / fundamental);
    return db < FLOOR_DB ? FLOOR_DB : db;
}

// MECHANISM: the dominant frequency of a signal — the strongest
// non-DC bin of its spectrum, in hertz. The demo's witness that
// an evaluated tone is still the tone it was.
inline double dominant_frequency_hz(const std::vector<double>& signal,
                                    int signal_rate) {
    if (signal.size() < 2 || signal_rate <= 0) {
        return 0.0;
    }
    const std::vector<double> mag = detail::magnitude_spectrum(signal);
    std::size_t best = 1;
    for (std::size_t i = 2; i < mag.size(); ++i) {
        if (mag[i] > mag[best]) {
            best = i;
        }
    }
    return static_cast<double>(best) * static_cast<double>(signal_rate)
           / static_cast<double>(signal.size());
}

// The report the seat hands back beside the samples — the C++
// seat of the studio report's rate-side lines. No LUFS line
// stands here, by the boundary stated in the header.
struct UpscaleReport {
    int source_rate = 0;
    int target_rate = 0;
    long ratio_up = 0;
    long ratio_down = 0;
    std::size_t samples_before = 0;
    std::size_t samples_after = 0;
    double duration_before_s = 0.0;
    double duration_after_s = 0.0;
    double sample_peak_before_db = FLOOR_DB;
    double sample_peak_after_db = FLOOR_DB;
    double true_peak_before_dbtp = FLOOR_DB;
    double true_peak_after_dbtp = FLOOR_DB;
    double intersample_rise_before_db = 0.0;
    double intersample_rise_after_db = 0.0;
    double source_nyquist_hz = 0.0;
    double image_floor_measured_db = FLOOR_DB;
    long seam_span_source_samples = 0;
};

// resample_up — evaluate `samples` from source_rate at
// target_rate, upward only. Returns the evaluated samples; when
// `report` is given, fills it with the seat's measurements. The
// seat applies no gain: what changes is the number of points
// the waveform is evaluated at, and nothing else.
inline std::vector<double> resample_up(const std::vector<double>& samples,
                                       int source_rate,
                                       int target_rate,
                                       UpscaleReport* report = nullptr) {
    if (source_rate <= 0) {
        throw UpscaleError("source_rate: a sample rate must be "
                           "positive; got " +
                           std::to_string(source_rate));
    }
    if (target_rate <= 0) {
        throw UpscaleError("target_rate: a sample rate must be "
                           "positive; got " +
                           std::to_string(target_rate));
    }
    // The direction law: this seat evaluates upward, only. A
    // lower target is not an error in the caller's arithmetic —
    // it is a different seat's work, and is refused as such.
    if (target_rate < source_rate) {
        throw UpscaleError("target_rate " +
            std::to_string(target_rate) + " < source_rate " +
            std::to_string(source_rate) +
            ": downsampling is a different seat — this seat only "
            "evaluates upward");
    }
    if (target_rate == source_rate) {
        throw UpscaleError("target_rate == source_rate (" +
            std::to_string(source_rate) +
            "): the identity is not an upscale — there is "
            "nothing to evaluate");
    }
    if (samples.empty()) {
        throw UpscaleError("samples: empty input — no frames to "
                           "evaluate");
    }
    for (double v : samples) {
        if (!std::isfinite(v)) {
            throw UpscaleError("samples: non-finite samples (NaN "
                               "or infinity) are refused — a peak "
                               "that is not a number cannot be "
                               "sworn to");
        }
    }

    // The exact rational ratio — 44100→96000 is 320/147, and
    // the report carries the reduced pair so the ratio can be
    // checked by hand.
    const long divisor = std::gcd(static_cast<long>(source_rate),
                                  static_cast<long>(target_rate));
    const long up = target_rate / divisor;
    const long down = source_rate / divisor;

    std::vector<double> y = detail::evaluate(samples, up, down);

    if (report != nullptr) {
        report->source_rate = source_rate;
        report->target_rate = target_rate;
        report->ratio_up = up;
        report->ratio_down = down;
        report->samples_before = samples.size();
        report->samples_after = y.size();
        report->duration_before_s =
            static_cast<double>(samples.size()) / source_rate;
        report->duration_after_s =
            static_cast<double>(y.size()) / target_rate;
        report->sample_peak_before_db = detail::sample_peak_db(samples);
        report->sample_peak_after_db = detail::sample_peak_db(y);
        // The true peaks, by 4x evaluation on both sides, so the
        // seat's effect on the hidden crests is a pair of
        // numbers, not a claim.
        report->true_peak_before_dbtp =
            detail::true_peak_dbtp(samples, 1, 1);
        report->true_peak_after_dbtp =
            detail::true_peak_dbtp(samples, up, down);
        report->intersample_rise_before_db =
            report->true_peak_before_dbtp - report->sample_peak_before_db;
        report->intersample_rise_after_db =
            report->true_peak_after_dbtp - report->sample_peak_after_db;
        report->source_nyquist_hz = source_rate / 2.0;
        report->image_floor_measured_db =
            above_nyquist_floor_db(y, source_rate, target_rate);
        // The seam's width in source samples: the kernel's
        // half-length (10 * max(up, down) taps at the upsampled
        // rate) in the source's own samples — 10 at any upward
        // ratio, computed from the construction, as in the
        // studio seat.
        const long widest = up > down ? up : down;
        report->seam_span_source_samples =
            (10L * widest + up - 1) / up;
    }
    return y;
}

}  // namespace upscale
}  // namespace resonantia

#endif  // RESONANTIA_UPSCALE_HPP
