from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT, seq
from lux4600.projector import Projector
from lux4600.records import *
from lux4600.img import Strip
from PIL import Image
import time

# Stitched image produced using boilerplate code in lux4600\grayscale.py
# gs10 x 4320 takes 380.94 seconds to upload, ~6.3 minutes
stitched_image = r"test\test-grayscale\1920x4320_gs4_A_stitched.bmp"
img = Image.open(stitched_image)

strip = Strip(img, 0)
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)

projector.check_connection()

# Comment this out if image has already been uploaded since 
# the projector was last powered on to save time.
time_elapsed = time.time()
projector.send_strip(strip)
time_elapsed = time.time() - time_elapsed
print(f"Time elapsed to send strip: {time_elapsed:.2f} seconds")

sequencer = seq.Sequencer(r"test\test-seq\1920x4320_gs4_scroll.txt", 1440)

projector.send_sequencer(sequencer)
projector.check_sequencer_error()

# Show a horizantally mirrored strip of the underlying image
# This is, visually, what should be projected
mirror = Image.open(r'test\test-grayscale\1920x4320_gs4_A.bmp')
mirror = mirror.transpose(Image.FLIP_LEFT_RIGHT)
mirror.show()

# Run the sequencer to start the scrolling effect
projector.start_sequencer()
input("Press Enter to stop the sequencer...")
projector.stop_sequencer()
