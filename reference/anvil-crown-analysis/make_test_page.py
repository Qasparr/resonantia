#!/usr/bin/env python3
# =====================================================================
# 93
#
# make_test_page.py — engraves ONE toolchain-proof page from the
# phase-1 analysis of "THE ANVIL AND CROWN": the hook unit's chord
# read plus the melody sketch's notes in that window, quantised.
#
# Date: VIII day of November, Dies Solis, Sol in Scorpio,
#       Anno V:xii e.n. (2026 e.v.)
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice).
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# MECHANISM:
#   1. Read melody-sketch.json + chords.csv (the machine outputs).
#   2. Take the hook window (bars 13-16 on the phase grid) and the
#      sketch notes inside it with confidence >= 0.45.
#   3. Quantise onsets and durations to the 8th-note grid at the
#      measured 69.8 BPM. THIS QUANTISATION IS EDITORIAL: the page is
#      a proof that the engraving toolchain works end to end, stamped
#      as such on its face — it is NOT a finished score, and the .ly
#      header says so where any reader will meet it first.
#   4. Emit hook-fragment.ly (LilyPond 2.26) with the caveats printed
#      on the page itself; the desk then renders the PDF.
# =====================================================================

import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE, BAR, BPM = 0.570, 3.438397, 69.8
EIGHTH = BAR / 8.0
WIN_BAR0 = 13                      # bars 13-16 (1-based)
N_BARS = 4
WIN_T0 = PHASE + (WIN_BAR0 - 1) * BAR
WIN_T1 = WIN_T0 + N_BARS * BAR
CONF_MIN = 0.45

NAMES = ["c", "cis", "d", "dis", "e", "f", "fis", "g", "gis", "a", "ais", "b"]


def ly_note(midi):
    name = NAMES[midi % 12]
    octv = midi // 12 - 4          # midi 60 -> c'
    return name + ("'" * octv if octv > 0 else "," * (-octv))


DUR = {1: "8", 2: "4", 3: "4.", 4: "2", 6: "2.", 8: "1"}


def decompose(slots):
    out = []
    for chunk in (8, 6, 4, 3, 2, 1):
        while slots >= chunk:
            out.append(chunk)
            slots -= chunk
    return out


def render_span(pitch, slots, start_slot):
    """Emit LilyPond tokens for one note or rest, respecting barlines.
    A span is split at barlines into power-of-two/dotted chunks; a
    pitched span's chunks are tied (tie AFTER every chunk but last)."""
    chunks = []
    remaining, cur = slots, start_slot
    while remaining > 0:
        take = min(remaining, 8 - (cur % 8))
        chunks += decompose(take)
        cur += take
        remaining -= take
    if pitch is None:
        return [f"r{DUR[c]}" for c in chunks]
    return [f"{ly_note(pitch)}{DUR[c]}" + ("~" if i < len(chunks) - 1 else "")
            for i, c in enumerate(chunks)]


sketch = json.load(open(os.path.join(HERE, "melody-sketch.json")))
notes = [n for n in sketch["notes"]
         if WIN_T0 <= n["onset_s"] < WIN_T1 and n["conf"] >= CONF_MIN]
dropped = [n for n in sketch["notes"]
           if WIN_T0 <= n["onset_s"] < WIN_T1 and n["conf"] < CONF_MIN]

# monophonic slot map: slot -> (pitch or None)
total_slots = N_BARS * 8
slots = [None] * total_slots
spans = []
for n in sorted(notes, key=lambda z: z["onset_s"]):
    s0 = int(round((n["onset_s"] - WIN_T0) / EIGHTH))
    ln = max(1, int(round(n["dur_s"] / EIGHTH)))
    s0 = min(s0, total_slots - 1)
    ln = min(ln, total_slots - s0)
    spans.append((s0, ln, n["midi"]))
spans.sort()
clean = []
last_end = 0
for s0, ln, midi in spans:
    if s0 < last_end:
        ln -= (last_end - s0)
        s0 = last_end
        if ln <= 0:
            continue
    clean.append((s0, ln, midi))
    last_end = s0 + ln

tokens = []
cur = 0
for s0, ln, midi in clean:
    if s0 > cur:
        tokens += render_span(None, s0 - cur, cur)
        cur = s0
    tokens += render_span(midi, ln, cur)
    cur += ln
if cur < total_slots:
    tokens += render_span(None, total_slots - cur, cur)

chords = {}
with open(os.path.join(HERE, "chords.csv")) as fh:
    for row in csv.DictReader(fh):
        chords[int(row["bar"])] = row["chord"]
bar_reads = [chords.get(WIN_BAR0 + i, "UNCLEAR") for i in range(N_BARS)]

ly = r"""\version "2.26.0"
\header {
  title = "THE ANVIL AND CROWN — Hook Fragment"
  subtitle = "TRANSCRIPTION-ANALYSIS · TOOLCHAIN PROOF — NOT A FINISHED SCORE"
  composer = "Johnathan 'Qasparr' Monroe — generated in Gemini (Lyria)"
  tagline = "Desk engraving proof · 2026-11-08 · audit against the audio before any use"
}
\paper { #(set-paper-size "letter") }
\score {
  <<
    \new ChordNames \chordmode { a1 a a a }
    \new Staff {
      \key a \major \time 4/4 \tempo 4 = 70
      """ + " ".join(tokens) + r"""
    }
  >>
  \layout { }
}
\markup \vspace #2
\markup \wordwrap {
  Caveats, printed on the page by design: measured tempo is 69.8 BPM
  (shown rounded to 70). Chord read: bars 15-16 are per-bar bench
  labels (A); bars 13-14 are UNCLEAR per bar in chords.csv and are
  shown as A on segment-level evidence only (hook unit, medium
  confidence). Melody: machine sketch notes (autocorrelation track,
  confidence >= 0.45) quantised editorially; the A-sharp/B cluster in
  bars 13-14 is flagged in FORM-MAP.md as probable harmony-partial
  tracking, NOT verified lead melody. """ + f"{len(dropped)} sketch notes below the confidence floor were omitted from this page and remain in melody-sketch.json." + r"""
}
"""
with open(os.path.join(HERE, "hook-fragment.ly"), "w") as fh:
    fh.write(ly)
print(f"window {WIN_T0:.2f}-{WIN_T1:.2f}s bars {WIN_BAR0}-{WIN_BAR0 + N_BARS - 1}"
      f" | per-bar reads {bar_reads} | notes engraved {len(clean)}"
      f" | below-floor omitted {len(dropped)}")

# 93 — Live, Love, and let Love, Live.
