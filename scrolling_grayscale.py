from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT, seq
from lux4600.projector import Projector
from lux4600.records import *
from lux4600.img import Strip
from PIL import Image
import time

# Load the stitched (1-bit) image.
# --
# (This image was created using boilerplate code in lux4600/grayscale.py)
stitched_image = r"test\test-grayscale\1920x4320_gs4_A_stitched.bmp"
img = Image.open(stitched_image)

# Initialize strip from the stitched image at INUM 0
strip = Strip(img, 0)

# Initialize projector with the default IP address and ports
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)
projector.check_connection()

# Send the strip to the projector. 
# The projector will automatically split the image into packets and upload them.
# --
# (Comment this out if image has already been uploaded since the projector was last powered on to save time)
time_elapsed = time.time()
projector.send_strip(strip)
time_elapsed = time.time() - time_elapsed
print(f"Time elapsed to send strip: {time_elapsed:.2f} seconds")

# Initialize sequencer with the sequencer file and the packet size, default 1440.
# More documentation on the sequencer can be found in the Visitech manual.
sequencer = seq.Sequencer(r"test\test-seq\1920x4320_gs4_scroll.txt", 1440)

#Send the sequencer to the projector.
projector.send_sequencer(sequencer)

# Show a horizantally mirrored strip of the underlying image
# This is, visually, what should be projected
mirror = Image.open(r'test\test-grayscale\1920x4320_gs4_A.bmp')
mirror = mirror.transpose(Image.FLIP_LEFT_RIGHT)
mirror.show()

# Run the sequencer to start the scrolling effect
projector.start_sequencer()
input("Press Enter to stop the sequencer...")
projector.stop_sequencer()
