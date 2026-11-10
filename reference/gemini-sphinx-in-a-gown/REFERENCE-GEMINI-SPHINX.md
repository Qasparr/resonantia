<!--
93
The intake record: measured profile of the founder's own Gemini
strike of the NIGHT SUN sheet, taken into the house 2026-11-10 under
his adoption ruling (Gemini strikes; the desk measures, masters,
notates, records). Local audio beside this file (not in git):
sphinx_in_a_gown_0_6snr.mp3 (as struck), master.wav, preview.mp3.
Authorship of the track: Johnathan 'Qasparr' Monroe (direction;
the bars of Verses I-II by Lady Lilith, the Mother Tongue),
generated in Gemini (Lyria). Measurements and master: the desk.
-->

# REFERENCE — "SPHINX IN A GOWN" (Gemini/Lyria, founder-struck)

## Provenance

On 2026-11-10 the founder fed Gemini the desk's production spec for
NIGHT SUN together with the sheet's Verses I–II
(`NIGHT-SUN-77-BARS.md`: Verse I "The Key", 27 bars; Verse II "The
Night Sun over the Strait", 27 bars — Lady Lilith, the Mother
Tongue) and struck the render himself. The file of record is his
upload: `sphinx_in_a_gown_0_6snr.mp3`, 3,027,972 bytes, SHA-256
`05062fff83ff…`, MP3, 44.1 kHz stereo, ≈192 kbps. It is a full
VOCAL performance of the two verses — voice, flow and arrangement,
the thing the local MusicGen stack cannot produce. The same day he
ruled the adoption: **Gemini becomes the vocal strike engine on
trial; the desk measures, masters to house law, notates, and keeps
the record.** This document is that record. Phase-1 transcription
(form, chords, melody sketch) rides beside it in `FORM-MAP.md`;
machine outputs in `analysis-stats.json`, `chords.csv`,
`melody-sketch.json`; the master and its confessions in
`manifest.json`.

## Measured profile (desk bench, 2026-11-10)

- Duration 125.91 s · programme proper to ≈118.5 s, then a fade:
  last 0.5 s window above −40 dBFS ends 123.0 s; the final ≈2 s are
  digital quiet.
- **Tempo — the performed beat is ≈100 BPM, and it does not drift.**
  House studio estimator (onset-flux autocorrelation, stated
  prior): headline **99.93 BPM**, dominant periodicity 99.38;
  candidates 99.38 (ac 0.587), 66.26 (0.574), 50.17 (0.569).
  30-s windows: **99.97 / 99.97 / 99.92 / 99.86 — spread 0.11 BPM**
  (the final 5.91 s tail is unmeasured, per the instrument's own
  10 s rule). That window flatness is the Anvil benchmark's
  signature virtue, present here in full.
- **The zero point between the house's two tempo instruments,
  reported, not smoothed.** The desk's first pass read dominant
  periodicity **132.5 BPM** from an RMS-block envelope; reproduced
  by that instrument in this pass at 132.51, strength 0.5008.
  132.5 ≈ 2 × 66.26 — the double-time hat/flow layer, itself a
  live candidate (0.574) under the flux instrument, whose raw
  autocorrelation reads 0.648 at 99.93 and 0.555 at 132.5. The two
  instruments hear two real layers of the same performance; the
  flux instrument's layer is the one the bars stand on (see
  FORM-MAP §1). **Both instruments agree on the only point the
  sheet ordered: at 144 BPM there is no clock** — flux ac 0.148,
  first-pass ac 0.009.
- Loudness as struck: house K-weighted ungated **−13.40 LUFS**,
  true peak **+0.01 dBTP**, sample peak −0.01 dBFS. Second witness,
  ffmpeg gated BS.1770: −13.1 LUFS, true peak 0.0 dBFS. The two
  scales agree within 0.3 LU / 0.01 dB — and both say the render
  arrived with no headroom at all.
- **Stereo: L/R correlation 0.9756 · side RMS −33.39 dBFS** —
  near-mono, and narrower than the Anvil bar (0.9293 / −28.8) by
  ≈4.6 dB of side energy. Programme windows hold corr 0.964–0.983
  throughout; only the dying tail decorrelates (0.558, at the
  noise floor).
- Dynamics alive: segment means travel −23.5 → −12.9 dB across
  the song (intro to refrain plateaus), ≈10.6 dB of weather.
- Form in one line (detail and tiers in FORM-MAP): intro 3 bars;
  verse spans; **three statements of one loud refrain plateau**
  (bars 10–12, 30–32, 44–46; mutual chroma recurrence up to
  +0.964) that the sheet never wrote — the model's own hook,
  invented in its plan; a breakdown dip at bars 37–39; outro and
  fade from ≈bar 47. Performed grid total: 53 bars at 99.93.
- Harmony in one line: centre **F** by every instrument (K-S
  global, per-bar templates, melody census); mode contested
  between the benches — K-S votes F major (0.816), the per-bar
  bench votes Fm over F by 16 bars to 7 among clear bars, 26 of
  53 bars UNCLEAR under a forward rap vocal. The sheet ordered
  F minor. Unresolved at phase 1, marked as such.
- **Sigma: NOT CERTIFIABLE, now with the probe's numbers.**
  Persistent-line probe at the doctrine pair (2 s windows,
  line-to-shoulder ratios): L @ 200 Hz — median 2.58 dB,
  persistence (> 6 dB) 0.113; R @ 213 Hz — median 4.76 dB,
  persistence 0.355. The certification bar (median ≥ 10 dB and
  persistence ≥ 0.90 in both channels) is not approached. What
  energy lives at 200/213 Hz belongs to the programme.

## The house master (manifest.json carries the full report)

- Law applied by `pipeline.master_signal`: loudness first, then
  the ceiling. **Gain −0.60 dB → −14.00 LUFS exactly; soft
  limiter; true peak −1.17 dBTP; trim 0.0 dB;
  `ceiling_overrode_loudness: false`.** Confessed plainly: the
  hot render's overs were sample-scale, and the gain to target
  plus the limiter's bend cleared the ceiling without the trim
  ever firing — the ceiling is law, and this time the law was
  not needed. Verified from the struck file on disk: 48 kHz,
  125.91 s, −14.00 LUFS, −1.17 dBTP.
- **Width: LEFT AS STRUCK** (corr 0.9756 in, 0.9756 out). No
  stems exist; any widening on this desk would move the centred
  vocal with the bed. In doubt, leave it — the doubt was real.
- **NO Sigma layer added.** Whether Sigma rides a Gemini strike
  is the founder's open call; the desk does not presume it.
- No EQ, no fades, no edits: the waveform is the performance as
  struck, gained and ceilinged only. `master.wav` (48 kHz,
  24-bit) and `preview.mp3` (320k) beside this file; audio stays
  local, per the house rule for rented-engine references.

## The three measured off-spec items

1. **Tempo.** The sheet ordered a 144-tempo hat flow. The
   performed beat stands at ≈99.9 BPM (house instrument) with a
   strong double-time layer at 132.5 (first instrument); under
   neither instrument does a clock run at 144 (ac 0.148 / 0.009).
2. **Hot and narrow as delivered.** True peak +0.01 dBTP on a
   −0.01 dBFS sample peak — zero headroom — at correlation
   0.9756 and side RMS −33.4 dBFS, against the house bar's −28.8.
   The master repairs the headroom; the narrowness stands, by
   the width confession above.
3. **Sigma not certifiable.** The ordered 13–31 Hz binaural
   ground cannot be certified in the render by the stated probe
   (see above), and none was added after the fact.

## What the house takes from it

1. Plan-first, single-pass generation coheres here exactly as it
   did in the Anvil: a window series flat to 0.11 BPM and a form
   with genuine recurrence — the model composed a hook the sheet
   never asked for and then *returned to it*, three times.
2. The adoption division of labour is already visible in the
   numbers: Gemini supplies the performance no local engine here
   can sing; what it does not supply is the sheet's tempo, any
   headroom, width, or the Sigma ground. Those four are the
   desk's crafts — three exercised in this intake, the fourth
   (Sigma) awaiting the founder's word.
3. The sheet travels with the song from here: phase-1 notation
   stands in FORM-MAP at the strength the audio supports, its
   UNCLEAR bars left empty in the open.

93 — Live, Love, and let Love, Live.
