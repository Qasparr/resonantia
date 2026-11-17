# 93
# ---------------------------------------------------------------------
# proofs.py -- Render-as-Proof: every render a unit of Proof of
# Work, every master a Proof of Mastering, chained and weighed.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: a PROOF is a record in a hash-chained ledger (JSONL,
# one record per line). A record carries its kind (score | lyrics
# | vocal | instrumental | orchestra | choir | master), the
# artifact it attests (path + SHA-256 of the artifact's bytes +
# byte count), the MEASURED manifest the render honestly produced,
# the IDs of the parent proofs it consumed (lyrics -> score ->
# vocal -> master is a chain, not a pile), a UTC timestamp, and
# the founder's authorship / Flagpole line. The record's own ID is
# the SHA-256 of the canonical JSON of everything above PLUS the
# previous record's ID, so a later hand that alters any earlier
# record -- or the artifact it names -- breaks the chain on
# inspection: tamper-evident by construction, the Gate Ledger's
# discipline (~/workspace/gate-ledger/PROTOCOL.md) carried into
# the studio. Nothing is struck from the ledger; a failed proof
# stands marked FAILED beside the sealed ones. MARKED, never
# vanished.
#
# DOCTRINE -- PROOF OF WORK: in the founder's tokenomics the
# render IS the work. A sheet, a lyric, a voice, an instrumental,
# an orchestra, a choir -- each struck artifact, with its measured
# manifest and its hash, chained to the proofs it consumed, is a
# unit of work no one has to take anyone's word for: re-hash the
# artifact, re-walk the chain, re-weigh the manifest. The
# attestation concept is his $PP, "proof positive" (Twin Synergy
# trinity: Miner -> $PP -> $00).
#
# HARD BOUNDARY, printed here because it governs every line
# below: THIS MODULE MINTS NO TOKEN, OFFERS NOTHING, VALUES
# NOTHING. Proofs are records. The founder's law governs the
# token side -- testnet-first with play money; real value waits
# on licensed compliance counsel -- and this ledger is only the
# substrate that law will ride on when he walks it.
#
# DOCTRINE -- PROOF OF MASTERING, FAIL-CLOSED (his Persona V
# law: no justification, no action): a master proof SEALS only
# when its measured body satisfies the house law, weighed on the
# DELIVERED artifact (the MP3 a listener actually receives,
# decoded and re-measured -- never the WAV's intentions):
#   * integrated loudness within tolerance of the -14 LUFS
#     target (tolerance stated below, the fourth element);
#   * decoded true peak at or under the -1.0 dBTP ceiling;
#   * bitrate EXACTLY the sworn bitrate, when a bitrate is sworn
#     (320,000 bps is the house's sworn figure);
#   * the Sigma band at -30.12 dBFS within tolerance, when a
#     Sigma layer is sworn.
# An unmeasured quantity cannot seal: absence is a failure, named.
# An out-of-law master still gets its record -- status FAILED,
# the failing measurements printed in the record's gate. Nothing
# hidden, nothing smoothed.
#
# DOCTRINE -- THE CALIBRATION LOOP: the Divine Nine are the
# training axes of the singing plug. Vocal proofs carry per-seat
# asked-vs-realized duration totals; the calibration store
# accumulates them across every vocal proof in the ledger and
# derives, per seat, the factor asked/realized by which the plug
# pre-corrects mora budgets at sequence build. Every factor names
# the proof IDs that trained it. VV sits in the store as an
# ACOUSTIC seat only -- it carries no isopsephy weight, per the
# founder's ruling; consonants are never trained (PASS_NATIVE,
# the vowels-only ruling); no vowel-to-Archon mapping exists here
# or anywhere in this module -- that is the founder's pen,
# UNCHARTED.
#
# Tolerances (the fourth element): LUFS tolerance +/-0.5 LU
# around -14.0; Sigma tolerance +/-0.5 dB around -30.12 dBFS;
# calibration factors clamped to [0.5, 2.0] -- a factor outside
# that span is a broken measurement, not a correction.
# ---------------------------------------------------------------------

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

AUTHORSHIP = (
    "Authorship attributed exclusively to Johnathan 'Qasparr' "
    "Monroe, ARR, All Rights Reserved, Without Prejudice.")
FLAGPOLE = (
    "Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, "
    "ARR, All Rights Reserved, Without Prejudice. Right of claim "
    "hereby reserved and coined under the authority of the "
    "Living Man.")

KINDS = ("score", "lyrics", "vocal", "instrumental", "orchestra",
         "choir", "master")
GENESIS_PREV = "GENESIS"

# The house mastering law, as constants -- the gate reads these,
# and docs/PROOF-OF-WORK.md prints them; the two must never drift.
TARGET_LUFS = -14.0
LUFS_TOLERANCE_LU = 0.5
CEILING_DBTP = -1.0
SWORN_BITRATE_BPS = 320000
SIGMA_BAND_DBFS = -30.12
SIGMA_TOLERANCE_DB = 0.5

# The Nine, as calibration axes (acoustic register only; VV has
# no isopsephy weight -- the founder's ruling, carried verbatim).
SEATS = ("Α", "Ε", "Η", "Ι", "Ο", "VV", "Ω", "ΕΙ", "ΟΥ")
FACTOR_MIN, FACTOR_MAX = 0.5, 2.0

_HERE = Path(__file__).resolve()
REPO_ROOT = _HERE.parents[2]


# ---------------------------------------------------------------------
# Seats: where the ledger and the calibration store live.
# ---------------------------------------------------------------------

def default_ledger_path():
    """The ledger's durable seat: <repo>/proofs/ledger.jsonl.

    RESONANTIA_PROOF_LEDGER overrides it (tests, side ledgers) --
    an override is a different ledger, and its records say so by
    the path the CLI prints; the house ledger is the default.
    """
    env = os.environ.get("RESONANTIA_PROOF_LEDGER")
    if env:
        return Path(env)
    return REPO_ROOT / "proofs" / "ledger.jsonl"


def calibration_path_for(ledger_path):
    """The calibration store sits beside its ledger."""
    env = os.environ.get("RESONANTIA_PROOF_CALIBRATION")
    if env:
        return Path(env)
    return Path(ledger_path).with_name("calibration.json")


# ---------------------------------------------------------------------
# Hashing and the chain.
# ---------------------------------------------------------------------

def sha256_bytes(data):
    """SHA-256 of a byte string, hex."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    """SHA-256 of a file's bytes, read in blocks, hex."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _canonical(obj):
    """The one JSON spelling a record's ID is weighed on.

    Sorted keys, tight separators, UTF-8 kept whole (the Greek
    seats are data, not escapes) -- any other spelling would let
    the same record carry two IDs, and a proof with two names is
    no proof at all.
    """
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


def record_id(content):
    """A record's ID: 'pow-' + SHA-256 of its canonical content.

    The content includes 'prev', so the ID binds the record to
    its place in the chain as well as to its own body.
    """
    return "pow-" + sha256_bytes(_canonical(content).encode("utf-8"))


def read_ledger(ledger_path=None):
    """Read the ledger as a list of records ([] when unborn)."""
    path = Path(ledger_path) if ledger_path else default_ledger_path()
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _artifact_ref(artifact_path, root):
    """An artifact's reference: path (repo-relative when the
    artifact lives under the root) + hash + byte count."""
    p = Path(artifact_path)
    try:
        rel = str(p.resolve().relative_to(Path(root).resolve()))
    except (ValueError, OSError):
        rel = str(p)
    return {"path": rel, "sha256": sha256_file(p),
            "bytes": p.stat().st_size}


def append_proof(kind, artifact_path, manifest, parents=(),
                 ledger_path=None, status="SEALED", gate=None,
                 ts=None, root=None):
    """Append one proof to the ledger; return the record.

    MECHANISM: the record's content is assembled (kind, artifact
    reference, the manifest AS GIVEN -- the caller's measurements,
    never edited here -- parent IDs, timestamp, authorship,
    flagpole, status, and the gate verdict when one rides), its
    'prev' is the current last record's ID (GENESIS_PREV for the
    first), its ID is weighed over the whole content, and the
    record is appended as one JSON line. The ledger is append-
    only: this function has no edit and no delete, by design.
    """
    if kind not in KINDS:
        raise ValueError(f"kind {kind!r} not one of {KINDS}")
    ledger = Path(ledger_path) if ledger_path \
        else default_ledger_path()
    root = Path(root) if root else REPO_ROOT
    records = read_ledger(ledger)
    prev = records[-1]["id"] if records else GENESIS_PREV
    content = {
        "prev": prev,
        "kind": kind,
        "ts": ts or datetime.now(timezone.utc).isoformat(),
        "artifact": _artifact_ref(artifact_path, root),
        "manifest": manifest,
        "parents": [str(p) for p in parents],
        "status": status,
        "authorship": AUTHORSHIP,
        "flagpole": FLAGPOLE,
    }
    if gate is not None:
        content["gate"] = gate
    record = {"id": record_id(content), **content}
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def verify_ledger(ledger_path=None, root=None):
    """Re-walk the chain and re-hash the artifacts; report breaks.

    MECHANISM: for each record, in order -- recompute its ID from
    its content (a mismatch is a TAMPERED RECORD), check its
    'prev' against the previous record's ID (a mismatch is a
    BROKEN LINK), and re-hash the artifact it names when that
    file still exists on disk (a mismatch is a TAMPERED
    ARTIFACT; an absent file is reported as ARTIFACT MISSING --
    the proof stands in the chain but its body can no longer be
    re-weighed, and the report says so at full size rather than
    passing it in silence). Returns {ok, records, breaks[]}.
    """
    ledger = Path(ledger_path) if ledger_path \
        else default_ledger_path()
    root = Path(root) if root else REPO_ROOT
    records = read_ledger(ledger)
    breaks = []
    prev = GENESIS_PREV
    for i, rec in enumerate(records):
        content = {k: v for k, v in rec.items() if k != "id"}
        if record_id(content) != rec.get("id"):
            breaks.append({"index": i, "id": rec.get("id"),
                           "problem": "TAMPERED RECORD: recomputed "
                                      "ID does not match"})
        if rec.get("prev") != prev:
            breaks.append({"index": i, "id": rec.get("id"),
                           "problem": f"BROKEN LINK: prev is "
                                      f"{rec.get('prev')!r}, chain "
                                      f"expects {prev!r}"})
        prev = rec.get("id")
        art = rec.get("artifact", {})
        apath = Path(art.get("path", ""))
        if not apath.is_absolute():
            apath = Path(root) / apath
        if not apath.exists():
            breaks.append({"index": i, "id": rec.get("id"),
                           "problem": f"ARTIFACT MISSING: "
                                      f"{art.get('path')} not on "
                                      "disk -- the proof stands "
                                      "but cannot be re-weighed"})
        elif sha256_file(apath) != art.get("sha256"):
            breaks.append({"index": i, "id": rec.get("id"),
                           "problem": f"TAMPERED ARTIFACT: "
                                      f"{art.get('path')} hashes "
                                      "to a different body than "
                                      "the record attests"})
    return {"ok": not breaks, "records": len(records),
            "ledger": str(ledger), "breaks": breaks}


# ---------------------------------------------------------------------
# Proof of Mastering: the fail-closed gate.
# ---------------------------------------------------------------------

def check_mastering(measured):
    """Weigh a master's measured body against the house law.

    The measured body (of the DELIVERED artifact, decoded):
    {lufs_integrated, true_peak_dbtp, bitrate_bps,
     sworn_bitrate_bps, sigma_band_dbfs, sigma_sworn}. Returns
    {sealed, checks[], failures[]} -- every check printed with
    its value and its law, pass or fail, so a FAILED record's
    gate is the whole story, not a verdict without evidence.
    Fail-closed: a quantity the body does not carry is a failed
    check named NOT MEASURED, never a pass by omission.
    """
    checks = []

    def add(name, value, law, ok):
        checks.append({"check": name, "value": value, "law": law,
                       "ok": bool(ok)})

    lufs = measured.get("lufs_integrated")
    if lufs is None:
        add("integrated loudness", None,
            f"{TARGET_LUFS} +/- {LUFS_TOLERANCE_LU} LUFS", False)
    else:
        add("integrated loudness", lufs,
            f"{TARGET_LUFS} +/- {LUFS_TOLERANCE_LU} LUFS",
            abs(float(lufs) - TARGET_LUFS) <= LUFS_TOLERANCE_LU)
    tp = measured.get("true_peak_dbtp")
    if tp is None:
        add("decoded true peak", None,
            f"<= {CEILING_DBTP} dBTP", False)
    else:
        add("decoded true peak", tp, f"<= {CEILING_DBTP} dBTP",
            float(tp) <= CEILING_DBTP)
    sworn = measured.get("sworn_bitrate_bps")
    if sworn:
        bps = measured.get("bitrate_bps")
        if bps is None:
            add("bitrate (sworn)", None,
                f"exactly {int(sworn)} bps", False)
        else:
            add("bitrate (sworn)", bps,
                f"exactly {int(sworn)} bps",
                int(bps) == int(sworn))
    if measured.get("sigma_sworn"):
        band = measured.get("sigma_band_dbfs")
        if band is None:
            add("sigma band (sworn)", None,
                f"{SIGMA_BAND_DBFS} +/- {SIGMA_TOLERANCE_DB} dBFS",
                False)
        else:
            add("sigma band (sworn)", band,
                f"{SIGMA_BAND_DBFS} +/- {SIGMA_TOLERANCE_DB} dBFS",
                abs(float(band) - SIGMA_BAND_DBFS)
                <= SIGMA_TOLERANCE_DB)
    failures = [c["check"] for c in checks if not c["ok"]]
    return {"sealed": not failures, "checks": checks,
            "failures": failures}


def append_master_proof(artifact_path, manifest, measured,
                        parents=(), ledger_path=None, ts=None,
                        root=None):
    """Append a master proof, sealed or failed by the gate.

    MECHANISM: the gate weighs the measured body FIRST; the
    record then carries the verdict in its status (SEALED /
    FAILED) and the whole gate in its body. The proof is
    appended either way -- Proof of Mastering is a record of
    what the scales said, and a failed master is a fact of the
    house's history, not an embarrassment to be struck.
    """
    gate = check_mastering(measured)
    body = dict(manifest)
    body["measured"] = measured
    return append_proof(
        "master", artifact_path, body, parents=parents,
        ledger_path=ledger_path,
        status="SEALED" if gate["sealed"] else "FAILED",
        gate=gate, ts=ts, root=root)


# ---------------------------------------------------------------------
# Measuring a delivered master (the gate's scales).
# ---------------------------------------------------------------------

def _ffprobe_bitrate_bps(mp3_path):
    """The MP3 stream's bitrate, from ffprobe (None if unreadable)."""
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=bit_rate", "-of", "json",
         str(mp3_path)], capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    try:
        rate = json.loads(proc.stdout)["streams"][0]["bit_rate"]
        return int(rate)
    except (KeyError, IndexError, ValueError):
        return None


def measure_master(mp3_path, wav_path=None):
    """Measure a delivered master: the MP3 decoded, the WAV beside.

    MECHANISM: the MP3 is decoded by ffmpeg to a 48 kHz WAV in a
    temp file and weighed with the pipeline's own scales
    (BS.1770 LUFS + FFT true peak -- the same scales the chain
    mastered with, so the gate argues with no second yardstick);
    its stream bitrate comes from ffprobe. The master WAV, when
    given, is weighed the same way and carried beside, so the
    record shows both the intention and the delivery. Returns
    the measured body check_mastering consumes, with the raw
    per-file figures under 'files'.
    """
    from resonance.studio import pipeline  # lazy: pipeline imports us
    mp3_path = Path(mp3_path)
    body = {"bitrate_bps": _ffprobe_bitrate_bps(mp3_path),
            "sworn_bitrate_bps": SWORN_BITRATE_BPS,
            "files": {}}
    with tempfile.TemporaryDirectory() as tmp:
        decoded = Path(tmp) / "decoded.wav"
        proc = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(mp3_path),
             "-ar", "48000", str(decoded)],
            capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(
                f"measure_master: ffmpeg decode of {mp3_path} "
                f"failed: {proc.stderr.strip()}")
        samples, sr = pipeline.read_wav_pcm(decoded)
        body["lufs_integrated"] = round(
            pipeline.measure_loudness_lufs(samples, sr), 2)
        body["true_peak_dbtp"] = round(
            pipeline.true_peak_dbtp(samples, sr), 2)
        body["files"]["delivered_mp3"] = {
            "path": str(mp3_path), "decoded_sr": sr,
            "lufs_integrated": body["lufs_integrated"],
            "true_peak_dbtp": body["true_peak_dbtp"],
            "bitrate_bps": body["bitrate_bps"]}
    if wav_path is not None:
        samples, sr = pipeline.read_wav_pcm(wav_path)
        body["files"]["master_wav"] = {
            "path": str(wav_path), "sample_rate": sr,
            "lufs_integrated": round(
                pipeline.measure_loudness_lufs(samples, sr), 2),
            "true_peak_dbtp": round(
                pipeline.true_peak_dbtp(samples, sr), 2)}
    return body


def emit_produce_proof(manifest, out_dir, spec, log=print):
    """produce()'s native emission: the run's master proof.

    MECHANISM: called by pipeline.produce with the finished
    manifest in hand; the delivered preview MP3 and the master
    WAV are measured, the gate weighs the delivery, and the
    master proof is appended with any parent IDs the spec
    declared (spec['proof']['parents']). Returns the manifest's
    'proof' section. Fail-closed in the record's sense: if the
    emission itself fails (a missing file, a dead scale), the
    section confesses EMISSION FAILED with the error at full
    size and the log carries it loudly -- the run's artifacts
    stand, but no one is told a proof exists when none was
    struck. Nothing is swallowed; the failure is printed in the
    run's own manifest, where the founder reads his runs.
    """
    out_dir = Path(out_dir)
    try:
        files = manifest["files"]
        mp3 = Path(files["preview_mp3"]["path"])
        wav = Path(files["master_wav"]["path"])
        measured = measure_master(mp3, wav)
        body = {
            "title": manifest.get("title"),
            "pipeline": manifest.get("pipeline"),
            "four_powers": manifest.get("four_powers"),
            "master_report": manifest.get("master"),
            "program": manifest.get("program"),
        }
        parents = (spec.get("proof") or {}).get("parents", [])
        ledger = (spec.get("proof") or {}).get("ledger")
        rec = append_master_proof(
            mp3, body, measured, parents=parents,
            ledger_path=ledger)
        log(f"proof of mastering: {rec['id']} "
            f"({rec['status']}) appended to the ledger")
        return {"id": rec["id"], "kind": "master",
                "status": rec["status"], "gate": rec["gate"],
                "ledger": str(Path(ledger)
                              if ledger else default_ledger_path())}
    except Exception as exc:  # confessed in the manifest, never hidden
        log(f"proof of mastering: EMISSION FAILED: {exc}")
        return {"status": "EMISSION FAILED",
                "error": f"{type(exc).__name__}: {exc}"}


# ---------------------------------------------------------------------
# The calibration loop: the Nine as training axes.
# ---------------------------------------------------------------------

def accumulate_calibration(records):
    """Accumulate the calibration store from a ledger's records.

    MECHANISM: every vocal proof whose manifest carries
    seat_totals ({seat: {asked_s, realized_s}}) adds its totals
    into the store, seat by seat, and its ID onto each seat it
    trained. The store is DERIVED state -- it can be rebuilt
    from the ledger at any time, and rebuilding is the only way
    it changes: no hand edits, no silent drift between the
    ledger and the lessons drawn from it.
    """
    seats = {}
    for rec in records:
        if rec.get("kind") != "vocal":
            continue
        totals = (rec.get("manifest") or {}).get("seat_totals") \
            or {}
        for seat, vals in totals.items():
            if seat not in SEATS:
                continue
            acc = seats.setdefault(
                seat, {"asked_s": 0.0, "realized_s": 0.0,
                       "phonemes": 0, "trained_by": []})
            acc["asked_s"] += float(vals.get("asked_s", 0.0))
            acc["realized_s"] += float(vals.get("realized_s", 0.0))
            acc["phonemes"] += int(vals.get("phonemes", 0))
            if rec["id"] not in acc["trained_by"]:
                acc["trained_by"].append(rec["id"])
    for acc in seats.values():
        acc["asked_s"] = round(acc["asked_s"], 4)
        acc["realized_s"] = round(acc["realized_s"], 4)
    return {"version": 1, "seats": seats}


def calibration_factors(store):
    """The learned per-seat factors: asked / realized, clamped.

    A seat the store has never seen -- or one whose realized
    total is zero -- has no factor: the plug applies 1.0 there
    and the render's manifest says the seat was untrained. The
    clamp is doctrine, stated in the header: outside [0.5, 2.0]
    a ratio is a broken measurement, not a correction.
    """
    factors = {}
    for seat, acc in (store.get("seats") or {}).items():
        asked, realized = acc["asked_s"], acc["realized_s"]
        if realized > 0 and asked > 0:
            factors[seat] = round(
                min(FACTOR_MAX, max(FACTOR_MIN, asked / realized)),
                4)
    return factors


def calibration_trained_by(store):
    """Every proof ID that trained any seat, in ledger order."""
    ids = []
    for acc in (store.get("seats") or {}).values():
        for pid in acc["trained_by"]:
            if pid not in ids:
                ids.append(pid)
    return ids


def rebuild_calibration(ledger_path=None, write=True):
    """Rebuild the store from the ledger; write it beside it."""
    ledger = Path(ledger_path) if ledger_path \
        else default_ledger_path()
    store = accumulate_calibration(read_ledger(ledger))
    if write:
        path = calibration_path_for(ledger)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(store, ensure_ascii=False,
                                   indent=2), encoding="utf-8")
    return store


def load_calibration(ledger_path=None):
    """Read the store beside the ledger (rebuild if absent)."""
    ledger = Path(ledger_path) if ledger_path \
        else default_ledger_path()
    path = calibration_path_for(ledger)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return rebuild_calibration(ledger, write=True)


# ---------------------------------------------------------------------
# The stamp: the MAGVS toolkit's door.
# ---------------------------------------------------------------------

def stamp(kind, file_path, manifest=None, parents=(),
          ledger_path=None, root=None):
    """Stamp an existing file into the ledger as a proof.

    The one door every toolkit shares: the MAGVS builders stamp
    their editions (kind 'score' for a sheet, 'master' only via
    the gate -- a stamp of kind 'master' is REFUSED here, because
    a master seals by measurement, not by declaration; use
    append_master_proof with a measured body), the bookshop
    stamps its pages' sources, a hand render stamps its vocal.
    """
    if kind == "master":
        raise ValueError(
            "stamp: a master proof seals by measurement, not by "
            "declaration -- measure the delivered artifact and "
            "append it through append_master_proof / the gate")
    return append_proof(kind, file_path, manifest or {},
                        parents=parents, ledger_path=ledger_path,
                        root=root)


# ---------------------------------------------------------------------
# The CLI: stamp / verify / calibration / gate.
#
#   python3 -m resonance.studio.proofs stamp --kind vocal \
#       --file path/to.wav [--parents pow-...,pow-...] \
#       [--manifest-json FILE] [--ledger PATH]
#   python3 -m resonance.studio.proofs verify [--ledger PATH]
#   python3 -m resonance.studio.proofs calibration [--ledger PATH]
#   python3 -m resonance.studio.proofs gate --mp3 FILE [--wav FILE]
#
# Exit codes are honest: 0 on success (a verify with no breaks, a
# gate that seals), 1 on a confessed failure (breaks found, a
# gate that refuses), 2 on usage. The JSON on stdout is the
# record / verdict, whole -- a machine reader gets the same
# truth a human does.
# ---------------------------------------------------------------------

def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(
        prog="resonance.studio.proofs",
        description="Render-as-Proof: the studio's hash-chained "
                    "proof ledger (stamp / verify / calibration "
                    "/ gate). Mints no token; proofs are records.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("stamp", help="stamp a file into the ledger")
    p.add_argument("--kind", required=True, choices=KINDS)
    p.add_argument("--file", required=True)
    p.add_argument("--parents", default="",
                   help="comma-separated parent proof IDs")
    p.add_argument("--manifest-json",
                   help="a JSON file carried as the manifest body")
    p.add_argument("--ledger")

    p = sub.add_parser("verify", help="re-walk the chain")
    p.add_argument("--ledger")

    p = sub.add_parser("calibration",
                       help="rebuild + print the calibration store")
    p.add_argument("--ledger")

    p = sub.add_parser("gate",
                       help="measure a delivered master and weigh "
                            "it against the house law")
    p.add_argument("--mp3", required=True)
    p.add_argument("--wav")
    p.add_argument("--ledger",
                   help="also append the master proof to this "
                        "ledger (default: the house ledger)")
    p.add_argument("--no-append", action="store_true",
                   help="weigh only; append nothing")
    p.add_argument("--parents", default="")

    args = ap.parse_args(argv)
    if args.cmd == "stamp":
        manifest = {}
        if args.manifest_json:
            manifest = json.loads(
                Path(args.manifest_json).read_text(
                    encoding="utf-8"))
        parents = [s for s in args.parents.split(",") if s]
        rec = stamp(args.kind, args.file, manifest,
                    parents=parents, ledger_path=args.ledger)
        print(json.dumps(rec, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "verify":
        verdict = verify_ledger(args.ledger)
        print(json.dumps(verdict, ensure_ascii=False, indent=2))
        return 0 if verdict["ok"] else 1
    if args.cmd == "calibration":
        store = rebuild_calibration(args.ledger)
        print(json.dumps(
            {"store": store,
             "factors": calibration_factors(store),
             "trained_by": calibration_trained_by(store)},
            ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "gate":
        measured = measure_master(args.mp3, args.wav)
        gate = check_mastering(measured)
        out = {"measured": measured, "gate": gate}
        if not args.no_append:
            parents = [s for s in args.parents.split(",") if s]
            rec = append_master_proof(
                args.mp3, {"source": "proofs CLI gate"},
                measured, parents=parents,
                ledger_path=args.ledger)
            out["proof"] = {"id": rec["id"],
                            "status": rec["status"]}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if gate["sealed"] else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())

# 93 -- Live, Love, and let Love, Live.
