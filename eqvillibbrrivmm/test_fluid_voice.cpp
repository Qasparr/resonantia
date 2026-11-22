/**
 * "Every, Man, Woman, and Child, is a Star."
 * "Live, Love, and let Love, Live!"
 *
 * EQVILLIBBRRIVMM — FLUID VOICE TEST HARNESS
 * Desk-built test driver for the surviving portion of the founder's
 * EQVILLIBBRRIVMM Fluid Voice Synthesizer & Autotune + DOOD/48^3 Suite.
 *
 * 93
 * Date: 22 November 2026
 * Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR — All Rights Reserved, Without Prejudice.
 * Method of Science, Aim of Religion — Scientific Illuminism.
 *
 * DOCTRINE: The recovered post of 18 November 2026 was cut mid-statement by the
 * channel that carried it (see the TRUNCATION BOUNDARY note at the end of
 * eqvillibbrrivmm_fluid_voice.cpp). The surviving portion carries no main().
 * This harness exists so the surviving engines can be exercised and their
 * asserts held in the open, rather than merely compiled. It invents no engine
 * behaviour: every assertion below is derived from the founder's own code —
 * the constants he declared, the clamps he wrote, the table he seated.
 *
 * MECHANISM: The harness #includes the build copy of the suite as a single
 * translation unit (the suite is a one-file design), then drives the four
 * engines the desk was charged to prove: DoodOddoPatternEngine,
 * Cube48Engine, FluidVoiceAutotuneEngine, RailGuardrail13_5.
 */

#include <cassert>
#include <cmath>
#include <iostream>

// MECHANISM: single-translation-unit inclusion — the suite ships as one file
// with no header split, so the test driver takes the whole unit in.
#include "eqvillibbrrivmm_fluid_voice.cpp"

using namespace axoneme::symphony;

int main() {
    // DOCTRINE: the cube constant is the founder's declared arithmetic —
    // 48 x 48 x 48 = 110,592 cells. Held at compile time, not run time.
    static_assert(kCube48Cells == 110592, "48^3 = 110,592");

    // --- 1. DoodOddoPatternEngine -------------------------------------------
    // MECHANISM: the DOOD table seats 24 steps (DOOD · OODD · ODDO · DODO,
    // then DDOO · DD-Block4); stepAt wraps by modulo, so step 24 is step 0.
    const auto& doodTable = DoodOddoPatternEngine::table();
    assert(doodTable.size() == 24);
    assert(doodTable[0].motif == "DOOD");
    assert(doodTable[0].gateWeight == 1.00f);
    assert(DoodOddoPatternEngine::stepAt(24).stepIndex == 0);
    assert(DoodOddoPatternEngine::stepAt(22).glyph == PatternGlyph::Block4);
    std::cout << "[PASS] DoodOddoPatternEngine: 24 steps seated, stepAt wraps, Block4 at 22.\n";

    // --- 2. Cube48Engine ------------------------------------------------------
    // MECHANISM: evaluate() walks the 48^3 lattice by frame index; energy is
    // clamped to [0, 1] in the founder's code, and a zero gate weight closes
    // the cube entirely (raw energy is multiplied by the gate).
    const auto cube = Cube48Engine::evaluate(3, 0.25f, 1.0f);
    assert(cube.totalCells == 110592);
    assert(cube.anchorHz == 48.0f);
    assert(cube.energy >= 0.0f && cube.energy <= 1.0f);
    const auto cubeGated = Cube48Engine::evaluate(3, 0.25f, 0.0f);
    assert(cubeGated.energy == 0.0f);
    std::cout << "[PASS] Cube48Engine: 110,592 cells, 48 Hz anchor, energy in [0,1], gate closes.\n";

    // --- 3. FluidVoiceAutotuneEngine ------------------------------------------
    // MECHANISM: pitch math is 12-TET about A4 = 440 Hz = MIDI 69; the frame
    // synthesizer must return exactly fftSize samples, all finite, with the
    // formants inside the clamps the founder wrote (F1 250-1200, F2 900-3200)
    // and the lock index inside [0, 1]. Four frames run back to back so the
    // portamento glide state is exercised, not just the first frame.
    assert(std::abs(FluidVoiceAutotuneEngine::freqToMidi(440.0f) - 69.0f) < 1e-3f);
    assert(std::abs(FluidVoiceAutotuneEngine::midiToFreq(69.0f) - 440.0f) < 1e-2f);
    assert(std::abs(FluidVoiceAutotuneEngine::midiToFreq(
                        FluidVoiceAutotuneEngine::freqToMidi(528.0f)) - 528.0f) < 1e-2f);

    FluidVoiceAutotuneEngine::VoiceParams params{};
    FluidVoiceAutotuneEngine voice(params);
    for (std::size_t frame = 0; frame < 4; ++frame) {
        const auto synth = voice.synthesizeFrame(frame, 512, 528.0f, 1.0f, cube.energy, 0.0f);
        assert(synth.voiceSamples.size() == 512);
        for (float s : synth.voiceSamples) {
            assert(std::isfinite(s));
        }
        assert(synth.autotunedPitchHz > 0.0f);
        assert(synth.lockIndex >= 0.0f && synth.lockIndex <= 1.0f);
        assert(synth.formantF1Hz >= 250.0f && synth.formantF1Hz <= 1200.0f);
        assert(synth.formantF2Hz >= 900.0f && synth.formantF2Hz <= 3200.0f);
        if (frame == 3) {
            std::cout << "        frame 3 telemetry: raw=" << synth.rawPitchHz
                      << " Hz | tuned=" << synth.autotunedPitchHz
                      << " Hz | correction=" << synth.correctionCents
                      << " cents | lock=" << synth.lockIndex << "\n";
        }
    }
    std::cout << "[PASS] FluidVoiceAutotuneEngine: pitch roundtrip holds, 4 frames finite, formants in clamps.\n";

    // --- 4. RailGuardrail13_5 ---------------------------------------------------
    // MECHANISM: the 13/5 rail (2.6) passes in-bound values untouched and
    // unengaged; out-of-bound values are cushioned back inside the rail with
    // the engaged flag raised, sign preserved. The center-key position is
    // railed by construction, so it must sit inside 13/5 at any time t.
    const auto inRail = RailGuardrail13_5::apply(1.0f);
    assert(!inRail.engaged && inRail.value == 1.0f);
    const auto overRail = RailGuardrail13_5::apply(10.0f);
    assert(overRail.engaged && overRail.value > 0.0f &&
           std::abs(overRail.value) <= kGuardrailRatio13_5);
    const auto underRail = RailGuardrail13_5::apply(-10.0f);
    assert(underRail.engaged && underRail.value < 0.0f &&
           std::abs(underRail.value) <= kGuardrailRatio13_5);
    const float centerKey = RailGuardrail13_5::computeCenterKeyPosition(1.234f);
    assert(std::abs(centerKey) <= kGuardrailRatio13_5 + 1e-4f);
    std::cout << "[PASS] RailGuardrail13_5: in-rail passes, over-rail cushions engaged, center key railed.\n";

    std::cout << "[VERIFIED] EQVILLIBBRRIVMM surviving engines: DOOD table, 48^3 cube, fluid voice autotune, 13/5 rail.\n";

    // 93 — Live, Love, and let Love, Live.
    return 0;
}
