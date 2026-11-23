// =============================================================================
// RESONANTIA — android/eqapp/src/main/jni/toolkit_jni.cpp — the JNI
// bridge for the house toolkit's two C++ seats: nabla (the Del
// operator) and upscale (evaluation upward), computed ON THE
// DEVICE at tap time.
//
// Epigraph: "A compact symbol. A powerful idea."
//
// 93.
// Date: 23 November 2026.
// Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
// ARR — All Rights Reserved, Without Prejudice.
// Method of Science, Aim of Religion — Scientific Illuminism.
//
// SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
//   Hypothesis: that the two studio seats the founder ordered
//     ported ("Can you write it in cpp to be used in the app?",
//     XXIII Nov 2026) can run their own sworn demonstrations on
//     the phone — the nabla checks against the closed-form
//     fields, the upscale demo against the tone and the hidden
//     crest — and print MEASURED numbers, computed at the tap,
//     that stand beside the bench's host proof of the same code
//     (android/eqapp/host/toolkit_host_test.cpp, quoted in
//     android/APK-BUILD.md).
//   Method: two JNI entries beside eq_jni.cpp's runSuite, in the
//     same library. Each builds its built-in test fields/tones,
//     calls the port headers (nabla.hpp, upscale.hpp) exactly as
//     the host harness calls them, formats the measured results,
//     and returns them as a String. Nothing is bundled, cached,
//     or read from disk: if the numbers on the screen differ
//     from the bench's, the screen is what the device measured
//     and the difference is itself the report.
//   Observation: (the host proof stands in APK-BUILD.md; the
//     on-device figures are the founder's tap to make.)
//   Result: this bridge.
//
// DOCTRINE:
//   - The demonstrations are demonstrations: built-in fields
//     and tones, named as such on the screen. No wording here
//     or in the app claims the seats have been wired to the
//     founder's files — they compute what they are shown
//     computing, and the headers name their provenance (the
//     studio seats and their commits) as provenance, not as
//     a claim that the phone ran Python.
//   - A thrown error is reported on the screen, never swallowed
//     — the same law eq_jni.cpp keeps for the suite.
//
// All Rights Reserved, Without Prejudice.
// "Live, Love, and let Love, Live."
// =============================================================================

#include <jni.h>

#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

#include "nabla.hpp"
#include "upscale.hpp"

namespace {

using resonantia::nabla::Field;

// MECHANISM: a small scientific-notation formatter for the
// measured errors — three significant digits, the shape the
// bench record quotes.
std::string sci(double v) {
    char buf[64];
    std::snprintf(buf, sizeof(buf), "%.3e", v);
    return buf;
}

std::string fixed2(double v) {
    char buf[64];
    std::snprintf(buf, sizeof(buf), "%.2f", v);
    return buf;
}

// MECHANISM: build a field on a grid from a function of the
// seat's coordinates — the same meshgrid the host harness
// builds, in array-axis order (axis 0 is x, 1 is y, 2 is z).
Field build_field(const std::vector<std::size_t>& shape, double h,
                  double (*fn)(double, double, double)) {
    Field f{shape, std::vector<double>(0)};
    std::size_t seats = 1;
    for (std::size_t len : shape) {
        seats *= len;
    }
    f.data.assign(seats, 0.0);
    const std::vector<std::size_t> strides =
        resonantia::nabla::strides_of(shape);
    for (std::size_t flat = 0; flat < seats; ++flat) {
        double coord[3] = {0.0, 0.0, 0.0};
        for (std::size_t axis = 0; axis < shape.size(); ++axis) {
            const std::size_t i = (flat / strides[axis]) % shape[axis];
            coord[axis] = static_cast<double>(i) * h;
        }
        f.data[flat] = fn(coord[0], coord[1], coord[2]);
    }
    return f;
}

double worst_error(const Field& computed,
                   double (*analytic)(double, double, double), double h) {
    double worst = 0.0;
    const std::vector<std::size_t> strides =
        resonantia::nabla::strides_of(computed.shape);
    for (std::size_t flat = 0; flat < computed.size(); ++flat) {
        double coord[3] = {0.0, 0.0, 0.0};
        for (std::size_t axis = 0; axis < computed.ndim(); ++axis) {
            const std::size_t i = (flat / strides[axis]) % computed.shape[axis];
            coord[axis] = static_cast<double>(i) * h;
        }
        const double err = std::fabs(computed.data[flat]
                                      - analytic(coord[0], coord[1], coord[2]));
        if (err > worst) {
            worst = err;
        }
    }
    return worst;
}

double worst_abs(const Field& f) {
    double worst = 0.0;
    for (double v : f.data) {
        if (std::fabs(v) > worst) {
            worst = std::fabs(v);
        }
    }
    return worst;
}

// The built-in fields, named at their seats so the lambdas of
// the harness become plain functions the bridge can pass.
double f_x2y(double x, double y, double) { return x * x * y; }
double a_2xy(double x, double y, double) { return 2.0 * x * y; }
double a_x2(double x, double, double) { return x * x; }
double f_x(double x, double, double) { return x; }
double f_y(double, double y, double) { return y; }
double f_z(double, double, double z) { return z; }
double a_3(double, double, double) { return 3.0; }
double f_rot_x(double, double y, double) { return -1.7 * y; }
double f_rot_y(double x, double, double) { return 1.7 * x; }
double f_zero(double, double, double) { return 0.0; }
double a_2w(double, double, double) { return 3.4; }
double f_mix(double x, double y, double z) {
    return x * x * x * y + y * z * z + z * x * x;
}
double f_quad(double x, double y, double z) {
    return x * x + y * y + z * z;
}
double a_6(double, double, double) { return 6.0; }
double f_harm(double x, double y, double) { return x * x - y * y; }

// MECHANISM: the interior peak of an evaluated signal — seats
// whose source time stands clear of the first and last seam
// spans, so the figure is the waveform itself, not the seam.
double interior_peak(const std::vector<double>& y, long up, long down,
                     long seam, std::size_t source_count) {
    double peak = 0.0;
    for (std::size_t m = 0; m < y.size(); ++m) {
        const double t = static_cast<double>(m)
                         * static_cast<double>(down)
                         / static_cast<double>(up);
        if (t >= static_cast<double>(seam)
            && t <= static_cast<double>(source_count - 1)
                        - static_cast<double>(seam)) {
            const double a = std::fabs(y[m]);
            if (a > peak) {
                peak = a;
            }
        }
    }
    return peak;
}

std::string nabla_checks() {
    using namespace resonantia::nabla;
    const std::size_t n = 33;
    const double h = 2.0 / static_cast<double>(n - 1);
    double worst = 0.0;
    std::string out =
        "NABLA — the Del operator, computed on this device.\n"
        "C++ seat of resonance/studio/nabla.py (commit a41ee87);\n"
        "the studio Python seat remains the reference. Built-in\n"
        "fields on a 33x33x33 grid over [0,2]^3, judged against\n"
        "their closed forms:\n\n";

    const Field f = build_field({n, n, n}, h, f_x2y);
    const std::vector<Field> g = gradient(f, h);
    const double e_gx = worst_error(g[0], a_2xy, h);
    const double e_gy = worst_error(g[1], a_x2, h);
    const double e_gz = worst_abs(g[2]);
    worst = std::max(worst, std::max(e_gx, std::max(e_gy, e_gz)));
    out += "grad(x^2 y) = (2xy, x^2, 0): worst errors "
           + sci(e_gx) + ", " + sci(e_gy) + ", " + sci(e_gz) + "\n";

    const std::vector<Field> identity{
        build_field({n, n, n}, h, f_x), build_field({n, n, n}, h, f_y),
        build_field({n, n, n}, h, f_z)};
    const double e_div = worst_error(divergence(identity, h), a_3, h);
    worst = std::max(worst, e_div);
    out += "div(x, y, z) = 3: worst error " + sci(e_div) + "\n";

    const std::vector<Field> rotation{
        build_field({n, n, n}, h, f_rot_x),
        build_field({n, n, n}, h, f_rot_y),
        build_field({n, n, n}, h, f_zero)};
    const double e_rdiv = worst_abs(divergence(rotation, h));
    const std::vector<Field> rc = curl(rotation, h);
    const double e_rcurl = std::max(
        worst_abs(rc[0]),
        std::max(worst_abs(rc[1]), worst_error(rc[2], a_2w, h)));
    worst = std::max(worst, std::max(e_rdiv, e_rcurl));
    out += "rigid rotation w=1.7: div worst " + sci(e_rdiv)
           + ", curl vs (0, 0, 3.4) worst " + sci(e_rcurl) + "\n";

    const Field fm = build_field({n, n, n}, h, f_mix);
    const std::vector<Field> cg = curl(gradient(fm, h), h);
    double e_cg = 0.0;
    for (const Field& comp : cg) {
        e_cg = std::max(e_cg, worst_abs(comp));
    }
    worst = std::max(worst, e_cg);
    out += "curl(grad(f)) = 0: worst |component| " + sci(e_cg) + "\n";

    const double e_l6 = worst_error(
        laplacian(build_field({n, n, n}, h, f_quad), h), a_6, h);
    const double e_l0 = worst_abs(
        laplacian(build_field({n, n, n}, h, f_harm), h));
    worst = std::max(worst, std::max(e_l6, e_l0));
    out += "Laplacian(x^2+y^2+z^2) = 6: worst error " + sci(e_l6) + "\n";
    out += "Laplacian(x^2-y^2) = 0: worst |value| " + sci(e_l0) + "\n";

    out += "\nWorst error over all checks: " + sci(worst)
           + (worst < 1e-9
                  ? " — within the sworn 1e-9.\n"
                  : " — ABOVE the sworn 1e-9; the bench is told.\n");
    return out;
}

std::string upscale_demo() {
    using namespace resonantia::upscale;
    const int sr = 44100;
    const int tr = 96000;
    const double pi = 3.14159265358979323846;
    std::string out =
        "UPSCALE — evaluation upward, computed on this device.\n"
        "C++ seat of resonance/studio/upscale.py (commit 97a63b9);\n"
        "the studio Python seat remains the reference. Loudness\n"
        "stays a studio measurement — no LUFS line stands here.\n\n";

    std::vector<double> tone(static_cast<std::size_t>(sr));
    for (int i = 0; i < sr; ++i) {
        tone[static_cast<std::size_t>(i)] =
            std::sin(2.0 * pi * 1000.0 * i / sr);
    }
    UpscaleReport rep;
    const std::vector<double> y = resample_up(tone, sr, tr, &rep);
    const double dom = dominant_frequency_hz(y, tr);
    const double tone_interior =
        interior_peak(y, rep.ratio_up, rep.ratio_down,
                      rep.seam_span_source_samples, tone.size());
    out += "1 kHz tone, 44100 -> 96000 at the exact ratio "
           + std::to_string(rep.ratio_up) + "/"
           + std::to_string(rep.ratio_down) + ": "
           + std::to_string(rep.samples_before) + " -> "
           + std::to_string(rep.samples_after) + " samples\n";
    out += "dominant frequency after: " + fixed2(dom) + " Hz\n";
    out += "sample peak " + fixed2(rep.sample_peak_before_db) + " -> "
           + fixed2(rep.sample_peak_after_db) + " dB; true peak "
           + fixed2(rep.true_peak_before_dbtp) + " -> "
           + fixed2(rep.true_peak_after_dbtp) + " dBTP\n";
    out += "interior peak " + sci(tone_interior)
           + " (the crest 1.0, within the kernel's ripple)\n";
    out += "floor above 22050 Hz: "
           + fixed2(rep.image_floor_measured_db) + " dB"
           + (rep.image_floor_measured_db <= IMAGE_FLOOR_DB
                  ? " — under the sworn -90 dB floor; nothing\n"
                    "synthesized above the source Nyquist.\n"
                  : " — ABOVE the sworn -90 dB floor; the bench\n"
                    "is told.\n");

    std::vector<double> crest(8192);
    for (std::size_t i = 0; i < crest.size(); ++i) {
        crest[i] = std::sin(2.0 * pi * (sr / 4.0)
                                * static_cast<double>(i) / sr
                            + pi / 4.0);
    }
    UpscaleReport crep;
    const std::vector<double> cy = resample_up(crest, sr, tr, &crep);
    const double crest_interior =
        interior_peak(cy, crep.ratio_up, crep.ratio_down,
                      crep.seam_span_source_samples, crest.size());
    out += "\nThe hidden crest — a tone at sr/4 phased pi/4, its\n"
           "samples reading only +/-0.7071:\n";
    out += "sample peak before " + fixed2(crep.sample_peak_before_db)
           + " dB; true peak before "
           + fixed2(crep.true_peak_before_dbtp) + " dBTP\n";
    out += "interior peak after " + sci(crest_interior)
           + " — the crest was always there, between the\n"
             "samples; this seat evaluates it, it does not\n"
             "invent it.\n";
    return out;
}

}  // namespace

extern "C" JNIEXPORT jstring JNICALL
Java_com_qasparr_resonantia_EqMainActivity_runNablaChecks(
        JNIEnv* env, jobject /* thiz */) {
    std::string out;
    try {
        out = nabla_checks();
    } catch (const std::exception& e) {
        // DOCTRINE: a thrown error is reported on the screen,
        // never swallowed — the same law as the suite's bridge.
        out = std::string("Nabla checks failed: ") + e.what() + "\n";
    } catch (...) {
        out = "Nabla checks failed: unknown native exception\n";
    }
    return env->NewStringUTF(out.c_str());
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_qasparr_resonantia_EqMainActivity_runUpscaleDemo(
        JNIEnv* env, jobject /* thiz */) {
    std::string out;
    try {
        out = upscale_demo();
    } catch (const std::exception& e) {
        out = std::string("Upscale demo failed: ") + e.what() + "\n";
    } catch (...) {
        out = "Upscale demo failed: unknown native exception\n";
    }
    return env->NewStringUTF(out.c_str());
}
