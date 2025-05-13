from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT, seq
from lux4600.projector import Projector
from lux4600.records import *
from lux4600.img import Strip
from PIL import Image

# Load the scrolling binary (1080x1920) image.
img = Image.open(r"test\test-binary\1920x20000_binary_scroll.bmp")

# Initialize strip from the stitched image at INUM 0
strip = Strip(img, 0)

# Initialize projector with the default IP address and ports
# (This is the same as the projector's IP address and ports in the lux4600.py file)
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)

projector.check_connection()

# Send the strip to the projector. 
# Because the image is 20000 pixels tall, we need to split it into packets of 5 lines each instead of 6.
projector.send_strip(strip, lines_per_packet=5)

# Initialize sequencer with the sequencer file and the packet size, default 1440.
# More documentation on the sequencer can be found in the Visitech manual.
sequencer = seq.Sequencer(r"test\test-seq\1bit-scroll-seq.txt", 1440)

# vSend the sequencer to the projector.
projector.send_sequencer(sequencer)
projector.check_sequencer_error()

# Start the sequencer to show the static image
projector.start_sequencer()
