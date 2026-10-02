"""
One-off experiment (2026-09-28, requested by Davide): test whether a real
ControlNet (Replicate, model jagilley/controlnet-scribble) can turn the
Freestyle line art from `render_freestyle` (generate_flag.py) into a
photorealistic pergola image, as a geometrically-constrained alternative to
the current Gemini-based passo 6 (which only ever treats reference images as
a soft suggestion, never a hard constraint — see 3d/NOTES.md).

This is deliberately NOT wired into pergolando-backend yet: it's a quick
local test of the ControlNet step in isolation (line art -> image), not the
full "compose onto the real photo" pipeline (that needs a second step —
inpainting or low-strength img2img on the real photo — not prototyped here).

Usage:
    python 3d/replicate_scribble_test.py path/to/freestyle_lineart.png "extra prompt words"

Reads the API token from 3d/.env (REPLICATE_API_TOKEN=..., gitignored, never
committed).
"""

import base64
import json
import sys
import time
import urllib.request
from pathlib import Path

import requests

MODEL_VERSION = "435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117"  # jagilley/controlnet-scribble

PROMPT = (
    "real outdoor aluminum pergola, retractable fabric roof, flat continuous "
    "light fabric canopy, no slats, no louvers, mounted to a house wall, "
    "modern garden patio, photorealistic photo, natural daylight, soft shadows"
)
NEGATIVE_EXTRA = (
    ", louvered roof, slatted roof, bioclimatic pergola, roller shutter, "
    "roller tube, string lights, fairy lights"
)


def load_env(env_path: Path) -> str:
    for line in env_path.read_text().splitlines():
        if line.startswith("REPLICATE_API_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit(f"REPLICATE_API_TOKEN not found in {env_path}")


def to_data_url(image_path: Path) -> str:
    data = image_path.read_bytes()
    if len(data) > 256_000:
        raise SystemExit(
            f"{image_path} is {len(data)} bytes, over Replicate's 256KB data-URL "
            "limit — downscale/flatten it first (see how flag_freestyle_ref_white.png "
            "was produced in this session's scratchpad)."
        )
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: replicate_scribble_test.py <lineart.png> [extra prompt words]")

    image_path = Path(sys.argv[1])
    extra_prompt = " ".join(sys.argv[2:])
    prompt = f"{PROMPT}, {extra_prompt}" if extra_prompt else PROMPT

    token = load_env(Path(__file__).parent / ".env")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "wait=59",
    }
    payload = {
        "version": MODEL_VERSION,
        "input": {
            "image": to_data_url(image_path),
            "prompt": prompt,
            "n_prompt": (
                "longbody, lowres, bad anatomy, bad hands, missing fingers, "
                "extra digit, fewer digits, cropped, worst quality, low quality"
                + NEGATIVE_EXTRA
            ),
            "num_samples": "1",
            "image_resolution": "768",
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
    print("Output URLs:", output_urls)

    out_dir = image_path.parent

    for i, url in enumerate(output_urls):
        dest = out_dir / f"replicate_scribble_out_{i}.png"
        urllib.request.urlretrieve(url, dest)
        print("Saved:", dest)


if __name__ == "__main__":
    main()
