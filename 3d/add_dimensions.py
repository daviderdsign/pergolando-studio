"""
Post-process a `generate_flag.py --outputMode ortho_*` render: overlays
technical-drawing dimension lines (extension lines, arrows, cm labels) using
the projection info saved in the `<output>.json` sidecar.

Pure PIL, no Blender needed — orthographic projection is a simple affine
transform (world meters -> pixels), computed directly from `ortho_scale`,
`right_axis`/`up_axis` and `center_world` in the sidecar. Dimension lines
snap to the render's own true bbox extent (`bbox_min`/`bbox_max`), not to
nominal L_cm/P_cm/H_cm alone, which can be a few cm off from any single
piece's real geometry.

Usage:
    python 3d/add_dimensions.py 3d/test_photos/ortho_top.png
    (reads 3d/test_photos/ortho_top.png.json, writes
     3d/test_photos/ortho_top_quotato.png)
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

EXT_LINE_GAP = 8  # px gap between geometry and the start of an extension line
EXT_LINE_OVERSHOOT = 10  # px the extension line continues past the dim line
ARROW_SIZE = 9
DIM_COLOR = (200, 30, 30)
LINE_WIDTH = 2


def load_font(size):
    for candidate in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_projector(meta, margin=0):
    right = meta["right_axis"]
    up = meta["up_axis"]
    center = meta["center_world"]
    world_per_px = meta["ortho_scale"] / meta["resolution_x"]
    cx, cy = meta["resolution_x"] / 2 + margin, meta["resolution_y"] / 2 + margin

    def project(p_world):
        d = [p_world[i] - center[i] for i in range(3)]
        right_comp = sum(d[i] * right[i] for i in range(3))
        up_comp = sum(d[i] * up[i] for i in range(3))
        return (cx + right_comp / world_per_px, cy - up_comp / world_per_px)

    return project


def draw_arrow_head(draw, tip, direction, color):
    """`direction` is the unit vector the arrow points along (away from the
    dimension line's far end, i.e. pointing outward)."""
    dx, dy = direction
    # two wings at +-25 degrees, using perpendicular for a simple triangle
    px, py = -dy, dx
    wing = ARROW_SIZE
    spread = ARROW_SIZE * 0.4
    p1 = (tip[0] - dx * wing + px * spread, tip[1] - dy * wing + py * spread)
    p2 = (tip[0] - dx * wing - px * spread, tip[1] - dy * wing - py * spread)
    draw.polygon([tip, p1, p2], fill=color)


def draw_linear_dimension(draw, font, p1_geom, p2_geom, offset, label, horizontal):
    """p1_geom/p2_geom: the two points on the geometry being measured
    (pixels). offset: perpendicular distance (px, signed) to push the
    dimension line away from the geometry. `horizontal`: True if the
    dimension line itself should run left-right (offset applied vertically),
    False if it runs top-bottom (offset applied horizontally)."""
    if horizontal:
        y_dim = p1_geom[1] + offset
        ext1_start = (p1_geom[0], p1_geom[1] + (EXT_LINE_GAP if offset > 0 else -EXT_LINE_GAP))
        ext1_end = (p1_geom[0], y_dim + (EXT_LINE_OVERSHOOT if offset > 0 else -EXT_LINE_OVERSHOOT))
        ext2_start = (p2_geom[0], p2_geom[1] + (EXT_LINE_GAP if offset > 0 else -EXT_LINE_GAP))
        ext2_end = (p2_geom[0], y_dim + (EXT_LINE_OVERSHOOT if offset > 0 else -EXT_LINE_OVERSHOOT))
        dim_p1 = (p1_geom[0], y_dim)
        dim_p2 = (p2_geom[0], y_dim)
        dir1 = (-1.0, 0.0) if dim_p1[0] < dim_p2[0] else (1.0, 0.0)
        dir2 = (1.0, 0.0) if dim_p1[0] < dim_p2[0] else (-1.0, 0.0)
    else:
        x_dim = p1_geom[0] + offset
        ext1_start = (p1_geom[0] + (EXT_LINE_GAP if offset > 0 else -EXT_LINE_GAP), p1_geom[1])
        ext1_end = (x_dim + (EXT_LINE_OVERSHOOT if offset > 0 else -EXT_LINE_OVERSHOOT), p1_geom[1])
        ext2_start = (p2_geom[0] + (EXT_LINE_GAP if offset > 0 else -EXT_LINE_GAP), p2_geom[1])
        ext2_end = (x_dim + (EXT_LINE_OVERSHOOT if offset > 0 else -EXT_LINE_OVERSHOOT), p2_geom[1])
        dim_p1 = (x_dim, p1_geom[1])
        dim_p2 = (x_dim, p2_geom[1])
        dir1 = (0.0, -1.0) if dim_p1[1] < dim_p2[1] else (0.0, 1.0)
        dir2 = (0.0, 1.0) if dim_p1[1] < dim_p2[1] else (0.0, -1.0)

    draw.line([ext1_start, ext1_end], fill=DIM_COLOR, width=1)
    draw.line([ext2_start, ext2_end], fill=DIM_COLOR, width=1)
    draw.line([dim_p1, dim_p2], fill=DIM_COLOR, width=LINE_WIDTH)
    draw_arrow_head(draw, dim_p1, dir1, DIM_COLOR)
    draw_arrow_head(draw, dim_p2, dir2, DIM_COLOR)

    mid = ((dim_p1[0] + dim_p2[0]) / 2, (dim_p1[1] + dim_p2[1]) / 2)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 4
    if horizontal:
        text_pos = (mid[0] - tw / 2, mid[1] - th - pad * 2)
    else:
        text_pos = (mid[0] + pad * 2, mid[1] - th / 2)
    draw.rectangle(
        [text_pos[0] - pad, text_pos[1] - pad, text_pos[0] + tw + pad, text_pos[1] + th + pad],
        fill=(255, 255, 255),
    )
    draw.text(text_pos, label, fill=DIM_COLOR, font=font)


MARGIN = 140  # px of extra white canvas on every side, for dim lines/labels


def annotate(png_path: Path):
    meta = json.loads(Path(str(png_path) + ".json").read_text())
    project = make_projector(meta, margin=MARGIN)

    im = Image.open(png_path).convert("RGBA")
    canvas_size = (im.width + 2 * MARGIN, im.height + 2 * MARGIN)
    bg = Image.new("RGB", canvas_size, (255, 255, 255))
    bg.paste(im, (MARGIN, MARGIN), mask=im.split()[3])
    draw = ImageDraw.Draw(bg)
    font = load_font(22)

    bmin, bmax = meta["bbox_min"], meta["bbox_max"]
    view = meta["view"]

    if view == "top":
        # width (L): along X, offset below (front side, larger image-Y)
        p1 = project((bmin[0], bmin[1], bmin[2]))
        p2 = project((bmax[0], bmin[1], bmin[2]))
        # actual pixel Y for front edge varies by X in theory (it doesn't,
        # orthographic top view: front edge is a straight line at Y=bmin[1])
        draw_linear_dimension(
            draw, font, p1, p2, offset=40, label=f"L = {meta['L_cm']:.0f} cm", horizontal=True
        )
        # depth (SP): along Y, offset to the right
        p1 = project((bmax[0], bmin[1], bmin[2]))
        p2 = project((bmax[0], bmax[1], bmin[2]))
        draw_linear_dimension(
            draw, font, p1, p2, offset=40, label=f"SP = {meta['P_cm']:.0f} cm", horizontal=False
        )

    elif view == "front":
        p1 = project((bmin[0], bmin[1], bmin[2]))
        p2 = project((bmax[0], bmin[1], bmin[2]))
        draw_linear_dimension(
            draw, font, p1, p2, offset=40, label=f"L = {meta['L_cm']:.0f} cm", horizontal=True
        )
        p1 = project((bmax[0], bmin[1], bmin[2]))
        p2 = project((bmax[0], bmin[1], bmax[2]))
        draw_linear_dimension(
            draw, font, p1, p2, offset=40, label=f"P = {meta['H_cm']:.0f} cm", horizontal=False
        )

    elif view == "side":
        p1 = project((bmin[0], bmin[1], bmin[2]))
        p2 = project((bmin[0], bmax[1], bmin[2]))
        draw_linear_dimension(
            draw, font, p1, p2, offset=40, label=f"SP = {meta['P_cm']:.0f} cm", horizontal=True
        )
        # front height, at the front (left, min Y)
        p1 = project((bmin[0], bmin[1], bmin[2]))
        p2 = project((bmin[0], bmin[1], bmax[2]))
        draw_linear_dimension(
            draw, font, p1, p2, offset=-40, label=f"P = {meta['H_cm']:.0f} cm", horizontal=False
        )
        # rear height, at the wall (right, max Y)
        rear_h = meta["H_cm"] + meta["deltaH_cm"]
        p1 = project((bmin[0], bmax[1], bmin[2]))
        p2 = project((bmin[0], bmax[1], bmax[2]))
        draw_linear_dimension(
            draw, font, p1, p2, offset=40, label=f"H = {rear_h:.0f} cm", horizontal=False
        )

    out_path = png_path.with_name(png_path.stem + "_quotato.png")
    bg.save(out_path)
    print("Saved:", out_path)


if __name__ == "__main__":
    annotate(Path(sys.argv[1]))
