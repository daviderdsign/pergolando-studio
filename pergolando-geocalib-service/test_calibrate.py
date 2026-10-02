"""
One-off manual test of calibrate_placement() against a real photo (2026-09-28,
requested by Davide — verifying passo 3 end-to-end before touching passo 4/6b).
Not part of the service itself; run directly with this venv's python.
"""

import base64
import json
import sys

from server import calibrate_placement

photo_path = sys.argv[1] if len(sys.argv) > 1 else "../3d/test_photos/test.jpg"

with open(photo_path, "rb") as f:
    foto_b64 = base64.b64encode(f.read()).decode("ascii")

# Wall-floor junction, sampled from the actual pixel colors (transition from
# beige wall to the dark baseboard/shadow line) between the left lamp post
# and where the existing roof structure starts occluding the wall — the
# 650cm run Davide measured. Image is 640x480.
payload = {
    "fotoBase64": foto_b64,
    "punti": [
        {"xNorm": 100 / 640, "yNorm": 290 / 480},
        {"xNorm": 360 / 640, "yNorm": 276 / 480},
    ],
    "lineaLunghezzaCm": 650,
    "lRichiestaCm": 600,
    "pRichiestaCm": 350,
    "altezzaCm": 250,
}

result = calibrate_placement(payload)
print(json.dumps(result, indent=2))
