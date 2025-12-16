from PIL import Image, ImageDraw
from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT
from lux4600 import seq
from lux4600.projector import Projector
from lux4600.seq import Sequencer
from lux4600.img import Strip


def make_test_pattern(width: int, height: int) -> Image.Image:
	"""Create a simple 1-bit test pattern (horizontal bars) for visibility."""
	img = Image.new('1', (width, height), 0)
	draw = ImageDraw.Draw(img)
	bar_height = 12
	spacing = 96
	y = 0
	while y < height:
		draw.rectangle((0, y, width - 1, min(y + bar_height, height - 1)), fill=1)
		y += spacing
	return img


def main():
	width, height = 1920, 4320  # adjust if you want fewer rows (e.g., 2160)

	# Set this to your image path
	img_path = r"test\test-grayscale\1920x4320_gs10_A.bmp"
	img = Image.open(img_path)

	# Normalize to 1-bit and target size for RLE Type 5
	# if img.mode != "1":
	# 	img = img.convert("1") # convert to 1-bit grayscale through dithering
	# if img.size != (width, height):
	# 	img = img.resize((width, height))

	# test_image = make_test_pattern(width, height)

	projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)

	# Halt any running sequencer before upload to avoid contention
	projector.stop_sequencer()

	# Upload a normal 1-bit image (Type 4, uncompressed)
	# projector.send_image_rle(img, width=width, height=height, inum=0)
	strip = Strip(img, 0)
	projector.send_strip(strip, lines_per_packet=6)
	sequencers = [seq.Sequencer(r"test\test-seq\1bit-scroll-seq.txt", 1440)]
	# If your sequencer is already loaded on the projector, start it to display the uploaded image.
	try:
		projector.send_sequencer(sequencers[0])
	except Exception as exc:
		print(f"Sequencer start failed (upload still succeeded): {exc}")
	projector.start_sequencer() 


if __name__ == "__main__":
	main()