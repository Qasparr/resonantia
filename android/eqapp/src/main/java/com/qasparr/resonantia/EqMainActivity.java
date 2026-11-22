// =============================================================================
// RESONANTIA — EqMainActivity.java — the whole Java side of the
// EQVILLIBBRRIVMM APK: one screen, one RUN control, one scrollable
// pane of monospace text. Framework APIs only; no external dependency
// exists in this file, so nothing had to be fetched to build it.
//
// Epigraph: "Every, Man, Woman, and Child, is a Star."
// "Live, Love, and let Love, Live!"
// — the founder's own header on the suite itself.
//
// 93.
// Date: 22 November 2026.
// Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
// ARR — All Rights Reserved, Without Prejudice.
// Method of Science, Aim of Religion — Scientific Illuminism.
//
// MECHANISM: onCreate builds the view tree in code (no layout XML, so
// the hand build needs no resource compilation beyond the manifest):
// a vertical LinearLayout holding the RUN button above a ScrollView
// holding the output TextView. The button starts a background thread
// — the suite's verification walks 456,533 cells and must not block
// the UI thread — and the thread posts the returned telemetry back
// through runOnUiThread. The native method runSuite() is implemented
// in eq_jni.cpp inside libeqvillibbrrivmm.so.
//
// DOCTRINE: the screen shows what the suite itself prints — its
// [VERIFIED] line and its telemetry, verbatim — plus the bridge's own
// exit-code line. Nothing is paraphrased, decorated, or hidden: if
// the suite fails on the device, the failure is what the screen says.
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

    private TextView output;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);

        Button run = new Button(this);
        run.setText("RUN EQVILLIBBRRIVMM SUITE");

        output = new TextView(this);
        output.setTypeface(Typeface.MONOSPACE);
        output.setTextIsSelectable(true);
        output.setText("Resonantia EQVILLIBBRRIVMM\n"
                + "The founder's suite, native on this device.\n"
                + "Press RUN — the suite verifies itself and reports.\n");

        ScrollView scroll = new ScrollView(this);
        scroll.addView(output);

        run.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                output.setText("Running...\n");
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        String result;
                        try {
                            result = runSuite();
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
        });

        root.addView(run, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));
        root.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);
    }
}
