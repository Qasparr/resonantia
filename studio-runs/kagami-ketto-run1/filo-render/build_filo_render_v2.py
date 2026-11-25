# 93
# ---------------------------------------------------------------------
# build_filo_render_v2.py -- the FILO render set for KAGAMI KETTOU,
# REPAIRED: the bed rebuilt from the filed score on modeled
# instruments, the vocals re-seated IN FRONT of it, the whole
# re-struck under the master law as the FILO set's v2.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR, All Rights Reserved, Without Prejudice.
# Written XXV day of November, Anno V:xii e.n. (2026 e.v.), under
# the Method of Science, Aim of Religion -- Scientific Illuminism.
#
# THE COMMISSION (the founder's direct order, 2026-11-25 06:43 EST):
# "Do them both but in order of synergy" -- both defects of the
# house render repaired, in the synergy order: the bed first,
# because a voice cannot be seated in front of a bed that is
# itself under repair; the balance second, on the new bed.
#
# THE DEFECTS (the founder's ear, 2026-11-25 06:41 EST; the
# parent desk's measurements stand in RECEIPT-V2.md):
#   1. "No voices" -- the v1 full master's vocal layer measures
#      some 20 dB under its bed. The original build saved only
#      mastered WAVs, never premasters, so the balance was baked
#      into the only sources the FILO pass had. The repair does
#      not re-open a finished master: it goes back to the two
#      honest sources -- the filed score for the bed, the filed
#      vocal stem for the voice -- and mixes them again.
#   2. "The instrumentals is 16 bit again" -- the founder's
#      standing law: no 16-bit MIDI SOUND for a track to be
#      rapped over; dream-caliber instrumentals. The v1 bed's
#      piano was a five-partial decaying sine stack and its
#      violin a static harmonic stack -- synthesis, honestly
#      labeled as such in the original build, and still the
#      sound his law names. MIDI DATA was never the defect:
#      the score is notation and stands untouched. The SOUND
#      is rebuilt.
#
# THE ROADS, INVENTORIED BEFORE ANYTHING WAS STRUCK (the full
# inventory stands in RECEIPT-V2.md; the summary belongs here):
#   * No sample-playback renderer runs on this box: no
#     fluidsynth or timidity binary, no libfluidsynth, no
#     pyfluidsynth; and the one soundfont on disk (GeneralUser
#     GS) is a GM bank -- the defect's own class of sound, not
#     its cure.
#   * No GPU stands on this box (no nvidia-smi, no device):
#     the generative roads (ACE-Step bench-noted behind its GPU
#     gate; MusicGen) cannot run -- and could not carry a filed
#     score note-for-note if they did. A generative bed would
#     CHANGE the composition, which this repair forbids.
#   * The road that runs, and the house's own doctrine: FIRST-
#     PRINCIPLES SYNTHESIS at 48 kHz float -- the road of the
#     eightoeight seat (a synthesizer instrument, weighed 21/21
#     on this bench, and the founder's approved seat for the
#     kit and the Super 808, which therefore STAND unchanged).
#     The two named melodic seats are rebuilt as physical
#     MODELS, below.
#
# MECHANISM -- STEP 1, THE BED REBUILT (the synergy order: bed
# first). The event lists are the original build's own --
# build_instrument_events() imported from build_kagami_ketto.py,
# the score's verification re-run inside this build (125/125) --
# so every note, duration, swing placement, pan and gain of the
# filed composition is IDENTICAL. Only two voice functions are
# new, and the mix structure around them is the original
# render's, seat for seat:
#   * GRAND PIANO, modeled: partials stretched by the string
#     inharmonicity law f_k = k*f*sqrt(1 + B*k^2); two unison
#     strings per note, detuned a cent and a half apart; every
#     partial decaying on its own two-stage envelope (the fast
#     strike decay, then the long soundboard tail -- the shape
#     that makes a piano a piano and a sine stack not); a
#     hammer-noise transient at the strike; a gentle soundboard
#     lowpass over the sum; and a natural ring PAST the written
#     duration, faded, the way a struck string actually behaves.
#   * VIOLIN, modeled bowed string: a harmonic stack shaped by
#     the bridge-hill resonance near 2.6 kHz; vibrato that RAMPS
#     in (rate 5.4 Hz, depth to a half percent) with its tremolo
#     riding the same cycle; a slow seeded bow-pressure wobble
#     on the upper partials, so the spectrum breathes instead of
#     standing still; band-passed bow noise under the tone,
#     following the bow envelope.
#   * CALIBRATION, DISCLOSED: each modeled note is RMS-matched
#     to the v1 voice's note at the same pitch and written
#     duration (ratio capped to [0.4, 2.5]), so the mix gains
#     the original render placed by hand still mean what they
#     meant. The models change the SOUND; they do not smuggle
#     in a new balance for the bed's own seats.
#   * UNCHANGED, BY DESIGN: the eightoeight kit and Super 808
#     (the founder's approved synthesizer seat), the Sigma
#     solfeggio bed, the chord-root sub, and the pads -- the
#     ground the duel stands on. The defect named the melodic
#     instruments; the ground stands.
#
# MECHANISM -- STEP 2, THE VOICE IN FRONT. The filed vocal stem
# (44.1 kHz mono) is resampled to the studio rate by the exact
# rational 160/147 and seated dual-mono at the centre. ONE gain
# is computed from the VERSES themselves -- Verse A and Verse B,
# the duel's body: the gain that seats the verses' windowed RMS
# at the target ratio against the NEW bed's windowed RMS in the
# same windows (a battle record's voice at, not under, its bed;
# the target is printed in the build record). One gain, not a
# per-section ride: Shion's seat and the close take the same
# gain and keep the stem's own dynamics (the close is the
# loudest seat, as written), and their ratios are printed as
# the consequence, not smoothed into the target.
#
# MECHANISM -- STEP 3, THE MASTERING. The FILO discipline
# holds: the full render is struck first, as a whole; the
# instrumental follows; the vocals (03) are NOT re-struck --
# the v1 03 was mastered from this same stem, unchanged, and
# stands (RECEIPT-V2.md says so at full size). Mastering is the
# house road entire: pipeline.master_signal to -14.0 LUFS with
# the strike ceiling at -1.35 dBTP, WAV at 24-bit, MP3 by
# ffmpeg/libmp3lame at 320k, and the law weighed on the DECODED
# MP3 by vocal_exam.judge_masterlaw -- never on the WAV.
#
# DOCTRINE: a repair returns to honest sources or it is a
# patch on a defect. The score was never wrong; the stem was
# never wrong; the SOUND of two seats and one balance were.
# Those, and only those, are what this build changes -- and
# everything it changes, it prints.
#
# 93 -- Live, Love, and let Love, Live.
# ---------------------------------------------------------------------

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, resample_poly, sosfilt

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG.parents[1]))   # the repo root
sys.path.insert(0, str(PKG))              # the original build

import build_kagami_ketto as bk           # noqa: E402  the score's own build
from resonance.core.notes import midi_to_freq  # noqa: E402
from resonance.studio import eightoeight as e8  # noqa: E402
from resonance.studio import pipeline, vocal_exam  # noqa: E402

SR = bk.SR                       # 48000, the studio rate
EIGHTH_S = bk.EIGHTH_S
BAR_S = bk.BAR_S
TARGET_LUFS = -14.0              # house master law: integrated loudness
CEILING_DBTP = -1.35             # strike ceiling; decode margin under -1.0
SWORN_BPS = 320000               # house master law: exactly 320,000 bps
TARGET_VERSE_RATIO = 1.05        # the gain's law: the VERSES (the
                                 # duel's body) seated at-or-above
                                 # their bed, windowed RMS -- +0.4 dB.
                                 # The overall ratio is the verses'
                                 # consequence, printed, not targeted.


# ---------------------------------------------------------------------
# THE MODELED GRAND PIANO.
#
# MECHANISM: a struck string is not a stack of sines standing in
# a row. Its partials are STRETCHED sharp by the string's own
# stiffness (the inharmonicity law below), the high partials die
# faster than the low (each partial carries its own decay), the
# first instant is mostly hammer and brightness and the long
# tail mostly fundamental (the two-stage envelope), and a real
# note is two or three strings a cent apart, beating gently
# against each other (the unisons). Each of those is a term in
# the sum below; take any one away and the ear hears the
# synthesizer again. The note rings past its written duration
# -- strings do -- and the ring is faded at its end, never cut.
# ---------------------------------------------------------------------

def grand_piano_note(freq, dur_s, vel=1.0):
    tail = 1.4
    n = max(1, int((dur_s + tail) * SR))
    t = np.arange(n) / SR
    # String stiffness grows as pitch falls; B is the standard
    # inharmonicity coefficient, scaled mildly with pitch.
    B = 1.1e-4 * (261.6 / max(freq, 30.0)) ** 0.7
    B = min(B, 8.0e-4)
    # Fundamental decay: low strings ring long, high strings
    # short -- the piano's own geography.
    tau1 = float(np.clip(3.2 * (110.0 / freq) ** 0.45, 0.45, 3.6))
    kmax = int(min(30, max(4, 13500.0 / freq)))
    tone = np.zeros(n)
    # Two unison strings, a cent and a half apart.
    for cents in (-1.5, 1.5):
        f0 = freq * (2.0 ** (cents / 1200.0))
        for k in range(1, kmax + 1):
            fk = k * f0 * math.sqrt(1.0 + B * k * k)
            if fk > 15000.0:
                break
            # Brightness: the strike speaks in the high partials
            # and leaves them first.
            amp = (1.0 / k ** 0.85) * math.exp(-k * freq / 5200.0)
            tau_k = tau1 / (1.0 + 0.30 * (k - 1))
            env = (0.72 * np.exp(-t / tau_k)
                   + 0.28 * np.exp(-t / (tau_k * 3.6)))
            phase = 0.35 * math.sin(k * 12.9898)  # deterministic
            tone += amp * env * np.sin(2 * np.pi * fk * t + phase)
    tone *= 0.5
    # The hammer: a short burst of banded noise at the strike.
    rng = np.random.default_rng(int(freq * 10) + 93)
    hn = int(0.009 * SR)
    noise = rng.standard_normal(hn)
    sos_hp = butter(2, 1200.0, btype="high", fs=SR, output="sos")
    sos_lp = butter(2, 5200.0, btype="low", fs=SR, output="sos")
    hammer = sosfilt(sos_lp, sosfilt(sos_hp, noise))
    hammer *= np.exp(-np.arange(hn) / SR / 0.004)
    tone[:hn] += 0.55 * hammer
    # The soundboard: a gentle lowpass over the whole note.
    sos_sb = butter(2, 7800.0, btype="low", fs=SR, output="sos")
    tone = sosfilt(sos_sb, tone)
    # Attack ramp (no click), and the ring's end faded, not cut.
    atk = np.minimum(1.0, t / 0.003)
    fade = np.ones(n)
    fn = int(0.07 * SR)
    fade[-fn:] = 0.5 * (1.0 + np.cos(np.pi * np.arange(fn) / fn))
    tone = tone * atk * fade
    return (tone * vel).astype(np.float64)


# ---------------------------------------------------------------------
# THE MODELED VIOLIN (bowed string).
#
# MECHANISM: a bowed string's spectrum is alive while it sounds:
# the bow feeds every harmonic, the bridge and body throw their
# weight behind the band near 2.6 kHz (the bridge hill below),
# the player's vibrato arrives AFTER the attack and deepens into
# the note (the ramp below), the bow's pressure wanders slowly
# and the upper partials breathe with it (the seeded wobble),
# and under the tone sits the bow's own hair-and-rosin noise,
# banded and quiet, following the same envelope. A static stack
# has none of these; that stillness is what the founder's ear
# named. The note sounds for its written duration -- a bow
# lifts when the score says -- with its release inside it.
# ---------------------------------------------------------------------

def bowed_violin_note(freq, dur_s, vel=1.0, seed=93):
    n = max(1, int(dur_s * SR))
    t = np.arange(n) / SR
    # Vibrato: 5.4 Hz, depth ramping from nothing to a half
    # percent across the note's first half-second.
    vib_env = np.clip((t - 0.10) / 0.35, 0.0, 1.0)
    vib = 1.0 + 0.005 * vib_env * np.sin(2 * np.pi * 5.4 * t)
    phase = 2 * np.pi * np.cumsum(freq * vib) / SR
    # Bow pressure: a slow, seeded wander on the high partials.
    rng = np.random.default_rng(seed)
    wob = 1.0 + 0.16 * np.sin(2 * np.pi * 0.63 * t + rng.uniform(0, 6.28))
    kmax = int(min(26, max(6, 9800.0 / freq)))
    tone = np.zeros(n)
    for k in range(1, kmax + 1):
        fk = k * freq
        # Bridge hill: the body's weight near 2.6 kHz.
        hill = 0.68 + 0.62 * math.exp(-((fk - 2600.0) / 1150.0) ** 2)
        amp = (1.0 / k ** 0.80) * hill
        part = amp * np.sin(k * phase)
        if k >= 6:
            part = part * wob
        tone += part
    tone /= sum((1.0 / k ** 0.80)
                * (0.68 + 0.62 * math.exp(-((k * freq - 2600.0)
                                            / 1150.0) ** 2))
                for k in range(1, kmax + 1))
    # Bow noise: banded, quiet, under the tone.
    noise = rng.standard_normal(n)
    sos_bp = butter(2, [900.0, 3600.0], btype="band", fs=SR,
                    output="sos")
    bow = sosfilt(sos_bp, noise)
    bow /= (np.max(np.abs(bow)) or 1.0)
    # The bow envelope: a real attack swell, a living sustain
    # (a slight crescendo, then settle), the lift at the end.
    atk = np.clip(t / 0.045, 0.0, 1.0)
    atk = atk * atk * (3.0 - 2.0 * atk)          # smoothstep
    rel_n = min(0.06, dur_s * 0.2)
    rel = np.clip((dur_s - t) / rel_n, 0.0, 1.0)
    swell = 1.0 + 0.07 * np.clip(t / (0.4 * dur_s + 1e-9), 0.0, 1.0)
    trem = 1.0 + 0.05 * vib_env * np.sin(2 * np.pi * 5.4 * t + 0.7)
    env = atk * rel * swell * trem
    out = tone * env + 0.045 * bow * (atk * rel)
    return (out * vel).astype(np.float64)


# ---------------------------------------------------------------------
# CALIBRATION: the modeled note carries the level the v1 voice
# carried at the same pitch and written duration, so the
# original render's placed gains still mean what they meant.
# ---------------------------------------------------------------------

def _rms(x):
    x = np.asarray(x, dtype=np.float64)
    return float(np.sqrt(np.mean(x * x))) if x.size else 0.0


def _matched(new_note, old_note, window_samples):
    """Scale new_note so its RMS over the written window equals
    the v1 note's RMS; the ratio is capped so no pathology can
    shout or vanish."""
    old_r = _rms(old_note)
    new_r = _rms(new_note[:window_samples])
    if old_r <= 0 or new_r <= 0:
        return new_note
    ratio = float(np.clip(old_r / new_r, 0.4, 2.5))
    return new_note * ratio


def piano_v2(freq, dur_s, vel=1.0):
    new = grand_piano_note(freq, dur_s, vel)
    old = bk.piano_note(freq, dur_s, vel).astype(np.float64)
    return _matched(new, old, len(old)).astype(np.float32)


def violin_v2(freq, dur_s, vel=1.0, seed=93):
    new = bowed_violin_note(freq, dur_s, vel, seed=seed)
    old = bk.violin_note(freq, dur_s, vel).astype(np.float64)
    return _matched(new, old, len(old)).astype(np.float32)


# ---------------------------------------------------------------------
# STEP 1 -- THE BED, REBUILT. The original render's structure,
# seat for seat; the two melodic voice functions are the only
# substitution. (Sigma bed, chord-root sub, kit, Super 808 and
# pads are the original build's own code, called, not re-typed.)
# ---------------------------------------------------------------------

def render_bed_v2(inst_events):
    total_s = 93 * BAR_S
    n = int(round(total_s * SR))
    mix = np.zeros((2, n), dtype=np.float32)
    t = np.arange(n) / SR
    bed = np.zeros(n, dtype=np.float32)
    for j, carrier in enumerate((174.0, 285.0, 396.0, 417.0)):
        trem = 0.85 + 0.15 * np.sin(2 * np.pi * 0.05 * (j + 1) * t
                                    + j)
        bed += (0.045 * trem
                * np.sin(2 * np.pi * carrier * t)).astype(np.float32)
    mix[0] += bed
    mix[1] += bed * 0.92
    for name, bars, _s in bk.SECTIONS:
        b0 = bk.SECTION_START[name] - 1
        for bi in range(bars):
            root_hz = midi_to_freq(bk.ROOTS[name][bi] - 12)
            i0 = int((b0 + bi) * BAR_S * SR)
            seg = (0.10 * np.sin(2 * np.pi * root_hz
                                 * np.arange(int(BAR_S * SR)) / SR))
            mix[0, i0:i0 + len(seg)] += seg.astype(np.float32)
            mix[1, i0:i0 + len(seg)] += seg.astype(np.float32)
    shots = {"kick": e8.kick(tune="VV").astype(np.float32),
             "snare": e8.snare().astype(np.float32),
             "hat": e8.hihat(open_=False).astype(np.float32),
             "open": e8.hihat(open_=True).astype(np.float32)}
    gains = {"kick": 0.85, "snare": 0.50, "hat": 0.24, "open": 0.28}
    for name, bars, _s in bk.SECTIONS:
        b0 = bk.SECTION_START[name] - 1
        for bi in range(bars):
            for step, kind in bk.kit_steps(
                    name, last_bar=(name == "close"
                                    and bi == bars - 1)):
                at = (b0 + bi) * 13 + step
                at = bk._swung(at)
                bk._place(mix, shots[kind], at * EIGHTH_S,
                          gains[kind], pan=0.0)
    super_params = {"decay_tau": 0.42, "drive": 0.45, "click": 0.15}
    for ev in inst_events["B808"]:
        root_hz = midi_to_freq(ev["midi"])
        hit = e8.kick(fundamental=root_hz,
                      sweep_start=root_hz * 2.5,
                      seconds=ev["dur"] * EIGHTH_S + 0.25,
                      **super_params).astype(np.float32)
        bk._place(mix, hit, bk._swung(ev["start"]) * EIGHTH_S,
                  0.80, pan=0.0)
    for ev in inst_events["RH"]:
        note = piano_v2(midi_to_freq(ev["midi"]),
                        ev["dur"] * EIGHTH_S, vel=0.34)
        bk._place(mix, note, bk._swung(ev["start"]) * EIGHTH_S,
                  1.0, pan=0.12)
    for ev in inst_events["LH"]:
        note = piano_v2(midi_to_freq(ev["midi"]),
                        ev["dur"] * EIGHTH_S, vel=0.30)
        bk._place(mix, note, bk._swung(ev["start"]) * EIGHTH_S,
                  1.0, pan=-0.12)
    for name in ("shion", "reprise"):
        bars = dict((nm, b) for nm, b, _s in bk.SECTIONS)[name]
        b0 = bk.SECTION_START[name] - 1
        for bi in range(bars):
            root = bk.ROOTS[name][bi]
            for off in (12, 15, 19):
                note = bk.pad_note(midi_to_freq(root + off), BAR_S,
                                   vel=0.045)
                bk._place(mix, note, (b0 + bi) * BAR_S, 1.0, pan=0.0)
    for idx, ev in enumerate(inst_events["VLN"]):
        note = violin_v2(midi_to_freq(ev["midi"]),
                         ev["dur"] * EIGHTH_S, vel=0.38,
                         seed=93 + idx)
        bk._place(mix, note, bk._swung(ev["start"]) * EIGHTH_S,
                  1.0, pan=-0.08)
    return mix


# ---------------------------------------------------------------------
# THE BALANCE, MEASURED. Windowed RMS over the singing sections
# (Verses A and B, Shion's seat, the close), one-second windows,
# windows where the voice actually sounds.
# ---------------------------------------------------------------------

SINGING_SECTIONS = ("verse_a", "verse_b", "shion", "close")


def _singing_slices(n_samples):
    out = []
    for name in SINGING_SECTIONS:
        b0 = bk.SECTION_START[name] - 1
        bars = dict((nm, b) for nm, b, _s in bk.SECTIONS)[name]
        i0 = int(b0 * BAR_S * SR)
        i1 = min(n_samples, int((b0 + bars) * BAR_S * SR))
        out.append((name, slice(i0, i1)))
    return out


def windowed_balance(voice_mono, bed_stereo):
    """Per singing section and overall: the voice's RMS against
    the bed's, over one-second windows where the voice sounds
    (window RMS above -45 dBFS). voice_mono and bed_stereo are
    at the studio rate; the bed is read as its mono sum's RMS
    per channel pair (the stereo RMS)."""
    per = {}
    v_all, b_all = [], []
    for name, sl in _singing_slices(bed_stereo.shape[1]):
        v = voice_mono[sl]
        b = bed_stereo[:, sl]
        vs, bs = [], []
        win = SR
        for i0 in range(0, v.shape[0] - win + 1, win):
            vr = _rms(v[i0:i0 + win])
            if vr > 10 ** (-45.0 / 20.0):
                vs.append(vr)
                bs.append(_rms(b[:, i0:i0 + win]))
        if vs:
            v_rms = float(np.sqrt(np.mean(np.square(vs))))
            b_rms = float(np.sqrt(np.mean(np.square(bs))))
            per[name] = {"voice_rms": v_rms, "bed_rms": b_rms,
                         "ratio": v_rms / b_rms if b_rms else None,
                         "windows": len(vs)}
            v_all += vs
            b_all += bs
    overall = None
    if v_all:
        v_rms = float(np.sqrt(np.mean(np.square(v_all))))
        b_rms = float(np.sqrt(np.mean(np.square(b_all))))
        overall = {"voice_rms": v_rms, "bed_rms": b_rms,
                   "ratio": v_rms / b_rms if b_rms else None,
                   "windows": len(v_all)}
    return {"per_section": per, "overall": overall}


def measure_before():
    """The v1 balance, from the only sources v1 left: the vocal
    layer is what the full master holds that the instrumental
    master does not (master minus instrumental, sample for
    sample); the bed is the instrumental master itself."""
    master, sr1 = sf.read(str(PKG / "master.wav"), always_2d=True)
    inst, sr2 = sf.read(str(PKG / "instrumental-master.wav"),
                        always_2d=True)
    assert sr1 == sr2 == SR
    diff = (master - inst).T                      # (2, N)
    voice_layer = 0.5 * (diff[0] + diff[1])       # its mono sum
    return windowed_balance(voice_layer, inst.T)


# ---------------------------------------------------------------------
# STEP 3 -- THE MASTERING ROAD (the house's own, as the original
# build and the FILO pass both struck it).
# ---------------------------------------------------------------------

def master_and_judge(samples, out_base):
    mastered, mrep = pipeline.master_signal(
        np.asarray(samples, dtype=np.float64), SR,
        TARGET_LUFS, CEILING_DBTP)
    wav_path = HERE / f"{out_base}.wav"
    mp3_path = HERE / f"{out_base}.mp3"
    sf.write(str(wav_path), mastered.T, SR, subtype="PCM_24")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
         "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3_path)],
        check=True)
    verdict = vocal_exam.judge_masterlaw(mp3_path,
                                         sworn_bps=SWORN_BPS)
    return {"wav": wav_path.name, "mp3": mp3_path.name,
            "mp3_bytes": mp3_path.stat().st_size,
            "mastering": mrep, "verdict": verdict}


def main():
    record = {}
    # The score proves itself before a note is re-sounded.
    ver = bk.verify_all()
    record["score_verification"] = {
        "checks": len(ver["checks"]),
        "passed": sum(1 for c in ver["checks"] if c["ok"])}
    assert record["score_verification"]["passed"] == 125
    inst_events = bk.build_instrument_events()
    record["events"] = {k: len(v) for k, v in inst_events.items()}

    # STEP 1 -- the bed rebuilt from the filed score.
    bed = render_bed_v2(inst_events)

    # The voice, from its filed stem, at the studio rate.
    mono, sr_in = sf.read(str(PKG / "vocal-stem.wav"))
    assert sr_in == 44100 and mono.ndim == 1
    voice = resample_poly(mono.astype(np.float64), 160, 147)
    n = bed.shape[1]
    voice = voice[:n] if len(voice) >= n else np.pad(
        voice, (0, n - len(voice)))

    # The balance BEFORE (v1, from its own masters) ...
    record["balance_before_v1"] = measure_before()
    # ... and the gain that seats the voice in front of the
    # NEW bed, computed from the singing sections.
    raw = windowed_balance(voice, bed.astype(np.float64))
    record["balance_voice_raw_vs_new_bed"] = raw
    # The gain's basis is the VERSES: their windowed RMS pooled
    # (each section's RMS is already the root-mean-square of its
    # windows, so pool by window count).
    va, vb = (raw["per_section"]["verse_a"],
              raw["per_section"]["verse_b"])
    wsum = va["windows"] + vb["windows"]
    verse_voice = math.sqrt(
        (va["voice_rms"] ** 2 * va["windows"]
         + vb["voice_rms"] ** 2 * vb["windows"]) / wsum)
    verse_bed = math.sqrt(
        (va["bed_rms"] ** 2 * va["windows"]
         + vb["bed_rms"] ** 2 * vb["windows"]) / wsum)
    verse_ratio_raw = verse_voice / verse_bed
    gain = TARGET_VERSE_RATIO / verse_ratio_raw
    record["voice_gain"] = {"linear": gain,
                            "db": 20.0 * math.log10(gain),
                            "basis": "verse_a + verse_b pooled",
                            "verse_ratio_raw": verse_ratio_raw,
                            "target_verse_ratio": TARGET_VERSE_RATIO}
    voice_st = np.vstack([voice * gain, voice * gain])
    after = windowed_balance(voice * gain, bed.astype(np.float64))
    record["balance_after_v2_premaster"] = after

    # STEP 2 + 3 -- the mix, then the mastering, FILO order:
    # the full render first as a whole, the instrumental after.
    full = bed.astype(np.float64) + voice_st
    record["01_full_render_v2"] = master_and_judge(
        full, "01-full-render-kagami-kettou-v2")
    record["02_instrumental_v2"] = master_and_judge(
        bed, "02-instrumental-kagami-kettou-v2")
    record["03_vocals"] = ("STANDS as v1 (03-vocals-kagami-"
                           "kettou.mp3): mastered from this same "
                           "stem, unchanged; not re-struck.")
    (HERE / "build-record-v2.json").write_text(
        json.dumps(record, indent=2, default=str),
        encoding="utf-8")
    print(json.dumps(record, indent=2, default=str))


if __name__ == "__main__":
    main()
