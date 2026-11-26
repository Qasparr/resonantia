# 93
# ---------------------------------------------------------------------
# blend_curves.py -- the Beta blend curves: three mix shapes seated
# as a small documented utility for the render chain -- a symmetric
# bell, a late snap, an early lean -- each in two forms: the density
# as a gain envelope, and its integral as a crossfade.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written XXVI day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# PROVENANCE: the plate "LEX STELLARRVM * BETA * Blending", received
# from the founder 2026-11-26 as an exhibit in the Gamma-Hebdomad
# audit (pontifex/research/gamma-hebdomad-audit, Exhibit 1; SHA-256
# 05bd4607b6efb3d67ee8e52031a406734cacbb3b497beebcc47f8d14e2dd6adb).
# The plate plots three Beta densities against an axis it labels
# "t in [0,1] -- Mix": BETA(2,2) Symmetric Bell, BETA(5,1) Late Snap,
# BETA(2,5) Early Lean. The audit recomputed the three densities from
# their pdfs and verified the plate at every coordinate (modes 0.5 /
# 1.0 / 0.2; peaks 1.5 / 5.0 / 2.4576; each integrates to 1) -- audit
# claims M-01..M-03, all VERIFIED. Seated by the desk under the
# founder's standing delegation of 2026-11-26 ("if this is useful for
# our house repo toolkit in anyway you know what to do with it"), at
# desk strength, revisable by his pen. The toolkit disposition is
# printed in the audit's closing section.
#
# MECHANISM: pure functions of t in [0,1], no state, no audio.
#   * beta_pdf(t, a, b) -- the density t^(a-1) (1-t)^(b-1) / B(a,b),
#     with B(a,b) = Gamma(a) Gamma(b) / Gamma(a+b) from math.gamma.
#   * density_envelope(t, a, b) -- the density divided by its own
#     peak, so the curve tops at exactly 1.0: the plate's shapes
#     usable as gain envelopes (a swell, a late rise, an early lean).
#   * blend(t, a, b) -- the regularized incomplete beta I_t(a,b),
#     the density's integral: a crossfade weight running 0 -> 1 whose
#     SHAPE the (a,b) seat sets -- symmetric S for (2,2), hugging the
#     floor then snapping up for (5,1), rising early then settling
#     for (2,5). Computed by the continued-fraction expansion
#     (Numerical Recipes' betacf), no dependency beyond math.
# The three presets carry the plate's own names. All three happen to
# have closed-form integrals -- I_t(2,2) = 3t^2 - 2t^3,
# I_t(5,1) = t^5, I_t(2,5) = 1 - (1-t)^5 (1 + 5t) -- and the tests
# swear the continued fraction against those closed forms, so the
# general road is proven on the seats the plate actually draws.
#
# LABEL HONESTY: these are blend SHAPES, mathematics only. Nothing
# here adopts the plate's framing, names a doctrine, or touches a
# seated instrument; the render chain may call the curves or not, as
# its own seats decide.
# ---------------------------------------------------------------------

import math

__all__ = [
    "SYMMETRIC_BELL", "LATE_SNAP", "EARLY_LEAN", "PRESETS",
    "beta_pdf", "density_envelope", "blend",
    "bell_envelope", "late_snap_envelope", "early_lean_envelope",
    "symmetric_blend", "late_snap_blend", "early_lean_blend",
]

# The plate's three seats, (a, b), under the plate's own names.
SYMMETRIC_BELL = (2.0, 2.0)
LATE_SNAP = (5.0, 1.0)
EARLY_LEAN = (2.0, 5.0)
PRESETS = {
    "symmetric_bell": SYMMETRIC_BELL,
    "late_snap": LATE_SNAP,
    "early_lean": EARLY_LEAN,
}


def _clamp01(t):
    """DOCTRINE: the mix parameter lives on [0,1]; outside readings
    are clamped to the nearer end, never extrapolated."""
    return 0.0 if t < 0.0 else (1.0 if t > 1.0 else float(t))


def beta_pdf(t, a, b):
    """The Beta(a,b) density at t. Endpoints are taken by their
    limits for the seats this house uses (a, b >= 1): the density is
    0 at an end whose exponent is positive, and the (5,1) seat reads
    its full 5.0 at t = 1."""
    t = _clamp01(t)
    if t == 0.0:
        return 0.0 if a > 1.0 else (1.0 / _beta_fn(a, b) if a == 1.0
                                    else math.inf)
    if t == 1.0:
        return 0.0 if b > 1.0 else (1.0 / _beta_fn(a, b) if b == 1.0
                                    else math.inf)
    return (t ** (a - 1.0)) * ((1.0 - t) ** (b - 1.0)) / _beta_fn(a, b)


def _beta_fn(a, b):
    """B(a,b) = Gamma(a) Gamma(b) / Gamma(a+b)."""
    return math.gamma(a) * math.gamma(b) / math.gamma(a + b)


def _peak(a, b):
    """(mode_t, peak_value) of the density: the interior mode
    (a-1)/(a+b-2) when a, b > 1; the t = 1 end for the (a, 1) seats;
    the t = 0 end for the (1, b) seats."""
    if a > 1.0 and b > 1.0:
        m = (a - 1.0) / (a + b - 2.0)
        return m, beta_pdf(m, a, b)
    if b == 1.0 and a >= 1.0:
        return 1.0, beta_pdf(1.0, a, b)
    if a == 1.0 and b >= 1.0:
        return 0.0, beta_pdf(0.0, a, b)
    # Unimodal boundary case (a, b both < 1 is bimodal and not a
    # blend seat this house uses): fall back to a fine scan.
    best_t, best_v = 0.0, -1.0
    for i in range(1001):
        t = i / 1000.0
        v = beta_pdf(t, a, b)
        if v > best_v:
            best_t, best_v = t, v
    return best_t, best_v


def density_envelope(t, a, b):
    """The plate's curve as a gain envelope: the Beta(a,b) density
    divided by its own peak, so the shape tops at exactly 1.0 at its
    mode and keeps the plate's proportions everywhere else."""
    _, peak = _peak(a, b)
    return beta_pdf(t, a, b) / peak


def _betacf(a, b, x):
    """The continued fraction for the incomplete beta function
    (Numerical Recipes, betacf): evaluated by the modified Lentz
    algorithm to 3e-14 relative tolerance."""
    max_it, eps, fpmin = 200, 3.0e-14, 1.0e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, max_it + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def blend(t, a, b):
    """The crossfade weight I_t(a,b) (regularized incomplete beta):
    0 at t = 0, 1 at t = 1, monotone between, shaped by the seat.
    Uses the symmetry I_t(a,b) = 1 - I_(1-t)(b,a) on the half where
    the continued fraction converges fastest."""
    t = _clamp01(t)
    if t == 0.0:
        return 0.0
    if t == 1.0:
        return 1.0
    front = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(t) + b * math.log(1.0 - t))
    if t < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, t) / a
    return 1.0 - front * _betacf(b, a, 1.0 - t) / b


# The plate's three shapes, by name, in both forms.
def bell_envelope(t):
    """BETA(2,2) as an envelope: a symmetric swell, 0 -> 1 -> 0,
    peaking at the middle of the mix."""
    return density_envelope(t, *SYMMETRIC_BELL)


def late_snap_envelope(t):
    """BETA(5,1) as an envelope: near-silent until late, rising to
    its full height only at the very end of the mix."""
    return density_envelope(t, *LATE_SNAP)


def early_lean_envelope(t):
    """BETA(2,5) as an envelope: a fast early rise peaking a fifth
    of the way through the mix, then a long fall."""
    return density_envelope(t, *EARLY_LEAN)


def symmetric_blend(t):
    """BETA(2,2) as a crossfade: the symmetric S, half-blended at
    the middle (I = 3t^2 - 2t^3)."""
    return blend(t, *SYMMETRIC_BELL)


def late_snap_blend(t):
    """BETA(5,1) as a crossfade: holds the first source late, then
    snaps across (I = t^5)."""
    return blend(t, *LATE_SNAP)


def early_lean_blend(t):
    """BETA(2,5) as a crossfade: leans into the second source early,
    then settles (I = 1 - (1-t)^5 (1 + 5t))."""
    return blend(t, *EARLY_LEAN)
