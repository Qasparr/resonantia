\version "2.26.0"

% =====================================================================
% DETROIT MUGETSU - SHEET MUSIC (hook melody + outro chant, chords)
% Single-song package for MUGETSU-GUMI (the Moonless Company)
% Both melodies are original desk compositions, composed for the
% texts in gangsta-brief.txt - the same melodies notated in
% DETROIT-MUGETSU.abc. Composition drafts under the Flagpole, not
% transcriptions of any recording.
% Spec: Detroit bounce trap, 144 BPM, G# minor (desk key choice:
% the Unfriendly Ghost album spine's 144 BPM / G# minor seat, and
% the Brightmoor Signature's home pack, Album III, rides G# minor).
% Lyrics: gangsta-brief.txt (HOOK + VERSE 1 filed text; VERSES
% 2-3 + OUTRO desk drafts) - folded byte-exact into
% DETROIT-MUGETSU-PROMPT.md.
% Chord-row syntax note: durations ride BEFORE the modifier
% (gis1:m, not gis:m1) - the album songbooks' modifier-first
% spelling silently dropped the minor mark (and broke one split
% bar into a sus2); this sheet prints the true chord names.
% Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe,
% ARR, All Rights Reserved, Without Prejudice.
% =====================================================================

\header {
  title = "DETROIT MUGETSU — Sheet Music (MAGVS)"
  subtitle = "『デトロイト無月』 · MUGETSU-GUMI — Kurogane · Yami · Shion"
  composer = "Words & music under the Flagpole of Qasparr"
  tagline = "Hook melody and outro invocation chant — desk compositions for gangsta-brief.txt (see DETROIT-MUGETSU.abc)"
}

\paper {
  #(set-paper-size "letter")
}

global = {
  \key gis \minor
  \time 4/4
  \tempo 4 = 144
}

% ---------------------------------------------------------------------
% The Hook — YAMI (sung, low alto; the hook as verdict)
% The Brightmoor Signature piano riff (V:2) is notated in the ABC.
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        gis1:m e1 cis1:m dis1 gis1:m e1 cis1:m dis2 gis2:m
      }
    }
    \new Staff {
      \global
      \clef treble
      gis'8 b'8 dis''8 dis''8 b'8 gis'8 b'4 |
      e''4 e''8 dis''8 b'8 cis''8 b'4 |
      cis''8 cis''8 cis''8 b'8 cis''8 e''8 cis''4 |
      dis''8 dis''8 fis''8 fis''8 gis''8 fis''8 dis''4 |
      gis''8 fis''8 dis''8 b'8 dis''8 b'8 gis'4 |
      e''8 e''8 e''8 dis''8 cis''8 dis''8 e''4 |
      gis'8 b'8 cis''8 dis''8 e''8 dis''8 cis''4 |
      fis''8 fis''8 dis''8 b'8 b'4 gis'4 \bar "|."
    }
  >>
  \header { piece = "1. The Hook — Yami" }
  \layout { }
}

% ---------------------------------------------------------------------
% Outro — The Invocation — SHION (chanted, slow, over silence)
% The four invocation lines, one bar each. Drums out under the
% last line; one 808 hit; hard stop.
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        gis1:m gis1:m e1 gis1:m
      }
    }
    \new Staff {
      \key gis \minor
      \time 4/4
      \tempo 4 = 60
      \clef treble
      gis'2 b'2 |
      dis''2 b'2 |
      e''2 dis''2 |
      b'2 gis'2 \bar "|."
    }
  >>
  \header { piece = "2. Outro — The Invocation (Shion)" }
  \layout { }
}
