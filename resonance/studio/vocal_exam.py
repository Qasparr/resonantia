#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — studio/vocal_exam.py — THE VOCAL EXAM, Phase 1:
# the benchmark-and-simulation harness for sung vocals. A fixed
# corpus of sung items with their sheets as ground truth, five
# judges that grade renders by measurement, and a predictor that
# states, from a sheet alone, what a perfect render would score.
#
# Epigraph: "Prove all things; hold fast that which is good."
# — 1 Thessalonians 5:21 (KJV), the house's standing text for
#   every instrument that claims to measure.
#
# 93.
# Date: 24 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
#   Hypothesis: that a singing engine improves the way a language
#     model improves — by sitting a FIXED exam, graded by
#     instruments instead of impressions, its failures naming the
#     parameter to adjust — and that the house's one historical
#     calibration (the DETROIT MUGETSU hook, 90.38% of asked
#     durations on run 1, 99.52% on run 2) is the primitive form
#     of that loop with a single judge, generalizable to five.
#   Method: a versioned corpus (studio/exam/corpus.json) whose
#     sheets are ground truth, with a declared held-out split
#     calibration may never tune on; judges that measure through
#     the house's sworn instruments only (the Fourier seat for
#     pitch, the pipeline's BS.1770 / true-peak scales for the
#     master law, the plug's own wav scale for durations); a
#     predictor that computes the perfect render's expectation
#     from the sheet alone; and a baseline run that scores the
#     two Mugetsu renders of record and writes its results
#     append-only (studio/exam/results.jsonl).
#   Observation: the duration judge, applied to the artifacts of
#     record, reproduces the recorded history from the audio
#     itself: the eight line WAVs of run 1 sum to 12.0512 s
#     against the sheet's 13.3333 s (90.38%), run 2's to
#     13.2702 s (99.52%) — the ledger's figures, re-measured, not
#     re-typed. The remaining judges' baseline readings stand in
#     studio/exam/results.jsonl and docs/VOCAL-EXAM.md, stated
#     with their unmeasurable counts beside them.
#   Result: this module and its corpus. Phase 1 scores what
#     exists; it sings nothing new. The loop that spends these
#     scores — sit, adjust, re-sit — is Phase 2's work, and the
#     founder's ear remains the final gate for "good": this exam
#     grades the measurable, and claims nothing beyond it.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""The Vocal Exam — benchmark and simulation harness for vocals.

DOCTRINE — WHAT THIS HARNESS IS, AND WHAT IT REFUSES TO BE:
  An exam is a fixed set of questions with a marking scheme.
  This one is for sung vocals: a corpus of items (sustained
  Divine Nine vowels, short phrases in English and Japanese,
  and the DETROIT MUGETSU hook as the house test piece), each
  carrying its sheet — notes, durations, phoneme and vowel
  targets — as ground truth. A render sits the exam; five
  judges grade it by measurement; the scores land in an
  append-only results file, so every engine and every version
  carries a comparable history. A held-out split is declared
  in the corpus: calibration may never tune on held-out items,
  so a method that merely memorizes the practice items is
  caught by the items it never saw — the train/test split of
  the language-model world, carried into the vocal road.

  What the exam refuses to be is a judge of GOOD. Pitch,
  duration, onset, vowel identity, and master-law compliance
  are measurable, and the exam grades exactly those. Whether
  a take is good remains the founder's ear, as it has stood
  over every vocal run of record. A judge that cannot measure
  honestly returns the state UNSUNG (no render exists) or
  UNMEASURABLE (a render exists but this measurement cannot
  be read from it) — a state, never a fabricated score.

MECHANISM — THE FIVE JUDGES:
  * durations: the house's historical law — realization =
    100 · Σrealized / Σasked over an item's segments, the very
    scale the Mugetsu calibration was struck on. It is NOT
    clamped at 100: run 2's longest line realized 103.1%, and
    the exam reports overshoot as plainly as undershoot.
  * pitch: per note, the Fourier seat's dominant frequency
    over the note's steady centre, read against the sheet's
    MIDI target in cents (1200·log2 of the ratio). Pitch is
    measured through studio/fourier.py — the sworn frequency
    instrument — never through a new ad-hoc transform.
  * onsets: an energy-envelope rise read against each
    expected onset in the assembled render. Where the
    preceding sound has not fallen below threshold — a line
    overhanging its bar line, as run 2's do — there is no gap
    to read an onset against, and the judge says UNMEASURABLE
    rather than inventing a placement.
  * vowels: a linear-predictive formant read (pre-emphasis,
    autocorrelation LPC, pole selection by frequency and
    bandwidth) over the steadiest window of the segment,
    compared in log-frequency (octave) distance against the
    seated Divine Nine targets carried in
    studio/diffsinger.py's STATIONS table — the one table of
    record. Limits, stated once and printed in every read:
    LPC reads the spectral envelope through the harmonic
    comb, so at high F0 the sampling of that envelope is
    sparse and the read coarsens; segments under ~60 ms and
    near-silent segments cannot carry two formants and are
    UNMEASURABLE; the canon's two glides (ΕΙ, ΟΥ) have no
    steady state and are refused as steady targets.
  * master law: the delivered file weighed on the house's
    own scales — integrated loudness and true peak by
    studio/pipeline.py's BS.1770 and oversampled scales, on
    the DECODED audio for MP3 (the house's decoded road, the
    one the run-2 gate was sealed on), bitrate by ffprobe's
    stream read. Laws: −14.0 ± 0.5 LUFS; decoded true peak
    ≤ −1.0 dBTP; bitrate exactly the sworn figure when a
    record swears one.

MECHANISM — THE PREDICTOR:
  predict(item) computes, from the sheet alone, the
  expectation a perfect render would meet: the note table
  with target frequencies, the total duration, the vowel
  targets in force, and the perfect scores (100.0% duration,
  0 cents, 0 ms, distance 0). It renders nothing and
  measures nothing; it is the simulation half of the
  harness — the expectation stated before the take exists.
"""

import json
import math
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from resonance.studio import diffsinger as _ds
from resonance.studio import fourier as _fourier
from resonance.studio import pipeline as _pipeline

__all__ = [
    "ExamError",
    "CORPUS_PATH",
    "RESULTS_PATH",
    "load_corpus",
    "corpus_items",
    "midi_hz",
    "item_notes",
    "predict",
    "judge_durations",
    "judge_pitch",
    "judge_onsets",
    "judge_vowel",
    "judge_masterlaw",
    "judge_language",
    "judge_coverage",
    "score_hook_run",
]

_HERE = Path(__file__).resolve().parent
CORPUS_PATH = _HERE / "exam" / "corpus.json"
RESULTS_PATH = _HERE / "exam" / "results.jsonl"

# The master law, as the house's own gate states it (the run-2
# master gate of record: -14.0 +/- 0.5 LUFS; <= -1.0 dBTP).
MASTER_LUFS = -14.0
MASTER_LUFS_TOL = 0.5
MASTER_CEILING_DBTP = -1.0

# Vowel-judge tolerances, stated once (see the docstring):
# a read matches its target when the target is the nearest
# station and the log-frequency distance is within this.
VOWEL_MATCH_OCTAVES = 0.35
_VOWEL_MIN_SEGMENT_S = 0.06


class ExamError(ValueError):
    """A refusal by name from the Vocal Exam harness."""


# ---------------------------------------------------------------------
# The corpus: fixed items, sheets as ground truth.
# ---------------------------------------------------------------------

def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) \
        and math.isfinite(float(x))


def _check_note(owner, note):
    if not isinstance(note.get("midi"), int) \
            or not 0 <= note["midi"] <= 127:
        raise ExamError(f"{owner}: midi must be an int in "
                        f"[0, 127]; got {note.get('midi')!r}")
    if not _is_number(note.get("dur_s")) or note["dur_s"] <= 0:
        raise ExamError(f"{owner}: dur_s must be a positive "
                        f"number; got {note.get('dur_s')!r}")


def load_corpus(path=None):
    """Load and validate the exam corpus; return it as a dict.

    MECHANISM: the corpus is data, versioned in its own file;
    validation is structural — a stamped version, unique item
    ids, a declared held-out split with at least one item on
    it, and every sheet entry carrying a lawful MIDI note and
    a positive duration. A corpus that fails validation is
    refused by name: an exam with a bent sheet grades nothing.
    """
    path = Path(path) if path is not None else CORPUS_PATH
    try:
        corpus = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ExamError(f"corpus: no file at {path}")
    except json.JSONDecodeError as exc:
        raise ExamError(f"corpus: {path} does not parse: {exc}")
    if not isinstance(corpus.get("version"), int):
        raise ExamError("corpus: 'version' must be a stamped int; "
                        f"got {corpus.get('version')!r}")
    items = corpus.get("items")
    if not isinstance(items, list) or not items:
        raise ExamError("corpus: 'items' must be a non-empty list")
    seen = set()
    held_out = 0
    for item in items:
        iid = item.get("id")
        if not iid or iid in seen:
            raise ExamError(f"corpus: item id missing or "
                            f"duplicated: {iid!r}")
        seen.add(iid)
        if item.get("held_out"):
            held_out += 1
        if item.get("kind") == "hook":
            lines = item.get("lines")
            if not lines:
                raise ExamError(f"corpus: hook item {iid} has "
                                f"no lines")
            for line in lines:
                for note in line.get("notes", []):
                    _check_note(f"corpus {iid}/{line.get('id')}",
                                note)
                for ph in line.get("phonemes", []):
                    if not _is_number(ph.get("dur_s")) \
                            or ph["dur_s"] <= 0:
                        raise ExamError(
                            f"corpus {iid}: phoneme dur_s must "
                            f"be positive; got {ph.get('dur_s')!r}")
        else:
            for seg in item.get("segments", []):
                _check_note(f"corpus {iid}", seg)
    if held_out == 0:
        raise ExamError("corpus: the held-out split is empty — "
                        "an exam calibration could memorize is "
                        "not an exam")
    return corpus


def corpus_items(corpus):
    """The corpus's items as an {id: item} mapping."""
    return {item["id"]: item for item in corpus["items"]}


# ---------------------------------------------------------------------
# The sheet, flattened: notes on one timeline.
# ---------------------------------------------------------------------

def midi_hz(midi):
    """The equal-tempered frequency of a MIDI note, in Hz."""
    return 440.0 * 2.0 ** ((float(midi) - 69.0) / 12.0)


def item_notes(item):
    """Flatten an item's sheet to notes on one timeline.

    MECHANISM: returns [{midi, hz, start_s, dur_s}] in sheet
    order — for a hook item, its lines laid end to end on the
    asked grid; for segment items, the segments in order.
    Pure computation from the sheet; the same flattening the
    predictor and the pitch judge's expectation both read.
    """
    notes = []
    t = 0.0
    if item.get("kind") == "hook":
        raw = [n for line in item["lines"] for n in line["notes"]]
    else:
        raw = item.get("segments", [])
    for n in raw:
        notes.append({"midi": n["midi"], "hz": midi_hz(n["midi"]),
                      "start_s": t, "dur_s": float(n["dur_s"])})
        t += float(n["dur_s"])
    return notes


def predict(item, corpus_version=None):
    """The simulation: a perfect render's expected measurements.

    MECHANISM: from the sheet alone — the note table with
    target frequencies, the total asked duration, the vowel
    targets in force (the seated STATIONS coordinates), and
    the perfect scores each judge would return for a render
    that met the sheet exactly. Nothing is rendered and
    nothing is measured; this is the expectation a real
    render is graded against.
    """
    notes = item_notes(item)
    stations = []
    if item.get("kind") == "hook":
        for line in item["lines"]:
            for ph in line["phonemes"]:
                if ph.get("station"):
                    stations.append(ph["station"])
    else:
        for seg in item.get("segments", []):
            if seg.get("station"):
                stations.append(seg["station"])
            for ph in seg.get("phonemes", []):
                if ph.get("station"):
                    stations.append(ph["station"])
    targets = {}
    for st in stations:
        info = _ds.STATIONS.get(st)
        if info and info.get("formants") is not None:
            targets[st] = {"f1_hz": info["formants"][0],
                           "f2_hz": info["formants"][1]}
    return {
        "item_id": item["id"],
        "corpus_version": corpus_version,
        "held_out": bool(item.get("held_out")),
        "total_dur_s": round(sum(n["dur_s"] for n in notes), 6),
        "notes": [{"midi": n["midi"], "hz": round(n["hz"], 4),
                   "start_s": round(n["start_s"], 6),
                   "dur_s": n["dur_s"]} for n in notes],
        "vowel_targets": targets,
        "expected_perfect": {
            "duration_accuracy_pct": 100.0,
            "pitch_abs_cents": 0.0,
            "onset_abs_ms": 0.0,
            "vowel_distance_octaves": 0.0,
        },
    }


# ---------------------------------------------------------------------
# Judge 1 — durations, on the house's historical scale.
# ---------------------------------------------------------------------

def judge_durations(asked_s, realized_s):
    """Duration accuracy of a render against its sheet.

    MECHANISM: the house's realization law, the scale both
    Mugetsu runs were struck on — accuracy_pct = 100 ·
    Σrealized / Σasked over the item's segments, reported
    unclamped (overshoot past 100 is a reading, not an
    error). Per-segment ratios ride along so a failure names
    its segment. Refusals by name: mismatched segment counts,
    non-positive asked durations, negative realized ones.
    """
    asked = [float(a) for a in asked_s]
    realized = [float(r) for r in realized_s]
    if len(asked) != len(realized):
        raise ExamError(f"durations: {len(asked)} asked segments "
                        f"against {len(realized)} realized — the "
                        f"sheet and the render disagree about "
                        f"the item's shape")
    if not asked:
        raise ExamError("durations: no segments to judge")
    if any(a <= 0 for a in asked):
        raise ExamError("durations: asked durations must be "
                        "positive")
    if any(r < 0 for r in realized):
        raise ExamError("durations: realized durations must "
                        "not be negative")
    total_a = sum(asked)
    total_r = sum(realized)
    return {
        "judge": "durations",
        "accuracy_pct": round(100.0 * total_r / total_a, 4),
        "asked_total_s": round(total_a, 6),
        "realized_total_s": round(total_r, 6),
        "per_segment": [
            {"asked_s": round(a, 6), "realized_s": round(r, 6),
             "ratio_pct": round(100.0 * r / a, 4)}
            for a, r in zip(asked, realized)],
    }


# ---------------------------------------------------------------------
# Judge 2 — pitch, through the sworn Fourier seat.
# ---------------------------------------------------------------------

def _mono(samples):
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim == 2:
        x = x.mean(axis=0) if x.shape[0] <= x.shape[1] \
            else x.mean(axis=1)
    return x


def judge_pitch(samples, sample_rate, notes):
    """Pitch error per note, in cents, via the Fourier seat.

    MECHANISM: each note is read over its steady centre (the
    middle 50% of its span, transitions excluded) by
    fourier.dominant_frequency — the sworn instrument — and
    compared with the sheet's target as 1200·log2(measured /
    target). A note whose centre is shorter than 30 ms
    cannot carry a sworn read at song pitches and returns
    UNMEASURABLE, counted, never interpolated. Aggregates:
    median absolute cents (the robust centre), mean signed
    cents (the bias), worst absolute cents.
    """
    x = _mono(samples)
    sr = float(sample_rate)
    per_note = []
    measured = []
    for note in notes:
        start = float(note["start_s"]) + 0.25 * float(note["dur_s"])
        dur = 0.5 * float(note["dur_s"])
        i0 = int(round(start * sr))
        i1 = int(round((start + dur) * sr))
        target = midi_hz(note["midi"])
        if dur < 0.03 or i1 - i0 < 256 or i0 < 0 or i1 > x.size:
            per_note.append({"midi": note["midi"],
                             "target_hz": round(target, 4),
                             "state": "UNMEASURABLE",
                             "reason": "steady centre under 30 ms "
                                       "or outside the render"})
            continue
        hz, _mag = _fourier.dominant_frequency(x[i0:i1], sr)
        cents = 1200.0 * math.log2(hz / target)
        measured.append(cents)
        per_note.append({"midi": note["midi"],
                         "target_hz": round(target, 4),
                         "measured_hz": round(hz, 4),
                         "cents": round(cents, 2)})
    out = {"judge": "pitch", "per_note": per_note,
           "n_measured": len(measured),
           "n_unmeasurable": len(per_note) - len(measured)}
    if measured:
        abs_c = sorted(abs(c) for c in measured)
        out["median_abs_cents"] = round(abs_c[len(abs_c) // 2], 2)
        out["mean_cents"] = round(sum(measured) / len(measured), 2)
        out["max_abs_cents"] = round(abs_c[-1], 2)
    return out


# ---------------------------------------------------------------------
# Judge 3 — onsets, read off the energy envelope.
# ---------------------------------------------------------------------

def judge_onsets(samples, sample_rate, expected_s, search_s=0.35):
    """Onset timing error per expected onset, in milliseconds.

    MECHANISM: a 5 ms RMS envelope; the threshold stands at
    max(4× the envelope's quiet decile, 3% of its peak) — the
    decile, not the median, because on dense program the
    median window is itself sung. An
    onset is the first threshold crossing inside
    [expected − 50 ms, expected + search_s] that holds for
    three consecutive windows. Two honest refusals, returned
    as UNMEASURABLE states: the envelope already stands above
    threshold at the window's head (the preceding sound has
    not fallen — an overhang leaves no gap to read against),
    and no crossing inside the window at all.
    """
    x = _mono(samples)
    sr = float(sample_rate)
    win = max(1, int(round(0.005 * sr)))
    n_win = x.size // win
    if n_win < 8:
        raise ExamError("onsets: render too short to carry an "
                        "envelope")
    env = np.sqrt(np.mean(
        x[:n_win * win].reshape(n_win, win) ** 2, axis=1))
    # The floor is the envelope's quiet decile, not its median:
    # on dense program the median window is itself sung, and a
    # threshold built on it stands above the very gaps the
    # judge exists to read (the baseline's first strike read
    # 1 of 8 onsets on run 1 for exactly this reason — the
    # coordinate is recorded in docs/VOCAL-EXAM.md).
    floor = float(np.percentile(env, 10))
    peak = float(np.max(env))
    threshold = max(4.0 * floor, 0.03 * peak)
    hop_s = win / sr
    results = []
    measured = []
    for t0 in expected_s:
        t0 = float(t0)
        w0 = max(0, int((t0 - 0.05) / hop_s))
        w1 = min(n_win, int((t0 + float(search_s)) / hop_s) + 1)
        if w0 >= w1:
            results.append({"expected_s": round(t0, 6),
                            "state": "UNMEASURABLE",
                            "reason": "window outside the render"})
            continue
        if env[w0] > threshold:
            results.append({"expected_s": round(t0, 6),
                            "state": "UNMEASURABLE",
                            "reason": "preceding sound still above "
                                      "threshold — no gap to read "
                                      "an onset against"})
            continue
        found = None
        for w in range(w0, w1 - 2):
            if env[w] > threshold and env[w + 1] > threshold \
                    and env[w + 2] > threshold:
                found = w * hop_s
                break
        if found is None:
            results.append({"expected_s": round(t0, 6),
                            "state": "UNMEASURABLE",
                            "reason": "no threshold crossing inside "
                                      "the search window"})
            continue
        err_ms = (found - t0) * 1000.0
        measured.append(err_ms)
        results.append({"expected_s": round(t0, 6),
                        "detected_s": round(found, 6),
                        "error_ms": round(err_ms, 2)})
    out = {"judge": "onsets", "per_onset": results,
           "n_measured": len(measured),
           "n_unmeasurable": len(results) - len(measured),
           "threshold": round(threshold, 6)}
    if measured:
        out["mean_error_ms"] = round(
            sum(measured) / len(measured), 2)
        out["max_abs_error_ms"] = round(
            max(abs(e) for e in measured), 2)
    return out


# ---------------------------------------------------------------------
# Judge 4 — vowel identity, by an LPC formant read.
# ---------------------------------------------------------------------

def _levinson(r, order):
    """Levinson–Durbin: LPC coefficients from autocorrelation.

    MECHANISM: the textbook recursion, with the standard
    numerical hygiene stated in the open: reflection
    coefficients are clamped to |k| <= 0.9999, because a
    perfectly periodic frame (a synthetic vowel is one) can
    drive the unguarded recursion onto the unit circle and
    out of the stable region entirely — the clamp keeps the
    filter stable without moving any lawful pole's reading
    by more than rounding.
    """
    a = np.zeros(order + 1)
    a[0] = 1.0
    e = r[0]
    if e <= 0:
        return None
    for i in range(1, order + 1):
        acc = r[i] + sum(a[j] * r[i - j] for j in range(1, i))
        k = max(-0.9999, min(0.9999, -acc / e))
        prev = a.copy()
        for j in range(1, i):
            a[j] = prev[j] + k * prev[i - j]
        a[i] = k
        e *= (1.0 - k * k)
        if e <= 0:
            return None
    return a


def _lpc_formants(segment, sr):
    """(F1, F2) in Hz from one steady segment, or None.

    MECHANISM: pre-emphasis (0.97), the steadiest 120 ms by
    energy, Hann window, autocorrelation LPC (order 20 at
    44.1 kHz class rates, 16 below — order 14 merges the
    canon's close formant pairs, measured on the bench),
    poles kept when their
    frequency sits in [150, Nyquist−500] Hz and their
    bandwidth under 450 Hz (VV's seated pole measures
    ~410 Hz wide on a planted synthetic — the ceiling was
    raised from 350 on that measurement, recorded here);
    F1 is the first pole in
    [200, 1100], F2 the first above it in [600, 2800]
    (the floor is 600, not 700, because VV's seated F2 IS
    700 and a lawful read of it lands at ~646).
    Fewer than two lawful poles is not a reading.
    """
    x = np.asarray(segment, dtype=np.float64)
    if x.size < int(_VOWEL_MIN_SEGMENT_S * sr):
        return None
    if float(np.sqrt(np.mean(x ** 2))) < 10 ** (-45.0 / 20.0):
        return None  # near-silent: no envelope to read
    win_n = min(x.size, int(round(0.120 * sr)))
    hop = max(1, win_n // 2)
    best, best_e = 0, -1.0
    for s in range(0, x.size - win_n + 1, hop):
        e = float(np.sum(x[s:s + win_n] ** 2))
        if e > best_e:
            best, best_e = s, e
    frame = x[best:best + win_n].copy()
    frame[1:] -= 0.97 * frame[:-1]
    frame *= np.hanning(frame.size)
    # Order 20 at song rates: order 14 merges the canon's
    # close F1/F2 pairs (Α 730/1090, Ο 570/840) into a single
    # pole — measured on the bench, both pairs split cleanly
    # at 20 (711/1077 and 553/845 against their targets).
    order = 20 if sr >= 40000 else 16
    r = np.correlate(frame, frame, mode="full")[frame.size - 1:]
    r = r[:order + 1].copy()
    if r[0] <= 0:
        return None
    r[0] *= 1.0001  # a whisper of white noise: the standard
    # regularization against a singular autocorrelation (a
    # perfectly periodic frame is exactly that)
    a = _levinson(r, order)
    if a is None:
        return None
    roots = np.roots(a)
    poles = []
    for root in roots:
        if root.imag <= 0:
            continue
        freq = math.atan2(root.imag, root.real) * sr / (2 * math.pi)
        bw = -math.log(abs(root)) * sr / math.pi
        if 150.0 <= freq <= sr / 2 - 500.0 and bw < 450.0:
            poles.append((freq, bw))
    poles.sort()
    f1 = next((f for f, _ in poles if 200.0 <= f <= 1100.0), None)
    f2 = next((f for f, _ in poles
               if f1 is not None and f > f1 and 600.0 <= f <= 2800.0),
              None)
    if f1 is None or f2 is None:
        return None
    return f1, f2


def _octave_distance(f1, f2, t1, t2):
    return math.sqrt(math.log2(f1 / t1) ** 2
                     + math.log2(f2 / t2) ** 2)


def judge_vowel(samples, sample_rate, target_station):
    """Vowel identity: measured formants vs the seated target.

    MECHANISM: _lpc_formants reads (F1, F2); the read is
    placed against every steady station of the canon (the
    STATIONS table of record in studio/diffsinger.py) by
    octave distance; the verdict is MATCH when the target is
    the nearest station within VOWEL_MATCH_OCTAVES, else the
    nearest station and the distance are reported as the
    reading — coordinates, not a verdict blob. UNMEASURABLE
    states: glide targets (no steady state exists to read),
    short or near-silent segments, and segments whose poles
    do not resolve into two formants. The read's known limit
    rides in every result: at F0 above ~300 Hz the harmonic
    comb samples the envelope sparsely and the read coarsens
    (flagged high_f0).
    """
    info = _ds.STATIONS.get(target_station)
    if info is None:
        raise ExamError(f"vowel: {target_station!r} is not a "
                        f"station of the Nine")
    if info.get("formants") is None:
        return {"judge": "vowel", "target_station": target_station,
                "state": "UNMEASURABLE",
                "reason": "glide station: no steady state exists "
                          "to read — grade its onset segment "
                          "against the onset station"}
    x = _mono(samples)
    sr = float(sample_rate)
    f0_pre, _ = _fourier.dominant_frequency(x, sr)
    if f0_pre > 350.0 and x.size < 0.15 * sr:
        return {"judge": "vowel", "target_station": target_station,
                "state": "UNMEASURABLE",
                "reason": f"soprano comb: F0 ~{f0_pre:.0f} Hz "
                          f"samples the envelope too sparsely "
                          f"for a sworn two-formant read on a "
                          f"{1000.0 * x.size / sr:.0f} ms slice"}
    read = _lpc_formants(x, sr)
    if read is None:
        return {"judge": "vowel", "target_station": target_station,
                "state": "UNMEASURABLE",
                "reason": "segment too short, near-silent, or "
                          "its poles do not resolve into two "
                          "formants"}
    f1, f2 = read
    distances = {}
    for st, st_info in _ds.STATIONS.items():
        if st_info.get("formants") is None:
            continue
        t1, t2 = st_info["formants"]
        distances[st] = _octave_distance(f1, f2, t1, t2)
    nearest = min(distances, key=distances.get)
    f0, _ = _fourier.dominant_frequency(x, sr)
    return {
        "judge": "vowel",
        "target_station": target_station,
        "measured_f1_hz": round(f1, 1),
        "measured_f2_hz": round(f2, 1),
        "target_f1_hz": info["formants"][0],
        "target_f2_hz": info["formants"][1],
        "distance_octaves": round(distances[target_station], 4),
        "nearest_station": nearest,
        "nearest_distance_octaves": round(distances[nearest], 4),
        "match": bool(nearest == target_station
                      and distances[target_station]
                      <= VOWEL_MATCH_OCTAVES),
        "f0_hz": round(f0, 1),
        "high_f0": bool(f0 > 300.0),
    }


# ---------------------------------------------------------------------
# Judge 5 — the master law, on the house's own scales.
# ---------------------------------------------------------------------

def _read_wav(path):
    """WAV samples AS DELIVERED (channels preserved) + rate.

    MECHANISM: the master law weighs the delivered signal —
    the pipeline's loudness scale sums channel energies, so a
    stereo master averaged to mono before weighing reads
    ~3 dB light (the baseline's first strike read −17.01
    LUFS against the gate's sealed −14.0 for exactly this
    reason; the coordinate stands in docs/VOCAL-EXAM.md).
    The pitch/onset/vowel judges, which read a vocal line,
    take _read_wav_mono instead.
    """
    return _pipeline.read_wav_pcm(path)


def _read_wav_mono(path):
    data, sr = _pipeline.read_wav_pcm(path)
    return _mono(data), sr


def judge_masterlaw(path, sworn_bps=None):
    """Master-law compliance of a delivered audio file.

    MECHANISM: loudness and true peak are weighed by
    studio/pipeline.py's own scales — measure_loudness_lufs
    (the 48 kHz BS.1770 set; a file at another rate reads
    UNMEASURABLE on the loudness line rather than being
    mis-weighed) and true_peak_dbtp. An MP3 is first decoded
    to PCM by ffmpeg and weighed decoded — the house's
    decoded road — and its bitrate is ffprobe's stream read.
    Laws: integrated loudness −14.0 ± 0.5 LUFS; decoded true
    peak ≤ −1.0 dBTP; bitrate exactly sworn_bps when a
    record swears one (None = not sworn, reported, not
    judged).
    """
    path = Path(path)
    if not path.exists():
        raise ExamError(f"masterlaw: no file at {path}")
    suffix = path.suffix.lower()
    bitrate = None
    if suffix == ".mp3":
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=bit_rate", "-of",
             "json", str(path)],
            capture_output=True, text=True)
        try:
            bitrate = int(json.loads(
                probe.stdout)["streams"][0]["bit_rate"])
        except (ValueError, KeyError, IndexError):
            raise ExamError(f"masterlaw: ffprobe cannot read a "
                            f"bitrate from {path}")
        with tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            subprocess.run(
                ["ffmpeg", "-v", "error", "-y", "-i", str(path),
                 "-ar", "48000", "-c:a", "pcm_s24le", tmp_path],
                check=True, capture_output=True)
            samples, sr = _read_wav(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    elif suffix == ".wav":
        samples, sr = _read_wav(path)
    else:
        raise ExamError(f"masterlaw: {suffix} is not a delivered "
                        f"audio form this judge weighs")
    checks = []
    if sr == 48000:
        lufs = _pipeline.measure_loudness_lufs(samples, sr)
        checks.append({
            "check": "integrated loudness", "value": round(lufs, 2),
            "unit": "LUFS", "law": f"{MASTER_LUFS} +/- "
            f"{MASTER_LUFS_TOL} LUFS",
            "ok": bool(abs(lufs - MASTER_LUFS) <= MASTER_LUFS_TOL)})
    else:
        checks.append({
            "check": "integrated loudness", "state": "UNMEASURABLE",
            "reason": f"the pipeline's LUFS scale carries the "
                      f"48 kHz coefficient set; this file is "
                      f"{sr} Hz", "law": f"{MASTER_LUFS} +/- "
                      f"{MASTER_LUFS_TOL} LUFS", "ok": None})
    dbtp = _pipeline.true_peak_dbtp(samples, sr)
    checks.append({
        "check": "decoded true peak", "value": round(dbtp, 2),
        "unit": "dBTP", "law": f"<= {MASTER_CEILING_DBTP} dBTP",
        "ok": bool(dbtp <= MASTER_CEILING_DBTP)})
    if sworn_bps is not None:
        checks.append({
            "check": "bitrate (sworn)", "value": bitrate,
            "unit": "bps", "law": f"exactly {sworn_bps} bps",
            "ok": bool(bitrate == sworn_bps)})
    else:
        checks.append({
            "check": "bitrate", "value": bitrate, "unit": "bps",
            "law": "not sworn for this file", "ok": None})
    judged = [c["ok"] for c in checks if c["ok"] is not None]
    return {"judge": "masterlaw", "path": str(path),
            "sample_rate_hz": sr, "checks": checks,
            "compliant": bool(judged) and all(judged)}


# ---------------------------------------------------------------------
# Judges 6 and 7 — language and coverage (the detection seat,
# seated 24 November 2026; additive: Judges 1–5 keep their
# verdict semantics exactly).
# ---------------------------------------------------------------------

def judge_language(path, expected_lang=None):
    """Language identity: what language the render audibly is.

    MECHANISM: the detection seat's dedicated identification
    pass (studio/detect.py — whisper.cpp, ggml-base, offline)
    reads the file and returns its language and the model's
    own probability. Against expected_lang (the corpus item's
    lang field, when the caller hands one) the verdict is
    match True/False; without an expectation, match is None
    and the read stands as a coordinate. A seat that cannot
    run — binary or model absent — returns UNMEASURABLE with
    the reason, never a guessed language: this judge exists
    because the founder's ear once had to carry this question
    alone ("i heard a couple Japanese words in it"); the
    exam can now state the read beside the ear — for the
    record, the Mugetsu hook of record reads ja, p = 0.8241.
    """
    from resonance.studio import detect as _detect
    try:
        read = _detect.detect_language(path)
    except _detect.DetectError as e:
        return {"judge": "language", "state": "UNMEASURABLE",
                "reason": str(e), "expected": expected_lang}
    return {"judge": "language",
            "detected": read["language"],
            "probability": read["probability"],
            "expected": expected_lang,
            "match": (read["language"] == expected_lang)
            if expected_lang else None,
            "engine": read["engine"], "model": read["model"]}


def judge_coverage(path):
    """Speech coverage: where the voice is, and where it is not.

    MECHANISM: the detection seat's voice_segments (Silero
    VAD when seated, the measured energy VAD otherwise — the
    serving engine is named in the return) weighs speech
    seconds against the file's duration. The verdict is the
    coverage fraction with its coordinates (segment count,
    longest silence): a render that was asked to sing for
    13.3 s and is silent for 9 of them is caught here in
    numbers, not impressions. No pass/fail line is drawn by
    this judge — coverage is a coordinate the loop reads,
    like the onset judge's gaps.
    """
    from resonance.studio import detect as _detect
    try:
        read = _detect.voice_segments(path)
    except _detect.DetectError as e:
        return {"judge": "coverage", "state": "UNMEASURABLE",
                "reason": str(e)}
    return {"judge": "coverage", "engine": read["engine"],
            "coverage": read["coverage"],
            "speech_s": read["speech_s"],
            "duration_s": read["duration_s"],
            "n_segments": len(read["segments"]),
            "longest_silence_s": read["longest_silence_s"],
            "segments": read["segments"]}


# ---------------------------------------------------------------------
# The baseline road: score a Mugetsu engine run of record.
# ---------------------------------------------------------------------

def score_hook_run(run_dir, corpus, engine_label):
    """Score one Mugetsu hook run against the corpus sheet.

    MECHANISM: the asked side is the corpus hook item (the
    sheet both runs were sung from). Durations: per-line
    realized durations weighed by the plug's own scale
    (diffsinger.measure_wav over lines/*.wav) — the road the
    recorded history was struck on. Pitch and onsets: read
    off the assembled render, note and phoneme timelines
    laid by proportional mapping of the asked/realized .ds
    grids onto the measured line durations (the within-line
    split is proportional — the seam the plug's own
    seat_durations already names). Vowels: every seated
    vowel phoneme of 55 ms or more is read at its centre by
    judge_vowel and aggregated per station. Returns the
    exam record for the run; writes nothing.
    """
    run_dir = Path(run_dir)
    item = corpus_items(corpus)["mugetsu-hook"]
    asked = json.loads((run_dir / "sequence.ds").read_text())
    realized = json.loads(
        (run_dir / "sequence-realized.ds").read_text())
    asked_lines = [line["asked_dur_s"] for line in item["lines"]]
    realized_lines = []
    for line in item["lines"]:
        m = _ds.measure_wav(run_dir / "lines" / f"{line['id']}.wav")
        realized_lines.append(m["duration_s"])
    durations = judge_durations(asked_lines, realized_lines)

    samples, sr = _read_wav_mono(run_dir / "mugetsu-hook.wav")
    offsets = [float(e["offset"]) for e in asked]
    notes, vowel_reads = [], {}
    for li, line in enumerate(item["lines"]):
        line_asked = asked_lines[li]
        scale = realized_lines[li] / line_asked
        t = 0.0
        for note in line["notes"]:
            notes.append({"midi": note["midi"],
                          "start_s": offsets[li] + t * scale,
                          "dur_s": note["dur_s"] * scale})
            t += note["dur_s"]
        r_ph = [float(v) for v in realized[li]["ph_dur"].split()]
        r_total = sum(r_ph)
        p_scale = realized_lines[li] / r_total if r_total else 0.0
        pt = 0.0
        for ph, r_dur in zip(line["phonemes"], r_ph):
            dur = r_dur * p_scale
            if ph.get("station") and dur >= 0.055:
                c0 = offsets[li] + pt
                seg = samples[int(c0 * sr):
                              int((c0 + dur) * sr)]
                read = judge_vowel(seg, sr, ph["station"])
                vowel_reads.setdefault(
                    ph["station"], []).append(read)
            pt += r_dur
    pitch = judge_pitch(samples, sr, notes)
    onsets = judge_onsets(samples, sr, offsets)
    vowels = {}
    for station, reads in sorted(vowel_reads.items()):
        dists = [r["distance_octaves"] for r in reads
                 if "distance_octaves" in r]
        vowels[station] = {
            "n_reads": len(reads),
            "n_measured": len(dists),
            "n_unmeasurable": len(reads) - len(dists),
            "median_distance_octaves":
                round(sorted(dists)[len(dists) // 2], 4)
                if dists else None,
            "n_match": sum(1 for r in reads if r.get("match")),
        }
    language = judge_language(run_dir / "mugetsu-hook.wav",
                              expected_lang=item.get("lang"))
    coverage = judge_coverage(run_dir / "mugetsu-hook.wav")
    return {
        "item_id": "mugetsu-hook",
        "corpus_version": corpus["version"],
        "engine": engine_label,
        "render": str(run_dir / "mugetsu-hook.wav"),
        "state": "SCORED",
        "judges": {"durations": durations, "pitch": pitch,
                   "onsets": onsets, "vowels": vowels,
                   "language": language, "coverage": coverage},
    }
