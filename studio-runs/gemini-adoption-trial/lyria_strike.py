#!/usr/bin/env python3
# ============================================================================
# "Do what thou wilt shall be the whole of the Law."
#
# LYRIA STRIKE — ONE adoption-trial render of NIGHT SUN through the house
# Gemini credential (connector: custom.gemini), under the founder's adoption
# ruling of 2026-11-10: "Let's try to adopt."
#
# X day of November, Dies Martis, Sol in Scorpio, Anno V:xii e.n. (2026 e.v.)
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
# (Greek, -ARR, All Rights Reserved, Without Prejudice).
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# DOCTRINE of this instrument:
#   * ONE strike. A quota wall (HTTP 429 / limit 0) is a COMPLETE ANSWER,
#     not an obstacle to route around: no retry, no model-hopping, no
#     billing change. Billing is the founder's money decision, untaken
#     since 2026-10-26, and this script cannot take it for him.
#   * The credential is never seen here. The vault-backed caller pattern
#     from bin/gemini_call.py is mirrored exactly: the API key reaches the
#     request as an hsurr:* surrogate that authd swaps on approved egress,
#     addressed to generativelanguage.googleapis.com ONLY. The built URL
#     (which carries the surrogate) is never printed, logged, or saved.
#   * Whatever the model returns is recorded raw in the manifest — model,
#     finish reason, usage metadata, per-part inventory — minus any
#     credential material, of which this process holds none.
#
# MECHANISM:
#   prompt.txt --(generateContent body)--> POST v1beta/models/<model>
#   response parts --(inlineData, audio/*)--> concatenated in order to
#   strike.<ext>; every part inventoried (kind, mime, bytes, sha256) in
#   manifest.json, success or failure alike. The receipt is written either
#   way: a wall is a finding, and findings are filed, not vanished.
#   generationConfig is deliberately omitted: the text caller's
#   maxOutputTokens is a text-model control, and an unforced body is the
#   smallest honest request to an audio model.
#
# FOUR-ELEMENT TEST (Inputs / Processes / Outputs / Tolerances):
#   Inputs:    prompt.txt (spec + Verses I–II verbatim from the sheet),
#              one full-song Lyria model id (default lyria-3.5).
#   Processes: one POST; part inventory; audio concatenation in part order.
#   Outputs:   strike.<ext> (only if audio returns), manifest.json (always).
#   Tolerances: exit 0 iff audio saved; exit 2 = HTTP wall (reported, not
#              retried); exit 3 = credential error. Timeout 300 s.
# ============================================================================
import argparse, base64, datetime, hashlib, json, os, sys, urllib.request

# The skill-scaffold template path exists on the main host; the setup skill's
# own bin/ exists everywhere the skill is installed. Try both, in order —
# the same discipline as bin/gemini_call.py, whose pattern this mirrors.
for _cred_path in ("/opt/muse/skills/custom-connector-setup/templates/skill/bin",
                   "/opt/muse/skills/custom-connector-setup/bin"):
    if _cred_path not in sys.path:
        sys.path.insert(0, _cred_path)
    try:
        from dynamic_credentials import (  # noqa: E402,F401
            url_with_surrogate_query_param, read_json_response,
            DynamicCredentialError)
        break
    except ModuleNotFoundError:
        continue
else:
    raise SystemExit("dynamic_credentials module not found on any known path")

API = "https://generativelanguage.googleapis.com/v1beta/"
CREDENTIAL = "custom.gemini"
ALLOWED_HOSTS = ["generativelanguage.googleapis.com"]

EXT_BY_MIME = {
    "audio/wav": "wav", "audio/x-wav": "wav", "audio/mpeg": "mp3",
    "audio/mp3": "mp3", "audio/ogg": "ogg", "audio/flac": "flac",
    "audio/aac": "aac", "audio/L16": "pcm",
}


def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="lyria-3.5",
                    help="full-song Lyria model (default lyria-3.5)")
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    with open(args.prompt_file, "rb") as f:
        prompt_bytes = f.read()
    prompt = prompt_bytes.decode("utf-8")

    manifest = {
        "trial": "gemini-adoption-trial — NIGHT SUN, one Lyria strike",
        "ruling": "founder, 2026-11-10: 'Let's try to adopt.'",
        "model": args.model,
        "host": ALLOWED_HOSTS[0],
        "prompt_file": os.path.basename(args.prompt_file),
        "prompt_sha256": sha256_hex(prompt_bytes),
        "prompt_chars": len(prompt),
        "struck_at_utc": datetime.datetime.now(datetime.timezone.utc)
                           .isoformat(),
        "http_status": None, "finish_reason": None,
        "usage_metadata": None, "parts": [], "audio_file": None,
        "error": None,
    }

    def file_manifest():
        # The receipt is written on EVERY path — success, wall, or error.
        with open(os.path.join(args.out_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)

    body = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        url = url_with_surrogate_query_param(
            API + "models/" + args.model + ":generateContent",
            CREDENTIAL, allowed_hosts=ALLOWED_HOSTS)
    except DynamicCredentialError as e:
        manifest["error"] = "credential error: %s" % e
        file_manifest()
        print("CREDENTIAL ERROR:", e, file=sys.stderr)
        print("93 — Live, Love, and let Love, Live.")
        return 3

    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            manifest["http_status"] = r.status
            resp = read_json_response(r)
    except urllib.error.HTTPError as e:
        # A wall is a complete answer. Record it raw; do not retry.
        err_body = e.read().decode("utf-8", "replace")
        manifest["http_status"] = e.code
        manifest["error"] = err_body
        file_manifest()
        print("HTTP ERROR", e.code, err_body[:800], file=sys.stderr)
        print("93 — Live, Love, and let Love, Live.")
        return 2
    except Exception as e:  # transport failure — also recorded, not retried
        manifest["error"] = "transport: %r" % e
        file_manifest()
        print("TRANSPORT ERROR:", e, file=sys.stderr)
        print("93 — Live, Love, and let Love, Live.")
        return 2

    manifest["usage_metadata"] = resp.get("usageMetadata")
    cand = (resp.get("candidates") or [{}])[0]
    manifest["finish_reason"] = cand.get("finishReason")
    if "promptFeedback" in resp:
        manifest["prompt_feedback"] = resp["promptFeedback"]

    audio_chunks, audio_mime = [], None
    for i, p in enumerate(cand.get("content", {}).get("parts", [])):
        entry = {"index": i}
        if "inlineData" in p:
            data = base64.b64decode(p["inlineData"].get("data", ""))
            mime = p["inlineData"].get("mimeType", "")
            entry.update(kind="inlineData", mime_type=mime,
                         bytes=len(data), sha256=sha256_hex(data))
            if mime.startswith("audio/"):
                audio_chunks.append(data)
                audio_mime = audio_mime or mime
            else:
                # Non-audio inline payload: kept, named by index, declared.
                fn = "part-%d.%s" % (i, mime.split("/")[-1] or "bin")
                with open(os.path.join(args.out_dir, fn), "wb") as f:
                    f.write(data)
                entry["saved_as"] = fn
        elif "text" in p:
            entry.update(kind="text", chars=len(p["text"]),
                         sha256=sha256_hex(p["text"].encode()))
            with open(os.path.join(args.out_dir, "part-%d.txt" % i), "w") as f:
                f.write(p["text"])
            entry["saved_as"] = "part-%d.txt" % i
        else:
            entry.update(kind=sorted(p.keys())[0] if p else "empty")
        manifest["parts"].append(entry)

    if audio_chunks:
        audio = b"".join(audio_chunks)
        fn = "strike." + EXT_BY_MIME.get(audio_mime, "bin")
        with open(os.path.join(args.out_dir, fn), "wb") as f:
            f.write(audio)
        manifest["audio_file"] = {
            "name": fn, "mime_type": audio_mime, "bytes": len(audio),
            "sha256": sha256_hex(audio), "chunks": len(audio_chunks),
        }
        print("AUDIO SAVED -> %s (%d bytes, %s)"
              % (fn, len(audio), audio_mime))
    else:
        print("NO AUDIO in response. finishReason:",
              manifest["finish_reason"])
    file_manifest()
    print("manifest.json written.")
    print("93 — Live, Love, and let Love, Live.")
    return 0 if audio_chunks else 2


if __name__ == "__main__":
    sys.exit(main())
