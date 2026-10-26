# 93
# composition.py -- Liber Oz Lilith: the Fibonacci Arpeggio of the
#   Solfeggio Harmonies. The construction itself: data, mappings, and the
#   score builder shared by build_composition.py (writes the ABC and the
#   segment table), render_composition.py (renders the binaural WAV), and
#   build_teachers_edition.py (prints the Teacher's Edition).
#
# Epigraph: "Live, Love, and let Love, Live." -- the Author's sealing
#   dictum for the Aeon of Ma'at, comma as dictated.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice)
# XXV day of October, Dies Solis, Sol in Scorpio, Anno V:xii e.n.
# (2026 e.v.)
#
# ---------------------------------------------------------------------------
# HYPOTHESIS (the Author's pattern, made exact): the six solfeggio rungs
#   printed on the Author's Axoneme mandala (UT 396, RE 417, MI 528,
#   FA 639, SOL 741, LA 852) can serve at once as binaural carriers,
#   chord roots, and the pitch field of a melody derived letter-by-letter
#   from the Lilith Revision text -- so that text, ground, and beat are
#   one body, and every note can be re-derived by any reader from the
#   published tables alone.
# METHOD:    deterministic mappings only; no randomness anywhere. The
#   letter-to-pitch map, the chord construction, the Fibonacci arpeggio
#   pattern, and the binaural offset table are pure functions, stated in
#   full below and printed again in the Teacher's Edition.
# OBSERVATION: on a six-rung ladder, skip-one (tertian) stacking yields
#   exactly two complementary trichords alternating by root parity; the
#   13-chord cycle therefore walks all six roots twice and returns to
#   the first root for the thirteenth chord -- the cycle closes where
#   it opened, which is the spiral's own shape.
# RESULT:    build_score() returns the ABC 2.1 text, the per-bar segment
#   table (carrier + binaural offset for every bar), and the ledger of
#   counts the audits check against.
#
# HONESTY: no medical or therapeutic efficacy is claimed for anything
#   built here -- not for the solfeggio frequencies, the binaural beats,
#   or the listening. The Author's stated aim for the work (Samadhi and
#   the Violet Flame) is recorded in the Teacher's Edition as HIS
#   framing, under his name; this code certifies frequencies and
#   mappings, nothing more.
# ---------------------------------------------------------------------------
import re
from fractions import Fraction
from pathlib import Path

# -- the ladder (ATTESTED data) ---------------------------------------------
# The six rungs exactly as printed on the Author's Axoneme mandala,
# UT..LA. Every one of the six is also a key of the engine's own
# resonance.core.notes.SOLFEGGIO table -- build_composition asserts the
# agreement, so the mandala and the engine can never silently diverge.
LADDER = (
    ("UT", 396),
    ("RE", 417),
    ("MI", 528),
    ("FA", 639),
    ("SOL", 741),
    ("LA", 852),
)
LADDER_HZ = tuple(hz for _, hz in LADDER)

# -- the Fibonacci sets (ATTESTED arithmetic) --------------------------------
# The spiral on the mandala counts 1, 1, 2, 3, 5, 8, 13, 21. FIB7 is the
# binaural offset cycle: the beat steps through these seven values, one
# per chord, "arpeggio the flow of the Sigma" implemented literally.
FIB7 = (1, 1, 2, 3, 5, 8, 13)


def _fib(n):
    """The first n Fibonacci numbers as the mandala prints them: 1,1,2,..."""
    out, a, b = [], 1, 1
    for _ in range(n):
        out.append(a)
        a, b = b, a + b
    return tuple(out)


# MECHANISM: the ground arpeggio's 16-step figure. Step j of every bar
#   sounds triad tone number FIB16[j] (mod 3) -- the Fibonacci sequence
#   itself, folded onto the three chord tones. The pattern is identical
#   in every bar of the working; what changes is the chord it walks.
# DOCTRINE:  the spiral is the fingerprint; the chord is the ground it
#   walks on. Figure and ground are separable so each can be audited.
FIB16 = tuple(f % 3 for f in _fib(16))  # (1,1,2,0,2,2,1,0,1,1,2,0,2,2,1,0)

# -- the frame (CONSTRUCTED, per the Author's amendments) --------------------
N_CHORDS = 13          # the 13 Sacred Chords: one full cycle, exactly once
N_VERSES = 36          # the Text of the Lilith Revision: verses 0..35
INVOCATION_BARS = 6    # one bar per rung, ascending: the ladder is called
SEALING_BARS = 3       # Mother tongue, Father tongue, Child: the seal x3
AM_BARS = 1            # the final sonority, named by the Author: AM
BAR_SIXTEENTHS = 16    # 4/4 at L:1/16 -- one bar line every 16 letters
BPM = 120              # Q:1/4=120: one bar = exactly 2.000 s at 44.1 kHz
SAMPLE_RATE = 44100

# The source text: Witness A, the September Lilith-voiced revision, as
# filed in the liberd repo. The composition maps THE TEXT section only.
SOURCE_TEXT = Path(
    "/home/hatch/workspace/liberd/libers/"
    "liber-oz-lilith-revision/Liber_OZ_Lilith_Revision.md")


def extract_verses():
    """The 36 verses of THE TEXT, in order, as spoken text.

    Extraction rule (published, mechanical): take the lines headed
    '**N.**' between '## THE TEXT' and '## COMMENTARY'; remove
    square-bracketed editorial annotations (they are apparatus, not
    speech -- vv. 29 and 34 carry them); remove the citation tail of
    v. 25 ('-- Liber AL, I:51.'), which is a citation, not speech.
    Letters A-Z only are mapped; everything else is a phrase mark.
    """
    raw = SOURCE_TEXT.read_text(encoding="utf-8")
    body = raw.split("## THE TEXT")[1].split("## COMMENTARY")[0]
    verses = {}
    for m in re.finditer(r"^\*\*(\d+)\.\*\*\s+(.*?)\s*$", body, re.M):
        t = re.sub(r"\[.*?\]", "", m.group(2))
        t = t.split("— Liber AL")[0].strip()
        verses[int(m.group(1))] = t
    if sorted(verses) != list(range(N_VERSES)):
        raise ValueError(
            f"source text must yield verses 0..{N_VERSES - 1}, "
            f"got {sorted(verses)}")
    return [verses[n] for n in range(N_VERSES)]


def letters_of(verse_text):
    """The A-Z letters of a verse, in order -- the atoms of the melody."""
    return [c.upper() for c in verse_text if c.isalpha() and c.isascii()]


# -- pitch machinery ---------------------------------------------------------
# MECHANISM: ABC notation names 12-TET pitches; the ladder's frequencies
#   are not 12-TET. The engine's own freq_to_midi defines each rung's
#   SHADOW -- the nearest notatable pitch (396 -> G4/67, 417 -> G#4/68,
#   528 -> C5/72, 639 -> D#5/75, 741 -> F#5/78, 852 -> G#5/80). The
#   score sings shadows; the binaural ground sounds the true rungs.
#   The duality is the design, and it is stated wherever it matters.
def shadow_midis():
    """The six rungs' 12-TET shadow pitches, via the engine's own table."""
    from resonance.core.notes import freq_to_midi
    return tuple(freq_to_midi(hz) for hz in LADDER_HZ)


def triad_for_chord(k):
    """Chord k's three shadow pitches, ascending. k is 0-based (0..12).

    Construction (published): the root rung is r = k mod 6; the triad
    stacks rungs {r, r+2, r+4} mod 6 -- skip-one stacking, the hexatonic
    analogue of building a triad in thirds. On six rungs this yields
    two complementary trichords: even roots give {UT, MI, SOL}'s
    shadows, odd roots {RE, FA, LA}'s. Chord 12 (the thirteenth) has
    root rung 0 again: the return.
    """
    shadow = shadow_midis()
    r = k % 6
    return tuple(sorted(shadow[(r + 2 * i) % 6] for i in range(3)))


def chord_of_verse(v):
    """Verse v's governing chord (0-based): floor(v * 13 / 36).

    The 36 verses are dealt across the 13 chords as evenly as integers
    allow: chords 0..11 govern three verses each, chord 12 governs the
    final two (vv. 34-35, the Sealing verses of the Text itself).
    """
    return (v * N_CHORDS) // N_VERSES


def offset_of_chord(k):
    """Chord k's binaural offset in Hz: the Fibonacci flow, FIB7[k mod 7].

    Chords 0..12 take offsets 1,1,2,3,5,8,13,1,1,2,3,5,8 -- the beat
    climbs the spiral and begins it again, in step with the roots.
    """
    return FIB7[k % len(FIB7)]


def letter_to_midi(letter, chord_k):
    """One letter -> one shadow pitch over the governing chord's triad.

    Mapping (published): the letter's ordinal (A=1 .. Z=26) minus one,
    mod 6, gives the degree d in 0..5. Degrees 0..2 are the chord's
    triad ascending; degrees 3..5 are the same triad an octave higher.
    The text-voice can therefore never leave the sounding chord: text
    and ground are one body by construction.
    """
    tones = triad_for_chord(chord_k)
    d = (ord(letter) - ord("A")) % 6
    return tones[d % 3] + 12 * (d // 3)


# -- ABC tokens ---------------------------------------------------------------
_PC_TOKEN = {0: "C", 1: "^C", 2: "D", 3: "^D", 4: "E", 5: "F", 6: "^F",
             7: "G", 8: "^G", 9: "A", 10: "^A", 11: "B"}


def midi_to_abc(midi):
    """MIDI -> ABC token in the engine parser's own octave convention.

    Uppercase = octave 4 (C4 = 60), lowercase = octave 5, apostrophes
    raise, commas lower. Sharps are written explicitly (^) because the
    score's key is C: no accidental is ever left to a key signature.
    """
    name = _PC_TOKEN[midi % 12]
    octave = midi // 12 - 1
    if octave == 4:
        return name
    if octave == 5:
        return name.lower() if not name.startswith("^") else \
            "^" + name[1].lower()
    if octave > 5:
        base = name.lower() if not name.startswith("^") else \
            "^" + name[1].lower()
        return base + "'" * (octave - 5)
    return name + "," * (4 - octave)


def _dur(midi, sixteenths):
    """A note token with an explicit sixteenth-count length."""
    return f"{midi_to_abc(midi)}{sixteenths}"


def _chord_token(midis, sixteenths):
    """An ABC 2.1 chord: lengths ride inside the brackets in this engine."""
    return "[" + "".join(_dur(m, sixteenths) for m in midis) + "]"


# -- the score ----------------------------------------------------------------
def build_score():
    """Build (abc_text, segments, ledger) for the whole composition.

    segments: one dict per bar, in sounding order --
      {bar (0-based), section, label, verse, chord (0-based or None),
       carrier_hz, offset_hz}
    The render script consumes this table for the binaural ground; the
    Teacher's Edition prints it as the pattern table. One table, three
    readers, no second transcription to drift.

    Bar layout (162 bars, each exactly 16 sixteenths):
      bars 0..5      the Invocation -- V:1 rests; V:2 sustains the
                     rungs ascending, one per bar; carrier = the rung;
                     offset = 1 Hz (the seed of the flow).
      bars 6..157    the Working -- the 36 verses in order; each verse
                     takes ceil(letters/16) bars, its last bar padded
                     with rests to the bar line (the verse breath).
                     V:2 walks the governing chord's triad by FIB16.
      bars 158..160  the Sealing -- the seal stated three times, in the
                     Mother tongue (triad at -12), the Father tongue
                     (triad as built), the Child (triad at +12): three
                     registers, one per tongue, over the final chord.
                     (The Author's dictation names the three tongues;
                     no file of his identifies them with historical
                     languages, and none is invented here.)
      bar 161        AM -- the final sonority: the final chord's triad
                     in all three registers at once; V:1 crowns it with
                     the root in the Child register. Carrier returns
                     to UT 396 at offset 1: the flow seals at the seed.
    """
    verses = extract_verses()
    shadow = shadow_midis()
    segments = []
    v1_lines = []   # (comment_or_None, abc_line, w_line_or_None)
    v2_lines = []

    def add_segment(section, label, verse, chord, carrier, offset):
        segments.append({
            "bar": len(segments), "section": section, "label": label,
            "verse": verse, "chord": chord,
            "carrier_hz": carrier, "offset_hz": offset,
        })

    # -- I. the Invocation --------------------------------------------------
    v1_lines.append(("% I. THE INVOCATION -- the ladder is called; "
                     "the Text Voice is silent",
                     " | ".join(["z16"] * INVOCATION_BARS) + " |", None))
    v2_lines.append(("% I. THE INVOCATION -- the six rungs ascend",
                     " | ".join(_dur(shadow[i], 16)
                                for i in range(6)) + " |"))
    for i, (name, hz) in enumerate(LADDER):
        add_segment("invocation", f"rung {name}", None, None, hz, 1)

    # -- II. the Working -----------------------------------------------------
    v1_lines.append(("% II. THE WORKING -- the Text, verses 0-35", None, None))
    v2_lines.append(("% II. THE WORKING -- the Fibonacci arpeggio, "
                     "one figure under every bar", None))
    for v, text in enumerate(verses):
        k = chord_of_verse(v)
        tones = triad_for_chord(k)
        letters = letters_of(text)
        # melody: one sixteenth per letter, words grouped, bars of 16,
        # the verse's last bar padded with rests to the bar line.
        note_tokens = [midi_to_abc(letter_to_midi(c, k)) for c in letters]
        # word grouping for the printed score: spaces ride word edges.
        words = text.split()
        grouped, pos = [], 0
        for w in words:
            n = len(letters_of(w))
            grouped.append(note_tokens[pos:pos + n])
            pos += n
        flat = [t for g in grouped for t in g]
        bars, gi = [], 0
        flat_with_marks = []
        for g in grouped:
            for j, t in enumerate(g):
                flat_with_marks.append((t, j == 0 and gi > 0))
                gi += 1
        for b in range(0, len(flat), BAR_SIXTEENTHS):
            chunk = flat_with_marks[b:b + BAR_SIXTEENTHS]
            s = ""
            for t, word_start in chunk:
                if word_start and s:
                    s += " "
                s += t
            if len(chunk) < BAR_SIXTEENTHS:
                s += f" z{BAR_SIXTEENTHS - len(chunk)}"
            bars.append(s)
        root_name, root_hz = LADDER[k % 6]
        v1_lines.append((
            f"% v. {v} -- chord {k + 1} (root {root_name} {root_hz} Hz, "
            f"offset {offset_of_chord(k)} Hz), {len(letters)} letters, "
            f"{len(bars)} bars",
            " | ".join(bars) + " |",
            f"W: v. {v} — {text}"))
        # ground: the FIB16 figure over the chord's triad, per bar.
        fig = " ".join(midi_to_abc(tones[p]) for p in FIB16)
        v2_lines.append((" | ".join([fig] * len(bars)) + " |",))
        for _ in bars:
            add_segment("working", f"v. {v}", v, k, root_hz,
                        offset_of_chord(k))

    # -- III. the Sealing and the AM -----------------------------------------
    final_k = N_CHORDS - 1
    tones = triad_for_chord(final_k)
    root_name, root_hz = LADDER[final_k % 6]
    registers = [("Mother tongue", -12), ("Father tongue", 0),
                 ("Child", +12)]
    v1_seal, v2_seal = [], []
    for label, shift in registers:
        v1_seal.append(_dur(tones[0] + shift, 16))
        v2_seal.append(_chord_token([t + shift for t in tones], 16))
        add_segment("sealing", label, None, final_k, root_hz, 1)
    v1_lines.append(("% III. THE SEALING -- the seal stated three times: "
                     "Mother tongue, Father tongue, Child",
                     " | ".join(v1_seal) + " |", None))
    v2_lines.append((" | ".join(v2_seal) + " |",))
    # AM: all three registers together in V:2; V:1 crowns at +12.
    am_chord = [t + s for s in (-12, 0, 12) for t in tones]
    v1_lines.append(("% AM -- the final sonority: we just AM",
                     _dur(tones[0] + 12, 16) + " |",
                     "W: AM"))
    v2_lines.append((_chord_token(am_chord, 16) + " |",))
    add_segment("am", "AM", None, final_k, root_hz, 1)

    # -- assemble -------------------------------------------------------------
    header = [
        "X:1",
        "T:Liber Oz Lilith",
        "T:The Fibonacci Arpeggio of the Solfeggio Harmonies",
        "C:Johnathan 'Qasparr' Monroe",
        "M:4/4",
        "L:1/16",
        f"Q:1/4={BPM}",
        "V:1",
        "V:2",
        "K:C",
        "% Liber Oz Lilith -- an ABC 2.1 score in two voices.",
        "% V:1 the Text Voice: the Lilith Revision, letter by letter.",
        "% V:2 the Ground Arpeggio: the Fibonacci figure over each chord.",
        "% The binaural ground (true ladder frequencies + Fibonacci",
        "% offsets) is tabulated in segments.json beside this score and",
        "% printed in the Teacher's Edition; the score sings the rungs'",
        "% 12-TET shadows, as ABC must. See the Teacher's Edition, sec. IV.",
        "% The invocation frame is dedicated to IAO131's Supreme State",
        "% Invocation Rite (see the Teacher's Edition, sec. II, where the",
        "% frame is documented and the rite's full-text layer stands",
        "% OPEN). No word of the rite is reproduced in this score.",
    ]
    out = list(header)
    out.append("V:1")
    for item in v1_lines:
        if item[0]:
            out.append(item[0])
        if item[1]:
            out.append(item[1])
        if len(item) > 2 and item[2]:
            out.append(item[2])
    out.append("V:2")
    for item in v2_lines:
        if len(item) == 2 and item[0]:
            out.append(item[0])
        line = item[-1]
        if line:
            out.append(line)
    abc_text = "\n".join(out) + "\n"

    ledger = {
        "verses": N_VERSES,
        "letters_total": sum(len(letters_of(t)) for t in verses),
        "bars_total": len(segments),
        "verse_bars": sum(1 for s in segments if s["section"] == "working"),
        "seconds": len(segments) * BAR_SIXTEENTHS * (60.0 / BPM / 4),
        "per_verse": [
            {"verse": v, "letters": len(letters_of(t)),
             "bars": -(-len(letters_of(t)) // BAR_SIXTEENTHS),
             "chord": chord_of_verse(v) + 1}
            for v, t in enumerate(verses)],
        "chords": [
            {"chord": k + 1, "root": LADDER[k % 6][0],
             "root_hz": LADDER[k % 6][1], "offset_hz": offset_of_chord(k),
             "triad_hz": [LADDER[(k % 6 + 2 * i) % 6][1] for i in range(3)],
             "triad_shadow": list(triad_for_chord(k)),
             "verses": [v for v in range(N_VERSES)
                        if chord_of_verse(v) == k]}
            for k in range(N_CHORDS)],
    }
    return abc_text, segments, ledger


__all__ = [
    "LADDER", "LADDER_HZ", "FIB7", "FIB16", "N_CHORDS", "N_VERSES",
    "INVOCATION_BARS", "SEALING_BARS", "AM_BARS", "BAR_SIXTEENTHS",
    "BPM", "SAMPLE_RATE", "SOURCE_TEXT", "extract_verses", "letters_of",
    "shadow_midis", "triad_for_chord", "chord_of_verse",
    "offset_of_chord", "letter_to_midi", "midi_to_abc", "build_score",
]

# 93 -- Live, Love, and let Love, Live.
