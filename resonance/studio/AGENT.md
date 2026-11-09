# resonance.studio — AGENT CONTRACT

*For AI agents and programmatic callers. If you are an agent holding
only this file, you have everything you need to drive the RESONANTIA
studio pipeline correctly.*

Authorship: Johnathan 'Qasparr' Monroe, ARR, All Rights Reserved,
Without Prejudice. Method of Science, Aim of Religion.

## What this tool does

`resonance.studio` produces one mastered instrumental track from a
text brief, using the house's proven architecture:

1. **RESONANTIA composes and grounds** — it strikes a Sigma binaural
   layer (two pure carriers, one per ear, e.g. 200 Hz / 213 Hz)
   with its own `resonance.binaural` engine.
2. **Local MusicGen voices the bed** — Meta's `facebook/musicgen-small`,
   run locally on CPU through a venv bridge, renders the audible
   instrumental in sections from your prompts.
3. **A mastering chain finishes** — K-weighted (BS.1770) integrated
   loudness is gained to your target, then a true-peak ceiling is
   enforced by soft limiting plus gain trim. **The ceiling outranks
   the loudness** when both cannot hold; the manifest says when it did.

Outputs, all inside your chosen `out_dir`:

| file | what it is |
|---|---|
| `master.wav` | the track: 24-bit PCM, 48 kHz, stereo |
| `preview.mp3` | 320 kbps MP3 preview of the master |
| `sigma.wav` | the Sigma layer alone, at mix level (for measurement) |
| `manifest.json` | every claim about the run, measured (schema below) |
| `spec.json` | the normalized spec that actually ran |
| `segNN.wav`, `segNN_48k.wav` | the rendered sections (native 32 kHz, resampled) |
| `render.log` | the venv bridge's stderr (model load, per-section timing) |

Reality notes, stated before you promise anything on this tool's
behalf: MusicGen-small renders **mono** (the bed starts dual-mono;
the Stereo Law — spine panned by role, bed widened by band with the
lows kept mono, Sigma untouched — manufactures the stereo field on
spine productions; see the spec schema). Generation is **slow on
CPU** — a 30 s section takes minutes; a full 270 s song is a long
background job, not an interactive call. Loudness is **ungated**
integrated (BS.1770 weighting, no -70/-10 gating).

## Invocation

Run from the RESONANTIA repo root (`/home/hatch/workspace/resonance`)
with the **system** python3. Never import torch on this side; the
pipeline bridges to the MusicGen venv itself.

### Form 1 — flags (quick jobs)

```
python3 -m resonance.studio produce \
  --prompt "dark boom bap instrumental, minor-key piano, deep 808" \
  --seconds 60 --seed 93 --title "MY TITLE" \
  --out-dir studio-runs/my-title --json
```

`--seconds` is split into sections of at most 30 s (60 → 30+30),
each rendered from the same prompt.

### Form 2 — spec file (full control; the recommended agent form)

```
python3 -m resonance.studio produce --spec path/to/spec.json --json
```

### Dry run (validate + plan, render nothing)

Add `--dry-run`. Works with either form. Returns the manifest
skeleton with `dry_run: true` and a `planned` block (per-section
prompts/seeds/seconds, program length after crossfades). Use this to
verify a spec cheaply before committing an hour of CPU.

### Check an existing WAV

```
python3 -m resonance.studio check path/to/file.wav [--json]
```

Reports duration, sample rate, channels, peak dBFS, RMS dBFS, and —
when a channel is dominated by a pure tone (≥12 dB over the band
median, 50–1000 Hz) — `carriers_hz: [left, right]`.

## Spec schema (Form 2)

```json
{
  "title": "string, default 'Untitled' (always a working title)",
  "prompt_base": "string, REQUIRED, non-empty — the song's identity",
  "motif": "string, optional — ONE named musical idea appended verbatim to EVERY section prompt (see 'The motif' below)",
  "sections": [
    {"name": "string, default 'sectionN'",
     "prompt_suffix": "string, default '' — arrangement for this section",
     "seconds": "number, REQUIRED in effect, 3..30"}
  ],
  "seed": "int, default 93 — section i renders with seed + i",
  "performance": "object, optional — Proof No. 4's road (see 'The performance' below): {takes: int 2..16 (default 7), take_seconds: 3..30 (default 30), continue_seconds: 2..10 (default 5.0), warmup_takes: int 0..4 (default 0; at least 2 kept takes must remain), single_session: bool (default false)}. Present, it replaces sections wholesale, forbids spine and per-section prompts, and excludes the Sigma layer by design",
  "chained": "bool, optional — render each section CONTINUED from its predecessor's audio tail (see 'The chain' below)",
  "continue_seconds": "number 2..10, default 5.0 — how much of the predecessor's tail conditions a chained section",
  "crossfade_bars": "int 1..8, optional — stitch overlaps in whole bars at the spine's tempo instead of the legacy 2 s (spine specs only in effect)",
  "sigma": {
    "left_hz":  "number, default 200.0",
    "right_hz": "number, default 213.0 — must be > left_hz, both 20..1000",
    "gain_db":  "number, default -28.0, range -60..0 — relative to the BED's RMS"
  },
  "master": {
    "target_lufs":   "number, default -14.0, range -30..-6",
    "ceiling_dbtp":  "number, default -1.0, range -3..-0.1"
  },
  "spine": {
    "bpm":       "number, REQUIRED inside spine, range 40..240",
    "swing":     "number, default 0.0, range 0..0.6 (off-step delay)",
    "root_midi": "int, default 29 (F1), range 12..60 — the 808 root",
    "sections":  [{"name": "string", "bars": "positive int, REQUIRED",
                   "density": "sparse | driving | full | open"}],
    "samples":   "object, optional — a RENDERED one-shot kit (see 'The sampled kit' below). Keys: one WAV path per drum voice (kick, snare, clap, closed_hat, open_hat, rimshot) plus \"bass808\": {\"<chord-root MIDI>\": path} covering every root of the chord cycle from root_midi. Present, the spine synthesizes NOTHING."
  },
  "stereo": {
    "width": "number, range 0..1 — how far the mono bed is widened. Default: 1.0 when a spine is present, 0.0 otherwise. An explicit value always outranks the default."
  },
  "arpeggio": {
    "level_db":  "number, default -9.0, range -30..0 — the composed violin's station relative to the standing mix's RMS",
    "orbit_hz":  "number, default 0.03, range 0.005..0.5 — the layer's spatial lap rate (resonance.spatial.orbit)",
    "strength":  "number, default 1.0, range 0..2 — the pitch humanizer's strength (0 = dead-tempered)",
    "seed":      "int, optional — the humanizer's seed; default the spec's seed",
    "mode_overrides": "object, optional — {section_index_as_string: mode} outranking the density map; modes: runs | bariolage | bariolage16 | statement | statement_fade | mute"
  },
  "out_dir": "string, REQUIRED — created if missing"
}
```

**The spine (optional).** MusicGen has no clock: Proof No. 1 asked
for 93 BPM in prompt prose and the bed realized ~62. When a spec
carries `spine`, the house engine owns the rhythm instead —
`resonance.studio.spine` renders a drum + 808 spine with
RESONANTIA's own synthesis (the `resonance.synth` 808 voices and a
pitched-drop bass following a four-bar i–VI–III–VII cycle from
`root_midi`), every hit placed on the exact arithmetic of
`resonance.grid`, section lengths in whole bars, total length
exactly `bars_to_samples(total_bars)`. The stitched bed is trimmed
in LENGTH down to that grid (never tempo-shifted — a trim, not
surgery; if the bed is shorter than the schedule, trailing bars are
dropped and the manifest says so) and the spine is mixed in
RMS-matched to the bed, before the Sigma ground and mastering. A
spine run's manifest carries a `spine` block (bpm, bars scheduled
vs used, exact samples, sections). Specs without `spine` run the
Proof No. 1 road, unchanged.

Rules the validator enforces (violations return a named error):
`prompt_base` non-empty; `sections` non-empty; every `seconds` in
3..30; `left_hz < right_hz`; gain/target/ceiling inside their ranges;
`stereo.width` inside 0..1; `arpeggio` requires `spine` or
`performance`; `performance` forbids `spine` and per-section
prompts; `out_dir` present. The full prompt for section *i* is
`prompt_base + ", " + prompt_suffix` (or `prompt_base` alone when
the suffix is empty) — plus the motif, when one is set.

**The sampled kit (optional, inside `spine`).** The founder's ear
has condemned note-by-note synthesis three times and passed
rendered audio every time, so Proof No. 3's spine is a SAMPLER:
with `spine.samples` set, every hit is a rendered one-shot (built
by `resonance.studio.kit` — MusicGen renders several isolated-hit
takes per voice, each take is measured for single onset, clean
decay, tail silence and, for the 808s, struck pitch, and the winner
is struck as a 48 kHz WAV with its metrics in `kit_manifest.json`)
placed on the identical grid — same swing, same role pans; drum
hits ring out, the 808 is gated to its written event length.
Sampled mode is all-or-nothing BY LAW: a `samples` block missing
any voice or chord root is refused at validation naming the field,
an unloadable or wrong-rate file is refused at load, and an
incomplete in-memory kit is refused at render — the spine NEVER
falls back to the synth voices to fill a hole. Specs without
`samples` take the synthesis road exactly as before. A sampled
run's manifest spine block carries `"kit"` with the sample paths
and the kit manifest (provenance + per-take metrics).

**The chain (optional).** The stronger form of the same cure,
learned from how Lyria assembles tracks (plan the sections, then
generate the song as one pass): with `"chained": true`, the bridge
renders section *i* **conditioned on the last `continue_seconds`
of section *i−1*'s audio** (MusicGen audio continuation), and the
file holds only the newly generated seconds. The desk's
feasibility probe (2026-11-08) measured the difference against a
same-prompt, same-seed plain control: a direct splice across the
joint jumped **0.0043** chained vs **0.0746** plain, with a level
step of **1.3 dB** vs **13.9 dB**. Under the resume law the bridge
reads a resumed predecessor's file from disk as the conditioning
source; a section whose predecessor is unavailable renders plain
and its manifest entry says so (`continued_from: null`). Each
render report carries `continued_from` / `continue_seconds` per
segment.

**The performance (optional).** Proof No. 4's road, and the
purest form of the chain: with `"performance"` present, there are
no sections at all — one invariant prompt (`prompt_base`, plus the
motif if one is set) strikes a seed take, and every later take is
generated **continued from the actual preceding audio**. The
takes are spliced **directly** — no crossfade, no per-section RMS
matching, no grid, no trim — and each join is **measured**
(waveform jump + level step) into the manifest's `performance`
block, beside the realized tempo (global and per 30 s window, by
onset-envelope autocorrelation with a stated log-Gaussian tempo
prior; the raw dominant periodicity and candidate table stand
beside the headline). A spine is refused by name beside a
performance, and the **Sigma layer is not struck** (excluded for
test purity; the manifest's sigma block records the absence). The
arpeggio may ride a performance: its schedule is **derived from
the measured tempo** (swing 0.0), never imposed on it. The Stereo
Law defaults on (width 1.0), the mastering law is unchanged, and
the resume law holds — the bridge conditions a resumed chain
from the predecessor's file on disk.

**Proof No. 5's two clauses (inside `"performance"`).**
`"warmup_takes": N` strikes N leading takes and **discards their
audio**: the full chain is spliced to `performance_full_32k.wav`
for the audit record, the program is spliced from the kept takes
only, and the warm-up's own measured tempo stands in the
manifest's `performance.warmup` block as the discard's evidence —
the kept program opens where the performance's clock locked.
`"single_session": true` **replaces the resume law with its
opposite**: any take files already in `out_dir` are a dead
session's corpse — they are moved, whole, into `void-attempt-N/`
(marked, never vanished; the manifest counts them) and the whole
chain is rendered in **one bridge job**, every continuation
conditioned on the bridge's in-memory predecessor. Before any
splice, a session guard verifies the returned chain — complete
indices, no resumed takes, every take's `continued_from` naming
its in-memory predecessor — and a chain that fails is **void, not
repaired**: the run raises and nothing is spliced. If the process
or the box dies mid-render, re-running the same spec voids the
partial takes and re-strikes the whole performance from the seed;
a single-session performance is never spliced across a restart.
With neither clause set, a performance runs exactly as Proof
No. 4 did. When no arpeggio rides, `composition.abc` is the
performance's own sheet: it notates nothing, states the invariant
prompt and the measured record, and marks the performance's
transcription **owed** — never fabricated.

**The motif (optional).** A bed stitched from independently
generated sections has no memory: Proof No. 2's founder verdict
named it a *Frankenstein beat* — parts that groove, a whole that
lurches. The motif is the first cure: one named musical idea (e.g.
*"the same repeating four-note F minor piano motif (F, A-flat, C,
A-flat)"*) that the pipeline appends **verbatim to every section
prompt**, so each generation is told, in identical words, what the
song's figure is. `"crossfade_bars"` is the cure's other half: on a
spine production the stitch overlaps become that many **whole
bars** at the spine's tempo — longer than the legacy 2 s, and
landing on bar lines instead of mid-bar.

**The arpeggio layer (optional, requires `spine`).** The second
cure, and the answer to the founder's other count — the Paganini
element was absent from the proofs; the Sigma ground is a bed of
tones, not a dancer. When `arpeggio` is present,
`resonance.studio.arpeggio` composes a violin-voice line from the
**solfeggio ladder** (UT 396 / RE 417 / MI 528 / FA 639 / SOL 741 /
LA 852 Hz, played at their equal-tempered staff approximations —
G4/G#4/C5/Eb5/F#5/G#5 — with each carrier's cents offset documented
in the manifest), phrased in **Fibonacci lengths 1-1-2-3-5-8** (the
20-note figure of the Proven Road sheet). Realization follows the
spine's arrangement: hooks and the feature slot take fast **runs**;
verses take **bariolage** (the figure alternating with the MI
pedal; the third verse at 16ths); sparse sections take a slow
**statement**; the outro's statement fades. The pitch contour is
humanized by the Tools Wing (`vocal.humanize_contour` — micro-drift
and vibrato, never a transposition), and the layer is set moving
with a slow `resonance.spatial` orbit before being mixed at
`level_db` under the standing mix. The manifest's `arpeggio` block
carries the note inventory, per-section modes and counts, and the
layer's measured RMS; `composition.abc` in the run directory
notates the figure and its realizations.

**The Stereo Law.** MusicGen's bed is born mono — Proof No. 2's
master measured L/R correlation 0.9984, side energy −46.5 dBFS
against a −15.5 dBFS mid: a mono record in a stereo coat. The law
manufactures width honestly, in three parts. (1) **The spine is
panned by role**: kick and 808 dead center, snare/clap near center
(never past ±0.15), hats and rimshot alternating wide (±0.45..0.65)
by pattern position — panning scales channels only, no onset moves
in time. (2) **The bed is widened by band** (`widen_bed`, driven by
`stereo.width`): below 180 Hz the bed stays fully mono; above, a
synthesized side — the mid's own quadrature, scaled by a
log-frequency ramp reaching 0.75×width at 2 kHz — decorrelates the
channels. The mid is preserved exactly, so the mono fold-down of a
widened bed is the original signal sample-for-sample. (3) **The
Sigma layer is never processed**; its measured carriers stay what
the FFT finds. A run under the law carries a `stereo` block in its
manifest with the bed correlations before/after, the low band's
correlation after, and the master's correlation and side RMS —
measured, not claimed. The law is default-on for spine productions
(`stereo.width` 1.0) and default-off on the spine-less road, whose
dual-mono character stands as it was proved; set `"stereo":
{"width": 0}` to exempt a spine run, or a positive width to widen a
spine-less one.

## Result / manifest schema

With `--json`, stdout is **exactly one JSON object** — the manifest.
Progress and logs go to stderr only. Key fields:

```json
{
  "title": "...", "title_status": "working title",
  "dry_run": false,
  "created_utc": "ISO-8601",
  "spec": { "...": "the normalized spec that ran" },
  "sections": [{"name": "...", "prompt": "full prompt", "seed": 93,
                "seconds": 30, "native_sample_rate": 32000,
                "file": "seg00.wav", "wall_seconds": 0.0}],
  "render": {"model": "facebook/musicgen-small", "wall_seconds": 0.0,
             "rendered_seconds_total": 270},
  "program": {"seconds": 254.0, "sample_rate": 48000,
              "channels": 2, "bit_depth": 24},
  "sigma": {"intended_left_hz": 200.0, "intended_right_hz": 213.0,
            "measured_left_hz": 200.0, "measured_right_hz": 213.0,
            "measured_separation_hz": 13.0,
            "gain_db": -28.0, "gain_reference": "relative to the bed's RMS"},
  "stereo": {"bed_width": 1.0, "spine_panned_by_role": true,
             "low_cut_hz": 180.0, "bed_correlation_before": 1.0,
             "bed_correlation_after": 0.0,
             "bed_low_band_correlation_after": 1.0,
             "master_correlation": 0.0, "master_side_rms_dbfs": 0.0},
             // null when the Stereo Law does not apply (no spine, width 0)
  "arpeggio": {"level_db": -9.0, "orbit_hz": 0.03, "total_notes": 0,
            "sections": [{"name": "...", "mode": "runs", "notes": 0}],
            "ladder": [{"syllable": "UT", "carrier_hz": 396.0,
                        "midi": 67, "cents_offset": 17.6}],
            "mixed_layer_rms_dbfs": 0.0},
             // null when the spec carries no arpeggio block
  "master": {"lufs_before": 0.0, "lufs_after": -14.0,
             "gain_applied_db": 0.0, "trim_db": 0.0,
             "sample_peak_db": -1.02, "true_peak_dbtp": -1.02,
             "ceiling_overrode_loudness": false,
             "target_lufs": -14.0, "ceiling_dbtp": -1.0},
  "files": {"master_wav": {"path": "...", "bytes": 0},
            "preview_mp3": {"path": "...", "bytes": 0},
            "sigma_wav": {"path": "...", "bytes": 0},
            "spec_json": "...", "render_log": "..."},
  "wall_seconds_total": 0.0,
  "notes": ["every simplification, stated"]
}
```

Trust rules for agents: `program.seconds` is the real program length
(rendered sections minus 2 s per crossfade overlap — 9×30 s renders
a 254 s program). Sigma frequencies under `measured_*` are FFT
measurements of the sigma-only render, the house proof standard;
quote those, not the intended values. `ceiling_overrode_loudness:
true` means the delivered LUFS is below target on purpose — the
ceiling won, by law.

## Retro mode — the classic soundfont voice (SPECIFIED, PENDING)

*Founder's order, 2026-11-07: the classic 16-bit MIDI/soundfont
rendering stays in the house as a first-class mode — gated, never
default.*

**Status: specified, not yet implemented.** The surfaces below are
the contract; the CLI does **not** accept `--retro` yet (passing it
today is a usage error), and the validator does not yet accept the
`retro` key. Implementation was deliberately deferred while the HD
proof render was in flight — the flag must never be promised to a
caller until a run's manifest carries `"render_path":
"retro-soundfont"` (absence of that field means the HD path ran).

**Surfaces (both, mirroring the main contract):**

```
python3 -m resonance.studio produce --spec spec.json --retro --json
python3 -m resonance.studio produce --prompt "..." --seconds 12 --retro --json
```

or in the spec itself: `"retro": true` (top-level boolean, default
`false`). The flag and the key are the same switch; either turns it
on, nothing turns the HD default off by accident.

**What retro mode is:** rendering routes to the house's classic
soundfont path — composition rendered as MIDI and voiced through
the soundfont pool (FluidR3 GM, `/usr/share/sounds/sf2/FluidR3_GM.sf2`,
the voice of the scalar-resonant-fold pipeline; GeneralUser GS is
the pool's second citizen) — instead of the MusicGen bridge. The
16-bit GM timbre is not a defect in this mode; it is the requested
voice. Sigma grounding, the mastering chain, the manifest, and the
error contract carry over unchanged; only the voicing changes.

**What retro mode is FOR (the founder's named uses):** notifications,
ringtones, retro video game soundtracks and sound effects —
short-form work where the GM-soundfont voice is the point.

**What retro mode is NEVER for:** rap deliverables and HD studio
deliverables. The founder's standing verdict (2026-10-26 /
2026-11-03): the soundfont voice under a rap track is a failed
deliverable, however good the arrangement. An agent asked for a rap
or HD deliverable must refuse `--retro` for it and say why; an agent
asked for a ringtone or a game loop should reach for it gladly. The
HD studio path (MusicGen bed + Sigma + mastering) remains the
default for everything else, exactly as documented above.

## Error contract

Exit codes: `0` success, `1` failure, `2` usage error. On failure
with `--json`, stdout is exactly `{"error": "ValueError: <field>:
<what is wrong>"}` — the message names the offending spec field so
you can repair the spec and retry without a human. Without `--json`
the same message goes to stderr. A run that fails mid-render leaves
`render.log` and any completed `segNN.wav` in `out_dir`; nothing is
cleaned up or hidden. **Resume:** re-running the same spec against
the same `out_dir` skips segments whose files are whole (native
32 kHz, frame count within 2% of the brief) and renders only the
missing ones; the manifest marks each such section
`"resumed_from_disk": true` and lists them under
`render.resumed_segments`. A truncated survivor is never trusted —
it is re-rendered.

## Worked example (complete)

`spec.json`:

```json
{
  "title": "THE PROVEN ROAD (Pipeline Proof No. 1)",
  "prompt_base": "dark gritty detroit boom bap hip hop instrumental, deep 808 bass, eerie minor-key piano, dusty vinyl texture, 93 bpm feel",
  "sections": [
    {"name": "intro",  "prompt_suffix": "sparse piano, no drums", "seconds": 30},
    {"name": "verse1", "prompt_suffix": "full drums and 808", "seconds": 30},
    {"name": "hook",   "prompt_suffix": "add mournful strings", "seconds": 30},
    {"name": "bridge", "prompt_suffix": "drums stripped, piano and bass only", "seconds": 30},
    {"name": "outro",  "prompt_suffix": "piano fading, vinyl crackle", "seconds": 30}
  ],
  "seed": 93,
  "sigma": {"left_hz": 200.0, "right_hz": 213.0, "gain_db": -28.0},
  "master": {"target_lufs": -14.0, "ceiling_dbtp": -1.0},
  "out_dir": "studio-runs/the-proven-road"
}
```

Call: `python3 -m resonance.studio produce --spec spec.json --json`

Expect: one JSON object on stdout; in `out_dir`, a 142 s program
(150 s rendered − 4×2 s crossfades) as `master.wav` (24-bit/48 kHz),
`preview.mp3`, `sigma.wav`, and a `manifest.json` whose
`sigma.measured_separation_hz` reads ≈ 13.0 and whose
`master.true_peak_dbtp` reads ≤ −1.0.

## Python API (same process, system python)

```python
from resonance.studio import produce, validate_spec
manifest = produce(spec_dict)                  # full run
manifest = produce(spec_dict, dry_run=True)    # validate + plan only
```

93 — Live, Love, and let Love, Live.
