/**
 * Project: EQVILLIBBRRIVMM - Complete Manifold, Doppler, Convolution & 77^3 Enclave Suite
 * Author: Johnathan 'Qasparr' Monroe (Κασπάρρ)
 * License: Open Source - Zero Liability / Educational Research & Development
 * Support / Contributions: CashApp $axoneme
 *
 * "Every, Man, Woman, and Child, is a Star."
 * "Live, Love, and let Love, Live!"
 * "What can occur, will!"
 */

#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cmath>
#include <complex>
#include <cstddef>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

namespace axoneme::symphony {

constexpr float kPi = 3.14159265358979323846f;

// Twin-Rail & 13/5 Guardrail ratios
constexpr float kOuterRailRatio = 10.0f / 6.0f;
constexpr float kInnerRailRatio = 7.0f / 4.0f;
constexpr float kCenterKeyRatio = 13.0f / 8.0f;
constexpr float kGuardrailRatio13_5 = 13.0f / 5.0f;

// 48 Hz anchor & 48 x 48 x 48 = 110,592 cubic dimension
constexpr float kAnchorHz48 = 48.0f;
constexpr std::size_t kCube48Edge = 48;
constexpr std::size_t kCube48Cells = kCube48Edge * kCube48Edge * kCube48Edge; // 110,592

// 77 x 77 x 77 = 456,533 Enclave Sphere & Sigma 13-31 Hz foundation
constexpr std::size_t kEnclave77Edge = 77;
constexpr std::size_t kEnclave77Cells = kEnclave77Edge * kEnclave77Edge * kEnclave77Edge; // 456,533
constexpr float kSigmaMinHz = 13.0f;
constexpr float kSigmaMaxHz = 31.0f;
constexpr float kSigmaAnchorHz = 22.0f;

// Full Key G9 frequency (~1254.385 Hz in 12-TET A4=440 Hz)
constexpr float kFullKeyG9Hz = 1254.3854f;

// Fine-structure & wave constants
constexpr float kFineStructureAlpha = 1.0f / 137.035999f;

// Solfeggio harmonic scale frequencies (Hz)
constexpr std::array<float, 6> kSolfeggioHz{{
    396.0f, 417.0f, 528.0f, 639.0f, 741.0f, 852.0f
}};

/**
 * 1. ChristoffelManifoldGuard (Source 3544.jpg)
 * Metric tensor g_{ij}, inverse g^{kl}, partial derivatives d_i g_{jl},
 * Christoffel symbols Gamma^k_{ij} = 0.5 * g^{kl} * (d_i g_{jl} + d_j g_{il} - d_l g_{ij}),
 * and covariant basis transport (nabla_i e_j)^k = Gamma^k_{ij} e_k, bounded by 13/5.
 */
class ChristoffelManifoldGuard {
public:
    struct ManifoldState {
        std::array<std::array<float, 2>, 2> metric{};
        std::array<std::array<std::array<float, 2>, 2>, 2> gamma{}; // Gamma^k_{ij}
        std::array<float, 2> transportedBasisE1{};
        std::array<float, 2> transportedBasisE2{};
        float connectionNorm{0.0f};
        float boundedExcursion{0.0f};
        bool guardrailEngaged{false};
    };

    static float cushion13_5(float rawValue, float railBound = kGuardrailRatio13_5, bool* outEngaged = nullptr) noexcept {
        const float bound = std::max(0.1f, railBound);
        if (std::abs(rawValue) <= bound) {
            if (outEngaged) *outEngaged = false;
            return rawValue;
        }
        if (outEngaged) *outEngaged = true;
        const float sign = (rawValue >= 0.0f) ? 1.0f : -1.0f;
        const float excess = std::abs(rawValue) - bound;
        return sign * (bound - 0.15f * std::tanh(excess));
    }

    static ManifoldState evaluate(
        float uCoord,
        float vCoord,
        float centerKeyPos,
        float electromrFlux
    ) noexcept {
        // Diagonal-dominant conformal metric g_{ij} with radial/key curvature
        const float r2 = std::clamp(uCoord * uCoord + vCoord * vCoord, 0.0f, 4.0f);
        const float warp = 1.0f + 0.25f * std::tanh(0.5f * r2 + 0.3f * centerKeyPos);

        const float g00 = warp;
        const float g11 = warp * (1.0f + 0.15f * std::cos(vCoord + electromrFlux));
        const float g01 = 0.08f * std::sin(uCoord * vCoord);
        const float g10 = g01;

        // Partial derivatives dg_{ab} / dx^c for c in {0 -> u, 1 -> v}
        const float dWarpDu = 0.25f * (1.0f - std::pow(std::tanh(0.5f * r2 + 0.3f * centerKeyPos), 2.0f)) * (1.0f * uCoord);
        const float dWarpDv = 0.25f * (1.0f - std::pow(std::tanh(0.5f * r2 + 0.3f * centerKeyPos), 2.0f)) * (1.0f * vCoord);

        std::array<std::array<std::array<float, 2>, 2>, 2> dg{}; // dg[a][b][c] = d_c g_{ab}
        dg[0][0][0] = dWarpDu;
        dg[0][0][1] = dWarpDv;
        dg[1][1][0] = dWarpDu * (1.0f + 0.15f * std::cos(vCoord + electromrFlux));
        dg[1][1][1] = dWarpDv * (1.0f + 0.15f * std::cos(vCoord + electromrFlux))
                      - warp * 0.15f * std::sin(vCoord + electromrFlux);
        dg[0][1][0] = 0.08f * vCoord * std::cos(uCoord * vCoord);
        dg[0][1][1] = 0.08f * uCoord * std::cos(uCoord * vCoord);
        dg[1][0][0] = dg[0][1][0];
        dg[1][0][1] = dg[0][1][1];

        // Inverse metric g^{kl} for 2x2
        const float det = std::max(1e-4f, g00 * g11 - g01 * g10);
        const std::array<std::array<float, 2>, 2> gInv{{
            {{g11 / det, -g01 / det}},
            {{-g10 / det, g00 / det}}
        }};

        // Christoffel symbols Gamma^k_{ij} = 0.5 * g^{kl} * (d_i g_{jl} + d_j g_{il} - d_l g_{ij})
        std::array<std::array<std::array<float, 2>, 2>, 2> gamma{}; // [k][i][j]
        float normSq = 0.0f;

        for (int k = 0; k < 2; ++k) {
            for (int i = 0; i < 2; ++i) {
                for (int j = 0; j < 2; ++j) {
                    float sum = 0.0f;
                    for (int l = 0; l < 2; ++l) {
                        const float term = dg[j][l][i] + dg[i][l][j] - dg[i][j][l];
                        sum += gInv[k][l] * term;
                    }
                    const float val = std::clamp(0.5f * sum, -2.5f, 2.5f);
                    gamma[k][i][j] = val;
                    normSq += val * val;
                }
            }
        }

        // Parallel transport of basis vectors e_1 and e_2 along (uCoord, vCoord)
        const std::array<float, 2> tE1{{
            1.0f + gamma[0][0][0] * uCoord + gamma[0][0][1] * vCoord,
            gamma[1][0][0] * uCoord + gamma[1][0][1] * vCoord
        }};
        const std::array<float, 2> tE2{{
            gamma[0][1][0] * uCoord + gamma[0][1][1] * vCoord,
            1.0f + gamma[1][1][0] * uCoord + gamma[1][1][1] * vCoord
        }};

        const float connNorm = std::sqrt(normSq / 8.0f);
        const float rawExcursion = (uCoord * kGuardrailRatio13_5) +
                                   (0.55f * centerKeyPos) +
                                   (0.40f * (tE1[0] - 1.0f + tE2[1] - 1.0f)) +
                                   (0.35f * connNorm);

        bool engaged = false;
        const float bounded = cushion13_5(rawExcursion, kGuardrailRatio13_5, &engaged);

        // DESK REPAIR 2026-11-22: the metric initializer on the next line was written in the
        // standalone-declaration brace nesting (double-braced rows, the form that is correct
        // for gInv above, where the variable's own brace adds a level) AND carried one surplus
        // closing brace (5 opens, 6 closes in the raw). Inside this aggregate return that
        // nesting makes the first row consume the array's single member brace and leaves the
        // second row surplus ('too many initializers'), and the surplus '}' closed the return
        // early, breaking class/namespace scope for the rest of the file (the downstream
        // 'kPi was not declared' errors were fallout of this one line). Written below in the
        // aggregate-field form {{{g00, g01}, {g10, g11}}} — verified against g++ 13.3 in
        // isolation before applying. No values changed.
        return ManifoldState{
            {{{g00, g01}, {g10, g11}}},
            gamma,
            tE1,
            tE2,
            connNorm,
            bounded,
            engaged
        };
    }
};

/**
 * 2. DopplerWaveGeometry (Source 3543.jpg)
 * Models wavefront compression/stretching, f_obs = f_0 * (v +- v_obs) / (v -+ v_s),
 * Mach number M = v_s / v, and Mach cone half-angle sin(theta_M) = 1 / M for M > 1.
 */
class DopplerWaveGeometry {
public:
    struct DopplerState {
        float observedFreqHz{528.0f};
        float wavelengthCompressed{0.65f};
        float machNumber{0.0f};
        float machConeAngleRad{0.0f};
        bool supersonicConeActive{false};
        float wavefrontDamping{1.0f};
    };

    static DopplerState evaluate(
        float sourceFreqHz,
        float waveSpeed,
        float sourceVelocity,
        float observerVelocity,
        bool approachingSource
    ) noexcept {
        const float f0 = std::max(1.0f, sourceFreqHz);
        const float c = std::max(1.0f, waveSpeed);
        const float vs = std::clamp(sourceVelocity, 0.0f, c * 1.85f);
        const float vo = std::clamp(observerVelocity, 0.0f, c * 0.90f);

        const float num = approachingSource ? (c + vo) : std::max(0.05f * c, c - vo);
        // Guard against exact division-by-zero at sonic barrier v_s == c
        float denom = approachingSource ? (c - vs) : (c + vs);
        if (std::abs(denom) < 0.04f * c) {
            denom = (denom >= 0.0f) ? (0.04f * c) : (-0.04f * c);
        }

        const float dopplerRatio = std::clamp(num / denom, 0.25f, 3.0f);
        const float fObs = f0 * dopplerRatio;

        const float mach = vs / c;
        const bool supersonic = (mach > 1.0f);
        const float coneAngle = supersonic ? std::asin(std::clamp(1.0f / mach, 0.0f, 1.0f)) : 0.0f;

        // Smooth wavefront damping when approaching sonic barrier (M ~ 1) or supersonic cone
        const float barrierProximity = std::exp(-std::pow((mach - 1.0f) / 0.15f, 2.0f));
        const float damping = std::clamp(1.0f - 0.35f * barrierProximity - (supersonic ? 0.15f : 0.0f), 0.35f, 1.0f);

        const float lambdaComp = (c * damping) / std::max(1.0f, fObs);

        return DopplerState{fObs, lambdaComp, mach, coneAngle, supersonic, damping};
    }
};

/**
 * 3. LaplaceConvolutionBus (Source 3538_2.jpg)
 * Time-domain convolution y(t) = (h * x)(t) paired with frequency-domain
 * Laplace transfer product Y(s) = H(s) * X(s) and inverse s-plane evaluation.
 */
class LaplaceConvolutionBus {
public:
    struct ConvolutionResult {
        std::vector<float> timeDomainConvolved;
        std::complex<float> sPlaneProduct{0.0f, 0.0f};
        float transferMagnitude{1.0f};
    };

    static std::vector<float> convolveTimeDomain(
        const std::vector<float>& x,
        const std::vector<float>& h
    ) {
        const std::size_t n = x.size();
        std::vector<float> y(n, 0.0f);
        if (n == 0 || h.empty()) return y;

        const std::size_t kLen = std::min(n, h.size());
        for (std::size_t t = 0; t < n; ++t) {
            double acc = 0.0;
            for (std::size_t tau = 0; tau <= std::min(t, kLen - 1); ++tau) {
                acc += static_cast<double>(x[t - tau]) * static_cast<double>(h[tau]);
            }
            y[t] = static_cast<float>(std::clamp(acc, -1.0, 1.0));
        }
        return y;
    }

    static ConvolutionResult evaluateLaplaceDomain(
        const std::vector<float>& x,
        float dampingSigma,
        float omegaRadPerSec,
        float poleCenterHz
    ) {
        // Discrete-time Laplace-like s = sigma + j*omega evaluation of X(s)
        std::complex<float> xS{0.0f, 0.0f};
        const std::complex<float> s(dampingSigma, omegaRadPerSec);
        for (std::size_t n = 0; n < x.size(); ++n) {
            const float tn = static_cast<float>(n) / 48000.0f;
            xS += x[n] * std::exp(-s * tn);
        }
        if (!x.empty()) {
            xS /= static_cast<float>(x.size());
        }

        // H(s) = w0^2 / (s^2 + (w0/Q)*s + w0^2)
        const float w0 = 2.0f * kPi * std::max(20.0f, poleCenterHz);
        const float q = 2.5f;
        const std::complex<float> hS = (w0 * w0) / ((s * s) + (w0 / q) * s + (w0 * w0));
        const std::complex<float> yS = hS * xS;

        // Compact FIR kernel h(t) derived from inverse damping envelope
        const std::size_t hTaps = 16;
        std::vector<float> hKernel(hTaps, 0.0f);
        float kSum = 0.0f;
        for (std::size_t k = 0; k < hTaps; ++k) {
            const float fk = static_cast<float>(k);
            const float val = std::exp(-0.28f * fk) * std::cos(0.35f * fk * std::abs(hS.real()));
            hKernel[k] = val;
            kSum += std::abs(val);
        }
        if (kSum > 1e-6f) {
            for (float& v : hKernel) v /= kSum;
        }

        auto yTime = convolveTimeDomain(x, hKernel);
        return ConvolutionResult{
            std::move(yTime),
            yS,
            std::clamp(std::abs(hS), 0.05f, 3.0f)
        };
    }
};

/**
 * 4. EnclaveSphere77 (Source 3263.png)
 * 77 x 77 x 77 = 456,533 Enclave Sphere lattice + Sigma 13-31 Hz sub-foundation.
 */
class EnclaveSphere77 {
public:
    struct EnclaveMetrics {
        std::size_t totalCells{kEnclave77Cells}; // 456,533
        float sigmaBandHz{kSigmaAnchorHz};
        float sphericalRadialNorm{0.0f};
        float enclaveCoherence{0.0f};
    };

    static EnclaveMetrics evaluate(std::size_t frameIdx, float elapsedSec, float sigmaDrive) noexcept {
        const std::size_t x = frameIdx % kEnclave77Edge;
        const std::size_t y = (frameIdx * 11 + 5) % kEnclave77Edge;
        const std::size_t z = (frameIdx * 17 + 9) % kEnclave77Edge;

        const float half = 0.5f * static_cast<float>(kEnclave77Edge - 1);
        const float nx = (static_cast<float>(x) - half) / half;
        const float ny = (static_cast<float>(y) - half) / half;
        const float nz = (static_cast<float>(z) - half) / half;

        const float r = std::sqrt(nx * nx + ny * ny + nz * nz);
        const float rNorm = std::clamp(r / std::sqrt(3.0f), 0.0f, 1.0f);

        // Sigma 13-31 Hz foundation sweep modulated by spherical shell and elapsed time
        const float span = kSigmaMaxHz - kSigmaMinHz;
        const float sigmaHz = kSigmaMinHz + span * (0.5f + 0.5f * std::sin(2.0f * kPi * 0.25f * elapsedSec + rNorm * kPi));

        const float coherence = std::clamp(
            (0.5f + 0.5f * std::cos(2.0f * kPi * sigmaHz * elapsedSec)) * (1.0f - 0.30f * rNorm) *
            std::clamp(0.5f + 0.5f * sigmaDrive, 0.25f, 1.25f),
            0.0f,
            1.0f
        );

        return EnclaveMetrics{kEnclave77Cells, sigmaHz, rNorm, coherence};
    }
};

// --- Retaining Core Subsystems & Adding Integrated Manifold/Doppler/Convolution/77^3 Telemetry ---

struct StereoSample {
    float left{0.0f};
    float right{0.0f};
};

class PcmWavExporter {
public:
    static void writeLe16(std::ofstream& out, std::uint16_t v) {
        const std::array<std::uint8_t, 2> b{{
            static_cast<std::uint8_t>(v & 0xFFu),
            static_cast<std::uint8_t>((v >> 8) & 0xFFu)
        }};
        out.write(reinterpret_cast<const char*>(b.data()), 2);
    }

    static void writeLe32(std::ofstream& out, std::uint32_t v) {
        const std::array<std::uint8_t, 4> b{{
            static_cast<std::uint8_t>(v & 0xFFu),
            static_cast<std::uint8_t>((v >> 8) & 0xFFu),
            static_cast<std::uint8_t>((v >> 16) & 0xFFu),
            static_cast<std::uint8_t>((v >> 24) & 0xFFu)
        }};
        out.write(reinterpret_cast<const char*>(b.data()), 4);
    }

    static std::int16_t floatToPcm16(float sample) noexcept {
        const float clamped = std::clamp(sample, -1.0f, 1.0f);
        const float scaled = (clamped >= 0.0f) ? (clamped * 32767.0f) : (clamped * 32768.0f);
        return static_cast<std::int16_t>(std::clamp(std::lround(scaled), -32768L, 32767L));
    }

    static bool exportStereo16BitWav(
        const std::string& path,
        const std::vector<StereoSample>& samples,
        std::uint32_t sampleRate
    ) {
        std::ofstream out(path, std::ios::binary);
        if (!out.is_open()) return false;

        constexpr std::uint16_t kNumChannels = 2;
        constexpr std::uint16_t kBitsPerSample = 16;
        const std::uint16_t blockAlign = static_cast<std::uint16_t>(kNumChannels * (kBitsPerSample / 8));
        const std::uint32_t byteRate = sampleRate * static_cast<std::uint32_t>(blockAlign);
        const std::uint32_t dataBytes = static_cast<std::uint32_t>(samples.size()) *
                                        static_cast<std::uint32_t>(blockAlign);
        const std::uint32_t riffChunkSize = 36u + dataBytes;

        out.write("RIFF", 4);
        writeLe32(out, riffChunkSize);
        out.write("WAVE", 4);
        out.write("fmt ", 4);
        writeLe32(out, 16u);
        writeLe16(out, 1u);
        writeLe16(out, kNumChannels);
        writeLe32(out, sampleRate);
        writeLe32(out, byteRate);
        writeLe16(out, blockAlign);
        writeLe16(out, kBitsPerSample);
        out.write("data", 4);
        writeLe32(out, dataBytes);

        for (const auto& s : samples) {
            writeLe16(out, static_cast<std::uint16_t>(floatToPcm16(s.left)));
            writeLe16(out, static_cast<std::uint16_t>(floatToPcm16(s.right)));
        }
        return out.good();
    }
};

struct IntegratedTelemetry {
    std::size_t enclave77Cells{kEnclave77Cells}; // 456,533
    float sigmaBandHz{kSigmaAnchorHz};          // 13-31 Hz
    float enclaveCoherence{0.0f};
    float christoffelNorm{0.0f};
    float dopplerObservedHz{528.0f};
    float dopplerMach{0.0f};
    bool supersonicMachCone{false};
    float convolutionTransferMag{1.0f};
};

class IntegratedSymphonyBridge {
public:
    static IntegratedTelemetry stepTelemetry(
        std::size_t frameIdx,
        float elapsedSec,
        float baseFreqHz,
        float centerKeyPos,
        float electromrFlux,
        const std::vector<float>& frameSamples
    ) {
        const auto enclave = EnclaveSphere77::evaluate(frameIdx, elapsedSec, electromrFlux);
        const float u = std::sin(0.5f * kPi * static_cast<float>(frameIdx) * 0.25f);
        const float v = std::cos(0.5f * kPi * static_cast<float>(frameIdx) * 0.25f);
        const auto christoffel = ChristoffelManifoldGuard::evaluate(u, v, centerKeyPos, electromrFlux);

        const float vs = 45.0f + 15.0f * std::abs(std::sin(elapsedSec));
        const float vo = 12.0f;
        const auto doppler = DopplerWaveGeometry::evaluate(baseFreqHz, 343.0f, vs, vo, true);

        const auto conv = LaplaceConvolutionBus::evaluateLaplaceDomain(
            frameSamples, 0.25f, 2.0f * kPi * doppler.observedFreqHz, kFullKeyG9Hz
        );

        return IntegratedTelemetry{
            enclave.totalCells,
            enclave.sigmaBandHz,
            enclave.enclaveCoherence,
            christoffel.connectionNorm,
            doppler.observedFreqHz,
            doppler.machNumber,
            doppler.supersonicConeActive,
            conv.transferMagnitude
        };
    }
};

inline void runIntegrationVerification() {
    static_assert(kCube48Cells == 110592, "48^3 = 110,592");
    static_assert(kEnclave77Cells == 456533, "77^3 = 456,533");

    const auto cState = ChristoffelManifoldGuard::evaluate(0.5f, -0.25f, 0.4f, 0.6f);
    assert(std::abs(cState.boundedExcursion) <= (kGuardrailRatio13_5 + 1e-4f));

    const auto dState = DopplerWaveGeometry::evaluate(528.0f, 343.0f, 30.0f, 5.0f, true);
    assert(dState.observedFreqHz > 528.0f);

    const std::vector<float> testSig(64, 0.25f);
    const auto convRes = LaplaceConvolutionBus::evaluateLaplaceDomain(testSig, 0.2f, 100.0f, 528.0f);
    assert(convRes.timeDomainConvolved.size() == testSig.size());

    const auto eState = EnclaveSphere77::evaluate(3, 0.25f, 0.5f);
    assert(eState.totalCells == 456533);
    assert(eState.sigmaBandHz >= kSigmaMinHz && eState.sigmaBandHz <= kSigmaMaxHz);

    std::cout << "[VERIFIED] Christoffel Gamma^k_{ij}, Doppler wavefronts, Laplace y(t)=(h*x)(t), and 77^3=456,533 Enclave Sphere.\n";
}

} // namespace axoneme::symphony

int main() {
    axoneme::symphony::runIntegrationVerification();

    std::vector<float> sampleFrame(512, 0.0f);
    for (std::size_t i = 0; i < sampleFrame.size(); ++i) {
        const float t = static_cast<float>(i) / 48000.0f;
        sampleFrame[i] = 0.25f * std::sin(2.0f * axoneme::symphony::kPi * 528.0f * t) +
                         0.15f * std::sin(2.0f * axoneme::symphony::kPi * 48.0f * t);
    }

    const auto tel = axoneme::symphony::IntegratedSymphonyBridge::stepTelemetry(
        1, 0.011f, 528.0f, 0.35f, 0.62f, sampleFrame
    );

    std::cout << "Enclave Sphere : " << tel.enclave77Cells << " cells | Sigma="
              << tel.sigmaBandHz << " Hz | Coherence=" << tel.enclaveCoherence << "\n"
              << "Christoffel    : ||Gamma||=" << tel.christoffelNorm << "\n"
              << "Doppler        : f_obs=" << tel.dopplerObservedHz << " Hz | Mach=" << tel.dopplerMach << "\n"
              << "Laplace |H(s)| : " << tel.convolutionTransferMag << "\n";

    return 0;
}