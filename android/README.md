# RESONANTIA v0.6.0 — "The Native Shell"

> *"Nothing is forbidden -- every thing is permitted."*
> — Assassin's Creed

Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
All Rights Reserved, Without Prejudice · CashApp $axoneme
93

## Hypothesis

The phone deserves the same engine as the desktop -- not a rewrite, not
a companion app. So v0.6.0 embeds CPython via Chaquopy, serves the
existing FastAPI render engine on **127.0.0.1:8765**, and puts a touch
WebView in front of it. One engine, two shells.

## Method

```
android/
├── settings.gradle / build.gradle / gradle.properties
├── DEPS.md                  -- the dependency ledger (read this first)
├── deps/fetch-deps.sh       -- pins + fetches every build dependency
├── deps/dl/                 -- machine-local fetch cache (gitignored)
└── app/
    ├── build.gradle         -- Chaquopy: CPython 3.11, pip(numpy, fastapi, uvicorn)
    ├── src/main/AndroidManifest.xml      -- no INTERNET permission (loopback needs none)
    ├── src/main/res/xml/network_security_config.xml  -- cleartext ONLY to 127.0.0.1
    ├── src/main/java/.../MainActivity.java -- boots Python on a thread, shows the WebView
    ├── src/main/python/resonantia_app.py  -- serves resonance.api on 127.0.0.1:8765
    └── src/main/assets/www/index.html     -- the touch UI (808 / binaural / ABC / jobs)
```

## Doctrine (non-negotiable)

- **Loopback-only, on-device too.** The server binds 127.0.0.1:8765;
  the manifest requests no INTERNET permission; the network security
  config permits cleartext solely to 127.0.0.1/localhost.
- **Debug signing only.** No release keystore is invented here -- a
  release keystore is John's to create and keep.
- **One ABI:** arm64-v8a. Real devices, not emulators.

## Observation -- building

```sh
cd ~/workspace/resonance/android
./deps/fetch-deps.sh          # pins + fetches everything (~500 MB, one time)
export JAVA_HOME=$PWD/deps/dl/jdk17
export ANDROID_HOME=$PWD/deps/dl/android-sdk
export PATH=$PWD/deps/dl/gradle-8.7/bin:$JAVA_HOME/bin:$PATH
gradle :app:assembleDebug
# APK -> app/build/outputs/apk/debug/app-debug.apk
```

## Result -- status

**Primary path: GitHub Actions** (`.github/workflows/build-apk.yml`).
The build host's sandbox fake-connects every Java socket, so Gradle can
never resolve dependencies there -- but GitHub's runners have full, real
network (`dl.chaquo.com` reachable, JVM normal). Trigger with
`gh workflow run build-apk.yml --repo Qasparr/resonantia`; the workflow
builds `:app:assembleDebug` and publishes `resonantia-0.6.0-debug.apk`
on the v0.6.0 release.

**Fallback: local build** (blocked on two conditions). Everything else
is vendored for a local build via `./deps/fetch-deps.sh`, but it needs
(1) `dl.chaquo.com` reachable AND (2) JVM TCP allowed (Muse settings ->
Permissions -> Direct network protocols -> `other_tcp` to Allow).
A scheduled watch (`resonantia-apk-block-watch`, every 6 hours) probes
both; the moment they clear it builds locally and pushes. The watch is
a backup while the Actions path is primary.
