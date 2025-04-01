from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT, seq
from lux4600.projector import Projector
from lux4600.records import *
from lux4600.img import Strip
from PIL import Image
import time

f1 = r"test\test-grayscale\1920x4320_gs4_A_stitched.bmp"
f2 = r"test\test-grayscale\1920x6480_gs2_A.bmp"
img = Image.open(f1)

strip = Strip(img, 0)
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)

projector.check_connection()

projector.send_strip(strip)

sequencer = seq.Sequencer(r"test\test-seq\1920x4320_gs4_scroll.txt", 1440)

projector.send_sequencer(sequencer)
projector.check_sequencer_error()

# Show a horizantally mirrored strip
mirror = strip.image.transpose(Image.FLIP_LEFT_RIGHT)
mirror.show()

projector.start_sequencer()
input("Press Enter to stop the sequencer...")
projector.stop_sequencer()
