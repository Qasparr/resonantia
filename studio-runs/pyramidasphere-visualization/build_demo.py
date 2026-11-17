# 93
# ---------------------------------------------------------------------
# build_demo.py -- The demonstration strike of the Pyramidasphere
# scene: the Tribunal Testimony Visualization.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# THE MEDIA ROAD, and the evidence for it: the founder's order
# names "Tribunal Testimony" -- a TEXT work in the house record
# (the Ali ode; the MAGVS witness instrument). A search of the
# workspace for Tribunal Testimony AUDIO (find over ~/workspace
# for *tribunal* in the audio extensions mp3/wav/m4a/flac/ogg)
# returned NOTHING; every *tribunal* hit is a document (PDF, MD,
# HTML, webp). No dedicated track exists to strike. The road
# taken is therefore the brief's second road: a precise
# 60-second excerpt of the sealed Pirate Essay audiobook's
# section IX, the Truth Audit -- the testimony section of the
# sealed master -- rendered by the new scene, its card and this
# record naming it an excerpt.
#
# THE OFFSET, computed, not recollected: the pilot's assembly
# (RUN-REPORT.md of the run, section IV) joined 21 chunks with
# 1.2 s of silence between chunks (2.5 s only before the Annex,
# chunk 18, and the Colophon, chunk 21 -- both AFTER section
# IX). Section IX is chunk 16 (16-s9-audit.wav). This driver
# measures chunks 01-15 from the run folder at strike time and
# adds the 15 joins of 1.2 s that precede chunk 16:
#   sum(chunks 01..15) = 2611.800 s   (ffprobe, this strike)
#   joins before IX    =  15 x 1.2   =   18.000 s
#   SECTION IX OFFSET  = 2629.800 s
# Cross-checks, both printed in the summary: the report's
# rounded part-table sums to 2612 s before IX (the chunk sum
# within its rounding), and chunks + all joins reconstruct the
# master's measured 3839.716667 s to under a millisecond.
#
# THE STRIKE: pyramidasphere.render() over the window
# [offset, offset + 60 s) of the sealed master -- the analysis
# decodes that window, the mux copies the master's own stream
# for that window under the house MP4 law. The render stands
# UNSTAMPED (no proof kind covers it; the ledger is untouched).
#
# THE VERIFICATION, in this same driver: the MP4 is re-probed
# (duration, streams -- the audio must read mp3, i.e. copied),
# and two distant scene frames (t = 12 s, t = 47 s) are
# extracted and compared pixel by pixel (the visualizer's own
# standard: mean absolute difference per channel and the share
# of pixels materially changed). Everything is written to
# RUN-SUMMARY.json beside the MP4.
# ---------------------------------------------------------------------

import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from resonance.studio import pyramidasphere as pyr

RUN1 = REPO / "studio-runs" / "pirate-essay-audiobook-run1"
MASTER = (Path.home() / "workspace" / "your_files" / "pirate-essay"
          / "THE-PIRATE-ESSAY-AUDIOBOOK.mp3")
HERE = Path(__file__).resolve().parent
OUT_MP4 = HERE / "tribunal-testimony-pyramidasphere.mp4"
EXCERPT_S = 60.0
JOIN_S = 1.2


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True,
        check=True)
    return float(out.stdout.strip())


def chunk_offset():
    """Section IX's offset in the master, measured this strike.

    MECHANISM: ffprobe every chunk WAV of run 1 in order; the
    offset is the sum of chunks 01-15 plus the fifteen 1.2 s
    joins that precede chunk 16. The reconstruction of the
    whole program (all chunks + all joins, the Annex and
    Colophon joins at 2.5 s) is returned beside it as the
    cross-check against the master's measured duration.
    """
    durations = []
    for n in range(1, 22):
        wav = sorted((RUN1 / "chunks").glob(f"{n:02d}-*.wav"))[0]
        durations.append(probe_duration(wav))
    offset = sum(durations[:15]) + 15 * JOIN_S
    joins_total = 18 * JOIN_S + 2 * 2.5
    reconstructed = sum(durations) + joins_total
    return offset, durations[15], reconstructed


def extract_frame(mp4, at_s, out_png):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", f"{at_s}", "-i",
         str(mp4), "-frames:v", "1", str(out_png)], check=True)


def frame_variance(png_a, png_b):
    """The visualizer's moving-frames standard, pixel by pixel."""
    a = np.asarray(Image.open(png_a), dtype=np.float32)
    b = np.asarray(Image.open(png_b), dtype=np.float32)
    diff = np.abs(a - b)
    return {
        "mean_abs_diff_per_channel": round(float(diff.mean()), 4),
        "pct_pixels_materially_changed": round(
            float((diff.max(axis=2) > 8).mean()) * 100.0, 3),
    }


def main():
    offset, s9_duration, reconstructed = chunk_offset()
    master_duration = probe_duration(MASTER)
    source_lines = [
        "Excerpt of the sealed master: THE-PIRATE-ESSAY-AUDIOBOOK.mp3",
        f"Section IX -- the Truth Audit (the testimony section), "
        f"60 s from {offset:.3f} s",
    ]
    summary = pyr.render(
        MASTER, OUT_MP4, seek=offset, duration=EXCERPT_S,
        source_lines=source_lines,
        source_name="THE-PIRATE-ESSAY-AUDIOBOOK.mp3 (excerpt, S IX)")

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_name,width,height:format=duration,size",
         "-of", "json", str(OUT_MP4)], capture_output=True,
        text=True, check=True)
    probed = json.loads(probe.stdout)
    extract_frame(OUT_MP4, 1.0, HERE / "frame-card.png")
    extract_frame(OUT_MP4, 12.0, HERE / "frame-12s.png")
    extract_frame(OUT_MP4, 47.0, HERE / "frame-47s.png")
    summary["media_road"] = {
        "dedicated_tribunal_testimony_audio": "none found -- find "
            "over ~/workspace for *tribunal* in mp3/wav/m4a/flac/ogg "
            "returned nothing; every *tribunal* hit is a document",
        "road_taken": "excerpt of the sealed Pirate Essay audiobook "
                      "master, section IX (the Truth Audit)",
        "section_ix_offset_s": round(offset, 3),
        "section_ix_duration_s": round(s9_duration, 3),
        "offset_derivation": "sum of run-1 chunks 01-15 measured "
            "by ffprobe at strike time + 15 joins x 1.2 s",
        "program_reconstruction_s": round(reconstructed, 4),
        "master_duration_s": round(master_duration, 4),
        "reconstruction_delta_s": round(
            abs(reconstructed - master_duration), 4),
    }
    summary["output_probe"] = probed
    summary["output_duration_delta_vs_window_s"] = round(
        abs(float(probed["format"]["duration"]) - EXCERPT_S), 4)
    summary["frame_variance_12s_vs_47s"] = frame_variance(
        HERE / "frame-12s.png", HERE / "frame-47s.png")
    (HERE / "RUN-SUMMARY.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 93 -- Live, Love, and let Love, Live.
