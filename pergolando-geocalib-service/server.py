"""
Minimal, dependency-light HTTP wrapper around GeoCalib (single-image camera
calibration — focal length + gravity direction, no manual reference lines)
plus a 2-point resection (resection.py) that places a traced reference line
in that calibrated camera.

Kept as its own service for the same reason as pergolando-blender-service:
this pulls in torch/opencv/scipy, a real dependency weight that has no
business inside the main Node backend image. See pergolando-backend's
PerspectiveService for the caller.

Step 3 of the "compose on a real photo" pipeline (see 3d/NOTES.md /
CHANGELOG.md, Fase G) — the seller traces the wall-floor intersection line
exactly where the pergola will sit and confirms its real length, instead of
tapping where a not-yet-installed pergola's feet would land: a real, visible
edge is far more precise to trace than a point floating in empty space, and
a monocular 2-point resection is very sensitive to input noise (a handful of
pixels off on a floating tap becomes a large real-world error). Two earlier
schemes were tried and abandoned — solvePnP on 4 tapped feet (nonsensical
rear feet for wall-mounted units, which have none on the floor at all), then
2 tapped feet with the pergola's own width assumed as the scale reference
(still too imprecise in practice) — see 3d/NOTES.md and CHANGELOG.md for the
full history.
"""

import base64
import io
import json
import math
import os
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2
import numpy as np
import torch
from geocalib import GeoCalib
from PIL import Image, ImageOps

from resection import ResectionError, project, resect_points, rotmat, resect_with_vertical, resect_with_ground_direction, resect_independent_references

from auto_references import detect_references
from photo_directions import detect_six,calibrate_six
from architectural_lines import architectural_directions, orthogonal_focal, depth_family_from_prior

PORT = int(os.environ.get("PORT", 8090))
MAX_BODY_BYTES = 30_000_000  # a phone photo, base64-encoded

_model = None


def get_model():
    global _model
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model = GeoCalib().to(device)
    return _model


def calibrate_placement(payload):
    if payload.get("puntiFuga") is not None:
        return calibrate_six(payload)
    punti = payload.get("punti")
    if not isinstance(punti, list) or len(punti) != 2:
        raise ValueError("servono esattamente 2 punti (inizio/fine della riga)")

    foto_b64 = payload.get("fotoBase64")
    if not foto_b64:
        raise ValueError("fotoBase64 mancante")
    if foto_b64.startswith("data:"):
        foto_b64 = foto_b64.split(",", 1)[1]

    # The traced line's own real length — usually the pergola's width, but
    # not always (the seller may trace a more precisely measurable reference
    # instead), so this is never assumed to equal l_cm.
    linea_lunghezza_cm = float(payload["lineaLunghezzaCm"])
    l_cm = float(payload["lRichiestaCm"])
    p_cm = float(payload["pRichiestaCm"])
    h_cm = float(payload["altezzaCm"])

    image_bytes = base64.b64decode(foto_b64)

    # Downscale before handing the image to GeoCalib — a real phone photo
    # (e.g. 4096x3072, 12.6MP) makes GeoCalib's own internal preprocessing
    # (kornia's anti-alias gaussian blur before resize) allocate a buffer
    # proportional to the INPUT resolution, not its target working size —
    # ~384MB for a single intermediate on a 12.6MP image, which exhausted
    # available memory. Reproduced standalone outside the server as a clean
    # `RuntimeError: not enough memory` from kornia/torch's CPU allocator;
    # inside the long-running threaded server the same condition instead
    # surfaced as a native access violation (process death, no Python
    # traceback at all) — found 2026-10-03 testing against a real phone
    # photo for the first time (every earlier test used small, pre-shrunk
    # test images). Camera calibration itself needs no fine detail, so
    # resizing first is strictly a fix, not a quality tradeoff; `punti` are
    # normalized (xNorm/yNorm) and `fx/fy/cx/cy` are computed from whatever
    # size we actually load, so everything downstream (resection, the
    # reprojected tettoNormalizzato) stays self-consistent regardless of
    # which resolution this ends up being.
    MAX_DIMENSION_PX = 1600
    with Image.open(io.BytesIO(image_bytes)) as pil_image:
        pil_image = ImageOps.exif_transpose(pil_image)
        pil_image = pil_image.convert("RGB")
        if max(pil_image.size) > MAX_DIMENSION_PX:
            scale = MAX_DIMENSION_PX / max(pil_image.size)
            new_size = (round(pil_image.width * scale), round(pil_image.height * scale))
            pil_image = pil_image.resize(new_size, Image.LANCZOS)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            pil_image.save(f, format="JPEG", quality=92)
            analysis_rgb=np.asarray(pil_image).copy()
            tmp_path = f.name

    try:
        model = get_model()
        device = next(model.parameters()).device
        image = model.load_image(tmp_path).to(device)
        result = model.calibrate(image)
    finally:
        os.unlink(tmp_path)

    camera = result["camera"]
    gravity = result["gravity"]

    h_px, w_px = image.shape[-2:]
    h_px, w_px = int(h_px), int(w_px)
    fx = float(camera.f[..., 0].squeeze())
    fy = float(camera.f[..., 1].squeeze())
    cx, cy = w_px / 2.0, h_px / 2.0
    focal35=payload.get("focaleEquivalente35Mm")
    if focal35 is not None:
        focal35=float(focal35)
        if not np.isfinite(focal35) or not 5<=focal35<=1000:raise ValueError("focale EXIF non valida")
        exif_fx=focal35*math.hypot(w_px,h_px)/math.hypot(36,24)
        if .4<exif_fx/fx<2.5:
            fy=exif_fx*(fy/fx);fx=exif_fx
            print("EXIF_FOCAL",focal35,fx,flush=True)
    roll = float(gravity.roll.squeeze())
    pitch = float(gravity.pitch.squeeze())

    # Canonical left-to-right wall direction, independent of tap order.
    original_first_is_right = punti[0]["xNorm"] > punti[1]["xNorm"]
    punti = sorted(punti, key=lambda p: (p["xNorm"], p["yNorm"]))
    p1_px = (punti[0]["xNorm"] * w_px, punti[0]["yNorm"] * h_px)
    p2_px = (punti[1]["xNorm"] * w_px, punti[1]["yNorm"] * h_px)

    # Resection uses the LINE's own measured length, not l_cm: the two are
    # usually equal (the line traces the pergola's own edge) but don't have
    # to be, and the measured value is the more trustworthy one. The line's
    # midpoint is still treated as the pergola's own center for everything
    # below (roof reprojection) — the origin/orientation this yields is the
    # same either way, only the calibration scale differs. See
    # CalcolaProspettivaDto for the full reasoning.
    #
    # depth_z_cm=p_cm: the traced line is the wall-floor junction, which is
    # the pergola's REAR edge (world Z=P), not its front (Z=0) — the wizard
    # only offers wall/ceiling mounting today, so this is always the wall.
    # Treating it as the front pushed the whole pergola depth the wrong way,
    # into the wall instead of out into open space (real bug, seen live).
    corner_world = (-linea_lunghezza_cm / 2, 0.0, p_cm)
    wall_end_world = (linea_lunghezza_cm / 2, 0.0, p_cm)
    points_world = [corner_world, wall_end_world]
    points_px = [p1_px, p2_px]

    # Optional control line: one extra tapped point, paired with punti[0]
    # (the corner) as its own start — e.g. the terrace's own side edge,
    # perpendicular to the wall it's built against. A single line gives
    # exactly 4 equations for the 4 unknowns (yaw, tx, ty, tz): zero slack,
    # so any tap imprecision lands entirely in yaw, which reads to a seller
    # as "the perspective looks subtly wrong on one side" rather than an
    # obvious error. This over-determines the system instead, letting
    # least-squares average the error down — ~4.5x lower mean yaw error
    # under simulated tap noise, verified before wiring this in.
    punto_controllo = payload.get("puntoControllo")
    linea_controllo_lunghezza_cm = payload.get("lineaControlloLunghezzaCm")
    if punto_controllo and linea_controllo_lunghezza_cm:
        controllo_px = (punto_controllo["xNorm"] * w_px, punto_controllo["yNorm"] * h_px)
        controllo_world = (
            wall_end_world[0] if original_first_is_right else corner_world[0],
            corner_world[1],
            corner_world[2] - float(linea_controllo_lunghezza_cm),
        )
        points_world.append(controllo_world)
        points_px.append(controllo_px)

    yaw, t = resect_points(points_world, points_px, roll, pitch, fx, fy, cx, cy)

    print("POSE_BASE", yaw, t.tolist(), roll, pitch, flush=True)
    vertical = payload.get("puntiVerticali")
    vertical_height = payload.get("altezzaVerticaleCm")
    depth_line = payload.get("puntiProfondita")
    if vertical is not None or vertical_height is not None:
        if not isinstance(vertical, list) or len(vertical) != 2 or vertical_height is None:
            raise ValueError("servono due punti verticali e la misura del tratto")
        vertical_px = [(p["xNorm"]*w_px, p["yNorm"]*h_px) for p in vertical]
        if depth_line is None:
            yaw, t, roll, pitch = resect_with_vertical(points_world, points_px, vertical_px, float(vertical_height), p_cm, roll, pitch, fx, fy, cx, cy)

    print("POSE_VERTICAL", yaw, t.tolist(), roll, pitch, flush=True)
    calibration_warning = None
    depth_line = payload.get("puntiProfondita")
    if depth_line is not None:
        if not isinstance(depth_line, list) or len(depth_line) != 2:
            raise ValueError("servono due punti del bordo del pavimento")
        depth_line = sorted(depth_line, key=lambda p: (p["xNorm"], p["yNorm"]))
        depth_px = [(p["xNorm"]*w_px, p["yNorm"]*h_px) for p in depth_line]
        vp = [(p["xNorm"]*w_px, p["yNorm"]*h_px) for p in vertical] if vertical else None
        prior_pose = (yaw, t.copy(), roll, pitch)
        # GeoCalib can resize; all line detections and pixel references must match.
        analysis_rgb=cv2.resize(analysis_rgb,(w_px,h_px))
        families=architectural_directions(analysis_rgb,points_px[:2],vp,np.array([[fx,0,cx],[0,fy,cy],[0,0,1.]]),rotmat(roll,pitch,yaw))
        K=np.array([[fx,0,cx],[0,fy,cy],[0,0,1.]])
        measured_focal=orthogonal_focal(families,K)
        if measured_focal is not None:
            ratio=fy/fx;fx=measured_focal["fx"];fy=fx*ratio
            K=np.array([[fx,0,cx],[0,fy,cy],[0,0,1.]])
            yaw,t=resect_points(points_world,points_px,roll,pitch,fx,fy,cx,cy)
            prior_pose=(yaw,t.copy(),roll,pitch)
            print("ARCHITECTURAL_FOCAL",fx,measured_focal["relative_spread"],flush=True)
        if len(families)==2:
            rays=[np.linalg.inv(K)@family["vp"] for _,family in families]
            expected_depth=np.cross(rays[0],rays[1]);expected_depth/=np.linalg.norm(expected_depth)
            depth_family=depth_family_from_prior(analysis_rgb,K,expected_depth)
            if depth_family is not None:families.append((2,depth_family))
        constraints=[]
        for axis,family in families:
            ray=np.linalg.inv(K)@family["vp"];ray/=np.linalg.norm(ray)
            constraints.append((axis,ray))
        print("ARCHITECTURAL_LINES",[(axis,family["count"],family["angular_rms_deg"],family["vp"].tolist()) for axis,family in families],flush=True)
        debug_dir=os.environ.get("PERGOLANDO_CALIBRATION_DEBUG_DIR")
        if debug_dir:
            os.makedirs(debug_dir,exist_ok=True)
            diagnostic=cv2.cvtColor(analysis_rgb,cv2.COLOR_RGB2BGR)
            cv2.imwrite(os.path.join(debug_dir,"foto-originale.png"),diagnostic)
            for axis,family in families:
                color=(80,80,225) if axis==0 else (80,180,60) if axis==1 else (230,130,40)
                for a,b in family["segments"]:
                    cv2.line(diagnostic,tuple(np.round(a).astype(int)),tuple(np.round(b).astype(int)),color,3)
            cv2.imwrite(os.path.join(debug_dir,"linee-rilevate.png"),diagnostic)

        try:
            yaw, t, roll, pitch, focal_scale = resect_independent_references(points_world, points_px, depth_px, p_cm, roll, pitch, fx, fy, cx, cy, vp, float(vertical_height) if vertical_height else None, architectural=constraints)
            fx *= focal_scale
            fy *= focal_scale
            print("INDEPENDENT_REFERENCES focal_scale", focal_scale, flush=True)
        except ResectionError as err:
            yaw, t, roll, pitch = prior_pose
            print("Depth reference fallback:", str(err), flush=True)
            calibration_warning = "Il bordo laterale non concorda con la stima della foto. Uso la riga misurata" + ("") + ": controlla il volume prima del rendering."


    print("POSE_FINAL", yaw, t.tolist(), roll, pitch, "fx", fx, flush=True)
    R = rotmat(roll, pitch, yaw)
    rvec, _ = cv2.Rodrigues(R)

    half_l = l_cm / 2
    roof_object_points = [
        (-half_l, -h_cm, 0.0),
        (half_l, -h_cm, 0.0),
        (-half_l, -h_cm, p_cm),
        (half_l, -h_cm, p_cm),
    ]
    tetto_normalizzato = []
    for P in roof_object_points:
        u, v = project(P, roll, pitch, yaw, t, fx, fy, cx, cy)
        tetto_normalizzato.append({"xNorm": u / w_px, "yNorm": v / h_px})

    fov_deg = math.degrees(2 * math.atan(w_px / (2 * fx)))

    return {
        "avviso": calibration_warning,
        "rvec": rvec.flatten().tolist(),
        "tvec": t.tolist(),
        "fovDeg": fov_deg,
        "imageWidthPx": w_px,
        "imageHeightPx": h_px,
        "tettoNormalizzato": tetto_normalizzato,
    }


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status, body):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        self._send_json(404, {"error": "not-found"})

    def do_POST(self):
        if self.path not in ("/calibrate-placement", "/detect-references"):
            self._send_json(404, {"error": "not-found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY_BYTES:
            self._send_json(413, {"error": "payload-too-large"})
            return
        raw = self.rfile.read(length)

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid-json"})
            return

        try:
            result = detect_six(payload) if self.path == "/detect-references" else calibrate_placement(payload)
        except ResectionError as err:
            self._send_json(422, {"error": "resection-failed", "message": str(err)})
            return
        except (ValueError, KeyError) as err:
            self._send_json(400, {"error": "invalid-payload", "message": str(err)})
            return
        except Exception as err:  # noqa: BLE001 — last-resort 500, logged below
            print("Unexpected error handling /calibrate-placement:", repr(err))
            self._send_json(500, {"error": "internal-error"})
            return

        self._send_json(200, result)


if __name__ == "__main__":
    get_model()  # load weights at startup, not on the first request
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"pergolando-geocalib-service listening on :{PORT}")
    server.serve_forever()

