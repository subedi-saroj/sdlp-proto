from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT, records
from lux4600.img import Grayscale, Strip
from lux4600.projector import Projector
from lux4600.seq import Sequencer
from PIL import Image
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT, 5)

if not projector.check_connection():
    print('Connection unsuccessful. Exiting.')
    exit()


# strip = Strip(Image.open(r".\test\test-repo\1920x20000_Test1.bmp"), 0)

# #
# # Prep the projector
# #
# projector.send_strip(strip)


# projector.start_sequencer()



grayscale_image = Grayscale(r".\test\test-repo\grayscale_test.bmp")

for strip in grayscale_image.strips:
    projector.send_strip(strip)
