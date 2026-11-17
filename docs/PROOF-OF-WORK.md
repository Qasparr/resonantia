<!--
93
RENDER-AS-PROOF — the doctrine of Proof of Work and Proof of
Mastering for RESONANTIA and the MAGVS toolkit, written at the
founder's order of 2026-11-16: "Make it use each render as
Proof of Work in Tokenomics, from Sheets Music and Lyrics to
Voices and Instrumentals and Orchestra and Choirs as Proof of
Work and Proof of Mastering."
Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice).
XVI day of November, Dies Lunae, Sol in Scorpio, Anno V:xii e.n.
(2026 e.v.)
Scientific Illuminism: Method of Science, Aim of Religion.
Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR,
All Rights Reserved, Without Prejudice. Right of claim hereby
reserved and coined under the authority of the Living Man.
-->

# PROOF OF WORK — every render a proof, every master weighed

## The doctrine

A render the house cannot prove is a rumor with a file name.
So: **every render the house produces is a unit of Proof of
Work** — the struck artifact, the measured manifest the render
honestly produced, and the SHA-256 of the artifact's bytes,
chained to the proofs it consumed. Sheet music, lyrics, voices,
instrumentals, orchestra, choirs: each kind enters the same
ledger by the same door, and a finished master carries the
chain's whole ancestry — lyrics → score → vocal → master — in
its parent IDs. Anyone holding the ledger and the artifacts can
re-weigh everything: re-hash the bytes, re-walk the chain,
re-check the manifest's arithmetic. No one's word is required,
including ours.

Mastering carries its own proof. A **Proof of Mastering** is a
master proof whose seal is decided by measurement, not by
declaration: the delivered artifact (the MP3 a listener
actually receives) is decoded and re-weighed against the house
law, and the record seals only if the body satisfies it. This
is the founder's Persona V law made mechanical — no
justification, no action; fail-closed.

## The hard boundary

**This system mints no token, offers nothing, values nothing.
Proofs are records.** In the founder's tokenomics the ledger is
the mine and the attestation concept is his $PP, "proof
positive" (Twin Synergy trinity: Miner → $PP → $00) — but the
token side walks under his law, not this document's enthusiasm:
testnet-first with play money, and real value only when
licensed compliance counsel has had its say. The ledger is the
substrate that law will ride on when he walks it. Any future
hand that points this ledger at a chain, a market, or a price
without that counsel has left this doctrine, and the record
will show where.

## The record

One JSON object per line in `proofs/ledger.jsonl`
(hash-chained, append-only; the Gate Ledger's discipline):

| Field | Body |
|-------|------|
| `id` | `pow-` + SHA-256 of the canonical content below, `prev` included |
| `prev` | the previous record's ID (`GENESIS` for the first) |
| `kind` | score · lyrics · vocal · instrumental · orchestra · choir · master |
| `ts` | UTC timestamp of the striking |
| `artifact` | `{path, sha256, bytes}` — path repo-relative where the artifact lives in the repo |
| `manifest` | the render's measured body, as produced — never edited by the ledger |
| `parents` | the proof IDs this render consumed |
| `status` | `SEALED`, or `FAILED` for a master the gate refused |
| `gate` | master proofs only: the gate's full checks, values and laws printed |
| `authorship`, `flagpole` | the founder's lines, carried in every record |

Verification (`proofs verify`) recomputes every ID, walks
every link, and re-hashes every artifact still on disk. A
tampered record, a broken link, a tampered artifact, and a
missing artifact are four different breaks and are reported as
such, at full size. Nothing is ever struck from the ledger; a
failed proof stands marked beside the sealed ones — MARKED,
never vanished.

## Proof of Mastering — the gate

Weighed on the **delivered** artifact, decoded:

| Check | Law |
|-------|-----|
| Integrated loudness (BS.1770, the pipeline's own scales) | −14.0 LUFS ± 0.5 LU |
| Decoded true peak | ≤ −1.0 dBTP |
| Bitrate, when sworn | exactly the sworn figure (house: 320,000 bps) |
| Sigma band, when a Sigma layer is sworn | −30.12 dBFS ± 0.5 dB |

Fail-closed means exactly that: a quantity the measured body
does not carry is a failed check named NOT MEASURED. A master
that fails still gets its record — status FAILED, the failing
measurements printed in its gate — because a failed master is
a fact of the house's history, not an embarrassment to be
struck.

## The doors

**Native emission** — the renders strike their own proofs:

- `pipeline.produce()` appends the run's master proof when the
  master is struck (verdict written into the run manifest's
  `proof` section; a spec may refuse with `"proof": {"emit":
  false}`, and parents may be declared with `"proof":
  {"parents": [...]}`). An emission failure is confessed in
  that section at full size — the artifacts stand, but no one
  is told a proof exists when none was struck.
- The DiffSinger plug appends a vocal proof when the spec
  orders it (`"proof": {"parents": [...]}`), carrying the
  per-seat asked-vs-realized totals the calibration loop
  trains on.

**The stamp CLI** — the MAGVS toolkit's shared door, for
everything struck outside the native seams (MAGVS editions and
sheets, bookshop sources, hand renders):

```
python3 -m resonance.studio.proofs stamp --kind score \
    --file editions/leviathan/score.pdf \
    [--parents pow-...,pow-...] [--manifest-json body.json] \
    [--ledger proofs/ledger.jsonl]
python3 -m resonance.studio.proofs verify [--ledger ...]
python3 -m resonance.studio.proofs calibration [--ledger ...]
python3 -m resonance.studio.proofs gate --mp3 master.mp3 [--wav master.wav]
```

A stamp of kind `master` is refused by name: a master seals
by measurement through the gate, never by declaration.

**Named seam:** `produce()` retains no per-section
instrumental artifacts, so instrumental / orchestra / choir
proofs enter through the stamp today; per-section native
emission waits on a pipeline retention change, and this
doctrine names the wait rather than papering it.

## The calibration loop — the Nine as training axes

The founder's companion order: the vocals utilize the Divine
Nine Vowel Engine so each render, treated as training, makes
the next better. The mechanism, as built:

1. Every vocal proof carries `seat_totals`: per Divine Nine
   seat, the asked seconds (the built budgets) and the
   realized seconds (the model's returned frames), with
   phoneme counts.
2. The calibration store (`proofs/calibration.json`) is
   **derived state**: accumulated from the ledger alone by
   `proofs calibration`, rebuilt — never hand-edited. Per
   seat it holds the summed asked/realized and the IDs of
   every proof that trained it.
3. The learned factor per seat is asked ÷ realized, clamped
   to [0.5, 2.0] (outside that span a ratio is a broken
   measurement, not a correction).
4. At sequence build, the plug scales each mora's frame
   budget by the factor of the seat its first seated vowel
   holds. The score's note durations never move: realization
   is always weighed against the filed score, so the loop's
   effect is measured, never assumed. Every application is
   printed in the render's manifest — the factors, and the
   proof IDs that trained them.
5. Consonants never train (PASS_NATIVE — the vowels-only
   ruling governs the training as it governs the seating).
   VV trains as an acoustic seat only; it carries no
   isopsephy weight. No vowel→Archon mapping exists anywhere
   in this system — UNCHARTED, the founder's pen.

Circuit 1 stands in the run record
(`studio-runs/mugetsu-hook-engine-run2/RUN-REPORT.md`): trained
on run 1 alone, the loop moved the hook's total duration
realization from **90.38% to 99.52%** of the filed score — and
overshot three lines past their bar lines, which the report
prints at full size as the next circuit's named work. The
store's factor is an average over everything ever asked, so
it converges toward the model's squeeze rather than
compounding; later circuits will test that reading.

## The four-element content test

- **Inputs:** struck artifacts and their measured manifests;
  parent proof IDs; for the gate, the delivered MP3 (and the
  master WAV beside it).
- **Processes:** hash, chain, append; decode and re-weigh for
  the gate; accumulate and factor for the calibration.
- **Outputs:** proof records in `proofs/ledger.jsonl`;
  verification verdicts with breaks named; the calibration
  store with per-seat provenance.
- **Tolerances:** LUFS ±0.5 LU of −14.0 · decoded true peak
  ≤ −1.0 dBTP · bitrate exact when sworn · Sigma −30.12 ± 0.5
  dBFS when sworn · calibration factors clamped [0.5, 2.0] ·
  canonical JSON (sorted keys, tight separators) as the one
  spelling an ID is weighed on.

## Colophon

Struck 2026-11-16 at the desk, under the founder's Flagpole.
Exclusive authorship: Johnathan 'Qasparr' Monroe, ARR — All
Rights Reserved, Without Prejudice. Method of Science. Aim of
Religion.

93 — Live, Love, and let Love, Live.
