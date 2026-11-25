# 93

# CRYSTAL IMPORT — the 5D Memory Crystal pattern importer

**Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
ARR, All Rights Reserved, Without Prejudice.**
Written XXV day of November, Anno V:xii e.n. (2026 e.v.), under the
Method of Science, Aim of Religion — Scientific Illuminism.

**Module:** `resonance/studio/crystal_import.py` ·
**Tests:** `tests/test_crystal_import.py` (22) ·
**Proof strike:** `studio-runs/crystal-import-proof/`

## Source — and its credit

The format below was read out of the source of a single-page Web
Audio instrument the founder found in the wild and ordered
imported:

> **Source: https://sortiarius.neocities.org/5D_Memory_Crystal_Evolution_05**
> (author unknown; the link stands as the credit, founder's ruling
> 2026-11-25 — where a used thing's author cannot be known, the
> source link it was got from is its credit.)

The page's own face prints its honesty line, honoured here by
repetition: its audio is "original generative music and sound
design, not a recording or decoding of extraterrestrial signals."

## What it reads — the format, as extracted (never guessed)

The page's **Save** writes `memory-crystal-pattern.json`:

```json
{ "title": "5D Memory Crystal pattern",
  "tempo": 72, "scale": "minor", "mood": "deep",
  "tracks": [ {track} x4 ] }
```

Each **track** object is `{name, base, wave, level, pattern, oct}`:

| Track | base | wave | level | oct |
|---|---|---|---|---|
| SUB HORIZON | 55 | sine | .34 | 0 |
| GLASS ORBIT | 110 | triangle | .16 | 1 |
| PHANTOM CHOIR | 220 | sine | .12 | 2 |
| SIGNAL DUST | 440 | sawtooth | .055 | 3 |

- **pattern**: 16 entries, each strictly **0 or 1** — the step
  button toggles with `pattern[j] ^= 1`. 1 strikes, 0 is silent.
  There is **no per-step level** in the source; the "−1" sometimes
  mistaken for one is the lowest option of the **Octave/register**
  select (−1…+3). Track level is per-track, slider 0–60%.
- **scales** (semitone offsets from the root A): `minor`
  [0,2,3,5,7,9,10] · `pent` [0,3,5,7,10] · `whole` [0,2,4,6,8,10]
  · `phryg` [0,1,3,5,7,8,10]. **moods** (strings in the file):
  deep, ritual, signal, ice. **tempo**: the slider's range is
  40–140 BPM, standing at 72.
- **timing**: the sequencer's tick is `ms = 60000/tempo/4` — a step
  is a **sixteenth note**; 16 steps make one 4/4 bar. At 72 BPM a
  step lasts **0.208 s** (the beat is 0.833 s).
- **the pitch walk** (`note(t, idx)`, idx = step + track index):
  `n = sc[(2·idx + ⌊idx/3⌋) mod len(sc)] + (idx%3==0 ? 0 :
  12·⌊idx/7⌋)`; `f = base · 2^((n−12)/12) · 2^oct`.

The page's **factory patterns** (its state on first opening) are
carried in the module as `DEFAULT_PATTERN` and used as the test
and proof fixture.

**Validation fails closed.** `load_pattern` / `validate_pattern`
refuse, with named errors: missing keys, a tempo outside the
slider's range, an unknown scale or mood, a track count other
than 4, a name/base/wave differing from the instrument's constants
(the page's UI offers no way to change them, so a file that
differs was not written by the page), a level outside 0–0.60, an
oct outside −1…+3, a pattern not 16 long, or any step not 0 or 1.

## The re-grounding — 440 → 432, printed

The page is tuned **A4 = 440**; the house field is **A4 = 432**.
The conversion keeps the page's degree walk and note identities
exactly and re-grounds only the frequencies. Every base is an A,
so each house base is the same A at 432 (`base × 432/440`, exact):

| Track | theirs | ours |
|---|---|---|
| SUB HORIZON | 55 Hz | **54 Hz** |
| GLASS ORBIT | 110 Hz | **108 Hz** |
| PHANTOM CHOIR | 220 Hz | **216 Hz** |
| SIGNAL DUST | 440 Hz | **432 Hz** |

`regrounding_report()` prints this; every converted event carries
both frequencies (`freq_page_hz`, `freq_house_hz`).

## The seats — role map, with reasoning

| Page voice | House seat | Reasoning |
|---|---|---|
| SUB HORIZON | **house 808** (`eightoeight.kick`, pitched to the event's house frequency) | a pitched sine bass at A1 — the 808 is the house's pitched bass body |
| GLASS ORBIT | **SSO Glockenspiel, program 39** | a bright triangle named for glass — the glockenspiel is the bank's glass: fast attack, long ring (violin pizzicato was the other candidate; glass names the choice) |
| PHANTOM CHOIR | **pad seat, gated** — Salamander Grand seated; SSO 1st Violins Sustain (prog 2) layer held | see the gate below |
| SIGNAL DUST | **SSO Xylophone, program 42**, low gain | a faint high sawtooth, the quietest voice — a short bright wooden strike. Program 42 **is** the xylophone (the transcription lab's correctio established that at cost); here it is used knowingly, for its own voice |

Track level → velocity is linear over the slider's range
(`vel = level / 0.60 × 127`), so the page's own balance ratios
survive the crossing.

### The articulation gate — measured, not assumed

The transcription lab's fix pass measured the pad bodies' floors
(attack-to-90% + one step; `RECEIPT-FIX.md`): **violins sustain
0.842 s · Salamander 0.130 s**. Against the page's steps:

- at 72 BPM a step is 0.208 s — **below** the violins floor,
  **above** the Salamander floor;
- at the page's slowest, 40 BPM, a step is 0.375 s — still below
  the violins floor. **No tempo the page allows seats a single
  choir step on the strings.**

So the import seats PHANTOM CHOIR on the Salamander Grand, and the
strings layer engages only where a note is made to sustain at
least the floor — a rendering decision a caller may take, never
the pattern's own content. The verdict rides on every choir event
(`event.gate`), printed.

## Outputs

- `convert(pattern)` → `CrystalEvent` list (track, role, seat,
  program, step, start/duration from tempo, MIDI, degree, both
  frequencies, velocity, gate).
- `to_abc(events, pattern)` → one ABC tune per track through the
  house writer (`resonance.abc.writer`), rests filling the grid so
  the text re-parses to the same events — verified for all four
  scales in the tests.
- `to_midi(events, pattern, path)` → a dependency-free Standard
  MIDI File (format 1, 480 ticks/beat), one track per voice. The
  808 has no General MIDI body; its track carries program 38
  (Synth Bass 1) as a **named placeholder** — the house strike
  renders the true 808 from the events, not from this file.

## The proof strike

`studio-runs/crystal-import-proof/` — the page's factory pattern
imported and looped four bars through the house sample road
(`proof_strike.py`; instruments credited in
`~/workspace/lab/samples/CREDITS.md`). Measured landing, printed
not smoothed: **−17.05 LUFS / −0.97 dBTP** (the −14 guide is not
reached: the premaster already peaks at the −1 ceiling — sparse
strikes, long quiet between them — so loudness normalization has
no headroom to give; the shortfall is the material's own crest),
MP3 at 320k CBR, spectral centroid 496.0 Hz. A mechanism
demonstration, not a caliber claim.

## The boundary

Import only. What is read is the page's **pattern file** — tempo,
scale, mood, step positions — never its code and never its
oscillators. The page's generative choices remain its author's;
what the house strikes from an imported pattern is the house's
rendering. The founder's ear gates any caliber claim.

93 — Live, Love, and let Love, Live.
