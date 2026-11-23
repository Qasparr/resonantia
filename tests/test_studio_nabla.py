#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — tests/test_studio_nabla.py — the Del operator judged
# analytically: every field below is chosen because its ∇ is known
# in closed form before the code runs.
#
# 93.
# Date: 23 November 2026.
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
# ARR — All Rights Reserved, Without Prejudice.
# Method of Science, Aim of Religion — Scientific Illuminism.
#
# SCIENTIFIC ILLUMINISM: a difference scheme is sworn only to the
# class it is exact on. studio/nabla.py differences with central
# differences in the interior and second-order one-sided
# differences at the edges, so it is exact — to floating-point
# rounding — for the gradient of quadratics, the divergence of
# linears, the curl of linears, and the Laplacian of quadratics,
# AT EVERY SEAT, EDGES INCLUDED. These tests therefore assert with
# tight tolerances over the WHOLE grid, boundary seats sworn with
# the interior ones, and they assert the shape law's refusals by
# the module's own error name. No snapshots: a stored array could
# only prove the code agrees with itself.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""Tests for resonance/studio/nabla.py, against closed-form ∇."""

import unittest

import numpy as np

from resonance.studio import nabla
from resonance.studio.nabla import NablaError

# The sworn tolerance: the scheme is exact in theory on the fields
# below, so what remains is floating-point rounding on grids of
# this size — measured at ~1e-15 in the bench probe. 1e-9 leaves
# three orders of headroom and still catches any real drift.
TOL = dict(rtol=1e-9, atol=1e-9)


def grid2(nx=9, ny=7, hx=0.25, hy=0.5):
    """An (x, y) meshgrid in 'ij' indexing: axis 0 is x, axis 1 is y."""
    x = np.arange(nx) * hx
    y = np.arange(ny) * hy
    return np.meshgrid(x, y, indexing="ij"), (hx, hy)


def grid3(n=6, h=0.4):
    """An (x, y, z) meshgrid in 'ij' indexing on a uniform spacing."""
    c = np.arange(n) * h
    return np.meshgrid(c, c, c, indexing="ij"), h


class TestGradient(unittest.TestCase):
    """∇f against fields whose gradient is written beside them."""

    def test_quadratic_gradient_exact_everywhere(self):
        # f(x, y) = x²y  →  ∇f = (2xy, x²). Exact on the whole
        # grid, edges included — the edge seats are the point of
        # the second-order one-sided differences.
        (X, Y), h = grid2()
        gx, gy = nabla.gradient(X ** 2 * Y, h)
        np.testing.assert_allclose(gx, 2 * X * Y, **TOL)
        np.testing.assert_allclose(gy, X ** 2, **TOL)

    def test_gradient_of_constant_field_is_zero(self):
        (X, Y), h = grid2()
        gx, gy = nabla.gradient(np.full_like(X, 7.0), h)
        np.testing.assert_allclose(gx, 0.0, **TOL)
        np.testing.assert_allclose(gy, 0.0, **TOL)

    def test_gradient_1d(self):
        # f(x) = x² → f′ = 2x, exact at every seat of a 1-D grid.
        x = np.arange(11) * 0.1
        (gx,) = nabla.gradient(x ** 2, 0.1)
        np.testing.assert_allclose(gx, 2 * x, **TOL)

    def test_gradient_3d(self):
        # f(x, y, z) = x² + yz → ∇f = (2x, z, y).
        (X, Y, Z), h = grid3()
        gx, gy, gz = nabla.gradient(X ** 2 + Y * Z, h)
        np.testing.assert_allclose(gx, 2 * X, **TOL)
        np.testing.assert_allclose(gy, Z, **TOL)
        np.testing.assert_allclose(gz, Y, **TOL)

    def test_scalar_spacing_applies_to_every_axis(self):
        # One number seats uniformly: the same field on a doubled
        # grid spacing must give the same analytic gradient.
        (X, Y), _ = grid2(hx=0.5, hy=0.5)
        gx, gy = nabla.gradient(X ** 2 * Y, 0.5)
        np.testing.assert_allclose(gx, 2 * X * Y, **TOL)
        np.testing.assert_allclose(gy, X ** 2, **TOL)


class TestDivergence(unittest.TestCase):
    """∇·F against fields whose divergence is written beside them."""

    def test_radial_field_divergence_is_three(self):
        # F = (x, y, z) → ∇·F = 1 + 1 + 1 = 3, at every seat.
        (X, Y, Z), h = grid3()
        div = nabla.divergence((X, Y, Z), h)
        np.testing.assert_allclose(div, 3.0, **TOL)

    def test_rigid_rotation_diverges_nowhere(self):
        # F = ω(−y, x, 0) → ∂(−ωy)/∂x + ∂(ωx)/∂y + 0 = 0: a pure
        # rotation neither sources nor sinks.
        (X, Y, Z), h = grid3()
        omega = 1.7
        div = nabla.divergence((-omega * Y, omega * X, np.zeros_like(X)), h)
        np.testing.assert_allclose(div, 0.0, **TOL)


class TestCurl(unittest.TestCase):
    """∇×F against fields whose curl is written beside them."""

    def test_rigid_rotation_curl_is_constant_2omega(self):
        # F = ω(−y, x, 0) → ∇×F = (0, 0, ∂(ωx)/∂x − ∂(−ωy)/∂y)
        # = (0, 0, 2ω): the curl of a rigid rotation is twice its
        # angular velocity, uniform at every seat.
        (X, Y, Z), h = grid3()
        omega = 1.7
        cx, cy, cz = nabla.curl((-omega * Y, omega * X, np.zeros_like(X)), h)
        np.testing.assert_allclose(cx, 0.0, **TOL)
        np.testing.assert_allclose(cy, 0.0, **TOL)
        np.testing.assert_allclose(cz, 2 * omega, **TOL)

    def test_gradient_field_is_irrotational(self):
        # ∇×(∇f) = 0 for any f — sworn here on f = x² + yz, whose
        # gradient the module itself takes: the composition of the
        # house's own operators must close.
        (X, Y, Z), h = grid3()
        grad = nabla.gradient(X ** 2 + Y * Z, h)
        cx, cy, cz = nabla.curl(grad, h)
        np.testing.assert_allclose(cx, 0.0, **TOL)
        np.testing.assert_allclose(cy, 0.0, **TOL)
        np.testing.assert_allclose(cz, 0.0, **TOL)


class TestLaplacian(unittest.TestCase):
    """∇²f against fields whose Laplacian is written beside them."""

    def test_laplacian_of_r_squared_is_six(self):
        # f = x² + y² + z² → ∇²f = 2 + 2 + 2 = 6, edges included.
        (X, Y, Z), h = grid3()
        lap = nabla.laplacian(X ** 2 + Y ** 2 + Z ** 2, h)
        np.testing.assert_allclose(lap, 6.0, **TOL)

    def test_harmonic_function_laplacian_is_zero(self):
        # f = x² − y² is harmonic: ∇²f = 2 − 2 = 0. Every seat in
        # balance with its neighbours.
        (X, Y), h = grid2()
        lap = nabla.laplacian(X ** 2 - Y ** 2, h)
        np.testing.assert_allclose(lap, 0.0, **TOL)


class TestShapeLaw(unittest.TestCase):
    """The refusals: every bad shape named by NablaError."""

    def test_4d_field_refused(self):
        with self.assertRaises(NablaError):
            nabla.gradient(np.zeros((3, 3, 3, 3)))

    def test_scalar_refused(self):
        with self.assertRaises(NablaError):
            nabla.gradient(5.0)

    def test_one_seat_axis_refused(self):
        with self.assertRaises(NablaError):
            nabla.gradient(np.zeros((1, 4)))

    def test_complex_field_refused(self):
        with self.assertRaises(NablaError):
            nabla.gradient(np.ones((3, 3), dtype=complex))

    def test_text_field_refused(self):
        with self.assertRaises(NablaError):
            nabla.gradient([["a", "b"], ["c", "d"]])

    def test_spacing_wrong_count_refused(self):
        with self.assertRaises(NablaError):
            nabla.gradient(np.zeros((3, 3, 3)), (1.0, 1.0))

    def test_spacing_zero_and_negative_refused(self):
        f = np.zeros((3, 3))
        with self.assertRaises(NablaError):
            nabla.gradient(f, 0.0)
        with self.assertRaises(NablaError):
            nabla.gradient(f, -1.0)

    def test_vector_field_mismatched_shapes_refused(self):
        with self.assertRaises(NablaError):
            nabla.divergence((np.zeros((3, 3)), np.zeros((4, 4))))

    def test_vector_field_wrong_count_refused(self):
        # Two components laid over a 3-D grid is not a 3-D field.
        with self.assertRaises(NablaError):
            nabla.divergence((np.zeros((3, 3, 3)), np.zeros((3, 3, 3))))

    def test_vector_field_bare_array_refused(self):
        with self.assertRaises(NablaError):
            nabla.divergence(np.zeros((3, 3)))

    def test_curl_refuses_2d_by_name(self):
        f = (np.zeros((4, 4)), np.zeros((4, 4)))
        with self.assertRaises(NablaError):
            nabla.curl(f)


if __name__ == "__main__":
    unittest.main()
