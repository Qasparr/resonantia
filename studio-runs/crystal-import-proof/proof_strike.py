# 93
# ---------------------------------------------------------------------
# proof_strike.py -- the Crystal importer's proof strike: the page's
# OWN factory pattern, imported by resonance.studio.crystal_import,
# looped four bars, and struck through the house sample road.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR, All Rights Reserved, Without Prejudice.
# Written XXV day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# SOURCE CREDIT (the founder's ruling, 2026-11-25: author unknown,
# the link stands as the credit):
#   https://sortiarius.neocities.org/5D_Memory_Crystal_Evolution_05
# The pattern struck here is the page's factory state, extracted
# from its source and carried in the module as DEFAULT_PATTERN.
# The instruments are the house's, credited in
# ~/workspace/lab/samples/CREDITS.md (Salamander Grand Piano by
# Alexander Holm, CC BY 3.0; Sonatina Symphonic Orchestra by
# Mattias Westlund / Peter Eastman, CC Sampling Plus 1.0), played
# by the house renderer tsf_render (TinySoundFont, Bernhard
# Schelling, MIT). The sub is the house 808 (eightoeight.kick).
#
# MECHANISM: convert(DEFAULT_PATTERN) -> events; loop the one-bar
# pattern four times in the open; sample seats struck per bank
# through tsf_render (SSO: glockenspiel 39 for GLASS ORBIT,
# xylophone 42 for SIGNAL DUST; Salamander: the gated PHANTOM
# CHOIR); SUB HORIZON placed as pitched 808 kicks at each event's
# HOUSE frequency (432 field); stems mixed at printed gains; peak
# guard 0.89; two-pass ffmpeg loudnorm toward the house guide
# (-14 LUFS / -1 dBTP); measured and printed, never smoothed.
#
# DOCTRINE: this is a MECHANISM demonstration -- a foreign pattern
# crossed into the house and sounded. It is not a caliber claim;
# the founder's ear gates caliber. Run with the transcription
# lab's venv python (mido / soundfile / scipy live there):
#   ~/workspace/lab/transcription-test/venv/bin/python proof_strike.py
#
# 93 -- Live, Love, and let Love, Live.
# ---------------------------------------------------------------------
import json
import subprocess
import sys
from pathlib import Path

import mido
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

HERE = Path(__file__).resolve().parent
REPO = Path.home() / "workspace/resonance"
sys.path.insert(0, str(REPO))

from resonance.studio import crystal_import as ci  # noqa: E402
from resonance.studio import eightoeight as eo     # noqa: E402

SR = 48000
BARS = 4
TSF = Path.home() / "workspace/lab/16bit-remedy/bin/tsf_render"
SSO = Path.home() / ("workspace/lab/samples/sso-sf2/"
                     "Sonatina_Symphonic_Orchestra.sf2")
SALAMANDER = Path.home() / (
    "workspace/lab/samples/SalamanderGrandPiano-SF2-V3+20200602/"
    "SalamanderGrandPiano-V3+20200602.sf2")
GAINS = {"sso": 1.0, "salamander": 0.9, "sub808": 0.9}
TAIL_S = 1.6


def write_strike_midi(path, looped, channels):
    """channels: {track_index: channel}. One MIDI per bank, holding
    only that bank's tracks, notes looped over BARS bars."""
    mid = mido.MidiFile(ticks_per_beat=480)
    meta = mido.MidiTrack()
    tempo = mido.bpm2tempo(ci.DEFAULT_PATTERN["tempo"])
    meta.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
    mid.tracks.append(meta)
    by_track = {}
    for ev, gstep in looped:
        if ev.track_index in channels:
            by_track.setdefault(ev.track_index, []).append((ev, gstep))
    for ti, items in sorted(by_track.items()):
        ch = channels[ti]
        tr = mido.MidiTrack()
        tr.append(mido.Message("program_change", channel=ch,
                               program=items[0][0].program, time=0))
        evs = []
        for ev, gstep in items:
            evs.append((gstep * 120, 1, ev))
            evs.append(((gstep + 1) * 120, 0, ev))
        evs.sort(key=lambda e: (e[0], e[1]))
        last = 0
        for tick, on, ev in evs:
            tr.append(mido.Message(
                "note_on" if on else "note_off", channel=ch,
                note=ev.midi, velocity=ev.velocity if on else 0,
                time=tick - last))
            last = tick
        mid.tracks.append(tr)
    mid.save(str(path))


def read_wav48(path):
    y, sr = sf.read(str(path), always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr != SR:
        y = resample_poly(y, SR, sr)
    return y.astype(np.float64)


def place(buf, note_buf, start_s, gain):
    i = int(round(start_s * SR))
    j = min(len(buf), i + len(note_buf))
    if j > i:
        buf[i:j] += gain * note_buf[:j - i]


def main():
    pattern = ci.DEFAULT_PATTERN
    events = ci.convert(pattern)
    step_s = ci.step_seconds(pattern["tempo"])
    total_s = BARS * ci.STEPS_PER_BAR * step_s + TAIL_S
    mix = np.zeros(int(total_s * SR), dtype=np.float64)

    looped = [(ev, bar * ci.STEPS_PER_BAR + ev.step)
              for bar in range(BARS) for ev in events]

    # --- the fixture artifacts: the pattern as saved, its ABC, its
    # MIDI -- the conversion's paper trail, beside the audio.
    (HERE / "crystal-default-pattern.json").write_text(
        json.dumps(pattern, indent=2) + "\n")
    (HERE / "crystal-default-pattern.abc").write_text(
        ci.to_abc(events, pattern))
    ci.to_midi(events, pattern, HERE / "crystal-default-pattern.mid")

    # --- SSO bank: GLASS ORBIT (glockenspiel 39), SIGNAL DUST
    # (xylophone 42).
    write_strike_midi(HERE / "work-sso.mid", looped, {1: 0, 3: 1})
    subprocess.run([str(TSF), str(SSO), str(HERE / "work-sso.mid"),
                    str(HERE / "work-sso.wav")], check=True)
    place(mix, read_wav48(HERE / "work-sso.wav"), 0.0, GAINS["sso"])

    # --- Salamander bank: PHANTOM CHOIR, gated onto the grand.
    write_strike_midi(HERE / "work-choir.mid", looped, {2: 0})
    subprocess.run([str(TSF), str(SALAMANDER),
                    str(HERE / "work-choir.mid"),
                    str(HERE / "work-choir.wav")], check=True)
    place(mix, read_wav48(HERE / "work-choir.wav"), 0.0,
          GAINS["salamander"])

    # --- SUB HORIZON: the house 808, pitched at the house field.
    for ev, gstep in looped:
        if ev.track_index != 0:
            continue
        kick = eo.kick(fundamental=ev.freq_house_hz, seconds=1.4)
        place(mix, kick, gstep * step_s,
              GAINS["sub808"] * ev.velocity / 127.0)

    # --- master: peak guard, one loudnorm pass, measure.
    peak = float(np.max(np.abs(mix))) or 1.0
    mix *= 0.89 / peak
    premaster = HERE / "crystal-proof-premaster.wav"
    sf.write(str(premaster), mix.astype(np.float32), SR)

    def loudnorm_json(path):
        r = subprocess.run(
            ["ffmpeg", "-hide_banner", "-i", str(path), "-af",
             "loudnorm=print_format=json", "-f", "null", "-"],
            capture_output=True, text=True)
        txt = r.stderr
        return json.loads("{" + txt[txt.index("[Parsed_loudnorm"):]
                          .split("{", 1)[1].rsplit("}", 1)[0] + "}")

    # Two-pass loudnorm toward the house guide (-14 / -1), the
    # second pass fed the first pass's measurements, linear mode.
    m1 = loudnorm_json(premaster)
    mastered = HERE / "crystal-proof.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-i", str(premaster), "-af",
         "loudnorm=I=-14:TP=-1:LRA=11"
         f":measured_I={m1['input_i']}:measured_TP={m1['input_tp']}"
         f":measured_LRA={m1['input_lra']}"
         f":measured_thresh={m1['input_thresh']}"
         f":offset={m1['target_offset']}:linear=true",
         "-ar", "48000", str(mastered)],
        check=True, capture_output=True)
    mp3 = HERE / "crystal-proof.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-i", str(mastered),
         "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3)],
        check=True, capture_output=True)

    js = loudnorm_json(mastered)
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=bit_rate",
         "-of", "json", str(mp3)], capture_output=True, text=True)
    bitrate = int(json.loads(probe.stdout)["format"]["bit_rate"])

    # Spectral centroid of the mastered strike (numpy LTAS read).
    y = read_wav48(mastered)
    frame = 4096
    mags = []
    for i in range(0, len(y) - frame, frame * 4):
        spec = np.abs(np.fft.rfft(y[i:i + frame]
                                  * np.hanning(frame)))
        mags.append(spec)
    avg = np.mean(mags, axis=0)
    freqs = np.fft.rfftfreq(frame, 1 / SR)
    centroid = float((freqs * avg).sum() / avg.sum())

    figures = {
        "pattern": "the page's factory pattern (DEFAULT_PATTERN), "
                   "tempo 72, scale minor, mood deep",
        "bars_struck": BARS,
        "events_per_bar": len(events),
        "step_seconds": step_s,
        "gains": GAINS,
        "master_wav": {"lufs": float(js["input_i"]),
                       "true_peak_dbtp": float(js["input_tp"])},
        "master_note": "the guide's -14 LUFS is not reached and the "
                       "shortfall is printed: the premaster already "
                       "peaks at the -1 dBTP ceiling (sparse strikes, "
                       "long quiet between them), so loudness "
                       "normalization has no headroom to give; the "
                       "landing is the material's own crest, not a "
                       "smoothed figure",
        "mp3_bitrate_bps": bitrate,
        "spectral_centroid_hz": round(centroid, 1),
        "choir_gate": next(e.gate for e in events
                           if e.track_name == "PHANTOM CHOIR"),
    }
    (HERE / "figures.json").write_text(json.dumps(figures, indent=2)
                                       + "\n")
    print(json.dumps(figures, indent=2))
    print(ci.regrounding_report(pattern))


if __name__ == "__main__":
    main()
