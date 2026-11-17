# RUN REPORT — THE 808 TOOLBOX DEMO KIT

Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
All Rights Reserved, Without Prejudice. XVI day of November, Anno
V:xii e.n. (2026 e.v.). Method of Science, Aim of Religion.

**Label:** "808" names the TR-808 sound family. Every voice in this
folder is synthesized in-house from oscillators, noise, and
envelopes by `resonance/studio/eightoeight.py`. Nothing samples
Roland's machine or plays its recordings.

**Hypothesis.** The classic voice family can be struck from first
principles with the house kit (stdlib + numpy at the studio rate),
each voice measuring as its recipe claims, and a kick can be tuned
by a seat of the Double-Letter Dial under the stated placement rule.

**Method.** `python3 -m resonance.studio.eightoeight kit` rendered
every registered voice at default parameters plus three dial-tuned
kicks (VV, LL, OO). Each file was re-read from disk and measured on
this side before its numbers entered `kit_manifest.json`: duration,
peak, RMS, and for the kicks the realized fundamental track
(autocorrelation — attack read through a 20 ms window as the
window's average pitch, tail through the last 250 ms). All files
are peak-set to 0.89 (−1.01 dBFS); the factor applied to each is
confessed in the manifest (the high-passed closed hat's natural
body is quiet and took ×4.67 of gain — printed, not hidden).

**Observation.** The dial kicks land on their seats: VV's tail
reads 44.3 Hz against the placed 44 (Δ +0.3), LL's 48.3 against 48
(Δ +0.3), OO's 60.0 against 60 (Δ 0.0). The default kick settles at
50.3 against its 50 Hz fundamental. Attack readings cluster at
116–122 Hz — the 20 ms window's average of the 160 → fundamental
sweep, the grain stated in the module. The dial data was read from
the repo seat (`resonance/studio/data/dial-table.json`); no
fallback was needed.

**Result.** Fourteen WAVs stand struck and measured in this folder
(manifest: `kit_manifest.json`). The kit's renders are stamped into
the proof ledger as instrumental proofs; the proof IDs and the
chain's verification stand in the build report that delivered this
run. The founder's ear verdict is not pre-claimed — as a
synthesizer, the toolbox is judged when he hears it.

93 — Live, Love, and let Love, Live.
