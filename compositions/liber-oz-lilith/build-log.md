# Liber Oz Lilith — Build Log (ultra-verbose)

2026-10-25, from the order at 23:24 EDT and its three amendments
(23:25 invocation frame; 23:27 banishing dictation; 23:29 Teacher's
Edition with the art and the ABC in the notes). Every step below:
hypothesis → method → observation → result, dead ends kept.

## 0. Source discipline FIRST (Amendment 1 is binding: establish, then weave)

**Hypothesis:** the workspace might hold some text of IAO131's
Supreme State Invocation Rite (the Four L's research files were the
named candidate), or at least a filed quotation budget.
**Method:** case-insensitive searches for "supreme state" and
"iao131" across `~/workspace` (md/txt/py/json/yaml), then targeted
searches for "Supreme" and "Invocation" in `~/MEMORY.md`, `~/memory/`,
`~/workspace/goals/`, `~/workspace/pontifex/research/`,
`~/workspace/liberd/libers/`; read `~/memory/people/iao131.md` and
the Four L's build script (`pontifex/research/four-l-marriage/
build-fourl-editions.py`), which embeds the quotations actually used.
**Observation:** no text of the rite exists anywhere in the
workspace. The "Supreme" hits are unrelated (Supreme Elemental Kings
in the 777 tables; Crowley-corpus material). The only IAO131 material
lawfully on hand is the Four L's essays material (fetched from
iao131.com 2026-10-18 at his order, filed in
`pontifex/research/four-l-marriage/`): summaries in our words + brief
quotes. His book *Fresh Fever From the Skies* is not on hand (the
IAO131 goal file confirms: requested through his own channel; the
audit waits for the PDF he requests himself; no third-door copies).
**Result:** the rite contributes **zero quotable words**. The
composition's invocation layer is built to the rite's framing
function (invocation opens; the working follows), the rite is
credited by name, exactly one already-on-hand IAO131 quotation is
carried (§II of the edition), and the rite's full-text layer is
marked **OPEN** in the document. Nothing of the rite was fabricated
or reconstructed — including from model memory, which was not used
as a source for it in any form.

**Quote accounting (counted from the filed build script):**
IAO131's own prose quoted in the Four L's study: "strength" line —
"the establishment of Life, Liberty, Love, and Light in the hearts
of all men." = **14 words**; "thelemites" line — "we band together
into communities in order to preserve and promulgate the Law of
Life, Light, Love, and Liberty." = **19 words**; total **33 ≈ the
filed ~32**. (The other two quotes in that study are the Gnostic
Mass Creed and Liber DCCCXXXVII *via* him — not his prose.) Cap:
50 total. This artifact re-quotes only the 14-word "strength" line,
once: cumulative 47/50 by per-artifact accounting, 33/50 distinct.
The composition document asserts this accounting; the test suite
verifies the quote occurs exactly once in the edition and recounts
its words.

**Amendment 2 source check:** "Mother tongue"/"Father tongue"
appear nowhere in his filed corpus (searched). Per the amendment's
own discipline, the three tongues are carried in the document
exactly under his names — Mother tongue, Father tongue, Child —
with no historical language identified or invented for any of them.
His banishing dictation and the fires sentence are quoted verbatim
in §IV.6, attributed and dated (his text; no budget applies).

## 1. Recon of the engines (reuse, never re-implement)

**Method:** read the repo README/module map; `binaural/generator.py`
(binaural_beat: L = carrier − beat/2, R = carrier + beat/2);
`diagnostics/verify.py` (verify_binaural: Hann-windowed rFFT,
parabolic peak, tol 0.5 Hz, verdict dict, failures reported never
raised); `core/notes.py` (SOLFEGGIO nine; freq_to_midi/midi_to_freq);
`abc/parser.py` (base parser: single voice, no chords — its own
docstring refuses them); `abc/abc21.py` (parse_abc21, Tune21,
tune_voice, render_voice: multi-voice, chords, each voice an
independent timeline from beat 0); `abc/render.py` (note_events,
render_events, _oscillator_voice sine+2nd harmonic, ADSR-ish);
`core/io.py` (write_wav/read_wav/wav_info); `core/buffers.py`
(mix gains, normalize, fades); `synth/arpeggiator.py` (considered:
it renders MIDI-chord arpeggios through a pluck voice — the wrong
instrument here, since the ground must be exact-Hz binaural carriers
and the arpeggio figure must live in the *score*; not used, and the
reason is recorded rather than the tool forced).
**Observation:** everything needed exists: the ABC 2.1 machinery for
a two-voice score, the binaural generator for the ground, the FFT
verifier for forensics, the Solfeggio table for the ladder cross-check.
**Result:** architecture = score (abc21, two voices) + ground
(binaural_beat per bar) + voices (render_events per parsed voice) +
forensics (verify_binaural per segment group).

## 2. Text and counts

**Method:** extract THE TEXT's `**N.**` lines from
`liberd/libers/liber-oz-lilith-revision/Liber_OZ_Lilith_Revision.md`
(regex, mechanical rule), strip bracketed apparatus and v.25's
citation tail.
**Observation:** 36 verses (0–35) ✓; **2,192 letters** total;
152 verse bars at 16 sixteenths/bar. At Q:1/4=120 (bar = 2.000 s),
with the 10 frame bars: 162 bars = **324.0 s**, WAV ≈ 57 MB —
inside GitHub's per-file limit with room. (An earlier rough
eye-estimate of ~4,300 letters would have forced a tempo compromise;
the counted figure removed the problem. Count, don't guess.)

## 3. ABC syntax probes (before generating 19 KB of score)

**Method:** three probe tunes through parse_abc21.
**Observations (two dead ends, both instructive):**
(1) Chord durations after the bracket (`[GCE]16`) FAIL — "stray
length"; durations belong **inside** the brackets per note
(`[G16C16E16]`). (2) `G16`, `z16`, `W:` underlay lines, `%`
comments, `V:` switches, `^G'16` all parse as expected. Voice
timelines are independent from beat 0, so each voice is written as
one complete 648-beat stream.

## 4. The construction (composition.py)

Choices, each with its reasoning printed in the module and in the
edition §IV: ladder = the mandala six (asserted ⊆ engine SOLFEGGIO);
shadows via the engine's freq_to_midi (396→67, 417→68, 528→72,
639→75, 741→78, 852→80) with cent deviations printed in the edition
(FA and LA shadows stand −46.0¢ and −44.0¢ — near quarter-tones,
disclosed, never hidden); triads by skip-one stacking {r, r+2, r+4}
mod 6 (two complementary trichords alternate — stated as the
arithmetic it is); verses dealt to chords by floor(v·13/36) (3
verses per chord, chord 13 takes vv. 34–35); letter → degree
(ordinal−1) mod 6 over the chord's triad + octave; FIB16 = Fibonacci
mod 3 as the ground figure; offsets FIB7 by chord; the frame =
6 invocation bars (ground ascends, voice silent, offset 1) + 3
sealing bars (final triad at −12 / 0 / +12, V:1 holds the root per
register) + 1 AM bar (all registers together, V:1 crowns at +12,
carrier back to 396 @ 1 Hz).

## 5. Build + round-trip (build_composition.py)

**First run:** voice 1 exact; voice 2 "beats" assertion failed at
704 vs 648 — a builder bug, not a score bug: summing durations
double-counts chord tones (sealing 3×(3−1)×4 = 24 + AM (9−1)×4 =
32 = exactly the 56 excess). Fixed the invariant to timeline SPAN.
**Second run:** ladder cross-check ✓; ABC written (19,450 chars);
voice 1 round-trips exactly (2,196 notes = 2,192 letters + 3 sealing
+ 1 AM; span 648 beats); voice 2 exact (2,456 notes; span 648);
36 W: underlays == 36 source verses. Ledger: verses 36, letters
2,192, bars 162, seconds 324.0.

## 6. Melody spot-check (independent implementation)

**Method:** a throwaway re-derivation sharing no code with
composition.py (own extraction, own triad/letter functions on the
engine's freq_to_midi), comparing verses 0, 13, 30 note-for-note
against the parsed score.
**Observation:** verse 0 (67 notes, chord 1), verse 13 (98, chord
5), verse 30 (103, chord 11) — **all match exactly**. By eye,
verse 0 opens U·N·D·E·R → degrees 2·1·3·4·5 over {67,72,78} →
F♯5·C5·G5·C6·F♯6, and the score's first five tokens read ^f c g c'
^f'. (The same independent code now lives in the test suite.)

## 7. Render + forensics (render_composition.py)

**Dead end:** first run died printing — `wav_info` returns a tuple
(n_channels, sample_rate, n_frames), not the dict I assumed. Fixed
to the real contract.
**Render:** ground = 162 binaural_beat segments (amp 0.30) laid
bare — no crossfades, by the whole-cycle argument (bar = 2.000 s;
all carriers and sidebands integer Hz; every segment starts and
ends at a zero crossing). Voices from the parsed score via
render_events, gains: ground 1.0, melody 0.14, arpeggio 0.07;
peak-normalized to 0.89. WAV: 324.0 s, 44,100 Hz stereo, peak
0.890 (−1.01 dBFS), 57,153,644 bytes, SHA-256 c5b77307f9983e2a…
**Forensics (verify_binaural, tol ±0.5 Hz, 20 segment groups:
6 invocation bars + 13 chord spans + sealing/AM span):**
ground stem **20/20, worst error 0.000 Hz**; final mix read back
from the shipped WAV **20/20, worst error 0.006 Hz**. Spot values:
invocation UT bar peaks 395.5/396.5 (beat 1.000); chord 13 span
392.0/400.0 (beat 8.000); sealing span 395.5/396.5 (beat 1.000).
All 40 verdicts ship in forensics.json.

## 8. The plates and the Teacher's Edition (Amendment 3)

**Plates:** converted from the Author's filed set
(`~/workspace/your_files/axoneme-mandala/*.webp`) to PNG by lossless
re-encode (PIL): frontispiece 1280×1952, Plate II 2048×1152,
Plate III 2352×1008; provenance + the fidelity audit's three
residual tics ("key"→"Bey", UT's glyph garbled, wheel micro-lettering
impressionistic) written to plates/PROVENANCE.md and repeated in
§VII — disclosed exactly as reported, never smoothed.
**Dead end:** fpdf2 was present at recon (2.8.9) and gone at build
time — the known VM-cycle package wipe; reinstalled with
`pip install --break-system-packages fpdf2 pypdf`, per the standing
note.
**Build:** prose written once as blocks; two emitters (Markdown,
fpdf2 PDF). Every table computed at build time from composition.py's
ledger, segments.json, and forensics.json — chord table's measured
beats cross-asserted against the ledger's carrier/offset per chord,
so a mis-ordered ledger fails the build rather than printing.
**Verification of the edition itself:** PDF = **15 pages**,
14,418,543 bytes (the three lossless plates are 11.2 MB of it);
extracted text shows footers resolved ("— 1 of 15 —" … "— 15 of 15 —",
no literal {nb} anywhere); title block, Flagpole (head and colophon),
Thelemic date, the IAO131 quotation **exactly once** (MD and PDF
alike), the fires dictum once, the OPEN marker present; pages 1–2
rendered to images and eyeballed (title page clean; frontispiece
with caption seated). MD = 43,494 bytes, the full ABC printed whole
in Appendix A of both forms.
**Logo slot:** `~/workspace/templates/doctrine-logo.png` does not
exist (the Architect's selection among his marks was still with his
pen); the edition prints the slot empty and marked [OPEN], per the
format rule — no mark invented in its place.

## 9. Tests and suite

`tests/test_liber_oz_lilith.py` (script-style, house pattern): 23
checks — data tables, offsets, root walk, parse + spans, the three
independent verse derivations, segment accounting (6/152/3/1),
sealing-at-the-seed, per-bar carrier/offset agreement, WAV header
facts, three FFT verifications against the shipped WAV, the
Teacher's-Edition budget/quote/OPEN checks. **All pass.**
Full suite (`for t in tests/test_*.py`): **all 26 files pass**
(api 11 skipped and tags 7 skipped are pre-existing environment
skips — mutagen/FastAPI extras absent — untouched by this work,
which added files only).

## 10. What stands OPEN (printed, not buried)

1. The rite's full-text layer — §II of the edition. Completes when
   the text is lawfully in hand via the Author's channel to IAO131.
2. The Doctrine logo slot in the edition's header — the Architect's
   selection, his pen.
3. Nothing else. Every other quantity in the release was measured,
   and the measurements are in forensics.json.

93 — Live, Love, and let Love, Live.
