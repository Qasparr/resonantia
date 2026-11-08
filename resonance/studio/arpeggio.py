# 93
# ---------------------------------------------------------------------
# arpeggio.py -- the dancer: a composed violin arpeggio over the bed.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VIII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: when a studio spec carries an "arpeggio" block (and a
# spine -- this composition is written in bars), this module composes
# a violin-voice arpeggio from the SOLFEGGIO LADDER, phrases it in
# Fibonacci lengths (1-1-2-3-5-8, the house figure first notated in
# the Proven Road's composition sheet), voices it with an engine
# violin (a harmonic stack through body/brilliance formants), bends
# its pitch contour with the Tools Wing's humanizer (micro-drift,
# vibrato, scoops -- vocal.humanize_contour, an instrument контур is
# a contour), and sets it moving in the stereo field with
# resonance.spatial.orbit -- a slow lap, so it dances instead of
# standing in the middle of the room.
#
# DOCTRINE: Proof No. 2's founder verdict named two wounds: the bed
# was a Frankenstein collage, and the Paganini arpeggio the founder
# ordered was ABSENT -- the Sigma ground is a bed of pure tones at
# -28 dB, not a dancer. This layer is the answer to the second
# wound: a composed voice, at musical level, whose every note is
# written (composition.abc carries the figure and its realizations;
# the manifest carries the inventory). The ladder is played at its
# equal-tempered approximations, exactly as the Proven Road sheet
# doctrines them -- the carriers themselves (396/417/528/639/741/
# 852 Hz) belong to the Sigma ground; the cents each carrier stands
# from its staff pitch are documented in LADDER and the manifest,
# never smoothed away.
# ---------------------------------------------------------------------

import math

import numpy as np

from resonance import grid
from resonance.core.notes import midi_to_freq
from resonance.spatial.orbit import orbit
from resonance.vocal import humanize_contour

STEPS_PER_BAR = 16

# The solfeggio ladder as this house plays it: (syllable, carrier Hz,
# staff MIDI). The staff pitches are the nearest equal-tempered
# approximations, per the Proven Road composition doctrine:
#   UT 396 -> G4, RE 417 -> G#4, MI 528 -> C5, FA 639 -> Eb5,
#   SOL 741 -> F#5, LA 852 -> G#5.
# cents_offset(carrier, midi) states how far the true carrier stands
# from the staff pitch -- FA and LA stand ~+45 cents sharp, the
# ladder's wide steps, and the record says so.
LADDER = (
    ("UT", 396.0, 67),
    ("RE", 417.0, 68),
    ("MI", 528.0, 72),
    ("FA", 639.0, 75),
    ("SOL", 741.0, 78),
    ("LA", 852.0, 80),
)

# ABC tokens for the ladder's staff pitches (treble, octave 4/5),
# the same spellings the Proven Road sheet uses.
ABC_TOKENS = {67: "G", 68: "^G", 72: "c", 75: "_e", 78: "^f", 80: "^g"}

# The figure's phrase lengths: Fibonacci, climbing the ladder
# cyclically -- phrase k takes the next FIBONACCI_PHRASES[k] ladder
# notes from where the last phrase stopped. One pass is the cell:
# 20 notes, G | ^G | c _e | ^f ^g G | ^G c _e ^f ^g | G ^G c _e
# ^f ^g G ^G, exactly as first notated in the Proven Road sheet.
FIBONACCI_PHRASES = (1, 1, 2, 3, 5, 8)

# Cell positions where phrases begin (cumulative phrase lengths):
# the accents of the figure live here.
PHRASE_STARTS = (0, 1, 2, 4, 7, 12)

# The bariolage pedal: MI (C5), the ladder's middle rung -- the
# "open string" the figure alternates against, Paganini's device.
PEDAL_MIDI = 72

MODES = ("runs", "bariolage", "bariolage16", "statement",
         "statement_fade", "mute")

# Per-mode section gain (before the layer's RMS match to the bed):
# the dancer is featured on the hooks and the feature slot, and
# steps back under the verses -- it accompanies, it does not shout
# over the vocal chairs.
MODE_GAIN = {"runs": 1.0, "bariolage": 0.7, "bariolage16": 0.85,
             "statement": 0.5, "statement_fade": 0.5, "mute": 0.0}

DEFAULT_LEVEL_DB = -9.0
DEFAULT_ORBIT_HZ = 0.03
DEFAULT_STRENGTH = 1.0

# The violin's harmonic recipe: amplitudes ~1/k^0.9 for k = 1..10,
# struck per note with a fresh phase -- a bowed string re-articulates,
# it does not phase-lock across notes.
_HARMONICS = tuple(1.0 / (k ** 0.9) for k in range(1, 11))


def cents_offset(carrier_hz, midi):
    """Cents the true carrier stands from its staff pitch.

    MECHANISM: computed from the unrounded pitch -- 69 + 12*log2
    (f/440) -- because resonance.core.notes.freq_to_midi rounds to
    the nearest staff note, which would erase exactly the offset
    this number exists to state.
    """
    exact = 69.0 + 12.0 * math.log2(float(carrier_hz) / 440.0)
    return (exact - float(midi)) * 100.0


def ladder_inventory():
    """The six rungs, documented: syllable, carrier, staff, offset."""
    return [{
        "syllable": name, "carrier_hz": carrier, "midi": midi,
        "staff_hz": round(midi_to_freq(midi), 2),
        "cents_offset": round(cents_offset(carrier, midi), 1),
        "abc": ABC_TOKENS[midi],
    } for name, carrier, midi in LADDER]


def figure_cell():
    """The 20-note figure: ladder indices in Fibonacci phrases."""
    cell = []
    pos = 0
    for length in FIBONACCI_PHRASES:
        for _ in range(length):
            cell.append(pos % len(LADDER))
            pos += 1
    return cell


# ---------------------------------------------------------------------
# Spec handling.
# ---------------------------------------------------------------------

def normalize_arpeggio_spec(raw, default_seed=93):
    """Validate a spec's "arpeggio" block; return the normalized copy.

    MECHANISM: same contract style as the rest of the studio --
    every refusal names its field. level_db is the layer's station
    relative to the bed's RMS (it is a voice IN the mix, so the
    range stops at parity); orbit_hz is the spatial lap rate;
    strength scales the humanizer; mode_overrides maps a spine
    section INDEX (as a string, JSON's way) to a mode, outranking
    the density map for that section.
    """
    if not isinstance(raw, dict):
        raise ValueError("arpeggio: must be an object")
    level_db = float(raw.get("level_db", DEFAULT_LEVEL_DB))
    if not -30.0 <= level_db <= 0.0:
        raise ValueError(
            f"arpeggio.level_db: {level_db} outside -30..0")
    orbit_hz = float(raw.get("orbit_hz", DEFAULT_ORBIT_HZ))
    if not 0.005 <= orbit_hz <= 0.5:
        raise ValueError(
            f"arpeggio.orbit_hz: {orbit_hz} outside 0.005..0.5")
    strength = float(raw.get("strength", DEFAULT_STRENGTH))
    if not 0.0 <= strength <= 2.0:
        raise ValueError(
            f"arpeggio.strength: {strength} outside 0..2")
    seed = raw.get("seed")
    seed = int(default_seed if seed is None else seed)
    overrides = {}
    raw_over = raw.get("mode_overrides") or {}
    if not isinstance(raw_over, dict):
        raise ValueError("arpeggio.mode_overrides: must be an object")
    for key, mode in raw_over.items():
        try:
            idx = int(key)
        except (TypeError, ValueError):
            raise ValueError(
                f"arpeggio.mode_overrides: key {key!r} is not a "
                f"section index")
        if str(mode) not in MODES:
            raise ValueError(
                f"arpeggio.mode_overrides[{key!r}]: {mode!r} not "
                f"one of {MODES}")
        overrides[idx] = str(mode)
    return {"level_db": level_db, "orbit_hz": orbit_hz,
            "strength": strength, "seed": seed,
            "mode_overrides": overrides}


def mode_for_section(index, section, overrides=None):
    """The arpeggio mode one spine section is realized in.

    MECHANISM: the density map, the arrangement's own logic --
    full and open sections (hooks, the feature slot) take the fast
    RUNS; driving verses take BARIOLAGE (the figure alternating
    with the pedal, air between the notes); the third verse, the
    biggest chair, takes the same device at 16ths; sparse sections
    take the STATEMENT (the figure spoken slowly, phrases held);
    the outro's statement fades. An explicit override outranks the
    map, always.
    """
    if overrides and index in overrides:
        return overrides[index]
    name = str(section.get("name", ""))
    density = str(section.get("density", "driving"))
    if density == "sparse":
        return "statement_fade" if name.startswith("outro") \
            else "statement"
    if density in ("full", "open"):
        return "runs"
    if density == "driving":
        return "bariolage16" if name.startswith("verse3") \
            else "bariolage"
    return "bariolage"


# ---------------------------------------------------------------------
# Composition: events on the grid. An event is a dict:
# {step, dur_steps, midi, velocity, section, mode} -- step is the
# GLOBAL 16th-step index; sample placement happens at render, from
# the same unrounded accumulator the spine uses, with the spine's
# swing, so the dancer and the drums breathe the same bounce.
# ---------------------------------------------------------------------

def compose_events(spine_sections, overrides=None):
    """Compose the layer over a spine schedule. Returns (events, modes).

    MECHANISM: the figure cell tiles each section in the section's
    mode. RUNS: the cell at 16ths, phrase heads accented. BARIOLAGE:
    at 8ths, cell notes alternate with the pedal (Paganini's open
    string); BARIOLAGE16 is the same device at 16ths. STATEMENT:
    the figure once per pass at 8th-note spacing, each phrase's
    last note held two extra steps; passes repeat to fill the
    section and the final note holds to the section's end. All
    placement is step arithmetic -- deterministic, no RNG.
    """
    cell = figure_cell()
    events = []
    modes = []
    global_step = 0
    for idx, sec in enumerate(spine_sections):
        bars = int(sec["bars"])
        mode = mode_for_section(idx, sec, overrides)
        modes.append(mode)
        gain = MODE_GAIN[mode]
        n_steps = bars * STEPS_PER_BAR
        if mode == "runs":
            for s in range(n_steps):
                note = LADDER[cell[s % len(cell)]][2]
                vel = gain * (1.0 if s % len(cell) in PHRASE_STARTS
                              else 0.8)
                events.append({"step": global_step + s,
                               "dur_steps": 1, "midi": note,
                               "velocity": round(vel, 4),
                               "section": idx, "mode": mode})
        elif mode in ("bariolage", "bariolage16"):
            stride = 2 if mode == "bariolage" else 1
            k = 0
            for s in range(0, n_steps, stride):
                if k % 2 == 0:
                    note = LADDER[cell[(k // 2) % len(cell)]][2]
                    vel = gain * 0.95
                else:
                    note = PEDAL_MIDI
                    vel = gain * 0.6
                events.append({"step": global_step + s,
                               "dur_steps": stride, "midi": note,
                               "velocity": round(vel, 4),
                               "section": idx, "mode": mode})
                k += 1
        elif mode in ("statement", "statement_fade"):
            # One pass: phrases at 8th spacing (2 steps), phrase-
            # final notes held +2 steps. Pass = 20*2 + 5*2 = 50
            # steps; repeat passes until the section is full.
            pos = 0
            while pos < n_steps:
                cyc = 0
                for p, length in enumerate(FIBONACCI_PHRASES):
                    for j in range(length):
                        if pos >= n_steps:
                            break
                        note = LADDER[cell[cyc % len(cell)]][2]
                        last = (j == length - 1)
                        dur = 4 if last else 2
                        events.append({
                            "step": global_step + pos,
                            "dur_steps": dur, "midi": note,
                            "velocity": round(gain * 0.9, 4),
                            "section": idx, "mode": mode})
                        pos += 2 + (2 if last else 0)
                        cyc += 1
                # hold the pass's final note to the next pass / end
                if events and events[-1]["section"] == idx:
                    nxt = min(pos, n_steps)
                    ev = events[-1]
                    ev["dur_steps"] = max(
                        ev["dur_steps"],
                        nxt - (ev["step"] - global_step))
        global_step += n_steps
    return events, modes


# ---------------------------------------------------------------------
# The violin voice.
# ---------------------------------------------------------------------

def _smooth_len(n):
    """Smallest m >= n with prime factors only in {2, 3, 5, 7}.

    MECHANISM: the pipeline's fast-length doctrine, kept here in
    miniature so this module stands alone: a length with a large
    prime factor sends pocketfft down Bluestein's road (the
    10,066,019-sample lesson of Proof No. 2), and a measurement or
    shaping transform must never cost more than the music.
    """
    m = int(n)
    while True:
        r = m
        for p in (2, 3, 5, 7):
            while r % p == 0:
                r //= p
        if r == 1:
            return m
        m += 1


def _formant_shape(layer, sr):
    """Body and brilliance: the violin's wooden signature.

    MECHANISM: a static frequency-domain response over the whole
    layer -- a body resonance near 520 Hz, a brilliance presence
    near 2.9 kHz, the sub-bow region (under 150 Hz) pulled down,
    the air above 9.5 kHz rolled off. RMS is restored to the
    input's, so shaping changes the TIMBRE only; the layer's level
    is set afterwards, by the caller's RMS law.
    """
    x = np.asarray(layer, dtype=np.float64)
    if x.size == 0:
        return x
    rms_in = float(np.sqrt(np.mean(x ** 2))) or 1.0
    n_pad = _smooth_len(x.shape[0])
    spectrum = np.fft.rfft(x, n=n_pad)
    freqs = np.fft.rfftfreq(n_pad, d=1.0 / sr)
    logf = np.log(np.maximum(freqs, 1.0))
    resp = np.full(freqs.shape, 0.62)
    resp += 0.85 * np.exp(-0.5 * ((logf - math.log(520.0)) / 0.35) ** 2)
    resp += 1.05 * np.exp(-0.5 * ((logf - math.log(2900.0)) / 0.45) ** 2)
    low = freqs < 150.0
    resp[low] *= 0.35 + 0.65 * (freqs[low] / 150.0)
    resp /= np.sqrt(1.0 + (freqs / 9500.0) ** 2)
    y = np.fft.irfft(spectrum * resp, n=n_pad)[:x.shape[0]]
    rms_out = float(np.sqrt(np.mean(y ** 2))) or 1.0
    return y * (rms_in / rms_out)


def _note_span(freq_track, sr, velocity):
    """One bowed note: harmonics tracking a per-sample frequency.

    MECHANISM: phase is the integral of the (humanized) frequency
    track, so vibrato and drift are IN the pitch, not painted on
    after. The bow envelope attacks in ~6 ms and releases in
    ~12 ms -- fast enough for 16ths at tempo, smooth enough to
    never click. Amplitude is the event's velocity.
    """
    n = freq_track.shape[0]
    if n == 0:
        return np.zeros(0, dtype=np.float64)
    phase = 2.0 * np.pi * np.cumsum(freq_track) / sr
    tone = np.zeros(n, dtype=np.float64)
    for k, amp in enumerate(_HARMONICS, start=1):
        tone += amp * np.sin(k * phase)
    tone /= sum(_HARMONICS)
    env = np.ones(n, dtype=np.float64)
    atk = min(n, max(1, int(0.006 * sr)))
    rel = min(n, max(1, int(0.012 * sr)))
    env[:atk] *= 0.5 - 0.5 * np.cos(np.linspace(0.0, np.pi, atk))
    env[-rel:] *= 0.5 + 0.5 * np.cos(np.linspace(0.0, np.pi, rel))
    return tone * env * float(velocity)


# ---------------------------------------------------------------------
# The render.
# ---------------------------------------------------------------------

def render_arpeggio(arp, spine, sr=48000):
    """Render the layer for a normalized arpeggio + spine spec.

    Returns ((2, N) float64 stereo, report). N is exactly
    spine_samples(spine, sr) -- the layer is as long as the grid
    it dances on, not a sample more. Deterministic: the same two
    specs render the same layer to the bit (the humanizer's seed
    is in the spec; nothing else in the chain rolls dice).

    MECHANISM, in order: compose events on the step grid (with
    the spine's swing on odd steps, so dancer and drums share
    the bounce) -> lay a frame-level F0 contour (hop 256) ->
    humanize it (Tools Wing) -> strike each note from the
    humanized contour -> formant-shape the summed mono -> orbit
    it slowly through resonance.spatial -> report what was made.
    """
    from resonance.studio.spine import spine_samples
    bpm = float(spine["bpm"])
    swing = float(spine.get("swing", 0.0))
    n = spine_samples(spine, sr)
    step_float = grid.samples_per_beat(bpm, sr) / 4.0
    swing_late = swing * step_float
    events, modes = compose_events(spine["sections"],
                                   arp["mode_overrides"])
    hop = 256
    n_frames = int(n // hop) + 2
    contour = np.full(n_frames, np.nan, dtype=np.float64)
    spans = []
    for ev in events:
        step = ev["step"]
        at = int(round(step * step_float
                       + (swing_late if (step % STEPS_PER_BAR) % 2
                          else 0.0)))
        dur = max(1, int(round(ev["dur_steps"] * step_float)))
        end = min(n, at + dur)
        if at >= n or end <= at:
            continue
        f0 = midi_to_freq(ev["midi"])
        contour[at // hop:(end - 1) // hop + 1] = f0
        spans.append((at, end, ev))
    human = humanize_contour(contour, hop / sr,
                             strength=arp["strength"],
                             seed=arp["seed"])
    # The contour is NaN between notes (statement gaps, section
    # rests); interpolation across a NaN poisons a note whole, so
    # the table is filled from its voiced frames first -- each gap
    # takes its nearest voiced pitch, which only ever feeds the
    # edges of a note's own track.
    voiced = np.isfinite(human)
    if not np.any(voiced):
        raise ValueError("arpeggio: the composed line is empty")
    frame_idx = np.arange(n_frames)
    filled = np.interp(frame_idx, frame_idx[voiced], human[voiced])
    frame_pos = (np.arange(n_frames) + 0.5) * hop
    mono = np.zeros(n, dtype=np.float64)
    for at, end, ev in spans:
        track = np.interp(np.arange(at, end), frame_pos, filled)
        mono[at:end] += _note_span(track, sr, ev["velocity"])
    mono = _formant_shape(mono, sr)
    stereo = np.asarray(orbit(mono.astype(np.float32),
                              arp["orbit_hz"], n / sr,
                              sample_rate=sr), dtype=np.float64)
    if stereo.shape[1] > n:
        stereo = stereo[:, :n]
    elif stereo.shape[1] < n:
        stereo = np.pad(stereo, ((0, 0), (0, n - stereo.shape[1])))
    report = {
        "level_db": arp["level_db"],
        "orbit_hz": arp["orbit_hz"],
        "strength": arp["strength"],
        "seed": arp["seed"],
        "total_notes": len(spans),
        "sections": [
            {"name": sec["name"], "bars": int(sec["bars"]),
             "density": sec["density"], "mode": modes[i],
             "notes": sum(1 for e in spans if e[2]["section"] == i)}
            for i, sec in enumerate(spine["sections"])],
        "ladder": ladder_inventory(),
        "fibonacci_phrases": list(FIBONACCI_PHRASES),
        "figure_cell_midi": [LADDER[i][2] for i in figure_cell()],
        "layer_rms_dbfs": round(
            20.0 * math.log10(float(np.sqrt(np.mean(stereo ** 2))))
            if stereo.size else -120.0, 2),
    }
    return stereo, report


__all__ = [
    "FIBONACCI_PHRASES",
    "LADDER",
    "MODES",
    "compose_events",
    "figure_cell",
    "ladder_inventory",
    "mode_for_section",
    "normalize_arpeggio_spec",
    "render_arpeggio",
]

# 93 -- Live, Love, and let Love, Live.
