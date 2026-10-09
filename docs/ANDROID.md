# RESONANCE on Android — The Field Kit

**Authorship:** Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
**Date:** 2026-10-05 (Monday)
**Method:** Scientific Illuminism. 93.

> "Every man, woman, and child is a star."

## The verdict of the audit

On 2026-10-05 the engine was audited for phone-survival, and the audit
came back clean:

- **Zero platform-sensitive imports.** No `sounddevice`, no `pyaudio`, no
  `pygame`, no `tkinter` — nothing that needs a desktop audio stack or a
  windowing system. Verified by grep over the whole `resonance/` tree.
- **One runtime dependency: numpy.** And numpy installs in Termux via
  pip. That is the entire portability story.
- **File-rendering, not live audio.** The engine writes WAV files; it
  never demands a sound card. A phone plays files just fine.

**MECHANISM:** Termux gives the phone a real Linux userspace — Python,
pip, and a filesystem.
**DOCTRINE:** an engine that renders to files is already portable; the
"port" is mostly refusing to add desktop-only dependencies. The
discipline paid off here.

Both pillars below were verified rendering on 2026-10-05 (build host,
numpy + stdlib only): the 808 CLI wrote a 4-bar 140 BPM WAV (1.2 MB),
and `binaural_beat(10.0, carrier=528.0)` wrote a 5-second stereo WAV.
The phone run is the remaining verification — yours to perform.

## Setup (Termux)

```sh
# MECHANISM: install Python and numpy — the whole dependency tree.
# DOCTRINE: Termux is a real Linux userspace, not a toy. Treat it like one.
pkg install -y python git
pip install numpy

# MECHANISM: fetch the engine. No build step — it is pure Python.
git clone https://github.com/Qasparr/resonantia
cd resonance
```

## Render beats (808)

```sh
# MECHANISM: the synth CLI renders the built-in pattern to a stereo WAV.
#   --bpm, --bars, --swing, --sr, -o all do what they say.
# DOCTRINE: files, not streams — the phone's player handles playback,
#   the engine handles synthesis. Separation of concerns, pocket-sized.
PYTHONPATH=. python3 -m resonance.synth.cli --bpm 140 --bars 4 -o beat.wav
```

## Render entrainment (binaural)

```sh
# MECHANISM: 10 Hz alpha riding a 528 Hz carrier, 60 seconds, stereo WAV.
# DOCTRINE: the beat is perceived, not present — the interference happens
#   in the auditory pathway. The docstring says it; the physics agrees.
PYTHONPATH=. python3 -c "
from resonance.binaural.generator import binaural_beat
from resonance.core.io import write_wav
audio = binaural_beat(10.0, carrier=528.0, duration=60.0)
write_wav('alpha-528.wav', audio, 44100)
print('wrote alpha-528.wav')
"
```

## Play it

```sh
# MECHANISM: Termux plays audio files through the Android media stack.
#   Requires the Termux:API app alongside Termux.
pkg install -y termux-api
termux-media-player play beat.wav
```

## Honest limits

- **`resonance/burn/`** orchestrates desktop system tools (ffmpeg,
  growisofs, dvdauthor) — not a phone module. It stays home.
- **The AI wing's local guests** (MusicGen, Whisper via torch) want a GPU
  and gigabytes of weights — not a phone workload. The Gemini cloud guest
  works anywhere with a key and a network.
- **The render-job API** (`api = ["fastapi", "uvicorn"]`) *does* run in
  Termux — uvicorn binds loopback, and the phone's browser becomes the
  studio UI. Unverified on-device; documented as the next experiment.
- **This is v0.5.0, the Field Kit** — Termux-first, CLI-driven, file-based.
  The native APK (Chaquopy or Kivy wrapper) is v0.6.0 and honestly needs
  a build machine with the Android SDK — later, when the means exist.

## Roadmap

- [x] v0.5.0 — The Field Kit: audit + this doc (2026-10-05)
- [ ] v0.5.1 — John's on-device verification (Termux render + playback)
- [ ] v0.6.0 — Native APK wrapper (needs Android SDK build machine)

*"Live, Love, and let Love, Live." — 93.*
