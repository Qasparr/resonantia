# 93
# ---------------------------------------------------------------------
# crystal_import.py -- the 5D Memory Crystal pattern importer: a
# foreign instrument's saved patterns, read honestly, re-grounded
# from its 440 field into the house's 432, and seated on house
# instruments so the studio can strike them.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR, All Rights Reserved, Without Prejudice.
# Written XXV day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# SOURCE -- AND ITS CREDIT: the pattern format below was read out of
# the source of a single-page Web Audio instrument found by the
# founder in the wild (2026-11-25) and ordered imported:
#   Source: https://sortiarius.neocities.org/5D_Memory_Crystal_Evolution_05
#   (author unknown; the link stands as the credit, founder's ruling
#   2026-11-25 -- where a used thing's author cannot be known, the
#   source link it was got from is its credit.)
# The page's own face prints its honesty line, which this module
# honours by repeating: its audio is "original generative music and
# sound design, not a recording or decoding of extraterrestrial
# signals." What is imported here is a PATTERN FILE -- tempo, scale,
# mood, and step positions, the page's own save format -- never the
# page's code, never its oscillators. The page's generative choices
# remain its author's; what the house strikes from an imported
# pattern is the house's rendering.
#
# THE FORMAT, AS EXTRACTED FROM THE SOURCE (never guessed):
#   Save object ($('save').onclick), JSON.stringify(data, null, 2),
#   downloaded as memory-crystal-pattern.json:
#     {title: '5D Memory Crystal pattern', tempo: <number>,
#      scale: <string>, mood: <string>, tracks: [<track> x4]}
#   Track object (makeTracks()):
#     {name, base, wave, level, pattern, oct}
#     names  = ['SUB HORIZON', 'GLASS ORBIT', 'PHANTOM CHOIR',
#               'SIGNAL DUST']
#     bases  = [55, 110, 220, 440]        (A1 A2 A3 A4, at A4 = 440)
#     waves  = ['sine', 'triangle', 'sine', 'sawtooth']
#     levels = [.34, .16, .12, .055]      (per-track, slider 0..60%)
#     octs   = [0, 1, 2, 3]               (register select, -1..+3)
#     pattern = 16 entries, each strictly 0 or 1 -- the step button
#               toggles with pattern[j] ^= 1. 1 strikes, 0 is
#               silent. There is NO per-step level in the source;
#               the "-1" sometimes mistaken for one is the lowest
#               option of the Octave / register select.
#   Scales (semitone offsets from the root A):
#     minor [0,2,3,5,7,9,10] . pent [0,3,5,7,10] .
#     whole [0,2,4,6,8,10] . phryg [0,1,3,5,7,8,10]
#   Moods (strings only, in the file): deep, ritual, signal, ice.
#   Tempo: the page's slider runs 40..140 BPM, standing at 72.
#   Timing: the sequencer's tick is ms = 60000/tempo/4 -- a step is
#     a SIXTEENTH note; 16 steps make one 4/4 bar. At 72 BPM a step
#     lasts 0.208 s and a beat 0.833 s. (The commissioning brief
#     called 0.833 s "a step"; the source says otherwise, and this
#     module follows the source. The seam is printed, not smoothed:
#     it decides the articulation gate below.)
#   The page's pitch walk (note(t, idx), idx = step + track index):
#     n = sc[(2*idx + floor(idx/3)) % len(sc)]
#         + (0 if idx % 3 == 0 else 12 * floor(idx/7))
#     f = base * 2**((n - 12) / 12) * 2**oct
#   The page's own note rings ~1.4 s (0.06 s attack, exponential
#   decay) whatever the step length; the import keeps the grid's
#   truth -- duration from tempo -- and lets the seats ring.
#
# THE RE-GROUNDING: the page is tuned to A4 = 440; the HOUSE field
# is 432. The conversion keeps the page's degree walk and its note
# identities exactly, and re-grounds the frequencies: every base is
# an A, so the house bases are the same As at 432 --
#   theirs  55 / 110 / 220 / 440   (A4 = 440)
#   ours    54 / 108 / 216 / 432   (A4 = 432)
# each exactly base * 432/440. regrounding_report() prints this per
# track; every converted event carries both frequencies.
#
# THE SEATS (role mapping, with reasoning):
#   SUB HORIZON   -> the house 808 seat (resonance.studio.
#     eightoeight.kick, pitched to the event's house frequency).
#     Reasoning: the page's sub is a sine at A1 walking the scale's
#     floor -- a pitched bass voice, and the 808 is the house's
#     pitched bass body, sworn at 48 kHz.
#   GLASS ORBIT   -> SSO Glockenspiel, program 39. Reasoning: the
#     page's voice is a bright triangle at A2 named for glass; the
#     glockenspiel is the bank's glass -- fast attack, long ring,
#     no articulation-floor problem at step length. (Violin
#     pizzicato was the other candidate; glass names the choice.)
#   PHANTOM CHOIR -> the pad seat, GATED. The pad's full dress is
#     SSO 1st Violins Sustain (program 2) over the Salamander
#     Grand; but the fix lab measured the violins' articulation
#     floor at 0.842 s (attack-to-90% + one step; RECEIPT-FIX.md in
#     the transcription lab), and no step in the page's whole tempo
#     range (0.107 s at 140 BPM .. 0.375 s at 40 BPM) reaches it --
#     the choir's steps FAIL the floor at every tempo the page
#     allows. So the import seats the choir on the Salamander
#     Grand alone (floor 0.130 s, passed by every step at 72 BPM
#     and above ~46 BPM), and the strings layer engages only where
#     a note is made to sustain at least the floor -- a rendering
#     decision a caller may take, never the pattern's own content.
#     The gate verdict rides on every choir event, printed.
#   SIGNAL DUST   -> SSO Xylophone, program 42, at low gain.
#     Reasoning: the page's dust is a faint sawtooth at A4, level
#     .055, the quietest voice; a short bright wooden strike at low
#     gain is its honest body. Program 42 IS the xylophone -- the
#     transcription lab's correctio established that at cost (its
#     first excerpt struck the violin line on it unknowing); here
#     it is used knowingly, for its own voice.
#
# MECHANISM: pure functions over plain data, stdlib only.
#   load_pattern(path)  -- read + validate; fails closed with
#     named errors (CrystalImportError) on any deviation from the
#     extracted format.
#   convert(pattern)    -- the page's degree walk, re-grounded:
#     one CrystalEvent per struck step, with both frequencies,
#     the MIDI number, the velocity (track level mapped linearly
#     over the slider's range: vel = level / 0.60 * 127), the
#     seat, and the gate verdict where a gate applies.
#   to_abc(events, pattern) -- one ABC tune per track through the
#     house's own writer (resonance.abc.writer), rests filling the
#     grid so the text re-parses to the same events.
#   to_midi(events, pattern, path) -- a dependency-free Standard
#     MIDI File (format 1, 480 ticks per beat): one track per
#     voice, program per seat. The 808 has no General MIDI body;
#     its track carries program 38 (Synth Bass 1) as a NAMED
#     placeholder -- the house strike renders the true 808 from
#     the events, not from this file.
#
# DOCTRINE: an importer is sworn the way an instrument is sworn --
# the format is read from the source, not guessed; the validation
# fails closed; the re-grounding is printed, not silent; the gate
# is measured, not assumed. The founder's ear gates any caliber
# claim for anything struck from an imported pattern; this module
# claims the mechanism only.
#
# 93 -- Live, Love, and let Love, Live.
# ---------------------------------------------------------------------
from __future__ import annotations

import json
import struct
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from resonance.abc.parser import Event as ABCEvent
from resonance.abc.parser import Tune
from resonance.abc.writer import write_abc

# ---------------------------------------------------------------------
# The extracted constants -- the page's own, cited to its source.
# ---------------------------------------------------------------------

SOURCE_URL = ("https://sortiarius.neocities.org/"
              "5D_Memory_Crystal_Evolution_05")
PATTERN_TITLE = "5D Memory Crystal pattern"

TRACK_NAMES = ["SUB HORIZON", "GLASS ORBIT", "PHANTOM CHOIR",
               "SIGNAL DUST"]
BASE_FREQS_440 = [55, 110, 220, 440]          # A1 A2 A3 A4 at 440
# The same As at the house field: base * 432/440, exact for As.
BASE_FREQS_432 = [54, 108, 216, 432]
BASE_MIDIS = [33, 45, 57, 69]                 # A1 A2 A3 A4
WAVES = ["sine", "triangle", "sine", "sawtooth"]
DEFAULT_LEVELS = [0.34, 0.16, 0.12, 0.055]
DEFAULT_OCTS = [0, 1, 2, 3]
LEVEL_MAX = 0.60                              # the slider's 60%

SCALES = {
    "minor": [0, 2, 3, 5, 7, 9, 10],
    "pent": [0, 3, 5, 7, 10],
    "whole": [0, 2, 4, 6, 8, 10],
    "phryg": [0, 1, 3, 5, 7, 8, 10],
}
MOODS = ["deep", "ritual", "signal", "ice"]
TEMPO_MIN, TEMPO_MAX = 40, 140
STEPS_PER_BAR = 16

# The page's factory patterns (makeTracks()), verbatim.
DEFAULT_PATTERNS = [
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],   # SUB HORIZON
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],   # GLASS ORBIT
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],   # PHANTOM CHOIR
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],   # SIGNAL DUST
]

# The page standing as it is first opened: tempo 72, scale minor
# (the select's first option), mood deep (likewise), factory tracks.
DEFAULT_PATTERN = {
    "title": PATTERN_TITLE,
    "tempo": 72,
    "scale": "minor",
    "mood": "deep",
    "tracks": [
        {"name": TRACK_NAMES[i], "base": BASE_FREQS_440[i],
         "wave": WAVES[i], "level": DEFAULT_LEVELS[i],
         "pattern": list(DEFAULT_PATTERNS[i]), "oct": DEFAULT_OCTS[i]}
        for i in range(4)
    ],
}

# ---------------------------------------------------------------------
# The seats. Programs are SSO bank numbers per the verified bank map
# in the samples CREDITS / the remedy lab's inventory; the 808 seat
# is the house synth (eightoeight), program None.
# ---------------------------------------------------------------------

SEATS = {
    "SUB HORIZON": {
        "role": "sub",
        "seat": "house_808",
        "program": None,
        "midi_placeholder_program": 38,   # Synth Bass 1, named stand-in
        "reason": "a pitched sine bass at A1 -- the house 808 is the "
                  "house's pitched bass body",
    },
    "GLASS ORBIT": {
        "role": "glass",
        "seat": "sso_glockenspiel",
        "program": 39,
        "reason": "a bright triangle named for glass -- the "
                  "glockenspiel is the bank's glass: fast attack, "
                  "long ring",
    },
    "PHANTOM CHOIR": {
        "role": "choir",
        "seat": "pad",
        "program": 0,                     # Salamander Grand, seated
        "layer_program": 2,               # SSO 1st Violins Sustain
        "reason": "a slow sine pad -- seated on the Salamander "
                  "under the articulation gate; the violins layer "
                  "engages only at or above its measured floor",
    },
    "SIGNAL DUST": {
        "role": "dust",
        "seat": "sso_xylophone",
        "program": 42,
        "reason": "a faint high sawtooth, the quietest voice -- a "
                  "short bright wooden strike at low gain; program "
                  "42 IS the xylophone (the remedy lab's correctio), "
                  "used knowingly",
    },
}

# Articulation floors measured by the transcription lab's fix pass
# (fix1_attacks.py; RECEIPT-FIX.md): attack-to-90% + one step.
FLOOR_VIOLINS_SUSTAIN_S = 0.842
FLOOR_SALAMANDER_S = 0.130

HOUSE_A4 = 432.0
PAGE_A4 = 440.0


class CrystalImportError(ValueError):
    """Raised, with a named cause, on any deviation from the format
    the source actually writes. The importer fails closed."""


# ---------------------------------------------------------------------
# Validation -- every check names what it refuses and why.
# ---------------------------------------------------------------------

def validate_pattern(data):
    """Validate a decoded pattern object against the extracted
    format; return it unchanged if it stands. Fail closed."""
    if not isinstance(data, dict):
        raise CrystalImportError(
            f"pattern must be a JSON object, got {type(data).__name__}")
    for key in ("tempo", "scale", "mood", "tracks"):
        if key not in data:
            raise CrystalImportError(f"missing required key: {key!r}")
    if "title" in data and not isinstance(data["title"], str):
        raise CrystalImportError("title must be a string when present")

    tempo = data["tempo"]
    if isinstance(tempo, bool) or not isinstance(tempo, (int, float)):
        raise CrystalImportError(f"tempo must be a number, got {tempo!r}")
    if not (TEMPO_MIN <= tempo <= TEMPO_MAX):
        raise CrystalImportError(
            f"tempo {tempo} outside the page's slider range "
            f"{TEMPO_MIN}..{TEMPO_MAX}")

    if data["scale"] not in SCALES:
        raise CrystalImportError(
            f"unknown scale {data['scale']!r}; the page writes one of "
            f"{sorted(SCALES)}")
    if data["mood"] not in MOODS:
        raise CrystalImportError(
            f"unknown mood {data['mood']!r}; the page writes one of "
            f"{MOODS}")

    tracks = data["tracks"]
    if not isinstance(tracks, list) or len(tracks) != 4:
        raise CrystalImportError(
            f"tracks must be a list of exactly 4, got "
            f"{len(tracks) if isinstance(tracks, list) else type(tracks).__name__}")
    for i, t in enumerate(tracks):
        if not isinstance(t, dict):
            raise CrystalImportError(f"track {i} must be an object")
        for key in ("name", "base", "wave", "level", "pattern", "oct"):
            if key not in t:
                raise CrystalImportError(
                    f"track {i} missing required key: {key!r}")
        # Name, base and wave are constants of the instrument -- the
        # page's UI offers no way to change them, so a file that
        # differs was not written by the page.
        if t["name"] != TRACK_NAMES[i]:
            raise CrystalImportError(
                f"track {i} name {t['name']!r} is not the instrument's "
                f"{TRACK_NAMES[i]!r}")
        if t["base"] != BASE_FREQS_440[i]:
            raise CrystalImportError(
                f"track {i} base {t['base']!r} is not the instrument's "
                f"{BASE_FREQS_440[i]}")
        if t["wave"] != WAVES[i]:
            raise CrystalImportError(
                f"track {i} wave {t['wave']!r} is not the instrument's "
                f"{WAVES[i]!r}")
        level = t["level"]
        if isinstance(level, bool) or not isinstance(level, (int, float)) \
                or not (0.0 <= level <= LEVEL_MAX):
            raise CrystalImportError(
                f"track {i} level {level!r} outside the slider's "
                f"0..{LEVEL_MAX}")
        if t["oct"] not in (-1, 0, 1, 2, 3):
            raise CrystalImportError(
                f"track {i} oct {t['oct']!r} outside the register "
                f"select's -1..+3")
        pat = t["pattern"]
        if not isinstance(pat, list) or len(pat) != STEPS_PER_BAR:
            raise CrystalImportError(
                f"track {i} pattern must be {STEPS_PER_BAR} steps, got "
                f"{len(pat) if isinstance(pat, list) else type(pat).__name__}")
        for j, v in enumerate(pat):
            if v not in (0, 1):
                raise CrystalImportError(
                    f"track {i} step {j} is {v!r}; the page's steps "
                    f"are strictly 0 or 1")
    return data


def load_pattern(path):
    """Read a memory-crystal-pattern.json from disk and validate it.
    Returns the pattern dict; raises CrystalImportError, named."""
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as e:
        raise CrystalImportError(f"cannot read {p}: {e}") from e
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise CrystalImportError(f"{p} is not valid JSON: {e}") from e
    return validate_pattern(data)


# ---------------------------------------------------------------------
# The page's arithmetic, re-grounded.
# ---------------------------------------------------------------------

def step_seconds(tempo):
    """One step: the tick is 60000/tempo/4 ms -- a sixteenth note."""
    return 60.0 / tempo / 4.0


def degree_walk(scale_name, idx):
    """The page's pitch walk for step-index idx (= step + track no.).

    Returns (degree_index, semitone): the scale degree chosen and
    the total semitone offset n of the source's formula, octave
    lift included."""
    sc = SCALES[scale_name]
    k = (2 * idx + idx // 3) % len(sc)
    n = sc[k] + (0 if idx % 3 == 0 else 12 * (idx // 7))
    return k, n


def midi_for(track_index, semitone, oct_):
    """The note's MIDI number: base A of the track, the walk's
    semitone, the (n - 12) the source applies, the register."""
    return BASE_MIDIS[track_index] + (semitone - 12) + 12 * oct_


def freq_of_midi(midi, a4):
    """Equal-tempered frequency of a MIDI note at the given A4."""
    return a4 * 2.0 ** ((midi - 69) / 12.0)


def velocity_of_level(level):
    """Track level -> MIDI velocity: linear over the slider's
    range, so the page's own balance ratios survive the crossing."""
    return max(1, min(127, round(level / LEVEL_MAX * 127)))


@dataclass
class CrystalEvent:
    """One struck step, converted. Both fields' frequencies ride on
    it: freq_page_hz at A4 = 440 (theirs), freq_house_hz at
    A4 = 432 (ours). gate names the articulation verdict where a
    gate applies (the choir), else None."""
    track_index: int
    track_name: str
    role: str
    seat: str
    program: int | None
    step: int
    start_s: float
    dur_s: float
    midi: int
    degree_index: int
    semitone: int
    freq_page_hz: float
    freq_house_hz: float
    velocity: int
    level: float
    gate: str | None = None


def convert(pattern):
    """Convert a validated pattern to events: one per struck step,
    in track then step order. Duration is the step's own length --
    duration from tempo, the grid's truth."""
    validate_pattern(pattern)
    tempo = float(pattern["tempo"])
    dur = step_seconds(tempo)
    events = []
    for i, t in enumerate(pattern["tracks"]):
        seat = SEATS[t["name"]]
        for step, on in enumerate(t["pattern"]):
            if not on:
                continue
            k, n = degree_walk(pattern["scale"], step + i)
            midi = midi_for(i, n, t["oct"])
            gate = None
            program = seat["program"]
            seat_name = seat["seat"]
            if t["name"] == "PHANTOM CHOIR":
                # The articulation gate, measured not assumed: the
                # step against the two pad bodies' floors.
                if dur >= FLOOR_VIOLINS_SUSTAIN_S:
                    seat_name = "pad_violins_sustain+salamander"
                    program = seat["layer_program"]
                    gate = (f"step {dur:.3f}s >= violins sustain "
                            f"floor {FLOOR_VIOLINS_SUSTAIN_S}s: "
                            f"strings seated")
                elif dur >= FLOOR_SALAMANDER_S:
                    gate = (f"step {dur:.3f}s < violins sustain "
                            f"floor {FLOOR_VIOLINS_SUSTAIN_S}s, >= "
                            f"Salamander floor {FLOOR_SALAMANDER_S}s: "
                            f"Salamander seated, strings held")
                else:
                    gate = (f"step {dur:.3f}s < Salamander floor "
                            f"{FLOOR_SALAMANDER_S}s: Salamander "
                            f"seated as the fastest pad body the "
                            f"house holds, floor unmet and printed")
            events.append(CrystalEvent(
                track_index=i, track_name=t["name"],
                role=seat["role"], seat=seat_name, program=program,
                step=step, start_s=step * dur, dur_s=dur, midi=midi,
                degree_index=k, semitone=n,
                freq_page_hz=freq_of_midi(midi, PAGE_A4),
                freq_house_hz=freq_of_midi(midi, HOUSE_A4),
                velocity=velocity_of_level(t["level"]),
                level=t["level"], gate=gate))
    return events


def regrounding_report(pattern):
    """The re-grounding, printed per track: their base at 440
    against ours at 432. The conversion's tuning act, on its face."""
    validate_pattern(pattern)
    lines = [
        "RE-GROUNDING -- the page is tuned A4 = 440; the house "
        "field is A4 = 432.",
        "Every base is an A, so each house base is the same A at "
        "432 (base x 432/440, exact):",
    ]
    for i, t in enumerate(pattern["tracks"]):
        lines.append(
            f"  {t['name']:<14} base theirs {BASE_FREQS_440[i]:>3} Hz"
            f"  ->  ours {BASE_FREQS_432[i]:>3} Hz"
            f"   (track register oct {t['oct']:+d})")
    lines.append(
        "Note identities and the degree walk are the page's own, "
        "unchanged; only the tuning field moves.")
    return "\n".join(lines)


# ---------------------------------------------------------------------
# ABC -- one tune per track through the house writer. Rests fill
# the grid so the text re-parses to the same events it was written
# from (the writer places notes by token arithmetic; a gap left
# unwritten would not survive the round trip).
# ---------------------------------------------------------------------

def to_abc(events, pattern):
    """Serialize converted events as ABC: four tunes (X:1..4), one
    per track, 4/4, L:1/8, at the pattern's tempo. Each tune covers
    exactly one bar -- the pattern's own span -- with rests filling
    the silent steps."""
    validate_pattern(pattern)
    tempo = pattern["tempo"]
    step_beats = Fraction(1, 4)               # a sixteenth, in beats
    blocks = []
    for i, t in enumerate(pattern["tracks"]):
        evs = []
        cursor = 0
        for ev in sorted((e for e in events if e.track_index == i),
                         key=lambda e: e.step):
            start = ev.step * step_beats
            if start > cursor * step_beats:
                evs.append(ABCEvent("rest", None,
                                    Fraction(cursor) * step_beats,
                                    start - Fraction(cursor)
                                    * step_beats))
            evs.append(ABCEvent("note", ev.midi, start, step_beats))
            cursor = ev.step + 1
        if cursor < STEPS_PER_BAR:
            evs.append(ABCEvent("rest", None,
                                Fraction(cursor) * step_beats,
                                Fraction(STEPS_PER_BAR - cursor)
                                * step_beats))
        tune = Tune(
            headers={
                "X": str(i + 1),
                "T": f"5D Memory Crystal -- {t['name']}",
                "M": "4/4",
                "L": "1/8",
                "Q": f"1/4={tempo}",
                "K": "Am",
            },
            events=evs,
            beats_per_bar=Fraction(4, 1),
            default_len=Fraction(1, 2),
            bpm=float(tempo),
        )
        blocks.append(write_abc(tune))
    return "".join(blocks)


# ---------------------------------------------------------------------
# MIDI -- a dependency-free Standard MIDI File writer. Format 1,
# 480 ticks per beat; a step is 120 ticks. One track per voice,
# program per seat; the sub's track carries GM program 38 (Synth
# Bass 1) as a named placeholder for the house 808, which no GM
# program is. The house strike renders the true 808 from events.
# ---------------------------------------------------------------------

TICKS_PER_BEAT = 480
TICKS_PER_STEP = TICKS_PER_BEAT // 4


def _vlq(n):
    """MIDI variable-length quantity."""
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append(0x80 | (n & 0x7F))
        n >>= 7
    return bytes(reversed(out))


def _midi_track(events_bytes_events):
    """Assemble one MTrk chunk from (tick, bytes) pairs."""
    body = bytearray()
    last = 0
    for tick, data in sorted(events_bytes_events):
        body += _vlq(tick - last)
        body += data
        last = tick
    body += _vlq(0) + b"\xff\x2f\x00"          # end of track
    return b"MTrk" + struct.pack(">I", len(body)) + bytes(body)


def to_midi(events, pattern, path):
    """Write the converted events as a Standard MIDI File at path.
    Returns the path. Four bars' worth of pattern is NOT implied:
    the file holds the pattern's own single bar, as the ABC does;
    a strike loops it explicitly, in the open."""
    validate_pattern(pattern)
    tempo_us = int(round(60_000_000 / float(pattern["tempo"])))
    meta = _midi_track([(0, b"\xff\x51\x03" + tempo_us.to_bytes(3, "big"))])
    chunks = [meta]
    for i, t in enumerate(pattern["tracks"]):
        seat = SEATS[t["name"]]
        program = seat["program"]
        if program is None:
            program = seat["midi_placeholder_program"]
        evs = [(0, bytes([0xC0 | i, program]))]
        for ev in (e for e in events if e.track_index == i):
            on_tick = ev.step * TICKS_PER_STEP
            off_tick = on_tick + TICKS_PER_STEP
            evs.append((on_tick, bytes([0x90 | i, ev.midi, ev.velocity])))
            evs.append((off_tick, bytes([0x80 | i, ev.midi, 0])))
        chunks.append(_midi_track(evs))
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks),
                                    TICKS_PER_BEAT)
    p = Path(path)
    p.write_bytes(header + b"".join(chunks))
    return p


__all__ = [
    "SOURCE_URL", "PATTERN_TITLE", "TRACK_NAMES", "BASE_FREQS_440",
    "BASE_FREQS_432", "BASE_MIDIS", "WAVES", "DEFAULT_LEVELS",
    "DEFAULT_OCTS", "LEVEL_MAX", "SCALES", "MOODS", "TEMPO_MIN",
    "TEMPO_MAX", "STEPS_PER_BAR", "DEFAULT_PATTERNS",
    "DEFAULT_PATTERN", "SEATS", "FLOOR_VIOLINS_SUSTAIN_S",
    "FLOOR_SALAMANDER_S", "HOUSE_A4", "PAGE_A4",
    "CrystalImportError", "CrystalEvent", "validate_pattern",
    "load_pattern", "step_seconds", "degree_walk", "midi_for",
    "freq_of_midi", "velocity_of_level", "convert",
    "regrounding_report", "to_abc", "to_midi",
]
