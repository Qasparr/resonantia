# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# SPDX-License-Identifier: AGPL-3.0-only
"""
tests/test_liber_oz_lilith.py -- tests for the Liber Oz Lilith
composition (compositions/liber-oz-lilith/).

Run:  python3 tests/test_liber_oz_lilith.py   (from the repo root)
  or  python3 -m pytest tests/test_liber_oz_lilith.py

Style: each check prints "  ok: <name>"; any failure prints a FAIL
line and exits 1 -- the first red line is the diagnosis.

What is tested, and why: the composition's claims are (a) its data
(the ladder, the Fibonacci tables), (b) its mappings (letter -> pitch,
verse -> chord), re-derived here by an INDEPENDENT implementation
that shares no code with composition.py beyond the engine itself,
(c) its artifacts (the score parses and round-trips; the segment
table agrees with the chord table; the shipped WAV verifies by FFT
on sampled segment groups; the Teacher's Edition carries the IAO131
quotation exactly once, inside the standing budget).
"""
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "compositions" / "liber-oz-lilith"))

import composition as C  # noqa: E402
from resonance.abc.abc21 import parse_abc21, tune_voice  # noqa: E402
from resonance.core.io import read_wav, wav_info  # noqa: E402
from resonance.core.notes import SOLFEGGIO, freq_to_midi  # noqa: E402
from resonance.diagnostics.verify import verify_binaural  # noqa: E402

COMP = ROOT / "compositions" / "liber-oz-lilith"
FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok: {name}")
    else:
        print(f"FAIL: {name} {detail}")
        FAILURES.append(name)


# -- independent re-derivation (no composition.py mapping code) --------
def ind_verses():
    raw = C.SOURCE_TEXT.read_text(encoding="utf-8")
    body = raw.split("## THE TEXT")[1].split("## COMMENTARY")[0]
    out = {}
    for m in re.finditer(r"^\*\*(\d+)\.\*\*\s+(.*?)\s*$", body, re.M):
        t = re.sub(r"\[.*?\]", "", m.group(2))
        t = t.split("— Liber AL")[0].strip()
        out[int(m.group(1))] = t
    return out


def ind_letters(t):
    return [c for c in t.upper() if "A" <= c <= "Z"]


def ind_triad(k):
    sh = [freq_to_midi(hz) for _, hz in
          (("UT", 396), ("RE", 417), ("MI", 528),
           ("FA", 639), ("SOL", 741), ("LA", 852))]
    r = k % 6
    return sorted(sh[(r + 2 * i) % 6] for i in range(3))


def main():
    # (a) data ------------------------------------------------------------
    check("ladder is the mandala six, all in SOLFEGGIO",
          [hz for _, hz in C.LADDER] == [396, 417, 528, 639, 741, 852]
          and all(hz in SOLFEGGIO for _, hz in C.LADDER))
    check("FIB16 is the Fibonacci fold mod 3",
          C.FIB16 == (1, 1, 2, 0, 2, 2, 1, 0, 1, 1, 2, 0, 2, 2, 1, 0),
          str(C.FIB16))
    check("offsets climb the spiral by chord",
          [C.offset_of_chord(k) for k in range(13)]
          == [1, 1, 2, 3, 5, 8, 13, 1, 1, 2, 3, 5, 8])
    check("chord roots walk the ladder twice and return",
          [C.LADDER[k % 6][1] for k in range(13)]
          == [396, 417, 528, 639, 741, 852] * 2 + [396])

    # (b) the score artifact ---------------------------------------------
    abc_text = (COMP / "liber-oz-lilith.abc").read_text(encoding="utf-8")
    tune = parse_abc21(abc_text)
    check("score parses (abc21), two voices", tune.voices == ["1", "2"])
    w = [ln for ln in abc_text.splitlines() if ln.startswith("W: v.")]
    check("36 verse underlays == 36 verses in the source", len(w) == 36)
    for voice in ("1", "2"):
        sub = tune_voice(tune, voice)
        span = max(e.start + e.dur for e in sub.events)
        check(f"voice {voice} spans exactly 648 beats", span == 648)

    # independent letter-by-letter derivation of three verses
    verses = ind_verses()
    starts, beat = {}, 24  # 6 invocation bars x 4 beats
    for v in range(36):
        starts[v] = beat
        beat += (-(-len(ind_letters(verses[v])) // 16)) * 4
    ev = {e.start: e.midi for e in tune_voice(tune, "1").events
          if e.kind == "note"}
    for v in (0, 13, 30):
        k = (v * 13) // 36
        tones = ind_triad(k)
        want = []
        for ch in ind_letters(verses[v]):
            d = (ord(ch) - 65) % 6
            want.append(tones[d % 3] + 12 * (d // 3))
        got = [ev[Fraction(starts[v]) + Fraction(i, 4)]
               for i in range(len(want))]
        check(f"verse {v} re-derived independently ({len(want)} notes)",
              got == want)

    # (c) the segment table ---------------------------------------------
    segments = json.loads((COMP / "segments.json").read_text())
    by_section = {}
    for s in segments:
        by_section[s["section"]] = by_section.get(s["section"], 0) + 1
    check("162 bars: 6 invocation + 152 working + 3 sealing + 1 AM",
          len(segments) == 162 and by_section == {
              "invocation": 6, "working": 152, "sealing": 3, "am": 1},
          str(by_section))
    check("sealing + AM stand at UT 396, offset 1 (the seed)",
          all(s["carrier_hz"] == 396 and s["offset_hz"] == 1
              for s in segments if s["section"] in ("sealing", "am")))
    check("every working bar's carrier/offset is its chord's",
          all(s["carrier_hz"] == C.LADDER[s["chord"] % 6][1]
              and s["offset_hz"] == C.offset_of_chord(s["chord"])
              for s in segments if s["section"] == "working"))

    # (d) the WAV ----------------------------------------------------------
    wav = COMP / "liber-oz-lilith-binaural.wav"
    n_ch, sr, n_fr = wav_info(wav)
    check("WAV is 44.1 kHz stereo, 324.0 s",
          (n_ch, sr) == (2, 44100) and n_fr == 324 * 44100,
          f"{n_ch} ch {sr} Hz {n_fr} frames")
    audio, _ = read_wav(wav)
    bar = 88200
    # invocation bar 3 (MI 528, offset 1) and chord 13's span (bars
    # 154-158 in 1-based terms) and the sealing span (159-162).
    for a, b, carrier, offset, name in (
            (2, 3, 528, 1, "invocation rung MI"),
            (153, 158, 396, 8, "chord 13 span"),
            (158, 162, 396, 1, "sealing + AM")):
        verdict = verify_binaural(audio[:, a * bar:b * bar], offset,
                                  float(carrier), sample_rate=44100)
        check(f"WAV verifies: {name}", verdict["passed"],
              str(verdict["errors"]))

    # (e) the Teacher's Edition -------------------------------------------
    md = (COMP / "liber-oz-lilith-teachers-edition.md").read_text(
        encoding="utf-8")
    quote = ("the establishment of Life, Liberty, Love, and Light in "
             "the hearts of all men.")
    check("IAO131 quotation appears exactly once in the TE",
          md.count(quote) == 1, f"count={md.count(quote)}")
    check("IAO131 budget: 33 prior + 14 here = 47 <= 50",
          len(quote.split()) == 14 and 33 + 14 <= 50)
    check("the Author's fires dictum stands verbatim in the TE",
          "The fires engulf you and warm you and heal you." in md)
    check("the rite's full-text layer is marked OPEN",
          "[OPEN — the full-text layer" in md)
    pdf = COMP / "liber-oz-lilith-teachers-edition.pdf"
    check("TE PDF exists and is a PDF",
          pdf.exists() and pdf.read_bytes()[:4] == b"%PDF"
          and pdf.stat().st_size > 1_000_000)

    if FAILURES:
        print(f"\n{len(FAILURES)} liber-oz-lilith checks FAILED")
        return 1
    print("\nall liber-oz-lilith tests passed.")
    return 0


# pytest entry points (the script-style main above is the authority)
def test_all():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
