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
import json
import math
import os
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2
import numpy as np
import torch
from geocalib import GeoCalib

from resection import ResectionError, project, resect_points, rotmat

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
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(image_bytes)
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
    roll = float(gravity.roll.squeeze())
    pitch = float(gravity.pitch.squeeze())

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
            corner_world[0],
            corner_world[1],
            corner_world[2] - float(linea_controllo_lunghezza_cm),
        )
        points_world.append(controllo_world)
        points_px.append(controllo_px)

    yaw, t = resect_points(points_world, points_px, roll, pitch, fx, fy, cx, cy)

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
        if self.path != "/calibrate-placement":
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
            result = calibrate_placement(payload)
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
