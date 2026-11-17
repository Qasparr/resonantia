# 93
# ---------------------------------------------------------------------
# build_run.py -- MUGETSU HOOK, ENGINE RUN 1: the phase proof.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: this driver assembles the proof's spec from the filed
# sources of record and hands it to the engine module
# (resonance.studio.diffsinger.render) -- the hook is rendered
# END-TO-END THROUGH THE MODULE, never by calling the lab directly.
# The three sources, each read, none edited:
#   * the filed hook text, extracted byte-exact from
#     studio-runs/gemini-mugetsu-japanese/DETROIT-MUGETSU-PROMPT.md
#     (the founder's lyrics, raw and uncut; extraction takes the
#     first [HOOK -- YAMI, SUNG] block of the filed LYRICS section
#     and refuses if it does not find exactly eight lines with
#     the anchors the desk read in the file);
#   * the filed hook score, read from DETROIT-MUGETSU-HOOK-TEST.mid
#     by the module's own score reader (track "Hook melody"), at
#     the ABC's stated 144 BPM -- the MIDI carries no tempo meta,
#     so the clock is stated here, from the notation of record;
#   * the hook's pronunciation, in the mora table below -- the
#     desk's hand phonemization, each mora's phonemes taken from
#     the bank's own dsdict-ja.yaml, and cross-checked by an
#     independent kana mora splitter run over each line's reading:
#     the splitter's morae must equal the table's kana labels, or
#     the driver refuses. Two hands, one count.
#
# DOCTRINE: YAMI sings the hook (the package's formation); the
# bank documents no register for its three colors, so the seat is
# CIVET -- the house's proven lead (Spear and Magickal Helm's hook
# lead and verse; the lab's first Japanese phrase) -- the desk's
# choice, flagged in the run report for the founder's ear, not a
# claim about the bank. The alignment of 127 morae under 54 notes
# is the module's grouping law (CONSTRUCTED, labeled): contiguous
# runs proportional to note duration, one mora minimum per note,
# no mora dropped, no note altered, no syllable of the filed text
# added or removed. Lines sit at their bar starts (144 BPM, eight
# bars, 1.6667 s each); the score tiles each bar fully, so no
# breath padding is inserted -- the duration model's realized
# lengths are measured in the manifest, and any overhang past a
# bar line is named there, not trimmed here.
# ---------------------------------------------------------------------

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from resonance.studio import diffsinger as ds  # noqa: E402

PKG = REPO / "studio-runs" / "gemini-mugetsu-japanese"
PROMPT = PKG / "DETROIT-MUGETSU-PROMPT.md"
SCORE_MID = PKG / "DETROIT-MUGETSU-HOOK-TEST.mid"
BPM = 144.0
BAR_S = 60.0 / BPM * 4          # 4/4 at 144 BPM = 1.6667 s
SPEAKER = "Civet"

# The hook's pronunciation: (kana label, phoneme names) per mora,
# phonemes from the bank's dsdict-ja.yaml. Long-vowel marks are
# their own mora carrying the vowel sung (the bank writes long
# vowels as separate vowel morae); palatal morae are the bank's
# single tokens (ky, ny, my) plus the vowel.
MORAE = [
    # L1 デトロイト生まれ、ブライトムーア育ち (18)
    [("デ", ["d", "e"]), ("ト", ["t", "o"]), ("ロ", ["r", "o"]),
     ("イ", ["i"]), ("ト", ["t", "o"]), ("ウ", ["u"]),
     ("マ", ["m", "a"]), ("レ", ["r", "e"]), ("ブ", ["b", "u"]),
     ("ラ", ["r", "a"]), ("イ", ["i"]), ("ト", ["t", "o"]),
     ("ム", ["m", "u"]), ("ー", ["u"]), ("ア", ["a"]),
     ("ソ", ["s", "o"]), ("ダ", ["d", "a"]), ("チ", ["ch", "i"])],
    # L2 縁石の上から、全部見渡し (16)
    [("エ", ["e"]), ("ン", ["N"]), ("セ", ["s", "e"]),
     ("キ", ["ky", "i"]), ("ノ", ["n", "o"]), ("ウ", ["u"]),
     ("エ", ["e"]), ("カ", ["k", "a"]), ("ラ", ["r", "a"]),
     ("ゼ", ["z", "e"]), ("ン", ["N"]), ("ブ", ["b", "u"]),
     ("ミ", ["my", "i"]), ("ワ", ["w", "a"]), ("タ", ["t", "a"]),
     ("シ", ["sh", "i"])],
    # L3 誰にも頭下げねえ、俺は俺 (16)
    [("ダ", ["d", "a"]), ("レ", ["r", "e"]), ("ニ", ["ny", "i"]),
     ("モ", ["m", "o"]), ("ア", ["a"]), ("タ", ["t", "a"]),
     ("マ", ["m", "a"]), ("サ", ["s", "a"]), ("ゲ", ["g", "e"]),
     ("ネ", ["n", "e"]), ("エ", ["e"]), ("オ", ["o"]),
     ("レ", ["r", "e"]), ("ワ", ["w", "a"]), ("オ", ["o"]),
     ("レ", ["r", "e"])],
    # L4 月無き空でも、目を開け (12)
    [("ツ", ["ts", "u"]), ("キ", ["ky", "i"]), ("ナ", ["n", "a"]),
     ("キ", ["ky", "i"]), ("ソ", ["s", "o"]), ("ラ", ["r", "a"]),
     ("デ", ["d", "e"]), ("モ", ["m", "o"]), ("メ", ["m", "e"]),
     ("ヲ", ["w", "o"]), ("ア", ["a"]), ("ケ", ["k", "e"])],
    # L5 金じゃ買えねえ、この魂 (13)
    [("キ", ["ky", "i"]), ("ン", ["N"]), ("ジャ", ["j", "a"]),
     ("カ", ["k", "a"]), ("エ", ["e"]), ("ネ", ["n", "e"]),
     ("エ", ["e"]), ("コ", ["k", "o"]), ("ノ", ["n", "o"]),
     ("タ", ["t", "a"]), ("マ", ["m", "a"]), ("シ", ["sh", "i"]),
     ("イ", ["i"])],
    # L6 嘘は通らねえ、通すのは真実 (17)
    [("ウ", ["u"]), ("ソ", ["s", "o"]), ("ワ", ["w", "a"]),
     ("ト", ["t", "o"]), ("オ", ["o"]), ("ラ", ["r", "a"]),
     ("ネ", ["n", "e"]), ("エ", ["e"]), ("ト", ["t", "o"]),
     ("オ", ["o"]), ("ス", ["s", "u"]), ("ノ", ["n", "o"]),
     ("ワ", ["w", "a"]), ("シ", ["sh", "i"]), ("ン", ["N"]),
     ("ジ", ["j", "i"]), ("ツ", ["ts", "u"])],
    # L7 地べたから天まで、自分の足で (16)
    [("ジ", ["j", "i"]), ("ベ", ["b", "e"]), ("タ", ["t", "a"]),
     ("カ", ["k", "a"]), ("ラ", ["r", "a"]), ("テ", ["t", "e"]),
     ("ン", ["N"]), ("マ", ["m", "a"]), ("デ", ["d", "e"]),
     ("ジ", ["j", "i"]), ("ブ", ["b", "u"]), ("ン", ["N"]),
     ("ノ", ["n", "o"]), ("ア", ["a"]), ("シ", ["sh", "i"]),
     ("デ", ["d", "e"])],
    # L8 王冠は奪うもんじゃねえ、被るもんだ (19)
    [("オ", ["o"]), ("オ", ["o"]), ("カ", ["k", "a"]),
     ("ン", ["N"]), ("ワ", ["w", "a"]), ("ウ", ["u"]),
     ("バ", ["b", "a"]), ("ウ", ["u"]), ("モ", ["m", "o"]),
     ("ン", ["N"]), ("ジャ", ["j", "a"]), ("ネ", ["n", "e"]),
     ("エ", ["e"]), ("カ", ["k", "a"]), ("ブ", ["b", "u"]),
     ("ル", ["r", "u"]), ("モ", ["m", "o"]), ("ン", ["N"]),
     ("ダ", ["d", "a"])],
]

READINGS = [
    "デトロイトウマレブライトムーアソダチ",
    "エンセキノウエカラゼンブミワタシ",
    "ダレニモアタマサゲネエオレワオレ",
    "ツキナキソラデモメヲアケ",
    "キンジャカエネエコノタマシイ",
    "ウソワトオラネエトオスノワシンジツ",
    "ジベタカラテンマデジブンノアシデ",
    "オオカンワウバウモンジャネエカブルモンダ",
]

_SMALL = set("ャュョァィゥェォヮ")


def split_morae(reading):
    """Independent kana mora splitter (the second hand).

    MECHANISM: small kana join the mora before them; ッ, ン and
    ー stand alone; every other kana is one mora. This hand knows
    nothing of the table -- agreement between the two is the
    check, and disagreement is a refusal, by name.
    """
    out = []
    for ch in reading:
        if ch in _SMALL and out:
            out[-1] += ch
        else:
            out.append(ch)
    return out


def extract_hook_lines():
    """The filed hook text, byte-exact, from the prompt of record."""
    text = PROMPT.read_text(encoding="utf-8")
    anchor = text.index("LYRICS (folded in")
    hook = text.index("[HOOK", anchor)
    body = text[hook:].splitlines()[1:]
    lines = []
    for ln in body:
        if not ln.strip():
            break
        lines.append(ln)
    if len(lines) != 8:
        raise ValueError(f"hook extraction found {len(lines)} "
                         "lines, expected 8 -- refused")
    if not lines[0].startswith("デトロイト"):
        raise ValueError("hook line 1 anchor mismatch -- refused")
    if not lines[7].endswith("もんだ"):
        raise ValueError("hook line 8 anchor mismatch -- refused")
    return lines


def main():
    texts = extract_hook_lines()
    # Cross-check the phonemization, two hands one count.
    for i, (table, reading) in enumerate(zip(MORAE, READINGS), 1):
        split = split_morae(reading)
        labels = [k for k, _ in table]
        if split != labels:
            raise ValueError(
                f"line {i}: mora table and splitter disagree: "
                f"{labels} vs {split} -- refused")
    total_morae = sum(len(t) for t in MORAE)
    print(f"hook: 8 lines extracted byte-exact; {total_morae} "
          "morae, table and splitter in agreement")

    melody = ds.melody_from_midi(SCORE_MID, "Hook melody", bpm=BPM)
    notes = melody["notes"]
    counts = []
    bars = []
    for b in range(8):
        lo, hi = b * BAR_S, (b + 1) * BAR_S
        bar = [n for n in notes if lo - 1e-9 <= n["start"] < hi]
        counts.append(len(bar))
        bars.append(bar)
    if counts != [7, 6, 7, 7, 7, 7, 7, 6]:
        raise ValueError(f"bar note counts {counts} != the "
                         "verified [7,6,7,7,7,7,7,6] -- refused")
    for b, bar in enumerate(bars):
        tiled = sum(n["dur"] for n in bar)
        if abs(tiled - BAR_S) > 1e-6:
            raise ValueError(f"bar {b + 1} tiles {tiled:.4f}s, "
                             f"not the full {BAR_S:.4f}s")
    print(f"score: 54 notes over 8 bars at {BPM} BPM, counts "
          f"{counts}, every bar fully tiled")

    lines = []
    for i, (text, table, bar) in enumerate(
            zip(texts, MORAE, bars), 1):
        lines.append({
            "id": f"hook-l{i}", "lang": "ja", "speaker": SPEAKER,
            "text": text,
            "morae": [ph for _, ph in table],
            "notes": [{"midi": n["midi"], "dur": n["dur"]}
                      for n in bar],
            "offset": (i - 1) * BAR_S})
    spec = {"title": "DETROIT MUGETSU -- hook, engine run 1 "
                     "(YAMI seat: Civet)",
            "lines": lines, "assembly_file": "mugetsu-hook.wav",
            "threads": 4}
    (HERE / "spec.json").write_text(
        __import__("json").dumps(spec, ensure_ascii=False,
                                 indent=2),
        encoding="utf-8")
    manifest = ds.render(spec, HERE,
                         log=lambda m: print(m, flush=True))
    print(f"assembly: {manifest['assembly']['measured']}")
    print(f"nine: {manifest['nine']}")
    print(f"walls: {manifest['walls']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 93 -- Live, Love, and let Love, Live.
