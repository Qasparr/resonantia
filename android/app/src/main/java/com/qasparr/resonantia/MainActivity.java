// Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
// All Rights Reserved, Without Prejudice · CashApp $axoneme
// 93
//
// MainActivity -- the native shell around the Python engine.
//
// HYPOTHESIS: the smallest honest native app is a launcher: boot the
//   embedded CPython on a worker thread (it runs uvicorn, which
//   blocks), then point a WebView at the loopback engine. The Java
//   layer owns NO audio logic -- it is a window, not an engine.
// METHOD:    onCreate spawns the Python thread FIRST (server takes
//   seconds to rise), then builds the WebView over a file:// asset.
//   index.html polls /health until the engine answers, so no sleep
//   tuning is needed here. JavaScript is on (the UI is a JS app);
//   setAllowUniversalAccessFromFileURLs lets the file:// page fetch
//   http://127.0.0.1:8765 -- the ONLY host it ever contacts, enforced
//   by network_security_config.xml.
// DOCTRINE:  loopback-only, preserved from the desktop engine. The
//   server binds 127.0.0.1:8765; no INTERNET permission is requested.
//   And: never die silent. The engine thread's exceptions are caught
//   and shown on screen as a traceback page; the Python bootstrap
//   writes every boot step to boot.log, so even a native crash --
//   which raises no exception at all -- leaves its last step for the
//   next launch to display. (Added 2026-10-08: the v0.6.0 launch
//   died on the splash with no message. This harness exists so the
//   next death introduces itself.)

package com.qasparr.resonantia;

import android.app.Activity;
import android.content.pm.PackageManager;
import android.Manifest;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.io.StringWriter;

public class MainActivity extends Activity {

    private static final String TAG = "RESONANTIA";

    private WebView webView;
    private Thread engineThread;

    // MECHANISM: READ_MEDIA_AUDIO is a dangerous permission -- the
    //   manifest declares it, but Android still demands a runtime ask.
    //   The cutter refuses loudly without it (the engine never fails
    //   silent), so the request fires once at launch; denial simply
    //   leaves the cutter gated until the user grants it in Settings.
    // DOCTRINE:  ask for the one thing the features need, at the
    //   moment the app starts, with no dark patterns and no retries.
    private static final int REQ_AUDIO = 77;

    private void ensureAudioPermission() {
        String perm = (Build.VERSION.SDK_INT >= 33)
                ? Manifest.permission.READ_MEDIA_AUDIO
                : Manifest.permission.READ_EXTERNAL_STORAGE;
        if (checkSelfPermission(perm) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{perm}, REQ_AUDIO);
        }
    }

    // MECHANISM: the boot log is the flight recorder. Python appends
    //   one line per boot step; a clean boot ends with "serving"
    //   (or "server stopped cleanly"). If the process dies mid-boot
    //   -- native crash, LMK kill -- no exception ever propagates,
    //   but the log's last line names the step that killed it.
    // DOCTRINE:  forensics over guesswork. Read the previous run's
    //   last words before starting the next run.
    private String readPreviousDeath(File bootLog) {
        if (!bootLog.exists()) {
            return null;
        }
        String last = null;
        try (BufferedReader r = new BufferedReader(new FileReader(bootLog))) {
            String line;
            while ((line = r.readLine()) != null) {
                if (!line.trim().isEmpty()) {
                    last = line.trim();
                }
            }
        } catch (Exception e) {
            Log.w(TAG, "could not read boot log", e);
            return null;
        }
        if (last == null
                || last.contains("serving")
                || last.contains("cleanly")) {
            return null; // previous boot lived; nothing to report.
        }
        return last;
    }

    private static String esc(String s) {
        return s.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;");
    }

    // The error page: the engine's last words, on screen, in the
    // project's colors -- so a phone-only user can screenshot them
    // and the scribe can read the traceback.
    private void showErrorPage(String trace, String previousDeath) {
        StringBuilder html = new StringBuilder();
        html.append("<html><body style='background:#1a0b2e;color:#e8d5a3;");
        html.append("font-family:monospace;padding:18px'>");
        html.append("<h2 style='color:#d4af37'>RESONANTIA engine failed</h2>");
        if (previousDeath != null) {
            html.append("<p><b>Previous launch died during:</b><br>");
            html.append(esc(previousDeath)).append("</p>");
        }
        html.append("<p>Send a screenshot of this to Qasparr's assistant:</p>");
        html.append("<pre style='white-space:pre-wrap;font-size:12px'>");
        html.append(esc(trace)).append("</pre>");
        html.append("</body></html>");
        webView.loadData(html.toString(), "text/html", "UTF-8");
    }

    // Shown when the previous launch died without an exception: the
    // forensics first, then yields to the real UI (the engine needs
    // seconds to rise; index.html polls /health on its own). If the
    // engine throws, the error page replaces whatever is showing.
    private void showBootDiagnostic(String previousDeath) {
        String html = "<html><body style='background:#1a0b2e;color:#e8d5a3;"
                + "font-family:monospace;padding:18px'>"
                + "<h2 style='color:#d4af37'>RESONANTIA diagnostics</h2>"
                + "<p><b>Last launch died during:</b><br>"
                + esc(previousDeath) + "</p>"
                + "<p>Restarting the engine&hellip; if it dies again, "
                + "screenshot this page.</p>"
                + "</body></html>";
        webView.loadData(html, "text/html", "UTF-8");
        webView.postDelayed(() ->
            webView.loadUrl("file:///android_asset/www/index.html"), 8000);
    }

    private void startEngine(String bootLogPath,
                             String previousDeath) {
        engineThread = new Thread(() -> {
            try {
                if (!Python.isStarted()) {
                    Python.start(new AndroidPlatform(this));
                }
                Python.getInstance()
                      .getModule("resonantia_app")
                      .callAttr("main", bootLogPath);
            } catch (Throwable t) {
                // Loud, on screen: the engine's last words.
                StringWriter sw = new StringWriter();
                t.printStackTrace(new PrintWriter(sw));
                String trace = sw.toString();
                Log.e(TAG, "engine thread died", t);
                runOnUiThread(() -> showErrorPage(trace, previousDeath));
            }
        });
        engineThread.setDaemon(true);
        engineThread.start();
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        ensureAudioPermission();

        webView = new WebView(this);
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        // file:// UI asset fetching http://127.0.0.1:8765 only.
        s.setAllowUniversalAccessFromFileURLs(true);
        webView.setWebViewClient(new WebViewClient());
        setContentView(webView);

        // Forensics first: what did the last launch die doing?
        File bootLog = new File(getFilesDir(), "boot.log");
        String previousDeath = readPreviousDeath(bootLog);
        if (bootLog.exists()) {
            bootLog.delete(); // this run writes its own record.
        }

        // The engine thread: boots CPython, then blocks inside uvicorn
        // serving 127.0.0.1:8765. Daemon so it dies with the activity.
        startEngine(bootLog.getAbsolutePath(), previousDeath);

        if (previousDeath != null) {
            showBootDiagnostic(previousDeath);
        } else {
            webView.loadUrl("file:///android_asset/www/index.html");
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }

    @Override
    public void onBackPressed() {
        // Back walks the UI's history; at the root it exits, as expected.
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
