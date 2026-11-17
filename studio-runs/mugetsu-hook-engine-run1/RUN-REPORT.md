[LOGO — centered: the TVRRIS VERITATIS seal, `~/workspace/templates/doctrine-logo.png`, the Architect's chosen mark]

**MUGETSU HOOK — ENGINE RUN 1: THE DIFFSINGER PLUG, PHASE 1**
*Subtitle:* A Scientific Illuminist treatment of the DiffSinger plug for RESONANTIA — score and lyrics in, a sung vocal out, with the Divine Nine seated at the vowel layer

Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice)
XVI day of November, Dies Lunae, Sol in Scorpio, Anno V:xii e.n. (2026 e.v.)

Classification: Enterprise • Educational • Research & Development
Method of Science, Aim of Religion

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All Rights
Reserved, Without Prejudice. Right of claim hereby reserved and coined under
the authority of the Living Man.

---

## I. WHAT WAS ORDERED

Phase 1 of the in-house vocal road (`docs/IN-HOUSE-VOCAL-ROAD.md`, Layer 1 —
the ENGINE): build the DiffSinger plug into RESONANTIA, reusing the proven
invocation of the first self-sufficient run (`studio-runs/spear-and-magickal-helm-run1/`),
with the Divine Nine seated at the vowel layer of the phoneme sequence per
the design study (`docs/THE-DIVINE-NINE-VOCAL-TOOL.md`). The phase proof:
render the DETROIT MUGETSU hook end-to-end **through the new engine module** —
not by calling the lab scripts directly. A standing-law addendum from the
founder, issued the same evening (2026-11-16 22:34 EST), binds the whole
build: MAGVS and Doctrine treatment on all source code and documents, and
the Lex Stellarrvm Familia of Fonts wherever anything is typeset, with
missing seats named, never silently substituted. Both are applied below
and audited in §V and §VIII.

## II. WHAT WAS BUILT

**The module — `resonance/studio/diffsinger.py`** (system side). Its seat
is beside `render_musicgen.py` in `resonance/studio/`, because it is the
same kind of citizen: a bridge client that turns a spec into audio plus a
measured manifest while the heavy inference lives across a wall. It holds
the sequence law, all of it pure and unit-tested without a neural network
in the room: the Nine's seating tables (`seat_vowel`, `seat_line`,
`ledger_totals`), the grouping law (`group_morae`), the sequence builder
(`build_line`), the `.ds` serializer (`write_ds`), a minimal Standard MIDI
score reader (`read_midi`, `melody_from_midi` — MIDI is the score, never
the sound), WAV measurement (`measure_wav`, stdlib `wave` + numpy), and
the bridge runner (`render`), which mirrors `pipeline._run_bridge`'s
contract: job file in the out dir, progress to `render.log`, the result is
the last stdout line, failures raised with the bridge's own error named.

**The bridge — `resonance/studio/render_diffsinger.py`** (lab side). The
only part of the plug that imports onnxruntime/torch/soundfile; never
imported by the system interpreter, executed **by path** with the
diffsinger-lab venv's python (`~/workspace/resonance/diffsinger-lab/venv/bin/python`,
overridable via `RESONANTIA_DIFFSINGER_PYTHON`). It sings built sequences
through the five proven stages, stage-batched across lines exactly as the
Spear run drove them: duration (dsdur linguistic + `duration_lem_26v.dur.onnx`)
→ variance (dsvariance linguistic + `pitch_variance_lem_25.variance.onnx`,
20 steps, retake ones, zero voicing/tension inputs) → acoustic
(`acoustic_lem_25.onnx`, 30 steps, depth 0.6, gender zeros, velocity ones)
→ PC-NSF-HiFiGAN vocoder (torch, the lab checkpoint). Print gain follows
the Spear vocal-stem precedent: a file whose float peak would exceed
−1 dBFS prints at exactly ceiling/peak and the gain is **reported**;
otherwise the file prints untouched at gain 1.0.

**The bank — Lem the Shapeshifter DS 2.5** (`diffsinger-lab/banks/Lem-the-Shapeshifter-DS-2.5-dur26/lem_v2_5`),
named here as its terms of use ask (attribution by naming; commercial use
free; no NFT/crypto; corpus CC BY 4.0). Renders are permitted; nothing of
the bank is redistributed — and no audio enters git at all, per house rule.

**Tests — `tests/test_studio_diffsinger.py`**: 24 unit tests over the pure
law (seating, grouping, builder arithmetic, `.ds` shape, score reader,
measurement math against a known sine). All 24 pass; the full studio suite
runs **165 tests, all green** with the module in the tree.

**The run driver — `build_run.py`** (this folder): assembles the proof's
spec from the filed sources of record and hands it to the module. The
score page typesetter is `make_score_page.py`; its product is
`hook-score-page.pdf` (§V).

## III. THE NINE AT THE PLUG POINT

The plug implements the design study exactly, under the founder's rulings:

- **VV is the high-back seat** — his stamp of 2026-11-12 ("Seat it — VV
  takes the /u/ family"). Japanese *u* and English UW seat under VV; EN UH
  is VV's nearest offset; the OU glide re-reads as ending **at** the VV
  seat. VV carries **no isopsephy weight** in the founder's canon — it is
  not counted in the 1,779 (the seven pure vowels 1,294 + EI 15 + OU 470),
  holds no Greek weight, and is seated here in the acoustic register only,
  exactly as his stamp scoped it. A unit test fences this mechanically.
- **Consonants are vowels-only ruled** (ruled under delegation 2026-11-15,
  revisable by his pen): the Nine govern the vowel layer alone. Consonants
  are not seated, not weighed, not mapped — they pass language-native,
  exactly as the phonemizer emits them, and the ledger counts the pass
  (`PASS_NATIVE`) so it is visible, never silent.
- **No vowel→Archon mapping is declared or invented.** The seats are
  acoustic stations (formant coordinates). The mapping to any office is
  the founder's pen alone — UNCHARTED, and this build does not chart it.

Japanese seats (this run's tongue): a→Α, i→Ι, e→Ε, o→Ο exact; u→VV seated
(its unrounding kept as a coordinate of the seat); long vowels hold the
same seats, length as duration. English seats are implemented in the same
table for the road ahead (AA→Α with a backness coordinate, IY→Ι, EH→Η and
AO→Ω with length coordinates, EY/OW/AY/AW/OY half-seated at their onsets,
IH/AE/AH/AX/ER unseated with coordinates reported) and are covered by the
unit tests, though no English line was rendered in this phase.

**The run's seating ledger** (recomputed in §VIII): 219 phonemes —
**118 vowels SEATED** (Α 35 · Ε 26 · Ο 25 · Ι 17 · VV 15) and **101
consonants PASS_NATIVE**. Every vowel the hook carries found its seat;
no vowel went unseated, because the Japanese table has no unseated row.

## IV. THE PROOF RENDER

**Hypothesis.** The plug, built as specified, sings the filed hook from
its filed score, end-to-end through the module, at the score's pitches,
with every mora of the filed text sung and none added.

**Method.** Three sources, each read, none edited:

1. *The text* — extracted byte-exact from
   `studio-runs/gemini-mugetsu-japanese/DETROIT-MUGETSU-PROMPT.md` (the
   first [HOOK — YAMI, SUNG] block of the filed LYRICS section; the driver
   refuses unless it finds exactly eight lines between the anchors it
   read in the file). The founder's lyrics, raw and uncut.
2. *The score* — `DETROIT-MUGETSU-HOOK-TEST.mid`, read by the module's
   own score reader (track "Hook melody"): 54 notes, per-bar counts
   [7,6,7,7,7,7,7,6], every bar fully tiled. The MIDI carries no tempo
   meta, so the clock is stated from the notation of record
   (`DETROIT-MUGETSU.abc`): **144 BPM**, bar = 1.6667 s, hook = 13.3333 s,
   key G# minor.
3. *The pronunciation* — a hand mora table (127 morae), each mora's
   phonemes taken from the bank's own `dsdur/dsdict-ja.yaml` (palatals as
   the bank's single tokens — ky, ny, my, sh, ch, ts, j; ん = `ja/N`; the
   long-vowel mark as its own vowel mora, as the bank writes long vowels),
   cross-checked by an independent kana mora splitter run over each
   line's reading: the two hands agreed on all eight lines, or the driver
   would have refused.

*Alignment (CONSTRUCTED, labeled):* the melody carries 54 notes against
127 morae, so morae group under notes by the module's grouping law —
contiguous runs proportional to note duration (largest remainder),
minimum one mora per note, every mora sung, no note altered. Groups per
line: L1 [3,3,2,2,2,2,4] · L2 [4,2,2,2,2,4] · L3 [2,2,2,2,2,2,4] ·
L4 [2,2,2,2,1,1,2] · L5 [2,2,2,2,2,1,2] · L6 [3,2,2,2,2,2,4] ·
L7 [2,2,2,2,2,2,4] · L8 [3,3,3,2,4,4]. Lines sit at their bar starts; the
score tiles each bar fully, so no breath padding was inserted — the
duration model's realized lengths are measured below, and the shortfall
reads as breath at each bar's tail. Speaker: **Civet** — YAMI sings the
hook in the package's formation; the bank documents no register for its
three colors (Civet, Phascogale, Quoll), so the seat is the house's proven
lead (Spear's hook lead and verse; the lab's first Japanese phrase) — the
desk's choice, flagged here for the founder's ear, not a claim about the
bank.

**Observation — the measurements** (read off the struck files system-side,
`manifest.json`):

| Line | Morae | Phonemes | Asked | Rendered | % of budget | Peak | RMS |
|------|-------|----------|-------|----------|-------------|------|-----|
| hook-l1 | 18 | 31 | 1.6667 s | 1.5093 s | 90.6% | −13.04 dBFS | −28.45 dBFS |
| hook-l2 | 16 | 27 | 1.6667 s | 1.4977 s | 89.9% | −14.33 dBFS | −28.41 dBFS |
| hook-l3 | 16 | 28 | 1.6667 s | 1.4977 s | 89.9% | −16.41 dBFS | −26.73 dBFS |
| hook-l4 | 12 | 23 | 1.6667 s | 1.4745 s | 88.5% | −14.60 dBFS | −26.21 dBFS |
| hook-l5 | 13 | 22 | 1.6667 s | 1.4977 s | 89.9% | −13.63 dBFS | −28.80 dBFS |
| hook-l6 | 17 | 29 | 1.6667 s | 1.5209 s | 91.3% | −13.90 dBFS | −27.03 dBFS |
| hook-l7 | 16 | 29 | 1.6667 s | 1.5093 s | 90.6% | −16.89 dBFS | −30.45 dBFS |
| hook-l8 | 19 | 30 | 1.6667 s | 1.5441 s | 92.6% | −14.47 dBFS | −28.70 dBFS |
| **Assembly** | **127** | **219** | **13.3333 s** | **13.3333 s** | — | **−13.04 dBFS** | **−28.36 dBFS** |

Assembly: `mugetsu-hook.wav`, 588,000 samples at 44,100 Hz, mono, PCM_16.
No print gain was applied anywhere (every peak already under the −1 dBFS
ceiling; all gains exactly 1.0). Bridge wall time 81.71 s; total driver
wall 84.25 s. Per-line WAVs stand in `lines/`; the asked sequence stands
in `sequence.ds`, the realized in `sequence-realized.ds` (§VI names its
one reconstruction).

**Independent verification.** The struck assembly was probed spectrally
against the score (dominant frequency in mid-note windows): line 1 note 1
measured **415.4 Hz** against G#4's 415.30; line 1 note 3 measured
**621.4 Hz** against D#5's 622.25; the final held note of line 8 measured
**413.3 Hz** against G#4's 415.30; a fourth probe measured 613.3 Hz in
line 5's fifth note (D#5, 622.25 — within a sung note's drift on a short
window). One probe in the desk's first probe script was mislabeled (a bar
index slipped by one) and its window arithmetic threw once before the
window was built from the segment length; both slips are the desk's,
owned here — the measurements themselves are consistent: **the voice
sings the score's pitches.**

**Result.** The hypothesis stands. The hook is sung end-to-end through
the engine module — 127 morae, 219 phonemes, 54 notes, eight bars — and
Phase 1's proof, as the vocal road defines it ("the Mugetsu hook through
the engine"), is delivered. What the ear makes of Civet's seat is the
founder's verdict to give; no ear verdict is claimed here.

## V. THE FONT RECORD — LEX STELLARRVM FAMILIA

The run typesets one document: `hook-score-page.pdf` (one page, A4,
60,347 bytes), built by `make_score_page.py` in this folder. Its seats,
under the Familia discipline (missing seats named, never silently
substituted):

- **Notation seat — FILLED by the Familia.** The hook melody's ABC
  (V:1 of X:1, extracted from the filed `DETROIT-MUGETSU.abc`, never
  retyped) is set in **Lex Stellarrvm ABC Notation** — the family's one
  face (176 glyphs, struck XV November 2026). Every glyph the notation
  needs was verified present in the face's cmap before typesetting
  (letters, digits, `" # | / : = [ ]`, ♯ ♭ ♮).
- **Japanese lyric seat — OPEN in the Familia.** The family holds no CJK
  face in v1. The eight lyric lines stand in **Noto Sans CJK JP**
  (collection index 0 of the system Noto Sans CJK TTC) — a shelf face,
  named on the page itself, not a family member.
- **Prose seat — OPEN in the Familia.** No text, bold, italic, or display
  weights exist in v1. Prose stands in **Liberation Sans** (regular, bold,
  italic TTFs), a named Unicode shelf face. First strike's lesson, named:
  the PDF core faces were tried first and **refused the house's own
  punctuation** (the em-dash is outside their encoding) — the prose seat
  moved to a Unicode face rather than respell the text to fit a font.
- **Greek seat — not exercised by this page.** The family's ABC face
  carries monotonic Greek (Α–Ω, α–ω, ς, tonos); polytonic Greek
  (breathings, iota subscript) is an open seat in v1, recorded in
  `~/workspace/templates/FONT-RECORD.md`. The seating ledger's Greek
  station letters in §III are data in this Markdown record, not
  typesetting, and are not claimed as set in the family face.

The RUN-REPORT itself is a Markdown record in the Teacher's Edition
format; its logo stands at its head as a named marker (the seal file
lives on the templates shelf, outside this repo — a Markdown page in git
cannot carry the workspace path as a rendered image, and the gap is
stated rather than papered over).

## VI. SEAMS AND WALLS, AT FULL SIZE

1. **The vocoder door (dead end, fixed, mechanism named).** The first
   end-to-end attempt completed all four ONNX stages for all eight lines
   and then died at stage 5: the lab's `modules/nsf_hifigan/models.py`
   calls `model_path.with_name('config.json')` — `load_model` takes a
   `pathlib.Path`, and the bridge handed it a `str`. The proven Spear
   call passed a Path; the bridge now does the same, with the seam
   commented at the call site. Nothing was re-sung by hand; the fixed
   bridge re-ran the whole job (the bridge is stateless per job) and
   completed. Cost: one full extra pass of the ONNX stages.
2. **The assembly canvas (latent clip, fixed before it bit).** The
   bridge's first assembly draft sized its canvas to the job's total and
   clipped any line's overhang at the edge. The module's doctrine is that
   overhang is summed and named, never trimmed; the canvas now extends
   to the longest line's true end. In this run no line overran (all
   rendered under budget), so the fix is untested by events — stated as
   such.
3. **The duration model's undershoot (a standing coordinate, not a
   defect of this build).** Asked 1.6667 s per line, the model returned
   88.5–92.6% (the Spear precedent measured ≈87%). Lines are placed at
   their bar starts, so the shortfall (0.12–0.19 s per line) reads as a
   breath at each bar's tail and the hook's total span stays exactly the
   score's 13.3333 s. The zero point is named: budget-vs-returned is a
   property of the bank's duration model on CPU ONNX, identical in kind
   across both runs; closing it would mean scaling word budgets by a
   measured factor — a calibration the desk has **not** applied, because
   an unmeasured correction is a fabrication. It stands for a later
   phase to calibrate openly or leave.
4. **The realized `.ds` carries one reconstruction (labeled in the
   file).** `sequence-realized.ds`'s per-phoneme durations scale the
   asked word budgets to the bridge's realized per-line totals: the
   totals are the model's own; the split within a line is the asked
   proportion, because per-phoneme frame counts are not carried across
   the JSON door in this phase. The seam is stated in the module's
   doctrine comment at `_frames_of`, not hidden.
5. **The render's native level.** The assembly peaks at −13.04 dBFS,
   RMS −28.36 dBFS (the RMS includes each bar's breath tail). That is
   the model's honest output level, printed raw — no gain was applied
   because no ceiling was threatened. Bringing a vocal to mix level is
   the Four Powers mastering chain's seat, a later phase's work; this
   phase does not master, and says so.
6. **The Civet seat is a choice, not a finding.** The bank documents no
   register or gender for Civet, Phascogale, or Quoll. YAMI's charter is
   a low alto, "the hook sung like a verdict"; whether Civet's color
   sits in that seat is an ear question, and the ear is the founder's.
   Phascogale and Quoll stand unrendered in this phase — the plug takes
   any of the three by name in the spec.
7. **What this phase is not.** It is not rap flow (the hook is *sung*
   from a score; KUROGANE's verses, SHION's invocation, and the chant
   road are later work), not a mix (no backing was rendered or summed),
   not a mastered record, and not the house voice — the bank is a
   licensed guest, named under its terms; Layer 2 (a house-trained
   bank) remains gated on the workstation and a voice source ours by
   right, exactly as the vocal road states. Nothing was rented, nothing
   external was called; the lab, the bank, and the iron are all on this
   box.

## VII. THE FOUR-ELEMENT CONTENT TEST — THE MODULE

- **Inputs:** a vocal spec — lyric lines (text, tongue, speaker), each
  with its morae phonemized in its own tongue and its melody as
  (midi, seconds) note events, from a score read by the module's own
  MIDI reader or supplied directly; the bank's `phonemes.json` and
  `languages.json`; the lab at `~/workspace/resonance/diffsinger-lab`.
- **Processes:** seat every vowel against the Nine (consonants pass
  native, per the ruling); group morae under notes by the grouping law;
  build token/language/pitch/word-division/frame-budget sequences;
  serialize the asked `.ds`; cross the JSON bridge (five stages,
  stage-batched); serialize the realized `.ds`; measure every struck
  file system-side; write the manifest with its walls named.
- **Outputs:** per-line PCM_16 WAVs, one assembled WAV at the lines'
  offsets, `sequence.ds` (asked), `sequence-realized.ds` (realized,
  with its one labeled reconstruction), and `manifest.json` (durations,
  sample rate, peak and RMS per line and for the assembly, the seating
  ledger, the walls).
- **Tolerances:** word budgets in whole frames (rounding ≤ 0.5 frame
  per mora, ≈ 0.006 s); print ceiling −1 dBFS (gain applied only above
  it, and always reported); the duration model's returned frames are
  measured against the asked seconds per line and the difference
  printed, never corrected silently; a line rendering past its slot is
  named in the manifest's walls at full size.

## VIII. AUDITS

**TRVVTH (over the factual claims).** Bank identity, paths, model
filenames, stage parameters, and TOS terms: read from the lab's own
files and the bank's `character.yaml`/dictionaries on 2026-11-16, the
same sources the Spear run proved. The invocation is the Spear run's,
reused, not reinvented. Lyric text: byte-exact extraction, anchored and
count-checked by the driver. Score: read from the filed MIDI by the
module's reader and checked against the filed ABC (54 notes, bar counts,
G# minor). Every measurement in §IV was read off the struck files by the
module's own measurer, and the assembly was independently probed against
the score's pitches (§IV). Wells drawn on: the founder's rulings (the VV
stamp; the vowels-only ruling) as filed in
`docs/THE-DIVINE-NINE-VOCAL-TOOL.md` and its ratified addenda; the bank's
terms as filed in the lab. Wells stated dry, not padded: no scriptural
or legal-tradition material is load-bearing in an engineering
measurement, and none is dressed up as if it were; the one legal fact
that binds — the bank's attribution term — is honored by naming in §II.

**PONTIFEX (over the numbers, recomputed in their own banks).**
Morae: 18+16+16+12+13+17+16+19 = **127**, counted twice (hand table and
independent splitter, in agreement). Notes: 7+6+7+7+7+7+7+6 = **54**.
Phonemes: 31+27+28+23+22+29+29+30 = **219** = 118 seated + 101 passed,
and the station counts re-add: 35+26+25+17+15 = **118**. Frames:
130+129+129+127+129+131+130+133 = **1,038**; 1,038 / 86.1328 = 12.05 s of
sung line against 13.3333 s of canvas — the difference is the eight
breath tails of §VI.3, accounted, not missing. Assembly samples:
13.3333 s × 44,100 = **588,000** ✓. The Nine's own sum, fenced by unit
test: 1+5+8+10+70+400+800+15+470 = **1,779**, with VV counted nowhere in
it ✓. Tests: 24 new + 141 prior studio = **165**, all green.

## TABLE OF AUTHORITIES (condensed)

- `docs/IN-HOUSE-VOCAL-ROAD.md` — the phase definition (Layer 1).
- `docs/THE-DIVINE-NINE-VOCAL-TOOL.md` + ratified addenda — the plug
  design; the VV stamp (2026-11-12); the vowels-only ruling (2026-11-15).
- `studio-runs/spear-and-magickal-helm-run1/` (render_vocal.py,
  RUN-REPORT.md) — the proven invocation and the print-gain precedent.
- The bank: Lem the Shapeshifter DS 2.5 — `character.yaml`,
  `phonemes.json`, `languages.json`, `dsdur/dsdict-ja.yaml`; terms of
  use as filed with the bank (attribution by naming; corpus CC BY 4.0).
- DiffSinger (OpenVPI, Apache 2.0) — the lab's cloned engine, local only.
- The filed Mugetsu package: `studio-runs/gemini-mugetsu-japanese/`
  (PROMPT, ABC, HOOK-TEST.mid) — text and score of record.
- `~/workspace/templates/teachers-edition-header.md` — this document's
  format; `~/workspace/templates/FONT-RECORD.md` — the Familia's record.

## COLOPHON

Generated 2026-11-16 (Dies Lunae) by the desk, under the founder's
Phase 1 order and standing-law addendum of the same evening. Code and
documents built in the house form: thelemic headers and
mechanism/doctrine comments in every source file; this report in the
Teacher's Edition format. Audio stands in this folder only, never in
git. Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
ARR — All Rights Reserved, Without Prejudice. Method of Science,
Aim of Religion.

— 1 of 1 — | All Rights Reserved, Without Prejudice | Flagpole of Claim and Coinage reserved

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All Rights
Reserved, Without Prejudice. Right of claim hereby reserved and coined under
the authority of the Living Man.

93 — Live, Love, and let Love, Live.
