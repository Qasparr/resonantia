#!/usr/bin/env python3
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
#
# android/make-launcher-icons.py -- forge the RESONANTIA launcher icons
#   from the approved emblem (assets/logo.webp).
#
# EPIGRAPH: "Every man, woman, and child is a star." -- Liber AL, I:3 (his reading)
# DATE:     Sol in Libra, 2026 e.v.
#
# HYPOTHESIS: the installed APK shows Android's placeholder glyph because
#   the manifest declares no android:icon and res/ holds no mipmap
#   drawables -- the emblem only ships inside the WebView UI
#   (assets/www/logo.webp), which the launcher never reads.
# METHOD:    1) Resize the 1600x1600 emblem to the five legacy launcher
#               densities (48/72/96/144/192 px) as ic_launcher.png.
#            2) Build adaptive-icon foregrounds: the emblem at 72dp,
#               centered on a transparent 108dp canvas, per density --
#               the circular mandala then sits inside the 66dp safe
#               circle the launcher masks to.
#            3) Emit mipmap-anydpi-v26/ic_launcher.xml (adaptive icon:
#               deep-purple background + emblem foreground) and
#               values/colors.xml carrying the background color.
#            4) The manifest edit (android:icon / android:roundIcon on
#               <application>) is a separate, audited step -- this
#               script writes drawables only.
# OBSERVATION: run once, commit the PNGs; they are static resources,
#   not per-build staging (unlike the Python package + www emblem).
# RESULT:    res/mipmap-*/ic_launcher{,_foreground}.png,
#   res/mipmap-anydpi-v26/ic_launcher.xml, res/values/colors.xml.
#
# MECHANISM: Pillow does the resampling (LANCZOS -- the honest filter
#   for downscaling a detailed mandala); densities follow the Android
#   launcher spec (mdpi=1x baseline, 48dp legacy / 108dp adaptive).
# DOCTRINE:  the emblem is his approved sigil -- this script resizes,
#   never redraws; the artwork's authority stays with the original.
#
# 93 93/93 -- Love is the law, love under will.

"""Forge RESONANTIA launcher icons from assets/logo.webp."""

from pathlib import Path
from PIL import Image

# -- Anchorage: paths -------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent          # ~/workspace/resonance
EMBLEM = REPO / "assets" / "logo.webp"                 # the approved sigil
RES = REPO / "android" / "app" / "src" / "main" / "res"

# -- Doctrine: the Android launcher density ladder ---------------------------
# Legacy icons are 48dp; adaptive layers are 108dp. mdpi is the 1x baseline.
DENSITIES = {  # name: scale factor
    "mdpi": 1,
    "hdpi": 1.5,
    "xhdpi": 2,
    "xxhdpi": 3,
    "xxxhdpi": 4,
}
LEGACY_DP = 48        # classic launcher icon size
ADAPTIVE_DP = 108     # adaptive-icon layer size
FOREGROUND_DP = 72    # emblem diameter -- inside the 66dp safe circle-ish,
                      # close enough for a radially symmetric mandala
BACKGROUND_COLOR = "#24125A"  # the emblem's own indigo field, sampled
                      # from its corner pixel -- the adaptive background
                      # meets the artwork with no visible seam


def main() -> None:
    # MECHANISM: open once; LANCZOS keeps the mandala's fine lines honest
    # at small sizes (no blur-the-truth BOX filter).
    emblem = Image.open(EMBLEM).convert("RGBA")
    assert emblem.size[0] == emblem.size[1], "emblem must be square"

    for name, scale in DENSITIES.items():
        mipmap = RES / f"mipmap-{name}"
        mipmap.mkdir(parents=True, exist_ok=True)

        # 1) Legacy icon: emblem edge-to-edge at 48dp.
        legacy_px = int(LEGACY_DP * scale)
        emblem.resize((legacy_px, legacy_px), Image.LANCZOS).save(
            mipmap / "ic_launcher.png")

        # 2) Adaptive foreground: emblem at 72dp, centered on a
        #    transparent 108dp canvas -- the launcher masks the rest.
        canvas_px = int(ADAPTIVE_DP * scale)
        fg_px = int(FOREGROUND_DP * scale)
        canvas = Image.new("RGBA", (canvas_px, canvas_px), (0, 0, 0, 0))
        small = emblem.resize((fg_px, fg_px), Image.LANCZOS)
        canvas.alpha_composite(small, ((canvas_px - fg_px) // 2,) * 2)
        canvas.save(mipmap / "ic_launcher_foreground.png")

    # 3) Adaptive-icon descriptor (API 26+; his Galaxy A16 uses this path).
    anydpi = RES / "mipmap-anydpi-v26"
    anydpi.mkdir(parents=True, exist_ok=True)
    (anydpi / "ic_launcher.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@color/ic_launcher_background"/>\n'
        '    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n'
        '</adaptive-icon>\n')

    # 4) The background color the adaptive icon stands on.
    values = RES / "values"
    values.mkdir(parents=True, exist_ok=True)
    (values / "colors.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<resources>\n'
        f'    <color name="ic_launcher_background">{BACKGROUND_COLOR}</color>\n'
        '</resources>\n')

    print("icons forged:",
          sorted(p.name for p in RES.glob("mipmap-mdpi/*")),
          "+ mipmap-anydpi-v26/ic_launcher.xml + values/colors.xml")


if __name__ == "__main__":
    main()
