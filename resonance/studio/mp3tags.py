# 93
# ---------------------------------------------------------------------
# mp3tags.py -- The proof stamp: a master's ID3 face.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: a pure-stdlib ID3v2 reader/writer (no mutagen in the
# house, and the proofs module's stdlib-only law is kept here too).
# The reader parses an ID3v2.3 or ID3v2.4 tag into frames, carrying
# every frame it does not own as opaque bytes; the writer re-emits
# the tag as ID3v2.4 (UTF-8 text, syncsafe sizes), preserving those
# foreign frames payload-for-payload and replacing the house's own
# frames wholesale, so a re-stamp is idempotent and never stacks.
# The audio body -- every byte after the tag -- is never touched,
# and audio_bytes() exposes it so a caller can PROVE that: the
# stamped file and its attested twin carry the same audio, byte
# for byte, whatever their tags say.
#
# DOCTRINE -- THE STAMP: since Render-as-Proof (resonantia
# 1c3724c), every master carries a proof in the ledger, but the
# delivered MP3 itself was mute: nothing in the file a listener
# receives named its proof. This module gives the file its face:
#   * TXXX/RESONANTIA PROOF  -- the master proof's ledger ID;
#   * TXXX/RESONANTIA STATUS -- SEALED, or FAILED;
#   * TXXX/RESONANTIA GATE   -- FAILED only: every failing check
#     with its measured value against its law. Fail-closed in the
#     metadata too: a failed master gets no stamp of pride, it
#     gets its failure printed on its face;
#   * TXXX/AUTHORSHIP        -- the founder's authorship line;
#   * COMM (eng)             -- the Flagpole of Claim and Coinage;
#   * TIT2                   -- the run's title, when it has one.
# The authorship and Flagpole strings are imported from proofs.py
# -- one source of truth, never a second spelling.
#
# DOCTRINE -- THE ATTESTED TWIN (why preserve_attested_copy
# exists): a proof record attests its artifact by SHA-256 of the
# artifact's whole bytes, and verify_ledger re-hashes the file on
# disk -- a body altered after its record stands is reported
# TAMPERED ARTIFACT. A proof's ID is the hash of a record that
# itself contains the artifact's hash, so an ID can never be
# written into the very body that record attests: the circle does
# not close, and pretending otherwise would corrupt the chain.
# The lawful order is therefore: the pristine encode is preserved
# untouched as the attested twin (the body the master proof
# attests and verification re-weighs), and the DELIVERED file --
# same audio, proven byte-identical after its tag -- carries the
# stamp with that proof's ID. Both bodies stand in the run folder,
# the record's manifest names the delivered file, and the stamp
# names the record. Nothing hidden, nothing smoothed.
#
# FAILURE LAW: exotic tag furniture this writer does not carry --
# an extended header, unsynchronisation, a footer, a compressed
# or encrypted foreign frame -- is REFUSED with a named error,
# never silently mangled. A file already carrying a house stamp
# is not pristine and is refused as an attested body: the twin
# must be the pre-stamp bytes, or it attests nothing.
# ---------------------------------------------------------------------

import shutil
from pathlib import Path

from resonance.studio.proofs import AUTHORSHIP, FLAGPOLE

# The house's own frame keys, as (frame id, TXXX description).
# A frame is the house's if it is a TXXX/COMM whose description
# is one of these, or the COMM carrying the Flagpole (desc "").
DESC_PROOF = "RESONANTIA PROOF"
DESC_STATUS = "RESONANTIA STATUS"
DESC_GATE = "RESONANTIA GATE"
DESC_AUTHORSHIP = "AUTHORSHIP"
_HOUSE_DESCS = {DESC_PROOF, DESC_STATUS, DESC_GATE, DESC_AUTHORSHIP}

_TEXT_ENCODING_UTF8 = 3  # ID3 text encoding byte: UTF-8 (v2.4).


class TagError(RuntimeError):
    """A tag this writer refuses to carry, named at full size."""


# ---------------------------------------------------------------------
# Reading: header, frames, the audio body.
# ---------------------------------------------------------------------

def _syncsafe_to_int(b):
    """ID3 syncsafe integer: 7 bits per byte, big-endian."""
    return ((b[0] & 0x7F) << 21) | ((b[1] & 0x7F) << 14) \
        | ((b[2] & 0x7F) << 7) | (b[3] & 0x7F)


def _int_to_syncsafe(n):
    """Inverse of _syncsafe_to_int (28-bit range)."""
    if n < 0 or n >= (1 << 28):
        raise TagError(f"tag size {n} outside the syncsafe range")
    return bytes([(n >> 21) & 0x7F, (n >> 14) & 0x7F,
                  (n >> 7) & 0x7F, n & 0x7F])


def parse_tag(data):
    """Parse the ID3v2 tag at the head of MP3 bytes.

    Returns {"version": 3|4|None, "frames": [(frame_id, flags,
    payload)], "tag_end": int, "audio": bytes}. A file with no
    ID3v2 header parses as version None, no frames, the whole
    body as audio. Foreign frames come back as opaque payloads;
    text is decoded only for the house's own frames, by
    read_stamp(). Refusals (TagError) name their cause: a major
    version outside 3/4, an extended header, unsynchronisation,
    or a footer -- furniture this writer does not carry.
    """
    if len(data) < 10 or data[:3] != b"ID3":
        return {"version": None, "frames": [], "tag_end": 0,
                "audio": bytes(data)}
    major = data[3]
    if major not in (3, 4):
        raise TagError(
            f"ID3v2.{major} is outside this writer's carry "
            f"(v2.3 and v2.4 only)")
    flags = data[5]
    if flags & 0x80:
        raise TagError("unsynchronised tag refused: this writer "
                       "does not carry unsynchronisation")
    if flags & 0x40:
        raise TagError("extended header refused: this writer "
                       "does not carry extended headers")
    if flags & 0x10:
        raise TagError("ID3v2.4 footer refused: this writer "
                       "does not carry footers")
    tag_end = 10 + _syncsafe_to_int(data[6:10])
    if tag_end > len(data):
        raise TagError("tag header claims more bytes than the "
                       "file holds -- a truncated or lying tag")
    frames = []
    pos = 10
    while pos + 10 <= tag_end:
        frame_id = data[pos:pos + 4]
        if frame_id == b"\x00\x00\x00\x00":
            break  # padding: the tag's remainder is silence
        if not all(65 <= c <= 90 or 48 <= c <= 57 for c in frame_id):
            break  # not a frame header: treat the rest as padding
        size_bytes = data[pos + 4:pos + 8]
        if major == 4:
            size = _syncsafe_to_int(size_bytes)
        else:
            size = int.from_bytes(size_bytes, "big")
        frame_flags = data[pos + 8:pos + 10]
        end = pos + 10 + size
        if end > tag_end:
            raise TagError(
                f"frame {frame_id!r} overruns the tag -- a "
                f"truncated or lying frame")
        frames.append((frame_id.decode("ascii"), frame_flags,
                       bytes(data[pos + 10:end])))
        pos = end
    return {"version": major, "frames": frames, "tag_end": tag_end,
            "audio": bytes(data[tag_end:])}


def audio_bytes(path):
    """The file's audio body: every byte after its ID3v2 tag.

    The stamp's honesty check rides on this: a delivered file
    and its attested twin differ in their tags and must agree
    here exactly.
    """
    return parse_tag(Path(path).read_bytes())["audio"]


# ---------------------------------------------------------------------
# Text frames: building and reading the house's own.
# ---------------------------------------------------------------------

def _text_payload(text):
    """A plain text frame's payload: UTF-8, encoding byte first."""
    return bytes([_TEXT_ENCODING_UTF8]) + text.encode("utf-8")


def _txxx_payload(desc, value):
    """A TXXX payload: encoding, description, NUL, value."""
    return bytes([_TEXT_ENCODING_UTF8]) + desc.encode("utf-8") \
        + b"\x00" + value.encode("utf-8")


def _comm_payload(text):
    """A COMM payload (English, empty description)."""
    return bytes([_TEXT_ENCODING_UTF8]) + b"eng" + b"\x00" \
        + text.encode("utf-8")


def _decode_text(payload):
    """Decode a text payload's string part (after its framing).

    Encoding byte 0 (Latin-1), 1 (UTF-16 with BOM), 2 (UTF-16BE),
    3 (UTF-8) are all read; anything else is refused by name.
    """
    if not payload:
        return ""
    enc = payload[0]
    raw = payload[1:]
    if enc == 0:
        return raw.decode("latin-1")
    if enc == 1:
        return raw.decode("utf-16")
    if enc == 2:
        return raw.decode("utf-16-be")
    if enc == 3:
        return raw.decode("utf-8", "replace")
    raise TagError(f"text encoding byte {enc} is not an ID3 "
                   f"encoding this reader carries")


def _split_txxx(payload):
    """Split a TXXX payload into (description, value)."""
    if not payload:
        return "", ""
    enc = payload[0]
    body = payload[1:]
    if enc in (1, 2):
        # UTF-16 descriptions terminate in a double NUL; the
        # house never writes these, but a foreign TXXX might.
        sep = body.find(b"\x00\x00")
        if sep < 0:
            return _decode_text(payload), ""
        desc = _decode_text(bytes([enc]) + body[:sep + 1])
        value = _decode_text(bytes([enc]) + body[sep + 2:])
        return desc, value
    # Latin-1 and UTF-8 both terminate the description in one NUL.
    sep = body.find(b"\x00")
    if sep < 0:
        return _decode_text(payload), ""
    codec = "utf-8" if enc == 3 else "latin-1"
    return (body[:sep].decode(codec, "replace"),
            body[sep + 1:].decode(codec, "replace"))


def _frame_desc(frame_id, payload):
    """A frame's TXXX/COMM description (None when it has none)."""
    if frame_id == "TXXX":
        return _split_txxx(payload)[0]
    if frame_id == "COMM":
        return _comm_desc(payload)
    return None


def _comm_desc(payload):
    """A COMM frame's description (after encoding + language)."""
    if len(payload) < 4:
        return ""
    enc = payload[0]
    body = payload[4:]
    if enc in (1, 2):
        sep = body.find(b"\x00\x00")
        if sep < 0:
            return _decode_text(bytes([enc]) + body)
        return _decode_text(bytes([enc]) + body[:sep + 1])
    sep = body.find(b"\x00")
    if sep < 0:
        return body.decode("utf-8" if enc == 3 else "latin-1",
                           "replace")
    return body[:sep].decode("utf-8" if enc == 3 else "latin-1",
                             "replace")


def _comm_text(payload):
    """A COMM frame's text (after encoding + language + desc)."""
    if len(payload) < 4:
        return ""
    enc = payload[0]
    body = payload[4:]
    if enc in (1, 2):
        sep = body.find(b"\x00\x00")
        text = body[sep + 2:] if sep >= 0 else body
        return _decode_text(bytes([enc]) + text)
    sep = body.find(b"\x00")
    text = body[sep + 1:] if sep >= 0 else body
    return text.decode("utf-8" if enc == 3 else "latin-1",
                       "replace")


def _is_house_frame(frame_id, payload):
    """True when a frame belongs to this module's stamp.

    MECHANISM: a TXXX is the house's when its description is one
    of the stamp's; a COMM is the house's only when it is the
    Flagpole carrier itself (empty description, the Flagpole as
    its text) -- a stranger's plain comment is foreign and is
    preserved, never eaten by a re-stamp.
    """
    if frame_id == "TXXX":
        return _frame_desc(frame_id, payload) in _HOUSE_DESCS
    if frame_id == "COMM":
        return _comm_desc(payload) == "" \
            and _comm_text(payload) == FLAGPOLE
    return False


def read_stamp(path):
    """Read the house stamp from an MP3's tag ({} when unstamped).

    Returns the stamp's fields by name: proof, status, gate,
    authorship, flagpole (the COMM body), title -- only those
    present. A file with no tag, or a tag with no house frames,
    reads as {}: unstamped is a fact, not an error.
    """
    parsed = parse_tag(Path(path).read_bytes())
    stamp = {}
    title = None
    for frame_id, _flags, payload in parsed["frames"]:
        if frame_id == "TXXX":
            desc, value = _split_txxx(payload)
            if desc == DESC_PROOF:
                stamp["proof"] = value
            elif desc == DESC_STATUS:
                stamp["status"] = value
            elif desc == DESC_GATE:
                stamp["gate"] = value
            elif desc == DESC_AUTHORSHIP:
                stamp["authorship"] = value
        elif frame_id == "COMM" and _comm_desc(payload) == "":
            stamp["flagpole"] = _comm_text(payload)
        elif frame_id == "TIT2":
            title = _decode_text(payload)
    # The stamp's defining mark is its proof frame: a file with
    # a title but no proof ID carries another tool's tag, not
    # this house's stamp, and reads as unstamped.
    if "proof" not in stamp:
        return {}
    if title is not None:
        stamp["title"] = title
    return stamp


# ---------------------------------------------------------------------
# Writing: preserve the foreign, replace the house's, emit v2.4.
# ---------------------------------------------------------------------

def _serialize_frame(frame_id, payload):
    """One ID3v2.4 frame: id, syncsafe size, zero flags, payload."""
    return frame_id.encode("ascii") + _int_to_syncsafe(len(payload)) \
        + b"\x00\x00" + payload


def _check_carriable(frame_id, flags):
    """Refuse foreign frames whose flags this writer can't carry.

    MECHANISM: in both v2.3 and v2.4 the second flag byte marks
    compression and encryption (bits differ in position between
    versions, so both positions are checked). A compressed or
    encrypted payload re-emitted raw would be a lie in bytes;
    grouping bits are harmless identity and are carried.
    """
    if len(flags) >= 2 and flags[1] & 0b10001001:
        raise TagError(
            f"frame {frame_id} carries compression/encryption "
            f"flags this writer refuses to re-emit raw")


def _gate_text(gate):
    """The FAILED gate as one line: every failing check named
    with its measured value against its law."""
    parts = []
    for check in (gate or {}).get("checks", []):
        if not check.get("ok"):
            parts.append(f"{check['check']}: {check.get('value')} "
                         f"(law: {check['law']})")
    return "; ".join(parts)


def stamp_master_tags(path, *, proof_id, status, gate=None,
                      title=None):
    """Stamp a delivered master MP3 with its proof's face.

    MECHANISM: parse the file's tag, drop every house frame,
    carry every foreign frame payload-for-payload, append the
    stamp's frames, and re-emit the whole tag as ID3v2.4 ahead
    of the untouched audio body. SEALED stamps carry the proof
    ID and status; FAILED stamps carry the ID, the FAILED
    status, and the gate's failing checks printed in full --
    the stamp of a failure is its evidence, not its shame.
    Returns the stamp dict written (as read_stamp would read it).
    """
    path = Path(path)
    data = path.read_bytes()
    parsed = parse_tag(data)
    kept = []
    for frame_id, flags, payload in parsed["frames"]:
        if _is_house_frame(frame_id, payload):
            continue
        if frame_id == "TIT2" and title:
            # The stamp owns the title face when a title is
            # given; an untitled stamp leaves a title it finds
            # exactly as it found it.
            continue
        _check_carriable(frame_id, flags)
        kept.append((frame_id, payload))
    frames = list(kept)
    if title:
        frames.append(("TIT2", _text_payload(title)))
    frames.append(("TXXX", _txxx_payload(DESC_AUTHORSHIP,
                                         AUTHORSHIP)))
    frames.append(("TXXX", _txxx_payload(DESC_PROOF, proof_id)))
    frames.append(("TXXX", _txxx_payload(DESC_STATUS, status)))
    if status == "FAILED":
        frames.append(("TXXX", _txxx_payload(
            DESC_GATE, _gate_text(gate) or "FAILED")))
    frames.append(("COMM", _comm_payload(FLAGPOLE)))
    body = b"".join(_serialize_frame(fid, payload)
                    for fid, payload in frames)
    tag = b"ID3" + bytes([4, 0, 0]) + _int_to_syncsafe(len(body)) \
        + body
    path.write_bytes(tag + parsed["audio"])
    return read_stamp(path)


def preserve_attested_copy(path):
    """Preserve a pristine encode as its attested twin.

    MECHANISM: the twin sits beside the delivered file as
    '<stem>.attested<ext>' and is a byte copy of the pre-stamp
    encode -- the body a master proof attests. Law: an absent
    twin is created; a present twin must be byte-identical to
    the file as it now stands, else the copy REFUSES (an earlier
    record attests those bytes; destroying them would break the
    chain to save a disk block). A file already carrying a house
    stamp is not pristine and is refused as a body to preserve.
    Returns the twin's path.
    """
    path = Path(path)
    if read_stamp(path):
        raise TagError(
            f"{path} already carries a house stamp -- it is not "
            f"the pristine encode and cannot be preserved as an "
            f"attested body")
    twin = path.with_name(path.stem + ".attested" + path.suffix)
    if twin.exists():
        if twin.read_bytes() != path.read_bytes():
            raise TagError(
                f"attested twin {twin} already stands with "
                f"different bytes -- an earlier proof attests "
                f"them; refusing to overwrite the attested body")
        return twin
    shutil.copyfile(path, twin)
    return twin
