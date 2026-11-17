# THE ASCII ENGINE — DEMONSTRATION RUN REPORT

Struck XVII November 2026, from `resonance/studio/ascii.py` by
`build_demos.py` in this folder. Authorship attributed exclusively
to Johnathan 'Qasparr' Monroe, ARR, All Rights Reserved, Without
Prejudice. Method of Science, Aim of Religion.

## Hypothesis

The founder's reframing (XVII Nov 2026, 00:14 EST) seats ASCII as a
rendering engine in the DAMN NFO viewer lineage, the weighing
doctrine untouched. The hypothesis struck here: the studio's own
kit (stdlib + numpy + PIL, the visualizer's seat geometry and
analysis core) suffices to build that engine honestly — true CP437
bytes rather than Unicode lookalikes, a scene-form .nfo under the
80-column law, an image renderer whose glyphs are chosen by
measured coverage, and a dial frame drawn from gains the
visualizer itself weighed — with every claim in the demos read
from the records they describe, none invented.

## Method

The module was built pure-core first (CP437 table, ramp, layout,
slot geometry) and weighed by `tests/test_studio_ascii.py` (24
tests) before any demo was struck. The demos were then struck by
`build_demos.py`, which reads every Mugetsu fact from
`../mugetsu-hook-engine-run2/run2-summary.json` and
`manifest.json` at strike time, weighs the dial gains from the
sealed `master.mp3` through `visualize.decode_audio` +
`visualize.analyse` (no second weighing path), and renders the
founder's Pyramidasphere plate at two widths. Verification was
independent where a witness exists: the .nfo bytes were decoded
by BOTH the engine's own decoder and the standard library's cp437
codec, and the struck dial frame was compared line-for-line
against `dial_frame()` re-run on the recorded gains vector.

## Observation

**The CP437 table.** 148 seated glyphs (the 95 printable ASCII at
their own points, 53 extended), every entry verified against the
stdlib cp437 codec — zero mismatches, in the smoke check and in
the test suite. The classic control-picture glyphs at bytes
0x01–0x1E (the card suits the DAMN viewer drew) are NOT seated:
this host's codec witnesses control codes there, so those bytes
cannot be verified byte-for-glyph; the engine seats the printable
range and names the unseated range in its header.

**The plate.** At width 100 (33 rows) the sphere under-read: a
rounded dome of lattice, a denser knot where the star sits but no
star legible in it, the rings only hinted, the plaque lost. At
width 160 (53 rows) the sphere reads whole — round, rimmed,
latticed — and the star reads at its center as a bright dense core
with radiating structure (a `█` heart at the knot, rows 20–23),
honestly a brilliant core rather than a crisp star outline; the
rings trace faintly at the equator; the plaque and stand do not
resolve (dark brass on black, fine lettering — no width tried
would carry them, and none is claimed to). Both widths are kept
in this folder; 160 is the headline strike.

**The .nfo.** `mugetsu-run2.nfo`: 2,829 bytes, 54 lines, widest
line 78 — inside the 80-column law. Byte verification: the
engine's decoder and the stdlib codec return identical 54 lines;
54 CRLF endings, zero bare LF; every byte ≥ 0x80 is a seated glyph
(11 distinct); ╔ at 0xC9, ═ at 0xCD (×230), █ at 0xDB, ░ at 0xB0,
─ at 0xC4 all at their CP437 points. The facts in it are the run
folder's own: 219 phonemes (118 seated, 101 PASS_NATIVE), run 1
at 90.38% and run 2 at 99.52% realization, the master sealed at
−14.0 LUFS / −2.82 dBTP / exactly 320,000 bps, and the three proof
IDs of the chain.

**The dial frame.** The analysis reproduced the visualizer
demo's own reference band-energy exactly: 12.3706. Peak frame
152 of 402, t = 5.083 s. Gains at that frame span 0.546–0.809 —
at the hook's loudest moment the whole first-octave crowd is lit
between half and four-fifths, which is the true picture of a sung
vowel weighed in the band where the seats live; pairs sharing a
tone share a band and therefore a gain (13 distinct gains across
26 pairs, the 192 Hz seats quietest at 0.546, SS at 152 Hz
loudest at 0.809). The struck artifact equals `dial_frame()` on
the recorded vector line-for-line, and the CLI's `--gains` door
reproduces the same frame body from `gains-peak.json` alone.

**The axis is ordinal, and says so.** On the sworn log band the
tones crowd into 100–192 Hz; a metric character axis would crush
all 26 pairs into its first columns. The frame's probing spreads
the cluster so each pair owns a column — position is the dial's
order, the feet name the seated span (100 Hz / 192 Hz), and the
lamp heights are the measurement. Stated in the module, not
smoothed over here.

## Result

The engine stands: `resonance/studio/ascii.py` (the NFO writer,
the image renderer, the dial frame; CLI doors `nfo`, `render`,
`frame`, each printing a JSON summary). Tests: 24/24 new; the
full studio suite 259/259 (baseline 235 + 24, no regressions).
Pontifex untouched; ASCII weighs nothing; the doctrine in the
module's header states the reframing in terms.

## Failures and dead ends, at full size

1. **The decoder's first form ate its own line endings.** The
   first smoke strike failed the round trip: `decode_cp437`
   tried to seat the CRLF bytes as glyphs and refused byte 0x0D.
   The ending bytes are structure, not glyphs; the decoder now
   splits the stream into lines at the byte level before seating.
   The round-trip test pins the fix.
2. **One test's arithmetic, not the module's.** The leader test
   asserted the info colon at column 17; the composed line puts
   it at 16 — the dots run out TO the leader column and the colon
   sits on it. The test was corrected, with the reason at the
   assertion.
3. **Width 100 under-read the plate** (above). Adjusted to 160
   and both kept, as the record stands.
4. **The control-picture seat was considered and not taken**
   (above) — a named boundary of this host's witness, not a
   defect of the character set.
