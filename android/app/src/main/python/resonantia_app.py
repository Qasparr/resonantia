# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
"""resonantia_app -- the Chaquopy bootstrap for RESONANTIA v0.6.0.

HYPOTHESIS: the Android app and the desktop CLI must run the SAME
  engine, or the APK is a second implementation wearing the project's
  name. So the bootstrap does one thing: serve the existing
  resonance.api render service on 127.0.0.1:8765, exactly as
  `resonance-serve` does on desktop.
METHOD:    main() builds the app via resonance.api.service.create_app
  and runs uvicorn programmatically (blocking -- MainActivity runs
  this on a worker thread). Host and port are constants, not options:
  loopback-only is doctrine, not preference.
DOCTRINE:  127.0.0.1:8765, always. The WebView UI only ever fetches
  this origin (see network_security_config.xml).
"""

HOST = "127.0.0.1"
PORT = 8765


def main():
    """Boot the render engine. Blocks inside uvicorn -- call on a thread."""
    try:
        import uvicorn  # noqa: F401
    except Exception:
        # Loud, on-device: without the pip set from app/build.gradle
        # there is no engine, and silence would be the lie.
        raise RuntimeError(
            "resonantia_app: uvicorn is missing -- the Chaquopy pip "
            "block in android/app/build.gradle did not install."
        )
    from resonance.api.service import create_app

    app = create_app()
    # log_level warning: on a phone, uvicorn's access chatter is noise.
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
