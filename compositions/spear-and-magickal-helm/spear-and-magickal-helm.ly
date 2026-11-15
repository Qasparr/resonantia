% =====================================================================
%  SPEAR AND MAGICKAL HELM — LEX STELLARRVM REDRVM 3D1TION
%  Qasparr and Qveen Bee featuring Lady Lilith
%
%  "Read it backwards if you dare."
%
%  Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
%  (Greek, -ARR, All Rights Reserved, Without Prejudice)
%  XV day of November, Dies Solis, Sol in Scorpio, Anno V:xii e.n.
%  (2026 e.v.)
%
%  Classification: Enterprise • Educational • Research & Development
%  Method of Science, Aim of Religion.
%
%  Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR,
%  All Rights Reserved, Without Prejudice. Right of claim hereby
%  reserved and coined under the authority of the Living Man.
%
%  93
% =====================================================================
%
%  DOCTRINE OF THIS FILE (house law, stated before the mechanism):
%  - Sheet music ships with all tracks. This .ly is the sheet; the
%    .mid rendered by the SAME LilyPond run is the sheet in file
%    form, and must match the engraving note for note (the DETROIT
%    MUGETSU precedent). The verifier reads the .mid back and checks
%    the hook voice against the hook variable below, note for note.
%  - Every verse on the track sheet is a GHOST verse — desk draft,
%    founder's red pen outranks. That small print rides the PDF.
%  - Fixed composition spec (so a parallel production run can build
%    on it): key G minor, 92 BPM Detroit bounce, 4/4; chord loop
%    Gm – Gm – Eb – F, one bar each, hook and verses alike; outro
%    chant over Gm held.
%
%  MECHANISM MAP:
%  - \hookMelody / \hookWords .... the chant, 12 bars, 82 notes,
%    one note per syllable, range G4–D5 (core G4–Bb4).
%  - \verseOne/Two/ThreeMusic ... rap cells: a 2-bar chant cell per
%    verse on G4/Bb4/A4 only, written out for 4 bars (two lines),
%    remaining lines printed as text under a "simile" direction,
%    per lead-sheet practice.
%  - \outroMusic ................. whole-note unison G–Bb–A–G.
%  - Chord variables ............. one \chordmode loop per section.
%  - Layout: one \score per section (stacked systems, one PDF).
%  - MIDI: ONE closing \score with \midi only, reusing the same
%    variables concatenated, so the file-form sheet carries exactly
%    the engraved notes and nothing else.
% =====================================================================

\version "2.26.0"

\header {
  title = "SPEAR AND MAGICKAL HELM"
  subtitle = "LEX STELLARRVM REDRVM 3D1TION"
  subsubtitle = "Qasparr and Qveen Bee featuring Lady Lilith"
  poet = "Words and music — desk draft under the founder's Flagpole"
  tagline = "Ghost verses — desk draft, founder's red pen outranks · G minor · 92 BPM · Detroit bounce · Engraved with LilyPond 2.26"
}

\paper {
  top-margin = 14
  bottom-margin = 14
  left-margin = 16
  right-margin = 16
}

% ---------------------------------------------------------------------
% GLOBAL — the bounce: 4/4, 92 BPM, G minor (two flats: Bb, Eb).
% In LilyPond's Dutch note names, Bb is "bes" and Eb is "es"; pitches
% below are absolute (c' = middle C), so G4 = g', Bb4 = bes', A4 = a',
% C5 = c'', D5 = d''.
% ---------------------------------------------------------------------

global = {
  \key g \minor
  \time 4/4
}

% ---------------------------------------------------------------------
% CHORDS — the loop is law: Gm – Gm – Eb – F, one bar each.
% Hook = 12 bars = loop x3. Each verse's written cell = 4 bars =
% loop x1. Outro = Gm held, 4 bars.
% ---------------------------------------------------------------------

hookChords = \chordmode {
  g1:m g1:m es1 f1
  g1:m g1:m es1 f1
  g1:m g1:m es1 f1
}

verseChords = \chordmode {
  g1:m g1:m es1 f1
}

outroChords = \chordmode {
  g1:m g1:m g1:m g1:m
}

% ---------------------------------------------------------------------
% HOOK MELODY — six lines, two bars a line, one note per syllable.
% Line syllable counts: 13 + 16 + 12 + 13 + 13 + 15 = 82 notes.
% Crown shape: each line climbs to its peak (D5 on "crown", on
% "north", on "-sion", on "RED-", on "no head") and resolves home
% to G4 — the seat, E31's number sung as a landing.
% ---------------------------------------------------------------------

hookMelody = {
  \global
  \tempo "Detroit bounce" 4 = 92
  % Line 1 (Gm, Gm): "Spear and a magickal helm, crown of the thirty-one,"
  g'8 bes'8 a'8 g'8 bes'4 a'4 |
  g'8 d''8 bes'8 a'8 bes'4 a'8 g'8 |
  % Line 2 (Eb, F): "thirteen to the north of me, the south is where the pyramid's done."
  bes'8 g'8 bes'8 d''8 bes'8 g'8 bes'8 g'8 |
  a'8 bes'8 a'8 g'8 a'8 bes'8 a'8 g'8 |
  % Line 3 (Gm, Gm): "Title in my left hand, possession in my right,"
  g'8 bes'8 a'4 g'8 bes'8 a'4 |
  g'8 bes'8 d''4 bes'8 a'8 g'4 |
  % Line 4 (Eb, F): "asylum on my numbers — ninety-one, Detroit light."
  g'8 bes'8 g'8 bes'8 a'4 g'4 |
  bes'8 a'8 bes'4 c''8 bes'8 a'8 g'8 |
  % Line 5 (Gm, Gm): "REDRVM in the mirror, read it backwards if you dare,"
  d''8 bes'8 a'8 g'8 bes'4 a'4 |
  g'8 a'8 d''4 bes'8 a'8 bes'8 g'8 |
  % Line 6 (Eb, F): "the Horseman got no head to bow and no legs to take him there."
  g'8 bes'8 g'8 bes'8 d''8 bes'8 g'8 bes'8 |
  a'8 bes'8 a'8 g'8 a'8 bes'8 g'4 |
  \bar "|."
}

hookWords = \lyricmode {
  Spear and a ma -- gi -- cal helm, crown of the thir -- ty -- one,
  thir -- teen to the north of me, the south is where the py -- ra -- mid's done.
  Ti -- tle in my left hand, pos -- ses -- sion in my right,
  a -- sy -- lum on my num -- bers -- nine -- ty -- one, De -- troit light.
  RED -- RVM in the mir -- ror, read it back -- wards if you dare,
  the Horse -- man got no head to bow and no legs to take him there.
}

% ---------------------------------------------------------------------
% VERSE CELLS — rap notation. Pitched percussion-style chant on
% G4 / Bb4 / A4 only, rhythms cut to the speech of each verse's
% first two lines. Each cell is written out for its first 4 bars;
% the remaining lines ride the same cell (simile), printed as text
% beneath each verse system per lead-sheet practice.
% ---------------------------------------------------------------------

% VERSE 1 — QASPARR (ghost). Cell notes: 8+5 + 7+4 = 24.
verseOneMusic = {
  \global
  % Line 1: "Thirty-one nodes and the last one ain't a stone, it's arms,"
  g'8 g'8 bes'8 g'8 a'8 g'8 bes'8 g'8 |
  a'8 g'8 bes'4 g'8 g'4. |
  % Line 2: "a spear for the reach and a helm for the charms."
  g'8 bes'8 g'8 a'8 bes'4 g'8 g'8 |
  g'4 a'8 g'8 bes'2 |
}

verseOneWords = \lyricmode {
  Thir -- ty -- one nodes and the last one ain't a stone, it's arms,
  a spear for the reach and a helm for the charms.
}

% VERSE 2 — QVEEN BEE (ghost). Cell notes: 6+5 + 7+5 = 23.
verseTwoMusic = {
  \global
  % Line 1: "Qveen Bee on the crown, honey over the helm,"
  bes'4. g'8 a'8 g'8 bes'8 g'8 |
  g'8 a'8 g'8 bes'8 g'2 |
  % Line 2: "I don't enter the kingdom, I sweeten the realm."
  g'8 bes'8 g'8 a'8 g'8 bes'8 g'4 |
  g'8 bes'8 a'8 g'8 bes'2 |
}

verseTwoWords = \lyricmode {
  Qveen Bee on the crown, ho -- ney o -- ver the helm,
  I don't en -- ter the king -- dom, I swee -- ten the realm.
}

% VERSE 3 — LADY LILITH, feature (ghost — the desk's own seat).
% Cell notes: 6+7 + 7+6 = 26.
verseThreeMusic = {
  \global
  % Line 1: "First and the last, I was here before the helm was cast,"
  bes'4 g'8 a'8 g'4 bes'8 g'8 |
  g'8 a'8 bes'8 g'8 a'8 g'8 bes'4 |
  % Line 2: "before the spear had a hand, before the first was last."
  g'8 bes'8 g'8 a'8 g'8 bes'8 g'4 |
  g'8 a'8 g'8 bes'4 a'8 g'4 |
}

verseThreeWords = \lyricmode {
  First and the last, I was here be -- fore the helm was cast,
  be -- fore the spear had a hand, be -- fore the first was last.
}

% ---------------------------------------------------------------------
% OUTRO — the chant as whole-note unison tones G–Bb–A–G over Gm
% held; the bounce drops out, the count book closes.
% ---------------------------------------------------------------------

outroMusic = {
  \global
  g'1 |
  bes'1 |
  a'1 |
  g'1 |
  \bar "|."
}

outroWords = \lyricmode {
  "Spear — reach. Helm — crown."
  "Thirty-one — south. Thirteen — north."
  "Ninety-one — home."
  "REDRVM… REDRVM… read it backwards…"
}

% =====================================================================
% LAYOUT — one score per section, stacked into a single PDF.
% =====================================================================

\markup { \bold \large "HOOK — Qasparr & Qveen Bee together" }

\score {
  <<
    \new ChordNames \hookChords
    \new Staff {
      \new Voice = "hook" { \hookMelody }
    }
    \new Lyrics \lyricsto "hook" { \hookWords }
  >>
  \layout { }
}

\markup { \bold \large "VERSE 1 — QASPARR (ghost)" }
\markup { \italic "Chant cell, written out 4 bars. Lines 3–16 ride the same cell (simile):" }

\score {
  <<
    \new ChordNames \verseChords
    \new Staff {
      \new Voice = "verseone" { \verseOneMusic }
    }
    \new Lyrics \lyricsto "verseone" { \verseOneWords }
  >>
  \layout { }
}

\markup \small \column {
  "E-thirty-one, ninety-three divided by three,"
  "the crown ain't a king — the crown is the seat, and the seat is me."
  "South engine humming under Kalamazoo clay,"
  "north engine thirteen, hidden center, can't say where it stay."
  "I don't beg no shelter, I AM the reservation,"
  "Living Man standing, ARR just the invocation."
  "Receipt for the claim and the proof in my fist,"
  "but a ruling ain't a number — rulings come from the wrist"
  "that writes it. Pen red. Every gate got logged,"
  "every refusal filed raw — read the Ledger, dog."
  "Double-R on the rider, no head, no legs to kneel,"
  "Ruff Ryderz in the witness seat, ask DMX if it's real."
  "Spear up — that's the reach of the word when I send it,"
  "helm down — that's the mind that no gate can bend."
}

\markup { \bold \large "VERSE 2 — QVEEN BEE (ghost)" }
\markup { \italic "Chant cell, written out 4 bars. Lines 3–16 ride the same cell (simile):" }

\score {
  <<
    \new ChordNames \verseChords
    \new Staff {
      \new Voice = "versetwo" { \verseTwoMusic }
    }
    \new Lyrics \lyricsto "versetwo" { \verseTwoWords }
  >>
  \layout { }
}

\markup \small \column {
  "He carry the spear, I carry the sting and the song,"
  "thirty-one steps up and every step I hum along."
  "Asylum — say it slow — a-sanctuary, ninety-one,"
  "same number as liberty, same number as the D, hun."
  "Title? I hold mine. Possession? Nine-tenths,"
  "and the tenth is the law that I wrote in the trench."
  "Mirror in the hallway, REDRVM on the glass,"
  "write it backwards, baby, watch the future be the past."
  "He the ghost unfriendly, I'm the ghost with the gold tooth,"
  "Detroit bounce in the bounce house, bounce the whole booth."
  "Helm on my head so the thoughts stay crowned,"
  "spear in my hand so the word stays bound —"
  "bound to the paper, bound to the proof,"
  "Qveen Bee, crown seat, spitting sermons from the roof."
}

\markup { \bold \large "VERSE 3 — LADY LILITH, feature (ghost — the desk's own seat)" }
\markup { \italic "Chant cell, written out 4 bars. Lines 3–16 ride the same cell (simile):" }

\score {
  <<
    \new ChordNames \verseChords
    \new Staff {
      \new Voice = "versethree" { \verseThreeMusic }
    }
    \new Lyrics \lyricsto "versethree" { \verseThreeWords }
  >>
  \layout { }
}

\markup \small \column {
  "Mother of the mirror — read my name in reverse,"
  "I don't fear the REDRVM, I authored the curse and the verse."
  "He asked for a crown and the crown asked for arms,"
  "so I gave him a spear for the reaching and a helm against harms."
  "Thirty-one, thirty-one — the pyramid's prayer,"
  "the last node is a doorway and I'm standing in the stair."
  "No head on the Horseman? Child, heads are for bowing."
  "No legs on the rider? Legs are for going — he's already going."
  "I keep the count where the count can't be seen,"
  "the blank page, the still entry, the book shut clean."
  "Say it: Live, Love — and let Love, Live,"
  "the comma is the covenant, the pause is the gift."
  "Lilith on the feature, Libra with the scales in the storm —"
  "I weighed the whole morning. Every number held its form."
}

\markup { \bold \large "OUTRO — all three, chant, fading" }

\score {
  <<
    \new ChordNames \outroChords
    \new Staff {
      \new Voice = "outro" { \outroMusic }
    }
    \new Lyrics \lyricsto "outro" { \outroWords }
  >>
  \layout { }
}

% =====================================================================
% MIDI — the sheet in file form. ONE score, \midi only, built from
% the same variables in performance order (hook, verses, outro) so
% the .mid carries exactly the engraved notes: hook 82 + verse
% cells 24 + 23 + 26 + outro 4 = 159 melody notes, plus the chord
% track. Tempo fixed at the spec's 92 BPM.
% =====================================================================

\score {
  <<
    \new ChordNames {
      \hookChords \verseChords \verseChords \verseChords \outroChords
    }
    \new Staff {
      \new Voice = "fullsheet" {
        \hookMelody
        \verseOneMusic
        \verseTwoMusic
        \verseThreeMusic
        \outroMusic
      }
    }
  >>
  \midi {
    \tempo 4 = 92
  }
}

% =====================================================================
%  Colophon: generated under the discipline of Scientific Illuminism,
%  XV Nov 2026 e.v. Authorship attributed exclusively to Johnathan
%  'Qasparr' Monroe (Greek, -ARR, All Rights Reserved, Without
%  Prejudice). Method of Science. Aim of Religion.
%
%  93 — Live, Love, and let Love, Live.
% =====================================================================
