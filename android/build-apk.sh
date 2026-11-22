#!/usr/bin/env bash
# =============================================================================
# RESONANTIA — android/build-apk.sh — the hand build of the
# EQVILLIBBRRIVMM APK. No Gradle, no network, no Play Store: every
# tool below already stands on this machine, vendored or laid out by
# hand, because this host's JVM has no real TCP and Gradle can never
# resolve a dependency here (the standing proof lives in
# android/DEPS.md and android/deps/JvmNetCheck.java).
#
# Epigraph: "Every, Man, Woman, and Child, is a Star."
# "Live, Love, and let Love, Live!"
# — the founder's own header on the suite itself.
#
# 93.
# Date: 22 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# THE CHAIN (each step names its tool; versions recorded in
# android/APK-BUILD.md):
#   1. NDK r30 clang++ cross-compiles eq_jni.cpp — which #includes
#      the founder's manifold .cpp whole, its main renamed by the
#      preprocessor inside the bridge file only — into
#      libeqvillibbrrivmm.so for arm64-v8a, libc++ linked static so
#      the APK carries exactly one native library.
#   2. javac (vendored Temurin JDK 17) compiles EqMainActivity.java
#      against the android-34 android.jar, framework APIs only.
#   3. d8 (build-tools 34.0.0) dexes the classes to classes.dex.
#   4. aapt2 link strikes the base APK from the manifest alone
#      (the app builds its views in code; there are no resources).
#   5. zip seats classes.dex at the root and the .so at
#      lib/arm64-v8a/, stored uncompressed.
#   6. zipalign aligns (-p: native libraries page-aligned).
#   7. apksigner signs with android/debug.keystore — the house
#      debug strike. DOCTRINE: no release keystore is invented
#      here; a release key is the founder's to create and keep,
#      per his self-signed doctrine.
#   8. The verification battery runs inside this script: apksigner
#      verify, zipalign -c, aapt2 dump badging, contents listing.
#      A failed check fails the build — set -e is the gate.
#
# USAGE:  ./build-apk.sh
# OUTPUT: android/eqapp/build/Resonantia-EQVILLIBBRRIVMM.apk
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================
set -euo pipefail

ANDROID_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$ANDROID_DIR/.." && pwd)"
EQAPP="$ANDROID_DIR/eqapp"

SDK="$ANDROID_DIR/deps/dl/android-sdk"
BT="$SDK/build-tools/34.0.0"
ANDROID_JAR="$SDK/platforms/android-34/android.jar"
JDK="$ANDROID_DIR/deps/dl/jdk17"
NDK_BIN="$HOME/workspace/pqpe-ndk/ndk/android-ndk-r30/toolchains/llvm/prebuilt/linux-x86_64/bin"
CXX="$NDK_BIN/aarch64-linux-android26-clang++"

export JAVA_HOME="$JDK"
export PATH="$JDK/bin:$PATH"

BUILD="$EQAPP/build"
rm -rf "$BUILD"
mkdir -p "$BUILD/classes" "$BUILD/dex" "$BUILD/lib/arm64-v8a"

echo "== 1/8 NDK cross-compile: libeqvillibbrrivmm.so (arm64-v8a) =="
# MECHANISM: -I"$REPO_ROOT" lets the bridge write
# #include "eqvillibbrrivmm/eqvillibbrrivmm_manifold.cpp" — the
# founder's file is consumed as it stands, never copied, never edited.
# No -DNDEBUG: the suite's asserts stay armed on the device.
"$CXX" -std=c++17 -O2 -fPIC -shared -static-libstdc++ \
    -I"$JDK/include" -I"$JDK/include/linux" -I"$REPO_ROOT" \
    -o "$BUILD/lib/arm64-v8a/libeqvillibbrrivmm.so" \
    "$EQAPP/src/main/jni/eq_jni.cpp"

echo "== 2/8 javac: EqMainActivity.java =="
# MECHANISM: -encoding UTF-8 is load-bearing — this host's locale is
# US-ASCII, and the house header carries em-dashes; without the flag
# javac refuses the file outright (30 unmappable-character errors on
# the first strike, recorded in APK-BUILD.md).
"$JDK/bin/javac" -encoding UTF-8 -source 8 -target 8 -cp "$ANDROID_JAR" \
    -d "$BUILD/classes" \
    "$EQAPP/src/main/java/com/qasparr/resonantia/EqMainActivity.java"

echo "== 3/8 d8: classes.dex =="
"$BT/d8" --lib "$ANDROID_JAR" --min-api 26 --output "$BUILD/dex" \
    $(find "$BUILD/classes" -name '*.class')

echo "== 4/8 aapt2 link: base APK from the manifest =="
"$BT/aapt2" link -o "$BUILD/base.apk" -I "$ANDROID_JAR" \
    --manifest "$EQAPP/src/main/AndroidManifest.xml"

echo "== 5/8 zip: seat classes.dex and the native library =="
(cd "$BUILD/dex" && zip -q "$BUILD/base.apk" classes.dex)
(cd "$BUILD" && zip -q -0 base.apk lib/arm64-v8a/libeqvillibbrrivmm.so)

echo "== 6/8 zipalign =="
"$BT/zipalign" -f -p 4 "$BUILD/base.apk" "$BUILD/aligned.apk"

echo "== 7/8 apksigner: house debug strike =="
"$BT/apksigner" sign \
    --ks "$ANDROID_DIR/debug.keystore" \
    --ks-pass pass:android --key-pass pass:android \
    --out "$BUILD/Resonantia-EQVILLIBBRRIVMM.apk" \
    "$BUILD/aligned.apk"

echo "== 8/8 verification battery =="
"$BT/apksigner" verify --print-certs "$BUILD/Resonantia-EQVILLIBBRRIVMM.apk"
"$BT/zipalign" -c -v 4 "$BUILD/Resonantia-EQVILLIBBRRIVMM.apk"
"$BT/aapt2" dump badging "$BUILD/Resonantia-EQVILLIBBRRIVMM.apk"
unzip -l "$BUILD/Resonantia-EQVILLIBBRRIVMM.apk"
sha256sum "$BUILD/Resonantia-EQVILLIBBRRIVMM.apk"

echo "BUILD OK: $BUILD/Resonantia-EQVILLIBBRRIVMM.apk"
