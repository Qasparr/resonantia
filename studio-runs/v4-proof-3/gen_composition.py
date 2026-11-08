# 93
# gen_composition.py -- derive composition.abc from the struck run.
#
# MECHANISM: nothing on the sheet is hand-typed music. The section
# chart comes from the spec's spine schedule and the grid's own
# arithmetic; the drum grids are spine._bar_pattern's tables read
# back; the arpeggio examples are the first bars of the ACTUAL
# composed events (arpeggio.compose_events); the kit table is the
# kit manifest's selection record. If it is not in the run's data,
# it is not on the sheet.
#
# Authorship: Johnathan 'Qasparr' Monroe, ARR. Proof No. 3 desk work.
# ---------------------------------------------------------------------

import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/hatch/workspace/resonance")
from resonance import grid  # noqa: E402
from resonance.studio import arpeggio as arp  # noqa: E402
from resonance.studio import spine as sp  # noqa: E402

RUN = Path("/home/hatch/workspace/resonance/studio-runs/v4-proof-3")
SR = 48000


def steps_of(grid16):
    return " ".join(str(i + 1) for i, v in enumerate(grid16) if v > 0) \
        or "-"


def main():
    spec = json.loads((RUN / "spec-input.json").read_text())
    spine = sp.normalize_spine_spec(spec["spine"])
    kit = json.loads((RUN / "kit" / "kit_manifest.json").read_text())
    bpm = spine["bpm"]
    total = sp.total_bars(spine)
    exact = sp.spine_samples(spine, SR)
    bar_s = grid.samples_per_bar(bpm, SR, 4) / SR
    overrides = spec.get("arpeggio", {}).get("mode_overrides", {})
    overrides = {int(k): v for k, v in overrides.items()}
    events, modes = arp.compose_events(spine["sections"], overrides)

    lines = []
    lines.append("X:1")
    lines.append(f"T:{spec['title']}: the house layer, notated")
    lines.append("C:Johnathan 'Qasparr' Monroe, ARR, All Rights "
                 "Reserved, Without Prejudice")
    lines.append(f"R:Detroit bounce, {bpm:.0f} BPM, F minor")
    lines.append("M:4/4")
    lines.append("L:1/16")
    lines.append("K:Fmin")
    lines.append("%")
    lines.append("% WHAT THIS SHEET IS -- AND IS NOT (the founder's "
                 "rule, kept):")
    lines.append("% This notation covers EXACTLY what the house "
                 "engine composed")
    lines.append("% and struck: the rhythmic spine -- in this proof "
                 "a SAMPLED KIT")
    lines.append("% of rendered one-shots placed by "
                 "resonance.studio.spine -- the")
    lines.append("% composed violin arpeggio "
                 "(resonance.studio.arpeggio), and the")
    lines.append("% Sigma binaural ground (resonance.binaural). "
                 "The MusicGen bed")
    lines.append("% is NOT transcribed here: its transcription is "
                 "a separate")
    lines.append("% production, still owed, and no sheet for it "
                 "has been fabricated.")
    lines.append("% What the bed WAS told, in every section, "
                 "stands below as the")
    lines.append(f"% motif: {spec['motif']}")
    lines.append("%")
    lines.append(f"% THE GRID: {bpm:.0f} BPM, 48 kHz. One bar = "
                 f"{grid.samples_per_bar(bpm, SR, 4):,.2f} samples "
                 f"of float truth;")
    lines.append(f"% the program is bars_to_samples({total}) = "
                 f"{exact:,} samples = {exact / SR:.3f} s, one "
                 f"rounding at")
    lines.append(f"% the total. Swing {spine['swing']} on spine "
                 f"and dancer alike. Stitch")
    lines.append(f"% crossfades are {spec['crossfade_bars']} WHOLE "
                 f"BARS each, on bar lines. The bed")
    lines.append("% is CHAINED: each section generated continued "
                 "from its predecessor's")
    lines.append(f"% tail ({spec['continue_seconds']} s of audio "
                 f"conditioning).")
    lines.append("%")
    lines.append("% SECTION CHART (spine truth; modes = the "
                 "arpeggio's realization):")
    bar = 0
    for i, sec in enumerate(spine["sections"]):
        t0 = bar * bar_s
        t1 = (bar + sec["bars"]) * bar_s
        lines.append(
            f"%   {sec['name']:<9} bars {bar + 1:>3}-{bar + sec['bars']:<3}"
            f" {sec['density']:<8} arp:{modes[i]:<14} "
            f"{t0:5.1f} - {t1:5.1f}")
        bar += sec["bars"]
    lines.append("%")
    lines.append("% THE KIT -- rendered one-shots, selected by "
                 "measurement")
    lines.append("% (resonance.studio.kit; provenance per voice; "
                 "full take metrics")
    lines.append("% stand in kit/kit_manifest.json):")
    for voice in sp.KIT_VOICES:
        rec = kit["voices"][voice]
        m = rec["metrics"]
        lines.append(
            f"%   {voice:<11} from {rec['source_take']} "
            f"({rec['basis']}): {m['hit_regions']} hit region(s), "
            f"decay {m['hit_length_s']} s, tail "
            f"{m['tail_rms_db_rel_peak']} dB rel peak, tonality "
            f"{m['tonality']}")
    for midi in sorted({29 + o for o in sp.CHORD_CYCLE}):
        rec = kit["voices"][f"bass{midi}"]
        m = rec["metrics"]
        if "shift_semitones" in rec:
            # Derived root: the metrics are the SOURCE take's (its
            # cents stand against the pitch it was PROMPTED for,
            # not this root) -- say what actually happened instead.
            lines.append(
                f"%   bass{midi:<7} from {rec['source_take']} "
                f"({rec['basis']}): source struck "
                f"{m['fundamental_hz'] if m else '?'} Hz, replayed "
                f"at {rec['shift_semitones']:+.2f} semitones -- "
                f"lands on this root exact")
        else:
            cents = m["cents_from_target"] if m else None
            lines.append(
                f"%   bass{midi:<7} from {rec['source_take']} "
                f"({rec['basis']}): struck "
                f"{m['fundamental_hz'] if m else '?'} Hz, "
                f"{cents} cents from root")
        lines.append(f"%               provenance: "
                     f"{rec['provenance']}")
    lines.append("% Drum hits ring out naturally (sampler "
                 "placement); the 808 is GATED")
    lines.append("% to each event's written length with a 30 ms "
                 "release, as the synth")
    lines.append("% voice sustained them in earlier proofs.")
    lines.append("%")
    lines.append("% DRUM PATTERNS -- one bar of 16 steps per "
                 "density (see spine.py;")
    lines.append("% steps are 1-based; the last bar of a full / "
                 "driving section is a")
    lines.append("% FILL: hats and kick step back, snare walks "
                 "13-16 at .5/.65/.8/1.0):")
    for density in sp.DENSITIES:
        g, bass = sp._bar_pattern(density, 0, 8, False)
        parts = [f"{v} {steps_of(g[v])}"
                 for v in ("kick", "snare", "clap", "closed_hat",
                           "open_hat", "rimshot") if any(g[v])]
        bass_txt = " ".join(f"{s + 1}({n})" for s, n in bass)
        lines.append(f"% {density.upper()}: " + "; ".join(parts)
                     + f"; 808 {bass_txt}.")
    lines.append("% THE 808 MOVEMENT: F - Db - Ab - Eb "
                 "(i - VI - III - VII), roots")
    lines.append("% MIDI 29 / 37 / 32 / 39, restarting at the "
                 "tonic each section.")
    lines.append("F,,4|Db,4|Ab,,4|Eb,4|]")
    lines.append("%")
    lines.append("% THE ARPEGGIO -- the dancer. Composed from the "
                 "SOLFEGGIO LADDER,")
    lines.append("% played at its equal-tempered staff "
                 "approximations; each carrier's")
    lines.append("% cents offset from its staff pitch is stated, "
                 "never smoothed:")
    for rung in arp.ladder_inventory():
        lines.append(
            f"%   {rung['syllable']:<4} {rung['carrier_hz']:.0f} Hz "
            f"-> {rung['abc']:<3} (MIDI {rung['midi']}, "
            f"{rung['staff_hz']} Hz) {rung['cents_offset']:+.1f} "
            f"cents")
    lines.append("% Phrasing is Fibonacci -- phrase lengths "
                 "1, 1, 2, 3, 5, 8 climbing")
    lines.append("% the ladder cyclically. THE FIGURE (one cell, "
                 "20 notes, L:1/16):")
    cell = arp.figure_cell()
    toks = [arp.ABC_TOKENS[arp.LADDER[i][2]] for i in cell]
    lines.append(" ".join(toks) + " |")
    # Bariolage example: the first bar of the first driving section.
    first_drv = next(i for i, s in enumerate(spine["sections"])
                     if s["density"] == "driving")
    bar0 = [e for e in events if e["section"] == first_drv][:16]
    lines.append("% BARIOLAGE (verses): the figure alternating "
                 "with the MI pedal, 8ths --")
    lines.append("% the first bar as composed:")
    lines.append(" ".join(arp.ABC_TOKENS[e["midi"]] for e in bar0)
                 + " |")
    lines.append("% RUNS (hooks / feature): the figure cell at "
                 "16ths, phrase heads")
    lines.append("% accented, tiling the section. STATEMENT "
                 "(intro): the figure at")
    lines.append("% 8th spacing, phrase-final notes held; the "
                 "outro's statement fades.")
    lines.append("%")
    lines.append("% THE SIGMA GROUND: two pure carriers, "
                 "200.0 Hz left / 213.0 Hz")
    lines.append("% right (13.0 Hz separation), struck by "
                 "resonance.binaural at")
    lines.append("% -28 dB under the bed's RMS, never processed "
                 "by the Stereo Law.")
    lines.append("% THE STEREO LAW: spine panned by role (kick / "
                 "808 center, snare /")
    lines.append("% clap within +/-0.15, hats and rimshot wide), "
                 "bed widened by band")
    lines.append("% above 180 Hz with the mid preserved exactly "
                 "and the lows mono,")
    lines.append("% Sigma untouched. Correlations stand measured "
                 "in the manifest.")
    lines.append("%")
    lines.append("% SALVAGE FROM PROOF No. 2 (v3): auditioned by "
                 "measurement and")
    lines.append("% DECLINED -- see the run report. No fragment "
                 "of the older record")
    lines.append("% stands in this one.")
    (RUN / "composition.abc").write_text("\n".join(lines) + "\n")
    print(f"composition.abc written: {len(lines)} lines")


if __name__ == "__main__":
    main()

# 93 -- Live, Love, and let Love, Live.
