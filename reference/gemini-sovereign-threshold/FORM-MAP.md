<!--
93
TRANSCRIPTION-ANALYSIS — phase 1 (analysis only). Every figure in this
document was MEASURED from the audio by analyze_sovereign.py (the
Sphinx intake bench, carried over whole, with the 49-bar audit, the
Sigma sweep probe and the arpeggio assessment added for this brief).
Interpretations are tier-marked as such. No lyric is transcribed here;
no note or chord is fabricated. Where the bench could not see, the
bench says so, in the open. Grid B's full machine record stands in
grid-b-audit.json and chords-grid-b.csv beside this file.
-->

# SOVEREIGN AT THE THRESHOLD — Form Map, Key, Chords, Melody Sketch

### A Scientific Illuminist treatment of a Gemini-only recording

**Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice)**
X day of November, Dies Martis, Sol in Scorpio, Anno V:xii e.n. (2026 e.v.)

**Classification:** Enterprise • Educational • Research & Development
**Method of Science, Aim of Religion**

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All
Rights Reserved, Without Prejudice. Right of claim hereby reserved and
coined under the authority of the Living Man.

---

## 0. Tier and confidence marks used in this document

- **MEASURED** — read off the audio by the bench; reproducible by
  re-running `analyze_sovereign.py` (grid B by its override).
- **INTERPRETATION** — a desk judgement laid over measurements; the
  measurements are printed beside it so the judgement can be audited.
- **Confidence** — HIGH: several independent features agree.
  MEDIUM: the lead feature is clear, one alternative stands.
  LOW: the evidence is thin and the label is a placeholder with its
  seams showing.

## 1. The grid — a named boundary, two clocks (MEASURED)

| Quantity | Grid A (bench of record) | Grid B (alternative clock) |
|---|---|---|
| Tempo | **90.07 BPM** (estimator headline) | **120.19 BPM** (first-pass dominant) |
| Beat | 0.6663 s | 0.4992 s |
| Bar (4/4) | 2.6646 s | 1.9968 s |
| Downbeat phase | 0.075 s | 0.26 s |
| Bars in file | 45 | 60 |
| Boundary snaps | 0.10–1.16 s | 0.21–0.98 s |

**This file does not keep one clock the way its predecessor did.**
The flux estimator's candidate family is {44.94 (ac 0.737),
60.09 (0.698), 120.19 (0.669), 90.07 (0.666)} — one pulse train
read at the ratios 3:4:6:8 (44.94 × 4/3 ≈ 60.09, × 2 ≈ 90.07,
× 8/3 ≈ 120.19). The estimator's log-prior crowns 90.07 as its
headline, but its own dominant periodicity is 44.94 (the 90 line's
half), and its 30-s windows split down the middle: **90.07 /
120.10 / 90.08 / 120.03 — spread 30.03 BPM**, against the Sphinx
strike's 0.11. The desk's first-pass instrument (RMS-block
envelope) crowns 120.19 outright (strength 0.558). Raw flux
autocorrelation at the contested points: 44.94 → 0.737,
90.07 → 0.653, 120.19 → 0.669, **144 → 0.234** (first-pass ac at
144: 0.056 — no instrument finds the sheet's old 144 here either;
this brief, unlike the sheet, ordered no number, only bounce).

Grid A stands as the bench of record because it is the house
estimator's headline — the same rule that seated the Sphinx grid.
Grid B is carried in full (`grid-b-audit.json`) because §3 shows
the brief's form fits it far more closely. **The zero point is
the 3:4 ratio between the two clocks, and it is reported, not
resolved by preference.** Bar numbers below are grid A's unless
marked (B).

## 2. Form — measured segments (grid A; seconds are grid-free)

Boundaries by the novelty function, snapped to grid A; the merge
pass dissolved nothing on either grid. The last three rows are
read with the RMS-contour instrument (§6.4), not the segmenter's
levels alone.

| # | Bars (A) | Seconds | Mean dB | Character (MEASURED features) |
|---|---|---|---|---|
| S0 | 1–3 | 0.00–8.07 | −23.8 | Quietest music; low centroid (1.35 kHz); tracker lock 0.59 — the song's densest; recurs with S2 (+0.843) |
| S1 | 4–8 | 8.07–21.39 | −15.4 | Build slope +0.49 dB/s; recurs with S3 (+0.896) |
| S2 | 9–19 | 21.39–50.70 | −15.3 | Long span; gentle fall (−0.28 dB/s); highest verse chroma stability (0.709) |
| S3 | 20–33 | 50.70–88.01 | −14.2 | **Loudest span in the song**; flat slope; recurs with S1 (+0.896) |
| S4 | 34–37 | 88.01–98.67 | −37.4 | The fall: slope −8.00 dB/s, level collapses to the floor |
| S5 | 38–41 | 98.67–109.32 | −150.0 | **Exact digital silence** (verified sample-for-sample: 100% zeros, max abs 0.0) |
| S6 | 42–45 | 109.32–119.56 | −69.8 | The whisper: pitched content returns at −36…−63 dB (peaks to −23.6 dBFS); recurs with S4 (+0.662); file ends in zeros within the last second |

Grid B segments, for the audit in §3: 1–4 · 5–11 · 12–25 · 26–44 ·
45–50 (the fall, −51.0, slope −11.48) · 51–55 (silence) · 56–60
(whisper, −63.2).

**Programme shape, in seconds, owing nothing to either grid:**
full level 0–≈95 s; the fall runs ≈95–98.7 s; exact zeros
≈99.0–109.9 s (10.9 s of dead air inside the file); a whisper
reprise ≈110–118.5 s; zeros again to the file's end at 119.56 s.

## 3. The 49-bar audit (MEASURED coordinates; the reading tiered)

The brief ordered: intro 1–3 · Verse I 4–23 · refrain 24–26 ·
Verse II 27–46 · outro 47–49. Distances from each ordered
interior boundary to the nearest measured segment boundary:

| Ordered boundary | Grid A distance | Grid B distance |
|---|---|---|
| Start of bar 4 (Verse I in) | **0.00 bars** (8.07 s, exact) | 1.00 bar (8.25 s) |
| Start of bar 24 (refrain in) | 4.00 bars (nearest seam 50.70 s) | 2.00 bars (nearest seam 50.18 s) |
| Start of bar 27 (Verse II in) | 7.00 bars (nearest seam 50.70 s) | 1.00 bar (nearest seam 50.18 s) |
| Start of bar 47 (outro in) | 1.16 bars (nearest seam 119.56 s, the file's end) | 2.00 bars (nearest seam 88.12 s) |
| Total bars / 49 ordered | 45 in file; ≈37 at full level | 60 in file; programme span ≈49 (below) |

**The total-span coordinate (grid B):** 49 bars at 1.9968 s from
the 0.26 s phase end at **98.11 s**; the measured programme
reaches the floor at ≈98.7 s (segment boundary 98.67 on grid A,
zeros from ≈99.0). The ordered song-length and the performed
programme-length agree on grid B to within ≈0.6 s — and then the
file keeps going: 10.9 s of zeros and an 8.5 s whisper the brief
never ordered in that shape.

**The Verse I/II seam — located as a boundary for the first
time** (the Sphinx intake left it unlocated). The seam at
**50.70 s** (raw novelty peak 50.81) divides the two long,
mutually rhyming verse spans (S1+S2 before it, S3 after it;
S1↔S3 recurrence +0.896). Its brief-relative coordinate is
grid-bound: start of bar 20 on grid A (four bars before the
ordered refrain) — start of **bar 26 on grid B (inside the
ordered refrain's last bar, one bar before Verse II's ordered
start)**. INTERPRETATION, MEDIUM as a seam, LOW as a bar number:
the model's internal verse division stands at 50.7 s; on the
clock that fits the total span, it falls where the brief put the
refrain's tail — the refrain and the seam occupy the same ground.

**The refrain (ordered bars 24–26, a chanted plateau line): NO
measured segment corresponds to it on either grid.** On grid A,
bars 24–26 lie inside S3, the loudest span (level rank 1 of 7),
which declares no internal boundary there. On grid B, bars 24–26
straddle the 25/26 seam — the seam above. No 3-bar plateau
recurs anywhere in this performance (the Sphinx strike's hook
returned three times; this one's recurrences pair whole verse
spans with each other). INTERPRETATION, MEDIUM: if the refrain
was sung as ordered, it is woven into the loudest span without a
joint the bench can find — or the seam at 50.7 s *is* its exit.
The founder's ASR of record carries a thrice-repeated chant-like
figure in the latter half ("the sound, like you're shutting the
leather…"), which this bench cannot place in time and does not
promote into a location.

**Verse bulk (grid B):** the three verse spans total exactly
40 bars (7 + 14 + 19) against the ordered 20 + 20 — the bulk is
right on grid B and the division is not (7/14/19 in place of two
clean twenties, with the intro at 4 bars against 3 ordered).

## 4. Key (MEASURED chroma, INTERPRETATION of centre)

Krumhansl–Schmuckler against the duration-weighted global chroma:

| Candidate | Correlation |
|---|---|
| **D minor** | **0.867** |
| F major | 0.650 |
| A minor | 0.644 |

Margin 0.217 — the widest key margin in either intake. The
global chroma heads A (0.145) and D (0.137) with F third (0.109);
the melody census heads D (41 of 156). **Centre: D — HIGH.**
Mode: the bench's clearest single witness is the whisper
(§5) — **D minor, MEDIUM-HIGH**, against the brief's ordered
**F minor**. F is D minor's relative major pole and the ordered
centre's presence in the chroma is real (third head, F ×2 clear
bars, F at bar 44) — the performance may be heard as orbiting
the F/D axis from the D side. The brief's coordinate stands
unmet as ordered: no bench in this intake crowns F minor.

## 5. Chord progression (MEASURED per bar; full tables in chords.csv / chords-grid-b.csv)

Distribution, grid A (45 bars): **UNCLEAR ×22 · Dm ×6 · D ×5 ·
A# ×5 · D5 ×4 · F ×2 · Am ×1.** Grid B (60 bars): **Dm ×19 ·
UNCLEAR ×25 · D5 ×5 · A# ×5 · D ×3 · F ×0** in clear labels,
with single A#5/A#m/Am.

**The progression, at the strength the evidence carries: a
D-minor vamp** — Dm and its bare fifth D5 alternating, A#
(B♭) as the recurring VI pole, F appearing as the III. On grid
A the clear bars cluster at the edges (bars 1–4: D, D5, A#, Dm;
bar 19: A# at HIGH, the grid's best verse bar); the verse
interiors fall under the gate (22 of 45 UNCLEAR) where the rap
rides forward, exactly as in the Sphinx intake.

**The whisper is the bench's best harmonic witness.** Bars
42–44 (grid A), at −84…−41 dB mean levels, read **D5 (margin
0.089, HIGH) · A# (0.106, HIGH) · F (0.114, HIGH)** — the three
widest template margins in the file, wider than any bar of the
full-level programme. With nothing competing, the template bench
hears the cadence plainly: i–VI–III colour over the D centre,
corroborating §4 from the quiet end of the song.

## 6. Method notes and failures found on the way (marked, per house law)

1. **The tempo zero point (§1) is a boundary between rungs of
   one pulse family, not an error in any instrument.** All
   readings stand in `analysis-stats.json` with their raw
   autocorrelations. What neither grid survives is the window
   test: this performance's pulse is not flat on any single
   rung (the Sphinx strike's signature virtue is absent here).
2. **The segmenter swallows the silence's edges.** Novelty
   sleeps on zeros; the silence's true span (≈99.0–109.9 s,
   exact) and the whisper's (≈110–118.5 s) come from the
   per-second RMS probe and the exact-zero test, printed in
   §2 — grid-free instruments, labelled as such.
3. **The arpeggio bed-census artefact.** The ungated bed track's
   pitch-class census is headed B (159 of 426) — and B4
   (493.9 Hz) sits at the f0 tracker's 500 Hz ceiling. A census
   pinned to the instrument's ceiling is the tracker registering
   bright broadband content at its limit, not a harmony. It is
   one of the reasons §7 of the REFERENCE reads the arpeggio as
   it does; the artefact is marked here so the census is never
   quoted without it.
4. **Voiced density measures trackability, not presence** —
   inherited from the Sphinx intake, unchanged: read §2's locks
   (intro 0.59, whisper 0.08–0.29) as where pitch stood still
   long enough to be tracked, never as where the vocal is absent.
5. **The merge pass dissolved nothing on either grid** —
   `boundaries_merged_away` stands empty in both records; the
   six novelty seams are all real changes of level or fingerprint.

## 7. Melody sketch (summary; full data in melody-sketch.json)

- 156 notes from the gated autocorrelation track; coverage
  18.4% of frames (Sphinx: 14.0% — a marginally more trackable
  performance). Range MIDI 41–71 (F2–B4); mean confidence 0.590;
  **13 notes flagged `octave_suspect`**, flagged — not corrected.
- Pitch census: D 41 · A 24 · F 22 · A# 16 · B 16 · D# 10 · E 8 ·
  C 6 · F# 5 · G 4 · G# 3 · C# 1. The head corroborates §4's D
  centre through the voice itself. B (16) in a *vocal* sketch is
  read as blue-note/intonation registration (the Sphinx clause);
  it is the **bed** census's B-dominance (§6.3) that is the
  artefact, and the two are not to be confused.
- Rapped passages are not melody: the sketch quantises the
  flow's intonation. Its reliable zones are the intro and the
  whisper, where the tracker locks; the verses are its floor,
  not its portrait.

## 8. What would raise each tier

- **The grid (90.07 vs 120.19):** a phase-2 onset-by-onset audit
  of the kick/hat pattern against both rungs, or the founder's
  word on the bounce he hears. The 3:4 boundary is named either
  way.
- **The refrain's seat and function:** the founder's dictation
  on his own song — the settling evidence, as with the Sphinx.
- **The 22–25 UNCLEAR bars:** stems, or a bass-isolated re-run;
  the whisper suggests the vamp is there to be heard once the
  vocal is not on top of it.
- **The arpeggio:** a phase-2 pass on a high-band-isolated track
  (the violin's register, above the voice) is the road that
  could raise §7's NOT ESTABLISHED to a finding either way.
- **Line-accurate form map:** lyric timing against the sheet —
  phase 2, the machine transcript standing as draft scaffold
  only, per the Anvil ruling.

---

Colophon: analysis generated on this desk from the founder's
uploaded render of record; script, CSVs, JSONs and this map live
together in `resonance/reference/gemini-sovereign-threshold/`,
with the intake profile in `REFERENCE-GEMINI-SOVEREIGN.md` and
the master and its confessions in `manifest.json`. Nothing herein
is a finished transcription. The audio stays local; this document
may travel.

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All
Rights Reserved, Without Prejudice.

93 — Live, Love, and let Love, Live.
