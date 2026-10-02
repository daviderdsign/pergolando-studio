"""
Second Replicate experiment (2026-09-28): compose the Freestyle-conditioned
pergola directly onto Davide's real terrace photo, using Flux inpainting +
ControlNet (fermatresearch/flux-controlnet-inpaint) instead of Gemini.

Inputs (all produced earlier this session, see 3d/NOTES.md):
 - 3d/test_photos/test.jpg: the real photo.
 - 3d/test_photos/inpaint_mask.png: filled silhouette mask (from
   render_isolated at the calibrated PnP camera pose), dilated slightly.
 - 3d/test_photos/control_lineart.png: Freestyle line art at the SAME
   calibrated camera pose, flattened onto white (canny-like).

Reads REPLICATE_API_TOKEN from 3d/.env.
"""

import base64
import json
import sys
import time
import urllib.request
from pathlib import Path

import requests

MODEL_VERSION_URL = "https://api.replicate.com/v1/models/fermatresearch/flux-controlnet-inpaint"

PROMPT = (
    "white aluminum pergola with retractable fabric roof. The roof is a "
    "SINGLE flat continuous solid white fabric panel, completely smooth, "
    "no ribs, no stripes, no corrugation, NOT a rolled-up awning, NOT a "
    "striped shutter, NOT roof tiles. Two straight vertical white aluminum "
    "support legs/posts clearly visible, reaching all the way down to the "
    "floor. Mounted to the house wall. Overcast cloudy day, soft diffuse "
    "light, no harsh sun, gentle soft shadows on the floor. Cozy outdoor "
    "furniture underneath (a small table and chairs). Photorealistic photo, "
    "matching the existing scene lighting."
)
NEGATIVE_HINT = ""  # this model has no negative_prompt field


def load_token(env_path: Path) -> str:
    for line in env_path.read_text().splitlines():
        if line.startswith("REPLICATE_API_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit(f"REPLICATE_API_TOKEN not found in {env_path}")


def to_data_url(path: Path, mime: str) -> str:
    data = path.read_bytes()
    if len(data) > 256_000:
        raise SystemExit(f"{path} is {len(data)} bytes, over the 256KB data-URL limit")
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def main():
    base = Path(__file__).parent / "test_photos"
    token = load_token(Path(__file__).parent / ".env")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "wait=59",
    }

    # Resolve the model's latest version id first (no owner/model shorthand
    # for non-official models, per Replicate's HTTP API docs).
    model_resp = requests.get(MODEL_VERSION_URL, headers=headers, timeout=30)
    model_resp.raise_for_status()
    version_id = model_resp.json()["latest_version"]["id"]
    print("Using version:", version_id)

    payload = {
        "version": version_id,
        "input": {
            "image": to_data_url(base / "test.jpg", "image/jpeg"),
            "mask": to_data_url(base / "inpaint_mask.png", "image/png"),
            "control_image": to_data_url(base / "control_lineart.png", "image/png"),
            "prompt": PROMPT,
            "strength": 0.95,
            "conditioning_scale": 0.65,
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
            "enable_hyper_flux_8_step": False,
            "output_format": "png",
        },
    }

    print("Submitting prediction...")
    resp = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers=headers,
        data=json.dumps(payload),
        timeout=70,
    )
    if not resp.ok:
        print(resp.status_code, resp.text)
    resp.raise_for_status()
    prediction = resp.json()

    get_url = prediction["urls"]["get"]
    while prediction["status"] not in ("succeeded", "failed", "canceled"):
        print(f"status: {prediction['status']}, polling...")
        time.sleep(3)
        prediction = requests.get(get_url, headers=headers, timeout=30).json()

    if prediction["status"] != "succeeded":
        print(json.dumps(prediction, indent=2))
        raise SystemExit(f"prediction {prediction['status']}")

    output_urls = prediction["output"]
    if isinstance(output_urls, str):
        output_urls = [output_urls]
    print("Output URLs:", output_urls)

    suffix = sys.argv[1] if len(sys.argv) > 1 else "0"
    for i, url in enumerate(output_urls):
        dest = base / f"inpaint_out_{suffix}_{i}.png"
        urllib.request.urlretrieve(url, dest)
        print("Saved:", dest)


if __name__ == "__main__":
    main()
