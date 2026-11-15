# SPEAR AND MAGICKAL HELM — FIRST SELF-SUFFICIENT RUN: RUN REPORT

**XV day of November, 2026 e.v. — Resonantia studio, run 1.**
**Order:** *"Sheet Music and Try the first self sufficient run."*
**Result: a complete master, struck end-to-end on the house road — nothing rented, nothing external, nothing downloaded.**

Spec (fixed): **G minor · 92 BPM · 4/4 · chord loop Gm – Gm – E♭ – F, one bar each · outro over Gm.** Structure as run: 26 bars — hook section 8 bars (sung lines on bars 1–6), verse 1 across 16 bars, outro 2 bars. Lyrics performed **exactly as written** on the track sheet (`docs/SPEAR-AND-MAGICKAL-HELM-REDRVM-3D1TION.md`, ghost drafts) — not one word altered; the only desk work on the text is pronunciation (hand phonemisation into the bank's `en/*` ARPAbet tokens).

---

## THE DELIVERABLES (this directory)

| file | what it is |
|---|---|
| `spear-and-magickal-helm-resonantia.wav` | **the master** — 48 kHz · 24-bit · 68.326 s · **−14.0 LUFS integrated · −1.08 dBTP** (read back from the struck file) |
| `vocal-stem.wav` | the vocal stem, 24-bit, printed peak-safe at −1.00 dBFS (print gain −3.27 dB, recorded in `run_data.json`) |
| `backing-stem.wav` | the backing stem, 24-bit, peak −9.19 dBFS |
| `render_vocal.py` / `build_run.py` | the run's two drivers — the run is reproducible from these |
| `lines/` + `lines_manifest.json` | the 28 rendered vocal lines (44.1 kHz) and their score record |
| `run_data.json` | every measurement cited below, machine-readable |

Audio stays out of git (lab precedent); this report and the drivers are what commit.

---

## STAGE 1 — SCORE · **PASS, with one flag**

No sheet-builder MIDI had landed at `compositions/spear-and-magickal-helm/` when the run began (the directory did not exist), so the chant melodies were **composed in-house to the fixed spec** and are flagged as such: hook = narrow chant in G minor (G3–F4, chord-aware per bar), verse 1 = rhythmic chant on G3 with A3 penultimate lifts and F3/G3 line-final falls. When the engraved sheet's MIDI lands, a conformance pass can re-voice the melodies note-for-note; the words, grid, and structure will not change.

## STAGE 2 — VOCAL · **RENDERED COMPLETE — one credibility flag, carried open**

Road: **DiffSinger** (OpenVPI code, Apache 2.0) + **Lem the Shapeshifter DS 2.5** bank (licence-clean; its terms permit commercial use), English phoneme path, driven directly on CPU — the Wave F pipeline, stage-batched. Speakers: **Civet** (hook lead + all of verse 1), **Quoll** (hook unison layer, −7 dB, panned opposite).

- **28 of 28 lines rendered.** No missing lines, no overhang past any bar line.
- Line levels even: RMS −27.4 … −31.7 dBFS across all 28.
- Pitch follows the score: spot-measured F0 medians — hook 1: 211 Hz vs 220 scored · hook 4: **262 vs 262** · verse 1: **196 vs 196** · verse 14: 196 vs 196 · verse 16: 196 vs 196 (YIN reads a few Hz low on breathy frames; the vocoder is fed the score F0, so pitch is score-determined).
- **Wall 1 — duration compression (measured, coordinates given):** the duration model returns ≈87% of the frame budget it is handed, uniformly — every line lands 2.19–2.31 s against its 2.61 s bar. Lines were placed at bar starts, so the grid holds and the shortfall reads as a ~0.3 s breath at each line end. A run-2 calibration (scale budgets ×~1.15) is the known fix; it was not applied silently here.
- **Wall 2 — the verse is sung chant, not rap (the honest flag):** verse 1 was attempted in full as rhythmic chant and **technically carried** — all 16 lines on the 16th-weighted grid, no collapse even at 15 syllables to the bar (verse 14). But DiffSinger *sings*: vowels sustain where rap would spit. Whether this chant carries as a verse is **the founder's ear call, flagged here, not decided by the desk.** The vocal stem is a separate file precisely so an instrumental-verse mix is one mute away.
- Carried over from Wave F: the variance model's voicing output sits on its known unnormalized scale (line means −32 … −42). Renders are stable regardless; the calibration item stands open, unchanged, not tuned silently.

## STAGE 3 — BACKING · **PASS, with one confessed synthesis**

Detroit bounce at 92 BPM, swung 16ths (swing 0.14), deep kick, snap:

- **Drums — rendered audio, house provenance:** the studio's struck kit from `studio-runs/v4-proof-3/kit/` (MusicGen-small rendered one-shots, selected by measurement 2026-11-08) — kick, snare, clap, closed/open hats, rimshot — placed on the grid. Nothing note-synthesized, per the house doctrine the founder's ear set.
- **Bass — the studio's own voice:** `spine.bass808` on the loop roots (G1 · E♭1 · F1), three hits per bar riding the kick pattern.
- **Pad — SYNTHESIS, CONFESSED:** chord triads (Gm: G3 B♭3 D4 · E♭: G3 B♭3 E♭4 · F: F3 A3 C4) built from detuned harmonic stacks through a scipy lowpass. There is **no fluidsynth and no soundfont on this box** (checked), so the pad is the run's one synthesized layer — named here at full size so the founder can strike it, exactly as the kit doctrine requires.
- **Outro (bars 25–26, Gm):** the bounce drops out as the sheet directs — kick + one long 808 + fading pad. The sheet's *"single piano note"* is a synthesized decaying G3 strike: **no piano exists on this box** — wall, with coordinates (a soundfont or a struck MusicGen piano one-shot for the kit is the run-2 fix).

## STAGE 4 — MIX · **PASS, staged hot — reported, not hidden**

Staging: backing bed −21.0 dBFS RMS, vocal −18.0 dBFS RMS (vocal +14.76 dB of gain from its raw lines; backing −11.96 dB). **The premix peaked at +3.18 dBFS** — legal in the float domain (nothing clipped), but hot: Velle's compressor spent real gain reduction taming it (below). Run-2 should stage the vocal ~3 dB lower and let the chain polish instead of wrestle.

## STAGE 5 — MASTER: THE FOUR POWERS · **PASS — HOUSE LAW MET**

| power | reading |
|---|---|
| **SCIRE** (Know) | premix measured before any touch: −14.45 LUFS · +3.18 dBTP · crest 19.42 dB |
| **VELLE** (Will) | engaged — EQ: +1.5 dB peak @ 3 kHz, +1.0 dB highshelf @ 8 kHz · comp 2:1 over −18 dB, knee 6 — measured GR max 10.5 dB / mean 4.15 dB · stage RMS Δ −5.69 dB |
| **VAPOUR** | **not engaged** — no saturation was ordered; the stage stood idle and says so |
| **AUDERE** (Dare) | gain +6.36 dB → soft limit → ceiling trim 0.00 dB — **the ceiling did not override the loudness** |
| **TACERE** (Silent) | delivered true peak −1.08 dBTP against the −1.0 ceiling (headroom 0.08 dB) · TPDF dither at the 24-bit word, seed 31013 |

**Final, read back from the struck file: −14.0 LUFS integrated · −1.08 dBTP · 68.326 s · 48 kHz / 24-bit.** Metering map (display convention): `#B2F4CE02`.

---

## WHAT A FULL-TRACK RUN STILL NEEDS (the open list)

1. **Verses 2–3 and the outro chant** — out of this run's scope by the order's own staging (hook + verse 1 first). The pipeline now takes a line in ~15 s of compute; the remaining 34 lines are a batch, not a research problem.
2. **A house voice.** Lem sings well and its licence is clean, but it is a borrowed singer. Qasparr's own bank (trained or licensed) remains the road's end, as the Self-Sufficiency Register already records.
3. **True rap delivery.** DiffSinger sings; if the founder's ear refuses the verse chant, the verse road is a performance engine question, reopened with this run's measurements on the table.
4. **The engraved sheet's MIDI** — melody conformance pass when it lands.
5. **A piano** (soundfont or struck one-shot) for the outro note, and optionally a rendered pad to retire the confessed synthesis.
6. **Duration calibration** (×~1.15 budget scale) and **cooler mix staging** (−3 dB vocal) — both measured here, both cheap.

**Self-sufficiency verdict:** every stage of this master — score, voice, drums, bass, pad, mix, mastering, measurement — ran on this box, on house or licence-clean tools, with no account, no rental, and no network call. The register's dependence (1), the sung voice, narrows accordingly: *performed* is no longer Gemini-only for a first render — with the verse's credibility flag flying openly above it.

**Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All Rights Reserved, Without Prejudice. Right of claim hereby reserved and coined under the authority of the Living Man.**

93 — Live, Love, and let Love, Live.
