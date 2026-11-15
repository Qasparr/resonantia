# HONEY AND HAMMER — THE EXPLICIT REMIX: RUN 2 — RUN REPORT

**XV day of November, 2026 e.v. — Resonantia studio, run 2.**
**Order:** *"print that next… Raw uncut xxxrated and dirty bounce… variables controlled by resonantia."*
**Result: the full remix, printed end-to-end on the house road — every section rendered, mastered to house law, and exported at the BOVNCE 320K spec. Nothing rented, nothing external, nothing downloaded.**

Spec (Resonantia variables, from the sheet): **G minor · 96 BPM · 4/4 · swung 16ths (0.14) · chord loop Gm – E♭ – B♭ – F, one bar each · 808 spine on the loop roots.** Structure as printed on the sheet: **70 bars** — hook 8, five 12-line sections (Sol Rey · Ari Sparkz · Qasparr feature · Sage Archer · Qveen Bee closing feature), outro chant 2. Lyrics performed **verbatim** from `docs/HONEY-AND-HAMMER-EXPLICIT-REMIX.md` (ghost drafts) — not one word altered, softened, or cleaned; the desk's only work on the text is pronunciation (hand phonemisation into the bank's `en/*` ARPAbet tokens).

---

## THE DELIVERABLES (this directory)

| file | what it is |
|---|---|
| `honey-and-hammer-explicit-remix-resonantia.wav` | **the master** — 48 kHz · 24-bit · 175.5 s · **−14.0 LUFS integrated · −1.03 dBTP** (read back from the struck file) |
| `honey-and-hammer-explicit-remix-320k.mp3` | **the BOVNCE 320K export** — MP3 (libmp3lame CBR), **bitrate read back from the file: 320,000 bps exactly** · 48 kHz · 175.5 s · 7,022,445 bytes · decoded read-back −14.0 LUFS · −1.04 dBTP |
| `vocal-stem.wav` | the vocal stem, 24-bit, printed peak-safe at −1.00 dBFS (print gain −2.52 dB, recorded in `run_data.json`) |
| `backing-stem.wav` | the backing stem, 24-bit, peak −8.25 dBFS (print gain 0.00 dB) |
| `render_vocal.py` / `build_run.py` | the run's two drivers — the run is reproducible from these |
| `lines/` + `lines_manifest.json` | the 74 rendered vocal lines (44.1 kHz) and their score record, incl. handed/nominal/rendered frame counts per line |
| `run_data.json` | every measurement cited below, machine-readable |

Audio stays out of git (lab precedent); this report, the drivers, the manifest, and the run data are what commit.

---

## STAGE 1 — SCORE · **PASS**

The sheet *is* the score: hook composed as a chord-aware chant in G minor (G3–F4, peaks on the stressed syllables — "bounce" D4, "down"/"again" E♭4, the final "friend" F4); verses and outro as the run-1 rhythmic chant cell (base note, +3 head lift on even lines, +2 penultimate lift, −2 final fall on odd lines), transposed per persona register (below). No conformance flag this run: unlike run 1, the words, grid, and structure all come from a sheet that already existed when the run began.

## STAGE 2 — VOCAL · **RENDERED COMPLETE — the standing credibility flag, carried open**

Road: **DiffSinger** (OpenVPI, Apache 2.0) + **Lem the Shapeshifter DS 2.5** (licence-clean), English phoneme path, CPU, stage-batched as in run 1.

**Speaker map** (the bank holds **three** speakers; the song names **five** personas — the two reuses are differentiated by chant register and are named here at full size):

| persona | bank speaker | register | sections |
|---|---|---|---|
| Qveen Bee | **Quoll** | base G3 (55) | hook lead lines 1·3·5·7, half of "both" lines 6·8, closing feature (12) |
| Sage Archer | **Phascogale** | base A3 (57) | hook responses 2·4, half of "both" lines 6·8, verse 3 (12) |
| Sol Rey | **Civet** | base G3 (55) | verse 1 (12) |
| Ari Sparkz | **Civet** *(reuse)* | base D3 (50) | verse 2 (12) |
| Qasparr | **Phascogale** *(reuse)* | base C3 (48) | feature (12) |
| Whole crew (outro) | Quoll + Civet layered | 55 / 50 | outro chant (2 lines × 2 voices) |

The hook's call-and-response is genuinely two voices — Quoll asks, Phascogale answers — panned −0.1 / +0.1; the "(both)" lines are both speakers layered at ±0.15. The outro adds the sheet's own texture: the hook chant at half volume underneath (hook 1 and hook 2 re-placed at bars 68–69, gain 0.45).

- **74 of 74 renders complete.** No missing lines. Every section of the sheet is on the master: hook (10 renders), all five 12-line sections (60), outro (4).
- Line levels: RMS −34.7 … −22.5 dBFS across the 74 (a wider spread than run 1 — the low end is the low-register Qasparr chant and the short outro lines; the vocal bus is staged as one, per below).
- Pitch follows the score exactly: spot-measured F0 medians — hook 1 **220 vs 220 Hz** · sol 1 **196 vs 196** · qas 1 **131 vs 131** · qveen 12 **196 vs 196** (the vocoder is fed the score F0; pitch is score-determined).
- **Run-1 lesson applied — duration calibration ×1.15: MEASURED, LANDED.** Run 1's model returned ≈87% of the budget it was handed. Here every `word_dur` was scaled ×1.15 before the model saw it. The manifest's totals: rendered **15,878** frames against nominal (uncalibrated) **15,901** — a ratio of **0.9986**, i.e. lines now fill their bars (mean rendered line 214.6 frames vs the 215.3-frame bar). Against the calibrated hand-in the model's intrinsic return reads 0.8661, consistent with run 1's ≈0.87 — the compensation cancels it almost exactly. **The calibration is confirmed and can stand as the bench constant.**
- **The calibration's flip side, reported not hidden:** with lines now filling the bar, 21 placements overhang their bar line by **0.019–0.077 s** (worst: qas 3, 77 ms) — the tail of a line breathing into the next bar's 40 ms lead-in. No line is cut; nothing collides audibly at these magnitudes, but the coordinates are printed (full list in `run_data.json`) so the founder's ear judges with the map in hand. Run 1's alternative was 0.3 s of dead air at every line end; this is the tighter trade.
- **The standing flag (not graded here, by the order's own terms):** DiffSinger *sings*. The verses are rhythmic chant, technically carried — every line on the grid, no collapse at 16 syllables to the bar (sol 11). Whether the chant carries as rap, and whether the two register-shifted speaker reuses read as distinct personas, are **the founder's ear calls**, flagged, not decided by the desk. The vocal stem is a separate file precisely so an instrumental-verse mix is one mute away.
- Carried over from Wave F / run 1, unchanged: the variance model's voicing output sits on its unnormalized scale (line means −47.2 … −29.9 this run). Renders are stable regardless; the calibration item stands open, not tuned silently.

## STAGE 3 — BACKING · **PASS, with the standing confessed synthesis**

Detroit bounce at 96 BPM, swung 16ths (0.14, run 1's start point), deep kick, snap:

- **Drums — rendered audio, house provenance:** the studio's struck kit from `studio-runs/v4-proof-3/kit/` (MusicGen-small rendered one-shots, selected by measurement 2026-11-08), placed on the grid — same pattern family as run 1, verse sections carrying the extra step-14 kick and step-7 rimshot.
- **Bass — the studio's own voice:** `spine.bass808` on the loop roots (**G1 · E♭1 · B♭1 · F1** — the B♭ is new to this song's loop), three hits per bar riding the kick pattern.
- **Pad — SYNTHESIS, CONFESSED (standing wall):** chord triads (Gm: G3 B♭3 D4 · E♭: G3 B♭3 E♭4 · B♭: F3 B♭3 D4 · F: F3 A3 C4) from detuned harmonic stacks through a scipy lowpass. There is still **no fluidsynth and no soundfont on this box** (re-checked for this run), so the pad remains a synthesized layer — named at full size, as the kit doctrine requires.
- **Outro (bars 68–69):** the sheet's direction followed literally — **the 808 line drops out entirely**; one kick at bar 68, the hook chant at half volume under the crew chant, and a single note. The note is a synthesized decaying G3 strike: **no piano exists on this box** — run 1's wall, standing, with the same fix named (a soundfont or a struck piano one-shot for the kit).

## STAGE 4 — MIX · **PASS — staging cooler, one recorded trim**

Staging (run-1 lesson applied): backing bed −21.0 dBFS RMS, **vocal −20.5 dBFS RMS** (run 1 staged the vocal at −18 and the premix peaked +3.18 dBFS). The vocal bus still crests on stacked hook doubles: premix peak **+2.70 dBFS before trim** — legal in float, nothing clipped — and the run's recorded guard trim of **−2.20 dB** brought the premix to **+0.50 dBFS peak / −19.94 dBFS RMS** before the chain. The trim is in `run_data.json`, not buried. Velle's compressor consequently worked less than run 1 (GR max 9.32 / mean 2.97 dB, against run 1's 10.5 / 4.15).

## STAGE 5 — MASTER: THE FOUR POWERS · **PASS — HOUSE LAW MET**

| power | reading |
|---|---|
| **SCIRE** (Know) | premix measured before any touch: −18.40 LUFS · +0.54 dBTP · crest 20.44 dB |
| **VELLE** (Will) | engaged — EQ: +1.5 dB peak @ 3 kHz, +1.0 dB highshelf @ 8 kHz · comp 2:1 over −18 dB, knee 6 — measured GR max 9.32 dB / mean 2.97 dB · stage RMS Δ −3.61 dB |
| **VAPOUR** | **not engaged** — no saturation was ordered; the stage stood idle and says so |
| **AUDERE** (Dare) | gain +8.15 dB → soft limit → ceiling trim 0.00 dB — **the ceiling did not override the loudness** |
| **TACERE** (Silent) | delivered true peak −1.03 dBTP against the −1.0 ceiling (headroom 0.03 dB) · TPDF dither at the 24-bit word, seed 32015 |

**Final, read back from the struck file: −14.0 LUFS integrated · −1.03 dBTP · 175.5 s · 48 kHz / 24-bit.** Metering map (display convention): `#9DF4D901`.

## STAGE 6 — EXPORT: BOVNCE 320K · **PASS — VERIFIED FROM THE FILE**

The master was encoded with ffmpeg / libmp3lame at 320 kbps CBR, 48 kHz. **The bitrate was read back from the struck file with ffprobe: 320,000 bps — the spec, exact, not the encoder's promise.** Decoded read-back of the MP3 itself: **−14.0 LUFS integrated · −1.04 dBTP · 175.5 s · 7,022,445 bytes.** The MP3 holds house law through the codec.

---

## THE WALLS, WITH COORDINATES (what run 3 inherits)

1. **Three bank speakers, five personas.** Civet doubles as Sol Rey (55) and Ari Sparkz (50); Phascogale doubles as Sage Archer (57) and Qasparr (48). Register separation is real but it is not five voices. A house voice bank — or a second licence-clean bank — closes this; it is the same wall as run 1's open item 2, now measured against a five-persona song.
2. **Rap delivery.** Standing, ungraded: the founder's ear rules on the chant, here as in run 1 — now with five sections of evidence instead of one.
3. **The pad and the piano note** remain synthesized (no soundfont on the box). A soundfont or struck one-shots retire both.
4. **Line-end overhang ≤ 77 ms** is the duration calibration's cost side, printed in full in `run_data.json`. If the ear dislikes it, the next calibration targets 0.99 of the bar instead of 1.00 — a one-constant change, now that the model's return ratio is measured at two independent points (0.87 run 1, 0.8661 run 2).
5. **Variance voicing scale** — carried open since Wave F, unchanged, renders stable.

**Self-sufficiency verdict:** the whole song — hook, three crew verses, both features, outro — was scored, sung, backed, mixed, mastered, measured, and exported on this box, on house or licence-clean tools, with no account, no rental, and no network call. Run 1 proved the road on a hook and a verse; run 2 drove the full record down it, and the one calibration run 1 could only name is now a measured bench constant (×1.15 → 0.9986 of the bar).

**Per the sheet: this is not a bookshop item** — no listing, no price; the original single stands at $2.50 as issued. Any listing is a separate ruling of the founder's.

**Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All Rights Reserved, Without Prejudice. Right of claim hereby reserved and coined under the authority of the Living Man.**

93 — Live, Love, and let Love, Live.
