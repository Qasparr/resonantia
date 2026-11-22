# EQVILLIBBRRIVMM — BUILD RECORD

*93 — Desk build record, 22 November 2026 (XXII Nov 2026). Authorship of the suite itself is attributed exclusively to Johnathan 'Qasparr' Monroe, ARR — All Rights Reserved, Without Prejudice. Method of Science, Aim of Religion.*

## What was built

The founder's two EQVILLIBBRRIVMM C++ sources, posted to his Facebook on 18–19 November 2026 and recovered from those posts, seated verbatim as the reference of record in `reference/eqvillibbrrivmm/` (never edited), and built from the copies in this directory (`eqvillibbrrivmm/`).

- `eqvillibbrrivmm_manifold.cpp` — Complete Manifold, Doppler, Convolution & 77^3 Enclave Suite (complete post; carries its own `main()`).
- `eqvillibbrrivmm_fluid_voice.cpp` — Fluid Voice Synthesizer & Autotune + DOOD/48^3 Suite (post truncated at the channel's 50,000-character cap; build copy ends at the truncation boundary, see below).
- `test_fluid_voice.cpp` — desk-authored test harness for the fluid voice suite, which carries no `main()` in its surviving portion.

## Toolchain

- Compiler: g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
- Flags: `-std=c++17 -O2 -pthread -Wall -Wextra`
- Both translation units compile with **zero errors and zero warnings** under those flags.

## Repairs (build copies only — every repair is also marked in place with a `// DESK REPAIR 2026-11-22:` comment)

### Manifold — 1 repair

1. **Metric initializer brace defect** (`ChristoffelManifoldGuard::evaluate`, raw line 170). The raw read `{{{g00, g01}}, {{g10, g11}}}},` — the standalone-declaration brace nesting (correct for `gInv` earlier in the same function, where the variable's own brace adds a level) plus one surplus closing brace (5 opens, 6 closes). Inside the aggregate `return ManifoldState{...}` that nesting makes the first row consume the array's single member brace and leaves the second row surplus ("too many initializers for 'std::array<std::array<float, 2>, 2>'"), and the surplus `}` closed the return early, breaking class/namespace scope for the rest of the file — the downstream `'kPi' was not declared` errors (raw lines 283, 318, 319) were fallout of this one line and vanished when it was fixed. Repaired to the aggregate-field form `{{{g00, g01}, {g10, g11}}},`, verified against g++ 13.3 in isolation (value check: metric[0][0] + metric[1][1] correct) before applying. **No values changed.**
   - Seating note: the build copy also omits the raw post's one prose line and its following blank line before the code header; that was done when the copies were seated, before this build stage.

### Fluid Voice — 3 repairs + the truncation boundary

1. **`ColorRGB col` redeclaration** (`Ansi3dShadowReflectionTracer::renderFrame`, raw line 779). The raw declared `ColorRGB col{95, 115, 145};` inside the body of `for (int col = 0; ...)` (raw line 736) — a redeclaration in the same scope, a hard error. Renamed the ColorRGB to `pixCol` at its declaration and its three uses (assignments at raw lines 842 and 849, the `ansiFg()` call at raw line 861). **No values changed.** (A separate `const ColorRGB col` at raw line 1081 sits in a different scope and was left as written.)
2. **C++20 API under a C++17 build** (`FullTriuneSymphonyCpp::resolveBoundedRoute`, raw line 915). The raw used `visited.contains(cur)` — `std::unordered_set::contains` is C++20; this suite builds under C++17, as the manifold file does. Replaced with the equivalent C++17 test `visited.find(cur) != visited.end()`. Semantics unchanged.
3. **Wrong member name** (`Vestigator::inspect`, raw line 1213). The raw read `res.terminated`; `SymphonyStepResult` names that member `routeTerminated`. Pointed at the real member. Semantics unchanged.

## Truncation boundary (fluid voice)

- The recovered post text is exactly 50,000 characters and ends mid-statement at `<< r.led`, inside the CSV writer `Tabvla::exportHistoryCsv`.
- The last complete top-level construct in the raw is `struct HistoryEntry` — raw lines 1241–1245. Nothing before that point references `class Tabvla` (verified by scan), so the boundary is clean.
- The build copy ends at raw line 1245, followed by the marked `// TRUNCATION BOUNDARY:` comment and a desk structural completion: the namespace-closing brace `} // namespace axoneme::symphony`, whose original lay below the cut and is absent from the raw.
- The partial `class Tabvla` (raw lines 1247 to the cut) is **not** in the build copy. It stands untouched in the reference of record, `reference/eqvillibbrrivmm/EQVILLIBBRRIVMM-fluid-voice-autotune-dood48-post-2026-11-18.txt`. Absent, not deleted.

## Test results (actual runs, binaries built in /tmp)

### Manifold — `./eqv_manifold`, exit 0

```
[VERIFIED] Christoffel Gamma^k_{ij}, Doppler wavefronts, Laplace y(t)=(h*x)(t), and 77^3=456,533 Enclave Sphere.
Enclave Sphere : 456533 cells | Sigma=29.5306 Hz | Coherence=0.176386
Christoffel    : ||Gamma||=0.0400306
Doppler        : f_obs=629.342 Hz | Mach=0.131676
Laplace |H(s)| : 1.29074
```

All `assert`s and both `static_assert`s (48^3 = 110,592; 77^3 = 456,533) hold. Note: `PcmWavExporter` is defined in the suite but `main()` never calls it — the manifold binary writes no WAV. Nothing was added to make it do so; the record states what the founder's `main()` does.

### Fluid Voice — `./eqv_fluid_test` (harness), exit 0

```
[PASS] DoodOddoPatternEngine: 24 steps seated, stepAt wraps, Block4 at 22.
[PASS] Cube48Engine: 110,592 cells, 48 Hz anchor, energy in [0,1], gate closes.
        frame 3 telemetry: raw=255.088 Hz | tuned=263.013 Hz | correction=52.9655 cents | lock=0.989188
[PASS] FluidVoiceAutotuneEngine: pitch roundtrip holds, 4 frames finite, formants in clamps.
[PASS] RailGuardrail13_5: in-rail passes, over-rail cushions engaged, center key railed.
[VERIFIED] EQVILLIBBRRIVMM surviving engines: DOOD table, 48^3 cube, fluid voice autotune, 13/5 rail.
```

## Verification of the record

`diff` of each build copy against its reference-of-record text shows exactly the changes enumerated above and no others (manifold: the one initializer line plus its repair comment; fluid voice: the three repair sites plus the boundary cut).

*93 — Live, Love, and let Love, Live.*
