"""
Generate 22 identical grayscale images with two tensile test specimens.

Canvas: 5400 rows × 3640 columns
Pixel size: 10.8 microns
Background: Black (0)
Specimens: White (255)
"""

from PIL import Image, ImageDraw
import os
import math

# Image parameters
IMG_WIDTH = 3640
IMG_HEIGHT = 5400
PIXEL_SIZE_MICRONS = 10.8

# Tensile specimen dimensions (in mm, converted to pixels)
def mm_to_px(mm):
    return int(mm * 1000 / PIXEL_SIZE_MICRONS)

TOTAL_LENGTH = mm_to_px(30)      # 2778 pixels
GAGE_WIDTH = mm_to_px(3.18)      # 294 pixels
GAGE_LENGTH = mm_to_px(4.88)     # 452 pixels
GRIP_LENGTH = mm_to_px(9)        # 833 pixels
GRIP_WIDTH = mm_to_px(9)         # 833 pixels

# Calculate transition length (remaining space after grips and gage)
TRANSITION_LENGTH = (TOTAL_LENGTH - 2 * GRIP_LENGTH - GAGE_LENGTH) // 2

print(f"Specimen dimensions (in pixels):")
print(f"  Total length: {TOTAL_LENGTH}")
print(f"  Grip: {GRIP_WIDTH} × {GRIP_LENGTH}")
print(f"  Gage: {GAGE_WIDTH} × {GAGE_LENGTH}")
print(f"  Transition: {TRANSITION_LENGTH} per side")
print()

def create_tensile_specimen_mask(width, height):
    """
    Create a binary mask for a tensile specimen.
    Returns a PIL Image with white specimen on black background.
    """
    img = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(img)
    
    # Calculate vertical positions
    y_start = (height - TOTAL_LENGTH) // 2
    
    y_grip1_start = y_start
    y_grip1_end = y_grip1_start + GRIP_LENGTH
    
    y_trans1_start = y_grip1_end
    y_trans1_end = y_trans1_start + TRANSITION_LENGTH
    
    y_gage_start = y_trans1_end
    y_gage_end = y_gage_start + GAGE_LENGTH
    
    y_trans2_start = y_gage_end
    y_trans2_end = y_trans2_start + TRANSITION_LENGTH
    
    y_grip2_start = y_trans2_end
    y_grip2_end = y_grip2_start + GRIP_LENGTH
    
    # Center horizontally
    x_center = width // 2
    
    # Draw first grip (top)
    grip1_left = x_center - GRIP_WIDTH // 2
    grip1_right = x_center + GRIP_WIDTH // 2
    draw.rectangle([grip1_left, y_grip1_start, grip1_right, y_grip1_end], fill=255)
    
    # Draw gage section (middle)
    gage_left = x_center - GAGE_WIDTH // 2
    gage_right = x_center + GAGE_WIDTH // 2
    draw.rectangle([gage_left, y_gage_start, gage_right, y_gage_end], fill=255)
    
    # Draw second grip (bottom)
    grip2_left = x_center - GRIP_WIDTH // 2
    grip2_right = x_center + GRIP_WIDTH // 2
    draw.rectangle([grip2_left, y_grip2_start, grip2_right, y_grip2_end], fill=255)
    
    # Draw transitions with smooth radius (arc-based fillet)
    # Calculate fillet radius based on available transition length
    width_diff = (GRIP_WIDTH - GAGE_WIDTH) / 2
    radius = min(TRANSITION_LENGTH, width_diff * 1.5)  # Use appropriate radius
    
    # Transition 1: from grip to gage (top transition)
    for i in range(TRANSITION_LENGTH):
        y = y_trans1_start + i
        # Use a circular/arc profile for smooth transition
        progress = i / TRANSITION_LENGTH
        # Smooth curve using cosine function for gradual transition
        curve_factor = (1 - math.cos(progress * math.pi)) / 2
        current_width = GRIP_WIDTH - (GRIP_WIDTH - GAGE_WIDTH) * curve_factor
        left = x_center - int(current_width // 2)
        right = x_center + int(current_width // 2)
        draw.line([(left, y), (right, y)], fill=255, width=1)
    
    # Transition 2: from gage to grip (bottom transition)
    for i in range(TRANSITION_LENGTH):
        y = y_trans2_start + i
        # Use a circular/arc profile for smooth transition
        progress = i / TRANSITION_LENGTH
        # Smooth curve using cosine function for gradual transition
        curve_factor = (1 - math.cos(progress * math.pi)) / 2
        current_width = GAGE_WIDTH + (GRIP_WIDTH - GAGE_WIDTH) * curve_factor
        left = x_center - int(current_width // 2)
        right = x_center + int(current_width // 2)
        draw.line([(left, y), (right, y)], fill=255, width=1)
    
    return img

# Create output directory
output_dir = "generated_images_tensile_scrolling"
os.makedirs(output_dir, exist_ok=True)

print(f"Generating 22 images in '{output_dir}/'")
print(f"Image size: {IMG_WIDTH} × {IMG_HEIGHT}")
print()

# Create specimen template (only need to generate once since all images are identical)
# The specimen template will be placed on the canvas
specimen_width = GRIP_WIDTH + 100  # Add some padding
specimen_height = TOTAL_LENGTH + 100

specimen_mask = create_tensile_specimen_mask(specimen_width, specimen_height)

# Generate 22 identical images
for img_num in range(1, 23):
    # Create black background
    img = Image.new('L', (IMG_WIDTH, IMG_HEIGHT), 0)
    
    # Position specimens: side by side in center with 300 px gap
    GAP = 300
    
    # Calculate total width needed for both specimens + gap
    total_width = 2 * specimen_width + GAP
    
    # Center this total width on the canvas
    start_x = (IMG_WIDTH - total_width) // 2
    
    # Left specimen position
    left_x = start_x
    left_y = (IMG_HEIGHT - specimen_height) // 2
    
    # Right specimen position (left specimen + its width + gap)
    right_x = left_x + specimen_width + GAP
    right_y = (IMG_HEIGHT - specimen_height) // 2
    
    # Paste left specimen
    img.paste(specimen_mask, (left_x, left_y), specimen_mask)
    
    # Paste right specimen
    img.paste(specimen_mask, (right_x, right_y), specimen_mask)
    
    # Save image
    filename = f"{img_num}.bmp"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath)
    
    print(f"✓ {filename} - Tensile specimens positioned")

print(f"\n✅ All 22 images generated in '{output_dir}/'")
print(f"\nSpecimen positions:")
print(f"  Left specimen: x={left_x}, y={left_y}")
print(f"  Right specimen: x={right_x}, y={right_y}")
