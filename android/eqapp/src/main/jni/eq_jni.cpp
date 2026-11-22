// =============================================================================
// RESONANTIA — android/eqapp/src/main/jni/eq_jni.cpp — the JNI bridge that
// seats the founder's EQVILLIBBRRIVMM manifold suite inside the APK as a
// native shared library.
//
// Epigraph: "Every, Man, Woman, and Child, is a Star."
// "Live, Love, and let Love, Live!"
// — the founder's own header on the suite itself
//   (eqvillibbrrivmm/eqvillibbrrivmm_manifold.cpp).
//
// 93.
// Date: 22 November 2026.
// Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
// ARR — All Rights Reserved, Without Prejudice.
// Method of Science, Aim of Religion — Scientific Illuminism.
//
// SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
//   Hypothesis: that the founder's suite, which carries its own
//     verification inside its main() (asserts on the Christoffel guard,
//     the Doppler geometry, the Laplace convolution bus, and the 77^3 =
//     456,533-cell Enclave Sphere, then prints its telemetry to
//     std::cout), can run whole on the phone — the same code, not a
//     port — if its entry point is renamed at build time and its
//     std::cout is captured for the screen.
//   Method: this translation unit #includes the founder's .cpp whole,
//     with the preprocessor renaming main → eqvillibbrrivmm_suite_main
//     for this unit only. The founder's text is never edited; the
//     rename is a build flag carried in this file's own lines, visible
//     to any reader, reversible by deleting this file. The JNI entry
//     below swaps std::cout's stream buffer into a string stream,
//     calls the renamed main, restores the buffer, and returns the
//     captured telemetry to Java as a String.
//   Observation: (recorded in android/APK-BUILD.md after the strike.)
//   Result: this bridge, libeqvillibbrrivmm.so, and the telemetry on
//     the phone's screen.
//
// DOCTRINE:
//   - The founder's .cpp is the law; this file adds a doorway, never a
//     rewrite. No value in the suite is touched, rounded, or re-derived.
//   - The suite's asserts stay ARMED (no -DNDEBUG anywhere in the
//     build): the verification that runs on the phone is the same
//     verification that runs on the desktop, or the APK would be a
//     photograph of the suite instead of the suite.
//   - The WAV exporter in the founder's file is defined but never
//     called by his main(); this bridge does not call it either. What
//     main() does is what the phone does — nothing added.
//
// All Rights Reserved, Without Prejudice.
// "Live, Love, and let Love, Live."
// =============================================================================

#include <jni.h>

#include <iostream>
#include <sstream>
#include <string>

// MECHANISM: rename the founder's entry point for THIS translation
// unit only. The #define lives and dies inside this file; the .cpp on
// disk keeps its own main() and still builds as a desktop program.
#define main eqvillibbrrivmm_suite_main
#include "eqvillibbrrivmm/eqvillibbrrivmm_manifold.cpp"
#undef main

extern "C" JNIEXPORT jstring JNICALL
Java_com_qasparr_resonantia_EqMainActivity_runSuite(JNIEnv* env,
                                                    jobject /* thiz */) {
    // MECHANISM: capture std::cout. The suite speaks only through
    // std::cout (verified against the source: its file-writing
    // exporter is never called by main), so swapping the stream
    // buffer captures the whole of its output — the [VERIFIED] line
    // and the four telemetry lines — verbatim.
    std::ostringstream captured;
    std::streambuf* previous = std::cout.rdbuf(captured.rdbuf());

    int rc = 0;
    std::string failure;
    try {
        rc = eqvillibbrrivmm_suite_main();
    } catch (const std::exception& e) {
        // DOCTRINE: a thrown error is reported on the screen, never
        // swallowed and never allowed to kill the app silently.
        failure = e.what();
    } catch (...) {
        failure = "unknown native exception";
    }
    std::cout.rdbuf(previous);

    std::string out = captured.str();
    if (!failure.empty()) {
        out += "\n[EQVILLIBBRRIVMM] suite threw: " + failure + "\n";
    }
    out += "\n[EQVILLIBBRRIVMM] suite exit code: " + std::to_string(rc) + "\n";
    return env->NewStringUTF(out.c_str());
}
