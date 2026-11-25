# KAGAMI KETTOU — FILO RENDER SET, V2 (THE REPAIR)

*Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR, All Rights Reserved, Without Prejudice. Flagpole of Claim and Coinage reserved. Method of Science, Aim of Religion.*

**The commission** (the founder, 2026-11-25 06:43 EST): “Do them both but in order of synergy.” Both ear defects of the house render repaired, in the synergy order — the bed first, because a voice cannot be seated in front of a bed that is itself under repair; the balance second, on the new bed.

**Standing of the set:** the v2 files below **supersede the v1 01 and 02** of this folder (RECEIPT.md). The v1 files are kept, marked superseded, never vanished. **03 stands as v1** — see its line below. Nothing here touches DECISIONS.md or the mastering of record, which remains the founder's ear when an external strike lands.

---

## THE DEFECTS, AS MEASURED

1. **“No voices”** (founder's ear, 2026-11-25 06:41 EST). The parent desk measured the v1 full master's vocal layer at RMS 0.0197 against its bed's 0.1952 — some 20 dB under. This build re-measured on the delivered v1 MP3s by the same difference method (full minus instrumental, whole singing sections): Verse A **0.128 (−17.9 dB)** · Verse B **0.122 (−18.3 dB)** · Shion **0.176 (−15.1 dB)** · close **0.277 (−11.2 dB)**. The ear was right; the balance was baked into the only sources v1 left (two mastered WAVs, no premasters).
2. **“The instrumentals is 16 bit again.”** The founder's standing law: no 16-bit MIDI *sound* for a track to be rapped over — dream-caliber instrumentals. The v1 bed's piano was a five-partial decaying sine stack; its violin a static harmonic stack with vibrato. Honestly labeled synthesis in the original build — and still the sound the law names. The *score* (MIDI data as notation) was never the defect and is untouched: this build re-ran the original build's own verification, **125/125 checks passed**, and rendered the original build's own event lists (VLN 216 · RH 340 · LH 173 · B808 173 events — identical notes, durations, swing, pans, gains).

## THE ROADS, INVENTORIED BEFORE ANYTHING WAS STRUCK

- **Sample playback — cannot run here.** No fluidsynth or timidity binary, no libfluidsynth, no pyfluidsynth on this box. The one soundfont on disk, GeneralUser GS v1.471, is a GM bank — the defect's own class of sound, not its cure.
- **Generative roads — cannot run, and could not lawfully serve.** No GPU stands on this box (no nvidia-smi, no device). ACE-Step stands bench-noted behind its GPU gate; MusicGen likewise wants iron this box does not hold. And a generative bed would *change the composition* — this repair forbids it; the filed score is the record.
- **The road taken: first-principles physical-model synthesis at 48 kHz float** — the house's own doctrine, the road of the eightoeight seat (the founder's approved synthesizer instrument; the kit and Super 808 therefore **stand unchanged**). The two named melodic seats were rebuilt as models:
  - **Grand piano, modeled** — partials stretched by the string inharmonicity law f_k = k·f·√(1 + B·k²); two unison strings per note detuned ±1.5 cents; per-partial two-stage decay (fast strike decay, long soundboard tail); a banded hammer-noise transient at the strike; a soundboard lowpass over the sum; a natural ring past the written duration, faded, never cut.
  - **Violin, modeled bowed string** — harmonic stack shaped by the bridge-hill resonance near 2.6 kHz; vibrato (5.4 Hz) ramping in to a half-percent depth with its tremolo on the same cycle; a slow seeded bow-pressure wobble on the upper partials; band-passed bow noise under the tone, following the bow envelope.
  - **Calibration, disclosed:** each modeled note is RMS-matched to the v1 voice's note at the same pitch and written duration (ratio capped to [0.4, 2.5]), so the original render's placed mix gains still mean what they meant. The models change the sound; they smuggle in no new balance among the bed's own seats.
  - **Unchanged by design:** the eightoeight kit and Super 808, the Sigma solfeggio bed, the chord-root sub, and the pads — the ground the duel stands on.

## STEP 2 — THE VOICE IN FRONT

Source: the filed `vocal-stem.wav` (44.1 kHz mono; detection reads it Japanese, p = 0.8986), resampled to 48 kHz by the exact rational 160/147, seated dual-mono at the centre. **One gain: +17.93 dB (×7.88)**, computed from the verses themselves — the pooled windowed RMS of Verses A+B against the new bed (raw verse ratio 0.133) — targeting a verse ratio of **1.05**. One gain, not a per-section ride: the stem's own dynamics stand (the close is the loudest seat, as written).

**The balance, printed both ways it can honestly be read** (windowed/section RMS, voice against bed):

| section | v1 (delivered diff) | v2 premaster — the mix itself | v2 (delivered diff) |
|---|---|---|---|
| Verse A | 0.128 · −17.9 dB | **1.078 · +0.65 dB** | 0.771 · −2.26 dB |
| Verse B | 0.122 · −18.3 dB | **1.021 · +0.18 dB** | 0.742 · −2.59 dB |
| Shion | 0.176 · −15.1 dB | **1.469 · +3.34 dB** | 1.005 · +0.04 dB |
| Close | 0.277 · −11.2 dB | **2.320 · +7.31 dB** | 1.457 · +3.27 dB |
| Overall (singing windows) | 0.151 · −16.4 dB | **1.271 · +2.08 dB** | — |

The two v2 columns differ for a stated reason, not a hidden one: 01 and 02 are mastered *separately* to the same −14 LUFS, and the full master's loudness is voice-carried, so after normalization its bed component sits lower and the difference of the two delivered masters understates the mix's own ratio. The premaster column is the mix as mixed; the delivered column is the same difference method that found the defect, applied to the delivered files — on that method the verses improved by **+15.6 dB and +15.7 dB**. Both are printed; neither is smoothed.

## STEP 3 — THE DELIVERABLES, WEIGHED ON THE DECODED MP3

Mastering road, the house's own: `pipeline.master_signal` to −14.0 LUFS, strike ceiling −1.35 dBTP, WAV 24-bit, MP3 by ffmpeg/libmp3lame at 320k, judged by `vocal_exam.judge_masterlaw` on the decode — and **re-judged independently** after the build, same figures.

| # | file | LUFS | decoded TP | bitrate | verdict |
|---|---|---|---|---|---|
| 01 | `01-full-render-kagami-kettou-v2.mp3` (10,077,165 B) | −14.29 | −1.35 dBTP | 320,000 bps | **COMPLIANT** |
| 02 | `02-instrumental-kagami-kettou-v2.mp3` (10,077,165 B) | −14.01 | −1.32 dBTP | 320,000 bps | **COMPLIANT** |
| 03 | `03-vocals-kagami-kettou.mp3` (v1) | −14.22 | −1.37 dBTP | 320,000 bps | **STANDS** — mastered from this same stem, unchanged; not re-struck |

Mastering notes, disclosed: 01's chain reports `ceiling_overrode_loudness: true` (gain −7.86 dB, trim −0.18 dB; −14.29 stands inside the ±0.5 law). 02 took no trim (−14.01). Each MP3 stands beside its mastered 24-bit WAV under the same name.

## SOURCES AND FILES

- Bed: rendered in this build from the filed score — `build_kagami_ketto.py`'s `build_instrument_events()`, imported, its verification re-run (125/125). No score file, lyric, or event was edited.
- Voice: `../vocal-stem.wav`, as filed. No re-synthesis, no edit to the stem.
- Build script: `build_filo_render_v2.py` (annotated, house form). Build record: `build-record-v2.json`.
- The FILO discipline holds: the full render struck first, as a whole; the instrumental after it; the vocals' seat undisturbed.

## WHAT COULD NOT RUN

FluidSynth/TiMidity and any sample-library road (no renderer, no library but a GM bank); ACE-Step and MusicGen (no GPU on this box; and generative audio cannot carry a filed score). Each is named here at full size rather than silently routed around: the modeled-synthesis road was not a fallback quietly accepted — it is the highest-caliber road that runs on this box *and* the house's own doctrine.

## THE EAR

The verdict on the new bed's caliber and the front-seated voice belongs to the founder, as it did for v1 — this receipt claims the measurements, not the ear.

93 — Live, Love, and let Love, Live.

---

**ADDENDUM (2026-11-25, marked, the original above unaltered):** this set's **01 is superseded by FILO v3** (RECEIPT-V3.md) — the track re-rendered as its own track under the founder's order of 2026-11-25 08:00 EST, its vocals re-struck and gated, seated on this set's bed (which stands in v3 as 02, byte-identical). This set's 02 otherwise stands as struck. The v2 files are kept, marked superseded in part, never vanished.
