from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT, seq
from lux4600.projector import Projector
projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)
projector.check_connection()
projector.send_sequencer(seq.Sequencer(r"test\test-seq\1bit-scroll-seq.txt", 1440))
# projector.send_sequencer(seq.Sequencer(r"test\test-seq\clear_global.txt", 1440))
projector.start_sequencer()