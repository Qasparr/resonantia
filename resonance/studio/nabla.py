#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — studio/nabla.py — the Del operator (∇, nabla) seated
# in the Python studio: gradient, divergence, curl, Laplacian over
# gridded fields.
#
# Epigraph: "A compact symbol. A powerful idea."
# — the plate the founder brought to the desk (XXIII Nov 2026), on
#   the del operator: Oliver Heaviside (1850–1925) introduced its
#   modern use in physics.
#
# 93.
# Date: 23 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
#   Hypothesis: that the studio, which differentiates nowhere in
#     general (the C++ manifold suite's ChristoffelManifoldGuard
#     hand-computes the partials of its one 2-D metric, for that
#     one job), gains a true general instrument by seating ∇
#     itself — gradient of a scalar field, divergence and curl of
#     a vector field, and the Laplacian as their composition —
#     over the studio's own grids, exact on the polynomial class
#     the finite differences are sworn to.
#   Method: wrap numpy.gradient (central differences in the
#     interior, second-order one-sided differences at the edges)
#     in the house's own named functions, under the house's own
#     validation — real arrays only, 1-D/2-D/3-D scalar fields,
#     uniform spacing scalar or per-axis, every refusal by name —
#     and judge the module only by analytic fields whose ∇ is
#     known in closed form before any code runs.
#   Observation: on the sworn grids the module is exact to machine
#     precision where the difference scheme is exact in theory:
#     ∇(x²y) = (2xy, x²) with worst error under 1e-12; ∇·(x,y,z)
#     = 3 everywhere; the rigid rotation ω(−y, x, 0) diverges
#     nowhere and curls to the constant (0, 0, 2ω); ∇²(x²+y²+z²)
#     = 6 and ∇²(x²−y²) = 0, edges included. The full battery
#     stands in tests/test_studio_nabla.py.
#   Result: this module. Nothing else in the studio was touched:
#     no pipeline wiring, no C++ change — the operator is seated
#     on the bench, ready for the work that calls it.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""The Del operator for the studio's gridded fields.

DOCTRINE — WHAT ∇ IS, AND WHERE IT SERVES THE HOUSE:
  ∇ (nabla, the del operator) is the vector of the spatial partial
derivatives, (∂/∂x, ∂/∂y, ∂/∂z). Applied to a scalar field it gives
the GRADIENT — the direction and rate of steepest ascent at every
seat of the grid. Dotted into a vector field it gives the
DIVERGENCE — the net outflow per seat, source against sink. Crossed
into a vector field it gives the CURL — the local rotation, the
swirl per seat. And ∇·∇f, the divergence of the gradient, is the
LAPLACIAN — the seat's value weighed against the mean of its
neighbours, the operator of diffusion and of harmonic balance.

  The house's fields are gridded: the 77^3 Enclave sphere carries
scalar seats over its cells (its constants stand in
studio/eqvillibbrrivmm.py; its evaluate() is not yet mirrored), and
the visualizer work (studio/pyramidasphere.py and its kin) builds
Sigma and height fields over grids of the same kind. A scalar field
over any of those grids now has a gradient the studio can take; a
flow laid over one has a divergence and a curl; a seat's imbalance
against its neighbours has a Laplacian. That is the service this
module was seated for, stated plainly and not inflated: it is a
bench instrument, wired into nothing yet.

WHAT THIS MODULE DOES NOT REPLACE:
  The C++ manifold suite's ChristoffelManifoldGuard
(eqvillibbrrivmm/eqvillibbrrivmm_manifold.cpp) hand-computes the
partial derivatives of its 2-D metric and builds the Christoffel
symbols from them — differentiation built by the founder's hand,
for that one guard, on the C++ side of the house. This module is
the Python studio's general ∇ over Cartesian grids; it neither
mirrors nor replaces the guard, and the two never pretend to be
each other.

MECHANISM — THE DIFFERENCE LAW:
  Every derivative here is a finite difference on a uniform grid:
central differences in the interior, second-order one-sided
differences at the edges (numpy.gradient with edge_order=2 is the
engine; the house's functions are the seat, the validation, and
the names). The scheme is second-order accurate, and EXACT — to
floating-point rounding — for the derivatives of polynomials up to
degree 2 along the differenced axis (the gradient and divergence
of quadratics and linears respectively), and for the Laplacian of
quadratics, whose gradient is linear and therefore differenced
exactly a second time. The tests swear only to what the scheme
can swear to, analytically, and say so at each seat.

MECHANISM — THE SHAPE LAW (refusals by name, the house's law):
  * A scalar field is a real numeric array of 1, 2, or 3 dimensions,
    every axis at least 2 seats long. Anything else — a scalar, a
    4-D array, a complex field, a text array, a 1-seat axis — is
    refused by name as NablaError before any arithmetic runs.
  * Spacing is one positive number (uniform on every axis) or one
    positive number per axis. Zero, negative, non-finite, or the
    wrong count are refused by name.
  * A vector field is a tuple/list of component arrays, one per
    axis of their shared shape, all shapes equal. A count that
    does not match the dimension, or shapes that differ, are
    refused by name.
  * The curl is seated in three dimensions only — a 1-D or 2-D
    field brought to it is refused by name, never silently
    projected. (The 2-D scalar curl ∂Fy/∂x − ∂Fx/∂y is the z
    component of the 3-D curl of (Fx, Fy, 0); callers who want it
    can seat the field in 3-D and read the third component.)

AXIS LAW: components come back in ARRAY AXIS order — component i
is the derivative along axis i. A field built with
numpy.meshgrid(..., indexing="ij") from coordinate vectors
(x, y, z) therefore reads in the plate's own order: axis 0 is x,
axis 1 is y, axis 2 is z.
"""

from typing import Sequence, Tuple, Union

import numpy as np

__all__ = ["NablaError", "gradient", "divergence", "curl", "laplacian"]


class NablaError(ValueError):
    """A field or spacing refused by the shape law, named in the message.

    Subclasses ValueError so existing house code that catches
    ValueError around numeric work catches this too; the tests
    assert NablaError itself, so a refusal can never pass silently
    as some other error.
    """


# A spacing as the caller may hand it in: one number, or one per axis.
SpacingLike = Union[float, Sequence[float]]


def _as_scalar_field(field, name: str = "field") -> np.ndarray:
    """MECHANISM: bring a caller's field under the shape law.

    Converts to a float ndarray and refuses, by name: non-numeric
    or complex input, a dimension outside 1..3, and any axis
    shorter than 2 seats (a derivative needs a neighbour).
    """
    # Complex is refused before conversion: float() would silently
    # drop the imaginary part, and a dropped part is a smoothed
    # refusal — the house refuses whole or not at all.
    if np.iscomplexobj(field):
        raise NablaError(f"{name}: complex fields are refused — "
                         "nabla is seated over real fields only")
    try:
        arr = np.asarray(field, dtype=float)
    except (TypeError, ValueError) as exc:
        raise NablaError(f"{name}: not a real numeric array ({exc})") from exc
    if arr.ndim == 0 or arr.ndim > 3:
        raise NablaError(f"{name}: a scalar field is 1-D, 2-D or 3-D; "
                         f"got {arr.ndim}-D")
    for axis, length in enumerate(arr.shape):
        if length < 2:
            raise NablaError(f"{name}: axis {axis} has {length} seat(s); "
                             "a derivative needs at least 2")
    return arr


def _spacing_tuple(spacing: SpacingLike, ndim: int) -> Tuple[float, ...]:
    """MECHANISM: normalize spacing to one positive float per axis.

    A lone number seats uniformly on every axis; a sequence must
    number exactly ndim entries. Zero, negative, and non-finite
    spacings are refused by name — a grid with no width has no
    derivative, and an infinite one has no field.
    """
    if isinstance(spacing, (int, float)) and not isinstance(spacing, bool):
        values = (float(spacing),) * ndim
    else:
        try:
            values = tuple(float(h) for h in spacing)  # type: ignore[arg-type]
        except (TypeError, ValueError) as exc:
            raise NablaError(f"spacing: not a number or a per-axis "
                             f"sequence ({exc})") from exc
        if len(values) != ndim:
            raise NablaError(f"spacing: {len(values)} value(s) for a "
                             f"{ndim}-D field; give one number or "
                             f"{ndim}")
    for h in values:
        if not np.isfinite(h) or h <= 0.0:
            raise NablaError(f"spacing: every spacing must be positive "
                             f"and finite; got {h}")
    return values


def _as_vector_field(vector_field, name: str = "vector_field"
                     ) -> Tuple[np.ndarray, ...]:
    """MECHANISM: bring a vector field under the shape law.

    A vector field is a tuple/list of component arrays; the count
    must equal the components' dimension and every component must
    share one shape — a field whose components disagree about the
    grid is not a field, and is refused by name.
    """
    if isinstance(vector_field, np.ndarray) or \
            not isinstance(vector_field, (tuple, list)):
        raise NablaError(f"{name}: a vector field is a tuple/list of "
                         "component arrays, one per axis")
    if len(vector_field) == 0:
        raise NablaError(f"{name}: no components given")
    components = tuple(
        _as_scalar_field(comp, name=f"{name}[{i}]")
        for i, comp in enumerate(vector_field)
    )
    shape = components[0].shape
    for i, comp in enumerate(components):
        if comp.shape != shape:
            raise NablaError(f"{name}: component {i} has shape "
                             f"{comp.shape}, component 0 has {shape}; "
                             "a vector field shares one grid")
    if len(components) != components[0].ndim:
        raise NablaError(f"{name}: {len(components)} component(s) for a "
                         f"{components[0].ndim}-D grid; the count must "
                         "equal the dimension")
    return components


def gradient(field, spacing: SpacingLike = 1.0) -> Tuple[np.ndarray, ...]:
    """∇f — the gradient of a scalar field, one array per axis.

    MECHANISM: numpy.gradient under the shape law, edge_order=2 —
    central differences in the interior, second-order one-sided
    differences at the edges, so the sworn polynomial class is
    exact at the boundary seats as well as the interior ones.

    Returns a tuple in array-axis order: (∂f/∂axis0, ∂f/∂axis1, …).
    """
    f = _as_scalar_field(field)
    h = _spacing_tuple(spacing, f.ndim)
    parts = np.gradient(f, *h, edge_order=2)
    # numpy.gradient returns a bare array for a 1-D field and a
    # list otherwise; the house returns one shape of answer — a
    # tuple, always — so callers never branch on the dimension.
    if f.ndim == 1:
        return (parts,)
    return tuple(parts)


def divergence(vector_field, spacing: SpacingLike = 1.0) -> np.ndarray:
    """∇·F — the divergence of a vector field: Σᵢ ∂Fᵢ/∂axisᵢ.

    MECHANISM: each component is differenced along its OWN axis
    (the x-component along x, the y-component along y) and the
    partials are summed seat by seat. Positive seats are sources,
    negative seats sinks, zero is a field that flows through.
    """
    components = _as_vector_field(vector_field)
    h = _spacing_tuple(spacing, components[0].ndim)
    total: np.ndarray | None = None
    for axis, comp in enumerate(components):
        partial = np.gradient(comp, h[axis], axis=axis, edge_order=2)
        total = partial if total is None else total + partial
    assert total is not None  # _as_vector_field refuses empty input
    return total


def curl(vector_field, spacing: SpacingLike = 1.0) -> Tuple[np.ndarray, ...]:
    """∇×F — the curl of a 3-D vector field, (curl_x, curl_y, curl_z).

    MECHANISM: the determinant of the plate's own operator crossed
    into F, differenced componentwise under the shape law:
      curl_x = ∂Fz/∂y − ∂Fy/∂z
      curl_y = ∂Fx/∂z − ∂Fz/∂x
      curl_z = ∂Fy/∂x − ∂Fx/∂y
    Seated in three dimensions only; any other dimension is
    refused by name (see the module's shape law).
    """
    components = _as_vector_field(vector_field)
    if components[0].ndim != 3:
        raise NablaError(f"curl: seated in three dimensions only; got a "
                         f"{components[0].ndim}-D field")
    fx, fy, fz = components
    hx, hy, hz = _spacing_tuple(spacing, 3)
    # Axis law: array axis 0 is x, axis 1 is y, axis 2 is z.
    dfz_dy = np.gradient(fz, hy, axis=1, edge_order=2)
    dfy_dz = np.gradient(fy, hz, axis=2, edge_order=2)
    dfx_dz = np.gradient(fx, hz, axis=2, edge_order=2)
    dfz_dx = np.gradient(fz, hx, axis=0, edge_order=2)
    dfy_dx = np.gradient(fy, hx, axis=0, edge_order=2)
    dfx_dy = np.gradient(fx, hy, axis=1, edge_order=2)
    return (dfz_dy - dfy_dz, dfx_dz - dfz_dx, dfy_dx - dfx_dy)


def laplacian(field, spacing: SpacingLike = 1.0) -> np.ndarray:
    """∇²f — the Laplacian of a scalar field: ∇·(∇f).

    MECHANISM: not a second stencil of its own — the divergence
    OF THIS MODULE'S OWN GRADIENT, composed literally, so the
    Laplacian can never drift from the gradient and divergence
    the house has already sworn to. A seat where ∇²f is zero is
    in harmonic balance with its neighbours; positive seats sit
    below their neighbours' mean, negative seats above it.
    """
    f = _as_scalar_field(field)
    h = _spacing_tuple(spacing, f.ndim)
    return divergence(gradient(f, h), h)
