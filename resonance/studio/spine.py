# 93
# ---------------------------------------------------------------------
# spine.py -- the house engine's rhythmic spine for the studio road.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VIII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: when a studio spec carries a "spine" block, this module
# renders the drum + 808 skeleton with RESONANTIA's own synthesis --
# the resonance.synth 808 voices (kick / snare / clap / hats / rim)
# and a pitched-drop 808 bass struck here -- and lays every hit on
# the EXACT grid of resonance.grid: step offsets come from the
# unrounded samples-per-beat accumulator, rounded once per hit, and
# the whole spine is exactly grid.bars_to_samples(total_bars) long.
# Section lengths are whole bars, by construction, never by hope.
#
# DOCTRINE: the bed (MusicGen) supplies timbre; it has no clock --
# Proof No. 1 asked it for 93 BPM in prose and it answered ~62.
# The spine supplies the clock. The founder refused tempo surgery
# on the bed; instead the house engine owns the rhythmic spine,
# and the arithmetic closes to the sample.
# ---------------------------------------------------------------------

import numpy as np

from resonance import grid
from resonance.core.notes import midi_to_freq
from resonance.synth.voices import VOICES

STEPS_PER_BAR = 16

# The four-bar chord cycle under every section, as semitone offsets
# from the spine root: F - Db - Ab - Eb over an F root is the
# i - VI - III - VII anthem loop, one root per bar, restarting at
# the tonic whenever a new section begins.
CHORD_CYCLE = (0, 8, 3, 10)

DENSITIES = ("sparse", "driving", "full", "open")

DEFAULT_ROOT_MIDI = 29  # F1: the root of F minor, where the song lives.


# ---------------------------------------------------------------------
# The 808 bass voice: a pitched drop that holds its note.
# ---------------------------------------------------------------------

def bass808(midi, dur_s, sr=48000, velocity=1.0):
    """An 808 bass note: sine with a pitch drop into `midi`, sustained.

    MECHANISM: the kick in resonance.synth is a drop that dies --
    this is its melodic sibling: frequency falls from ~1.6x the
    target to the target in the first ~25 ms (the attack "thump"),
    then HOLDS the pitch for the note's duration under a slow decay
    to a sustain floor, with a short release at the end so notes
    hand off cleanly instead of clicking. A breath of second
    harmonic keeps it audible on small speakers. Phase is the
    integral of the frequency envelope, as physics requires.
    """
    freq = midi_to_freq(int(midi))
    n = max(1, int(round(dur_s * sr)))
    t = np.arange(n, dtype=np.float64) / sr
    f = freq * (1.0 + 0.6 * np.exp(-t / 0.025))
    phase = 2.0 * np.pi * np.cumsum(f) / sr
    env = np.exp(-t / max(0.35, dur_s)) * 0.45 + 0.55
    attack = min(n, max(1, int(0.004 * sr)))
    env[:attack] *= np.linspace(0.0, 1.0, attack)
    release = min(n, max(1, int(0.03 * sr)))
    env[-release:] *= np.linspace(1.0, 0.0, release)
    tone = np.sin(phase) + 0.18 * np.sin(2.0 * phase)
    return (tone * env * float(velocity)).astype(np.float64)


# ---------------------------------------------------------------------
# Patterns: one bar of 16 steps per density. Values are velocities;
# the bass speaks in (step, length_in_steps) events on the bar root.
# ---------------------------------------------------------------------

def _bar_pattern(density, bar_in_section, bars_in_section, fill):
    """(voice_grids, bass_events) for one bar of `density`.

    MECHANISM: patterns are written per density, with two honest
    variations: the last bar of a section is a fill (snare ramp,
    drums thin to the downbeats) and even/odd bars trade small
    ornaments (open hat, ghost kick) so a loop breathes. Everything
    is table-driven and deterministic -- no RNG anywhere in the
    spine, so a render is reproducible to the sample.
    """
    g = {name: [0.0] * STEPS_PER_BAR
         for name in ("kick", "snare", "clap", "closed_hat", "open_hat",
                      "rimshot")}
    bass = []
    even = (bar_in_section % 2 == 0)
    if density == "full":  # the hook: everything on, bounce forward
        for s, v in ((0, 1.0), (6, 0.75), (8, 1.0), (14, 0.8)):
            g["kick"][s] = v
        for s in (4, 12):
            g["clap"][s] = 0.95
        for s in range(0, 16, 2):
            g["closed_hat"][s] = 0.55 if s % 4 else 0.8
        if not even:
            g["open_hat"][14] = 0.7
        bass = [(0, 6), (6, 2), (8, 6)]
    elif density == "driving":  # a verse: 16th hats, lean kick
        g["kick"][0] = 1.0
        g["kick"][8] = 1.0
        g["kick"][10] = 0.85
        if not even:
            g["kick"][15] = 0.5
        for s in (4, 12):
            g["snare"][s] = 1.0
        for s in range(16):
            g["closed_hat"][s] = 0.65 if s % 4 == 0 else 0.38
        if bar_in_section % 4 == 3:
            g["open_hat"][14] = 0.75
        bass = [(0, 4), (3, 1), (6, 2), (8, 4), (10, 2), (12, 3)]
    elif density == "open":  # the feature slot: air, but grooving
        g["kick"][0] = 1.0
        g["kick"][8] = 0.95
        for s in (4, 12):
            g["snare"][s] = 0.95
        for s in range(0, 16, 2):
            g["closed_hat"][s] = 0.5
        if not even:
            g["open_hat"][14] = 0.65
            g["rimshot"][7] = 0.4
            g["rimshot"][15] = 0.4
        bass = [(0, 8), (8, 6)]
    else:  # sparse: intro / outro -- the frame, not the picture
        g["kick"][0] = 0.95
        g["closed_hat"][0] = 0.45
        g["closed_hat"][8] = 0.45
        if bar_in_section >= 2:
            g["closed_hat"][4] = 0.3
            g["closed_hat"][12] = 0.3
        if not even:
            g["rimshot"][4] = 0.45
        bass = [(0, 12)]
    if fill and density in ("full", "driving"):
        # Last bar: hats and kick step back; the snare walks home.
        g["closed_hat"] = [0.0] * STEPS_PER_BAR
        g["open_hat"] = [0.0] * STEPS_PER_BAR
        g["kick"] = [0.0] * STEPS_PER_BAR
        g["kick"][0] = 1.0
        g["kick"][8] = 0.9
        ramp = (0.5, 0.65, 0.8, 1.0)
        for j, s in enumerate((12, 13, 14, 15)):
            g["snare"][s] = ramp[j]
        g["clap"] = [0.0] * STEPS_PER_BAR
        bass = [(0, 8)]
    return g, bass


# ---------------------------------------------------------------------
# Spec handling: normalize + measure, shared by validation and render.
# ---------------------------------------------------------------------

def normalize_spine_spec(raw):
    """Validate a spec's "spine" block; return the normalized copy.

    MECHANISM: same contract style as the pipeline's own validator --
    every refusal names its field, so an agent can repair the spec
    without asking a human. Densities are the four the pattern table
    knows; bars are whole and positive; swing is the sequencer's own
    range (delayed off-steps, never negative time travel).
    """
    if not isinstance(raw, dict):
        raise ValueError("spine: must be an object")
    bpm = float(raw.get("bpm", 0))
    if not 40.0 <= bpm <= 240.0:
        raise ValueError(f"spine.bpm: {bpm} outside 40..240")
    swing = float(raw.get("swing", 0.0))
    if not 0.0 <= swing <= 0.6:
        raise ValueError(f"spine.swing: {swing} outside 0..0.6")
    root = int(raw.get("root_midi", DEFAULT_ROOT_MIDI))
    if not 12 <= root <= 60:
        raise ValueError(f"spine.root_midi: {root} outside 12..60")
    sections = raw.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValueError("spine.sections: required, a non-empty list")
    norm = []
    for i, sec in enumerate(sections):
        if not isinstance(sec, dict):
            raise ValueError(f"spine.sections[{i}]: must be an object")
        bars = sec.get("bars")
        if not isinstance(bars, int) or isinstance(bars, bool) or bars < 1:
            raise ValueError(
                f"spine.sections[{i}].bars: must be a positive int")
        density = str(sec.get("density", "driving"))
        if density not in DENSITIES:
            raise ValueError(
                f"spine.sections[{i}].density: {density!r} not one of "
                f"{DENSITIES}")
        norm.append({"name": str(sec.get("name", f"spine{i + 1}")),
                     "bars": bars, "density": density})
    return {"bpm": bpm, "swing": swing, "root_midi": root,
            "beats_per_bar": 4, "sections": norm}


def total_bars(spine):
    return sum(s["bars"] for s in spine["sections"])


def spine_samples(spine, sr):
    """The spine's exact length: bars_to_samples, single rounding."""
    return grid.bars_to_samples(total_bars(spine), spine["bpm"], sr,
                                spine["beats_per_bar"])


def trim_spine_spec(spine, max_bars):
    """A copy of the spine spec cut to `max_bars` whole bars.

    MECHANISM: bars come off the END of the schedule (the outro is
    what a short bed truncates in any honest arrangement) until the
    sections sum to max_bars; sections that fall entirely past the
    cut disappear from the copy. The caller's spec is not mutated.
    """
    out = dict(spine)
    kept, left = [], max_bars
    for sec in spine["sections"]:
        if left <= 0:
            break
        take = min(sec["bars"], left)
        kept.append({**sec, "bars": take})
        left -= take
    out["sections"] = kept
    return out


# ---------------------------------------------------------------------
# The render itself.
# ---------------------------------------------------------------------

def render_spine(spine, sr=48000):
    """Render the spine: float64 stereo (2, N), N exact by the grid.

    MECHANISM: hits are placed at round(global_step * step_float),
    where step_float is the UNROUNDED samples-per-16th from
    resonance.grid -- each offset is rounded independently from the
    true accumulator, so no rounding creep accumulates across 90
    bars. Swing delays odd steps within the bar by swing * one step
    (the sequencer's convention). The 808 bass follows the four-bar
    chord cycle, restarting at the tonic each section. The buffer
    is allocated at exactly spine_samples() long; voice tails that
    would fall past the end are cut by the buffer edge, the way the
    last bar of any record is cut by the record ending. Peak above
    1.0 is normalized to 0.95, the sequencer's own convention; a
    quieter spine keeps its dynamics.
    """
    spine = normalize_spine_spec(spine)
    bpm, sr = spine["bpm"], int(sr)
    n = spine_samples(spine, sr)
    mix = np.zeros((2, n), dtype=np.float64)
    step_float = grid.samples_per_beat(bpm, sr) / 4.0
    swing_late = spine["swing"] * step_float
    voice_cache = {}

    def hit(voice, velocity):
        key = (voice, round(float(velocity), 3))
        if key not in voice_cache:
            voice_cache[key] = VOICES[voice](
                velocity=float(velocity), sr=sr).astype(np.float64)
        return voice_cache[key]

    def place(buf, at):
        if at >= n:
            return
        end = min(n, at + buf.shape[0])
        if end > at:
            mix[0, at:end] += buf[:end - at]
            mix[1, at:end] += buf[:end - at]

    global_step = 0
    for sec in spine["sections"]:
        for bar in range(sec["bars"]):
            fill = bar == sec["bars"] - 1 and sec["bars"] > 1
            grids, bass = _bar_pattern(sec["density"], bar,
                                       sec["bars"], fill)
            root = spine["root_midi"] + CHORD_CYCLE[bar % 4]
            for voice, steps in grids.items():
                for step, vel in enumerate(steps):
                    if vel <= 0.0:
                        continue
                    at = int(round((global_step + step) * step_float
                                   + (swing_late if step % 2 else 0.0)))
                    place(hit(voice, vel), at)
            for step, length in bass:
                at = int(round((global_step + step) * step_float
                               + (swing_late if step % 2 else 0.0)))
                note = bass808(root, length * step_float / sr, sr)
                place(note, at)
            global_step += STEPS_PER_BAR
    peak = float(np.max(np.abs(mix))) if n else 0.0
    if peak > 1.0:
        mix *= 0.95 / peak
    return mix


__all__ = [
    "CHORD_CYCLE",
    "DENSITIES",
    "bass808",
    "normalize_spine_spec",
    "render_spine",
    "spine_samples",
    "total_bars",
    "trim_spine_spec",
]

# 93 -- Live, Love, and let Love, Live.
