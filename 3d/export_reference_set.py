"""
Exports the agreed-upon reference image set for the ComfyUI/ControlNet
compositing experiment (passo 6b) — NOT part of the live wizard flow, this
is an offline tool: `3d/generate_flag.py` writes each render to a random
temp file and hands it back as base64 to whatever called it (the wizard's
own live preview, or pergolando-blender-service), it never saves a named
file to disk. This script is what actually produces the fixed-name set
Davide asked for (session of 2026-09-30, confirmed again 2026-10-03):

    01_original.jpg   - the real site photo, copied in as-is
    02_lineart.png     - Grease Pencil Line Art (render_lineart_gp)
    03_depth.png        - depth map (render_depth_map)
    04_mask.png          - inpainting alpha mask (render_mask)
    05_material_id.png    - flat per-material-category pass (render_material_id)
    structure_lineart.png  - partial line art: montanti+travi+guide only
    roof_lineart.png         - partial line art: frangitratta+telo only
                              (both added 2026-10-04, Davide's own names —
                              no number prefix, unlike 01-05 above)

`02_lineart.png` switched from Blender's Freestyle renderer to a Grease
Pencil + Line Art modifier setup (2026-10-04, Davide's exact settings:
crease ~130deg, contour on, material boundary off, intersection on, loose
off, overlapping edges off, thin ~1-2px strokes, no fill) — render_freestyle
still exists in generate_flag.py (still used by the ortho_* elevation
views) but is no longer what this script calls for the lineart entries.

The "beauty" full-color render (render_colored) used to be exported too, as
05_beauty.png, with material_id bumped to 06 — dropped on request
(2026-10-04, not needed for this set) and material_id moved back down to
05. render_colored itself is untouched in generate_flag.py; this script
just no longer calls it.

Runs OUTSIDE Blender (plain Python + Pillow — this process just shells out
to Blender once per mode, same `--background --factory-startup flag.blend
--python generate_flag.py -- --config-json ... --output ...` invocation
pergolando-blender-service itself uses, see that file's server.js) so it
can also be run standalone from a terminal, independent of the live
backend/frontend.

Usage:
    py 3d/export_reference_set.py --config config.json \\
        --output-dir 3d/test_photos/test_02/reference_set \\
        [--original-photo 3d/test_photos/test_02/sfondo.jpg] \\
        [--camera camera.json]

`config.json` shape: same as generate_flag.py's own (L_cm/P_cm/H_cm/
deltaH_cm/fissaggio, optional nGuide — omit to auto-derive from L_cm, see
that script's derive_n_guide_from_l), plus optional colorRgb/fabricRgb/
frangitrattaRgb for the beauty pass. `camera.json` (optional): the same
rvec/tvec/fovDeg/imageWidthPx/imageHeightPx shape the wizard sends for a
real-photo match — when given, every mode shares this exact camera so the
whole set lines up pixel-for-pixel with `--original-photo`; when omitted,
each mode falls back to generate_flag.py's own default orbit camera
(standalone documentation shot, no photo to match).
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

SCRIPT_DIR = Path(__file__).parent
FLAG_BLEND_DEFAULT = SCRIPT_DIR / "flag.blend"
GENERATE_SCRIPT_DEFAULT = SCRIPT_DIR / "generate_flag.py"

# Same env var pergolando-blender-service/server.js uses for the production
# path — kept consistent so both only need to be set once per machine.
BLENDER_EXE_ENV = "BLENDER_EXECUTABLE_PATH"
BLENDER_EXE_FALLBACK_WIN = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

MODES = [
    ("02_lineart.png", "lineart"),
    ("03_depth.png", "depth"),
    ("04_mask.png", "mask"),
    ("05_material_id.png", "material_id"),
    ("structure_lineart.png", "lineart_structure"),
    ("roof_lineart.png", "lineart_roof"),
]


def resolve_blender_exe(explicit):
    if explicit:
        return explicit
    env = os.environ.get(BLENDER_EXE_ENV)
    if env:
        return env
    if os.name == "nt" and Path(BLENDER_EXE_FALLBACK_WIN).exists():
        return BLENDER_EXE_FALLBACK_WIN
    return "blender"


def run_blender(blender_exe, flag_blend, generate_script, config, output_path):
    cmd = [
        blender_exe,
        "--background",
        "--factory-startup",  # see pergolando-blender-service/server.js's own comment
        str(flag_blend),
        "--python",
        str(generate_script),
        "--",
        "--config-json",
        json.dumps(config),
        "--output",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0 or not output_path.exists():
        raise RuntimeError(
            f"Blender failed for {output_path.name} (exit {result.returncode}):\n"
            f"{result.stdout[-2000:]}\n{result.stderr[-2000:]}"
        )


def export_original_photo(photo_path, output_dir):
    img = Image.open(photo_path)
    img = ImageOps.exif_transpose(img)  # same correctness fix as the geocalib service
    img = img.convert("RGB")
    out_path = output_dir / "01_original.jpg"
    img.save(out_path, "JPEG", quality=95)
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True, help="path to a generate_flag.py-shaped JSON config")
    parser.add_argument("--output-dir", required=True, help="directory to write the numbered set into")
    parser.add_argument("--original-photo", help="real site photo, copied in as 01_original.jpg")
    parser.add_argument("--camera", help="path to a camera JSON (rvec/tvec/fovDeg/imageWidthPx/imageHeightPx)")
    parser.add_argument("--blender-exe", help=f"override Blender executable (else ${BLENDER_EXE_ENV} or a default path)")
    parser.add_argument("--flag-blend", default=str(FLAG_BLEND_DEFAULT))
    parser.add_argument("--generate-script", default=str(GENERATE_SCRIPT_DEFAULT))
    args = parser.parse_args()

    # Resolved to an ABSOLUTE path before ever reaching Blender: a relative
    # --output path reaches Blender's own scene.render.filepath, which (found
    # 2026-10-04) resolves relative paths against something other than this
    # process's cwd on Windows (a run with --output-dir "3d/test_photos/..."
    # landed at "C:\3d\test_photos\...", nowhere near the actual repo) — only
    # PIL's own file I/O (the 01_original.jpg copy) respected cwd correctly.
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.config, "r", encoding="utf-8") as f:
        base_config = json.load(f)

    camera_cfg = None
    if args.camera:
        with open(args.camera, "r", encoding="utf-8") as f:
            camera_cfg = json.load(f)

    blender_exe = resolve_blender_exe(args.blender_exe)
    flag_blend = str(Path(args.flag_blend).resolve())
    generate_script = str(Path(args.generate_script).resolve())

    produced = []

    if args.original_photo:
        path = export_original_photo(Path(args.original_photo), output_dir)
        produced.append(path)
        print(f"  01_original.jpg  <- {args.original_photo}")

    for filename, output_mode in MODES:
        config = {**base_config, "outputMode": output_mode}
        if camera_cfg:
            config["camera"] = camera_cfg
        out_path = output_dir / filename
        run_blender(blender_exe, flag_blend, generate_script, config, out_path)
        produced.append(out_path)
        print(f"  {filename}")

    print(f"\n{len(produced)} file in {output_dir}")


if __name__ == "__main__":
    sys.exit(main())
