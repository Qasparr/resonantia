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

## The deeper block: the JVM has no real TCP on this host (2026-10-08)

Proven, not theorized: a Java `Socket.connect()` to 127.0.0.1:9 (a
closed port) **succeeds** -- a real TCP stack would refuse it. Every
Java socket is fake-connected to a sandbox policy message
("Other TCP connections is turned off for this assistant..."), which
is why `sdkmanager` and any JVM HTTPS fetch die in
`HttpURLConnection.doTunneling0` with `NoSuchElementException` even
when handed explicit, correct proxy credentials. Python and curl are
unaffected (proxy-fluent); only the JVM is intercepted.

Consequences:
- `sdkmanager` can never download here -- fetch-deps.sh fetches the
  SDK zips with curl and lays out the SDK by hand instead.
- `gradle` can never resolve dependencies here -- even when
  dl.chaquo.com returns, a Gradle build on this host cannot reach the
  network. The build needs BOTH blocks cleared.
- Remedy: Muse settings -> Permissions -> Direct network protocols ->
  switch `other_tcp` from Deny to Allow. The sandbox message itself
  points there. The `resonantia-apk-block-watch` schedule checks JVM
  TCP (via `deps/JvmNetCheck.java`) on every run and proceeds the
  moment both blocks clear.
- Until then: `GRADLE_OPTS` from `deps/jvm-proxy-opts.sh` carries the
  egress proxy (with auth) for the post-fix world; direct egress is
  dead (curl --noproxy returns 000).
