from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT, seq
from lux4600.projector import Projector
from lux4600.records import *
from lux4600.img import Strip
from PIL import Image

img = Image.open(r"test\test-grayscale\1920x4320-gs-stripes.bmp")

strip = Strip(img, 0)
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)

projector.check_connection()

projector.send_strip(strip)

sequencer = seq.Sequencer(r"test\test-seq\8bit-1080.txt", 1440)

projector.send_sequencer(sequencer.packets)
projector.check_sequencer_error()

projector.send_strip(strip)


projector.start_sequencer()
