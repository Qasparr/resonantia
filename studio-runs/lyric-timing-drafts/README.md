# LYRIC TIMING DRAFTS — seated artifacts of the detection seat

Struck 24 November 2026 by `resonance/studio/detect.py`'s
`lyric_timing_draft`, under the founder's standing rule: *a
track with no notation gets a transcription production, never
a fabricated sheet.* These are DRAFTS — the first artifact of
a transcription production — and each says so in its own
header. The words are a machine listener's (whisper.cpp,
ggml-base, fully offline), unverified against any lyric of
record; the pitches are a neutral placeholder; the timings
are the transcription's segment offsets, exact in the JSON
sidecars.

| Draft | Source render | Language read | Segments |
|---|---|---|---|
| pirate-essay-opening | Pirate Essay audiobook run 1, master.wav, first 30 s (spoken narration, ZONOS3-Mini) | en, p = 0.9848 | 3 |
| mugetsu-hook-run2 | DETROIT MUGETSU hook, engine run 2 (sung, DiffSinger) | ja, p = 0.8241 | 7 |

**The Mugetsu coordinate, at full size.** The hook's true
sheet stands in the Vocal Exam corpus (8 lines, of record:
「デトロイト生まれ、ブライトムーア育ち」…). The draft's words
are Japanese in shape and are **not** those words — at base
model size, the seat identifies the sung hook's LANGUAGE
reliably (ja, p = 0.8241, where the founder's ear heard "a
couple Japanese words") and times its phrases, but it does
not recover the lyric. Both facts stand; neither is smoothed.
A larger Whisper model is a drop-in at the same seat
(`RESONANTIA_WHISPER_MODEL`) whenever the bench grows.
