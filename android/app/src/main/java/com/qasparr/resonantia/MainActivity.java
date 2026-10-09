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

package com.qasparr.resonantia;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends Activity {

    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // The engine thread: boots CPython, then blocks inside uvicorn
        // serving 127.0.0.1:8765. Daemon so it dies with the activity.
        Thread engine = new Thread(() -> {
            if (!Python.isStarted()) {
                Python.start(new AndroidPlatform(this));
            }
            Python.getInstance()
                  .getModule("resonantia_app")
                  .callAttr("main");
        });
        engine.setDaemon(true);
        engine.start();

        webView = new WebView(this);
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        // file:// UI asset fetching http://127.0.0.1:8765 only.
        s.setAllowUniversalAccessFromFileURLs(true);
        webView.setWebViewClient(new WebViewClient());
        setContentView(webView);
        webView.loadUrl("file:///android_asset/www/index.html");
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
