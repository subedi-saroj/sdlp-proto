from PIL import Image, ImageDraw
from lux4600 import IP, DATA_PORT, IMAGE_DATA_PORT
from lux4600.projector import Projector


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
	width, height = 1920, 3240
	test_image = make_test_pattern(width, height)

	projector = Projector(IP, DATA_PORT, IMAGE_DATA_PORT)

	# Upload the RLE-compressed image to inum 0 in Type 5 mode
	projector.send_image_rle(test_image, width=width, height=height, inum=0)

	# If your sequencer is already loaded on the projector, start it to display the uploaded image.
	try:
		projector.start_sequencer()
	except Exception as exc:
		print(f"Sequencer start failed (upload still succeeded): {exc}")


if __name__ == "__main__":
	main()