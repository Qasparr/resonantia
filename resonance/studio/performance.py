# 93
# ---------------------------------------------------------------------
# performance.py -- Proof No. 4's road: one performance, no assembly.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VIII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: produce_performance(spec) renders ONE continuous
# performance. A seed take is generated from the spec's single
# invariant prompt; every later take is generated CONTINUED from
# the actual preceding audio (the bridge's audio conditioning --
# the model plays through the join), and the takes are spliced
# DIRECTLY: no crossfade, no per-section RMS matching, no grid, no
# trim. The joins are then MEASURED (waveform jump and level step
# at each splice) and confessed in the manifest, because a splice
# you do not weigh is a seam you are hiding. The performance's
# tempo is its own: realized tempo is measured globally and per
# 30 s window by onset-envelope autocorrelation, and the one
# permitted overlay -- the composed arpeggio -- takes its schedule
# FROM that measured tempo. The performance leads; the dancer
# follows. The Stereo Law's bed widening and the mastering law
# apply unchanged, on shared pipeline machinery.
#
# DOCTRINE: the founder's ear has convicted assembly three times
# (soundfont kit, synth spine, rendered one-shot kit -- "sounds
# like SNES MIDI", "Frankenstein") and passed whole-performance
# generation twice (Proof No. 1; the Lyria benchmark, one pass,
# zero drift). This module is the performance hypothesis in its
# purest form the house can build: nothing in the track was placed
# by a grid, cut from a kit, or dreamed by a second prompt. What
# is absent is absent BY DESIGN and is listed in the manifest:
# no spine, no kit, no samples, no synthesized voice, and no Sigma
# layer (excluded for test purity at the founder's order -- the
# v4b A/B ACQUITTED Sigma; its absence here is hygiene, not
# suspicion). If the pure method cannot reach the aimed length,
# the honest performance is delivered at the length it reached
# and the manifest says so.
#
# PROOF No. 5 (this module's second ruling): the desk's spectral
# audit of Proof No. 4 convicted the composed arpeggio layer --
# praised as an effect on dense assembled tracks, it read as a
# "weird wind instrument" standing over a bare performance
# (solfeggio ridges +9..+27 dB above the raw performance). The
# founder's stamp on the desk's solution: IF IT ISN'T IN THE
# PERFORMANCE, IT ISN'T IN THE TRACK. So the Paganini line moves
# INSIDE the prompt -- the performance generates its own violin
# arpeggios, in tune and in phrase, and NOTHING rides: no composed
# arpeggio, no Sigma, no spine, no kit. Two more of Proof No. 4's
# measured wounds get their cures in the same ruling. Its joins
# clicked where the chain had been resumed across a restart; the
# one join chained inside a single process was invisible (0.001).
# So a spec may now demand `single_session`: the whole chain is
# born in ONE bridge process, every continuation conditioned on
# in-memory audio, no take is resumed from disk, and an
# interrupted chain is VOID -- set aside under void-attempt-N/,
# never spliced -- and the performance is re-struck whole from
# the seed. And its tempo wandered for ~90 s before locking, so
# a spec may strike `warmup_takes`: leading takes played and
# DISCARDED, their audio never in the program, so the kept
# program opens where the performance's clock has locked. The
# warm-up's own tempo is measured and confessed, so the discard
# stands on evidence, not on hope.
# ---------------------------------------------------------------------

import json
import math
import sys
import time
import wave
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from resonance.studio import arpeggio as arpeggio_mod
from resonance.studio import pipeline as pipe

# The tempo search band. Detroit bounce lives in it whole: the
# floor admits the half-time feel the benchmark itself realized
# (~70), the ceiling admits double-time readings of it (~200).
TEMPO_MIN_BPM = 40.0
TEMPO_MAX_BPM = 200.0

# The arpeggio's arc over a performance, as (name, density, weight)
# -- the same dramaturgy the spine schedules carried (statement in,
# bariolage under the verses, runs on the lifts, the third verse at
# 16ths, the outro's statement fading), apportioned by weight over
# however many bars the performance's own tempo gives it. The
# names are load-bearing: arpeggio.mode_for_section reads the
# "verse3" and "outro" prefixes for its two special modes.
_ARC = (
    ("intro", "sparse", 8),
    ("groove", "driving", 16),
    ("lift", "full", 16),
    ("verse3 ride", "driving", 16),
    ("groove", "driving", 16),
    ("lift", "full", 16),
    ("outro", "sparse", 8),
)


# ---------------------------------------------------------------------
# Tempo: the performance's own clock, measured -- never imposed.
# ---------------------------------------------------------------------

def onset_envelope(samples, sr, frame=2048, hop=512):
    """Spectral-flux onset envelope of a mono signal.

    MECHANISM: successive STFT magnitudes, positive differences
    summed -- the classic onset envelope: it rises where energy
    ARRIVES (a struck drum, a new note) and sleeps where the sound
    merely continues. Returns (envelope, envelope_rate_hz). The
    transforms are plain rffts of Hann-windowed frames; at song
    length this is seconds of arithmetic, not minutes.
    """
    x = np.asarray(samples, dtype=np.float64)
    n_frames = 1 + max(0, (x.shape[0] - frame) // hop)
    win = np.hanning(frame)
    env = np.zeros(n_frames, dtype=np.float64)
    prev = None
    for i in range(n_frames):
        seg = x[i * hop:i * hop + frame]
        if seg.shape[0] < frame:
            seg = np.pad(seg, (0, frame - seg.shape[0]))
        mag = np.abs(np.fft.rfft(seg * win))
        if prev is not None:
            env[i] = float(np.sum(np.maximum(mag - prev, 0.0)))
        prev = mag
    return env, sr / hop


def tempo_from_envelope(env, env_rate, min_bpm=TEMPO_MIN_BPM,
                        max_bpm=TEMPO_MAX_BPM):
    """The tempo an onset envelope beats at, by autocorrelation.

    MECHANISM: mean-remove the envelope, autocorrelate it (FFT,
    zero-padded to twice the length), and weigh the periodicities
    it finds. Two facts shape the weighing, both stated rather
    than hidden. First, a raw autocorrelation argmax on dense
    program material locks onto the loudest SLOW periodicity --
    the phrase swell, the backbeat's two-beat span -- not the
    beat; the desk measured exactly that failure on the house's
    own masters (a 140 BPM spine read as 49 under its own bed).
    Second, every working tempo estimator answers with a prior;
    this one multiplies the autocorrelation by a log-Gaussian
    tempo prior (center 100 BPM, sigma one octave -- wide and
    gentle, a lean, not a shove) and takes the strongest
    surviving lag, refined by parabolic interpolation. The raw
    dominant periodicity and the top candidate periodicities are
    reported beside the headline, so the prior's work is visible
    and the reader can overrule the estimator with its own
    numbers. Returns None when the envelope is silent or too
    short to hold a period honestly.
    """
    e = np.asarray(env, dtype=np.float64)
    if e.size < int(env_rate * 8) or not np.any(e):
        return None
    e = e - float(np.mean(e))
    n = e.shape[0]
    nfft = 1 << int(np.ceil(np.log2(2 * n)))
    spec = np.fft.rfft(e, n=nfft)
    ac = np.fft.irfft(spec * np.conj(spec), n=nfft)[:n]
    if ac[0] <= 0.0:
        return None
    ac = ac / ac[0]
    lag_min = max(2, int(env_rate * 60.0 / max_bpm))
    lag_max = min(n - 2, int(env_rate * 60.0 / min_bpm))
    if lag_max <= lag_min:
        return None
    lags = np.arange(lag_min, lag_max, dtype=np.float64)
    bpms = 60.0 * env_rate / lags
    prior = np.exp(-0.5 * (np.log2(bpms / 100.0)) ** 2)
    score = ac[lag_min:lag_max] * prior
    k = lag_min + int(np.argmax(score))
    shift = 0.0
    if 0 < k < n - 1:
        a, b, c = float(ac[k - 1]), float(ac[k]), float(ac[k + 1])
        denom = a - 2.0 * b + c
        if denom != 0.0:
            shift = 0.5 * (a - c) / denom
    bpm = 60.0 * env_rate / (k + shift)
    dominant = lag_min + int(np.argmax(ac[lag_min:lag_max]))
    # The top candidate periodicities: local maxima of the raw
    # autocorrelation, strongest first -- the evidence table the
    # headline was chosen from.
    seg = ac[lag_min:lag_max]
    peaks = [i for i in range(1, seg.shape[0] - 1)
             if seg[i] >= seg[i - 1] and seg[i] >= seg[i + 1]]
    peaks.sort(key=lambda i: -seg[i])
    candidates = [{"bpm": round(60.0 * env_rate / (lag_min + i), 2),
                   "autocorrelation": round(float(seg[i]), 4)}
                  for i in peaks[:3]]
    return {"bpm": round(bpm, 2),
            "peak_autocorrelation": round(float(ac[k]), 4),
            "dominant_periodicity_bpm":
                round(60.0 * env_rate / dominant, 2),
            "candidates": candidates,
            "double_time_candidate_bpm":
                round(2.0 * bpm, 2) if 2.0 * bpm <= max_bpm * 1.02
                else None}


def window_tempos(env, env_rate, total_seconds, window_s=30.0):
    """Realized tempo per window: the drift measurement.

    MECHANISM: the same autocorrelation, run on each window's
    slice of the one onset envelope. The benchmark's distinction
    is a window series that does not move (~0 drift); this is the
    instrument that can say whether a performance holds its clock
    or wanders. A final partial window is measured when it holds
    at least 10 s; shorter tails are reported unmeasured rather
    than dressed in a number they cannot support.
    """
    out = []
    start = 0.0
    while start < total_seconds:
        end = min(total_seconds, start + window_s)
        if end - start >= 10.0 or start == 0.0:
            i0 = int(start * env_rate)
            i1 = int(end * env_rate)
            t = tempo_from_envelope(env[i0:i1], env_rate)
            out.append({
                "start_s": round(start, 1), "end_s": round(end, 1),
                "bpm": (t or {}).get("bpm"),
                "peak_autocorrelation":
                    (t or {}).get("peak_autocorrelation"),
            })
        start = end
    return out


# ---------------------------------------------------------------------
# The joins: a direct splice, weighed at the splice.
# ---------------------------------------------------------------------

def measure_joins(mono, sr, join_samples, context_s=0.25):
    """Weigh every join in a directly-spliced performance.

    MECHANISM: at each join sample j, the waveform jump
    |x[j] - x[j-1]| -- the very number the chaining feasibility
    probe weighed (0.0043 chained vs 0.0746 plain) -- and the
    level step: RMS of the `context_s` after the join minus RMS
    of the `context_s` before it, in dB. The reference is the
    performance's own internal weather: the median and 99th
    percentile of |diff| across the whole stream, so a join is
    judged against the music's own transitions, not against
    silence. Returns (joins, summary).
    """
    x = np.asarray(mono, dtype=np.float64)
    if x.size < 2:
        return [], {"count": 0}
    diffs = np.abs(np.diff(x))
    ref_median = float(np.median(diffs))
    ref_p99 = float(np.percentile(diffs, 99))
    ctx = max(1, int(context_s * sr))

    def _rms_db(a):
        if a.size == 0:
            return -120.0
        r = float(np.sqrt(np.mean(a ** 2)))
        return 20.0 * math.log10(r) if r > 0.0 else -120.0

    joins = []
    for j, at in enumerate(join_samples):
        if not 0 < at < x.shape[0]:
            continue
        jump = float(abs(x[at] - x[at - 1]))
        joins.append({
            "join": j + 1,
            "after_take": f"take{j + 1}",
            "at_sample": int(at),
            "at_seconds": round(at / sr, 3),
            "waveform_jump": round(jump, 5),
            "jump_vs_median_internal":
                round(jump / ref_median, 2) if ref_median > 0 else None,
            "rms_step_db": round(
                _rms_db(x[at:at + ctx]) - _rms_db(x[max(0, at - ctx):at]),
                2),
        })
    jumps = [j["waveform_jump"] for j in joins]
    summary = {
        "count": len(joins),
        "waveform_jump_mean":
            round(float(np.mean(jumps)), 5) if jumps else None,
        "waveform_jump_max":
            round(float(np.max(jumps)), 5) if jumps else None,
        "internal_jump_median": round(ref_median, 5),
        "internal_jump_p99": round(ref_p99, 5),
        "splice": "direct -- no crossfade, no gain, no trim",
    }
    return joins, summary


# ---------------------------------------------------------------------
# The single session: one process, one chain, or the run is void.
# ---------------------------------------------------------------------

def assert_session_chain(take_reports, expected=None):
    """Refuse any chain that was not born whole in one session.

    MECHANISM: Proof No. 4's joins clicked exactly where its chain
    had been spliced across a restart; the one join chained inside
    a single bridge process was invisible. The single-session rule
    therefore stands guard at the splice with three checks over
    the take reports of ONE render result: (1) the indices are
    exactly 0..n-1, each once -- and, when `expected` is given,
    exactly that many takes -- so an interrupted render that
    returned partial results names its missing takes here and the
    run dies BEFORE any splice; (2) no take carries
    resumed_from_disk -- a take inherited from a dead session is
    precisely the splice the rule exists to forbid; (3) every take
    after the seed testifies continued_from == its own index - 1
    -- the bridge's own word that its conditioning came from the
    in-memory predecessor, not from a file read back off disk.
    Raises RuntimeError: a chain that fails is not repaired, it is
    VOID. Returns the count of takes verified.
    """
    n = len(take_reports)
    if n == 0:
        raise RuntimeError(
            "performance: single-session chain has no takes -- "
            "the render returned nothing; the chain is void, "
            "refusing to splice")
    if expected is not None and n != expected:
        raise RuntimeError(
            f"performance: single-session chain returned {n} "
            f"takes of {expected} -- an interrupted render is "
            f"void, refusing to splice")
    seen = sorted(int(r["index"]) for r in take_reports)
    if seen != list(range(n)):
        raise RuntimeError(
            f"performance: single-session chain is incomplete "
            f"(take indices {seen}, expected 0..{n - 1}) -- an "
            f"interrupted render is void, refusing to splice")
    for r in take_reports:
        i = int(r["index"])
        if r.get("resumed_from_disk"):
            raise RuntimeError(
                f"performance: take {i} was resumed from disk -- "
                f"a single-session chain admits no inherited "
                f"takes; the chain is void, refusing to splice")
        if i > 0 and r.get("continued_from") != i - 1:
            raise RuntimeError(
                f"performance: take {i} testifies "
                f"continued_from={r.get('continued_from')!r}, not "
                f"{i - 1} -- its conditioning did not come from "
                f"the in-memory predecessor; the chain is void, "
                f"refusing to splice")
    return n


def void_prior_takes(out_dir, take_count):
    """Set aside a dead session's takes; return the void record.

    MECHANISM: before a single-session strike, any segNN.wav of
    this chain's indices already in out_dir is the corpse of an
    interrupted attempt. The house rule is MARKED, NEVER VANISHED:
    the files are not deleted but moved, whole, into
    void-attempt-N/ (N = one past the highest void directory
    already present), and the record of what was found -- the
    directory and the take indices -- goes into the manifest, so
    the count of voided attempts is evidence, not anecdote.
    Returns None when the ground was clean (no prior takes).
    """
    out_dir = Path(out_dir)
    found = []
    for i in range(take_count):
        p = out_dir / f"seg{i:02d}.wav"
        if p.exists():
            found.append((i, p))
    if not found:
        return None
    prior_voids = [d for d in out_dir.glob("void-attempt-*")
                   if d.is_dir()]
    n = len(prior_voids) + 1
    void_dir = out_dir / f"void-attempt-{n}"
    void_dir.mkdir(parents=True, exist_ok=False)
    for _i, p in found:
        p.rename(void_dir / p.name)
    return {"attempt": n, "directory": void_dir.name,
            "takes_found": [i for i, _p in found],
            "disposition": "set aside unspliced; the performance "
                           "was re-struck whole from the seed"}


# ---------------------------------------------------------------------
# The dancer's schedule, derived from the measured tempo.
# ---------------------------------------------------------------------

def build_arp_schedule(program_seconds, bpm, beats_per_bar=4):
    """A spine-shaped schedule whose clock is the performance's own.

    MECHANISM: whole bars of the measured tempo that fit inside
    the program (floor -- the dancer never asks the performance
    to stretch), apportioned across the house arc by weight with
    a 4-bar floor per chair, rounding drift settled on the
    largest section. swing is 0.0 BY LAW here: swing is a grid's
    opinion about time, and this record has no grid -- the
    dancer's humanizer gives it life instead. The result feeds
    arpeggio.render_arpeggio unchanged (bpm, swing, beats_per_bar,
    sections of name/bars/density -- the shape it already eats).
    """
    if bpm is None or bpm <= 0:
        raise ValueError("performance: cannot schedule the "
                         "arpeggio on an unmeasured tempo")
    sec_per_bar = beats_per_bar * 60.0 / float(bpm)
    total_bars = int(program_seconds // sec_per_bar)
    if total_bars < 4 * len(_ARC):
        raise ValueError(
            f"performance: {total_bars} bars is too few for the "
            f"arpeggio's arc ({4 * len(_ARC)} minimum)")
    wsum = sum(w for _, _, w in _ARC)
    bars = [max(4, int(round(total_bars * w / wsum)))
            for _, _, w in _ARC]
    drift = total_bars - sum(bars)
    if drift != 0:
        k = max(range(len(bars)), key=lambda i: bars[i])
        bars[k] += drift
    sections = [{"name": name, "bars": b, "density": density}
                for (name, density, _), b in zip(_ARC, bars)]
    return {"bpm": float(bpm), "swing": 0.0,
            "beats_per_bar": beats_per_bar, "sections": sections}


# ---------------------------------------------------------------------
# The take splice: the bridge's own bytes, joined and nothing more.
# ---------------------------------------------------------------------

def _splice_take_files(paths, out_path):
    """Concatenate PCM WAV take files sample-exactly.

    MECHANISM: stdlib wave, frame bytes copied verbatim from each
    take into one file of the seed take's format -- no decode, no
    gain, no fade: the splice the join measurement then weighs is
    the splice that actually happened. A take whose format
    disagrees with the seed take's is refused loudly. Returns the
    cumulative boundary sample indices (0, ..., total).
    """
    with wave.open(str(paths[0]), "rb") as w0:
        fmt = (w0.getframerate(), w0.getnchannels(),
               w0.getsampwidth())
        params = w0.getparams()
    boundaries = [0]
    total = 0
    with wave.open(str(out_path), "wb") as out:
        out.setparams(params)
        for p in paths:
            with wave.open(str(p), "rb") as w:
                if (w.getframerate(), w.getnchannels(),
                        w.getsampwidth()) != fmt:
                    raise ValueError(
                        f"performance: take file {p} does not "
                        f"match the seed take's format")
                frames = w.getnframes()
                out.writeframes(w.readframes(frames))
                total += frames
                boundaries.append(total)
    return boundaries


# ---------------------------------------------------------------------
# The sheet: composition.abc for a performance.
# ---------------------------------------------------------------------

def _mmss(seconds):
    m = int(seconds // 60)
    return f"{m}:{seconds - 60 * m:04.1f}"


def write_composition_abc(path, spec, schedule, tempo, joins,
                          join_summary, program_seconds):
    """Write the run's composition.abc -- the house layer, notated.

    MECHANISM: everything on the sheet derives from the run's own
    data (the composed arpeggio events recomputed from the same
    schedule the render ate; the joins and tempo as measured).
    The performance itself is NOT transcribed: per the founder's
    standing rule its transcription is a separate production,
    owed and marked owed -- never fabricated. What the bed was
    told stands on the sheet verbatim: the one invariant prompt.
    """
    arp = spec["arpeggio"]
    events, modes = arpeggio_mod.compose_events(
        schedule["sections"], arp["mode_overrides"])
    bpm = tempo["global_bpm"]
    bar_s = schedule["beats_per_bar"] * 60.0 / bpm
    lines = []
    lines.append("X:1")
    lines.append(f"T:{spec['title']}: the house layer, notated")
    lines.append("C:Johnathan 'Qasparr' Monroe, ARR, All Rights "
                 "Reserved, Without Prejudice")
    lines.append(f"R:Detroit bounce, F minor -- tempo the "
                 f"performance's own: measured {bpm} BPM")
    lines.append("M:4/4")
    lines.append("L:1/16")
    lines.append("K:Fmin")
    lines.append("%")
    lines.append("% WHAT THIS SHEET IS -- AND IS NOT (the founder's "
                 "rule, kept):")
    lines.append("% This notation covers EXACTLY what the house "
                 "engine composed")
    lines.append("% and struck over the performance: the composed "
                 "violin arpeggio")
    lines.append("% (resonance.studio.arpeggio), complete below. "
                 "The performance")
    lines.append("% itself -- the MusicGen bed, one continuous "
                 "performance -- is")
    lines.append("% NOT transcribed here: its transcription is a "
                 "separate")
    lines.append("% production, still owed, and no sheet for it "
                 "has been fabricated.")
    lines.append("% What the bed was told stands below, verbatim, "
                 "ONCE -- the")
    lines.append("% single invariant prompt of the seed take and "
                 "every continuation:")
    lines.append(f"%   {spec['prompt_base']}")
    lines.append("%")
    lines.append(f"% THE PERFORMANCE: {tempo['takes']} takes, each "
                 f"extension generated")
    lines.append(f"% CONTINUED from the preceding audio "
                 f"({tempo['continue_seconds']} s of conditioning"
                 f") -- the model plays")
    lines.append("% through every join. The takes are spliced "
                 "DIRECTLY: no crossfade,")
    lines.append("% no RMS matching, no grid, no trim, no spine, "
                 "no kit, no samples,")
    lines.append("% no synthesized voice, and NO SIGMA LAYER "
                 "(excluded for test")
    lines.append("% purity at the founder's order; the v4b A/B "
                 "acquitted Sigma -- its")
    lines.append("% absence here is hygiene, not suspicion).")
    lines.append("%")
    lines.append(f"% THE JOINS, WEIGHED (native 32 kHz splice "
                 f"points): the program's own")
    lines.append(f"% internal jumps read median "
                 f"{join_summary['internal_jump_median']}, p99 "
                 f"{join_summary['internal_jump_p99']}; the joins:")
    for j in joins:
        lines.append(
            f"%   join {j['join']} after {j['after_take']} at "
            f"{_mmss(j['at_seconds'])}: waveform jump "
            f"{j['waveform_jump']} ({j['jump_vs_median_internal']}x "
            f"the median internal jump), level step "
            f"{j['rms_step_db']:+.2f} dB")
    lines.append("%")
    lines.append(f"% REALIZED TEMPO (onset-envelope "
                 f"autocorrelation, measured on the")
    lines.append(f"% performance, imposed by nobody): global "
                 f"{bpm} BPM. The 30 s windows:")
    win = ", ".join(
        f"{w['start_s']:.0f}s:{w['bpm']}" for w in tempo["windows_30s"])
    lines.append(f"%   {win}")
    lines.append(f"% Window spread: {tempo['window_bpm_spread']} "
                 f"BPM. The benchmark (the Anvil) drifts ~0; "
                 f"this is")
    lines.append("% the number this proof is weighed against.")
    lines.append("%")
    lines.append("% THE ARPEGGIO -- the dancer, and the one "
                 "assembled element the")
    lines.append("% founder's ear has praised (Proofs No. 2-3). "
                 "Its schedule is DERIVED")
    lines.append(f"% FROM THE MEASURED TEMPO: {sum(s['bars'] for s in schedule['sections'])} bars of "
                 f"{bar_s:.3f} s, swing 0.0 --")
    lines.append("% no grid was imposed on the performance to "
                 "give the dancer one.")
    lines.append("% Section chart (modes = the arpeggio's "
                 "realization):")
    bar = 0
    for i, sec in enumerate(schedule["sections"]):
        t0 = bar * bar_s
        t1 = (bar + sec["bars"]) * bar_s
        lines.append(
            f"%   {sec['name']:<11} bars {bar + 1:>3}-"
            f"{bar + sec['bars']:<3} {sec['density']:<8} "
            f"arp:{modes[i]:<14} {_mmss(t0)} - {_mmss(t1)}")
        bar += sec["bars"]
    lines.append("% Composed from the SOLFEGGIO LADDER, played at "
                 "its equal-tempered")
    lines.append("% staff approximations; each carrier's cents "
                 "offset from its staff")
    lines.append("% pitch is stated, never smoothed:")
    for rung in arpeggio_mod.ladder_inventory():
        lines.append(
            f"%   {rung['syllable']:<4} {rung['carrier_hz']:.0f} Hz "
            f"-> {rung['abc']:<3} (MIDI {rung['midi']}, "
            f"{rung['staff_hz']} Hz) {rung['cents_offset']:+.1f} "
            f"cents")
    lines.append("% Phrasing is Fibonacci -- phrase lengths "
                 "1, 1, 2, 3, 5, 8 climbing")
    lines.append("% the ladder cyclically. THE FIGURE (one cell, "
                 "20 notes, L:1/16):")
    cell = arpeggio_mod.figure_cell()
    toks = [arpeggio_mod.ABC_TOKENS[arpeggio_mod.LADDER[i][2]]
            for i in cell]
    lines.append(" ".join(toks) + " |")
    first_drv = next(
        (i for i, s in enumerate(schedule["sections"])
         if s["density"] == "driving"), None)
    if first_drv is not None:
        bar0 = [e for e in events
                if e["section"] == first_drv][:16]
        lines.append("% BARIOLAGE (the grooves): the figure "
                     "alternating with the MI")
        lines.append("% pedal -- the first bar as composed:")
        lines.append(" ".join(
            arpeggio_mod.ABC_TOKENS[e["midi"]] for e in bar0) + " |")
    lines.append("% RUNS (the lifts): the figure cell at 16ths, "
                 "phrase heads accented,")
    lines.append("% tiling the section. STATEMENT (intro): the "
                 "figure at 8th spacing,")
    lines.append("% phrase-final notes held; the outro's "
                 "statement fades. The third")
    lines.append("% chair's groove takes the bariolage at 16ths.")
    lines.append("%")
    lines.append("% THE STEREO LAW (part 2 only -- there is no "
                 "spine to pan, and no")
    lines.append("% Sigma to spare): the bed is widened by band "
                 "above 180 Hz with the")
    lines.append("% mid preserved exactly and the lows fully "
                 "mono. Correlations stand")
    lines.append("% measured in the manifest.")
    lines.append("%")
    lines.append("% 93 -- Live, Love, and let Love, Live.")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_performance_sheet_abc(path, spec, tempo, joins,
                                join_summary, program_seconds,
                                warmup=None, session=None):
    """Write composition.abc for a performance NOTHING rides.

    MECHANISM: Proof No. 5's sheet. There is no house layer to
    notate -- the composed arpeggio is gone by the founder's
    ruling (if it isn't in the performance, it isn't in the
    track), and the Paganini line the prompt demanded was played
    BY the performance, as part of its body. Per the founder's
    standing rule the sheet therefore notates NOTHING and says
    so: what stands here is the run's own record -- the one
    invariant prompt verbatim, the session and warm-up facts,
    the weighed joins, the measured tempo -- and the
    transcription of the performance itself (its violin line
    included, being part of the body) marked OWED: a separate
    production, never fabricated on this sheet.
    """
    perf = spec["performance"]
    bpm = tempo["global_bpm"]
    lines = []
    lines.append("X:1")
    lines.append(f"T:{spec['title']}: the performance, unaccompanied")
    lines.append("C:Johnathan 'Qasparr' Monroe, ARR, All Rights "
                 "Reserved, Without Prejudice")
    lines.append(f"R:Detroit bounce, F minor -- tempo the "
                 f"performance's own: measured {bpm} BPM")
    lines.append("M:4/4")
    lines.append("L:1/16")
    lines.append("K:Fmin")
    lines.append("%")
    lines.append("% WHAT THIS SHEET IS -- AND IS NOT (the founder's "
                 "rule, kept):")
    lines.append("% NO notation stands on this sheet, and that is "
                 "the honest state")
    lines.append("% of the record. Nothing was composed over this "
                 "performance:")
    lines.append("% no arpeggio layer, no Sigma, no spine, no kit "
                 "-- the founder's")
    lines.append("% ruling after Proof No. 4: IF IT ISN'T IN THE "
                 "PERFORMANCE, IT")
    lines.append("% ISN'T IN THE TRACK. The Paganini line stands "
                 "in the prompt")
    lines.append("% below, and the performance played it as part "
                 "of its own body.")
    lines.append("% The transcription of the performance itself "
                 "-- violin line")
    lines.append("% included -- is a SEPARATE PRODUCTION, still "
                 "OWED, and no")
    lines.append("% sheet for it has been fabricated.")
    lines.append("% What the performance was told stands below, "
                 "verbatim, ONCE --")
    lines.append("% the single invariant prompt of the seed take "
                 "and every")
    lines.append("% continuation:")
    lines.append(f"%   {spec['prompt_base']}")
    lines.append("%")
    if session and session.get("single_session"):
        lines.append(
            f"% THE SESSION: the whole chain -- {perf['takes']} "
            f"takes -- was born in")
        lines.append(
            "% ONE bridge process, every continuation conditioned "
            "on the preceding")
        lines.append(
            "% audio IN MEMORY. No take was resumed from disk; an "
            "interrupted chain")
        lines.append(
            "% is void by rule, and the session guard weighed "
            "this chain before")
        lines.append("% the splice was allowed.")
        voids = session.get("voided_attempts") or []
        if voids:
            lines.append(
                f"% Voided attempts set aside before this strike: "
                f"{len(voids)} "
                f"({', '.join(v['directory'] for v in voids)}).")
    if warmup and warmup.get("takes"):
        lines.append(
            f"% THE WARM-UP: {warmup['takes']} leading take(s) "
            f"were struck and")
        lines.append(
            f"% DISCARDED -- their audio is nowhere in this "
            f"program. The warm-up's")
        lines.append(
            f"% own measured tempo: {warmup['tempo']['global_bpm']} "
            f"BPM. The kept program")
        lines.append(
            f"% opens at kept take 1 ({warmup['kept_opens_at_seconds']} "
            f"s into the chain).")
    lines.append(
        f"% THE PERFORMANCE: {tempo['takes']} takes struck, "
        f"{program_seconds:.1f} s of kept")
    lines.append(
        f"% program, each extension generated CONTINUED from the "
        f"preceding audio")
    lines.append(
        f"% ({tempo['continue_seconds']} s of conditioning) -- the "
        f"model plays through")
    lines.append("% every join. The kept takes are spliced "
                 "DIRECTLY: no crossfade,")
    lines.append("% no RMS matching, no grid, no trim.")
    lines.append("%")
    lines.append(f"% THE JOINS, WEIGHED (native 32 kHz splice "
                 f"points, kept program):")
    lines.append(f"% the program's own internal jumps read median "
                 f"{join_summary['internal_jump_median']}, p99 "
                 f"{join_summary['internal_jump_p99']}; the joins:")
    for j in joins:
        lines.append(
            f"%   join {j['join']} after {j['after_take']} at "
            f"{_mmss(j['at_seconds'])}: waveform jump "
            f"{j['waveform_jump']} ({j['jump_vs_median_internal']}x "
            f"the median internal jump), level step "
            f"{j['rms_step_db']:+.2f} dB")
    lines.append("%")
    lines.append(f"% REALIZED TEMPO (onset-envelope "
                 f"autocorrelation, measured on the")
    lines.append(f"% kept program, imposed by nobody): global "
                 f"{bpm} BPM. The 30 s windows:")
    win = ", ".join(
        f"{w['start_s']:.0f}s:{w['bpm']}" for w in tempo["windows_30s"])
    lines.append(f"%   {win}")
    lines.append(f"% Window spread: {tempo['window_bpm_spread']} "
                 f"BPM. The benchmark (the Anvil) drifts ~0; "
                 f"this is")
    lines.append("% the number this proof is weighed against.")
    lines.append("%")
    lines.append("% THE STEREO LAW (part 2 only -- there is no "
                 "spine to pan, and no")
    lines.append("% Sigma to spare): the bed is widened by band "
                 "above 180 Hz with the")
    lines.append("% mid preserved exactly and the lows fully "
                 "mono. Correlations stand")
    lines.append("% measured in the manifest.")
    lines.append("%")
    lines.append("% 93 -- Live, Love, and let Love, Live.")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------
# The dry-run plan: the performance weighed before it is struck.
# ---------------------------------------------------------------------

def _planned_manifest(spec):
    perf = spec["performance"]
    planned = {
        "performance": {
            "takes": perf["takes"],
            "take_seconds": perf["take_seconds"],
            "continue_seconds": perf["continue_seconds"],
            "warmup_takes": perf["warmup_takes"],
            "kept_takes": perf["takes"] - perf["warmup_takes"],
            "single_session": perf["single_session"],
            "invariant_prompt": pipe._full_prompt(spec,
                                                  spec["sections"][0]),
            "planned_total_seconds":
                perf["takes"] * perf["take_seconds"],
            "planned_program_seconds":
                (perf["takes"] - perf["warmup_takes"])
                * perf["take_seconds"],
            "joins": perf["takes"] - perf["warmup_takes"] - 1,
            "method": "one invariant prompt; a seed take extended "
                      "only by audio continuation; direct splices"
                      + ("; warm-up takes struck and discarded"
                         if perf["warmup_takes"] else "")
                      + ("; single session -- one bridge process, "
                         "no resume, an interrupted chain is void"
                         if perf["single_session"] else ""),
        },
        "arpeggio": ({
            "level_db": spec["arpeggio"]["level_db"],
            "orbit_hz": spec["arpeggio"]["orbit_hz"],
            "note": "the schedule derives from the measured tempo "
                    "after the render; its events cannot be "
                    "counted before the performance exists"}
            if spec.get("arpeggio") else None),
        "sigma": "absent by design (test purity)",
        "master": spec["master"],
        "sample_rate": pipe.TARGET_SR,
    }
    if spec["stereo"]["width"] > 0.0:
        planned["stereo"] = {
            "bed_width": spec["stereo"]["width"],
            "spine_panned_by_role": False,
            "low_cut_hz": pipe.STEREO_LOW_CUT_HZ,
        }
    return {
        "title": spec["title"],
        "title_status": "working title",
        "dry_run": True,
        "spec": spec,
        "planned": planned,
        "files": {},
        "notes": ["dry run: spec validated, nothing rendered"],
    }


# ---------------------------------------------------------------------
# produce_performance(): the road itself.
# ---------------------------------------------------------------------

def produce_performance(spec, dry_run=False, log=None):
    """Run a performance production; return the manifest dict.

    MECHANISM: render the takes through the venv bridge -> splice
    the kept take files sample-exactly at the native rate and
    WEIGH the joins -> resample the one performance to 48 kHz ->
    measure its realized tempo, globally and per window -> widen
    the bed (Stereo Law, part 2) -> lay the arpeggio, when the
    spec carries one, on a schedule derived from the measured
    tempo -> fade the ends -> master (loudness, then the ceiling,
    which is law) -> strike the files -> manifest, everything
    measured, everything absent confessed.

    Two spec clauses change the render's shape. `single_session`
    replaces the resume law with its opposite: prior takes are
    voided (set aside, never spliced), the whole chain renders in
    ONE bridge job, and the session guard verifies the chain
    before the splice. `warmup_takes` strikes leading takes whose
    audio never enters the program: the full chain is spliced for
    the audit record, the kept program is spliced from the takes
    after the warm-up, and the warm-up's own tempo is measured as
    the discard's evidence.
    """
    log = log or (lambda msg: print(f"[studio] {msg}",
                                    file=sys.stderr, flush=True))
    out_dir = Path(spec["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    if dry_run:
        manifest = _planned_manifest(spec)
        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest

    perf = spec["performance"]
    sections = spec["sections"]
    prompt = pipe._full_prompt(spec, sections[0])
    t_start = time.time()
    single_session = bool(perf.get("single_session"))
    n_warm = int(perf.get("warmup_takes", 0))
    session_block = {"single_session": single_session,
                     "voided_attempts": [],
                     "render_invocations_this_run": 0,
                     "takes_verified_by_guard": None}

    # -- (a) render the takes, one model load, the chain unbroken --
    render_by_index = {}
    render_model = "facebook/musicgen-small"
    render_wall = 0.0
    if single_session:
        # THE SINGLE SESSION (Proof No. 5's ruling): any take
        # files already on the ground are a dead session's corpse
        # -- set them aside VOID, unspliced, then strike the WHOLE
        # chain in one bridge job, so every continuation conditions
        # on the bridge's own in-memory predecessor. The session
        # guard weighs the returned chain before any splice is
        # allowed; a chain that fails it is void, not repaired.
        voided = void_prior_takes(out_dir, len(sections))
        if voided is not None:
            session_block["voided_attempts"].append(voided)
            log(f"voided prior attempt {voided['attempt']}: takes "
                f"{voided['takes_found']} set aside unspliced -- "
                f"re-striking the whole performance from the seed")
        job = {"out_dir": str(out_dir), "segments": [
            {"index": i, "prompt": prompt,
             "seconds": sections[i]["seconds"],
             "seed": spec["seed"] + i,
             "file": f"seg{i:02d}.wav",
             "continue_seconds": (perf["continue_seconds"]
                                  if i > 0 else 0.0)}
            for i in range(len(sections))]}
        log(f"rendering all {len(sections)} takes in ONE bridge "
            f"session (single-session rule: no resume; an "
            f"interrupted chain is void)...")
        render = pipe._run_bridge(job, out_dir, log)
        session_block["render_invocations_this_run"] = 1
        render_model = render["model"]
        render_wall = render["wall_seconds"]
        for r in render["segments"]:
            render_by_index[r["index"]] = {**r, "resumed": False}
        guard_reports = [
            {"index": i,
             "resumed_from_disk": bool(
                 render_by_index.get(i, {}).get("resumed")),
             "continued_from":
                 render_by_index.get(i, {}).get("continued_from")}
            for i in sorted(render_by_index)]
        session_block["takes_verified_by_guard"] = \
            assert_session_chain(guard_reports,
                                 expected=len(sections))
        log("session guard: the chain is whole -- every take was "
            "born in this session and continued from its in-memory "
            "predecessor")
    else:
        # Resume law: whole takes already on disk are not
        # re-rendered; the bridge conditions a resumed chain from
        # the predecessor's file, so a restarted run keeps the
        # performance whole. A truncated survivor is re-rendered,
        # never trusted.
        todo = []
        for i, s in enumerate(sections):
            seg_file = out_dir / f"seg{i:02d}.wav"
            if seg_file.exists() and pipe._segment_file_ok(
                    seg_file, s["seconds"]):
                with wave.open(str(seg_file), "rb") as w:
                    render_by_index[i] = {
                        "index": i, "file": seg_file.name,
                        "sample_rate": w.getframerate(),
                        "frames": w.getnframes(),
                        "wall_seconds": None, "resumed": True}
                log(f"take {i} already rendered -- resuming past it")
            else:
                todo.append(i)
        if todo:
            job = {"out_dir": str(out_dir), "segments": [
                {"index": i, "prompt": prompt,
                 "seconds": sections[i]["seconds"],
                 "seed": spec["seed"] + i,
                 "file": f"seg{i:02d}.wav",
                 "continue_seconds": (perf["continue_seconds"]
                                      if i > 0 else 0.0)}
                for i in todo]}
            log(f"rendering {len(todo)} takes via the venv bridge "
                f"(one performance, chained)...")
            render = pipe._run_bridge(job, out_dir, log)
            render_model = render["model"]
            render_wall = render["wall_seconds"]
            for r in render["segments"]:
                render_by_index[r["index"]] = {**r, "resumed": False}
    take_reports = []
    for i, s in enumerate(sections):
        r = render_by_index[i]
        take_reports.append({
            "name": s["name"], "prompt": prompt,
            "seed": spec["seed"] + i, "seconds": s["seconds"],
            "native_sample_rate": r["sample_rate"],
            "frames": r.get("frames"),
            "file": r["file"], "wall_seconds": r["wall_seconds"],
            "resumed_from_disk": bool(r.get("resumed")),
            # The chain, as the bridge reported it. A take resumed
            # from disk carries null: the chain fact lives in the
            # render that struck it, and this manifest will not
            # pretend to remember what it did not witness.
            "continued_from": r.get("continued_from"),
            "continue_seconds": r.get("continue_seconds", 0.0),
        })

    # -- (b) the splice: direct, and then weighed ------------------
    # The kept program is the takes after the warm-up; the full
    # chain (warm-up included) is also spliced, for the audit
    # record and for the warm-up's own evidence. When there is no
    # warm-up the kept program IS the whole chain -- the Proof
    # No. 4 shape of the record, unchanged.
    log("splicing the takes directly and weighing the joins...")
    native_path = out_dir / "performance_32k.wav"
    kept_idx = list(range(n_warm, len(sections)))
    boundaries = _splice_take_files(
        [out_dir / f"seg{i:02d}.wav" for i in kept_idx],
        native_path)
    native, native_sr = pipe.read_wav_pcm(native_path)
    if native.ndim == 2:
        native = native[0]
    native = np.asarray(native, dtype=np.float64)
    joins, join_summary = measure_joins(
        native, native_sr, boundaries[1:-1])
    if n_warm:
        # The weigher counts positions within the array it was
        # handed; against the kept splice its "take{j+1}" names
        # the kept position, not the chain's take. Relabel to the
        # chain's own names so the record speaks of the takes that
        # were actually struck.
        for k, j in enumerate(joins):
            j["after_take"] = f"take{n_warm + k + 1}"
    full_path = None
    full_chain_seconds = None
    warmup_block = {"takes": 0, "discarded": False,
                    "audio_in_program": False}
    if n_warm:
        full_path = out_dir / "performance_full_32k.wav"
        full_bounds = _splice_take_files(
            [out_dir / f"seg{i:02d}.wav"
             for i in range(len(sections))], full_path)
        full, full_sr = pipe.read_wav_pcm(full_path)
        if full.ndim == 2:
            full = full[0]
        full = np.asarray(full, dtype=np.float64)
        full_chain_seconds = round(full_bounds[-1] / full_sr, 3)
        warm_end = full_bounds[n_warm]
        warm_env, warm_rate = onset_envelope(
            full[:warm_end], full_sr)
        warm_tempo = tempo_from_envelope(warm_env, warm_rate)
        full_joins, _full_summary = measure_joins(
            full, full_sr, full_bounds[1:-1])
        boundary_join = (full_joins[n_warm - 1]
                         if len(full_joins) >= n_warm else None)
        warmup_block = {
            "takes": n_warm,
            "take_indices": list(range(n_warm)),
            "seconds_struck": round(warm_end / full_sr, 3),
            "discarded": True,
            "audio_in_program": False,
            "tempo": {
                "global_bpm": (warm_tempo or {}).get("bpm"),
                "peak_autocorrelation":
                    (warm_tempo or {}).get("peak_autocorrelation"),
                "dominant_periodicity_bpm": (warm_tempo or {}).get(
                    "dominant_periodicity_bpm"),
                "candidate_periodicities":
                    (warm_tempo or {}).get("candidates"),
            },
            "boundary_join_into_kept": boundary_join,
            "kept_opens_at_seconds": round(warm_end / full_sr, 3),
            "note": "the warm-up was struck to be discarded: the "
                    "kept program opens where the performance's "
                    "clock had locked. Its tempo stands measured "
                    "here so the discard is evidence, not hope.",
        }
        log(f"warm-up discarded: {n_warm} take(s), "
            f"{warmup_block['seconds_struck']}s, its own tempo "
            f"{warmup_block['tempo']['global_bpm']} BPM")

    # -- (c) one resample of the whole performance -----------------
    bed48_path = out_dir / "performance_48k.wav"
    pipe._ffmpeg(["-i", str(native_path), "-ar", str(pipe.TARGET_SR),
                  "-ac", "2", "-c:a", "pcm_s24le", str(bed48_path)],
                 "resample performance")
    bed, sr = pipe.read_wav_pcm(bed48_path)
    assert sr == pipe.TARGET_SR
    if bed.ndim == 1:  # MusicGen-small is mono: dual it, honestly.
        bed = np.stack([bed, bed])
    bed = np.asarray(bed, dtype=np.float64)
    total_seconds = bed.shape[1] / pipe.TARGET_SR

    # -- (d) the tempo is the performance's own: measure it --------
    log("measuring the realized tempo (global and per window)...")
    mid = 0.5 * (bed[0] + bed[1])
    env, env_rate = onset_envelope(mid, pipe.TARGET_SR)
    tempo_global = tempo_from_envelope(env, env_rate)
    windows = window_tempos(env, env_rate, total_seconds)
    win_bpms = [w["bpm"] for w in windows if w["bpm"] is not None]
    tempo_block = {
        "global_bpm": (tempo_global or {}).get("bpm"),
        "global_peak_autocorrelation":
            (tempo_global or {}).get("peak_autocorrelation"),
        "dominant_periodicity_bpm":
            (tempo_global or {}).get("dominant_periodicity_bpm"),
        "candidate_periodicities":
            (tempo_global or {}).get("candidates"),
        "double_time_candidate_bpm":
            (tempo_global or {}).get("double_time_candidate_bpm"),
        "estimator": "onset envelope (spectral flux) "
                     "autocorrelation with a log-Gaussian tempo "
                     "prior (center 100 BPM, sigma 1 octave), "
                     f"{TEMPO_MIN_BPM:.0f}..{TEMPO_MAX_BPM:.0f} BPM "
                     "search on the performance's mid channel; "
                     "the dominant periodicity and the candidate "
                     "table stand beside the headline so the "
                     "prior's work is visible",
        "windows_30s": windows,
        "window_bpm_min": min(win_bpms) if win_bpms else None,
        "window_bpm_max": max(win_bpms) if win_bpms else None,
        "window_bpm_spread":
            round(max(win_bpms) - min(win_bpms), 2)
            if win_bpms else None,
        "takes": perf["takes"],
        "continue_seconds": perf["continue_seconds"],
    }

    # -- (e) the Stereo Law, part 2: the bed takes its width -------
    stereo_width = spec["stereo"]["width"]
    stereo_report = None
    if stereo_width > 0.0:
        stereo_report = {
            "bed_width": stereo_width,
            "spine_panned_by_role": False,
            "low_cut_hz": pipe.STEREO_LOW_CUT_HZ,
        }
        corr_before = pipe.channel_correlation(bed)
        log(f"widening the bed (Stereo Law, width "
            f"{stereo_width:.2f})...")
        bed = pipe.widen_bed(bed, pipe.TARGET_SR, stereo_width)
        stereo_report.update({
            "bed_correlation_before": round(corr_before, 4),
            "bed_correlation_after":
                round(pipe.channel_correlation(bed), 4),
            "bed_low_band_correlation_after": round(
                pipe.band_correlation(bed, pipe.TARGET_SR, 20.0,
                                      pipe.STEREO_LOW_CUT_HZ), 4),
        })

    # -- (f) the arpeggio: the dancer follows the performance ------
    arpeggio_report = None
    schedule_block = None
    if spec.get("arpeggio"):
        if tempo_block["global_bpm"] is None:
            raise RuntimeError(
                "performance: the realized tempo could not be "
                "measured, so the arpeggio has no honest schedule "
                "-- the run refuses rather than imposing a grid")
        log("composing the arpeggio on the measured tempo...")
        schedule = build_arp_schedule(total_seconds,
                                      tempo_block["global_bpm"])
        layer, arpeggio_report = arpeggio_mod.render_arpeggio(
            spec["arpeggio"], schedule, pipe.TARGET_SR)
        rendered = layer.shape[1]
        target = bed.shape[1]
        if rendered > target:
            layer = layer[:, :target]
            fit = "sliced to the program"
        elif rendered < target:
            layer = np.pad(layer, ((0, 0), (0, target - rendered)))
            fit = "zero-padded to the program"
        else:
            fit = "exact"
        layer_rms = float(np.sqrt(np.mean(layer ** 2)))
        mixed_dbfs = None
        if layer_rms > 0:
            ref_rms = float(np.sqrt(np.mean(bed ** 2)))
            gain = (ref_rms
                    * 10 ** (spec["arpeggio"]["level_db"] / 20.0)
                    / layer_rms)
            bed = bed + layer * gain
            mixed_dbfs = round(20.0 * math.log10(layer_rms * gain), 2)
        arpeggio_report["mixed_layer_rms_dbfs"] = mixed_dbfs
        schedule_block = {
            "bpm": schedule["bpm"],
            "bpm_source": "measured from the performance itself "
                          "(onset-envelope autocorrelation)",
            "swing": schedule["swing"],
            "total_bars": sum(s["bars"]
                              for s in schedule["sections"]),
            "sections": schedule["sections"],
            "layer_rendered_samples": rendered,
            "program_samples": target,
            "layer_fit": fit,
        }
        write_composition_abc(
            out_dir / "composition.abc", spec, schedule,
            tempo_block, joins, join_summary, total_seconds)
    else:
        # Nothing rides (Proof No. 5's shape): the sheet carries
        # no notation -- the performance's transcription, its
        # in-performance violin line included, is owed, and the
        # sheet says so instead of fabricating one.
        write_performance_sheet_abc(
            out_dir / "composition.abc", spec, tempo_block, joins,
            join_summary, total_seconds, warmup=warmup_block,
            session=session_block)

    # -- (g) fades: a record ends; it does not stop -----------------
    head = int(pipe.HEAD_FADE_S * pipe.TARGET_SR)
    tail = int(pipe.END_FADE_S * pipe.TARGET_SR)
    bed[:, :head] *= np.linspace(0.0, 1.0, head)
    bed[:, -tail:] *= np.linspace(1.0, 0.0, tail)

    # -- (h) master: loudness first, ceiling is law -----------------
    log("mastering...")
    mastered, master_report = pipe.master_signal(
        bed, pipe.TARGET_SR, spec["master"]["target_lufs"],
        spec["master"]["ceiling_dbtp"])
    if stereo_report is not None:
        stereo_report.update({
            "master_correlation":
                round(pipe.channel_correlation(mastered), 4),
            "master_side_rms_dbfs":
                round(pipe.side_rms_dbfs(mastered), 2),
        })

    # -- (i) strike the files ----------------------------------------
    master_npy = out_dir / "_master_float.npy"
    np.save(master_npy,
            np.asarray(mastered, dtype=np.float32).T.copy())
    master_wav = out_dir / "master.wav"
    pipe._run_bridge({"finalize": [
        {"npy": str(master_npy), "out": str(master_wav),
         "sample_rate": pipe.TARGET_SR, "subtype": "PCM_24"},
    ]}, out_dir, log)
    master_npy.unlink()
    preview = out_dir / "preview.mp3"
    pipe._ffmpeg(["-i", str(master_wav), "-codec:a", "libmp3lame",
                  "-b:a", "320k", str(preview)], "preview mp3")

    notes = [
        "performance: ONE invariant prompt, struck once as a seed "
        "take and extended only by audio continuation -- the model "
        "plays through every join. The takes are spliced DIRECTLY: "
        "no crossfade, no per-take RMS matching (there are no "
        "sections to match), no grid, no trim, no tempo surgery "
        "of any kind.",
        "absent by design: the Sigma binaural layer (excluded for "
        "test purity at the founder's order -- the v4b A/B "
        "acquitted it; its absence here is hygiene, not "
        "suspicion), any spine, any kit or sample, any "
        "synthesized voice, any second prompt.",
        "tempo: the performance chose its own clock. The prompt "
        "asked for energy and bounce, never a number; realized "
        "tempo stands measured -- globally and per 30 s window -- "
        "in the performance block. Drift is reported, not "
        "corrected.",
        "the performance itself is not transcribed in "
        "composition.abc: its transcription is a separate "
        "production, owed and marked owed -- never fabricated.",
        "loudness is K-weighted integrated, UNGATED (BS.1770 "
        "gating omitted in the proof build, stated not hidden).",
        "2 s tail fade + 5 ms head fade applied before mastering.",
    ]
    if spec.get("arpeggio"):
        notes.append(
            "arpeggio: the composed violin layer rides on a "
            "schedule derived from the MEASURED tempo (the "
            "performance leads, the dancer follows), swing 0.0 -- "
            "no grid was imposed on the performance to give the "
            "dancer one. Its notation is complete in "
            "composition.abc.")
    else:
        notes.append(
            "nothing rides: there is NO composed arpeggio layer "
            "in this run. The Paganini line stands in the prompt "
            "itself, and the performance played its own violin "
            "arpeggios as part of its body -- in tune, in phrase, "
            "or not at all; the ear will judge what the prompt "
            "bought. composition.abc notates nothing and marks "
            "the performance's transcription owed.")
    if single_session:
        notes.append(
            "single session: the whole chain was born in ONE "
            "bridge process; every continuation was conditioned "
            "on the bridge's in-memory predecessor; no take was "
            "resumed from disk, and the session guard verified "
            "the chain before the splice. "
            + (f"Voided attempts set aside before this strike: "
               f"{len(session_block['voided_attempts'])} "
               f"({', '.join(v['directory'] for v in session_block['voided_attempts'])})."
               if session_block["voided_attempts"] else
               "No prior attempt stood on the ground to void."))
    if n_warm:
        notes.append(
            f"warm-up: {n_warm} leading take(s) "
            f"({warmup_block['seconds_struck']} s) were struck "
            f"and DISCARDED -- their audio is nowhere in the "
            f"program. The warm-up's own measured tempo was "
            f"{warmup_block['tempo']['global_bpm']} BPM; the kept "
            f"program's windows stand in the performance block "
            f"for the lock-in question.")
    if not 180.0 <= total_seconds <= 210.0:
        notes.append(
            f"program length {total_seconds:.1f} s stands outside "
            f"the 3:00-3:30 aim of the brief -- the performance is "
            f"delivered at the length it honestly reached, as the "
            f"brief orders, not padded or cut to fit the aim.")
    if any(r.get("resumed") for r in render_by_index.values()):
        notes.append(
            "takes resumed from disk carry continued_from: null in "
            "this manifest -- the chain fact lives in the render "
            "that struck them, and the manifest does not pretend "
            "to remember what it did not witness.")

    manifest = {
        "title": spec["title"],
        "title_status": "working title",
        "dry_run": False,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "pipeline": "resonance.studio v1 (proof-of-concept build)",
        "spec": spec,
        "sections": take_reports,
        "render": {"model": render_model,
                   "wall_seconds_this_run": render_wall,
                   "resumed_segments":
                   [i for i in range(len(sections))
                    if render_by_index[i].get("resumed")],
                   "rendered_seconds_total":
                   sum(s["seconds"] for s in sections)},
        "program": {"seconds": round(total_seconds, 3),
                    "sample_rate": pipe.TARGET_SR, "channels": 2,
                    "bit_depth": 24},
        "performance": {
            "method": "one continuous performance: a seed take "
                      "extended only by audio continuation under "
                      "one invariant prompt; direct splices, "
                      "weighed",
            "invariant_prompt": prompt,
            "takes": perf["takes"],
            "take_seconds": perf["take_seconds"],
            "continue_seconds": perf["continue_seconds"],
            "session": session_block,
            "warmup": warmup_block,
            "kept_take_indices": kept_idx,
            "native_sample_rate": native_sr,
            "native_seconds": round(boundaries[-1] / native_sr, 3),
            "full_chain_native_seconds": full_chain_seconds,
            "joins": joins,
            "join_summary": join_summary,
            "realized_tempo": tempo_block,
            "arpeggio_schedule": schedule_block,
            "absent_by_design": [
                "sigma layer (test purity; acquitted by the v4b "
                "A/B)",
                "spine (synth or sampled)",
                "kit / one-shot samples of any kind",
                "synthesized voices",
                "per-section prompts, motif resets, section names "
                "in generation",
                "crossfade stitching of independent takes",
                "per-section RMS matching",
                "tempo forcing, grid trimming, time-stretching",
            ] + ([] if spec.get("arpeggio") else [
                "composed arpeggio layer (the Paganini line is "
                "generated INSIDE the performance, per the "
                "founder's ruling: if it isn't in the performance, "
                "it isn't in the track)",
            ]),
        },
        "spine": None,
        "arpeggio": arpeggio_report,
        "stereo": stereo_report,
        "sigma": {
            "absent": True,
            "intended_left_hz": None,
            "intended_right_hz": None,
            "measured_left_hz": None,
            "measured_right_hz": None,
            "measured_separation_hz": None,
            "gain_db": None,
            "gain_reference": "not struck in this run",
            "engine": "excluded for test purity (founder's "
                      "order); acquitted by the v4b A/B",
        },
        "master": master_report,
        "files": {
            "master_wav": {"path": str(master_wav),
                           "bytes": master_wav.stat().st_size},
            "preview_mp3": {"path": str(preview),
                            "bytes": preview.stat().st_size},
            "performance_32k_wav": {"path": str(native_path),
                                    "bytes": native_path.stat()
                                    .st_size},
            "performance_full_32k_wav":
                {"path": str(full_path),
                 "bytes": full_path.stat().st_size}
                if full_path is not None else None,
            "performance_48k_wav": {"path": str(bed48_path),
                                    "bytes": bed48_path.stat()
                                    .st_size},
            "composition_abc": str(out_dir / "composition.abc"),
            "spec_json": str(out_dir / "spec.json"),
            "render_log": str(out_dir / "render.log"),
        },
        "wall_seconds_total": round(time.time() - t_start, 2),
        "notes": notes,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    log(f"done in {manifest['wall_seconds_total']}s -> {master_wav}")
    return manifest


__all__ = [
    "assert_session_chain",
    "build_arp_schedule",
    "measure_joins",
    "onset_envelope",
    "produce_performance",
    "tempo_from_envelope",
    "void_prior_takes",
    "window_tempos",
    "write_composition_abc",
    "write_performance_sheet_abc",
]

# 93 -- Live, Love, and let Love, Live.
