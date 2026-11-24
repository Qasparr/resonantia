# OFFLINE-PRODUCTION — THE STANDALONE MAP

*A Scientific Illuminist treatment of Resonantia as an offline,
standalone production house: every seat local, owned, and
measured — no cloud seat, no subscription, no telemetry.*

Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice).
XXIV day of November, Dies Martis, Sol in Sagittario, Anno V:xii
e.n. (2026 e.v.). Classification: Enterprise • Educational •
Research & Development. Method of Science, Aim of Religion.

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR,
All Rights Reserved, Without Prejudice. Right of claim hereby
reserved and coined under the authority of the Living Man.

---

## §I — THE COMMISSION AND THE MAP IN ONE VIEW

Commissioned by the founder, 24 November 2026: *"Anything
improving the goal of a offline standalone voice and 808 and
instrumental productions and sheets. Voice and language
detections etc."* The map, seat by seat — state, road, gate:

| Seat | State | Road | Gate |
|---|---|---|---|
| Singing | **Built** | DiffSinger + the Divine Nine at the plug point; sheets first, always | The house bank (IN-HOUSE-VOCAL-ROAD Phase 2) waits on the workstation + a founder-ruled voice source |
| Speech | **Built** | ZONOS3-Mini via llama.cpp `llama-tts` b12438 (`~/workspace/lab/zonos3-mini`), predefined voices | A house voice of its own waits on the same bank road |
| Voice signatures | **In sibling build** | Fish Audio S2 via llama.cpp (Feed, 2026-11-17) as the signature backend; registry + plug | This doc records the seat; its build reports separately |
| **Detection** | **Built this day** | whisper.cpp + ggml-base; Silero VAD over ONNX; energy fallback | Larger Whisper models are drop-ins (`RESONANTIA_WHISPER_MODEL`) |
| 808 | **Built; measured this day** | `studio/eightoeight.py`, pure synthesis, dial-tuned (VV) | Ear verdicts are the founder's, queued |
| Instrumentals | **Built in-house; two pieces bench-noted** | The studio's own synthesis/spine roads | ACE-Step 1.5 and YuE2 are GPU-class — §IV |
| Sheets | **Built; draft road added this day** | ABC notation layer; performance road strikes `composition.abc`; detection strikes lyric timing DRAFTS | No engraver on this box — §V |
| Mastering | **Built** | `pipeline.master_signal`; the law −14 LUFS · ≤ −1.0 dBTP decoded · 320,000 bps when sworn | — |
| Examination | **Built; two judges added this day** | The Vocal Exam (7 judges) | Phase 2 loop is its own commission |

The bench this map stands on: 4 cores shared at 1.5, ~8 GB
RAM, **no GPU**. Every "built" above runs on it today.

## §II — THE DETECTION SEAT (built this day)

`resonance/studio/detect.py` — voice activity, language
identification, transcription, fully offline, on the ggml
family: whisper.cpp is the sibling runtime of the llama.cpp
family the speech seat already rides (the Feed's ZONOS3-Mini
merge, b12424, 2026-11-15, is the same event family; the
house's own speech build is b12438).

**The model trade, printed.** ggml-base (multilingual,
147,951,465 bytes) over tiny (~75 MB): tiny decodes faster,
but identification is this seat's first duty and base is the
stronger identifier; on this bench base reads a 20 s clip's
language in ~5 s and transcribes it in ~13 s. Base is the
seat; the size is a drop-in, not a doctrine.

**First reads, as measured** (the module header carries
them; they stand here as the seat's record):

- Pirate Essay narration (spoken EN, ZONOS3-Mini):
  **en, p = 0.9972**; transcript meets its script's
  load-bearing words.
- DETROIT MUGETSU hook (sung JA, DiffSinger): dedicated
  detection pass **ja, p = 0.8241** — the exam can now state
  beside the founder's ear ("i heard a couple Japanese
  words in it") that the hook *is* Japanese. Two coordinates
  stand with it: the auto-decoding pass misfires to English
  on the same audio (hence the seat's two-pass law: detect,
  then decode forced), and the Japanese-forced transcript is
  kana in shape but **not the sheet's words** — lyric-accurate
  transcription of a sung soprano is beyond the base model.
- Silero VAD: the v5 model read statefully **with** its
  trained 64-sample context (without it, clear narration
  reads p ≤ 0.071 — measured, and printed in the module so
  no future hand rediscovers it): max p = 1.0, 85.6% of
  frames over threshold on the narration. The energy VAD
  (quiet-decile threshold, the onset judge's idiom) stands
  as fallback; the serving engine is named in every return.

**Wiring.** The Vocal Exam gains Judges 6 and 7 —
`judge_language` (against the corpus item's `lang`) and
`judge_coverage` (speech seconds over duration, segment
count, longest silence) — additive only: Judges 1–5 keep
their verdict semantics, and both new judges sit in
`score_hook_run`'s record. VoiceStudio (Feed, 2026-11-16)
carries 11 transcription engines in suite form; the house
takes the capability as a *seat*, not a suite — one runtime
family, one exam, no second application to keep.

**Rebuild recipe** (the seat's assets live in `tools/`,
gitignored as local assets under the diffsinger-lab
precedent):

```
git clone --depth 1 https://github.com/ggerganov/whisper.cpp tools/whisper.cpp
cmake -B tools/whisper.cpp/build -DCMAKE_BUILD_TYPE=Release -DWHISPER_SDL2=OFF
cmake --build tools/whisper.cpp/build -j 2 --target whisper-cli
curl -L -o tools/whisper.cpp/models/ggml-base.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
curl -L -o tools/silero/silero_vad.onnx \
  https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx
python3 -m pip install --user --break-system-packages onnxruntime
```

## §III — THE 808 SEAT (completed this day)

The toolbox (`studio/eightoeight.py`, 2026-11-16) already
stood as a parametric instrument; this day weighed it and
seated it on the grid. Four measurement tests (21/21 in its
suite): fundamental at argument within 2 Hz; decay across
one tau at e⁻¹ within 0.06 for three taus; drive's harmonic
growth; headroom through the mastering chain. The pattern
demo (`studio-runs/eightoeight-pattern-demo/`) strikes two
bars of the KRS foundation — 144 BPM, 13/8 Sigma Mega, the
kick dial-tuned to VV at 44 Hz — mastered and judged:
**−14.01 LUFS · −1.35 dBTP decoded · exactly 320,000 bps**,
its drum sheet (`sheet.abc`) beside it.

## §IV — INSTRUMENTALS: THE GPU PIECES, BENCH-NOTED

Weighed honestly, attempted not at all — on this machine an
attempt that cannot finish is a cost dressed as work (the
VOCALOID7 bench-note precedent, `docs/IN-HOUSE-VOCAL-ROAD.md`).

**ACE-Step 1.5** (Feed, 2026-11-14; Apache-2.0). Full-song
generation, local: under 2 s on an A100, under 10 s on an
RTX 3090, 48 kHz stereo out. *What it would add:* a
prompt-to-song instrumental draft engine beside the house's
own synthesis roads. *The gate, exact:* a CUDA GPU of the
3090 class (24 GB VRAM is the comfortable seat; the model
family wants double-digit GB and CUDA kernels) — this box
has no GPU at all, and CPU inference for a diffusion song
model at album lengths is not a road, it is a wait. It
enters the house the day the workstation does (the same
arrival that unblocks the vocal bank road), and not before.

**YuE2 Studio** (Feed, 2026-11-14). Score-first full songs:
the composition written as ABC and engraved *before* it
sings, offline, no account, no telemetry — the closest
philosophical kin on the board to this house's sheets-first
law, and already studied here (`docs/STUDY-YUE2.md`).
*What it would add:* an external score-first song engine
whose ABC the house notation layer can read natively.
*The gate, exact:* minimum 6 GB VRAM; a 3-minute song in
about a minute wants 24 GB+. Same arrival, same day.

**What landed now, CPU-honest:** the 808 seat completed and
grid-struck (§III), and the detection seat (§II) — which
serves instrumentals too: coverage and transcription reads
now examine any render the instrumental roads strike. The
survey found no other CPU-honest gap in the existing
instrumental chain: the spine, kit, arpeggio, and synthesis
roads stand as built, and their open items are ear verdicts
(the founder's), not missing machinery.

## §V — SHEETS: THE DRAFT ROAD

`detect.lyric_timing_draft` wires the detection seat into
the sheets pipeline as a **LYRIC TIMING DRAFT**: segment
timestamps → an ABC at Q:1/4=60 (a quarter note is a second;
lengths read as seconds), words on the `w:` line, exact
offsets in `%%text` comments and a JSON sidecar. It serves
the founder's standing rule — *a track with no notation gets
a transcription production, never a fabricated sheet* — as
that production's first artifact, marked DRAFT in its title
and header, its words unverified by construction. Seated
artifacts: `studio-runs/lyric-timing-drafts/` (the Pirate
Essay opening; the Mugetsu hook, whose coordinate against
its true sheet is printed in that folder's README). The
gap, at full size: no engraver (LilyPond/abcm2ps) stands on
this box, so house sheets ship as ABC — the notation layer
of record — and engraved PDFs wait on the engraver's
arrival, claimed nowhere until then.

## §VI — THE PHONE ROAD

Google's offline voice runtimes (Feed, 2026-11-16; AI Edge
ASR + diffusion TTS pairing with on-device small models,
the speech loop under 180 ms) are the **phone** road: they
belong with the EQVILLIBBRRIVMM APK line (the toolkit
already computes on the founder's device) as its future
voice layer — detection and speech on the phone itself,
offline, beside the nabla/upscale seats. Recorded here as
the road's named option; nothing on the phone changes this
day, and the studio seats above are this commission's build.

---

— 1 of 1 — | All Rights Reserved, Without Prejudice |
Flagpole of Claim and Coinage reserved

93 — Live, Love, and let Love, Live.
