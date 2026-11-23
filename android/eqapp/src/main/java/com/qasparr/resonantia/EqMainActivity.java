// =============================================================================
// RESONANTIA — EqMainActivity.java — the whole Java side of the
// EQVILLIBBRRIVMM APK: one screen, three RUN controls, one
// scrollable pane of monospace text. Framework APIs only; no
// external dependency exists in this file, so nothing had to be
// fetched to build it.
//
// Epigraph: "Every, Man, Woman, and Child, is a Star."
// "Live, Love, and let Love, Live!"
// — the founder's own header on the suite itself.
//
// 93.
// Date: 22 November 2026 (v1); v2 the 23rd.
// Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
// ARR — All Rights Reserved, Without Prejudice.
// Method of Science, Aim of Religion — Scientific Illuminism.
//
// MECHANISM: onCreate builds the view tree in code (no layout XML,
// so the hand build needs no resource compilation beyond the
// manifest): a vertical LinearLayout holding the three buttons
// above a ScrollView holding the output TextView. Each button
// starts a background thread — the suite's verification walks
// 456,533 cells and the toolkit's demonstrations compute, none of
// which may block the UI thread — and the thread posts the
// returned text back through runOnUiThread. The native methods
// are implemented in eq_jni.cpp (runSuite) and toolkit_jni.cpp
// (runNablaChecks, runUpscaleDemo) inside libeqvillibbrrivmm.so.
//
// DOCTRINE: the screen shows what the native code itself returns
// — the suite's [VERIFIED] line and telemetry verbatim, and the
// toolkit demonstrations' MEASURED figures, computed on this
// device at the tap. Nothing is paraphrased, decorated, or
// hidden: if a call fails on the device, the failure is what the
// screen says.
//
// v2 — 23 November 2026. The founder's redirect, in his words:
// "Can you write it in cpp to be used in the app?" So v2 is not
// the record pane this file's first v2 draft carried (a bundled
// text of the bench's numbers, struck before any v2 build and
// replaced at his word, before it ever shipped): the app now
// COMPUTES both toolkit seats in C++ on the device — nabla (the
// Del operator) and upscale (evaluation upward), ported from the
// studio seats at a41ee87 and 97a63b9, host-proven on the bench
// before the strike (android/eqapp/host/). RUN NABLA CHECKS and
// RUN UPSCALE DEMO run the seats' own analytic demonstrations on
// built-in fields and tones and print the measured results. The
// demonstrations are demonstrations — no wording here claims
// the seats have been wired to the founder's files — and the
// studio Python seats remain the reference implementations.
//
// All Rights Reserved, Without Prejudice.
// "Live, Love, and let Love, Live."
// =============================================================================

package com.qasparr.resonantia;

import android.app.Activity;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public class EqMainActivity extends Activity {

    static {
        System.loadLibrary("eqvillibbrrivmm");
    }

    /** Implemented in eq_jni.cpp: runs the founder's suite main()
     *  with std::cout captured, and returns the captured telemetry. */
    private native String runSuite();

    /** Implemented in toolkit_jni.cpp: runs the C++ nabla seat's
     *  analytic checks on built-in fields, on this device, and
     *  returns the measured results. */
    private native String runNablaChecks();

    /** Implemented in toolkit_jni.cpp: runs the C++ upscale seat's
     *  demonstration (a 1 kHz tone and the hidden crest), on this
     *  device, and returns the measured results. */
    private native String runUpscaleDemo();

    private TextView output;

    /** The one road every control takes: announce, compute on a
     *  background thread, post the returned text to the pane. A
     *  native call that throws is shown as the failure it is. */
    private void runNative(final java.util.concurrent.Callable<String> call,
                           String runningText) {
        output.setText(runningText);
        new Thread(new Runnable() {
            @Override
            public void run() {
                String result;
                try {
                    result = call.call();
                } catch (Throwable t) {
                    result = "Native call failed: " + t + "\n";
                }
                final String text = result;
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        output.setText(text);
                    }
                });
            }
        }).start();
    }

    private Button addButton(LinearLayout root, String label,
                             View.OnClickListener listener) {
        Button button = new Button(this);
        button.setText(label);
        button.setOnClickListener(listener);
        root.addView(button, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));
        return button;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);

        output = new TextView(this);
        output.setTypeface(Typeface.MONOSPACE);
        output.setTextIsSelectable(true);
        output.setText("Resonantia EQVILLIBBRRIVMM\n"
                + "The founder's suite, native on this device.\n"
                + "Press RUN — the suite verifies itself and reports.\n"
                + "Press RUN NABLA CHECKS or RUN UPSCALE DEMO — the\n"
                + "house toolkit's C++ seats compute their sworn\n"
                + "demonstrations here and print what they measure.\n");

        ScrollView scroll = new ScrollView(this);
        scroll.addView(output);

        addButton(root, "RUN EQVILLIBBRRIVMM SUITE",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        runNative(new java.util.concurrent.Callable<String>() {
                            @Override
                            public String call() {
                                return runSuite();
                            }
                        }, "Running...\n");
                    }
                });
        addButton(root, "RUN NABLA CHECKS",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        runNative(new java.util.concurrent.Callable<String>() {
                            @Override
                            public String call() {
                                return runNablaChecks();
                            }
                        }, "Running nabla checks...\n");
                    }
                });
        addButton(root, "RUN UPSCALE DEMO",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        runNative(new java.util.concurrent.Callable<String>() {
                            @Override
                            public String call() {
                                return runUpscaleDemo();
                            }
                        }, "Running upscale demo...\n");
                    }
                });

        root.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);
    }
}
