"""
Generate 34 grayscale images with progressive microchannel features.

Images 1-10: Solid white patch (baseline)
Images 11-24: White patch with microchannels of varying thicknesses
  - 11.bmp: 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70 px channels
  - 12.bmp: 25, 30, 35, 40, 45, 50, 55, 60, 65, 70 px channels
  - ...continuing until channels are progressively removed
  - 24.bmp: only 70 px channel
Images 25-34: Solid white patch (baseline)
"""

from PIL import Image
import os

# Image parameters
IMG_WIDTH = 3640
IMG_HEIGHT = 4320
PATCH_WIDTH = 1600
PATCH_HEIGHT = 2150

# Microchannel parameters
CHANNEL_WIDTHS = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]  # in pixels
CHANNEL_GAP = 110  # pixel gap between channels (not including channel width)
NUM_CHANNELS = len(CHANNEL_WIDTHS)

# Calculate centered patch position
patch_x = (IMG_WIDTH - PATCH_WIDTH) // 2
patch_y = (IMG_HEIGHT - PATCH_HEIGHT) // 2

# Calculate vertical space needed for all channels (sum of widths + gaps between them)
total_channel_height = sum(CHANNEL_WIDTHS) + CHANNEL_GAP * (NUM_CHANNELS - 1)
channels_start_offset = (PATCH_HEIGHT - total_channel_height) // 2

# Create output directory
output_dir = "generated_images"
os.makedirs(output_dir, exist_ok=True)

print(f"Generating 34 images in '{output_dir}/'")
print(f"Image size: {IMG_WIDTH} × {IMG_HEIGHT}")
print(f"White patch: {PATCH_WIDTH} × {PATCH_HEIGHT} at ({patch_x}, {patch_y})")
print(f"Channel widths: {CHANNEL_WIDTHS} px")
print(f"Gap between channels: {CHANNEL_GAP} px")
print()

for img_num in range(1, 35):
    # Create dark background
    img = Image.new('L', (IMG_WIDTH, IMG_HEIGHT), 0)
    pixels = img.load()
    
    # Fill the white patch
    for y in range(patch_y, patch_y + PATCH_HEIGHT):
        for x in range(patch_x, patch_x + PATCH_WIDTH):
            pixels[x, y] = 255
    
    # Add microchannels for images 11-24
    if 11 <= img_num <= 24:
        # Determine which channels to draw
        # 20px channel (idx 0): appears in layers 11-14 (4 layers)
        # 25px channel (idx 1): appears in layers 11-15 (5 layers)
        # 30px channel (idx 2): appears in layers 11-16 (6 layers)
        # etc.
        start_channel_idx = max(0, img_num - 14)
        
        for ch_idx in range(start_channel_idx, NUM_CHANNELS):
            channel_width = CHANNEL_WIDTHS[ch_idx]
            
            # Calculate vertical position (centered within patch)
            # Each channel starts after the previous channel + its gap
            channel_y_in_patch = channels_start_offset
            for i in range(ch_idx):
                channel_y_in_patch += CHANNEL_WIDTHS[i] + CHANNEL_GAP
            
            channel_y_abs = patch_y + channel_y_in_patch
            
            # Draw horizontal channel (dark/black line)
            # The channel thickness is the channel_width in pixels
            for y in range(channel_y_abs, channel_y_abs + channel_width):
                if 0 <= y < IMG_HEIGHT:
                    for x in range(patch_x, patch_x + PATCH_WIDTH):
                        pixels[x, y] = 0  # Black (0) for microchannel
    
    # Save image
    filename = f"{img_num}.bmp"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath)
    
    if 1 <= img_num <= 10:
        print(f"✓ {filename} - Baseline layer (solid white patch)")
    elif 11 <= img_num <= 24:
        start_idx = img_num - 11
        channels_in_this_layer = [str(w) for w in CHANNEL_WIDTHS[start_idx:]]
        print(f"✓ {filename} - Channels: {', '.join(channels_in_this_layer)} px")
    else:
        print(f"✓ {filename} - Baseline layer (solid white patch)")

print(f"\n✅ All 34 images generated in '{output_dir}/'")
