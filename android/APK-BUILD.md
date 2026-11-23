# APK-BUILD.md — the EQVILLIBBRRIVMM APK, struck by hand

> Stage 5 of the Resonantia build, 22 November 2026. The deliverable:
> a working, direct-install Android APK of the founder's
> EQVILLIBBRRIVMM suite — no Play Store anywhere in the chain, no
> Gradle, no network. Signed, aligned, sideloadable by tap-install
> from a downloaded file.
>
> Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
> ARR — All Rights Reserved, Without Prejudice.
> Method of Science, Aim of Religion — Scientific Illuminism.
> "Live, Love, and let Love, Live."

## What already stood (read before a line was written)

- `android/app/` — the Chaquopy WebView shell for the full Resonantia
  engine (a different product; **untouched** by this stage). It
  declares the house package: namespace and applicationId
  `com.qasparr.resonantia`, compileSdk 34, minSdk 26, targetSdk 34.
- `android/deps/dl/android-sdk/` — SDK laid out by hand: platform
  android-34, build-tools 34.0.0, cmdline-tools.
- `android/deps/dl/jdk17/` — vendored Temurin JDK 17.
- `android/debug.keystore` — the house debug keystore (alias
  `androiddebugkey`; fingerprint below).
- `~/workspace/pqpe-ndk/ndk/android-ndk-r30/` — NDK r30.
- `eqvillibbrrivmm/eqvillibbrrivmm_manifold.cpp` — the founder's
  suite: compiles clean natively, runs its own verification +
  telemetry, exit 0. Its `main()` is unguarded (no
  `EQVILLIBBRRIVMM_NO_MAIN` in the source), prints only through
  `std::cout`, and never calls its WAV exporter.

## What this stage added

| File | What it is |
|------|------------|
| `android/build-apk.sh` | The reproducible hand build (the chain below). |
| `android/eqapp/src/main/jni/eq_jni.cpp` | JNI bridge. #includes the founder's .cpp whole with `main` renamed by the preprocessor **inside this file only** (`-Dmain` equivalent, carried in the bridge's own lines); captures `std::cout`, runs the renamed main, returns the telemetry as a String. The founder's text is never edited. |
| `android/eqapp/src/main/java/com/qasparr/resonantia/EqMainActivity.java` | Minimal Activity, framework APIs only: a RUN button and a scrollable monospace pane. Views built in code — no layout XML, so no resource compilation is needed. The suite runs on a background thread; results post back to the UI thread. |
| `android/eqapp/src/main/AndroidManifest.xml` | The eqapp's own manifest: package `com.qasparr.resonantia` (kept from the house declaration), minSdk 26, targetSdk 34, label **Resonantia EQVILLIBBRRIVMM**, **no permissions requested at all**, `extractNativeLibs="true"`. |
| `android/APK-BUILD.md` | This record. |

## The route (build-apk.sh, step by step)

1. **NDK cross-compile** — `aarch64-linux-android26-clang++`
   `-std=c++17 -O2 -fPIC -shared -static-libstdc++`, JNI headers from
   the vendored JDK, repo root on the include path so the bridge
   consumes the founder's .cpp where it stands. **No `-DNDEBUG`**:
   the suite's asserts stay armed on the device. libc++ is linked
   static, so the APK carries exactly one native library.
2. **javac** — Temurin 17, `-encoding UTF-8 -source 8 -target 8`,
   classpath = android-34 `android.jar`.
3. **d8** — build-tools 34.0.0, `--min-api 26` → `classes.dex`.
4. **aapt2 link** — base APK struck from the manifest alone.
5. **zip** — `classes.dex` at the root; the .so at
   `lib/arm64-v8a/`, stored uncompressed.
6. **zipalign** — `-p 4` (native libraries page-aligned).
7. **apksigner sign** — `android/debug.keystore`, alias
   `androiddebugkey` (the house debug strike; see Boundaries).
8. **Verification battery** — inside the script; any failure fails
   the build.

## Tool versions (as struck)

| Tool | Version |
|------|---------|
| NDK | r30 (Pkg.Revision 30.0.16248370), clang 21.0.0 (16134705, based on r574158c) |
| JDK | Temurin 17.0.11+9 (OpenJDK 17.0.11, 2024-04-16) |
| aapt2 | 2.19-10229193 (build-tools 34.0.0) |
| d8 / zipalign / apksigner | build-tools 34.0.0 |
| Platform | android-34 |

## The strikes

- **First strike failed at step 2** — javac read the source as
  US-ASCII (this host's locale) and refused the house header's
  em-dashes: 30 unmappable-character errors. Repair: `-encoding
  UTF-8` on the javac line, marked in the script where it stands.
  Nothing else in the chain changed.
- **Second strike: the whole chain passed**, verification battery
  included, exit 0.

## Verification outputs (second strike, verbatim excerpts)

apksigner verify --print-certs:

```
Signer #1 certificate DN: CN=Android Debug, O=Android, C=US
Signer #1 certificate SHA-256 digest: 9a4a776834dab6dae5660b87836b4435294b7c317a5b334a81d9c00e2a2c7723
Signer #1 certificate SHA-1 digest: 78d87c6aadd6e9bbba14a47f6348529166df25b0
```

— matching the keystore's own fingerprint
(9A:4A:77:68:34:DA:B6:DA:…:2C:77:23, read by keytool before signing).

zipalign -c -v 4:

```
    49 AndroidManifest.xml (OK - compressed)
   852 resources.arsc (OK)
   961 classes.dex (OK - compressed)
  4096 lib/arm64-v8a/libeqvillibbrrivmm.so (OK)
Verification succesful
```

(the .so sits at offset 4096 — page-aligned, as `-p` struck it).

aapt2 dump badging:

```
package: name='com.qasparr.resonantia' versionCode='1' versionName='1.0' platformBuildVersionName='14' platformBuildVersionCode='34' compileSdkVersion='34'
sdkVersion:'26'
targetSdkVersion:'34'
application: label='Resonantia EQVILLIBBRRIVMM' icon=''
launchable-activity: name='com.qasparr.resonantia.EqMainActivity'  label='' icon=''
native-code: 'arm64-v8a'
```

Contents (unzip -l):

```
     2020  AndroidManifest.xml
       40  resources.arsc
     4028  classes.dex
  4598640  lib/arm64-v8a/libeqvillibbrrivmm.so
      519  META-INF/ANDROIDD.SF
     1221  META-INF/ANDROIDD.RSA
      392  META-INF/MANIFEST.MF
```

Native library, inspected directly: ELF 64-bit LSB shared object,
ARM aarch64; its dynamic symbol table exports exactly the JNI entry
the Activity declares —
`Java_com_qasparr_resonantia_EqMainActivity_runSuite`.

## The artifact

- Path: `~/workspace/your_files/Resonantia-EQVILLIBBRRIVMM.apk`
  (build output also at `android/eqapp/build/`, gitignored — house
  precedent keeps binaries out of git).
- Size: **4,612,628 bytes**.
- SHA-256: **88536e9dd44481e7f268ffdcdd662e862701db194030f8df21d88e8a0bb39eb4**
  (identical at the build path and the delivered copy).

## Boundaries — printed, not hidden

- **No device or emulator exists on this box** (no /dev/kvm), so the
  install-and-launch test can only happen on the founder's phone
  (Galaxy A16 5G, Exynos 1330, arm64-v8a — the APK's one ABI).
  Structural verification — signature, alignment, badging,
  contents, exported JNI symbol — is what this stage swears to,
  no more. The suite's arithmetic is the same code that passes
  natively, with its asserts armed; the on-device RUN is the
  founder's tap to make.
- **Debug signing.** The APK is signed with the house debug
  keystore, per the standing doctrine that no release keystore is
  invented by the desk. A release keystore of the founder's own is
  the future seat; an APK signed with a different key will not
  install over this one, so the key change, when he makes it, is a
  fresh install.
- **Same package as the future Resonantia shell.** The eqapp keeps
  the declared `com.qasparr.resonantia`; when the full shell's APK
  is ever struck under the same id and a different key, Android
  will treat it the same way — noted here so the collision is a
  decision on record, not a surprise.
- The Chaquopy/Gradle path for the full engine remains exactly as
  `android/DEPS.md` records it; this stage neither clears nor
  worsens that block — it walks around it with a native suite that
  needs nothing from the network.

---

# v2 — the toolkit seats, in C++, computed on the device

> 23 November 2026. The founder ordered the rebuild ("Rebuild the
> apk to reflect the changes") and then upgraded the order in his
> own words: **"Can you write it in cpp to be used in the app?"**
> So v2's scope is REAL COMPUTE, and this section states it
> exactly. The v1 record above stands as the prior strike,
> marked, not vanished.
>
> Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
> ARR — All Rights Reserved, Without Prejudice.
> Method of Science, Aim of Religion — Scientific Illuminism.
> "Live, Love, and let Love, Live."

## What v2 is — and what it is not

Since v1, the repo gained three things: the pipeline EQ cut-in +
KRS Mastering Rule seal (88d6909, Python), `resonance/studio/
nabla.py` (a41ee87, Python), and `resonance/studio/upscale.py`
(97a63b9, Python). The first v2 draft of this rebuild carried
those seats as a bundled text record for the app to display; the
founder's redirect replaced that draft before any v2 strike —
**the app does not display the bench's numbers, it computes its
own.** Both studio seats now stand in C++ beside the suite's JNI
bridge, proven on the host before the strike (below), and the
app's two new controls run their analytic demonstrations on
built-in fields and tones at tap time and print the measured
results. The demonstrations are demonstrations — the seats are
not wired to the founder's files, and no wording in the app
claims they are. The studio Python seats remain the reference
implementations; the EQ/KRS cut-ins remain Python-side pipeline
work and are not in this app in any form.

## What changed

| File | What it is |
|------|------------|
| `android/eqapp/src/main/jni/nabla.hpp` | The Del operator in C++: gradient / divergence / curl / Laplacian over 1-D/2-D/3-D double-precision fields, numpy.gradient's edge_order=2 scheme written out (central interior, second-order one-sided edges), the Laplacian composed literally as divergence∘gradient, refusals by name as NablaError. One coordinate stated in its header: the edge scheme needs 3 seats per axis — numpy refuses a 2-seat axis in its own words (probed), this port refuses it in the house's. |
| `android/eqapp/src/main/jni/upscale.hpp` | Evaluation upward in C++: a Kaiser-windowed sinc at β = 10.0 (the modified Bessel I0 by its defining series), exact gcd ratios, no gain, nothing synthesized above the source Nyquist. The taps are designed in closed form where scipy's firwin designs by frequency sampling — same window, same β, same 10-source-sample span; the floor is therefore re-measured, not inherited. True peaks by 4× FFT oversampling (the house scale's own method, `pipeline.true_peak_dbtp`, so the seat argues with no second yardstick; the transform is a mixed-radix Cooley–Tukey with a Bluestein road for lengths whose smallest prime factor stands above 5). **No LUFS line**: pyloudnorm has no on-device seat, so the report carries rates/ratio/counts/durations, sample + true peaks, and the measured above-Nyquist floor — and says why the loudness line is absent. Mono: the port is the studio seat's kernel; channels are a caller's loop. |
| `android/eqapp/src/main/jni/toolkit_jni.cpp` | The JNI bridge: `runNablaChecks` (the closed-form battery on built-in fields) and `runUpscaleDemo` (a 1 kHz tone at 44.1k → 96k, and the sr/4 phase-π/4 hidden crest), each returning measured figures as text. |
| `android/eqapp/host/toolkit_host_test.cpp` | The host proof: the same headers, the Python seats' own analytic cases, compiled with the bench's g++ 13.3.0 and run before the strike. Its output is quoted below. It is not part of the APK and not part of the Python suite. |
| `android/eqapp/src/main/java/com/qasparr/resonantia/EqMainActivity.java` | Three controls now: RUN (the suite, unchanged), RUN NABLA CHECKS, RUN UPSCALE DEMO — the same plain framework style, the same pane, the same law (the screen shows what the native code returns; a failure is shown as a failure). |
| `android/eqapp/src/main/AndroidManifest.xml` | versionCode 2, versionName "2.0". Package, label, SDKs, and the empty permission list unchanged. |
| `android/build-apk.sh` | Step 1 compiles `toolkit_jni.cpp` into the same library beside `eq_jni.cpp`. Nothing else in the chain changes. |

## What did not change

- The founder's C++ manifold suite and its JNI bridge: byte for
  byte. The RUN control does exactly what v1's did.
- The signing: the same house debug keystore, the same
  certificate (below) — **v2 installs over v1 as an update.**
- The chain: no Gradle, no network, the same vendored tools.
- The Python suite: **394 tests ran, OK** — re-run at this
  strike; no Python file was touched by v2.

## The host proof (quoted, not paraphrased)

`g++ -std=c++17 -O2 android/eqapp/host/toolkit_host_test.cpp`,
exit 0 — **32 checks, 0 failures.** The measured figures:

- Nabla: grad(x²y) worst error **0** (2-D and 3-D, edges
  included); div(x, y, z) = 3, worst error **0**; the rigid
  rotation ω = 1.7 divergence-free to **7.1e-15**, its curl the
  constant (0, 0, 2ω) to **5.8e-15**; curl∘grad **0**;
  ∇²(x²+y²+z²) = 6 and ∇²(x²−y²) = 0, worst error **0**; five
  refusal cases (curl of a 2-D field, wrong-count spacing, zero
  spacing, a 4-D field, a 2-seat axis) each refused as
  NablaError.
- Upscale: ratio **320/147** exact; 44,100 → **96,000** samples;
  the awkward count 44,101 → **96,003**; dominant frequency
  **1000 Hz** after; RMS moved **2.6e-07**; the floor above
  22,050 Hz measured **−109.675 dB** against the sworn −90 dB
  (the Python seat's bench figure was −109.7 — the closed-form
  taps realize the same floor, with ~19.7 dB of headroom kept);
  sample peaks −0.00 → −0.00 dB, true peaks −0.00 → −0.00 dBTP
  on the tone.
- The hidden crest (sr/4, phase π/4): sample peak before
  **−3.0103 dB** (sworn −3.01); interior evaluated peak
  **0.9999871** (the studio bench measured 0.999986); true peak
  before **0.00 dBTP** on the house scale.
- Two coordinates printed, not smoothed. (1) The tone's
  interior peak measured **1.0000010** — the finite kernel's
  ripple standing 1.04e-6 above the analytic crest; the
  harness's sworn bound is a stated 1e-5 with the figure
  printed, and the port's header names the ripple rather than
  claiming the interior never overshoots. (2) The crest
  record's whole-file true peak after read **0.00 dBTP** here
  (8,192 samples); the studio record's +0.80 dBTP was a
  one-second full-scale record beginning mid-crest — different
  signals, both reported as measured; the seam doctrine is
  unchanged and the whole-file figures still include the seams.

## Verification outputs (the v1 battery, run on v2)

apksigner verify --print-certs — the v1 certificate, unchanged:

```
Signer #1 certificate DN: CN=Android Debug, O=Android, C=US
Signer #1 certificate SHA-256 digest: 9a4a776834dab6dae5660b87836b4435294b7c317a5b334a81d9c00e2a2c7723
```

zipalign -c -v 4: all entries OK; the .so at offset **8192** —
page-aligned, as `-p` struck it (v1's stood at 4096; the larger
classes.dex moved the seat, the alignment is the sworn part).

aapt2 dump badging (excerpts):

```
package: name='com.qasparr.resonantia' versionCode='2' versionName='2.0' platformBuildVersionName='14' platformBuildVersionCode='34' compileSdkVersion='34'
sdkVersion:'26'
targetSdkVersion:'34'
application: label='Resonantia EQVILLIBBRRIVMM' icon=''
launchable-activity: name='com.qasparr.resonantia.EqMainActivity'  label='' icon=''
native-code: 'arm64-v8a'
```

(no `uses-permission` lines — zero permissions, as v1.)

Contents (unzip -l): AndroidManifest.xml 2,020 · resources.arsc
40 · classes.dex 6,436 · lib/arm64-v8a/libeqvillibbrrivmm.so
4,662,232 · the three META-INF signature files.

JNI exports, read off the built library directly
(`llvm-nm -D --defined-only`, filtered to the Java entries) —
exactly three, the suite's and the two seats':

```
Java_com_qasparr_resonantia_EqMainActivity_runNablaChecks
Java_com_qasparr_resonantia_EqMainActivity_runSuite
Java_com_qasparr_resonantia_EqMainActivity_runUpscaleDemo
```

## The artifact

- Path: `~/workspace/your_files/Resonantia-EQVILLIBBRRIVMM-v2.apk`
  (build output also at `android/eqapp/build/`, gitignored — the
  binary stays out of git, per house precedent).
- Size: **4,678,164 bytes** (v1: 4,612,628 — the growth is the
  two seats in the library and the larger classes.dex).
- SHA-256: **963036679b739e279e69e5ee2a6d155d29333d8a5fe90d6059b20ee77202ae51**
  (identical at the build path and the delivered copy).

## Boundaries — printed, not hidden

- **No device or emulator exists on this box** (no /dev/kvm), so
  the install-and-launch test can only happen on the founder's
  phone — now as an **update over v1** (same package, same key,
  versionCode 2 over 1). Structural verification — signature,
  alignment, badging, contents, the three exported JNI symbols —
  plus the host proof of the very headers the library carries,
  is what this stage swears to. The on-device RUN taps (all
  three) are the founder's to make; the numbers his screen
  prints are the device's own measurements, and any difference
  from the bench figures quoted above is itself reportable.
- **Debug signing**, as v1: no release keystore is invented by
  the desk; a release key of the founder's own remains the
  future seat, and a key change will mean a fresh install.
- The seats compute their demonstrations on built-in fields
  and tones. Wiring them to the founder's own files (a field
  source for ∇, an audio file path for the upscale seat) is a
  further seat, not claimed here.
