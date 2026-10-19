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

def resect_with_vertical(points_world, points_px, vertical_px, height_cm, wall_z, roll, pitch, fx, fy, cx, cy):
    """Refine a measured wall vertical, independent of the floor-line origin.

    The vertical lies on the same facade (Z=wall_z). Its unknown X and Y
    are optimized; its bottom is NOT assumed to be on the ground. Gravity
    from GeoCalib remains a soft prior, rather than freely drifting.
    """
    if not np.isfinite(height_cm) or height_cm <= 0:
        raise ResectionError("altezza verticale non valida")
    vertical_px = sorted([np.asarray(p, dtype=float) for p in vertical_px], key=lambda p: p[1], reverse=True)
    if np.linalg.norm(vertical_px[1] - vertical_px[0]) < 8:
        raise ResectionError("segna una verticale piu lunga")
    yaw, t = resect_points(points_world, points_px, roll, pitch, fx, fy, cx, cy)
    R = rotmat(roll, pitch, yaw)
    camera_center = -R.T @ t
    bottom = vertical_px[0]
    ray = R.T @ np.array([(bottom[0]-cx)/fx, (bottom[1]-cy)/fy, 1.0])
    if abs(ray[2]) < 1e-8:
        raise ResectionError("la verticale non interseca la parete")
    s = (wall_z-camera_center[2])/ray[2]
    if s <= 0:
        raise ResectionError("la verticale e dietro la camera")
    start = camera_center + s*ray
    initial = np.array([yaw, *t, start[0], start[1], roll, pitch])
    prior_sigma = np.deg2rad(3.0)
    def residual(params):
        angle, tx, ty, tz, vx, vy, rr, pp = params
        tt = np.array([tx, ty, tz])
        world = list(points_world) + [(vx, vy, wall_z), (vx, vy-height_cm, wall_z)]
        observed = list(points_px) + vertical_px
        errors = []
        for P, px in zip(world, observed):
            cam = rotmat(rr, pp, angle) @ np.asarray(P) + tt
            if cam[2] <= 1:
                errors.extend([1e4+abs(cam[2])*100, 1e4+abs(cam[2])*100])
            else:
                errors.extend(project(P, rr, pp, angle, tt, fx, fy, cx, cy)-px)
        errors.extend([10*(rr-roll)/prior_sigma, 10*(pp-pitch)/prior_sigma])
        return np.asarray(errors)
    result = least_squares(residual, initial, loss="soft_l1", f_scale=8, max_nfev=300)
    angle, tx, ty, tz, vx, vy, rr, pp = result.x
    tt = np.array([tx,ty,tz])
    world = list(points_world) + [(vx,vy,wall_z),(vx,vy-height_cm,wall_z)]
    R = rotmat(rr,pp,angle)
    if not result.success or not np.all(np.isfinite(result.x)) or any((R@np.asarray(P)+tt)[2]<=1 for P in world):
        raise ResectionError("riferimenti verticali non coerenti con la foto")
    rms = np.sqrt(np.mean(residual(result.x)[:-2]**2))
    if rms > 18 or (-R.T@tt)[1] >= 0:
        raise ResectionError("controlla riga, verticale e misure: la camera non e plausibile")
    return angle, tt, rr, pp


def resect_with_ground_direction(points_world, points_px, ground_px, wall_z, roll, pitch, fx, fy, cx, cy, vertical_px=None, height_cm=None):
    """Constrain the depth vanishing point to a visible perpendicular floor edge.

    The edge position and length are irrelevant: K.T times its image line is
    the plane normal of its viewing rays. A true depth direction must lie in
    that plane. Gravity is a soft prior so a small GeoCalib error cannot force
    the wrong depth orientation. All outputs remain one physical camera.
    """
    a,b = [np.asarray(p,dtype=float) for p in ground_px]
    if np.linalg.norm(b-a) < 12:
        raise ResectionError("segna un tratto piu lungo del bordo del terrazzo")
    line = np.cross([*a,1.0],[*b,1.0])
    K = np.array([[fx,0,cx],[0,fy,cy],[0,0,1.0]])
    normal = K.T @ line
    normal /= np.linalg.norm(normal)
    yaw,t = resect_points(points_world,points_px,roll,pitch,fx,fy,cx,cy)
    vp = None
    if vertical_px is not None:
        if height_cm is None or not np.isfinite(height_cm) or height_cm <= 0:
            raise ResectionError("altezza verticale non valida")
        vp = sorted([np.asarray(p,dtype=float) for p in vertical_px],key=lambda p:p[1],reverse=True)
        if np.linalg.norm(vp[1]-vp[0]) < 8:
            raise ResectionError("segna una verticale piu lunga")
    R=rotmat(roll,pitch,yaw)
    center=-R.T@t
    initial=[yaw,*t,roll,pitch]
    if vp is not None:
        ray=R.T@np.array([(vp[0][0]-cx)/fx,(vp[0][1]-cy)/fy,1.0])
        if abs(ray[2]) < 1e-8:
            raise ResectionError("la verticale non interseca la parete")
        start=center+(wall_z-center[2])/ray[2]*ray
        initial.extend([start[0],start[1]])
    def observations(params):
        world=list(points_world)
        px=list(points_px)
        if vp is not None:
            vx,vy=params[6:8]
            world.extend([(vx,vy,wall_z),(vx,vy-height_cm,wall_z)])
            px.extend(vp)
        return world,px
    def residual(params):
        angle,tx,ty,tz,rr,pp=params[:6]
        R=rotmat(rr,pp,angle);tt=np.array([tx,ty,tz])
        world,px=observations(params);errors=[]
        for P,pixel in zip(world,px):
            cam=R@np.asarray(P)+tt
            if cam[2] <= 1:
                errors.extend([1e4+abs(cam[2])*100]*2)
            else:
                errors.extend(project(P,rr,pp,angle,tt,fx,fy,cx,cy)-pixel)
        errors.extend([1000*np.dot(normal,R[:,2]),20*(rr-roll)/np.deg2rad(3),20*(pp-pitch)/np.deg2rad(3)])
        return np.asarray(errors)
    candidates=[]
    for shift in [0,-.6,.6]:
        seed=np.asarray(initial);seed[0]+=shift
        lower=np.full(len(seed), -np.inf);upper=np.full(len(seed),np.inf)
        lower[4:6]=np.array([roll,pitch])-np.deg2rad(1.5)
        upper[4:6]=np.array([roll,pitch])+np.deg2rad(1.5)
        result=least_squares(residual,seed,bounds=(lower,upper),max_nfev=500)
        if not result.success or not np.all(np.isfinite(result.x)):
            continue
        angle,tx,ty,tz,rr,pp=result.x[:6];tt=np.array([tx,ty,tz]);R=rotmat(rr,pp,angle)
        center=-R.T@tt;world,_=observations(result.x)
        if center[1]>=0 or center[2]>=wall_z or any((R@np.asarray(P)+tt)[2]<=1 for P in world):
            continue
        candidates.append((result.cost,result))
    if not candidates:
        raise ResectionError("bordo del terrazzo e riferimenti non coerenti")
    result=min(candidates,key=lambda v:v[0])[1]
    angle,tx,ty,tz,rr,pp=result.x[:6];tt=np.array([tx,ty,tz]);R=rotmat(rr,pp,angle)
    errors=residual(result.x)
    if np.sqrt(np.mean(errors[:-3]**2))>12 or abs(np.dot(normal,R[:,2]))>np.sin(np.deg2rad(1.5)):
        raise ResectionError("controlla che il bordo scelto sia perpendicolare al muro")
    return angle,tt,rr,pp



def resect_independent_references(points_world, points_px, ground_px, wall_z, roll, pitch, fx, fy, cx, cy, vertical_px=None, height_cm=None, architectural=None):
    """Joint camera fit: depth direction plus a measured vertical at free XYZ.
    Gravity is a soft prior. Keep the GeoCalib focal length: single depth
    and vertical lines do not independently identify focal length and pose.
    """
    a,b=map(lambda p:np.asarray(p,dtype=float),ground_px)
    if np.linalg.norm(a-b)<12:raise ResectionError('segna un bordo laterale piu lungo')
    image_line=np.cross([*a,1.],[*b,1.]);image_line/=np.linalg.norm(image_line[:2])
    yaw,t=resect_points(points_world,points_px,roll,pitch,fx,fy,cx,cy)
    vp=sorted([np.asarray(p,dtype=float) for p in vertical_px],key=lambda p:p[1],reverse=True) if vertical_px is not None else None
    if vp is not None and (not height_cm or height_cm<=0 or np.linalg.norm(vp[1]-vp[0])<8):raise ResectionError('verticale o altezza non valida')
    initial=[yaw,*t,roll,pitch]
    if vp is not None:
        R=rotmat(roll,pitch,yaw);center=-R.T@t
        ray=R.T@np.array([(vp[0][0]-cx)/fx,(vp[0][1]-cy)/fy,1.])
        distance=(wall_z-center[2])/ray[2] if abs(ray[2])>1e-8 else 1000
        initial.extend(center+distance*ray)
    def residual(params):
        angle,tx,ty,tz,rr,pp=params[:6];tt=np.array([tx,ty,tz]);f=1.0
        world=list(points_world);pixels=list(points_px)
        if vp is not None:
            start=np.array(params[6:9]);world.extend([start,start+np.array([0,-height_cm,0])]);pixels.extend(vp)
        errors=[];R=rotmat(rr,pp,angle)
        for point,pixel in zip(world,pixels):
            cam=R@point+tt
            if cam[2]<=1:errors.extend([10000+abs(cam[2])*100]*2)
            else:errors.extend(project(point,rr,pp,angle,tt,fx*f,fy*f,cx,cy)-pixel)
        K=np.array([[fx*f,0,cx],[0,fy*f,cy],[0,0,1.]])
        normal=K.T@image_line;normal/=np.linalg.norm(normal)
        errors.extend([1500*np.dot(normal,R[:,2]),3*(rr-roll)/np.deg2rad(3),3*(pp-pitch)/np.deg2rad(3)])
        for axis,ray in architectural or []:
            errors.extend(120*np.cross(R[:,axis],ray))
        return np.array(errors)
    candidates=[]
    for shift in [0,-.6,.6]:
        seed=np.array(initial);seed[0]+=shift
        lo=np.full(len(seed),-np.inf);hi=np.full(len(seed),np.inf)
        lo[4:6]=[roll-np.deg2rad(10),pitch-np.deg2rad(12)]
        hi[4:6]=[roll+np.deg2rad(10),pitch+np.deg2rad(12)]
        fit=least_squares(residual,seed,bounds=(lo,hi),max_nfev=1000,x_scale='jac')
        if not fit.success or not np.all(np.isfinite(fit.x)):continue
        rr,pp=fit.x[4:6];R=rotmat(rr,pp,fit.x[0]);tt=fit.x[1:4]
        if (-R.T@tt)[1]>=0:continue
        world=list(points_world)
        if vp is not None:world.extend([fit.x[6:9],fit.x[6:9]+[0,-height_cm,0]])
        if any((R@point+tt)[2]<=1 for point in world):continue
        candidates.append(fit)
    if not candidates:raise ResectionError('non riesco a conciliare i riferimenti: controlla misure e direzioni')
    best=min(candidates,key=lambda f:f.cost);errors=residual(best.x)
    if np.sqrt(np.mean(errors[:2*(len(points_world)+(2 if vp is not None else 0))]**2))>18 or abs(errors[2*(len(points_world)+(2 if vp is not None else 0))])>1500*np.sin(np.deg2rad(1.5)):
        raise ResectionError('le direzioni segnate non risultano perpendicolari con queste misure')
    return best.x[0],best.x[1:4],best.x[4],best.x[5],1.0
