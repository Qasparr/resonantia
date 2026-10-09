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
  loopback-only is doctrine, not preference. Every boot step is
  appended to boot_log (a path handed in by MainActivity); if the
  process dies mid-boot -- e.g. a native crash, which raises no
  Python exception -- the log's last line says exactly which step
  killed it, and the next launch shows it on screen.
DOCTRINE:  127.0.0.1:8765, always. The WebView UI only ever fetches
  this origin (see network_security_config.xml). And: never die
  silent. A dead engine leaves its last words in the boot log; a
  raised engine leaves its traceback for MainActivity's error page.
"""

HOST = "127.0.0.1"
PORT = 8765


def main(boot_log=None):
    """Boot the render engine. Blocks inside uvicorn -- call on a thread.

    boot_log -- file path (str) the boot steps are appended to, or
      None for a quiet boot. MainActivity passes its app-private
      boot.log and reads it back on the next launch.
    """

    def log(step):
        # Best-effort: logging must never be what kills the boot.
        if boot_log:
            try:
                with open(boot_log, "a") as f:
                    f.write(step + "\n")
            except Exception:
                pass

    try:
        log("py: import uvicorn")
        try:
            import uvicorn  # noqa: F401
        except Exception:
            # Loud, on-device: without the pip set from app/build.gradle
            # there is no engine, and silence would be the lie.
            raise RuntimeError(
                "resonantia_app: uvicorn is missing -- the Chaquopy pip "
                "block in android/app/build.gradle did not install."
            )
        log("py: import resonance.api.service")
        from resonance.api.service import create_app

        log("py: create_app()")
        app = create_app()
        # Lifespan hook: the single POSITIVE signal that the server is
        # really up. Without it, a healthy engine relaunching would
        # look like a death in the boot log (the log would end at
        # "uvicorn.run", never reaching "serving"), and the next
        # launch would falsely report "died during: uvicorn.run".
        # With it, the forensics stay honest: "serving" means serving.
        from contextlib import asynccontextmanager

        _lifespan = app.router.lifespan_context

        @asynccontextmanager
        async def _boot_lifespan(app_):
            log("py: serving")
            if _lifespan is not None:
                async with _lifespan(app_):
                    yield
            else:
                yield

        app.router.lifespan_context = _boot_lifespan
        log("py: uvicorn.run(127.0.0.1:8765)")
        # log_level warning: on a phone, uvicorn's access chatter is noise.
        uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
        log("py: server stopped cleanly")
    except BaseException as e:
        # The engine's last words, written before the exception
        # propagates to MainActivity (which shows them on screen).
        log("py: FAILED: %r" % (e,))
        raise
