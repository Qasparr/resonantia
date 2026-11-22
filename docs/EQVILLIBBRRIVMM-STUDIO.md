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

## Cut in (2026-11-22)

*Under the founder's ruling of 2026-11-22 — "whatever is waiting
on me, just do it if its ready" — the seam above was cut in. The
"deliberately untouched" state recorded above stands as the
pre-ruling record; what follows is the landed wiring.*

- `validate_spec` carries the optional `eq_pole_hz` key (a number
  in 20..20000), validated beside the other mastering keys.
  Absent, the key is struck from the normalized spec entirely —
  an EQ-less spec means exactly what it meant before the cut.
- In `produce()`'s section road, each stem passes through
  `eqvillibbrrivmm.apply_eq` at the pole, per channel, as its
  samples are read (step (b), after the resample read, before
  the stitch) — hence before the spine, the Sigma ground, and
  `master_signal()`, as the seam prescribed.
- The run manifest gains an `eq` block only when the key was
  ordered: the pole, the bus's measured transfer magnitude
  (first stem, first channel at top line; every stem's
  per-channel measurement in `stems`), and the application
  point. An absent key strikes no eq block and changes no
  sample — weighed in tests/test_studio_pipeline_cutins.py by
  rendering one fixed two-tone spec both ways: identical master
  bytes without the key; with the key, the high band's share of
  the program falls, as the bus's probed direction said it must.
- The performance road refuses `eq_pole_hz` by name in
  `validate_spec` rather than carrying it silently: its takes
  are one invariant performance under Proofs No. 4/5, and the
  bus does not ride that road in this cut-in.

## Divergences on the record

Printed in the module itself, never smoothed: Python computes in
float64 where the C++ computes in float32 (agreement to float32
precision, not bit-exactness); the C++ phase wrap at 2*pi*1024 is
unreachable at studio frame sizes and is not reproduced;
EnclaveSphere77 stands as constants only in this stage.

*93 — Live, Love, and let Love, Live.*
