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
