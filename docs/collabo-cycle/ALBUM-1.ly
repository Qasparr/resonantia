\version "2.26.0"

% =====================================================================
% CROWN FIRE SEASON - SONGBOOK (hook melodies with chords)
% The Five-Album Collabo Cycle - Album I
% All nine hook melodies are original desk compositions, composed
% for the lyric drafts in ALBUM-1.md - the same melodies notated
% in ALBUM-1.abc. Composition drafts under the Flagpole, not
% transcriptions of any recording.
% Spec: Detroit bounce trap, 144 BPM, A major.
% Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe,
% ARR, All Rights Reserved, Without Prejudice.
% =====================================================================

\header {
  title = "CROWN FIRE SEASON — Sheet Music (MAGVS)"
  subtitle = "The Five-Album Collabo Cycle · Album I"
  composer = "Words & music under the Flagpole of Qasparr"
  tagline = "Hook melodies and chords — desk compositions for the ghost-draft lyrics (ALBUM-1.md / ALBUM-1.abc)"
}

\paper {
  #(set-paper-size "letter")
}

global = {
  \key a \major
  \time 4/4
  \tempo 4 = 144
}

% ---------------------------------------------------------------------
% Track 1 — Season Opener
% Writing seat: SOL REY · Hook sung by Qveen Bee (feature)
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        a1 fis:m1 d1 e1 a1 fis:m1 d2 e2 a1
      }
    }
    \new Staff {
      \global
      \clef treble
      e'8 e'8 a'8 a'8 b'8 cis''8 d''4 |
      cis''8 cis''8 a'8 fis'8 a'8 b'8 a'4 |
      d''8 d''8 cis''8 a'8 b'8 cis''8 d''4 |
      b'8 b'8 cis''8 d''8 e''4 b'4 |
      e''8 e''8 d''8 cis''8 b'8 cis''8 d''4 |
      cis''8 b'8 a'8 fis'8 a'8 b'8 cis''4 |
      d''8 d''8 e''8 fis''8 e''8 d''8 b'4 |
      e''8 cis''8 a'8 b'8 a'2 \bar "|."
    }
  >>
  \header { piece = "1. Season Opener" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 2 — Match Head
% Writing seat: ARI SPARKZ · Chant hook; double-time riff in the ABC
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        a1 a1 e1 e1 a1 a1 d2 e2 a1
      }
    }
    \new Staff {
      \global
      \clef treble
      a'8 a'8 a'4 r4 a'4 |
      b'8 b'8 cis''4 r4 b'4 |
      cis''8 cis''8 d''4 r4 cis''4 |
      a'8 a'8 b'4 r4 a'4 |
      a'8 a'8 cis''4 r4 a'4 |
      e''8 e''8 d''4 r4 b'4 |
      d''8 d''8 b'4 r4 cis''4 |
      a'8 a'8 b'4 a'2 \bar "|."
    }
  >>
  \header { piece = "2. Match Head" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 3 — Bow and Arrow
% Writing seat: SAGE ARCHER · Hook sung by Qveen Bee (feature)
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        a1 d1 fis:m1 e1 a1 d1 fis:m2 e2 a1
      }
    }
    \new Staff {
      \global
      \clef treble
      a'4 cis''8 e''8 a''4 e''4 |
      d''4 fis''8 e''8 d''8 cis''8 b'4 |
      cis''4 e''8 cis''8 a'8 b'8 fis'4 |
      b'4 d''8 cis''8 b'8 gis'8 e'4 |
      a'4 cis''8 e''8 a''4 gis''4 |
      fis''4 e''8 d''8 cis''8 b'8 a'4 |
      e''4 d''8 cis''8 b'8 cis''8 a'4 |
      a''8 gis''8 e''8 cis''8 a'2 \bar "|."
    }
  >>
  \header { piece = "3. Bow and Arrow" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 4 — First Through the Door
% Writing seat: SOL REY · Chant hook, all Crown Fire
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        a1 a1 d1 a1 a1 a1 e1 a1
      }
    }
    \new Staff {
      \global
      \clef treble
      a'4 a'4 b'4 a'4 |
      a'4 a'4 cis''4 a'4 |
      d''4 d''4 cis''4 b'4 |
      a'4 b'4 cis''4 a'4 |
      a'4 a'4 b'4 cis''4 |
      e''4 e''4 d''4 b'4 |
      b'4 b'4 d''4 b'4 |
      cis''4 b'4 a'2 \bar "|."
    }
  >>
  \header { piece = "4. First Through the Door" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 5 — Dearborn to Brightmoor
% Writing seat: ARI SPARKZ · Hook sung by Sage Archer; road riff in the ABC
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        a1 e1 fis:m1 d1 a1 e1 d2 e2 a1
      }
    }
    \new Staff {
      \global
      \clef treble
      e'8 a'8 b'8 cis''8 d''8 cis''8 b'4 |
      b'8 cis''8 d''8 e''4 d''8 b'4 |
      cis''4 a'8 b'8 cis''8 d''8 b'4 |
      d''8 e''8 fis''4 e''8 d''8 b'4 |
      e'8 a'8 b'8 cis''8 d''8 cis''8 b'4 |
      e''4 d''8 cis''8 b'8 a'8 b'4 |
      d''4 cis''8 b'8 a'8 gis'8 b'4 |
      cis''8 b'8 a'8 e'8 a'2 \bar "|."
    }
  >>
  \header { piece = "5. Dearborn to Brightmoor" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 6 — Travel Light
% Writing seat: SAGE ARCHER · Hook sung by Qveen Bee (feature lead)
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        a1 d1 a1 e1 fis:m1 d1 a2 e2 a1
      }
    }
    \new Staff {
      \global
      \clef treble
      e'8. a'16 b'8 cis''8 d''8 e''8 d''4 |
      d''8. a'16 b'8 cis''8 d''8 b'8 a'4 |
      cis''8. a'16 b'8 cis''8 b'8 a'8 e'4 |
      b'8. gis'16 b'8 cis''8 d''8 b'8 gis'4 |
      a'8. fis'16 a'8 cis''8 e''8 cis''8 a'4 |
      d''8. fis''16 e''8 d''8 cis''8 b'8 a'4 |
      e''8. cis''16 b'8 cis''8 d''8 e''8 b'4 |
      a'8. e'16 a'8 b'8 cis''4 a'4 \bar "|."
    }
  >>
  \header { piece = "6. Travel Light" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 7 — The Chant
% Writing seat: SOL REY · Call-and-response chant, all Crown Fire
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        a1 a1 fis:m1 d1 a1 a1 e1 a1
      }
    }
    \new Staff {
      \global
      \clef treble
      e'8 e'8 a'8 a'8 r4 e''4 |
      e'8 e'8 a'8 a'8 r4 d''4 |
      a'8 a'8 cis''8 cis''8 b'8 b'8 a'4 |
      d''8 d''8 cis''8 cis''8 b'8 b'8 a'4 |
      e'8 e'8 b'8 b'8 r4 e''4 |
      e'8 e'8 b'8 b'8 r4 d''4 |
      b'8 b'8 d''8 d''8 b'8 b'8 gis'4 |
      e''8 e''8 d''8 b'8 a'2 \bar "|."
    }
  >>
  \header { piece = "7. The Chant" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 8 — Gasoline Confession
% Writing seat: ARI SPARKZ · Hook sung by Qveen Bee; tag-team feature;
% nervous double-time riff in the ABC
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        fis:m1 d1 a1 e1 fis:m1 d1 e1 a1
      }
    }
    \new Staff {
      \global
      \clef treble
      fis'4 a'8 cis''8 b'8 a'8 fis'4 |
      a'4 d''8 cis''8 b'8 a'8 fis'4 |
      e'4 a'8 b'8 cis''8 d''8 b'4 |
      b'4 d''8 cis''8 b'8 gis'8 e'4 |
      fis'4 a'8 cis''8 e''8 cis''8 a'4 |
      fis''4 e''8 d''8 cis''8 b'8 a'4 |
      b'4 cis''8 d''8 e''8 d''8 b'4 |
      e''8 cis''8 a'8 b'8 a'2 \bar "|."
    }
  >>
  \header { piece = "8. Gasoline Confession" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 9 — Crown Fire Season
% Writing seat: ALL THREE · Title track, all voices
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        a1 e1 fis:m1 d1 a1 e1 d2 e2 a1
      }
    }
    \new Staff {
      \global
      \clef treble
      a'4 e''4 a''4 e''4 |
      e''4 d''8 b'8 e''4 b'4 |
      cis''4 fis''8 e''8 d''8 cis''8 a'4 |
      d''4 fis''4 a''4 fis''4 |
      a'4 e''4 a''4 gis''4 |
      e''4 gis''8 e''8 d''8 cis''8 b'4 |
      fis''4 e''8 d''8 b'8 cis''8 d''4 |
      a''8 e''8 cis''8 b'8 a'2 \bar "|."
    }
  >>
  \header { piece = "9. Crown Fire Season" }
  \layout { }
}
