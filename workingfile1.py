from lux4600 import *
from lux4600.projector import Projector
from lux4600.img import Strip
from lux4600.seq import Sequencer
from PIL import Image
import time, sys, os

'''
Author: David Alexander
Date: 2025-12-05
Last updated: 2025-12-16

This script demonstrates 4-bit weighted grayscale printing with separate left/right bitplane uploads.

The overall process is as follows:
    0. Before running this script, create an image 2880x3240 pixels in size.
        - FULL_WIDTH = 2880
        - FULL_HEIGHT = 3240
       This can be a grayscale image or a color image. The color image will be converted to grayscale.
    
    1. The image is split into two grayscale strips of 1920 pixels wide and 3240 rows tall. 
        - GS_STRIP_WIDTH = 1920
        - GS_STRIP_HEIGHT = FULL_HEIGHT
       There will be an overlap of 960 pixels between the strips.
        - OVERLAP = 960

    2. The two grayscale strips are "scaled" over the overlap, so that the sum of the two overlap
        regions is equal to the original value. 
    
    3. Each strip is converted to 4 weighted bitplanes (binary 1/2/4/8 representation).
        - BITPLANES = 4 (16 grayscale levels)

    4. Left bitplanes are uploaded to inums 0, 1699, 3398, 5097
       Right bitplanes are uploaded to inums 6876, 8575, 10274, 11973
    
    5. Sequencer loads from these inums to display left and right simultaneously.
    
    6. The projector and axes are started simultaneously for a single layer.
    7. The projector and X-Y axes are stopped after the layer is complete. Z axes increments.
        - LAYER_HEIGHT = 0.4 (mm)

    --> Repeat for some number of layers.
        - LAYERS = 6
'''
def preprocess_grayscale_image(filepath):
    # Constants
    FULL_WIDTH = 2880 # width of pre-processed grayscale image
    FULL_HEIGHT = 3240 # height of pre-processed grayscale image

    GS_STRIP_WIDTH = 1920 # width of each strip
    OVERLAP = GS_STRIP_WIDTH * 2 - FULL_WIDTH

    BITPLANES = 4 # number of weighted bitplanes (4 -> 16 levels)

    # Step 0: Load the grayscale image
    full_grayscale_image = Image.open(filepath)

    # Step 1: Split the image into strips
    left_strip = Image.new('L', (GS_STRIP_WIDTH, FULL_HEIGHT), 0)  # 'L' mode ensures 8-bit grayscale
    left_strip.paste(full_grayscale_image.crop((0, 0, GS_STRIP_WIDTH, FULL_HEIGHT)), (0, 0))

    right_strip = Image.new('L', (GS_STRIP_WIDTH, FULL_HEIGHT), 0)  # 'L' mode ensures 8-bit grayscale
    right_strip.paste(full_grayscale_image.crop((GS_STRIP_WIDTH//2, 0, FULL_WIDTH, FULL_HEIGHT)), (0, 0))

    # Step 2: Scale the strips over the overlap

    def scale_overlap(strip:Image.Image, side:str) -> Image.Image:
        for y in range(0, FULL_HEIGHT):

            # Note: this indexing only works because the overlap is 960 pixels wide
            # and the strips are 1920 pixels wide. If the overlap is changed, this
            # indexing will need to be changed as well.
            for x in range(0, OVERLAP):
                
                # Linear overlap scaling functions
                if side == 'L':
                    func = lambda x, current: int((current / OVERLAP) * (OVERLAP - x))
                    pixel_x = x + OVERLAP
                elif side == 'R':
                    func = lambda x, current: int((current / OVERLAP) * x)
                    pixel_x = x
                else:
                    raise ValueError("Invalid side. Use 'L' or 'R'.")

                pixel_y = y # for clarity

                val = strip.getpixel((pixel_x, pixel_y)) # New grayscale value for left strip
                
                if val > 0:
                    strip.putpixel((pixel_x, pixel_y), func(x, val))
        return strip

    left_strip = scale_overlap(left_strip, 'L')
    right_strip = scale_overlap(right_strip, 'R')

    # Save strips after overlap scaling for verification
    left_strip.save("bitplanes/left_strip_after_overlap.bmp")
    right_strip.save("bitplanes/right_strip_after_overlap.bmp")

    # Step 3: Generate weighted bitplanes (binary 1/2/4/8) instead of equal-duration thresholds
    def bitplane_images(img: Image.Image, bits: int) -> list[Image.Image]:
        gray = img.convert('L')
        scaled = gray.point(lambda p: p >> 4)  # Scale 0-255 to 0-15 for 4 bits
        planes = []
        for bit in range(bits):  # bit 0 = LSB (weight 1), bit 3 = MSB (weight 8)
            planes.append(scaled.point(lambda p, b=bit: 255 if ((p >> b) & 1) else 0))
        return planes

    left_planes = bitplane_images(left_strip, BITPLANES)
    right_planes = bitplane_images(right_strip, BITPLANES)

    # Return both left and right plane lists (NOT stitched together)
    return (left_planes, right_planes)

# Step 4: Initialize the projector
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)

projector.check_connection()

# Constants for inum spacing
STEP_INUM = 1699 #1699  # Changed from 1699 for simpler testing; revert to 1699 if needed
BITPLANES = 4

# Step 5: Create sequencer for 4-bit weighted bitplanes
sequencer = seq.Sequencer(r"test\test-seq\seq_scroll_4bit_gray_visitech_for.txt", 1440)

# Step 6: Start the projector and axes simultaneously for a single layer
# import axes
# from zaber_motion import Units, wait_all

input("Press Enter to start the projector and axes...")

# CRITICAL FIX: Set INUM_SIZE to 1080 (DMD height) ONCE before uploads
print("\nSetting INUM_SIZE to 1080 (DMD height)...")
projector.send(records.SetInumSize(1080).bytes())
print("✅ INUM_SIZE set\n")

# zaber_axes = axes.ZaberAxes("COM3")
# zaber_axes.home()

# Z_START = 100 # mm, initial z position
# X_START = 60 # mm, initial x position
# Y_START = 50 # mm, initial y position

# zaber_axes.ZAxis.move_absolute(Z_START, Units.LENGTH_MILLIMETRES)
# zaber_axes.XAxis.move_absolute(X_START, Units.LENGTH_MILLIMETRES)
# zaber_axes.YAxis.move_absolute(Y_START, Units.LENGTH_MILLIMETRES)

LAYER_HEIGHT = 0.4
LAYERS = 6

# Create output directory for bitplane verification
os.makedirs("bitplanes", exist_ok=True)

# Set LED driver amplitude to 1500 (0 TO 4095)
# Ensure water cooling system is functional if amplitude > 100
projector.send(records.SetLedDriverAmplitude(0, 1500).bytes())

#
# THESE ARE CAREFULLY CALIBRATED VALUES
# TODO: verify with celestron handheld microscope from the natural resources library
#
SCROLLING_VELOCITY = 1.8 # mm/s
SCROLLING_DIST = 23.2 # mm
LATERAL_INCREMENT = 10 # mm
#


for i in range(LAYERS):

    print(f"Layer {i+1} out of {LAYERS}")

    left_planes, right_planes = preprocess_grayscale_image(r"test\test-dogbone\2880x3240_dogbone_HORZ.bmp")
    
    # Upload left bitplanes to inums 0, 1699, 3398, 5097
    print("Uploading left bitplanes...")
    for bit in range(BITPLANES):
        inum = bit * (STEP_INUM)
        strip = Strip(left_planes[bit], inum)
        strip.save(f"bitplanes/left_bitplane_{bit}_inum_{inum}.bmp")
        projector.send_strip(strip)
    
    # Upload right bitplanes to inums 6876, 8575, 10274, 11973 (offset by 4 * STEP_INUM)
    print("Uploading right bitplanes...")
    for bit in range(BITPLANES):
        inum = (BITPLANES + bit) * STEP_INUM
        strip = Strip(right_planes[bit], inum)
        strip.save(f"bitplanes/right_bitplane_{bit}_inum_{inum}.bmp")
        projector.send_strip(strip)

    projector.send(records.SetLedDriverAmplitude(0, 1500).bytes())  # Ensure LED amplitude is set

    # zaber_axes.XAxis.move_absolute(X_START, Units.LENGTH_MILLIMETRES)

    # projector.send_sequencer(sequencers[0])  # Alternate between left and right sequencers
    projector.send_sequencer(sequencer)
    projector.start_sequencer()

    # zaber_axes.scroll(SCROLLING_DIST, SCROLLING_VELOCITY)
    # zaber_axes.scroll(-SCROLLING_DIST, SCROLLING_VELOCITY)

    # projector.stop_sequencer()
    # zaber_axes.increment_lateral(LATERAL_INCREMENT)
    # projector.send_sequencer(sequencers[1])
    # projector.start_sequencer()

    # zaber_axes.scroll(SCROLLING_DIST, SCROLLING_VELOCITY)
    # zaber_axes.scroll(-SCROLLING_DIST, SCROLLING_VELOCITY)
    # projector.stop_sequencer()

    # zaber_axes.increment_layer(LAYER_HEIGHT)

# zaber_axes.ZAxis.move_absolute(30, Units.LENGTH_MILLIMETRES)
# projector.send(records.SetLedDriverAmplitude(0, 100).bytes()) # Set LED amplitude back to 100