# 93
# ---------------------------------------------------------------------
# build_kagami_ketto.py -- KAGAMI KETTOU (the desk's title, pending
# the founder's pen): a KRS-One Method mirrored-duel stalemate
# battle in Japanese, struck in-house as HOUSE VERSION 1.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR, All Rights Reserved, Without Prejudice.
# Written XXIV day of November, Anno V:xii e.n. (2026 e.v.), under
# the Method of Science, Aim of Religion -- Scientific Illuminism.
#
# THE COMMISSION (founder's spec, 2026-11-24 15:21-15:22 EST):
# "follow the Sheets and Lyrics doctrine format for KRS-One Method
# for BARS in Japanese at 144 BPM with Violin, Grand Piano and
# Super 808 Bass with Sigma Gmega bed and 1776=93 as a solfeggio
# arpeggio capriccio mirrored duel stalemate battle" + "2 guys
# 1 girl all Japanese but all Detroit Bounce and KRSOne compliant."
# ('Gmega' is read as Mega -- the desk's reading, marked.)
#
# BUILD ORDER AS FOLLOWED BY THIS RUN (stated plainly, per the
# commission): the founder's numbered deliverables for THIS piece
# name the sheets first, so this run follows sheets -> lyrics ->
# instrumental -> vocal, the score-first law. The KRS Mastering
# Rule's locked order (instrumental -> lyrics -> sheets last)
# governs tracks that declare "mastering_rule": "krs-blueprint"
# in the pipeline; this strike is a studio-runs production under
# the founder's explicit deliverable order for the piece, and the
# run report prints both orders and the one followed.
#
# MECHANISM, in order:
#   1. COMPOSITION DATA (below) is the single source of truth:
#      sections, the capriccio derivation, the Japanese bars with
#      kana + romaji morae + GLOSS apparatus, melodies by printed
#      rule, the mirror constructed as data (B's note sequence IS
#      A's reversed, in code, not by resemblance).
#   2. VERIFICATION of the mirror at the desk's own hand: paired
#      mora counts equal, B's line-ending vowel sequence == the
#      exact reverse of A's, B's (midi, dur) sequence == the exact
#      reverse of its pair's. Any failure refuses the build.
#   3. SHEETS FIRST: sheet.abc written from the same data (ABC is
#      the layer of record; no engraver stands on this box).
#   4. LYRICS: LYRICS.md written from the same data, raw and
#      uncut; the English lines are GLOSS apparatus only.
#   5. INSTRUMENTAL: rendered through the studio's seats as they
#      stand (eightoeight kit + VV kick, the Super 808 treatment,
#      house violin/piano synthesis in this file), mastered with
#      pipeline.master_signal to the law and weighed by
#      vocal_exam.judge_masterlaw.
#   6. VOCAL RUN: score-first through resonance.studio.diffsinger
#      (the Mugetsu precedent road), calibration factors rebuilt
#      from the proof ledger, speakers Civet (Kurogane AND his
#      Mirror -- the same voice turned) and Phascogale (Shion,
#      soprano seat; the bank documents no registers, so the seat
#      is flagged for the founder's ear). The detection seat reads
#      the render's language and the read is printed.
#   7. GEMINI PROMPT: GEMINI-PROMPT.md embeds sheet.abc and
#      LYRICS.md BYTE-EXACT inside the house prompt-pack shape
#      (docs/LYRA-GEMINI-PROMPT-PACKS.md is the precedent).
#   8. RECORD: RUN-REPORT.md + manifest.json. The founder's
#      mastering rider (2026-11-24 15:25) is printed in the
#      report as this piece's standing mastering instruction:
#      both versions kept entire; the better version takes the
#      mastering of record; his ear is the final gate.
#
# DOCTRINE: the lyrics below are the desk's Japanese bars written
# for the founder's Mugetsu-Gumi detachment (KUROGANE the male
# lead; his MIRROR, the same voice turned; SHION, soprano of the
# invocation, holding the capriccio line and the close). YAMI is
# not seated in this piece under the founder's 2-guys-1-girl
# count; her verdict-hook is the named alternate his pen may
# swap in. No real performer's voice is used or imitated: the
# DiffSinger bank's speakers are synthetic seats, and the cast
# are the house's created personae.
# ---------------------------------------------------------------------

import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from resonance.core.notes import SOLFEGGIO_FREQS, midi_to_freq
from resonance.studio import diffsinger as ds
from resonance.studio import eightoeight as e8
from resonance.studio import pipeline, proofs, vocal_exam
from resonance.studio import detect as detect_mod

SR = 48000
BPM = 144
EIGHTH_S = 60.0 / BPM / 2.0          # one eighth at 144 BPM
BAR_S = 13 * EIGHTH_S                # one 13/8 bar = 2.708333 s
SWING = 0.12                         # of an eighth, odd steps late
TITLE = "KAGAMI KETTOU"
SUBTITLE = "鏡決闘 — the mirrored duel that ends in a draw"

# ---------------------------------------------------------------------
# The form: 93 bars exactly (the KRS foundation count).
# (name, bars, seat) -- seats drive arrangement + vocal placement.
# ---------------------------------------------------------------------
SECTIONS = [
    ("capriccio_i",   8,  "Capriccio I -- the arena opens"),
    ("verse_a",       16, "KUROGANE -- Verse A, bars 9-24"),
    ("verse_b",       16, "THE MIRROR -- Verse B, bars 25-40"),
    ("shion",         8,  "SHION -- capriccio seat, bars 41-48"),
    ("capriccio_ii",  8,  "Capriccio II -- retrograde, bars 49-56"),
    ("duel",          16, "Instrumental duel, bars 57-72"),
    ("reprise",       16, "Full-ensemble reprise, bars 73-88"),
    ("close",         5,  "Stalemate close, bars 89-93"),
]
assert sum(b for _, b, _ in SECTIONS) == 93

SECTION_START = {}
_pos = 1
for _name, _bars, _seat in SECTIONS:
    SECTION_START[_name] = _pos
    _pos += _bars

# Chord roots (midi of the root, F-minor family) per section, one
# root per bar, cycled. Verse B's cycle is Verse A's REVERSED --
# the harmony itself is mirrored, printed here as data.
ROOTS = {
    "capriccio_i":  [41] * 8,                       # F
    "verse_a":      [41, 37, 44, 39] * 4,           # F Db Ab Eb
    "verse_b":      [39, 44, 37, 41] * 4,           # Eb Ab Db F
    "shion":        [41] * 8,                       # F
    "capriccio_ii": [41] * 8,                       # F
    "duel":         [41, 39] * 8,                   # F / Eb
    "reprise":      [41, 37, 44, 39] * 4,           # F Db Ab Eb
    "close":        [41] * 5,                       # F held
}

# The Brightmoor signature: the dark four-note grand-piano motif,
# F - Ab - C - Ab, identical wherever it plays (manifest of record:
# studio-runs/brightmoor-rachets-v3). Steps/durations in eighths:
# the motif tiles the 13/8 bar exactly (3+3+3+4).
MOTIF = [(53, 0, 3), (56, 3, 3), (60, 6, 3), (56, 9, 4)]

# ---------------------------------------------------------------------
# THE CAPRICCIO DERIVATION (the house's construction, printed --
# never dressed as an attested system).
#
# 1776 = 93 by the founder's formula: 17 + 76 = 93.
#   * The digit string of 1776 -- 1, 7, 7, 6 -- is read as DEGREES
#     of the house solfeggio nine (resonance.core.notes:
#     174, 285, 396, 417, 528, 639, 741, 852, 963 Hz). The cell is
#     therefore degrees [1, 7, 7, 6] = carriers [174, 741, 741,
#     639] Hz, played at their equal-tempered staff approximations
#     (the arpeggio module's standing doctrine; the cents each
#     carrier stands from its staff pitch are printed in the
#     report, never smoothed away).
#   * THE HEAD: the cell stated 4 times (16 attacks) + the crown
#     degree 9 (963 Hz) as attack 17. 17 stands at the door.
#   * THE BODY: the cell RETROGRADED -- [6, 7, 7, 1], the mirror
#     inside the flight itself -- stated 19 times = 76 attacks.
#   * 17 + 76 = 93 attacks exactly. The count IS the formula.
#   * Placement: attacks walk the eighth grid of 8 bars (104
#     slots); the crown attack holds 4 slots (+3) and eight of
#     the body attacks (every 8th, the first eight) hold 2 (+8):
#     93 attacks + 11 held slots = 104.
#   * Register: the head at staff pitch; in the body, from the
#     11th cell onward, degrees 3 and above climb +12 (degree 1,
#     the foundation carrier, never climbs).
#   * CAPRICCIO II is Capriccio I in exact retrograde: the whole
#     93-attack (pitch, duration) sequence reversed -- the mirror
#     point of the piece, verifiable event by event.
# ---------------------------------------------------------------------
LADDER_HZ = list(SOLFEGGIO_FREQS)     # 174 .. 963, degrees 1..9


def staff_midi(carrier_hz):
    """Nearest equal-tempered staff pitch of a carrier, and the
    cents the carrier stands from it (printed, never smoothed)."""
    exact = 69.0 + 12.0 * math.log2(float(carrier_hz) / 440.0)
    midi = int(round(exact))
    return midi, round((exact - midi) * 100.0, 1)


CELL = [1, 7, 7, 6]                   # the digits of 1776 as degrees


def build_capriccio_i():
    """Return the 93 events of Capriccio I: dicts with degree,
    carrier_hz, midi, start_eighth (within the 8 bars), dur_eighths."""
    degrees = CELL * 4 + [9] + CELL[::-1] * 19
    assert len(degrees) == 93, len(degrees)
    events = []
    slot = 0
    for i, deg in enumerate(degrees):
        attack_no = i + 1
        dur = 1
        if attack_no == 17:
            dur = 4                   # the crown holds the door
        elif attack_no > 17 and (attack_no - 17) % 8 == 0 \
                and attack_no <= 81:
            dur = 2                   # eight body attacks hold
        # 93 attacks + 3 (crown) + 8 (body holds) = 104 slots.
        midi, _cents = staff_midi(LADDER_HZ[deg - 1])
        if attack_no > 17:
            body_idx = attack_no - 18             # 0-based in body
            cell_no = body_idx // 4 + 1           # 1..19
            if cell_no >= 11 and deg >= 3:
                midi += 12                        # the climb
        events.append({"attack": attack_no, "degree": deg,
                       "carrier_hz": LADDER_HZ[deg - 1],
                       "midi": midi, "start_eighth": slot,
                       "dur_eighths": dur})
        slot += dur
    assert slot == 104, slot          # 8 bars of 13 eighths, tiled
    return events


def build_capriccio_ii(events_i):
    """Capriccio II: the exact retrograde. Event k of II is event
    94-k of I with pitch and duration carried; starts re-walked
    from slot 0 so the retrograde tiles the same 104 slots."""
    rev = list(reversed(events_i))
    out = []
    slot = 0
    for j, ev in enumerate(rev):
        out.append({"attack": j + 1, "degree": ev["degree"],
                    "carrier_hz": ev["carrier_hz"],
                    "midi": ev["midi"], "start_eighth": slot,
                    "dur_eighths": ev["dur_eighths"],
                    "mirror_of_attack": ev["attack"]})
        slot += ev["dur_eighths"]
    assert slot == 104, slot
    return out


CAP_I = build_capriccio_i()
CAP_II = build_capriccio_ii(CAP_I)

# 93 -- Live, Love, and let Love, Live.

# ---------------------------------------------------------------------
# THE BARS. Filed raw and uncut, in the house's bilingual filing:
# kana, romaji morae (the DiffSinger dictionary's graphemes), and a
# literal English GLOSS line per line -- apparatus only, never a
# rewrite. Knowledge bars in the Teacha's discipline: every line
# teaches; the duel is fought with self-knowledge, and the mirror
# is answered by turning the same lesson around.
#
# MIRROR LAW (binding, verified below): Verse B line j answers
# Verse A line 17-j. Paired lines carry EQUAL mora counts. B's
# line-ending vowel sequence is the EXACT REVERSE of A's. B's
# (midi, duration) note sequence is the EXACT REVERSE of its
# pair's -- the mirror is constructed in code, not by ear.
# ---------------------------------------------------------------------

# (kana, [romaji morae], gloss)
VERSE_A = [
    ("かがみのまえにたつおとこ",
     ["ka", "ga", "mi", "no", "ma", "e", "ni", "ta", "tsu", "o",
      "to", "ko"],
     "A man stands before the mirror."),
    ("おのれしらぬものはまける",
     ["o", "no", "re", "shi", "ra", "nu", "mo", "no", "wa", "ma",
      "ke", "ru"],
     "Who does not know himself loses."),
    ("ことばはけんよりもつよく",
     ["ko", "to", "ba", "wa", "ke", "n", "yo", "ri", "mo", "tsu",
      "yo", "ku"],
     "Words are stronger than the sword."),
    ("しんじつひとつかがみにうつる",
     ["shi", "n", "ji", "tsu", "hi", "to", "tsu", "ka", "ga", "mi",
      "ni", "u", "tsu", "ru"],
     "One truth is reflected in the mirror."),
    ("デトロイトのかぜほねまでさむい",
     ["de", "to", "ro", "i", "to", "no", "ka", "ze", "ho", "ne",
      "ma", "de", "sa", "mu", "i"],
     "The Detroit wind is cold to the bone."),
    ("それでもおれはここにたつ",
     ["so", "re", "de", "mo", "o", "re", "wa", "ko", "ko", "ni",
      "ta", "tsu"],
     "Still, I stand here."),
    ("ビートはじゅうさんはくのうみ",
     ["bi", "i", "to", "wa", "ju", "u", "sa", "n", "ha", "ku",
      "no", "u", "mi"],
     "The beat is a sea of thirteen counts."),
    ("はちぶおんぷにのるたましい",
     ["ha", "chi", "bu", "o", "n", "pu", "ni", "no", "ru", "ta",
      "ma", "shi", "i"],
     "A soul rides the eighth notes."),
    ("まなべまなべくちよりさきに",
     ["ma", "na", "be", "ma", "na", "be", "ku", "chi", "yo", "ri",
      "sa", "ki", "ni"],
     "Learn, learn -- before the mouth speaks."),
    ("みみをすませてこころできけ",
     ["mi", "mi", "o", "su", "ma", "se", "te", "ko", "ko", "ro",
      "de", "ki", "ke"],
     "Clear your ears; listen with your heart."),
    ("かがみのおとこてきではない",
     ["ka", "ga", "mi", "no", "o", "to", "ko", "te", "ki", "de",
      "wa", "na", "i"],
     "The man in the mirror is not the enemy."),
    ("そいつはせんせいかおはおれ",
     ["so", "i", "tsu", "wa", "se", "n", "se", "i", "ka", "o",
      "wa", "o", "re"],
     "He is the teacher; the face is mine."),
    ("まけをしるものつよくなる",
     ["ma", "ke", "o", "shi", "ru", "mo", "no", "tsu", "yo", "ku",
      "na", "ru"],
     "Who knows defeat becomes strong."),
    ("かちにおぼれるものはおちる",
     ["ka", "chi", "ni", "o", "bo", "re", "ru", "mo", "no", "wa",
      "o", "chi", "ru"],
     "Who drowns in victory falls."),
    ("きゅうじゅうさんのかずむねにきざむ",
     ["kyu", "u", "ju", "u", "sa", "n", "no", "ka", "zu", "mu",
      "ne", "ni", "ki", "za", "mu"],
     "I carve the number 93 into my chest."),
    ("しょうぶはここからまだおわらない",
     ["sho", "u", "bu", "wa", "ko", "ko", "ka", "ra", "ma", "da",
      "o", "wa", "ra", "na", "i"],
     "The battle, from here, is not yet over."),
]

# B_j answers A_(17-j). The final mora of each B line was seated
# first -- its vowel is dictated by the reversed ending sequence --
# and the line was written to land on it.
VERSE_B = [
    ("おわりではないこここそはじまり",
     ["o", "wa", "ri", "de", "wa", "na", "i", "ko", "ko", "ko",
      "so", "ha", "ji", "ma", "ri"],
     "It is not the end; this very place is the beginning."),
    ("おなじかずをむねにきざみもやす",
     ["o", "na", "ji", "ka", "zu", "o", "mu", "ne", "ni", "ki",
      "za", "mi", "mo", "ya", "su"],
     "I carve the same number in my chest, and burn."),
    ("おちたところからまたのぼる",
     ["o", "chi", "ta", "to", "ko", "ro", "ka", "ra", "ma", "ta",
      "no", "bo", "ru"],
     "From the place I fell, I climb again."),
    ("つよさはまけからうまれる",
     ["tsu", "yo", "sa", "wa", "ma", "ke", "ka", "ra", "u", "ma",
      "re", "ru"],
     "Strength is born from defeat."),
    ("せんせいのこえはおれのこえ",
     ["se", "n", "se", "i", "no", "ko", "e", "wa", "o", "re",
      "no", "ko", "e"],
     "The teacher's voice is my voice."),
    ("てきはいないかがみのなかに",
     ["te", "ki", "wa", "i", "na", "i", "ka", "ga", "mi", "no",
      "na", "ka", "ni"],
     "There is no enemy inside the mirror."),
    ("こころのみみできいたこたえ",
     ["ko", "ko", "ro", "no", "mi", "mi", "de", "ki", "i", "ta",
      "ko", "ta", "e"],
     "The answer heard with the heart's ear."),
    ("くちよりさきにまなんだみち",
     ["ku", "chi", "yo", "ri", "sa", "ki", "ni", "ma", "na", "n",
      "da", "mi", "chi"],
     "The road learned before the mouth spoke."),
    ("たましいのせてはちぶのなみ",
     ["ta", "ma", "shi", "i", "no", "se", "te", "ha", "chi", "bu",
      "no", "na", "mi"],
     "Carrying the soul: a wave of eighth notes."),
    ("じゅうさんのうみはいまここに",
     ["ju", "u", "sa", "n", "no", "u", "mi", "wa", "i", "ma",
      "ko", "ko", "ni"],
     "The sea of thirteen is here, now."),
    ("さむさのなかでここにたつ",
     ["sa", "mu", "sa", "no", "na", "ka", "de", "ko", "ko", "ni",
      "ta", "tsu"],
     "Inside the cold, I stand here."),
    ("デトロイトのかぜはいまもおなじ",
     ["de", "to", "ro", "i", "to", "no", "ka", "ze", "wa", "i",
      "ma", "mo", "o", "na", "ji"],
     "The Detroit wind is the same, even now."),
    ("かがみにうつるしんじつひとつ",
     ["ka", "ga", "mi", "ni", "u", "tsu", "ru", "shi", "n", "ji",
      "tsu", "hi", "to", "tsu"],
     "Reflected in the mirror: one truth."),
    ("けんにまさることばひびく",
     ["ke", "n", "ni", "ma", "sa", "ru", "ko", "to", "ba", "hi",
      "bi", "ku"],
     "Words that surpass the sword resound."),
    ("まけるはおのれしらぬやつ",
     ["ma", "ke", "ru", "wa", "o", "no", "re", "shi", "ra", "nu",
      "ya", "tsu"],
     "The one who loses is the one who does not know himself."),
    ("かがみまえにたつはおとこ",
     ["ka", "ga", "mi", "ma", "e", "ni", "ta", "tsu", "wa", "o",
      "to", "ko"],
     "The one standing before the mirror is a man."),
]

# SHION's capriccio seat (bars 41-48): the invocation voice holds
# the arena's center -- the piece's midpoint (bar 46.5) falls
# inside her seat.
SHION_LINES = [
    ("むげつのそらにひらくはな",
     ["mu", "ge", "tsu", "no", "so", "ra", "ni", "hi", "ra", "ku",
      "ha", "na"],
     "A flower opens in the moonless sky."),
    ("むらさきのほのおやけどはしない",
     ["mu", "ra", "sa", "ki", "no", "ho", "no", "o", "ya", "ke",
      "do", "wa", "shi", "na", "i"],
     "The violet flame does not burn."),
    ("いやすちからをうたにかえて",
     ["i", "ya", "su", "chi", "ka", "ra", "o", "u", "ta", "ni",
      "ka", "e", "te"],
     "Turn the healing power into song."),
    ("かがみのむこうであえるあした",
     ["ka", "ga", "mi", "no", "mu", "ko", "o", "de", "a", "e",
      "ru", "a", "shi", "ta"],
     "Tomorrow, we can meet beyond the mirror."),
    ("ふたりのこえはひとつになる",
     ["fu", "ta", "ri", "no", "ko", "e", "wa", "hi", "to", "tsu",
      "ni", "na", "ru"],
     "Two voices become one."),
    ("かちもまけもここにはない",
     ["ka", "chi", "mo", "ma", "ke", "mo", "ko", "ko", "ni", "wa",
      "na", "i"],
     "Neither victory nor defeat is here."),
    ("じゅうさんのそらにかけるはし",
     ["ju", "u", "sa", "n", "no", "so", "ra", "ni", "ka", "ke",
      "ru", "ha", "shi"],
     "A bridge hung across the sky of thirteen."),
    ("うたいつづけるあかつきまで",
     ["u", "ta", "i", "tsu", "zu", "ke", "ru", "a", "ka", "tsu",
      "ki", "ma", "de"],
     "Keep singing until the dawn."),
]

# THE STALEMATE CLOSE (bars 89-93): both duelists and the girl
# land on the SAME line -- the shared ground. No winner is sung.
CLOSE_LINE = (
    "かがみはかがみわれらはひとつ",
    ["ka", "ga", "mi", "wa", "ka", "ga", "mi", "wa", "re", "ra",
     "wa", "hi", "to", "tsu"],
    "The mirror is the mirror; we are one.")
FINAL_LINE = (
    "しょうぶはひきわけこれがこたえ",
    ["sho", "u", "bu", "wa", "hi", "ki", "wa", "ke", "ko", "re",
     "ga", "ko", "ta", "e"],
    "The battle is a draw -- this is the answer.")

# ---------------------------------------------------------------------
# Kana -> romaji mora splitter: the second hand. Every filed mora
# table is cross-checked against the kana string it claims to
# read; a disagreement refuses the build (the Mugetsu precedent).
# ---------------------------------------------------------------------
_SMALL = {"ゃ": "ya", "ゅ": "yu", "ょ": "yo"}
_KANA_ROWS = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
    "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "わ": "wa", "を": "o", "ん": "n",
    "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o",
    "ゃ": "ya", "ゅ": "yu", "ょ": "yo",
}
_KATA_TO_HIRA = {chr(c): chr(c - 0x60) for c in range(0x30A1, 0x30F6)}


_PALATAL_STEM = {"ki": "ky", "gi": "gy", "shi": "sh", "ji": "j",
                 "chi": "ch", "ni": "ny", "hi": "hy", "bi": "by",
                 "pi": "py", "mi": "my", "ri": "ry"}


def split_morae(kana_text):
    """Split a kana string into romaji morae. Katakana is folded
    to hiragana first; a palatal kana followed by a small ya/yu/yo
    forms one palatal mora (ki + small-ya -> kya); the long-vowel
    mark repeats the previous mora's vowel as its own mora
    (bi + mark -> bi, i), exactly as the filed tables read it."""
    text = "".join(_KATA_TO_HIRA.get(ch, ch) for ch in kana_text)
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "ー":
            if not out:
                raise ValueError("splitter: leading long-vowel mark")
            out.append(ending_vowel(out[-1]))
            i += 1
            continue
        if ch not in _KANA_ROWS:
            raise ValueError(f"splitter: no mora for {ch!r}")
        base = _KANA_ROWS[ch]
        if (i + 1 < len(text) and text[i + 1] in _SMALL
                and base in _PALATAL_STEM):
            base = _PALATAL_STEM[base] + _SMALL[text[i + 1]][1:]
            i += 2
        else:
            i += 1
        out.append(base)
    return out


def load_ja_dict():
    """Parse the bank's own dsdict-ja.yaml entries (grapheme ->
    phoneme list) with a small hand parser -- the dictionary of
    record decides what may be sung, not this file's opinion."""
    path = (HERE.parents[1] / "diffsinger-lab" / "banks"
            / "Lem-the-Shapeshifter-DS-2.5-dur26" / "lem_v2_5"
            / "dsdur" / "dsdict-ja.yaml")
    entries = {}
    current = None
    in_entries = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("entries:"):
            in_entries = True
            continue
        if not in_entries:
            continue
        if raw.startswith("- grapheme: "):
            current = raw.split(":", 1)[1].strip().strip("'\"")
            entries[current] = []
        elif raw.strip().startswith("- ja/") and current:
            # The plug composes the language prefix itself
            # (build_line keys phonemes as f"{lang}/{name}"), so
            # the dictionary's ja/ prefix is stripped here and
            # bare names are carried, as the Mugetsu tables do.
            name = raw.strip()[2:]
            entries[current].append(
                name[3:] if name.startswith("ja/") else name)
    return entries


JA_DICT = load_ja_dict()


def mora_phonemes(morae):
    """Romaji morae -> the bank's phoneme lists, per its own
    dictionary. An unknown grapheme refuses, by name."""
    out = []
    for m in morae:
        if m not in JA_DICT:
            raise ValueError(f"dictionary: no grapheme {m!r}")
        out.append(list(JA_DICT[m]))
    return out


def ending_vowel(mora):
    """The vowel a romaji mora ends on (its rhyme seat)."""
    for ch in reversed(mora):
        if ch in "aiueo":
            return ch
    raise ValueError(f"no vowel in mora {mora!r}")


# ---------------------------------------------------------------------
# Note rules. Durations in EIGHTHS; every vocal bar tiles 13.
#
# VERSE RULE (the chant): every mora starts at 1 eighth. A short
# line (fewer morae than 13) adds whole eighths at the accent
# seats -- head, final, middle, in that order. A long line runs
# sixteenth pairs at mora pairs (1,2), (5,6), (9,10), (13,14)
# (0-based starts 1, 5, 9, 13), each pair shedding one eighth,
# until the bar tiles.
# MELODY RULE (the chant): seat F3 (53); every 4th mora and the
# line head lift to Ab3 (56); the penultimate mora lifts to C4
# (60); the final mora settles back to F3 (53).
# SHION RULE (sung): the melody walks a printed F-minor template
# in the soprano seat, rotated by line; durations give the final
# mora +2 eighths and pure-vowel morae +1, then the sixteenth-pair
# rule trims any overflow and accent seats absorb any shortfall.
# ---------------------------------------------------------------------
_PAIR_STARTS = (1, 5, 9, 13)


def tile_durations(m, target=13.0, sung=False, morae=None):
    durs = [1.0] * m
    if sung:
        durs[-1] += 2.0
        if morae:
            for i, g in enumerate(morae):
                if g in ("a", "i", "u", "e", "o") and i != m - 1:
                    durs[i] += 1.0
    total = sum(durs)
    pi = 0
    while total > target and pi < len(_PAIR_STARTS):
        s = _PAIR_STARTS[pi]
        if s + 1 < m and durs[s] == 1.0 and durs[s + 1] == 1.0:
            durs[s] = durs[s + 1] = 0.5
            total -= 1.0
        pi += 1
    if total > target:  # last resort: shave the longest holds
        i = int(np.argmax(durs))
        while total > target:
            durs[i] -= 0.5
            total -= 0.5
    accents = [0, m - 1, m // 2, 1, m - 2]
    ai = 0
    while total < target:
        durs[accents[ai % len(accents)]] += 1.0
        total += 1.0
        ai += 1
    assert abs(sum(durs) - target) < 1e-9, (m, durs)
    return durs


def chant_melody(m):
    notes = [53] * m
    for i in range(m):
        if i % 4 == 0:
            notes[i] = 56
    if m >= 2:
        notes[-2] = 60
    notes[-1] = 53
    notes[0] = 56
    return notes


_SHION_TEMPLATE = [65, 68, 70, 72, 70, 68, 65, 68,
                   72, 75, 72, 68, 70, 68]


def shion_melody(m, line_idx):
    rot = _SHION_TEMPLATE[line_idx % 4:] + _SHION_TEMPLATE[:line_idx % 4]
    notes = [rot[i % len(rot)] for i in range(m)]
    notes[-1] = 65
    return notes


def build_vocal_lines():
    """Assemble every sung line of the piece as data: id, seat,
    speaker, kana, morae, notes (midi, dur_s), offset_s, gloss.
    The mirror is CONSTRUCTED here: B's notes are the reverse of
    its pair's, taken from the built A line itself."""
    lines = []

    def notes_for(morae, melody):
        durs = tile_durations(len(morae))
        return [{"midi": md, "dur": d * EIGHTH_S}
                for md, d in zip(melody, durs)], durs

    a_built = []
    for i, (kana, morae, gloss) in enumerate(VERSE_A):
        notes, _ = notes_for(morae, chant_melody(len(morae)))
        a_built.append(notes)
        lines.append({
            "id": f"a{i + 1:02d}", "seat": "KUROGANE",
            "speaker": "Civet", "kana": kana, "morae": morae,
            "notes": notes, "gloss": gloss,
            "offset": (SECTION_START["verse_a"] - 1 + i) * BAR_S,
            "bar": SECTION_START["verse_a"] + i})
    for j, (kana, morae, gloss) in enumerate(VERSE_B):
        pair = a_built[15 - j]
        notes = [{"midi": n["midi"], "dur": n["dur"]}
                 for n in reversed(pair)]
        lines.append({
            "id": f"b{j + 1:02d}", "seat": "THE MIRROR",
            "speaker": "Civet", "kana": kana, "morae": morae,
            "notes": notes, "gloss": gloss,
            "offset": (SECTION_START["verse_b"] - 1 + j) * BAR_S,
            "bar": SECTION_START["verse_b"] + j,
            "mirror_of": f"a{16 - j:02d}"})
    for i, (kana, morae, gloss) in enumerate(SHION_LINES):
        durs = tile_durations(len(morae), sung=True, morae=morae)
        mel = shion_melody(len(morae), i)
        notes = [{"midi": md, "dur": d * EIGHTH_S}
                 for md, d in zip(mel, durs)]
        lines.append({
            "id": f"s{i + 1:02d}", "seat": "SHION",
            "speaker": "Phascogale", "kana": kana, "morae": morae,
            "notes": notes, "gloss": gloss,
            "offset": (SECTION_START["shion"] - 1 + i) * BAR_S,
            "bar": SECTION_START["shion"] + i})
    # The close: C1 over bars 89-90 (both duelists in unison),
    # bar 91 Shion alone at the octave, bar 92 all three, bar 93
    # the final line, all three. One line, one ground.
    ck, cm, cg = CLOSE_LINE
    c_durs = tile_durations(len(cm), target=26.0)
    c_mel = chant_melody(len(cm))
    c_notes = [{"midi": md, "dur": d * EIGHTH_S}
               for md, d in zip(c_mel, c_durs)]
    base = SECTION_START["close"] - 1
    lines.append({"id": "c-guy", "seat": "KUROGANE",
                  "speaker": "Civet", "kana": ck, "morae": cm,
                  "notes": c_notes, "gloss": cg,
                  "offset": base * BAR_S, "bar": base + 1})
    lines.append({"id": "c-mirror", "seat": "THE MIRROR",
                  "speaker": "Civet", "kana": ck, "morae": cm,
                  "notes": [dict(n) for n in c_notes], "gloss": cg,
                  "offset": base * BAR_S, "bar": base + 1})
    s_durs = tile_durations(len(cm), sung=True, morae=cm)
    s_notes = [{"midi": md + 12, "dur": d * EIGHTH_S}
               for md, d in zip(c_mel, s_durs)]
    lines.append({"id": "c-shion-91", "seat": "SHION",
                  "speaker": "Phascogale", "kana": ck, "morae": cm,
                  "notes": s_notes, "gloss": cg,
                  "offset": (base + 2) * BAR_S, "bar": base + 3})
    lines.append({"id": "c-guy-92", "seat": "KUROGANE",
                  "speaker": "Civet", "kana": ck, "morae": cm,
                  "notes": [{"midi": n["midi"],
                             "dur": n["dur"] / 2.0} for n in c_notes],
                  "gloss": cg,
                  "offset": (base + 3) * BAR_S, "bar": base + 4})
    lines.append({"id": "c-shion-92", "seat": "SHION",
                  "speaker": "Phascogale", "kana": ck, "morae": cm,
                  "notes": [{"midi": md + 12,
                             "dur": d * EIGHTH_S / 2.0}
                            for md, d in zip(c_mel, c_durs)],
                  "gloss": cg,
                  "offset": (base + 3) * BAR_S, "bar": base + 4})
    fk, fm, fg = FINAL_LINE
    f_durs = tile_durations(len(fm))
    f_mel = chant_melody(len(fm))
    f_notes = [{"midi": md, "dur": d * EIGHTH_S}
               for md, d in zip(f_mel, f_durs)]
    lines.append({"id": "f-guy", "seat": "KUROGANE + MIRROR",
                  "speaker": "Civet", "kana": fk, "morae": fm,
                  "notes": f_notes, "gloss": fg,
                  "offset": (base + 4) * BAR_S, "bar": base + 5})
    lines.append({"id": "f-shion", "seat": "SHION",
                  "speaker": "Phascogale", "kana": fk, "morae": fm,
                  "notes": [{"midi": n["midi"] + 12, "dur": n["dur"]}
                            for n in f_notes], "gloss": fg,
                  "offset": (base + 4) * BAR_S, "bar": base + 5})
    return lines


VOCAL_LINES = build_vocal_lines()


def morae_match(split, table):
    """Splitter output vs a filed romaji table. Exact, with ONE
    named convention: the topic particle は is sung 'wa' (its
    pronunciation, and the reading the bank's dictionary is fed),
    so a splitter 'ha' may match a filed 'wa'. In this corpus the
    content-word は stands filed as 'ha' in exactly three places
    -- はく (A7, counts), はな (S1, flower), はし (S7, bridge) --
    and every other は is the particle. Second convention, same
    kind: the long-vowel う after an o-mora is sung 'o' (the
    ō of むこう, S4 -- the one place it occurs)."""
    if len(split) != len(table):
        return False
    for i, (s, t) in enumerate(zip(split, table)):
        if s == t or (s == "ha" and t == "wa"):
            continue
        if (s == "u" and t == "o" and i > 0
                and ending_vowel(table[i - 1]) == "o"):
            continue
        return False
    return True


def verify_all():
    """The desk's own audit, run before anything is written:
    kana tables vs the splitter, paired mora counts, the reversed
    ending-vowel sequence, the constructed note mirror, and the
    capriccio counts. Returns the verification record."""
    rec = {"checks": []}

    def check(name, ok, detail):
        rec["checks"].append({"check": name, "ok": bool(ok),
                              "detail": detail})
        if not ok:
            raise ValueError(f"verification failed: {name}: {detail}")

    for seat, verse in (("A", VERSE_A), ("B", VERSE_B),
                        ("S", SHION_LINES)):
        for i, (kana, morae, _g) in enumerate(verse):
            split = split_morae(kana)
            check(f"{seat}{i + 1} kana table == splitter",
                  morae_match(split, morae),
                  f"{split} vs {morae}")
            mora_phonemes(morae)  # raises by name if unsingable
    for kana, morae, _g in (CLOSE_LINE, FINAL_LINE):
        check("close kana table == splitter",
              morae_match(split_morae(kana), morae), kana)
        mora_phonemes(morae)
    rec["phoneme_dictionary_entries"] = len(JA_DICT)

    for j in range(16):
        a = VERSE_A[15 - j]
        b = VERSE_B[j]
        check(f"pair B{j + 1}/A{16 - j} mora counts equal",
              len(a[1]) == len(b[1]),
              f"{len(a[1])} vs {len(b[1])}")
    a_end = [ending_vowel(v[1][-1]) for v in VERSE_A]
    b_end = [ending_vowel(v[1][-1]) for v in VERSE_B]
    check("B ending vowels == reverse(A ending vowels)",
          b_end == a_end[::-1], f"A {a_end} / B {b_end}")
    rec["a_ending_vowels"] = a_end
    rec["b_ending_vowels"] = b_end

    by_id = {ln["id"]: ln for ln in VOCAL_LINES}
    for j in range(16):
        a = by_id[f"a{16 - j:02d}"]
        b = by_id[f"b{j + 1:02d}"]
        a_seq = [(n["midi"], round(n["dur"], 9)) for n in a["notes"]]
        b_seq = [(n["midi"], round(n["dur"], 9)) for n in b["notes"]]
        check(f"B{j + 1} notes == reverse(A{16 - j} notes)",
              b_seq == a_seq[::-1], "constructed in code")
    for ln in VOCAL_LINES:
        total = sum(n["dur"] for n in ln["notes"])
        bars = 2 if ln["id"] in ("c-guy", "c-mirror") else 1
        check(f"line {ln['id']} tiles its bar(s)",
              abs(total - bars * BAR_S) < 1e-6,
              f"{total:.6f}s vs {bars * BAR_S:.6f}s")
    check("capriccio I attacks == 93", len(CAP_I) == 93,
          f"{len(CAP_I)}")
    check("capriccio I head == 17 attacks before body",
          CAP_I[16]["degree"] == 9 and CAP_I[16]["attack"] == 17,
          "attack 17 is the crown degree 9")
    check("capriccio II == retrograde of I",
          [(e["midi"], e["dur_eighths"]) for e in CAP_II]
          == [(e["midi"], e["dur_eighths"])
              for e in reversed(CAP_I)],
          "event-for-event")
    rec["capriccio_attacks"] = len(CAP_I)
    rec["vocal_lines"] = len(VOCAL_LINES)
    rec["total_morae"] = sum(len(ln["morae"]) for ln in VOCAL_LINES)
    return rec

# 93 -- Live, Love, and let Love, Live.

# ---------------------------------------------------------------------
# THE SHEETS. ABC is the layer of record (no engraver stands on
# this box). The sheet is GENERATED from the composition data --
# the same events the render strikes -- so score and sound cannot
# drift apart. The written grid is straight; the Detroit Bounce
# swing (0.12 of an eighth on odd steps) is a performance
# displacement applied at render and disclosed here and in the
# report, never hidden inside the notation.
# ---------------------------------------------------------------------
_PC_FLAT = {0: "C", 1: "_D", 2: "D", 3: "_E", 4: "E", 5: "F",
            6: "_G", 7: "G", 8: "_A", 9: "A", 10: "_B", 11: "B"}


def _dur_suffix(d):
    from fractions import Fraction
    f = Fraction(d).limit_denominator(4)
    if f.denominator == 1:
        return "" if f.numerator == 1 else str(f.numerator)
    if f.numerator == 1:
        return f"/{f.denominator}"
    return f"{f.numerator}/{f.denominator}"


def midi_token(midi, dur):
    name = _PC_FLAT[midi % 12]
    octv = midi // 12 - 1          # midi 60 -> octave 4 (C)
    if octv >= 5:
        tok = name.lower() + "'" * (octv - 5)
    elif octv == 4:
        tok = name.lower()
    elif octv == 3:
        tok = name
    else:
        tok = name + "," * (3 - octv)
    return tok + _dur_suffix(dur)


def render_voice_bars(events, total_bars=93):
    """Events: dicts {start (eighths, global), dur, midi}. Returns
    one ABC string per bar, notes split at barlines with ties,
    gaps filled with rests -- every bar tiles exactly 13."""
    bars = [[] for _ in range(total_bars)]
    for ev in sorted(events, key=lambda e: e["start"]):
        pos = float(ev["start"])
        remaining = float(ev["dur"])
        first = True
        while remaining > 1e-9:
            bar = int(pos // 13)
            in_bar = pos - bar * 13
            seg = min(remaining, 13.0 - in_bar)
            bars[bar].append((in_bar, seg, ev["midi"], first,
                              remaining - seg > 1e-9))
            pos += seg
            remaining -= seg
            first = False
    out = []
    for bar_segs in bars:
        toks = []
        cursor = 0.0
        for in_bar, seg, midi, _first, continues in sorted(bar_segs):
            if in_bar > cursor + 1e-9:
                toks.append("z" + _dur_suffix(in_bar - cursor))
            tok = midi_token(midi, seg)
            if continues:
                tok += "-"
            toks.append(tok)
            cursor = in_bar + seg
        if cursor < 13.0 - 1e-9:
            toks.append("z" + _dur_suffix(13.0 - cursor))
        if not toks:
            toks = ["z13"]
        out.append(" ".join(toks))
    return out


def section_bar_range(name):
    start = SECTION_START[name]
    bars = dict((n, b) for n, b, _s in SECTIONS)[name]
    return start, start + bars - 1


def build_instrument_events():
    """The instrumental event lists per voice, from the form.
    Returns dict voice -> events (eighth grid, global)."""
    ev = {"VLN": [], "RH": [], "LH": [], "B808": []}
    for name, bars, _seat in SECTIONS:
        b0 = SECTION_START[name] - 1          # 0-based first bar
        for bi in range(bars):
            bar = b0 + bi
            g = bar * 13                       # global eighth
            root = ROOTS[name][bi]
            # Grand piano, left hand: root and fifth.
            if name in ("shion", "close"):
                ev["LH"].append({"start": g, "dur": 13,
                                 "midi": root})
            else:
                ev["LH"].append({"start": g, "dur": 6,
                                 "midi": root})
                ev["LH"].append({"start": g + 6, "dur": 7,
                                 "midi": root + 7})
            # Super 808 line: the root, held.
            if name == "close":
                ev["B808"].append({"start": g, "dur": 13,
                                   "midi": root - 12})
            elif name == "shion":
                ev["B808"].append({"start": g, "dur": 13,
                                   "midi": root - 12})
            else:
                ev["B808"].append({"start": g, "dur": 6,
                                   "midi": root - 12})
                ev["B808"].append({"start": g + 6, "dur": 7,
                                   "midi": root - 12})
            # Grand piano, right hand: the Brightmoor motif,
            # identical wherever it plays -- except the duel's
            # even bars, where the piano ANSWERS with the motif
            # retrograded (the mirror in the instruments).
            if name == "duel" and bi % 2 == 1:
                for midi, step, dur in [(56, 0, 3), (60, 3, 3),
                                        (56, 6, 3), (53, 9, 4)]:
                    ev["RH"].append({"start": g + step, "dur": dur,
                                     "midi": midi})
            elif name != "duel" or bi % 2 == 0:
                if name != "duel":
                    for midi, step, dur in MOTIF:
                        ev["RH"].append({"start": g + step,
                                         "dur": dur, "midi": midi})
            # Violin: the duel's odd bars carry the motif up the
            # octave; its even bars are the piano's answer (above).
            if name == "duel":
                if bi < 8 and bi % 2 == 0:
                    for midi, step, dur in MOTIF:
                        ev["VLN"].append({"start": g + step,
                                          "dur": dur,
                                          "midi": midi + 12})
                elif bi >= 8:
                    ev["VLN"].append({"start": g, "dur": 13,
                                      "midi": 72 if bi % 4 < 2
                                      else 75})
    # Violin: the capriccios.
    for sec_name, cap in (("capriccio_i", CAP_I),
                          ("capriccio_ii", CAP_II)):
        g0 = (SECTION_START[sec_name] - 1) * 13
        for e in cap:
            ev["VLN"].append({"start": g0 + e["start_eighth"],
                              "dur": e["dur_eighths"],
                              "midi": e["midi"]})
    # Violin: reprise long tones, one per four bars.
    r0 = SECTION_START["reprise"] - 1
    for k, midi in enumerate((65, 68, 72, 68)):
        ev["VLN"].append({"start": (r0 + 4 * k) * 13, "dur": 52,
                          "midi": midi})
    # Violin: the close -- one held tone at the door and at the end.
    c0 = SECTION_START["close"] - 1
    ev["VLN"].append({"start": c0 * 13, "dur": 13, "midi": 72})
    ev["VLN"].append({"start": (c0 + 4) * 13, "dur": 13, "midi": 65})
    return ev


def kit_bar_tokens(section_name, bar_idx_in_section, last_bar=False):
    """One bar of the kit voice. Tokens: F, = kick (the VV seat),
    c = snare, ^g = closed hat, ^a = open hat; chords bracketed.
    The pattern is the 808 demo's, weighed 21/21 on this bench:
    kick steps [0,3,6,10], snare [4,11], hats on odd steps, the
    open hat at 12."""
    if section_name == "close":
        hits = {0: ["F,"]}
        if last_bar:
            hits[4] = ["c"]
            hits[11] = ["c"]
    elif section_name == "shion":
        hits = {0: ["F,"], 6: ["F,"]}
        for s in (1, 3, 5, 7, 9, 11):
            hits.setdefault(s, []).append("^g")
    else:
        hits = {s: ["F,"] for s in (0, 3, 6, 10)}
        hits[4] = ["c"]
        hits[11] = ["c"]
        for s in (1, 3, 5, 7, 9, 11):
            hits.setdefault(s, []).append("^g")
        hits.setdefault(12, []).append("^a")
    toks = []
    for step in range(13):
        if step in hits:
            parts = hits[step]
            toks.append(parts[0] if len(parts) == 1
                        else "[" + "".join(parts) + "]")
        else:
            toks.append("z")
    return " ".join(toks)


def vocal_events(seats):
    ev = []
    for ln in VOCAL_LINES:
        if ln["seat"] not in seats:
            continue
        pos = ln["offset"] / EIGHTH_S
        for n in ln["notes"]:
            ev.append({"start": pos, "dur": n["dur"] / EIGHTH_S,
                       "midi": n["midi"]})
            pos += n["dur"] / EIGHTH_S
    return ev


def write_sheet(path, inst_events):
    voices = {}
    voices["VLN"] = render_voice_bars(inst_events["VLN"])
    voices["RH"] = render_voice_bars(inst_events["RH"])
    voices["LH"] = render_voice_bars(inst_events["LH"])
    voices["B808"] = render_voice_bars(inst_events["B808"])
    voices["KUR"] = render_voice_bars(
        vocal_events({"KUROGANE", "KUROGANE + MIRROR"}))
    voices["MIR"] = render_voice_bars(
        vocal_events({"THE MIRROR", "KUROGANE + MIRROR"}))
    voices["SHI"] = render_voice_bars(vocal_events({"SHION"}))
    kit = []
    for name, bars, _seat in SECTIONS:
        for bi in range(bars):
            kit.append(kit_bar_tokens(
                name, bi,
                last_bar=(name == "close" and bi == bars - 1)))
    order = ["VLN", "RH", "LH", "B808", "KIT", "KUR", "MIR", "SHI"]
    names = {"VLN": "Violin", "RH": "Grand Piano RH",
             "LH": "Grand Piano LH", "B808": "Super 808 Bass",
             "KIT": "808 Kit", "KUR": "KUROGANE",
             "MIR": "THE MIRROR", "SHI": "SHION"}
    lines = [
        "X:1",
        f"T:{TITLE} -- {SUBTITLE}",
        "C:Mugetsu-Gumi, for Johnathan 'Qasparr' Monroe",
        "M:13/8",
        "L:1/8",
        "Q:1/4=144",
        "K:Fmin",
        "% KRS-One Method: 93 bars, 144 BPM, 13/8 Sigma Mega grid.",
        "% Capriccio derivation (house construction, printed): the",
        "% digits of 1776 read as solfeggio degrees [1,7,7,6]; head",
        "% = cell x4 + crown degree 9 (17 attacks); body = the cell",
        "% retrograded [6,7,7,1] x19 (76 attacks); 17+76 = 93.",
        "% Capriccio II is Capriccio I in exact retrograde.",
        "% Mirror map: B_j answers A_(17-j); B's notes are A's",
        "% reversed (pitch and duration); B's ending vowels are",
        "% A's reversed. The full map is filed in LYRICS.md.",
        "% Kit legend: F, = kick (VV seat, 44 Hz), c = snare,",
        "% ^g = closed hat, ^a = open hat.",
        "% Detroit Bounce: odd eighth steps are played 0.12 of an",
        "% eighth late (swing), disclosed here; the written grid",
        "% above is straight, as written.",
    ]
    bar_section = {}
    for name, bars, _seat in SECTIONS:
        s = SECTION_START[name]
        for bi in range(bars):
            bar_section[s + bi] = (name, bi)
    for v in order:
        lines.append(f"V:{v} name=\"{names[v]}\"")
        body = voices[v] if v != "KIT" else kit
        chunk = []
        for bar_no in range(1, 94):
            sec_name, _bi = bar_section[bar_no]
            if bar_no == SECTION_START[sec_name]:
                chunk.append(f"\"_{sec_name} bar {bar_no}\"")
            chunk.append(body[bar_no - 1] + " |")
            if bar_no % 4 == 0:
                lines.append(" ".join(chunk))
                chunk = []
        if chunk:
            lines.append(" ".join(chunk))
        lines.append("|]")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_lyrics(path):
    out = []
    out.append(f"# {TITLE} — {SUBTITLE}")
    out.append("")
    out.append("Lyrics filed raw and uncut, in the house's "
               "bilingual filing: kana, romaji morae, and a "
               "literal English GLOSS under each section "
               "(apparatus only — the gloss is never a rewrite).")
    out.append("")
    out.append("**Cast (the founder's ruling, 2026-11-24: 2 guys "
               "1 girl, all Japanese, all Detroit Bounce, "
               "KRS-One compliant):** KUROGANE （黒鋼）, the male "
               "lead — GUY ONE. THE MIRROR — GUY TWO: Kurogane's "
               "own voice turned, the diplomatic half-turn made "
               "audible. SHION （紫苑） — THE GIRL: soprano of the "
               "invocation; she holds the capriccio seat and the "
               "close. YAMI is not seated in this piece under the "
               "2-guys-1-girl count; her verdict-hook is the "
               "named alternate the founder's pen may swap in.")
    out.append("")
    out.append("**Form:** 93 bars · 144 BPM · 13/8 Sigma Mega. "
               "Capriccio I (1–8) · Verse A (9–24) · Verse B, "
               "the mirror (25–40) · Shion (41–48) · Capriccio "
               "II, retrograde (49–56) · instrumental duel "
               "(57–72) · reprise (73–88) · stalemate close "
               "(89–93).")
    out.append("")

    def block(title, verse, seat):
        out.append(f"## {title}")
        out.append("")
        for i, (kana, morae, gloss) in enumerate(verse, 1):
            out.append(f"{seat} {i}. {kana}")
            out.append(f"   {' '.join(morae)}")
        out.append("")
        out.append("GLOSS (literal, apparatus only):")
        for i, (_k, _m, gloss) in enumerate(verse, 1):
            out.append(f"{i}. {gloss}")
        out.append("")

    block("VERSE A — KUROGANE (bars 9–24)", VERSE_A, "A")
    block("VERSE B — THE MIRROR (bars 25–40)", VERSE_B, "B")
    block("SHION — the capriccio seat (bars 41–48)", SHION_LINES,
          "S")
    out.append("## THE STALEMATE CLOSE (bars 89–93)")
    out.append("")
    out.append("Bars 89–90: KUROGANE and THE MIRROR in unison. "
               "Bar 91: SHION alone, at the octave. Bar 92: all "
               "three. Bar 93: the final line, all three. One "
               "line, one ground — no winner is sung.")
    out.append("")
    ck, cm, cg = CLOSE_LINE
    fk, fm, fg = FINAL_LINE
    out.append(f"CLOSE. {ck}")
    out.append(f"   {' '.join(cm)}")
    out.append(f"FINAL. {fk}")
    out.append(f"   {' '.join(fm)}")
    out.append("")
    out.append("GLOSS (literal, apparatus only):")
    out.append(f"CLOSE. {cg}")
    out.append(f"FINAL. {fg}")
    out.append("")
    out.append("## THE MIRROR MAP (verifiable from this file and "
               "sheet.abc)")
    out.append("")
    out.append("Verse B line j answers Verse A line 17−j. Paired "
               "lines carry equal mora counts. B's line-ending "
               "vowel sequence is the exact reverse of A's. B's "
               "(pitch, duration) note sequence is the exact "
               "reverse of its pair's — constructed in code and "
               "verified before anything was rendered.")
    out.append("")
    out.append("| B line | answers | A ending vowel | B ending "
               "vowel | morae A = B |")
    out.append("|---|---|---|---|---|")
    for j in range(16):
        a = VERSE_A[15 - j]
        b = VERSE_B[j]
        out.append(f"| B{j + 1} | A{16 - j} | "
                   f"{ending_vowel(a[1][-1])} | "
                   f"{ending_vowel(b[1][-1])} | "
                   f"{len(a[1])} = {len(b[1])} |")
    out.append("")
    out.append("A's ending vowels, in order: "
               + " ".join(ending_vowel(v[1][-1]) for v in VERSE_A)
               + ". B's, in order: "
               + " ".join(ending_vowel(v[1][-1]) for v in VERSE_B)
               + " — the same sequence, turned.")
    out.append("")
    out.append("## THE CAPRICCIO DERIVATION (the house's "
               "construction — printed, never dressed as an "
               "attested system)")
    out.append("")
    out.append("1776 = 93 by the founder's formula: 17 + 76 = 93. "
               "The digits of 1776 — 1, 7, 7, 6 — are read as "
               "degrees of the house solfeggio nine (174, 285, "
               "396, 417, 528, 639, 741, 852, 963 Hz): the cell "
               "is degrees [1, 7, 7, 6] = carriers [174, 741, "
               "741, 639] Hz, played at their equal-tempered "
               "staff approximations (the house arpeggio "
               "doctrine; the cents offsets are printed in the "
               "run report). HEAD: the cell ×4 plus the crown "
               "degree 9 = 17 attacks. BODY: the cell retrograded "
               "[6, 7, 7, 1] ×19 = 76 attacks. 17 + 76 = 93 "
               "attacks; the count is the formula. Capriccio II "
               "(bars 49–56) is Capriccio I in exact retrograde.")
    out.append("")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return path

# 93 -- Live, Love, and let Love, Live.

# ---------------------------------------------------------------------
# SYNTHESIS SEATS (named, as the bench honestly holds them).
#   * Kit + kick: resonance.studio.eightoeight, the studio's own
#     instrument (weighed 21/21 on this bench the same day).
#   * SUPER 808 BASS: the same kick with the treatment pushed --
#     drive 0.15 -> 0.45, decay_tau 0.16 -> 0.42, struck at each
#     bar's chord root. Not a different instrument: the recipe
#     delta and both measurements are printed in the report.
#   * VIOLIN: a bowed harmonic stack (amplitudes 1/k^0.9, the
#     house arpeggio recipe) with vibrato, synthesized here.
#   * GRAND PIANO: a decaying harmonic stack with a stretched
#     second partial, synthesized here.
#   * SIGMA BED: pure-tone carriers of the solfeggio set at low
#     level under everything (the Sigma ground), plus the chord
#     root an octave down.
# No 16-bit MIDI sound anywhere in this strike: every voice is
# synthesized at 48 kHz float and mastered from the float sum.
# ---------------------------------------------------------------------

def piano_note(freq, dur_s, vel=1.0):
    n = max(1, int(dur_s * SR))
    t = np.arange(n) / SR
    tau = min(1.4, 0.35 + 0.55 * dur_s)
    env = np.exp(-t / tau)
    env *= np.minimum(1.0, t / 0.004 + 0.15)
    tone = (np.sin(2 * np.pi * freq * t)
            + 0.55 * np.sin(2 * np.pi * freq * 2.003 * t)
            + 0.30 * np.sin(2 * np.pi * freq * 3.01 * t)
            + 0.16 * np.sin(2 * np.pi * freq * 4.16 * t)
            + 0.07 * np.sin(2 * np.pi * freq * 5.43 * t))
    return (tone * env * vel).astype(np.float32)


def violin_note(freq, dur_s, vel=1.0, seed=93):
    n = max(1, int(dur_s * SR))
    t = np.arange(n) / SR
    vib = 1.0 + 0.004 * np.sin(2 * np.pi * 5.5 * t) \
        * np.minimum(1.0, np.maximum(0.0, (t - 0.08) / 0.25))
    phase = 2 * np.pi * np.cumsum(freq * vib) / SR
    tone = np.zeros(n)
    for k in range(1, 11):
        tone += (1.0 / k ** 0.9) * np.sin(k * phase)
    tone /= sum(1.0 / k ** 0.9 for k in range(1, 11))
    atk = np.minimum(1.0, t / 0.010)
    rel = np.minimum(1.0, np.maximum(
        0.0, (dur_s - t) / min(0.05, dur_s * 0.3)))
    return (tone * atk * rel * vel).astype(np.float32)


def pad_note(freq, dur_s, vel=1.0):
    from scipy.signal import butter, sosfilt
    n = max(1, int(dur_s * SR))
    t = np.arange(n) / SR
    saw = np.zeros(n)
    for detune in (0.996, 1.004):
        ph = (freq * detune * t) % 1.0
        saw += 2.0 * ph - 1.0
    sos = butter(2, 1100.0, btype="low", fs=SR, output="sos")
    tone = sosfilt(sos, saw)
    env = np.minimum(1.0, t / 0.35) * np.minimum(
        1.0, np.maximum(0.0, (dur_s - t) / 0.4))
    peak = np.max(np.abs(tone)) or 1.0
    return (tone / peak * env * vel).astype(np.float32)


def _place(mix, mono, start_s, gain, pan=0.0):
    """Place a mono float32 voice into the stereo mix with an
    equal-power pan. Out-of-range tails are clipped, never wrapped."""
    i0 = int(round(start_s * SR))
    if i0 >= mix.shape[1]:
        return
    seg = mono[:mix.shape[1] - i0]
    left = math.cos((pan + 1.0) * math.pi / 4.0)
    right = math.sin((pan + 1.0) * math.pi / 4.0)
    mix[0, i0:i0 + len(seg)] += seg * (gain * left)
    mix[1, i0:i0 + len(seg)] += seg * (gain * right)


def _swung(start_eighth):
    """Detroit Bounce: odd whole steps inside the bar are played
    SWING of an eighth late. Fractional starts (sixteenth pairs)
    are placed as written."""
    step = start_eighth % 13
    if abs(step - round(step)) < 1e-9 and int(round(step)) % 2 == 1:
        return start_eighth + SWING
    return start_eighth


def kit_steps(section_name, last_bar=False):
    """(step, kind) pairs for one bar -- the sample-domain twin of
    kit_bar_tokens; both are written from the one pattern law."""
    if section_name == "close":
        hits = [(0, "kick")]
        if last_bar:
            hits += [(4, "snare"), (11, "snare")]
        return hits
    if section_name == "shion":
        return ([(0, "kick"), (6, "kick")]
                + [(s, "hat") for s in (1, 3, 5, 7, 9, 11)])
    return ([(s, "kick") for s in (0, 3, 6, 10)]
            + [(4, "snare"), (11, "snare")]
            + [(s, "hat") for s in (1, 3, 5, 7, 9, 11)]
            + [(12, "open")])


def render_instrumental(inst_events):
    """Render the full 93-bar instrumental. Returns (stereo
    float32 premaster, report dict)."""
    total_s = 93 * BAR_S
    n = int(round(total_s * SR))
    mix = np.zeros((2, n), dtype=np.float32)
    # The Sigma bed: solfeggio carriers, low, under everything.
    t = np.arange(n) / SR
    bed = np.zeros(n, dtype=np.float32)
    for j, carrier in enumerate((174.0, 285.0, 396.0, 417.0)):
        trem = 0.85 + 0.15 * np.sin(2 * np.pi * 0.05 * (j + 1) * t
                                    + j)
        bed += (0.045 * trem
                * np.sin(2 * np.pi * carrier * t)).astype(np.float32)
    mix[0] += bed
    mix[1] += bed * 0.92
    # Chord-root sub, one per bar.
    for name, bars, _s in SECTIONS:
        b0 = SECTION_START[name] - 1
        for bi in range(bars):
            root_hz = midi_to_freq(ROOTS[name][bi] - 12)
            i0 = int((b0 + bi) * BAR_S * SR)
            seg = (0.10 * np.sin(2 * np.pi * root_hz
                                 * np.arange(int(BAR_S * SR)) / SR))
            mix[0, i0:i0 + len(seg)] += seg.astype(np.float32)
            mix[1, i0:i0 + len(seg)] += seg.astype(np.float32)
    # The kit one-shots, from the studio's own instrument.
    shots = {"kick": e8.kick(tune="VV").astype(np.float32),
             "snare": e8.snare().astype(np.float32),
             "hat": e8.hihat(open_=False).astype(np.float32),
             "open": e8.hihat(open_=True).astype(np.float32)}
    gains = {"kick": 0.85, "snare": 0.50, "hat": 0.24, "open": 0.28}
    for name, bars, _s in SECTIONS:
        b0 = SECTION_START[name] - 1
        for bi in range(bars):
            for step, kind in kit_steps(
                    name, last_bar=(name == "close"
                                    and bi == bars - 1)):
                at = (b0 + bi) * 13 + step
                at = _swung(at)
                _place(mix, shots[kind], at * EIGHTH_S,
                       gains[kind], pan=0.0)
    # Super 808 bass line: the same kick, treatment pushed.
    super_params = {"decay_tau": 0.42, "drive": 0.45, "click": 0.15}
    for ev in inst_events["B808"]:
        root_hz = midi_to_freq(ev["midi"])
        hit = e8.kick(fundamental=root_hz,
                      sweep_start=root_hz * 2.5,
                      seconds=ev["dur"] * EIGHTH_S + 0.25,
                      **super_params).astype(np.float32)
        _place(mix, hit, _swung(ev["start"]) * EIGHTH_S, 0.80,
               pan=0.0)
    # Grand piano.
    for ev in inst_events["RH"]:
        note = piano_note(midi_to_freq(ev["midi"]),
                          ev["dur"] * EIGHTH_S, vel=0.34)
        _place(mix, note, _swung(ev["start"]) * EIGHTH_S, 1.0,
               pan=0.12)
    for ev in inst_events["LH"]:
        note = piano_note(midi_to_freq(ev["midi"]),
                          ev["dur"] * EIGHTH_S, vel=0.30)
        _place(mix, note, _swung(ev["start"]) * EIGHTH_S, 1.0,
               pan=-0.12)
    # Pads under Shion and the reprise.
    for name in ("shion", "reprise"):
        bars = dict((nm, b) for nm, b, _s in SECTIONS)[name]
        b0 = SECTION_START[name] - 1
        for bi in range(bars):
            root = ROOTS[name][bi]
            for off in (12, 15, 19):
                note = pad_note(midi_to_freq(root + off), BAR_S,
                                vel=0.045)
                _place(mix, note, (b0 + bi) * BAR_S, 1.0, pan=0.0)
    # Violin.
    for ev in inst_events["VLN"]:
        note = violin_note(midi_to_freq(ev["midi"]),
                           ev["dur"] * EIGHTH_S, vel=0.38)
        _place(mix, note, _swung(ev["start"]) * EIGHTH_S, 1.0,
               pan=-0.08)
    # The Super treatment, measured both ways for the record.
    plain = e8.kick(tune="VV")
    super_vv = e8.kick(fundamental=float(
        e8.fundamental_for_pair("VV")["placed_hz"]),
        sweep_start=110.0, seconds=1.5, **super_params)
    report = {
        "duration_s": round(n / SR, 4),
        "super_808": {
            "seat": "VV (44 Hz placed fundamental)",
            "plain_kick": {**e8.measure_buffer(plain),
                           **e8.kick_track(plain)},
            "super_kick": {**e8.measure_buffer(super_vv),
                           **e8.kick_track(super_vv)},
            "treatment": super_params,
            "recipe_delta": "drive 0.15 -> 0.45; decay_tau "
                            "0.16 -> 0.42; click 0.5 -> 0.15; "
                            "same eightoeight.kick instrument",
        },
    }
    return mix, report


def master_and_judge(samples, stem, out_base):
    """Master a stereo float mix to the law and weigh the MP3.
    Writes <out_base>.wav (24-bit) and <out_base>.mp3 (320k).

    The law is weighed on the DECODED MP3 (the house's decoded
    road), so the float master is struck with its ceiling at
    -1.35 dBTP: MP3 decode can move a true peak by a few tenths,
    and a master aimed exactly at -1.0 can decode a hair over
    the -1.0 ceiling (this run's first instrumental strike read
    exactly -1.0 decoded and the judge refused it). The margin
    is the bench's own precedent: the 808 pattern demo decoded
    at -1.35 dBTP."""
    mastered, mrep = pipeline.master_signal(
        np.asarray(samples, dtype=np.float64), SR, -14.0, -1.35)
    wav_path = HERE / f"{out_base}.wav"
    mp3_path = HERE / f"{out_base}.mp3"
    sf.write(str(wav_path), mastered.T, SR, subtype="PCM_24")
    import subprocess
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
         "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3_path)],
        check=True)
    verdict = vocal_exam.judge_masterlaw(mp3_path, sworn_bps=320000)
    return {"wav": wav_path.name, "mp3": mp3_path.name,
            "mastering": mrep, "verdict": verdict}


def render_vocals(calibration_factors, trained_by):
    """The score-first vocal run through the DiffSinger plug.
    Returns (manifest, spec) -- or raises, and the caller prints
    the gap at full size."""
    spec_lines = []
    for ln in VOCAL_LINES:
        spec_lines.append({
            "id": ln["id"], "lang": "ja", "speaker": ln["speaker"],
            "text": ln["kana"],
            "morae": mora_phonemes(ln["morae"]),
            "notes": ln["notes"], "offset": ln["offset"]})
    spec = {"title": f"{TITLE} -- house version 1 vocal run "
                     f"(KUROGANE + MIRROR seat: Civet; "
                     f"SHION seat: Phascogale)",
            "lines": spec_lines, "assembly_file": "vocal-stem.wav",
            "threads": 4,
            "calibration": {"factors": calibration_factors,
                            "trained_by": trained_by}}
    (HERE / "spec.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2),
        encoding="utf-8")
    manifest = ds.render(spec, HERE,
                         log=lambda m: print(m, flush=True))
    return manifest, spec

# 93 -- Live, Love, and let Love, Live.

# ---------------------------------------------------------------------
# THE GEMINI PROMPT (founder's addition, 2026-11-24 15:25: "Save
# full sheets and lyrics as a prompt to Gemini"). The prompt
# TRANSPORTS the sheets and lyrics byte-exact; it never edits
# them. Shape follows docs/LYRA-GEMINI-PROMPT-PACKS.md, the
# precedent of record: spec in instruction form first, then the
# complete score and the complete bars, then honest limits and
# return instructions.
# ---------------------------------------------------------------------

def write_gemini_prompt(path):
    sheet_text = (HERE / "sheet.abc").read_text(encoding="utf-8")
    lyrics_text = (HERE / "LYRICS.md").read_text(encoding="utf-8")
    prompt = f"""# {TITLE} — {SUBTITLE}
## A performance prompt for Gemini — Mugetsu-Gumi, the Japanese detachment of the house

One of two strikes of the same piece. The house version was built
in-house at Resonantia (sheets, lyrics, instrumental and a sung
vocal run are already filed). This prompt is the Gemini strike:
when it is made, the two versions are compared BY MEASUREMENT and
the founder's ear decides which takes the mastering of record;
the other is kept filed, entire, never discarded (the founder's
ruling, 2026-11-24). Paste everything inside the fence below into
Gemini, in one message.

```text
You are the performer and producer for a finished Japanese rap
track: "{TITLE}" — a KRS-One Method mirrored-duel stalemate
battle, performed by MUGETSU-GUMI, a three-persona rap detachment.
Produce the complete track from the score and lyrics embedded
below. The sheets and lyrics are the composer's filed originals:
perform them EXACTLY as written — do not rewrite, translate,
clean up, shorten, or add a single line.

THE SPEC
- Method: KRS-One compliant — knowledge bars, no wasted lines,
  the verse as lesson. The battle is fought with self-knowledge.
- Tempo and grid: 144 BPM, 13/8 time (thirteen eighth notes per
  bar), 93 bars total. The form, in order: Capriccio I (bars
  1-8, instrumental flight) · Verse A (9-24) · Verse B, the
  mirror (25-40) · the girl's capriccio seat (41-48) ·
  Capriccio II (49-56, the capriccio in exact retrograde) ·
  instrumental duel (57-72) · full-ensemble reprise (73-88) ·
  stalemate close (89-93).
- Cast — 2 guys, 1 girl, ALL JAPANESE, all delivered in DETROIT
  BOUNCE (the bounce lives in the rhythm of the delivery and the
  beat, whatever the tongue; odd eighth steps lean late):
  * KUROGANE （黒鋼） — GUY ONE, the male lead: young male voice,
    forward, rough-edged, street diction, testimony at the
    front. He states Verse A.
  * THE MIRROR — GUY TWO: Kurogane's own voice TURNED — the same
    voice, answering Verse A line-for-line in reverse
    architecture (Verse B). Same singer, mirrored delivery.
  * SHION （紫苑） — THE GIRL: soprano, clear and high, the
    invocation voice; the violet flame that does not burn but
    heals. She holds bars 41-48 and joins the close.
- The mirror law (binding): Verse B line j answers Verse A line
  17-j; B's melody and rhythm are A's reversed; B's line-ending
  vowels are A's ending vowels reversed. The mirror map is
  printed at the end of the lyrics — keep the mirroring AUDIBLE.
- The close is a STALEMATE: bars 89-93 land all three voices on
  the SAME shared line. No winner. Do not resolve the duel.
- Instruments: violin (it carries the capriccio arpeggio),
  grand piano (lead string seat; the dark four-note Brightmoor
  motif F - Ab - C - Ab repeats identically wherever it plays),
  Super 808 bass (deep, driven, long-decay 808 at the chord
  roots, kick tuned to the VV seat at 44 Hz), 808 kit, and a
  quiet solfeggio-carrier bed under everything.
- The capriccio: an arpeggio flight DERIVED from 1776 = 93
  (17 + 76 = 93): the digits of 1776 read as solfeggio degrees
  [1, 7, 7, 6] over the nine carriers (174, 285, 396, 417, 528,
  639, 741, 852, 963 Hz); 17 attacks state the head, 76 the
  mirrored body — 93 attacks in all. Play it as written in the
  score; Capriccio II is the same flight in exact retrograde.
- Language: Japanese throughout, exactly the kana lines filed
  below. The romaji under each line is the reading; the English
  GLOSS lines are apparatus for understanding only — never sing
  the gloss.
- Mastering target for your strike: integrated loudness near
  -14 LUFS, true peak at or below -1.0 dBTP, delivered as a
  full-quality audio file (and, if you can, the vocal and
  instrumental stems separately).

=== THE SCORE (ABC notation — the complete sheet, verbatim) ===
{sheet_text.rstrip()}
=== END OF SCORE ===

=== THE LYRICS (filed raw and uncut — verbatim) ===
{lyrics_text.rstrip()}
=== END OF LYRICS ===

HONEST LIMITS AND RETURN INSTRUCTIONS
- If any line, note, or section cannot be performed as written,
  say exactly which one and why, in a short note AFTER the audio
  — do not silently substitute, simplify, or drop it.
- Return: (1) the finished track audio; (2) if possible, the
  vocal stem and the instrumental stem; (3) a one-paragraph note
  stating your tempo, key, and any place you departed from the
  score (there should be none). The lyrics you sing must be the
  lyrics above, byte for byte.
```

Filed by the desk for Johnathan 'Qasparr' Monroe, ARR, All Rights
Reserved, Without Prejudice — Scientific Illuminism: the Method
of Science, the Aim of Religion.
"""
    path.write_text(prompt, encoding="utf-8")
    written = path.read_text(encoding="utf-8")
    assert sheet_text.rstrip() in written, "sheet not verbatim"
    assert lyrics_text.rstrip() in written, "lyrics not verbatim"
    return {"path": path.name,
            "bytes": len(written.encode("utf-8")),
            "sheet_verbatim": True, "lyrics_verbatim": True}


# ---------------------------------------------------------------------
# THE RECORD.
# ---------------------------------------------------------------------

def write_report(path, rec):
    v = rec["verification"]
    cents_rows = []
    for deg, hz in enumerate(LADDER_HZ, 1):
        midi, cents = staff_midi(hz)
        cents_rows.append(
            f"| {deg} | {hz} | {midi} | {cents:+.1f} |")
    checks_ok = sum(1 for c in v["checks"] if c["ok"])
    out = []
    out.append(f"# {TITLE} — RUN REPORT (House Version 1)")
    out.append("")
    out.append(f"*{SUBTITLE}* — a KRS-One Method mirrored-duel "
               "stalemate battle in Japanese, struck in-house at "
               "Resonantia. The desk's title, pending the "
               "founder's pen.")
    out.append("")
    out.append("**Commission** (founder, 2026-11-24 15:21–15:22 "
               "EST): “follow the Sheets and Lyrics doctrine "
               "format for KRS-One Method for BARS in Japanese at "
               "144 BPM with Violin, Grand Piano and Super 808 "
               "Bass with Sigma Gmega bed and 1776=93 as a "
               "solfeggio arpeggio capriccio mirrored duel "
               "stalemate battle” + “2 guys 1 girl all Japanese "
               "but all Detroit Bounce and KRSOne compliant.” "
               "‘Gmega’ is read as Mega — the desk's reading, "
               "marked. Additions the same day: the Gemini prompt "
               "(15:25) and the mastering rider (15:25, printed "
               "below as this piece's standing instruction).")
    out.append("")
    out.append("**Build order followed:** sheets → lyrics → "
               "instrumental → vocal (the founder's numbered "
               "deliverables for this piece name the sheets "
               "first; the score-first law). The KRS Mastering "
               "Rule's locked order (instrumental → lyrics → "
               "sheets last) governs pipeline tracks declaring "
               "“mastering_rule”: “krs-blueprint”; this strike "
               "is a studio-runs production under the founder's "
               "explicit order for the piece, and both orders "
               "are printed here so the record cannot drift.")
    out.append("")
    out.append("## The cast, as seated")
    out.append("")
    out.append("- **KUROGANE （黒鋼） — GUY ONE.** The Gumi's male "
               "lead; Detroit bounce delivered in Japanese. He "
               "states Verse A (bars 9–24). Sung seat: Civet.")
    out.append("- **THE MIRROR — GUY TWO.** The desk's reading of "
               "the mirrored duel, marked as the desk's reading "
               "and revisable by the founder's pen: the second "
               "guy is Kurogane's own voice turned — the "
               "diplomatic half-turn made audible. The Gumi's "
               "filed bench holds no second male persona, so the "
               "mirror is seated in the SAME voice (Civet) rather "
               "than inventing a persona the founder has not "
               "chartered. He answers with Verse B (bars 25–40), "
               "constructed as Verse A reversed.")
    out.append("- **SHION （紫苑） — THE GIRL.** Soprano of the "
               "invocation; she holds the capriccio seat "
               "(bars 41–48 — the piece's midpoint, bar 46.5, "
               "falls inside her seat) and the close. Sung seat: "
               "Phascogale.")
    out.append("- **YAMI is not seated** in this piece under the "
               "founder's 2-guys-1-girl count. Her verdict-hook "
               "is the named alternate his pen may swap in.")
    out.append("")
    out.append("## The capriccio derivation (the house's "
               "construction — printed, never attested)")
    out.append("")
    out.append("1776 = 93 by the founder's formula: 17 + 76 = 93. "
               "The digits of 1776 — 1, 7, 7, 6 — are read as "
               "degrees of the house solfeggio nine. HEAD: cell "
               "×4 + crown degree 9 = **17 attacks**. BODY: the "
               "cell retrograded [6, 7, 7, 1] ×19 = **76 "
               "attacks**. Total **93 attacks**, walking 104 "
               "eighth slots (the crown holds 4 slots; eight "
               "body attacks — every 8th, the first eight — "
               "hold 2). Capriccio II is Capriccio "
               "I in exact retrograde, verified event-for-event. "
               "Carriers are played at their equal-tempered "
               "staff approximations (the house arpeggio "
               "doctrine); the cents each carrier stands from "
               "its staff pitch:")
    out.append("")
    out.append("| degree | carrier Hz | staff midi | cents |")
    out.append("|---|---|---|---|")
    out.extend(cents_rows)
    out.append("")
    out.append("## The mirror, verified before anything rendered")
    out.append("")
    out.append(f"- Desk audit: **{checks_ok}/{len(v['checks'])} "
               "checks passed** (kana tables against an "
               "independent splitter for every line; every mora "
               "against the bank's own dictionary; paired mora "
               "counts; note tiling of every bar; the capriccio "
               "counts).")
    out.append(f"- A's ending vowels: "
               f"{' '.join(v['a_ending_vowels'])}")
    out.append(f"- B's ending vowels: "
               f"{' '.join(v['b_ending_vowels'])} — the same "
               "sequence, turned.")
    out.append("- B's (pitch, duration) sequence is A's reversed "
               "**by construction in code** and re-verified from "
               "the built lines — all 16 pairs exact.")
    out.append("- The harmony mirrors too: Verse B's chord cycle "
               "[Eb Ab Db F] is Verse A's [F Db Ab Eb] reversed.")
    out.append("")
    out.append("## The instrumental")
    out.append("")
    si = rec["instrumental"]
    out.append(f"- Duration {si['duration_s']} s (93 bars × "
               "13/8 at 144 BPM). Seats: eightoeight kit (kick "
               "on the VV seat), Super 808 bass, grand piano "
               "(Brightmoor motif F–Ab–C–Ab in the right hand, "
               "identical wherever it plays; in the duel the "
               "piano answers the violin's motif with the motif "
               "retrograded), violin (the capriccio; the duel "
               "exchanges), solfeggio-carrier Sigma bed, chord "
               "pads under Shion and the reprise. Detroit Bounce "
               "swing 0.12 of an eighth on odd steps, applied at "
               "render and disclosed in the sheet.")
    sup = si["super_808"]
    out.append(f"- **Super 808, measured:** the plain VV kick "
               f"reads peak {sup['plain_kick']['peak_dbfs']} "
               f"dBFS, tail {sup['plain_kick']['tail_hz_last_250ms']} "
               f"Hz; the Super strike (drive 0.45, decay_tau "
               f"0.42, click 0.15 — the same instrument, treatment "
               f"pushed) reads peak {sup['super_kick']['peak_dbfs']} "
               f"dBFS, RMS {sup['super_kick']['rms_dbfs']} dBFS, "
               f"tail {sup['super_kick']['tail_hz_last_250ms']} Hz "
               f"over {sup['super_kick']['duration_s']} s.")
    for label, key in (("Instrumental master", "inst_master"),):
        verdict = rec[key]["verdict"]
        mrep = rec[key]["mastering"]
        out.append(f"- **{label}** ({rec[key]['mp3']}): mastered "
                   f"at {mrep['lufs_after']} LUFS, true peak "
                   f"{mrep['true_peak_dbtp']} dBTP; master-law "
                   f"verdict on the decoded MP3 — "
                   f"{json.dumps(verdict, ensure_ascii=False)}")
    out.append("")
    out.append("## The vocal run")
    out.append("")
    if rec.get("vocal"):
        voc = rec["vocal"]
        out.append(f"- Score-first through the DiffSinger road "
                   f"(Lem the Shapeshifter DS 2.5 bank): "
                   f"**{voc['lines_rendered']} lines** — Verse A "
                   f"16, Verse B 16, Shion 8, the close 7 — every "
                   f"line the score carries. Speakers: Civet "
                   f"(Kurogane AND his Mirror — the same voice "
                   f"turned), Phascogale (Shion).")
        out.append(f"- Calibration factors from the proof "
                   f"ledger: {voc['calibration_factors']} "
                   f"(trained by {voc['calibration_trained_by']}).")
        out.append(f"- Assembly measured: {voc['assembly']}")
        out.append(f"- Asked span: {voc['asked_span_s']} s "
                   f"(the full 93 bars).")
        if rec.get("full_master"):
            fm = rec["full_master"]
            out.append(f"- **Full master** ({fm['mp3']}): "
                       f"mastered at "
                       f"{fm['mastering']['lufs_after']} LUFS, "
                       f"true peak "
                       f"{fm['mastering']['true_peak_dbtp']} dBTP; "
                       f"master-law verdict on the decoded MP3 — "
                       f"{json.dumps(fm['verdict'], ensure_ascii=False)}")
        if rec.get("detection"):
            out.append(f"- **Detection seat:** "
                       f"{rec['detection']}")
    else:
        out.append(f"- **GAP — the vocal run did not land:** "
                   f"{rec.get('vocal_gap')}")
    out.append("")
    out.append("## Gaps, at full size")
    out.append("")
    for gap in rec["gaps"]:
        out.append(f"- {gap}")
    out.append("")
    out.append("## THE MASTERING RIDER (the founder's ruling, "
               "2026-11-24 15:25 — this piece's standing "
               "mastering instruction)")
    out.append("")
    out.append("> “We will use the better version for the "
               "mastering but keep the one you had going too.”")
    out.append("")
    out.append("Applied: this package keeps BOTH versions entire "
               "— the house version (this run, complete in this "
               "folder) and the Gemini strike (seat reserved at "
               "`gemini-version/`, to be filed there when made "
               "from GEMINI-PROMPT.md). When both exist, they are "
               "compared BY MEASUREMENT and the founder's ear "
               "decides which takes the mastering of record; the "
               "other stays filed, never discarded.")
    out.append("")
    out.append("## Files")
    out.append("")
    for f in rec["files"]:
        out.append(f"- {f}")
    out.append("")
    out.append("## Ear-verdict queue")
    out.append("")
    out.append("This piece joins the founder's ear queue: the "
               "house version's full master, the instrumental, "
               "and the vocal stem. The verdict is his alone and "
               "is not pre-claimed. Named flags for his ear: "
               "Phascogale's soprano seat for Shion (the bank "
               "documents no registers); the mirror heard in one "
               "voice (Civet for both duelists — the desk's "
               "reading of the form); the capriccio's wide "
               "solfeggio steps against the F-minor bed.")
    out.append("")
    out.append("## Questions for the founder's pen")
    out.append("")
    out.append("1. The title: KAGAMI KETTOU （鏡決闘） is the "
               "desk's proposal, pending his pen.")
    out.append("2. The Mirror in Kurogane's own voice (the "
               "desk's reading) — or does his pen seat a second "
               "male persona in the Gumi?")
    out.append("3. YAMI's verdict-hook as the alternate girl "
               "seat — swap in, or does Shion hold?")
    out.append("4. When the Gemini strike lands: the comparison "
               "is printed by measurement; his ear names the "
               "mastering of record.")
    out.append("")
    out.append("---")
    out.append("Authorship attributed exclusively to Johnathan "
               "'Qasparr' Monroe, ARR, All Rights Reserved, "
               "Without Prejudice. Flagpole of Claim and Coinage "
               "reserved. Method of Science, Aim of Religion.")
    out.append("")
    out.append("93 — Live, Love, and let Love, Live.")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return path


def main():
    rec = {}
    print("== verify ==", flush=True)
    rec["verification"] = verify_all()
    ok = sum(1 for c in rec["verification"]["checks"] if c["ok"])
    print(f"verification: {ok}/{len(rec['verification']['checks'])}"
          " checks passed", flush=True)
    inst_events = build_instrument_events()
    print("== sheets first ==", flush=True)
    write_sheet(HERE / "sheet.abc", inst_events)
    print("== lyrics ==", flush=True)
    write_lyrics(HERE / "LYRICS.md")
    print("== instrumental ==", flush=True)
    mix, inst_report = render_instrumental(inst_events)
    rec["instrumental"] = inst_report
    rec["inst_master"] = master_and_judge(mix,
                                           "instrumental",
                                           "instrumental-master")
    print(f"instrumental master: {rec['inst_master']['verdict']}",
          flush=True)
    print("== vocal run ==", flush=True)
    store = proofs.rebuild_calibration()
    factors = proofs.calibration_factors(store)
    trained = proofs.calibration_trained_by(store)
    rec["gaps"] = [
        "No engraver stands on this box: the sheets ship as ABC, "
        "the layer of record (the standing house position).",
        "The DiffSinger bank documents no speaker registers: "
        "Phascogale is seated for Shion's soprano by the desk and "
        "flagged for the founder's ear; Civet is the proven seat "
        "of record (the Mugetsu hook).",
        "The Gemini version is a reserved seat, not a render: it "
        "exists when the founder pastes GEMINI-PROMPT.md and the "
        "strike returns. Nothing in this report claims it.",
    ]
    try:
        manifest, _spec = render_vocals(factors, trained)
        stem = HERE / "vocal-stem.wav"
        asked = max(ln["offset"] + sum(n["dur"] for n in ln["notes"])
                    for ln in VOCAL_LINES)
        rec["vocal"] = {
            "lines_rendered": len(VOCAL_LINES),
            "calibration_factors": factors,
            "calibration_trained_by": trained,
            "assembly": manifest.get("assembly", {}).get(
                "measured"),
            "asked_span_s": round(asked, 4),
            "walls": manifest.get("walls"),
            "nine": manifest.get("nine"),
        }
        print(f"vocal assembly: {rec['vocal']['assembly']}",
              flush=True)
        # The full mix: instrumental premaster + the sung stem.
        data, rate = sf.read(str(stem), always_2d=True)
        if rate != SR:
            from scipy.signal import resample_poly
            from math import gcd
            g = gcd(SR, rate)
            data = np.stack([resample_poly(data[:, ch], SR // g,
                                           rate // g)
                             for ch in range(data.shape[1])],
                            axis=1)
        full = np.array(mix, dtype=np.float32)
        vox = data.mean(axis=1).astype(np.float32) * 0.9
        full[0, :min(len(vox), full.shape[1])] += vox[:full.shape[1]]
        full[1, :min(len(vox), full.shape[1])] += vox[:full.shape[1]]
        rec["full_master"] = master_and_judge(full, "full",
                                              "master")
        print(f"full master: {rec['full_master']['verdict']}",
              flush=True)
        try:
            det = detect_mod.detect_language(stem)
            judge = vocal_exam.judge_language(stem, "ja")
            rec["detection"] = {"detect_language": det,
                                "judge_language": judge}
        except Exception as exc:  # the read is printed, not hidden
            rec["detection"] = {"error": f"{type(exc).__name__}: "
                                         f"{exc}"}
        print(f"detection: {rec['detection']}", flush=True)
    except Exception as exc:
        rec["vocal_gap"] = f"{type(exc).__name__}: {exc}"
        rec["gaps"].append(
            "THE VOCAL RUN DID NOT LAND: " + rec["vocal_gap"]
            + " — the sheets, lyrics, instrumental and Gemini "
              "prompt stand complete; the sung strike is the "
              "open coordinate.")
        print(f"VOCAL GAP: {rec['vocal_gap']}", flush=True)
    print("== gemini prompt ==", flush=True)
    rec["gemini_prompt"] = write_gemini_prompt(
        HERE / "GEMINI-PROMPT.md")
    print(f"gemini prompt: {rec['gemini_prompt']}", flush=True)
    (HERE / "gemini-version" / "RESERVED.md").write_text(
        "# THE GEMINI VERSION — seat reserved\n\n"
        "This folder holds the Gemini strike of KAGAMI KETTOU "
        "when it is made from ../GEMINI-PROMPT.md. Under the "
        "founder's mastering rider (2026-11-24), both versions "
        "are kept entire; the better version takes the mastering "
        "of record, decided by measurement and the founder's "
        "ear. Nothing is filed here yet, and nothing in the run "
        "report claims otherwise.\n",
        encoding="utf-8")
    rec["files"] = sorted(
        p.name for p in HERE.iterdir() if p.is_file())
    write_report(HERE / "RUN-REPORT.md", rec)
    (HERE / "manifest.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2,
                   default=str), encoding="utf-8")
    print(json.dumps({"verification_checks": ok,
                      "inst_master": rec["inst_master"]["verdict"],
                      "vocal": rec.get("vocal", {}).get("assembly"),
                      "full_master": rec.get("full_master", {})
                      .get("verdict"),
                      "detection": rec.get("detection"),
                      "gemini_prompt": rec["gemini_prompt"]},
                     ensure_ascii=False, indent=2, default=str),
          flush=True)


if __name__ == "__main__":
    main()

# 93 -- Live, Love, and let Love, Live.
