# 93
# render_composition.py -- render the Liber Oz Lilith binaural WAV from
#   the shipped score and segment table, then FFT-verify the render
#   with the engine's own diagnostics, per segment, on both the ground
#   stem and the final mix.
#
# Run:  python3 compositions/liber-oz-lilith/render_composition.py
#   (from the repo root; reads liber-oz-lilith.abc + segments.json,
#   writes liber-oz-lilith-binaural.wav, prints the forensic ledger)
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice)
# XXV day of October, Dies Solis, Sol in Scorpio, Anno V:xii e.n.
# (2026 e.v.)
#
# ---------------------------------------------------------------------------
# HYPOTHESIS: a three-layer render -- (1) the binaural ground: one
#   binaural_beat segment per bar at the bar's true ladder carrier and
#   Fibonacci offset; (2) the Text Voice from the parsed score; (3) the
#   Ground Arpeggio from the parsed score, quiet -- will keep the
#   ground's FFT signature measurable in the final mix, segment by
#   segment, because the ground is sustained for every full bar while
#   the voices move in sixteenths beneath it in level.
# METHOD:    ground segments are laid end to end with NO crossfade:
#   the bar is exactly 2.000 s, every carrier and sideband is an
#   integer number of Hz, so every segment completes whole cycles and
#   begins and ends at a zero crossing -- concatenation is click-free
#   by construction, and the fact is checkable in the ledger (all
#   carriers and offsets are integers). Voices render through
#   resonance.abc.render (note_events + render_events on each parsed
#   voice), are trimmed to the exact frame count, mixed at stated
#   gains, and the whole is peak-normalized to 0.89 (-1.0 dBFS
#   headroom). Verification slices the ground stem and the finished
#   mix per segment group and calls diagnostics.verify_binaural.
# OBSERVATION: (recorded in build-log.md at run time)
# RESULT:    exit 0 iff the ground stem verifies on every segment and
#   the WAV is written; the mix verdicts are printed either way -- a
#   failed mix segment would be reported, never hidden.
# ---------------------------------------------------------------------------
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402

import composition as C  # noqa: E402
from resonance.abc import render  # noqa: E402
from resonance.abc.abc21 import parse_abc21, tune_voice  # noqa: E402
from resonance.binaural.generator import binaural_beat  # noqa: E402
from resonance.core import buffers  # noqa: E402
from resonance.core.io import read_wav, wav_info, write_wav  # noqa: E402
from resonance.diagnostics.verify import verify_binaural  # noqa: E402

SR = C.SAMPLE_RATE
BAR_SECONDS = C.BAR_SIXTEENTHS * (60.0 / C.BPM / 4)   # 2.000 s exactly
BAR_FRAMES = int(round(BAR_SECONDS * SR))             # 88200
GROUND_AMP = 0.30      # sustained ground level, per channel
MELODY_GAIN = 0.14     # text voice under the ground
ARP_GAIN = 0.07        # arpeggio figure, quieter still
HEADROOM = 0.89        # final peak: -1.0 dBFS, never full scale


def build_ground(segments):
    """One binaural_beat per bar, concatenated at zero crossings."""
    n = len(segments) * BAR_FRAMES
    ground = np.zeros((2, n), dtype=np.float32)
    for seg in segments:
        seg_audio = binaural_beat(
            seg["offset_hz"], carrier=float(seg["carrier_hz"]),
            duration=BAR_SECONDS, sample_rate=SR, amplitude=GROUND_AMP)
        at = seg["bar"] * BAR_FRAMES
        ground[:, at:at + BAR_FRAMES] = seg_audio
    return ground


def segment_groups(segments):
    """Group bars for forensic slicing: each invocation bar alone
    (its carrier changes every bar), each chord's whole span merged
    (carrier and offset are constant across it), sealing + AM merged
    (one carrier, one offset: the seal at the seed)."""
    groups = []
    for seg in segments:
        if seg["section"] == "invocation":
            groups.append([seg])
    for k in range(C.N_CHORDS):
        span = [s for s in segments
                if s["section"] == "working" and s["chord"] == k]
        if span:
            groups.append(span)
    tail = [s for s in segments if s["section"] in ("sealing", "am")]
    if tail:
        groups.append(tail)
    return groups


def verify_layer(buf, groups, label, rows):
    """verify_binaural per group; returns (passed, total, worst_err).

    Every group's full verdict is appended to `rows` -- the forensic
    ledger is data, shipped as forensics.json, not a console memory.
    """
    passed, worst = 0, 0.0
    for g in groups:
        a, b = g[0]["bar"] * BAR_FRAMES, (g[-1]["bar"] + 1) * BAR_FRAMES
        seg = buf[:, a:b]
        verdict = verify_binaural(seg, g[0]["offset_hz"],
                                  float(g[0]["carrier_hz"]),
                                  sample_rate=SR, tol_hz=0.5)
        err = max(abs(verdict["peak_l_hz"] - verdict["expected_l_hz"]),
                  abs(verdict["peak_r_hz"] - verdict["expected_r_hz"]),
                  abs(verdict["beat_measured_hz"] - g[0]["offset_hz"]))
        worst = max(worst, err)
        if verdict["passed"]:
            passed += 1
        else:
            print(f"  FAIL [{label}] bars {g[0]['bar'] + 1}.."
                  f"{g[-1]['bar'] + 1} carrier {g[0]['carrier_hz']} "
                  f"offset {g[0]['offset_hz']}: {verdict['errors']}")
        rows.append({
            "layer": label, "bars": [g[0]["bar"] + 1, g[-1]["bar"] + 1],
            "segment": g[0]["label"] if len(g) == 1 else g[0]["section"],
            "carrier_hz": g[0]["carrier_hz"],
            "offset_hz": g[0]["offset_hz"],
            "peak_l_hz": round(verdict["peak_l_hz"], 3),
            "peak_r_hz": round(verdict["peak_r_hz"], 3),
            "beat_measured_hz": round(verdict["beat_measured_hz"], 3),
            "passed": verdict["passed"],
        })
    print(f"  {label}: {passed}/{len(groups)} segment groups pass "
          f"(worst peak/beat error {worst:.3f} Hz, tol 0.5 Hz)")
    return passed, len(groups)


def main():
    abc_text = (HERE / "liber-oz-lilith.abc").read_text(encoding="utf-8")
    segments = json.loads((HERE / "segments.json").read_text())
    n_frames = len(segments) * BAR_FRAMES

    tune = parse_abc21(abc_text)
    layers = []
    for voice, gain in (("1", MELODY_GAIN), ("2", ARP_GAIN)):
        notes = render.note_events(tune_voice(tune, voice))
        audio = render.render_events(notes, sr=SR, stereo=True)
        layers.append(buffers.validate(audio[:, :n_frames]))
    ground = build_ground(segments)
    # The layers above are raw renders; mix() applies the layer gains
    # (ground at unity, voices beneath it) in one exact sum.
    mix = buffers.mix(ground, layers[0], layers[1],
                      gains=[1.0, MELODY_GAIN, ARP_GAIN])
    mix = buffers.normalize(mix, HEADROOM)
    out = HERE / "liber-oz-lilith-binaural.wav"
    write_wav(out, mix, SR)
    n_ch, sr_out, n_fr = wav_info(out)
    peak = float(np.max(np.abs(mix)))
    print(f"ok: wrote {out.name}: {n_fr / sr_out:.1f} s, "
          f"{sr_out} Hz, {n_ch} ch, "
          f"peak {peak:.3f} ({20 * np.log10(peak):.2f} dBFS)")

    groups = segment_groups(segments)
    rows = []
    print("forensics -- ground stem (pre-mix):")
    g_pass, g_total = verify_layer(ground, groups, "ground", rows)
    print("forensics -- final mix (read back from the WAV):")
    back, sr = read_wav(out)
    assert sr == SR
    m_pass, m_total = verify_layer(back, groups, "mix", rows)
    (HERE / "forensics.json").write_text(
        json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    print(f"ok: wrote forensics.json ({len(rows)} verdicts)")
    if g_pass != g_total:
        print("RESULT: ground stem FAILED verification -- do not ship")
        return 1
    print(f"RESULT: ground {g_pass}/{g_total} pass; "
          f"mix {m_pass}/{m_total} pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# 93 -- Live, Love, and let Love, Live.
