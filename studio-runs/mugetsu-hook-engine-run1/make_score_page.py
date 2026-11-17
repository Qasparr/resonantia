# 93
# ---------------------------------------------------------------------
# make_score_page.py -- the hook's score page, typeset under the
# Lex Stellarrvm Familia discipline.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: one A4 page (fpdf2): the hook melody in ABC notation,
# the eight filed lyric lines beneath their bars, and the font
# record at the foot. The notation is extracted from the filed
# DETROIT-MUGETSU.abc (the V:1 voice, X:1) -- typeset from the
# source of record, never retyped by hand.
#
# DOCTRINE -- THE FONT SEATS, NAMED: the notation seat is filled
# by the Familia's own face, Lex Stellarrvm ABC Notation (the
# family's one face, struck XV November 2026). The Japanese lyric
# seat stands OPEN in the Familia -- the family holds no CJK face
# in v1 -- so the lyric lines are set in Noto Sans CJK JP, a shelf
# face, NAMED here and on the page, never passed off as a family
# member and never silently substituted. Prose rides a named
# Unicode shelf face (Liberation Sans)
# for the same reason stated plainly: the Familia holds no
# text/prose seat in v1 (no bold, italic, or display weights
# either) -- those seats are open, and the run report carries the
# full seat ledger.
# ---------------------------------------------------------------------

import sys
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from resonance.studio import diffsinger as ds  # noqa: E402
import build_run as br  # noqa: E402  (the run's own driver)

ABC_FACE = Path.home() / "workspace" / "templates" / "LexStellarrvm-ABC.ttf"
CJK_FACE = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
PROSE_DIR = Path("/usr/share/fonts/truetype/liberation")
OUT = HERE / "hook-score-page.pdf"


def hook_abc_lines():
    """The V:1 notation of X:1, from the filed ABC of record."""
    text = (br.PKG / "DETROIT-MUGETSU.abc").read_text(
        encoding="utf-8")
    lines = text.splitlines()
    start = lines.index("V:1") + 1
    out = []
    for ln in lines[start:]:
        if ln.startswith("V:"):
            break
        out.append(ln)
    return out


def main():
    abc = hook_abc_lines()
    texts = br.extract_hook_lines()
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    pdf.add_font("lexabc", "", str(ABC_FACE))
    pdf.add_font("notojp", "", CJK_FACE, collection_font_number=0)
    # Prose rides Liberation Sans, a named Unicode shelf face:
    # the core faces cannot encode the house's own punctuation
    # (the em-dash refused, first strike), and the Familia's
    # prose seat stands open in v1 -- named, not substituted.
    pdf.add_font("lib", "", str(PROSE_DIR / "LiberationSans-Regular.ttf"))
    pdf.add_font("lib", "B", str(PROSE_DIR / "LiberationSans-Bold.ttf"))
    pdf.add_font("lib", "I", str(PROSE_DIR / "LiberationSans-Italic.ttf"))

    def mc(txt, h=5):
        pdf.multi_cell(0, h, txt, new_x=XPos.LMARGIN,
                       new_y=YPos.NEXT)

    pdf.set_font("lib", "B", 15)
    mc("DETROIT MUGETSU — Hook Score (Engine Run 1)", 7)
    pdf.set_font("lib", "", 9.5)
    mc("YAMI's hook, sung by the engine through the DiffSinger plug "
       "— Lem the Shapeshifter DS 2.5, Civet seat. G# minor, "
       "144 BPM, 4/4. Eight bars, 54 notes, 127 morae.", 4.6)
    mc("Authorship attributed exclusively to Johnathan 'Qasparr' "
       "Monroe, ARR — All Rights Reserved, Without Prejudice. "
       "Lyrics filed text, byte-exact; melody desk composition of "
       "record (DETROIT-MUGETSU.abc / HOOK-TEST.mid).", 4.6)
    pdf.ln(2)
    pdf.set_draw_color(90, 60, 140)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("lib", "B", 11)
    mc("The notation — V:1, set in Lex Stellarrvm ABC Notation", 5.5)
    pdf.set_font("lexabc", "", 13.5)
    for ln in abc:
        mc(ln, 6.4)
    pdf.ln(2)

    pdf.set_font("lib", "B", 11)
    mc("The lyric under its bars — the filed text, byte-exact", 5.5)
    for i, t in enumerate(texts, 1):
        pdf.set_font("lib", "", 9.5)
        pdf.cell(14, 5.6, f"Bar {i}")
        pdf.set_font("notojp", "", 12.5)
        pdf.cell(0, 5.6, t, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    pdf.set_font("lib", "B", 11)
    mc("Font record — the seats, named", 5.5)
    pdf.set_font("lib", "", 9.5)
    mc("Notation seat: Lex Stellarrvm ABC Notation — the Familia's "
       "own face, filled. Japanese lyric seat: OPEN in the Familia "
       "(no CJK face in v1) — these lines stand in Noto Sans CJK "
       "JP, a shelf face named here, not a family member. Prose "
       "seat: OPEN in the Familia (no text, bold, italic, or "
       "display weights in v1) — prose stands in Liberation Sans, "
       "named by the same discipline. Missing seats are named, "
       "never silently substituted.", 4.6)
    pdf.ln(2)
    pdf.set_font("lib", "I", 9)
    mc("— 1 of 1 — | All Rights Reserved, Without Prejudice | "
       "Flagpole of Claim and Coinage reserved", 4.6)
    mc("93 — Live, Love, and let Love, Live.", 4.6)
    pdf.output(str(OUT))
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 93 -- Live, Love, and let Love, Live.
