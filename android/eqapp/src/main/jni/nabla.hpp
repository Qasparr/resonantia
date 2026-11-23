// =============================================================================
// RESONANTIA — android/eqapp/src/main/jni/nabla.hpp — the Del operator
// (nabla) in C++, seated with the EQVILLIBBRRIVMM app's native code:
// gradient, divergence, curl, Laplacian over gridded fields.
//
// Epigraph: "A compact symbol. A powerful idea."
// — the plate the founder brought to the desk (XXIII Nov 2026), on
//   the del operator: Oliver Heaviside (1850-1925) introduced its
//   modern use in physics.
//
// 93.
// Date: 23 November 2026.
// Authorship attributed exclusively to Johnathan 'Qasparr' Monroe,
// ARR — All Rights Reserved, Without Prejudice.
// Method of Science, Aim of Religion — Scientific Illuminism.
//
// SCIENTIFIC ILLUMINISM — hypothesis → method → observation → result:
//   Hypothesis: that the studio's nabla seat (resonance/studio/
//     nabla.py, landed XXIII Nov 2026 at a41ee87) can stand in C++
//     on the device with its semantics intact — the same difference
//     scheme, the same shape law, the same refusals by name — so
//     the phone computes the operator itself instead of carrying
//     a picture of the bench's numbers.
//   Method: this header is a port, not a reinvention. It carries
//     the Python seat's own scheme — central differences in the
//     interior, second-order one-sided differences at the edges
//     (numpy.gradient's edge_order=2 formulas, written out below)
//     — over double-precision fields, and its Laplacian is composed
//     literally as the divergence of this header's own gradient,
//     exactly as the Python seat composes its own. The reference
//     implementation remains the Python seat; this port is judged
//     against the same closed-form fields (the host harness under
//     android/eqapp/host/ runs them on the bench before any APK
//     strike, and the app re-runs them on the device at tap time).
//   Observation: (recorded in android/APK-BUILD.md after the
//     host proof and the strike.)
//   Result: this header, the toolkit JNI bridge that calls it,
//     and the measured numbers in the record.
//
// DOCTRINE — WHAT THIS SEAT IS AND IS NOT:
//   - It is the general operator over the caller's grids: a scalar
//     field is 1-D, 2-D, or 3-D; components come back in array-axis
//     order (axis 0 is x, axis 1 is y, axis 2 is z for a field
//     built in that order), as in the Python seat's axis law.
//   - Precision: double throughout. The Python seat computes in
//     float64 as well (numpy's default for its inputs), so no
//     precision boundary is crossed by the port; the sworn
//     tolerances are the analytic ones, and the harness prints
//     the measured errors rather than asserting them unseen.
//   - One coordinate where the port's law is stated more sharply
//     than the Python seat's: the second-order edge formula needs
//     THREE seats on an axis. The Python seat pre-refuses axes
//     under 2 seats and lets numpy refuse a 2-seat axis in its own
//     words ("at least (edge_order + 1) elements are required" —
//     probed on this bench). This port refuses under-3 axes by
//     its own name, before any arithmetic: same boundary, named
//     in the house's voice instead of the engine's.
//
// MECHANISM — THE SHAPE LAW (refusals by name, as NablaError):
//   * A scalar field is 1, 2, or 3 dimensional, every axis at
//     least 3 seats long (see the doctrine note above). A 0-D or
//     4-D field, or a short axis, is refused by name.
//   * Spacing is one positive finite number (uniform) or one per
//     axis. Zero, negative, non-finite, or the wrong count are
//     refused by name.
//   * A vector field is one component per axis of a shared grid;
//     a wrong count or mismatched shapes are refused by name.
//   * The curl is seated in three dimensions only; any other
//     dimension is refused by name, never silently projected.
//
// All Rights Reserved, Without Prejudice.
// "Live, Love, and let Love, Live."
// =============================================================================

#ifndef RESONANTIA_NABLA_HPP
#define RESONANTIA_NABLA_HPP

#include <cmath>
#include <cstddef>
#include <stdexcept>
#include <string>
#include <vector>

namespace resonantia {
namespace nabla {

// DOCTRINE: a refusal is a named error, thrown before any
// arithmetic runs — the C++ seat of the Python seat's NablaError.
// The message names the fault; nothing is silently coerced.
class NablaError : public std::runtime_error {
public:
    explicit NablaError(const std::string& message)
        : std::runtime_error(message) {}
};

// MECHANISM: a gridded scalar field — a shape (1 to 3 axis
// lengths) and its seats in row-major order (last axis fastest),
// the same memory picture as numpy's default array order, so a
// field built axis-by-axis reads identically in both seats.
struct Field {
    std::vector<std::size_t> shape;  // one length per axis
    std::vector<double> data;        // product(shape) seats

    std::size_t ndim() const { return shape.size(); }
    std::size_t size() const { return data.size(); }
};

// MECHANISM: row-major strides — stride of the last axis is 1,
// each earlier stride the product of the lengths after it.
inline std::vector<std::size_t> strides_of(
        const std::vector<std::size_t>& shape) {
    std::vector<std::size_t> strides(shape.size(), 1);
    for (std::size_t a = shape.size(); a-- > 1;) {
        strides[a - 1] = strides[a] * shape[a];
    }
    return strides;
}

// MECHANISM: bring a caller's field under the shape law. Refuses
// by name: a dimension outside 1..3, data that does not fill the
// shape, and any axis shorter than 3 seats (the second-order
// edge formula's own requirement — see the header's doctrine).
inline void check_scalar_field(const Field& f, const char* name) {
    if (f.ndim() == 0 || f.ndim() > 3) {
        throw NablaError(std::string(name) +
            ": a scalar field is 1-D, 2-D or 3-D; got " +
            std::to_string(f.ndim()) + "-D");
    }
    std::size_t seats = 1;
    for (std::size_t axis = 0; axis < f.ndim(); ++axis) {
        if (f.shape[axis] < 3) {
            throw NablaError(std::string(name) + ": axis " +
                std::to_string(axis) + " has " +
                std::to_string(f.shape[axis]) +
                " seat(s); the second-order edge scheme needs "
                "at least 3");
        }
        seats *= f.shape[axis];
    }
    if (f.data.size() != seats) {
        throw NablaError(std::string(name) + ": data holds " +
            std::to_string(f.data.size()) + " seat(s) for a shape "
            "of " + std::to_string(seats) +
            "; a field fills its grid exactly");
    }
}

// MECHANISM: normalize spacing to one positive finite double per
// axis. The single-value overload seats uniformly; the per-axis
// overload must number exactly ndim entries. Zero, negative, and
// non-finite spacings are refused by name — a grid with no width
// has no derivative, and an infinite one has no field.
inline std::vector<double> spacing_tuple(double spacing,
                                         std::size_t ndim) {
    return std::vector<double>(ndim, spacing);
}

inline std::vector<double> spacing_tuple(
        const std::vector<double>& spacing, std::size_t ndim) {
    if (spacing.size() != ndim) {
        throw NablaError("spacing: " +
            std::to_string(spacing.size()) + " value(s) for a " +
            std::to_string(ndim) +
            "-D field; give one number or " + std::to_string(ndim));
    }
    return spacing;
}

inline void check_spacing(const std::vector<double>& h) {
    for (double v : h) {
        if (!std::isfinite(v) || v <= 0.0) {
            throw NablaError("spacing: every spacing must be "
                             "positive and finite; got " +
                             std::to_string(v));
        }
    }
}

// MECHANISM: bring a vector field under the shape law — one
// component per axis, every component a lawful scalar field, all
// sharing one shape. A field whose components disagree about the
// grid is not a field, and is refused by name.
inline void check_vector_field(const std::vector<Field>& components,
                               const char* name) {
    if (components.empty()) {
        throw NablaError(std::string(name) + ": no components given");
    }
    for (std::size_t i = 0; i < components.size(); ++i) {
        check_scalar_field(components[i], name);
        if (components[i].shape != components[0].shape) {
            throw NablaError(std::string(name) + ": component " +
                std::to_string(i) +
                " does not share component 0's shape; a vector "
                "field shares one grid");
        }
    }
    if (components.size() != components[0].ndim()) {
        throw NablaError(std::string(name) + ": " +
            std::to_string(components.size()) +
            " component(s) for a " +
            std::to_string(components[0].ndim()) +
            "-D grid; the count must equal the dimension");
    }
}

// MECHANISM: the derivative of f along one axis, at every seat —
// the engine of the whole header, numpy.gradient's edge_order=2
// scheme written out:
//   interior seat i:  (f[i+1] - f[i-1]) / (2h)
//   first seat:       (-3 f[0] + 4 f[1] - f[2]) / (2h)
//   last seat:        (3 f[n-1] - 4 f[n-2] + f[n-3]) / (2h)
// Central in the interior (exact on cubics), second-order
// one-sided at the edges (exact on quadratics) — so the sworn
// polynomial class is exact at the boundary seats as well.
inline Field derivative_along_axis(const Field& f, std::size_t axis,
                                   double h) {
    Field out{f.shape, std::vector<double>(f.size(), 0.0)};
    const std::vector<std::size_t> strides = strides_of(f.shape);
    const std::size_t n = f.shape[axis];
    const std::size_t stride = strides[axis];
    const double inv2h = 1.0 / (2.0 * h);
    for (std::size_t flat = 0; flat < f.size(); ++flat) {
        const std::size_t i = (flat / stride) % n;
        double d;
        if (i == 0) {
            d = (-3.0 * f.data[flat] + 4.0 * f.data[flat + stride]
                 - f.data[flat + 2 * stride]) * inv2h;
        } else if (i == n - 1) {
            d = (3.0 * f.data[flat] - 4.0 * f.data[flat - stride]
                 + f.data[flat - 2 * stride]) * inv2h;
        } else {
            d = (f.data[flat + stride] - f.data[flat - stride])
                * inv2h;
        }
        out.data[flat] = d;
    }
    return out;
}

// gradient — nabla f: the gradient of a scalar field, one Field
// per axis, in array-axis order (axis 0 first). Each component is
// the derivative along its own axis under the scheme above.
inline std::vector<Field> gradient(const Field& field,
                                   const std::vector<double>& spacing) {
    check_scalar_field(field, "field");
    const std::vector<double> h = spacing_tuple(spacing, field.ndim());
    check_spacing(h);
    std::vector<Field> parts;
    parts.reserve(field.ndim());
    for (std::size_t axis = 0; axis < field.ndim(); ++axis) {
        parts.push_back(derivative_along_axis(field, axis, h[axis]));
    }
    return parts;
}

inline std::vector<Field> gradient(const Field& field, double spacing) {
    return gradient(field,
                    spacing_tuple(spacing, field.ndim()));
}

// divergence — nabla . F: each component differenced along its
// OWN axis (the x-component along x, the y-component along y)
// and the partials summed seat by seat. Positive seats are
// sources, negative seats sinks, zero is a field that flows
// through.
inline Field divergence(const std::vector<Field>& components,
                        const std::vector<double>& spacing) {
    check_vector_field(components, "vector_field");
    const std::vector<double> h =
        spacing_tuple(spacing, components[0].ndim());
    check_spacing(h);
    Field total{components[0].shape,
                std::vector<double>(components[0].size(), 0.0)};
    for (std::size_t axis = 0; axis < components.size(); ++axis) {
        const Field partial =
            derivative_along_axis(components[axis], axis, h[axis]);
        for (std::size_t s = 0; s < total.size(); ++s) {
            total.data[s] += partial.data[s];
        }
    }
    return total;
}

inline Field divergence(const std::vector<Field>& components,
                        double spacing) {
    return divergence(components,
                      spacing_tuple(spacing, components[0].ndim()));
}

// curl — nabla x F: the curl of a 3-D vector field, returned as
// (curl_x, curl_y, curl_z):
//   curl_x = dFz/dy - dFy/dz
//   curl_y = dFx/dz - dFz/dx
//   curl_z = dFy/dx - dFx/dy
// Seated in three dimensions only; any other dimension is
// refused by name, never silently projected.
inline std::vector<Field> curl(const std::vector<Field>& components,
                               const std::vector<double>& spacing) {
    check_vector_field(components, "vector_field");
    if (components[0].ndim() != 3) {
        throw NablaError("curl: seated in three dimensions only; "
                         "got a " +
                         std::to_string(components[0].ndim()) +
                         "-D field");
    }
    const std::vector<double> h = spacing_tuple(spacing, 3);
    check_spacing(h);
    const Field& fx = components[0];
    const Field& fy = components[1];
    const Field& fz = components[2];
    // Axis law: array axis 0 is x, axis 1 is y, axis 2 is z.
    const Field dfz_dy = derivative_along_axis(fz, 1, h[1]);
    const Field dfy_dz = derivative_along_axis(fy, 2, h[2]);
    const Field dfx_dz = derivative_along_axis(fx, 2, h[2]);
    const Field dfz_dx = derivative_along_axis(fz, 0, h[0]);
    const Field dfy_dx = derivative_along_axis(fy, 0, h[0]);
    const Field dfx_dy = derivative_along_axis(fx, 1, h[1]);
    std::vector<Field> out(3, Field{fx.shape,
                                    std::vector<double>(fx.size(), 0.0)});
    for (std::size_t s = 0; s < fx.size(); ++s) {
        out[0].data[s] = dfz_dy.data[s] - dfy_dz.data[s];
        out[1].data[s] = dfx_dz.data[s] - dfz_dx.data[s];
        out[2].data[s] = dfy_dx.data[s] - dfx_dy.data[s];
    }
    return out;
}

inline std::vector<Field> curl(const std::vector<Field>& components,
                               double spacing) {
    return curl(components, spacing_tuple(spacing, 3));
}

// laplacian — nabla^2 f: NOT a second stencil of its own — the
// divergence OF THIS HEADER'S OWN GRADIENT, composed literally,
// so the Laplacian can never drift from the gradient and
// divergence the house has already sworn to. A seat where the
// Laplacian is zero is in harmonic balance with its neighbours.
inline Field laplacian(const Field& field,
                       const std::vector<double>& spacing) {
    check_scalar_field(field, "field");
    const std::vector<double> h = spacing_tuple(spacing, field.ndim());
    check_spacing(h);
    return divergence(gradient(field, h), h);
}

inline Field laplacian(const Field& field, double spacing) {
    return laplacian(field, spacing_tuple(spacing, field.ndim()));
}

}  // namespace nabla
}  // namespace resonantia

#endif  // RESONANTIA_NABLA_HPP
