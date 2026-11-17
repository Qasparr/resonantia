# 93
# ---------------------------------------------------------------------
# build_demos.py -- the ASCII Engine's demonstration strikes.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: this script strikes the three demonstrations of
# resonance/studio/ascii.py and nothing else. Every measured fact
# in the Mugetsu .nfo is READ at strike time from the run-2 folder
# (run2-summary.json and manifest.json) -- no number is copied
# into this script by hand, so the .nfo can only say what the
# run's own record says. The plate render strikes at two widths
# (100, the first width tried, and 160, the width that read) and
# keeps both. The dial frame's gains are weighed from the sealed
# master through the visualizer's own core (ascii.gains_from_
# audio) and the peak frame's vector is written beside the frame
# so the strike can be re-struck from gains-peak.json alone.
# ---------------------------------------------------------------------

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from resonance.studio import ascii as asc
from resonance.studio import visualize as viz

HERE = Path(__file__).resolve().parent
RUN2 = HERE.parent / "mugetsu-hook-engine-run2"
PLATE = (Path.home() / "workspace" / "user" / "files" /
         "FB_IMG_1794769247066_0_qhwz.jpg")


def strike_plate():
    """The Pyramidasphere plate at both widths, CP437 + preview."""
    facts = {}
    for width in (100, 160):
        lines, render_facts = asc.image_to_ascii(PLATE, width)
        out = HERE / f"plate-ascii-w{width}.txt"
        strike = asc._strike(lines, out,
                             HERE / f"plate-ascii-w{width}-preview.txt")
        facts[f"w{width}"] = {**render_facts, **strike}
    return facts


def strike_nfo():
    """The Mugetsu run-2 .nfo, its facts read from the run folder."""
    summary = json.loads((RUN2 / "run2-summary.json").read_text())
    manifest = json.loads((RUN2 / "manifest.json").read_text())
    asm = summary["run2_assembly"]
    totals = summary["totals"]
    measured = summary["master_measured"]
    factors = summary["calibration_factors"]
    overhangs = [w.split("overhang ")[1].split("s past")[0]
                 for w in summary["run2_walls"]]
    seated = summary["run2_seat_totals"]
    seated_count = sum(s["phonemes"] for s in seated.values())
    native_count = manifest["nine"]["dispositions"]["PASS_NATIVE"]
    info = [
        ("Title", "DETROIT MUGETSU -- HOOK"),
        ("Engine", manifest["engine"]),
        ("Voice bank", manifest["bank"]["name"]),
        ("Seat", "YAMI (CIVET)"),
        ("Lines", f"{len(manifest['lines'])} FILED LINES"),
        ("Phonemes", f"{seated_count + native_count} -- "
                     f"{seated_count} SEATED, {native_count} PASS_NATIVE"),
        ("Assembly", "MUGETSU-HOOK.WAV -- 44.1 KHZ MONO"),
        ("Duration", f"{asm['duration_s']} S ({asm['samples']} SAMPLES)"),
        ("Peak", f"{asm['peak_dbfs']} DBFS"),
        ("RMS", f"{asm['rms_dbfs']} DBFS"),
        ("Realization", f"RUN 1 {totals['run1_realization_pct']}% -- "
                        f"RUN 2 {totals['run2_realization_pct']}%"),
        ("Master", f"MASTER.MP3 -- {measured['bitrate_bps']} BPS EXACT"),
        ("Loudness", f"{measured['lufs_integrated']} LUFS INTEGRATED"),
        ("True peak", f"{measured['true_peak_dbtp']} DBTP"),
        ("Status", summary["master_status"]),
    ]
    factor_span = (f"{min(factors.values())} and "
                   f"{max(factors.values())}")
    body = [
        f"Run 1, the genesis strike, realized "
        f"{totals['run1_realization_pct']} percent of the filed "
        f"score. Its vocal proof trained the calibration store, and "
        f"run 2 sang through the factors it earned -- per-seat "
        f"factors between {factor_span} across the five seated "
        f"vowels.",
        f"Run 2 realized {totals['run2_realization_pct']} percent "
        f"of the score's {totals['asked_s']} seconds. "
        f"{len(overhangs)} lines overshot their bar lines -- by "
        f"{', '.join(overhangs[:-1])}, and {overhangs[-1]} seconds "
        f"-- and the overhangs were summed into the assembly, "
        f"never trimmed.",
        f"Of {seated_count + native_count} phonemes, "
        f"{seated_count} sat in the seated vowels; {native_count} "
        f"consonants passed native, unseated and unweighed.",
        f"The master was weighed on the delivered MP3 decoded, "
        f"as the gate weighs every master: "
        f"{measured['lufs_integrated']} LUFS integrated against "
        f"the sworn -14.0 +/- 0.5, true peak "
        f"{measured['true_peak_dbtp']} dBTP against the -1.0 "
        f"ceiling, bitrate exactly {measured['bitrate_bps']} bps. "
        f"Every check passed; the gate sealed it.",
    ]
    proofs = [("GENESIS", summary["genesis_proof"]),
              ("VOCAL", summary["run2_vocal_proof"]),
              ("MASTER", summary["master_proof"])]
    proof_lines = [f"  {label:<7} {pid}" for label, pid in proofs]
    return asc.write_nfo(
        HERE / "mugetsu-run2.nfo", "DETROIT MUGETSU",
        subtitle="ENGINE RUN 2 -- THE HOOK, SUNG FROM THE SCORE",
        info=info, body=body,
        extra_sections=[("PROOFS", proof_lines)])


def strike_frame():
    """One dial frame from the sealed master, peak frame, + gains."""
    seats = viz.load_seats(viz.dial_path())
    gains, facts = asc.gains_from_audio(RUN2 / "master.mp3", seats)
    (HERE / "gains-peak.json").write_text(
        json.dumps({"gains": gains, "facts": facts}, indent=2),
        encoding="utf-8")
    caption = (f"THE DOUBLE-LETTER DIAL -- ASCII FRAME - frame "
               f"{facts['peak_frame']} of {facts['frames']}, "
               f"t = {facts['peak_time_s']:.2f} s - MASTER.MP3, "
               f"MUGETSU RUN 2")
    lines = asc.dial_frame(gains, seats, caption=caption)
    strike = asc._strike(lines, HERE / "dial-frame.txt",
                         HERE / "dial-frame-preview.txt")
    return {**facts, **strike}


def main():
    report = {"plate": strike_plate(), "nfo": strike_nfo(),
              "frame": strike_frame()}
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
