# THE PIRATE ESSAY — AUDIOBOOK RUN 1

## Run Report of the First In-House Audiobook

**A Scientific Illuminist treatment of a narration, a mastering,
and a sealing**

Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice)
XVII day of November, Dies Martis, Sol in Scorpio,
Anno V:xii e.n. (2026 e.v.)

Classification: Enterprise • Educational • Research & Development
Method of Science, Aim of Religion

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR,
All Rights Reserved, Without Prejudice. Right of claim hereby
reserved and coined under the authority of the Living Man.

---

## I. THE COMMISSION

On the sixteenth of November the founder asked whether the house
should do audiobooks in house now — the house having agents, a
persona, and a speech seat. The desk answered YES under his
widened delegation for that night's work, and this run is the
pilot: his own stamped essay, *The Pirate Essay — The
Seventy-Seven Trinities* (17 pp, $9, Cash App note PIRATE ESSAY),
read whole by the house speech seat, mastered to house law, and
sealed in the Render-as-Proof ledger, with a video edition as the
second half. No listing, pricing, or posting of the audio or
video editions was made — the desk rules those when the pilot
lands, and the founder's ear is the quality gate. This report
claims measurements only.

## II. THE NARRATION SCRIPT

The essay's words are preserved. What changed is only what the
ear cannot use, under rules stated here so the reading can be
reproduced and audited (`NARRATION-SCRIPT.md`, 21 chunk files in
`script/`, 8,935 words):

- Markdown furniture, footnote markers, and page furniture are
  not read. Footnotes are read at each section's end, as their
  own chunks, so the argument's body is never interrupted.
- The § VIII audit ledger and the § IX truth audit are read as
  their verdicts and findings, not as rows of arithmetic; § X,
  the Table of Authorities, is read as prose lines.
- Parenthetical letter-breakdowns are rendered as claim + bank
  ("weighs seventy-seven in the English ordinal bank"), never as
  spelled-out sums.
- Greek and Hebrew are read in the essay's own transliterations
  (πλοῖον → "ploion", σκαμνόν → "skamnon", ἀλήθεια → "aletheia",
  θέλημα → "thelema", πειρατής → "peirates", πεῖρα → "peira",
  עז → "Oz"). The voice never meets a script it cannot speak.
- Numbers are spelled out; display caps are lowered to the
  word's spoken form (TRVVTH is read "Truth"); where the
  spelling itself is the argument (HVLL, VVHY, XVHD), the word
  is spelled letter by letter.
- The Colophon's typography paragraph — print furniture about
  fonts — is skipped as such; the Colophon's substance, the
  ratification, and both Flagpoles (head and close) are read.

## III. THE RENDER — TWO CEILINGS, FOUND AT FULL SIZE

**Hypothesis.** The proven llama-tts invocation from the speech
lab's bench work would read the chunks as struck.

**Method.** Render per chunk (21 generations), assemble in
document order.

**Observation — failure one.** Chunk 02 (about 800 words) landed
at exactly 33.50 s, identical to chunk 01's first strike: this
build's default generation cap is **512 frames**, and it
truncates *silently* — no error, a clean-looking WAV, a third of
the text simply absent. Corrected with `-n 9000`, the model's
own ten-minute design ceiling, and verified on a test chunk
(570 frames, clean stop at the text's end).

**Observation — failure two.** Under `-n 9000`, chunks 02 and 04
then both stopped at **exactly 1,999 frames** with identical
byte counts on different texts — a second, hard ceiling at
1,999 frames (about 133 s) that no flag in the proven invocation
lifts. Tail-energy checks did not discriminate the cuts (the
codec ends frames quietly); the identical frame counts are the
proof. Chunks 01, 03, 05 had landed below the ceiling with frame
counts inside the plausible band for their word counts (6.5–7.5
frames/word, mutually consistent) and were accepted complete;
a later duplicate strike of one piece reproduced its frame
count within 2 frames (1,051 vs 1,053), confirming the engine
is near-deterministic on identical text.

**Result — the piece driver.** `render_pieces.py`: no
generation is ever asked for more than **190 words** (about
1,300 frames at this material's density). Pieces join inside
their chunk with 0.35 s of silence; every piece is validated on
landing — frames ≥ 1,990 would mean the ceiling was touched
(split and re-render), and a frames-per-word ratio outside
[3.0, 9.0] would flag a suspected premature stop. The batch
rendered **58 pieces across the 18 remaining chunks with zero
flags**: no ceiling touched, no pace outlier. Two operational
notes ride with the record: tracked background sessions on this
box were twice killed by SIGTERM at about 5.6 minutes, so the
batch ran fully detached (`setsid nohup`), the pattern the
first batch had already proven; and the whole render took
about three hours of wall time at 0.35–0.5× real-time on the
shared CPU. Long narration is a batch job here; the pilot
prices that in.

The voice is **Imogen_en-British_F_1**, a predefined voice
shipping inside the model's own release (ZONOS3-Mini via
llama.cpp llama-tts b12438). No voice was cloned, trained, or
imitated. This is the speech seat — it reads; it does not sing,
and nothing in this run is presented as sung.

## IV. ASSEMBLY

The 21 chunks (44.1 kHz mono) were converted to the master's
48 kHz and joined in document order with silence only — 1.2 s
between chunks, 2.5 s before the Annex and before the Colophon.
No content was trimmed anywhere in the run. Program:
**3,839.72 s (63 min 60 s)** of narration and joins, struck as a
24-bit assembled WAV.

| Part | Chunks | Duration |
|---|---|---|
| Title block, Flagpole, seal | 01 | 0:59 |
| § I. The Frame — Three Trinities at Seventy-Seven (+ footnotes) | 02–03 | 6:46 |
| § II. The Take — The Stool, the Loot, and the Treasure (+ footnotes) | 04–05 | 4:41 |
| § III. The Ship — The Hull Is the Engine (+ footnotes) | 06–07 | 5:57 |
| § IV. The Code — Articles Before the Voyage (+ footnotes) | 08–09 | 8:23 |
| § V. The License — The Same Act, the Other Paper (+ footnotes) | 10–11 | 6:39 |
| § VI. The Bottom — Rock Bottom as the Port of Departure (+ footnotes) | 12–13 | 4:54 |
| § VII. The Four-Element Content Test | 14 | 3:24 |
| § VIII. The Pontifex Audit Ledger (read as its verdicts) | 15 | 1:49 |
| § IX. Truth Audit | 16 | 5:34 |
| § X. Table of Authorities, condensed | 17 | 1:55 |
| Annex — The Greek Proofs (three parts, incl. the defect record) | 18–20 | 9:59 |
| Colophon, Ratification, closing Flagpole | 21 | 2:34 |
| **Program total (incl. 26.6 s of joins)** | **21 chunks** | **64:00** |

## V. THE MASTER — THE LAW, A DEAD BODY, AND TWO ATTEMPTS

House law: −14.0 ± 0.5 LUFS integrated, delivered MP3 decoding
to ≤ −1.0 dBTP, exactly 320,000 bps. The chain is the Four
Powers path of the Mugetsu run-2 master: Scire measures, the
mastering law of `pipeline.master_signal` (gain, the pipeline's
own soft limiter, true-peak trim), Tacere's TPDF dither at the
24-bit strike under the house seed 93, Velle and Vapour not
engaged — a single speech stem has no mix to shape and no Sigma
couple to print.

**The dead body.** The first master strike died silently
mid-chain: process gone, no traceback, a 2.95 GB working array
left on disk. Diagnosis, at full size: the whole-signal scales
cannot carry a 64-minute program on this box —
`measure_loudness_lufs` takes an FFT the length of the signal
per channel (about 3 GB of complex spectrum), and four_powers'
RMS witness squares the whole (2, N) body into RAM. The repair
kept the law and changed the body: the loudness scale is the
pipeline's *own* ungated K-weighted figure with its *own*
biquad coefficients, applied in the time domain in blocks
(validated against the whole-signal scale on two 90 s slices of
this program: **delta 0.0000 LU** on both), Scire's witnesses
accumulated block-wise, and the pipeline's oversampled true
peak in 120 s windows with 5 s overlaps. The build script
carries this as a dated correctio in its header; the original
plan stands above it, marked, not vanished.

**Attempt 1.** Scire: −22.37 LUFS, true peak −2.76 dBTP, crest
22.61 dB. Gain +8.37 dB; the ceiling overrode loudness (trim
−0.29 dB) → −14.34 LUFS, WAV true peak −1.02 dBTP. The gate
measured the *delivered MP3 decoded* at **−0.88 dBTP** — the
codec's decode overshoot (+0.14 dB over the steered peak) broke
the ceiling law, and the gate **FAILED** the master, as it is
built to do. Loudness and bitrate passed. The FAILED record
stands in the ledger permanently: `pow-875cbecb…`.

**Attempt 2** (the calibration loop's own move, the failed
measurement spent as knowledge): the limiter and trim steer to
−1.30 dBTP, budgeting the decode overshoot, and the gain
pre-compensates +0.38 dB for the lower ceiling's extra limiting
cost, from attempt 1's measured transfer. Result: gain
+8.75 dB, trim −0.32 dB, −14.03 LUFS, WAV true peak −1.32 dBTP,
delivered MP3 decoding to **−1.26 dBTP** — inside every law,
with margin. The gate **SEALED** it.

## VI. THE PROOFS

- **Proof of Work (vocal)** — `pow-683111a6845eff2cc9233c492ceb1f4f7ae39308aadf5443cfe5fa5128b86936` — **SEALED**. The manifest names the engine (ZONOS3-Mini via llama-tts b12438, the ggml-org model pair), the predefined voice, the source text's path and SHA-256, the narration script's hash, all 21 chunks with their durations, and the honest label: *spoken narration render — speech, not sung performance*. On attempt 2 the standing record was reused as parent rather than re-stamped; the narration was not re-rendered.
- **Proof of Mastering, attempt 1** — `pow-875cbecbf6a46800a2ec84e4ee69200607ff96224a5c5eedb7772824c63c966d` — **FAILED** (decoded true peak −0.88 dBTP vs law ≤ −1.0; loudness −14.34 ✓; bitrate 320,000 ✓).
- **Proof of Mastering, attempt 2** — `pow-8245e4c5bb9aaef6a01f6b09f5da133286bdaab4329b2b863c1753242a1c26f6` — **SEALED** (loudness −14.03 LUFS ✓; decoded true peak −1.26 dBTP ✓; bitrate exactly 320,000 bps ✓). Artifact: 153,591,405 bytes, SHA-256 `0ce28b9df55e860e298040a77de106d9bd9eee8f7519b3b306ebd73e355fadb5`. Label: *spoken-word audiobook master*.
- **Ledger verify** after the run: 20 records; the hash chain
  (record IDs and prev-links) verifies whole. One artifact-body
  flag stands, explained here at full size: the FAILED attempt-1
  record attests the attempt-1 MP3 body at the deliverable path,
  and attempt 2 was mastered onto that same path, so the file
  now hashes to the sealed attempt-2 body and verify reports
  the attempt-1 artifact as TAMPERED. No record was edited; the
  chain is intact; the flag is the visible cost of reusing one
  path for two attempts. **The lesson, filed for every future
  run: masters are struck to attempt-specific paths, and only a
  SEALED master is promoted to the deliverable name.**

Two measurement confessions ride in the sealed record itself:
`proofs.measure_master` — the gate's own whole-signal measurer —
could not run on this box at all (it decodes into /tmp, a
512 MB tmpfs that a 64-minute decode cannot fit; the failure is
environmental, not musical), so the gate was fed by the same
scales computed in blocks over the decoded MP3, with the
substitution confessed in the manifest's measurement note. The
scales are the house's; only their bodies are blocked.

## VII. THE VIDEO EDITION

A static, honest visual at 1920×1080: the bookshop front cover
on the doctrine purple (#4B0082), the TVRRIS VERITATIS seal,
the title, and the narration credit, composed in PIL
(`video-frame.png`, inspected full-size before encoding: cover
upright, text clean). The audio is the sealed master's own
stream, **copied, not re-encoded**, into the MP4 — the video is
an edition of the master, not a new master. One cosmetic seam,
named: the seal asset carries its own black field, so the seal
sits on a black square against the purple; the asset was used
as the house keeps it.

The edition took three strikes, and the record keeps all
three. At 30 frames per second, encoding 115,200 frames of
1080p on this throttled box runs to about a hundred minutes —
and the exposure killed it twice: a service restart at about
one minute (a 1.8 MB partial file, removed), and a second death
at about minute 100, leaving 222 MB of MP4 with no moov atom —
a body no player can open, removed likewise. The correctio,
recorded in the build script itself: a still cover does not
need thirty frames a second. At **1 fps** the same frame, the
same encoder settings, the same stream-copied audio landed in
**254.7 s**. Final figures, independently re-probed: duration
**3,839.736 s** against the master's 3,839.717 s (delta
0.019 s); **166,577,788 bytes**; H.264 video 1920×1080 at
1 fps; the audio stream MP3, copied bit-for-bit from the
sealed master.

## VIII. SEAMS AND OPEN ITEMS

- **The founder's ear is the gate.** Everything above is
  measurement. Whether Imogen's British reading serves the
  essay — its pace runs brisk, roughly 140 words per minute
  across the program, faster in footnote runs — is his verdict
  to give, and it is not pre-claimed here.
- **Greek and Hebrew** are read in the essay's own
  transliterations by design (§ II); the voice's handling of
  the Latin legal phrases and the spelled-letter words
  (HVLL, VVHY, XVHD) could not be ear-checked from this side
  of the desk — the listening-proxy checks (frame counts, pace
  bands, join integrity) all pass, and a transcript spot-check
  is the founder's playback away.
- **One body per path** (§ VI) is the run's procedural lesson;
  the second is that `proofs.measure_master` needs a
  long-form decode path (workspace disk, blocked scales) before
  the next audiobook — the confession fallback worked, but the
  gate's own scales should be able to carry an hour.
- The assembled and master WAVs, chunks, and pieces (about
  2.3 GB) remain in the run folder on this box for re-work;
  audio never enters git. The committed record is the script,
  the drivers, the logs, the manifest, and this report.

## FILES OF THE RUN

- `THE-PIRATE-ESSAY-AUDIOBOOK.mp3` — the sealed master, beside
  the essay in `~/workspace/your_files/pirate-essay/`
  (153,591,405 bytes; 48 kHz; 3,839.72 s).
- `THE-PIRATE-ESSAY-VIDEO.mp4` — the video edition, same folder.
- `NARRATION-SCRIPT.md` — the reading script, same folder and
  in this run folder; chunk files in `script/`.
- `render_pieces.py`, `render_batch.sh`, `build_audiobook.py` —
  the drivers, in this run folder.
- `pieces.log`, `render.log`, `build-*.log` — the run's raw
  record.
- `manifest.json` — assemble/master/proofs/video measurements.
- Ledger: `proofs/ledger.jsonl` in this repo (20 records).

---

## COLOPHON

This report was generated under the discipline of Scientific
Illuminism on the seventeenth day of November, 2026 e.v., from
the run's own logs and ledger records; every number in it is
traceable to one of the files named above. The narration, the
mastering, and the sealing were executed in house, on the
house's own box, with no rented service and no outside voice.

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR,
All Rights Reserved, Without Prejudice. Right of claim hereby
reserved and coined under the authority of the Living Man.

93 — Live, Love, and let Love, Live.
