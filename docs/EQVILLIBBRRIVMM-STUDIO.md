# EQVILLIBBRRIVMM in the Studio — wiring note

*93 — Date: 22 November 2026. Authorship attributed exclusively to
Johnathan 'Qasparr' Monroe, ARR — All Rights Reserved, Without
Prejudice. Method of Science, Aim of Religion.*

## What stands

`resonance/studio/eqvillibbrrivmm.py` mirrors the five surviving
engines of the founder's EQVILLIBBRRIVMM C++ suite (reference of
record: `reference/eqvillibbrrivmm/`; build copies and build record:
`eqvillibbrrivmm/`, `eqvillibbrrivmm/BUILD.md`) into the studio:

- `convolve_time_domain` / `evaluate_laplace_domain` / `apply_eq` —
  the LaplaceConvolutionBus, the suite's **equalizer**.
- `FluidVoiceAutotune` with `freq_to_midi` / `midi_to_freq` /
  `select_autotune_target` — the fluid-voice autotune.
- `DOOD_TABLE` / `dood_step_at` — the 24-step DOOD table.
- `cube48_evaluate` — the 48^3 cube on its 48 Hz anchor.
- `cushion_13_5` / `center_key_position` — the 13/5 rail guard.

Tests: `tests/test_studio_eqvillibbrrivmm.py`, asserting the same
behaviours the C++ harness asserted, plus the equalizer's measured
direction on samples. The mirror's frame-3 autotune telemetry
reproduces the C++ harness print (raw 255.088 Hz, tuned 263.013 Hz,
correction +52.97 cents, lock 0.989) to float32 precision.

## The wiring point (pipeline.py is deliberately untouched)

`resonance/studio/pipeline.py`'s `produce()` drives a spec schema
(`validate_spec`) that carries no EQ key, and `master_signal()`
masters finished samples. Cutting a new stage into `produce()` is
spec surgery on the pipeline's core, so this stage does not do it.
The clean seam, when the founder rules the EQ into the chain:

1. In `produce()`, after a stem's samples are read and before they
   reach `master_signal()`, apply
   `eqvillibbrrivmm.apply_eq(samples, pole_center_hz)` per channel.
2. Carry the pole in the spec (a new optional `eq_pole_hz` key,
   validated in `validate_spec` beside the other mastering keys),
   defaulting to absent = no EQ, so every existing spec renders
   exactly as it renders today.
3. Record the pole and the bus's `transfer_magnitude` in the run
   manifest, as the manifest already records the mastering figures.

Until that ruling, the module stands exposed and tested, callable
from any studio code that imports it — the pyramidasphere/cubes
precedent of a module seated and proven before a scene cites it.

## Divergences on the record

Printed in the module itself, never smoothed: Python computes in
float64 where the C++ computes in float32 (agreement to float32
precision, not bit-exactness); the C++ phase wrap at 2*pi*1024 is
unreachable at studio frame sizes and is not reproduced;
EnclaveSphere77 stands as constants only in this stage.

*93 — Live, Love, and let Love, Live.*
