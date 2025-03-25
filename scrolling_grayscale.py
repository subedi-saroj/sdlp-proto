from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT, seq
from lux4600.projector import Projector
from lux4600.records import *
from lux4600.img import Strip
from PIL import Image
import time

img = Image.open(r"test\test-grayscale\1920x6480_gs2_A.bmp")

strip = Strip(img, 0)
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)

projector.check_connection()

projector.send_strip(strip)

sequencer = seq.Sequencer(r"test\test-seq\1920x6480_gs2_scroll.txt", 1440)

projector.send_sequencer(sequencer.packets)
projector.check_sequencer_error()

projector.send_strip(strip)


projector.start_sequencer()
input("Press Enter to stop the sequencer...")
projector.stop_sequencer()
