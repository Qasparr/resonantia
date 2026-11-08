# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# SPDX-License-Identifier: AGPL-3.0-only
"""
tests/test_tools_wing.py -- script-style tests for the Tools Wing:
resonance.grid, resonance.tempo, resonance.repair, resonance.vocal.

Run:  python3 tests/test_tools_wing.py   (from the repo root)
   or python3 -m pytest tests/test_tools_wing.py

Style: each test prints "  ok: <name>"; the end prints
"<N> tools-wing tests passed." Any failure raises immediately.
Ground truth is synthetic throughout -- known sines, known clicks,
known contours -- the only honest ground truth without a corpus.
The assertions measure what the module docstrings claim, in the
units the docstrings claim them in.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resonance import grid, repair, tempo, vocal

PASSED = 0
SR = 44100


def check(name, fn):
    """Run one test; print ok or raise."""
    global PASSED
    fn()
    PASSED += 1
    print(f"  ok: {name}")


def sine(freq, dur_s, sr=SR, amp=0.5):
    t = np.arange(int(dur_s * sr)) / sr
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float64)


def harmonic_stack(f0, dur_s, sr=SR, n_harm=8, amp=0.5):
    t = np.arange(int(dur_s * sr)) / sr
    x = np.zeros_like(t)
    for k in range(1, n_harm + 1):
        x += (amp / k) * np.sin(2 * np.pi * f0 * k * t)
    return x


def dominant_freq(x, sr):
    mag = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    freqs = np.fft.rfftfreq(len(x), 1.0 / sr)
    return freqs[int(np.argmax(mag[1:])) + 1]


# ------------------------------------------------------------- grid

def t_grid_exact_beat_math():
    assert grid.samples_per_beat(120.0, 48000) == 24000.0
    assert grid.samples_per_bar(120.0, 48000) == 96000.0
    assert grid.bars_to_samples(4, 120.0, 48000) == 384000
    # The 93 BPM case from the docstring: one rounding, at the total.
    assert grid.bars_to_samples(4, 93.0, 48000) == 495484


def t_grid_bad_tempo_refused():
    for fn in (lambda: grid.samples_per_beat(0.0, SR),
               lambda: grid.samples_per_beat(120.0, 0),
               lambda: grid.fit_loop_to_bars(np.zeros(10), -5.0, SR)):
        try:
            fn()
        except ValueError:
            continue
        raise AssertionError("non-positive tempo/sr not refused")


def t_grid_fit_trim_pad_nearest():
    bar = grid.bars_to_samples(1, 120.0, SR)  # 22050
    x = np.ones(int(1.5 * bar))
    trimmed = grid.fit_loop_to_bars(x, 120.0, SR, mode="trim")
    assert len(trimmed) == bar, f"trim: {len(trimmed)} != {bar}"
    padded = grid.fit_loop_to_bars(x, 120.0, SR, mode="pad")
    assert len(padded) == 2 * bar
    assert np.all(padded[len(x):] == 0.0)  # the pad is silence, stated
    nearest = grid.fit_loop_to_bars(x, 120.0, SR, mode="nearest")
    assert len(nearest) == 2 * bar  # 1.5 rounds to 2
    assert len(x) == int(1.5 * bar)  # input never mutated


def t_grid_drift_measured_not_hidden():
    bar = grid.bars_to_samples(1, 120.0, SR)
    d = grid.measure_drift(bar + 100, 120.0, SR)
    assert d["n_bars"] == 1 and d["drift_samples"] == 100
    assert abs(d["drift_ms"] - 1000.0 * 100 / SR) < 1e-9
    d0 = grid.measure_drift(bar, 120.0, SR)
    assert d0["drift_samples"] == 0 and d0["drift_beats"] == 0.0


def t_grid_beat_positions():
    pos = grid.beat_positions(44100, 120.0, SR)  # 1 s at 120 BPM
    assert list(pos) == [0, 22050]  # beat lines at 0 and 0.5 s only
    pos93 = grid.beat_positions(48000, 93.0, 48000)
    assert pos93[1] == int(round(60.0 * 48000 / 93.0))


# ------------------------------------------------------------ tempo

def t_wsola_doubles_duration_pitch_held():
    x = sine(440.0, 0.5)
    y = tempo.wsola(x, 2.0)
    assert abs(len(y) - 2 * len(x)) <= 0.02 * 2 * len(x), len(y)
    mid = y[len(y) // 4: 3 * len(y) // 4]
    assert abs(dominant_freq(mid, SR) - 440.0) < 15.0


def t_wsola_compresses():
    x = sine(330.0, 1.0)
    y = tempo.wsola(x, 0.5)
    assert abs(len(y) - len(x) // 2) <= 0.03 * len(x), len(y)
    mid = y[len(y) // 4: 3 * len(y) // 4]
    assert abs(dominant_freq(mid, SR) - 330.0) < 15.0


def t_time_stretch_vocoder_road():
    x = sine(440.0, 0.5)
    y = tempo.time_stretch(x, SR, 1.5, method="vocoder")
    assert len(y) == int(round(len(x) * 1.5))
    mid = y[len(y) // 4: 3 * len(y) // 4]
    assert abs(dominant_freq(mid, SR) - 440.0) < 20.0


def t_time_stretch_auto_smoke():
    rng = np.random.RandomState(3)
    bursts = np.zeros(SR)
    for s in range(0, SR, SR // 4):
        bursts[s:s + 400] = rng.randn(400)  # transient-rich material
    y = tempo.time_stretch(bursts, SR, 2.0, method="auto")
    assert abs(len(y) - 2 * SR) <= 0.05 * 2 * SR


def t_shift_pitch_octave_wsola_road():
    x = sine(220.0, 0.6)
    y = tempo.shift_pitch(x, SR, 12.0, method="wsola")
    assert len(y) == len(x)
    mid = y[len(y) // 4: 3 * len(y) // 4]
    assert abs(dominant_freq(mid, SR) - 440.0) < 40.0


def t_tempo_bad_rate_refused():
    for fn in (lambda: tempo.wsola(np.zeros(100), 0.0),
               lambda: tempo.time_stretch(np.zeros(100), SR, -1.0)):
        try:
            fn()
        except ValueError:
            continue
        raise AssertionError("non-positive rate not refused")


# ----------------------------------------------------------- repair

def t_remove_dc():
    x = sine(220.0, 0.5) + 0.3
    y = repair.remove_dc(x)
    assert abs(float(np.mean(y))) < 1e-9


def t_declick_removes_injected_click():
    clean = sine(220.0, 1.0)
    x = clean.copy()
    x[20000] += 3.0  # the injected click
    y, spans = repair.declick(x)
    assert spans, "click not detected"
    assert any(s <= 20000 < e for s, e in spans), spans
    err = np.max(np.abs(y - clean))
    assert err < 0.05, f"residual error after declick: {err}"


def t_repair_gap_ar_bridge():
    clean = sine(330.0, 1.0)
    x = clean.copy()
    x[10000:10200] = 0.0  # a 200-sample hole
    y = repair.repair_gap(x, 10000, 10200)
    rms = float(np.sqrt(np.mean((y[10000:10200] - clean[10000:10200]) ** 2)))
    assert rms < 0.05, f"AR bridge RMS error: {rms}"


def t_repair_gap_short_cubic():
    clean = sine(440.0, 0.5)
    x = clean.copy()
    x[5000:5003] = 0.0
    y = repair.repair_gap(x, 5000, 5003)
    err = np.max(np.abs(y[5000:5003] - clean[5000:5003]))
    assert err < 0.02, f"cubic bridge error: {err}"


def t_repair_tear_continuity():
    clean = sine(330.0, 1.5)
    x = clean.copy()
    s, e = 22050, 22050 + 2205  # 50 ms tear
    x[s:e] = 0.0
    y = repair.repair_tear(x, s, e)
    step = abs(y[s] - y[s - 1])
    assert step < 0.1, f"seam step: {step}"
    rms = float(np.sqrt(np.mean((y[s:e] - clean[s:e]) ** 2)))
    assert rms < 0.15, f"tear fill RMS error: {rms}"


def t_decrackle_reduces_impulse_rain():
    clean = sine(220.0, 1.0)
    rng = np.random.RandomState(11)
    x = clean.copy()
    idx = np.arange(3000, len(x) - 100, 5000)
    x[idx] += rng.choice([-1.0, 1.0], len(idx)) * 0.8
    before = float(np.sum((x - clean) ** 2))
    y = repair.decrackle(x)
    after = float(np.sum((y - clean) ** 2))
    assert after < 0.4 * before, f"crackle energy {before} -> {after}"


def t_declip_rebuilds_crest():
    clean = sine(220.0, 1.0, amp=1.0)
    x = np.clip(clean, -0.6, 0.6)
    y, spans = repair.declip(x)
    assert spans, "no clipped plateau found"
    assert float(np.max(y)) > 0.9, f"crest not rebuilt: {np.max(y)}"
    rms = float(np.sqrt(np.mean((y - clean) ** 2)))
    assert rms < 0.05, f"declip RMS error: {rms}"


# ------------------------------------------------------------ vocal

def t_autocorr_tracker_finds_stack():
    x = harmonic_stack(220.0, 1.0)
    f0, voiced = vocal.track_f0_autocorr(x, SR)
    med = float(np.nanmedian(f0[voiced]))
    assert abs(med - 220.0) < 6.0, f"tracked {med}"
    silence = np.zeros(SR)
    f0s, voiced_s = vocal.track_f0_autocorr(silence, SR)
    assert not voiced_s.any()


def t_humanize_contour_adds_life_keeps_melody():
    hop_s = 512 / SR
    f0 = np.full(200, 220.0)
    f0[80:100] = np.nan  # an unvoiced gap
    out = vocal.humanize_contour(f0, hop_s, seed=5)
    assert np.isnan(out[80:100]).all(), "unvoiced frames fabricated"
    v = np.isfinite(out)
    cents = 1200.0 * np.log2(out[v] / 220.0)
    assert float(np.std(cents)) > 4.0, f"contour still flat: {np.std(cents)}"
    assert abs(float(np.mean(cents))) < 15.0, "melody (mean) moved"
    out2 = vocal.humanize_contour(f0, hop_s, seed=5)
    assert np.allclose(out[v], out2[v]), "not deterministic per seed"


def t_jitter_measure_and_normalize():
    hop_s = 512 / SR
    alt = np.where(np.arange(200) % 2 == 0, 200.0, 212.0)
    before = vocal.measure_jitter_shimmer(alt)["jitter_pct"]
    flat = np.full(200, 200.0)
    jflat = vocal.measure_jitter_shimmer(flat)["jitter_pct"]
    assert before > 1.0 and jflat == 0.0, (before, jflat)
    norm = vocal.normalize_jitter_shimmer_contour(alt, amount=1.0)
    after = vocal.measure_jitter_shimmer(norm)["jitter_pct"]
    assert after < 0.5 * before, f"jitter {before} -> {after}"
    del hop_s


def _vowel(f0=150.0, dur=1.0):
    """Synthetic vowel: harmonics under a two-formant envelope."""
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)
    for k in range(1, 40):
        f = f0 * k
        env = (np.exp(-0.5 * ((f - 730) / 90) ** 2)
               + 0.6 * np.exp(-0.5 * ((f - 1090) / 110) ** 2))
        x += env * np.sin(2 * np.pi * f * t)
    return 0.5 * x / np.max(np.abs(x))


def _envelope_peak(x, lo=400.0, hi=2500.0):
    mag = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    # 4 ms lifter: the coarsest quefrency that still resolves the
    # vowel's two formants as two (measured; 1 ms merges them).
    env = vocal._cepstral_envelope(mag, int(SR * 0.004))
    freqs = np.fft.rfftfreq(len(x), 1.0 / SR)
    band = (freqs >= lo) & (freqs <= hi)
    return freqs[band][int(np.argmax(env[band]))]


def t_formant_shift_keeps_formants_home():
    from resonance.pitch import pitch_shift
    x = _vowel()
    naive = pitch_shift(x, SR, 7.0)
    fixed = vocal.formant_preserving_shift(x, SR, 7.0)
    p_naive = _envelope_peak(naive)
    p_fixed = _envelope_peak(fixed)
    assert p_naive > 950.0, f"naive formant should drag up: {p_naive}"
    assert abs(p_fixed - 730.0) < 0.25 * 730.0, \
        f"corrected formant off home: {p_fixed}"
    same = vocal.formant_preserving_shift(x, SR, 0.0)
    assert np.array_equal(same, x)


def t_debuzz_reduces_spectral_ripple():
    # A harmonic stack whose envelope carries an imposed 300 Hz
    # ripple -- the over-even comb regularity the tool exists to
    # soften. Ripple is measured at the tool's own smoothing scale
    # (9 STFT bins), on the time-averaged frame magnitudes: bin-scale
    # FFT ripple would measure the analysis window, not the comb.
    from resonance.pitch.shift import _stft
    t = np.arange(SR) / SR
    x = np.zeros(SR)
    for k in range(1, 30):
        f = 180.0 * k
        env = (1.0 / k) * (1.0 + 0.45 * np.sin(2 * np.pi * f / 300.0))
        x += env * np.sin(2 * np.pi * f * t)
    x *= 0.3 / np.max(np.abs(x))

    def ripple(sig):
        spec = _stft(sig, 2048, 512)
        logmag = np.log(np.mean(np.abs(spec), axis=1) + 1e-12)
        smooth = np.convolve(logmag, np.ones(9) / 9, mode="same")
        freqs = np.fft.rfftfreq(2048, 1.0 / SR)
        band = (freqs > 200) & (freqs < 4000)
        return float(np.std((logmag - smooth)[band]))

    y = vocal.debuzz(x, SR, amount=1.0)
    assert ripple(y) < 0.7 * ripple(x), (ripple(x), ripple(y))


def t_add_presence_deterministic_and_quiet():
    x = sine(200.0, 1.0)
    y1 = vocal.add_presence(x, SR, level_db=-42.0, seed=2)
    y2 = vocal.add_presence(x, SR, level_db=-42.0, seed=2)
    assert np.array_equal(y1, y2), "presence layer not deterministic"
    r = float(np.sqrt(np.mean(y1 ** 2)) / np.sqrt(np.mean(x ** 2)))
    assert 1.0 < r < 1.05, f"presence too loud or absent: rms x{r}"


def t_humanize_end_to_end():
    x = harmonic_stack(200.0, 1.5)
    f0_in, v_in = vocal.track_f0_autocorr(x, SR)
    y = vocal.humanize(x, SR, seed=4)
    assert len(y) == len(x)
    f0_out, v_out = vocal.track_f0_autocorr(y, SR)
    med_in = float(np.nanmedian(f0_in[v_in]))
    med_out = float(np.nanmedian(f0_out[v_out]))
    assert abs(med_out - med_in) / med_in < 0.05, (med_in, med_out)

    def cents_std(f0, v):
        c = 1200.0 * np.log2(f0[v] / np.nanmedian(f0[v]))
        return float(np.std(c))

    assert cents_std(f0_out, v_out) > cents_std(f0_in, v_in) + 3.0, \
        (cents_std(f0_in, v_in), cents_std(f0_out, v_out))


check("grid_exact_beat_math", t_grid_exact_beat_math)
check("grid_bad_tempo_refused", t_grid_bad_tempo_refused)
check("grid_fit_trim_pad_nearest", t_grid_fit_trim_pad_nearest)
check("grid_drift_measured_not_hidden", t_grid_drift_measured_not_hidden)
check("grid_beat_positions", t_grid_beat_positions)
check("wsola_doubles_duration_pitch_held", t_wsola_doubles_duration_pitch_held)
check("wsola_compresses", t_wsola_compresses)
check("time_stretch_vocoder_road", t_time_stretch_vocoder_road)
check("time_stretch_auto_smoke", t_time_stretch_auto_smoke)
check("shift_pitch_octave_wsola_road", t_shift_pitch_octave_wsola_road)
check("tempo_bad_rate_refused", t_tempo_bad_rate_refused)
check("remove_dc", t_remove_dc)
check("declick_removes_injected_click", t_declick_removes_injected_click)
check("repair_gap_ar_bridge", t_repair_gap_ar_bridge)
check("repair_gap_short_cubic", t_repair_gap_short_cubic)
check("repair_tear_continuity", t_repair_tear_continuity)
check("decrackle_reduces_impulse_rain", t_decrackle_reduces_impulse_rain)
check("declip_rebuilds_crest", t_declip_rebuilds_crest)
check("autocorr_tracker_finds_stack", t_autocorr_tracker_finds_stack)
check("humanize_contour_adds_life", t_humanize_contour_adds_life_keeps_melody)
check("jitter_measure_and_normalize", t_jitter_measure_and_normalize)
check("formant_shift_keeps_formants_home", t_formant_shift_keeps_formants_home)
check("debuzz_reduces_spectral_ripple", t_debuzz_reduces_spectral_ripple)
check("add_presence_deterministic_and_quiet", t_add_presence_deterministic_and_quiet)
check("humanize_end_to_end", t_humanize_end_to_end)

print(f"\n{PASSED} tools-wing tests passed.")
