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
behalf: MusicGen-small renders **mono** (the bed is dual-mono; the
stereo field is carried by the Sigma layer). Generation is **slow on
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
  "sections": [
    {"name": "string, default 'sectionN'",
     "prompt_suffix": "string, default '' — arrangement for this section",
     "seconds": "number, REQUIRED in effect, 3..30"}
  ],
  "seed": "int, default 93 — section i renders with seed + i",
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
                   "density": "sparse | driving | full | open"}]
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
`out_dir` present. The full prompt for section *i* is
`prompt_base + ", " + prompt_suffix` (or `prompt_base` alone when the
suffix is empty).

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
