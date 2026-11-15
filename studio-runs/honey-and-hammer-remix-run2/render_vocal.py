#!/usr/bin/env python3
"""
HONEY AND HAMMER — THE EXPLICIT REMIX: run 2, the vocal stage.

House road, same bench as run 1: DiffSinger (OpenVPI, Apache-2.0) +
Lem the Shapeshifter DS 2.5 (licence-clean), English phoneme path,
CPU. Lyrics performed VERBATIM from
docs/HONEY-AND-HAMMER-EXPLICIT-REMIX.md (ghost drafts) — not one word
altered, softened, or cleaned; the work below is pronunciation only
(hand phonemisation into the bank's en/* ARPAbet tokens).

Spec (Resonantia variables): G minor, 96 BPM, 4/4. One lyric line
per bar. Structure: hook 8 bars, then five 12-line sections
(Sol Rey, Ari Sparkz, Qasparr feature, Sage Archer, Qveen Bee
feature), outro chant 2 bars.

Speaker map (the bank holds THREE speakers; the song names FIVE
personas — the two reuses are differentiated by chant register and
are flagged as a bank-size wall in the run report):
    Qveen Bee   -> Quoll       (hook lead + closing feature, base 55)
    Sage Archer -> Phascogale  (hook responses + verse 3, base 57)
    Sol Rey     -> Civet       (verse 1, base 55)
    Ari Sparkz  -> Civet       (verse 2, pitched down, base 50)
    Qasparr     -> Phascogale  (feature, pitched down, base 48)
    Outro crew  -> Quoll + Civet layered

RUN-1 LESSON APPLIED — duration calibration: run 1 measured the
duration model returning ~87% of the frame budget it was handed,
uniformly. Here every word_dur handed to the model is scaled by
CAL = 1.15 (~1/0.87). The manifest records handed (calibrated),
nominal (uncalibrated), and rendered frames per line so the new
ratio is measured, not assumed.
"""
import gc
import json
import pathlib
import sys

import numpy as np
import onnxruntime as ort

LAB = pathlib.Path.home() / "workspace/resonance/diffsinger-lab"
BANK = LAB / "banks" / "Lem-the-Shapeshifter-DS-2.5-dur26" / "lem_v2_5"
VOC = LAB / "DiffSinger" / "checkpoints" / "pc_nsf_hifigan_44.1k_hop512_128bin_2025.02"
RUN = pathlib.Path(__file__).resolve().parent
LINES_DIR = RUN / "lines"
LINES_DIR.mkdir(parents=True, exist_ok=True)

SR, HOP = 44100, 512
FPS = SR / HOP                      # 86.1328 frames per second
EN = 1                              # languages.json: en -> 1
BPM = 96.0
BAR_S = 4 * 60.0 / BPM              # 2.5 s
LEAD_SP = 0.04                      # breath before the line
TAIL_SP = 0.14                      # breath after the line
SYL_S = BAR_S - LEAD_SP - TAIL_SP   # syllables fill the rest
CAL = 1.15                          # run-1 duration calibration

ph = json.load(open(BANK / "phonemes.json", encoding="utf8"))


def pid(name):
    return ph[name] if name in ("SP", "AP") else ph["en/" + name]


# ---------------------------------------------------------------------
# THE SCORE. Hook syllables: (phonemes, midi, weight). Verse/outro
# syllables: (phonemes, weight) — chant pitches from verse_melody().
# Lyrics verbatim from the sheet.
# ---------------------------------------------------------------------
# HOOK — Qveen Bee (Quoll) lead, Sage Archer (Phascogale) responses;
# lines 6 and 8 are "(both)" and render on both speakers.
HOOK = [
    # H1 (Gm, Qveen): Honey on the hammer, watch it drip when I bounce it —
    [("hh ah", 58, 1.4), ("n iy", 55, 1.0), ("aa n", 55, 0.8),
     ("dh ax", 53, 0.5), ("hh ae", 58, 1.4), ("m er", 57, 1.0),
     ("w aa ch", 58, 1.4), ("ih t", 55, 0.6), ("d r ih p", 57, 1.4),
     ("w eh n", 55, 0.7), ("ay", 55, 0.9), ("b aw n s", 62, 1.8),
     ("ih t", 58, 1.2)],
    # H2 (Eb, Sage): bounce it, bounce it —
    [("b aw n s", 58, 1.6), ("ih t", 55, 1.0), ("b aw n s", 58, 1.6),
     ("ih t", 55, 2.6)],
    # H3 (Bb, Qveen): Booty so loud that the whole club announce it —
    [("b uw", 60, 1.4), ("t iy", 58, 0.9), ("s ow", 58, 1.0),
     ("l aw d", 62, 1.6), ("dh ae t", 55, 0.7), ("dh ax", 53, 0.5),
     ("hh ow l", 58, 1.3), ("k l ah b", 60, 1.4), ("ax", 57, 0.6),
     ("n aw n s", 62, 1.7), ("ih t", 58, 1.4)],
    # H4 (F, Sage): bounce it, bounce it —
    [("b aw n s", 60, 1.6), ("ih t", 57, 1.0), ("b aw n s", 60, 1.6),
     ("ih t", 57, 2.6)],
    # H5 (Gm, Qveen): He want the honey 'cause the honey make him spend,
    [("hh iy", 55, 0.9), ("w aa n t", 58, 1.4), ("dh ax", 53, 0.5),
     ("hh ah", 58, 1.3), ("n iy", 57, 0.9), ("k ao z", 58, 1.4),
     ("dh ax", 53, 0.5), ("hh ah", 58, 1.3), ("n iy", 57, 0.9),
     ("m ey k", 58, 1.3), ("hh ih m", 55, 0.8), ("s p eh n d", 55, 1.8)],
    # H6 (Eb, BOTH): Hammer come down, make it clap, do it again —
    [("hh ae", 58, 1.4), ("m er", 55, 0.9), ("k ah m", 58, 1.2),
     ("d aw n", 63, 1.6), ("m ey k", 60, 1.2), ("ih t", 57, 0.6),
     ("k l ae p", 60, 1.5), ("d uw", 58, 1.0), ("ih t", 55, 0.6),
     ("ax", 57, 0.7), ("g eh n", 63, 2.0)],
    # H7 (Bb, Qveen): Raw and uncut, this the X-rated end,
    [("r ao", 58, 1.5), ("ae n d", 55, 0.7), ("ah n", 58, 1.2),
     ("k ah t", 60, 1.4), ("dh ih s", 55, 0.8), ("dh ax", 53, 0.5),
     ("eh k s", 58, 1.2), ("r ey", 60, 1.3), ("t ih d", 57, 0.9),
     ("eh n d", 62, 2.0)],
    # H8 (F, BOTH): Bounce, booty, bounce — tell your friend, tell your friend.
    [("b aw n s", 60, 1.5), ("b uw", 58, 1.2), ("t iy", 57, 0.9),
     ("b aw n s", 60, 1.5), ("t eh l", 58, 1.2), ("y ao r", 57, 0.7),
     ("f r eh n d", 60, 1.5), ("t eh l", 58, 1.2), ("y ao r", 57, 0.7),
     ("f r eh n d", 65, 2.2)],
]
HOOK_SPEAKERS = {0: ("Quoll",), 1: ("Phascogale",), 2: ("Quoll",),
                 3: ("Phascogale",), 4: ("Quoll",),
                 5: ("Quoll", "Phascogale"), 6: ("Quoll",),
                 7: ("Quoll", "Phascogale")}

# VERSE 1 — SOL REY (Civet, base 55)
SOL = [
    [("s ow l", 1.3), ("r ey", 1.5), ("s iy", 1.1), ("z ax n", 0.9),
     ("ow", 1.2), ("p ax", 0.7), ("n er", 0.8), ("k ae p", 1.3),
     ("t ax n", 1.0), ("ah v", 0.6), ("dh ax", 0.5), ("f ay r", 2.0)],
    [("w ao k t", 1.4), ("ih n", 0.8), ("w ih dh", 0.8), ("dh ax", 0.5),
     ("hh ae", 1.3), ("m er", 0.9), ("ae n d", 0.6), ("dh ax", 0.5),
     ("hh ah", 1.3), ("n iy", 0.9), ("f ao r", 0.8), ("hh ay r", 2.0)],
    [("sh iy", 1.0), ("b ae k", 1.4), ("ih t", 0.7), ("ah p", 1.1),
     ("aa n", 0.8), ("dh ax", 0.5), ("k ae p", 1.3), ("t ax n", 0.9),
     ("m ey k", 1.3), ("dh ax", 0.5), ("hh ow l", 1.2), ("f l ao r", 1.4),
     ("p er", 0.9), ("s p ay r", 2.0)],
    [("ae s", 1.5), ("s ow", 1.0), ("f ae t", 1.4), ("dh ae t", 0.7),
     ("dh ax", 0.5), ("b aw n s", 1.6), ("t ey k", 1.2), ("dh ax", 0.5),
     ("r uw m", 1.4), ("hh ay", 1.0), ("er", 2.0)],
    [("n ow", 1.2), ("p ae n", 1.2), ("t iy z", 0.9), ("ah n", 0.9),
     ("d er", 0.9), ("dh ax", 0.5), ("s k er t", 1.5), ("sh iy", 0.9),
     ("k ey m", 1.3), ("r eh", 1.0), ("d iy", 0.8), ("t ax", 0.5),
     ("s ih n", 2.0)],
    [("hh ah", 1.3), ("n iy", 0.9), ("d r ih", 1.2), ("p ih n", 0.9),
     ("d aw n", 1.3), ("hh er", 0.8), ("th ay z", 1.5), ("l eh t", 0.9),
     ("dh ax", 0.5), ("g ey m z", 1.4), ("b ih", 0.8), ("g ih n", 2.0)],
    [("sh iy", 0.9), ("r ay d", 1.4), ("ih t", 0.6), ("l ay k", 1.2),
     ("ax", 0.5), ("d ih", 1.1), ("t r oy t", 1.4), ("p ih s", 1.1),
     ("t ax n", 0.9), ("ah p", 1.1), ("ae n d", 0.6), ("d aw n", 1.4),
     ("w ih n", 1.0), ("w ih n", 2.0)],
    [("ay", 1.0), ("jh ah s t", 1.3), ("k ow ch", 1.5), ("f r ah m", 0.8),
     ("dh ax", 0.5), ("th r ow n", 1.5), ("w ih dh", 0.7), ("ax", 0.4),
     ("d eh v", 1.0), ("ax", 0.6), ("l ih sh", 0.9), ("g r ih n", 2.0)],
    [("t w er k", 1.4), ("ao f", 1.1), ("ch ae m", 1.2), ("p iy", 0.7),
     ("ax n", 0.8), ("t w ih n", 1.3), ("ch iy k s", 1.5), ("ih n", 0.6),
     ("ax", 0.4), ("s eh", 1.0), ("sh ax n", 2.0)],
    [("eh v", 1.0), ("r iy", 0.8), ("b aw n s", 1.5), ("ih z", 0.6),
     ("ax", 0.4), ("b l eh s", 1.2), ("ih ng", 0.9), ("eh v", 1.0),
     ("r iy", 0.8), ("k l ae p", 1.5), ("ih z", 0.6), ("ax", 0.4),
     ("l eh s", 1.1), ("ax n", 2.0)],
    [("sh iy", 0.9), ("p uh t", 1.3), ("dh ae t", 0.8), ("p uh", 1.3),
     ("s iy", 0.9), ("aa n", 0.8), ("dh ax", 0.5), ("hh ae", 1.3),
     ("m er", 0.9), ("t ih l", 0.9), ("dh ax", 0.5), ("hh ae", 1.3),
     ("m er", 0.9), ("k ax n", 1.0), ("f eh s", 1.1), ("ih n", 2.0)],
    [("s ow l", 1.3), ("r ey", 1.4), ("d ow n t", 1.4), ("d uw", 1.1),
     ("s ao f t", 1.5), ("b oy", 1.3), ("ay", 0.9), ("d uw", 1.1),
     ("r ao", 1.5), ("n ow", 0.9), ("k w eh s", 1.1), ("ch ax n", 2.2)],
]

# VERSE 2 — ARI SPARKZ (Civet pitched down, base 50)
ARI = [
    [("d ih r", 1.2), ("b ao r n", 1.3), ("t ax", 0.6), ("b r ay t", 1.3),
     ("m ao r", 1.2), ("ay", 0.9), ("b r ao t", 1.4), ("dh ax", 0.5),
     ("f r iy k", 1.5), ("ih n", 0.6), ("dh ax", 0.5), ("r ay d", 2.0)],
    [("sh iy", 0.9), ("d ow n t", 1.4), ("t ao k", 1.4), ("ih n", 0.6),
     ("dh ax", 0.5), ("k l ah b", 1.5), ("sh iy", 0.9), ("l eh t", 1.0),
     ("hh er", 0.7), ("ae s", 1.5), ("s p iy k", 1.4), ("w ay d", 2.0)],
    [("b aw n s", 1.6), ("ih t", 0.7), ("aa n", 0.8), ("dh ax", 0.5),
     ("s p aa r k", 1.6), ("t ih l", 0.8), ("dh ax", 0.5),
     ("s p aa r k", 1.6), ("k ae ch", 1.4), ("f ay r", 2.2)],
    [("b uw", 1.3), ("t iy", 0.9), ("k l ae", 1.3), ("p ih n", 0.9),
     ("l ay k", 1.1), ("ax", 0.4), ("k w ay r", 1.5), ("ih n", 0.6),
     ("dh eh m", 0.8), ("f ih sh", 1.1), ("n eh t", 1.0), ("w ay r z", 2.0)],
    [("sh iy", 0.9), ("s eh d", 1.3), ("aa", 1.1), ("r iy", 1.1),
     ("g ow", 1.3), ("d iy p", 1.6), ("s ow", 0.8), ("ay", 0.8),
     ("d ah g", 1.4), ("ih n", 0.6), ("dh ax", 0.5), ("hh ah", 1.2),
     ("n iy", 0.8), ("p aa t", 2.0)],
    [("l ih k t", 1.4), ("ih t", 0.6), ("t ih l", 0.8), ("sh iy", 0.9),
     ("s k r iy m d", 1.6), ("dh eh n", 0.8), ("ay", 0.8), ("hh ih t", 1.3),
     ("dh ax", 0.5), ("m ah", 1.2), ("n iy", 0.8), ("s p aa t", 2.0)],
    [("hh ae", 1.3), ("m er", 0.9), ("ih n", 0.6), ("hh er", 0.7),
     ("hh ae n d", 1.4), ("ae n d", 0.6), ("sh iy", 0.9), ("s w ih ng", 1.5),
     ("ih t", 0.6), ("l ay k", 1.1), ("sh iy", 0.8), ("m iy n", 1.4),
     ("ih t", 2.0)],
    [("eh k s", 1.1), ("r ey", 1.2), ("t ih d", 0.9), ("ah n", 1.0),
     ("r ey", 1.2), ("t ih d", 0.9), ("m ah", 1.1), ("dh er", 0.7),
     ("f ah", 1.2), ("k er", 0.8), ("ay", 0.9), ("s iy n", 1.4),
     ("ih t", 2.0)],
    [("n ow", 1.2), ("k ah t", 1.5), ("n ow", 1.2), ("eh", 1.1),
     ("d ih t", 0.9), ("dh ih s", 1.0), ("dh ax", 0.5), ("d ih", 1.0),
     ("r eh k", 1.1), ("t er z", 0.9), ("f r iy k", 1.5), ("k ah t", 2.0)],
    [("sh iy", 0.9), ("s w aa", 1.2), ("l ow", 1.0), ("dh ax", 0.5),
     ("p r ay d", 1.5), ("ae n d", 0.6), ("sh iy", 0.9), ("b aw n s", 1.6),
     ("w ih dh", 0.7), ("hh er", 0.7), ("n iy z", 1.4), ("ah p", 2.0)],
    [("th r iy", 1.2), ("t uw", 1.2), ("z ih", 1.0), ("r ow", 1.0),
     ("k ey", 1.4), ("dh ae t s", 1.3), ("dh ax", 0.5), ("b ih t", 1.1),
     ("r ey t", 1.1), ("ah v", 0.6), ("l ah s t", 2.2)],
    [("aa", 1.2), ("r iy", 1.1), ("s p aa r k s", 1.6), ("s eh t", 1.2),
     ("ih t", 0.6), ("ao f", 1.2), ("ih n", 0.6), ("dh ax", 0.5),
     ("b aw n s", 1.6), ("w iy", 0.8), ("t r ah s t", 2.2)],
]

# FEATURE — QASPARR (Phascogale pitched down, base 48)
QAS = [
    [("k ax", 1.2), ("s p aa r", 1.4), ("dh ax", 0.5), ("ah n", 1.0),
     ("f r eh n d", 1.1), ("l iy", 0.9), ("g ow s t", 1.6), ("ay", 0.9),
     ("d ow n t", 1.3), ("n aa k", 1.4), ("ay", 0.8), ("w ao k", 1.4),
     ("th r uw", 2.0)],
    [("hh ah", 1.3), ("n iy", 0.9), ("aa n", 0.8), ("m ay", 0.9),
     ("hh ae", 1.3), ("m er", 0.9), ("ae n d", 0.6), ("dh ax", 0.5),
     ("hh ae", 1.3), ("m er", 0.9), ("s t ey", 1.4), ("t r uw", 2.0)],
    [("sh iy", 0.9), ("ax", 0.4), ("k w iy n", 1.5), ("ih n", 0.6),
     ("dh ax", 0.5), ("s t r iy t s", 1.5), ("b ah t", 0.8), ("ax", 0.4),
     ("f r iy k", 1.5), ("ih n", 0.6), ("m ay", 0.8), ("sh iy t s", 2.0)],
    [("m ey k", 1.2), ("hh er", 0.7), ("b aw n s", 1.6), ("aa n", 0.7),
     ("dh ax", 0.5), ("g ow s t", 1.6), ("t ih l", 0.7), ("dh ax", 0.5),
     ("g ow s t", 1.6), ("f iy l", 1.3), ("hh iy t", 2.2)],
    [("ay m", 1.2), ("dh ax", 0.5), ("l ih", 1.1), ("v ih ng", 1.0),
     ("m ae n", 1.5), ("b ey", 1.1), ("b iy", 0.9), ("n ow", 1.1),
     ("m ae s", 1.2), ("t er", 0.9), ("n ow", 1.1), ("l iy sh", 2.0)],
    [("sh iy", 0.9), ("b eh g", 1.4), ("f ao r", 0.7), ("dh ax", 0.5),
     ("hh ae", 1.3), ("m er", 0.9), ("l ay k", 1.1), ("ax", 0.4),
     ("s ih", 1.1), ("n er", 0.9), ("b eh g", 1.4), ("dh ax", 0.5),
     ("p r iy s t", 2.0)],
    [("ay", 0.9), ("g ih v", 1.2), ("hh er", 0.7), ("t ay", 1.2),
     ("t ax l", 0.9), ("t ax", 0.5), ("dh ax", 0.5), ("n ay t", 1.5),
     ("p ax", 1.0), ("z eh", 1.1), ("sh ax n", 1.0), ("ah v", 0.6),
     ("dh ax", 0.5), ("sh iy t s", 2.0)],
    [("ax", 0.8), ("s ay", 1.2), ("l ax m", 1.0), ("ih n", 0.6),
     ("m ay", 0.8), ("aa r m z", 1.5), ("w eh n", 0.7), ("dh ax", 0.5),
     ("b uw", 1.2), ("t iy", 0.9), ("n iy d", 1.3), ("p iy s", 2.0)],
    [("r ao", 1.4), ("d ao g", 1.5), ("d aa k", 1.2), ("t r ih n", 1.0),
     ("dh ih s", 1.0), ("dh ax", 0.5), ("ah n", 1.1), ("k ah t", 1.2),
     ("k r iy d", 2.2)],
    [("p l ae n t", 1.5), ("dh ax", 0.5), ("f l ae g", 1.2), ("p ow l", 1.1),
     ("d iy p", 1.6), ("dh ae t s", 1.2), ("dh ax", 0.5), ("k l ey m", 1.5),
     ("ae n d", 0.6), ("dh ax", 0.5), ("d iy d", 2.2)],
    [("n ay n", 1.2), ("t iy", 0.8), ("w ah n", 1.2), ("aa n", 0.7),
     ("hh er", 0.7), ("n ah m", 1.1), ("b er z", 0.9), ("l ih", 1.0),
     ("b er", 0.7), ("t iy", 0.9), ("d ih", 1.1), ("t r oy t", 1.3),
     ("s iy d", 2.0)],
    [("k ax", 1.2), ("s p aa r", 1.4), ("s ay n", 1.5), ("dh ax", 0.5),
     ("r ih", 1.0), ("s iy t", 1.2), ("eh v", 1.0), ("r iy", 0.8),
     ("t ay m", 1.4), ("sh iy", 0.8), ("ax", 0.7), ("g r iy d", 2.2)],
]

# VERSE 3 — SAGE ARCHER (Phascogale, base 57)
SAGE = [
    [("s ey jh", 1.4), ("aa r", 1.1), ("ch er", 0.9), ("t r ae", 1.1),
     ("v ax l", 0.9), ("s iy t", 1.4), ("ay", 0.9), ("t ey k", 1.3),
     ("dh ax", 0.5), ("sh ow", 1.4), ("aa n", 0.7), ("dh ax", 0.5),
     ("r ow d", 2.0)],
    [("eh v", 1.0), ("r iy", 0.8), ("s ih", 1.1), ("t iy", 0.9),
     ("g eh t", 1.2), ("dh ax", 0.5), ("b aw n s", 1.6), ("eh v", 1.0),
     ("r iy", 0.8), ("s t ey jh", 1.5), ("g eh t", 1.2), ("dh ax", 0.5),
     ("l ow d", 2.0)],
    [("m ay", 1.1), ("ae s", 1.5), ("ih z", 0.6), ("dh ax", 0.5),
     ("p ae s", 1.2), ("p ao r t", 1.2), ("s t ae m p", 1.5), ("ih t", 0.6),
     ("ae t", 0.7), ("dh ax", 0.5), ("d ao r", 2.2)],
    [("b aw n s", 1.6), ("ih t", 0.6), ("ih n", 0.6), ("dh ax", 0.5),
     ("v iy", 1.2), ("ay", 1.2), ("p iy", 1.2), ("b aw n s", 1.6),
     ("ih t", 0.6), ("aa n", 0.7), ("dh ax", 0.5), ("f l ao r", 2.2)],
    [("hh iy", 0.9), ("f ih l m", 1.4), ("ih t", 0.6), ("ih n", 0.6),
     ("hh ih z", 0.8), ("m ay n d", 1.5), ("k ao z", 0.9), ("dh ax", 0.5),
     ("b aa", 1.2), ("d iy", 0.9), ("t uw", 1.1), ("r eh r", 2.0)],
    [("hh ah", 1.3), ("n iy", 0.9), ("th ih k", 1.5), ("hh ae", 1.3),
     ("m er", 0.9), ("hh eh", 1.2), ("v iy", 0.9), ("hh ae n d z", 1.5),
     ("f uh l", 1.2), ("ah v", 0.6), ("m ay", 0.8), ("hh eh r", 2.0)],
    [("ay", 0.9), ("r ay d", 1.4), ("ih t", 0.6), ("r ih", 1.1),
     ("v er s", 1.2), ("w aa ch", 1.3), ("hh ih m", 0.8), ("s t eh r", 1.4),
     ("ae t", 0.7), ("dh ax", 0.5), ("k l ae p", 2.2)],
    [("s ey jh", 1.4), ("d ow n t", 1.4), ("ch ey s", 1.5), ("dh ax", 0.5),
     ("b ae g", 1.5), ("dh ax", 0.5), ("b ae g", 1.5), ("ch ey s", 1.5),
     ("dh ax", 0.5), ("l ae p", 2.2)],
    [("ah n", 1.1), ("k ah t", 1.2), ("ae n d", 0.6), ("ah n", 1.0),
     ("b aa", 1.1), ("dh er d", 1.0), ("ay m", 1.1), ("dh ax", 0.5),
     ("eh k s", 1.4), ("ih n", 0.6), ("dh ax", 0.5), ("r ey", 1.2),
     ("t ih d", 2.0)],
    [("eh v", 1.0), ("r iy", 0.8), ("b aw n s", 1.6), ("ax", 0.4),
     ("v ey", 1.1), ("k ey", 1.1), ("sh ax n", 1.0), ("ae n d", 0.6),
     ("hh iy", 0.8), ("g l ae d", 1.4), ("dh ae t", 0.7), ("hh iy", 0.7),
     ("w ey", 1.2), ("t ih d", 2.0)],
    [("t eh l", 1.2), ("dh ax", 0.5), ("d iy", 1.2), ("jh ey", 1.2),
     ("r ah n", 1.3), ("ih t", 0.6), ("b ae k", 1.4), ("t eh l", 1.2),
     ("dh ax", 0.5), ("k l ah b", 1.4), ("g eh t", 1.1), ("n ey", 1.2),
     ("k ih d", 2.0)],
    [("s ey jh", 1.4), ("aa r", 1.1), ("ch er", 0.9), ("th er d", 1.3),
     ("s iy t", 1.4), ("m ey k", 1.3), ("dh ax", 0.5), ("hh ow l", 1.2),
     ("er th", 1.4), ("sh ey k", 1.5), ("ih t", 2.2)],
]

# FEATURE — QVEEN BEE closing (Quoll, base 55)
QVEEN = [
    [("k w iy n", 1.6), ("b iy", 1.5), ("k r aw n", 1.5), ("s iy t", 1.4),
     ("hh ah", 1.3), ("n iy", 0.9), ("m ey d", 1.3), ("ah v", 0.6),
     ("g ow l d", 2.2)],
    [("ay", 0.9), ("d ow n t", 1.4), ("b aw n s", 1.6), ("f ao r", 0.7),
     ("ax", 0.4), ("b oy", 1.4), ("ay", 0.9), ("b aw n s", 1.6),
     ("k ao z", 0.9), ("ay m", 1.0), ("b ow l d", 2.2)],
    [("hh ae", 1.3), ("m er", 0.9), ("ih n", 0.6), ("hh ih z", 0.8),
     ("hh ae n d", 1.4), ("b ah t", 0.7), ("dh ax", 0.5), ("hh ah", 1.3),
     ("n iy", 0.9), ("r ah n", 1.3), ("dh ax", 0.5), ("sh ow", 2.0)],
    [("d r ih p", 1.5), ("s ow", 1.0), ("hh eh", 1.2), ("v iy", 0.9),
     ("m ey k", 1.3), ("ax", 0.4), ("g r ow n", 1.5), ("m ae n", 1.3),
     ("s l ow", 2.2)],
    [("hh iy", 0.9), ("iy t", 1.4), ("dh ax", 0.5), ("hh ah", 1.3),
     ("n iy", 0.9), ("aw t", 1.3), ("dh ax", 0.5), ("jh aa r", 1.5),
     ("l ay k", 1.1), ("ih t s", 0.8), ("k ax", 1.0), ("m y uw n", 1.1),
     ("y ax n", 2.0)],
    [("t ah ng", 1.5), ("g ey m", 1.5), ("hh ow", 1.2), ("l iy", 0.9),
     ("dh ae t s", 1.2), ("ax", 0.4), ("d ih", 1.1), ("t r oy t", 1.3),
     ("r iy", 1.0), ("y uw n", 1.1), ("y ax n", 2.0)],
    [("dh eh n", 0.9), ("ay", 0.9), ("b aw n s", 1.6), ("aa n", 0.7),
     ("dh ax", 0.5), ("th r ow n", 1.6), ("t ih l", 0.7), ("dh ax", 0.5),
     ("th r ow n", 1.6), ("k r ae k", 2.2)],
    [("k w iy n", 1.6), ("t ae k s", 1.5), ("p ey", 1.4), ("dh ax", 0.5),
     ("hh ah", 1.3), ("n iy", 0.9), ("ao r", 0.8), ("g eh t", 1.2),
     ("s eh n t", 1.3), ("b ae k", 2.2)],
    [("r ao", 1.5), ("ah n", 1.1), ("k ah t", 1.2), ("eh k s", 1.2),
     ("eh k s", 1.2), ("eh k s", 1.2), ("aa n", 0.8), ("dh ax", 0.5),
     ("m aa r", 1.2), ("k iy", 2.0)],
    [("b uw", 1.3), ("t iy", 0.9), ("b aw n s", 1.6), ("s ih m", 1.1),
     ("f ax", 0.8), ("n iy", 0.9), ("ih n", 0.6), ("dh ax", 0.5),
     ("k iy", 1.4), ("ah v", 0.6), ("jh iy", 2.2)],
    [("t eh l", 1.2), ("ax m", 0.8), ("k r aw n", 1.5), ("f ay r", 1.5),
     ("b er n d", 1.4), ("ih t", 0.6), ("ae n d", 0.6), ("dh ax", 0.5),
     ("k w iy n", 1.6), ("s t ae m p t", 1.4), ("f r iy", 2.2)],
    [("hh ah", 1.3), ("n iy", 0.9), ("aa n", 0.7), ("dh ax", 0.5),
     ("hh ae", 1.3), ("m er", 0.9), ("dh ae t s", 1.3), ("dh ax", 0.5),
     ("l ao", 1.5), ("dh ae t s", 1.2), ("m iy", 2.2)],
]

# OUTRO — whole crew chant (rendered on Quoll base 55 + Civet base 50)
OUTRO = [
    [("b aw n s", 1.6), ("ih t", 0.8), ("th r iy", 1.2), ("t uw", 1.2),
     ("z ih", 0.9), ("r ow", 1.1), ("b aw n s", 1.6), ("ih t", 0.8),
     ("r ao", 2.2)],
    [("hh ah", 1.4), ("n iy", 1.0), ("d r ih p", 1.7), ("hh ae", 1.4),
     ("m er", 1.0), ("l ao", 2.4)],
]

SECTIONS = [  # (id prefix, persona, speaker, chant base, lines)
    ("sol", "Sol Rey", "Civet", 55, SOL),
    ("ari", "Ari Sparkz", "Civet", 50, ARI),
    ("qas", "Qasparr", "Phascogale", 48, QAS),
    ("sage", "Sage Archer", "Phascogale", 57, SAGE),
    ("qveen", "Qveen Bee", "Quoll", 55, QVEEN),
]
PERSONA = {"Quoll": "Qveen Bee", "Phascogale": "Sage Archer"}


def verse_melody(base, idx, n_syl):
    """Run-1 chant cell, transposed: base, +3 head lift on even lines,
    +2 penultimate lift, line-final fall of -2 on odd lines."""
    notes = [base] * n_syl
    if idx % 2 == 0:
        notes[0] = base + 3
    if n_syl >= 3:
        notes[-2] = base + 2
    notes[-1] = base - 2 if idx % 2 == 1 else base
    return notes


def make_job(lid, persona, spk, syl):
    """syl: [(phones_str, midi, weight)] -> one render job dict."""
    tot = float(sum(w for _, _, w in syl))
    words = [("SP", LEAD_SP, None)]
    for phones, midi, w in syl:
        words.append((phones, SYL_S * w / tot, midi))
    words.append(("SP", TAIL_SP, None))
    tokens, langs, ph_midi, word_div = [], [], [], []
    word_dur, word_nom = [], []
    for phones, dur_s, midi in words:
        if phones == "SP":
            tokens.append(pid("SP")); langs.append(EN)
            ph_midi.append(0); word_div.append(1)
            ps = ["SP"]
        else:
            ps = phones.split()
            for p in ps:
                tokens.append(pid(p)); langs.append(EN)
            ph_midi.extend([midi] * len(ps))
            word_div.append(len(ps))
        word_nom.append(max(1, int(round(dur_s * FPS))))
        word_dur.append(max(1, int(round(dur_s * FPS * CAL))))
    return {"id": lid, "persona": persona, "spk": spk,
            "tokens": tokens, "langs": langs, "ph_midi": ph_midi,
            "word_div": word_div, "word_dur": word_dur,
            "handed_frames": int(sum(word_dur)),
            "nominal_frames": int(sum(word_nom)),
            "score_midi": [m for _, m, _ in syl]}


def build_jobs():
    jobs = []
    for i, line in enumerate(HOOK):
        syl = [(p, m, w) for p, m, w in line]
        for spk in HOOK_SPEAKERS[i]:
            jobs.append(make_job(f"hook{i+1}", PERSONA[spk], spk, syl))
    for prefix, persona, spk, base, lines in SECTIONS:
        for i, line in enumerate(lines):
            mel = verse_melody(base, i, len(line))
            syl = [(p, m, w) for (p, w), m in zip(line, mel)]
            jobs.append(make_job(f"{prefix}{i+1}", persona, spk, syl))
    for i, line in enumerate(OUTRO):
        for spk, base in (("Quoll", 55), ("Civet", 50)):
            mel = verse_melody(base, i, len(line))
            syl = [(p, m, w) for (p, w), m in zip(line, mel)]
            jobs.append(make_job(f"out{i+1}", "Whole crew", spk, syl))
    return jobs


def check_tokens():
    bad = set()
    for j in build_jobs():
        for t in j["tokens"]:
            if t < 0:
                bad.add(t)
    # pid() raises KeyError on unknown tokens during build_jobs itself;
    # reaching here means every token resolved.
    print(f"[check] {len(build_jobs())} jobs, all tokens resolved",
          flush=True)


opts = ort.SessionOptions()
opts.intra_op_num_threads = 4


def sess(path):
    return ort.InferenceSession(str(path), sess_options=opts,
                                providers=["CPUExecutionProvider"])


def main():
    if "--check" in sys.argv:
        check_tokens()
        return
    jobs = build_jobs()
    print(f"[score] {len(jobs)} line renders", flush=True)
    spk_emb = {s: np.fromfile(BANK / f"{s}.emb", dtype=np.float32
                              ).reshape(1, 1, 256)
               for s in ("Civet", "Quoll", "Phascogale")}

    # ---- Stage 1+2: duration model, all lines -------------------------
    s_ling = sess(BANK / "dsdur" / "linguistic.onnx")
    s_dur = sess(BANK / "dsdur" / "duration_lem_26v.dur.onnx")
    for j in jobs:
        tokens = np.array([j["tokens"]], dtype=np.int64)
        langs = np.array([j["langs"]], dtype=np.int64)
        enc, xmask = s_ling.run(None, {
            "tokens": tokens, "languages": langs,
            "word_div": np.array([j["word_div"]], dtype=np.int64),
            "word_dur": np.array([j["word_dur"]], dtype=np.int64)})
        spk_tok = np.repeat(spk_emb[j["spk"]], tokens.shape[1], axis=1)
        pred = s_dur.run(None, {
            "encoder_out": enc, "x_masks": xmask,
            "ph_midi": np.array([j["ph_midi"]], dtype=np.int64),
            "spk_embed": spk_tok})[0]
        frames = np.maximum(1, np.round(pred.reshape(-1)).astype(np.int64))
        j["frames"] = frames
        j["T"] = int(frames.sum())
        print(f"[dur] {j['id']}/{j['spk']}: {j['T']} frames "
              f"({j['T']/FPS:.2f}s) handed {j['handed_frames']} "
              f"nominal {j['nominal_frames']}", flush=True)
    del s_ling, s_dur; gc.collect()

    # ---- Stage 3: variance model, all lines ---------------------------
    s_ling = sess(BANK / "dsvariance" / "linguistic.onnx")
    s_var = sess(BANK / "dsvariance" / "pitch_variance_lem_25.variance.onnx")
    for j in jobs:
        tokens = np.array([j["tokens"]], dtype=np.int64)
        langs = np.array([j["langs"]], dtype=np.int64)
        frames = j["frames"]; T = j["T"]
        enc2, _ = s_ling.run(None, {"tokens": tokens, "languages": langs,
                                    "ph_dur": frames.reshape(1, -1)})
        midi_frames = np.repeat(np.array(j["ph_midi"], dtype=np.float32),
                                frames)
        nz = np.where(midi_frames > 0)[0]
        filled = midi_frames.copy(); last = midi_frames[nz[0]]
        for i in range(T):
            if filled[i] > 0:
                last = filled[i]
            else:
                filled[i] = last
        j["filled"] = filled
        j["f0"] = np.where(midi_frames > 0,
                           440.0 * 2 ** ((midi_frames - 69) / 12), 0.0)
        spk_fr = np.repeat(spk_emb[j["spk"]], T, axis=1)
        j["spk_fr"] = spk_fr
        retake = np.ones((1, T, 2), dtype=bool)
        zeros = np.zeros((1, T), dtype=np.float32)
        voicing, tension = s_var.run(None, {
            "encoder_out": enc2, "ph_dur": frames.reshape(1, -1),
            "pitch": filled.reshape(1, -1).astype(np.float32),
            "voicing": zeros, "tension": zeros, "retake": retake,
            "spk_embed": spk_fr, "steps": np.array(20, dtype=np.int64)})
        j["voicing"] = voicing.astype(np.float32)
        j["tension"] = tension.astype(np.float32)
        print(f"[var] {j['id']}/{j['spk']}: voicing mean "
              f"{voicing.mean():.2f} tension mean {tension.mean():.2f}",
              flush=True)
    del s_ling, s_var; gc.collect()

    # ---- Stage 4: acoustic model, all lines ---------------------------
    s_ac = sess(BANK / "acoustic_lem_25.onnx")
    for j in jobs:
        T = j["T"]
        mel = s_ac.run(None, {
            "tokens": np.array([j["tokens"]], dtype=np.int64),
            "languages": np.array([j["langs"]], dtype=np.int64),
            "durations": j["frames"].reshape(1, -1),
            "f0": j["f0"].reshape(1, -1).astype(np.float32),
            "voicing": j["voicing"], "tension": j["tension"],
            "gender": np.zeros((1, T), dtype=np.float32),
            "velocity": np.ones((1, T), dtype=np.float32),
            "spk_embed": j["spk_fr"],
            "depth": np.array(0.6, dtype=np.float32),
            "steps": np.array(30, dtype=np.int64)})[0]
        j["mel"] = mel
        print(f"[acoustic] {j['id']}/{j['spk']}: mel {mel.shape}",
              flush=True)
    del s_ac; gc.collect()

    # ---- Stage 5: vocoder, all lines ----------------------------------
    sys.path.insert(0, str(LAB / "DiffSinger"))
    import torch
    from modules.nsf_hifigan.models import load_model
    import soundfile as sf
    model, _h = load_model(VOC / "model.ckpt")
    model.eval()
    manifest = []
    for j in jobs:
        with torch.no_grad():
            c = torch.from_numpy(j["mel"]).transpose(1, 2)
            f0t = torch.from_numpy(
                j["f0"].reshape(1, -1).astype(np.float32))
            wav = model(c, f0t).view(-1).cpu().numpy()
        name = f"{j['id']}_{j['spk'].lower()}.wav"
        sf.write(LINES_DIR / name, wav, SR)
        manifest.append({"id": j["id"], "persona": j["persona"],
                         "speaker": j["spk"], "file": name,
                         "samples": int(len(wav)), "frames": j["T"],
                         "handed_frames": j["handed_frames"],
                         "nominal_frames": j["nominal_frames"],
                         "score_midi": j["score_midi"]})
        print(f"[vocoder] {name}: {len(wav)} samples", flush=True)
        del j["mel"], j["spk_fr"], j["voicing"], j["tension"]
        gc.collect()
    (RUN / "lines_manifest.json").write_text(json.dumps(manifest, indent=2))
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
