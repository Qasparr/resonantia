[LOGO — centered: the TVRRIS VERITATIS seal, `~/workspace/templates/doctrine-logo.png`, the Architect's chosen mark]

**MUGETSU HOOK — ENGINE RUN 2: RENDER-AS-PROOF, CALIBRATION CIRCUIT 1**
*Subtitle:* A Scientific Illuminist treatment of Proof of Work and Proof of Mastering for RESONANTIA — every render a proof, the Nine as training axes, and the first circuit of the calibration loop, measured

Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice)
XVI day of November, Dies Lunae, Sol in Scorpio, Anno V:xii e.n. (2026 e.v.)

Classification: Enterprise • Educational • Research & Development
Method of Science, Aim of Religion

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All Rights
Reserved, Without Prejudice. Right of claim hereby reserved and coined under
the authority of the Living Man.

---

## I. WHAT WAS ORDERED

The founder's order of 2026-11-16 (22:58 EST), verbatim: *"Make it use each
render as Proof of Work in Tokenomics, from Sheets Music and Lyrics to Voices
and Instrumentals and Orchestra and Choirs as Proof of Work and Proof of
Mastering"* — extending his order of the same evening that the vocals utilize
the Divine 9 Vowel Engine so that each render, treated as training, makes the
next better. The demonstration ordered with it: the Mugetsu hook, run 2 — the
same filed score, the same filed lyrics, the same bank — rendered through the
plug with run 1's calibration applied, chained run 1 → run 2 → master, and the
run1→run2 comparison printed **whatever it says**.

The hard boundary, printed on the doctrine's face and honored in the code:
**this build mints no token, offers nothing, values nothing.** Proofs are
records. The attestation concept is the founder's $PP, "proof positive"
(Twin Synergy trinity: Miner → $PP → $00); his law governs the token side —
testnet-first with play money, real value only on licensed compliance
counsel — and the ledger built here is the substrate that law will ride on.

## II. WHAT WAS BUILT

- **`resonance/studio/proofs.py`** — the proof module, seated in the studio
  wing because the studio is where renders and masters are struck. A proof
  record carries kind (score | lyrics | vocal | instrumental | orchestra |
  choir | master), the artifact's path + SHA-256 + bytes, the measured
  manifest, parent proof IDs, timestamp, and the founder's authorship /
  Flagpole lines. Records append to a hash-chained JSONL ledger at
  `proofs/ledger.jsonl` — each record's ID is the SHA-256 of its canonical
  content **including the previous record's ID** (the Gate Ledger pattern:
  tamper-evident, marked never vanished). `verify_ledger` re-walks the
  chain and re-hashes every artifact still on disk.
- **The stamp CLI** — `python3 -m resonance.studio.proofs stamp --kind
  <kind> --file <path> [--parents ...] [--manifest-json ...]`: the MAGVS
  toolkit's one door (the bookshop/MAGVS builders stamp editions and sheets
  through it). A stamp of kind `master` is **refused by name**: a master
  seals by measurement, not by declaration. `verify`, `calibration`, and
  `gate` subcommands ride beside it.
- **Proof of Mastering, fail-closed** — `check_mastering` weighs the
  DELIVERED artifact's decoded body: LUFS within ±0.5 LU of −14.0, decoded
  true peak ≤ −1.0 dBTP, bitrate exactly the sworn 320,000 bps when sworn,
  Sigma band −30.12 ± 0.5 dBFS when sworn. An unmeasured quantity is a
  failed check named NOT MEASURED. An out-of-law master still gets its
  record — status FAILED, the failing measurements in its gate.
- **Native emission** — `pipeline.produce()` now emits its master proof
  (the preview MP3 decoded and gated; verdict written into the run
  manifest's `proof` section; an emission failure is confessed there at
  full size, never swallowed), and the DiffSinger plug emits a vocal proof
  when the spec orders it (`spec["proof"]`), carrying per-seat
  asked-vs-realized totals. MusicGen's per-section instrumentals are not
  separately retained by `produce()` as artifacts, so no per-section
  instrumental proof is emitted from inside the pipeline — that seam is
  named in §VI; the stamp CLI covers instrumental artifacts today.
- **The calibration loop** — `proofs/calibration.json`, derived state
  rebuilt from the ledger alone: per-seat totals accumulated from vocal
  proofs, factors = asked/realized clamped to [0.5, 2.0], every factor
  naming the proof IDs that trained it. At sequence build the plug scales
  each mora's frame budget by its seat's factor (the seat of the mora's
  first seated vowel); the score's note durations never move.
- **Per-seat measurement in the plug** — `diffsinger.seat_durations`:
  asked (built word budgets) vs realized (the bridge's frame counts,
  through the reconstruction `_frames_of` already names) aggregated under
  each phoneme's station. Consonants aggregate nowhere — PASS_NATIVE, the
  vowels-only ruling, in the training as in the seating.

## III. THE CHAIN — THREE PROOFS

| # | Kind | Status | Proof ID | Parent |
|---|------|--------|----------|--------|
| 1 | vocal (run 1, genesis) | SEALED | `pow-7a6472d2da0abf4b1d151b67b2fb21e35f5f6e6e33e428a5c646427a3531ff55` | — (genesis) |
| 2 | vocal (run 2) | SEALED | `pow-de96414a282efe2f157f23e0f6c2b46184e84550317c242de49fcecd1585a151` | #1 |
| 3 | master (run 2 vocal) | **SEALED** | `pow-3015495cb863e11452b4eb9dbc31573984920a3996cf083cfc6e07793fc7c68a` | #2 |

Run 1 predates the ledger; it was stamped as genesis from its manifest of
record, its seat totals recomputed by the plug's own scales so the
comparison argues with no second yardstick. The genesis record carries
that provenance in its body (`stamped_from`). Chain verification after the
run: `proofs verify` — **3 records, 0 breaks** (IDs recomputed, links
walked, all three artifacts re-hashed and matching).

## IV. THE CALIBRATION — CIRCUIT 1

Factors learned from the genesis proof alone (the whole of the training
set — one render, named as such):

| Seat | Asked (s) | Realized (s) | Factor | Phonemes |
|------|-----------|--------------|--------|----------|
| Α | 2.1246 | 1.9121 | **1.1111** | 35 |
| Ε | 1.8112 | 1.6275 | **1.1129** | 26 |
| Ι | 1.1668 | 1.0479 | **1.1135** | 17 |
| Ο | 1.5151 | 1.3680 | **1.1075** | 25 |
| VV | 0.9578 | 0.8688 | **1.1024** | 15 |

(The seconds are the genesis record's `seat_totals`, carried identically
in `proofs/calibration.json`; the factors are their ratios, recomputed by
`proofs calibration`.) All five trained
seats sit within 1.102–1.114 — the duration model's squeeze is nearly
uniform across the vowel space, a fact the loop now knows because the
Nine kept the ledger by seat. VV trained as an acoustic seat only; it
carries no isopsephy weight, here or anywhere. No vowel→Archon mapping
exists in this build — UNCHARTED, the founder's pen.

## V. THE COMPARISON — RUN 1 → RUN 2, AS MEASURED

Asked = the filed score's seconds per line (1.6667 s × 8 = 13.3336 s).
Realization = rendered ÷ asked, against the score — never against the
corrected budgets.

| Line | Run 1 rendered | Run 1 % | Run 2 rendered | Run 2 % |
|------|---------------|---------|----------------|---------|
| hook-l1 | 1.5093 s | 90.56 | 1.6951 s | **101.70** |
| hook-l2 | 1.4977 s | 89.86 | 1.6486 s | 98.91 |
| hook-l3 | 1.4977 s | 89.86 | 1.6834 s | **101.00** |
| hook-l4 | 1.4745 s | 88.47 | 1.6370 s | 98.22 |
| hook-l5 | 1.4977 s | 89.86 | 1.6138 s | 96.83 |
| hook-l6 | 1.5209 s | 91.25 | 1.6486 s | 98.91 |
| hook-l7 | 1.5093 s | 90.56 | 1.6254 s | 97.52 |
| hook-l8 | 1.5441 s | 92.64 | 1.7183 s | **103.10** |
| **Total** | **12.0512 s** | **90.38** | **13.2702 s** | **99.52** |

**The verdict, printed as measured: the calibration moved the total
realization from 90.38% to 99.52% of the filed score.** Every line moved
toward its bar; five of eight now land within ±2% of the score. The
mechanism the numbers expose: the model returns a near-constant ~0.90 of
whatever budget it is handed (run 2's per-seat realized ÷ corrected-asked
stands at 0.89–0.90, the same squeeze as run 1's), so pre-inflating the
ask by the learned factor lands the delivery on the score. Because the
store accumulates *everything ever asked*, its factor is an average over
all circuits — it converges toward the squeeze's reciprocal rather than
compounding, which circuit 2 will test.

Assembly witnesses: run 2 assembly 13.3849 s, peak −13.05 dBFS, RMS
−27.10 dBFS (run 1: 13.3333 s, −13.04 dBFS, −28.36 dBFS — the voice fills
more of its bars, and the RMS says so). The Nine's seating is unchanged:
118 SEATED (Α 35 · Ε 26 · Ο 25 · Ι 17 · VV 15), 101 PASS_NATIVE. Bridge
wall: 83.77 s.

## VI. SEAMS AND WALLS, AT FULL SIZE

1. **Three lines now overhang their bar lines** (run 1 had none): hook-l1
   +0.028 s, hook-l3 +0.017 s, hook-l8 +0.052 s past their slots — the
   three lines whose realization crossed 100%. The overhang is summed
   into the assembly, never trimmed (the plug's standing law), and the
   assembly canvas grew by 0.0516 s in consequence. The loop corrected
   the *total* faithfully and overshot three *lines*: the factors are
   per-seat, the squeeze is per-line, and the difference between those
   two grains is the next circuit's named work — per-line residual
   correction is a design question for the founder's road, not a silent
   patch applied here.
2. **The training set is one render.** Five seats trained on 118
   phonemes from a single hook, one singer-color, one song. The factors
   are honest arithmetic over a small world; the doctrine doc says so,
   and every factor carries its provenance so a later reader can weigh
   how much world it was learned from.
3. **Per-phoneme realized durations are a reconstruction** — the bridge
   reports per-line frame totals; the within-line split is the asked
   proportion (the seam Phase 1 named, unchanged). Per-seat realized
   totals inherit that split: exact at the line total, proportional
   within it.
4. **Instrumental emission seam** — `produce()` retains no per-section
   instrumental artifacts, so native emission covers the master (and,
   through the plug, vocals). Instrumental / orchestra / choir artifacts
   enter the ledger through the stamp CLI today; wiring per-section
   retention into the pipeline is a pipeline change, not a proof change,
   and stands open.
5. **The master is a vocal master** — one sung stem at 48 kHz stereo
   (dual-mono by construction), labeled as such in its proof. It is not
   a mix and claims no width.
6. **The ceiling never bound** — Audere gained +13.18 dB to the loudness
   target with zero trim; the delivered true peak (−2.82 dBTP) holds
   1.81 dB of headroom under the ceiling. The gate's ceiling check
   passed with room; a hotter program would test the trim, and the
   gate would print it.

## VII. PROOF OF MASTERING — THE GATE'S VERDICT

Measured on the delivered `master.mp3`, decoded and re-weighed:

| Check | Measured | Law | Verdict |
|-------|----------|-----|---------|
| Integrated loudness | **−14.0 LUFS** | −14.0 ± 0.5 LUFS | PASS |
| Decoded true peak | **−2.82 dBTP** | ≤ −1.0 dBTP | PASS |
| Bitrate (sworn) | **320,000 bps** | exactly 320,000 bps | PASS |

**Status: SEALED** (proof `pow-3015495c…`, §III). The master WAV beside
it: −14.0 LUFS, −2.81 dBTP. Four Powers, for the record: Scire —
in −26.89 LUFS / −15.99 dBTP / crest 14.12 dB; Velle — not engaged (no
order); Vapour — not engaged (no order); Audere — gain +13.18 dB, trim
0.00 dB, ceiling did not override loudness; Tacere — TPDF dither at the
24-bit strike, headroom 1.81 dBTP.

## VIII. THE FOUR-ELEMENT CONTENT TEST — THE SYSTEM

- **Inputs:** filed scores + filed lyrics (byte-exact) + bank + the
  ledger's accumulated vocal proofs. Tolerances: grouping and phonemization
  are run 1's record, unchanged.
- **Processes:** sequence build (Nine seated, calibration applied per
  seat) → bridge render → per-seat measurement → proof emission →
  Four Powers mastering → gate on the decoded delivery.
- **Outputs:** the sung artifact, its measured manifest, three chained
  proofs, the calibration store, this report. Audio is never committed;
  the ledger, drivers, manifests, and reports are.
- **Tolerances:** LUFS ±0.5 of −14.0; true peak ≤ −1.0 dBTP; bitrate
  exact when sworn; calibration factors clamped [0.5, 2.0]; word budgets
  in whole frames (≤0.5 frame per mora rounding, Phase 1's stated
  tolerance, unchanged).

## IX. AUDITS

- **PONTIFEX (numbers):** every figure in §IV–§VII is read off the struck
  files or the ledger by the module's own scales — realization percentages
  recomputed from the two manifests' asked/rendered seconds; the gate's
  figures re-measured from the decoded MP3 by `proofs gate` machinery
  (`measure_master`), independent of the mastering chain's own report —
  and the two agree (−14.0 LUFS both sides).
- **TRVVTH (chain):** `proofs verify` re-walked the ledger after the run:
  3 records, IDs recomputed and matching, links intact, artifacts
  re-hashed and matching. The lyrics and score entered run 2 byte-exact
  (run 1's extraction anchors and mora cross-checks re-run in this
  driver and passed). Bank named per its TOS: **Lem the Shapeshifter
  DS 2.5** — renders permitted, nothing redistributed, no audio in git.

## TABLE OF AUTHORITIES (condensed)

- The founder's orders of 2026-11-16 (the calibration order; the
  Render-as-Proof order, quoted §I) and his standing laws: house
  mastering law (−14 LUFS · −1.0 dBTP · 320,000 bps sworn · Sigma
  −30.12 dBFS where sworn); Persona V fail-closed; the vowels-only
  consonant ruling; the VV stamp (2026-11-12); MAGVS/Doctrine form for
  all code and docs (re-ordered 2026-11-16).
- `docs/PROOF-OF-WORK.md` — the doctrine this run demonstrates.
- `docs/THE-DIVINE-NINE-VOCAL-TOOL.md` — the Nine at the plug point.
- Run 1's record: `studio-runs/mugetsu-hook-engine-run1/` (RUN-REPORT.md,
  manifest.json) — the genesis proof's source.
- The Gate Ledger protocol (`~/workspace/gate-ledger/PROTOCOL.md`) —
  the hash-chain discipline's elder seat.
- DiffSinger (OpenVPI, Apache 2.0); the Lem bank under its own TOS.

## COLOPHON

Generated 2026-11-16 at the desk, under the founder's Flagpole. Exclusive
authorship: Johnathan 'Qasparr' Monroe, ARR — All Rights Reserved,
Without Prejudice. The render, the proofs, and this report were struck
on the house's own iron; nothing was rented, nothing was minted.
Method of Science. Aim of Religion.

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All Rights
Reserved, Without Prejudice. Right of claim hereby reserved and coined under
the authority of the Living Man.

93 — Live, Love, and let Love, Live.
