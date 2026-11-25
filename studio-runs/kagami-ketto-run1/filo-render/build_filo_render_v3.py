# 93
# ---------------------------------------------------------------------
# build_filo_render_v3.py -- the FILO render set for KAGAMI
# KETTOU, v3: the track re-rendered as its OWN track on the
# Mugetsu-proven road, its vocals trained on its own phrases,
# gated before mixing, and struck in front of the v2 bed.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR, All Rights Reserved, Without Prejudice.
# Written XXV day of November, Anno V:xii e.n. (2026 e.v.), under
# the Method of Science, Aim of Religion -- Scientific Illuminism.
#
# THE COMMISSION (the founder's direct order, 2026-11-25 08:00
# EST): "return to the mugetsu version then rerender the 2nd
# Japanese track as its own track no reminence of Mugetsu in it."
#
# WHAT THIS BUILD CONSUMES (all of it struck and gated by
# v3-render/build_v3_vocals.py, whose records stand beside it):
#   * THE NEW STEM -- v3-render/vocal-stem-v3.wav: the filed
#     score's 47 lines re-rendered through the DiffSinger plug
#     (Lem the Shapeshifter DS 2.5; Civet for Kurogane and his
#     Mirror, Phascogale for Shion), calibrated by factors
#     trained on KAGAMI PASS 1 ALONE (the uncalibrated genesis
#     struck for this purpose): {'VV': 1.1412, 'A': 1.1443,
#     'E': 1.1411, 'I': 1.1426, 'O': 1.1415}, trained_by the
#     pass-1 proof pow-26ef27c5... in the run's LOCAL ledger
#     (v3-render/ledger-v3.jsonl). NO factor trained on a
#     Mugetsu phrase stands anywhere in this render -- the v1
#     stem's borrowed factors {1.1054...1.1203, trained by the
#     two Mugetsu hook proofs} were the remnant, and they are
#     gone.
#   * THE GATE IT PASSED BEFORE MIXING (the step whose absence
#     caused the v2 repair): durations 99.84% of the score in
#     total (sections 98.88--102.99); realized-.ds note-onset
#     drift mean 15.0--17.7 ms per section, max 88 ms (v1:
#     mean 37.6--61.4, max 204); pitch by YIN autocorrelation
#     median |cents| 0.72--0.91 per section (four notes past
#     200 cents, named in the gate record, of 620 measured);
#     language Japanese p = 0.8823. The gate's first strike
#     read pitch through the exam's dominant-frequency judge
#     and FAILED the stem at octave medians; that instrument
#     stands REFUTED on this material (it reads a harmonic,
#     not the fundamental -- a YIN read of the same windows
#     returns the written pitches), and both records stand:
#     v3-render/gate-record-v3.json (marked) and
#     v3-render/gate-pitch-record-v3.json (the corrected gate,
#     FINAL VERDICT: PASS).
#   * THE BED -- filo-render/02-instrumental-kagami-kettou-
#     v2.wav, the v2 modeled bed (physical-model piano and
#     violin over the approved eightoeight/Sigma ground),
#     reused as the commission directs. It enters this mix as
#     its mastered WAV: the v2 build retained no bed premaster
#     as a file, and that seam is disclosed here rather than
#     papered over -- the full render is therefore mastered
#     once more as a whole, as the FILO discipline requires.
#
# MECHANISM:
#   * The voice: the new stem resampled 44.1 -> 48 kHz by the
#     exact rational 160/147, seated dual-mono. ONE gain,
#     computed as v2's was: the gain that seats the VERSES'
#     pooled windowed RMS at 1.05 against this bed's (the
#     duel's body at, not under, its bed); Shion and the close
#     take the same gain and keep the stem's own dynamics.
#   * FILO order: 01 the full render first, as a whole; 02
#     the instrumental (the v2 bed re-struck under v3
#     numbering -- byte-identical audio, stated, not
#     disguised); 03 the vocals alone (the new stem mastered
#     by the v1 03 road, its disclosed gain-staging passes
#     and all).
#   * Mastering is the house road entire: pipeline.
#     master_signal to -14.0 LUFS, strike ceiling -1.35 dBTP,
#     WAV 24-bit, MP3 by ffmpeg/libmp3lame at 320k, and the
#     law weighed on the DECODED MP3 by vocal_exam.
#     judge_masterlaw.
#   * The balance is printed twice, as before: premaster
#     (windowed, per singing section) and delivered (the
#     struck 01 minus the struck 02, sample for sample,
#     against 02) -- the same subtraction that convicted v1.
#
# DOCTRINE: v1 and v2 stay filed, marked superseded, never
# vanished. This set claims the house render only; the
# mastering-of-record question (DECISIONS.md) is untouched.
#
# 93 -- Live, Love, and let Love, Live.
# ---------------------------------------------------------------------

import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
V3 = PKG / "v3-render"
sys.path.insert(0, str(PKG.parents[1]))   # the repo root
sys.path.insert(0, str(HERE))             # the v2 build, called

import build_filo_render_v2 as fv2        # noqa: E402  balance machinery
from resonance.studio import pipeline, vocal_exam  # noqa: E402

SR = 48000
TARGET_LUFS = -14.0
CEILING_DBTP = -1.35
SWORN_BPS = 320000
TARGET_VERSE_RATIO = fv2.TARGET_VERSE_RATIO   # 1.05, v2's law


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encode_mp3(wav_path, mp3_path):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
         "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3_path)],
        check=True)


def master_and_judge(samples, out_base):
    """The house mastering road, as the v1 and v2 builds struck
    it: master_signal to the law, 24-bit WAV, 320k MP3, and the
    verdict weighed on the DECODED MP3."""
    mastered, mrep = pipeline.master_signal(
        np.asarray(samples, dtype=np.float64), SR,
        TARGET_LUFS, CEILING_DBTP)
    wav_path = HERE / f"{out_base}.wav"
    mp3_path = HERE / f"{out_base}.mp3"
    sf.write(str(wav_path), mastered.T, SR, subtype="PCM_24")
    encode_mp3(wav_path, mp3_path)
    verdict = vocal_exam.judge_masterlaw(mp3_path,
                                         sworn_bps=SWORN_BPS)
    return {"wav": wav_path.name, "mp3": mp3_path.name,
            "mp3_bytes": mp3_path.stat().st_size,
            "mastering": mrep, "verdict": verdict}


def strike_vocals_v3(source_wav, out_base):
    """FILO 03: the new stem alone, by the v1 03 road entire --
    resample 160/147, dual-mono, and the chain run in disclosed
    passes until the weighed loudness stands inside tolerance
    or three passes are spent."""
    mono, sr_in = sf.read(str(source_wav))
    if sr_in != 44100 or mono.ndim != 1:
        raise ValueError(f"vocal stem: expected 44.1 kHz mono, "
                         f"got sr={sr_in}, ndim={mono.ndim}")
    up = resample_poly(mono.astype(np.float64), 160, 147)
    mastered = np.vstack([up, up])
    mrep = {"passes": []}
    for _ in range(3):
        mastered, one = pipeline.master_signal(
            mastered, SR, TARGET_LUFS, CEILING_DBTP)
        mrep["passes"].append(one)
        if abs(one["lufs_after"] - TARGET_LUFS) <= 0.5:
            break
    mrep["lufs_after_final"] = mrep["passes"][-1]["lufs_after"]
    wav_path = HERE / f"{out_base}.wav"
    mp3_path = HERE / f"{out_base}.mp3"
    sf.write(str(wav_path), mastered.T, SR, subtype="PCM_24")
    encode_mp3(wav_path, mp3_path)
    verdict = vocal_exam.judge_masterlaw(mp3_path,
                                         sworn_bps=SWORN_BPS)
    return {"source": str(source_wav),
            "source_bytes": source_wav.stat().st_size,
            "wav": wav_path.name, "mp3": mp3_path.name,
            "mp3_bytes": mp3_path.stat().st_size,
            "mastering": mrep, "verdict": verdict}


def main():
    record = {}
    # The bed, reused as the commission directs: v2's struck
    # instrumental WAV.
    bed, sr_bed = sf.read(
        str(HERE / "02-instrumental-kagami-kettou-v2.wav"),
        always_2d=True)
    assert sr_bed == SR
    bed = bed.T.astype(np.float64)                     # (2, N)
    n = bed.shape[1]

    # The new voice, at the studio rate.
    mono, sr_in = sf.read(str(V3 / "vocal-stem-v3.wav"))
    assert sr_in == 44100 and mono.ndim == 1
    voice = resample_poly(mono.astype(np.float64), 160, 147)
    voice = voice[:n] if len(voice) >= n else np.pad(
        voice, (0, n - len(voice)))

    # The balance: raw read, the verses' gain, the after read.
    raw = fv2.windowed_balance(voice, bed)
    record["balance_voice_raw_vs_v2_bed"] = raw
    va, vb = (raw["per_section"]["verse_a"],
              raw["per_section"]["verse_b"])
    wsum = va["windows"] + vb["windows"]
    verse_voice = math.sqrt(
        (va["voice_rms"] ** 2 * va["windows"]
         + vb["voice_rms"] ** 2 * vb["windows"]) / wsum)
    verse_bed = math.sqrt(
        (va["bed_rms"] ** 2 * va["windows"]
         + vb["bed_rms"] ** 2 * vb["windows"]) / wsum)
    verse_ratio_raw = verse_voice / verse_bed
    gain = TARGET_VERSE_RATIO / verse_ratio_raw
    record["voice_gain"] = {
        "linear": gain, "db": 20.0 * math.log10(gain),
        "basis": "verse_a + verse_b pooled",
        "verse_ratio_raw": verse_ratio_raw,
        "target_verse_ratio": TARGET_VERSE_RATIO}
    record["balance_after_v3_premaster"] = fv2.windowed_balance(
        voice * gain, bed)

    # FILO 01 -- the full render first, as a whole.
    voice_st = np.vstack([voice * gain, voice * gain])
    record["01_full_render_v3"] = master_and_judge(
        bed + voice_st, "01-full-render-kagami-kettou-v3")

    # FILO 02 -- the v2 bed re-struck under v3 numbering:
    # byte-identical copies, stated as such, judged again on
    # their own decode.
    for ext in ("wav", "mp3"):
        shutil.copyfile(
            HERE / f"02-instrumental-kagami-kettou-v2.{ext}",
            HERE / f"02-instrumental-kagami-kettou-v3.{ext}")
    record["02_instrumental_v3"] = {
        "wav": "02-instrumental-kagami-kettou-v3.wav",
        "mp3": "02-instrumental-kagami-kettou-v3.mp3",
        "byte_identical_to_v2": {
            "wav_sha256": _sha256(
                HERE / "02-instrumental-kagami-kettou-v3.wav"),
            "mp3_sha256": _sha256(
                HERE / "02-instrumental-kagami-kettou-v3.mp3")},
        "verdict": vocal_exam.judge_masterlaw(
            HERE / "02-instrumental-kagami-kettou-v3.mp3",
            sworn_bps=SWORN_BPS)}

    # FILO 03 -- the new vocals alone.
    record["03_vocals_v3"] = strike_vocals_v3(
        V3 / "vocal-stem-v3.wav", "03-vocals-kagami-kettou-v3")

    # The delivered balance, by the subtraction that convicted
    # v1: what the struck 01 holds that the struck 02 does not.
    full, _ = sf.read(
        str(HERE / "01-full-render-kagami-kettou-v3.wav"),
        always_2d=True)
    inst, _ = sf.read(
        str(HERE / "02-instrumental-kagami-kettou-v3.wav"),
        always_2d=True)
    diff = (full - inst).T
    voice_layer = 0.5 * (diff[0] + diff[1])
    record["balance_delivered_diff"] = fv2.windowed_balance(
        voice_layer, inst.T.astype(np.float64))

    (HERE / "build-record-v3.json").write_text(
        json.dumps(record, indent=2, default=str),
        encoding="utf-8")
    print(json.dumps(record, indent=2, default=str))


if __name__ == "__main__":
    main()

# 93 -- Live, Love, and let Love, Live.
