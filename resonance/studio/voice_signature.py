# 93
# ---------------------------------------------------------------------
# voice_signature.py -- the voice-signature plug: a registry of
# synthetic persona voices, enrollment under the founder's
# boundary, and renders through local llama.cpp TTS backends,
# every render measured on this side and written into the trail.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XXIV day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: a voice signature is a small, inspectable record --
# an ID, its holder (a persona, or the founder's seat), the voice
# spec AS FILED in the house record (quoted, never invented by
# this module), a reference WAV when one has been enrolled, that
# reference's provenance, and the backends that may render it.
# The registry lives beside this module in voice_signatures/
# (signatures.json + references/ + render_log.jsonl). enroll()
# validates a generated reference (stdlib wave: it must exist,
# parse, and carry real seconds), copies it into the registry,
# and records its SHA-256 and measured shape. render() hands
# (signature, text) to ONE named backend -- Fish Audio S2 via
# llama-tts (ggml-org llama.cpp, build b12452 or later, the build
# that brought S2 cloning into the runtime), or the house's
# proven ZONOS3-Mini seat via the same llama-tts family -- then
# MEASURES what came back on this side (duration, sample rate,
# peak, true peak, loudness) and appends the whole record to
# render_log.jsonl, the per-track documentation trail. A claim
# you cannot measure is a wish, so the log's numbers are read
# off the struck file here, never relayed from the backend.
#
# DOCTRINE -- THE BOUNDARY (the founder's, absolute, and printed
# here because this module is where it binds):
#   * Signatures enroll SYNTHETIC persona voices and GENERATED
#     references only. A reference enters this registry with
#     provenance kind GENERATED -- a render struck by a house
#     engine -- or it does not enter at all.
#   * THE FOUNDER'S OWN VOICE IS NEVER RECORDED, ENROLLED, OR
#     CLONED. His seat (holder id 'qasparr') is an imagined
#     synthetic voice under his filed spec -- the 2Pac register:
#     medium pitch, forward/urgent, nasal edge, diction like
#     testimony, emotion at the front -- authorized for pilot
#     tracks as an imagined voice only. The spec is FILED, not
#     written at enrollment: enroll() refuses a caller-supplied
#     spec for the founder's seat that parts from the filed one.
#   * NO CLONE OF ANY PERSON stands in this registry (house law,
#     docs/IN-HOUSE-VOCAL-ROAD.md, Layer 2: never the founder's
#     recorded voice, never a clone of any person). A provenance
#     claiming a recording, a clone, or a sampled real voice is
#     refused by name, for every holder, before any file moves.
# The refusals are code, not commentary: BoundaryError is raised
# at the enroll() gate, and the test suite holds the gate shut.
#
# DOCTRINE -- WHAT A SIGNATURE IS FOR, AND WHAT IT IS NOT FOR:
# signatures serve the SPEECH seat -- spoken passages, persona
# consistency across tracks, pilot and guide renders, narration.
# Sung vocals stay on the score-first road (the DiffSinger plug:
# sheets first, then singing from the sheets); a signature does
# NOT displace that law, and nothing in this module sings.
#
# DOCTRINE -- NO SILENT SUBSTITUTION: a render is the named
# signature through the named backend, or it does not happen.
# If the backend's binary or weights are absent, if the
# signature seats no such backend, or if a cloning backend is
# asked to speak for a signature with no reference enrolled
# (it would speak with an anonymous speaker -- somebody else's
# voice wearing the persona's name), render() raises
# BackendUnavailable / VoiceSignatureError and strikes nothing.
# There is no fallback voice in this module, on purpose.
#
# Tolerances (the fourth element): reference and render shapes
# are measured to the sample by stdlib wave; loudness is read
# on the rate-following pyloudnorm scale (the upscale seat's
# precedent, since renders land at engine-native rates) and,
# at 48 kHz exactly, also on the pipeline's own BS.1770 scale,
# each figure labelled with its scale; a render shorter than
# the loudness block is reported UNWEIGHED on that scale, never
# padded into a number. Wall-clock render time is recorded,
# not sworn -- this box shares its CPUs.
# ---------------------------------------------------------------------

import hashlib
import json
import os
import subprocess
import time
import wave
from pathlib import Path

import numpy as np

# The registry seats beside the module, as the exam corpus seats
# beside vocal_exam.py: data with the plug, inspectable in git.
REGISTRY_DIR = Path(__file__).resolve().parent / "voice_signatures"
DEFAULT_REGISTRY_PATH = REGISTRY_DIR / "signatures.json"
REFERENCES_DIRNAME = "references"
RENDER_LOG_NAME = "render_log.jsonl"
REGISTRY_SCHEMA = 1

# The founder's seat. The id is a load-bearing constant: the
# boundary checks below key on it, and the tests hold them shut.
FOUNDER_ID = "qasparr"

# The founder's filed spec, quoted from the house record (voice
# signatures RULED 2026-11-10, 07:37 EST; ear verdict the same
# morning: "Confirmed voices were perfect."). enroll() holds
# this text against any caller-supplied founder spec: the seat
# is spec-matched or the enrollment is refused.
FILED_FOUNDER_SPEC = {
    "register": (
        "the 2Pac register -- medium pitch, forward/urgent, nasal "
        "edge, diction like testimony, emotion at the front"),
    "summary": (
        "An imagined synthetic voice only, authorized to stand "
        "as the founder's for pilot tracks -- imagined, never a "
        "recording or clone of his voice. The struck Gemini "
        "voice was ruled TOO DEEP (2026-11-10); this register "
        "is the filed correction."),
    "source": (
        "MEMORY.md, voice signatures ruled 2026-11-10 07:37 EST; "
        "ear verdict 2026-11-10 07:47 EST"),
}

# The only provenance kind a reference may carry into this
# registry. Everything else -- a recording, a clone, a licensed
# real voice -- is a different instrument on a different road
# (a voicebank dataset, Layer 2 of the in-house vocal road),
# and is refused here by name.
GENERATED = "GENERATED"


class VoiceSignatureError(Exception):
    """A voice-signature refusal, by name."""


class BoundaryError(VoiceSignatureError):
    """The founder's boundary refused the enrollment."""


class BackendUnavailable(VoiceSignatureError):
    """The named backend cannot render here; nothing was struck."""


# ---------------------------------------------------------------------
# WAV measurement -- stdlib wave for the shape, numpy for the
# samples, the house scales for the weights. Every figure is
# measured off the file on this side of the wall.
# ---------------------------------------------------------------------

def measure_wav(path):
    """Measure a WAV file: shape, peak, true peak, loudness.

    MECHANISM: stdlib wave reads the header and frames; samples
    are de-interleaved to float64 in [-1, 1). True peak rides
    the pipeline's own 4x-oversampled scale (any rate). Loudness
    rides pyloudnorm, whose coefficients follow the rate (the
    upscale seat's precedent), and -- at exactly 48 kHz -- also
    the pipeline's BS.1770 scale. A scale that cannot weigh the
    file reports None with its reason in the record; no figure
    is ever padded or invented.
    """
    path = Path(path)
    if not path.exists():
        raise VoiceSignatureError(f"measure_wav: no such file: {path}")
    try:
        with wave.open(str(path), "rb") as w:
            channels = w.getnchannels()
            rate = w.getframerate()
            width = w.getsampwidth()
            n_frames = w.getnframes()
            raw = w.readframes(n_frames)
    except (wave.Error, EOFError) as exc:
        raise VoiceSignatureError(
            f"measure_wav: not a readable WAV: {path} ({exc})")
    if n_frames == 0 or rate <= 0:
        raise VoiceSignatureError(
            f"measure_wav: WAV carries no samples: {path}")
    dtype = {1: np.uint8, 2: np.int16, 4: np.int32}.get(width)
    if dtype is None:
        raise VoiceSignatureError(
            f"measure_wav: unseated sample width {width} bytes: {path}")
    x = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    if width == 1:
        x = (x - 128.0) / 128.0
    elif width == 2:
        x = x / 32768.0
    else:
        x = x / 2147483648.0
    x = x[: (len(x) // channels) * channels].reshape(-1, channels)
    record = {
        "duration_s": round(n_frames / float(rate), 4),
        "sample_rate": rate,
        "channels": channels,
        "frames": n_frames,
        "peak_dbfs": round(
            20.0 * np.log10(max(np.max(np.abs(x)), 1e-12)), 2),
        "lufs": None,
        "lufs_scale": None,
        "lufs_note": None,
        "dbtp": None,
    }
    # True peak on the pipeline's scale (rate-agnostic).
    try:
        from resonance.studio import pipeline as _pipeline
        record["dbtp"] = round(
            float(_pipeline.true_peak_dbtp(x.T.copy(), rate)), 2)
        if rate == 48000:
            record["lufs"] = round(
                float(_pipeline.measure_loudness_lufs(x.T.copy(), rate)), 2)
            record["lufs_scale"] = "pipeline BS.1770 (48 kHz set)"
    except Exception as exc:  # a scale that fails reports, never hides
        record["lufs_note"] = f"pipeline scales unavailable: {exc}"
    # Rate-following loudness (pyloudnorm) when the pipeline's
    # fixed 48 kHz set does not apply.
    if record["lufs"] is None:
        try:
            import pyloudnorm as _pyln
            meter = _pyln.Meter(rate)
            mono = x.mean(axis=1) if channels > 1 else x[:, 0]
            val = float(meter.integrated_loudness(
                mono if channels == 1 else x))
            if np.isfinite(val):
                record["lufs"] = round(val, 2)
                record["lufs_scale"] = "pyloudnorm (rate-following)"
                record["lufs_note"] = None
            else:
                record["lufs_note"] = (
                    "pyloudnorm read the file as silence/unweighable")
        except Exception as exc:
            note = f"pyloudnorm unavailable: {exc}"
            record["lufs_note"] = (
                note if record["lufs_note"] is None
                else record["lufs_note"] + "; " + note)
    return record


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# ---------------------------------------------------------------------
# The registry -- a JSON document of signature records. Loaded
# whole, saved whole, written atomically enough for a bench
# (temp file + rename), and validated on the way in: a registry
# that cannot prove its own shape does not load.
# ---------------------------------------------------------------------

def empty_registry():
    return {"schema": REGISTRY_SCHEMA, "signatures": []}


def load_registry(registry_path=None):
    """Load and shape-check the registry (missing file = empty)."""
    path = Path(registry_path) if registry_path else DEFAULT_REGISTRY_PATH
    if not path.exists():
        return empty_registry()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VoiceSignatureError(
            f"load_registry: registry unreadable: {path} ({exc})")
    if not isinstance(data, dict) or data.get("schema") != REGISTRY_SCHEMA \
            or not isinstance(data.get("signatures"), list):
        raise VoiceSignatureError(
            f"load_registry: registry shape unseated: {path}")
    seen = set()
    for rec in data["signatures"]:
        if not isinstance(rec, dict) or not rec.get("id") \
                or not rec.get("holder"):
            raise VoiceSignatureError(
                f"load_registry: a signature record lacks id/holder: "
                f"{path}")
        if rec["id"] in seen:
            raise VoiceSignatureError(
                f"load_registry: duplicate signature id: {rec['id']}")
        seen.add(rec["id"])
    return data


def save_registry(data, registry_path=None):
    path = Path(registry_path) if registry_path else DEFAULT_REGISTRY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    tmp.replace(path)
    return path


def get_signature(signature_id, registry_path=None):
    for rec in load_registry(registry_path)["signatures"]:
        if rec["id"] == signature_id:
            return rec
    raise VoiceSignatureError(
        f"get_signature: no signature seated under id "
        f"{signature_id!r}")


def list_signatures(registry_path=None):
    return [rec["id"] for rec in load_registry(registry_path)["signatures"]]


# ---------------------------------------------------------------------
# Enrollment -- the gate the boundary guards.
# ---------------------------------------------------------------------

def _check_provenance(signature_id, provenance):
    """Hold the boundary against a reference's provenance.

    The rules, in order, each refused by name:
      1. a reference must carry provenance at all;
      2. its kind must be GENERATED -- a recording, a clone, or
         a sampled real voice is refused for EVERY holder;
      3. a GENERATED claim must name its engine (a generation
         with no engine named is a claim, not a provenance);
      4. for the founder's seat, the provenance's subject may
         only be the imagined synthetic voice -- never the man.
    """
    if not isinstance(provenance, dict):
        raise BoundaryError(
            f"enroll: signature {signature_id!r} reference carries "
            f"no provenance; a reference without provenance does "
            f"not enter this registry")
    kind = str(provenance.get("kind", "")).strip().upper()
    if kind != GENERATED:
        raise BoundaryError(
            f"enroll: provenance kind {kind or '<none>'!r} refused "
            f"for signature {signature_id!r} -- this registry "
            f"enrolls GENERATED references only; a recording, a "
            f"clone, or a sampled real voice is a different "
            f"instrument on a different road (never the founder's "
            f"recorded voice, never a clone of any person)")
    if not str(provenance.get("engine", "")).strip():
        raise BoundaryError(
            f"enroll: GENERATED provenance for {signature_id!r} "
            f"names no engine; the generation must say what "
            f"struck it")
    if signature_id == FOUNDER_ID:
        subject = str(provenance.get("subject", "")).strip().lower()
        if subject not in ("", "imagined-synthetic", "imagined synthetic"):
            raise BoundaryError(
                f"enroll: the founder's seat enrolls an imagined "
                f"synthetic voice only; provenance subject "
                f"{subject!r} refused -- his own voice is never "
                f"recorded, enrolled, or cloned")


def _check_founder_spec(signature_id, spec):
    """The founder's spec is filed, not written at enrollment."""
    if signature_id != FOUNDER_ID or spec is None:
        return
    for field in ("register", "summary"):
        offered = str(spec.get(field, "")).strip()
        if offered and offered != FILED_FOUNDER_SPEC[field]:
            raise BoundaryError(
                f"enroll: caller spec for the founder's seat "
                f"parts from the filed spec at {field!r}; the "
                f"spec is filed (2026-11-10), not rewritten at "
                f"enrollment")


def enroll(signature_id, reference_wav=None, spec=None, *,
           holder=None, holder_kind=None, crew=None,
           provenance=None, backends=None, notes=None,
           enrolled_on=None, registry_path=None):
    """Enroll (or complete) a voice signature in the registry.

    MECHANISM: upsert by id. A new id requires a holder. The
    filed spec is stored as given for personas; for the
    founder's seat the filed spec is seated by the module and
    a parting caller spec is refused (see _check_founder_spec).
    A reference WAV is provenance-checked at the boundary gate,
    measured, hashed, and COPIED into the registry's
    references/ directory, so the registry is self-contained:
    the record's reference is the copy, its provenance, and its
    hash. Enrolling a reference seats the fish_s2 clone backend
    on the record unless the caller seats backends explicitly.

    Returns the stored record.
    """
    if not signature_id or not str(signature_id).strip():
        raise VoiceSignatureError("enroll: a signature needs an id")
    signature_id = str(signature_id).strip()
    # The boundary gates run BEFORE any bookkeeping: a refused
    # enrollment is refused whatever the registry holds, and a
    # recording or a clone never gets far enough to learn
    # whether its id was already seated.
    _check_founder_spec(signature_id, spec)
    if reference_wav is not None:
        _check_provenance(signature_id, provenance)
    reg_path = Path(registry_path) if registry_path \
        else DEFAULT_REGISTRY_PATH
    data = load_registry(reg_path)
    rec = None
    for existing in data["signatures"]:
        if existing["id"] == signature_id:
            rec = existing
            break
    if rec is None:
        if not holder and signature_id == FOUNDER_ID:
            holder = "QASPARR"  # the seat's holder is filed, too
        if not holder:
            raise VoiceSignatureError(
                f"enroll: new signature {signature_id!r} requires "
                f"a holder")
        rec = {
            "id": signature_id,
            "holder": holder,
            "holder_kind": holder_kind or (
                "founder" if signature_id == FOUNDER_ID else "persona"),
            "crew": crew,
            "spec": None,
            "reference": None,
            "backends": {},
            "enrolled": None,
            "notes": None,
        }
        data["signatures"].append(rec)
    if signature_id == FOUNDER_ID:
        rec["spec"] = dict(FILED_FOUNDER_SPEC)
        rec["holder_kind"] = "founder"
    elif spec is not None:
        rec["spec"] = spec
    if holder is not None:
        rec["holder"] = holder
    if crew is not None:
        rec["crew"] = crew
    if notes is not None:
        rec["notes"] = notes
    if backends is not None:
        rec["backends"] = backends
    if reference_wav is not None:
        src = Path(reference_wav)
        shape = measure_wav(src)  # refuses absent/unreadable/silent
        if shape["duration_s"] < 0.5:
            raise VoiceSignatureError(
                f"enroll: reference for {signature_id!r} is "
                f"{shape['duration_s']} s -- under the 0.5 s floor "
                f"for a voice worth enrolling")
        ref_dir = reg_path.parent / REFERENCES_DIRNAME
        ref_dir.mkdir(parents=True, exist_ok=True)
        dest = ref_dir / f"{signature_id}.wav"
        dest.write_bytes(src.read_bytes())
        rec["reference"] = {
            "file": f"{REFERENCES_DIRNAME}/{dest.name}",
            "sha256": _sha256(dest),
            "duration_s": shape["duration_s"],
            "sample_rate": shape["sample_rate"],
            "channels": shape["channels"],
            "provenance": provenance,
        }
        if backends is None and "fish_s2" not in rec["backends"]:
            rec["backends"]["fish_s2"] = {"mode": "clone"}
    rec["enrolled"] = enrolled_on or time.strftime("%Y-%m-%d")
    save_registry(data, reg_path)
    return rec


# ---------------------------------------------------------------------
# Backends -- the llama-tts family. Both seats speak the same
# CLI (the house's proven shape, from the ZONOS3 audiobook
# road): llama-tts -m <model> -mm <mmproj> [voice door]
# -p <text> -o <out.wav>. What differs is the voice door:
# Fish S2 clones from a reference (--tts-speaker-file +
# --tts-speaker-text); ZONOS3-Mini's proven ggml road names a
# built-in voice (--tts-voice). A backend reports its own
# availability from the files on disk; nothing is assumed.
# ---------------------------------------------------------------------

def _find_llama_tts(lab_dir):
    """The highest llama-tts build seated in a lab directory."""
    lab = Path(lab_dir)
    candidates = sorted(lab.glob("bin/llama-b*/llama-tts"))
    if not candidates:
        direct = lab / "bin" / "llama-tts"
        return direct if direct.exists() else None
    return candidates[-1]


def _find_model(lab_dir, *names):
    lab = Path(lab_dir)
    for name in names:
        hit = lab / "models" / name
        if hit.exists():
            return hit
    return None


class LlamaTtsBackend:
    """One llama-tts seat: a lab, a model pair, a build label."""

    name = "llama_tts"
    supports_clone = False
    supports_named_voice = False

    def __init__(self, lab_dir, model_names, mmproj_names, label):
        self.lab_dir = Path(lab_dir)
        self.binary = _find_llama_tts(self.lab_dir)
        self.model = _find_model(self.lab_dir, *model_names)
        self.mmproj = _find_model(self.lab_dir, *mmproj_names)
        self.label = label

    def available(self):
        """(ok, reason) -- the seat's own word about itself."""
        if self.binary is None:
            return False, (f"{self.label}: no llama-tts binary "
                           f"under {self.lab_dir}/bin")
        if self.model is None:
            return False, (f"{self.label}: no model seated under "
                           f"{self.lab_dir}/models")
        if self.mmproj is None:
            return False, (f"{self.label}: no mmproj/codec seated "
                           f"under {self.lab_dir}/models")
        return True, f"{self.label}: {self.binary.name} + " \
                     f"{self.model.name}"

    def _run(self, args, out_path, timeout=3600):
        cmd = [str(self.binary), "-m", str(self.model),
               "-mm", str(self.mmproj), "-t", "4"] + args + \
              ["-o", str(out_path)]
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0 or not Path(out_path).exists():
            tail = (proc.stderr or proc.stdout or "")[-800:]
            raise VoiceSignatureError(
                f"{self.label}: llama-tts struck nothing "
                f"(rc={proc.returncode}): {tail}")
        return proc


class FishS2Backend(LlamaTtsBackend):
    """Fish Audio S2 (Pro GGUF) -- the cloning seat.

    MECHANISM: the prompt carries the speaker tag
    (<|speaker:0|>) and the reference rides --tts-speaker-file
    with its transcript on --tts-speaker-text, per ggml-org's
    s2-pro-GGUF card. The weights stand under the Fish Audio
    Research License (research / non-commercial; commercial
    use limited) -- the seat is a bench instrument, and the
    license coordinate is printed in docs/VOICE-SIGNATURES.md.
    """

    name = "fish_s2"
    supports_clone = True

    def __init__(self, lab_dir=None):
        lab = lab_dir or os.environ.get(
            "RESONANTIA_FISH_S2_LAB",
            str(Path.home() / "workspace" / "lab" / "fish-s2"))
        super().__init__(
            lab,
            ("s2-pro-Q8_0.gguf", "s2-pro-BF16.gguf"),
            ("mmproj-s2-pro-BF16.gguf",),
            "fish_s2 (llama.cpp >= b12452)")

    def render_clone(self, reference_wav, reference_text, text,
                     out_path):
        prompt = text if text.lstrip().startswith("<|speaker:") \
            else f"<|speaker:0|>{text}"
        args = ["--tts-speaker-file", str(reference_wav)]
        if reference_text:
            args += ["--tts-speaker-text", reference_text]
        args += ["-p", prompt]
        return self._run(args, out_path)


class ZonosBackend(LlamaTtsBackend):
    """ZONOS3-Mini -- the house's proven speech seat (b12438).

    Its proven ggml road names a built-in voice; it does not
    clone from a reference through this plug, and the plug
    says so rather than pretending a preset is a signature's
    own voice: a signature seats this backend only by naming
    the voice its record carries.
    """

    name = "zonos"
    supports_named_voice = True

    def __init__(self, lab_dir=None):
        lab = lab_dir or os.environ.get(
            "RESONANTIA_ZONOS_LAB",
            str(Path.home() / "workspace" / "lab" / "zonos3-mini"))
        super().__init__(
            lab,
            ("ZONOS3-Mini-Q8_0.gguf",),
            ("mmproj-ZONOS3-Mini-F32.gguf",),
            "zonos (ZONOS3-Mini via llama-tts)")

    def render_voice(self, voice, text, out_path):
        return self._run(
            ["--tts-voice", voice, "-n", "9000", "-p", text],
            out_path)


def default_backends():
    """The bench's two seats, probed from their lab dirs."""
    return {"fish_s2": FishS2Backend(), "zonos": ZonosBackend()}


# ---------------------------------------------------------------------
# The plug -- registry + backends + the render trail.
# ---------------------------------------------------------------------

class SignaturePlug:
    """Drive the registry: enroll at the gate, render by name.

    The plug is deliberately small: it owns no voice of its
    own. It holds the registry's path and the backend seats,
    and every render it strikes is measured and written into
    the registry's render_log.jsonl before it is returned.
    """

    def __init__(self, registry_path=None, backends=None):
        self.registry_path = Path(registry_path) \
            if registry_path else DEFAULT_REGISTRY_PATH
        self.backends = backends if backends is not None \
            else default_backends()

    # -- enrollment, delegated to the module gate ---------------
    def enroll(self, signature_id, reference_wav=None, spec=None,
               **kwargs):
        return enroll(signature_id, reference_wav, spec,
                      registry_path=self.registry_path, **kwargs)

    def get(self, signature_id):
        return get_signature(signature_id, self.registry_path)

    # -- the render ---------------------------------------------
    def render(self, signature_id, text, backend="fish_s2",
               out_path=None):
        """Render `text` as `signature_id` through ONE backend.

        Raises BackendUnavailable when the backend is absent or
        the signature does not seat it; VoiceSignatureError
        when the render would not be the signature's own voice.
        On success the output is measured, the record appended
        to the render log, and the record returned.
        """
        if not text or not str(text).strip():
            raise VoiceSignatureError("render: no text handed in")
        sig = self.get(signature_id)
        seat = self.backends.get(backend)
        if seat is None:
            raise BackendUnavailable(
                f"render: no backend named {backend!r} stands "
                f"on this plug")
        ok, reason = seat.available()
        if not ok:
            raise BackendUnavailable(f"render: {reason}")
        seated = (sig.get("backends") or {}).get(backend)
        if seated is None:
            raise BackendUnavailable(
                f"render: signature {signature_id!r} does not "
                f"seat backend {backend!r}; refusing to "
                f"substitute another voice")
        reg_dir = self.registry_path.parent
        if out_path is None:
            stamp = time.strftime("%Y%m%d-%H%M%S")
            out_path = reg_dir / "renders" / \
                f"{signature_id}-{backend}-{stamp}.wav"
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        if getattr(seat, "supports_clone", False):
            ref = sig.get("reference")
            if not ref:
                raise VoiceSignatureError(
                    f"render: signature {signature_id!r} has no "
                    f"reference enrolled; backend {backend!r} "
                    f"would speak with an anonymous speaker, "
                    f"which is a substitution -- refused")
            ref_path = reg_dir / ref["file"]
            ref_text = (ref.get("provenance") or {}).get(
                "source_line")
            seat.render_clone(ref_path, ref_text, text, out_path)
            mode = "clone"
        elif getattr(seat, "supports_named_voice", False):
            voice = seated.get("voice")
            if not voice:
                raise BackendUnavailable(
                    f"render: signature {signature_id!r} seats "
                    f"backend {backend!r} with no voice named")
            seat.render_voice(voice, text, out_path)
            mode = "named-voice"
        else:
            raise BackendUnavailable(
                f"render: backend {backend!r} offers no voice "
                f"door this plug can drive")
        wall = round(time.time() - t0, 2)
        shape = measure_wav(out_path)
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "signature_id": signature_id,
            "holder": sig["holder"],
            "backend": backend,
            "mode": mode,
            "text": text,
            "out": str(out_path),
            "wall_s": wall,
            "reference": (sig.get("reference") or {}).get("file"),
            **shape,
        }
        log_path = reg_dir / RENDER_LOG_NAME
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record


def render(signature_id, text, backend="fish_s2", *,
           registry_path=None, out_path=None):
    """Module-level render through a default plug (see class)."""
    plug = SignaturePlug(registry_path=registry_path)
    return plug.render(signature_id, text, backend, out_path=out_path)


# 93 -- Live, Love, and let Love, Live.
