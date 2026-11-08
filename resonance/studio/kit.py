# 93
# ---------------------------------------------------------------------
# kit.py -- the rendered kit: drum one-shots MusicGen STRIKES, the
# spine only places.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VIII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: build_kit() renders several short takes per voice
# through the SAME venv bridge the bed uses (render_musicgen.py),
# each prompted for ONE isolated hit on silence, then MEASURES every
# take -- onset regions, decay, tail silence, tonal residue, and for
# the 808s the struck pitch against its chord root -- and selects
# per voice on the numbers. The winner is trimmed to its hit,
# peak-set, resampled to the studio rate, and struck as a 24-bit
# WAV. Every take's metrics, the selection's basis, and the full
# provenance stand in kit_manifest.json beside the samples.
#
# DOCTRINE: the founder's ear has now condemned note-by-note
# SYNTHESIS three times ("sounds MIDI") and passed RENDERED audio
# every time. So the kit is rendered, never synthesized: the spine
# becomes a sampler, placing struck audio on the grid. Selection is
# by measurement, not by hope -- a take that loops, bleeds melody,
# or rings into the next bar loses on numbers the manifest prints.
# The 808's four roots are derived from the single best MEASURED
# take, replayed at the exact fractional rate ratio to each root
# (what every sampler on earth does) and the manifest SAYS so --
# source take, measured pitch, and shift per root; nothing is
# quietly synthesized, ever.
# ---------------------------------------------------------------------

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

from resonance.studio import pipeline as _pipeline
from resonance.studio import spine as _spine

KIT_SR = 48000               # the studio rate the kit is struck at
TAKE_SR = 32000              # MusicGen's native rate (takes land here)
PEAK_TARGET = 0.9            # selected hits are peak-set to this
TAKES_PER_VOICE = 4
DRUM_TAKE_SECONDS = 3.0
BASS_TAKE_SECONDS = 4.0
SEED_BASE = 5000

DRUM_VOICES = _spine.KIT_VOICES

# One hit, on silence, nothing else: the prompts say exactly that,
# several ways, because the model must have no excuse for company.
PROMPTS = {
    "kick": "a single isolated kick drum hit, one punchy drum strike "
            "on complete silence, dry studio drum sample, no music, "
            "no other sounds",
    "snare": "a single isolated snare drum hit, one crisp snare "
             "strike on complete silence, dry studio drum sample, "
             "no music, no other sounds",
    "clap": "a single isolated hand clap, one clap strike on "
            "complete silence, dry studio sample, no music, no "
            "other sounds",
    "closed_hat": "a single isolated closed hi-hat hit, one short "
                  "metallic tick on complete silence, dry studio "
                  "drum sample, no music, no other sounds",
    "open_hat": "a single isolated open hi-hat hit, one sizzling "
                "open hi-hat strike on complete silence, dry studio "
                "drum sample, no music, no other sounds",
    "rimshot": "a single isolated rimshot hit, one woody rim click "
               "on complete silence, dry studio drum sample, no "
               "music, no other sounds",
}

# Longest first hit (seconds) that may be loop-cut out of a looped
# take, per voice: a closed hat is a tick, a kick is a punch -- a
# "first hit" longer than its voice's nature is two hits merged
# or a ring, and cutting it would smuggle the loop into the kit.
FIRST_HIT_MAX_S = {"kick": 0.8, "snare": 1.2, "clap": 0.6,
                   "closed_hat": 0.5, "open_hat": 2.0,
                   "rimshot": 0.6, "bass808": 3.0}

# The 808's chord roots as the spine's cycle names them: the house
# root is F1 (MIDI 29); CHORD_CYCLE walks +0/+8/+3/+10 semitones.
BASS_ROOT_MIDI = _spine.DEFAULT_ROOT_MIDI
BASS_PITCH_NAMES = {29: "F", 32: "A flat", 37: "D flat", 39: "E flat"}


def bass_midis():
    """The four chord-root MIDIs the kit must carry, ascending."""
    return sorted({BASS_ROOT_MIDI + off for off in _spine.CHORD_CYCLE})


def _bass_prompt(midi):
    name = BASS_PITCH_NAMES[midi]
    return (f"a single deep 808 bass drum hit tuned to {name}, one "
            f"long sub bass strike on complete silence, dry studio "
            f"sample, no melody, no other sounds")


# ---------------------------------------------------------------------
# Measurement: the scales every take is weighed on.
# ---------------------------------------------------------------------

def _envelope_db(x, sr, hop_s=0.001):
    """Peak envelope in dB relative to the take's own peak.

    MECHANISM: max-abs in 1 ms hops, smoothed over ~8 ms, expressed
    in dB under the take peak (0 dB = the loudest instant). Every
    region/decay figure below is read off this one curve, so the
    numbers in the manifest share a single definition.
    """
    hop = max(1, int(round(hop_s * sr)))
    n = len(x) // hop
    if n == 0:
        return np.zeros(0), hop / sr
    env = np.max(np.abs(x[:n * hop].reshape(n, hop)), axis=1)
    k = max(1, int(round(0.008 / hop_s)))
    if k > 1:
        env = np.convolve(env, np.ones(k) / k, mode="same")
    peak = float(env.max()) if env.size else 0.0
    if peak <= 0.0:
        return np.full(n, -120.0), hop / sr
    db = 20.0 * np.log10(np.maximum(env, 1e-9) / peak)
    return db, hop / sr


def _hit_regions(db, dt):
    """Split the envelope into hit regions.

    MECHANISM: a region is a run above -30 dB; two runs belong to
    the SAME hit when the valley between them never falls below
    -45 dB (a drum's own body breathing), and to DIFFERENT hits
    when it does (silence -- or near it -- separates strikes).
    Returns [(start_idx, end_idx)] in envelope samples.
    """
    above = db >= -30.0
    runs = []
    i = 0
    n = len(db)
    while i < n:
        if above[i]:
            j = i
            while j + 1 < n and above[j + 1]:
                j += 1
            runs.append([i, j])
            i = j + 1
        else:
            i += 1
    merged = []
    for run in runs:
        if merged:
            gap = db[merged[-1][1] + 1:run[0]]
            if gap.size and float(gap.min()) > -45.0:
                merged[-1][1] = run[1]
                continue
        merged.append(list(run))
    return [(a, b) for a, b in merged]


def _chroma_tonality(x, sr):
    """Largest pitch-class share of the window's spectrum, 0..1.

    MECHANISM: fold the magnitude spectrum (55 Hz..4 kHz) into the
    twelve pitch classes; noise spreads its energy across all
    twelve, a pitched residue concentrates it. The share of the
    strongest class is the residue's fingerprint -- report it, and
    let melodic bleed convict itself.
    """
    if x.size == 0:
        return 0.0
    n_pad = _pipeline._fast_len(x.size)
    spec = np.abs(np.fft.rfft(x * np.hanning(x.size), n=n_pad))
    freqs = np.fft.rfftfreq(n_pad, d=1.0 / sr)
    band = (freqs >= 55.0) & (freqs <= 4000.0)
    if not np.any(band):
        return 0.0
    midi = 69.0 + 12.0 * np.log2(freqs[band] / 440.0)
    classes = np.floor(midi + 0.5).astype(int) % 12
    energy = spec[band] ** 2
    chroma = np.zeros(12)
    np.add.at(chroma, classes, energy)
    total = float(chroma.sum())
    return float(chroma.max() / total) if total > 0 else 0.0


def _fundamental_cents(x, sr, target_midi):
    """(measured Hz, cents from target) of the window's low peak.

    MECHANISM: FFT peak in 25..140 Hz with parabolic interpolation
    on the log magnitude -- an 808's sustained body is a near-sine,
    so the peak IS the pitch, read to a few cents.
    """
    from resonance.core.notes import midi_to_freq
    if x.size == 0:
        return 0.0, None
    n_pad = _pipeline._fast_len(x.size * 4)
    spec = np.abs(np.fft.rfft(x * np.hanning(x.size), n=n_pad))
    freqs = np.fft.rfftfreq(n_pad, d=1.0 / sr)
    band = (freqs >= 25.0) & (freqs <= 140.0)
    idx = np.where(band)[0]
    if idx.size == 0:
        return 0.0, None
    k = int(idx[np.argmax(spec[idx])])
    delta = 0.0
    if 0 < k < len(spec) - 1:
        a, b, c = (math.log(spec[k - 1] + 1e-12),
                   math.log(spec[k] + 1e-12),
                   math.log(spec[k + 1] + 1e-12))
        den = a - 2.0 * b + c
        delta = 0.5 * (a - c) / den if den != 0 else 0.0
    hz = (k + delta) * sr / n_pad
    target = midi_to_freq(int(target_midi))
    cents = 1200.0 * math.log2(hz / target) if hz > 0 else None
    return float(hz), (float(cents) if cents is not None else None)


def measure_take(x, sr, voice, target_midi=None):
    """Weigh one take. Returns the metrics dict the manifest prints.

    MECHANISM: envelope -> hit regions -> the first hit's decay
    (last crossing of -42 dB before the next hit or the end) ->
    the tail beyond the decay (silence is the requirement) -> the
    decay window's tonality (drums) or struck pitch (the 808s).
    `clean_single` is the gate verdict; `trimmable` says a loopy
    take still holds one clean hit in front of a silent gap.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        x = x.mean(axis=1)
    db, dt = _envelope_db(x, sr)
    peak = float(np.max(np.abs(x))) if x.size else 0.0
    regions = _hit_regions(db, dt)
    out = {
        "peak_dbfs": round(20.0 * math.log10(peak), 2) if peak > 0
        else -120.0,
        "hit_regions": len(regions),
        "onset_s": None, "decay_end_s": None, "hit_length_s": None,
        "next_onset_s": None, "tail_rms_db_rel_peak": None,
        "tonality": None,
        "fundamental_hz": None, "cents_from_target": None,
        "sustain_db": None, "env_end_db": None,
        "decayed_within_take": False, "loop_cut": False,
        "clean_single": False, "trimmable": False,
    }
    if not regions or peak <= 0:
        return out
    duration = len(db) * dt
    out["env_end_db"] = round(float(db[-1]), 1) if db.size else None
    if len(regions) > 1:
        out["next_onset_s"] = round(regions[1][0] * dt, 3)
    a, b = regions[0]
    onset = a * dt
    # Decay end: the last envelope point above -42 dB, bounded by
    # the second hit's start when there is one.
    limit = regions[1][0] if len(regions) > 1 else len(db)
    seg = db[a:limit]
    over = np.where(seg > -42.0)[0]
    decay_idx = a + int(over[-1]) if over.size else b
    decay_end = decay_idx * dt
    out["onset_s"] = round(onset, 3)
    out["decay_end_s"] = round(decay_end, 3)
    out["hit_length_s"] = round(decay_end - onset, 3)
    # The tail: everything 50 ms past the decay, weighed against
    # the take's peak. A clean one-shot leaves ~nothing there.
    # When the decay runs to the take's end there IS no beyond --
    # the honest tail is then the take's own last 100 ms, not a
    # defaulted silence: a hit still ringing when the tape stops
    # must not be graded as if it had decayed.
    tail_from = int((decay_end + 0.05) * sr)
    if tail_from < x.size:
        tail = x[tail_from:]
    else:
        tail = x[-max(1, int(0.10 * sr)):]
    rms = float(np.sqrt(np.mean(tail ** 2))) if tail.size else 0.0
    out["tail_rms_db_rel_peak"] = round(
        20.0 * math.log10(rms / peak), 2) if rms > 0 else -120.0
    # Did the hit actually END inside the take? The decay point
    # must land clear of the final samples; a decay point AT the
    # end means the tape stopped mid-ring.
    out["decayed_within_take"] = bool(decay_end < duration - 0.05)
    # Sustain: the envelope's mean level 0.3..1.1 s after the
    # onset. A struck hit FALLS; a wash/texture the model laid
    # down instead of a hit stays up. This is the gate the first
    # build lacked -- several "clean" takes never decayed at all.
    w0 = a + int(0.3 / dt)
    w1 = min(len(db), a + int(1.1 / dt))
    if w1 > w0:
        out["sustain_db"] = round(float(np.mean(db[w0:w1])), 1)
    # A second hit convicts the take as a loop UNLESS the first hit
    # fully decayed into a >=120 ms near-silent gap before it --
    # then the first hit can simply be cut out of it.
    if len(regions) > 1:
        gap = db[decay_idx:regions[1][0]]
        out["trimmable"] = bool(
            gap.size * dt >= 0.120 and float(gap.min()) < -45.0)
    win = x[int(onset * sr):int(decay_end * sr)]
    if target_midi is not None:
        lo = int(0.10 * sr)
        hi = min(win.size, int(1.20 * sr))
        hz, cents = _fundamental_cents(win[lo:hi], sr, target_midi) \
            if hi > lo else (0.0, None)
        out["fundamental_hz"] = round(hz, 2) if hz else None
        out["cents_from_target"] = round(cents, 1) \
            if cents is not None else None
    else:
        # Skip the strike's own body (a quarter second, or 40% of
        # a short hit -- a hat is gone before 0.25 s and must still
        # be weighed), then judge what RINGS: residue, not attack.
        lo = min(int(0.25 * sr), int(0.4 * win.size))
        out["tonality"] = round(
            _chroma_tonality(win[lo:], sr), 3) if win.size > lo else None
    tail_ok = (out["tail_rms_db_rel_peak"] is not None
               and out["tail_rms_db_rel_peak"] <= -32.0)
    sustain_ok = (out["sustain_db"] is not None
                  and out["sustain_db"] <= -20.0)
    # Loop-cut eligibility: a take that loops still surrenders one
    # honest hit when the FIRST hit decays fast and fully before
    # the next strike -- the cut then holds exactly one hit, and
    # cut_hit's end clamps at the next onset to keep it that way.
    max_first = FIRST_HIT_MAX_S.get(voice, 1.0)
    out["loop_cut"] = bool(
        len(regions) > 1
        and out["hit_length_s"] is not None
        and out["hit_length_s"] <= max_first
        and out["sustain_db"] is not None
        and out["sustain_db"] <= -25.0)
    if target_midi is not None:
        pitch_ok = (out["cents_from_target"] is not None
                    and abs(out["cents_from_target"]) <= 60.0)
        out["clean_single"] = bool(
            len(regions) == 1 and tail_ok and pitch_ok
            and out["decayed_within_take"])
    else:
        tone_ok = (out["tonality"] is not None
                   and out["tonality"] <= 0.55)
        out["clean_single"] = bool(
            len(regions) == 1 and tail_ok and tone_ok
            and out["decayed_within_take"] and sustain_ok)
    return out


def _take_score(metrics, target_midi=None):
    """Rank key for one take: lower is better, gates dominate.

    MECHANISM: category first (clean single < trimmable < the
    rest), then the voice's own sin (pitch error for the 808s,
    tonality for the drums), then tail dirt, then hit length (a
    tighter hit wins ties -- it leaves the grid cleaner).
    """
    if metrics["clean_single"]:
        cat = 0
    elif metrics.get("loop_cut") or metrics["trimmable"]:
        cat = 1
    elif metrics["hit_regions"] == 1:
        cat = 2
    else:
        cat = 3
    tail = metrics["tail_rms_db_rel_peak"]
    tail = 0.0 if tail is None else tail
    sustain = metrics.get("sustain_db")
    sustain = 0.0 if sustain is None else sustain
    length = metrics["hit_length_s"] or 9.9
    if target_midi is not None:
        # The 808's sin is pitch: it outranks shape.
        sin = abs(metrics["cents_from_target"]) \
            if metrics["cents_from_target"] is not None else 999.0
        return (cat, round(float(sin), 3), round(float(tail), 2),
                round(float(sustain), 1), round(float(length), 3))
    # A drum's sin is SHAPE -- a hit that never falls is not a
    # hit, however clean its spectrum: tail and sustain outrank
    # tonality. (The first field's open hats taught this: the
    # scorer crowned a 3-second swell over a decaying strike on
    # a 0.07 tonality margin.)
    sin = metrics["tonality"] if metrics["tonality"] is not None \
        else 1.0
    return (cat, round(float(tail), 2), round(float(sustain), 1),
            round(float(sin), 3), round(float(length), 3))


# ---------------------------------------------------------------------
# Sample surgery: cut the hit out of the winning take, at pitch if
# the sampler must carry it there.
# ---------------------------------------------------------------------

def _resample_fft(x, sr_in, sr_out):
    """Band-limited resample by spectral zero-padding (numpy only)."""
    x = np.asarray(x, dtype=np.float64)
    n_out = int(round(len(x) * sr_out / sr_in))
    if n_out == len(x):
        return x.copy()
    spec = np.fft.rfft(x)
    out_spec = np.zeros(n_out // 2 + 1, dtype=complex)
    m = min(spec.size, out_spec.size)
    out_spec[:m] = spec[:m]
    return np.fft.irfft(out_spec, n=n_out) * (n_out / len(x))


def _rate_shift(x, semitones):
    """Replay a sample `semitones` up: a sampler's pitch, honestly.

    MECHANISM: linear interpolation on the resample grid -- for a
    near-sine sub voice the interpolation error lives far above
    the signal band. Duration scales by the inverse ratio, as a
    hardware sampler's does.
    """
    ratio = 2.0 ** (float(semitones) / 12.0)
    n_out = int(round(len(x) / ratio))
    pos = np.arange(n_out) * ratio
    return np.interp(pos, np.arange(len(x)), x)


def cut_hit(x, sr, metrics, tail_pad_s=0.12):
    """Cut [onset, decay_end + pad] out of a take, attack intact.

    MECHANISM: the start walks back from the measured onset to the
    last envelope point under -50 dB, so the transient's first
    whisper is kept; the end keeps a short natural tail past the
    -42 dB decay point, closed with a 5 ms fade so the cut itself
    never clicks.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        x = x.mean(axis=1)
    db, dt = _envelope_db(x, sr)
    onset_idx = int(float(metrics["onset_s"]) / dt)
    start = onset_idx
    while start > 0 and db[start] > -50.0:
        start -= 1
    start_s = max(0.0, start * dt - 0.001)
    end_s = min(len(x) / sr,
                float(metrics["decay_end_s"]) + tail_pad_s)
    # A loop-cut must hold ONE hit: when the take strikes again,
    # the pad stops 5 ms short of the next onset, however close
    # that onset sits -- the second hit never enters the sample.
    nxt = metrics.get("next_onset_s")
    if nxt is not None:
        end_s = min(end_s, float(nxt) - 0.005)
    hit = x[int(start_s * sr):int(end_s * sr)].copy()
    fade = min(hit.size, max(1, int(0.005 * sr)))
    if hit.size > fade:
        hit[-fade:] *= np.linspace(1.0, 0.0, fade)
    return hit


# ---------------------------------------------------------------------
# The build: render the takes, weigh them, strike the kit.
# ---------------------------------------------------------------------

def take_plan(takes_per_voice=TAKES_PER_VOICE, seed_base=SEED_BASE):
    """The full take list: (key, voice, prompt, seconds, seed, file).

    MECHANISM: deterministic order and seeds, so a resumed build
    asks the bridge for exactly the takes it asked for before the
    lights went out -- same plan, same seeds, same files.
    """
    plan = []
    i = 0
    for voice in DRUM_VOICES:
        for t in range(takes_per_voice):
            plan.append({
                "key": f"{voice}_t{t}", "voice": voice,
                "prompt": PROMPTS[voice],
                "seconds": DRUM_TAKE_SECONDS,
                "seed": seed_base + i,
                "file": f"{voice}_t{t}.wav",
                "target_midi": None})
            i += 1
    for midi in bass_midis():
        for t in range(takes_per_voice):
            plan.append({
                "key": f"bass{midi}_t{t}", "voice": "bass808",
                "prompt": _bass_prompt(midi),
                "seconds": BASS_TAKE_SECONDS,
                "seed": seed_base + i,
                "file": f"bass{midi}_t{t}.wav",
                "target_midi": midi})
            i += 1
    # Second wave, appended last so the first wave's seeds stand
    # as recorded: the hats came back from the first field as
    # sustained textures, not hits (every closed-hat take rang
    # for the whole take). New seeds; two closed hats asked for
    # as a sound effect rather than as music.
    extra = [
        ("closed_hat", PROMPTS["closed_hat"]),
        ("closed_hat", "one single metallic tick sound effect, a "
                       "very short dry click, then complete "
                       "silence, no music, no beat"),
        ("closed_hat", PROMPTS["closed_hat"]),
        ("closed_hat", "a single short closed hi-hat tick, dry "
                       "and sharp, one hit and then complete "
                       "silence, no music, no loop, no beat"),
        ("open_hat", "a single isolated open hi-hat hit, one dry "
                     "sizzling strike decaying away to complete "
                     "silence, no music, no beat, no other sounds"),
        ("open_hat", PROMPTS["open_hat"]),
    ]
    counts = {v: takes_per_voice for v in DRUM_VOICES}
    for voice, prompt in extra:
        t = counts[voice]
        counts[voice] += 1
        plan.append({
            "key": f"{voice}_t{t}", "voice": voice,
            "prompt": prompt,
            "seconds": DRUM_TAKE_SECONDS,
            "seed": seed_base + i,
            "file": f"{voice}_t{t}.wav",
            "target_midi": None})
        i += 1
    return plan


def select_kit(takes_dir, plan):
    """Measure every take on disk and select per voice.

    Returns (selection, all_metrics): selection maps a kit voice
    (drum name, or f"bass{midi}") to the winning take's record --
    {file, metrics, basis} -- where basis states in words why it
    won: "clean single hit" / "first hit cut from a looped take" /
    "best of an imperfect field". Missing or silent takes are
    measured as absent and can never win.
    """
    takes_dir = Path(takes_dir)
    by_voice = {}
    for item in plan:
        path = takes_dir / item["file"]
        voice_key = item["voice"] if item["target_midi"] is None \
            else f"bass{item['target_midi']}"
        rec = {"file": item["file"], "seed": item["seed"],
               "prompt": item["prompt"], "metrics": None}
        if path.exists():
            arr, sr = _pipeline.read_wav_pcm(path)
            rec["metrics"] = measure_take(arr, sr, item["voice"],
                                          item["target_midi"])
        by_voice.setdefault(voice_key, []).append(rec)
    selection = {}
    all_metrics = {}
    for voice_key, recs in sorted(by_voice.items()):
        target = None
        if voice_key.startswith("bass"):
            target = int(voice_key[4:])
        scored = []
        for rec in recs:
            m = rec["metrics"]
            if m is None or m["hit_regions"] == 0 \
                    or m["peak_dbfs"] <= -20.0:
                continue
            scored.append((_take_score(m, target), rec))
        all_metrics[voice_key] = recs
        if not scored:
            continue
        scored.sort(key=lambda pair: pair[0])
        best = scored[0][1]
        m = best["metrics"]
        if m["clean_single"]:
            basis = "clean single hit"
        elif m.get("loop_cut") or m["trimmable"]:
            basis = "first hit cut from a looped take"
        elif m["hit_regions"] == 1:
            basis = "best of an imperfect field (single hit, flaws " \
                    "in the metrics)"
        else:
            basis = "best of an imperfect field"
        selection[voice_key] = {**best, "basis": basis}
    return selection, all_metrics


def exact_midi_of_hz(hz):
    """A measured frequency as a fractional MIDI note number."""
    return 69.0 + 12.0 * math.log2(float(hz) / 440.0)


def pick_bass_source(all_metrics):
    """Choose THE 808 take the four chord roots are derived from.

    MECHANISM: every bass take of every prompted pitch is a
    candidate -- the model answers pitch names loosely (the
    field's "E flat" takes measured anywhere from B1 to G2), so
    the prompted pitch is no credential; the MEASURED pitch is.
    Tier 0 is a single hit that decayed inside its take into a
    tail at or below -45 dB. Within a tier, the take measuring
    closest to the house root F wins: the root carries the cycle,
    and it should ride the smallest shift. Returns the winning
    record plus its measured Hz and exact fractional MIDI, or
    None when no bass take measured a fundamental at all.
    """
    best = None
    for key, recs in sorted(all_metrics.items()):
        if not key.startswith("bass"):
            continue
        for rec in recs:
            m = rec["metrics"]
            if not m or not m.get("fundamental_hz"):
                continue
            tier = 0 if (
                m["hit_regions"] == 1
                and m.get("decayed_within_take")
                and m["tail_rms_db_rel_peak"] is not None
                and m["tail_rms_db_rel_peak"] <= -45.0) else 1
            exact = exact_midi_of_hz(m["fundamental_hz"])
            rank = (tier, round(abs(exact - BASS_ROOT_MIDI), 2),
                    m["tail_rms_db_rel_peak"] or 0.0)
            if best is None or rank < best[0]:
                best = (rank, {**rec, "exact_midi": exact})
    return best[1] if best else None


def _take_file_ok(path, seconds):
    """True when a previously rendered TAKE file is whole.

    MECHANISM: the pipeline's segment check demands the frame
    count within 2% of nominal, but MusicGen's token rounding
    lands a 3 s take at ~2.94 s -- just outside -- so every kit
    rebuild re-rendered the whole drum field. A take is weighed
    by measurement before it can win anything, so its wholeness
    bar is honestly looser: header parses, native rate, at least
    96% of the brief (a mid-write truncation falls far shorter).
    """
    import wave
    try:
        with wave.open(str(path), "rb") as w:
            frames, sr = w.getnframes(), w.getframerate()
    except Exception:
        return False
    return sr == TAKE_SR and 0.96 * seconds <= frames / sr \
        <= 1.02 * seconds


def _voice_usable(metrics):
    """The bar a selected take must clear to enter the kit as-is.

    A clean single, a loop-cut, or a trimmable first hit clears
    it outright; failing those, the hit must at least have
    decayed inside its take to a low sustain. A take that fails
    every branch is a texture wearing the voice's name -- the
    closed hats' whole field failed here -- and the build then
    takes the license-clean fallback when one is provided.
    """
    if metrics is None:
        return False
    if metrics["clean_single"] or metrics.get("loop_cut") \
            or metrics["trimmable"]:
        return True
    return bool(metrics.get("decayed_within_take")
                and metrics.get("sustain_db") is not None
                and metrics["sustain_db"] <= -20.0)


def build_kit(run_dir, takes_per_voice=TAKES_PER_VOICE,
              seed_base=SEED_BASE, log=None):
    """Render, weigh, and strike the kit under `run_dir`.

    Layout: takes in run_dir/kitbuild/, the struck kit in
    run_dir/kit/ (one WAV per voice + kit_manifest.json). Resume
    law applies to takes exactly as it does to bed sections: a
    whole take on disk is never re-rendered.
    """
    log = log or (lambda msg: print(f"[kit] {msg}", file=sys.stderr,
                                    flush=True))
    run_dir = Path(run_dir)
    takes_dir = run_dir / "kitbuild"
    kit_dir = run_dir / "kit"
    takes_dir.mkdir(parents=True, exist_ok=True)
    kit_dir.mkdir(parents=True, exist_ok=True)
    plan = take_plan(takes_per_voice, seed_base)

    todo = []
    for idx, item in enumerate(plan):
        path = takes_dir / item["file"]
        if path.exists() and _take_file_ok(path, item["seconds"]):
            log(f"take {item['file']} already rendered -- resuming")
        else:
            todo.append(idx)
    if todo:
        job = {"out_dir": str(takes_dir), "segments": [
            {"index": idx, "prompt": plan[idx]["prompt"],
             "seconds": plan[idx]["seconds"],
             "seed": plan[idx]["seed"], "file": plan[idx]["file"]}
            for idx in todo]}
        log(f"rendering {len(todo)} one-shot takes via the bridge...")
        _pipeline._run_bridge(job, run_dir, log)

    selection, all_metrics = select_kit(takes_dir, plan)
    missing = [v for v in DRUM_VOICES if v not in selection]
    if missing:
        raise RuntimeError(
            f"kit: no usable take for {missing} -- isolation failed "
            f"for those voices (see the metrics); the CC0 fallback "
            f"is a human decision, not a silent substitution")

    # The 808s: ONE measured take carries all four roots. The
    # first build shifted whole semitones from a take that itself
    # measured -185 cents from F, which would have parked the
    # whole bass cycle nearly two semitones under the bed's key.
    # The sampler's honest road is an EXACT shift: measure the
    # best take's true pitch, then shift by the precise fractional
    # semitones to each root -- one rendered timbre, every root
    # landed on pitch, stated per voice in the manifest.
    finals = {}   # kit-relative filename -> float64 mono at TAKE_SR
    sel_report = {}
    fallback_dir = run_dir / "kit-fallback"
    for voice in DRUM_VOICES:
        rec = selection[voice]
        fb_wav = fallback_dir / f"{voice}.wav"
        fb_json = fallback_dir / f"{voice}.provenance.json"
        if not _voice_usable(rec["metrics"]) \
                and fb_wav.exists() and fb_json.exists():
            # The founder's own fallback clause, mechanized: when
            # rendered isolation fails a voice, a license-clean
            # (CC0 / royalty-free) one-shot may stand in its place
            # -- measured by the same scales, provenance stated,
            # never passed off as a render.
            prov = json.loads(fb_json.read_text(encoding="utf-8"))
            arr, sr = _pipeline.read_wav_pcm(fb_wav)
            arr = np.asarray(arr, dtype=np.float64)
            if arr.ndim == 2:
                arr = arr.mean(axis=1)
            m = measure_take(arr, sr, voice)
            hit = cut_hit(arr, sr, m) if m["hit_regions"] else arr
            finals[f"{voice}.wav"] = _resample_fft(hit, sr, TAKE_SR)
            sel_report[voice] = {
                "source_take": f"kit-fallback/{voice}.wav",
                "seed": None,
                "basis": "license-clean fallback -- rendered "
                         "isolation failed for this voice (every "
                         "take in all_takes failed the usability "
                         "bar)",
                "metrics": m,
                "provenance": prov["provenance"],
                "fallback": prov}
            log(f"{voice}: rendered field unusable -- "
                f"license-clean fallback stands in")
            continue
        arr, sr = _pipeline.read_wav_pcm(takes_dir / rec["file"])
        finals[f"{voice}.wav"] = cut_hit(arr, sr, rec["metrics"])
        sel_report[voice] = {"source_take": rec["file"],
                             "seed": rec["seed"],
                             "basis": rec["basis"],
                             "metrics": rec["metrics"],
                             "provenance": "rendered one-shot "
                             "(facebook/musicgen-small, isolated-hit "
                             "prompt)"}
    src = pick_bass_source(all_metrics)
    if src is None:
        raise RuntimeError(
            "kit: no 808 take measured a fundamental -- the bass "
            "has no source to derive from (see the metrics)")
    arr, sr = _pipeline.read_wav_pcm(takes_dir / src["file"])
    src_hit = cut_hit(arr, sr, src["metrics"])
    src_hz = src["metrics"]["fundamental_hz"]
    for midi in bass_midis():
        key = f"bass{midi}"
        shift = midi - src["exact_midi"]
        finals[f"bass{midi}.wav"] = (
            _rate_shift(src_hit, shift) if abs(shift) > 1e-9
            else src_hit.copy())
        sel_report[key] = {
            "source_take": src["file"], "seed": src["seed"],
            "basis": "derived from the best measured 808 take by "
                     "exact rate shift",
            "metrics": src["metrics"],
            "shift_semitones": round(shift, 3),
            "source_fundamental_hz": src_hz,
            "provenance": f"rendered one-shot {src['file']} "
                          f"(measured {src_hz} Hz = MIDI "
                          f"{src['exact_midi']:.2f}) replayed at "
                          f"{shift:+.2f} semitones (exact sampler "
                          f"rate shift) to "
                          f"{BASS_PITCH_NAMES[midi]}; one rendered "
                          f"timbre carries all four roots, each "
                          f"landed on true pitch"}

    # Strike the finals: peak-set, resample to the studio rate,
    # written 24-bit by the bridge's soundfile hand.
    npy_paths = []
    finalize = []
    for name, arr in sorted(finals.items()):
        arr = _resample_fft(arr, TAKE_SR, KIT_SR)
        peak = float(np.max(np.abs(arr))) if arr.size else 0.0
        if peak > 0:
            arr = arr * (PEAK_TARGET / peak)
        npy = kit_dir / f"_{name}.npy"
        np.save(npy, np.asarray(arr, dtype=np.float32).reshape(-1, 1))
        npy_paths.append(npy)
        finalize.append({"npy": str(npy), "out": str(kit_dir / name),
                         "sample_rate": KIT_SR, "subtype": "PCM_24"})
    _pipeline._run_bridge({"finalize": finalize}, run_dir, log)
    for npy in npy_paths:
        npy.unlink()

    manifest = {
        "kit": "rendered one-shot library (RESONANTIA studio kit)",
        "model": "facebook/musicgen-small",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                     time.gmtime()),
        "sample_rate": KIT_SR,
        "peak_target": PEAK_TARGET,
        "voices": sel_report,
        "all_takes": {k: [{"file": r["file"], "seed": r["seed"],
                           "metrics": r["metrics"]} for r in recs]
                      for k, recs in sorted(all_metrics.items())},
        "files": {name: str(kit_dir / name) for name in finals},
        "doctrine": "every sample is rendered audio (MusicGen "
                    "one-shot takes, selected by measurement); the "
                    "spine places samples and synthesizes nothing. "
                    "The four 808 roots are one measured rendered "
                    "take replayed at exact fractional rate shifts, "
                    "stated per voice above.",
    }
    (kit_dir / "kit_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    log(f"kit struck: {len(finals)} samples in {kit_dir}")
    return manifest


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="resonance.studio.kit")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--takes", type=int, default=TAKES_PER_VOICE)
    ap.add_argument("--seed-base", type=int, default=SEED_BASE)
    args = ap.parse_args(argv)
    manifest = build_kit(args.run_dir, args.takes, args.seed_base)
    print(json.dumps({"ok": True,
                      "voices": sorted(manifest["voices"]),
                      "files": manifest["files"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# 93 -- Live, Love, and let Love, Live.
