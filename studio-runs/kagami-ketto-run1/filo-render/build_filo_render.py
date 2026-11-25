# 93
# ---------------------------------------------------------------------
# build_filo_render.py -- the FILO render set for KAGAMI KETTOU:
# the house render of the Japanese mirrored-duel rap, fully
# mastered, with the instrumental and the vocals kept separated
# by FILO sequence -- first in, last out: the full render takes
# the first pass AS A WHOLE, and the separated stems follow it.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR, All Rights Reserved, Without Prejudice.
# Written XXV day of November, Anno V:xii e.n. (2026 e.v.), under
# the Method of Science, Aim of Religion -- Scientific Illuminism.
#
# THE COMMISSION (the founder's direct order, 2026-11-25 06:28 EST):
# "the house render of the Japanese rap track fully mastered but
# keep the instrumental and vocals separated by FILO sequence so
# the full render still gets the first pass as a whole."
#
# MECHANISM -- the sequence, in FILO order:
#   01  THE FULL RENDER. Source: the package's master.wav, the
#       whole mix mastered as a whole by the original build
#       (pipeline.master_signal at -14 LUFS / -1.35 dBTP ceiling).
#       The float premaster was never saved to disk, so this WAV
#       is the whole-mix source of record; the FILO pass strikes
#       it to 320k MP3 by the build's own encode road and re-weighs
#       the decoded MP3 against the law. No second mastering pass
#       is laid over a finished master -- that would be a new
#       master, not this one, and the receipt says so.
#   02  THE INSTRUMENTAL ALONE. Source: instrumental-master.wav,
#       the bed (violin, grand piano, Super 808, Sigma Mega bed)
#       mastered separately by the original build at the same law;
#       struck and re-weighed by the same road as 01.
#   03  THE VOCALS ALONE. Source: vocal-stem.wav, the assembled
#       DiffSinger stem (47 lines: Kurogane, his Mirror, Shion) --
#       the one source that arrives UNMASTERED (44.1 kHz mono,
#       peak -4.08 dBFS, RMS -29.08 dBFS as filed). It is resampled
#       to the studio rate (48 kHz, polyphase 160/147), seated
#       dual-mono so the house mastering chain -- which speaks
#       stereo -- takes it without favour, and mastered for real:
#       pipeline.master_signal to -14.0 LUFS with the ceiling at
#       -1.35 dBTP, the margin the bench's precedent keeps so an
#       MP3 decode cannot carry the true peak over the -1.0 line.
#
# THE LAW (house master law, weighed on the DECODED MP3 by
# vocal_exam.judge_masterlaw -- never on the WAV): integrated
# loudness -14.0 +/- 0.5 LUFS; decoded true peak <= -1.0 dBTP;
# bitrate exactly 320,000 bps.
#
# DOCTRINE: FILO is an order of honour, not a mixing trick. The
# whole is weighed first because the whole is the work; the stems
# follow, separated and each under the same law, so any of the
# three can stand alone without re-opening the others. Nothing
# here touches the mastering OF RECORD: which version of this
# piece takes that seat (the house render, an external strike) is
# the founder's ear and remains open; this set is the house
# render, entire, and claims no more.
#
# 93 -- Live, Love, and let Love, Live.
# ---------------------------------------------------------------------

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG.parents[1]))

from resonance.studio import pipeline, vocal_exam  # noqa: E402

SR = 48000            # the studio rate; the loudness scale's own rate
TARGET_LUFS = -14.0   # house master law: integrated loudness
CEILING_DBTP = -1.35  # strike ceiling; decode margin under the -1.0 law
SWORN_BPS = 320000    # house master law: exactly 320,000 bps


def encode_mp3(wav_path: Path, mp3_path: Path) -> None:
    """Strike a 320k MP3 from a WAV by the build's own encode road.

    MECHANISM: ffmpeg + libmp3lame at a constant 320k, the same
    encoder call the original Kagami Ketto build used for its
    masters, so a FILO strike and a package master differ only in
    their source, never in their road.
    """
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
         "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3_path)],
        check=True)


def strike_from_mastered_wav(source_wav: Path, out_base: str) -> dict:
    """FILO 01/02 road: a source that arrives already mastered.

    MECHANISM: the mastered WAV is copied into the FILO folder
    under its sequence name (so the set is self-contained), struck
    to MP3, and the delivered MP3 is judged on its decode. The
    mastering figures carried into the record are the judge's --
    measured from the delivered file, not inherited from the
    source's reputation.
    """
    wav_path = HERE / f"{out_base}.wav"
    mp3_path = HERE / f"{out_base}.mp3"
    data, sr = sf.read(str(source_wav), always_2d=True)
    sf.write(str(wav_path), data, sr, subtype="PCM_24")
    encode_mp3(wav_path, mp3_path)
    verdict = vocal_exam.judge_masterlaw(mp3_path, sworn_bps=SWORN_BPS)
    return {"source": str(source_wav), "source_bytes": source_wav.stat().st_size,
            "wav": wav_path.name, "mp3": mp3_path.name,
            "mp3_bytes": mp3_path.stat().st_size, "verdict": verdict}


def strike_vocals(source_wav: Path, out_base: str) -> dict:
    """FILO 03 road: the one source that arrives unmastered.

    MECHANISM: read the 44.1 kHz mono stem, resample to the studio
    rate by the exact rational 160/147 (44100 * 160/147 = 48000),
    seat it dual-mono (2, N) for the stereo mastering chain, and
    master it with pipeline.master_signal at the law. The mastered
    WAV (24-bit) and the 320k MP3 are written under the sequence
    name; the MP3 is judged on its decode.
    """
    mono, sr_in = sf.read(str(source_wav))
    if sr_in != 44100 or mono.ndim != 1:
        raise ValueError(f"vocal stem: expected 44.1 kHz mono, "
                         f"got sr={sr_in}, ndim={mono.ndim}")
    up = resample_poly(mono.astype(np.float64), 160, 147)
    stereo = np.vstack([up, up])  # dual-mono: the same voice, both ears
    # GAIN STAGING, DISCLOSED: one pass of the chain lands this stem
    # at -14.6 LUFS -- the ceiling trim (-0.37 dB) overrides the
    # loudness by design, and the law's tolerance is +/- 0.5. So the
    # chain is run as mastering is actually run: in passes, each
    # pass the same house chain at the same law, until the weighed
    # loudness stands inside tolerance or three passes are spent.
    # Every pass's report is kept; the record shows its staging.
    mastered = stereo
    mrep = {"passes": []}
    for _ in range(3):
        mastered, one = pipeline.master_signal(mastered, SR, TARGET_LUFS,
                                               CEILING_DBTP)
        mrep["passes"].append(one)
        if abs(one["lufs_after"] - TARGET_LUFS) <= 0.5:
            break
    mrep["lufs_after_final"] = mrep["passes"][-1]["lufs_after"]
    wav_path = HERE / f"{out_base}.wav"
    mp3_path = HERE / f"{out_base}.mp3"
    sf.write(str(wav_path), mastered.T, SR, subtype="PCM_24")
    encode_mp3(wav_path, mp3_path)
    verdict = vocal_exam.judge_masterlaw(mp3_path, sworn_bps=SWORN_BPS)
    return {"source": str(source_wav), "source_bytes": source_wav.stat().st_size,
            "wav": wav_path.name, "mp3": mp3_path.name,
            "mp3_bytes": mp3_path.stat().st_size,
            "mastering": mrep, "verdict": verdict}


def main() -> None:
    record = {
        "01_full_render": strike_from_mastered_wav(
            PKG / "master.wav", "01-full-render-kagami-kettou"),
        "02_instrumental": strike_from_mastered_wav(
            PKG / "instrumental-master.wav", "02-instrumental-kagami-kettou"),
        "03_vocals": strike_vocals(
            PKG / "vocal-stem.wav", "03-vocals-kagami-kettou"),
    }
    print(json.dumps(record, indent=2, default=str))


if __name__ == "__main__":
    main()
