// =============================================================================
// RESONANTIA — android/eqapp/host/toolkit_host_test.cpp — the host
// proof of the C++ toolkit ports (nabla.hpp, upscale.hpp): the
// analytic battery, run on the bench with the host compiler BEFORE
// any APK strike, so the numbers the app later prints on the
// device were first sworn to where they could be checked.
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
//   Hypothesis: that the C++ ports seated beside the app's JNI
//     bridge meet the same analytic law as the Python studio seats
//     they port (nabla at a41ee87, upscale at 97a63b9) — the same
//     closed-form fields, the same sworn floor — when compiled
//     plain and run here.
//   Method: this file #includes the two port headers exactly as
//     the JNI bridge includes them (no test doubles, no second
//     implementation) and runs the Python seats' own cases:
//     nabla — grad(x^2 y) = (2xy, x^2) in 2-D and 3-D, div(x,y,z)
//     = 3, the rigid rotation divergence-free with curl the
//     constant (0, 0, 2w), curl of the port's own gradient zero,
//     Laplacian(x^2+y^2+z^2) = 6, Laplacian(x^2-y^2) = 0, and the
//     refusals by name; upscale — a 1 kHz tone at 44.1k evaluated
//     to 96k (frequency, counts, the measured floor above the
//     source Nyquist against the sworn -90 dB), the awkward
//     count 44101 -> 96003, the sr/4 phase-pi/4 hidden crest
//     (samples at +/-0.7071, the interior evaluated peak at the
//     analytic 1.0 and never above it), and the refusals by name.
//     Every check prints its MEASURED figure; a check that fails
//     fails the process (exit 1), and the build record quotes
//     this program's output, not a paraphrase of it.
//   Observation: (printed by the run; quoted in
//     android/APK-BUILD.md.)
//   Result: exit 0 with every check passing, or the exact
//     coordinate of the failure.
//
// BUILD AND RUN (from the repo root; the includes are relative,
// so the seat of the command does not matter):
//   g++ -std=c++17 -O2 android/eqapp/host/toolkit_host_test.cpp \
//       -o /tmp/toolkit_host_test && /tmp/toolkit_host_test
//
// DOCTRINE: this harness is a bench instrument. It is not part
// of the APK, it is not part of the Python suite (whose count
// stands untouched at 394), and its passing proves the PORTS —
// the on-device tap remains the founder's, as the record says.
//
// All Rights Reserved, Without Prejudice.
// "Live, Love, and let Love, Live."
// =============================================================================

#include <cmath>
#include <cstdio>
#include <functional>
#include <string>
#include <vector>

#include "../src/main/jni/nabla.hpp"
#include "../src/main/jni/upscale.hpp"

namespace {

int g_checks = 0;
int g_failures = 0;

// MECHANISM: one sworn line per case — the measured figure is
// printed whether the check passes or fails, so the record can
// quote the number and not the verdict alone.
void check(bool ok, const std::string& label, double measured) {
    ++g_checks;
    if (!ok) {
        ++g_failures;
    }
    std::printf("[%s] %-58s measured %.17g\n", ok ? "PASS" : "FAIL",
                label.c_str(), measured);
}

void check_bool(bool ok, const std::string& label) {
    ++g_checks;
    if (!ok) {
        ++g_failures;
    }
    std::printf("[%s] %s\n", ok ? "PASS" : "FAIL", label.c_str());
}

using resonantia::nabla::Field;

// MECHANISM: build a field on a grid from a function of the
// seat's coordinates — the harness's meshgrid, in array-axis
// order (axis 0 is x, axis 1 is y, axis 2 is z).
Field build_field(const std::vector<std::size_t>& shape, double h,
                  const std::function<double(double, double, double)>& fn) {
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

// MECHANISM: the worst absolute difference between a computed
// field and the analytic field it answers to, seat by seat.
double worst_error(const Field& computed,
                   const std::function<double(double, double, double)>& analytic,
                   double h) {
    double worst = 0.0;
    const std::vector<std::size_t> strides =
        resonantia::nabla::strides_of(computed.shape);
    for (std::size_t flat = 0; flat < computed.size(); ++flat) {
        double coord[3] = {0.0, 0.0, 0.0};
        for (std::size_t axis = 0; axis < computed.ndim(); ++axis) {
            const std::size_t i = (flat / strides[axis]) % computed.shape[axis];
            coord[axis] = static_cast<double>(i) * h;
        }
        const double err =
            std::fabs(computed.data[flat] - analytic(coord[0], coord[1], coord[2]));
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

void nabla_battery() {
    using namespace resonantia::nabla;
    std::printf("== NABLA — the Del operator, C++ port ==\n");
    const std::size_t n = 33;
    const double h = 2.0 / static_cast<double>(n - 1);  // grid [0,2]^d

    // grad(x^2 y) = (2xy, x^2) in 3-D (z seats carried, derivative 0).
    const Field f3 = build_field({n, n, n}, h,
        [](double x, double y, double) { return x * x * y; });
    const std::vector<Field> g3 = gradient(f3, h);
    check(worst_error(g3[0], [](double x, double y, double) {
              return 2.0 * x * y;
          }, h) < 1e-9,
          "nabla 3-D: grad(x^2 y).x vs 2xy, worst error",
          worst_error(g3[0], [](double x, double y, double) {
              return 2.0 * x * y;
          }, h));
    check(worst_error(g3[1], [](double x, double, double) {
              return x * x;
          }, h) < 1e-9,
          "nabla 3-D: grad(x^2 y).y vs x^2, worst error",
          worst_error(g3[1], [](double x, double, double) {
              return x * x;
          }, h));
    check(worst_abs(g3[2]) < 1e-9,
          "nabla 3-D: grad(x^2 y).z vs 0, worst |value|", worst_abs(g3[2]));

    // Per-axis spacing seats the same answer as uniform spacing.
    const std::vector<Field> g3b = gradient(f3, std::vector<double>{h, h, h});
    double same = 0.0;
    for (std::size_t s = 0; s < g3[0].size(); ++s) {
        same = std::max(same, std::fabs(g3b[0].data[s] - g3[0].data[s]));
    }
    check(same == 0.0, "nabla: per-axis spacing == uniform, worst diff", same);

    // grad(x^2 y) in 2-D, the seat the Python battery also swears.
    const Field f2 = build_field({n, n}, h,
        [](double x, double y, double) { return x * x * y; });
    const std::vector<Field> g2 = gradient(f2, h);
    check(worst_error(g2[0], [](double x, double y, double) {
              return 2.0 * x * y;
          }, h) < 1e-9,
          "nabla 2-D: grad(x^2 y).x vs 2xy, worst error",
          worst_error(g2[0], [](double x, double y, double) {
              return 2.0 * x * y;
          }, h));
    check(worst_error(g2[1], [](double x, double, double) {
              return x * x;
          }, h) < 1e-9,
          "nabla 2-D: grad(x^2 y).y vs x^2, worst error",
          worst_error(g2[1], [](double x, double, double) {
              return x * x;
          }, h));

    // div(x, y, z) = 3 everywhere.
    const std::vector<Field> identity{
        build_field({n, n, n}, h, [](double x, double, double) { return x; }),
        build_field({n, n, n}, h, [](double, double y, double) { return y; }),
        build_field({n, n, n}, h, [](double, double, double z) { return z; })};
    const Field div_id = divergence(identity, h);
    check(worst_error(div_id, [](double, double, double) { return 3.0; }, h)
              < 1e-9,
          "nabla: div(x, y, z) vs 3, worst error",
          worst_error(div_id, [](double, double, double) { return 3.0; }, h));

    // The rigid rotation w(-y, x, 0), w = 1.7: divergence-free,
    // curl the constant (0, 0, 2w).
    const double w = 1.7;
    const std::vector<Field> rotation{
        build_field({n, n, n}, h,
                    [w](double, double y, double) { return -w * y; }),
        build_field({n, n, n}, h,
                    [w](double x, double, double) { return w * x; }),
        build_field({n, n, n}, h,
                    [](double, double, double) { return 0.0; })};
    const Field div_rot = divergence(rotation, h);
    check(worst_abs(div_rot) < 1e-9,
          "nabla: div(rigid rotation) vs 0, worst |value|", worst_abs(div_rot));
    const std::vector<Field> curl_rot = curl(rotation, h);
    check(worst_abs(curl_rot[0]) < 1e-9 && worst_abs(curl_rot[1]) < 1e-9,
          "nabla: curl(rotation).x/.y vs 0, worst |value|",
          std::max(worst_abs(curl_rot[0]), worst_abs(curl_rot[1])));
    check(worst_error(curl_rot[2], [w](double, double, double) {
              return 2.0 * w;
          }, h) < 1e-9,
          "nabla: curl(rotation).z vs 2w, worst error",
          worst_error(curl_rot[2], [w](double, double, double) {
              return 2.0 * w;
          }, h));

    // curl of the port's own gradient: identically zero, because
    // the axis operators commute — the discrete identity, not a
    // truncation accident.
    const Field f_mix = build_field({n, n, n}, h,
        [](double x, double y, double z) {
            return x * x * x * y + y * z * z + z * x * x;
        });
    const std::vector<Field> curl_grad = curl(gradient(f_mix, h), h);
    double cg = 0.0;
    for (const Field& comp : curl_grad) {
        cg = std::max(cg, worst_abs(comp));
    }
    check(cg < 1e-9, "nabla: curl(grad(f)) vs 0, worst |component|", cg);

    // Laplacian(x^2+y^2+z^2) = 6; Laplacian(x^2-y^2) = 0.
    const Field f_quad = build_field({n, n, n}, h,
        [](double x, double y, double z) {
            return x * x + y * y + z * z;
        });
    const Field lap6 = laplacian(f_quad, h);
    check(worst_error(lap6, [](double, double, double) { return 6.0; }, h)
              < 1e-9,
          "nabla: Laplacian(x^2+y^2+z^2) vs 6, worst error",
          worst_error(lap6, [](double, double, double) { return 6.0; }, h));
    const Field f_harm = build_field({n, n, n}, h,
        [](double x, double y, double) { return x * x - y * y; });
    const Field lap0 = laplacian(f_harm, h);
    check(worst_abs(lap0) < 1e-9,
          "nabla: Laplacian(x^2-y^2) vs 0, worst |value|", worst_abs(lap0));

    // Refusals by name.
    bool refused = false;
    try {
        const std::vector<Field> two_d{identity[0], identity[1]};
        // A 2-component field over a 3-D grid is itself refused;
        // seat a true 2-D field to reach the curl refusal.
        const std::vector<Field> flat{
            build_field({n, n}, h, [](double x, double, double) { return x; }),
            build_field({n, n}, h, [](double, double y, double) { return y; })};
        (void)two_d;
        (void)curl(flat, h);
    } catch (const NablaError&) {
        refused = true;
    }
    check_bool(refused, "nabla: curl of a 2-D field refused as NablaError");

    refused = false;
    try {
        (void)gradient(f3, std::vector<double>{h, h});
    } catch (const NablaError&) {
        refused = true;
    }
    check_bool(refused, "nabla: wrong-count spacing refused as NablaError");

    refused = false;
    try {
        (void)gradient(f3, 0.0);
    } catch (const NablaError&) {
        refused = true;
    }
    check_bool(refused, "nabla: zero spacing refused as NablaError");

    refused = false;
    try {
        const Field four_d{{3, 3, 3, 3}, std::vector<double>(81, 1.0)};
        (void)gradient(four_d, h);
    } catch (const NablaError&) {
        refused = true;
    }
    check_bool(refused, "nabla: 4-D field refused as NablaError");

    refused = false;
    try {
        const Field short_axis{{2, 5, 5}, std::vector<double>(50, 1.0)};
        (void)gradient(short_axis, h);
    } catch (const NablaError&) {
        refused = true;
    }
    check_bool(refused,
               "nabla: 2-seat axis refused as NablaError (edge scheme)");
}

void upscale_battery() {
    using namespace resonantia::upscale;
    std::printf("== UPSCALE — evaluation upward, C++ port ==\n");
    const int sr = 44100;
    const int tr = 96000;
    const double pi = 3.14159265358979323846;

    // The 1 kHz tone, one second of it, full scale.
    std::vector<double> tone(sr);
    for (int i = 0; i < sr; ++i) {
        tone[i] = std::sin(2.0 * pi * 1000.0 * i / sr);
    }
    UpscaleReport rep;
    const std::vector<double> up = resample_up(tone, sr, tr, &rep);
    check_bool(rep.ratio_up == 320 && rep.ratio_down == 147,
               "upscale: 44100->96000 ratio is exactly 320/147");
    check(rep.samples_after == 96000 ? 1.0 : 0.0,
          "upscale: 44100 samples -> count out", (double)rep.samples_after);
    const double dom = dominant_frequency_hz(up, tr);
    check(std::fabs(dom - 1000.0) < 2.0,
          "upscale: dominant frequency of the evaluated tone (Hz)", dom);
    double rms_in = 0.0, rms_out = 0.0;
    for (double v : tone) {
        rms_in += v * v;
    }
    for (double v : up) {
        rms_out += v * v;
    }
    rms_in = std::sqrt(rms_in / tone.size());
    rms_out = std::sqrt(rms_out / up.size());
    check(std::fabs(rms_out - rms_in) < 0.002,
          "upscale: RMS out vs RMS in, |difference|",
          std::fabs(rms_out - rms_in));
    // Interior peak: seats whose source time stands clear of the
    // seams (the first and last seam spans) — the waveform
    // itself, evaluated. It must reach the crest, and it may
    // stand above it only by the kernel's own ripple: the
    // finite span rings at the 1e-6 scale (measured on this
    // bench at 1.04e-6), so the sworn bound is 1e-5 with the
    // measured figure printed — a bound stated, not loosened
    // in silence.
    double interior_peak = 0.0;
    for (std::size_t m = 0; m < up.size(); ++m) {
        const double t = static_cast<double>(m) * rep.ratio_down
                         / rep.ratio_up;
        if (t >= (double)rep.seam_span_source_samples
            && t <= (double)(sr - 1) - (double)rep.seam_span_source_samples) {
            interior_peak = std::max(interior_peak, std::fabs(up[m]));
        }
    }
    check(interior_peak >= 0.999 && interior_peak <= 1.00001,
          "upscale: tone interior peak (crest 1.0, ripple <= 1e-5)",
          interior_peak);
    // THE HONESTY PROOF: the floor above the source Nyquist,
    // measured on this port's own taps, against the sworn -90 dB.
    check(rep.image_floor_measured_db <= IMAGE_FLOOR_DB,
          "upscale: floor above 22050 Hz (dB, sworn <= -90)",
          rep.image_floor_measured_db);
    std::printf("       report: peaks sample %.2f -> %.2f dB, true "
                "%.2f -> %.2f dBTP, seam span %ld source samples, "
                "duration %.6f -> %.6f s\n",
                rep.sample_peak_before_db, rep.sample_peak_after_db,
                rep.true_peak_before_dbtp, rep.true_peak_after_dbtp,
                rep.seam_span_source_samples, rep.duration_before_s,
                rep.duration_after_s);

    // The awkward count, as the studio seat swears it.
    std::vector<double> awkward(44101, 0.0);
    for (std::size_t i = 0; i < awkward.size(); ++i) {
        awkward[i] = std::sin(2.0 * pi * 440.0 * (double)i / sr);
    }
    const std::vector<double> awkward_up = resample_up(awkward, sr, tr);
    check(awkward_up.size() == 96003 ? 1.0 : 0.0,
          "upscale: 44101 samples -> count out (sworn 96003)",
          (double)awkward_up.size());

    // The hidden crest: a tone at sr/4 phased pi/4 — its samples
    // read only +/-cos(pi/4) = +/-0.7071 (-3.01 dB) while the
    // waveform's crest stands at 1.0, between the samples.
    std::vector<double> crest(8192);
    for (std::size_t i = 0; i < crest.size(); ++i) {
        crest[i] = std::sin(2.0 * pi * (sr / 4.0) * (double)i / sr
                            + pi / 4.0);
    }
    UpscaleReport crep;
    const std::vector<double> crest_up = resample_up(crest, sr, tr, &crep);
    check(std::fabs(crep.sample_peak_before_db - (-3.01)) < 0.01,
          "upscale: crest case sample peak before (dB, sworn -3.01)",
          crep.sample_peak_before_db);
    double crest_interior = 0.0;
    for (std::size_t m = 0; m < crest_up.size(); ++m) {
        const double t = static_cast<double>(m) * crep.ratio_down
                         / crep.ratio_up;
        if (t >= (double)crep.seam_span_source_samples
            && t <= (double)(crest.size() - 1)
                        - (double)crep.seam_span_source_samples) {
            crest_interior = std::max(crest_interior, std::fabs(crest_up[m]));
        }
    }
    check(crest_interior >= 0.999 && crest_interior <= 1.000001,
          "upscale: crest interior peak (analytic 1.0, never above)",
          crest_interior);
    std::printf("       report: crest true peak before %.2f dBTP, "
                "after (whole file, seams in) %.2f dBTP\n",
                crep.true_peak_before_dbtp, crep.true_peak_after_dbtp);

    // Refusals by name.
    bool refused = false;
    try {
        (void)resample_up(tone, tr, sr);
    } catch (const UpscaleError&) {
        refused = true;
    }
    check_bool(refused, "upscale: downsampling refused as UpscaleError");

    refused = false;
    try {
        (void)resample_up(tone, sr, sr);
    } catch (const UpscaleError&) {
        refused = true;
    }
    check_bool(refused, "upscale: same-rate refused as UpscaleError");

    refused = false;
    try {
        (void)resample_up(std::vector<double>{}, sr, tr);
    } catch (const UpscaleError&) {
        refused = true;
    }
    check_bool(refused, "upscale: empty input refused as UpscaleError");

    refused = false;
    try {
        std::vector<double> bad = tone;
        bad[100] = std::nan("");
        (void)resample_up(bad, sr, tr);
    } catch (const UpscaleError&) {
        refused = true;
    }
    check_bool(refused, "upscale: NaN sample refused as UpscaleError");

    refused = false;
    try {
        (void)resample_up(tone, 0, tr);
    } catch (const UpscaleError&) {
        refused = true;
    }
    check_bool(refused, "upscale: zero rate refused as UpscaleError");
}

}  // namespace

int main() {
    nabla_battery();
    upscale_battery();
    std::printf("TOOLKIT HOST PROOF: %d checks, %d failure(s)\n",
                g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}
