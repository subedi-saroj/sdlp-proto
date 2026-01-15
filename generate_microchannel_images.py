"""
Generate 30 grayscale images with progressive microchannel features.

Images 1-10: Solid white patch (baseline)
Images 11-20: White patch with microchannels of varying thicknesses
  - 11.png: 5, 10, 15, 20, 25, 30, 35, 40, 45, 50 px channels
  - 12.png: 10, 15, 20, 25, 30, 35, 40, 45, 50 px channels
  - ...continuing until channels are progressively removed
  - 20.png: only 50 px channel
Images 21-30: Solid white patch (baseline)
"""

from PIL import Image
import os

# Image parameters
IMG_WIDTH = 3640
IMG_HEIGHT = 4320
PATCH_WIDTH = 3200
PATCH_HEIGHT = 2000

# Microchannel parameters
CHANNEL_WIDTHS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]  # in pixels
CHANNEL_SPACING = 100  # pixels between channel centerlines
NUM_CHANNELS = len(CHANNEL_WIDTHS)

# Calculate centered patch position
patch_x = (IMG_WIDTH - PATCH_WIDTH) // 2
patch_y = (IMG_HEIGHT - PATCH_HEIGHT) // 2

# Calculate vertical space needed for all channels
total_channel_height = CHANNEL_WIDTHS[-1] + CHANNEL_SPACING * (NUM_CHANNELS - 1)
channels_start_offset = (PATCH_HEIGHT - total_channel_height) // 2

# Create output directory
output_dir = "generated_images"
os.makedirs(output_dir, exist_ok=True)

print(f"Generating 30 images in '{output_dir}/'")
print(f"Image size: {IMG_WIDTH} × {IMG_HEIGHT}")
print(f"White patch: {PATCH_WIDTH} × {PATCH_HEIGHT} at ({patch_x}, {patch_y})")
print(f"Channel widths: {CHANNEL_WIDTHS} px")
print(f"Channel spacing: {CHANNEL_SPACING} px")
print()

for img_num in range(1, 31):
    # Create dark background
    img = Image.new('L', (IMG_WIDTH, IMG_HEIGHT), 0)
    pixels = img.load()
    
    # Fill the white patch
    for y in range(patch_y, patch_y + PATCH_HEIGHT):
        for x in range(patch_x, patch_x + PATCH_WIDTH):
            pixels[x, y] = 255
    
    # Add microchannels for images 11-20
    if 11 <= img_num <= 20:
        # Determine which channels to draw
        # Layer 11 draws channels 0-9 (all)
        # Layer 12 draws channels 1-9 (skip 5px)
        # Layer 13 draws channels 2-9 (skip 5px, 10px)
        # etc.
        start_channel_idx = img_num - 11
        
        for ch_idx in range(start_channel_idx, NUM_CHANNELS):
            channel_width = CHANNEL_WIDTHS[ch_idx]
            
            # Calculate vertical position (centered within patch)
            channel_y_in_patch = channels_start_offset + ch_idx * CHANNEL_SPACING
            channel_y_abs = patch_y + channel_y_in_patch
            
            # Draw horizontal channel (dark/black line)
            # The channel thickness is the channel_width in pixels
            for y in range(channel_y_abs, channel_y_abs + channel_width):
                if 0 <= y < IMG_HEIGHT:
                    for x in range(patch_x, patch_x + PATCH_WIDTH):
                        pixels[x, y] = 0  # Black (0) for microchannel
    
    # Save image
    filename = f"{img_num}.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath)
    
    if 1 <= img_num <= 10:
        print(f"✓ {filename} - Baseline layer (solid white patch)")
    elif 11 <= img_num <= 20:
        start_idx = img_num - 11
        channels_in_this_layer = [str(w) for w in CHANNEL_WIDTHS[start_idx:]]
        print(f"✓ {filename} - Channels: {', '.join(channels_in_this_layer)} px")
    else:
        print(f"✓ {filename} - Baseline layer (solid white patch)")

print(f"\n✅ All 30 images generated in '{output_dir}/'")
