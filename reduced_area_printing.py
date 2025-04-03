from lux4600 import *
from lux4600.projector import Projector
from lux4600.img import Strip
from lux4600.seq import Sequencer
from lux4600.grayscale import split_image, multiply_image, stitch_images
from PIL import Image

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
    7. The projector and axes are started simulteanously for a single layer.
    8. The projector and X-Y axes are stopped after the layer is complete. Z axes increments.
        - LAYER_HEIGHT = 0.5 (mm)

    --> Repeat steps 6 and 7 for some number of layers.
        - LAYERS = 10
'''

# Constants
FULL_WIDTH = 2880 # width of pre-processed grayscale image exported from Chitubox or GIMP as .bmp
FULL_HEIGHT = 3240 # height of pre-processed grayscale image

GS_STRIP_WIDTH = 1920 # width of each strip
OVERLAP = 960 # overlap between the two strips

FACTOR = 6 # grayscale multiplication factor
LAYER_HEIGHT = 0.5 # mm
LAYERS = 10 # number of layers to print

# Step 0: Load the grayscale image
full_grayscale_image = Image.open(r"test\test-dogbone\2880x3240_dogbone_A.bmp")

# Step 1: Split the image into strips
left_strip = Image.new('L', (GS_STRIP_WIDTH, FULL_HEIGHT), 0)  # 'L' mode ensures 8-bit grayscale
left_strip.paste(full_grayscale_image.crop((0, 0, GS_STRIP_WIDTH, FULL_HEIGHT)), (0, 0))

right_strip = Image.new('L', (GS_STRIP_WIDTH, FULL_HEIGHT), 0)  # 'L' mode ensures 8-bit grayscale
right_strip.paste(full_grayscale_image.crop((GS_STRIP_WIDTH//2, 0, FULL_WIDTH, FULL_HEIGHT)), (0, 0))

# Step 2: Scale the strips over the overlap

f_left = lambda x, current: int((current / OVERLAP) * (OVERLAP - x)) # linear right strip scaling function
f_right = lambda x, current: int((current / OVERLAP) * x) # linear left strip scaling function

# Scale the strip overlap region
def scale_overlap(strip:Image.Image, func, side:str) -> Image.Image:
    for y in range(0, FULL_HEIGHT):

        # Note: this indexing only works because the overlap is 960 pixels wide
        # and the strips are 1920 pixels wide. If the overlap is changed, this
        # indexing will need to be changed as well.
        for x in range(0, OVERLAP):

            if side == 'L':
                pixel_x = x + OVERLAP
            elif side == 'R':
                pixel_x = x
            else:
                raise ValueError("Invalid side. Use 'L' or 'R'.")

            pixel_y = y # for clarity

            val = strip.getpixel((pixel_x, pixel_y)) # New grayscale value for left strip
            
            if val > 0:
                strip.putpixel((pixel_x, pixel_y), func(x, val))
    return strip

left_strip = scale_overlap(left_strip, f_right, 'L')
right_strip = scale_overlap(right_strip, f_right, 'R')


