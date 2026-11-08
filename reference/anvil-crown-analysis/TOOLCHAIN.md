<!--
93
TRANSCRIPTION-ANALYSIS — engraving toolchain check, 2026-11-08.
Findings are stated at the strength they were verified: CHECKED,
INSTALLED, or PROVEN (ran end to end and was eyeballed).
-->

# Engraving Toolchain — Check and Proof

### A Scientific Illuminist treatment of the notation road

**Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice)**
VIII day of November, Dies Solis, Sol in Scorpio, Anno V:xii e.n. (2026 e.v.)

**Classification:** Enterprise • Educational • Research & Development
**Method of Science, Aim of Religion**

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All
Rights Reserved, Without Prejudice. Right of claim hereby reserved and
coined under the authority of the Living Man.

---

## Verdict

**LilyPond is INSTALLED and PROVEN on this box.** One full page —
chord symbols, key signature, melody line, printed caveats — was
engraved from the phase-1 analysis outputs and visually inspected:
[`hook-fragment.pdf`](hook-fragment.pdf) (1 page, Letter, 73,836
bytes), generated from [`hook-fragment.ly`](hook-fragment.ly) by
[`make_test_page.py`](make_test_page.py).

## What was checked, in order

1. **PATH: absent (CHECKED).** No `lilypond`, `abcm2ps`, `musescore`,
   `timidity`, or `abc2midi` on this box at check time.
2. **apt route: viable but deferred (CHECKED, not installed).** The
   Ubuntu 24.04 (noble) sources are configured, but the package lists
   were stale in this filesystem view (`apt-cache policy lilypond`
   empty), and the apt frontend was held first by an `apt-get update`
   and then by the scheduled Enclave Unity desktop install — a large
   job this desk did not contend with for the dpkg lock. Ubuntu
   universe carries LilyPond 2.24.x; that route remains open for a
   future foreground install once the frontend is idle, and a
   completed foreground transaction is the kind that survives this
   VM's restart recovery.
3. **Official binary bundle: INSTALLED.** LilyPond's self-contained
   Linux bundle, version **2.26.0**, fetched from the project's GitLab
   release address (42,590,078 bytes) and unpacked to the durable
   tools directory, per house convention:
   - binary: `~/workspace/bin/lilypond-2.26.0/bin/lilypond`
   - version string verified: *GNU LilyPond 2.26.0 (running Guile 3.0)*
   - the bundle also ships `abc2ly`, `midi2ly`, and `musicxml2ly` —
   directly relevant to the house rule that notation travels as ABC:
   an ABC master can now be converted to an engraved page in-house.
4. **Proof render: PROVEN.** `lilypond -o hook-fragment
   hook-fragment.ly` completed clean; the PDF was rasterised and
   read by eye. One defect was found on inspection — the long
   composer/tagline strings overflowed the page margins (LilyPond
   header fields do not wrap) — shortened, re-rendered, re-inspected:
   clean. Nothing unverified ships; this page was no exception.

## Limits of the chosen route, stated plainly

- The bundle lives outside apt: no automatic updates, and version
  discipline is the desk's own job. It sits under `~/workspace`, so
  VM rootfs resets do not take it (the apt cache lesson, applied in
  reverse: durable things live in the workspace tree).
- LilyPond engraves; it does not audit. It will set a wrong note as
  beautifully as a right one — which is why the proof page carries
  its caveats on its face, and why phase 2 is a hand audit against
  the audio, not a bigger LilyPond run.

## Alternatives surveyed (recorded; not needed)

- **apt `lilypond` (2.24.x, universe):** the standard route once the
  frontend frees; older than the bundle by two minor series.
- **abcm2ps (apt):** ABC-first engraving, consistent with the house
  ABC rule, but typographically weaker than LilyPond and behind the
  same apt lock at check time.
- **music21 (pip):** a musicology library, not an engraver — it
  still shells out to LilyPond or MuseScore to make a page.
- **reportlab-drawn staff (pip):** hand-rolled PDF staff lines; a
  last resort with poor musical typography. Rejected while any real
  engraver stands.

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All
Rights Reserved, Without Prejudice.

93 — Live, Love, and let Love, Live.
