"""
Generate a grayscale BMP image (3640x4320) containing a centered 1600x1600 patch
with horizontal line features.

Pattern inside centered patch:
- Horizontal lines from patch-left to patch-right
- Center line starts at 50 µm thickness
- Symmetric lines above and below increase as 100 µm, 150 µm, 200 µm, ...
- 500 µm vertical gap between neighboring lines (edge-to-edge)
- Pattern continues as long as it fits in the 1600x1600 patch
- Vertical boundary lines are drawn on the left and right patch boundaries
"""

from pathlib import Path
from PIL import Image, ImageDraw

# Canvas resolution
IMG_WIDTH = 3640
IMG_HEIGHT = 4320

# Center patch dimensions
PATCH_WIDTH = 1600
PATCH_HEIGHT = 1600

# Projector pixel pitch
PIXEL_SIZE_UM = 10.8

# Geometry
BASE_LINE_THICKNESS_UM = 50
LINE_GAP_UM = 1000
BOUNDARY_LINE_THICKNESS_PX = 200

# Colors (8-bit grayscale)
BACKGROUND = 0
FEATURE = 255


def um_to_px(um: float) -> int:
    """Convert microns to nearest integer pixels (minimum 1 px)."""
    return max(1, int(round(um / PIXEL_SIZE_UM)))


def generate_grid_lines_image(output_path: str | Path = "generated_images/grid_lines.bmp") -> Path:
    """Generate and save the requested BMP image."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("L", (IMG_WIDTH, IMG_HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(img)

    # Center patch bounds
    patch_left = (IMG_WIDTH - PATCH_WIDTH) // 2
    patch_top = (IMG_HEIGHT - PATCH_HEIGHT) // 2
    patch_right = patch_left + PATCH_WIDTH - 1
    patch_bottom = patch_top + PATCH_HEIGHT - 1

    # Convert geometry to pixels
    t_base = um_to_px(BASE_LINE_THICKNESS_UM)
    gap = um_to_px(LINE_GAP_UM)

    # Center line (50 µm)
    cy = patch_top + PATCH_HEIGHT // 2
    center_top = cy - t_base // 2
    center_bottom = center_top + t_base - 1

    # Build symmetric lines with increasing thickness: 100, 150, 200, ... µm
    lines = [(center_top, center_bottom, BASE_LINE_THICKNESS_UM)]

    # Upward stack
    next_thickness_um = BASE_LINE_THICKNESS_UM * 2
    next_bottom = center_top - gap - 1
    while True:
        t_px = um_to_px(next_thickness_um)
        next_top = next_bottom - t_px + 1
        if next_top < patch_top:
            break
        lines.append((next_top, next_bottom, next_thickness_um))
        next_thickness_um += BASE_LINE_THICKNESS_UM
        next_bottom = next_top - gap - 1

    # Downward stack
    next_thickness_um = BASE_LINE_THICKNESS_UM * 2
    next_top = center_bottom + gap + 1
    while True:
        t_px = um_to_px(next_thickness_um)
        next_bottom = next_top + t_px - 1
        if next_bottom > patch_bottom:
            break
        lines.append((next_top, next_bottom, next_thickness_um))
        next_thickness_um += BASE_LINE_THICKNESS_UM
        next_top = next_bottom + gap + 1

    # Draw full-width horizontal lines across the centered patch
    for y_top, y_bottom, _ in sorted(lines, key=lambda item: item[0]):
        draw.rectangle([patch_left, y_top, patch_right, y_bottom], fill=FEATURE)

    # Add vertical boundary lines on left and right patch boundaries
    y_min = min(y_top for y_top, _, _ in lines)
    y_max = max(y_bottom for _, y_bottom, _ in lines)
    left_boundary_right = patch_left + BOUNDARY_LINE_THICKNESS_PX - 1
    right_boundary_left = patch_right - BOUNDARY_LINE_THICKNESS_PX + 1
    draw.rectangle([patch_left, y_min, left_boundary_right, y_max], fill=FEATURE)
    draw.rectangle([right_boundary_left, y_min, patch_right, y_max], fill=FEATURE)

    img.save(output_path, format="BMP")
    return output_path


if __name__ == "__main__":
    out = generate_grid_lines_image()
    print(f"Saved: {out.resolve()}")
    print(f"Canvas: {IMG_WIDTH}x{IMG_HEIGHT}, centered patch: {PATCH_WIDTH}x{PATCH_HEIGHT}")
    print(
        "Pattern: thicknesses 50, 100, 150, ... µm (as far as patch permits), "
        f"gap={um_to_px(LINE_GAP_UM)} px, boundary_thickness={BOUNDARY_LINE_THICKNESS_PX} px"
    )
