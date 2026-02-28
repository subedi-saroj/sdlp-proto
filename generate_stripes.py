from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog


def generate_left_right_stripes(filepath):
    # Constants
    FULL_WIDTH = 3640 #3640 when 200 overlaps # width of pre-processed grayscale image #2880
    FULL_HEIGHT = 4320 # height of pre-processed grayscale image

    GS_STRIP_WIDTH = 1920 # width of each strip
    OVERLAP = GS_STRIP_WIDTH * 2 - FULL_WIDTH

    # Step 0: Load the grayscale image
    full_grayscale_image = Image.open(filepath)

    # Ensure grayscale for predictable overlap behavior
    full_grayscale_image = full_grayscale_image.convert('L')

    # Basic size check to match processing assumptions
    if full_grayscale_image.size != (FULL_WIDTH, FULL_HEIGHT):
        raise ValueError(
            f"Selected image must be {FULL_WIDTH}x{FULL_HEIGHT}. "
            f"Got {full_grayscale_image.size[0]}x{full_grayscale_image.size[1]}."
        )

    # Step 1: Split the image into strips
    # Left strip takes first GS_STRIP_WIDTH columns (0 to GS_STRIP_WIDTH-1)
    left_strip = Image.new('L', (GS_STRIP_WIDTH, FULL_HEIGHT), 0)  # 'L' mode ensures 8-bit grayscale
    left_strip.paste(full_grayscale_image.crop((0, 0, GS_STRIP_WIDTH, FULL_HEIGHT)), (0, 0))

    # Right strip takes last GS_STRIP_WIDTH columns (FULL_WIDTH - GS_STRIP_WIDTH to FULL_WIDTH-1)
    right_strip = Image.new('L', (GS_STRIP_WIDTH, FULL_HEIGHT), 0)  # 'L' mode ensures 8-bit grayscale
    right_strip.paste(full_grayscale_image.crop((FULL_WIDTH - GS_STRIP_WIDTH, 0, FULL_WIDTH, FULL_HEIGHT)), (0, 0))

    # Step 2: Scale the strips over the overlap

    def scale_overlap(strip:Image.Image, side:str) -> Image.Image:
        MIN_INTENSITY = 30  # Minimum intensity to avoid non-linearity at low values
        for y in range(0, FULL_HEIGHT):
            for x in range(0, OVERLAP):
                # Linear overlap scaling functions
                if side == 'L':
                    # Left strip: overlap is at the right edge (columns GS_STRIP_WIDTH-OVERLAP to GS_STRIP_WIDTH-1)
                    pixel_x = GS_STRIP_WIDTH - OVERLAP + x
                    factor = (OVERLAP - x) / OVERLAP
                elif side == 'R':
                    # Right strip: overlap is at the left edge (columns 0 to OVERLAP-1)
                    pixel_x = x
                    factor = x / OVERLAP
                else:
                    raise ValueError("Invalid side. Use 'L' or 'R'.")

                pixel_y = y
                val = strip.getpixel((pixel_x, pixel_y))

                if val > 0:
                    if val <= MIN_INTENSITY:
                        scaled_val = val
                    else:
                        scaled_val = int(MIN_INTENSITY + (val - MIN_INTENSITY) * factor)
                    strip.putpixel((pixel_x, pixel_y), scaled_val)
        return strip

    left_strip = scale_overlap(left_strip, 'L')
    right_strip = scale_overlap(right_strip, 'R')

    # If you do NOT want overlap scaling, comment these two lines above.

    # Save strips after overlap scaling for verification
    base_dir = os.path.dirname(filepath)
    out_dir = os.path.join(base_dir, "generated_images")
    os.makedirs(out_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(filepath))[0]
    left_path = os.path.join(out_dir, f"{base_name}_left_strip_after_overlap.bmp")
    right_path = os.path.join(out_dir, f"{base_name}_right_strip_after_overlap.bmp")

    left_strip.save(left_path)
    right_strip.save(right_path)

    return left_path, right_path


if __name__ == "__main__":
    # Prompt user to select one image file
    root = tk.Tk()
    root.withdraw()
    image_path = filedialog.askopenfilename(
        title="Select a grayscale image",
        filetypes=[("Bitmap files", "*.bmp"), ("All files", "*.*")]
    )

    if not image_path:
        raise RuntimeError("No image selected!")

    left_out, right_out = generate_left_right_stripes(image_path)
    print(f"Saved left strip: {left_out}")
    print(f"Saved right strip: {right_out}")