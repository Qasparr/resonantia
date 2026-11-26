[LOGO — the TVRRIS VERITATIS seal, ~/workspace/templates/doctrine-logo.png, centered]

**THE MISSING-PIECE SWEEP**
*Subtitle:* A Scientific Illuminist treatment of the vector and path-bearing terms of the wave physics of sound and light, audited against the Resonantia render chain and the EQVILLIBBRRIVMM suite

Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice)
XXV day of November, Dies Mercurii, Sol in Sagittarius,
Anno V:xii e.n. (2026 e.v.)

Classification: Enterprise • Educational • Research & Development
Method of Science, Aim of Religion

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All Rights
Reserved, Without Prejudice. Right of claim hereby reserved and coined under
the authority of the Living Man.

---

## I. THE COMMISSION AND THE QUESTION

The founder's order (2026-11-25 19:01 EST), verbatim: *"Search all known
sound amd light vector equations for a missing piece or parts. Lets get this
figured out cause i know it can be done."* ("amd" reads **And**, by his ruled
correctio.) Scope addition (19:04 EST), verbatim: *"And the EQVILLIBBRRIVMM
part if it needs more... havent been able to test it since we havent really
had a successful mastering since we built it."*

**The issue the sweep serves.** The house's renders keep failing the
founder's ear — thin, "16-bit" instrumental body; robotic vocals (Kagami
Ketto v3 verdict, 2026-11-25); the Honey Hammer garble — while passing every
scalar measure the bench applies (LUFS, true peak, bitrate, onset coverage,
pitch presence). The hypothesis under test, sharpened by the desk: **the
house chain models sound as a scalar pressure sum, static per note, while
the full wave physics of sound and of light is vector and path-bearing** —
and the missing pieces, if they exist, will be found where the physics has
terms the chain does not.

**The four-element content test** (standing law for every directive):
- **Inputs:** the governing equations of acoustics and of optics as seated
  in the standard literature; the house render chain and the EQVILLIBBRRIVMM
  suite as they actually stand in code (`~/workspace/resonance`, the
  transcription lab, the 16-bit remedy lab).
- **Processes:** a term-by-term lining-up of the two fields (the
  correspondence table, §V); a first-hand audit of the chain against every
  term (§VI, §VII); a ranked register of the absences (§VIII).
- **Outputs:** this document — the shelves (§III–IV), the table (§V), the
  audits (§VI–VII), the register (§VIII), and one calculated recommendation
  for the founder's yay or nay (§IX). **No build is implemented in this
  pass.** Research and recommendation only.
- **Tolerances:** every factual claim sourced or code-cited; every
  correspondence claim carries its killing evidence or is not seated (§II);
  every number in §VII recomputed from the test files and the ledger during
  the audit. Caliber claims: none — the founder's ear remains the gate.

## II. METHOD, TIERS, AND THE FALSIFIABILITY RULE

Three evidence standards govern the sweep:

1. **Literature claims** are seated only as the standard texts seat them —
   textbook or standard named for every equation (§III, §IV, Table of
   Authorities). Tier: ATTESTED.
2. **Correspondence claims** (sound ↔ light) are graded **PROVEN ANALOGY**
   (a theorem-level identity, text named), **STRUCTURAL PARALLEL** (same
   mathematics, different physics, the difference stated), or **NO
   COUNTERPART** (a negative finding). Under the founder's falsifiability
   rule — *"Of atleast one of Claim worthy of being disproven by evidence"*
   (2026-11-24) — every positively seated row names the observation that
   would kill it. A claim naming no killing evidence would be entered in
   the NOT-SEATED register (§X) and printed nowhere as proven. As the sweep
   fell out, every seated row named its killing evidence; the NOT-SEATED
   register stands empty, and says so.
3. **House claims** are graded **PRESENT / PARTIAL / ABSENT** from the code
   as read in this audit — file and mechanism cited for every grade, never
   from memory of summaries. Where a seat exists in the repo but has no
   call site in the chain that strikes delivered audio, the grade is
   PARTIAL and the split is printed. The audit corrected two of the desk's
   own starting hypotheses on the record (§VI.0) — corrections stand in
   place, marked, never vanished.

Reasoning rides with every assignment, per standing law: each term states
not only what the physics carries but *what the scalar sum throws away* —
that discard, and nothing else, is what makes a term a candidate
missing piece.

---

## III. THE ACOUSTICS SHELF — TWELVE TERMS

*The model under audit, defined:* a **scalar-pressure-sum model** represents
sound as p_tot(r,t) = Σᵢ aᵢ·pᵢ(t − τᵢ) — frozen scalar waveforms, scalar
gains, at most fixed delays, summed at a point. Each term below is a
mechanism that is not in that expression unless explicitly put back.

**III.1 — The scalar wave equation.** ∇²p − (1/c₀²)∂²p/∂t² = 0, with
c₀² = (∂p/∂ρ)_S. Not postulated: it is what remains after eliminating the
particle velocity **v** and the density perturbation between continuity,
Euler, and an adiabatic state equation — so it *inherits* their assumptions
(small perturbations, inviscid, homogeneous, no mean flow). *Discard:* even
this scalar equation is a propagation law in space-time; the sum discards
∇² — that p here and now constrains p everywhere else a travel-time later.
(Pierce, *Acoustics*, Ch. 1.)

**III.2 — The Euler momentum equation: v as a VECTOR.** ∇p = −ρ₀ ∂**v**/∂t.
Pressure gradient accelerates the medium; **v** carries magnitude *and
direction*. Two fields with identical p at a microphone can have opposite
**v** — a standing wave (pressure antinode, **v** = 0) vs a travelling wave
(p and **v** in phase). Specific acoustic impedance Z_s = p/v_n is the
complex ratio coupling them. *Discard:* direction, phase of motion,
impedance — travelling vs standing, near vs far. (Morse & Ingard,
*Theoretical Acoustics*, Ch. 2–3; Kinsler et al., *Fundamentals of
Acoustics*, §5.4.)

**III.3 — Acoustic intensity I = p·v.** Instantaneous intensity
**I**(r,t) = p·**v** [W/m²]; time-averaged complex intensity
**I**_c = ½ p̂ v̂*, whose real part is **active** intensity (net power flow,
dominant in the far field) and whose imaginary part is **reactive**
intensity (energy sloshing in the near field, averaging to zero transport).
Energy conservation: ∂w/∂t + ∇·**I** = 0, w = p²/2ρ₀c₀² + ρ₀|**v**|²/2.
*Discard:* energy flow itself — a scalar sum can cancel p to zero at a
point while intensity circulates through it, and can double p while adding
no net power. (Fahy, *Sound Intensity*, 2nd ed.; Jacobsen & Juhl.)

**III.4 — Continuity.** ∂ρ′/∂t + ρ₀∇·**v** = 0; with p = c₀²ρ′:
(1/c₀²)∂p/∂t + ρ₀∇·**v** = 0. The stiffness half of sound (Euler is the
inertia half); together they set c₀ and the fact that a source must
actually displace volume. *Discard:* the bookkeeping of mass and volume
displacement — summed pressures need correspond to no possible motion of
any medium. (Pierce, Ch. 1.)

**III.5 — Nonlinear acoustics: Westervelt and Kuznetsov.** From the state
equation's second-order term, the coefficient of nonlinearity
β = 1 + B/2A (air: B/A = γ−1, β = 1.2; water: B/A ≈ 5.2, β ≈ 3.5). Local
sound speed depends on the wave itself, c ≈ c₀ + βv: crests outrun troughs,
a sine wave steepens and generates harmonics 2f, 3f… *during propagation*,
toward a sawtooth/weak shock at the shock-formation distance
x̄ = ρ₀c₀³/(βωp₀). Westervelt (1963) governs directional progressive waves
with thermoviscous loss; Kuznetsov (1971) retains the local terms
Westervelt drops. *Discard:* amplitude-dependent propagation — in a scalar
sum, the harmonics at the output are exactly those put in at the input,
forever; steepening and intermodulation between summed components cannot
occur. (Hamilton & Blackstock (eds.), *Nonlinear Acoustics*, Ch. 2.)

**III.6 — Absorption and dispersion over distance.** Complex wavenumber
k(ω) = ω/c(ω) − jα(ω): α is attenuation, c(ω) is frequency-dependent phase
speed, and Kramers–Kronig causality ties them. Classical Stokes/Kirchhoff
absorption α_cl ∝ f² (viscosity + thermal conduction) underpredicts air
absorption by one to two orders of magnitude; vibrational relaxation of O₂
and N₂, catalysed by water vapour, dominates in air. ISO 9613-1 seats the
full shape (α in dB/m as a function of f, T, pressure, humidity);
indicative magnitudes at ~70% RH: ~4–5 dB/km at 1 kHz, ~27 dB/km at 4 kHz,
~95 dB/km at 8 kHz — *in addition to* geometric spreading. *Discard:*
distance as a spectral operator — a fixed gain/delay sum gives every path
the source's original spectrum, at any distance, in any humidity.
(ISO 9613-1:1993; ANSI/ASA S1.26; Blackstock, *Fundamentals of Physical
Acoustics*.)

**III.7 — Source radiation: directivity, radiation impedance, multipoles.**
A compact source's far field expands in multipoles: monopole (volume
velocity Q, omnidirectional, p = ρ₀Q̇(t−r/c₀)/4πr), dipole (∝ cos θ),
quadrupole — radiation efficiency scaling as (ka)²ˡ in power. Radiation
impedance Z_r = R_r + jX_r loads the source back: at ka ≪ 1, R_r ∝ (ka)²
(poor radiation) and X_r is mass-like. *Discard:* angle, size, and load —
one waveform for all directions, no ka scaling, no reaction of the air
back onto the source. (Morse & Ingard, Ch. 7; Pierce, Ch. 5.)

**III.8 — Driven-resonator source physics: excitation × body.** An
instrument is coupled oscillators: string modes driven by the excitation
*and* by the bridge force, body modes driven through the bridge admittance
Y_b(ω) — so string partial amplitudes, decay rates, and tuning are
functions of the body. Pluck position weights mode n by sin(nπx_exc/L).
Named consequences: two-stage decay (the two string polarisations decay at
different rates through Y_b), sympathetic resonance, the wolf note
(coupled-mode splitting when string and body modes coincide). *Discard:*
the instrument — a frozen waveform has all of this baked in for exactly
one note, one velocity, one instrument state, and can generate none of it
for the next. (Fletcher & Rossing, *The Physics of Musical Instruments*,
2nd ed.)

**III.9 — Digital waveguide synthesis (Smith).** The d'Alembert solution
of the 1-D wave equation is a sum of two *travelling* waves,
y(x,t) = y⁺(t−x/c) + y⁻(t+x/c) — sampled, two delay lines. At an impedance
discontinuity R₁→R₂, waves scatter: reflection Γ = (R₂−R₁)/(R₂+R₁).
Distributed loss and dispersion are lumped into filters at terminations:
a plucked string is one bidirectional delay line closed through a lowpass
reflection filter; stiffness is allpass dispersion in the loop. *Discard:*
traversal itself — travel time as structure, reflection at every impedance
change, and the distinction between the right- and left-going waves whose
sum the scalar model borrows. (Smith, *Physical Audio Signal Processing*,
CCRMA; "Physical Modeling Using Digital Waveguides," *Computer Music
Journal* 16(4), 1992.) — *Reasoning for its seat in this sweep: this is
the synthesis form of the founder's own traversal frame ("sound does
indeed travel," 2026-11-25 18:58 EST) — the wave equation rearranged so
that the path is the computation.*

**III.10 — Ray acoustics and the eikonal.** Short-wavelength ansatz in
Helmholtz gives |∇ψ|² = ω²/c(r)²; rays are the wavefronts' orthogonal
trajectories (Hamilton's equations on ω(k,r)), bending toward lower c;
amplitude follows from the transport equation (energy conservation along a
ray tube). Snell's law and specular reflection are corollaries. The model
fails by construction exactly where diffraction matters. *Discard:* path —
bending, focusing, shadowing, travel-time structure. (Pierce, Ch. 6;
Brekhovskikh, *Waves in Layered Media*; Landau & Lifshitz, *Fluid
Mechanics*.)

**III.11 — Doppler and path-length modulation.** f′ = f(c ± v_D)/(c ∓ v_S)
— but the general form is a *time-varying path length* L(t): the received
signal is the source signal at retarded time, instantaneously
f_inst ≈ f(1 − L̇/c). A sinusoidally varying path phase-modulates the wave
(sidebands at ω ± nΩ, Bessel amplitudes J_n(kΔL)) — the physics of
vibrato-by-motion, Leslie speakers, chorus, and instrumental micro-motion.
Millimetre-scale motion is kΔL ~ 1 at high audio frequencies: full phase
modulation. *Discard:* time-warping — a fixed-delay sum shifts a copy once;
it cannot continuously stretch, compress, and phase-modulate a waveform by
a moving path. (Smith, *Physical Audio Signal Processing*.)

**III.12 — Interchannel / interaural coherence.** For two channels,
magnitude-squared coherence γ²_xy(f) = |S_xy|²/(S_xx S_yy) ∈ [0,1]; its
ear-signal form is the IACC of room acoustics. The summing law itself is
coherence's corollary: N equal sources sum +20·log N dB fully coherent,
+10·log N dB mutually incoherent. Perceptually, decorrelation widens
apparent source width (ASW rises as IACC falls, Blauert & Lindemann 1986),
then spaciousness, then a diffuse unlocalisable image. *Discard:* the
relation *between* channels — hence image width, localisation, envelopment,
and even which summing law the sum obeys. (Blauert, *Spatial Hearing*;
Blauert & Lindemann, *JASA* 79(3), 1986; ISO 3382-1.)

*Shelf summary.* A scalar-pressure-sum model is not wrong as arithmetic —
superposition is exact for linear acoustics at a point. It is incomplete
as physics: every term above is a mechanism by which the pressures being
summed are **created, transformed, loaded, warped, decorrelated, or given
direction** before, during, and after the sum.

---

## IV. THE LIGHT SHELF — EIGHT TERMS

The mirror discipline: a scalar intensity model of light keeps one
non-negative number I(r,t) per point. Each term below is structure that
number throws away.

**IV.1 — Maxwell's equations.** ∇·**D** = ρ_f, ∇·**B** = 0,
∇×**E** = −∂**B**/∂t, ∇×**H** = **J**_f + ∂**D**/∂t. Two coupled *vector*
fields sustain each other (the displacement-current term is what permits
self-propagating waves in vacuum); transversality (∇·**B** = 0) is the
root of polarization. *Discard:* the second field, the direction of
oscillation, and phase. (Griffiths; Jackson; Born & Wolf, Ch. 1.)

**IV.2 — The Poynting vector S = E × H.** Poynting's theorem:
∂u/∂t + ∇·**S** = −**J**·**E**, u = ½(**E**·**D** + **H**·**B**). For a
plane wave ⟨S⟩ = ½cε₀n|E₀|² along **k**; field momentum density is
**g** = **S**/c². *Discard:* I = |⟨**S**⟩| keeps the magnitude and drops
the *direction* of energy flow — in standing, evanescent, or interfering
fields **S** circulates and is not parallel to **k**. (Physics LibreTexts,
"Poynting's Theorem.")

**IV.3 — Polarization and the Stokes parameters.** A transverse wave has
two components (E_x, E_y); their ratio and relative phase trace the
polarization ellipse. The complete measurable description of partially
polarized light is the Stokes vector (1852): S₀ = |E_x|² + |E_y|²,
S₁ = I_H − I_V, S₂ = I_{+45°} − I_{−45°}, S₃ = I_R − I_L, with degree of
polarization 𝒫 = √(S₁²+S₂²+S₃²)/S₀. Scalar intensity is exactly S₀ alone —
one of the four numbers. *The sound-side statement, placed precisely:*
sound in a **fluid** is longitudinal — one mode, no shear, **no
polarization degree of freedom**. Sound in a **solid** carries both
longitudinal (P) and transverse shear (S) waves, and the shear waves *do*
polarize (SV/SH), with P↔S mode conversion at boundaries. "Sound has no
polarization" is true for fluids and false for solids. (Stokes 1852;
Hecht, *Optics*, Ch. 8; Achenbach, *Wave Propagation in Elastic Solids*.)

**IV.4 — Optical coherence theory.** The predictive object is not **E** but
its two-point correlation: mutual coherence Γ₁₂(τ) = ⟨E₁(t+τ)E₂*(t)⟩,
complex degree of coherence γ₁₂(τ) = Γ₁₂/√(I₁I₂), measured directly as
fringe visibility 𝒱 = |γ₁₂(0)| at equal intensities. Coherence time
τ_c ~ 1/Δν; coherence area governed by the van Cittert–Zernike theorem
(far-field mutual intensity = Fourier transform of the source intensity
distribution). *Discard:* I(r) = Γ(r,r;0) is only the diagonal — whether
fields at two points or times can interfere at all is discarded whole.
(Born & Wolf, Ch. 10; Mandel & Wolf.)

**IV.5 — Huygens–Fresnel diffraction; the Kirchhoff integral.** Every
wavefront point sources secondary wavelets; Kirchhoff derived the
superposition from the wave equation via Green's identity:
U(P₀) = (1/4π)∮[G ∂U/∂n − U ∂G/∂n] dS, G = e^{ikr}/r — with the obliquity
factor K(χ) = ½(cos θ₀ + cos χ) that bare Huygens could not supply. The
integral propagates *complex amplitude*; |U|² forms only at the end.
Scalar theory is valid for apertures ≫ λ; below that, vector
(Stratton–Chu) diffraction is required. *Discard:* diffraction *is* phase —
from intensity on one plane, the field on the next cannot be computed at
all. (Born & Wolf, Ch. 8; Goodman, *Introduction to Fourier Optics*, Ch. 3.)

**IV.6 — The eikonal.** U = A e^{ik₀L} in Helmholtz, λ → 0, gives
|∇L|² = n²(r); rays obey d/ds(n dr/ds) = ∇n; Fermat's principle
δ∫n ds = 0 is the variational form. Fails at caustics, shadow boundaries,
and where n varies over ~λ. *Discard:* phase surfaces and their geometry —
no wavefronts, no rays, no account of why refraction bends. (Born & Wolf,
Ch. 3; Luneburg.)

**IV.7 — Fresnel coefficients.** At an interface, Maxwell's boundary
conditions give *separate* amplitude coefficients per polarization:
r_s = (n₁cosθ_i − n₂cosθ_t)/(n₁cosθ_i + n₂cosθ_t),
r_p = (n₂cosθ_i − n₁cosθ_t)/(n₂cosθ_i + n₁cosθ_t), with Snell's law from
phase matching. Consequences with no scalar analogue: Brewster's angle
(tan θ_B = n₂/n₁, r_p = 0), total internal reflection with
polarization-dependent phase shifts (the Fresnel rhomb's working
principle) and an evanescent field beyond the interface. At normal
incidence both reduce to r = (n₁−n₂)/(n₁+n₂). *Discard:* a scalar model
carries one R(θ); reality has R_s ≠ R_p and complex r — reflection
partially polarizes, and no scalar can state that. (Born & Wolf, Ch. 1;
Hecht, Ch. 4.)

**IV.8 — Doppler, relativistic.** No medium, no preferred frame, only
relative velocity: f′ = f√((1+β)/(1−β)) longitudinally — exactly the
geometric mean of the two classical acoustic formulas (at β = 0.5:
√(2.000 × 1.500) = 1.732) — and f′ = f/γ transversely, a pure time-dilation
redshift with **no classical counterpart**. The two theories agree to first
order in β and part at order β². This parting is the correspondence
table's measured zero point (§V, Row 9). (Einstein 1905; Taylor &
Wheeler, *Spacetime Physics*.)


---

## V. THE CORRESPONDENCE TABLE — SOUND ↔ LIGHT, TERM BY TERM

Classifications per §II. Every positively seated row carries its **killing
evidence** — the observation that would disprove it. The NOT-SEATED
register (§X) stands empty: no row required it.

| # | Term | Sound side | Light side | Seating |
|---|------|-----------|-----------|---------|
| 1 | Energy flux | **I** = p·**v** | **S** = **E**×**H** | **PROVEN ANALOGY** |
| 2 | Polarization | fluid: scalar p, none — solid: shear waves polarized | Stokes (S₀,S₁,S₂,S₃) | **NO COUNTERPART** (fluids) |
| 3 | Coherence | Γ⁽ᵖ⁾₁₂(τ) on pressure | Γ₁₂(τ) on **E** | **STRUCTURAL PARALLEL** |
| 4 | Diffraction | Kirchhoff integral on p | Kirchhoff integral on U | **PROVEN ANALOGY** |
| 5 | Eikonal / ray limit | ray acoustics, \|∇T\|² = 1/c² | geometric optics, \|∇L\|² = n² | **PROVEN ANALOGY** |
| 6 | Boundary reflection | R = (Z₂−Z₁)/(Z₂+Z₁) | Fresnel r_s, r_p | **STRUCTURAL PARALLEL** |
| 7 | Absorption | α(ω): viscothermal ∝ ω² classical + relaxation | α = 4πκ/λ: resonant | **STRUCTURAL PARALLEL** |
| 8 | Nonlinearity | quadratic, β = 1+B/2A; steepening → shock | χ⁽²⁾, χ⁽³⁾; Kerr cubic typical | **STRUCTURAL PARALLEL** (stated break) |
| 9 | Doppler | f′ = f(c±v_o)/(c∓v_s), medium frame | f′ = f√((1+β)/(1−β)), relative only | **STRUCTURAL PARALLEL** (first order only) |

**Row 1 — Energy flux. PROVEN ANALOGY.** Both fluxes are *derived*, not
postulated, as the divergence term of a local energy-conservation law:
Poynting's theorem on the light side (§IV.2); the acoustic energy corollary
with **I** = p**v** on the sound side (§III.3) — in both, the product of the
effort variable and the flow variable, in W/m² in both. *Texts:* Griffiths
§8.2; Pierce Ch. 2; Kinsler et al. **Killing evidence:** a configuration in
either domain where measured net energy crossing a closed surface disagrees
with ∮**S**·d**A** (resp. ∮**I**·d**A**) beyond experimental error — a
failure of the conservation derivation itself. None is on record.

**Row 2 — Polarization. NO COUNTERPART (fluids).** The row where the
analogy *fails*, asymmetrically: light is irreducibly vectorial (scalar
keeps S₀ of four); fluid sound is irreducibly scalar (the field *is* p,
with **v** slaved to it by Euler; no second component, no Stokes
structure). The failure's precise boundary: solid-borne shear waves restore
a *partial structural counterpart* (polarization of particle displacement
in an elastic medium, P↔S mode conversion with no dielectric-interface
analogue). *Falsifier of the negative claim, stated for completeness:*
demonstration of a transverse polarizable propagating mode in a simple
shear-free fluid at acoustic frequencies would overturn the fluid half.

**Row 3 — Coherence. STRUCTURAL PARALLEL.** The statistical machinery is
identical in form — Γ₁₂(τ), γ₁₂(τ), coherence time ~ 1/Δν, van
Cittert–Zernike — because those are theorems about *any* stationary random
field obeying a linear wave equation. Seated below PROVEN ANALOGY because
the optical theory's full form is a 2×2 coherence/polarization matrix, and
by Row 2 the fluid-acoustic field has no such extension: the scalar half
parallels exactly, the vector half has no parallel. **Killing evidence:**
a linear, stationary acoustic interference experiment whose measured fringe
visibility departs from |γ⁽ᵖ⁾₁₂(0)| computed from the measured pressure
cross-correlation, where the optical identity 𝒱 = |γ₁₂(0)| holds.

**Row 4 — Diffraction. PROVEN ANALOGY.** The strongest row: monochromatic
acoustic pressure and any single Cartesian component of **E** obey *the same
equation*, (∇² + k²)U = 0; the Helmholtz–Kirchhoff theorem is a theorem
about that equation and transfers verbatim — same integral, same obliquity
factor, same Fresnel/Fraunhofer approximations, same Airy pattern. The one
asymmetry runs in sound's favour: scalar diffraction is an *approximation*
for light and *exact* (within linear acoustics) for fluid sound, because
the field really is a scalar. *Texts:* Born & Wolf Ch. 8; Goodman Ch. 3;
Pierce Ch. 4. **Killing evidence:** a scalar-regime experiment (aperture
≫ λ both sides, linear amplitudes) where the acoustic pattern of an
aperture departs from the Kirchhoff prediction while the geometrically
identical optical pattern matches it, or vice versa — a split outcome
would falsify the shared-equation premise itself.

**Row 5 — Eikonal / ray limit. PROVEN ANALOGY.** The identical
short-wavelength limit of the identical Helmholtz equation: |∇L|² = n²
optics; |∇T|² = 1/c_s² acoustics (least-time Fermat, δ∫ds/c_s = 0); rays
orthogonal to wavefronts in both; Snell's law the same boundary condition
in two notations (sinθ/c on the sound side); shared failure modes —
caustics, shadow zones, breakdown at ~λ variation. *Texts:* Born & Wolf
Ch. 3; Brekhovskikh; Jensen et al., *Computational Ocean Acoustics*.
**Killing evidence:** a short-wavelength regime away from caustics where
measured acoustic paths violate least-time stationarity while optical
paths in the matched index profile satisfy Fermat — showing the limits are
not the same limit of the same equation.

**Row 6 — Boundary reflection. STRUCTURAL PARALLEL.** At normal incidence
the formulas are formally identical in shape — r = (n₁−n₂)/(n₁+n₂) optics;
R = (Z₂−Z₁)/(Z₂+Z₁) acoustics, from continuity of pressure and normal
particle velocity; matched impedances give R = 0 in both. Seated below
identity for three stated reasons: (i) optics has two coefficients at
oblique incidence, acoustics (fluid) one — Brewster's angle and
reflection-induced partial polarization have no fluid counterpart (Row 2
again); (ii) n and Z enter differently at oblique incidence; (iii) solid
boundaries restore P↔S mode conversion, no dielectric analogue. The shared
core — phase matching, Snell's law, θ_r = θ_i — is exact. **Killing
evidence:** a normal-incidence measurement on a lossless fluid–fluid
interface departing from (Z₂−Z₁)/(Z₂+Z₁) with independently measured ρ, c_s,
while the optical formula continues to hold on its side.

**Row 7 — Absorption. STRUCTURAL PARALLEL.** Shared mathematics only:
exponential decay from a complex wavenumber, I(x) = I₀e^{−αx} in a
homogeneous medium (Beer–Lambert optics; the same form acoustically).
Mechanisms and α(ω) laws are different physics — resonant electronic/
vibrational absorption vs viscothermal ω² plus molecular relaxation — and
no universal α(ω) shape is claimed across the two. **Killing evidence:**
non-exponential decay with distance in a homogeneous, linear, single-mode
medium at fixed frequency (geometric spreading divided out) on either side
— falsifying the complex-k mechanism both sides are claimed to share.

**Row 8 — Nonlinearity. STRUCTURAL PARALLEL, with a stated break.** Shared
structure: a nonlinear constitutive relation generates new frequencies —
optics **P** = ε₀(χ⁽¹⁾**E** + χ⁽²⁾**E**² + χ⁽³⁾**E**³ + …), acoustics
β = 1 + B/2A with cumulative distortion (Westervelt/Burgers). The break,
stated in the literature itself (Hamham et al., *Phys. Rev. B* 92, 054302
(2015)): homogeneous fluids are essentially non-dispersive for sound, so
acoustic harmonics stay in phase, accumulate, and steepen into **shocks**,
which ordinary optical media do not produce; and the dominant order differs
— quadratic in fluids, cubic (Kerr) the common optical case. **Killing
evidence (either direction rewrites the row):** (a) finite-amplitude sound
in a non-dispersive fluid failing to generate harmonics/steepen where
Burgers/Westervelt requires it, while phase-matched optical SHG occurs as
predicted; or (b) ordinary optical media steepening plane waves into true
discontinuities under the same non-dispersive conditions — which would
promote the row, not merely refute its limit.

**Row 9 — Doppler. STRUCTURAL PARALLEL, first order only — the table's
zero point.** At O(β) the two laws are identical (approach raises frequency
by ≈ 1 + β_radial in both). At O(β²) they *measurably part, and they part
exactly on the medium*: acoustics splits by who moves through the medium
(2.000 vs 1.500 at β = 0.5), light takes the single geometric-mean law
(1.732); acoustics has no transverse effect, light has f/γ (Ives–Stilwell
confirmed); acoustics admits Mach cones, vacuum light admits no
superluminal source. Per the founder's zero-point method, the boundary
coordinates are the finding: **the correspondence holds below β² and parts
at β², on the medium question.** **Killing evidence:** for the seated
first-order claim — matched-geometry low-velocity experiments disagreeing
at O(β). For the stated divergence — a transverse Doppler shift for sound
in a stationary medium, or experimental separation of source-moving vs
observer-moving light shifts in vacuum (a light-medium rest frame —
precisely what Michelson–Morley-type experiments have repeatedly failed
to find).

**Seating summary.** PROVEN ANALOGY: Rows 1, 4, 5 — theorem-level
identities. STRUCTURAL PARALLEL: Rows 3, 6, 7, 8, 9 — each with its limit
printed. NO COUNTERPART: Row 2 (fluids). NOT-SEATED: none required. The
table's measured zero point is Row 9; its standing structural absence is
Row 2, which Rows 3 and 6 inherit.

---

## VI. THE HOUSE AUDIT — THE RENDER CHAIN AGAINST EVERY TERM

*Evidence standard (§II.3): files read first-hand in this audit —
`resonance/studio/{pipeline, performance, spine, kit, arpeggio,
four_powers, eightoeight, eqvillibbrrivmm, crystal_import, acoustics,
doppler, detect, vocal_exam, diffsinger, render_diffsinger,
render_musicgen}.py`, the seats they call (`resonance/synth/voices.py`,
`resonance/vocal.py`, `resonance/binaural/`, `resonance/spatial/{orbit,
hrtf, distance, ambisonic}.py`), the transcription lab's render scripts,
and the 16-bit remedy lab's `tsf_render.c` + RECEIPT.md.*

**The chain, defined:** `pipeline.produce()` / `performance.produce_
performance()` and the lab render scripts that actually strike delivered
audio. Physics seats that exist in the repo with no call site in the chain
are graded PARTIAL with the split printed — a library is not a chain.

### VI.0 — Two desk hypotheses corrected by the audit (marked, not vanished)

The brief carried the desk's starting assumptions. Two did not survive
first-hand reading, and the corrections matter to the register (§VIII):

- **"Intensity/coherence unmanaged" — CORRECTED in its coherence half.**
  Interchannel coherence is one of the main chain's most *deliberate*
  mechanisms (the Stereo Law, VI.3). The intensity-vector half stands
  (VI.2). The desk candidate "intensity/coherence management in the mix"
  is therefore demoted and reframed in the register — coherence is
  PRESENT; what is absent is narrower.
- **"Master chain linear (no controlled nonlinearity)" — CORRECTED.**
  Controlled nonlinearity exists and is measured into the manifest
  (Vapour, VI.6) — it is *optional and off unless ordered*, and the one
  always-on nonlinearity is the limiter's tanh knee. The candidate
  "controlled nonlinearity" is killed as a missing piece in §VIII:
  present, unengaged by choice, is not absent.

### VI.1 — Scalar pressure summation: PRESENT (it is the chain's whole law); per-voice dynamics ABSENT

Everything is float sample addition of pressure waveforms; no other
summation law exists anywhere in the read corpus. `pipeline.produce()`:
per-section RMS matched to the median section RMS, gain clamped ±6 dB,
equal-power crossfades; spine added as one whole-layer RMS-relative scalar
(`bed + spine_arr·(b_rms/spine_rms)`); arpeggio and Sigma likewise
RMS-relative. `spine.place()`: `mix[ch, at:end] += buf·pan_gain`, per-event
amplitude only from the pattern table's deterministic velocities.
`render_diffsinger` assembly: lines summed onto a canvas at offsets;
overlaps sum, never duck. The lab roads print fixed gains (lead 0.90, pad
strings 0.55, pad piano 0.32, bass 0.85, kit bus 0.80); the fixed render's
one adaptive exception iterates *per-bus* gains (≤4 passes) against the
original master's LTAS fingerprint — still one static gain per bus.
**Per-voice dynamics in the mix: none** — no per-voice compressor,
sidechain, automation lane, or envelope follower on any stem in any road.
The only dynamics processor is post-mix, on the summed bus (VI.6).
*Term mapping: §III.1 — the chain is the scalar sum, exactly as
hypothesised. What the physics adds around the sum is the rest of this
section.*

### VI.2 — Particle velocity / intensity vector (p·v): ABSENT

No file computes a particle-velocity field, an intensity vector, or a
velocity potential for any rendered source; audio is scalar pressure end
to end. Nearest neighbours, neither of which is p·v modelling:
`acoustics.intensity_ratio()` / `level_change_db()` — scalar textbook
calculators whose own header states "pure functions, no state, **no
audio**… it renders nothing"; `spatial/ambisonic.encode()` — directional
*pressure* components (W = p/√2, Y = p·y_left, …) of a first-order
encoding, and ambisonics has **no call site in the studio chain**.
*Term mapping: §III.2, §III.3; correspondence Row 1 (PROVEN ANALOGY) —
the flux term is proven physics the chain nowhere computes.*

### VI.3 — Interchannel coherence: PRESENT in the main chain (the Stereo Law); absent in the lab and DiffSinger roads

`pipeline.py` manages coherence deliberately and *measures* it:
(i) spine pans by role, constant-power, kick/808 dead centre, hats
alternating ±0.55 by step; (ii) `widen_bed()` — true mid/side surgery: mid
(L+R)/2 preserved *exactly* (mono fold-down sample-identical), side gains
a synthesised quadrature side (mid's spectrum × k·j), k = 0 below 180 Hz
(**lows fully mono**), smoothstepping to width × 0.75 at 2 kHz; applied to
the MusicGen bed only; (iii) the Sigma binaural pair never widened or
processed — deliberately decorrelated carriers; (iv) `channel_
correlation()`, `band_correlation()`, `side_rms_dbfs()` computed before/
after widening and on the master, printed in the manifest's stereo block.
Counterpoints: `render_diffsinger` is mono throughout; the transcription
lab *destroys* stereo (`read_wav48()` folds tsf_render's stereo to mono
by channel mean). *Term mapping: §III.12; Row 3 — the chain's one
fully-carried vector-adjacent term, carried in the main road only.*

### VI.4 — Excitation × body coupling: PARTIAL — samples and primitive models; no coupled system anywhere

Per instrument, by actual mechanism:

| Seat | Mechanism | Class |
|---|---|---|
| MusicGen bed | neural generation, frozen once written | frozen waveform |
| Spine sampled kit | measured one-shot takes; the four 808 roots are **one take replayed at fractional rate shifts** | frozen / sampler |
| SSO strings, Salamander Grand (tsf_render) | SF2 playback; the "body" is baked into the sample + TSF envelope/filter | frozen waveform |
| 808 toolbox (`eightoeight.py`) | sine with phase = analytic integral of an exponential pitch envelope + filtered noise click; six-square metallic cluster for hats/cymbals; small tanh drive (0.15) "standing for the circuit's soft saturation — an approximation, stated" | primitive circuit model — excitation + filter, **no resonator feedback, no coupling** |
| Spine synth voices | pitch-swept sine (phase = cumsum f(t)), FFT-mask noise, exponential decays | primitive model |
| Arpeggio violin | harmonic stack (1/k^0.9, k=1..10) tracking a per-sample F0 track, then a **static whole-layer** FFT formant shape (~520 Hz body, ~2.9 kHz brilliance) — one fixed linear filter after summation; does not react to pitch, velocity, or excitation | excitation + *uncoupled* static body filter — the closest approach in the house |
| EQVILLIBBRRIVMM fluid voice | 3-partial glottal wave **plus two formant sines added** (F1/F2 clamped) — formants as independent oscillators, not a filter the glottal wave passes through | additive, uncoupled |
| DiffSinger vocal | neural source–filter inside the checkpoint (acoustic ONNX → mel, NSF-HiFiGAN fed the F0 track); coupling exists but is opaque and not a house model | neural, opaque |

**No instrument anywhere is a coupled excitation–resonator system**: no
string/body feedback, no modal resonator bank excited by an input, no
bore/pipe synthesis (the pipe formulas in `acoustics.py` are calculators
only). *Term mapping: §III.8 — the driven-resonator term is the audit's
largest instrument-side absence. This is the physics underneath the
"16-bit"/thin-body verdicts: a frozen waveform or an uncoupled filter can
replay a body; it cannot *be* one — the same excitation into the same body
at a new pitch or velocity produces, in the chain, a transposition; in
the physics, a new event.*

### VI.5 — Propagation layer: PARTIAL in the library, ABSENT in the delivered chain

In `produce()` / `produce_performance()`: **no propagation at all** — no
distance gain, no air absorption, no propagation delay, and **no reverb of
any kind, neither convolution nor algorithmic**, in mix or master. (The
only convolution in the chain is the EQ bus's 16-tap FIR — an EQ, §VII.)
Fake-room traces live inside two voices only (`eightoeight.clap()`: "the
'reverb' is a single exponential pretending — an approximation, stated; a
room it is not"). Library seats, **unwired**: `spatial/distance.apply()` —
1/r gain with near clamp + frequency-dependent air loss as a one-pole
lowpass, fc(d) = 20000/(1+d^1.5), honestly labelled "NOT ISO 9613-1", and
applying **no propagation delay**; `spatial/hrtf.pan()` — Woodworth ITD
(±0.66 ms) + sin² ILD + far-ear lowpass, reaching the chain only via
`spatial/orbit` for the arpeggio layer; `acoustics.delay_ms()` /
`echo_distance()` — computes delay-by-space numbers, renders nothing.
*Term mapping: §III.6, §III.10 — distance as a spectral operator and
delay-by-space both exist as calculators or partial seats; the chain
adopts none of them.*

### VI.6 — Nonlinearity: PRESENT, controlled, mostly optional; the default master is near-linear

The master chain in code order (`pipeline.produce()`): optional per-stem
EQ bus (§VII) → stitch → widen → spine → arpeggio → Sigma → **SCIRE**
(measurement only: ungated BS.1770 LUFS, FFT-oversampled true peak, crest)
→ **VELLE** (only if the spec orders it: zero-phase FFT EQ, ±12 dB max,
then a stereo-linked block feedforward compressor, ~5.3 ms blocks) →
**VAPOUR** (off unless ordered, drive 0–24 dB: y = tanh(g·x)/tanh(g),
peak-preserving, crest delta measured into the manifest) → fades →
**AUDERE** (`master_signal()`: pure gain to target, default −14.0 LUFS →
`soft_limit()` — **the one nonlinearity always in the chain**: linear
below a knee at 0.85 × ceiling, tanh bend above → true-peak trim by pure
gain if over ceiling, default −1.0 dBTP, with `ceiling_overrode_loudness`
confessed in the report) → **TACERE** (TPDF dither at the 24-bit LSB,
seeded, default on) → strike. Elsewhere: the 808's tanh drive (VI.4);
tsf_render's hard clamp ±1.0 on write. The lab roads finish with a single
ffmpeg loudnorm pass (I=−14 : TP=−1 : LRA=11) — *lab only; the house
master never calls loudnorm*, its loudness being its own ungated BS.1770
implementation. *Term mapping: §III.5; Row 8 — the chain's nonlinearity is
a limiter knee and an unengaged saturation seat. Propagation steepening
(Westervelt) has no analogue anywhere, and none is claimed for it: at
house levels and path lengths the physical effect is negligible in air —
the register (§VIII) seats the *seat's* honest scope, not the physics'
full claim.*

### VI.7 — Pitch / expression paths: PARTIAL — continuous inside synth notes; STEPWISE in the vocal road

Continuous where the house synthesises: `eightoeight` kick/tom and
`spine.bass808()` integrate frequency envelopes into phase analytically;
`arpeggio` builds a frame-level F0 contour through `vocal.humanize_
contour()` — micro-drift (low-passed random walk, 12–30 cents), vibrato on
sustained runs (120 ms onset ramp), attack scoops (−70 cents, τ = 30 ms) —
struck with phase = cumsum(humanised track), so the life is *in* the pitch.

**The vocal road is stepwise, and the audit names the v3 "robotic" verdict
in code:** `diffsinger.build_line()` enters pitch as one MIDI integer per
phoneme; `note_slur` is written `"0"` for every note — no slurs, bends, or
transitions are ever expressed. In `render_diffsinger` Stage 3, the pitch
fed forward is the stepwise `ph_midi` forward-filled across rests; the
variance ONNX predicts **only voicing and tension curves**; the F0 handed
to the acoustic model and the vocoder is computed *directly from the
stepwise MIDI* — `_f0 = 440·2^((midi_frames−69)/12)`, 0 on rests — a
staircase with instantaneous jumps at phoneme boundaries, no glide, no
overshoot, no vibrato term. Stage 4 freezes `gender = 0`, `velocity = 1`
for every frame. The one expressive axis that *is* modelled is duration
(Stages 1–2), and it is the one the house calibration loop corrects
(per-vowel-seat factors; run 1 at 90.38% → run 2 at 99.52% of asked
durations). **Net: a stepwise F0 + constant velocity/gender +
voicing/tension-only variance is a precise code-level description of
"sings, on pitch and on tempo after calibration, but robotic."**
The sample road is flat by construction too: `render.py` writes
**velocity 92 for every note-on**; tsf_render passes pitch bend through,
but no script writes any. *Term mapping: §III.11 — path-length/pitch-path
modulation exists for synth seats and is absent exactly where the ear
filed its verdict: the sung line.*

### VI.8 — Directivity / radiation: ABSENT in the chain

No per-source radiation pattern, polar response, or placement model for
any rendered source: spine hits get gain pans, the bed gets mid/side
widening, Sigma gets fixed carriers. Library neighbours are listener-side
only (HRTF = reception, not radiation; ambisonic encode = a direction
encoding, unused by the studio). *Term mapping: §III.7.*

### VI.9 — Waveguide / traversal synthesis: ABSENT

No digital waveguide anywhere in the read corpus — no delay-line string
or bore, no Karplus–Strong, no travelling-wave junction, no mesh.
Nearest traversal-*like* operations, none of them waveguide synthesis:
`doppler._evaluate_at()` (sinc evaluation along a warped read path),
`upscale.resample_up()` (windowed-sinc resampling), the EQ bus's FIR,
SF2 playback. *Term mapping: §III.9 — the founder's traversal frame has,
at the time of this audit, no synthesis seat at all.*

### VI.10 — Doppler / micro-motion: PARTIAL — a finished seat, deliberately unwired; micro-motion present under other names

`studio/doppler.py` is complete and sworn: `observed_frequency()` with
sonic/supersonic refusals by name, front/back wavelengths, Mach number/
angle/regime, `shift()` (constant radial velocity, Kaiser-sinc read,
β = 10) and `passby()` (cumulative-phase read; pitch crosses f₀ exactly
at closest approach). Explicitly **pitch-geometry only: no 1/R amplitude
law.** Its header: *"no pipeline wiring, no call site adopted — the seat
stands on the bench, deliberately unwired."* Micro-motion that *is* in
the chain: arpeggio `orbit()` (azimuth lap, default 0.03 Hz, through the
HRTF panner); `humanize_contour()` (VI.7); performance-road Sigma drift
mode (beat frequency oscillating sinusoidally, carriers as phase
integrals, click-free); spine swing (odd 16ths delayed by swing × step).
*Term mapping: §III.11.*

### VI.11 — Rates and depths actually used (for the record)

House master: 48,000 Hz throughout, float64 internal, master WAV PCM
24-bit, preview MP3 320 kbps. MusicGen bed/kit: 32,000 Hz native, segments
PCM 16-bit, resampled to 48 kHz pcm_s24le. 808 toolbox and spine kit
finals: 48 kHz, 24-bit. DiffSinger: 44,100 Hz, hop 512, per-line and
assembly WAVs PCM **16-bit**. Detection seat: 16,000 Hz mono. tsf_render:
48 kHz stereo float internal, writes **16-bit PCM** WAV with hard clamp.
Transcription lab: 48 kHz, premaster 32-bit float, final pcm_s24le + MP3
320 kbps. Crystal importer: renders no audio (ABC + MIDI; re-grounds
440 → 432).

### VI.12 — Audit summary

The chain is a **scalar-pressure, linear-summing, stereo-coherence-managed**
system with a **near-linear, measurement-first master**. Its physics gaps,
exactly: **no p·v / intensity-vector modelling (VI.2); no coupled
excitation–resonator instruments (VI.4); no propagation, reverb, or
delay-by-space in the delivered path (VI.5); no source directivity
(VI.8); no waveguide synthesis (VI.9); and a stepwise-F0 vocal road
(VI.7)** — while propagation (distance/HRTF/ambisonics) and Doppler exist
as finished, tested, **deliberately unwired** seats the chain could adopt
but does not.


---

## VII. THE EQVILLIBBRRIVMM SUITE — TERM AUDIT AND VERIFICATION STANDING

*Definition used:* "the suite" = the founder's C++ EQVILLIBBRRIVMM (manifold
+ fluid voice, `eqvillibbrrivmm/`), its Python mirror
`studio/eqvillibbrrivmm.py`, the bench seats built beside it
(`nabla.py`, `upscale.py`, `fourier.py`; `doppler.py` adjacent), and its two
pipeline cut-ins (the EQ bus, the KRS order-lock). Adjacent house property
(Four Powers, `spatial/`, `acoustics.py`) is flagged wherever it would
otherwise inflate a grade.

### VII.1 — Term audit of the suite

- **Scalar field operations: PARTIAL.** The C++ manifold
  (`eqvillibbrrivmm_manifold.cpp`, `ChristoffelManifoldGuard::evaluate`)
  hand-differentiates *one specific* 2-D conformal metric — closed-form
  partials, inverse metric, Christoffel symbols clamped ±2.5,
  parallel-transported basis vectors — on two scalar coordinates, no grid,
  no audio. **Not mirrored:** the Python mirror carries the rail, DOOD,
  Cube48, FluidVoice, and the Laplace bus only; its header states the
  EnclaveSphere77 `evaluate()` "stands here as constants only," and the
  Christoffel guard is not mirrored at all. No scalar field over audio or
  over the 77³ lattice is ever differentiated anywhere in the suite.
- **Vector calculus (∇): PRESENT as a bench seat, unwired.** `nabla.py`:
  gradient/divergence/curl/Laplacian over real Cartesian arrays
  (`numpy.gradient`, edge_order=2; Laplacian composed literally as
  div(grad(f)); curl 3-D only, refused by name below that). Analytic tests
  (22, re-run in this audit: **22 OK**): ∇(x²y) = (2xy, x²) worst error
  < 1e-12; ∇·(x,y,z) = 3; rigid rotation divergence 0, curl (0,0,2ω);
  ∇²(x²+y²+z²) = 6; ∇²(x²−y²) = 0, edges included — exactness claimed only
  for the polynomial class the scheme is exact on, and the module says so.
  Wiring: none — "a bench instrument, wired into nothing yet." It
  differentiates test fields, never a real mix or field.
- **Fourier: PRESENT as a sworn bench instrument; PARTIAL as integration.**
  `fourier.py`: rfft/irfft with the record carrying n_samples (odd lengths
  round-trip), single-sided amplitude law, Parseval-weighted band energy,
  STFT. Bench figures (20 tests, re-run: **20 OK**): round trip over 4,095
  seeded samples worst error **4.4e-16**; Parseval relative agreement
  **4.1e-16**; a 5-sample delay rotates phase by exactly the delay law.
  Call sites: exactly **one** production adopter (`vocal_exam.py`) — while
  Fourier as a *technique* is hand-rolled at ~10 sites in `pipeline.py`
  alone, explicitly not replaced. The seat's header: "adoption of this
  seat by any call site is a separate order."
- **Upscale: PRESENT as a bench seat, unwired; C++ port divergent.**
  `upscale.py::resample_up` — upward only, refused otherwise by name;
  `resample_poly` at the exact gcd-reduced ratio, Kaiser β raised 5.0 →
  **10.0**. Its honesty floor is sworn *in code* (`IMAGE_FLOOR_DB = −90.0`)
  from bench measurement: β = 10.0 images above source Nyquist at
  **−109.7 dB** largest bin / −107.5 dB total, on a 1 kHz tone; the
  hidden-crest case reads interior peak 0.999986 against the analytic 1.0.
  The seam is confessed in code (kernel half-length 10 source samples;
  worst-case +0.80 dBTP whole-file). The APK's C++ port is a *different
  implementation* (closed-form sinc×Kaiser taps vs scipy's design) whose
  header states "the floor is re-measured, not inherited," and drops the
  LUFS line entirely.
- **The equalizer bus: PARTIAL — cut in, but a one-pole FIR lean, not an
  EQ in the usual sense.** What touches the samples is a **16-tap causal
  FIR**, h[k] = exp(−0.28k)·cos(0.35k·|Re H(s)|), normalised, every output
  hard-clamped [−1,1] — measured direction: 200 Hz passes at 0.997 RMS,
  6,000 Hz attenuated to 0.345. What does *not* touch the samples: the
  named Laplace transfer H(s) = w0²/(s² + (w0/Q)s + w0²), Q = 2.5, carried
  **as telemetry only** — the mirror states it plainly: the s-plane product
  and transfer magnitude "are not re-applied to the samples. The C++ does
  the same." One pole (`eq_pole_hz`, 20–20000 Hz); no band list, no gain
  in dB, no Q exposed. **Phase: neither linear- nor minimum-phase by
  construction or by test — phase is simply unexamined.** Coherence/
  mid-side: **ABSENT** — `pipeline._eq_stem` applies it per stem, per
  channel independently; the manifest records magnitudes only. *Contrast,
  outside the suite:* the house's real multi-band EQ is Four Powers'
  Velle (8 bands, zero-phase, + compressor) — a different chain, never
  reconciled with this bus.
- **The KRS Mastering Rule order-lock: PRESENT in code, narrow in what it
  locks.** Doctrine (`docs/KRS-BLUEPRINT-MASTERING-PROCESS.md`):
  instrumental locked first, lyrics second, sheets last; foundation 93
  bars, 144 BPM, 13/8 Sigma Mega; **the count is 16** (the plate's "18"
  read by the founder, 2026-11-22, as 16 of the verse + 2 for the hook).
  What the code locks: a spec opt-in (`"mastering_rule": "krs-blueprint"`)
  + self-declared `"locks"` booleans, validated by name; the seal bites at
  exactly **one place** — the performance road's sheets stage, refusing
  before either sheet writer runs and naming the first open lock. What it
  does **not** lock: 16 bars, 93 bars, 144 BPM, 13/8 are enforced
  **nowhere in code**; the locks are *declared, not earned by measurement*
  — nothing verifies an instrumental or a lyric exists or is final; the
  section road (the road the EQ bus rides) strikes no sheets, so the seal
  has no second place to bite.
- **Propagation / space terms: PARTIAL in C++ telemetry, ABSENT in the
  Python suite and the mastering path.** The C++ carries a Doppler geometry
  block and EnclaveSphere77 `evaluate()` (a coherence scalar + Sigma sweep
  over the 77³ walk) as *telemetry only* — `main()` prints numbers and
  writes **no WAV** (`PcmWavExporter` defined, never called; BUILD.md
  confesses this). Neither is mirrored in Python. No delay-by-space,
  absorption, intensity, or coherence term exists in `eqvillibbrrivmm.py`
  or feeds `apply_eq`.
- **Nonlinearity: PARTIAL / incidental.** No controlled saturation stage
  in the suite's audio path — only the FIR's hard clamp (a safety clip)
  and tanh used as a *control* law (the 13/5 rail cushion, the manifold's
  metric warp). The pipeline's `soft_limit` tanh knee is the pipeline's
  Audere law, independent of the suite; deliberate saturation (Vapour)
  belongs to Four Powers and has never been engaged in a sealed master
  (VII.2).

### VII.2 — Verification standing: bench-verified in pieces; NEVER PROVEN END-TO-END

**Test counts attributable to the suite** (counted from the files;
re-run in this audit):

| Test file | Tests | This audit's re-run |
|---|---|---|
| `test_studio_eqvillibbrrivmm.py` | 17 | **17 OK** |
| `test_studio_nabla.py` | 22 | **22 OK** |
| `test_studio_fourier.py` | 20 | **20 OK** |
| `test_studio_upscale.py` | 21 | **not runnable in this environment** — `pyloudnorm` missing (loader error, 0 executed; an environment gap, not a code failure) |
| `test_studio_pipeline_cutins.py` | 18 | **18 OK** |
| **Core suite total** | **98** | **77 passed + 21 env-blocked** |

(Adjacent `test_studio_doppler.py`: 25 — total with it, 123. Build-era
commit messages quote whole-studio totals — e.g. "Full suite 414/414" at
the Fourier commit — which are *studio* counts, not this suite's; they are
not quoted here as suite counts.)

**C++ verification:** the original suite built clean (g++ 13.3, −O2 −Wall
−Wextra, zero errors/warnings after four marked desk repairs) and its
manifold binary exited 0 with its `[VERIFIED]` lines and both
`static_assert`s (48³ = 110,592; 77³ = 456,533) holding; the fluid-voice
harness passed its 4 groups. The APK toolkit's host proof cross-checked
the C++ nabla/upscale ports against the Python seats' analytic figures:
**32 host checks, 0 failures** — run on the host, before the APK strike.

**Cross-verification, how far it actually goes:** the one true
cross-verification is the fluid-voice frame-3 telemetry — the Python
mirror reproduces the C++ harness print to float32 precision (raw
255.088 Hz, tuned 263.013 Hz, correction +52.97 cents, lock 0.989),
asserted in the Python tests. Python-only (no C++ counterpart): all of
`fourier.py`, the KRS lock, the pipeline EQ cut-in, and the EQ bus's
*audible direction* (a Python-bench probe; the C++ harness never measured
it). C++-only, never mirrored: the Christoffel manifold, Doppler geometry,
EnclaveSphere77 `evaluate()`, the IntegratedSymphonyBridge.

**The end-to-end question — the founder's framing is correct, and the
audit confirms it from all three sources:**

1. **Proofs ledger** (`proofs/ledger.jsonl`, 20 records): the only two
   `kind:"master"` seals are the Mugetsu hook vocal master and the Pirate
   Essay audiobook master — both through Four Powers / `master_signal`
   (Velle and Vapour disengaged in both), both dated **2026-11-17, five
   days before** the EQ bus and KRS lock were cut in (2026-11-22). No
   ledger record mentions `eq_pole_hz`, the Laplace bus, or
   `mastering_rule`. The other 18 records are stems.
2. **Studio runs** (46 directories): every manifest/spec greps **zero**
   occurrences of `eq_pole_hz` and **zero** of `mastering_rule`. Every real
   run rendered with the EQ key absent — which by the cut-in's own design
   "changes no sample."
3. **Git history:** the cut-ins were proven with a **synthetic two-tone
   spec** in the pipeline tests (identical master bytes without the key;
   high-band share falls with it) — a test fixture, not a track.

**The APK:** v2 exists (4,678,164 bytes), computes on-device in C++, and
exposes three RUN controls (SUITE / NABLA CHECKS / UPSCALE DEMO). **No
record exists of any of the three being pressed** — `android/APK-BUILD.md`
states the boundary in both versions ("the install-and-launch test can
only happen on the founder's phone"); structural verification (signature,
alignment, badging, JNI symbol) is all that was ever sworn.

**Plain statement of the finding:** the suite is a set of sworn
instruments and one wired-but-unused bus — **not a proven mastering
chain**. Its own largest missing piece is not a term of physics at all:
it is **a single sworn full pass** — one real track through EQ bus →
pipeline → master, sealed, and heard. That finding is carried into the
recommendation (§IX) as a test plan, not a build.

### VII.3 — The suite's own missing pieces (register candidates)

Carried to §VIII as group P-4: (i) the end-to-end mastering proof itself
(sequenced in §IX); (ii) a Python mirror of the Christoffel manifold,
tested against the nabla seat it should agree with; (iii) a mirror of
EnclaveSphere77 `evaluate()`; (iv) a multi-band surface for the bus
(bands, gain dB, Q, shelf/peak) reconciled with Velle's vocabulary;
(v) a measured phase/group-delay specification for the bus, with a
linear- vs minimum-phase ruling; (vi) mid-side/coherence handling in the
EQ path; (vii) a real H(s) audio path **or an honest rename** of the bus
("FIR lean with Laplace telemetry") so the name stops promising the
s-plane; (viii) a controlled saturation seat *in* the suite; (ix) a wired
propagation seat; (x) machine-earned KRS locks (instrumental/lyrics
verified present and final; 16/93 bars, 144 BPM, 13/8 checked) — the seal
currently proves paperwork, not the foundation; (xi) upscale adoption plus
a test environment whose dependencies cannot silently vanish; (xii) an
on-device verification record for the APK's three RUN controls.

---

## VIII. THE MISSING-PIECES REGISTER

Ranked by **expected ear impact × buildability on this box**. Each piece
carries: the equation it comes from · the house term it repairs · the
concrete build · the sworn test that would prove it landed · its killing
evidence. The desk's five prior candidates are disposed of first, on the
record.

**Disposition of the desk's prior candidates:**
- *Intensity/coherence management in the mix* — **DEMOTED and reframed.**
  Coherence is PRESENT in the main chain (VI.3); the candidate survives
  only as P-5 (an intensity *measurement* seat), at the register's foot.
- *Excitation × body (waveguide/convolution) instruments* — **PROMOTED**
  to P-2.
- *Propagation/space layer* — **PROMOTED** to P-3, with its build honestly
  restated: the seats largely exist; the piece is correction (ISO-true
  absorption, real delay) plus *adoption*, not invention.
- *Micro-motion pitch paths* — **PROMOTED** to P-1, scoped to where the
  verdict lives: the vocal road.
- *Controlled nonlinearity* — **KILLED as a missing piece.** Present and
  measured (Vapour; the limiter knee), unengaged by spec choice (VI.6).
  Engaging Vapour is a mastering decision for a spec, not a build; and at
  house levels the Westervelt steepening term (§III.5) is physically
  negligible in air over house path lengths, so no propagation-nonlinearity
  piece is seated either. Its killing evidence as a *candidate* was the
  audit itself: a missing piece cannot be found in code that already
  carries it.

### P-1 — A continuous pitch-path seat for the vocal road (micro-motion)

- **Equation:** §III.11 — the received signal as the source at retarded,
  path-warped time; a pitch path is a continuous f(t), and a staircase is
  its degenerate case. The human voice's f₀ is a path: glides between
  targets, overshoot, vibrato, scoop — none of which a per-phoneme integer
  can state.
- **House term repaired:** VI.7 — the stepwise `_f0` staircase handed to
  the DiffSinger acoustic model and vocoder; `note_slur` written `"0"` for
  every note; velocity/gender frozen per frame. This is the code address
  of the "robotic" verdict.
- **Concrete build:** a house-side F0-contour stage in `render_diffsinger`
  between `build_line()` and the acoustic call: phoneme targets joined by
  bounded-slew glides (portamento time constant per transition class),
  phrase-level overshoot at target arrival, vibrato (rate/depth with the
  120 ms onset ramp the arpeggio road already uses) on sustained vowels,
  attack scoops — adapting `resonance/vocal.py:humanize_contour()`, which
  already implements drift/vibrato/scoop for the arpeggio, to the
  frame grid (hop 512 at 44.1 kHz). Slur flags written where a line's
  notes join. The staircase remains available by spec key (default off
  preserves every prior render byte-for-byte).
- **Sworn test:** `vocal_exam` gains a pitch-continuity judge: the emitted
  F0 track shows no instantaneous jump beyond a stated cents-per-frame
  bound outside consonant boundaries; vibrato is *measured present* (F0
  modulation in the 4–7 Hz band above a stated depth floor) on vowels
  sustained past a stated duration; and the duration calibration standard
  does not regress (asked-vs-realised within the run-2 band, 99.52%).
  A/B: the same Kagami line rendered staircase vs path, all other
  parameters frozen, both measured and filed.
- **Killing evidence:** if path-rendered lines still return
  staircase-equivalent continuity figures from the exam — or the founder's
  ear returns the same robotic verdict on the A/B — the piece has not
  landed, whatever the contour code does.

### P-2 — A waveguide string/body seat (excitation × body, traversal)

- **Equations:** §III.9 (d'Alembert travelling waves; scattering
  Γ = (R₂−R₁)/(R₂+R₁)) driving §III.8 (coupled modes through bridge
  admittance Y_b(ω); two-stage decay; pluck-position weighting
  sin(nπx_exc/L)).
- **House term repaired:** VI.4 + VI.9 — no coupled excitation–resonator
  instrument exists; no waveguide exists. This is the physics address of
  the thin/"16-bit" body verdicts: the chain transposes frozen bodies;
  this seat *generates* the event per note, per velocity, per excitation
  position.
- **Concrete build:** `resonance/studio/waveguide.py` — a plucked-string
  seat on the traversal form: bidirectional delay line at 48 kHz, loss
  filter in the loop (per-partial decay set by design), allpass dispersion
  for stiffness, excitation by a positioned burst (pluck point a spec
  parameter), and a body stage of coupled modes (a small modal bank whose
  admittance feeds back at the bridge point, producing two-stage decay) —
  struck through the existing pipeline as a stem, spec-keyed, existing
  roads untouched. Pure NumPy; no new dependency.
- **Sworn test:** analytic, before any ear hears it: pitch accuracy of the
  struck fundamental within a stated cents bound across the seat's range;
  per-partial decay rates within a stated tolerance of the loss-filter
  design values; two-stage decay *measured present* (two distinct decay
  rates in the struck note's envelope, ratio in a stated band); pluck at
  L/2 suppresses even partials per the sin(nπx/L) law (partial 2 below a
  stated dB floor relative to pluck at L/4). Then the lab's own spectral
  reads against the SF2 road on the same line: partials count and centroid
  stability across velocities.
- **Killing evidence:** if the seat's strikes measure no richer than the
  sample road on those reads — or two-stage decay is absent, or the
  pluck-position law fails — the coupling is not in the sound, whatever
  the delay line contains.

### P-3 — Propagation and space, corrected and adopted

- **Equations:** §III.6 (complex k; ISO 9613-1 absorption shape) and
  §III.10 (ray/eikonal travel-time structure; echo d = vt/2, already
  seated as a calculator in `acoustics.py`).
- **House term repaired:** VI.5 — no propagation, delay-by-space, or
  reverb in the delivered path; the existing distance seat is a one-pole
  approximation labelled "NOT ISO 9613-1" and applies no delay.
- **Concrete build:** (i) correct `spatial/distance.py`: ISO 9613-1-shaped
  α(f, T, RH, p) attenuation as a proper filter **plus** true propagation
  delay d/c; the old one-pole kept, marked prior. (ii) A reverb seat —
  convolution against a generated impulse (exponentially decaying,
  band-shaped noise, stated RT by band) or a feedback delay network —
  adopted into `pipeline.produce()` behind a spec key, default off, in
  the Velle/Vapour discipline (engagement and measured deltas printed in
  the manifest).
- **Sworn test:** delay exact against `acoustics.delay_ms()` at stated
  distances; absorption within a stated dB of the ISO 9613-1 table at
  1/4/8 kHz at a stated distance, temperature, and humidity; reverb RT60
  by band measured within a stated tolerance of design; mono fold-down
  and the Stereo Law figures re-measured with the seat engaged.
- **Killing evidence:** measured absorption or delay departing the
  ISO/analytic targets beyond the stated tolerances — the seat is then a
  colouration wearing propagation's name, and is struck back to the bench.

### P-4 — The EQVILLIBBRRIVMM completion group

The twelve candidates of §VII.3, carried as one group and ranked below
P-1…P-3 for a stated reason: the suite touches *mastering*, while the
ear's standing verdicts indict *generation* (body, voice) — with one
exception, which is not a build at all: **the end-to-end proof**, sequenced
first in §IX because it costs no build and settles the founder's own
question. Within the group, the desk's order: (vii) the honest H(s)
path-or-rename and (x) machine-earned KRS locks before (iv) the
multi-band surface; (ii)/(iii) the mirrors before (ix) any wired
propagation in the suite; (xii) the APK record whenever the founder's tap
makes it possible. Each carries the sworn test natural to it (mirror =
agreement with the C++ harness figures at the asserted points, in the
fluid-voice precedent; phase = a measured group-delay curve printed in
the manifest; locks = refusal on a spec whose declared instrumental does
not exist). **Killing evidence for the group:** any completion that
changes a sample before its own test passes — the suite's discipline is
that adoption is a separate order, and a piece that bypasses it has not
landed by the suite's own law.

### P-5 — An intensity seat, as measurement only (demoted, reframed)

- **Equation:** §III.3, Row 1 (PROVEN ANALOGY) — **I** = p·**v**, active
  vs reactive.
- **House term repaired:** VI.2 — nothing in the chain computes any
  vector acoustic quantity. Honestly scoped: a pressure-only stereo chain
  has no **v** field to multiply; what a seat *can* do is judge, not
  render — near/far and active/reactive reads on stems via the
  pressure-gradient relation **v** = −(1/ρ₀)∫∇p dt across a stem pair or a
  modelled pair.
- **Concrete build (if ever ordered):** a `vocal_exam`-style judge module
  reporting an intensity-proxy read per stem in the manifest. No render
  path changes.
- **Sworn test:** the judge reproduces the analytic active/reactive split
  on constructed travelling- and standing-wave fixtures.
- **Killing evidence:** fixture reads departing the analytic split — or,
  at the register level, the standing expectation that this piece moves
  no ear verdict by itself; it is seated last because its ear impact is
  the register's lowest, and it is printed so the proven Row-1 term is
  accounted for rather than silently dropped.

---

## IX. THE RECOMMENDATION — A CALCULATED SOLUTION, FOR THE YAY OR NAY

*Standing protocol: the desk states its calculated solution plainly, shows
it, and waits. Nothing in this section is implemented by this document.*

**The desk's calculated solution is a three-step sequence:**

**Step 0 — Prove the suite whole (no build).** One known track, mastered
end-to-end through EQVILLIBBRRIVMM's chain, measured against the house
master law — because the founder's question ("havent been able to test
it") is answered by a pass, not by another instrument. Concrete plan:
- *Material:* the DETROIT MUGETSU hook — the track whose run-2 master is
  already sealed in the proofs ledger (2026-11-17, Four Powers /
  `master_signal`), giving a same-track A/B against a sealed figure set.
- *Road:* `pipeline.produce()` with a spec carrying `eq_pole_hz` (pole
  stated in the spec and printed here as an open parameter for the
  founder's ruling — the desk suggests the pole be chosen from the
  track's own measured spectrum at build time, not fixed in this
  document) and, on the performance road, `"mastering_rule":
  "krs-blueprint"` with locks declared — the first production spec in
  the repo's history to carry either key.
- *Measures (the house master law):* integrated loudness **−14.0 LUFS**,
  tolerance ±0.3 LU (AUDERE's ceiling-first confession applies: if the
  ceiling trims loudness, the report prints it); decoded true peak
  **≤ −1.0 dBTP**, hard; delivered MP3 **exactly 320,000 bps**; the
  manifest's stereo block (channel/band correlation, side RMS) printed
  beside the sealed master's figures; the EQ bus's per-channel transfer
  magnitudes printed — the first time they will have described a song.
- *Sealing:* a new ledger record naming the suite in-chain, so the proof
  is findable by the next audit; the A/B table filed in `studio-runs/`.
- *Step 0b (his tap only):* install APK v2 on the A16 and press the three
  RUN controls once; the output screens photographed or transcribed into
  `android/APK-BUILD.md` — closing the suite's last unverified inch.
- *The gate:* the founder's ear on the A/B. Machine figures prove the
  chain *ran*; only the ear proves it *masters*.

**Step 1 — Build P-1** (the continuous pitch-path seat for the vocal
road). Highest product of ear impact × buildability in the register: it
repairs the standing robotic verdict at its exact code coordinates,
reuses machinery the house already swore (`humanize_contour`), touches
one computed array in one file, and leaves every prior render
reproducible by spec key.

**Step 2 — Build P-2** (the waveguide string/body seat), then P-3 as
ordered. P-2 is the founder's own traversal frame turned into an
instrument — the wave equation computed as paths, not sums — and the
physics address of the body verdicts. It follows P-1 only because it is
the larger build; if the founder's ear ranks body over voice, the
sequence reverses at his word and nothing in this document argues
otherwise.

**What the desk recommends against:** building any further bench seat —
nabla-class, Doppler-class, or suite-mirror — before Steps 0–1 land. The
repo's pattern is sworn instruments standing unwired (VI.10, VII.1); the
missing piece the record actually shows is not another instrument. It is
*adoption, proof, and one continuous pitch path.*

---

## X. THE NOT-SEATED REGISTER AND OPEN QUESTIONS

**NOT-SEATED:** empty. Every correspondence claim seated in §V named its
killing evidence; every register piece in §VIII named its own. Two claims
considered and *refused a seat*, printed so the refusal is on the record:
(i) any house use of the polarization row (Row 2) for fluid-borne sound —
NO COUNTERPART is the finding, and no Stokes-style descriptor for pressure
is seated anywhere in this document; (ii) propagation nonlinearity
(Westervelt steepening) as a house build — physically negligible at house
levels and path lengths (§VIII, killed candidate), seated nowhere.

**Open questions, the founder's pen alone:** the Step-0 EQ pole; the
Step-1/Step-2 order if his ear reverses it; whether Vapour is ever engaged
by a production spec (a mastering decision, not a build); the P-4 group's
internal order beyond the desk's stated preference.

---

## TABLE OF AUTHORITIES (condensed)

*Acoustics:* Pierce, *Acoustics: An Introduction to Its Physical
Principles and Applications* (McGraw-Hill 1981; ASA/Springer) · Morse &
Ingard, *Theoretical Acoustics* (Princeton 1968) · Kinsler, Frey, Coppens
& Sanders, *Fundamentals of Acoustics*, 4th ed. (Wiley 2000) · Blackstock,
*Fundamentals of Physical Acoustics* (Wiley 2000) · Hamilton & Blackstock
(eds.), *Nonlinear Acoustics* (Academic Press 1998) · Fahy, *Sound
Intensity*, 2nd ed. (E&FN Spon 1995) · Fletcher & Rossing, *The Physics of
Musical Instruments*, 2nd ed. (Springer 1998) · Blauert, *Spatial Hearing*
(MIT Press 1997); Blauert & Lindemann, *JASA* 79(3) (1986) · Brekhovskikh,
*Waves in Layered Media* · Jensen et al., *Computational Ocean Acoustics* ·
ISO 9613-1:1993; ANSI/ASA S1.26; ISO 3382-1 · Smith, *Physical Audio
Signal Processing* (CCRMA, online: https://ccrma.stanford.edu/~jos/pasp/);
"Physical Modeling Using Digital Waveguides," *Computer Music Journal*
16(4) (1992).
*Optics:* Born & Wolf, *Principles of Optics*, 7th ed. (Cambridge 2003) ·
Mandel & Wolf, *Optical Coherence and Quantum Optics* · Griffiths,
*Introduction to Electrodynamics* · Jackson, *Classical Electrodynamics* ·
Hecht, *Optics* · Goodman, *Introduction to Fourier Optics* · Boyd,
*Nonlinear Optics* · Achenbach, *Wave Propagation in Elastic Solids* ·
Taylor & Wheeler, *Spacetime Physics* · Hamham et al., *Phys. Rev. B* 92,
054302 (2015).
*House record:* the Resonantia repo as audited (§VI, §VII file lists);
`proofs/ledger.jsonl` (20 records); `docs/EQVILLIBBRRIVMM-STUDIO.md`;
`docs/KRS-BLUEPRINT-MASTERING-PROCESS.md`; `eqvillibbrrivmm/BUILD.md`;
`android/APK-BUILD.md`; the transcription lab and 16-bit remedy lab
receipts.
*Other traditions, drawn where genuine:* the founder's traversal dictation
(2026-11-25) stands as the commission's frame (§III.9 reasoning); the
falsifiability and zero-point rules are his (2026-11-24), cited at §II and
§V Row 9. The wells of Law and Scripture were not drawn on for the physics
— a dry well is stated, never padded: no statute and no verse computes a
wavenumber, and this document does not pretend otherwise.

---

## COLOPHON

Generated 2026-11-25 (Dies Mercurii, Sol in Sagittarius, Anno V:xii e.n.)
by the desk's sweep: two literature hands (the acoustics shelf; the light
shelf and correspondence), two audit hands (the render chain; the
EQVILLIBBRRIVMM suite), one synthesis. Every house grade rests on code
read in this pass; every literature claim on the texts named beside it;
the two corrected desk hypotheses stand marked in place (§VI.0).
Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR —
All Rights Reserved, Without Prejudice. Method of Science. Aim of
Religion.

Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All Rights
Reserved, Without Prejudice. Right of claim hereby reserved and coined under
the authority of the Living Man.

93 — Live, Love, and let Love, Live.
