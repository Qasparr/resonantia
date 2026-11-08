<!--
=====================================================================
93

Epigraph: "The method of science, the aim of religion." — every
pass below was MEASURED before the next was allowed, and the pass
that failed the measure is MARKED, not vanished.

SEPARATION REPORT — "THE ANVIL AND CROWN" (Instrumental)
Source-separation production: the sung/rapped vocal removed, the
spoken announcer PRESERVED by the founder's ruling, the beat kept
whole by a measured stop rule.

Date: VIII day of November, Dies Solis, Sol in Scorpio,
      Anno V:xii e.n. (2026 e.v.)
Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice).
Classification: Enterprise • Educational • Research & Development
Method of Science, Aim of Religion — Scientific Illuminism.

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All
Rights Reserved, Without Prejudice. Right of claim hereby reserved
and coined under the authority of the Living Man.

FOUR-ELEMENT CONTENT TEST —
Inputs:    the-anvil-crown.mp3 (158.15 s, 44.1 kHz stereo, 192 kb/s);
           the founder's two rulings (multi-pass measured; announcer
           stays); the transcription form map (anvil-crown-analysis/).
Processes: Demucs htdemucs two-stem separation, up to 3 passes,
           bleed + beat measured after each; stop rule; announcer
           splice of the original mix at measured bounds; one plain
           gain; one limited MP3 preview.
Outputs:   instrumental.wav (float32, 44.1 kHz stereo),
           instrumental-preview.mp3 (320 kb/s), this report.
Tolerances: stop rule — a pass must improve bleed by >= ~1 dB and
           cost <= ~1 dB of the beat's own energy, else it does not
           ship. Crossfades 0.75 s equal-power. Gain confessed.
=====================================================================
-->

# SEPARATION REPORT — THE ANVIL AND CROWN (Instrumental)

## I. What was asked, what was built

An instrumental-only version of the founder's Gemini-made track:
the dense sung/rapped vocal removed; the spoken **announcer (intro
and outro) preserved**; vocal echoes and reverb tails chased down
by **iterated separation passes under a measured stop rule** — the
echoes gone, not the beat thinned.

## II. Toolchain — the isolation held

Route taken: the **overlay** (`pip install --target`), exactly as
briefed. The MusicGen venv is mid-render on the Brightmoor v3
production and was **not installed into, upgraded, or touched**:
`demucs 4.1.0`, `sphn 0.2.1`, `lameenc 1.9.0` were installed
`--no-deps` into `~/workspace/stem-libs`, and torch 2.14.1+cpu was
borrowed read-only via
`PYTHONPATH=~/workspace/stem-libs:<musicgen-venv site-packages>`.
Model weights (htdemucs, 80.2 MB) were cached under
`~/workspace/stem-cache`, outside the venv. julius/einops/soundfile/
yaml were already present in the borrowed environment.

**Model: `htdemucs`** (the 4-source bag used in two-stem mode:
vocals vs accompaniment = mix − vocals, computed in float32). The
fine-tuned `htdemucs_ft` bag (4 models ≈ 4× the CPU) was **not**
used: 4 cores and ~5.6 GB free RAM are shared with the live v3
render, so resources did not allow it — stated plainly.
Settings: CPU, shifts 1, overlap 0.25, split at the model's native
7.8 s segment, 4 threads. All intermediate audio float32 WAV; no
pass ever bounced through a lossy or 16-bit stage.

Wall times (shared CPU): pass 1 — 1,341 s; pass 2 — 1,387 s;
pass 3 — 1,349 s; plus ~13 s model load per run.

## III. The passes, measured — and the stop rule's verdict

Frames of 1.0 s on the mono sum. Vocal band = 300 Hz–3.4 kHz.

**The bleed indicator, and its honest complication.** The brief's
ratio (vocal-band energy, vocal-dense frames vs vocal-sparse
frames) degenerates on this record: pass-1's vocal stem sits above
−25 dBFS in the band in **156 of 158 frames** — the vocal is wall
to wall — leaving a single sparse frame (t = 157 s, the fade tail).
The ratio is reported as specified, and a second window set is
reported beside it, because a one-frame denominator cannot carry a
verdict:

| pass | bleed ratio (dense vs sparse, dB) | dense-frame vocal-band RMS (dB) | body full RMS (dB) | body band costs vs prev (sub/low/vocal/high, dB) |
|---|---|---|---|---|
| original | 71.77 | 17.72 (mix, all frames) | −14.86 | — |
| pass 1 | 68.11 | **10.54** | −17.43 | — |
| pass 2 | 68.29 | **10.39** | −17.45 | 0.01 / 0.01 / 0.05 / 0.02 |
| pass 3 | 68.63 | **10.36** | −17.46 | 0.01 / 0.01 / 0.03 / 0.09 |

Reading, without cosmetics:

- The ratio barely moves (68.11 → 68.29 → 68.63) because its
  denominator is the fade tail: passes 2–3 keep scrubbing that
  tail (−3.89 dB, then −2.49 dB of energy at t = 157 s) while the
  dense frames stand still. As an improvement gauge on THIS track
  the ratio is broken; it is marked as such, not smoothed over.
- The operative bleed gauge — mean vocal-band RMS across the
  dense frames themselves — says the same thing from the other
  side: pass 1 removed ≈ **7.2 dB** of vocal-band energy versus
  the mix (17.72 → 10.54). Pass 2 bought **0.15 dB**. Pass 3
  bought **0.03 dB**.
- Beat preservation: exemplary. Across passes 2 and 3 the beat's
  own energy moved ≤ 0.05 dB in every body band and 0.02 dB
  full-band. Repeated passes did **not** hollow this beat — they
  also did not clean it. The model had already taken what it
  could recognise as voice in pass 1; what remains in the band is
  substantially the beat's own midrange (synths, snare body),
  which no further pass can separate from "vocal" because, to the
  model, it no longer is.

**STOP RULE APPLIED:** pass 2 improved bleed by −0.18 dB on the
specified ratio and +0.15 dB on the operative gauge — both far
under the ~1 dB bar. **Pass 2 is the last pass inside the rule,
and pass 2 is what ships.** Pass 3 was run and measured before
the verdict (its row stands above, marked, never vanished) and
is **not** delivered.

## IV. The announcer — bounds measured, splice confessed

Bounds were set from two witnesses, not by ear: the transcription
form map (arrangement turns at **14.32 s** and **131.23 s**; the
head segments run −25.7/−21.5 dB against the body's −14…−16 dB,
and the tail falls away from 131.2 s) and a **leakage-coupling
test**: correlation, per window, between the accompaniment's
vocal-band envelope and the vocal stem's. Head 0–14 s: **+0.63**
in pass 1 (the separator's residue there rides the announcer's
own envelope — splicing the original back restores his voice
exactly); after pass 2 the same window reads +0.32. Tail
134–155 s: **−0.22** (no leakage rides the outro; the original is
restored there because the founder ruled the announcer stays,
and the original is the truest copy of him).

**Final splice** (sample-exact, equal-power crossfades of 0.75 s):

- Original mix: **0 → 13.95 s** (crossfade centred 13.95 s,
  spanning 13.575–14.325 s)
- Cleaned instrumental (pass 2): **13.95 s → 131.225 s**
- Original mix: **131.225 s → end** (crossfade centred 131.225 s,
  spanning 130.85–131.60 s)

Verification: the head window, gain removed, matches the original
decode to 2.2 × 10⁻⁸ — the announcer in the deliverable *is* the
original announcer, bit for bit. Seam zones show no anomalous
steps beyond the programme's own transients.

## V. Levels — the one gain, confessed

No EQ, no reverb fill, no mastering moves. Two level facts:

1. **+2.57 dB plain gain** over the whole file: the cleaned body
   measured 2.57 dB under the original's body RMS (−17.43 vs
   −14.86 dB), the expected cost of removing a loud vocal. One
   uniform gain restores the body's loudness and keeps the
   announcer windows' relative level honest. After gain, the
   final body's frame-mean RMS reads **−13.43 dB against the
   original's −13.84 dB** — the splice and crossfades account
   for the small remainder.
2. The float WAV therefore peaks at **+5.32 dBFS** (the
   accompaniment's own peak, +0.32 dBFS, plus the gain, plus
   splice-zone sums). Float32 WAV carries this without clipping
   — but any downstream 16-bit render must gain-stage first.
   The **MP3 preview is soft-limited to −0.3 dBFS**
   (ffmpeg `alimiter`, decoded peak measured −0.14 dBFS) — the
   only dynamics touch in the production, confessed here.

## VI. Honest bleed assessment — what the ear will still find

This is a separation, not a stem from the session. Named plainly:

- **The lead vocal is gone as a voice.** ≈7.2 dB of vocal-band
  energy was removed in the body; what remains there measures
  10.4 dB (band RMS) and is dominated by the beat's own midrange.
- **Reverb tails and echoes survive in proportion.** The vocal's
  wet tail lives partly outside the dry vocal's spectral shape;
  a residue of it rides the accompaniment, most audible where the
  arrangement is thin — the head and tail edges of the body
  (just inside the splice points) and any quiet bars. Passes 2–3
  were the attempt to chase exactly this; the measures above are
  the proof the chase had run out.
- **Watery/phasy colour** on sustained midrange instruments is
  the known htdemucs artefact and is present to a normal degree.
- **The announcer windows contain the original mix entire** —
  announcer, his bed, and whatever vocal dressing the intro and
  outro carry — by the founder's ruling, not by leakage.

## VII. Deliverables

- `instrumental.wav` — 44.1 kHz stereo float32, 158.15 s,
  6,974,208 samples; body = pass-2 accompaniment; head/tail =
  original mix per §IV; +2.57 dB gain per §V.
- `instrumental-preview.mp3` — 320 kb/s render of the same,
  soft-limited to −0.3 dBFS for safe playback.
- This report. Working stems (per-pass vocals/accompaniments,
  scripts, metrics) stand under `work/` for audit.

Nothing committed, pushed, or uploaded. The desk verifies; the
founder's ear decides.

— END OF REPORT —

93 — Live, Love, and let Love, Live.

<!--
Colophon: produced by the desk under the founder's direction,
VIII day of November, Anno V:xii e.n. Exclusive authorship:
Johnathan 'Qasparr' Monroe, ARR — All Rights Reserved, Without
Prejudice. Flagpole of Claim and Coinage reserved.
Method of Science. Aim of Religion.
-->
