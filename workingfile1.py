from lux4600 import *
from lux4600.projector import Projector
from lux4600.img import Strip
from lux4600.seq import Sequencer
from PIL import Image
import time, sys, os
import tkinter as tk
from tkinter import filedialog

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

NOTES:
- The scroling stage (distance and velocity) is calibrated for 4320 rows images; inum set to 3 in 4bit gray sequencer.
The waitfor time for LedPulseWord is set at 10000 should be the middle ground. For more precise energy, calculate LED power.
stepinum is 1699; starting from 0 for left bitplanes and from 4*1699=6796 for right bitplanes.
'''

Z_START = 149.2 #149.2 mm, initial z position #150 focal position 
X_START = 55 # mm, initial x position #60 mm
Y_START = 40 # mm, initial y position #40 mm
offset =  0.54 #0.54   #mm ,calibrated offset for scrolling back gantry 0.54 mm 

# Constants for inum spacing
STEP_INUM = 1699 #1699  # Changed from 1699 for simpler testing; revert to 1699 if needed
BITPLANES = 4 #4

LAYER_HEIGHT = 0.05 #mm
solid_base_layers = set(range(2, 11)) #| set(range(26, 35))  # Layers 2-9 and 22-30 # Define solid base layers that should skip image upload
layers_go_up = 60 # how many layers the Z axis should go up each time
# for sequencer with ledpulseword waitfor time of 10000, t_1080 rows = 3.28 s
Intensity = 3 # 0.81 User intensity in mW/cm^2, calculate based on the energy required for the layer
times_first_layer = 10
LED =  int(140.99*Intensity-17.761 ) # LED driver amplitude (0 to 4095)
print(f"\nCalculated LED setting: {LED}")
# THESE ARE CAREFULLY CALIBRATED VALUES
# TODO: verify with celestron handheld microscope from the natural resources library
SCROLLING_VELOCITY = 3.55 # 3.55 mm/s 10.368 mm in 3.25 s average
SCROLLING_DIST =  34.992# 34.992 mm when row size is 4320 pixels - 1080 =  3240* 10.8 um
LATERAL_INCREMENT = 18.576 # 18.576 mm for only 200 overlap; 10.368 mm when overlap is 960 pixels *10.8 um

# Prompt user to select folder containing images
root = tk.Tk()
root.withdraw()
image_folder = filedialog.askdirectory(title="Select folder with layer images (e.g., 1.bmp, 2.bmp, ...)")
if not image_folder:
    raise RuntimeError("No folder selected!")

# Get sorted list of image files (expects names like 1.bmp, 2.bmp, ...)
image_files = sorted(
    [f for f in os.listdir(image_folder) if f.lower().endswith('.bmp') and os.path.splitext(f)[0].isdigit()],
    key=lambda x: int(os.path.splitext(x)[0])
)
LAYERS = len(image_files)
print(f"Found {LAYERS} layers in {image_folder}")

def preprocess_grayscale_image(filepath):
    # Constants
    FULL_WIDTH = 3640 #3640 when 200 overlaps # width of pre-processed grayscale image #2880
    FULL_HEIGHT = 4320 # height of pre-processed grayscale image

    GS_STRIP_WIDTH = 1920 # width of each strip
    OVERLAP = GS_STRIP_WIDTH * 2 - FULL_WIDTH

    BITPLANES = 4 # number of weighted bitplanes (4 -> 16 levels)

    # Step 0: Load the grayscale image
    full_grayscale_image = Image.open(filepath)

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
projector.stop_sequencer() # Stop if any running sequencer

# Step 5: Create sequencer for 4-bit weighted bitplanes
# sequencer = seq.Sequencer(r"test\test-seq\seq_scroll_4bit_gray_visitech_back.txt", 1440)
sequencers = [
        seq.Sequencer(r"test\test-seq\seq_scroll_4bit_gray_visitech_for.txt", 1440),
        seq.Sequencer(r"test\test-seq\seq_scroll_4bit_gray_visitech_back.txt", 1440)
]

# Step 6: Start the projector and axes simultaneously for a single layer
import axes
from zaber_motion import Units, wait_all

input("Press Enter to start the projector and axes...")

# Set INUM_SIZE to 4320 for 4-bit grayscale printing with scrolling
inumsize = 4320  # DMD height - set to max row size or higher #setting this to 1080 will make it difficult to scroll backward
print(f"\nSetting INUM_SIZE to {inumsize} (DMD height)...")
projector.send(records.SetInumSize(inumsize).bytes())
print(f"✅ INUM_SIZE set : {inumsize}\n") 

zaber_axes = axes.ZaberAxes("COM3")
zaber_axes.home()

zaber_axes.ZAxis.move_absolute(Z_START, Units.LENGTH_MILLIMETRES)
zaber_axes.XAxis.move_absolute(X_START, Units.LENGTH_MILLIMETRES)
zaber_axes.YAxis.move_absolute(Y_START, Units.LENGTH_MILLIMETRES)

# Create output directory for bitplane verification
os.makedirs("bitplanes", exist_ok=True)

for i, img_name in enumerate(image_files):
    print(f"Layer ✅ {i+1} ✅ of {LAYERS}: {img_name}")
    # Skip image upload for solid base layers
    if (i + 1) in solid_base_layers:
        print(f"Skipping image upload for solid base layer {i + 1}")
    else:
        img_path = os.path.join(image_folder, img_name)
        left_planes, right_planes = preprocess_grayscale_image(img_path)
        # left_planes, right_planes = preprocess_grayscale_image(r"test\test_images\dogbone_grayscale.bmp")
        
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

    # Set LED driver amplitude: for first layer use 10x LED, else use LED (0 to 4095)
    if (i + 1) == 1:
        led_val = min(LED * times_first_layer, 4095)
    else:
        led_val = LED
    # Ensure water cooling system is functional if amplitude > 100 
    projector.send(records.SetLedDriverAmplitude(0, led_val).bytes())

    projector.send_sequencer(sequencers[0]) #forward scroll
    projector.start_sequencer()
    zaber_axes.scroll(SCROLLING_DIST-offset, SCROLLING_VELOCITY)

    time.sleep(0.5)  # wait for a second at the end of the scroll
    zaber_axes.increment_lateral(LATERAL_INCREMENT)
    time.sleep(0.5)  # wait for a second after lateral increment

    projector.send_sequencer(sequencers[1]) #Backward scroll
    projector.start_sequencer()
    zaber_axes.scroll(-SCROLLING_DIST, SCROLLING_VELOCITY)

    zaber_axes.increment_layer(LAYER_HEIGHT*layers_go_up) #Delamination of the layer
    time.sleep(0.5) 
    zaber_axes.increment_layer(-LAYER_HEIGHT*(layers_go_up-1))

    zaber_axes.XAxis.move_absolute(X_START, Units.LENGTH_MILLIMETRES)
    zaber_axes.YAxis.move_absolute(Y_START, Units.LENGTH_MILLIMETRES)
    time.sleep(1) #material refill time

zaber_axes.ZAxis.move_absolute(10, Units.LENGTH_MILLIMETRES)
projector.send(records.SetLedDriverAmplitude(0, 100).bytes()) # Set LED amplitude back to 100
projector.stop_sequencer() # Stop if any running sequencer at the end of the print job