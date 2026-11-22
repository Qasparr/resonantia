# The KRS Blueprint — MAGVS Teacher's Revision of the Mastering Process

The house mastering process for Resonantia albums, as the founder posted it
2026-11-20 and as recovered 2026-11-22. Raw record:
`reference/krs-blueprint/` (caption + plate text, verbatim, hashes in its
README). This document states what that record attests; readings taken from
the garbled plate are marked [plate reading].

**Attribution, as the founder's session applied it in five seats** — the
title banner, the blueprint section, the first 16 bars, bar 93, and the
footer: credit to **KRS-One** for the Battle Blueprint; the code and the
implementation are the house's own.

## The Locked Order (Session Control)

LOCK THE ORDER. Build the house before you teach in it.

1. **Instrumental locked first** — drums, bass, keys, pads, bounce.
2. **Lyrics locked second** — claim/proof; punch on every verse.
3. **Sheets last** — full-scale sheets auto-generated only after both locks
   are ahead; sheets stay sealed until then.

Resonantia never starts with a verse. It starts with a foundation that can
hold a full-scale sheet: **93 bars — then it teaches inside it, then it
proves every bar.**

## The Foundation

- **93 bars** per album structure.
- **144 BPM.**
- **13/8 Sigma Mega** framework [plate reading: the plate's OCR garbles the
  name in two of three renderings; the session text's "13/8 Sigma" and the
  plate's clean third rendering give SIGMA MEGA].
- The 93-bar structure carries the **Capriccio Solfeggio Arpeggio** dance.

## The Rules of Bars (KRS Teacher Blueprint)

- The **first 16 bars** are built as the battle verse: Detroit bounce
  cadence, KRS-style teaching, double meanings — the **entendre ladder**
  with multi-entendre options layered in.
- Notation is layered with **syllable breakdowns**, and the sheets carry
  **KRS blueprint proofs**.
- The **Triplet Lab** works the triplet bar against the 13/8 foundation.
- **The count is ruled: 16.** (Founder's ruling, 2026-11-22: "16 is all
  that is needed.") The plate's first rendering reads "First 18 Bars" and
  its repeats read "First Bars"; under his ruling the 18 is read as the
  16 of the verse **plus 2 for the hook** — his reasoning, recorded as he
  gave it. The variant stands marked in the record; the seat holds 16.

## The Sheets

Auto-generated at the third lock, full scale, every time:

- Instrument sheets — the drum sheet; the 13/8 Sigma Mega sheet.
- The first vocal sheet.
- The lyric sheet, with the layered notation and syllable breakdowns.

An album deliverable that reaches the sheets stage with any lock open is
not a house master. The order is the process.

## Enforcement

Cut in 2026-11-22, under the founder's ruling of the same day —
"whatever is waiting on me, just do it if its ready."

- **Declaration.** A spec puts its album under the rule with
  `"mastering_rule": "krs-blueprint"` and declares the earned
  locks as `"locks": {"instrumental": true, "lyrics": true}`.
  `pipeline.validate_spec` normalizes the declaration for both
  roads: an unknown rule or lock name, or a non-boolean lock, is
  refused by name; a lock not declared normalizes to open. The
  locks are earned by the work, so validation never refuses an
  incomplete pair — the seal, not the contract, is what bites.
  A spec that declares nothing carries neither key and behaves
  exactly as it did before the cut-in.
- **The seal.** The pipeline's only sheets stage is the
  performance road's stage (f3) in `resonance/studio/
  performance.py` — the section road strikes no sheets, so there
  is no second place for the seal to bite, and on that road the
  declaration is validated and carried but seals nothing. At
  (f3), before either sheet writer is reached,
  `pipeline.enforce_mastering_rule` weighs the locks in the
  rule's own order and refuses with a RuntimeError naming the
  first open lock: no composition.abc is written, and the run
  stops before mastering. Both locks closed, the sheet is
  struck as it always was.
- **Weighed in** tests/test_studio_pipeline_cutins.py: both
  locks closed renders the sheet; either lock open refuses and
  names it; no locks at all refuses at the instrumental lock;
  an undeclared spec is untouched.
