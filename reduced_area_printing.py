from lux4600 import *
from lux4600.projector import Projector
from lux4600.img import Strip
from lux4600.seq import Sequencer
from lux4600.grayscale import split_image, multiply_image, stitch_images
from PIL import Image
import time, sys

'''
Author: David Alexander
Date: 2025-04-03
Last updated: 2025-04-03

This script shows an example print for the reduced area printing process.
It is a simplified version of the scrolling grayscale print, where only one grayscale
strip is used in every layer.

The overall process is as follows:
    0. Before running this script, create an image 2880x3240 pixels in size.
        - FULL_WIDTH = 2880
        - FULL_HEIGHT = 3240
       This can be a grayscale image or a color image. The color image will be converted to grayscale.
    
    1. The image is split into two grayscale strips of 1920 pixels wide and 3240 rows tall. 
        - GS_STRIP_WIDTH = 1920
        - GS_STRIP_HEIGHT = FULL_HEIGHT
       There will be an overlap of 960 pixels between the strips. (1920 * 2 = 2880 = 960 * 3)
        - OVERLAP = 960

    2. The two grayscale strips are "scaled" over the overlap, so that the sum of the two overlap
        regions is equal to the original value. 
    3. The strips are then multiplied by 6 to create 6 grayscale images.
        - FACTOR = 6

    4. The grayscale images are stitched together to create a single image.
    5. The stitched image is then uploaded to the projector.
    6. The sequencer is then created and uploaded to the projector.
    TODO
    7. The projector and axes are started simulteanously for a single layer.
    8. The projector and X-Y axes are stopped after the layer is complete. Z axes increments.
        - LAYER_HEIGHT = 0.5 (mm)

    --> Repeat steps 6 and 7 for some number of layers.
        - LAYERS = 5
'''
def preprocess_grayscale_image():
    # Constants
    FULL_WIDTH = 2880 # width of pre-processed grayscale image
    FULL_HEIGHT = 3240 # height of pre-processed grayscale image

    GS_STRIP_WIDTH = 1920 # width of each strip
    OVERLAP = 960 # overlap between the two strips

    FACTOR = 6 # grayscale multiplication factor

    # Step 0: Load the grayscale image
    full_grayscale_image = Image.open(r"test\test-dogbone\2880x3240_dogbone_VERT.bmp")

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

    # Step 3: Multiply the strips by the factor
    left_strip_images = multiply_image(left_strip, FACTOR)
    grayscale_strip = Strip(stitch_images(left_strip_images, FULL_HEIGHT * FACTOR * 2), 0)

    right_strip_images = multiply_image(right_strip, FACTOR)
    right_strip_images = stitch_images(right_strip_images, FULL_HEIGHT * FACTOR)

    # Step 4: Stitch the images together
    grayscale_strip.image.paste(right_strip_images, (0, FULL_HEIGHT * FACTOR))

    return grayscale_strip

# Step 5: Upload the stitched image to the projector
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)

projector.check_connection()

# # Comment this out if image has already been uploaded since 
# # the projector was last powered on to save time.
# grayscale_strip = preprocess_grayscale_image()
# projector.send_strip(grayscale_strip)

# Step 6: Create the sequencer files for left and right strips
sequencers = [
        seq.Sequencer(r"test\test-seq\2880x3240_gs6_R.txt", 1440),
        seq.Sequencer(r"test\test-seq\2880x3240_gs6_L.txt", 1440)
]

# TODO: Step 7: Start the projector and axes simultaneously for a single layer
import axes
from zaber_motion import Units, wait_all

input("Press Enter to start the projector and axes...")
zaber_axes = axes.ZaberAxes("COM3")
# zaber_axes.home()

Z_START = 150 # mm, initial z position
X_START = 60 # mm, initial x position
Y_START = 50 # mm, initial y position

zaber_axes.ZAxis.move_absolute(Z_START, Units.LENGTH_MILLIMETRES)
zaber_axes.XAxis.move_absolute(X_START, Units.LENGTH_MILLIMETRES)
zaber_axes.YAxis.move_absolute(Y_START, Units.LENGTH_MILLIMETRES)

LAYER_HEIGHT = 0.4
LAYERS = 6

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

    zaber_axes.XAxis.move_absolute(X_START, Units.LENGTH_MILLIMETRES)

    projector.send_sequencer(sequencers[0])  # Alternate between left and right sequencers
    projector.start_sequencer()

    zaber_axes.scroll(SCROLLING_DIST, SCROLLING_VELOCITY)
    zaber_axes.scroll(-SCROLLING_DIST, SCROLLING_VELOCITY)

    projector.stop_sequencer()
    zaber_axes.increment_lateral(LATERAL_INCREMENT)
    projector.send_sequencer(sequencers[1])
    projector.start_sequencer()

    zaber_axes.scroll(SCROLLING_DIST, SCROLLING_VELOCITY)
    zaber_axes.scroll(-SCROLLING_DIST, SCROLLING_VELOCITY)
    projector.stop_sequencer()

    zaber_axes.increment_layer(LAYER_HEIGHT)

zaber_axes.ZAxis.move_absolute(30, Units.LENGTH_MILLIMETRES)
projector.send(records.SetLedDriverAmplitude(0, 100).bytes()) # Set LED amplitude back to 100