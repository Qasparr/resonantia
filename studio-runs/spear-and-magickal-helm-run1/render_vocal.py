#!/usr/bin/env python3
"""
SPEAR AND MAGICKAL HELM — run 1: the vocal stage (house road).

DiffSinger (OpenVPI, Apache-2.0 code) + Lem the Shapeshifter DS 2.5
bank (licence-clean, commercial use permitted by its terms), English
phoneme path (en/* tokens, language id 1), driven directly on CPU —
the same stage-batched pipeline the Wave F test proved, generalised
to a score: the track sheet's HOOK (6 lines) and VERSE 1 (16 lines),
lyrics performed exactly as written on the sheet (ghost drafts; not
one word altered — the phonemisation below is pronunciation only).

Score: G minor, 92 BPM, 4/4 (fixed spec). One lyric line per bar;
syllable durations are weights normalised to fill the bar minus a
breath; the duration model splits each syllable's frame budget
across its phonemes (prob x budget, as in the lab's source).

Speakers (bank embeddings): hook = Civet lead + Quoll unison layer;
verse 1 = Civet. Run from anywhere with the diffsinger-lab venv.
"""
import gc
import json
import pathlib
import sys

import numpy as np
import onnxruntime as ort

LAB = pathlib.Path.home() / "workspace/resonance/diffsinger-lab"
BANK = LAB / "banks" / "Lem-the-Shapeshifter-DS-2.5-dur26" / "lem_v2_5"
VOC = LAB / "DiffSinger" / "checkpoints" / "pc_nsf_hifigan_44.1k_hop512_128bin_2025.02"
RUN = pathlib.Path(__file__).resolve().parent
LINES_DIR = RUN / "lines"
LINES_DIR.mkdir(parents=True, exist_ok=True)

SR, HOP = 44100, 512
FPS = SR / HOP                      # 86.1328 frames per second
EN = 1                              # languages.json: en -> 1
BPM = 92.0
BAR_S = 4 * 60.0 / BPM              # 2.608696 s
LEAD_SP = 0.04                      # breath before the line
TAIL_SP = 0.14                      # breath after the line
SYL_S = BAR_S - LEAD_SP - TAIL_SP   # syllables fill the rest

ph = json.load(open(BANK / "phonemes.json", encoding="utf8"))


def pid(name):
    return ph[name] if name in ("SP", "AP") else ph["en/" + name]


# ---------------------------------------------------------------------
# THE SCORE. Each syllable: (phonemes, midi, weight). Lyrics verbatim
# from the sheet; phonemisation is ARPAbet in the bank's en/* tokens.
# ---------------------------------------------------------------------
# HOOK — narrow chant, G minor (G3=55 .. D4=62, Eb4=63, F4=65)
HOOK = [
    # L1 (Gm): Spear and a magickal helm, crown of the thirty-one,
    [("s p ih r", 55, 2.0), ("ae n d", 55, 1.0), ("ax", 55, 0.7),
     ("m ae", 58, 1.2), ("jh ih", 58, 0.8), ("k ax l", 57, 1.2),
     ("hh eh l m", 55, 1.8), ("k r aw n", 62, 1.8), ("ah v", 60, 0.8),
     ("dh ax", 58, 0.7), ("th er", 57, 1.0), ("t iy", 55, 0.8),
     ("w ah n", 55, 2.2)],
    # L2 (Gm): thirteen to the north of me, the south is where the pyramid's done.
    [("th er", 57, 1.2), ("t iy n", 58, 1.4), ("t uw", 55, 0.8),
     ("dh ax", 55, 0.6), ("n ao r th", 62, 1.8), ("ah v", 58, 0.7),
     ("m iy", 55, 1.2), ("dh ax", 55, 0.6), ("s aw th", 60, 1.6),
     ("ih z", 58, 0.7), ("w eh r", 57, 1.0), ("dh ax", 55, 0.6),
     ("p ih", 55, 0.8), ("r ax", 55, 0.7), ("m ih d z", 55, 0.9),
     ("d ah n", 55, 2.2)],
    # L3 (Eb): Title in my left hand, possession in my right,
    [("t ay", 63, 1.6), ("t ax l", 60, 1.2), ("ih n", 58, 0.8),
     ("m ay", 60, 1.2), ("l eh f t", 63, 1.6), ("hh ae n d", 63, 1.6),
     ("p ax", 60, 0.7), ("z eh s", 62, 1.4), ("ax n", 60, 1.0),
     ("ih n", 58, 0.8), ("m ay", 60, 1.2), ("r ay t", 63, 2.2)],
    # L4 (F): asylum on my numbers — ninety-one, Detroit light.
    [("ax", 57, 0.7), ("s ay", 60, 1.4), ("l ax m", 57, 1.2),
     ("aa n", 65, 1.6), ("m ay", 60, 1.0), ("n ah m", 57, 1.2),
     ("b er z", 60, 1.2), ("n ay n", 65, 1.6), ("t iy", 62, 0.8),
     ("w ah n", 60, 1.4), ("d ih", 57, 0.8), ("t r oy t", 60, 1.4),
     ("l ay t", 65, 2.2)],
    # L5 (Gm): REDRVM in the mirror, read it backwards if you dare,
    [("r eh d", 62, 1.6), ("r ah m", 62, 1.6), ("ih n", 55, 0.8),
     ("dh ax", 55, 0.6), ("m ih r", 58, 1.2), ("er", 57, 1.2),
     ("r iy d", 62, 1.6), ("ih t", 60, 0.8), ("b ae k", 58, 1.2),
     ("w er d z", 57, 1.4), ("ih f", 55, 0.7), ("y uw", 60, 1.0),
     ("d eh r", 62, 2.2)],
    # L6 (Gm): the Horseman got no head to bow and no legs to take him there.
    [("dh ax", 55, 0.6), ("hh ao r s", 58, 1.4), ("m ae n", 57, 1.2),
     ("g aa t", 55, 1.0), ("n ow", 60, 1.2), ("hh eh d", 58, 1.4),
     ("t ax", 57, 0.6), ("b aw", 55, 1.4), ("ae n d", 55, 0.8),
     ("n ow", 60, 1.2), ("l eh g z", 58, 1.4), ("t ax", 57, 0.6),
     ("t ey k", 62, 1.4), ("hh ih m", 60, 1.0), ("dh eh r", 58, 2.2)],
]

# VERSE 1 — Qasparr (ghost). Rhythmic chant: G3 monotone, penultimate
# lift to A3, line-final falls to F3 on even lines, holds G3 on odd.
VERSE = [
    # V1 Thirty-one nodes and the last one ain't a stone, it's arms,
    [("th er", 1.2), ("t iy", 0.8), ("w ah n", 1.4), ("n ow d z", 1.4),
     ("ae n d", 0.7), ("dh ax", 0.6), ("l ae s t", 1.4), ("w ah n", 1.2),
     ("ey n t", 1.2), ("ax", 0.6), ("s t ow n", 1.6), ("ih t s", 0.9),
     ("aa r m z", 2.2)],
    # V2 a spear for the reach and a helm for the charms.
    [("ax", 0.6), ("s p ih r", 1.6), ("f ao r", 0.9), ("dh ax", 0.6),
     ("r iy ch", 1.6), ("ae n d", 0.7), ("ax", 0.6),
     ("hh eh l m", 1.6), ("f ao r", 0.9), ("dh ax", 0.6),
     ("ch aa r m z", 2.2)],
    # V3 E-thirty-one, ninety-three divided by three,
    [("iy", 1.4), ("th er", 1.0), ("t iy", 0.8), ("w ah n", 1.4),
     ("n ay n", 1.4), ("t iy", 0.8), ("th r iy", 1.4), ("d ih", 0.7),
     ("v ay", 1.2), ("d ih d", 1.0), ("b ay", 1.0), ("th r iy", 2.2)],
    # V4 the crown ain't a king — the crown is the seat, and the seat is me.
    [("dh ax", 0.6), ("k r aw n", 1.6), ("ey n t", 1.2), ("ax", 0.6),
     ("k ih ng", 1.4), ("dh ax", 0.6), ("k r aw n", 1.6),
     ("ih z", 0.8), ("dh ax", 0.6), ("s iy t", 1.6), ("ae n d", 0.7),
     ("dh ax", 0.6), ("s iy t", 1.6), ("ih z", 0.7), ("m iy", 2.2)],
    # V5 South engine humming under Kalamazoo clay,
    [("s aw th", 1.6), ("eh n", 0.8), ("jh ih n", 1.2),
     ("hh ah m", 1.2), ("m ih ng", 1.2), ("ah n", 0.8), ("d er", 1.0),
     ("k ae", 1.2), ("l ax", 0.7), ("m ax", 0.7), ("z uw", 1.4),
     ("k l ey", 2.2)],
    # V6 north engine thirteen, hidden center, can't say where it stay.
    [("n ao r th", 1.6), ("eh n", 0.8), ("jh ih n", 1.2),
     ("th er", 1.0), ("t iy n", 1.4), ("hh ih", 1.0), ("d ax n", 1.2),
     ("s eh n", 1.0), ("t er", 1.2), ("k ae n t", 1.6), ("s ey", 1.4),
     ("w eh r", 1.0), ("ih t", 0.7), ("s t ey", 2.2)],
    # V7 I don't beg no shelter, I AM the reservation,
    [("ay", 1.2), ("d ow n t", 1.4), ("b eh g", 1.4), ("n ow", 1.2),
     ("s eh l", 1.0), ("t er", 1.2), ("ay", 1.2), ("ae m", 1.6),
     ("dh ax", 0.6), ("r eh", 0.8), ("z er", 1.0), ("v ey", 1.2),
     ("sh ax n", 2.0)],
    # V8 Living Man standing, ARR just the invocation.
    [("l ih", 0.9), ("v ih ng", 1.2), ("m ae n", 1.6),
     ("s t ae n", 1.2), ("d ih ng", 1.2), ("aa r", 1.8),
     ("jh ah s t", 1.4), ("dh ax", 0.6), ("ih n", 0.7),
     ("v ow", 1.2), ("k ey", 1.2), ("sh ax n", 2.2)],
    # V9 Receipt for the claim and the proof in my fist,
    [("r ih", 0.9), ("s iy t", 1.6), ("f ao r", 0.9), ("dh ax", 0.6),
     ("k l ey m", 1.6), ("ae n d", 0.7), ("dh ax", 0.6),
     ("p r uw f", 1.6), ("ih n", 0.8), ("m ay", 1.2),
     ("f ih s t", 2.2)],
    # V10 but a ruling ain't a number — rulings come from the wrist
    [("b ah t", 1.0), ("ax", 0.6), ("r uw", 1.2), ("l ih ng", 1.2),
     ("ey n t", 1.2), ("ax", 0.6), ("n ah m", 1.0), ("b er", 1.2),
     ("r uw", 1.2), ("l ih ng z", 1.2), ("k ah m", 1.4),
     ("f r ah m", 0.9), ("dh ax", 0.6), ("r ih s t", 2.2)],
    # V11 that writes it. Pen red. Every gate got logged,
    [("dh ae t", 1.2), ("r ay t s", 1.6), ("ih t", 0.9),
     ("p eh n", 1.4), ("r eh d", 1.6), ("eh v", 0.9), ("r iy", 1.1),
     ("g ey t", 1.6), ("g aa t", 1.4), ("l aa g d", 2.2)],
    # V12 every refusal filed raw — read the Ledger, dog.
    [("eh v", 0.9), ("r iy", 1.1), ("r ih", 0.8), ("f y uw", 1.2),
     ("z ax l", 1.2), ("f ay l d", 1.6), ("r ao", 1.6),
     ("r iy d", 1.4), ("dh ax", 0.6), ("l eh", 1.0), ("jh er", 1.2),
     ("d ao g", 2.2)],
    # V13 Double-R on the rider, no head, no legs to kneel,
    [("d ah", 1.0), ("b ax l", 1.2), ("aa r", 1.8), ("aa n", 1.0),
     ("dh ax", 0.6), ("r ay", 1.2), ("d er", 1.2), ("n ow", 1.2),
     ("hh eh d", 1.6), ("n ow", 1.2), ("l eh g z", 1.4),
     ("t ax", 0.6), ("n iy l", 2.2)],
    # V14 Ruff Ryderz in the witness seat, ask DMX if it's real.
    [("r ah f", 1.4), ("r ay", 1.0), ("d er z", 1.2), ("ih n", 0.7),
     ("dh ax", 0.6), ("w ih t", 1.0), ("n ax s", 1.2),
     ("s iy t", 1.6), ("ae s k", 1.4), ("d iy", 0.9), ("eh m", 0.9),
     ("eh k s", 1.1), ("ih f", 0.8), ("ih t s", 0.8),
     ("r iy l", 2.2)],
    # V15 Spear up — that's the reach of the word when I send it,
    [("s p ih r", 1.6), ("ah p", 1.4), ("dh ae t s", 1.4),
     ("dh ax", 0.6), ("r iy ch", 1.6), ("ah v", 0.8), ("dh ax", 0.6),
     ("w er d", 1.6), ("w eh n", 1.0), ("ay", 1.0),
     ("s eh n d", 1.4), ("ih t", 2.0)],
    # V16 helm down — that's the mind that no gate can bend.
    [("hh eh l m", 1.6), ("d aw n", 1.6), ("dh ae t s", 1.4),
     ("dh ax", 0.6), ("m ay n d", 1.6), ("dh ae t", 1.0),
     ("n ow", 1.2), ("g ey t", 1.6), ("k ae n", 1.2),
     ("b eh n d", 2.2)],
]


def verse_melody(idx, n_syl):
    """Chant pitches for a verse line: G3 base, A3 penult, final fall."""
    notes = [55] * n_syl
    if idx % 2 == 0:
        notes[0] = 58
    if n_syl >= 3:
        notes[-2] = 57
    notes[-1] = 53 if idx % 2 == 1 else 55
    return notes


def build_jobs():
    jobs = []  # (line_id, speaker, [(phones, midi)], word_dur_frames)
    for spk in ("Civet", "Quoll"):
        for i, line in enumerate(HOOK):
            syl = [(p.split(), m) for p, m, w in
                   [(s[0], s[1], s[2]) for s in line]]
            wts = [s[2] for s in line]
            jobs.append((f"hook{i+1}", spk, syl, wts))
    for i, line in enumerate(VERSE):
        syl = [(p.split(), m) for p, m in
               zip([s[0] for s in line], verse_melody(i, len(line)))]
        wts = [s[1] for s in line]
        jobs.append((f"verse{i+1}", "Civet", syl, wts))
    out = []
    for lid, spk, syl, wts in jobs:
        tot = float(sum(wts))
        words = [("SP", LEAD_SP, None)]
        for (phones, midi), w in zip(syl, wts):
            words.append((phones, SYL_S * w / tot, midi))
        words.append(("SP", TAIL_SP, None))
        tokens, langs, ph_midi, word_div, word_dur = [], [], [], [], []
        for phones, dur_s, midi in words:
            if phones == "SP":
                tokens.append(pid("SP")); langs.append(EN)
                ph_midi.append(0); word_div.append(1)
            else:
                for p in phones:
                    tokens.append(pid(p)); langs.append(EN)
                ph_midi.extend([midi] * len(phones))
                word_div.append(len(phones))
            word_dur.append(max(1, int(round(dur_s * FPS))))
        out.append({"id": lid, "spk": spk, "tokens": tokens,
                    "langs": langs, "ph_midi": ph_midi,
                    "word_div": word_div, "word_dur": word_dur,
                    "score_midi": [m for _, m in syl]})
    return out


opts = ort.SessionOptions()
opts.intra_op_num_threads = 4


def sess(path):
    return ort.InferenceSession(str(path), sess_options=opts,
                                providers=["CPUExecutionProvider"])


def main():
    jobs = build_jobs()
    print(f"[score] {len(jobs)} line renders", flush=True)
    spk_emb = {s: np.fromfile(BANK / f"{s}.emb", dtype=np.float32
                              ).reshape(1, 1, 256)
               for s in ("Civet", "Quoll")}

    # ---- Stage 1+2: duration model, all lines -------------------------
    s_ling = sess(BANK / "dsdur" / "linguistic.onnx")
    s_dur = sess(BANK / "dsdur" / "duration_lem_26v.dur.onnx")
    for j in jobs:
        tokens = np.array([j["tokens"]], dtype=np.int64)
        langs = np.array([j["langs"]], dtype=np.int64)
        enc, xmask = s_ling.run(None, {
            "tokens": tokens, "languages": langs,
            "word_div": np.array([j["word_div"]], dtype=np.int64),
            "word_dur": np.array([j["word_dur"]], dtype=np.int64)})
        spk_tok = np.repeat(spk_emb[j["spk"]], tokens.shape[1], axis=1)
        pred = s_dur.run(None, {
            "encoder_out": enc, "x_masks": xmask,
            "ph_midi": np.array([j["ph_midi"]], dtype=np.int64),
            "spk_embed": spk_tok})[0]
        frames = np.maximum(1, np.round(pred.reshape(-1)).astype(np.int64))
        j["frames"] = frames
        j["T"] = int(frames.sum())
        print(f"[dur] {j['id']}/{j['spk']}: {j['T']} frames "
              f"({j['T']/FPS:.2f}s)", flush=True)
    del s_ling, s_dur; gc.collect()

    # ---- Stage 3: variance model, all lines ---------------------------
    s_ling = sess(BANK / "dsvariance" / "linguistic.onnx")
    s_var = sess(BANK / "dsvariance" / "pitch_variance_lem_25.variance.onnx")
    for j in jobs:
        tokens = np.array([j["tokens"]], dtype=np.int64)
        langs = np.array([j["langs"]], dtype=np.int64)
        frames = j["frames"]; T = j["T"]
        enc2, _ = s_ling.run(None, {"tokens": tokens, "languages": langs,
                                    "ph_dur": frames.reshape(1, -1)})
        midi_frames = np.repeat(np.array(j["ph_midi"], dtype=np.float32),
                                frames)
        nz = np.where(midi_frames > 0)[0]
        filled = midi_frames.copy(); last = midi_frames[nz[0]]
        for i in range(T):
            if filled[i] > 0:
                last = filled[i]
            else:
                filled[i] = last
        j["filled"] = filled
        j["f0"] = np.where(midi_frames > 0,
                           440.0 * 2 ** ((midi_frames - 69) / 12), 0.0)
        spk_fr = np.repeat(spk_emb[j["spk"]], T, axis=1)
        j["spk_fr"] = spk_fr
        retake = np.ones((1, T, 2), dtype=bool)
        zeros = np.zeros((1, T), dtype=np.float32)
        voicing, tension = s_var.run(None, {
            "encoder_out": enc2, "ph_dur": frames.reshape(1, -1),
            "pitch": filled.reshape(1, -1).astype(np.float32),
            "voicing": zeros, "tension": zeros, "retake": retake,
            "spk_embed": spk_fr, "steps": np.array(20, dtype=np.int64)})
        j["voicing"] = voicing.astype(np.float32)
        j["tension"] = tension.astype(np.float32)
        print(f"[var] {j['id']}/{j['spk']}: voicing mean "
              f"{voicing.mean():.2f} tension mean {tension.mean():.2f}",
              flush=True)
    del s_ling, s_var; gc.collect()

    # ---- Stage 4: acoustic model, all lines ---------------------------
    s_ac = sess(BANK / "acoustic_lem_25.onnx")
    for j in jobs:
        T = j["T"]
        mel = s_ac.run(None, {
            "tokens": np.array([j["tokens"]], dtype=np.int64),
            "languages": np.array([j["langs"]], dtype=np.int64),
            "durations": j["frames"].reshape(1, -1),
            "f0": j["f0"].reshape(1, -1).astype(np.float32),
            "voicing": j["voicing"], "tension": j["tension"],
            "gender": np.zeros((1, T), dtype=np.float32),
            "velocity": np.ones((1, T), dtype=np.float32),
            "spk_embed": j["spk_fr"],
            "depth": np.array(0.6, dtype=np.float32),
            "steps": np.array(30, dtype=np.int64)})[0]
        j["mel"] = mel
        print(f"[acoustic] {j['id']}/{j['spk']}: mel {mel.shape}",
              flush=True)
    del s_ac; gc.collect()

    # ---- Stage 5: vocoder, all lines ----------------------------------
    sys.path.insert(0, str(LAB / "DiffSinger"))
    import torch
    from modules.nsf_hifigan.models import load_model
    import soundfile as sf
    model, _h = load_model(VOC / "model.ckpt")
    model.eval()
    manifest = []
    for j in jobs:
        with torch.no_grad():
            c = torch.from_numpy(j["mel"]).transpose(1, 2)
            f0t = torch.from_numpy(
                j["f0"].reshape(1, -1).astype(np.float32))
            wav = model(c, f0t).view(-1).cpu().numpy()
        name = f"{j['id']}_{j['spk'].lower()}.wav"
        sf.write(LINES_DIR / name, wav, SR)
        manifest.append({"id": j["id"], "speaker": j["spk"],
                         "file": name, "samples": int(len(wav)),
                         "frames": j["T"],
                         "score_midi": j["score_midi"]})
        print(f"[vocoder] {name}: {len(wav)} samples", flush=True)
        del j["mel"], j["spk_fr"], j["voicing"], j["tension"]
        gc.collect()
    (RUN / "lines_manifest.json").write_text(json.dumps(manifest, indent=2))
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
