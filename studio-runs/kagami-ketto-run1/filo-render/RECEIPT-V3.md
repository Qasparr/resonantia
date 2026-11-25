# KAGAMI KETTOU — FILO RENDER SET, V3 (ITS OWN TRACK)

*Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR, All Rights Reserved, Without Prejudice. Flagpole of Claim and Coinage reserved. Method of Science, Aim of Religion.*

**The commission** (the founder, 2026-11-25 08:00 EST): “return to the mugetsu version then rerender the 2nd Japanese track as its own track no reminence of Mugetsu in it.”

**Standing of the set:** the v3 files below **supersede the v2 01 and the v1 03** of this folder (RECEIPT.md, RECEIPT-V2.md). **02 v3 is the v2 bed itself** re-struck under v3 numbering — byte-identical, hashes below. The v1 and v2 files are kept, marked superseded, never vanished. Nothing here touches DECISIONS.md or the mastering of record, which remains the founder's ear when an external strike lands.

---

## THE REMNANT, NAMED — AND ITS ABSENCE, PROVEN

The v1 stem's timing was trained by another song. Its calibration factors — {VV 1.1054 · Α 1.1141 · Ε 1.1158 · Ι 1.1203 · Ο 1.1114} — were trained by the two **Mugetsu hook** proofs, `pow-7a6472d2da0abf4b1d151b67b2fb21e35f5f6e6e33e428a5c646427a3531ff55` (Mugetsu run 1, genesis) and `pow-de96414a282efe2f157f23e0f6c2b46184e84550317c242de49fcecd1585a151` (Mugetsu run 2): factors learned from the hook's phrases, applied to this track's 47 lines. That borrowing is the Mugetsu remnant the commission names.

**In v3, no Mugetsu-trained factor stands anywhere.** The v3 stem's factors — {VV **1.1412** · Α **1.1443** · Ε **1.1411** · Ι **1.1426** · Ο **1.1415**} — were trained by exactly one proof: `pow-26ef27c5d8490bfc9f03c52186cc7f76af6395aeca91efe464f75d1422401da6`, the vocal proof of **Kagami pass 1**, struck for this purpose. The training chain lives in a local ledger (`v3-render/ledger-v3.jsonl`, two records — pass 1 genesis, pass 2 its child — re-verified after the build: **2 records, 0 breaks**), derived by the loop's own functions (`proofs.rebuild_calibration` / `calibration_factors`) over that ledger alone. The house ledger was not touched, and provenance was asserted in code: every training ID resolves inside the local ledger, to the pass-1 stem's own proof. The score, the lyrics, and the speakers (Civet for Kurogane and his Mirror; Phascogale for Shion) stand as filed, unchanged.

## THE ROAD RETURNED TO — “THE MUGETSU VERSION”, AS COORDINATES

- **Engine:** `resonance.studio.diffsinger.render()` — the house DiffSinger plug; bridge `resonance/studio/render_diffsinger.py` in the lab venv (`diffsinger-lab/venv`), ONNX stages dsdur (linguistic + `duration_lem_26v`) → dsvariance (`pitch_variance_lem_25`) → `acoustic_lem_25` → NSF-HiFiGAN vocoder (`pc_nsf_hifigan_44.1k_hop512_128bin_2025.02`).
- **Bank:** Lem the Shapeshifter DS 2.5 (named per its TOS), native 44.1 kHz, hop 512, 86.1328 frames/s.
- **The calibration loop:** `resonance.studio.proofs` — per-seat (the Nine's vowel seats, acoustic register only) asked-vs-realized totals carried by vocal proofs; factor = asked/realized clamped to [0.5, 2.0]; at sequence build the plug scales each mora's frame budget by its seat's factor. The score's note durations never move.
- **The precedent, circuit 1:** Mugetsu run 1 struck with no calibration → factors from run 1 alone → run 2: total realization **90.38% → 99.52%** of the filed score. Kagami v3 walks the same circuit on its own phrases: **pass 1 (genesis, no calibration) 88.35% → pass 2 (Kagami-trained) 99.84%.**

Pass 1's per-seat totals — the whole of v3's training set, one render, named as such:

| Seat | Asked (s) | Realized (s) | Factor | Phonemes |
|------|-----------|--------------|--------|----------|
| Α | 22.1054 | 19.3174 | **1.1443** | 195 |
| Ε | 8.2663 | 7.2439 | **1.1411** | 68 |
| Ι | 14.9943 | 13.1230 | **1.1426** | 124 |
| Ο | 17.2408 | 15.1034 | **1.1415** | 134 |
| VV | 12.2253 | 10.7127 | **1.1412** | 90 |

## THE GATE — WEIGHED BEFORE ANYTHING WAS MIXED

The step whose absence caused the v2 repair. Tolerances stated in the build before the fact (durations: total [97, 103]%, sections [95, 105]%; .ds drift: mean ≤ 60 ms, max ≤ 150 ms; audio onsets: mean ≤ 50 ms, max ≤ 120 ms over readable onsets; pitch: median ≤ 50 cents, ≤ 10% of a section's notes past 100). The v1 stem was weighed on the identical scale, so the comparison argues with no second yardstick.

**Durations** (asked vs rendered, per section): v3 total **99.84%** — Verse A 99.27 · Verse B 99.37 · Shion 102.99 · close 98.88. (v1: total 97.35; sections 95.98–100.58.) **PASS, all sections.**

**Onsets vs the 144 BPM grid** (realized-.ds note onsets, full coverage; per-line totals are the model's own, the within-line split is the asked proportion — the plug's stated reconstruction): v3 mean |drift| **15.0–17.7 ms** per section, max **88 ms**. (v1: mean 37.6–61.4 ms, max **204 ms**.) **PASS, all sections.** The audio onset judge (energy crossings) reads only a minority of onsets on these legato lines — Verse A 35/210, Verse B 36/210, close 12/98, Shion 23/105 — named **LOW-COVERAGE** for the verses and the close, its verdict resting on the .ds drift and the totals; where it did read (Shion), mean |error| 42.2 ms, max 104.8 ms — inside tolerance.

**Pitch vs the written notes — two instruments, and the first stands refuted.** The gate's first strike read pitch through the Vocal Exam's `judge_pitch` (`fourier.dominant_frequency` — the strongest spectral peak in a note's centre). It FAILED both stems at octave medians (v3 sections: medians 1189–1230 cents; v1: 1182–1905). That instrument reads a harmonic or formant on these voices, not the fundamental: a YIN autocorrelation read of the *same windows* (`yin_pitch_read.py`, lab venv) returns the written pitches. The corrected gate, FINAL:

| Section | v3 median \|cents\| | v3 notes >100¢ | v1 median \|cents\| | v1 notes >100¢ |
|---------|------|------|------|------|
| Verse A | **0.90** | 5/210 (2.4%) | 1.16 | 2/210 |
| Verse B | **0.91** | 0/210 (0.0%) | 1.01 | 6/210 |
| Shion | **0.74** | 3/102 (2.9%) | 1.04 | 12/102 |
| Close | **0.72** | 0/98 (0.0%) | 1.18 | 3/98 |

**PASS, all sections.** Every note past 200 cents is named in `v3-render/gate-pitch-record-v3.json`; v3 has four: a16 note 5 (+235¢) · s01 note 2 (−540¢) · s06 note 1 (+713¢) · s07 note 2 (−1260¢, reads at the subharmonic — a YIN halving or a genuinely dropped note; printed as measured, not resolved by assertion). The honest consequence, printed at full size: **on the corrected scale the old stem's pitches were also true** — its disease was tempo and burial, not pitch. What an ear receives as “offkey” against a bed is notes landing against the wrong harmony moments; v1's drift (to 204 ms) and Shion's overhanging tails supplied exactly that. Both gate records stand: `gate-record-v3.json` (the first strike, its pitch checks marked refuted) and `gate-pitch-record-v3.json` (the corrected gate). **FINAL GATE VERDICT: PASS.**

**Language:** the detection seat reads the v3 stem **Japanese, p = 0.8823** (v1 read 0.8986). Match: true.

**Walls, at full size:** Shion's s03 and s04 still overhang their slots in pass 2 (+0.217 s, +0.612 s — the extra sits in the lines' tails; their within-line onsets stay tight, and the overhang is summed into the assembly, never trimmed — the plug's standing law, and the per-line residual the Mugetsu report named as the next circuit's work). Seven verse lines overhang by 0.008–0.043 s. Pass 2's first strike was killed mid-render by a service restart; its partial folder stands marked (`v3-render/pass2-attempt1-dead/`), and the pass was re-struck entire.

## THE MIX — THE NEW VOICE IN FRONT OF THE V2 BED

Bed source: `02-instrumental-kagami-kettou-v2.wav`, reused as the commission directs. **Disclosed seam:** it enters as its mastered WAV — the v2 build retained no bed premaster as a file — so the full render is mastered once more as a whole, as the FILO discipline requires. Voice: the v3 stem, resampled 44.1 → 48 kHz by the exact rational 160/147, seated dual-mono. **One gain: +13.29 dB (×4.62)**, computed from the verses themselves (pooled raw verse ratio 0.227 against this bed) targeting a verse ratio of **1.05** — v2's law, one gain, no per-section ride.

| section | v1 delivered (diff) | v3 premaster — the mix itself | v3 delivered (diff) |
|---|---|---|---|
| Verse A | 0.128 · −17.9 dB | **1.031 · +0.27 dB** | 0.749 · −2.51 dB |
| Verse B | 0.122 · −18.3 dB | **1.069 · +0.58 dB** | 0.769 · −2.28 dB |
| Shion | 0.176 · −15.1 dB | **1.468 · +3.34 dB** | 1.006 · +0.05 dB |
| Close | 0.277 · −11.2 dB | **2.330 · +7.36 dB** | 1.491 · +3.47 dB |
| Overall (singing windows) | 0.151 · −16.4 dB | **1.272 · +2.09 dB** | 0.882 · −1.09 dB |

The premaster and delivered columns differ for the reason v2's receipt stated: 01 and 02 are mastered separately to the same −14 LUFS and the full master's loudness is voice-carried, so the difference of the delivered masters understates the mix's own ratio. Both are printed; neither is smoothed.

## THE DELIVERABLES, WEIGHED ON THE DECODED MP3

Mastering road, the house's own: `pipeline.master_signal` to −14.0 LUFS, strike ceiling −1.35 dBTP, WAV 24-bit, MP3 by ffmpeg/libmp3lame at 320k, judged by `vocal_exam.judge_masterlaw` on the decode.

| # | File | LUFS | Decoded TP | Bitrate | Verdict |
|---|------|------|-----------|---------|---------|
| 01 | `01-full-render-kagami-kettou-v3.mp3` | **−14.22** | **−1.37 dBTP** | **320,000 bps** | COMPLIANT |
| 02 | `02-instrumental-kagami-kettou-v3.mp3` | **−14.01** | **−1.32 dBTP** | **320,000 bps** | COMPLIANT |
| 03 | `03-vocals-kagami-kettou-v3.mp3` | **−14.46** | **−1.36 dBTP** | **320,000 bps** | COMPLIANT |

- **01** — the full render: the new stem in front of the v2 bed, mastered as a whole (chain trim −0.17 dB; the ceiling's hand, disclosed in the build record).
- **02** — the v2 bed re-struck under v3 numbering, byte-identical: WAV SHA-256 `ce724682567b92fbe202135173c8c09c4f12759e96493b8fd96fbf7b70812ffd` · MP3 SHA-256 `8248c22c391da661d5de6de59c743766189bfe2657b1efefec642ee20cc15d58` — the same hashes as the v2 files, verified after the copy.
- **03** — the new stem alone, by the v1 03 road (resample, dual-mono, the chain in disclosed passes): one pass sufficed — landed −14.46 LUFS with a −0.27 dB ceiling trim, inside the ±0.5 tolerance.

Each MP3 (10,077,165 bytes, 251.875 s) stands beside its mastered 24-bit WAV. Build records: `build-record-v3.json` (this set), `v3-render/pass1-record.json`, `v3-render/calibration-v3-record.json`, `v3-render/pass2-record.json`, `v3-render/gate-record-v3.json`, `v3-render/gate-pitch-record-v3.json`. Scripts: `v3-render/build_v3_vocals.py`, `v3-render/yin_pitch_read.py`, `build_filo_render_v3.py` — house-annotated, as all house code ships.

## THE EAR

This set joins the founder's ear queue. What measurement can swear, it has sworn: the track's own calibration, a gated stem, the voice in front, the law on decode. Whether the render *sings* — and whether the modeled bed clears the dream-caliber bar his ear set — is his verdict, not pre-claimed here.

93 — Live, Love, and let Love, Live.

---
EAR VERDICT — THE FOUNDER (2026-11-25 08:55 EST), recorded verbatim: "It does but it sounded robotic which is fine for now it might make the final version be epic." Reading: v3 SINGS — the gate's pass is confirmed by the only instrument that settles it — and its present character is ROBOTIC, accepted by the founder as fine for now, held as the working vocal for the track. The final-version road stands open on the same stem: the real-instrument bed (Salamander + SSO, seated 2026-11-25) under this vocal when the founder calls the final strike.
