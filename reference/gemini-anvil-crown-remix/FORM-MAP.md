<!--
93
TRANSCRIPTION-ANALYSIS — phase 1 (analysis only). Every figure in this
document was MEASURED from the audio by analyze_anvil_remix.py (the
Sovereign intake bench, carried over whole, with the 93-bar audit
seated for this brief). Interpretations are tier-marked as such. No
lyric is transcribed here; no note or chord is fabricated. Where the
bench could not see, the bench says so, in the open. Grid B's full
machine record stands in grid-b-audit.json and chords-grid-b.csv
beside this file.
-->

# HONEY AND HAMMER (THE ANVIL AND CROWN — REMIX) — Form Map, Key, Chords, Melody Sketch

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
  re-running `analyze_anvil_remix.py` (grid B by its override).
- **INTERPRETATION** — a desk judgement laid over measurements; the
  measurements are printed beside it so the judgement can be audited.
- **Confidence** — HIGH: several independent features agree.
  MEDIUM: the lead feature is clear, one alternative stands.
  LOW: the evidence is thin and the label is a placeholder with its
  seams showing.

## 1. The grid — a named boundary, one family, no crowned rung (MEASURED)

| Quantity | Grid A (bench of record) | Grid B (alternative clock) |
|---|---|---|
| Tempo | **95.91 BPM** (estimator headline) | **143.55 BPM** (dominant periodicity) |
| Beat | 0.6256 s | 0.4180 s |
| Bar (4/4) | 2.5023 s | 1.6719 s |
| Downbeat phase | 0.075 s | 0.115 s |
| Bars in file | 72 | 108 |
| Boundary snaps | 0.14–1.18 s | 0.09–0.72 s |

**This file does not keep one clock either — it keeps less of one
than its predecessors.** The flux estimator's candidate family is
{47.85 (ac 0.5588), 71.78 (0.5952), 143.55 (0.6127)}, with its own
headline at 95.91 (the ×2 rung of the ≈47.9 BPM fundamental; the
family stands at the ratios 2 : 3 : 4 : 6). The estimator crowns
95.91 by its log-prior while its *dominant periodicity* is 143.55 —
the rung nearest the ordered 144. Its 30-s windows split three
ways: **95.91 / 95.88 / 143.91 / 71.96 / 71.99 / 95.94 — spread
71.95 BPM**, against the Sphinx strike's 0.11 and the Sovereign
strike's 30.03. No rung is flat across this performance. Raw flux
autocorrelation at the named points: **72.0 → 0.6528 · 144.0 →
0.6393 · 143.55 → 0.6124 · 95.91 → 0.5642** — the ordered tempo's
neighbourhood carries the family's second-strongest raw reading,
a pulse-presence neither prior strike showed, without becoming
the measured clock. The desk's first-pass instrument (RMS-block
envelope) crowns 95.7, weakly (strength 0.2691; its ac at 144 is
0.1168).

Grid A stands as the bench of record because it is the house
estimator's headline — the same rule that seated both prior grids.
Grid B is carried in full (`grid-b-audit.json`) because §3 shows
the brief's form fits it far more closely. **The zero point is the
rung boundary inside one pulse family, and it is reported, not
resolved by preference.** Bar numbers below are grid A's unless
marked (B).

## 2. Form — measured segments (grid A; seconds are grid-free)

Boundaries by the novelty function, snapped to grid A; the merge
pass dissolved nothing on either grid. Levels are segment means.

| # | Bars (A) | Seconds | Mean dB | Character (MEASURED features) |
|---|---|---|---|---|
| S0 | 1–4 | 0.00–10.08 | −27.3 | The quiet room: level far below the body, rising slope +0.82 dB/s; voiced 0.45 — the intro |
| S1 | 5–7 | 10.08–17.59 | −13.8 | **Level rank 1 of 18**; recurs with S7 (**+0.885**) |
| S2 | 8–10 | 17.59–25.10 | −13.9 | Recurs with S1 (+0.850) |
| S3 | 11–14 | 25.10–35.11 | −14.1 | Recurs with S7 (+0.867) |
| S4 | 15–18 | 35.11–45.12 | −14.6 | Recurs with S9 (+0.797) |
| S5 | 19–23 | 45.12–57.63 | −13.9 | Long span, flat slope |
| S6 | 24–27 | 57.63–67.64 | −18.3 | A dip: slope −1.09 dB/s, voiced 0.36; recurs with S0 (+0.675) |
| S7 | 28–31 | 67.64–77.65 | −13.9 | Level rank 3; recurs with S1 (**+0.885**) — S1's twin |
| S8 | 32–37 | 77.65–92.66 | −14.2 | Longest full span so far; recurs with S1 (+0.785) |
| S9 | 38–40 | 92.66–100.17 | −14.3 | Recurs with S4 (+0.797) |
| S10 | 41–43 | 100.17–107.68 | −14.1 | Voiced 0.10 — the tracker's floor |
| S11 | 44–46 | 107.68–115.18 | −14.2 | Recurs with S10 (+0.776) |
| S12 | 47–49 | 115.18–122.69 | −16.1 | Falling slope −1.15 dB/s |
| S13 | 50–52 | 122.69–130.20 | −19.6 | Quietest segment of the full-level body after the intro; **voiced 0.66 — the file's highest** (see §6.5) |
| S14 | 53–56 | 130.20–140.21 | −18.1 | **Exactly the ordered half-hook's seat**; recurs with S1 (+0.633) |
| S15 | 57–62 | 140.21–155.22 | −15.1 | Rising slope +0.30 dB/s |
| S16 | 63–69 | 155.22–172.74 | −14.3 | Longest span; recurs with S2 (+0.819) |
| S17 | 70–72 | 172.74–179.10 | −47.1 | The fall: slope −12.44 dB/s, level collapses to the floor |

Grid B segments, for the audit in §3: 1–6 · 7–10 · 11–14 · 15–21 ·
22–26 · 27–34 · 35–40 · 41–46 · 47–55 · 56–60 · 61–64 · 65–68 ·
69–74 · 75–78 · 79–84 · 85–92 · 93–103 · 104–107 (the fall, −45.5).

**Programme shape, in seconds, owing nothing to either grid:**
full level 0–≈172.7 s with two measured dips (S6, S12–S14);
the fall runs ≈172.7–179.1 s; last window above −40 dBFS at
175.25 s; final window −84.4 dBFS. **No silence block stands
anywhere in the file** — no exact-zero span of the Sovereign
kind exists here.

## 3. The 93-bar audit (MEASURED coordinates; the reading tiered)

The brief ordered: intro 1–4 · hook 5–12 · Qasparr Verse I 13–28 ·
hook 29–36 · Qveen Bee Verse I 37–52 · hook-half 53–56 · Qasparr
Verse II 57–68 · Qveen Bee Verse II 69–80 · tag-team 81–92 ·
outro 93. Distances from each ordered interior boundary to the
nearest measured segment boundary (sign: + = the seam falls after
the ordered seat, − = before it):

| Ordered boundary | Grid A distance | Grid B distance |
|---|---|---|
| Start of bar 5 (hook in) | **0.00 bars** (10.08 s, exact) | +2.00 bars (seam 10.15 s) |
| Start of bar 13 (Q Verse I in) | +2.00 bars (seam 35.11 s) | +2.00 bars (seam 23.52 s) |
| Start of bar 29 (hook in) | −1.00 bar (seam 67.64 s) | −2.00 bars (seam 43.58 s) |
| Start of bar 37 (QB Verse I in) | +1.00 bar (seam 92.66 s) | −2.00 bars (seam 56.96 s) |
| Start of bar 53 (hook-half in) | **0.00 bars** (130.20 s, exact) | +3.00 bars (seam 92.07 s) |
| Start of bar 57 (Q Verse II in) | **0.00 bars** (140.21 s, exact) | −1.00 bar (seam 92.07 s — the same seam serves both seats) |
| Start of bar 69 (QB Verse II in) | +1.00 bar (seam 172.74 s) | **0.00 bars** (113.80 s, exact) |
| Start of bar 81 (tag-team in) | **no seam exists** — the grid ends at bar 72 (distance to file end: 8.46 bars) | −2.00 bars (seam 130.52 s) |
| Start of bar 93 (outro) | **no seam exists** — the grid ends at bar 72 (distance to file end: 20.46 bars) | **0.00 bars** (153.93 s, exact) |
| Total bars / 93 ordered | 72 in file; 93 would span 232.79 s | 108 in file; 93 span 155.60 s; programme at −40 dBFS = 105 bars |

**The total-span coordinate, both ways:** at the ordered 144 BPM
the song should run 155.0 s; the file runs 179.096 s. On grid A
the file is *short* of its orders (72 of 93 bars — the last two
seats have no ground to stand on). On grid B the file is *long*
(108 bars in file, ≈105 at programme level against 93 ordered)
and every seat has a seam within 3 bars, two of them exact. The
duration surplus and the bar deficit are one fact — the performed
clock is slower than the ordered clock — read on two grids.

**The hooks declare themselves (grid A).** The segment covering
the first hook seat (S1, bars 5–7, −13.83 dB) is the **loudest
segment in the file**, and its strongest recurrence is S7
(+0.885), the segment covering the second hook seat's head
(bars 28–31, −13.88 dB, rank 3) — whose strongest recurrence is
S1. **The two hook seats are mutual twins at the file's highest
pairing**: whatever else the bench cannot name, the hook *returns*,
and it returns at the top of the level table, as a hook should.
The ordered half-hook (bars 53–56) is **exactly one measured
segment** (S14, 130.20–140.21 s, recurrence +0.633 with S1) — the
audit's cleanest seat — but at rank 14 of 18 by level (−18.12 dB):
the half-hook, if it stands there, stands at half weight as well
as half length. The bench prints the coordinate; it does not
say why.

**On grid B** the strongest recurrence in the file is likewise a
pairing — S1↔S7 at **+0.975** — but its seats are bars 7–10 and
41–46: the first inside the ordered first hook, the second inside
Qveen Bee's ordered Verse I. The bench records the pairing and
its coordinates; assigning it a function is beyond this pass.

**Verse seams:** no segment boundary carries a performer's name
on either grid — the bench locates seams, not voices. The
founder's voice-note ASR of the performance (testimony, not
bench; the Sovereign precedent) carries the brief's formation in
order — intro line, hook, Qasparr Verse I, Qveen Bee Verse I
("Honey and hammer — I swing both when I enter"), hook reprise,
Qasparr Verse II, Qveen Bee's double-time Verse II, and the
tag-team close ("I bring the honey — I bring the hammer down …
every queen needs a forge — every forge needs a flame"). This
bench cannot place those events in time and does not promote
the testimony into locations. INTERPRETATION, MEDIUM: the
formation was performed as ordered; the bench's seams corroborate
its joints at the coordinates tabled above, on one clock or the
other, never both at once.

## 4. Key (MEASURED chroma, INTERPRETATION of centre)

Krumhansl–Schmuckler against the duration-weighted global chroma:

| Candidate | Correlation |
|---|---|
| **G# minor** | **0.633** |
| G# major | 0.532 |
| D# minor | 0.504 |

Margin **0.100** — the weakest key margin of the three intakes
(Sovereign's was 0.217). The global chroma heads G# (0.1144),
D# (0.1090), A# (0.1065) with B fourth (0.0978); the A pitch class
sits seventh of twelve (0.0775). **Centre: G# — MEDIUM. Mode:
minor — MEDIUM**, against the brief's ordered **A major**, which
no bench in this intake crowns: its template stands outside the
top three and its tonic pitch class is mid-chroma. The original
Anvil's A major — the reason the brief ordered it — is the
coordinate that does not transfer. Third strike, third
self-chosen key; the pattern is the finding.

## 5. Chord progression (MEASURED per bar; full tables in chords.csv / chords-grid-b.csv)

Distribution, grid A (72 bars): **UNCLEAR ×34 · G#m ×21 · D#5 ×3 ·
G# ×3 · Am ×3 · Bm ×2** · A, A#, A#m, D, Dm, F ×1. Grid B
(108 bars): **UNCLEAR ×48 · G#m ×27 · G# ×8 · A#m ×5 · D#5 ×5 ·
Am ×3** · A#5, D#m, E, F# ×2 · A, A#, Bm, C ×1.

**The progression, at the strength the evidence carries: a
G# minor vamp** — G#m as the standing centre on both grids, D#5
(its bare fifth) as the recurring pole, the minor colour
corroborating §4 from the per-bar bench. Nearly half the bars on
either grid fall under the UNCLEAR gate (34 of 72; 48 of 108)
where the rap rides forward and the template cannot separate
voice from harmony — the same failure geography as both prior
intakes, printed rather than filled in.

## 6. Method notes and failures found on the way (marked, per house law)

1. **The tempo zero point (§1) is a boundary between rungs of
   one pulse family, not an error in any instrument.** All
   readings stand in `analysis-stats.json` with their raw
   autocorrelations. What neither grid survives is the window
   test: this performance's pulse is not flat on any single
   rung, and its spread (71.95 BPM) is the widest the bench has
   recorded. Grid A's seats and grid B's seats cannot both be
   the song's joints; both are printed.
2. **The grid B run died once, and its first harvest was
   poisoned.** The first grid-B analysis was OOM-killed beside
   the desk's concurrent MusicGen render, and the harvest step
   then read the still-standing grid A file and wrote a
   `grid-b-audit.json` containing grid A's numbers under grid
   B's name. It was caught because its grid block was identical
   to A's — a forgery of exactly the kind the Hood intake's
   phantom-stdout incident taught this desk to hunt. The run
   was repeated clean (exit 0), the audit re-harvested from its
   own output, and grid A's files restored as the bench of
   record. The bogus file was overwritten, and the incident is
   recorded here so the correction is never mistaken for the
   record.
3. **The arpeggio bed-census artefact.** The ungated bed track's
   pitch-class census is headed B (284 of 756) — and B4
   (493.9 Hz) sits at the f0 tracker's 500 Hz ceiling. A census
   pinned to the instrument's ceiling is the tracker registering
   bright broadband content at its limit, not a harmony. It is
   one of the reasons the REFERENCE reads the arpeggio as it
   does; the artefact is marked here so the census is never
   quoted without it.
4. **The arpeggio bench's sight line.** The bed track is the mid
   channel; the brief's Paganini-arpeggio figure was ordered on
   the *hi-hats*, whose register lives in the high band this
   bench does not isolate. NOT ESTABLISHED (chord-step share
   0.246 against the 0.45 threshold; pattern score 0.840;
   coverage 0.493; density 4.22 notes/s) is therefore a finding
   about the evidence this bench can hold, printed with its
   thresholds in `analysis-stats.json` — neither PRESENT nor a
   clean ABSENT for the figure itself.
5. **Voiced density measures trackability, not presence** —
   inherited from the Sphinx intake, unchanged: read §2's locks
   (S13's 0.66 at −19.6 dB, S10's 0.10 at full level) as where
   pitch stood still long enough to be tracked, never as where
   the vocal is absent. S13 — the quietest segment of the
   full-level body after the intro (only S0, the intro itself,
   and S17, the fall, sit lower) and the most trackable — is
   consistent with a *sung* passage at low level; that reading
   is INTERPRETATION, LOW, and is marked as such rather than
   promoted into a seat assignment.
6. **The merge pass dissolved nothing on either grid** —
   `boundaries_merged_away` stands empty in both records; the
   seventeen novelty seams are all real changes of level or
   fingerprint. Seam *seconds* are grid-free measurements;
   seam *bar numbers* are only as good as the grid they were
   snapped to (snaps run to 1.18 s on grid A) — which is why §3
   prints both.

## 7. Melody sketch (summary; full data in melody-sketch.json)

- 368 notes from the gated autocorrelation track; coverage
  25.4 % of frames (Sovereign: 18.4 % — the most trackable
  performance of the three). Range MIDI 42–71 (F#2–B4); mean
  confidence 0.607, median 0.593; **2 notes flagged
  `octave_suspect`**, flagged — not corrected.
- Pitch census: A# 71 · B 56 · G# 52 · D# 43 · E 34 · D 32 ·
  C# 23 · F# 17 · G 14 · F 13 · C 7 · A 6. The census is headed
  A# — the supertonic of the measured G# minor centre, an
  unusual head for a *vocal* sketch; under the blue-note clause
  inherited from the Sphinx intake it is read as intonation and
  tracker registration over a dense, doubled performance, NOT
  as a rival centre (§4's chroma, which heads G#, outranks a
  gated sketch census). The two benches are printed side by
  side so the tension is visible, not averaged away.
- Rapped passages are not melody: the sketch quantises the
  flow's intonation. Its reliable zones are the sung passages —
  the intro and the hooks — where the tracker locks; the verses
  are its floor, not its portrait.

## 8. What would raise each tier

- **The grid (95.91 vs 143.55):** a phase-2 onset-by-onset audit
  of the kick/hat pattern against both rungs, or the founder's
  word on the bounce he hears. The family boundary is named
  either way.
- **Seat-accurate form:** lyric timing against the brief's texts
  — phase 2, the founder's ASR standing as testimony-scaffold
  only, per the Anvil ruling. That pass, not this bench, can
  give the tag-team seat (bars 81–92) a measured address.
- **The 34–48 UNCLEAR bars:** stems, or a bass-isolated re-run;
  the G#m vamp is there to be heard once the vocal is not on
  top of it.
- **The arpeggio:** a phase-2 pass on a high-band-isolated track
  (the hats' register, above the voice and the bed) is the road
  that could raise NOT ESTABLISHED to a finding either way.
- **The key's margin (0.100):** the same bass-isolated re-run;
  a weak crown is reported as a weak crown until a second
  instrument strengthens it.

---

Colophon: analysis generated on this desk from the founder's
uploaded render of record; script, CSVs, JSONs and this map live
together in `resonance/reference/gemini-anvil-crown-remix/`, with
the intake profile in `REFERENCE-GEMINI-ANVIL-REMIX.md` and the
master and its confessions in `manifest.json`. Nothing herein is
a finished transcription. The audio stays local; this document
may travel.

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All
Rights Reserved, Without Prejudice.

93 — Live, Love, and let Love, Live.
