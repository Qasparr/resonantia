# 93
# ---------------------------------------------------------------------
# visualize.py -- The In-House Media Visualizer: an audio file in,
# a video out, whose face is the Double-Letter Dial.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: the tool is a pipeline of small, separately weighed
# parts. (1) The source audio is decoded by ffmpeg (subprocess, the
# lab-bridge pattern this studio already trusts) to mono float
# samples at a fixed analysis rate -- analysis only; the artifact's
# own audio stream is never touched by the weighing. (2) The Dial's
# seats are read from dial-table.json (the engine-data seat in this
# repo, resonance/studio/data/dial-table.json; the desk master in
# ~/workspace/your_files/double-letter-dial/ is the fallback, and
# which one fed the render is printed in the run summary). Each of
# the 26 pairs carries its Method I tone -- the pair's ordinal
# weight read as Hz and lifted by octaves into the sworn band
# [100, 1000). (3) For every video frame, an FFT window centred on
# the frame's moment is weighed, and each seat's gain is the energy
# of the spectrum inside the seat's band (one semitone either side
# of its tone), normalised against the strongest band-energy found
# anywhere in the file, gamma-lifted, and smoothed (fast attack,
# slow decay) so the lamps move like lamps and not like static.
# (4) Frames are drawn with PIL and piped raw into ffmpeg, which
# muxes them with the source's audio stream COPIED, not re-encoded,
# whenever the container allows; if a copy is refused, the fallback
# is AAC at the house's sworn 320,000 bps and the run summary says
# so at full size. Nothing is hidden, nothing smoothed -- in the
# report as in the render.
#
# DOCTRINE -- THE FACE IS THE DIAL: the founder asked (XVI Nov
# 2026, 23:51 EST) whether a visualizer for media could be made
# from the in-house tools and kit. This module is the desk's yes,
# built only from what the house already holds: ffmpeg, numpy,
# PIL, the Dial's own data, and the Familia's notation face. The
# 26 pairs stand on a logarithmic frequency axis across the sworn
# band; a pair lights in gold in proportion to the energy the
# music itself puts near the pair's tone. The dial document's own
# finding is visible in the geometry and is NOT corrected away:
# Method I's seats cluster in the band's first octave (100-192 Hz,
# 13 distinct tones for 26 pairs), so the left of the face is
# crowded and the right is open sky. That is the measured shape
# of the instrument; the visualizer shows the dial as it stands.
#
# DOCTRINE -- FACES: the pair letters and the headings are drawn
# in Lex Stellarrvm ABC Notation, the notation seat of the Familia
# (~/workspace/templates/LexStellarrvm-ABC.ttf; all 26 capitals
# verified present in the face). Small print stands in Liberation
# Sans, the named shelf face. If the ABC face is absent on a
# machine, the render falls back to Liberation Sans and the run
# summary names the substitution -- a named seat, never a silent
# one (the Familia discipline).
#
# DOCTRINE -- LABEL LAW: the opening card names the render for
# what it is -- a visualizer render of a named source file, made
# in the house kit. No word is printed that the artifact has not
# earned: nothing here is Dolby, Atmos, or THX, and those words
# appear nowhere in the tool's output.
#
# INPUTS / PROCESSES / OUTPUTS / TOLERANCES (the four elements):
#   Inputs:    an audio file ffmpeg can decode (WAV/MP3 named);
#              the dial table; the two faces.
#   Processes: decode -> weigh (FFT per frame) -> draw (PIL) ->
#              encode (ffmpeg/x264, audio copied where lawful).
#   Outputs:   one MP4 whose duration is the source's duration
#              (within one frame), plus a JSON run summary on
#              stdout carrying every measurement the run made.
#   Tolerances: frame timing is exact by construction (frame i
#              weighs the window centred at (i + 1/2) / fps);
#              gains are a display mapping, not a measurement of
#              the music -- the manifest distinction is kept: the
#              spectrum is measured, the lamp is drawn.
#
# THE PURE CORE: seat geometry, band energies, the gain mapping,
# the smoothing, the waveform peaks, and the frame arithmetic are
# pure functions of their arguments (numpy the only companion),
# weighed by tests/test_studio_visualize.py with no ffmpeg and no
# font in the room. The impure rim -- decode, draw, encode -- is
# kept thin and at the edges, as the studio's other bridges keep
# theirs.
# ---------------------------------------------------------------------

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------
# Constants -- the sworn figures of the face.
# ---------------------------------------------------------------------

ANALYSIS_SR = 44100          # the rate the weighing hears at
FFT_SIZE = 8192              # window: 5.39 Hz bins at ANALYSIS_SR
BAND_HALF_OCTAVES = 1.0 / 12.0   # a seat hears one semitone either side
GAIN_GAMMA = 0.5             # square-root lift: quiet energy still shows
ATTACK = 0.55                # smoothing: how fast a lamp rises
DECAY = 0.18                 # smoothing: how slow it falls
AXIS_LO_HZ = 100.0           # the dial's sworn band, low edge
AXIS_HI_HZ = 1000.0          # the dial's sworn band, high edge

# The doctrine colours: a deep purple field, a violet for the
# unlit seat, and the house gold (#FFD700) for the lit one.
COLOUR_FIELD = (26, 5, 44)
COLOUR_PANEL = (43, 9, 66)
COLOUR_DIM = (112, 84, 158)
COLOUR_GOLD = (255, 215, 0)
COLOUR_PALE = (232, 222, 255)
COLOUR_FAINT = (150, 128, 190)

ABC_FONT = Path.home() / "workspace" / "templates" / "LexStellarrvm-ABC.ttf"
SANS_FONT = Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
SANS_FONT_BOLD = Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")

REPO_DIAL = Path(__file__).resolve().parent / "data" / "dial-table.json"
DESK_DIAL = (Path.home() / "workspace" / "your_files" /
             "double-letter-dial" / "dial-table.json")

FLAGPOLE_LINE = ("Flagpole of Claim and Coinage: Johnathan 'Qasparr' "
                 "Monroe, ARR, All Rights Reserved, Without Prejudice.")


# ---------------------------------------------------------------------
# The Dial's seats -- data in, geometry out. Pure.
# ---------------------------------------------------------------------

def dial_path(cli_path=None):
    """Which dial table feeds the render, in seat order.

    MECHANISM: an explicit --dial wins; else the engine-data seat
    in this repo; else the desk master in your_files. The caller
    prints the returned path in the run summary, so the seat a
    render actually used is never a matter of recollection.
    """
    if cli_path:
        return Path(cli_path)
    if REPO_DIAL.exists():
        return REPO_DIAL
    return DESK_DIAL


def load_seats(path):
    """Read the dial table into a seat list, sorted for the face.

    MECHANISM: the table's `pairs` mapping carries each pair's
    Method I tone at ['method1']['hz']. The face wants the seats
    in tone order, ties broken by the pair's name, so a column of
    pairs sharing one tone stacks in a stable, name order.
    Returns a list of {'pair': 'AA', 'hz': 128.0} dicts.
    """
    table = json.loads(Path(path).read_text(encoding="utf-8"))
    seats = [{"pair": pair, "hz": float(rec["method1"]["hz"])}
             for pair, rec in table["pairs"].items()]
    seats.sort(key=lambda s: (s["hz"], s["pair"]))
    return seats


def seat_x(hz, x0, x1, lo=AXIS_LO_HZ, hi=AXIS_HI_HZ):
    """A tone's place on the logarithmic frequency axis. Pure.

    MECHANISM: log interpolation between the band's edges -- equal
    ratios take equal room, which is how the dial's own band is
    sworn ([100, 1000) is one decade). A tone at an edge lands on
    that edge exactly; the mapping is monotonic in hz.
    """
    frac = (math.log(hz) - math.log(lo)) / (math.log(hi) - math.log(lo))
    return x0 + frac * (x1 - x0)


def layout_columns(seats):
    """Group the seats into columns, one column per distinct tone.

    MECHANISM: pairs sharing a Method I tone share a seat (the
    dial document counts 13 distinct tones for 26 pairs), so the
    face draws one column per tone with its pairs stacked. Returns
    [{'hz': h, 'pairs': [names in seat order]}, ...] in tone order.
    """
    columns = []
    for seat in seats:
        if columns and columns[-1]["hz"] == seat["hz"]:
            columns[-1]["pairs"].append(seat["pair"])
        else:
            columns.append({"hz": seat["hz"], "pairs": [seat["pair"]]})
    return columns


# ---------------------------------------------------------------------
# Frame arithmetic. Pure.
# ---------------------------------------------------------------------

def frame_count(duration_s, fps):
    """How many frames a duration earns at a frame rate. Pure.

    MECHANISM: round to the nearest whole frame, never fewer than
    one -- the video's duration is then the source's duration
    within half a frame, the tolerance the header swears.
    """
    return max(1, int(round(duration_s * fps)))


def frame_centre(i, fps):
    """The moment frame i weighs: the centre of its cell. Pure."""
    return (i + 0.5) / fps


# ---------------------------------------------------------------------
# The weighing -- spectrum in, lamp gains out. Pure (numpy only).
# ---------------------------------------------------------------------

def band_edges(tone, half_octaves=BAND_HALF_OCTAVES):
    """The band a seat hears: its tone, a semitone either side."""
    return tone * 2.0 ** (-half_octaves), tone * 2.0 ** half_octaves


def band_energy(mags, freqs, tone):
    """Mean spectral magnitude inside a seat's band. Pure.

    MECHANISM: the MEAN, not the sum, so a band holding more FFT
    bins earns no advantage from its width -- each seat is weighed
    by how strong the music is at its tone, not by how much of the
    ruler its band covers. An empty band (a tone below the lowest
    bin) weighs 0.0 and the lamp stays dark; the absence is data.
    """
    lo, hi = band_edges(tone)
    inside = (freqs >= lo) & (freqs <= hi)
    if not inside.any():
        return 0.0
    return float(mags[inside].mean())


def gain_from_energy(energy, reference, gamma=GAIN_GAMMA):
    """Map a band energy to a lamp gain in [0, 1]. Pure.

    MECHANISM: the energy's share of the strongest band-energy in
    the file, gamma-lifted so a seat at a quarter of the peak still
    shows at half light. Zero energy (or a silent file, reference
    0) maps to 0.0 exactly -- darkness is the honest reading of
    silence, and the division is guarded rather than smoothed.
    """
    if energy <= 0.0 or reference <= 0.0:
        return 0.0
    return float(min(1.0, (energy / reference) ** gamma))


def smooth_gain(previous, new, attack=ATTACK, decay=DECAY):
    """One step of lamp smoothing. Pure.

    MECHANISM: a lamp rises at the attack rate and falls at the
    decay rate -- fast to answer the music, slow to leave it, the
    behaviour of every honest meter bridge. The step is a convex
    blend, so a gain in [0, 1] stays in [0, 1].
    """
    rate = attack if new > previous else decay
    return previous + rate * (new - previous)


def analyse(samples, sr, fps, seats):
    """Weigh a whole file: per-frame, per-seat lamp gains.

    MECHANISM: two passes. The first walks every frame's FFT
    window (FFT_SIZE samples, Hann-windowed, centred on the
    frame's moment, zero-padded at the file's edges) and records
    each seat's raw band energy; the loudest band-energy anywhere
    becomes the reference. The second maps energies to gains and
    smooths them down the frames, seat by seat. Returns a list of
    frames, each a list of gains in seat order. This is the
    measurement the drawing merely shows.
    """
    n_frames = frame_count(len(samples) / sr, fps)
    hop = sr / fps
    window = np.hanning(FFT_SIZE).astype(np.float32)
    freqs = np.fft.rfftfreq(FFT_SIZE, d=1.0 / sr)
    tones = [s["hz"] for s in seats]
    energies = np.zeros((n_frames, len(seats)), dtype=np.float64)
    for i in range(n_frames):
        centre = int(frame_centre(i, fps) * sr)
        start = centre - FFT_SIZE // 2
        chunk = np.zeros(FFT_SIZE, dtype=np.float32)
        src_lo = max(0, start)
        src_hi = min(len(samples), start + FFT_SIZE)
        if src_hi > src_lo:
            chunk[src_lo - start:src_hi - start] = samples[src_lo:src_hi]
        mags = np.abs(np.fft.rfft(chunk * window))
        for j, tone in enumerate(tones):
            energies[i, j] = band_energy(mags, freqs, tone)
    reference = float(energies.max()) if energies.size else 0.0
    gains = np.zeros_like(energies)
    previous = np.zeros(len(seats), dtype=np.float64)
    for i in range(n_frames):
        for j in range(len(seats)):
            raw = gain_from_energy(energies[i, j], reference)
            previous[j] = smooth_gain(previous[j], raw)
            gains[i, j] = previous[j]
    return gains, reference


def waveform_peaks(samples, buckets):
    """Min/max peaks of a sample body in `buckets` columns. Pure.

    MECHANISM: the classic waveform reduction -- each bucket keeps
    the lowest and highest sample it covers, so the drawn strip is
    the signal's true silhouette at column resolution. A bucket
    past the end of a short body reads 0.0/0.0 (silence), never an
    invented value.
    """
    mins = np.zeros(buckets, dtype=np.float64)
    maxs = np.zeros(buckets, dtype=np.float64)
    n = len(samples)
    for b in range(buckets):
        lo = int(b * n / buckets)
        hi = max(lo + 1, int((b + 1) * n / buckets))
        seg = samples[lo:min(hi, n)]
        if seg.size:
            mins[b] = float(seg.min())
            maxs[b] = float(seg.max())
    return mins, maxs


# ---------------------------------------------------------------------
# The impure rim -- decode, draw, encode. Kept thin, at the edges.
# ---------------------------------------------------------------------

def decode_audio(path, sr=ANALYSIS_SR):
    """Decode any ffmpeg-readable audio to mono float32 samples.

    MECHANISM: ffmpeg writes raw little-endian float samples to
    stdout (the lab-bridge pattern); numpy reads the pipe. The
    decode is for ANALYSIS only -- the artifact's own stream is
    muxed untouched at encode time.
    """
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path),
         "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"],
        capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32).copy()


class Faces:
    """The render's typefaces, loaded once, substitutions named.

    MECHANISM: the ABC face is asked for first for headings and
    pair letters; Liberation Sans carries small print and stands
    in for the ABC face entire if the face is absent. `abc_used`
    records which happened, for the run summary.
    """

    def __init__(self):
        self.abc_used = ABC_FONT.exists()
        self._cache = {}

    def font(self, role, size):
        key = (role, size)
        if key not in self._cache:
            if role == "abc" and self.abc_used:
                path = ABC_FONT
            elif role == "sans-bold":
                path = SANS_FONT_BOLD
            else:
                path = SANS_FONT
            self._cache[key] = ImageFont.truetype(str(path), size)
        return self._cache[key]


def _lerp_colour(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _text(draw, xy, s, font, fill, anchor="la"):
    draw.text(xy, s, font=font, fill=fill, anchor=anchor)


def draw_card(width, height, source_name, faces):
    """The opening card: the render named for what it is.

    MECHANISM: a still held for the card seconds -- the dial's
    title in the notation face, the source file named, the honest
    label (a visualizer render, house kit), and the Flagpole.
    """
    img = Image.new("RGB", (width, height), COLOUR_FIELD)
    d = ImageDraw.Draw(img)
    cx = width // 2
    _text(d, (cx, height * 0.30), "THE DOUBLE-LETTER DIAL",
          faces.font("abc", 54), COLOUR_GOLD, "ma")
    _text(d, (cx, height * 0.30 + 84), "A VISUALIZER RENDER",
          faces.font("abc", 30), COLOUR_PALE, "ma")
    _text(d, (cx, height * 0.30 + 138), source_name,
          faces.font("sans", 24), COLOUR_PALE, "ma")
    _text(d, (cx, height * 0.30 + 182),
          "Resonantia -- the in-house kit: ffmpeg, numpy, PIL, the Dial",
          faces.font("sans", 19), COLOUR_FAINT, "ma")
    _text(d, (cx, height - 92),
          "Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,",
          faces.font("sans", 17), COLOUR_FAINT, "ma")
    _text(d, (cx, height - 66),
          "ARR, All Rights Reserved, Without Prejudice.",
          faces.font("sans", 17), COLOUR_FAINT, "ma")
    _text(d, (cx, height - 34), "93 -- Live, Love, and let Love, Live.",
          faces.font("sans", 17), COLOUR_DIM, "ma")
    return img


def draw_frame(width, height, columns, gains_by_pair, mins, maxs,
               progress, elapsed, duration, source_name, faces):
    """One frame of the dial face.

    MECHANISM: geometry first -- margins, the axis rail, the lamp
    field above it, the waveform strip below. Each column stands
    at its tone's log-axis place; its pairs stack upward from the
    rail, each pair a lamp (a bar whose height and gold answer its
    gain) crowned with its letters in the notation face. The
    waveform strip draws the whole file's silhouette, the elapsed
    part in gold, with the playhead at the frame's moment.
    """
    img = Image.new("RGB", (width, height), COLOUR_FIELD)
    d = ImageDraw.Draw(img)
    margin = 72
    axis_x0, axis_x1 = margin + 18, width - margin - 18
    rail_y = int(height * 0.66)
    lamp_top = int(height * 0.16)
    lamp_max = rail_y - lamp_top - 44

    _text(d, (margin, 30), "THE DOUBLE-LETTER DIAL",
          faces.font("abc", 30), COLOUR_GOLD)
    _text(d, (width - margin, 36), source_name,
          faces.font("sans", 17), COLOUR_FAINT, "ra")
    _text(d, (margin, 66), "Method I tones -- the weight lifted, [100, 1000) Hz",
          faces.font("sans", 15), COLOUR_FAINT)

    # The axis: rail, decade ticks, and their labels.
    d.line([(axis_x0, rail_y), (axis_x1, rail_y)], fill=COLOUR_DIM, width=2)
    for tick in (100, 200, 500, 1000):
        tx = seat_x(tick, axis_x0, axis_x1)
        d.line([(tx, rail_y), (tx, rail_y + 8)], fill=COLOUR_DIM, width=2)
        _text(d, (tx, rail_y + 12), str(tick), faces.font("sans", 13),
              COLOUR_FAINT, "ma")

    # The lamps: one column per tone, pairs stacked from the rail.
    for col_index, col in enumerate(columns):
        cx = seat_x(col["hz"], axis_x0, axis_x1)
        stack = len(col["pairs"])
        cell = lamp_max / 5.0  # the tallest stack on the dial is five
        for k, pair in enumerate(col["pairs"]):
            gain = gains_by_pair.get(pair, 0.0)
            base = rail_y - k * cell
            bar_h = max(5.0, (0.12 + 0.88 * gain) * (cell - 26))
            colour = _lerp_colour(COLOUR_DIM, COLOUR_GOLD, gain)
            # MECHANISM: PIL's rounded_rectangle inverts its inner
            # fill strips when the bar's height is under twice the
            # radius plus two -- a near-dark lamp is only ~5 px
            # tall -- so short lamps are drawn square and only a
            # tall lamp (height >= 14, radius 4) earns its corners.
            if bar_h >= 14:
                d.rounded_rectangle([cx - 13, base - bar_h, cx + 13, base],
                                    radius=4, fill=colour)
            else:
                d.rectangle([cx - 13, base - bar_h, cx + 13, base],
                            fill=colour)
            label_colour = _lerp_colour(COLOUR_DIM, COLOUR_GOLD,
                                        max(gain, 0.18))
            # MECHANISM: the dial's seats crowd into the band's
            # first octave, so neighbouring columns' rail-level
            # (k == 0) labels are wider than the gap between
            # columns and collide. Alternate columns stagger the
            # rail-level label one step higher; upper-stack labels
            # sit a full cell apart and need no such help.
            stagger = 16 if (k == 0 and col_index % 2 == 1) else 0
            _text(d, (cx, base - bar_h - 8 - stagger), pair,
                  faces.font("abc", 21), label_colour, "ms")

    # The waveform strip: the file's silhouette, elapsed in gold.
    strip_y0, strip_y1 = int(height * 0.80), int(height * 0.93)
    mid = (strip_y0 + strip_y1) / 2.0
    amp = (strip_y1 - strip_y0) / 2.0 - 4
    d.rectangle([margin, strip_y0, width - margin, strip_y1],
                outline=COLOUR_PANEL, width=1)
    buckets = len(mins)
    span = width - 2 * margin
    play_x = margin + progress * span
    for b in range(buckets):
        x = margin + (b + 0.5) * span / buckets
        colour = COLOUR_GOLD if x <= play_x else COLOUR_DIM
        d.line([(x, mid - maxs[b] * amp), (x, mid - mins[b] * amp)],
               fill=colour, width=1)
    d.line([(play_x, strip_y0), (play_x, strip_y1)], fill=COLOUR_PALE,
           width=1)
    _text(d, (margin, height - 26),
          f"{elapsed:0.1f} s / {duration:0.1f} s",
          faces.font("sans", 14), COLOUR_FAINT)
    _text(d, (width - margin, height - 26), "RESONANTIA VISUALIZER",
          faces.font("sans", 14), COLOUR_FAINT, "ra")
    return img


def encode(frames, source_audio, out_path, fps, width, height):
    """Pipe drawn frames into ffmpeg; mux the source audio.

    MECHANISM: raw RGB frames arrive on stdin; the source file is
    the second input and its audio stream is mapped and COPIED --
    the master's own bytes ride the video untouched. If the copy
    is refused (a container quarrel), the encode is retried once
    with AAC at the sworn 320,000 bps, and the returned mode says
    which happened: 'copy' or 'aac-320k'. No third attempt: a
    second refusal is a failure, reported, not worked around.
    """
    base = ["ffmpeg", "-v", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{width}x{height}", "-r", str(fps), "-i", "-",
            "-i", str(source_audio),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-preset", "medium", "-crf", "18"]
    for mode, acodec in (("copy", ["-c:a", "copy"]),
                         ("aac-320k", ["-c:a", "aac", "-b:a", "320k"])):
        proc = subprocess.Popen(base + acodec + [str(out_path)],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.PIPE)
        try:
            for frame in frames:
                proc.stdin.write(frame.tobytes())
            proc.stdin.close()
        except BrokenPipeError:
            pass
        err = proc.stderr.read().decode("utf-8", "replace")
        proc.wait()
        if proc.returncode == 0:
            return mode
        last_err = err
    raise RuntimeError(f"ffmpeg encode failed in both audio modes: {last_err}")


def visualize(audio_path, out_path, width=1280, height=720, fps=30,
              card_seconds=2.0, dial=None):
    """The whole road: audio in, MP4 out, measurements back.

    MECHANISM: decode -> analyse -> draw (card frames, then dial
    frames) -> encode. The returned summary is the run's measured
    manifest: durations, frame count, the reference energy, the
    dial seat used, the face used, and the audio mux mode. It is
    printed as JSON by the CLI door.
    """
    audio_path = Path(audio_path)
    samples = decode_audio(audio_path)
    duration = len(samples) / ANALYSIS_SR
    dial_file = dial_path(dial)
    seats = load_seats(dial_file)
    columns = layout_columns(seats)
    gains, reference = analyse(samples, ANALYSIS_SR, fps, seats)
    n_frames = frame_count(duration, fps)
    card_frames = min(n_frames, int(round(card_seconds * fps)))
    mins, maxs = waveform_peaks(samples, 480)
    faces = Faces()
    seat_order = [s["pair"] for s in seats]

    def frame_stream():
        card = draw_card(width, height, audio_path.name, faces)
        for _ in range(card_frames):
            yield card
        for i in range(card_frames, n_frames):
            gains_by_pair = {seat_order[j]: float(gains[i, j])
                             for j in range(len(seat_order))}
            yield draw_frame(width, height, columns, gains_by_pair,
                             mins, maxs, (i + 0.5) / n_frames,
                             frame_centre(i, fps), duration,
                             audio_path.name, faces)

    audio_mode = encode(frame_stream(), audio_path, out_path, fps,
                        width, height)
    return {
        "source": str(audio_path),
        "output": str(out_path),
        "duration_s": round(duration, 4),
        "frames": n_frames,
        "card_frames": card_frames,
        "fps": fps,
        "size": [width, height],
        "dial": str(dial_file),
        "seats": len(seats),
        "reference_energy": reference,
        "abc_face_used": faces.abc_used,
        "audio_mux": audio_mode,
    }


def main(argv=None):
    """The CLI door: `python3 -m resonance.studio.visualize ...`.

    MECHANISM: argparse in the studio's idiom; the run summary is
    printed as JSON on stdout, the studio's habit for machine-
    readable receipts.
    """
    p = argparse.ArgumentParser(
        prog="visualize",
        description="Render an audio file as a Double-Letter Dial video.")
    p.add_argument("input", help="source audio (WAV/MP3)")
    p.add_argument("output", help="destination MP4")
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=720)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--card-seconds", type=float, default=2.0)
    p.add_argument("--dial", default=None,
                   help="dial-table.json (default: the repo seat)")
    args = p.parse_args(argv)
    summary = visualize(args.input, args.output, width=args.width,
                        height=args.height, fps=args.fps,
                        card_seconds=args.card_seconds, dial=args.dial)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 93 -- Live, Love, and let Love, Live.
