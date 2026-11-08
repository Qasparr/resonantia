<!--
93
The Tools Wing — founder's order 2026-11-07 (19:47 EST), recorded by the
desk as an engineering spec. Build queues as the studio phase AFTER the
pipeline proof verifies (RESONANTIA-on-automatic standing order).
Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice).
-->

# THE TOOLS WING — tempo, pitch, beat arithmetic, repair, vocal correction

The founder's order, in his words: *"make the proper tools for applying
tempo, pitch, and for making the arithmetic work in beats. Like fixing
tears, pops, and cracks, or pronunciation errors by the vocal tracks
(not slang or accent but like where you can tell it was voiced by a
machine. There is known algorithms to fix these im sure. We want all
those tools or filters to be in resonantia."*

## A. TEMPO, PITCH, AND THE ARITHMETIC OF BEATS

- **Pitch** — exists in the engine (`resonance/pitch.py`); the wing
  verifies and hardens it, and adds **formant-preserving** shifting
  (see C) so shifted voices keep their body.
- **Tempo** — NEW: time-stretch with pitch held (phase-vocoder and
  WSOLA paths; WSOLA for speech/transient material, phase vocoder for
  tonal material), plus pitch-shift with tempo held.
- **Beat arithmetic** — NEW `grid` tools: sample-exact beat/bar math
  (BPM + sample rate → samples per beat, per bar); loop trim/pad to
  whole bars; drift measurement against the grid; the existing
  `resonance/quantize.py` is the note-timing arm of the same doctrine:
  *the arithmetic must close* — a loop that claims 4 bars IS 4 bars,
  to the sample.

## B. REPAIR — tears, pops, cracks (`repair` tools)

Known algorithms, as the founder said — this is a solved family:

- **De-click / de-pop:** detect transient outliers (short, loud,
  broadband), excise, and bridge the gap by autoregressive (AR)
  interpolation — the Janssen method family — which rebuilds the
  waveform from the signal's own statistics on both sides of the hole.
  Short gaps take LP/cubic bridging; the tool chooses by gap length.
- **Tear repair:** longer dropouts bridged by spectral/LP inpainting
  with equal-power crossfades at the seams.
- **De-crackle:** median-filter detection of the crackle floor
  (the vinyl family), attenuated without touching the programme.
- **De-clip:** soft reconstruction of clipped peaks (spline/LP
  extrapolation over the flat-top), plus DC-offset removal.

## C. VOCAL CORRECTION — removing the machine's tells (`vocal` tools)

Scope, stated plainly per the founder's own boundary: **not slang, not
accent** — those are the artist. The target is the set of artifacts by
which a listener can tell a vocal *was voiced by a machine*:

- **Pitch-contour humanization:** machine vocals ride quantized,
  unnaturally steady pitch. The tool restores micro-drift, natural
  attack scoops, and controlled vibrato, from the contour's own
  statistics.
- **Formant correction:** pitch processing that drags formants with it
  makes the chipmunk/mask voice. Formant-preserving correction (and
  formant re-seating after a shift) removes that tell.
- **Jitter/shimmer normalization:** cycle-to-cycle pitch and amplitude
  instability outside the human band is smoothed toward human ranges.
- **Spectral de-buzz:** envelope smoothing over the buzzy, over-even
  harmonic stacks synthesis leaves; breath/presence layer restored at
  low level so the voice sits in air again.

**Honest boundary (desk, marked):** replacing a wrongly-pronounced
*phoneme* with a different phoneme is not a filter — it needs
recognition + resynthesis (a heavy ML build, a different wing). What
this wing removes is the *voicing* tells — the machine sound the
founder named — which is where "you can tell it was voiced by a
machine" actually lives.

## D. THE --retro CONTEXT

Filed alongside the founder's --retro rule (same night): the classic
16-bit MIDI/soundfont path stays intact for notifications, ringtones,
retro game soundtracks and SFX — work it does *very well*, his words.
The tools of this wing serve both paths: repair and grid arithmetic
are path-agnostic; the vocal tools belong to the HD path.

## BUILD ORDER

1. Grid arithmetic + tempo (the arithmetic must close first).
2. Repair (de-click/de-pop, tear, de-crackle, de-clip).
3. Vocal correction (humanization, formants, jitter/shimmer, de-buzz).
Each lands with tests in the house style; the wing ships when the
studio proof has verified, per the automatic-advance standing order.

93 — Live, Love, and let Love, Live.
