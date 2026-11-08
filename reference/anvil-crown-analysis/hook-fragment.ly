\version "2.26.0"
\header {
  title = "THE ANVIL AND CROWN — Hook Fragment"
  subtitle = "TRANSCRIPTION-ANALYSIS · TOOLCHAIN PROOF — NOT A FINISHED SCORE"
  composer = "Johnathan 'Qasparr' Monroe — generated in Gemini (Lyria)"
  tagline = "Desk engraving proof · 2026-11-08 · audit against the audio before any use"
}
\paper { #(set-paper-size "letter") }
\score {
  <<
    \new ChordNames \chordmode { a1 a a a }
    \new Staff {
      \key a \major \time 4/4 \tempo 4 = 70
      r4. ais'8 r8 a'8 gis'8 ais'8 r8 a8 a8 b'8 r4. b'8 b'8 b'8 r8 b'8 g'8 r4. r4. fis8 e8 cis'8 g'8 r8
    }
  >>
  \layout { }
}
\markup \vspace #2
\markup \wordwrap {
  Caveats, printed on the page by design: measured tempo is 69.8 BPM
  (shown rounded to 70). Chord read: bars 15-16 are per-bar bench
  labels (A); bars 13-14 are UNCLEAR per bar in chords.csv and are
  shown as A on segment-level evidence only (hook unit, medium
  confidence). Melody: machine sketch notes (autocorrelation track,
  confidence >= 0.45) quantised editorially; the A-sharp/B cluster in
  bars 13-14 is flagged in FORM-MAP.md as probable harmony-partial
  tracking, NOT verified lead melody. 0 sketch notes below the confidence floor were omitted from this page and remain in melody-sketch.json.
}
