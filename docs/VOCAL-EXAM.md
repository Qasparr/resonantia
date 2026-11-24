<!--
93
"Do what thou wilt shall be the whole of the Law."
Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice).
XXIV day of November, Dies Martis, Sol in Sagittario,
Anno V:xii e.n. (2026 e.v.)
Scientific Illuminism: Method of Science, Aim of Religion.
Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR,
All Rights Reserved, Without Prejudice. Right of claim hereby
reserved and coined under the authority of the Living Man.
-->

# THE VOCAL EXAM — Phase 1

## The benchmark-and-simulation harness for sung vocals

This document states the harness's method, its judges and
their limits, the baseline results, and the loop protocol
for Phase 2. The design is the founder's, approved as
calculated on 2026-11-24 ("Build Phase 1 — pushed to the
infrastructure on completion"). The harness's terms, his:
**the exam grades the measurable; the founder's ear remains
the final gate for "good," and nothing here claims
otherwise.**

---

## §I — THE DESIGN

A singing engine improves the way a language model
improves: by sitting a **fixed exam**, graded by instruments
instead of impressions, its failures naming the parameter
to adjust. The house had already run the primitive form —
the DETROIT MUGETSU hook's calibration circuit, one judge
(durations), two runs, 90.38% → 99.52%. Phase 1 generalizes
that circuit into an instrument:

- **The corpus** (`resonance/studio/exam/corpus.json`,
  version 1, stamped 2026-11-24): 13 fixed items, each
  carrying its sheet as ground truth — ten Divine Nine
  vowel items (seven steady stations, the VV seat, and the
  two glides ΕΙ/ΟΥ), two short phrases (English; Japanese),
  and the DETROIT MUGETSU hook as the house test piece, its
  sheet taken from the run records of record (run 1's
  `spec.json` + asked `sequence.ds`: 8 lines, 54 notes, 118
  seated phonemes, 13.3333 s asked).
- **The held-out split**, declared in the corpus: vowel-Η,
  vowel-Ω, vowel-ΟΥ, and the Japanese phrase are held out.
  They may be sat for scoring; calibration may never tune
  on them. A method that memorizes the practice items is
  caught by the items it never saw.
- **The judges** (`resonance/studio/vocal_exam.py`): five,
  each returning measured values with units, each returning
  the state **UNSUNG** (no render exists) or
  **UNMEASURABLE** (a render exists but this measurement
  cannot be read from it) instead of a fabricated score.
- **The predictor**: from a sheet alone, the expected
  measurement table of a perfect render — target
  frequencies, total duration, vowel targets in force, and
  the perfect scores. The simulation half of the harness:
  the expectation stated before the take exists.
- **The results** (`resonance/studio/exam/results.jsonl`):
  append-only, proof-ledger discipline. Every record names
  its corpus version, its engine, its item, and its judge
  scores. History is never rewritten; a new sitting appends
  a new dated set.

## §II — THE JUDGES AND THEIR LIMITS

1. **Durations.** The house's realization law, the scale
   both Mugetsu runs were struck on: `100 · Σrealized /
   Σasked` over the item's segments, **unclamped** —
   overshoot past 100 is a reading, not an error (run 2's
   longest line realized 103.1% of its slot).
2. **Pitch.** Per note, the Fourier seat's dominant
   frequency over the note's steady centre (middle 50%),
   against the sheet's MIDI target in cents. Pitch is
   measured through `studio/fourier.py` — the sworn
   frequency instrument — never through a new transform.
   Notes whose centre is under 30 ms are UNMEASURABLE.
3. **Onsets.** A 5 ms RMS envelope; threshold at max(4× the
   envelope's quiet decile, 3% of its peak); an onset is
   the first sustained crossing inside the search window.
   Where the preceding sound has not fallen below
   threshold — a line overhanging its bar line — there is
   no gap to read against, and the onset is UNMEASURABLE.
4. **Vowels.** A linear-predictive formant read
   (pre-emphasis, autocorrelation LPC of order 20 at song
   rates, poles by frequency and bandwidth) over the
   segment's steadiest window, placed against the seated
   Divine Nine targets (`studio/diffsinger.py`'s STATIONS
   table — the one table of record) by log-frequency
   distance; MATCH when the target is the nearest station
   within 0.35 octaves. **Limits, stated once:** LPC reads
   the envelope through the harmonic comb, so at high F0
   the sampling coarsens (flagged `high_f0`); the canon's
   two glides have no steady state and are refused as
   steady targets; and the canon's finest step — Ο vs Ω,
   one height step apart — sits at the read's resolution
   limit: a planted Ω reads 0.101 octaves from its target
   with its nearest neighbour standing in {Ο, Ω}, asserted
   in the tests as a coordinate, not smoothed into a pass.
5. **Master law.** The delivered file on the house's own
   scales: integrated loudness and true peak by
   `studio/pipeline.py`, on the **decoded** audio for MP3
   (the house's decoded road), bitrate by ffprobe's stream
   read. Laws: −14.0 ± 0.5 LUFS; decoded true peak
   ≤ −1.0 dBTP; bitrate exactly the sworn figure when a
   record swears one. The loudness scale carries the
   48 kHz coefficient set; a file at another rate reads
   UNMEASURABLE on that line rather than being mis-weighed.

## §III — THE BASELINE (struck 2026-11-24)

What exists on disk, scored. Both Mugetsu runs sit the
hook item; run 2's delivered master sits the master law;
the remaining twelve items are **UNSUNG** — a state, not a
failure — each with its predictor's expectation recorded
beside it in the results file.

| Judge | Run 1 (uncalibrated) | Run 2 (calibration circuit 1) |
|---|---|---|
| Durations | **90.3841%** | **99.5266%** |
| Pitch (54 notes, all measured) | median 8.64 cents, mean −7.81, worst 263.97 | median 5.10 cents, mean −0.24, worst 22.27 |
| Onsets | 8/8 measured; mean +42.06 ms, worst 84.81 | 6/8 measured; mean +21.69 ms, worst 52.15; 2 UNMEASURABLE (line overhang) |
| Vowels | 31 reads attempted, **0 measured** | 31 reads attempted, **0 measured** |
| Master law (run 2 master.mp3) | — | **compliant**: −14.0 LUFS · −2.82 dBTP decoded · 320,000 bps exactly |

**The duration judge reproduces the recorded history from
the audio itself** — the eight line WAVs sum to 12.0512 s
(run 1) and 13.2702 s (run 2) against the sheet's
13.3333 s: 90.38% and 99.52%, the ledger's figures
re-measured, not re-typed.

**The pitch coordinate the calibration never claimed:**
run 1's worst note stands 263.97 cents off its target —
over two semitones, one note of 54 — while its median is
already 8.64. Calibration moved the median to 5.10 cents
and the worst case to 22.27. The exam's first new finding
is that the duration circuit was also, unmeasured, a pitch
circuit — and that run 1's defect was never its centre but
its tail.

**The vowel finding, at full size:** every one of the 31
vowel reads attempted on each run returned UNMEASURABLE,
and the reason is physical, not procedural. The hook is
sung at MIDI 68–75 — F0 ≈ 415–622 Hz — in phoneme slices
of 30–105 ms. At that pitch the harmonic comb samples the
vocal-tract envelope every ~500 Hz, and no honest
two-formant read resolves from it: three methods were
probed on the bench (single-frame LPC, cepstral envelope
peaks, frame-averaged LPC envelopes) and all three fail
credibly at this pitch and length. The judge therefore
refuses, by name ("soprano comb"), rather than inventing
formants. The vowel seat is **proven where a render can
carry it** — on planted synthetic vowels at F0 180 Hz, all
seven steady stations and VV match their targets (worst
distance 0.19 octaves) — and the corpus's sustained-vowel
items (1.2 s steady states at A3) exist precisely so the
loop's future renders can be vowel-graded. Grading the
hook's vowels awaits either lower-pitched or longer-held
renders; Phase 1 does not pretend otherwise.

**Coordinates struck during the build** (the judges were
corrected against planted truth before the baseline was
struck; each stands here so the record shows its work):

- The masterlaw judge's first strike read −17.01 LUFS
  against the gate's sealed −14.0: the judge had averaged
  the stereo master to mono before weighing, and the
  loudness scale sums channel energies. Corrected — the
  law weighs the file as delivered — and the judge now
  reproduces the sealed gate exactly (−14.0 / −2.82 /
  320,000).
- The onset judge's first threshold law (built on the
  envelope's median) read 1 of 8 onsets on run 1: on dense
  program the median window is itself sung. The threshold
  now stands on the quiet decile; run 1 reads 8/8.
- The vowel judge's LPC order began at 14, which merges
  the canon's close F1/F2 pairs (Α 730/1090, Ο 570/840)
  into one pole; at order 20 both pairs split cleanly
  (711/1077, 553/845 against target). Its bandwidth
  ceiling rose 350 → 450 Hz on VV's planted pole
  (measured ~410 Hz wide at its seat), and its F2 search
  floor fell 700 → 600 Hz because VV's seated F2 *is* 700
  and a lawful read of it lands at ~646. All three
  calibrations were made on planted synthetics, never on
  the baseline renders.

## §IV — THE LOOP PROTOCOL (Phase 2)

The exam exists to be spent. One circuit of the loop:

1. **Sit the exam.** The engine under improvement renders
   the corpus's train items (never the held-out split) and
   every render is scored by all five judges; the sitting
   appends its records to `results.jsonl`.
2. **Read the failures as coordinates.** Each judge's
   defect names its parameter: duration realization by
   seat names the seat's calibration factor (the circuit
   of record); pitch bias names the pitch curve; onset
   error names the attack/assembly timing; vowel distance
   names the formant target's offset; a master-law failure
   names the mastering stage, not the singer.
3. **Adjust one parameter class per circuit**, so the
   delta that follows has one cause.
4. **Re-sit and record the delta.** The same items, the
   same judges; the results file's two sittings are the
   improvement, stated as numbers with a history.
5. **Sit the held-out split** when a method claims to be
   done. A gain that appears on train items and vanishes
   on held-out items was memorization, not improvement,
   and the exam says so in its own records.
6. **The founder's ear closes the circuit.** Scores admit
   a render to his hearing; they do not pass it. A take is
   good when he says it is good — the exam's office is to
   make sure what reaches his ear has already survived
   every measurement the house can swear.

---

*Phase 1 stands: the corpus, the judges, the predictor,
the baseline. It sings nothing new — singing is the loop's
work, and the loop is Phase 2, on the founder's word.*
