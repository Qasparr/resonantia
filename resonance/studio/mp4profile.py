# 93
# ---------------------------------------------------------------------
# mp4profile.py -- One house encode profile for every MP4.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: pure functions that build the encode law -- the
# geometry (fit within the sworn frame, never upscale, even
# dimensions), the video arguments (H.264, yuv420p, the sworn
# quality), the audio ladder (a sealed master's bytes copied;
# AAC at the sworn bitrate as the one reported fallback), and
# the faststart flag -- as argument lists a caller splices into
# its own ffmpeg invocation. No subprocess lives here: the
# callers keep their loops (frames piped on stdin, a still image
# looped), and this module keeps the law they share, so the law
# can be weighed by tests with no ffmpeg in the room.
#
# DOCTRINE -- WHY ONE PROFILE: on the night this was written the
# house's young MP4 path had two callers, born hours apart, each
# hand-rolling the same encode: the visualizer (studio/visualize.py)
# and the audiobook pilot's video edition (studio-runs). Both had
# already converged on the substance -- libx264, yuv420p, the
# master's audio copied, AAC at 320,000 bps as the single
# fallback, the mode reported either way -- and differed only in
# accidents: 1280x720 against 1920x1080, a stillimage tune in one
# and not the other, and NEITHER carrying faststart, so a listener
# opening the file over the wire waits for the whole body before
# the first frame. A law stated twice will drift; stated once, it
# can be sworn. This module is that one statement.
#
# THE AUDIO RULE, stated plainly (both callers' observed law,
# generalized): where the source audio is a SEALED MASTER, its
# bytes are the sworn body and are copied unaltered; if the
# container refuses the copy, the encode retries ONCE with AAC
# at the sworn 320,000 bps and the returned mode says which
# happened -- 'copy' or 'aac-320k' -- and a second refusal is a
# failure, reported, not worked around. Where the source is NOT
# a sealed master there are no sworn bytes to preserve, and the
# ladder is the AAC rung alone.
#
# THE WIRING, named as the follow-up it is: on the night this
# module landed, both callers were in flight under other hands
# (the visualizer untracked and mid-build, the pilot's script a
# working file in its run folder), and the concurrency law of
# the house forbids wiring into files another build is editing.
# The module therefore lands with its tests, and the wiring --
# visualize.encode() and the pilot's successors building their
# argv from output_args()/audio_ladder() -- is the named next
# step, to be taken when those files are at rest.
#
# Tolerances (the fourth element): geometry is exact (integer
# arithmetic, scale factor never above 1, dimensions floored to
# even); the quality figure is the visualizer's sworn CRF 18;
# the audio bitrate is the house's sworn 320,000 bps, the same
# figure the mastering gate swears by.
# ---------------------------------------------------------------------

# The sworn figures of the house MP4.
MAX_WIDTH = 1920
MAX_HEIGHT = 1080
VIDEO_CODEC = "libx264"
PIX_FMT = "yuv420p"
PRESET = "medium"
CRF = 18
AUDIO_BITRATE_BPS = 320000
MOVFLAGS = "+faststart"

MODE_COPY = "copy"
MODE_AAC = "aac-320k"


def fit_within(width, height, max_width=MAX_WIDTH,
               max_height=MAX_HEIGHT):
    """Fit a frame within the sworn bounds; never upscale.

    MECHANISM: the scale is the smaller of the two bound ratios
    and 1 (an already-fitting frame is returned untouched, the
    no-upscale law); both dimensions are then floored to even,
    as yuv420p requires, with a floor of 2 so no dimension can
    vanish. Returns (width, height).
    """
    if width <= 0 or height <= 0:
        raise ValueError(f"frame dimensions must be positive, "
                         f"got {width}x{height}")
    scale = min(max_width / width, max_height / height, 1.0)
    w = int(width * scale)
    h = int(height * scale)
    return max(2, w - (w % 2)), max(2, h - (h % 2))


def audio_ladder(source_is_master):
    """The audio rungs, in the order they are attempted.

    Returns [(mode, argv)] -- for a sealed master, the copy rung
    first and the AAC rung as its one fallback; for any other
    source, the AAC rung alone (the rule stated in the header).
    The caller reports the mode that succeeded; a mode is a
    fact about the artifact, not a detail to be smoothed.
    """
    aac = (MODE_AAC, ["-c:a", "aac", "-b:a",
                      str(AUDIO_BITRATE_BPS // 1000) + "k"])
    if source_is_master:
        return [(MODE_COPY, ["-c:a", "copy"]), aac]
    return [aac]


def output_args(audio_mode, tune=None):
    """The shared encode tail: video law, one audio rung, the
    faststart flag -- everything after the caller's inputs and
    mappings, before the output path.

    MECHANISM: tune is the caller's to name (a still-image
    edition passes 'stillimage'; a drawn-frame render passes
    None) -- the profile governs the codec law, not the
    caller's subject. An unknown audio_mode is refused by name:
    a mode outside the ladder is not a rung.
    """
    modes = dict(audio_ladder(True) + audio_ladder(False))
    if audio_mode not in modes:
        raise ValueError(f"audio mode {audio_mode!r} is not a "
                         f"rung of the house ladder "
                         f"({sorted(modes)})")
    args = ["-c:v", VIDEO_CODEC, "-pix_fmt", PIX_FMT,
            "-preset", PRESET, "-crf", str(CRF)]
    if tune:
        args += ["-tune", tune]
    args += modes[audio_mode]
    args += ["-movflags", MOVFLAGS]
    return args


def build_command(input_args, output_path, *, audio_mode,
                  tune=None):
    """A whole ffmpeg argv: the house's quiet flags, the
    caller's input half, the profile's tail, the output.

    For callers whose encode is a single subprocess run; the
    frame-piping callers splice output_args() into their own
    command instead, under the same law.
    """
    return ["ffmpeg", "-v", "error", "-y", *input_args,
            *output_args(audio_mode, tune=tune),
            str(output_path)]
