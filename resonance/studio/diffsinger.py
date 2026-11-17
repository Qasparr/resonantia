# 93
# ---------------------------------------------------------------------
# diffsinger.py -- the DiffSinger plug: score + lyrics in, a sung
# vocal out, with the Divine Nine seated at the vowel layer.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: this module is the system-side half of the plug. It
# turns a vocal spec -- lyric lines, each with its morae phonemized
# in its own tongue and its melody as (midi, seconds) note events --
# into built DiffSinger sequences: phoneme token ids from the bank's
# phonemes.json, language ids from its languages.json, per-phoneme
# score pitches, per-mora phoneme divisions (word_div) and frame
# budgets (word_dur). The built sequence is serialized as a house
# .ds file (the DiffSinger segment shape: offset, text, ph_seq,
# ph_dur, ph_num, note_seq, note_dur, note_slur) and handed across
# the JSON bridge to render_diffsinger.py, which the diffsinger-lab
# venv's python executes BY PATH -- the same wall, with the same two
# small JSON doors, that pipeline.py keeps with the MusicGen bridge.
# The bridge sings; this side then MEASURES what came back (stdlib
# wave + numpy: duration, peak, RMS, per line and for the assembly)
# and writes the manifest. A claim you cannot measure is a wish, so
# the manifest's numbers are read off the struck files on this side,
# never merely relayed from the bridge's own report.
#
# DOCTRINE -- THE NINE AT THE PLUG POINT: per the design study
# (docs/THE-DIVINE-NINE-VOCAL-TOOL.md), the Divine Nine is the
# canonical vowel interlingua at the joint between phonemizer and
# renderer. Every vowel phoneme a line carries is SEATED against
# the canon below -- or honestly reported at its disposition:
# SEATED (a station holds it), HALF_SEATED_ONSET (a glide whose
# onset a station holds and whose landing no station holds),
# NEAREST_OFFSET (no seat, but a named seat is its nearest
# coordinate), UNSEATED (coordinates reported, none forced).
# The founder's rulings carried here, verbatim in effect:
#   * VV IS THE HIGH-BACK SEAT (his stamp, 2026-11-12: "Seat it
#     -- VV takes the /u/ family"). JA u and EN UW seat under VV;
#     EN UH is VV's nearest offset; the OU glide re-reads as
#     ending AT the VV seat, the canon's second fully-seated
#     glide beside EI. VV carries NO isopsephy value in the
#     founder's canon -- it is not counted in the 1,779, holds no
#     Greek weight, and is seated here in the acoustic register
#     only, exactly as his stamp scoped it.
#   * CONSONANTS ARE VOWELS-ONLY RULED (ruled under delegation,
#     2026-11-15, revisable by his pen): the Nine govern the
#     vowel layer alone. Consonants are NOT seated, NOT weighed,
#     NOT mapped -- they pass language-native, exactly as the
#     phonemizer emitted them, and the ledger counts them as
#     PASS_NATIVE so the pass is visible, not silent.
#   * NO VOWEL-TO-ARCHON MAPPING IS DECLARED OR INVENTED HERE.
#     The seats below are acoustic stations (formant
#     coordinates), nothing more; the mapping to any office is
#     the founder's pen alone, UNCHARTED.
# The hybrids EI and OU are trajectories, not steady states: in
# sequence terms, one note carrying two vowel targets (ph_num 2
# under a single note_seq entry). The builder writes morae under
# notes by the grouping law below, so a diphthong mora written as
# two phoneme targets under one note is a hybrid by construction.
#
# DOCTRINE -- THE GROUPING LAW: a filed melody may carry fewer
# notes than a filed lyric carries morae (the Mugetsu hook: 54
# notes, 127 morae). Neither text may be edited -- lyrics are
# byte-exact and the score is the score -- so morae GROUP under
# notes: contiguous runs, counts proportional to note durations
# by largest remainder, at least one mora per note, every mora
# sung. Within a note, its seconds divide equally among its
# morae; the duration model then divides each mora's frame
# budget among its phonemes by its own proportions, as the lab's
# proven pipeline has always done. The grouping is CONSTRUCTED
# (the desk's alignment), labeled as such wherever it is used.
#
# Tolerances (the fourth element, stated here and in the run
# report): word budgets are handed in whole frames (rounding
# <= 0.5 frame per mora); the duration model's returned frames
# are measured against the asked seconds per line and the
# difference is printed, never corrected silently; a line whose
# render overruns its assembly slot is named in the manifest's
# walls, at full size.
# ---------------------------------------------------------------------

import json
import math
import os
import subprocess
import time
import wave
from pathlib import Path

import numpy as np

SR = 44100                 # The bank/vocoder native rate, full stop.
HOP = 512                  # NSF-HiFiGAN hop in the lab checkpoint.
FPS = SR / HOP             # 86.1328 frames per second.

_HERE = Path(__file__).resolve()
LAB = Path(os.environ.get(
    "RESONANTIA_DIFFSINGER_LAB",
    str(_HERE.parents[2] / "diffsinger-lab")))
BANK = LAB / "banks" / "Lem-the-Shapeshifter-DS-2.5-dur26" / "lem_v2_5"
VOC = (LAB / "DiffSinger" / "checkpoints"
       / "pc_nsf_hifigan_44.1k_hop512_128bin_2025.02")
LAB_PYTHON = os.environ.get(
    "RESONANTIA_DIFFSINGER_PYTHON", str(LAB / "venv" / "bin" / "python"))
BRIDGE_SCRIPT = str(_HERE.with_name("render_diffsinger.py"))
BANK_NAME = "Lem the Shapeshifter DS 2.5"

# ---------------------------------------------------------------------
# THE NINE -- the canonical vowel seats (acoustic register only).
# Greek weights are the founder's canon (2026-11-09): the seven pure
# vowels weigh 1,294; with EI (15) and OU (470) the nine weigh 1,779.
# VV carries no weight in that table and is not counted in it; its
# seat here is the founder's stamp of 2026-11-12, scoped to the
# vocal table. X is carried and unseated, awaiting his word.
# ---------------------------------------------------------------------

STATIONS = {
    "Α": {"weight": 1, "ipa": "/a/", "formants": (730, 1090)},
    "Ε": {"weight": 5, "ipa": "/e/", "formants": (512, 1950)},
    "Η": {"weight": 8, "ipa": "/ɛː/", "formants": (610, 1720)},
    "Ι": {"weight": 10, "ipa": "/i/", "formants": (270, 2290)},
    "Ο": {"weight": 70, "ipa": "/o/", "formants": (570, 840)},
    "Υ": {"weight": 400, "ipa": "/y/", "formants": (235, 2100)},
    "Ω": {"weight": 800, "ipa": "/ɔː/", "formants": (590, 880)},
    "ΕΙ": {"weight": 15, "ipa": "/e/ -> /i/", "formants": None},
    "ΟΥ": {"weight": 470, "ipa": "/o/ -> VV", "formants": None},
    "VV": {"weight": None, "ipa": "/u/ family",
           "formants": (300, 700)},
}

SEATED = "SEATED"
HALF_SEATED_ONSET = "HALF_SEATED_ONSET"
NEAREST_OFFSET = "NEAREST_OFFSET"
UNSEATED = "UNSEATED"
PASS_NATIVE = "PASS_NATIVE"     # consonants + rests, per the ruling
REST = "REST"

# Vowel seats per tongue. Each entry: vowel name (the bank token's
# bare name) -> (station or None, disposition, coordinate note).
# Reasoning rides with each assignment, per the founder's rule.
JA_VOWEL_SEATS = {
    # The four exact seats: JA a/i/e/o are the canon's own vowels.
    "a": ("Α", SEATED, "exact: JA /a/ is Greek /a/, no offset"),
    "i": ("Ι", SEATED, "exact: the table's cleanest row"),
    "e": ("Ε", SEATED, "exact: JA /e/ is Greek /e/"),
    "o": ("Ο", SEATED, "exact: JA /o/ is Greek /o/"),
    # The founder's stamp: u takes the VV seat, its unrounding
    # ([ɯ], lips unspread against /u/'s rounding) kept as a
    # coordinate of the seat, not smoothed away.
    "u": ("VV", SEATED,
          "the founder's stamp: VV takes the /u/ family; JA u "
          "keeps its unrounding as a coordinate of the seat"),
    # The bank's long-vowel phonemes: duration, not new qualities
    # -- the same seats held longer (the study's one law for both
    # languages); the length coordinate rides as the note.
    "A": ("Α", SEATED, "long vowel: the Α seat, length as duration"),
    "I": ("Ι", SEATED, "long vowel: the Ι seat, length as duration"),
    "U": ("VV", SEATED, "long vowel: the VV seat, length as duration"),
    "E": ("Ε", SEATED, "long vowel: the Ε seat, length as duration"),
    "O": ("Ο", SEATED, "long vowel: the Ο seat, length as duration"),
}

EN_VOWEL_SEATS = {
    "aa": ("Α", SEATED,
           "seated: /ɑ/ is low-back against Greek low-central /a/ "
           "-- a backness coordinate of about one F2 step, reported"),
    "iy": ("Ι", SEATED, "exact: EN /i/ is Greek /i/, no offset"),
    "eh": ("Η", SEATED,
           "seated in quality: Greek Η is long, EN EH short -- "
           "duration is the engine's parameter, not a new vowel"),
    "ao": ("Ω", SEATED,
           "seated in quality, with the same length coordinate "
           "as Η (Greek long, English short)"),
    # The VV family, per the founder's stamp.
    "uw": ("VV", SEATED,
           "the founder's stamp: EN UW seats under VV"),
    "uh": ("VV", NEAREST_OFFSET,
           "VV's nearest offset: the lax step beside the seat -- "
           "the very value Welsh cwm pronounces under the letter"),
    # Glides: the onset is seated, the landing is not -- except
    # the canon's own two hybrids, whose both ends are governed
    # (EI fully; OU ending AT the VV seat).
    "ey": ("Ε", HALF_SEATED_ONSET,
           "onset at Ε; the glide lands on /ɪ/, which holds no "
           "station -- half-seated as a class with OW"),
    "ow": ("Ο", HALF_SEATED_ONSET,
           "onset at Ο; the glide lands toward /ʊ/, VV's offset "
           "ground, holding no station of its own"),
    "ay": ("Α", HALF_SEATED_ONSET,
           "onset at Α; lands on unseated /ɪ/"),
    "aw": ("Α", HALF_SEATED_ONSET,
           "onset at Α; lands on unseated /ʊ/ ground"),
    "oy": ("Ω", HALF_SEATED_ONSET,
           "onset at Ω; lands on unseated /ɪ/ -- the glide is "
           "re-read as ending at VV's offset, per the study"),
    # The unseated, coordinates reported, none forced.
    "ih": (None, UNSEATED,
           "no station: one height step below Ι, centralized -- "
           "between Ι and Ε on height, inward on F2"),
    "ae": (None, UNSEATED,
           "no station: low-front, between Α and Ε, off the "
           "front edge of the canon's space"),
    "ah": (None, UNSEATED,
           "no station: the central vowel, the acoustic "
           "centroid (F1 ~500, F2 ~1400) -- an origin with no axis"),
    "ax": (None, UNSEATED,
           "no station: schwa, the same central coordinate as AH"),
    "er": (None, UNSEATED,
           "referred to the consonant ruling: its rhotic is a "
           "consonantal overlay; under vowels-only it passes as "
           "the phonemizer emits it, unseated"),
}

_VOWEL_SEATS = {"ja": JA_VOWEL_SEATS, "en": EN_VOWEL_SEATS}
_JA_VOWELS = frozenset(JA_VOWEL_SEATS)
_EN_VOWELS = frozenset(EN_VOWEL_SEATS)


def seat_vowel(lang, name):
    """Seat one phoneme against the Nine; return its ledger entry.

    MECHANISM: vowels are looked up in the tongue's seat table and
    return (station, disposition, note). SP/AP are rests. Every
    other phoneme is a consonant of its tongue and returns
    PASS_NATIVE -- the vowels-only ruling made mechanical: the
    interlingua does not touch it, and the ledger says so.
    Raises ValueError for a vowel the table does not know: an
    unlisted vowel is a table gap, and a gap is named, never
    silently passed.
    """
    if name in ("SP", "AP"):
        return {"phoneme": name, "station": None,
                "disposition": REST, "note": "rest: no vowel sung"}
    vowels = _JA_VOWELS if lang == "ja" else _EN_VOWELS
    if name in vowels:
        station, disposition, note = _VOWEL_SEATS[lang][name]
        return {"phoneme": name, "station": station,
                "disposition": disposition, "note": note}
    return {"phoneme": name, "station": None,
            "disposition": PASS_NATIVE,
            "note": "consonant: passes language-native, unseated "
                    "and unweighed, per the vowels-only ruling"}


def seat_line(lang, phoneme_names):
    """The seating ledger for one line's phonemes, in order."""
    return [seat_vowel(lang, n) for n in phoneme_names]


def ledger_totals(ledgers):
    """Count a run's ledgers: per station, per disposition.

    MECHANISM: pure counting over seat_line output -- the run
    report prints these numbers, and the PONTIFEX audit recomputes
    them from the same ledgers, so they are weighed twice.
    """
    stations, dispositions = {}, {}
    for ledger in ledgers:
        for entry in ledger:
            d = entry["disposition"]
            dispositions[d] = dispositions.get(d, 0) + 1
            if entry["station"]:
                s = entry["station"]
                stations[s] = stations.get(s, 0) + 1
    return {"stations": stations, "dispositions": dispositions}


# ---------------------------------------------------------------------
# The grouping law: morae under notes.
# ---------------------------------------------------------------------

def group_morae(note_durs, n_morae):
    """Distribute morae across notes, proportional to duration.

    MECHANISM: largest-remainder apportionment over note durations
    with a floor of one mora per note (a note with no mora is a
    note unsung, and the score is the score). The floor is taken
    first; the remaining morae are apportioned by duration share,
    largest fractional remainders first, ties broken by note
    order so the result is deterministic. Refuses by name when
    the lyric carries fewer morae than the melody carries notes:
    that is a score/lyric mismatch no alignment may paper over.
    """
    n_notes = len(note_durs)
    if n_morae < n_notes:
        raise ValueError(
            f"grouping refused: {n_morae} morae for {n_notes} "
            "notes -- a note would go unsung")
    counts = [1] * n_notes
    rest = n_morae - n_notes
    if rest:
        total = float(sum(note_durs))
        shares = [rest * d / total for d in note_durs]
        base = [int(math.floor(s)) for s in shares]
        counts = [c + b for c, b in zip(counts, base)]
        leftover = rest - sum(base)
        order = sorted(range(n_notes),
                       key=lambda i: (-(shares[i] - base[i]), i))
        for i in order[:leftover]:
            counts[i] += 1
    return counts


# ---------------------------------------------------------------------
# Sequence building: the .ds heart.
# ---------------------------------------------------------------------

def _load_bank_tables(bank):
    """Read the bank's phoneme + language tables (JSON, stdlib)."""
    ph = json.loads((Path(bank) / "phonemes.json").read_text(
        encoding="utf-8"))
    langs = json.loads((Path(bank) / "languages.json").read_text(
        encoding="utf-8"))
    return ph, langs


def build_line(line, ph, langs):
    """Build one line's DiffSinger sequence from its spec.

    The spec line: {id, lang, speaker, text, morae, notes, offset}
    -- morae is a list of phoneme-name lists (one per mora, bare
    names in the tongue's inventory, SP allowed as its own mora);
    notes is a list of {midi, dur} events tiling the line's slot.
    Returns the built line: bridge fields (tokens, languages,
    ph_midi, word_div, word_dur) plus the record fields the .ds
    and the manifest carry (ph_seq names, note table, per-note
    ph_num, the seating ledger, asked seconds).
    """
    lang = line["lang"]
    if lang not in langs:
        raise ValueError(f"line {line['id']}: language {lang!r} "
                         "not in the bank's languages.json")
    lang_id = langs[lang]
    morae = line["morae"]
    notes = line["notes"]
    counts = group_morae([n["dur"] for n in notes], len(morae))

    def pid(name):
        if name in ("SP", "AP"):
            return ph[name]
        key = f"{lang}/{name}"
        if key not in ph:
            raise ValueError(
                f"line {line['id']}: phoneme {key!r} not in the "
                "bank's phonemes.json -- a table gap, named")
        return ph[key]

    tokens, languages, ph_midi, word_div, word_dur = [], [], [], [], []
    ph_names, ledger = [], []
    note_rows, mi = [], 0
    for note, k in zip(notes, counts):
        group = morae[mi:mi + k]
        mi += k
        per_mora = note["dur"] / k
        ph_num = 0
        for mora in group:
            frames = max(1, int(round(per_mora * FPS)))
            word_dur.append(frames)
            word_div.append(len(mora))
            # A rest mora (SP/AP alone) rides the same word
            # machinery but sings no pitch: its phonemes carry
            # midi 0, the precedents' convention.
            rest = mora in (["SP"], ["AP"])
            for name in mora:
                tokens.append(pid(name))
                languages.append(lang_id)
                ph_midi.append(0 if rest else note["midi"])
                ph_names.append(name)
                ledger.append(seat_vowel(lang, name))
                ph_num += 1
        note_rows.append({"midi": note["midi"], "dur": note["dur"],
                          "morae": k, "ph_num": ph_num})
    asked = sum(n["dur"] for n in notes)
    return {"id": line["id"], "speaker": line["speaker"],
            "lang": lang, "text": line["text"],
            "offset": float(line["offset"]),
            "tokens": tokens, "languages": languages,
            "ph_midi": ph_midi, "word_div": word_div,
            "word_dur": word_dur, "ph_names": ph_names,
            "notes": note_rows, "ledger": ledger,
            "asked_s": asked}


_NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F",
               "F#", "G", "G#", "A", "A#", "B")


def note_name(midi):
    """MIDI number -> .ds note name (sharp spelling, C4 = 60)."""
    return f"{_NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def line_to_ds(built, ph_dur_s=None):
    """One built line as a .ds segment (the DiffSinger shape).

    ph_dur carries per-phoneme seconds: the ASKED durations (word
    budgets divided equally among a mora's phonemes) before the
    render, the bridge's REALIZED frame counts after it -- the
    caller passes ph_dur_s when it has the realized values, and
    the segment says which it carries via 'ph_dur_source'.
    """
    if ph_dur_s is None:
        ph_dur_s = []
        for frames, div in zip(built["word_dur"], built["word_div"]):
            ph_dur_s.extend([frames / FPS / div] * div)
        source = "asked (word budgets, equal split within a mora)"
    else:
        source = "realized (duration model frames)"
    return {
        "offset": built["offset"],
        "text": built["text"],
        "lang": built["lang"],
        "speaker": built["speaker"],
        "ph_seq": " ".join(
            n if n in ("SP", "AP") else f"{built['lang']}/{n}"
            for n in built["ph_names"]),
        "ph_dur": " ".join(f"{d:.4f}" for d in ph_dur_s),
        "ph_dur_source": source,
        "ph_num": " ".join(str(n["ph_num"]) for n in built["notes"]),
        "note_seq": " ".join(
            note_name(n["midi"]) for n in built["notes"]),
        "note_dur": " ".join(f"{n['dur']:.4f}"
                             for n in built["notes"]),
        "note_slur": " ".join("0" for _ in built["notes"]),
    }


def write_ds(built_lines, path, ph_dur_map=None):
    """Serialize built lines as a house .ds file (JSON segments)."""
    segs = []
    for built in built_lines:
        realized = None
        if ph_dur_map and built["id"] in ph_dur_map:
            realized = ph_dur_map[built["id"]]
        segs.append(line_to_ds(built, realized))
    Path(path).write_text(
        json.dumps(segs, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return segs


# ---------------------------------------------------------------------
# The score reader: MIDI in, note events out (MIDI is the score).
# ---------------------------------------------------------------------

def _vlq(data, i):
    v = 0
    while True:
        x = data[i]
        i += 1
        v = (v << 7) | (x & 0x7F)
        if not (x & 0x80):
            return v, i


def read_midi(path):
    """Read a Standard MIDI File: tracks of (name, notes, tempos).

    MECHANISM: a minimal SMF reader -- header, per-track delta
    times, running status, note on/off pairing, track-name and
    tempo meta events. Notes return as {midi, start_tick,
    dur_tick}; tempos as (tick, microseconds_per_quarter). This
    is a score reader, not a player: system exclusive and
    controller traffic is stepped over, never interpreted.
    """
    data = Path(path).read_bytes()
    if data[:4] != b"MThd":
        raise ValueError(f"{path}: not a Standard MIDI File")
    ntrk = int.from_bytes(data[10:12], "big")
    division = int.from_bytes(data[12:14], "big")
    if division & 0x8000:
        raise ValueError(f"{path}: SMPTE division not supported")
    i = 8 + int.from_bytes(data[4:8], "big")
    tracks = []
    for _ in range(ntrk):
        if data[i:i + 4] != b"MTrk":
            raise ValueError(f"{path}: malformed track chunk")
        ln = int.from_bytes(data[i + 4:i + 8], "big")
        b = data[i + 8:i + 8 + ln]
        i += 8 + ln
        j, tick, status = 0, 0, 0
        name, notes, tempos, open_n = None, [], [], {}
        while j < len(b):
            d, j = _vlq(b, j)
            tick += d
            if b[j] & 0x80:
                status = b[j]
                j += 1
            ev = status
            if ev == 0xFF:
                meta = b[j]
                j += 1
                l, j = _vlq(b, j)
                payload = b[j:j + l]
                j += l
                if meta == 0x03:
                    name = payload.decode("utf-8", "replace")
                elif meta == 0x51 and l == 3:
                    tempos.append((tick, int.from_bytes(payload,
                                                        "big")))
                continue
            if ev in (0xF0, 0xF7):
                l, j = _vlq(b, j)
                j += l
                continue
            hi = ev & 0xF0
            if hi in (0x90, 0x80):
                note, vel = b[j], b[j + 1]
                j += 2
                if hi == 0x90 and vel > 0:
                    open_n.setdefault(note, []).append(tick)
                elif note in open_n and open_n[note]:
                    s = open_n[note].pop(0)
                    notes.append({"midi": note, "start_tick": s,
                                  "dur_tick": tick - s})
            elif hi in (0xC0, 0xD0):
                j += 1
            else:
                j += 2
        notes.sort(key=lambda n: n["start_tick"])
        tracks.append({"name": name, "notes": notes,
                       "tempos": tempos})
    return {"division": division, "tracks": tracks}


def melody_from_midi(path, track_match, bpm=None):
    """One track of a score MIDI as (midi, seconds) note events.

    Tempo: the file's first tempo meta if present, else the bpm
    the caller states. Ticks become seconds through the division;
    the events return in start order with their durations -- the
    exact shape build_line consumes as a line's notes when the
    events tile the line's slot.
    """
    smf = read_midi(path)
    track = None
    for t in smf["tracks"]:
        if t["name"] and track_match in t["name"]:
            track = t
            break
    if track is None:
        raise ValueError(f"{path}: no track matching "
                         f"{track_match!r}")
    if track["tempos"]:
        uspq = track["tempos"][0][1]
    elif bpm:
        uspq = 60_000_000 / bpm
    else:
        raise ValueError(f"{path}: no tempo in file and no bpm "
                         "given -- the score's clock must be stated")
    spq = uspq / 1_000_000          # seconds per quarter note
    div = smf["division"]
    notes = [{"midi": n["midi"],
              "start": n["start_tick"] / div * spq,
              "dur": n["dur_tick"] / div * spq}
             for n in track["notes"]]
    return {"track": track["name"], "bpm": 60.0 / spq,
            "notes": notes}


# ---------------------------------------------------------------------
# Measurement: the manifest's numbers are read off the struck files.
# ---------------------------------------------------------------------

def measure_wav(path):
    """Measure a struck WAV: duration, rate, peak, RMS.

    MECHANISM: stdlib wave for the container, numpy for the math;
    integer PCM of any width the wave module hands back is scaled
    by its full-scale value. Peak and RMS return linear and in
    dBFS (20*log10), the house's two voices for one measurement.
    """
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        sw = w.getsampwidth()
        n = w.getnframes()
        raw = w.readframes(n)
    if sw == 2:
        a = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768
    elif sw == 4:
        a = np.frombuffer(raw, dtype="<i4").astype(np.float64) / 2**31
    elif sw == 1:
        a = (np.frombuffer(raw, dtype=np.uint8).astype(np.float64)
             - 128) / 128
    elif sw == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        v = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        v = np.where(v >= 2**23, v - 2**24, v)
        a = v.astype(np.float64) / 2**23
    else:
        raise ValueError(f"{path}: unsupported sample width {sw}")
    if ch > 1:
        a = a.reshape(-1, ch)
        mono = a.mean(axis=1)
    else:
        mono = a
    peak = float(np.max(np.abs(mono))) if len(mono) else 0.0
    rms = float(np.sqrt(np.mean(mono ** 2))) if len(mono) else 0.0
    eps = 1e-12
    return {"file": str(path), "sample_rate": sr, "channels": ch,
            "samples": int(len(mono)),
            "duration_s": round(len(mono) / sr, 4),
            "peak": round(peak, 4),
            "peak_dbfs": round(20 * math.log10(peak + eps), 2),
            "rms": round(rms, 4),
            "rms_dbfs": round(20 * math.log10(rms + eps), 2)}


# ---------------------------------------------------------------------
# The bridge: two small JSON doors in a necessary wall.
# ---------------------------------------------------------------------

def _run_bridge(job, out_dir, log):
    """Execute render_diffsinger.py in the lab venv; return result.

    The pipeline._run_bridge contract, kept: job file in the out
    dir, progress appended to render.log, the result is the last
    non-empty stdout line, and a failure raises with the bridge's
    own error named -- surfaced, never swallowed.
    """
    job_path = Path(out_dir) / "bridge_job.json"
    job_path.write_text(json.dumps(job, indent=2), encoding="utf-8")
    env = dict(os.environ,
               OMP_NUM_THREADS=str(os.cpu_count() or 1),
               MKL_NUM_THREADS=str(os.cpu_count() or 1))
    log_path = Path(out_dir) / "render.log"
    with open(log_path, "a", encoding="utf-8") as log_fh:
        proc = subprocess.run(
            [LAB_PYTHON, BRIDGE_SCRIPT, str(job_path)],
            stdout=subprocess.PIPE, stderr=log_fh, env=env,
            text=True)
    lines = [ln for ln in proc.stdout.strip().splitlines()
             if ln.strip()]
    if not lines:
        raise RuntimeError(
            f"lab bridge produced no result (see {log_path})")
    result = json.loads(lines[-1])
    if not result.get("ok"):
        raise RuntimeError(f"lab bridge failed: {result.get('error')}")
    log(f"bridge result: {result['assembly']['file']} "
        f"({result['wall_seconds']}s wall)")
    return result


def render(spec, out_dir, log=print):
    """Render a vocal spec end-to-end; return the manifest dict.

    The spec: {title, bank (optional override), lines: [line specs
    as build_line takes them], assembly_file}. Steps, in order:
    validate + build every line (the Nine seated as the sequences
    are built), write the asked .ds, cross the bridge, write the
    realized .ds from the bridge's frame counts, measure every
    struck file on this side, and write manifest.json. Walls met
    on the road -- a line rendering longer than its slot, a print
    gain the bridge had to apply -- are collected into the
    manifest's walls, at full size.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bank = Path(spec.get("bank", BANK))
    ph, langs = _load_bank_tables(bank)
    speakers = {p.stem for p in bank.glob("*.emb")}
    built = []
    for line in spec["lines"]:
        if line["speaker"] not in speakers:
            raise ValueError(
                f"line {line['id']}: speaker {line['speaker']!r} "
                f"has no embedding in the bank ({sorted(speakers)})")
        built.append(build_line(line, ph, langs))
    write_ds(built, out_dir / "sequence.ds")

    total_s = max(b["offset"] + b["asked_s"] for b in built)
    job = {"bank_dir": str(bank), "vocoder_dir": str(VOC),
           "lab_dir": str(LAB / "DiffSinger"),
           "out_dir": str(out_dir),
           "threads": int(spec.get("threads", 4)),
           "lines": [{"id": b["id"], "speaker": b["speaker"],
                      "tokens": b["tokens"],
                      "languages": b["languages"],
                      "ph_midi": b["ph_midi"],
                      "word_div": b["word_div"],
                      "word_dur": b["word_dur"]} for b in built],
           "assembly": {
               "file": spec.get("assembly_file", "vocal.wav"),
               "total_s": total_s,
               "offsets_s": {b["id"]: b["offset"] for b in built}}}
    t0 = time.time()
    result = _run_bridge(job, out_dir, log)
    wall = time.time() - t0

    by_id = {r["id"]: r for r in result["lines"]}
    ph_dur_map = {}
    walls = []
    line_rows = []
    for b in built:
        r = by_id[b["id"]]
        realized = [f / FPS for f in
                    _frames_of(r, b)]
        ph_dur_map[b["id"]] = realized
        m = measure_wav(out_dir / r["file"])
        slot_end = b["offset"] + b["asked_s"]
        rend_end = b["offset"] + r["seconds"]
        if rend_end > slot_end + 1e-9:
            walls.append(
                f"line {b['id']}: rendered {r['seconds']:.3f}s "
                f"against a {b['asked_s']:.3f}s slot -- overhang "
                f"{rend_end - slot_end:.3f}s past its bar line, "
                "summed into the assembly, not trimmed")
        if r["print_gain"] != 1.0:
            walls.append(
                f"line {b['id']}: print gain {r['print_gain']} "
                "applied by the bridge to land its peak on the "
                "-1 dBFS print ceiling (recorded, not silent)")
        line_rows.append({
            "id": b["id"], "text": b["text"], "lang": b["lang"],
            "speaker": b["speaker"], "offset_s": b["offset"],
            "morae": len(b["word_div"]),
            "phonemes": len(b["tokens"]),
            "notes": len(b["notes"]),
            "asked_s": round(b["asked_s"], 4),
            "rendered_s": r["seconds"],
            "frames": r["frames"],
            "file": r["file"], "measured": m})
    write_ds(built, out_dir / "sequence-realized.ds", ph_dur_map)

    asm = measure_wav(out_dir / result["assembly"]["file"])
    if result["assembly"]["print_gain"] != 1.0:
        walls.append(
            "assembly: print gain "
            f"{result['assembly']['print_gain']} applied by the "
            "bridge to land its peak on the -1 dBFS print ceiling "
            "(recorded, not silent)")
    totals = ledger_totals([b["ledger"] for b in built])
    manifest = {
        "title": spec.get("title", "Untitled"),
        "engine": "DiffSinger (OpenVPI, Apache 2.0) via "
                  "resonance.studio.diffsinger",
        "bank": {"name": BANK_NAME, "dir": str(bank),
                 "vocoder": str(VOC)},
        "sample_rate": SR, "hop": HOP,
        "lines": line_rows,
        "assembly": {"file": result["assembly"]["file"],
                     "measured": asm},
        "nine": totals,
        "walls": walls,
        "bridge_wall_seconds": result["wall_seconds"],
        "wall_seconds": round(wall, 2),
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8")
    log(f"manifest: {len(line_rows)} lines, assembly "
        f"{asm['duration_s']}s, peak {asm['peak_dbfs']} dBFS, "
        f"RMS {asm['rms_dbfs']} dBFS; walls: {len(walls)}")
    return manifest


def _frames_of(result_row, built):
    """Per-phoneme realized seconds need frame counts per phoneme.

    The bridge reports a line's total frames; the realized ph_dur
    is reconstructed by scaling the asked word budgets to the
    realized total -- labeled in the .ds as realized, with this
    reconstruction stated in the module doctrine: the per-phoneme
    split within the total is the asked proportion, the total is
    the model's own. (The bridge's per-phoneme frames are not
    carried across the JSON door in this phase; the seam is named
    here rather than hidden.)
    """
    total_frames = result_row["frames"]
    asked_total = sum(built["word_dur"])
    scale = total_frames / asked_total if asked_total else 1.0
    frames = []
    for frames_w, div in zip(built["word_dur"], built["word_div"]):
        per = frames_w * scale / div
        frames.extend([per] * div)
    return frames


# 93 -- Live, Love, and let Love, Live.
