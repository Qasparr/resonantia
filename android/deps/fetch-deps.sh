#!/usr/bin/env bash
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
#
# android/deps/fetch-deps.sh -- pin and fetch EVERY build dependency.
#
# HYPOTHESIS: a build that depends on the network at build time is a
#   build that depends on luck. So this script fetches each dependency
#   ONCE, pinned, into android/deps/dl/ (machine-local, gitignored),
#   and stages the Python package + emblem into the Gradle tree.
# METHOD:    1) Temurin JDK 17 (no root needed -- tarball, not apt).
#            2) Android SDK cmdline-tools -> sdkmanager installs exactly
#               platform android-34 + build-tools 34.0.0.
#            3) Gradle 8.7 (pairs with AGP 8.5.2).
#            4) Chaquopy Gradle plugin mirrored into deps/dl/maven
#               (settings.gradle lists that file:// repo first, so a
#               flaky dl.chaquo.com never breaks a prepared machine).
#            5) Stage: copy ../../resonance -> app/src/main/python/
#               and ../../assets/logo.webp -> app/src/main/assets/www/.
#            Every step is idempotent: re-running skips what is present
#            and verified. Any failure is loud (set -euo pipefail) and
#            names the URL that failed.
# RESULT:    after this script, `gradle :app:assembleDebug` runs with
#   the network needed only for Chaquopy's own runtime/pip resolution
#   (which requires dl.chaquo.com reachable -- the tracked block).

set -euo pipefail

DEPS="$HOME/workspace/resonance/android/deps/dl"
ANDR="$HOME/workspace/resonance/android"
mkdir -p "$DEPS"
cd "$DEPS"

# -- pinned versions (one ledger; DEPS.md is the human-readable twin) --
JDK_URL="https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.11%2B9/OpenJDK17U-jdk_x64_linux_hotspot_17.0.11_9.tar.gz"
CMDLINE_URL="https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
GRADLE_VERSION="8.7"
GRADLE_URL="https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip"
CHAQUOPY_VERSION="17.0.0"   # pinned 2026-10-08 from chaquo.com docs
CHAQUOPY_MAVEN="https://dl.chaquo.com/maven"

have() { command -v "$1" >/dev/null 2>&1; }
need() { have "$1" || { echo "fetch-deps: need '$1' (curl/unzip)"; exit 2; }; }
need curl; need unzip

# -- 1. JDK 17 -----------------------------------------------------------
if [ ! -x "$DEPS/jdk17/bin/java" ]; then
    echo "fetch-deps: JDK 17 ..."
    curl -sSL -o jdk17.tar.gz "$JDK_URL"
    mkdir -p jdk17 && tar xzf jdk17.tar.gz -C jdk17 --strip-components=1
    rm jdk17.tar.gz
fi
export JAVA_HOME="$DEPS/jdk17"
export PATH="$JAVA_HOME/bin:$PATH"
java -version 2>&1 | head -1

# -- 2. Android SDK -------------------------------------------------------
if [ ! -x "$DEPS/android-sdk/cmdline-tools/latest/bin/sdkmanager" ]; then
    echo "fetch-deps: SDK cmdline-tools ..."
    curl -sSL -o cmdline.zip "$CMDLINE_URL"
    mkdir -p android-sdk/cmdline-tools
    unzip -q cmdline.zip -d android-sdk/cmdline-tools
    mv android-sdk/cmdline-tools/cmdline-tools android-sdk/cmdline-tools/latest
    rm cmdline.zip
fi
export ANDROID_HOME="$DEPS/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
yes | sdkmanager --licenses >/dev/null 2>&1 || true
sdkmanager --install "platforms;android-34" "build-tools;34.0.0" 2>&1 | tail -2

# -- 3. Gradle ------------------------------------------------------------
if [ ! -x "$DEPS/gradle-${GRADLE_VERSION}/bin/gradle" ]; then
    echo "fetch-deps: Gradle ${GRADLE_VERSION} ..."
    curl -sSL -o gradle.zip "$GRADLE_URL"
    unzip -q gradle.zip
    rm gradle.zip
fi
export PATH="$DEPS/gradle-${GRADLE_VERSION}/bin:$PATH"
gradle --version 2>/dev/null | grep -m1 Gradle

# -- 4. Chaquopy plugin mirror --------------------------------------------
# The plugin jar+pom, laid out as a Maven repo so settings.gradle's
# file:// entry resolves it without the network. The plugin's own
# runtime/pip artifacts still resolve from dl.chaquo.com at build
# time -- which is exactly the tracked block (see DEPS.md).
MAVEN_DIR="$DEPS/maven/com/chaquo/python/gradle/${CHAQUOPY_VERSION}"
if [ ! -f "$MAVEN_DIR/gradle-${CHAQUOPY_VERSION}.jar" ]; then
    echo "fetch-deps: probing dl.chaquo.com ..."
    if curl -sS -o /dev/null --max-time 20 \
            "$CHAQUOPY_MAVEN/com/chaquo/python/gradle/maven-metadata.xml"; then
        echo "fetch-deps: dl.chaquo.com reachable -- mirroring plugin ..."
        mkdir -p "$MAVEN_DIR"
        base="$CHAQUOPY_MAVEN/com/chaquo/python/gradle/${CHAQUOPY_VERSION}"
        for ext in jar pom module; do
            curl -sSL -o "$MAVEN_DIR/gradle-${CHAQUOPY_VERSION}.$ext" \
                "$base/gradle-${CHAQUOPY_VERSION}.$ext"
        done
        ls -la "$MAVEN_DIR"
    else
        echo "fetch-deps: WARNING: dl.chaquo.com still unreachable --"
        echo "  the Chaquopy plugin cannot be mirrored yet. The build"
        echo "  stays blocked on it (tracked; see DEPS.md)."
    fi
else
    echo "fetch-deps: Chaquopy plugin already mirrored."
fi

# -- 5. Stage the Python package + emblem ----------------------------------
echo "fetch-deps: staging resonance package ..."
rm -rf "$ANDR/app/src/main/python/resonance"
cp -r "$HOME/workspace/resonance/resonance" "$ANDR/app/src/main/python/resonance"
find "$ANDR/app/src/main/python/resonance" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
echo "fetch-deps: staging emblem ..."
cp "$HOME/workspace/resonance/assets/logo.webp" "$ANDR/app/src/main/assets/www/logo.webp"

echo
echo "fetch-deps: DONE. Build with:"
echo "  export JAVA_HOME=$DEPS/jdk17"
echo "  export ANDROID_HOME=$DEPS/android-sdk"
echo "  export PATH=$DEPS/gradle-${GRADLE_VERSION}/bin:\$JAVA_HOME/bin:\$PATH"
echo "  cd $ANDR && gradle :app:assembleDebug"
echo "  APK -> $ANDR/app/build/outputs/apk/debug/app-debug.apk"
