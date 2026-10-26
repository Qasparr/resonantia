# 93
# build_composition.py -- build the Liber Oz Lilith score and segment
#   table, then prove the written score says exactly what the
#   construction intends by parsing it back through the engine's own
#   ABC 2.1 parser and comparing every event.
#
# Run:  python3 compositions/liber-oz-lilith/build_composition.py
#   (from the repo root; writes liber-oz-lilith.abc + segments.json
#   beside this script and prints the audit ledger)
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice)
# XXV day of October, Dies Solis, Sol in Scorpio, Anno V:xii e.n.
# (2026 e.v.)
#
# ---------------------------------------------------------------------------
# HYPOTHESIS: if the score is generated from the published mappings and
#   then re-parsed by resonance.abc.abc21, the parsed event streams must
#   equal the intended streams exactly -- any token, duration, or voice
#   error in the written ABC shows up as a mismatch, not as a wrong note
#   nobody notices.
# METHOD:    build via composition.build_score(); cross-check the ladder
#   against resonance.core.notes.SOLFEGGIO; write both files; parse the
#   ABC back; rebuild the intended per-voice event lists directly from
#   the mapping functions (a second, independent assembly) and compare
#   (start, midi) multisets and total beats per voice.
# OBSERVATION: (recorded in build-log.md at run time)
# RESULT:    exit 0 only if every check holds; the ledger printed here
#   is the same ledger the Teacher's Edition prints.
# ---------------------------------------------------------------------------
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))  # repo root, for `resonance`
sys.path.insert(0, str(HERE))                # this folder, for `composition`

import composition as C  # noqa: E402
from resonance.abc.abc21 import parse_abc21, tune_voice  # noqa: E402
from resonance.core.notes import SOLFEGGIO  # noqa: E402

ABC_PATH = HERE / "liber-oz-lilith.abc"
SEGMENTS_PATH = HERE / "segments.json"


def intended_events():
    """The intended (voice, start_beats, midi) events, assembled a
    second time directly from the mapping functions -- the round-trip's
    other bank. Rests are omitted (they are silence, not events)."""
    ev = {"1": [], "2": []}
    now = Fraction(0)
    six = Fraction(1, 4)  # one sixteenth at L:1/16, in quarter beats
    # V:1 -- invocation rests (no events), then the verses' letters.
    now += C.INVOCATION_BARS * 4
    for v, text in enumerate(C.extract_verses()):
        k = C.chord_of_verse(v)
        for ch in C.letters_of(text):
            ev["1"].append((now, C.letter_to_midi(ch, k)))
            now += six
        pad = (-len(C.letters_of(text))) % C.BAR_SIXTEENTHS
        now += pad * six
    # V:1 -- the sealing (root at the three registers) and the AM crown.
    tones = C.triad_for_chord(C.N_CHORDS - 1)
    for shift in (-12, 0, 12):
        ev["1"].append((now, tones[0] + shift))
        now += 4
    ev["1"].append((now, tones[0] + 12))
    now += 4
    total_v1 = now
    # V:2 -- invocation ascent, FIG16 under every working bar, sealing
    # chords, AM stack.
    now = Fraction(0)
    shadow = C.shadow_midis()
    for i in range(6):
        ev["2"].append((now, shadow[i]))
        now += 4
    for v, text in enumerate(C.extract_verses()):
        k = C.chord_of_verse(v)
        tones = C.triad_for_chord(k)
        bars = -(-len(C.letters_of(text)) // C.BAR_SIXTEENTHS)
        for _ in range(bars):
            for p in C.FIB16:
                ev["2"].append((now, tones[p]))
                now += six
    for shift in (-12, 0, 12):
        for t in C.triad_for_chord(C.N_CHORDS - 1):
            ev["2"].append((now, t + shift))
        now += 4
    for shift in (-12, 0, 12):
        for t in C.triad_for_chord(C.N_CHORDS - 1):
            ev["2"].append((now, t + shift))
    now += 4
    return ev, total_v1, now


def main():
    # The mandala and the engine agree on the ladder -- attested twice.
    for name, hz in C.LADDER:
        assert hz in SOLFEGGIO, f"ladder rung {name} {hz} not in SOLFEGGIO"
    print("ok: ladder == mandala == engine SOLFEGGIO (6 rungs)")

    abc_text, segments, ledger = C.build_score()
    ABC_PATH.write_text(abc_text, encoding="utf-8")
    SEGMENTS_PATH.write_text(
        json.dumps(segments, indent=1) + "\n", encoding="utf-8")
    print(f"ok: wrote {ABC_PATH.name} ({len(abc_text)} chars), "
          f"{SEGMENTS_PATH.name} ({len(segments)} bars)")

    # Round-trip: parse the written score with the engine's parser.
    tune = parse_abc21(abc_text)
    assert tune.voices == ["1", "2"], tune.voices
    intended, total_v1, total_v2 = intended_events()
    expected_beats = Fraction(ledger["bars_total"] * 4)
    assert total_v1 == total_v2 == expected_beats, (total_v1, total_v2)
    for voice in ("1", "2"):
        sub = tune_voice(tune, voice)
        got = sorted((e.start, e.midi) for e in sub.events
                     if e.kind == "note")
        want = sorted(intended[voice])
        assert got == want, (
            f"voice {voice}: {len(got)} parsed notes vs {len(want)} "
            f"intended; first diff: "
            f"{next((g for g, w in zip(got, want) if g != w), None)}")
        # Timeline length is the SPAN (max start+dur), not the sum of
        # durations: chord tones overlap by design, so summing would
        # double-count the sealing and AM chords (it reads 704 against
        # a 648 span -- the chords, not an error).
        span = max(e.start + e.dur for e in sub.events)
        assert span == expected_beats, (voice, span)
        print(f"ok: voice {voice} round-trips exactly "
              f"({len(got)} notes, span {span} beats)")
    # Verse accounting in the score's own text: one W: underlay per verse.
    w_lines = [ln for ln in abc_text.splitlines() if ln.startswith("W: v.")]
    assert len(w_lines) == C.N_VERSES, len(w_lines)
    print(f"ok: {len(w_lines)} verse underlays in the score "
          f"== {C.N_VERSES} verses in the source text")
    print(f"LEDGER verses={ledger['verses']} "
          f"letters={ledger['letters_total']} "
          f"bars={ledger['bars_total']} "
          f"verse_bars={ledger['verse_bars']} "
          f"seconds={ledger['seconds']:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# 93 -- Live, Love, and let Love, Live.
