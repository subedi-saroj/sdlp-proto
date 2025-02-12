from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT
from lux4600.img import Grayscale, Strip
from lux4600.projector import Projector

projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT, 10)

grayscale_image = Grayscale(r"..\test\test-repo\grayscale_test.bmp")

