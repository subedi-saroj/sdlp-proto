from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT, records
from lux4600.img import Grayscale, Strip
from lux4600.projector import Projector
from lux4600.seq import Sequencer
from PIL import Image
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT, 5)

# if not projector.check_connection():
#     print('Connection unsuccessful. Exiting.')
#     exit()


# Load the image
strip = Strip(Image.open(r".\test\test-grayscale\1.bmp"), 0)

##
## Prep the projector
##



#grayscale_image = Grayscale(r"..\test\test-repo\grayscale_test.bmp")

