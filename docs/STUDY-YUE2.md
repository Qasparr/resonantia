<!--
93
"Do what thou wilt shall be the whole of the Law."
Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice).
XII day of November, Dies Jovis, Sol in Scorpio, Anno V:xii e.n.
(2026 e.v.)
Scientific Illuminism: Method of Science, Aim of Religion.
Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR,
All Rights Reserved, Without Prejudice. Right of claim hereby
reserved and coined under the authority of the Living Man.

DOCTRINE OF THIS STUDY: a study only. No code was integrated,
no weights were downloaded, nothing was installed. The study
reads YuE2 from its primary sources and reports what they
establish, what they contradict, and what they leave open —
divergences printed as coordinates (the zero-point method),
never smoothed into a verdict. What RESONANTIA may adopt from
YuE2 is DESIGN. YuE2's weights, tokenizer, and latent space
stay YuE2's, under YuE2's licence, which is read in full at §III.
-->

# STUDY: YuE2
## The score-first song engine, read from its own sources — and what RESONANTIA can lawfully learn from it

**Scope.** YuE2 (multimodal-art-projection / M·A·P) is the
strongest study target surfaced by the desk's 2026-11-12
vocal-rendering research: a lyrics-to-song engine whose planner
writes an *editable ABC-notation score* before any audio exists.
RESONANTIA composes in ABC natively. This study answers, from
primary sources, how YuE2's pipeline actually works, whether a
house-written ABC score can be injected into it as a hard input,
what its licence permits and forbids, what hardware it truly
needs, where its English/Mandarin-only limit lives, and which of
its design elements are portable into RESONANTIA's own native
vocal module as clean-room design.

**Sources read (primary).** The GitHub repository
`multimodal-art-projection/YuE` at commit
`1116bea76032bee5668e5f097294d082fa0b84f0` (default branch
`main`; repository metadata: created 2025-01-23, licence
Apache-2.0, version line at v0.1.6): `README.md`,
`docs/generation.md`, `docs/hardware.md`, `MODEL_LICENSE`,
`LICENSE`, `examples/song.json`, `examples/melody.abc`,
`examples/README.md`, and the bundled agent-skill reference
`skills/yue2-music/references/abc-editing.md`. The Hugging Face
model card `m-a-p/YuE2-3B`. The arXiv abstract page for the YuE2
technical report (arXiv:2609.33757, Yuan et al., submitted
27 September 2026). Where the fetch channel could not expose a
source line-by-line — the raw `src/yue2/*.py` files and the
arXiv PDF's internals — the study says so and files the item
under GAPS (§VII) instead of guessing. A secondary code index
(DeepWiki, which cites `src/yue2/` files with line numbers) was
used only to corroborate file paths and the request schema, and
is marked secondary wherever it carries weight.

---

## I. ARCHITECTURE, END TO END

### I.1 The shape in one paragraph

YuE2 is a single **AR–NAR Mixture-of-Transformers (MoT)**
backbone (the YuE2-3B checkpoint) plus a separate VAE decoder
(the YuE2-Vae checkpoint). The autoregressive (AR) side first
*writes a readable score* — melody and harmony in ABC notation —
then expands that plan into **semantic music tokens**. The
non-autoregressive (NAR) side then realizes acoustic latents
from those tokens by **flow matching**. The VAE decodes the
latents into **48 kHz stereo** audio. The paper's abstract
states the design in its authors' own terms: a single AR–NAR
MoT "first writes a readable score specifying melody and
harmony, expands it into semantic music tokens, and realizes it
as full-song audio," with **MERT2** and **SheetSage2** supplying
semantic and symbolic supervision learned from recordings
without aligned scores. In the authors' preference study,
experts preferred symbolic planning **49.3%** of the time versus
**34.6%** without it.

### I.2 The staged API — the pipeline as the code exposes it

The public surface is a staged pipeline, documented in
`docs/generation.md` and the model card, implemented in
`src/yue2/pipeline.py` with the CLI in `src/yue2/cli.py`
(paths corroborated by the repo's own docs and the secondary
code index):

```python
from yue2 import YuE2Pipeline, SymbolicPlan

plan     = pipe.plan(**request)              # the ABC score, as an object
restored = SymbolicPlan.load("outputs/plan") # a saved plan, restored exactly
semantic = pipe.generate_semantic(restored)  # AR: plan + lyrics -> semantic tokens
latents  = pipe.synthesize(semantic)         # NAR: flow matching -> acoustic latents
audio    = pipe.decode(latents)              # VAE: latents -> 48 kHz stereo
```

`pipe(**request)` runs the same stages end to end. A pipeline
processes **one request at a time**. The request itself is a
small dictionary — `examples/song.json` is the canonical
specimen:

```json
{
  "id": "city_lights",
  "style": "English, warm piano pop, expressive female voice, acoustic piano, rounded bass and light drums, lyrical memorable melody, unhurried phrasing, 88 BPM",
  "lyrics": "[Verse]\n…\n\n[Chorus]\n…",
  "cot": "full",
  "seed": 831001
}
```

The request schema (validated in `request_kwargs`,
`src/yue2/cli.py`, per the secondary index at lines 40–57)
admits `style`/`tags`, `lyrics`, `cot`, `abc`/`abc_path`
(mutually exclusive), `seed`, `cfg_scale`, `id`, and the
advanced `abc_sampling`/`semantic_sampling` dictionaries. The
`style` string carries genre, instruments, vocal character,
**language**, and tempo; `lyrics` carries `[Verse]`/`[Chorus]`
section tags. There is **no phoneme input, no reference-speaker
input, and no per-section singer-identity field** anywhere in
the documented surface (`docs/generation.md`).

### I.3 Stage 1 — plan(): the score as a first-class artifact

The `cot` (chain-of-thought) field selects the planning depth:

- `cot="full"` — a melody **and chord** plan; the default.
- `cot="melody"` — a melody-only plan; the model composes free
  accompaniment. Recommended for covers.
- `cot="off"` — no symbolic plan; generation proceeds directly
  from lyrics and style.

The plan's score has exactly **two monophonic melody parts —
Vocal and Ins** (instrumental). Harmony is carried as quoted
chord symbols inside the Vocal line, including while the Vocal
rests. The native ABC dialect is specified, strictly, in
`skills/yue2-music/references/abc-editing.md`:

```
X:1
T:
M:4/4
L:1/32
Q:1/4=88
V: Vocal clef=treble name="Vocal Melody" snm="Vocal"
V: Ins clef=treble name="Ins Melody" snm="Inst."
K:G
% verse
V: Vocal
"Gmaj7"B8d8"Am7"c8A8|"D7"F16"G"G16|
```

And the repository's own runnable specimen, `examples/melody.abc`
(an original eight-bar melody; `L:1/16`, `Q:1/4=88`, `K:C`):

```
X:1
T:
M:4/4
L:1/16
Q:1/4=88
V: Vocal clef=treble name="Vocal Melody" snm="Vocal"
V: Ins clef=treble name="Ins Melody" snm="Inst."
K:C
% verse
V: Vocal
E2G2A2G2E2D2C4|D2E2G2E2D2C2D4|E2G2A2c2B2A2G4|F2E2D2E2G2E2C4|
V: Ins
Z4|
```

Three properties of this dialect matter to the house:

1. **The chord vocabulary is bounded.** Native qualities are:
   major (no suffix), `m`, `dim`, `aug`, `7`, `maj7`, `m7`,
   `dim7`, `m7b5`, `sus4`, `sus2`, `6`, `m6`, `7sus4`, `m(maj7)`;
   slash basses are allowed. `C:maj`, `C13`, `A7alt`, `Cmaj9`
   are **not** native.
2. **The parser is a gatekeeper, on purpose.** The bundled
   helper `skills/yue2-music/scripts/abc_tools.py` (stdlib-only;
   `parse_abc(text)` importable without loading any model;
   `inspect` / `strip-chords` / `compare` subcommands) *rejects*
   tuplets, grace notes, polyphonic stacks, repeats, alternate
   endings, slurs, broken rhythms, decorations, lyric `w:` fields,
   custom voices, and unsupported key modes or chord qualities.
   Adding a third ABC voice does **not** create an independently
   controlled part (`docs/generation.md`).
3. **Accidental semantics differ from general ABC.** In YuE2's
   dialect an accidental propagates by letter across octaves
   within the bar; the skill reference warns not to "silently
   substitute a parser with different accidental semantics."
   A house ABC file is therefore not automatically a YuE2 ABC
   file — it must pass YuE2's dialect gate (see §II).

**Lyric alignment is deliberately kept out of the score.** The
generation API "accepts lyrics and ABC, not a forced
phoneme-to-note alignment channel"; alignment data belongs in
sidecar JSON/Markdown, and `w:` fields must not be added to the
model's ABC. This is a design decision the house should note:
the score stays a pure composition artifact; the phonetic layer
rides beside it, never inside it.

### I.4 Stage 2 — generate_semantic(): AR expansion to semantic tokens

Given a plan (generated, supplied, or restored), the AR side of
the MoT expands it — conditioned on the plan and the lyrics —
into semantic music tokens. (A community port describes the
semantic stream as one codec id per 1/25 s of audio; that figure
is community-sourced, not primary, and is filed as such.) The
semantic stage is where composition becomes performance intent:
the score fixes *what* the notes are; the semantic tokens carry
the sung, played realization the acoustic stage will voice.

### I.5 Stage 3 — synthesize(): flow matching to acoustic latents

The NAR side generates the acoustic latents by flow matching —
the generation guide's progress callbacks expose the internals
at two named points: `"nar"` midpoint steps and `"vae"` tiles.
A secondary snapshot of the code index describes the NAR solve
as 32 midpoint steps of flow matching; the step count is marked
secondary here. In low-VRAM mode the pipeline unloads the song
model before VAE decoding and keeps only the active AR or NAR
module on the accelerator (§IV).

### I.6 Stage 4 — decode(): the VAE to 48 kHz stereo

`decode()` runs the YuE2-Vae decoder (FP32) over the latents and
writes 48 kHz stereo audio. The decoder is a **separate
checkpoint with its own identity**: `YuE2-Vae` is the default
listening decoder; `YuE2-Vae-legacy` is the decoder used by the
published evaluation protocol. Decoding is independently
callable from the CLI on a saved latent file:

```
yue2 decode runs/default/song/latent.npy --vae m-a-p/YuE2-Vae --output decoded.wav
```

Per `docs/generation.md`, decode loads only the FP32 VAE and
accepts finite `[T,64]` or `[1,64,T]` latents for the standard
decoder (tile size default 1024, halo 16).

### I.7 Artifacts and integrity — every stage leaves a receipt

`save_artifacts()` retains, alongside `audio.flac`: the
`score.abc` (when applicable), `plan.json`, the semantic tokens,
`latent.npy`, the effective config, timings, **model identities,
and integrity records**. `SongResult.load(directory,
expected_identity=…)` restores saved artifacts *without
initializing models*. Saved plans are token-exact:
`SymbolicPlan.load` "restores exact token IDs and checks the
saved files" — which is why the documented editing loop never
edits a saved plan in place (§II). The CLI rounds out the
surface: `yue2 generate --request examples/song.json`,
`yue2 validate`, `yue2 inspect`, `yue2 export --output
offline-pipeline --offline` (an offline bundle), and the
`doctor` / `batch` subcommands in `src/yue2/cli.py`
(secondary index, lines 60–146).

### I.8 Companions

Two sibling models supply the system's ears: **SheetSage2**
transcribes a recording into the same symbolic world (score.abc),
which is what makes the cover workflow possible — transcribe,
edit the score, re-render in a new style — and **MERT2** supplies
semantic supervision. On the authors' SHS100K zero-shot cover
benchmark, the full-score pipeline reaches CLEWS mAP **0.647** /
Hit@1 **71.3%**, versus **0.006** / **0.3%** without a score:
the score is doing the identity work. On the authors' own
WildSongBench (192 prompts), YuE2 scores **6.7316** SongBench
average, and **6.9632** at best-of-8 — the highest observed mean
in their table (Suno v5 6.8721, Mureka 9 6.9377) — with the
README's own honesty note standing beside the numbers: "The
small gap between the highest means does not establish
statistical significance."

---

## II. THE ABC QUESTION — CAN A HOUSE SCORE BE INJECTED?

**Answer: YES — at the composition level, through the front
door, as a documented first-class input.** The ABC is not merely
an internal byproduct. Three independent primary sources agree:

- The README's quick-start table defines the request field
  directly: `abc=...` — "Supply your own score in `full` or
  `melody` mode."
- `docs/generation.md` states it as a rule: **"Supplying `abc`
  uses that composition directly; it requires `full` or
  `melody`."**
- The model card's cover workflow passes
  `abc=Path("melody.abc").read_text(...)` with `cot="melody"`,
  and `examples/README.md` shows the same for harmonization
  comparisons: one melody, two `score.abc` variants differing
  only in chord symbols, same lyrics, style, and seed.

The documented **editing loop** is the same door, used twice:

```
plan = pipe.plan(**request)     # generate a plan
plan.save(...)                  # keep its artifacts
# edit the COPY of score.abc — never the saved plan in place
# resubmit the edited text as a fresh `abc` input
```

"Do not change a saved plan in place" is not etiquette; it is
mechanics. `SymbolicPlan.load` restores exact token IDs and
verifies the saved files against their integrity records, so a
hand-edited saved plan fails its own checks. The supported
intervention point is the **ABC text**, re-tokenized on a fresh
submission — which is precisely the intervention point a
house that composes in ABC would want.

**The one softening, stated in the source's own words:**
"Meter, tempo and note durations condition generation; they are
not hard timing constraints on the waveform." The supplied score
is a hard input for *composition* — pitches, harmony, structure,
the identity of the song (the SHS100K numbers at §I.8 are the
evidence) — but the renderer treats its timing as conditioning,
not as a sample-exact grid. A house score injected into YuE2
would be *the song*, performed with the model's own sense of
time. Whether that distinction matters is a musical judgment;
the study's duty is to print the coordinate.

**Below the ABC level, the doors narrow — and here the study
must be exact about what is and is not verified:**

- **Latents → audio: VERIFIED door.** The `yue2 decode` CLI
  (§I.6) decodes a saved `latent.npy` with only the VAE loaded.
  An externally held latent file in the documented shapes is a
  real input.
- **Saved semantic artifacts → re-synthesis: DOCUMENTED as an
  artifact flow.** `SongResult.load` restores a result's saved
  artifacts (semantic tokens and latents among them) without
  initializing models, and the staged objects compose
  (`generate_semantic` → `synthesize` → `decode`). Restoring and
  re-running *the pipeline's own* intermediates is supported.
- **Hand-constructing a `SymbolicPlan` or a semantic-token
  sequence from scratch, outside `plan()` and the `abc` request
  field: NOT VERIFIED.** No primary source read documents a
  public constructor for a plan object from externally tokenized
  ABC, nor a `SemanticResult.load`-style entry for foreign
  tokens. What would settle it: a line-level read of
  `src/yue2/pipeline.py` and the plan/token classes (the fetch
  channel used for this study could not render those files;
  see §VII), or a runtime probe against an installed copy —
  which this study, by its terms, does not perform.

**Dialect caveat for house scores.** Injection is real, but the
gate is YuE2's dialect (§I.3): two monophonic voices only, the
bounded chord vocabulary, no tuplets/repeats/decorations/`w:`
fields, and YuE2's own accidental propagation. RESONANTIA's ABC
output would need a dialect-conformance pass — the repo ships
exactly the tool for checking it (`abc_tools.py inspect` /
`compare`, runnable without a GPU or the model).

---

## III. LICENCE READ

Two instruments govern YuE2, and they split cleanly along the
code/weights line.

### III.1 The code — Apache 2.0, verified

The repository's `LICENSE` file is the standard **Apache License
Version 2.0, January 2004**, read in full for this study:
copyright grant (§2), patent grant with litigation termination
(§3), and the usual redistribution conditions (§4). The README's
licence table concurs: "Code, agent skill, and documentation:
Apache 2.0." The desk may study, port, and re-implement the
code's *design* — and, licence-wise, the code itself — under
Apache terms. Third-party components bundled with the repo
retain their own licences (`THIRD_PARTY_NOTICES.md`; contents
not read in full — §VII).

### III.2 The weights — CC BY-NC 4.0 plus a dated creator permission

`MODEL_LICENSE` (read in full at the pinned commit) opens with
its scope: "The YuE2-3B, YuE2-Vae and YuE2-Vae-legacy checkpoint
weights are licensed under Creative Commons
Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)."
Onto that base it bolts an **additional permission dated
2026-09-16**, whose load-bearing clauses are these:

**The individual permission.** "the YuE2 model licensors grant
personal users, content creators and musicians acting in an
individual capacity permission to use the model weights free of
charge to generate outputs, and to publish, distribute, sell,
license or otherwise monetize those outputs, subject to the
responsible-use conditions below." And its reach: "For these
individual creative activities, the model licensors waive the
NonCommercial restriction to the extent necessary. These users
do not need a separate commercial license from, or owe license
fees or royalties to, the model licensors for this use or for
monetizing their outputs. This includes distributing or
licensing their outputs to clients and publishing them on
commercial platforms."

**What that means for this house, stated plainly.** Johnathan
'Qasparr' Monroe, releasing music commercially **under his own
name, acting in an individual capacity**, is the permission's
named case: he may run the weights, generate songs, and sell,
license, and distribute the *outputs* — on commercial platforms,
to clients — with no fee and no royalty owed to the YuE2
licensors. The permission covers the outputs; "Generated outputs
are not subject to the model weights' NonCommercial restriction
solely because they were generated with YuE2."

**The company line.** "The individual creator permission does
not authorize commercial use of the model weights by companies.
Companies wishing to use the model weights commercially should
contact ryuanab@connect.ust.hk to discuss a commercial license."
The permission is personal. It does not flow to a company, and
it does not make the weights a product component.

**Redistribution.** "This permission concerns generating and
using outputs; it does not extend to commercial redistribution
or sale of the model weights." Sharing the weights themselves
remains governed by CC BY-NC 4.0 — non-commercial sharing with
attribution; no selling them, under any reading.

**Attribution.** For outputs, credit is a courtesy, not a duty:
"We strongly encourage users to credit YuE2 by including the
model name or the #YuE2 tag when sharing generated work. Credit
on generated outputs is optional and is not a condition of this
additional permission or of output monetization." For the
*weights*, attribution remains a real CC BY-NC duty: identify
YuE2, the model name, and its source repository (the three
Hugging Face repo URLs) when sharing weights or adapted weights.

**Responsible use is a condition, not a suggestion.** "you must
not use the model weights or generated outputs for illegal,
harmful, deceptive or otherwise unethical purposes, including
fraud, harassment or deceptive impersonation. You are
responsible for your inputs, outputs and use of the model,
including obtaining any necessary rights and consent." The
weights ship as-is, without warranties, liability disclaimed.
Academic use is free for non-commercial research and education
under CC BY-NC; the licence notes that this "does not itself
grant commercial-use rights to an institution," while an
academic acting *individually* may rely on the individual
permission. The permission is expressly separate from, and does
not restrict, rights under CC BY-NC 4.0, Apache 2.0, or earlier
permission grants, and it covers only rights the licensors have
authority to grant — no rights in third-party material are
conveyed.

**Desk note (not legal advice).** The permission reads as if
drafted for exactly the solo-creator case. Two seams deserve a
lawyer's eye before the house leans commercial weight on it:
(1) where "acting in an individual capacity" ends if a release
ever runs through a house entity rather than his own name; and
(2) the interaction between the responsible-use condition and
ordinary artistic content. Both are flagged, neither is resolved
here.

---

## IV. HARDWARE, FROM SOURCE

### IV.1 The stated baseline

README quick start: **"Linux · Python 3.12 · NVIDIA GPU with
BF16 support and 24 GB VRAM. YuE2 produces 48 kHz stereo audio
without quantization."** `docs/generation.md` gives the working
rule: "Use a 24GB GPU and 24GB available host RAM; maximum-context
testing peaked at 14.08 GiB." The model card's quick start says
Linux · Python 3.10+ · 24GB NVIDIA GPU BF16 — a Python-version
discrepancy between the repo (3.12) and the Hugging Face wheel
(3.10+) that the study notes without resolving (§VII). The song
model runs BF16; the VAE decoder runs FP32; PyTorch is pinned
(2.14.1 on macOS, 2.10.0 elsewhere, per `docs/hardware.md`).

### IV.2 Measured figures (model card; PyTorch 2.10, Transformers 4.57.6, no quantization, default YuE2-Vae, 32 warm samples)

| Device / mode | LM speed | Generation | Audio produced | Peak VRAM |
|---|---|---|---|---|
| RTX 4090 24GB · full CoT | 139.48 tok/s | 71.04 s | 214.85 s | 11.18 GiB |
| RTX 4090 24GB · melody | — | 68.68 s | 214.67 s | 11.02 GiB |
| RTX 4090 24GB · off | — | 57.91 s | 196.88 s | 11.09 GiB |
| H800 80GB · full | 164.38 tok/s | 54.74 s | 224.96 s | 10.34 GiB |

Read plainly: on the baseline card the full pipeline renders a
~3.6-minute song in ~71 seconds — roughly **3× faster than
realtime** — and the *measured* peak (≈11.2 GiB) sits well under
the 24 GB *stated* requirement; the headroom is the
maximum-context case (14.08 GiB peak). A separate vLLM server
runtime is documented (H800, 32 concurrent requests, 373.53
songs/hour, 76.61 GiB peak) — a serving path, not a desktop one.

### IV.3 The low road — low-VRAM, other devices, CPU

`docs/hardware.md` is unusually honest about the edges:

- **Devices.** The pipeline accepts `--device cuda, mps, xpu, or
  cpu` (AMD ROCm rides the `cuda` device name). Everything past
  NVIDIA is labeled **experimental**.
- **Low-memory mode.** `yue2 generate --device cuda --low-vram
  --budget 8`, or `from_pretrained(..., low_vram=True)`: only
  the active AR or NAR module stays on the accelerator, the song
  model is unloaded before VAE decoding, and FP8 AR weights
  (explicitly requested, supported on NVIDIA) are restored to
  BF16 before acoustic prefill. "Transfers require host RAM and
  can reduce speed."
- **A real 8 GB data point.** A Windows machine with an RTX 5060
  Laptop (8 GB) completed two full songs (NAR + VAE) under BF16
  + FP8 AR with `low_vram=True` and a 6,000-token cap; an
  ABC-text replay on the same machine produced 5,823 semantic
  tokens from a 3,491-token prefix (NAR/VAE not run in that
  test). An Intel Arc Pro B70 32 GB (XPU) completed a 58-second
  song and two consecutive requests.
- **The unmeasured frontier, in the source's words:** "Stable
  length limits on 6/8/12 GB devices remain to be measured; long
  KV caches can still exhaust memory."
- **CPU.** A CPU device path exists, and the hardware doc bounds
  exactly what is known about it: "CPU tests cover equations,
  cache visibility, placement order, cancellation/retry and
  artifact integrity. They do not establish accelerator speed,
  supported song lengths or unchanged full-model audio quality."
  Translation for the house: CPU YuE2 is *correct*, on the
  evidence; whether it is *usable* — speed, song length, quality
  parity — is UNVERIFIED from primary sources (§VII).
- **Optional speed switches.** `YUE2_COMPILE=1` enables
  torch.compile decode; `YUE2_XPUGRAPH=1` is experimental.

### IV.4 Quantization

In the **official** repo there is **no quantization or GGUF
path**: the README's phrase is "without quantization," and the
only reduced-precision mechanism is the low-VRAM mode's opt-in
FP8 AR weights (restored to BF16 for the acoustic stage).
*Community:* GGUF conversions of YuE2 circulate outside the
official repo (e.g., Serveurperso/YuE2-GGUF) — community work,
not upstream, one line as ordered.

### IV.5 Against the house's present box

Stated for scale, from §IV.1–IV.3 against the known house
hardware (this VM: no GPU, ~6–8 GB RAM): YuE2 does not run here
in any documented-useful configuration. Its floor — even the
experimental 8 GB laptop path — presumes a discrete GPU the box
does not have. This is the same hardware gate the 2026-11-12
research recorded; the study confirms it from source.

---

## V. LANGUAGE REALITY

**Verified: the demonstrated language world of YuE2 is English
and Mandarin, full stop.** The model card's demos — text-to-music
and covers alike — are English and Mandarin only (Cyber Metal ·
English; 今晚不眠 · Mandarin; Passion · English rock; 最炫民族风 ·
Mandarin cover). The string "Japanese" appears **nowhere** on
the model card (verified by search of the card's full text) and
nowhere in the README's demos. There is no language parameter in
the API: language is one more free-text hope inside the `style`
string, alongside genre and tempo (§I.2), with no phoneme channel
behind it (§I.2, §I.3).

**Where the constraint lives — NOT SETTLED by the sources read.**
The study can bound the possibilities but not convict one. The
planner's text handling is a Qwen-family tiktoken tokenizer
(identified in a community adapter's file inventory — secondary),
which in principle encodes Japanese text without difficulty; a
tokenizer is therefore an unlikely wall. The paper's abstract
says the model's semantic and symbolic supervision is *learned
from recordings* via MERT2 and SheetSage2 — a training-data
mechanism, which points the finger at the **training mix**: a
model whose sung supervision is English and Mandarin sings
English and Mandarin. But the training corpus's language
composition is documented only inside the arXiv PDF, which this
study could not open beyond its abstract (§VII). The honest
coordinate: constraint location UNVERIFIED; training-mix
explanation best-supported by the abstract's own description.

**What Japanese would require.** Not a prompt, not a tokenizer
swap, not a style string. Japanese singing would require the
model to have learned Japanese lyric phonetics against melody —
that is, Japanese-language sung supervision in training, or a
fine-tune of the backbone on such data (itself gated on data,
compute, and the weights' licence, which permits an individual's
use but not commercial weight redistribution). For DETROIT
MUGETSU and the house's Japanese book, YuE2 as released is not a
road; the Gumi's road remains the Gemini strike at quota refill,
with DiffSinger — Japanese-native by design — as the owned
engine under study in the parallel research.

---

## VI. MAPPING ONTO RESONANTIA

### VI.a Design elements RESONANTIA can adopt — portable as DESIGN

1. **The ABC-planner contract.** A human-readable, human-editable
   symbolic score as the *load-bearing intermediate* between
   intention and audio — generated or supplied, versioned,
   diffable, re-submittable. Portable because it is an interface,
   not a model: RESONANTIA already composes in ABC; adopting the
   contract means treating its own ABC the way YuE2 treats
   `score.abc` — the artifact every later stage answers to.
2. **The strict dialect gate.** A bounded chord vocabulary, a
   rejecting parser, and `inspect`/`compare` tooling that verify
   a score's invariants (pitches, onsets, meter, tempo) after
   every edit, *before* any rendering is attempted. Portable
   because it is stdlib-grade engineering: YuE2's own
   `abc_tools.py` needs no model to run. A house dialect gate
   would let desk, founder, and future modules argue about a
   score in the open, with the gate — not taste — ruling validity.
3. **Staging with receipts.** Four stages, each callable alone,
   each leaving inspectable artifacts with model identities and
   integrity records, each restorable without re-running the
   stages before it. Portable because it is pipeline discipline:
   RESONANTIA's studio already keeps manifests; YuE2's
   `save_artifacts` discipline — plan, tokens, latents, config,
   timings, identities — is the mature form of the same instinct,
   and its `decode`-only CLI is the proof that late stages make
   honest standalone tools.
4. **The sidecar rule for phonetics.** Lyrics and alignment ride
   *beside* the score (sidecar JSON/Markdown; never `w:` fields
   inside the model's ABC). Portable because it is a data-hygiene
   decision, and it dovetails with the house's own work: the
   Divine Nine vocal tool (filed this same day) seats vowels at
   exactly such a plug point — a phonetic sidecar is where a
   vowel canon can lawfully govern without ever touching the
   composition artifact.
5. **The edit-the-copy loop.** Never mutate a sealed plan;
   edit a copy of its human-readable form and resubmit it as a
   fresh input, letting integrity checks guard the sealed
   originals. Portable because it is the desk's own standing law
   — dispositions marked, never vanished — expressed as an API.
6. **The decoder as a separate, swappable artifact.** Two VAE
   variants (listening vs evaluation) behind one `decode()`
   contract. Portable as a pattern: RESONANTIA's mastering chain
   already treats rendering as a replaceable final stage; YuE2
   shows the same courtesy extended into the neural stack.

### VI.b What cannot come over

1. **The weights.** YuE2-3B and both VAEs are CC BY-NC 4.0 with
   the individual-creator permission (§III). The founder may
   *use* them and sell the *outputs* under his own name; the
   house may not redistribute them commercially, embed them in a
   product, or lend the permission to any company. An owned
   RESONANTIA vocal module cannot be YuE2 inside.
2. **The tokenizer and semantic codec specifics.** The semantic
   token stream is meaningful only to the checkpoint that learned
   it — its vocabulary, its token rate, its AR/NAR division of
   labor are properties of the trained weights, not of the
   design. Copying the *staging* costs nothing; copying the
   *tokens* copies nothing usable.
3. **The VAE latent space.** A `[T,64]` latent is a coordinate
   in YuE2-Vae's learned space; the decoder that voices it is
   the checkpoint. The 64-channel shape is a fact to design
   around, not an asset to import.
4. **The training supervision stack as data.** MERT2 and
   SheetSage2 are separate models with their own terms; more
   fundamentally, the *corpus* they supervised from is not
   published with the model. The recipe's ingredient list is
   visible; the ingredients are not on the truck.

### VI.c What an owned clean-room implementation would need — honest scale

A house-built engine of YuE2's architecture — AR score planner
→ semantic tokens → flow-matching acoustic stage → VAE decoder,
trained on house-lawful data — would need, at minimum:

- **Data:** a large corpus of recordings with lyrics, from which
  symbolic scores and semantic supervision can be derived
  automatically (YuE2's own answer to the alignment problem is
  two teacher models, MERT2 and SheetSage2, themselves trained
  systems). Assembling, licensing, and cleaning such a corpus —
  and building or training the transcription/feature teachers —
  is a research program before the first song model trains.
- **Compute:** YuE2 is a 3B-class MoT whose *inference* baseline
  is a 24 GB GPU. Training a model of that class is
  datacenter work — multi-GPU clusters, weeks-to-months of
  wall-clock, plus the separate VAE training on 48 kHz stereo
  music. This is not a bigger version of a desk build; it is a
  different species of undertaking, priced in GPU-months.
- **People-time:** the failure modes (alignment drift, semantic
  codec collapse, decoder artifacts) are research-grade and are
  debugged by listening, at scale, for months.

The study's conclusion on this column is deliberately flat:
**adopt the contracts (§VI.a) now; treat the model itself as a
reference instrument to learn from — and, under the individual
permission, an instrument the founder may personally use — not
as a foundation to build the owned module on.** RESONANTIA's
owned vocal road remains the score-conditioned singing-synthesis
shape identified in the 2026-11-12 research (DiffSinger-class:
written score + phonetic sidecar in, sung vocal out, CPU,
Apache-licensed code, house-trained or house-licensed voice),
with YuE2's planner contract as its composition discipline.

---

## VII. GAPS — WHAT THIS STUDY COULD NOT VERIFY FROM PRIMARY SOURCES

Listed plainly, each with what would settle it:

1. **The arXiv PDF's internals.** Only the abstract was read;
   the PDF did not open through the fetch channel. Model
   layer counts, hidden sizes, exact parameter count, training
   corpus scale and language mix, and tokenizer design are
   therefore UNVERIFIED from the paper. (Community figures —
   28 layers, vocab 184,704, ~3.63B parameters — circulate in
   secondary coverage and are marked community wherever this
   study mentions them.) *Settled by:* reading the PDF.
2. **`src/yue2/*.py` not read line-by-line.** GitHub's rendered
   file pages did not expose those sources to the fetch tool.
   Function-level claims in §I–§II rest on the repo's own
   documentation (`docs/generation.md`, `docs/hardware.md`,
   README, examples, the bundled skill reference) plus a
   secondary code index's line citations (`src/yue2/cli.py`,
   `src/yue2/pipeline.py`, `src/yue2/storage.py`,
   `src/yue2/modeling_yue2.py`). *Settled by:* a local clone
   read — outside this study's no-download terms for weights,
   though not for code; a future desk pass may close this.
3. **External construction of plan/semantic objects.** Whether a
   caller can hand-build a `SymbolicPlan` or semantic-token
   sequence outside `plan()` / the `abc` field is NOT VERIFIED
   (§II). *Settled by:* the line-level code read in item 2, or a
   runtime probe.
4. **Where the language constraint mechanically lives.** Planner,
   tokenizer, or training mix — bounded and argued at §V, not
   settled. *Settled by:* the paper's data section (item 1) or
   controlled prompting experiments (a runtime matter).
5. **CPU feasibility in practice.** Speed, supported song
   lengths, and quality parity on CPU are expressly unestablished
   by the hardware doc itself. *Settled by:* upstream benchmarks
   or a house runtime test on GPU-less hardware.
6. **Stable song-length limits on 6/8/12 GB devices.** Expressly
   "remain to be measured" upstream. *Settled by:* upstream
   measurement.
7. **`THIRD_PARTY_NOTICES.md` contents.** The bundled-component
   licences beyond the Apache/CC split were not read in full.
   *Settled by:* one read of that file.
8. **Python-version discrepancy.** Repo README/hardware: Python
   3.12. Model-card wheel path: Python 3.10+. Which governs a
   source install versus the wheel is not reconciled in the
   sources read. Minor; noted.
9. **SheetSage2 and MERT2 internals.** Their architectures,
   licences, and hardware are outside this study's read set;
   they enter here only in their documented roles. *Settled by:*
   a companion study, if the desk ever weighs the transcription
   road.

---

*Study closed. The score is the contract; the licence is the
fence; the hardware is the gate; the gaps are printed at the
same size as the findings.*

93 — Live, Love, and let Love, Live.
