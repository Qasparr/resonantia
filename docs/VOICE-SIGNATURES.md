<!--
93
The voice-signature seat of the RESONANTIA desk, written the
day the founder commissioned it from his Feed finds —
"Implement what is needed or can be used in synergistic
fashion with our house toolkit" (2026-11-24).
Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice).
XXIV day of November, Dies Martis, Sol in Sagittarius,
Anno V:xii e.n. (2026 e.v.)
Scientific Illuminism: Method of Science, Aim of Religion.
Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR,
All Rights Reserved, Without Prejudice. Right of claim hereby
reserved and coined under the authority of the Living Man.
-->

# VOICE SIGNATURES — the speech seat, enrolled and gated

## What a signature is

A voice signature is a small, inspectable record in
`resonance/studio/voice_signatures/signatures.json`: an ID,
its holder, the voice spec **as filed** in the house record
(quoted from the people pages and the rulings — never
invented by the desk), a reference WAV when one has been
enrolled, that reference's provenance, and the backends that
may render it. The plug is `resonance/studio/voice_signature.py`;
its shape follows the DiffSinger plug: the system side holds
the law and the measurement, the engine strikes across a
small door, and every render is measured on this side and
written into the trail (`render_log.jsonl`) before it is
returned.

Thirteen signatures stand seated from the filed specs: the
founder's seat, QVEEN BEE (soprano, ruled 2026-11-10), LADY
LILITH (the Mother Tongue), BANSHEE, and the nine crew
members of Crown Fire, Undercurrent, and Mugetsu-Gumi.
Crew records whose people pages file no register spec say
exactly that — *no register spec filed* — rather than
wearing an invented one.

## THE BOUNDARY (the founder's, absolute)

- Signatures enroll **synthetic persona voices and
  GENERATED references only**. A reference enters with
  provenance kind `GENERATED` — a render struck by a house
  engine — or it does not enter.
- **The founder's own voice is never recorded, enrolled, or
  cloned.** His seat is an imagined synthetic voice under
  his filed spec — the 2Pac register: medium pitch,
  forward/urgent, nasal edge, diction like testimony,
  emotion at the front — authorized for pilot tracks as an
  imagined voice only. The spec is filed (2026-11-10), not
  written at enrollment; the gate refuses a parting one.
- **No clone of any person** stands in this registry (house
  law, IN-HOUSE-VOCAL-ROAD.md Layer 2).

These are not comments. They are the `enroll()` gate, and
the test suite (`tests/test_studio_voice_signature.py`,
19 tests) holds them shut: a founder recording refused, a
founder clone refused, a persona clone-of-a-person refused,
an engineless "generation" refused, a reference-less clone
render refused. **No silent substitution**: a render is the
named signature through the named backend, or it does not
happen — there is no fallback voice in the module.

## Where the seat stands in the architecture

- **Singing stays score-first.** Sung vocals ride the
  DiffSinger plug (sheets first, then singing from the
  sheets, the Divine Nine at the vowel layer). Signatures
  do not displace that law, and nothing in the plug sings.
- **Signatures serve the speech seat**: spoken passages,
  persona consistency across tracks, pilot and guide
  renders, narration — the seats where a voice must be
  *the same voice* every time it speaks.
- **The ZONOS3-Mini road is a backend, not a rival.** The
  proven narration seat (the Pirate Essay audiobook,
  llama-tts b12438, `~/workspace/lab/zonos3-mini`) stands in
  the plug as the `zonos` named-voice backend: a signature
  seats it only by naming the built-in voice its record
  carries — a preset is never passed off as a persona's own
  enrolled voice.
- **Renders are measured, not mastered.** The plug reports
  duration, rate, peak, true peak, and loudness of what was
  struck; the −14 LUFS master law is downstream pipeline
  work at assembly, exactly as with DiffSinger renders.

## The Fish S2 backend — and its license coordinate

The cloning backend is **Fish Audio S2 Pro** through
llama.cpp (the runtime this bench already speaks; the
Feed find of 2026-11-17: b12452 brought S2 cloning into
`llama-tts`; the bench seats b12681). Weights:
`ggml-org/s2-pro-GGUF` — `s2-pro-Q8_0.gguf` (4,291 MB) +
`mmproj-s2-pro-BF16.gguf` (2,046 MB) — held in the lab
(`~/workspace/lab/fish-s2`), never in git, on the
diffsinger-lab precedent. Cloning rides
`--tts-speaker-file` + `--tts-speaker-text`.

**License, at full size:** the S2 Pro weights stand under
the **Fish Audio Research License** — free for research and
non-commercial use; **commercial use is limited**. The seat
is therefore a bench and pilot instrument today. Any
commercial strike (a bookshop audio item, a sold track)
through this backend wants the founder's ruling and a
license review first; the plug's research use does not
settle that question and does not pretend to.

## The other two Feed finds, weighed

- **VoiceStudio v0.5.9-beta.5** — a full local suite
  (cloning, dubbing, dictation, transcription; AGPL-3.0).
  Weighed and **not adopted**: the studio's architecture
  takes backends at a plug point, not suites wholesale,
  and an AGPL suite is a heavy seat for a capability the
  llama-tts family already gives the bench. It stands as
  a bench reference — the next local bench to measure
  against, in the Feed's own words — not an install.
- **Google AI Edge offline speech runtimes** — on-device
  ASR + diffusion TTS for mobile SLMs. That is the
  **phone road**: the natural seat is the EQVILLIBBRRIVMM
  APK line (`android/`), where an on-device speech layer
  would let the app speak and hear without a network.
  Noted against that line as an option for the founder's
  word; not built here — this build is the desktop bench.

## Phase 2 — the backend proof, as struck (2026-11-24)

Struck under the founder's word the same day ("Try it",
15:12 EST). What stands proven, and where the machine
refused — both at full size:

- **The weights are on the bench, byte-exact.**
  `s2-pro-Q8_0.gguf` 4,290,962,464 B and
  `mmproj-s2-pro-BF16.gguf` 2,045,798,720 B, each matching
  its HuggingFace blob size to the byte, in
  `~/workspace/lab/fish-s2/models` beside llama.cpp
  **b12681** (the Feed piece's floor was b12452).
- **One signature stands enrolled from a generated
  reference.** QVEEN BEE's reference was struck by the
  proven ZONOS3 road (b12438, preset Imogen_en-British_F_1;
  the line "Qveen Bee, Featured Voices. Detroit Brightmoor
  — the purr before the bite."), 5.33 s at 44.1 kHz, and
  enrolled through the plug's own gate with its provenance
  on the record (GENERATED; engine, date, and source line
  named). It seats `fish_s2: clone`. The preset is a bench
  seed, printed as such in her record — the founder's ear
  is the gate on whether the seat carries her.
- **The clone pipeline runs — and this cell refuses it at
  the memory wall.** The plug's render loaded both weights,
  took the enrolled reference and its transcript, and
  **generated frames** (the engine's own log: frames
  advancing at 0.01 frames/s, ~90 s a frame under the
  shared-CPU throttle and page thrash — 84 GB paged in
  36 minutes). At 36.4 minutes, 19+ frames in, the process
  (5.83 GB resident and climbing; the BF16 codec alone is
  2.0 GB and no smaller quant of it exists) was
  **OOM-killed (rc −9)** against this cell's 6 GiB shared
  limit, shared that hour with the 777 TABVLA build. The
  plug raised clean — *llama-tts struck nothing* — struck
  no artifact, and logged no render. **No clone render
  exists, and none is claimed.**
- **The coordinate, stated plainly:** the seat is
  backend-ready and generation-verified; a full line does
  not fit this machine as it stands. What the piece wants
  is a machine giving the process ≥ 8 GB to itself and
  several whole cores (or a GPU) — or a smaller quant of
  the pair, which ggml-org does not ship today (Q8_0 and
  BF16 only). On such a machine the same plug call renders
  unchanged; nothing in the registry or the gate waits on
  anything but room.

## Open seats

- Eleven of thirteen signatures stand spec-only: a
  generated reference per persona is enrollment work, one
  short line each, and each first seat is the founder's
  ear call before it carries a track.
- The founder's seat enrolls only when a generated
  reference matching the filed register is struck — an
  imagined voice, seated as imagined, or the seat stays
  honestly empty.
- VOCALOID7 and ACE stay filed for the day a Windows or
  Mac machine enters the house (IN-HOUSE-VOCAL-ROAD.md);
  nothing in this seat changes that.
