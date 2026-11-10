<!--
93
TRANSCRIPTION-ANALYSIS — phase 1 (analysis only). Every figure in this
document was MEASURED from the audio by analyze_sphinx.py (the Anvil
phase-1 bench, carried over whole, with the intake front-end added).
Interpretations are tier-marked as such. No lyric is transcribed here;
no note or chord is fabricated. Where the bench could not see, the
bench says so, in the open.
-->

# SPHINX IN A GOWN — Form Map, Key, Chords, Melody Sketch

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
  re-running `analyze_sphinx.py`.
- **INTERPRETATION** — a desk judgement laid over measurements; the
  measurements are printed beside it so the judgement can be audited.
- **Confidence** — HIGH: several independent features agree.
  MEDIUM: the lead feature is clear, one alternative stands.
  LOW: the evidence is thin and the label is a placeholder with its
  seams showing.

## 1. The grid (MEASURED, house studio estimator)

| Quantity | Value |
|---|---|
| Duration | 125.910 s (programme to ≈118.5 s, then fade) |
| Tempo (house estimator headline) | 99.93 BPM |
| Dominant periodicity (same instrument) | 99.38 BPM |
| Candidates | 99.38 (ac 0.587) · 66.26 (0.574) · 50.17 (0.569) |
| 30-s windows | 99.97 / 99.97 / 99.92 / 99.86 — **spread 0.11 BPM** |
| Beat | 0.6004 s |
| Bar (4/4) | 2.4017 s |
| Bars in file | 53 (bar 53 is a partial fade bar) |
| Downbeat phase estimate | 0.03 s into the file — **LOW-MEDIUM** confidence |

Zero point, stated per the house rule — **the two tempo instruments
of this house disagree on this file, at a named coordinate.** The
desk's first pass (RMS-block envelope, plain autocorrelation) read
dominant periodicity 132.5 BPM; this pass reproduces that reading
by that instrument exactly (132.51, strength 0.5008). The studio
estimator (onset-flux envelope) reads its raw autocorrelation
strongest at 99.93 (0.648), then 99.38 (0.586), 66.26 (0.575),
132.5 (0.555). The relation is arithmetic, not mystery: 132.5 ≈
2 × 66.26 — the first instrument crowns the double-time hat/flow
layer; the second crowns the beat the bars stand on, and its
window series is flat to 0.11 BPM across the whole song, the
benchmark behaviour. The grid above is the flux instrument's; the
99.93/132.5 boundary is recorded, not resolved by preference.
**Both instruments agree that 144 BPM — the sheet's ordered tempo
— carries no clock in this performance** (flux ac 0.148;
first-pass ac 0.009). A half-time reading also stands open: at
66.26 BPM the file is ≈35 bars and every "bar" below is half a
bar; the 99.93 grid is used because it is the estimator's headline
with the flat window series, and because the snap test below
corroborates it at Anvil strength.

Boundary snaps on this grid ran 0.21–0.83 s (median ≈0.75 s,
≈31% of the 2.40 s bar; the Anvil grid's median was ≈25% of its
bar). No boundary exceeded the 1.4 s SOFT threshold, so no seam in
§2 carries the soft-seam flag — but the phase estimate itself
stays LOW-MEDIUM, as the Anvil's did: a uniformly shifted grid
fits the same evidence, and bar numbers are counted on this one.

## 2. Form — measured segments

Boundaries were found by the novelty function (spectral flux +
chroma change), peak-picked, snapped to the bar grid, and passed
through the merge pass — **which dissolved nothing**: every one of
the 12 interior seams carries a real change of level or harmony
fingerprint across it. Voiced density is the pitch tracker's lock
rate (see §6.2 before reading anything into it).

| # | Bars | Seconds | Mean dB | Character (MEASURED features) |
|---|---|---|---|---|
| S0 | 1–3 | 0.00–7.24 | −23.5 | Quietest music in the file; steepest build (+0.73 dB/s); tracker lock 0.81 — the only dense lock in the song; low centroid (2.3 kHz) |
| S1 | 4–9 | 7.24–21.65 | −16.6 | The build continues (+0.64 dB/s); level arrives in steps |
| S2 | 10–12 | 21.65–28.85 | −13.0 | First ceiling; chroma fingerprint recurs with S7 at +0.964 |
| S3 | 13–15 | 28.85–36.06 | −15.8 | Falling slope (−0.89 dB/s), bright (3.6 kHz); recurs with S8 (+0.911) |
| S4 | 16–19 | 36.06–45.66 | −15.6 | Plateau, highest chroma stability of the verses (0.751) |
| S5 | 20–23 | 45.66–55.27 | −14.0 | Plateau; recurs with S2 (+0.952) |
| S6 | 24–29 | 55.27–69.68 | −14.7 | Longest verse span (6 bars); recurs with S1 (+0.899) |
| S7 | 30–32 | 69.68–76.88 | −12.9 | Second ceiling; +0.964 twin of S2 |
| S8 | 33–36 | 76.88–86.49 | −16.0 | Falling slope; recurs with S3 (+0.911) |
| S9 | 37–39 | 86.49–93.70 | −18.9 | The dip: quietest full-music segment; brightest (3.7 kHz); tracker lock 0.37 |
| S10 | 40–43 | 93.70–103.30 | −15.2 | Plateau restored; recurs with S11 (+0.945) |
| S11 | 44–46 | 103.30–110.51 | −12.9 | Third ceiling; recurs with S7 (+0.962) |
| S12 | 47–53 | 110.51–125.91 | −39.4* | Outro + fade (*the mean swallows the fade: programme holds plateau level to ≈118.5 s, then falls — last window above −40 dBFS ends 123.0 s; final ≈2 s are digital quiet) |

## 3. Form — the reading (INTERPRETATION)

| Bars | Label | Confidence | Grounds |
|---|---|---|---|
| 1–3 | **INTRO** | HIGH | Quietest segment by 6.9 dB, steepest build, and the song's only dense pitch-tracker lock — a chanted or spoken threshold over a bare bed; nothing else in the track looks like this |
| 4–9 | **VERSE A** | MEDIUM | Full flow arrives as the build completes; the first span of the performed verses |
| 10–12 | **REFRAIN PLATEAU 1** | MEDIUM | First ceiling (−13.0) and the fingerprint that returns at bars 30–32 and 44–46 — the hook the model invented (the sheet writes none) |
| 13–29 | **VERSE SPAN I** | MEDIUM as a span; the internal seam is **UNRESOLVED** | Seventeen bars of flowing level across four segments. The sheet's Verse I / Verse II division lives somewhere inside this span (or at the plateau after it); this bench cannot locate it — candidate seams at bars 16, 20, 24 stand at LOW |
| 30–32 | **REFRAIN PLATEAU 2** | MEDIUM | Second ceiling (−12.9), +0.964 twin of Plateau 1 |
| 33–36 | **VERSE SPAN IIa** | MEDIUM-LOW | Falling slope off the plateau; recurs with S3 — the spans rhyme across the plateaus |
| 37–39 | **BREAKDOWN / DIP** | MEDIUM | Only full-music dip in the song; brightest segment; the tracker partially re-locks (0.37) — a pitched or spoken drop before the close |
| 40–43 | **VERSE SPAN IIb** | MEDIUM-LOW | Level restored out of the dip |
| 44–46 | **REFRAIN PLATEAU 3** | MEDIUM | Third ceiling (−12.9), +0.962 — the hook's closing statement |
| 47–53 | **OUTRO + FADE** | HIGH | Plateau to ≈bar 49, then a fast fade to the floor by ≈124 s (RMS contour, not the segmenter — see §6.4) |

**Where the sheet's verses land, stated at the strength the
evidence carries.** The founder fed Verses I–II — 54 lines — and
the render performs both (his account, and the ASR of record; this
bench transcribes no lyrics). The performed programme spans bars
1–49 with the vocal's spans at bars 4–46. **The line arithmetic
does not close at one line per bar**: 54 lines over ≈43 verse
bars is ≈1.26 lines per bar, and if the three plateaus are sung
hook rather than verse, denser still. The delivery is denser than
the sheet's layout — which is precisely the layer the first
instrument heard at 132.5. A line-accurate map (which bar carries
which line, and where Verse II begins) is a phase-2 production
against the founder's sheet and ear; phase 1 leaves the seam
unlocated rather than guessed. **The standing ambiguity, named
plainly** (the Anvil clause, inherited): in the three plateaus the
bench cannot separate *hook* from *verse* by features alone —
Lyria writes both at full energy. They stand as REFRAIN PLATEAU,
marked unresolved; the founder's account of his own song settles
them in one stroke whenever he cares to.

## 4. Key (MEASURED chroma, INTERPRETATION of centre)

Krumhansl–Schmuckler profile correlation against the
duration-weighted global chroma (peak-picked chroma, the v2
method the Anvil audit validated):

| Candidate | Correlation |
|---|---|
| **F major** | **0.816** |
| C major | 0.699 |
| F minor | 0.659 |

The global chroma itself is headed F (0.147) and C (0.132); the
melody sketch's pitch census is headed F (47 of 120 notes); the
per-bar bench's clearest single bar is bar 1, an F5 at correlation
0.929 with margin 0.116 (HIGH). **Centre: F — HIGH confidence;
three independent instruments concur.**

**Mode: CONTESTED, and the contest is the finding.** The K-S
global read votes F major (margin 0.117 over C major, 0.157 over
F minor). The per-bar template bench votes the other way among
the bars it can read at all: **Fm ×16 against F ×7** (plus F5 ×2).
And the sheet ordered F minor. The zero point is structural and
named: a duration-weighted global chroma is ruled by the loudest
material — the three refrain plateaus, whose templates read F/F5
— while the bar-level bench hears the verse bed's minor third.
**Phase-1 reading: an F vamp, minor-leaning at bar level, mode
unresolved between the benches — MEDIUM-LOW.** No crown is forced;
a phase-2 bass-isolated pass is the road that could settle it.

## 5. Chord progression (MEASURED per bar; full table in chords.csv)

Distribution over 53 bars: **Fm ×16 · UNCLEAR ×26 · F ×7 · F5 ×2 ·
Am ×1 · A#m ×1.**

**The progression, stated at the strength the evidence carries: an
F vamp — F minor and F major templates alternating over one centre
— with the alternation visible where the evidence is least thin:**
bar 1 reads F5 (HIGH, the bench's best bar); bars 3–5 read an Fm
run at MEDIUM; bar 25 reads Fm (MEDIUM), bar 28 F (MEDIUM). After
that the bench reads the vamp's centre holding while **26 of 53
bars — 49% — fall under the gate and stand as UNCLEAR**, concentrated
where the rap rides forward over the bed and the triad templates
cannot separate. Those bars are labelled UNCLEAR in `chords.csv`,
in the open; they were not filled in by guessing the vamp
continues, even though it very probably does.

Single-bar outliers Am (bar 7) and A#m (one bar in the back half)
sit at LOW confidence and small margins; they are recorded in the
CSV and flagged here as **probable template noise**, marked — not
vanished, and not promoted into a "progression" they cannot
support.

## 6. Method notes and failures found on the way (marked, per house law)

1. **The tempo zero point (§1) is a boundary between instruments,
   not an error in either.** Both readings are preserved in
   `analysis-stats.json` with their raw autocorrelations at the
   contested points, so any future bench can re-weigh them.
2. **Voiced density measures trackability, not presence.** Across
   the verse spans the autocorrelation pitch tracker locks on
   only 0.00–0.16 of frames — a rapped line's pitch is
   intonation in motion, and the tracker honestly reports that
   it cannot hold it. Read §2's voice column as "where a pitched
   voice or bed element stood still long enough to be tracked"
   (the intro's 0.81, the dip's 0.37), never as "where the vocal
   is absent". The vocal is present throughout the spans; the
   founder's transcript and the segment levels both establish
   it. The instrument's limit is stated so its numbers are not
   mistaken for the song's facts.
3. **The merge pass dissolved nothing.** All 12 novelty seams
   survived (level steps or fingerprint changes across every
   one) — where the Anvil's segmentation needed two dissolutions,
   this performance's section joints are simply more pronounced.
   `boundaries_merged_away` stands empty in the record.
4. **The segmenter swallows the fade.** Novelty sleeps on a dying
   signal, so S12 spans plateau and fade as one segment; the
   programme/fade boundary at ≈118.5 s in §2–§3 comes from the
   RMS contour (0.5 s windows, thresholds at −30/−40/−50/−60
   dBFS), a different instrument, and is labelled as such
   wherever it is used.

## 7. Melody sketch (summary; full data in melody-sketch.json)

- 120 notes from the gated autocorrelation track; sketch coverage
  14.0% of frames passed the voicing + vocal-likelihood gates —
  against the Anvil's 26.4%. The difference is the material: a
  sung performance holds pitch; a rapped one spends it.
- Range MIDI 40–71 (E2–B4); mean note confidence 0.568; 6 notes
  flagged `octave_suspect`, flagged — not corrected.
- Pitch census: F 47 · F# 22 · C 14 · A# 10 · E 9 · G# 7 · B 4 ·
  A 2. The head corroborates §4's centre. **F# (22 notes) is
  foreign to both F collections** and is read here as the
  tracker's registration of intonation slides and blue-note
  inflections in the flow — a known failure mode on rap, marked,
  not harmonised into a key it would falsify.
- **Rapped passages are not melody:** across the verses the
  sketch quantises the flow's pitch contour. Its most reliable
  zone is the intro, where the tracker locks densely; its
  weakest is everywhere the verses run. The sketch is the floor
  an engraving pass may audit against the audio — by the house
  rule (sheet music ships with all tracks), the notation owed
  for this strike starts from this floor and from the founder's
  sheet, never from invention.

## 8. What would raise each tier

- **The Verse I/II seam and the plateaus' function:** the
  founder's word on his own song — his dictation is the settling
  evidence, as it was for the Anvil.
- **Mode (major vs minor) and the 26 UNCLEAR bars:** stems, or a
  bass-isolated re-run at longer windows; a phase-2 production
  may attempt both.
- **Melody:** a phase-2 pass with a dedicated vocal tracker plus
  hand audit; on a rap performance the hand audit is not a
  luxury but the instrument of record.
- **Line-accurate form map:** lyric timing against the sheet —
  phase 2, with the founder's red pen over the machine transcript
  (which stands as draft scaffold only, per the Anvil ruling).

---

Colophon: analysis generated on this desk from the founder's
uploaded render of record; script, CSV, JSON and this map live
together in `resonance/reference/gemini-sphinx-in-a-gown/`, with
the intake profile in `REFERENCE-GEMINI-SPHINX.md` and the master
and its confessions in `manifest.json`. Nothing herein is a
finished transcription. The audio stays local; this document may
travel.

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All
Rights Reserved, Without Prejudice.

93 — Live, Love, and let Love, Live.
