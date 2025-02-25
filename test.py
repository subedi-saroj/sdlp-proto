from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT, records
from lux4600.img import Grayscale, Strip
from lux4600.projector import Projector
from lux4600.seq import Sequencer
from PIL import Image
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT, 5)

if not projector.check_connection():
    print('Connection unsuccessful. Exiting.')
    exit()

#
# Load the image
#
test_image = Image.open(r".\test\test-repo\1_1920x6840.bmp")

strip = Strip(test_image, 0)

projector.send_strip(strip)
print('image sent')

# Load the sequencer file

seq = Sequencer(r".\test\test-seq\1bit-scroll-seq.txt", 1440)
projector.send_sequencer(seq.packets)

projector.start_sequencer()
