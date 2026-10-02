"""
Camera resection: given the camera's roll/pitch (from GeoCalib, gravity-only,
yaw-ambiguous by construction) and focal length, plus 2+ image points with
known world coordinates (world Y=0, on one or two traced reference lines),
solve for the remaining 4 unknowns — yaw and the 3 translation components —
via nonlinear least squares.

Verified against GeoCalib's own rotation convention (see 3d/NOTES.md or the
session that produced this file for the derivation): GeoCalib's gravity
vector satisfies `gravity == Rz(roll) @ Rx(pitch) @ (0,-1,0)`, and rotating by
yaw around the world Y axis (applied as `@ Ry(yaw)`, i.e. first) leaves that
product unchanged for any yaw — so this reuses GeoCalib's own roll/pitch
directly, no re-derivation from the gravity vector needed.

World/object convention matches pergolando-backend's PerspectiveService and
3d/generate_flag.py exactly: X = width (right+), Y = height (down+, so the
roof is negative Y), Z = depth (front=0, rear=P). Camera convention: X right,
Y down, Z forward (same as OpenCV/GeoCalib).

A single 2-point line gives exactly 4 equations for the 4 unknowns — zero
redundancy, so any tap imprecision on those 2 points propagates entirely
into the solved yaw (this is what actually reads as "wrong perspective" to a
seller, not a focal-length problem). A second, ideally perpendicular,
control line (e.g. the terrace edge, perpendicular to the wall it's built
against) over-determines the system and lets least-squares average the
error down instead of absorbing it whole — verified synthetically (~4.5x
lower mean yaw error under the same simulated tap noise) before wiring this
in for real.
"""

import numpy as np
from scipy.optimize import least_squares


def rotmat(roll, pitch, yaw):
    cr, sr = np.cos(roll), np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)
    Rx = np.array([[1, 0, 0], [0, cp, sp], [0, -sp, cp]])
    Ry = np.array([[cy, 0, -sy], [0, 1, 0], [sy, 0, cy]])
    Rz = np.array([[cr, sr, 0], [-sr, cr, 0], [0, 0, 1]])
    return Rz @ Rx @ Ry


def project(P_world, roll, pitch, yaw, t, fx, fy, cx, cy):
    R = rotmat(roll, pitch, yaw)
    p_cam = R @ np.asarray(P_world, dtype=float) + t
    u = fx * p_cam[0] / p_cam[2] + cx
    v = fy * p_cam[1] / p_cam[2] + cy
    return np.array([u, v])


class ResectionError(ValueError):
    """The tapped points don't correspond to a plausible camera pose —
    e.g. they're degenerate (too close together) or the solver didn't
    converge. Surfaced to the seller as "try retapping the points"."""


def resect_points(points_world, points_px, roll, pitch, fx, fy, cx, cy):
    """General resection over N >= 2 known world<->pixel correspondences.

    `points_world` and `points_px` must be the same length and in
    corresponding order. Returns (yaw, t) for `rotmat(roll, pitch, yaw)` /
    world-to-camera translation `t`, such that the known points reproject
    as closely as possible onto their pixels (exactly, for N=2; a
    least-squares fit for N>2).
    """
    if len(points_world) != len(points_px) or len(points_world) < 2:
        raise ResectionError("servono almeno 2 punti con coordinate corrispondenti")

    p0, p_last = np.array(points_px[0]), np.array(points_px[-1])
    px_dist = np.linalg.norm(p_last - p0)
    if px_dist < 2.0:
        raise ResectionError("i punti sono troppo vicini tra loro")

    w0, w_last = np.asarray(points_world[0], dtype=float), np.asarray(points_world[-1], dtype=float)
    real_dist = np.linalg.norm(w_last - w0)

    # initial guess: rough depth from the first/last pixel separation,
    # centered on the first point.
    z0 = fx * max(real_dist, 1.0) / px_dist
    x0 = (p0[0] - cx) / fx * z0
    y0 = (p0[1] - cy) / fy * z0
    params0 = np.array([0.0, x0 - w0[0], y0 - w0[1], z0 - w0[2]])

    def residuals(params):
        yaw, tx, ty, tz = params
        t = np.array([tx, ty, tz])
        res = []
        for P, px in zip(points_world, points_px):
            res.append(project(P, roll, pitch, yaw, t, fx, fy, cx, cy) - np.array(px))
        return np.concatenate(res)

    result = least_squares(residuals, params0)
    # `cost` is 0.5 * sum(residuals**2) (scipy's convention) — for N=2 this
    # solve is exact by construction (4 equations, 4 unknowns), so a high
    # cost there really means "didn't converge at all". For N>2 (a control
    # line) nonzero residual is normal and expected — it's exactly what
    # lets the fit average tap noise across points instead of absorbing it
    # whole — so the tolerance has to allow real per-point pixel slack
    # (~25px RMS) instead of demanding near-exact agreement, or every
    # over-determined solve would spuriously fail (real bug, hit on the
    # first live test of this).
    px_tolerance = 25.0
    max_cost = len(points_world) * px_tolerance**2
    if not result.success or result.cost > max_cost:
        raise ResectionError("la posa della camera non converge su questi punti")

    yaw, tx, ty, tz = result.x
    return yaw, np.array([tx, ty, tz])


def resect(p1_px, p2_px, roll, pitch, L_cm, fx, fy, cx, cy, depth_z_cm=0.0):
    """Single-line convenience wrapper over `resect_points`: p1_px/p2_px are
    the traced line's start/end pixels, `L_cm` its real length.

    `depth_z_cm` is the line's own position along the world Z (depth) axis —
    0 for a line traced at the front (open-space edge), or the pergola's
    full depth P for a line traced at the wall (today's only case: the
    wizard offers wall/ceiling mounting only, and the wall-floor junction is
    the REAR edge, not the front — see CalcolaProspettivaDto).
    """
    P1 = [-L_cm / 2, 0.0, depth_z_cm]
    P2 = [L_cm / 2, 0.0, depth_z_cm]
    return resect_points([P1, P2], [p1_px, p2_px], roll, pitch, fx, fy, cx, cy)
