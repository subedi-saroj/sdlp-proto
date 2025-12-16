from PIL import Image, ImageDraw
from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT
from lux4600 import seq
from lux4600.projector import Projector
from lux4600.seq import Sequencer
from lux4600.img import Strip


def make_large_test_pattern(width: int, height: int) -> Image.Image:
	"""Create a solid black 1-bit image for a large 43200-row test."""
	img = Image.new('1', (width, height), 0)
	return img


def main():
	width, height = 1920, 43200  # 6 blocks of 7200 rows each, or just a large image
	
	print(f"Creating test image {width}x{height}...")
	test_image = make_large_test_pattern(width, height)
	
	projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)
	
	# Halt any running sequencer before upload to avoid contention
	projector.stop_sequencer()
	
	# Convert to 1-bit if needed
	if test_image.mode != "1":
		test_image = test_image.convert("1")
	
	print(f"Uploading {width}x{height} image to inum 0...")
	
	# Upload using uncompressed Type 4
	strip = Strip(test_image, 0)
	projector.send_strip(strip, lines_per_packet=6)
	
	print("Image upload complete. Starting sequencer...")
	
	# Load and start a simple 1-bit scroll sequencer
	sequencers = [seq.Sequencer(r"test\test-seq\1bit-scroll-seq.txt", 1440)]
	
	try:
		projector.send_sequencer(sequencers[0])
	except Exception as exc:
		print(f"Sequencer load failed (upload still succeeded): {exc}")
	
	projector.start_sequencer()
	print("Done. Sequencer is running.")


if __name__ == "__main__":
	main()
