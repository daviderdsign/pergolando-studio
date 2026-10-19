"""
Headless, parametric generator for the Flag pergola 3D model.

Run with Blender in background mode, with `3d/flag.blend` as the file to
open (its on-disk state is the calibration reference: a 3x3m, H=200cm,
delta_h=40cm assembly) and this script as `--python`:

    blender --background flag.blend --python generate_flag.py -- \\
        --config config.json --output render.png

`config.json` (or an inline --config-json string) shape:
{
  "L_cm": 450, "P_cm": 350, "H_cm": 230, "deltaH_cm": 50,
  "fissaggio": "autoportante" | "parete",
  "camera": {                       # optional — omit for a simple orbit render
    "rvec": [rx, ry, rz],           # OpenCV solvePnP output, PnP-world convention
    "tvec": [tx, ty, tz],           # in cm (matches pergolando-backend's PerspectiveService)
    "fovDeg": 60,
    "imageWidthPx": 1920,
    "imageHeightPx": 1080
  }
}

Naming note: L_cm/P_cm/H_cm/deltaH_cm are this script's own internal names,
kept for now to avoid touching the backend/wizard contract. They do NOT
match the vendor's own field names for this hardware, which are (per
Davide, from the real order form): L (width, same), SP (depth — this
script's P_cm), P (FRONT height — this script's H_cm), H (REAR height —
this script's H_cm + deltaH_cm), H1 (H - P — this script's deltaH_cm).
Rename this script's own parameters to match only when the wizard/backend
are updated together — see 3d/NOTES.md.

This transcribes, as faithfully as possible, every technique validated
interactively over many BlenderMCP sessions (see `3d/NOTES.md` for the
narrative/rationale) into one reusable function per piece. It never writes
back to `flag.blend` itself — it only ever produces a render (and, if
`--save-blend` is passed, a *separate* .blend for inspection).

Known limitations (deliberately out of scope for this first version):
  - Timpano/Trave_Laterale (the optional "closed pergola" gable) is NOT
    parametrized yet — only made parallel-to-guide for the single reference
    size, per Davide's explicit request. Always excluded from the render.
  - Pilastrino_intermedio and Skipper are unexplained pieces, always
    excluded.
"""

import argparse
import json
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))

import bmesh
import bpy

BASE_ROT = (math.pi / 2, 0.0, 0.0)

# ---------------------------------------------------------------------------
# Calibration constants, all read from 3d/NOTES.md — see that file for the
# reasoning behind each one. None of these should need to change unless the
# reference flag.blend itself is recalibrated.
# ---------------------------------------------------------------------------
REF_L_CM = 300.0
REF_P_NOMINAL_CM = 300.0
REF_H_CM = 200.0

FOOT_THRESHOLD_CM = 20.0  # Montante foot-detail cutoff
TRAVE_OVERHANG_CM = 2.41  # Trave half-length beyond post outer edge
TRAVE_POSTERIORE_OVERHANG_CM = 1.2
FRANGITRATTA_CAP_MARGIN_CM = 2.6  # Frangitratta_Iniziale_Finale: REF_L/2 - cur_half
FRANGITRATTA_INTERMEDIO_MARGIN_CM = 2.85
TETTUCCIO_ENDCAP_OUTER_CM = 150.47  # Tettuccio's own end-cap outer X at REF_L
FRANGITRATTA_SPACING_M = 0.50
TETTUCCIO_PERIOD_CM = 11.1994875
TETTUCCIO_RIB_HALF_WIDTH_CM = 5.65
TETTUCCIO_RIDGE_LOWER_CM = 1.0  # the two 0.5cm ridge corrections from the live session

# ---------------------------------------------------------------------------
# Pivot-based rail geometry — replaces the old per-piece front/rear-ring
# offset math entirely. The reference flag.blend was reworked (2026-09-26)
# so world Y=0 sits exactly at the rear-most point of Aggancio_Parete (the
# wall bracket): SP (depth) now measures straight from there, and the whole
# Guida/Telo/Frangitratta/Tettuccio/Supporto assembly rotates as ONE rigid
# group around a single physical pivot — the hole through the two "zanche"
# brackets on Guida. Found by clustering nearby vertices (stable at a 4-5cm
# radius, 88 verts) and confirmed to reproduce the untouched reference mesh
# exactly (zero diff) when the rail's own rotation/extension come out to
# zero. See 3d/NOTES.md for the full derivation and the live tests that
# validated this against Davide's own Blender session.
# ---------------------------------------------------------------------------
PIVOT_LOCAL_Y = 240.3172149658203  # local Y = height
PIVOT_LOCAL_Z = 13.917588233947754  # local Z = depth from the wall
FRONT_REF_LOCAL_Y = 222.54885838062467
FRONT_REF_LOCAL_Z = 310.5169673805073
PIVOT_HEIGHT_OFFSET_CM = 5.0  # the pivot sits this far above the vendor's own "H" (rear height) mark — no more precise physical reference exists
FRONT_GROUP_Z_THRESHOLD_CM = PIVOT_LOCAL_Z + 20.0  # vertices past this are "reaching toward the front" and get the SP-driven extension


def world_bbox(obj):
    mw = obj.matrix_world
    xs, ys, zs = [], [], []
    for v in obj.data.vertices:
        w = mw @ v.co
        xs.append(w.x)
        ys.append(w.y)
        zs.append(w.z)
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


def world_yz_center(obj):
    (_, _), (ymin, ymax), (zmin, zmax) = world_bbox(obj)
    return (ymin + ymax) / 2, (zmin + zmax) / 2


def mirror_x_copy(src, dst_name):
    mesh_copy = src.data.copy()
    for v in mesh_copy.vertices:
        v.co.x = -v.co.x
    # Negating one axis flips handedness, which leaves every face's winding
    # (and therefore its normal) inverted — invisible in the shaded/material
    # renders used everywhere else, but Freestyle silhouette detection reads
    # face orientation directly: found 2026-09-28 rendering an exact
    # front-on orthographic elevation, where the mirrored leg (Montante.001)
    # vanished almost entirely (only a small non-mirrored foot detail
    # remained) while the un-mirrored one rendered fine.
    bm = bmesh.new()
    bm.from_mesh(mesh_copy)
    for f in bm.faces:
        f.normal_flip()
    bm.to_mesh(mesh_copy)
    bm.free()
    dst = bpy.data.objects[dst_name]
    dst.data = mesh_copy
    dst.location = (0, 0, 0)
    dst.rotation_euler = BASE_ROT
    dst.scale = (0.01, 0.01, 0.01)
    return dst


def stretch_x_symmetric(obj, new_half_cm):
    verts = obj.data.vertices
    cur_half = max(v.co.x for v in verts)
    delta = new_half_cm - cur_half
    for v in verts:
        if v.co.x > 0:
            v.co.x += delta
        elif v.co.x < 0:
            v.co.x -= delta
    obj.data.update()
    return delta


def _mesh_center_yz(obj):
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    return (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2


def _mesh_center_x(obj):
    xs = [v.co.x for v in obj.data.vertices]
    return (min(xs) + max(xs)) / 2


def _translate_x_copy(src, dst_name, target_x_center):
    """Plain (non-mirrored) duplicate of src's CURRENT mesh, shifted along
    local X only, so it keeps src's own Y/Z (already rail-transformed) and
    cross-section/orientation exactly — used for intermediate guides/
    supports, which don't need src's handedness flipped (unlike the two
    edge copies, see mirror_x_copy): there's no physical reason to assume a
    middle rail is mirrored rather than just translated, and no reference
    asset exists to check against (see guide_x_targets' docstring)."""
    mesh_copy = src.data.copy()
    delta_x = target_x_center - _mesh_center_x(src)
    for v in mesh_copy.vertices:
        v.co.x += delta_x
    dst = bpy.data.objects.get(dst_name)
    if dst is None:
        dst = bpy.data.objects.new(dst_name, mesh_copy)
        bpy.context.collection.objects.link(dst)
    else:
        dst.data = mesh_copy
    dst.location = src.location
    dst.rotation_euler = src.rotation_euler
    dst.scale = src.scale
    return dst


def _remove_stale_copies(name_prefix):
    i = 1
    while True:
        extra = bpy.data.objects.get(f"{name_prefix}{i}")
        if extra is None:
            break
        bpy.data.objects.remove(extra, do_unlink=True)
        i += 1


# Real catalog thresholds (apps/studio/storage/bundles/Flag/*/catalog/
# database.json, sotto_modelli.flag.varianti_montaggio): "2guide" up to
# 550cm, "3guide" 600-1100cm, "4guide" 1150-1400cm (1400 is also this
# product's absolute L_max_modulo_cm — there is no "5guide" tier in the
# real price list). The 551-599 and 1101-1149 gaps are real: the vendor's
# own price list doesn't sell those widths at all (see note_estrazione in
# the same file) — rounded UP to the next tier here (more structure, never
# less) since this is only a fallback for when the caller doesn't know/send
# the real varianteMontaggio (see nGuide wiring in Scene3dService).
def derive_n_guide_from_l(l_cm):
    if l_cm <= 550:
        return 2
    if l_cm <= 1100:
        return 3
    return 4


def guide_x_targets(l_cm, n_guide):
    """N evenly-spaced guide centers across the full width, from -L/2 to
    +L/2 (n_guide=2 lands exactly on the two edges, matching the original
    2-guide-only geometry with zero change). n_guide=3 adds one at the
    center; n_guide=4 adds two at the quarter points. No modeled reference
    exists in flag.blend for a real 3/4-guide unit (the FBX reverse-
    engineering only ever captured the 2-guide reference size) — this
    reuses the edge Guida/Supporto pieces translated into place as the best
    available approximation, not a verified reproduction of the real
    intermediate hardware. Flagged to Davide; see 3d/NOTES.md."""
    n_guide = max(2, min(4, round(n_guide)))
    half = l_cm / 2
    if n_guide == 2:
        return [-half, half]
    step = l_cm / (n_guide - 1)
    return [-half + i * step for i in range(n_guide)]


def _translate_to_yz(obj, target_y, target_z):
    cur_y, cur_z = _mesh_center_yz(obj)
    dy, dz = target_y - cur_y, target_z - cur_z
    for v in obj.data.vertices:
        v.co.y += dy
        v.co.z += dz
    obj.data.update()


def _rotate_around_own_center(obj, rotation_delta):
    cy, cz = _mesh_center_yz(obj)
    cos_a, sin_a = math.cos(rotation_delta), math.sin(rotation_delta)
    for v in obj.data.vertices:
        rel_y, rel_z = v.co.y - cy, v.co.z - cz
        v.co.y = cy + (rel_z * sin_a + rel_y * cos_a)
        v.co.z = cz + (rel_z * cos_a - rel_y * sin_a)
    obj.data.update()


def compute_rail(H_cm, delta_h_cm, P_cm):
    """H_cm = front height (vendor's "P"), delta_h_cm = vendor's "H1" (rear
    minus front rise), P_cm = depth (vendor's "SP"). Returns a `rail` tuple
    consumed by every rail_* helper below: (rotation_delta, extension_cm,
    target_angle, pivot_target_y).

    The pivot's own target height is fixed at PIVOT_HEIGHT_OFFSET_CM above
    the vendor's "H" (rear height) mark: H_cm + delta_h_cm + 5. From there,
    the rotation angle is whatever swings the guide's own front reference
    point (calibrated once against the untouched reference mesh) to land at
    the requested front height/depth; the extension is the resulting change
    in reach along that same direction — needed because a pure rotation
    alone can't change the pivot-to-front distance, only its angle.
    """
    pivot_target_y = H_cm + delta_h_cm + PIVOT_HEIGHT_OFFSET_CM
    front_target_y = H_cm + (FRONT_REF_LOCAL_Y - REF_H_CM)
    front_target_z = P_cm + (FRONT_REF_LOCAL_Z - REF_P_NOMINAL_CM)

    dy = front_target_y - pivot_target_y
    dz = front_target_z - PIVOT_LOCAL_Z
    target_angle = math.atan2(dy, dz)
    target_arm = math.hypot(dy, dz)

    dy_ref = FRONT_REF_LOCAL_Y - PIVOT_LOCAL_Y
    dz_ref = FRONT_REF_LOCAL_Z - PIVOT_LOCAL_Z
    ref_angle = math.atan2(dy_ref, dz_ref)
    ref_arm = math.hypot(dy_ref, dz_ref)

    return target_angle - ref_angle, target_arm - ref_arm, target_angle, pivot_target_y


def rail_transform_verts(obj, rail, delta_x_cm=0.0, extend=True):
    """Rotate obj's vertices rigidly around the pivot by rail's
    rotation_delta. If extend, vertices whose ORIGINAL local Z is past
    FRONT_GROUP_Z_THRESHOLD_CM (the "reaching toward the front" part of the
    piece, not the fixed-bracket end near the pivot) also get translated by
    rail's extension along the target_angle direction — this is what lets
    Guida/Telo/the Frangitratta cap reach an arbitrary SP without distorting
    their own cross-section (a pure rotation can't change the pivot-to-front
    distance). Pieces that stay entirely near the pivot (Tettuccio,
    Frangitratta_Finale, Aggancio_Parete, the rear posts/beam) should pass
    extend=False: same rotation, no reach change, so they swing with the
    bracket instead of stretching toward a front they don't reach."""
    rotation_delta, extension, target_angle, pivot_target_y = rail
    cos_a, sin_a = math.cos(rotation_delta), math.sin(rotation_delta)
    ext_z = extension * math.cos(target_angle)
    ext_y = extension * math.sin(target_angle)
    translate_y = pivot_target_y - PIVOT_LOCAL_Y
    for v in obj.data.vertices:
        orig_z = v.co.z
        rel_y = v.co.y - PIVOT_LOCAL_Y
        rel_z = v.co.z - PIVOT_LOCAL_Z
        new_rel_z = rel_z * cos_a - rel_y * sin_a
        new_rel_y = rel_z * sin_a + rel_y * cos_a
        new_y = PIVOT_LOCAL_Y + new_rel_y + translate_y
        new_z = PIVOT_LOCAL_Z + new_rel_z
        if extend and orig_z > FRONT_GROUP_Z_THRESHOLD_CM:
            new_y += ext_y
            new_z += ext_z
        v.co.y = new_y
        v.co.z = new_z
        if delta_x_cm:
            if v.co.x > 0:
                v.co.x += delta_x_cm
            elif v.co.x < 0:
                v.co.x -= delta_x_cm
    obj.data.update()


def build_montante(L_cm, H_cm, delta_z_cm, n_guide=2):
    montante = bpy.data.objects["Montante"]
    verts = montante.data.vertices

    delta_y = H_cm - max(v.co.y for v in verts)
    delta_x = L_cm / 2 - max(v.co.x for v in verts)
    for v in verts:
        if v.co.y > FOOT_THRESHOLD_CM:
            v.co.y += delta_y
        v.co.x += delta_x
        v.co.z += delta_z_cm
    montante.data.update()

    mirror_x_copy(montante, "Montante.001")

    # A guide spanning more than the two edges needs its own vertical
    # support underneath, same as the edge ones (Davide, 2026-10-04) — the
    # earlier assumption that Trave alone was enough span support was
    # wrong. Reuses the already-positioned edge Montante as a template,
    # translated along X only (same technique as the intermediate
    # Guida/Supporto copies) — correct height/depth, just moved into place.
    prefix = "Montante_intermedio_"
    _remove_stale_copies(prefix)
    targets = guide_x_targets(L_cm, n_guide)
    for i, target_x in enumerate(targets[1:-1], start=1):
        _translate_x_copy(montante, f"{prefix}{i}", target_x)

    return montante


def build_montante_posteriore(delta_x_cm, rail):
    """The rear posts are part of the fixed rear bracket assembly, not
    depth-shifted by SP at all (only Montante/Trave, at the front, move with
    SP) — they just rotate with the pivot like Tettuccio/Aggancio_Parete."""
    built = []
    for name in ("Montante_Posteriore_Dx", "Montante_Posteriore_Sx"):
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        rail_transform_verts(obj, rail, delta_x_cm=delta_x_cm, extend=False)
        built.append(obj)
    return built


def build_trave(L_cm, H_cm, delta_z_cm):
    trave = bpy.data.objects["Trave"]
    for v in trave.data.vertices:
        v.co.y += H_cm - REF_H_CM
        v.co.z += delta_z_cm
    stretch_x_symmetric(trave, L_cm / 2 + TRAVE_OVERHANG_CM)
    return trave


def build_trave_posteriore(L_cm, delta_x_cm, rail):
    tp = bpy.data.objects["Trave_Posteriore"]
    stretch_x_symmetric(tp, L_cm / 2 + TRAVE_POSTERIORE_OVERHANG_CM)
    rail_transform_verts(tp, rail, delta_x_cm=0.0, extend=False)
    return tp


def _build_rail_piece_with_intermediates(obj_name, rail, delta_x_cm, l_cm, n_guide):
    """Builds the two edge copies of obj_name (exactly the original
    2-guide-only behaviour, zero change at n_guide=2) plus, for n_guide=3/4,
    plain-translated copies at the intermediate guide positions — see
    guide_x_targets for the positions and why they're an approximation."""
    piece = bpy.data.objects[obj_name]
    rail_transform_verts(piece, rail, delta_x_cm=delta_x_cm, extend=True)
    mirror_x_copy(piece, f"{obj_name}.001")

    prefix = f"{obj_name}_intermedio_"
    _remove_stale_copies(prefix)
    targets = guide_x_targets(l_cm, n_guide)
    for i, target_x in enumerate(targets[1:-1], start=1):
        _translate_x_copy(piece, f"{prefix}{i}", target_x)

    return piece


def build_supporto(delta_x_cm, rail, l_cm, n_guide):
    return _build_rail_piece_with_intermediates("Supporto", rail, delta_x_cm, l_cm, n_guide)


def build_guida(rail, delta_x_cm, l_cm, n_guide):
    return _build_rail_piece_with_intermediates("Guida", rail, delta_x_cm, l_cm, n_guide)


def build_frangitratta(L_cm, rail, delta_x_cm):
    # stretch_x_symmetric already sets each piece's absolute half-width from
    # L_cm directly (unlike Guida/Telo/Trave, which start from a fixed
    # reference half-width and get shifted by delta_x_cm) — passing
    # delta_x_cm to rail_transform_verts too would double it.
    cap = bpy.data.objects["Frangitratta_Iniziale_Finale"]
    stretch_x_symmetric(cap, L_cm / 2 - FRANGITRATTA_CAP_MARGIN_CM)
    rail_transform_verts(cap, rail, delta_x_cm=0.0, extend=True)

    # Frangitratta_Finale is literally the same physical piece as the cap,
    # just installed at the opposite (rear) end — the file used to share one
    # mesh datablock between the two objects, which silently corrupted
    # whichever one was transformed second. Always give it its own copy
    # before touching its vertices.
    finale = bpy.data.objects["Frangitratta_Finale"]
    if finale.data.users > 1:
        finale.data = finale.data.copy()
    stretch_x_symmetric(finale, L_cm / 2 - FRANGITRATTA_CAP_MARGIN_CM)
    rail_transform_verts(finale, rail, delta_x_cm=0.0, extend=False)

    # drop any stale extra copies from a previous run at a different SP
    i = 2
    while True:
        extra = bpy.data.objects.get(f"Frangitratta_pos_{i}")
        if extra is None:
            break
        bpy.data.objects.remove(extra, do_unlink=True)
        i += 1

    cap_y, cap_z = _mesh_center_yz(cap)
    fin_y, fin_z = _mesh_center_yz(finale)
    span_cm = math.hypot(cap_y - fin_y, cap_z - fin_z)
    n_intermedi = max(0, round(span_cm / (FRANGITRATTA_SPACING_M * 100)) - 1)

    pos1 = bpy.data.objects["Frangitratta_pos_1"]
    if pos1.data.users > 1:
        pos1.data = pos1.data.copy()
    stretch_x_symmetric(pos1, L_cm / 2 - FRANGITRATTA_INTERMEDIO_MARGIN_CM)
    pristine_template = pos1.data.copy()

    rotation_delta = rail[0]
    for i in range(1, n_intermedi + 1):
        t = i / (n_intermedi + 1)
        target_y = fin_y + t * (cap_y - fin_y)
        target_z = fin_z + t * (cap_z - fin_z)
        name = f"Frangitratta_pos_{i}"
        obj = bpy.data.objects.get(name)
        if obj is None:
            obj = bpy.data.objects.new(name, pristine_template.copy())
            obj.rotation_euler = pos1.rotation_euler
            obj.scale = pos1.scale
            obj.location = (0, 0, 0)
            bpy.context.collection.objects.link(obj)
        else:
            obj.data = pristine_template.copy()
            obj.location = (0, 0, 0)
        # each intermediate is a rigid copy of the reference piece — move it
        # onto its target spot (interpolated between the already-transformed
        # cap and finale, so it's guaranteed to land between them regardless
        # of SP) then rotate it about its OWN center to match the rail's
        # angle, so it stays perpendicular to Telo/Guida instead of just
        # sliding into place at the old, un-rotated angle.
        _translate_to_yz(obj, target_y, target_z)
        _rotate_around_own_center(obj, rotation_delta)

    return n_intermedi


def build_tettuccio(L_cm, rail):
    tett = bpy.data.objects["Tettuccio"]

    # extract a fresh rib unit-cell from the current (single- or multi-rib)
    # mesh, from whatever rib currently sits nearest x=0
    dup = tett.copy()
    dup.data = tett.data.copy()
    bpy.context.collection.objects.link(dup)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    dup.select_set(True)
    bpy.context.view_layer.objects.active = dup
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(dup.data)
    # find the rib nearest x=0 by locating any vert within +-1 period of 0
    candidate_x = min((v.co.x for v in bm.verts if abs(v.co.x) < TETTUCCIO_PERIOD_CM), key=abs, default=0.0)
    to_delete = [v for v in bm.verts if not (candidate_x - 6.5 < v.co.x < candidate_x + 6.5)]
    bmesh.ops.delete(bm, geom=to_delete, context="VERTS")
    bmesh.update_edit_mesh(dup.data)
    bpy.ops.object.mode_set(mode="OBJECT")
    for v in dup.data.vertices:
        v.co.x -= candidate_x  # recenter the extracted rib on x=0
    rib_template = dup.data
    bpy.data.objects.remove(dup, do_unlink=True)

    # strip every existing rib from Tettuccio, keep only the two end-caps
    bpy.context.view_layer.objects.active = tett
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    tett.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(tett.data)
    # ribs live well inside the end-caps. Empirically, a margin of 20 lands
    # exactly on a vertex belonging to one large connected face on the RIGHT
    # end-cap only (not a symmetric mesh feature) — deleting that one vertex
    # cascades bmesh.ops.delete into removing that whole face group (and
    # everything only reachable through it), leaving the right end-cap mostly
    # gone while the left (more finely subdivided there) survives intact.
    # Margin 22 clears that vertex on both sides (confirmed symmetric via a
    # direct test sweeping the margin) without eating meaningfully more of
    # the rib zone.
    inner_bound = TETTUCCIO_ENDCAP_OUTER_CM - 22.0
    ridge_verts = [v for v in bm.verts if -inner_bound < v.co.x < inner_bound]
    bmesh.ops.delete(bm, geom=ridge_verts, context="VERTS")
    bmesh.update_edit_mesh(tett.data)
    bpy.ops.object.mode_set(mode="OBJECT")

    cur_outer = max(v.co.x for v in tett.data.vertices)
    target_outer = L_cm / 2 + (TETTUCCIO_ENDCAP_OUTER_CM - REF_L_CM / 2)
    delta_cap = target_outer - cur_outer
    for v in tett.data.vertices:
        if v.co.x > 0:
            v.co.x += delta_cap
        else:
            v.co.x -= delta_cap

    # Ribs are allowed to reach right up under the end-caps (the end-cap
    # faces are exactly what's meant to cover them there, per Davide) — the
    # only real constraint is that a rib must not poke out past the true
    # outer edge. So the rib range is derived directly from target_outer
    # (symmetric by construction), not from measuring whatever survived the
    # strip above — that measurement was fragile (see the strip's own
    # comment) and made ribs stop short of the end-cap for no visual reason.
    rib_reach_margin = 8.8  # cm of clean, rib-free border left at the very edge
    outer_limit = target_outer - rib_reach_margin
    k_max = math.floor((outer_limit - TETTUCCIO_RIB_HALF_WIDTH_CM) / TETTUCCIO_PERIOD_CM)
    k_min = -k_max

    new_ribs = []
    for k in range(k_min, k_max + 1):
        mesh_copy = rib_template.copy()
        for v in mesh_copy.vertices:
            v.co.x += k * TETTUCCIO_PERIOD_CM
            v.co.y -= TETTUCCIO_RIDGE_LOWER_CM
        obj = bpy.data.objects.new(f"Tettuccio_rib_tmp_{k}", mesh_copy)
        bpy.context.collection.objects.link(obj)
        obj.rotation_euler = tett.rotation_euler
        obj.scale = tett.scale
        obj.location = tett.location
        new_ribs.append(obj)

    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in new_ribs:
        o.select_set(True)
    tett.select_set(True)
    bpy.context.view_layer.objects.active = tett
    bpy.ops.object.join()

    # Tettuccio only ever rotates with the rear pivot — its own width/rib
    # count is entirely a function of L (above), never of SP, per Davide:
    # "il tettuccio... dovrebbe semplicemente ruotare, non muoversi e non
    # fare nulla [altro]".
    rail_transform_verts(tett, rail, delta_x_cm=0.0, extend=False)
    return len(new_ribs) + 1


def build_telo(rail, delta_x_cm):
    telo = bpy.data.objects["Telo"]
    rail_transform_verts(telo, rail, delta_x_cm=delta_x_cm, extend=True)


def build_aggancio_parete(delta_x_cm, rail):
    for name, sign in (("Aggancio_Parete", 1), ("Aggancio_Parete.002", -1)):
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        for v in obj.data.vertices:
            v.co.x += sign * delta_x_cm
        rail_transform_verts(obj, rail, delta_x_cm=0.0, extend=False)


def set_fissaggio_variant(fissaggio):
    vl = bpy.context.view_layer

    def find_lc(layer_coll, name):
        if layer_coll.collection.name == name:
            return layer_coll
        for child in layer_coll.children:
            found = find_lc(child, name)
            if found:
                return found
        return None

    lc_auto = find_lc(vl.layer_collection, "Config_Autoportante")
    lc_parete = find_lc(vl.layer_collection, "Config_Parete")
    lc_auto.exclude = fissaggio != "autoportante"
    lc_parete.exclude = fissaggio != "parete"


def hide_unfinished_accessories():
    """Timpano/Trave_Laterale aren't parametrized for arbitrary L/P/H yet;
    Pilastrino_intermedio/Skipper are still unexplained. Keep all four out of
    every render until they're properly generalized."""
    for name in ("Timpano", "Trave_Laterale", "Pilastrino_intermedio", "Skipper"):
        obj = bpy.data.objects.get(name)
        if obj is not None and obj.name in bpy.context.view_layer.objects:
            obj.hide_render = True
            obj.hide_set(True)


def build_pergola(L_cm, P_cm, H_cm, delta_h_cm, fissaggio, n_guide=2):
    delta_x_cm = L_cm / 2 - REF_L_CM / 2
    # Only the FRONT structure (Montante, Trave) moves with SP — the rear is
    # fixed at the wall bracket (world Y=0), per the 2026-09-26 rework.
    delta_z_cm = P_cm - REF_P_NOMINAL_CM

    rail = compute_rail(H_cm, delta_h_cm, P_cm)

    build_montante(L_cm, H_cm, delta_z_cm, n_guide)
    build_trave(L_cm, H_cm, delta_z_cm)
    build_montante_posteriore(delta_x_cm, rail)
    build_trave_posteriore(L_cm, delta_x_cm, rail)

    build_supporto(delta_x_cm, rail, L_cm, n_guide)
    build_guida(rail, delta_x_cm, L_cm, n_guide)
    n_intermedi = build_frangitratta(L_cm, rail, delta_x_cm)
    build_tettuccio(L_cm, rail)
    build_telo(rail, delta_x_cm)
    build_aggancio_parete(delta_x_cm, rail)

    set_fissaggio_variant(fissaggio)
    hide_unfinished_accessories()

    bpy.context.view_layer.update()
    return {"n_frangitratta_intermedi": n_intermedi}


def apply_visual_offset(offset_x_cm=0.0, offset_z_cm=0.0):
    """Rigid world-space nudge of the ENTIRE already-built pergola — added
    2026-10-04 so the wizard can let a seller fine-tune a render's on-photo
    fit (small calibration mismatches: "position was right but it reads a
    bit too far left/forward") WITHOUT touching the real quote dimensions
    (L_cm/P_cm/H_cm stay exactly what the customer configured; only this
    render gets nudged). Deliberately NOT exposed as a quote field — see
    RenderScene3dDto's doc.

    Every object in this file shares the exact same rotation_euler/scale/
    location (BASE_ROT, 0.01, origin — confirmed empirically), so a uniform
    LOCAL vertex delta is already a uniform WORLD delta, no per-object
    transform math needed. Local-space convention throughout this script
    (see rail_transform_verts etc.): X=width, Y=height, Z=depth — so
    offset_x_cm is left/right, offset_z_cm is forward/back. Height is
    deliberately NOT offered here: "lower it" means override H_cm itself
    (every leg still reaches exactly to world Y=0, the real ground) rather
    than floating/sinking the whole rigid body, which a Y offset would do.
    """
    if offset_x_cm == 0.0 and offset_z_cm == 0.0:
        return
    for obj in bpy.context.view_layer.objects:
        if obj.type != "MESH" or not obj.visible_get():
            continue
        for v in obj.data.vertices:
            v.co.x += offset_x_cm
            v.co.z += offset_z_cm
        obj.data.update()


# ---------------------------------------------------------------------------
# Camera + render
# ---------------------------------------------------------------------------


def setup_camera_from_pnp(rvec, tvec, fov_deg, image_w, image_h):
    """Converts an OpenCV solvePnP pose (see pergolando-backend's
    PerspectiveService — same PnP-world convention: X right, Y down, Z away
    from camera, all in cm) into a Blender camera transform, and configures
    the render resolution + matching field of view.

    NOTE: front_offset below predates the 2026-09-26 rework that moved the
    world origin to the rear wall bracket — it may need revisiting now that
    "front" is no longer roughly centered on the world origin. Not yet
    re-verified against the new coordinate convention.
    """
    import mathutils

    rvec_v = mathutils.Vector(rvec)
    angle = rvec_v.length
    axis = rvec_v.normalized() if angle > 1e-9 else mathutils.Vector((1, 0, 0))
    R = mathutils.Matrix.Rotation(angle, 3, axis)  # object(world)->camera rotation
    t = mathutils.Vector(tvec) * 0.01  # cm -> m

    # World point (PnP convention, meters) = R^T * (camera_point - t)... but we
    # need the CAMERA's own world transform. solvePnP gives R,t such that:
    #   p_cam = R * p_world + t
    # => camera position in PnP-world = -R^T * t
    # => camera's own rotation (world->camera basis vectors) = R^T columns
    R_inv = R.transposed()
    cam_pos_pnp = -(R_inv @ t)

    # PnP-world (X right, Y down, Z depth) -> Blender pergola world (X right,
    # Z up, Y depth), same convention used throughout flag.blend:
    #   blender_X = pnp_X, blender_Y = pnp_Z + front_offset, blender_Z = -pnp_Y
    front_offset = world_yz_center(bpy.data.objects["Trave"])[0]

    def pnp_to_blender(v):
        return mathutils.Vector((v.x, v.z + front_offset, -v.y))

    cam_pos_blender = pnp_to_blender(cam_pos_pnp)

    # Camera basis vectors in PnP-world are R_inv's columns (camera's local
    # X/Y/Z axes expressed in world coords); transform each the same way,
    # then re-derive a rotation matrix (no translation) from them for Blender.
    cam_x_pnp = mathutils.Vector((R_inv[0][0], R_inv[1][0], R_inv[2][0]))
    cam_y_pnp = mathutils.Vector((R_inv[0][1], R_inv[1][1], R_inv[2][1]))
    cam_z_pnp = mathutils.Vector((R_inv[0][2], R_inv[1][2], R_inv[2][2]))

    def dir_to_blender(v):
        return mathutils.Vector((v.x, v.z, -v.y))

    bx = dir_to_blender(cam_x_pnp)
    by = dir_to_blender(cam_y_pnp)
    bz = dir_to_blender(cam_z_pnp)

    # OpenCV camera looks down +Z (cam_z), with +Y down, +X right. Blender's
    # camera looks down local -Z, with +Y up, +X right — so Blender's basis
    # is (cam_x, -cam_y, -cam_z).
    blender_cam_x = bx
    blender_cam_y = -by
    blender_cam_z = -bz
    rot_matrix = mathutils.Matrix((blender_cam_x, blender_cam_y, blender_cam_z)).transposed()

    cam_data = bpy.data.cameras.new("PnPCamera")
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.angle = math.radians(fov_deg)
    cam_obj = bpy.data.objects.new("PnPCamera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = cam_pos_blender
    cam_obj.rotation_euler = rot_matrix.to_euler()
    bpy.context.scene.camera = cam_obj

    # Without this, cam_obj.matrix_world still reflects the depsgraph's
    # stale (pre-creation, effectively identity) state — the location/
    # rotation set above haven't been propagated yet. Every projection
    # (render, world_to_camera_view) silently uses that stale transform
    # instead: found 2026-09-28 testing against a real photo, where every
    # world point was projecting to the exact same pixel (frame center)
    # instead of their actual positions.
    bpy.context.view_layer.update()

    scene = bpy.context.scene
    scene.render.resolution_x = image_w
    scene.render.resolution_y = image_h
    scene.render.resolution_percentage = 100
    return cam_obj


def scene_world_bbox():
    vl = bpy.context.view_layer
    bpy.context.view_layer.update()
    mins = [1e9, 1e9, 1e9]
    maxs = [-1e9, -1e9, -1e9]
    for obj in vl.objects:
        if obj.type != "MESH" or not obj.visible_get():
            continue
        mw = obj.matrix_world
        for v in obj.data.vertices:
            w = mw @ v.co
            for i in range(3):
                mins[i] = min(mins[i], w[i])
                maxs[i] = max(maxs[i], w[i])
    return mins, maxs


# Orthographic elevation/plan views (documentazione preventivo, 2026-09-28).
# Each entry gives the camera's (forward, up) directions in Blender WORLD
# coordinates (X=larghezza, Y=profondità con -Y=fronte/+Y=retro-parete,
# Z=altezza — vedi NOTES.md). "right" is derived as up x forward to complete
# a right-handed local frame (local X=right, Y=up, Z=-forward, matching
# Blender's default camera convention, same as setup_camera_from_pnp above).
ORTHO_VIEWS = {
    # Plan/top view: looking straight down. Rear (wall) at the TOP of the
    # image, front at the bottom — reads like a real architectural plan of
    # a wall-mounted piece.
    "top": ((0, 0, -1), (0, 1, 0)),
    # Front elevation: standing in front, looking at the wall. Width (X)
    # horizontal, height (Z) vertical.
    "front": ((0, 1, 0), (0, 0, 1)),
    # Side elevation: viewed from +X looking toward -X. Depth (Y) horizontal
    # (front on the left, wall/rear on the right), height (Z) vertical —
    # this is the view that shows the roof's slope (deltaH).
    "side": ((-1, 0, 0), (0, 0, 1)),
}


def setup_ortho_camera(view, margin=1.15, resolution_long_side=1400):
    """Orthographic camera for a technical elevation/plan view (no
    perspective — true-to-scale, like a CAD drawing). Returns a dict with
    everything `add_dimensions.py` needs to place dimension lines in pixel
    space afterwards: the world "right"/"up" axes actually used, the
    camera's world-space center, ortho_scale (world units spanning the
    image horizontally) and resolution.
    """
    import mathutils

    forward, up = ORTHO_VIEWS[view]
    forward = mathutils.Vector(forward).normalized()
    up = mathutils.Vector(up).normalized()
    # Right-handed local frame (X=right, Y=up, Z=-forward): right x up must
    # equal -forward, i.e. right = forward x up (not up x forward, which
    # gives the mirrored/wrong-handed sign).
    right = forward.cross(up).normalized()

    mins, maxs = scene_world_bbox()
    center = mathutils.Vector([(mins[i] + maxs[i]) / 2 for i in range(3)])
    size = mathutils.Vector([maxs[i] - mins[i] for i in range(3)])

    extent_right = abs(right.x) * size.x + abs(right.y) * size.y + abs(right.z) * size.z
    extent_up = abs(up.x) * size.x + abs(up.y) * size.y + abs(up.z) * size.z
    ortho_scale = extent_right * margin
    aspect = (extent_up * margin) / ortho_scale
    if aspect >= 1:
        resolution_y = resolution_long_side
        resolution_x = max(1, round(resolution_long_side / aspect))
        # keep ortho_scale tied to the HORIZONTAL extent regardless of which
        # side ended up longer, so sensor_fit stays consistent below
    else:
        resolution_x = resolution_long_side
        resolution_y = max(1, round(resolution_long_side * aspect))

    diag = size.length + 1.0
    cam_pos = center - forward * diag * 2

    cam_data = bpy.data.cameras.new(f"OrthoCamera_{view}")
    cam_data.type = "ORTHO"
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.ortho_scale = ortho_scale
    cam_data.clip_start = 0.01
    cam_data.clip_end = diag * 4
    cam_obj = bpy.data.objects.new(f"OrthoCamera_{view}", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = cam_pos

    local_z = -forward
    rot_matrix = mathutils.Matrix((right, up, local_z)).transposed()
    cam_obj.rotation_euler = rot_matrix.to_euler()
    bpy.context.scene.camera = cam_obj
    bpy.context.view_layer.update()

    scene = bpy.context.scene
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = 100

    return {
        "view": view,
        "right_axis": list(right),
        "up_axis": list(up),
        "center_world": list(center),
        "ortho_scale": ortho_scale,
        "resolution_x": resolution_x,
        "resolution_y": resolution_y,
        # True rendered geometry extent (meters, world space) — lets a
        # post-process dimensioning script (add_dimensions.py) snap quote
        # lines to the ACTUAL silhouette edges rather than trusting nominal
        # L_cm/P_cm/H_cm alone, which can be a few cm off from any single
        # piece's real extent (overhangs, end-cap details, calibration
        # offsets baked into the reference mesh).
        "bbox_min": list(mins),
        "bbox_max": list(maxs),
    }


def render_isolated(output_path, transparent=True):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    scene.render.film_transparent = transparent
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


def render_depth_map(output_path):
    """
    Step 5's real deliverable: not a materialed render at all, just a
    relative depth map of the pergola silhouette (near = bright, background/
    far = transparent black) — the structural conditioning image ControlNet
    needs so it doesn't invent a different shape. No lighting or materials
    are involved, so this is both simpler AND cheaper to compute than the
    "debug" material render `render_isolated` produces (that one exists only
    for visually sanity-checking the geometry itself, e.g. from the wizard's
    "Genera anteprima 3D" preview).
    """
    scene = bpy.context.scene
    cam = scene.camera
    if cam is None:
        raise RuntimeError("render_depth_map requires a camera to already be set")

    vl = bpy.context.view_layer
    bpy.context.view_layer.update()
    cam_pos = cam.matrix_world.translation
    near_dist = 1e9
    far_dist = 0.0
    for obj in vl.objects:
        if obj.type != "MESH" or not obj.visible_get():
            continue
        mw = obj.matrix_world
        for v in obj.data.vertices:
            d = (mw @ v.co - cam_pos).length
            near_dist = min(near_dist, d)
            far_dist = max(far_dist, d)

    vl.use_pass_z = True
    # Blender 5.x is mid-way through unifying the compositor's node set with
    # the shader editor's, and the scene compositor is now itself just a
    # node GROUP (CompositorNodeMath/CompositorNodeMapRange/
    # CompositorNodeComposite no longer exist as of this version):
    #  - generic ShaderNode* equivalents work fine inside a CompositorNodeTree
    #  - the tree needs an explicit interface output socket + a
    #    NodeGroupOutput node, there's no more dedicated "Composite" node
    ng = bpy.data.node_groups.new("PergolandoDepthComposite", "CompositorNodeTree")
    scene.compositing_node_group = ng
    tree = ng
    tree.nodes.clear()
    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    rl = tree.nodes.new("CompositorNodeRLayers")
    rl.layer = vl.name

    map_range = tree.nodes.new("ShaderNodeMapRange")
    map_range.inputs["From Min"].default_value = near_dist
    map_range.inputs["From Max"].default_value = far_dist
    map_range.inputs["To Min"].default_value = 1.0
    map_range.inputs["To Max"].default_value = 0.05
    map_range.clamp = True
    tree.links.new(rl.outputs["Depth"], map_range.inputs["Value"])

    # zero out anything outside the geometry (background) via alpha, rather
    # than trusting Map Range's clamp alone — the background's Z value is an
    # arbitrarily huge sentinel, not a real distance
    mask_mul = tree.nodes.new("ShaderNodeMath")
    mask_mul.operation = "MULTIPLY"
    tree.links.new(map_range.outputs[0], mask_mul.inputs[0])
    tree.links.new(rl.outputs["Alpha"], mask_mul.inputs[1])

    combine = tree.nodes.new("CompositorNodeCombineColor")
    for i in range(3):
        tree.links.new(mask_mul.outputs[0], combine.inputs[i])

    set_alpha = tree.nodes.new("CompositorNodeSetAlpha")
    tree.links.new(combine.outputs[0], set_alpha.inputs["Image"])
    tree.links.new(rl.outputs["Alpha"], set_alpha.inputs["Alpha"])

    group_output = tree.nodes.new("NodeGroupOutput")
    tree.links.new(set_alpha.outputs[0], group_output.inputs[0])

    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


def render_freestyle(output_path):
    """
    Passo 6b (esperimento richiesto da Davide, 2026-09-28): contorni puliti
    via Freestyle, per un vero ControlNet — non un edge-detection Canny su
    un render raster, ma la line art "da disegno tecnico" che Freestyle
    genera direttamente dalla geometria (silhouette/crease/border), pensata
    per un ControlNet-lineart o -scribble più che per un ControlNet-canny
    classico. A differenza di `render_depth_map` (mappa di profondità in
    scala di grigi), qui l'output sono linee nere su sfondo trasparente.
    """
    scene = bpy.context.scene
    cam = scene.camera
    if cam is None:
        raise RuntimeError("render_freestyle requires a camera to already be set")

    # Freestyle needs a real render engine — Workbench (used elsewhere in
    # this script for the "debug" reference views) has no Freestyle support
    # at all. Never hardcode a single engine id blindly (identifiers shift
    # between Blender versions, per project convention) — try candidates in
    # order of preference and use whichever one this Blender build accepts.
    for engine_id in ("CYCLES", "BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine_id
            break
        except TypeError:
            continue
    else:
        raise RuntimeError(
            "no supported render engine found for Freestyle (tried CYCLES, "
            "BLENDER_EEVEE_NEXT, BLENDER_EEVEE)"
        )

    vl = bpy.context.view_layer
    scene.render.use_freestyle = True
    vl.use_freestyle = True

    fs = vl.freestyle_settings
    if not fs.linesets:
        fs.linesets.new("PergolandoLineSet")
    lineset = fs.linesets.active
    lineset.select_silhouette = True
    lineset.select_crease = True
    lineset.select_border = True

    # Freestyle draws its strokes ON TOP of the normal shaded render by
    # default (the Combined output) — not what a ControlNet conditioning
    # image wants on its own. Blender 5.x has no separate "Freestyle" pass to
    # pull out in the compositor instead (confirmed by RNA introspection:
    # no ViewLayer.use_pass_freestyle, no such Render Layers output socket —
    # unlike render_depth_map's Z pass, which does exist). Line-only output
    # instead relies on the fact that Freestyle reads edges straight from
    # mesh geometry, not from shading: give every mesh a Holdout material,
    # which cuts its surface out of the Combined image entirely (transparent,
    # since film_transparent is on) while Freestyle keeps drawing strokes on
    # top of that hole. Confirmed empirically on a standalone test cube
    # before touching this file. These material swaps are never
    # saved — this Blender process only ever renders and exits.
    holdout_mat = bpy.data.materials.new("PergolandoFreestyleHoldout")
    holdout_mat.use_nodes = True
    nt = holdout_mat.node_tree
    nt.nodes.clear()
    holdout_node = nt.nodes.new("ShaderNodeHoldout")
    output_node = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(holdout_node.outputs[0], output_node.inputs["Surface"])

    for obj in vl.objects:
        if obj.type != "MESH" or not obj.visible_get():
            continue
        if obj.data.materials:
            for i in range(len(obj.data.materials)):
                obj.data.materials[i] = holdout_mat
        else:
            obj.data.materials.append(holdout_mat)

    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


# Which pieces feed each of the two partial line-art references (2026-10-04,
# Davide's exact split): "montanti" = Montante/.001 (front legs) +
# Montante_Posteriore_Dx/Sx (rear legs) — all start with "Montante"; "travi"
# = Trave (front beam) + Trave_Posteriore (rear beam) — both start with
# "Trave" (this also matches "Trave_Laterale", but that piece is always
# hidden/excluded — see hide_unfinished_accessories — so it never reaches
# render_lineart_gp's visible-objects filter anyway); "guide" = Guida/.001
# + any Guida_intermedio_N (multi-guide, see guide_x_targets) — all start
# with "Guida". The roof split is simpler: every Frangitratta_* piece plus
# Telo's own profile — deliberately NOT Tettuccio (not asked for).
LINEART_STRUCTURE_PREFIXES = ("Montante", "Trave", "Guida")
LINEART_ROOF_PREFIXES = ("Frangitratta", "Telo")


def render_lineart_gp(output_path, object_filter=None, crease_deg=130.0, line_radius=0.008, samples=64):
    """
    Line-art via Grease Pencil's Line Art modifier — replaces the earlier
    Freestyle+Holdout technique (render_freestyle above) for the ComfyUI
    reference set, per Davide's explicit modifier settings (2026-10-04):
    Crease ON (threshold ~120-140 deg), Silhouette/Contour ON, Material
    Boundary OFF, Intersection ON (needed to see where Telo meets
    Frangitratta instead of them merging into one outline), Loose OFF,
    Overlapping Edges OFF, very thin lines (~1-2px) — and critically, NO
    FILL: stroke-only output, none of Freestyle's "large flat shape" look.

    `object_filter`: optional iterable of name PREFIXES — when given, only
    source objects whose name starts with one of these prefixes feed the
    Line Art modifier (used for structure_lineart.png/roof_lineart.png);
    None (default) uses the whole visible scene, same coverage as the old
    render_freestyle.

    Two real Blender 5.2 quirks found making this work, neither documented
    anywhere obvious, both confirmed by direct depsgraph inspection:
    - The LINEART modifier's target_layer/target_material are BOTH empty
      by default and silently produce zero strokes until explicitly
      pointed at a real GP layer/material that already exists on the GP
      object the modifier lives on.
    - hide_render=True on a source mesh ALSO produces zero strokes for it
      — Line Art reads source geometry from the very depsgraph being
      built for the render, and a hide_render object isn't evaluated into
      it at all. Holdout materials (same trick render_freestyle already
      used) keep objects "present" for Line Art to read while
      contributing nothing to the final Combined image — this is why
      every source object below gets a Holdout material instead of being
      hidden, even though hiding would otherwise be simpler.
    """
    scene = bpy.context.scene
    cam = scene.camera
    if cam is None:
        raise RuntimeError("render_lineart_gp requires a camera to already be set")

    vl = bpy.context.view_layer
    visible_meshes = [o for o in vl.objects if o.type == "MESH" and o.visible_get()]
    if object_filter is not None:
        source_objs = [o for o in visible_meshes if any(o.name.startswith(p) for p in object_filter)]
        if not source_objs:
            raise RuntimeError(f"render_lineart_gp: object_filter {object_filter!r} matched no visible mesh objects")
    else:
        source_objs = visible_meshes

    holdout_mat = bpy.data.materials.new("PergolandoLineArtHoldout")
    holdout_mat.use_nodes = True
    nt = holdout_mat.node_tree
    nt.nodes.clear()
    holdout_node = nt.nodes.new("ShaderNodeHoldout")
    output_node = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(holdout_node.outputs[0], output_node.inputs["Surface"])
    for obj in source_objs:
        if obj.data.materials:
            for i in range(len(obj.data.materials)):
                obj.data.materials[i] = holdout_mat
        else:
            obj.data.materials.append(holdout_mat)

    if object_filter is not None:
        # The LINEART modifier's source_type='COLLECTION' is what supports
        # an arbitrary object SUBSET ('OBJECT' only takes a single object)
        # — build a throwaway collection just for this filtered set. An
        # object can belong to more than one collection at once, so this
        # doesn't disturb the scene's real collection structure. Every
        # OTHER mesh must be fully hidden from render too, or it'd show
        # through as a plain (un-outlined) silhouette.
        source_collection = bpy.data.collections.new("PergolandoLineArtSource_tmp")
        bpy.context.scene.collection.children.link(source_collection)
        for obj in source_objs:
            source_collection.objects.link(obj)
        excluded = set(source_objs)
        for obj in visible_meshes:
            if obj not in excluded:
                obj.hide_render = True
    else:
        source_collection = bpy.context.scene.collection

    bpy.ops.object.grease_pencil_add(type="EMPTY")
    gp_obj = bpy.context.active_object
    gp_obj.name = "PergolandoLineArt"
    mod = gp_obj.modifiers.new("LineArt", type="LINEART")
    mod.source_type = "COLLECTION"
    mod.source_collection = source_collection
    mod.use_crease = True
    mod.crease_threshold = math.radians(crease_deg)
    mod.use_contour = True
    mod.use_material = False
    mod.use_intersection = True
    mod.use_loose = False
    mod.use_edge_overlap = False
    mod.radius = line_radius

    gp_mat = gp_obj.data.materials[0]
    mod.target_layer = gp_obj.data.layers[0].name
    mod.target_material = gp_mat
    gp_mat.grease_pencil.show_fill = False
    gp_mat.grease_pencil.show_stroke = True
    gp_mat.grease_pencil.color = (0.0, 0.0, 0.0, 1.0)

    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = samples
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


def render_colored(
    output_path,
    color_rgb,
    fissaggio,
    resolution=(2560, 1920),
    fabric_rgb=None,
    frangitratta_rgb=None,
    include_backdrop=True,
):
    """
    Documentazione preventivo (2026-09-28), quarta vista: non un tecnico a
    linee ma una prospettiva "come sarebbe davvero" — colore reale, luce
    **solo ambientale** (un mondo/World uniforme come unica sorgente: niente
    sole, niente luci dirette) per ombre morbide, mai nette.

    `color_rgb` va sulla struttura in alluminio (tutti i pezzi tranne
    `Telo`); `fabric_rgb`, se dato, va SOLO su `Telo` (il telo in tessuto,
    finitura più opaca/ruvida della struttura verniciata) — permette di
    distinguere ad es. RAL 9016 bianco per l'alluminio da un telo "panna"
    diverso, invece di un unico colore uniforme su tutto (2026-09-30).

    Pavimento e (se `fissaggio == "parete"`) un piano muro esistono SOLO per
    dare all'illuminazione ambientale qualcosa su cui proiettare un'ombra di
    contatto morbida — mai visibili loro stessi nel render finale (Davide,
    2026-09-30): sono **shadow catcher** Cycles (`obj.is_shadow_catcher`),
    trasparenti ovunque tranne dove cade davvero un'ombra, con output finale
    RGBA (`film_transparent=True`) — quindi il risultato è "solo la pergola
    (+ la sua ombra)" su sfondo trasparente, componibile su qualunque sfondo
    dopo.
    """
    import mathutils

    scene = bpy.context.scene
    vl = bpy.context.view_layer

    # Powder-coated aluminum, not raw/brushed metal: Metallic close to 1 so
    # it actually reflects its surroundings (a metal=0 diffuse "white
    # plastic" shader was exactly the "flat, no shading" look Davide
    # flagged, 2026-09-30) — needs a varied environment to reflect (see
    # HDRI below), not just a flat color, or it still reads as flat.
    # Roughness: 0.3 -> 0.15 (2026-10-04) read as near-chrome/mirror-like
    # hard streak highlights instead of a painted-metal sheen — reverted
    # direction, raised to 0.5 (2026-10-05, Davide: "molto meno
    # riflettenti"). Still not declared final — easy to re-tune from here.
    mat = bpy.data.materials.new("PergolandoColored")
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color_rgb, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.9
    bsdf.inputs["Roughness"].default_value = 0.5

    fabric_mat = None
    if fabric_rgb is not None:
        fabric_mat = bpy.data.materials.new("PergolandoFabric")
        fabric_mat.use_nodes = True
        fabric_bsdf = next(n for n in fabric_mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        fabric_bsdf.inputs["Base Color"].default_value = (*fabric_rgb, 1.0)
        # Explicit Metallic=0 (Principled's own default, but spelled out so
        # it can't drift later) + Roughness close to 1: fabric must read as
        # a flat matte textile, no reflections at all (2026-10-04, Davide).
        fabric_bsdf.inputs["Metallic"].default_value = 0.0
        fabric_bsdf.inputs["Roughness"].default_value = 0.95

    # Frangitratta pieces are the real "parti in plastica" — confirmed by
    # the bundle's own catalog data, where colorePlastica's UI label is
    # literally "Colore frangitratta" (2026-10-03; an earlier guess had
    # lumped them in with the aluminum struttura color for lack of a known
    # mapping). Non-metallic, matte — plastic, not painted aluminum.
    frangitratta_mat = None
    if frangitratta_rgb is not None:
        frangitratta_mat = bpy.data.materials.new("PergolandoFrangitratta")
        frangitratta_mat.use_nodes = True
        ft_bsdf = next(n for n in frangitratta_mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        ft_bsdf.inputs["Base Color"].default_value = (*frangitratta_rgb, 1.0)
        ft_bsdf.inputs["Roughness"].default_value = 0.5

    for obj in vl.objects:
        if obj.type != "MESH" or not obj.visible_get():
            continue
        if fabric_mat is not None and obj.name == "Telo":
            piece_mat = fabric_mat
        elif frangitratta_mat is not None and obj.name.startswith("Frangitratta"):
            piece_mat = frangitratta_mat
        else:
            piece_mat = mat
        if obj.data.materials:
            for i in range(len(obj.data.materials)):
                obj.data.materials[i] = piece_mat
        else:
            obj.data.materials.append(piece_mat)

    mins, maxs = scene_world_bbox()
    center = mathutils.Vector([(mins[i] + maxs[i]) / 2 for i in range(3)])
    size = mathutils.Vector([maxs[i] - mins[i] for i in range(3)])
    footprint = max(size.x, size.y)

    # `include_backdrop=False`: for the wizard's photo-match overlay (a real
    # site photo already provides the floor/wall), not the standalone
    # documentation shot — skips the shadow-catcher floor/wall entirely so
    # there's nothing to composite but the pergola itself, real materials,
    # transparent elsewhere (2026-10-03).
    if include_backdrop:
        bg_color = (0.86, 0.855, 0.85)
        backdrop_mat = bpy.data.materials.new("PergolandoBackdrop")
        backdrop_mat.use_nodes = True
        backdrop_bsdf = next(n for n in backdrop_mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        backdrop_bsdf.inputs["Base Color"].default_value = (*bg_color, 1.0)
        backdrop_bsdf.inputs["Roughness"].default_value = 0.9

        # Floor + wall exist ONLY to give the ambient light something to
        # bounce off and to catch a soft contact shadow under/behind the
        # pergola — per Davide (2026-09-30), the floor/wall themselves must
        # NOT be visible in the final image, only the pergola and the shadow
        # it casts. Cycles' "shadow catcher" object flag does exactly this:
        # the plane is fully transparent in the render except where a shadow
        # actually falls on it, composited straight into the alpha channel —
        # so it still needs to be physically present and lit for the shadow
        # math to work, it just never shows as a solid backdrop.
        bpy.ops.mesh.primitive_plane_add(size=footprint * 6, location=(center.x, center.y, mins[2]))
        floor = bpy.context.active_object
        floor.name = "PergolandoFloor"
        floor.data.materials.append(backdrop_mat)
        floor.is_shadow_catcher = True

        if fissaggio == "parete":
            # Vertical shadow catcher behind the wall-attachment side, same
            # reasoning as the floor — never visible itself, only its shadow.
            wall_y = maxs[1] + 0.02
            bpy.ops.mesh.primitive_plane_add(
                size=1.0, location=(center.x, wall_y, mins[2] + (maxs[2] - mins[2]) * 1.2)
            )
            wall = bpy.context.active_object
            wall.name = "PergolandoWallBackdrop"
            wall.rotation_euler = (math.radians(90), 0, 0)
            wall.scale = (footprint * 2, (maxs[2] - mins[2]) * 3, 1)
            wall.data.materials.append(backdrop_mat)
            wall.is_shadow_catcher = True

    # HDRI instead of a flat World color (Davide, 2026-09-30): a single flat
    # color has no variation for a metallic material to reflect, which was
    # the other half of why the aluminum looked flat/uniform — a mirror
    # pointed at a blank grey card still looks like a blank grey card. A
    # soft studio HDRI (Poly Haven, CC0, downloaded into 3d/hdri/) gives
    # real, varied highlights/reflections while staying soft/ambient — no
    # actual sun/lamp added, so shadows stay soft, matching the original
    # "ombre morbide, mai nette" requirement.
    world = scene.world or bpy.data.worlds.new("PergolandoWorld")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    bg_node = nt.nodes.new("ShaderNodeBackground")
    env_tex = nt.nodes.new("ShaderNodeTexEnvironment")
    hdri_path = Path(__file__).parent / "hdri" / "studio_small_08_1k.hdr"
    env_tex.image = bpy.data.images.load(str(hdri_path))
    nt.links.new(env_tex.outputs["Color"], bg_node.inputs["Color"])
    bg_node.inputs["Strength"].default_value = 1.0
    world_output = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(bg_node.outputs["Background"], world_output.inputs["Surface"])

    # If the caller already set up a camera (e.g. setup_camera_from_pnp, to
    # match this same shot's line art/depth/mask renders exactly), use it
    # as-is — resolution included — instead of this function's own default
    # "a bit from above" auto-framing. Added 2026-09-30 so all four outputs
    # of one shot (freestyle/depth/mask/colored) can share one perspective.
    if scene.camera is None:
        offset = mathutils.Vector((1.0, -1.7, 1.15))  # "un po' dall'alto"
        cam_data = bpy.data.cameras.new("ColoredCamera")
        cam_data.angle = math.radians(45)
        cam_obj = bpy.data.objects.new("ColoredCamera", cam_data)
        bpy.context.collection.objects.link(cam_obj)
        cam_obj.location = center + offset * max(size.length, footprint)
        direction = center - cam_obj.location
        cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        scene.camera = cam_obj
        bpy.context.view_layer.update()
        scene.render.resolution_x, scene.render.resolution_y = resolution
        scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True

    # EEVEE (2026-10-04, measured on the real test_02 camera/scene): ~5s vs
    # Cycles' ~27s at 128 samples, visually equivalent for this preview's
    # purpose — `use_raytracing` gives the metallic material real
    # reflections instead of falling back to flat screen-space ones. Note:
    # when include_backdrop=True, the floor/wall's `is_shadow_catcher` flag
    # (set above) has NO effect under EEVEE — confirmed empirically it
    # renders as a plain opaque plane instead of "transparent except where a
    # shadow falls". Harmless today (nothing calls render_colored with
    # include_backdrop=True — see 3d/NOTES.md), but if that path gets reused
    # later, it needs either a real fix or to stay on Cycles for that case.
    # A working two-pass EEVEE+Cycles hybrid (pergola on EEVEE, shadow-only
    # pass on Cycles via Holdout, composited through Blender's own
    # compositor) was prototyped and confirmed working 2026-10-04, then
    # shelved on Davide's call — not worth the complexity while unused.
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.use_raytracing = True
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


def render_mask(output_path):
    """
    Terzo output della pipeline di compositing (richiesto da Davide): una
    maschera — bianco/alfa=1 dove c'è la pergola, nero/alfa=0 sullo sfondo
    — nella STESSA camera/risoluzione/frame del render Canny
    (`render_freestyle`) e della foto di sfondo, pixel per pixel.

    Non serve un Object Index: nella scena Blender esistono SOLO i pezzi
    della pergola (nessun oggetto di sfondo concorrente), quindi il canale
    Alpha di un render con `film_transparent=True` è già una maschera
    oggetto/non-oggetto esatta, senza configurare `pass_index` per nulla.

    Corretto 2026-09-30 su richiesta di Davide: **niente dilatazione/margine
    ombre, niente blur/bordi sfumati** (un primo tentativo li aveva
    entrambi — vedi versione precedente nella cronologia git/NOTES.md) —
    solo la sagoma esatta della pergola, e soprattutto un **vero canale
    alfa PNG** (RGBA), non solo il valore replicato nei canali RGB. (Un
    secondo giro verso una versione binaria bianco/nero via soglia
    compositor è stato provato e poi ritirato da Davide come informazione
    sbagliata — questa RGBA resta la versione voluta.)
    """
    scene = bpy.context.scene
    cam = scene.camera
    if cam is None:
        raise RuntimeError("render_mask requires a camera to already be set")

    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


# Material-category ID pass (2026-10-03, richiesto da Davide): un riferimento
# extra per ComfyUI/ControlNet accanto a canny/depth/mask — colori piatti e
# NON illuminati, uno per categoria di materiale reale, non un render
# fotorealistico. Rosso = struttura in alluminio, verde = plastica, giallo =
# telo in tessuto. Correzione importante (2026-10-03, stesso giorno): i pezzi
# "Frangitratta" sono le parti in plastica reali — confermato dal catalogo del
# bundle stesso, dove l'etichetta UI di colorePlastica è letteralmente "Colore
# frangitratta" (`apps/studio/storage/bundles/Flag/*/catalog/database.json`,
# `prodotto.colori.parti_plastiche.tag`) — un tentativo precedente li aveva
# lasciati nel rosso/struttura per mancanza di un mapping noto.
MATERIAL_ID_STRUTTURA_RGB = (1.0, 0.0, 0.0)
MATERIAL_ID_PLASTICA_RGB = (0.0, 1.0, 0.0)
MATERIAL_ID_TELO_RGB = (1.0, 1.0, 0.0)


def render_material_id(output_path):
    """
    Pass "ID materiale": un colore piatto, non illuminato (shader Emission
    puro — niente luce, niente ombre, niente riflessi: il colore in output è
    sempre esattamente quello assegnato, indipendentemente dall'angolazione
    o dall'illuminazione) per categoria di pezzo. Stessa camera/risoluzione
    del Canny/depth/mask per restare nello stesso set coerente.
    """
    scene = bpy.context.scene
    cam = scene.camera
    if cam is None:
        raise RuntimeError("render_material_id requires a camera to already be set")

    vl = bpy.context.view_layer

    def flat_material(name, rgb):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        emission = nt.nodes.new("ShaderNodeEmission")
        emission.inputs["Color"].default_value = (*rgb, 1.0)
        emission.inputs["Strength"].default_value = 1.0
        output_node = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(emission.outputs[0], output_node.inputs["Surface"])
        return mat

    struttura_mat = flat_material("MaterialID_Struttura", MATERIAL_ID_STRUTTURA_RGB)
    telo_mat = flat_material("MaterialID_Telo", MATERIAL_ID_TELO_RGB)
    plastica_mat = flat_material("MaterialID_Plastica", MATERIAL_ID_PLASTICA_RGB)

    for obj in vl.objects:
        if obj.type != "MESH" or not obj.visible_get():
            continue
        if obj.name == "Telo":
            piece_mat = telo_mat
        elif obj.name.startswith("Frangitratta"):
            piece_mat = plastica_mat
        else:
            piece_mat = struttura_mat
        if obj.data.materials:
            for i in range(len(obj.data.materials)):
                obj.data.materials[i] = piece_mat
        else:
            obj.data.materials.append(piece_mat)

    # EEVEE instead of Cycles (2026-10-04, Davide flagged real render times):
    # flat Emission colors need zero path-traced lighting to resolve — EEVEE
    # renders this instantly, Cycles was only ever noise-free here because
    # samples was already capped low, not because it needed ray tracing.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


def main():
    from pathlib import Path
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="path to a JSON config file")
    parser.add_argument("--config-json", help="inline JSON config string")
    parser.add_argument("--output", required=True, help="output PNG path")
    parser.add_argument("--save-blend", help="optional: also save the built scene here")
    args = parser.parse_args(argv)

    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    elif args.config_json:
        cfg = json.loads(args.config_json)
    else:
        raise SystemExit("--config or --config-json is required")

    n_guide = cfg["nGuide"] if "nGuide" in cfg else derive_n_guide_from_l(cfg["L_cm"])
    build_pergola(
        L_cm=cfg["L_cm"],
        P_cm=cfg["P_cm"],
        H_cm=cfg["H_cm"],
        delta_h_cm=cfg["deltaH_cm"],
        fissaggio=cfg.get("fissaggio", "autoportante"),
        n_guide=n_guide,
    )
    apply_visual_offset(cfg.get("offsetXCm", 0.0), cfg.get("offsetZCm", 0.0))

    if cfg.get("technicalViews"):
        sys.path.insert(0, str(Path(__file__).parent))
        from technical_views import render_technical_views
        render_technical_views(args.output,cfg)
        return
    output_mode = cfg.get("outputMode", "silhouette")

    # Technical 2D elevations/plan (documentazione preventivo, 2026-09-28):
    # true-to-scale orthographic camera + the same Freestyle line-art
    # technique as the ControlNet experiment, no perspective distortion.
    # Bypasses the perspective camera_cfg/default-camera setup entirely —
    # `add_dimensions.py` draws the quote lines afterwards as a separate
    # post-process, using the projection info saved alongside the render.
    if output_mode.startswith("ortho_"):
        view = output_mode[len("ortho_") :]
        if view not in ORTHO_VIEWS:
            raise SystemExit(f"unknown ortho view {view!r}, expected one of {list(ORTHO_VIEWS)}")
        projection = setup_ortho_camera(view)
        render_freestyle(args.output)
        sidecar = {
            **projection,
            "L_cm": cfg["L_cm"],
            "P_cm": cfg["P_cm"],
            "H_cm": cfg["H_cm"],
            "deltaH_cm": cfg["deltaH_cm"],
            "fissaggio": cfg.get("fissaggio", "autoportante"),
        }
        with open(str(args.output) + ".json", "w", encoding="utf-8") as f:
            json.dump(sidecar, f, indent=2)
        if args.save_blend:
            bpy.ops.wm.save_as_mainfile(filepath=args.save_blend)
        return

    if output_mode == "colored":
        color_rgb = tuple(cfg.get("colorRgb", [0.82, 0.80, 0.77]))
        fabric_rgb = tuple(cfg["fabricRgb"]) if "fabricRgb" in cfg else None
        frangitratta_rgb = tuple(cfg["frangitrattaRgb"]) if "frangitrattaRgb" in cfg else None
        colored_camera_cfg = cfg.get("camera")
        if colored_camera_cfg:
            # Match this shot's line art/depth/mask exactly, instead of
            # render_colored's own default "a bit from above" auto-camera.
            setup_camera_from_pnp(
                colored_camera_cfg["rvec"],
                colored_camera_cfg["tvec"],
                colored_camera_cfg.get("fovDeg", 60),
                colored_camera_cfg["imageWidthPx"],
                colored_camera_cfg["imageHeightPx"],
            )
            from photo_intrinsics import apply_photo_intrinsics
            apply_photo_intrinsics(bpy.context.scene,bpy.context.scene.camera.data,colored_camera_cfg)
        render_colored(
            args.output,
            color_rgb,
            cfg.get("fissaggio", "autoportante"),
            fabric_rgb=fabric_rgb,
            frangitratta_rgb=frangitratta_rgb,
            include_backdrop=cfg.get("includeBackdrop", True),
        )
        if cfg.get('includeShadows') and cfg.get('camera'):
            sys.path.insert(0,str(Path(__file__).parent))
            from eevee_shadows import render_floor_shadows
            render_floor_shadows(bpy.context.scene,args.output,cfg)
        if args.save_blend:
            bpy.ops.wm.save_as_mainfile(filepath=args.save_blend)
        return

    camera_cfg = cfg.get("camera")
    if camera_cfg:
        setup_camera_from_pnp(
            camera_cfg["rvec"],
            camera_cfg["tvec"],
            camera_cfg.get("fovDeg", 60),
            camera_cfg["imageWidthPx"],
            camera_cfg["imageHeightPx"],
        )
        from photo_intrinsics import apply_photo_intrinsics
        apply_photo_intrinsics(bpy.context.scene,bpy.context.scene.camera.data,camera_cfg)
    else:
        # simple default orbit camera + basic lighting, for a quick visual
        # sanity check only — not meant to look "good", just legible.
        # `viewPreset` picks the offset (default "isometrico", the original
        # single angle) — added because a single angle alone wasn't enough
        # of a visual anchor for Gemini's compositing step (passo 6): it was
        # hallucinating a slatted "bioclimatic" roof instead of the real
        # flat telo, presumably because that one angle didn't unambiguously
        # show the telo is a flat continuous panel. A few more angles of the
        # SAME real geometry (especially from underneath, looking straight
        # up at the telo) as extra reference images should leave it a lot
        # less room to guess wrong.
        import mathutils

        vl = bpy.context.view_layer
        bpy.context.view_layer.update()
        mins = [1e9, 1e9, 1e9]
        maxs = [-1e9, -1e9, -1e9]
        for obj in vl.objects:
            if obj.type != "MESH" or not obj.visible_get():
                continue
            mw = obj.matrix_world
            for v in obj.data.vertices:
                w = mw @ v.co
                for i in range(3):
                    mins[i] = min(mins[i], w[i])
                    maxs[i] = max(maxs[i], w[i])
        center = mathutils.Vector([(mins[i] + maxs[i]) / 2 for i in range(3)])
        size = max(maxs[i] - mins[i] for i in range(3))

        # KNOWN ISSUE (found 2026-09-27): the Tettuccio's real nervature
        # (the correct, intentional ~11.2cm-period ribs — see NOTES.md)
        # casts a strong dark shadow line at each rib specifically in the
        # strip nearest the guide, in both "laterale" and "dall_alto".
        # From there it's visually indistinguishable from a slatted/
        # louvered roof with real gaps, even though the surface is
        # continuous. This was confirmed NOT to be a camera-angle artifact
        # (a near-vertical "dall_alto" shows the same band) and NOT the
        # leftover `Tettuccio_Lato_Dx/Sx` piece (confirmed absent from
        # flag.blend). Likely a lighting/shading question for that one
        # strip — unresolved, needs Davide's read on how deep those ribs
        # really are on the physical product.
        view_preset = cfg.get("viewPreset", "isometrico")
        offsets = {
            # 3/4 elevated angle — the original, only preset before this.
            "isometrico": mathutils.Vector((1.1, -1.6, 0.9)),
            # End-on profile, pulled back to fit the full depth in frame:
            # shows the roof's cross-section (telo/tettuccio thickness,
            # guide profile) — makes "flat continuous panel, no gaps
            # between blades" obvious, unlike a real louvered roof's
            # profile. Tried "from below" first instead (more direct in
            # theory) but the telo's own sliding bars cast shadow bands on
            # its underside that read as slats just as easily — this side
            # profile is the one that actually disambiguates.
            "laterale": mathutils.Vector((3.4, -0.5, 0.25)),
            # Near-vertical top-down. A "steep-but-not-vertical" version was
            # tried first; going nearly straight down made no difference to
            # the artifact below, so this is kept simply as the cleanest,
            # least-distorted top view — see the nervature note above
            # `offsets` for the actual open issue.
            "dall_alto": mathutils.Vector((0.03, -0.05, 4.5)),
        }
        offset = offsets.get(view_preset, offsets["isometrico"])

        cam_data = bpy.data.cameras.new("DefaultCamera")
        cam_data.angle = math.radians(50)
        cam_obj = bpy.data.objects.new("DefaultCamera", cam_data)
        bpy.context.collection.objects.link(cam_obj)
        cam_obj.location = center + offset * size
        direction = center - cam_obj.location
        cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.camera = cam_obj
        bpy.context.scene.render.resolution_x = 2560
        bpy.context.scene.render.resolution_y = 1920

        # These renders exist purely to hand Gemini unambiguous geometry
        # (this function's own docstring: "not meant to look good, just
        # legible") — so a single hard sun light was actively wrong here:
        # on 2026-09-27 it was found to cast a shadow at every Tettuccio
        # rib that reads as a real gap between roof slats, i.e. it was
        # manufacturing the exact hallucination these renders are meant to
        # prevent. Switched to Workbench FLAT shading: no light, no
        # shadows, no shading model at all — just each material's base
        # colour, which is exactly "geometry information" with nothing to
        # misread as structure that isn't there.
        scene = bpy.context.scene
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "FLAT"
        scene.display.shading.color_type = "MATERIAL"
        scene.display.shading.show_shadows = False
        scene.display.shading.show_cavity = False
        scene.display.shading.background_type = "VIEWPORT"
        scene.display.shading.background_color = (0.15, 0.15, 0.15)

    if output_mode == "depth":
        render_depth_map(args.output)
    elif output_mode == "freestyle":
        render_freestyle(args.output)
    elif output_mode == "lineart":
        render_lineart_gp(args.output)
    elif output_mode == "lineart_structure":
        render_lineart_gp(args.output, object_filter=LINEART_STRUCTURE_PREFIXES)
    elif output_mode == "lineart_roof":
        render_lineart_gp(args.output, object_filter=LINEART_ROOF_PREFIXES)
    elif output_mode == "mask":
        render_mask(args.output)
    elif output_mode == "material_id":
        render_material_id(args.output)
    else:
        render_isolated(args.output, transparent=bool(camera_cfg))

    if args.save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=args.save_blend)


if __name__ == "__main__":
    main()
