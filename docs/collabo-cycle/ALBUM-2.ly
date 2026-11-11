\version "2.26.0"

% =====================================================================
% UNDERCURRENT - SONGBOOK (hook melodies with chords)
% The Five-Album Collabo Cycle - Album II
% All nine hook melodies are original desk compositions, composed
% for the lyric drafts in ALBUM-2.md - the same melodies notated
% in ALBUM-2.abc. Composition drafts under the Flagpole, not
% transcriptions of any recording.
% Spec: Deep Detroit bounce, 92 BPM, D minor. Sigma 13 Hz.
% Harmonica wail on Tracks 2 and 8 only.
% Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe,
% ARR, All Rights Reserved, Without Prejudice.
% =====================================================================

\header {
  title = "UNDERCURRENT — Sheet Music (MAGVS)"
  subtitle = "The Five-Album Collabo Cycle · Album II"
  composer = "Words & music under the Flagpole of Qasparr"
  tagline = "Hook melodies and chords — desk compositions for the ghost-draft lyrics (ALBUM-2.md / ALBUM-2.abc)"
}

\paper {
  #(set-paper-size "letter")
}

global = {
  \key d \minor
  \time 4/4
  \tempo 4 = 92
}

% ---------------------------------------------------------------------
% Track 1 — Still Water
% Writing seat: NOIR (Scorpio - VENOM) · Qasparr feature verse opens under the surface - Noir carries the body - Qveen Bee feature hook, sung
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        d:m1 bes1 d:m1 c1 d:m1 bes1 f1 d:m1
      }
    }
    \new Staff {
      \global
      \clef treble
      a'8 a'8 d'8 d'8 f'8 e'8 d'4 |
      f'8 f'8 g'8 a'8 g'8 f'4. |
      a'8 a'8 d'8 e'8 f'8 e'4. |
      e'8 e'8 f'8 g'8 a'4 g'4 |
      a'8 a'8 d'8 d'8 f'8 e'8 d'4 |
      f'8 f'8 g'8 a'8 g'8 f'4. |
      a'8 a'8 c''8 a'8 g'8 f'4. |
      e'8 d'8 c'8 d'4 d'4. \bar "|."
    }
  >>
  \header { piece = "1. Still Water" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 2 — 3 A.M. Tide
% Writing seat: LULLABY LUX (Pisces - DEPTH) · Qveen Bee sung lead (feature) - HARMONICA WAIL, track 1 of 2
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        d:m1 g:m1 bes1 c1 d:m1 g:m1 f1 d:m1
      }
    }
    \new Staff {
      \global
      \clef treble
      d'8 d'8 e'8 f'8 e'8 d'4. |
      g'8 g'8 a'8 g'8 f'8 e'4. |
      f'8 f'8 g'8 a'8 bes'4 a'4 |
      a'8 a'8 g'8 e'8 c'4 d'4 |
      d'8 d'8 e'8 f'8 g'8 a'4. |
      g'8 a'8 bes'8 a'8 g'8 f'4. |
      a'8 c''8 a'8 g'8 f'8 e'4. |
      f'8 e'8 d'8 c'8 d'2 \bar "|."
    }
  >>
  \header { piece = "2. 3 A.M. Tide" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 3 — The Ledger
% Writing seat: HARBOR JUNE (Cancer - MEMORY) · Qasparr storytelling feature - Qveen Bee sung hook
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        d:m1 d:m1 f1 c1 d:m1 bes1 f1 d:m1
      }
    }
    \new Staff {
      \global
      \clef treble
      a'8 a'8 a'8 d'8 a'8 a'4. |
      a'8 a'8 d'8 e'8 d'8 c'4. |
      f'8 f'8 f'8 a'8 g'8 f'4. |
      e'8 e'8 g'8 e'8 c'4 d'4 |
      a'8 a'8 a'8 d'8 a'8 a'4. |
      f'8 f'8 a'8 g'8 f'8 e'4. |
      f'8 g'8 a'8 c''8 a'8 g'4. |
      f'8 e'8 d'8 e'8 d'2 \bar "|."
    }
  >>
  \header { piece = "3. The Ledger" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 4 — Venom in Velvet
% Writing seat: NOIR (Scorpio - VENOM) · Noir carries the body - Qveen Bee feature rap verse leads the middle - Noir hook, whispered
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        d:m1 d:m1 bes1 c1 d:m1 g:m1 f1 d:m1
      }
    }
    \new Staff {
      \global
      \clef treble
      d'8 d'8 f'8 e'8 d'8 c'4. |
      d'8 e'8 f'8 g'8 f'8 e'4. |
      f'8 g'8 a'8 g'8 f'8 e'4. |
      e'8 f'8 g'8 a'8 g'4 e'4 |
      d'8 d'8 f'8 e'8 d'8 c'4. |
      g'8 g'8 a'8 bes'8 a'8 g'4. |
      a'8 g'8 f'8 e'8 d'8 c'4. |
      d'8 e'8 f'8 e'8 d'2 \bar "|."
    }
  >>
  \header { piece = "4. Venom in Velvet" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 5 — Drown the Chorus
% Writing seat: LULLABY LUX (Pisces - DEPTH) · Both headliners, sung - Qasparr feature verse - Lullaby Lux sung-rap close
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        d:m1 bes1 d:m1 c1 d:m1 bes1 f1 d:m1
      }
    }
    \new Staff {
      \global
      \clef treble
      a'8 c''8 a'8 g'8 f'8 e'4. |
      f'8 g'8 a'8 g'8 f'8 e'4. |
      d'8 e'8 f'8 g'8 a'4 g'4 |
      e'8 d'8 c'8 d'8 e'4 c'4 |
      a'8 c''8 d''8 c''8 a'8 g'4. |
      f'8 g'8 a'8 bes'8 a'4 g'4 |
      a'8 g'8 f'8 e'8 d'8 c'4. |
      d'8 c'8 d'8 e'8 d'2 \bar "|."
    }
  >>
  \header { piece = "5. Drown the Chorus" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 6 — Names and Dates
% Writing seat: HARBOR JUNE (Cancer - MEMORY) · Memory roll-call - Qasparr feature verse - Qveen Bee sung hook
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        d:m1 d:m1 f1 c1 d:m1 bes1 f1 d:m1
      }
    }
    \new Staff {
      \global
      \clef treble
      d'8 d'8 d'8 e'8 f'8 e'4. |
      d'8 d'8 d'8 e'8 d'8 c'4. |
      f'8 f'8 f'8 g'8 a'8 g'4. |
      e'8 e'8 e'8 f'8 g'4 e'4 |
      d'8 d'8 d'8 e'8 f'8 e'4. |
      f'8 f'8 f'8 g'8 a'4 f'4 |
      a'8 a'8 g'8 f'8 e'8 d'4. |
      e'8 f'8 e'8 d'8 d'2 \bar "|."
    }
  >>
  \header { piece = "6. Names and Dates" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 7 — Pressure
% Writing seat: NOIR (Scorpio - VENOM) · Tag-team Qasparr + Qveen Bee - hook: Noir, with Lullaby Lux & Harbor June undercurrent
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        d:m1 d:m1 bes1 c1 d:m1 g:m1 f1 d:m1
      }
    }
    \new Staff {
      \global
      \clef treble
      d'8 e'8 f'8 g'8 a'8 g'4. |
      a'8 a'8 g'8 f'8 e'8 d'4. |
      f'8 g'8 a'8 bes'8 c''4 a'4 |
      c''8 a'8 g'8 f'8 e'4 d'4 |
      d'8 e'8 f'8 g'8 a'8 c''4. |
      d''8 c''8 bes'8 a'8 g'8 f'4. |
      a'8 c''8 d''8 c''8 a'4 g'4 |
      a'8 g'8 f'8 e'8 d'2 \bar "|."
    }
  >>
  \header { piece = "7. Pressure" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 8 — Moon over the Strait
% Writing seat: LULLABY LUX (Pisces - DEPTH) · Qveen Bee soprano closer-form (feature) - HARMONICA WAIL, track 2 of 2
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        d:m1 bes1 f1 c1 d:m1 g:m1 f1 d:m1
      }
    }
    \new Staff {
      \global
      \clef treble
      a'8 c''8 d''8 e''8 d''8 c''4. |
      d''8 c''8 bes'8 a'8 g'4 f'4 |
      a'8 c''8 f''8 e''8 d''8 c''4. |
      e''8 d''8 c''8 a'8 g'4 e'4 |
      a'8 c''8 d''8 e''8 f''4 e''4 |
      d''8 e''8 f''8 d''8 c''8 a'4. |
      c''8 d''8 e''8 f''8 e''4 d''4 |
      c''8 a'8 f'8 e'8 d'2 \bar "|."
    }
  >>
  \header { piece = "8. Moon over the Strait" }
  \layout { }
}

% ---------------------------------------------------------------------
% Track 9 — Undercurrent
% Writing seat: ALL THREE (Noir - Lullaby Lux - Harbor June) · Title track, all voices - Qveen Bee sung hook + reprise (same melody)
% ---------------------------------------------------------------------
\score {
  <<
    \new ChordNames {
      \chordmode {
        d:m1 bes1 f1 c1 d:m1 g:m1 f1 d:m1
      }
    }
    \new Staff {
      \global
      \clef treble
      d'8 f'8 a'8 d''8 c''8 a'4. |
      bes'8 a'8 g'8 f'8 e'4 d'4 |
      f'8 a'8 c''8 a'8 g'8 f'4. |
      e'8 g'8 c''8 a'8 g'4 e'4 |
      d'8 f'8 a'8 d''8 c''4 a'4 |
      g'8 bes'8 d''8 c''8 bes'4 a'4 |
      a'8 c''8 d''8 e''8 d''4 c''4 |
      d''8 c''8 a'8 f'8 d'2 \bar "|."
    }
  >>
  \header { piece = "9. Undercurrent" }
  \layout { }
}
