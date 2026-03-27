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

This script demonstrates binary printing with 6 strips and 200px overlap.

The overall process is as follows:
    0. Before running this script, create an image 10520x8640 pixels in size.
        - FULL_WIDTH = 10520
        - FULL_HEIGHT = 8640
       This can be a grayscale image. The grayscale image will be converted to binary (0 or 1).
    
    1. The image is split into six binary strips of 1920 pixels wide and 8640 rows tall. 
        - STRIP_WIDTH = 1920
        - FULL_HEIGHT = 8640
       There will be an overlap of 200 pixels between consecutive strips.
        - OVERLAP = 200
    
    3. Each strip is converted to binary (0 or 1) based on grayscale threshold.

    4. Strips 1 & 2 are uploaded to inums 0, 1699
       Strips 3 & 4 are uploaded to inums 0, 1699 (reuse same inums)
       Strips 5 & 6 are uploaded to inums 0, 1699 (reuse same inums)
    
    5. Sequencer loads from these inums to display left and right strips simultaneously.
    
    6. The projector and axes are started simultaneously for a single layer.
    7. After each pair of strips, forward and backward scrolls are performed.
        - LAYER_HEIGHT = 0.05 (mm)

    --> Repeat for some number of layers.
        - LAYERS = number of image files

NOTES:
- The scroling stage (distance and velocity) is calibrated for 4320 rows images; inum set to 3 in 4bit gray sequencer.
The waitfor time for LedPulseWord is set at 10000 should be the middle ground. For more precise energy, calculate LED power.
stepinum is 1699; starting from 0 for left bitplanes and from 4*1699=6796 for right bitplanes.
'''

Z_START = 149.2 #149.2 mm, initial z position #150 focal position 
X_START = 20 # mm, initial x position #60 mm
Y_START = 15 # mm, initial y position #40 mm
offset =  0.54 #0.54   #mm ,calibrated offset for scrolling back gantry 0.54 mm 

# Constants for inum spacing
STEP_INUM = 799 #1699  # inum spacing for two strips (left and right)

LAYER_HEIGHT = 0.1 #mm
solid_base_layers = set(range(2, 11)) #| set(range(26, 35))  # Layers 2-9 and 22-30 # Define solid base layers that should skip image upload
layers_go_up = 30 # how many layers the Z axis should go up each time
# for sequencer with ledpulseword waitfor time of 10000, t_1080 rows = 3.28 s
Intensity = 2 # 0.81 User intensity in mW/cm^2, calculate based on the energy required for the layer
times_first_layer = 10
LED =  int(140.99*Intensity-17.761 ) # LED driver amplitude (0 to 4095)
print(f"\nCalculated LED setting: {LED}")
# THESE ARE CAREFULLY CALIBRATED VALUES
# TODO: verify with celestron handheld microscope from the natural resources library
SCROLLING_VELOCITY = 3.55 # 3.55 mm/s 10.368 mm in 3.25 s average
SCROLLING_DIST = 81.648 # 34.992 mm when row size is 4320 pixels - 1080 =  3240* 10.8 um
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
    FULL_WIDTH = 10520 # width of pre-processed grayscale image (6 strips of 1920 with 200px overlap)
    FULL_HEIGHT = 8640 # height of pre-processed grayscale image

    STRIP_WIDTH = 1920 # width of each strip
    OVERLAP = 200 # overlap between consecutive strips

    # Step 0: Load the grayscale image
    full_grayscale_image = Image.open(filepath).convert('L')  # Ensure 8-bit grayscale

    # Step 1: Extract 6 strips with 200px overlap
    # Strip positions: 0-1920, 1720-3640, 3440-5360, 5160-7080, 6880-8800, 8600-10520
    strip_positions = [
        (0, 1920),           # Strip 1
        (1720, 3640),        # Strip 2 (overlap 200)
        (3440, 5360),        # Strip 3 (overlap 200)
        (5160, 7080),        # Strip 4 (overlap 200)
        (6880, 8800),        # Strip 5 (overlap 200)
        (8600, 10520)        # Strip 6 (overlap 200)
    ]
    
    strips = []
    for i, (start_x, end_x) in enumerate(strip_positions):
        strip = Image.new('L', (STRIP_WIDTH, FULL_HEIGHT), 0)
        strip.paste(full_grayscale_image.crop((start_x, 0, end_x, FULL_HEIGHT)), (0, 0))
        strips.append(strip)

    # Step 2: Convert each strip to binary (threshold at 128)
    def grayscale_to_binary(img: Image.Image, threshold: int = 128) -> Image.Image:
        return img.point(lambda p: 255 if p >= threshold else 0, '1')

    binary_strips = [grayscale_to_binary(strip) for strip in strips]

    # Save strips for verification
    for i, strip in enumerate(binary_strips):
        strip.save(f"bitplanes/strip_{i+1}_binary.bmp")

    # Return list of 6 binary strips
    return binary_strips

# Step 4: Initialize the projector
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)

projector.check_connection()
projector.stop_sequencer() # Stop if any running sequencer

# Step 5: Create sequencer for 4-bit weighted bitplanes
# sequencer = seq.Sequencer(r"test\test-seq\seq_scroll_4bit_gray_visitech_back.txt", 1440)
sequencers = [
        seq.Sequencer(r"test\test-seq\seq_scroll_binary_visitech_for.txt", 1440),
        seq.Sequencer(r"test\test-seq\seq_scroll_binary_visitech_back .txt", 1440)
]

# Step 6: Start the projector and axes simultaneously for a single layer
import axes
from zaber_motion import Units, wait_all

input("Press Enter to start the projector and axes...")

# Set INUM_SIZE to 4320 for 4-bit grayscale printing with scrolling
inumsize = 8640  # DMD height - set to max row size or higher #setting this to 1080 will make it difficult to scroll backward
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
        binary_strips = preprocess_grayscale_image(img_path)
        
        # Process 3 pairs of strips (1-2, 3-4, 5-6)
        for pair_idx in range(3):
            strip1_idx = pair_idx * 2
            strip2_idx = pair_idx * 2 + 1
            
            # Upload strip 1 to inum 0
            print(f"Uploading strip {strip1_idx + 1} to inum 0...")
            strip1 = Strip(binary_strips[strip1_idx], 0)
            strip1.save(f"bitplanes/pair_{pair_idx+1}_strip1_inum_0.bmp")
            projector.send_strip(strip1)
            
            # Upload strip 2 to inum STEP_INUM
            print(f"Uploading strip {strip2_idx + 1} to inum {STEP_INUM}...")
            strip2 = Strip(binary_strips[strip2_idx], STEP_INUM)
            strip2.save(f"bitplanes/pair_{pair_idx+1}_strip2_inum_{STEP_INUM}.bmp")
            projector.send_strip(strip2)

            # Set LED driver amplitude: for first layer use 10x LED, else use LED (0 to 4095)
            if (i + 1) == 1:
                led_val = min(LED * times_first_layer, 4095)
            else:
                led_val = LED
            # Ensure water cooling system is functional if amplitude > 100 
            projector.send(records.SetLedDriverAmplitude(0, led_val).bytes())

            # Forward scroll
            projector.send_sequencer(sequencers[0])
            projector.start_sequencer()
            zaber_axes.scroll(SCROLLING_DIST-offset, SCROLLING_VELOCITY)

            time.sleep(0.5)  # wait at the end of the scroll
            zaber_axes.increment_lateral(LATERAL_INCREMENT)
            time.sleep(0.5)  # wait after lateral increment

            # Backward scroll
            projector.send_sequencer(sequencers[1])
            projector.start_sequencer()
            zaber_axes.scroll(-SCROLLING_DIST, SCROLLING_VELOCITY)

            time.sleep(0.5)

            time.sleep(0.5)  # wait at the end of the scroll
            zaber_axes.increment_lateral(LATERAL_INCREMENT)
            time.sleep(0.5)  # wait after lateral increment

    # Delamination after all 3 pairs are complete for this layer
    zaber_axes.increment_layer(LAYER_HEIGHT*layers_go_up)
    time.sleep(0.5) 
    zaber_axes.increment_layer(-LAYER_HEIGHT*(layers_go_up-1))

    zaber_axes.XAxis.move_absolute(X_START, Units.LENGTH_MILLIMETRES)
    zaber_axes.YAxis.move_absolute(Y_START, Units.LENGTH_MILLIMETRES)
    time.sleep(1) #material refill time

zaber_axes.ZAxis.move_absolute(10, Units.LENGTH_MILLIMETRES)
projector.send(records.SetLedDriverAmplitude(0, 100).bytes()) # Set LED amplitude back to 100
projector.stop_sequencer() # Stop if any running sequencer at the end of the print job