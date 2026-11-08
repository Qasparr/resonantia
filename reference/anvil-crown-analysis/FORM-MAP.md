<!--
93
TRANSCRIPTION-ANALYSIS — phase 1 (analysis only). Every figure in this
document was MEASURED from the audio by analyze_anvil_crown.py
(numpy + soundfile). Interpretations are tier-marked as such. No lyric
is transcribed here; no note or chord is fabricated. Where the bench
could not see, the bench says so, in the open.
-->

# THE ANVIL AND CROWN — Form Map, Key, Chords, Melody Sketch

### A Scientific Illuminist treatment of a Gemini-only recording

**Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice)**
VIII day of November, Dies Solis, Sol in Scorpio, Anno V:xii e.n. (2026 e.v.)

**Classification:** Enterprise • Educational • Research & Development
**Method of Science, Aim of Religion**

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All
Rights Reserved, Without Prejudice. Right of claim hereby reserved and
coined under the authority of the Living Man.

---

## 0. Tier and confidence marks used in this document

- **MEASURED** — read off the audio by the bench; reproducible by
  re-running `analyze_anvil_crown.py`.
- **INTERPRETATION** — a desk judgement laid over measurements; the
  measurements are printed beside it so the judgement can be audited.
- **Confidence** — HIGH: several independent features agree.
  MEDIUM: the lead feature is clear, one alternative stands.
  LOW: the evidence is thin and the label is a placeholder with its
  seams showing.

## 1. The grid (MEASURED, from the standing bench)

| Quantity | Value |
|---|---|
| Duration | 158.145 s |
| Tempo (bench, flat in all five 30-s windows) | 69.8 BPM |
| Beat | 0.8596 s |
| Bar (4/4) | 3.4384 s |
| Bars in file | 46 (bar 46 is a partial decay tail, −78 dB mean) |
| Downbeat phase estimate | 0.57 s into the file — **LOW-MEDIUM** confidence |

Zero point, stated per the house rule: the phase search maximises
onset-flux alignment and lands at 0.57 s, but a grid shifted uniformly
by that amount fits the same evidence; bar numbers below are counted
on the phase grid. A second tactus reading also stands open: at
double time, 139.6 BPM, the file is 92 bars and every "bar" below is
two bars. The 69.8 grid is used because it is the bench-measured
pulse; the ambiguity is recorded, not resolved by preference.

## 2. Form — measured segments

Boundaries were found by a novelty function (spectral flux + chroma
change), peak-picked, then **snapped to the bar grid** — an engraving
skeleton lives on the grid. Snap distances ran 0.04–1.67 s (median
≈0.85 s); boundaries with snap > 1.4 s (at bars 8, 15, 21, 22, 35) are
SOFT and carry LOW confidence as section seams. One candidate boundary
(34.95 s, inside bar 11) was dissolved by the merge pass (same level,
same harmony fingerprint across it) and is recorded here, marked —
not vanished.

| # | Bars | Seconds | Mean dB | Character (MEASURED features) |
|---|---|---|---|---|
| S0 | 1–2 | 0.00–7.45 | −25.7 | Quietest music; voiced density 0.46, low centroid (2.5 kHz) — speech-led |
| S1 | 3–5 | 7.45–17.76 | −21.5 | Steepest build in the song, +1.04 dB/s; speech still dense (0.37) |
| S2 | 6–7 | 17.76–24.64 | −16.0 | Level steps up ≈5.5 dB — the full track arrives |
| S3 | 8–12 | 24.64–41.83 | −15.6 | Sustained plateau; seam at bar 8 is the softest in the song (LOW) |
| S4 | 13–14 | 41.83–48.71 | −13.9 | Loudest point so far; highest chroma stability (0.743) |
| S5 | 15–18 | 48.71–62.46 | −15.6 | Plateau; fingerprint recurs with S3 (+0.81) |
| S6 | 19–20 | 62.46–69.34 | −15.5 | Plateau; recurs with S10 (+0.88) |
| S7 | 21–22 | 69.34–76.21 | −14.1 | Level steps up again |
| S8 | 23–28 | 76.21–96.85 | −14.7 | Long plateau, 6 bars; recurs with S12 at +0.92 — the strongest recurrence in the song |
| S9 | 29–30 | 96.85–103.72 | −16.9 | The dip: quietest full-music segment, rising slope (+0.77 dB/s) |
| S10 | 31–32 | 103.72–110.60 | −14.8 | Plateau restored |
| S11 | 33–34 | 110.60–117.48 | −14.3 | Plateau, bright (centroid 4.2 kHz) |
| S12 | 35–38 | 117.48–131.23 | −14.0 | Final plateau, 4 bars; S8's twin (+0.92) |
| S13 | 39–42 | 131.23–144.98 | −23.2 | Level collapses; voiced density 0.47 — the highest in the song: speech-led again |
| S14 | 43–46 | 144.98–158.15 | −39.3 | Decay tail, slope −4.56 dB/s, into silence |

## 3. Form — the reading (INTERPRETATION)

| Bars | Label | Confidence | Grounds |
|---|---|---|---|
| 1–5 | **INTRO** — announcer's frame over an assembling bed | HIGH | Speech-led features + the song's steepest build; nothing else in the track looks like this |
| 6–12 | **VERSE 1** | MEDIUM | First full-level plateau; the bar-8 seam may be a fill, not a break (LOW as a seam) |
| 13–14 | **HOOK 1** (short form) | MEDIUM | Loudest-so-far peak + highest harmonic stability |
| 15–18 | **VERSE 2** | MEDIUM-HIGH | Level falls back; fingerprint recurs with Verse 1 (+0.81) |
| 19–22 | **VERSE 3 → HOOK 2** | LOW-MEDIUM | Two 2-bar units rising −15.5 → −14.1; the split of function inside them is the bench's weakest call |
| 23–28 | **REFRAIN PLATEAU A** | MEDIUM | Long, loud, stable; function (big hook vs. verse) not separable from its twin below |
| 29–30 | **BREAKDOWN / DIP** | MEDIUM | Only full-music dip in the song, rising out of itself |
| 31–34 | **FINAL VERSE → HOOK pair** | LOW-MEDIUM | Two plateau units at restored level |
| 35–38 | **REFRAIN PLATEAU B** | MEDIUM | S8's twin (+0.92): same material, closing position |
| 39–46 | **OUTRO** — announcer's verdict over a dying bed, then decay | HIGH | Speech-led features return; the tail falls 16 dB across four bars to silence |

**The standing ambiguity, named plainly:** in the mid-song plateaus
(bars 23–28 and 35–38) the bench cannot separate *hook* from *verse*
— Lyria writes both at full energy, and the features that usually
divide them (level, stability, recurrence) point both ways. The
founder's lyric sheet, when it comes from him, settles those two
labels in one stroke; until then they stand as REFRAIN PLATEAU,
marked unresolved. No label in this section outranks the audio, and
none outranks his account of his own song.

## 4. Key (MEASURED chroma, INTERPRETATION of centre)

Krumhansl–Schmuckler profile correlation against the duration-weighted
global chroma (peak-picked chroma, v2 — see §6 for the v1 failure):

| Candidate | Correlation |
|---|---|
| **A major** | **0.669** |
| C# minor | 0.587 |
| F# minor | 0.369 |

**Reading: A major — MEDIUM confidence.** The margin over C# minor is
0.081. The zero point is structural: A major, C# minor and F# minor
share one pitch collection (three sharps), so chroma alone can rank
them but cannot crown one beyond dispute. The corroborating witness
agrees with the leader: the melody sketch's pitch census is headed by
A (46 notes), E (33+), C# (30), G# (29), F# (23) — the tonic triad
A–C#–E is the song's centre of gravity, and A is the chord the bench
reads in 21 of 46 bars. A minor-key hearing (F#m or C#m) is not
excluded by this evidence; it is out-voted, not disproven.

## 5. Chord progression (MEASURED per bar; full table in chords.csv)

Distribution over 46 bars: **A ×21 · C#m ×5 · UNCLEAR ×17 · Dm ×1 ·
A#m ×1 · C# ×1.**

**The progression, stated at the strength the evidence carries: an
A-major vamp (I) with C# minor (vi) alternation, MEDIUM confidence at
segment level, LOW at most individual bars.** The alternation is
visible where the evidence is least thin: bars 1–2 read C#m → A;
bars 10–12 read C#m → A → C#m. After bar 12 the bench reads long A
plateaus, broken by bars whose margins fall under the gate and stand
as UNCLEAR — 17 of them, concentrated where the vocal rides forward
over a thin bed and the triad templates cannot separate. Those bars
are labelled UNCLEAR in `chords.csv`, in the open; they were not
filled in by guessing the vamp continues, even though it very
probably does.

Single-bar outliers Dm (bar 31), A#m (bar 36) and C# (bar 44) all sit
at LOW confidence and small margins; they are recorded in the CSV and
flagged here as **probable template noise**, marked — not vanished,
and not promoted into a "progression" they cannot support.

## 6. Method failures found on the way (marked, per house law)

1. **Chroma v1 measured nothing.** Summing log-magnitudes over all
   FFT bins let the broadband floor vote in every pitch class at
   once; the chroma came out near-uniform, every bar failed its gate
   (correlation ≈0.54, margins ≈0.01), and the key read tilted to a
   D minor that the melody census contradicts. Fixed in v2 by
   peak-picked bins in an 80–2500 Hz band; the v2 numbers are the
   ones in this document. The v1 outputs were overwritten by the v2
   run and the failure is recorded here and in the script's comments.
2. **Segmentation v1 shattered the song** (23 fragments, one per
   bar-level fill) and its stability/recurrence features were
   degenerate (≈1.00 everywhere — frame-overlap cosine and raw cosine
   on non-negative vectors). Fixed with a 6.8 s minimum spacing, 1-s
   lag stability, Pearson recurrence, and a merge pass.

## 7. Melody sketch (summary; full data in melody-sketch.json)

- 325 notes from the gated autocorrelation track; sketch coverage
  26.4% of frames passed the voicing + vocal-likelihood gates.
- Range MIDI 41–71 (F2–B4); mean note confidence 0.58; 10 notes
  flagged `octave_suspect`, flagged — not corrected.
- **Weakest zone, named:** the bars 13–14 hook stack, where the track
  clings to an A#/B cluster at confidence ≈0.5 — most consistent with
  the tracker riding a harmony partial in the vocal stack, not the
  lead. A# is foreign to the A-major collection; treat every note in
  dense stacks as suspect until the engraving pass audits it by ear
  and hand.
- **Speech zones are not melody:** the intro and outro carry 53 and
  59 sketch "notes" respectively — the tracker's quantisation of the
  announcer's intonation. They are in the JSON because the machine
  produced them and the record keeps what the machine did; the
  honesty header brands them, and no engraver should set them.

## 8. What would raise each tier

- **Form labels (hook vs. verse in the plateaus):** the founder's
  lyric sheet — his dictation is the settling evidence.
- **Chord bars now UNCLEAR:** stems, or a bass-isolated re-run at
  longer windows; a phase-2 production may attempt both.
- **Melody:** a phase-2 pass with a dedicated vocal source (mid/side
  difference modelling) plus hand audit; the sketch is the floor,
  not the ceiling.

---

Colophon: analysis generated on this desk from the reference MP3 of
record; script, CSV, JSON and this map live together in
`resonance/reference/anvil-crown-analysis/`. Nothing herein is a
finished transcription. The engraving toolchain proof, if produced,
rides in the same directory and says so on its face.

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All
Rights Reserved, Without Prejudice.

93 — Live, Love, and let Love, Live.
