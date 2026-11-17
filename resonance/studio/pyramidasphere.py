# 93
# ---------------------------------------------------------------------
# pyramidasphere.py -- The Pyramidasphere scene of the in-house
# media visualizer: three Pyramidaspheres seated in a 3-fold
# pyramid of 31 nodes, driven by the music's own weighing.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# THE COMMISSION: the founder ordered (XVII Nov 2026, 05:02 EST):
# "Generate a media visualer Lex Stellarrvm Pyramidasphere Tribunal
# Testimony Visualization with 3 Pyramidaspeheres in a 3 Fold
# 31^3 =93 Pyramid Itself". This module is that scene, built as a
# sibling of the visualizer on the ascii.py precedent: the weighing
# is the visualizer's own (its FFT discipline, its gain mapping,
# its smoothing, its faces), imported and never forked; what is
# new here is the face and the fold weighing that feeds it.
#
# THE FACE: three lattice spheres in the founder's plate's own
# register (THE-PYRAMIDASPHERE-FRONTISPIECE.jpg, Enclave files --
# purple-gold lattice of glowing points, a gold star at the heart,
# a green field rising in the lower hemisphere, a gold rim) seated
# in a 3-fold pyramid: the HIGH fold at the apex, the LOW and MID
# folds at the base, so the folds climb the pyramid. Behind them
# stands the pyramid frame of exactly 31 nodes (below). Each
# sphere brightens and its star flares with its own fold's energy;
# the frame's nodes light with the whole program's energy.
#
# THE 31 NODES: the frame's count is the Pyramidasphere
# instrument's own printed frame -- the square tiers
# 1^2 + 2^2 + 3^2 + 4^2 = 30, plus the crown, = 31. The layout
# draws rows of 1, 4, 9, and 16 nodes at one constant pitch (a
# square-number lattice), crowned by the thirty-first node at the
# apex joint. The run summary counts the nodes from the layout
# actually drawn: a node count that is claimed is the node count
# that is drawn.
#
# THE DECLARED EQUATION: the opening card carries the founder's
# inscription "31^3 = 93" as HIS declared equation -- the card is
# his inscription, not the desk's arithmetic. The desk's
# arithmetic stands beside it, in this header and in every run
# summary, unsuppressed and unsmoothed: 31^3 = 29,791 by
# multiplication; 31 + 31 + 31 = 93 by the threefold sum. Both
# printed, neither smoothed -- the house law for declared
# equations (a declaration stands as a declaration, its delta
# printed beside it).
#
# THE FOLD WEIGHING: the visualizer weighs a semitone band per
# dial seat; the folds weigh three broad bands with the same
# discipline -- the same FFT size, the same Hann window centred
# on the frame's moment, the same MEAN-of-magnitudes law (a wider
# band earns no advantage from its width), the same gamma lift
# and attack/decay smoothing, and ONE shared reference across the
# folds (the strongest fold-energy anywhere in the file), so the
# three spheres are weighed against each other honestly, as the
# dial's seats are. The bands are three octaves each, geometric:
# LOW 30-240 Hz (the voice's fundamental body), MID 240-1920 Hz
# (the formant body), HIGH 1920-15360 Hz (sibilance and air) --
# together the audible field the 44,100 Hz analysis rate carries.
# The program energy that lights the frame is the mean magnitude
# across the whole fold field, weighed against its own maximum.
#
# THE ENCODE: the house MP4 law, taken from mp4profile.py -- the
# wiring that module named as its follow-up, performed here by a
# caller at rest: H.264, yuv420p, CRF 18, +faststart, and the
# audio ladder (a sealed master's stream copied; AAC at the
# sworn 320,000 bps the one reported fallback).
#
# DOCTRINE -- LABEL LAW: the card names the render for what it
# is -- a Pyramidasphere visualization render of a named source,
# made in the house kit. No word is printed that the artifact
# has not earned: nothing here is Dolby, Atmos, or THX.
#
# THE UNSTAMPED SEAM: a visualizer render stands UNSTAMPED in
# the Render-as-Proof ledger -- no kind among score | lyrics |
# vocal | instrumental | orchestra | choir | master covers a
# picture of a master, and this module does not force one and
# does not touch the ledger. The seam was named to the founder
# with the visualizer itself; it stands named here again.
#
# INPUTS / PROCESSES / OUTPUTS / TOLERANCES (the four elements):
#   Inputs:    an audio file ffmpeg can decode (a window of it,
#              by --seek/--duration, when the caller names one);
#              the two faces (the Familia's notation face, the
#              named shelf face).
#   Processes: decode (windowed) -> weigh (FFT per frame, the
#              visualizer's discipline) -> draw (PIL) -> encode
#              (ffmpeg/x264 under mp4profile's law, audio copied
#              where lawful).
#   Outputs:   one MP4 whose duration is the weighed window's
#              duration (within one frame), plus a JSON run
#              summary on stdout carrying every measurement.
#   Tolerances: frame timing is exact by construction (frame i
#              weighs the window centred at (i + 1/2) / fps);
#              a stream-copied window is cut at MP3 packet
#              granularity (one frame of the codec, 24 ms at
#              48 kHz) while the analysis decode of the same
#              nominal window is sample-placed -- the summary
#              prints the output's measured duration, not the
#              nominal one; gains are a display mapping of a
#              measured spectrum, the visualizer's distinction.
# ---------------------------------------------------------------------

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from . import mp4profile
from . import visualize as viz

# ---------------------------------------------------------------------
# Constants -- the sworn figures of the scene.
# ---------------------------------------------------------------------

# The fold bands: three octaves each, geometric, edges shared so
# the three folds partition the field without gap or overlap.
FOLD_NAMES = ("LOW", "MID", "HIGH")
FOLD_BANDS = ((30.0, 240.0), (240.0, 1920.0), (1920.0, 15360.0))
PROGRAM_BAND = (FOLD_BANDS[0][0], FOLD_BANDS[-1][1])

# The card's texts, as ordered.
CARD_TITLE_LINES = ("LEX STELLARRVM PYRAMIDASPERE",
                    "TRIBUNAL TESTIMONY VISUALIZATION")
INSCRIPTION = "31^3 = 93"
# The desk's arithmetic, printed beside the inscription wherever
# the inscription is recorded (the header above, the run summary):
# both figures, neither smoothed.
ARITHMETIC = {"31^3_by_multiplication": 31 ** 3,
              "31+31+31_by_threefold_sum": 31 + 31 + 31}

# The doctrine colours (the visualizer's field, the plate's
# register): deep purple field, violet lattice, house gold, the
# green of the plate's rising field.
COLOUR_FIELD = viz.COLOUR_FIELD
COLOUR_PANEL = viz.COLOUR_PANEL
COLOUR_DIM = viz.COLOUR_DIM
COLOUR_GOLD = viz.COLOUR_GOLD
COLOUR_PALE = viz.COLOUR_PALE
COLOUR_FAINT = viz.COLOUR_FAINT
COLOUR_SPHERE_BODY = (38, 16, 62)
COLOUR_LATTICE = (150, 110, 230)
COLOUR_LATTICE_DOT = (198, 164, 255)
COLOUR_GREEN = (36, 205, 122)
COLOUR_GREEN_DEEP = (18, 150, 92)
COLOUR_FRAME = (70, 44, 110)

STAR_POINTS = 12        # the plate's star, counted in projection
BRIGHTNESS_STEPS = 24   # the sphere tiles' brightness cache grain


# ---------------------------------------------------------------------
# The pyramid frame -- 31 nodes, counted from the layout. Pure.
# ---------------------------------------------------------------------

def pyramid_rows(width, height):
    """The frame's rows, crown first, as (x, y) lists. Pure.

    MECHANISM: the instrument's frame -- tiers of 1^2, 2^2, 3^2,
    4^2 nodes (1, 4, 9, 16) at one constant pitch, every row
    centred on the field's axis, crowned by the thirty-first
    node at the apex joint above the 1-tier. Rows are returned
    crown-first: [[crown], [1 tier], [4 tier], [9 tier],
    [16 tier]]. The pitch is one node spacing for every tier, so
    a tier's width is (count - 1) pitches and the lattice is a
    true square-number lattice, not a set of rows stretched to
    fit a triangle.
    """
    cx = width / 2.0
    pitch = width * 0.040625
    crown = [(cx, height * 0.4583)]
    tiers = []
    for count, y_frac in ((1, 0.5333), (4, 0.6139),
                          (9, 0.6972), (16, 0.7806)):
        y = height * y_frac
        x0 = cx - (count - 1) * pitch / 2.0
        tiers.append([(x0 + k * pitch, y) for k in range(count)])
    return [crown] + tiers


def pyramid_nodes(width, height):
    """The frame's nodes as one flat list, row order. Pure.

    MECHANISM: the flattening of pyramid_rows(); its length IS
    the node count the run summary swears by -- 1 + 1 + 4 + 9 +
    16 = 31 by construction, counted here, not asserted.
    """
    return [node for row in pyramid_rows(width, height)
            for node in row]


def node_edges(rows):
    """The frame's members: which nodes a line joins. Pure.

    MECHANISM: within a row, consecutive nodes are joined (the
    tier stringers). Between rows, each node is joined to the
    nearest node of the row above by horizontal distance, ties
    taking both (a node centred between two above is a joint of
    both). The crown joins the 1-tier beneath it by the same
    rule. Returns a list of ((x1, y1), (x2, y2)) pairs.
    """
    edges = []
    for row in rows:
        for a, b in zip(row, row[1:]):
            edges.append((a, b))
    for upper, lower in zip(rows, rows[1:]):
        for node in lower:
            best = min(abs(node[0] - u[0]) for u in upper)
            for u in upper:
                if abs(node[0] - u[0]) == best:
                    edges.append((u, node))
    return edges


# ---------------------------------------------------------------------
# The three seats -- the folds climb the pyramid. Pure.
# ---------------------------------------------------------------------

def sphere_seats(width, height):
    """The three Pyramidaspheres' seats, in pyramid order. Pure.

    MECHANISM: pyramid order is apex first, then the base from
    the left: the apex carries the HIGH fold, the base-left the
    LOW, the base-right the MID -- the folds ascend base-left ->
    base-right -> apex. Each seat is {'name', 'fold', 'cx',
    'cy', 'r'} in frame coordinates.
    """
    return [
        {"name": "APEX", "fold": "HIGH",
         "cx": width * 0.500, "cy": height * 0.2611,
         "r": height * 0.1417},
        {"name": "BASE LEFT", "fold": "LOW",
         "cx": width * 0.250, "cy": height * 0.6389,
         "r": height * 0.1583},
        {"name": "BASE RIGHT", "fold": "MID",
         "cx": width * 0.750, "cy": height * 0.6389,
         "r": height * 0.1583},
    ]


def star_points(cx, cy, r_outer, r_inner, points=STAR_POINTS):
    """A star polygon's vertices, first point straight up. Pure.

    MECHANISM: 2 * points vertices alternating outer and inner
    radius, the first at -90 degrees (the plate's star stands
    one point up). The drawing joins them in order and closes
    the polygon; a second, smaller star rotated half a step is
    laid over it at draw time for the plate's compound read.
    """
    pts = []
    for k in range(2 * points):
        r = r_outer if k % 2 == 0 else r_inner
        a = -math.pi / 2.0 + k * math.pi / points
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ---------------------------------------------------------------------
# The fold weighing -- the visualizer's discipline, broad bands.
# Pure (numpy only).
# ---------------------------------------------------------------------

def fold_energy(mags, freqs, lo, hi):
    """Mean spectral magnitude inside a fold's band. Pure.

    MECHANISM: the visualizer's band law carried to a broad
    band -- the MEAN, not the sum, so a band holding more FFT
    bins earns no advantage from its width. An empty band
    weighs 0.0; the absence is data.
    """
    inside = (freqs >= lo) & (freqs < hi)
    if not inside.any():
        return 0.0
    return float(mags[inside].mean())


def analyse_folds(samples, sr, fps):
    """Weigh a whole file: per-frame fold gains + program gains.

    MECHANISM: the visualizer's two passes, folded. The first
    walks every frame's FFT window (the visualizer's FFT_SIZE,
    Hann-windowed, centred on the frame's moment, zero-padded
    at the edges) and records the three folds' raw energies and
    the program energy (the mean magnitude across the whole
    fold field). ONE reference -- the strongest fold-energy
    anywhere in the file -- serves all three folds, so the
    spheres are weighed against each other honestly; the
    program meter keeps its own reference, being a meter of the
    whole against itself. The second pass maps energies through
    the visualizer's own gain_from_energy and smooth_gain,
    imported, never forked. Returns (fold_gains, program_gains,
    reference, program_reference): fold_gains[i] is a (LOW,
    MID, HIGH) tuple for frame i.
    """
    n_frames = viz.frame_count(len(samples) / sr, fps)
    window = np.hanning(viz.FFT_SIZE).astype(np.float32)
    freqs = np.fft.rfftfreq(viz.FFT_SIZE, d=1.0 / sr)
    energies = np.zeros((n_frames, len(FOLD_BANDS)), dtype=np.float64)
    program = np.zeros(n_frames, dtype=np.float64)
    for i in range(n_frames):
        centre = int(viz.frame_centre(i, fps) * sr)
        start = centre - viz.FFT_SIZE // 2
        chunk = np.zeros(viz.FFT_SIZE, dtype=np.float32)
        src_lo = max(0, start)
        src_hi = min(len(samples), start + viz.FFT_SIZE)
        if src_hi > src_lo:
            chunk[src_lo - start:src_hi - start] = samples[src_lo:src_hi]
        mags = np.abs(np.fft.rfft(chunk * window))
        for j, (lo, hi) in enumerate(FOLD_BANDS):
            energies[i, j] = fold_energy(mags, freqs, lo, hi)
        program[i] = fold_energy(mags, freqs, *PROGRAM_BAND)
    reference = float(energies.max()) if energies.size else 0.0
    program_reference = float(program.max()) if program.size else 0.0
    fold_gains = np.zeros_like(energies)
    previous = np.zeros(len(FOLD_BANDS), dtype=np.float64)
    prog_gains = np.zeros(n_frames, dtype=np.float64)
    prog_prev = 0.0
    for i in range(n_frames):
        for j in range(len(FOLD_BANDS)):
            raw = viz.gain_from_energy(energies[i, j], reference)
            previous[j] = viz.smooth_gain(previous[j], raw)
            fold_gains[i, j] = previous[j]
        raw_p = viz.gain_from_energy(program[i], program_reference)
        prog_prev = viz.smooth_gain(prog_prev, raw_p)
        prog_gains[i] = prog_prev
    return fold_gains, prog_gains, reference, program_reference


# ---------------------------------------------------------------------
# The impure rim -- decode, draw, encode. Kept thin, at the edges.
# ---------------------------------------------------------------------

def _lerp(a, b, t):
    """A colour between two colours at t in [0, 1]."""
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _text(draw, xy, s, font, fill, anchor="la"):
    draw.text(xy, s, font=font, fill=fill, anchor=anchor)


def decode_window(path, seek=0.0, duration=None):
    """Decode a window of any ffmpeg-readable audio. Rim.

    MECHANISM: the visualizer's decode (ffmpeg to raw float
    samples, the lab-bridge pattern) with the caller's window:
    -ss/-t ride before the input so the decode is placed at the
    named moment. Analysis only -- the artifact's own stream is
    muxed untouched at encode time.
    """
    cmd = ["ffmpeg", "-v", "error"]
    if seek:
        cmd += ["-ss", f"{seek:.3f}"]
    if duration:
        cmd += ["-t", f"{duration:.3f}"]
    cmd += ["-i", str(path), "-f", "f32le", "-ac", "1",
            "-ar", str(viz.ANALYSIS_SR), "-"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32).copy()


def _hash2(i, j):
    """A deterministic positional hash in [0, 1). Pure.

    MECHANISM: the green field's dot scatter must re-strike
    identically on every render (the house's seeded-noise
    doctrine), so its 'randomness' is a hash of the dot's own
    grid seat -- no RNG state, no clock, the same sphere every
    time the same code draws it.
    """
    v = (i * 73856093) ^ (j * 19349663) ^ 0x93
    return ((v * 2654435761) % 100000) / 100000.0


def sphere_tile(radius):
    """One Pyramidasphere's still body, drawn once. Rim (PIL).

    MECHANISM: a square tile of 2r x 2r holding the plate's
    register: the dark body; the lattice -- parallels and
    meridians as ellipse outlines in violet, with glowing dots
    where the plate's grid points shine (dots stepped along
    each parallel's ellipse); the green field rising in the
    lower hemisphere (dots seated by the positional hash, their
    density and brightness growing with depth, as the plate's
    field rises); the gold rim. The star is NOT in the tile --
    it flares with the fold's energy and is drawn per frame.
    Brightness by energy is applied to the whole tile at paste
    time through a quantized cache (see ScenePainter).
    """
    r = int(radius)
    size = 2 * r
    img = Image.new("RGB", (size, size), COLOUR_FIELD)
    d = ImageDraw.Draw(img)
    cx = cy = r
    d.ellipse([0, 0, size - 1, size - 1], fill=COLOUR_SPHERE_BODY)

    # The green field: dots in the lower hemisphere, denser and
    # brighter with depth. A dot is seated where its positional
    # hash falls under the depth's density law.
    step = max(5, r // 12)
    for gy in range(-r + 4, r - 2, step):
        for gx in range(-r + 4, r - 2, step):
            if gx * gx + gy * gy > (r - 5) ** 2:
                continue
            depth = gy / r            # -1 top .. +1 bottom
            if depth < -0.05:
                continue              # the field is a lower sea
            density = 0.10 + 0.85 * ((depth + 0.05) / 1.05) ** 1.5
            if _hash2(gx, gy) < density:
                colour = _lerp(COLOUR_GREEN_DEEP, COLOUR_GREEN,
                               min(1.0, (depth + 0.3) / 1.3))
                d.ellipse([cx + gx - 1.6, cy + gy - 1.6,
                           cx + gx + 1.6, cy + gy + 1.6], fill=colour)

    # The lattice: parallels (ellipse outlines at latitudes)
    # with their glowing grid dots, then meridians.
    for lat_deg in (-62, -42, -22, 0, 22, 42, 62):
        lat = math.radians(lat_deg)
        off = r * math.sin(lat)
        half_chord = r * math.cos(lat)
        eh = 0.20 * half_chord
        width = 2 if lat_deg == 0 else 1
        d.ellipse([cx - half_chord, cy + off - eh,
                   cx + half_chord, cy + off + eh],
                  outline=COLOUR_LATTICE, width=width)
        for k in range(15):
            t = k * 2.0 * math.pi / 15.0
            px = cx + half_chord * math.cos(t)
            py = cy + off + eh * math.sin(t)
            d.ellipse([px - 1.4, py - 1.4, px + 1.4, py + 1.4],
                      fill=COLOUR_LATTICE_DOT)
    for frac in (0.30, 0.58, 0.84):
        a = r * frac
        d.ellipse([cx - a, cy - r, cx + a, cy + r],
                  outline=COLOUR_LATTICE, width=1)
    d.line([(cx, cy - r), (cx, cy + r)], fill=COLOUR_LATTICE, width=1)

    # The rim: the plate's gold ring of light.
    d.ellipse([1, 1, size - 2, size - 2], outline=COLOUR_GOLD, width=3)
    d.ellipse([4, 4, size - 5, size - 5], outline=COLOUR_DIM, width=1)
    return img


class ScenePainter:
    """The scene's per-render drawing state. Rim (PIL).

    MECHANISM: the sphere tiles are drawn once per radius and
    re-struck at quantized brightness levels through a cache --
    a sphere's brightness answers its fold's gain, and the
    cache keeps 1,800 frames from re-drawing 1,800 lattices.
    The faces are the visualizer's own Faces (the Familia's
    notation face, the named shelf face, substitutions named
    in the run summary through abc_used).
    """

    def __init__(self):
        self.faces = viz.Faces()
        self._tiles = {}
        self._bright = {}
        self._masks = {}

    def mask(self, radius):
        """The circular paste mask for a seat's tile.

        MECHANISM: a tile is square and its corners are field,
        but a brightness factor under 1 darkens those corners
        BELOW the frame's field, so an unmasked paste stands in
        the frame as a dark square around the sphere (the first
        demo strike showed exactly that). The mask -- a filled
        circle in an L image, cached per radius -- pastes only
        the sphere's own disc; the field outside the rim is the
        frame's, untouched.
        """
        key_r = int(round(radius))
        if key_r not in self._masks:
            m = Image.new("L", (2 * key_r, 2 * key_r), 0)
            ImageDraw.Draw(m).ellipse([0, 0, 2 * key_r - 1,
                                       2 * key_r - 1], fill=255)
            self._masks[key_r] = m
        return self._masks[key_r]

    def tile(self, radius, gain):
        key_r = int(round(radius))
        if key_r not in self._tiles:
            self._tiles[key_r] = sphere_tile(key_r)
        factor = 0.38 + 0.82 * float(gain)
        step = int(round(factor * BRIGHTNESS_STEPS))
        key = (key_r, step)
        if key not in self._bright:
            self._bright[key] = ImageEnhance.Brightness(
                self._tiles[key_r]).enhance(step / BRIGHTNESS_STEPS)
        return self._bright[key]


def draw_card(width, height, source_lines, faces):
    """The opening card: the title as ordered, the inscription.

    MECHANISM: a still held for the card seconds -- the title
    in the notation face exactly as the founder ordered it, the
    inscription "31^3 = 93" in the bold shelf face (the notation
    face's seat is letters; the inscription is arithmetic and
    stands in the face that carries figures), named on the card
    itself as the founder's declared equation, the source
    window named, the honest label, and the Flagpole.
    """
    img = Image.new("RGB", (width, height), COLOUR_FIELD)
    d = ImageDraw.Draw(img)
    cx = width // 2
    _text(d, (cx, height * 0.20), CARD_TITLE_LINES[0],
          faces.font("abc", 42), COLOUR_GOLD, "ma")
    _text(d, (cx, height * 0.20 + 58), CARD_TITLE_LINES[1],
          faces.font("abc", 42), COLOUR_GOLD, "ma")
    _text(d, (cx, height * 0.44), INSCRIPTION,
          faces.font("sans-bold", 54), COLOUR_GOLD, "ma")
    _text(d, (cx, height * 0.44 + 66),
          "the founder's declared equation",
          faces.font("sans", 16), COLOUR_FAINT, "ma")
    _text(d, (cx, height * 0.44 + 100),
          "Three Pyramidaspheres in a 3-fold pyramid of 31 nodes",
          faces.font("sans", 19), COLOUR_PALE, "ma")
    y = height * 0.44 + 140
    for line in source_lines:
        _text(d, (cx, y), line, faces.font("sans", 17),
              COLOUR_PALE, "ma")
        y += 26
    _text(d, (cx, height - 92),
          "Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,",
          faces.font("sans", 17), COLOUR_FAINT, "ma")
    _text(d, (cx, height - 66),
          "ARR, All Rights Reserved, Without Prejudice.",
          faces.font("sans", 17), COLOUR_FAINT, "ma")
    _text(d, (cx, height - 34), "93 -- Live, Love, and let Love, Live.",
          faces.font("sans", 17), COLOUR_DIM, "ma")
    return img


def draw_frame(width, height, painter, fold_gains, program_gain,
               elapsed, duration, source_name):
    """One frame of the Pyramidasphere scene.

    MECHANISM: the frame in draw order -- the pyramid's frame
    first (its stringers and tier edges, dim violet warming
    with the program gain), the three sphere tiles pasted at
    their seats at their folds' brightness, the gold stars
    flaring at the spheres' hearts, the 31 nodes struck last
    as the frame's joints (lit by the program gain), the fold
    labels beneath their spheres, and the house's furniture
    (heading, elapsed time). fold_gains is a {'LOW','MID',
    'HIGH'} mapping; each sphere answers its own fold.
    """
    faces = painter.faces
    img = Image.new("RGB", (width, height), COLOUR_FIELD)
    d = ImageDraw.Draw(img)
    margin = 72
    rows = pyramid_rows(width, height)
    nodes = [n for row in rows for n in row]
    seats = sphere_seats(width, height)
    crown = rows[0][0]
    base_y = height * 0.8556
    corners = [(width * 0.1906, base_y), (width * 0.8094, base_y)]

    _text(d, (margin, 30), "LEX STELLARRVM PYRAMIDASPERE",
          faces.font("abc", 26), COLOUR_GOLD)
    _text(d, (width - margin, 36), source_name,
          faces.font("sans", 15), COLOUR_FAINT, "ra")
    _text(d, (margin, 64),
          "Tribunal Testimony Visualization -- the folds: LOW - MID - HIGH",
          faces.font("sans", 13), COLOUR_FAINT)

    # The frame: stringers crown-to-corners, the base line, and
    # the node lattice's members, warming with the program.
    edge_colour = _lerp(COLOUR_FRAME, COLOUR_DIM,
                        0.25 + 0.55 * program_gain)
    d.line([crown, corners[0]], fill=edge_colour, width=2)
    d.line([crown, corners[1]], fill=edge_colour, width=2)
    d.line([corners[0], corners[1]], fill=edge_colour, width=2)
    for a, b in node_edges(rows):
        d.line([a, b], fill=edge_colour, width=1)

    # The spheres at their seats, each at its fold's brightness,
    # its star flaring with the same gain.
    for seat in seats:
        gain = float(fold_gains.get(seat["fold"], 0.0))
        tile = painter.tile(seat["r"], gain)
        r = int(round(seat["r"]))
        img.paste(tile, (int(seat["cx"]) - r, int(seat["cy"]) - r),
                  painter.mask(seat["r"]))
        star_colour = _lerp(COLOUR_DIM, COLOUR_GOLD, 0.25 + 0.75 * gain)
        r_out = seat["r"] * (0.30 + 0.22 * gain)
        for scale, rot in ((1.0, 0.0), (0.58, math.pi / STAR_POINTS)):
            pts = star_points(seat["cx"], seat["cy"],
                              r_out * scale, r_out * scale * 0.45)
            if rot:
                pts = [(seat["cx"] + (x - seat["cx"]) * math.cos(rot)
                        - (y - seat["cy"]) * math.sin(rot),
                        seat["cy"] + (x - seat["cx"]) * math.sin(rot)
                        + (y - seat["cy"]) * math.cos(rot))
                       for x, y in pts]
            d.polygon(pts, outline=star_colour, width=2)
        core = 2.0 + 5.0 * gain
        d.ellipse([seat["cx"] - core, seat["cy"] - core,
                   seat["cx"] + core, seat["cy"] + core],
                  fill=_lerp(COLOUR_PALE, COLOUR_GOLD, gain))
        _text(d, (seat["cx"], seat["cy"] + seat["r"] + 12),
              f"FOLD - {seat['fold']}", faces.font("abc", 19),
              _lerp(COLOUR_DIM, COLOUR_GOLD, 0.2 + 0.8 * gain), "ma")

    # The 31 nodes: the frame's joints, lit by the program.
    node_colour = _lerp(COLOUR_DIM, COLOUR_GOLD,
                        0.15 + 0.85 * program_gain)
    node_r = 3.0 + 2.5 * program_gain
    for i, (x, y) in enumerate(nodes):
        rr = node_r + (1.5 if i == 0 else 0.0)   # the crown stands out
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=node_colour)

    _text(d, (margin, height - 26),
          f"{elapsed:0.1f} s / {duration:0.1f} s",
          faces.font("sans", 14), COLOUR_FAINT)
    _text(d, (width // 2, height - 26), "THE 31-NODE PYRAMID - 31^3 = 93",
          faces.font("sans", 13), COLOUR_FAINT, "ma")
    _text(d, (width - margin, height - 26), "RESONANTIA VISUALIZER",
          faces.font("sans", 14), COLOUR_FAINT, "ra")
    return img


def encode(frames, source_audio, out_path, fps, width, height,
           seek=0.0, duration=None):
    """Pipe drawn frames into ffmpeg; mux the source's window.

    MECHANISM: the visualizer's encode under mp4profile's law:
    raw RGB frames on stdin; the source file is the second
    input, windowed by -ss/-t when the caller names a window,
    its audio stream mapped and COPIED -- the master's own
    bytes ride the video untouched. The audio ladder is
    mp4profile's for a sealed master (copy first, AAC at the
    sworn 320,000 bps the one fallback); the video tail --
    codec, pixel format, CRF, faststart -- is mp4profile's
    output_args for the mode that succeeds. The returned mode
    says which rung held. A second refusal is a failure,
    reported, not worked around.
    """
    base = ["ffmpeg", "-v", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{width}x{height}", "-r", str(fps), "-i", "-"]
    if seek:
        base += ["-ss", f"{seek:.3f}"]
    if duration:
        base += ["-t", f"{duration:.3f}"]
    base += ["-i", str(source_audio), "-map", "0:v", "-map", "1:a"]
    last_err = ""
    for mode, _rung in mp4profile.audio_ladder(True):
        proc = subprocess.Popen(
            base + mp4profile.output_args(mode) + [str(out_path)],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
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


def render(audio_path, out_path, width=1280, height=720, fps=30,
           card_seconds=2.0, seek=0.0, duration=None,
           source_lines=(), source_name=None):
    """The whole road: audio in, Pyramidasphere MP4 out.

    MECHANISM: decode the window -> weigh the folds -> draw
    (card frames, then scene frames) -> encode under the house
    MP4 law. The returned summary is the run's measured
    manifest: the window, the node count counted from the
    layout actually drawn, the fold bands and their peaks, the
    references, the durations, the mux mode, and the proof
    seam's standing note.
    """
    audio_path = Path(audio_path)
    started = time.time()
    samples = decode_window(audio_path, seek=seek, duration=duration)
    weighed = len(samples) / viz.ANALYSIS_SR
    fold_gains, prog_gains, reference, prog_reference = analyse_folds(
        samples, viz.ANALYSIS_SR, fps)
    n_frames = viz.frame_count(weighed, fps)
    card_frames = min(n_frames, int(round(card_seconds * fps)))
    nodes = pyramid_nodes(width, height)
    seats = sphere_seats(width, height)
    painter = ScenePainter()
    name = source_name or audio_path.name
    lines = list(source_lines) or [f"Source: {name}"]
    fold_index = {name_: j for j, name_ in enumerate(FOLD_NAMES)}

    def frame_stream():
        card = draw_card(width, height, lines, painter.faces)
        for _ in range(card_frames):
            yield card
        for i in range(card_frames, n_frames):
            gains = {name_: float(fold_gains[i, j])
                     for name_, j in fold_index.items()}
            yield draw_frame(width, height, painter, gains,
                             float(prog_gains[i]),
                             viz.frame_centre(i, fps), weighed, name)

    audio_mode = encode(frame_stream(), audio_path, out_path, fps,
                        width, height, seek=seek, duration=duration)
    return {
        "scene": "pyramidasphere",
        "title": " ".join(CARD_TITLE_LINES),
        "inscription": INSCRIPTION,
        "inscription_kind": "the founder's declared equation",
        "arithmetic_beside_it": ARITHMETIC,
        "source": str(audio_path),
        "window": {"seek_s": seek, "duration_s": duration},
        "weighed_duration_s": round(weighed, 4),
        "frames": n_frames,
        "card_frames": card_frames,
        "fps": fps,
        "size": [width, height],
        "node_count_drawn": len(nodes),
        "node_tiers": [len(r) for r in pyramid_rows(width, height)],
        "sphere_seats": [{"name": s["name"], "fold": s["fold"]}
                         for s in seats],
        "fold_bands_hz": {n: list(b) for n, b in
                          zip(FOLD_NAMES, FOLD_BANDS)},
        "fold_reference_energy": reference,
        "program_reference_energy": prog_reference,
        "fold_gain_peaks": {n: round(float(fold_gains[:, j].max()), 4)
                            for n, j in fold_index.items()},
        "abc_face_used": painter.faces.abc_used,
        "audio_mux": audio_mode,
        "mp4_profile": "resonance/studio/mp4profile.py output_args "
                       "(libx264, yuv420p, CRF 18, +faststart)",
        "proof": "UNSTAMPED -- no ledger kind covers a visualizer "
                 "render; the ledger is untouched",
        "wall_time_s": round(time.time() - started, 2),
    }


def main(argv=None):
    """The CLI door: `python3 -m resonance.studio.pyramidasphere`.

    MECHANISM: argparse in the studio's idiom; the run summary
    is printed as JSON on stdout, the studio's habit for
    machine-readable receipts.
    """
    p = argparse.ArgumentParser(
        prog="pyramidasphere",
        description="Render an audio file (or a window of it) as a "
                    "Pyramidasphere visualization video.")
    p.add_argument("input", help="source audio (WAV/MP3)")
    p.add_argument("output", help="destination MP4")
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=720)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--card-seconds", type=float, default=2.0)
    p.add_argument("--seek", type=float, default=0.0,
                   help="window start, seconds into the source")
    p.add_argument("--duration", type=float, default=None,
                   help="window length, seconds (default: to the end)")
    p.add_argument("--window-note", default=None,
                   help="small-print line naming the window, for the card")
    args = p.parse_args(argv)
    lines = [f"Source: {Path(args.input).name}"]
    if args.window_note:
        lines.append(args.window_note)
    summary = render(args.input, args.output, width=args.width,
                     height=args.height, fps=args.fps,
                     card_seconds=args.card_seconds, seek=args.seek,
                     duration=args.duration, source_lines=lines)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 93 -- Live, Love, and let Love, Live.
