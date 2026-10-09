# DEPS.md -- the v0.6.0 dependency ledger

> Every dependency of the RESONANTIA native APK, with its pinned
> version, its source, and its status. A dependency is not "handled"
> until it is either vendored in this repo or fetched by
> `deps/fetch-deps.sh` into `deps/dl/`. -- Qasparr's build doctrine

## Status key

- **OK** -- fetched or fetchable now.
- **BLOCKED** -- unreachable from the build host (tracked by the
  `resonantia-apk-block-watch` schedule; it fires the build the moment
  the block clears).

## The ledger

| # | Dependency | Pinned | Source | Size | Status | Notes |
|---|-----------|--------|--------|------|--------|-------|
| 1 | Temurin JDK 17 | 17.0.11+9 | github.com/adoptium | ~190 MB tarball | OK | No root needed; lives in `deps/dl/jdk17` |
| 2 | Android SDK cmdline-tools | 11076708 | dl.google.com | ~150 MB zip | OK | Reachable; installs into `deps/dl/android-sdk` |
| 3 | SDK platform android-34 | 34 | via sdkmanager | ~60 MB | OK | `compileSdk = 34` |
| 4 | SDK build-tools | 34.0.0 | via sdkmanager | ~55 MB | OK | Pinned to match AGP 8.5.2 |
| 5 | Gradle | 8.7 | services.gradle.org | ~120 MB zip | OK | Pairs with AGP 8.5.2 |
| 6 | Android Gradle Plugin | 8.5.2 | google()/mavenCentral() | ~small | OK | In root `build.gradle` |
| 7 | **Chaquopy Gradle plugin** | **17.0.0** | **dl.chaquo.com/maven** | ~2 MB | **BLOCKED** | **The hold.** `dl.chaquo.com` returns empty replies (HTTP 000) from the build host since 2026-10-08. No mirror exists. Mirrored to `deps/dl/maven` by fetch-deps.sh the moment it is reachable. |
| 8 | Chaquopy embedded CPython | 3.11 | via Chaquopy plugin | ~25 MB (arm64) | BLOCKED | Resolved by the plugin at build time; same host block |
| 9 | Chaquopy numpy wheel | (plugin's index) | dl.chaquo.com/pypi | ~15 MB | BLOCKED | Same host block |
| 10 | fastapi / uvicorn | (pip, unpinned) | via Chaquopy pip index | ~small | BLOCKED | Pure-Python; resolve at build time; same host block |
| 11 | resonance package | repo HEAD | this repo | -- | OK | Staged by fetch-deps.sh into `app/src/main/python/` |
| 12 | emblem logo.webp | repo HEAD | `assets/logo.webp` | ~small | OK | Staged by fetch-deps.sh into `app/src/main/assets/www/` |

## Why the big pieces stay out of git

The SDK + JDK + Gradle (~500 MB) are machine-local in `deps/dl/`
(gitignored): GitHub refuses files over 100 MB and the metered-cellular
rule forbids bloating the clone. What the repo DOES hold: the complete
build project, this ledger, and the pinned fetch recipes -- so any
machine reproduces the build from the repo alone, needing only the
network for rows 7-10 (the tracked block).

## The block, precisely

- `dl.chaquo.com` -- TLS completes, then empty reply (curl exit 52,
  HTTP 000), consistently since 2026-10-08 ~21:35 EDT.
- `dl.google.com`, `services.gradle.org`, `github.com`, `chaquo.com`
  (docs), PyPI -- all reachable. The block is specific to the Chaquopy
  download host, not the build host's network.
- Chaquopy publishes no mirror for its Maven repo, its Python runtime,
  or its numpy wheels (verified 2026-10-08).
