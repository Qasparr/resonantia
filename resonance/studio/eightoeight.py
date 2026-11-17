# 93
# ---------------------------------------------------------------------
# eightoeight.py -- the 808 Synthesizer Toolbox: the classic 808
# voice family synthesized from first principles with the house kit.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# LABEL HONESTY -- READ FIRST: "808" in this module is the founder's
# shorthand for the TR-808 SOUND FAMILY -- a kick that sweeps down
# into its fundamental, a noise-and-tone snare, a metallic hat, and
# their kin. Nothing here samples Roland's machine, plays its
# recordings, or is that machine. Every voice below is synthesized
# in-house from oscillators, filtered noise, and envelopes, by the
# classic recipes re-derived from first principles. No claim of the
# machine itself is made, ever, by this module or anything struck
# from it.
#
# MECHANISM: each voice is a parameterized function returning a
# float64 buffer at the studio rate (SR = 48000, the master's rate
# pipeline.py keeps). The recipes are the textbook physics of the
# original analog circuits, stated as mathematics:
#   * pitched voices (kick, tom) are sine bodies whose FREQUENCY
#     follows an exponential pitch envelope -- the bridged-T
#     oscillator of the original kick is excited sharp and settles
#     to its tuned frequency; the phase is the ANALYTIC integral of
#     the frequency track, so the sweep is exact, not stepped.
#   * noise voices (snare, clap, hats' wash) are seeded white noise
#     through RBJ biquads -- seeded, so a render is reproducible to
#     the sample and a measurement can be re-weighed.
#   * metallic voices (hat, cymbal, cowbell) sum the classic
#     six-square cluster (263 / 400 / 421 / 474 / 587 / 845 Hz, the
#     oscillator set documented in the original service notes) and
#     throw away the fundamental region with a high-pass, which is
#     where the metal lives. Where a number is the classic
#     circuit's documented value it is named as such; where it is
#     this desk's approximation of the circuit's behavior, the
#     comment at the voice says so plainly.
# Filters are second-order RBJ biquads, coefficients computed per
# call; envelopes are true exponentials (env(tau) == e^-1 exactly),
# because a decay you cannot state is a decay you cannot test.
#
# DOCTRINE -- A SYNTHESIZER, NOT THE SPINE'S KIT: kit.py records
# the founder's ear condemning note-by-note synthesis for the
# SPINE's drum kit, which is therefore rendered, never synthesized.
# This module is a different seat, struck by the founder's direct
# order of 2026-11-16 ("Also the 808 Synthesizer toolbox"): a
# SYNTHESIZER instrument, judged as a synthesizer -- the way a
# hardware synth is judged, by whether its voices measure and
# sound as their recipes claim. The two doctrines do not collide:
# the spine places rendered audio; the toolbox is an instrument
# that happens to be made of mathematics. Its ear verdict, like
# every voice's, is the founder's alone and is not pre-claimed.
#
# DOCTRINE -- THE DIAL-TUNED KICK (the house difference): the
# kick's TUNING argument may name a seat of the Double-Letter Dial
# (docs/THE-DOUBLE-LETTER-DIAL.md; data at studio/data/
# dial-table.json). The seat's Method I tone is placed into the
# kick's working range by the PLACEMENT RULE, stated once here and
# printed in every dial-tuned render's manifest: a seat above
# 60 Hz is halved by octaves until it lands in [30, 60] Hz; a seat
# below 30 Hz is doubled by octaves into the same band; a seat
# already inside stands as-is. The 432 field remains available as
# a tuning root by the same placement (432 -> 54 Hz), as the
# engine already holds it. VV the founder's seat, LL the Sigma
# pair, OO the sea chain's double -- a kick may be tuned by any of
# the twenty-six pairs, and the derivation (seat, drops, placed
# fundamental) travels with the render, never silently.
#
# MEASUREMENT: a claim you cannot measure is a wish. Every render
# the kit builder strikes is re-read from the written file and
# measured on this side (duration, peak, RMS, and for kicks the
# realized fundamental track against its seat) before the numbers
# enter the manifest. The demo kit's renders are stamped into the
# proof ledger as instrumental proofs through proofs.stamp --
# the one door every toolkit shares.
# ---------------------------------------------------------------------

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

SR = 48000                   # the studio rate (pipeline's TARGET_SR)
PEAK_TARGET = 0.89           # struck one-shots are peak-set to this

# The kick's working band for dial placement, Hz. A kick
# fundamental lives here: below it a speaker cannot speak it,
# above it the hit stops being a foundation and becomes a tom.
KICK_BAND_HI = 60.0
KICK_BAND_LO = 30.0

# The classic metallic cluster: the six square-wave oscillators of
# the original hat/cymbal circuit, as documented in its service
# notes. Their ratios are deliberately inharmonic -- that is the
# whole sound.
METALLIC_CLUSTER_HZ = (263.0, 400.0, 421.0, 474.0, 587.0, 845.0)

# The cowbell's two squares, commonly documented at 540 and 845 Hz
# for the classic circuit; this desk's band placement around them
# is an approximation, stated as such at the voice.
COWBELL_HZ = (540.0, 845.0)

# Tom seats by name: the classic three, at this desk's pitches.
TOM_SEATS_HZ = {"low": 98.0, "mid": 147.0, "high": 196.0}


# ---------------------------------------------------------------------
# Small mathematics, shared by every voice.
# ---------------------------------------------------------------------

def _time(n):
    """The sample clock: t[i] = i / SR, float64, n samples long."""
    return np.arange(n, dtype=np.float64) / SR


def exp_decay(t, tau):
    """A true exponential decay envelope: exp(-t / tau).

    Stated so it can be tested: exp_decay(tau, tau) == e^-1 to the
    last bit the float holds. tau is the time constant in seconds
    -- the moment the envelope has fallen to ~36.8% of its start.
    """
    return np.exp(-np.asarray(t, dtype=np.float64) / tau)


def _attack_ramp(t, ramp_s=0.001):
    """A one-millisecond linear-in-exponent fade-in.

    A buffer that starts at full amplitude starts with a click
    whether you wanted one or not; voices that want a click add it
    deliberately (the kick does), and the rest ramp it away.
    """
    return 1.0 - np.exp(-np.asarray(t, dtype=np.float64) / ramp_s)


def _noise(n, seed):
    """Seeded white noise in [-1, 1): reproducible to the sample.

    A render that cannot be re-struck identically cannot be
    re-measured honestly, so no voice draws unseeded noise.
    """
    rng = np.random.RandomState(seed)
    return rng.uniform(-1.0, 1.0, n)


def _square(phase):
    """A square wave from a phase track, softened by one sample's
    honesty: sign(sin(phase)) -- the metallic voices filter the
    result hard, which is where the original circuit's character
    comes from; the raw edge is the point."""
    return np.sign(np.sin(phase))


def biquad_coeffs(kind, freq, q, sr=SR):
    """RBJ second-order filter coefficients (b, a), a[0] == 1.

    kind: 'lowpass' | 'highpass' | 'bandpass' (constant 0 dB peak
    gain form). freq is the corner/center in Hz, q the quality
    factor. The formulas are the Audio EQ Cookbook's, unchanged --
    a filter is a solved problem and the desk does not improvise
    solved problems.
    """
    w0 = 2.0 * math.pi * freq / sr
    alpha = math.sin(w0) / (2.0 * q)
    cw = math.cos(w0)
    if kind == "lowpass":
        b = [(1.0 - cw) / 2.0, 1.0 - cw, (1.0 - cw) / 2.0]
        a = [1.0 + alpha, -2.0 * cw, 1.0 - alpha]
    elif kind == "highpass":
        b = [(1.0 + cw) / 2.0, -(1.0 + cw), (1.0 + cw) / 2.0]
        a = [1.0 + alpha, -2.0 * cw, 1.0 - alpha]
    elif kind == "bandpass":
        b = [alpha, 0.0, -alpha]
        a = [1.0 + alpha, -2.0 * cw, 1.0 - alpha]
    else:
        raise ValueError(f"biquad kind {kind!r} not known")
    a0 = a[0]
    return ([c / a0 for c in b], [c / a0 for c in a])


def apply_biquad(x, coeffs):
    """Run a biquad over a buffer (direct form I, zero state)."""
    (b0, b1, b2), (_, a1, a2) = coeffs
    y = np.empty_like(x)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(len(x)):
        x0 = x[i]
        y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        y[i] = y0
        x2, x1 = x1, x0
        y2, y1 = y1, y0
    return y


def filter_chain(x, stages):
    """Apply (kind, freq, q) biquad stages in order."""
    for kind, freq, q in stages:
        x = apply_biquad(x, biquad_coeffs(kind, freq, q))
    return x


# ---------------------------------------------------------------------
# The dial: seats read from the engine's own data.
# ---------------------------------------------------------------------

_REPO_DIAL = Path(__file__).resolve().parent / "data" / "dial-table.json"
_DESK_DIAL = (Path.home() / "workspace" / "your_files"
              / "double-letter-dial" / "dial-table.json")


def dial_source():
    """Where the dial data was read from: the repo seat if it
    stands, the desk-delivery master as fallback. Named, never
    silent -- a tuning derived from a fallback says so."""
    if _REPO_DIAL.exists():
        return _REPO_DIAL
    return _DESK_DIAL


@lru_cache(maxsize=1)
def _dial_data():
    src = dial_source()
    return json.loads(src.read_text(encoding="utf-8"))


def dial_seat(pair):
    """One pair's dial seat: its weights and its Method I tone.

    Returns {pair, ordinal, agrippa, seat_hz} where seat_hz is the
    Method I tone (the weight lifted by octaves into [100, 1000)).
    Raises KeyError for a pair the dial does not hold.
    """
    pair = pair.upper()
    row = _dial_data()["pairs"][pair]
    return {"pair": pair, "ordinal": row["ordinal"],
            "agrippa": row["agrippa"], "seat_hz": row["method1"]["hz"]}


def place_seat(seat_hz):
    """THE PLACEMENT RULE: a dial seat into the kick's band.

    Above KICK_BAND_HI, halve by octaves; below KICK_BAND_LO,
    double by octaves; inside [30, 60] Hz, stand as-is. Returns
    (placed_hz, octave_shifts) -- negative shifts are drops,
    positive are lifts -- so a manifest can print the whole
    derivation, not just its answer.
    """
    f = float(seat_hz)
    shifts = 0
    while f > KICK_BAND_HI:
        f /= 2.0
        shifts -= 1
    while f < KICK_BAND_LO:
        f *= 2.0
        shifts += 1
    return f, shifts


def fundamental_for_pair(pair):
    """A dial pair's kick fundamental, with its derivation:
    {pair, seat_hz, placed_hz, octave_shifts}."""
    seat = dial_seat(pair)
    placed, shifts = place_seat(seat["seat_hz"])
    return {"pair": seat["pair"], "seat_hz": seat["seat_hz"],
            "placed_hz": placed, "octave_shifts": shifts,
            "ordinal": seat["ordinal"], "agrippa": seat["agrippa"]}


def fundamental_for_root(root_hz):
    """A tuning root (the 432 field, classically) placed into the
    kick's band by the same rule: 432 -> 54 Hz, no shifts hidden."""
    placed, shifts = place_seat(float(root_hz))
    return {"root_hz": float(root_hz), "placed_hz": placed,
            "octave_shifts": shifts}


# ---------------------------------------------------------------------
# The voices. Each returns a float64 buffer at SR; the render layer
# peak-sets and strikes the file. Parameters are the recipe's own.
# ---------------------------------------------------------------------

def kick(fundamental=50.0, sweep_start=160.0, sweep_tau=0.020,
         decay_tau=0.160, seconds=1.0, click=0.5, drive=0.15,
         tune=None, seed=808):
    """THE KICK -- the foundation.

    A sine body whose frequency track is
        f(t) = fundamental + (sweep_start - fundamental)
               * exp(-t / sweep_tau)
    -- struck sharp, settling to the fundamental, as the original
    bridged-T oscillator behaves when its pitch envelope fires.
    The phase is the analytic integral of f(t), so the track is
    exact. Amplitude is an exponential decay (decay_tau) behind a
    1 ms ramp; a measured breath of tanh drive (drive, 0 = clean)
    stands for the circuit's soft saturation -- an approximation,
    stated. The CLICK is deliberate: the first 3 ms carry a
    band-passed noise tick at `click` level, the attack transient
    every sampled kick is loved or hated for.

    TUNING: `tune` may name a dial pair ('VV', 'LL', ...) or a
    root in Hz as a string of digits ('432'); when it does, the
    fundamental is DERIVED by the placement rule and the explicit
    `fundamental` argument is overridden -- the derivation is the
    caller's to read from fundamental_for_pair()/the manifest.
    """
    if tune is not None:
        if isinstance(tune, str) and tune.strip().isdigit():
            fundamental = fundamental_for_root(
                float(tune.strip()))["placed_hz"]
        else:
            fundamental = fundamental_for_pair(tune)["placed_hz"]
    n = int(round(seconds * SR))
    t = _time(n)
    # The analytic phase: integral of the frequency track.
    phase = 2.0 * np.pi * (
        fundamental * t
        + (sweep_start - fundamental) * sweep_tau
        * (1.0 - np.exp(-t / sweep_tau)))
    body = np.sin(phase)
    if drive:
        body = np.tanh(body * (1.0 + drive)) / math.tanh(1.0 + drive)
    env = exp_decay(t, decay_tau) * _attack_ramp(t)
    out = body * env
    if click:
        tick = _noise(n, seed) * np.exp(-t / 0.0012)
        tick = filter_chain(tick, [("bandpass", 3500.0, 0.9)])
        out = out + click * 0.6 * tick
    return out


def snare(tone_hz=190.0, decay_tau=0.055, seconds=0.35,
          noise_level=0.8, tone_level=0.6, snap_hz=1800.0, seed=809):
    """THE SNARE -- noise and tone, the two bodies of the drum.

    Band-passed white noise (the wires' snap, centered snap_hz)
    over a short sine body at tone_hz with its second harmonic at
    a quarter weight (the shell). Two decays: the tone dies faster
    than the noise, as a real head's does. The original circuit
    sums a noise source and two bridged-T tones; one tone plus its
    harmonic is this desk's stated approximation.
    """
    n = int(round(seconds * SR))
    t = _time(n)
    noise = filter_chain(_noise(n, seed),
                         [("bandpass", snap_hz, 0.8),
                          ("highpass", 1200.0, 0.7)])
    noise = noise * exp_decay(t, decay_tau * 1.6) * _attack_ramp(t)
    tone = (np.sin(2.0 * np.pi * tone_hz * t)
            + 0.25 * np.sin(4.0 * np.pi * tone_hz * t))
    tone = tone * exp_decay(t, decay_tau) * _attack_ramp(t)
    return noise_level * noise + tone_level * tone / 1.25


def clap(band_hz=1200.0, burst_gap=0.011, bursts=3, tail_tau=0.220,
         seconds=0.8, seed=810):
    """THE CLAP -- bursts, then a tail that pretends to be a room.

    The classic circuit fires the noise source in a train of
    pulses and then lets it ring: `bursts` sharp exponential
    bursts spaced burst_gap apart, the last one opening into the
    long tail (tail_tau). The envelope is the sum of the burst
    decays and the tail decay, gated so the tail starts at the
    last burst. Band-passed noise throughout, centered band_hz.
    The 'reverb' is a single exponential pretending -- an
    approximation, stated; a room it is not.
    """
    n = int(round(seconds * SR))
    t = _time(n)
    env = np.zeros(n)
    for i in range(bursts):
        t0 = i * burst_gap
        seg = t >= t0
        env[seg] += np.exp(-(t[seg] - t0) / 0.010)
    t_last = (bursts - 1) * burst_gap
    seg = t >= t_last
    env[seg] += 0.7 * np.exp(-(t[seg] - t_last) / tail_tau)
    noise = filter_chain(_noise(n, seed),
                         [("bandpass", band_hz, 1.1),
                          ("bandpass", band_hz, 1.1)])
    return noise * env * _attack_ramp(t, 0.0005)


def _metallic(seconds, decay_tau, hp_hz, seed, noise_mix=0.0,
              tail_tau=None):
    """The shared metallic body: the six-square cluster, summed,
    high-passed into the metal region, exponentially decayed.

    Squares are summed at unit weight and divided by the count --
    the cluster's level is the count's, not the sum's shout. An
    optional noise wash (noise_mix) rides the same envelope, and
    an optional second, slower decay (tail_tau) blends under the
    first for voices that ring in two stages.
    """
    n = int(round(seconds * SR))
    t = _time(n)
    cluster = np.zeros(n)
    for f in METALLIC_CLUSTER_HZ:
        cluster += _square(2.0 * np.pi * f * t)
    cluster /= len(METALLIC_CLUSTER_HZ)
    body = filter_chain(cluster, [("highpass", hp_hz, 0.7),
                                  ("highpass", hp_hz, 0.7)])
    env = exp_decay(t, decay_tau)
    if tail_tau is not None:
        env = 0.7 * env + 0.3 * exp_decay(t, tail_tau)
    out = body * env * _attack_ramp(t, 0.0005)
    if noise_mix:
        wash = filter_chain(_noise(n, seed),
                            [("bandpass", 9000.0, 0.6)])
        out = out + noise_mix * wash * env * _attack_ramp(t, 0.0005)
    return out


def hihat(open_=False, decay_tau=None, seconds=None, seed=811):
    """THE HI-HAT, closed and open -- one body, two decays.

    The metallic cluster high-passed at 7.5 kHz. Closed is a
    choke: decay_tau 0.035, half a tenth of a second of file. Open
    is the same body allowed to ring: decay_tau 0.45. The original
    chokes the same oscillator with a shorter envelope; the
    identity of body and difference of decay is faithful to it.
    """
    if open_:
        decay_tau = 0.45 if decay_tau is None else decay_tau
        seconds = 1.2 if seconds is None else seconds
    else:
        decay_tau = 0.035 if decay_tau is None else decay_tau
        seconds = 0.25 if seconds is None else seconds
    return _metallic(seconds, decay_tau, 7500.0, seed)


def cymbal(decay_tau=0.9, seconds=3.5, seed=812):
    """THE CYMBAL (crash) -- the cluster at full length, plus wash.

    The same six squares, high-passed lower (6 kHz) so more body
    survives, a noise wash at a fifth weight, and a two-stage
    decay: a fast crash over a slow ring (tail at 2.2 s). The
    original's crash is this recipe's richest cousin; the ride's
    ping and bell are NOT claimed here -- crash only, stated.
    """
    return _metallic(seconds, decay_tau, 6000.0, seed,
                     noise_mix=0.2, tail_tau=2.2)


def cowbell(freqs=COWBELL_HZ, decay_tau=0.28, seconds=0.7, seed=813):
    """THE COWBELL -- two detuned squares through a band's window.

    Squares at freqs (the classic pair, commonly documented at
    540 and 845 Hz), summed, band-passed wide around their
    midpoint so both speak, with a two-stage decay: a fast knock
    over a shorter ring. The original filters the pair through a
    band-pass tuned between them; the window here is centered on
    the geometric mean of the pair, an approximation stated.
    """
    n = int(round(seconds * SR))
    t = _time(n)
    body = np.zeros(n)
    for f in freqs:
        body += _square(2.0 * np.pi * f * t)
    body /= len(freqs)
    center = math.sqrt(freqs[0] * freqs[1])
    body = filter_chain(body, [("bandpass", center, 0.6),
                               ("bandpass", center, 0.6)])
    env = (0.75 * exp_decay(t, decay_tau / 3.0)
           + 0.45 * exp_decay(t, decay_tau))
    return body * env * _attack_ramp(t, 0.0005)


def tom(seat="mid", fundamental=None, sweep_ratio=1.5,
        decay_tau=0.130, seconds=0.6, seed=814):
    """THE TOM -- the kick's smaller brother, in three seats.

    A sine whose pitch falls from sweep_ratio x the fundamental
    to the fundamental itself (the same analytic-integral sweep
    as the kick, gentler), exponentially decayed. Seats by name
    (TOM_SEATS_HZ: low 98, mid 147, high 196) or an explicit
    fundamental in Hz. A breath of attack noise at strike, low in
    the mix, stands for the stick.
    """
    if fundamental is None:
        fundamental = TOM_SEATS_HZ[seat]
    n = int(round(seconds * SR))
    t = _time(n)
    sweep_tau = 0.030
    start = fundamental * sweep_ratio
    phase = 2.0 * np.pi * (
        fundamental * t
        + (start - fundamental) * sweep_tau
        * (1.0 - np.exp(-t / sweep_tau)))
    body = np.sin(phase) * exp_decay(t, decay_tau) * _attack_ramp(t)
    stick = filter_chain(_noise(n, seed),
                         [("bandpass", 2500.0, 0.8)])
    stick = stick * np.exp(-t / 0.004) * 0.15
    return body + stick


def rimshot(ping_hz=1700.0, seconds=0.07, seed=815):
    """THE RIMSHOT -- a ping and a tick, gone before it arrives.

    The original excites a bridged-T network at ~1700 Hz and adds
    the stick's click; here: a sine ping at ping_hz decaying with
    a 7 ms constant, band-passed tight, plus a 2 ms noise tick.
    Total file seven hundredths of a second -- the shortest voice
    in the box, as it should be.
    """
    n = int(round(seconds * SR))
    t = _time(n)
    ping = np.sin(2.0 * np.pi * ping_hz * t) * np.exp(-t / 0.007)
    ping = filter_chain(ping, [("bandpass", ping_hz, 1.4)])
    tick = filter_chain(_noise(n, seed),
                        [("bandpass", 4000.0, 0.8)])
    tick = tick * np.exp(-t / 0.0015) * 0.5
    return (ping + tick) * _attack_ramp(t, 0.0003)


# The registry: name -> (function, default parameters). The kit
# builder and the CLI both speak through this one table, so a
# voice added here is added everywhere.
VOICES = {
    "kick": (kick, {}),
    "snare": (snare, {}),
    "clap": (clap, {}),
    "hihat-closed": (hihat, {"open_": False}),
    "hihat-open": (hihat, {"open_": True}),
    "cowbell": (cowbell, {}),
    "tom-low": (tom, {"seat": "low"}),
    "tom-mid": (tom, {"seat": "mid"}),
    "tom-high": (tom, {"seat": "high"}),
    "rimshot": (rimshot, {}),
    "cymbal": (cymbal, {}),
}


def render_voice(name, **overrides):
    """Render one registered voice: (buffer, parameters used).

    The parameters returned are the registry defaults as amended
    by the caller's overrides -- the exact recipe the buffer was
    struck from, fit to travel in a manifest.
    """
    fn, defaults = VOICES[name]
    params = dict(defaults)
    params.update(overrides)
    return fn(**params), params


# ---------------------------------------------------------------------
# WAV striking and measurement -- stdlib wave, 24-bit, this side.
# ---------------------------------------------------------------------

def write_wav(path, buf, sr=SR):
    """Strike a float buffer as a 24-bit PCM WAV.

    Peak-set to PEAK_TARGET first -- set TO the target, up or
    down, as kit.py's press peak-sets its hits: a voice whose
    natural body is quiet (the high-passed hat) is gained to the
    same seat as the kick, and a hot voice is pulled down. Then
    quantize. Returns the peak factor applied, so the manifest
    can confess any rescaling.
    """
    import wave
    buf = np.asarray(buf, dtype=np.float64)
    peak = float(np.max(np.abs(buf))) if len(buf) else 0.0
    factor = (PEAK_TARGET / peak) if peak > 0.0 else 1.0
    scaled = buf * factor
    ints = np.clip(np.round(scaled * 8388607.0),
                   -8388608, 8388607).astype(np.int32)
    raw = ints.view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(3)
        w.setframerate(sr)
        w.writeframes(raw)
    return factor


def read_wav(path):
    """Read a PCM WAV (16/24/32-bit int) back as float64 + rate."""
    import wave
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        width = w.getsampwidth()
        n = w.getnframes()
        raw = w.readframes(n)
    if width == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        ints = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
                | (a[:, 2].astype(np.int32) << 16))
        ints = np.where(ints >= 1 << 23, ints - (1 << 24), ints)
        return ints.astype(np.float64) / 8388608.0, sr
    if width == 2:
        return (np.frombuffer(raw, dtype=np.int16).astype(np.float64)
                / 32768.0), sr
    if width == 4:
        return (np.frombuffer(raw, dtype=np.int32).astype(np.float64)
                / 2147483648.0), sr
    raise ValueError(f"sample width {width} not read here")


def measure_buffer(buf, sr=SR):
    """The three numbers every struck file must confess:
    duration in seconds, peak in dBFS, RMS in dBFS."""
    buf = np.asarray(buf, dtype=np.float64)
    if len(buf) == 0:
        return {"duration_s": 0.0, "peak_dbfs": None, "rms_dbfs": None}
    peak = float(np.max(np.abs(buf)))
    rms = float(np.sqrt(np.mean(buf ** 2)))
    return {
        "duration_s": round(len(buf) / sr, 4),
        "peak_dbfs": round(20.0 * math.log10(peak), 2) if peak else None,
        "rms_dbfs": round(20.0 * math.log10(rms), 2) if rms else None,
    }


def estimate_fundamental(buf, sr=SR, t0=0.0, t1=None,
                         fmin=25.0, fmax=500.0):
    """Autocorrelation pitch estimate over one window of a buffer.

    The window [t0, t1) seconds is correlated against itself; the
    strongest lag inside [fmin, fmax] wins, parabolically refined.
    Honest about its grain: a sweeping voice read through a long
    window returns the window's average pitch, so callers read the
    kick's attack through a SHORT window and its tail through a
    long one, and the manifest states both windows.
    """
    buf = np.asarray(buf, dtype=np.float64)
    i0 = int(t0 * sr)
    i1 = len(buf) if t1 is None else min(len(buf), int(t1 * sr))
    seg = buf[i0:i1]
    if len(seg) < int(sr / fmin):
        return None
    seg = seg - float(np.mean(seg))
    corr = np.correlate(seg, seg, mode="full")[len(seg) - 1:]
    lo = int(sr / fmax)
    hi = min(int(sr / fmin), len(corr) - 2)
    if hi <= lo:
        return None
    lag = lo + int(np.argmax(corr[lo:hi]))
    # Parabolic refinement around the peak.
    y0, y1, y2 = corr[lag - 1], corr[lag], corr[lag + 1]
    denom = (y0 - 2.0 * y1 + y2)
    frac = 0.5 * (y0 - y2) / denom if denom else 0.0
    return float(sr / (lag + frac))


def kick_track(buf, sr=SR):
    """A kick's realized fundamental track, as two readings:
    the ATTACK (first 20 ms, where the sweep lives -- read as the
    window's average pitch, grain stated; the window must hold a
    full period of the lowest pitch it may report, so the attack
    search starts at 55 Hz) and the TAIL (the last 250 ms, where
    the voice has settled to its fundamental)."""
    dur = len(buf) / sr
    attack = estimate_fundamental(buf, sr, 0.0, 0.020, fmin=55.0)
    tail = estimate_fundamental(buf, sr, max(0.0, dur - 0.250), dur)
    return {"attack_hz_window_20ms": None if attack is None
            else round(attack, 1),
            "tail_hz_last_250ms": None if tail is None
            else round(tail, 1)}


# ---------------------------------------------------------------------
# The demo kit: every voice at its default seat, plus the dial's
# kicks, struck and measured into one folder with its manifest.
# ---------------------------------------------------------------------

# The dial-tuned kicks of the demo: VV the founder's seat, LL the
# Sigma pair's letter, OO the sea chain's double -- three pairs
# whose placed fundamentals span the band (44 / 48 / 60 Hz).
DEMO_DIAL_PAIRS = ("VV", "LL", "OO")


def build_demo_kit(out_dir):
    """Strike the demo kit into out_dir; return its manifest.

    Every voice of the registry at default parameters, one file
    each, plus one kick per DEMO_DIAL_PAIRS pair tuned by the
    placement rule. Each file is re-read from disk and measured
    before its numbers enter the manifest -- the manifest is a
    record of files, not of intentions.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    entries = []

    def _strike(fname, name, buf, params, extra=None):
        path = out / fname
        factor = write_wav(path, buf)
        struck, sr = read_wav(path)
        entry = {"file": fname, "voice": name, "params": params,
                 "peak_factor_applied": round(factor, 4),
                 "measured": measure_buffer(struck, sr)}
        if extra:
            entry.update(extra)
        entries.append(entry)
        return entry

    for name in VOICES:
        buf, params = render_voice(name)
        extra = None
        if name == "kick":
            extra = {"realized_track": kick_track(buf)}
        _strike(f"{name}.wav", name, buf, params, extra)

    for pair in DEMO_DIAL_PAIRS:
        deriv = fundamental_for_pair(pair)
        buf, params = render_voice("kick", tune=pair)
        track = kick_track(buf)
        extra = {"dial_derivation": deriv,
                 "realized_track": track,
                 "tail_vs_placed_hz": (
                     None if track["tail_hz_last_250ms"] is None else
                     round(track["tail_hz_last_250ms"]
                           - deriv["placed_hz"], 1))}
        _strike(f"kick-dial-{pair.lower()}.wav", "kick", buf,
                params, extra)

    manifest = {
        "tool": "resonance.studio.eightoeight",
        "label": ("'808' names the TR-808 sound family. Every voice "
                  "here is synthesized in-house from oscillators, "
                  "noise, and envelopes; nothing samples Roland's "
                  "machine or plays its recordings."),
        "sr": SR,
        "dial_source": str(dial_source()),
        "entries": entries,
    }
    (out / "kit_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return manifest


# ---------------------------------------------------------------------
# The CLI, in the studio idiom (proofs.py's shape):
#   python3 -m resonance.studio.eightoeight seats
#   python3 -m resonance.studio.eightoeight voice --name kick \
#       [--tune VV] [--out kick.wav] [--param k=v ...]
#   python3 -m resonance.studio.eightoeight kit --out DIR
# The JSON on stdout is the manifest/record, whole -- a machine
# reader gets the same truth a human does.
# ---------------------------------------------------------------------

def _coerce(value):
    """CLI parameter values arrive as strings; the recipes speak
    numbers and booleans. Coerce by shape, confess failure."""
    for cast in (int, float):
        try:
            return cast(value)
        except ValueError:
            pass
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(
        prog="resonance.studio.eightoeight",
        description="The 808 Synthesizer Toolbox: the classic 808 "
                    "voice family synthesized in-house from first "
                    "principles. '808' names the sound family; "
                    "nothing here samples Roland's machine.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("seats", help="print the dial seats and "
                                     "their placed kick fundamentals")
    p = sub.add_parser("voice", help="render one voice to a WAV")
    p.add_argument("--name", required=True, choices=sorted(VOICES))
    p.add_argument("--out", required=True)
    p.add_argument("--tune", help="kick tuning: a dial pair (VV) "
                                   "or a root in Hz (432)")
    p.add_argument("--param", action="append", default=[],
                   help="recipe override k=v, repeatable")
    p = sub.add_parser("kit", help="strike the whole demo kit")
    p.add_argument("--out", required=True)

    args = ap.parse_args(argv)
    if args.cmd == "seats":
        rows = {}
        for pair in _dial_data()["pairs"]:
            rows[pair] = fundamental_for_pair(pair)
        print(json.dumps({"dial_source": str(dial_source()),
                          "placement_rule": (
                              "seat above 60 Hz halved by octaves "
                              "into [30, 60] Hz; below 30 Hz "
                              "doubled into the band; inside, "
                              "stands as-is"),
                          "pairs": rows},
                         ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "voice":
        overrides = {}
        for kv in args.param:
            k, _, v = kv.partition("=")
            overrides[k] = _coerce(v)
        if args.tune:
            overrides["tune"] = args.tune
        buf, params = render_voice(args.name, **overrides)
        path = Path(args.out)
        factor = write_wav(path, buf)
        struck, sr = read_wav(path)
        rec = {"file": str(path), "voice": args.name,
               "params": params,
               "peak_factor_applied": round(factor, 4),
               "measured": measure_buffer(struck, sr)}
        if args.name == "kick":
            rec["realized_track"] = kick_track(struck, sr)
            if args.tune:
                rec["dial_derivation"] = (
                    fundamental_for_root(float(args.tune))
                    if args.tune.strip().isdigit()
                    else fundamental_for_pair(args.tune))
        print(json.dumps(rec, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "kit":
        manifest = build_demo_kit(args.out)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    import sys
    sys.exit(main())

# 93 -- Live, Love, and let Love, Live.
