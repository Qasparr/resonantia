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

**BLOCKED on `dl.chaquo.com`** (the Chaquopy download host: TLS opens,
then empty replies -- HTTP 000 -- since 2026-10-08). Everything else in
DEPS.md is fetched or fetchable. A scheduled watch
(`resonantia-apk-block-watch`, every 6 hours) probes the host; the
moment it answers, the watch runs fetch-deps.sh, builds the APK, and
pushes it to GitHub as the v0.6.0 release. Nothing for anyone to do
until then -- final install/launch verification happens on John's
Android device regardless, since the build host cannot boot Android.
