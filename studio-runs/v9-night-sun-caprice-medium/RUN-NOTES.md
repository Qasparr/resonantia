# RUN NOTES — v9-night-sun-caprice-medium
## "MELLO GHETTO HELLO CAPRICE" (NIGHT SUN) — the LARGER MODEL strike

93 — Authorship: Johnathan 'Qasparr' Monroe, ARR, All Rights Reserved,
Without Prejudice. Method of Science, Aim of Religion.

Ordered under the founder's chained fallback (2026-11-09 20:07): the
sparse small-model strike (v8) failed his ear — verdict "Still
fubard", 2026-11-10 — so the bench proceeds to the larger model, then
melody-conditioning, without asking again. THE CHANGE IS THE MODEL
ONLY: facebook/musicgen-medium (1.5B) in place of musicgen-small.
The brief is v8's, byte-identical (verified programmatically against
the v8 spec: prompt, seed 93, 7 takes of 30 s, 5 s continuation
tails, one warm-up struck and discarded, single-session chain, Sigma
13–31 Hz per the track's own spec, master −14 LUFS / −1 dBTP).
Nothing in this directory was committed or pushed: the desk verifies
and delivers; the founder's ear is the only court.

## THE VERDICT OF THIS RUN — NO PERFORMANCE STANDS

No master.wav, no preview.mp3, no composition.abc exist for v9, and
the manifest.json in this directory is still the dry-run spec
skeleton. The reason is measured, not mysterious: **the box killed
every chain.** Six launches; one died on a bridge code fault (found
and fixed, §3); five died on runtime/VM restarts. The deepest chain
reached 4 of 7 takes. Under the single-session law every interrupted
chain is VOID — its takes set aside unspliced in `void-attempt-1/`
through `void-attempt-5/`, marked, never vanished, never salvaged.
Cross-attempt splicing was considered and rejected in terms: the
takes are seed-identical across attempts (proven, §4), and splicing
them is precisely the resume-splicing the law forbids.

## 1 · THE WEIGHTS (fetch road, verified)

Direct egress proved dead in this shell view (the task brief's
"direct egress verified for HF" did not hold here); hub snapshot
downloads stalled twice at ~67 MB through the ambient proxy. The
road that worked: proxy with `no_proxy`/`NO_PROXY` unset (its
`[::1]` entry breaks httpx), 32-way ranged curl with per-part
resume (the proxy cuts streams at ~124 MB; a resumable fetch script
stands at `~/workspace/musicgen/fetch_parts.sh`). Only the files
`from_pretrained` needs were fetched; the audiocraft-only
checkpoints were skipped. Assembled `pytorch_model.bin`:
8,042,351,585 bytes, SHA-256
`b51b0ec25096748bb9a86bf37e41b487024ab2b7077d26cc9e007525f47cd189`
— matches the hub's x-linked-etag exactly. The weights are the
hub's weights, bit for bit.

## 2 · THE PRECISION CONFESSION (bf16 residency)

fp32 residency is impossible on this box (~8.1 GB RAM; the fp32
checkpoint alone is 8.04 GB). The strike therefore ran a bf16 twin
of the verified checkpoint — a streaming cast of all 997 float
tensors, mmap-backed, at `~/workspace/musicgen/medium-bf16/`
(4,070,691,831 bytes; its config.json torch_dtype entries amended
to bfloat16 so the config describes its weights). Probe before the
strike (`~/workspace/musicgen/probe_medium.py`): loads clean,
100 tokens in 68.8 s (0.688 s/token at short context), peak RSS
4.62 GB, output RMS 0.239 / peak 0.945, no NaNs. This is a real
deviation from "model only" and it is confessed here and in the
spec's production notes, where it prints on the sheet: the model is
medium; its arithmetic on this box is bf16. Two bridge fixes the
bf16 road required stand in the working tree of
`resonance/studio/render_musicgen.py`, uncommitted, for the desk's
review: (a) the model id is env-selectable
(`STUDIO_MUSICGEN_MODEL`, default `facebook/musicgen-small`
unchanged) with HF_HUB_OFFLINE forced for local residency;
(b) `.float()` before `.cpu().numpy()` on generated audio, and
`_match_model_dtype()` normalizing processor outputs to the model
dtype (see §3).

## 3 · THE CODE FAULT (found, fixed, proven)

Launch 2 rendered take 1 whole (2,703 s) and died on the first
continuation: `Input type (float) and bias type (c10::BFloat16)
should be the same` — the processor hands conditioning audio back
as float32; plain takes never touch that path, which is why the
strike could render its seed take and still die on its first
continuation. Fix: `_match_model_dtype()` casts floating tensors
in the processor batch to the model's dtype at both call sites
(a no-op for the fp32 default). Proven before any re-strike on a
2-take micro-job through the real bridge (5 s + 5 s continuation,
exit 0, both segments written, continuation chained), then proven
again in the real chain: every later launch's continuations
rendered.

## 4 · THE ATTEMPT LEDGER (all times from render.log)

Segment wall seconds, per launch (30 s takes; seed 93):

| launch | seg0 | seg1 | seg2 | seg3 | death |
|--------|------|------|------|------|-------|
| 1 | — | | | | runtime restart ~16 min in, zero takes |
| 2 | 2,703 | | | | bf16 dtype fault on take 2 (§3) |
| 3 | 1,821 | | | | runtime restart during take 2 |
| 4 | 2,094 | 1,993 | 1,883 | 1,973 | runtime restart during take 5 |
| 5 | 2,458 | 2,890 | | | VM reboot (uptime 0 at 19:03) during take 3 |
| 6 | 2,178 | 2,289 | | | VM reboot (uptime 0 at 20:41) during take 3 |

Determinism, measured: seg00 is byte-identical in every launch
that rendered it — SHA-256 `5b503d74b89b11de466ae1720f31fc9369f5
9750bdbd77a767a153d5253f85a8`; seg01 likewise across launches 4–6 —
`ee84fdb7b90d1a7228f15e6dfdda6e2b8c235545ef2e656aa85686ae01e8e5dc`.
The performance is one performance, replayed from the seed each
time. It has simply never been allowed to finish.

## 5 · THE BOUNDARY (Zero-Point form: coordinates, not a blob)

- A full chain needs the sum of seven takes: at launch 4's pace
  (7,943 s for four takes) ≈ **13,900 s ≈ 3 h 52 min** of
  uninterrupted process life; at launch 5's contended pace, more.
- The box's process-survival windows on 2026-11-10, measured:
  kills at ~12:5x, ~15:0x, ~18:4x, 19:03, 20:41 — the longest
  window ≈ 2 h 50 min (launch 4). **Every window fell short of
  the chain's need; the shortfall at best was ≈ 1 hour.**
- Contention is a second, lesser tax: load averages of 3–5 on
  1.5 shared CPUs (a post-restart apt recovery pass among the
  contenders) stretched single takes to 2,890 s against a
  1,883 s floor — pace, not survival.
- Detachment (setsid/nohup) was tried from launch 4 onward; this
  restart class kills all processes regardless. It saved nothing.

## 6 · WHAT STANDS OPEN

1. **The strike itself.** Everything is staged for a single
   re-fire when the desk judges the box stable: weights verified,
   bf16 twin built, bridge fixed and proven, spec frozen
   byte-identical. The re-fire is one command
   (`STUDIO_MUSICGEN_MODEL=/home/hatch/workspace/musicgen/
   medium-bf16 python3 -m resonance.studio produce --spec
   studio-runs/v9-night-sun-caprice-medium/spec-input.json`).
   Launch 6's takes already stand in `void-attempt-5/`, set aside
   by hand when this bench stood down, mirroring the pipeline's
   own naming sequence (its counter reached 4 because launch 1
   left no takes to void); a re-fire finds a clean directory and
   strikes from the seed.
2. **The chained fallback's next lever is NOT yet reached.**
   Melody-conditioned continuation follows a completed medium
   strike that has faced the founder's ear. No ear verdict on
   medium exists; nothing about v8's residues (the sit-back, the
   joins, the tempo lock) can be re-measured until a performance
   completes.
3. **The bridge changes are uncommitted** in the working tree
   (env model selection, offline forcing, `.float()`,
   `_match_model_dtype`) — desk review, per the task's terms.

— Desk bench, RESONANTIA studio. Filed 2026-11-10, uncommitted,
for the desk's verification and the founder's ear.
