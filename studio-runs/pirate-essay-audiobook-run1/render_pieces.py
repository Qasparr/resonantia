#!/usr/bin/env python3
# =====================================================================
# RENDER PIECES -- the narration batch driver, second form.
#
# WHY THIS DRIVER EXISTS (the record, at full size): llama-tts in
# this build carries TWO silent ceilings. The first, found on the
# batch's first strike: a default generation cap of 512 frames
# (33.5 s), passed with -n 9000. The second, found when chunks 02
# and 04 both stopped at EXACTLY 1999 frames with identical byte
# counts on different texts: a hard frame ceiling at 1999 frames
# (~133 s) that no flag in the proven invocation lifts. Both
# ceilings truncate without a word of complaint.
#
# THE ANSWER: no generation is ever asked for more than a piece of
# <= 190 words (~1,300 frames at this material's observed density),
# pieces are joined inside their chunk with 0.35 s of silence, and
# every piece is validated on landing: frames >= 1990 means the
# ceiling was touched (split the piece and re-render); a
# frames-per-word ratio outside [3.0, 9.0] flags a suspected
# premature stop for the run report. Chunks already accepted
# complete (01, 03, 05 -- frame counts inside the plausible band
# for their word counts, mutually consistent) carry .done markers
# and are not re-rendered.
# =====================================================================

import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = Path.home() / "workspace" / "lab" / "zonos3-mini"
BIN = LAB / "bin" / "llama-b12438" / "llama-tts"
MODEL = LAB / "models" / "ZONOS3-Mini-Q8_0.gguf"
MPROJ = LAB / "models" / "mmproj-ZONOS3-Mini-F32.gguf"
VOICE = "Imogen_en-British_F_1"
SCRIPT = HERE / "script"
CHUNKS = HERE / "chunks"
PIECES = HERE / "pieces"
MAX_WORDS = 190
CEILING_FRAMES = 1990
LOG = HERE / "pieces.log"


def log(rec):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(rec, flush=True)


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def make_pieces(text, max_words=MAX_WORDS):
    pieces, cur, cur_w = [], [], 0
    for para in text.split("\n\n"):
        for sent in split_sentences(para):
            w = len(sent.split())
            if w > max_words:  # a single long sentence: clause-split
                clauses = re.split(r"(?<=,)\s+", sent)
                buf, bw = [], 0
                for cl in clauses:
                    cw = len(cl.split())
                    if bw + cw > max_words and buf:
                        pieces.append(" ".join(buf))
                        buf, bw = [], 0
                    buf.append(cl)
                    bw += cw
                if buf:
                    sent = " ".join(buf)
                    w = bw
                    if cur_w + w > max_words and cur:
                        pieces.append(" ".join(cur))
                        cur, cur_w = [], 0
                    cur.append(sent)
                    cur_w += w
                continue
            if cur_w + w > max_words and cur:
                pieces.append(" ".join(cur))
                cur, cur_w = [], 0
            cur.append(sent)
            cur_w += w
    if cur:
        pieces.append(" ".join(cur))
    return pieces


def render_piece(text, out_path):
    t0 = time.time()
    proc = subprocess.run(
        [str(BIN), "-m", str(MODEL), "-mm", str(MPROJ),
         "--tts-voice", VOICE, "-t", "4", "-n", "9000",
         "-p", text, "-o", str(out_path)],
        capture_output=True, text=True)
    wall = time.time() - t0
    frames = None
    m = re.findall(r"generated (\d+) frames", proc.stderr)
    if m:
        frames = int(m[-1])
    dur = None
    if out_path.exists():
        pr = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "csv=p=0", str(out_path)],
            capture_output=True, text=True)
        try:
            dur = float(pr.stdout.strip())
        except ValueError:
            dur = None
    return proc.returncode, frames, dur, wall


def render_chunk(name, text):
    pieces = make_pieces(text)
    piece_wavs = []
    for i, ptext in enumerate(pieces):
        words = len(ptext.split())
        out = PIECES / f"{name}-p{i:02d}.wav"
        rc, frames, dur, wall = render_piece(ptext, out)
        fpw = round(frames / words, 2) if frames and words else None
        flag = None
        if frames is not None and frames >= CEILING_FRAMES:
            flag = "CEILING TOUCHED"
        elif fpw is not None and not (3.0 <= fpw <= 9.0):
            flag = f"PACE OUTLIER frames/word={fpw}"
        log({"chunk": name, "piece": i, "words": words,
             "frames": frames, "seconds": dur, "wall_s": round(wall, 1),
             "rc": rc, "flag": flag})
        if flag == "CEILING TOUCHED":
            # Split the piece in half at sentence boundaries and
            # re-render the halves in its place.
            halves = make_pieces(ptext, max_words=MAX_WORDS // 2)
            sub_wavs = []
            for j, htext in enumerate(halves):
                hout = PIECES / f"{name}-p{i:02d}h{j}.wav"
                rc2, fr2, dur2, wall2 = render_piece(htext, hout)
                log({"chunk": name, "piece": f"{i}h{j}",
                     "words": len(htext.split()), "frames": fr2,
                     "seconds": dur2, "wall_s": round(wall2, 1),
                     "rc": rc2, "flag": "half of a ceiling piece"})
                sub_wavs.append(hout)
            piece_wavs.extend(sub_wavs)
            out.unlink(missing_ok=True)
        else:
            piece_wavs.append(out)
    # Join the chunk's pieces with 0.35 s of silence between them.
    sil = PIECES / ".sil035.wav"
    if not sil.exists():
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
             "anullsrc=r=44100:cl=mono", "-t", "0.35",
             "-c:a", "pcm_s16le", str(sil)], check=True)
    listf = PIECES / f"{name}.concat.txt"
    lines = []
    for k, pw in enumerate(piece_wavs):
        if k:
            lines.append(f"file '{sil.name}'")
        lines.append(f"file '{pw.name}'")
    listf.write_text("\n".join(lines) + "\n", encoding="utf-8")
    target = CHUNKS / f"{name}.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(listf), "-c:a", "pcm_s16le", str(target)],
        check=True, cwd=str(PIECES))
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of", "csv=p=0", str(target)],
        capture_output=True, text=True).stdout.strip()
    (PIECES / f"{name}.done").touch()
    log({"chunk": name, "joined_seconds": float(dur),
         "pieces": len(piece_wavs), "status": "CHUNK DONE"})


def main():
    only = sys.argv[1:] or None
    for sf in sorted(SCRIPT.glob("*.txt")):
        name = sf.stem
        if only and name not in only:
            continue
        if (PIECES / f"{name}.done").exists():
            print(f"SKIP {name} (done)", flush=True)
            continue
        print(f"=== {name}", flush=True)
        render_chunk(name, sf.read_text(encoding="utf-8"))
    print("PIECES BATCH DONE", flush=True)


if __name__ == "__main__":
    main()
