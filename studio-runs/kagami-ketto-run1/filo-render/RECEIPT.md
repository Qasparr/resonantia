# KAGAMI KETTOU — THE FILO RENDER SET · RECEIPT

*Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR, All Rights Reserved, Without Prejudice. Struck XXV day of November, Anno V:xii e.n. (2026 e.v.), under the Method of Science, Aim of Religion — Scientific Illuminism.*

**The commission** (the founder's direct order, 2026-11-25 06:28 EST): "the house render of the Japanese rap track fully mastered but keep the instrumental and vocals separated by FILO sequence so the full render still gets the first pass as a whole."

## The FILO sequence — and why

FILO: **first in, last out.** The full render enters first and takes the first pass **as a whole** — the whole mix, mastered as one body, is the work, and it is weighed first. The separated stems follow it out, each mastered separately to the same law, so any one of the three can stand alone without re-opening the others:

| # | Deliverable | What it is |
|---|---|---|
| 01 | `01-full-render-kagami-kettou.mp3` | The full render — vocals and bed together, mastered as a whole |
| 02 | `02-instrumental-kagami-kettou.mp3` | The instrumental alone — violin, grand piano, Super 808, Sigma Mega bed |
| 03 | `03-vocals-kagami-kettou.mp3` | The vocals alone — Kurogane, his Mirror, Shion (47 DiffSinger lines) |

Each MP3 stands beside its mastered 24-bit WAV of the same sequence name. Build script: `build_filo_render.py`, in this folder.

## Sources — what each deliverable was built from

- **01** ← `../master.wav` (72,540,044 bytes; 48 kHz stereo, 24-bit) — the package's whole-mix mastered WAV, struck by the original build through `pipeline.master_signal`. The float premaster was never saved to disk, so this WAV is the whole-mix source of record. The FILO pass laid **no second mastering pass** over a finished master — that would be a new master, not this one; it struck the WAV to 320k MP3 by the build's own encode road (ffmpeg / libmp3lame) and re-weighed the decoded MP3 against the law.
- **02** ← `../instrumental-master.wav` (72,540,044 bytes; 48 kHz stereo, 24-bit) — the bed mastered separately by the original build at the same law; struck and re-weighed by the same road as 01.
- **03** ← `../vocal-stem.wav` (22,215,420 bytes; 44.1 kHz **mono**, 16-bit) — the one source that arrived **unmastered** (as filed: peak −4.08 dBFS, RMS −29.08 dBFS). It was mastered for real in this pass: resampled to the studio rate (48 kHz, polyphase 160/147), seated dual-mono for the stereo mastering chain, and run through `pipeline.master_signal` at −14.0 LUFS with the ceiling at −1.35 dBTP. **Gain staging, disclosed:** one pass landed at −14.6 LUFS — the ceiling trim (−0.37 dB) overrides the loudness by the chain's own design, outside the law's ±0.5 tolerance — so the chain ran a second pass (+0.6 dB gain, −0.19 dB trim), landing at −14.22 LUFS. Both passes' reports stand in the build record; nothing was smoothed.

## Measured — on the decoded delivered MP3s (judge: `vocal_exam.judge_masterlaw`)

House master law: integrated loudness −14.0 ± 0.5 LUFS · decoded true peak ≤ −1.0 dBTP · bitrate exactly 320,000 bps.

| # | LUFS | True peak (decoded) | Bitrate | Verdict |
|---|---|---|---|---|
| 01 full render | **−14.02** | **−1.34 dBTP** | **320,000 bps** | COMPLIANT |
| 02 instrumental | **−14.02** | **−1.34 dBTP** | **320,000 bps** | COMPLIANT |
| 03 vocals | **−14.22** | **−1.37 dBTP** | **320,000 bps** | COMPLIANT |

Each delivered MP3 is 10,077,165 bytes; duration 251.875 s (93 bars × 13/8 at 144 BPM), 48 kHz.

## Boundaries kept

- The package's existing masters, `DECISIONS.md`, and all other package files are untouched.
- **The mastering of record remains open.** This set is the house render, entire; which version of the piece takes the mastering of record is the founder's ear, per the mastering rider of 2026-11-24. Nothing here claims that seat.
- Nothing was unmixed and no stem was fabricated: each deliverable descends from a real source file in the package, named above.

93 — Live, Love, and let Love, Live.
