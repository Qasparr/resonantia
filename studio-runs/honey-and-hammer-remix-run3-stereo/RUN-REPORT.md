# HONEY AND HAMMER — THE EXPLICIT REMIX: RUN 3 — THE STEREO RE-RENDER

**XV day of November, 2026 e.v. — Resonantia studio, run 3.**
**Order (the founder's ear verdict on run 2):** *"Something's off — make it full stereo and Dolby rendered."*
**Result: he was right, and the ruler says exactly what was off. Run 2 was a mono record in a stereo container. Run 3 is the same song — same 74 line renders, same kit, same chain — on a real stage: correlation +0.9985 → +0.490, side energy 0.08% → 25.49%, mastered to house law, plus a true HRTF binaural headphone render. The "Dolby" part is answered at full size in its own section below: what can and cannot be done on this box, with coordinates.**

---

## STEP 1 — DIAGNOSIS, BEFORE ANYTHING WAS TOUCHED

Run 2's struck files, measured on the mid/side ruler (M = (L+R)/2, S = (L−R)/2):

| run 2 file | L/R corr | RMS L | RMS R | side − mid | side energy |
|---|---|---|---|---|---|
| master | **+0.9985** | −15.40 | −15.41 | −31.13 dB | **0.08%** |
| vocal stem | +0.9962 | −23.04 | −23.00 | −27.22 dB | 0.19% |
| backing stem | **+1.0000** | −21.00 | −21.00 | −219 dB (nil) | **0.00%** |

Windowed correlation of the run 2 master never leaves +0.99 across the whole song. The cause is in run 2's own build script, at full size: **every backing element was placed at pan 0.0** — kick, snare, clap, hats, rimshot, 808, and the pad (a mono stack) — so the backing stem is bit-for-bit dual-mono. The vocal fares no better: all 60 verse lines at pan 0.0, and only the hook's ±0.1 / ±0.15 pans produce the stem's entire 0.19% of side energy. Nothing was broken and nothing clipped; the mix simply had **no stage** — every voice and every instrument stacked on the centre line. That is the "something off" the ear caught, measured.

## STEP 2 — THE STEREO RE-MIX (from run 2's lines and kit; nothing re-sung)

Only the stage picture changed. Lines, kit one-shots, 808 voice, pad synthesis, staging targets (backing −21.0 / vocal −20.5 dBFS RMS), and the Four Powers settings are run 2's, verbatim.

**Backing placement:** kick and the 808 spine stay centred — the low end is mono by law. Snare centred. Clap split into a stereo pair (−5 ms / +7 ms around the step, pan ∓0.40). Closed hats walk a pan pattern (−0.45 / +0.35 / −0.30 / +0.50 across the bar); open hat +0.60; rimshots ∓0.50. The pad is now two independently detuned harmonic stacks — one per ear (L: −5/+3 cents through a 1.0 kHz lowpass; R: −3/+5 cents through 1.2 kHz) — over a quieter centre core (0.013 against the stacks' 0.058).

**Vocal placement:** hook call-and-response widened from ±0.1 to **∓0.35** (Quoll left, Phascogale right); the "(both)" doubles split to **∓0.55**. Verse features stay centred dry — a rap verse sits in the middle — but every section now carries a **stereo room tail**: a synthetic stereo impulse (decorrelated decaying noise, one per ear, 20 ms predelay) convolved as a send — verses −13 dB, hook −15 dB, outro −11 dB. The outro is layered wide: Quoll −0.5 / Civet +0.5 over the hook chant at ∓0.3.

**After, same ruler:**

| run 3 file | L/R corr | RMS L | RMS R | side − mid | side energy |
|---|---|---|---|---|---|
| **stereo master** | **+0.490** | −15.53 | −15.36 | **−4.66 dB** | **25.49%** |
| vocal stem (stereo) | +0.045 | −22.00 | −21.44 | −0.39 dB | 47.74% |
| backing stem (stereo) | +0.953 | −20.93 | −21.07 | −16.17 dB | 2.36% |

Read honestly: the vocal stage is now genuinely wide (the room tails decorrelate it almost completely; the hook reads as two people across a room, the verses stay centred in the dry with the room around them). The backing's *placement* is spread but its *energy* stays centre-anchored — corr +0.953 — because the centred kick, 808, and snare carry the record's weight, which is how a bounce record is built; its width lives in the hats, the clap pair, the rimshots, and the pad edges. Windowed correlation of the master runs +0.37…+0.63 through the song — the image breathes by section instead of sitting at 1.000.

**Master — the Four Powers, run 2's settings:** Scire premix −16.29 LUFS · crest 18.0 dB · Velle engaged (same EQ; comp GR max 9.19 / mean 4.23 dB) · Vapour idle, not ordered · Audere +6.91 dB, ceiling did not override loudness · Tacere TPDF dither (seed 32016), headroom 0.60 dB. **Final, read back from the struck file: −14.0 LUFS integrated · −1.61 dBTP · 175.5 s · 48 kHz / 24-bit.** The true peak sits 0.6 dB under the −1.0 ceiling rather than on it (run 2 read −1.03): the wider image's peak structure differs, the ceiling is a ceiling, and the delivered number is the measured one. Metering map: `#A8EEBF0D`.

**BOVNCE 320K, verified from the file:** MP3 (libmp3lame CBR) — **ffprobe reads exactly 320,000 bps** · 48 kHz · 7,022,445 bytes · decoded read-back −14.0 LUFS · −1.60 dBTP · image identical to the WAV (corr +0.490, side 25.49%).

## STEP 3 — "DOLBY RENDERED," AT FULL SIZE

**True Dolby Atmos authoring cannot be done on this box, and no file in this run is Dolby or Atmos.** Atmos delivery is an ADM BWF master rendered by Dolby's licensed renderer (the Dolby Atmos Renderer / production suite). That renderer is licensed commercial software; it is not installed here, and renting or subscribing to it is barred by the founder's standing non-rented rule for this bench. Those are the coordinates — the wall is a licence, not a capability of the room. Any file labelled "Dolby" or "Atmos" that this studio could produce today would be a false label, so none carries it.

**What was delivered instead — a binaural render, which is the form in which Atmos mixes are most often actually judged** (headphones): the stereo master convolved through a measured HRTF set with ffmpeg's `sofalizer` (libmysofa) using the **MIT KEMAR** dummy-head set on this box (`/usr/share/libmysofa/MIT_KEMAR_normal_pinna.sofa`), frequency-domain mode, the two channels rendered as virtual loudspeakers at ∓30°. The render was struck at the SOFA set's native 44.1 kHz, resampled to 48 kHz, given one constant gain, and TPDF-dithered (seed 32017). Its image on the ruler: correlation **−0.266**, side energy **63.28%** — properly decorrelated, outside-the-head placement on headphones, exactly what a binaural render should measure.

**Its one limit, printed:** the binaural sits at **−17.77 LUFS · −1.05 dBTP**, not −14.0. HRTF convolution raises crest factor; from the raw render (−19.44 LUFS · −2.72 dBTP) the ceiling-bound gain was +1.67 dB before the −1 dBTP ceiling bound. Reaching −14.0 would take a second limiting pass over the spatial render — a re-master of the binaural itself — and this run does not silently re-master a render; the binaural is delivered as a pure render of the house-law stereo master, 3.8 dB under house loudness, ceiling intact. The closing move, if the founder orders it, is named: one Audere pass over the binaural, at the cost of its dynamics. Binaural MP3: **320,000 bps verified**, decoded −17.77 LUFS · −1.04 dBTP.

## THE DELIVERABLES (this directory)

| file | what it is |
|---|---|
| `honey-and-hammer-explicit-remix-stereo-resonantia.wav` | **the stereo master** — 48 kHz · 24-bit · 175.5 s · −14.0 LUFS · −1.61 dBTP · corr +0.490 · side 25.49% |
| `honey-and-hammer-explicit-remix-stereo-320k.mp3` | the stereo BOVNCE 320K export — 320,000 bps verified from the file |
| `honey-and-hammer-explicit-remix-binaural.wav` | **the binaural headphone render** (KEMAR HRTF) — 48 kHz · 24-bit · −17.77 LUFS · −1.05 dBTP · corr −0.266 |
| `honey-and-hammer-explicit-remix-binaural-320k.mp3` | the binaural 320K export — 320,000 bps verified |
| `vocal-stem-stereo.wav` / `backing-stem-stereo.wav` | the run 3 stems, 24-bit, peak-safe prints |
| `binaural_raw.wav` | the unfinalized sofalizer render at the SOFA set's native 44.1 kHz (intermediate, kept for the record) |
| `build_run3.py` / `binaural_finalize.py` | the run's drivers — reproducible |
| `run_data.json` | every measurement cited above, machine-readable |

Audio stays out of git; this report, the drivers, and the run data are what commit.

## THE WALLS, WITH COORDINATES (what run 4 inherits)

1. **The Atmos wall is a licence wall** (Step 3): Dolby's renderer, not installed, not rentable under the house rule. The binaural is the honest headphone deliverable until that changes.
2. **The binaural's 3.8 dB** — ceiling-bound as printed; closing it means an Audere pass over the render, founder's call.
3. **Backing width is placement-wide, energy-centred** (corr +0.953): the low end and snare hold the middle by design. If the ear wants the *bed itself* wider, the next move is stereo drum overheads/room on the kit — the struck kit is mono one-shots, so that is a kit question, not a pan question.
4. **Standing from run 2, unchanged:** three bank speakers for five personas; rap-delivery credibility is the founder's ear call, ungraded; the pad and the outro note remain synthesized (no soundfont on the box).

**Self-sufficiency verdict:** diagnosed on the ruler, re-mixed from the house's own stems and lines, re-mastered through the Four Powers to house law, exported at the verified 320K spec, and spatially rendered through an open HRTF set — no account, no rental, no network call, and no false label anywhere on it.

**Per the sheet: this is not a bookshop item** — no listing, no price; the original single stands at $2.50 as issued. Any listing is a separate ruling of the founder's.

**Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All Rights Reserved, Without Prejudice. Right of claim hereby reserved and coined under the authority of the Living Man.**

93 — Live, Love, and let Love, Live.
