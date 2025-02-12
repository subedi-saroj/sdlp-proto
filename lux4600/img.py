from PIL import Image
from typing import Iterator
import grayscale


class Strip:

    def __init__(self, image:Image.Image, inum:int):

        self.image = image

        self.image.convert("1") # Convert to 1-bit bmp
        self.width, self.height = self.image.size
        self.inum = inum

        self.packets = self.to_packets(inum)

    def to_packets(self, lines_per_packet:int=240) -> Iterator[bytes]:
        
        # Check inum and lines per packet
        StripValueError.check_inum_size(self.inum)
        StripValueError.check_packet_size(lines_per_packet, self.tobytes())

        # Split into packets
        lines = self.height // (self.width//8)  # Assuming each line is 1920 pixels wide and 1 bit per pixel = 240 bytes
        num_packets = lines // lines_per_packet

        for i in range(num_packets):

            # Calculate range of bytes to send
            start = i * lines_per_packet * (self.width//8)
            end = (i + 1) * lines_per_packet * (self.width//8)
            offset = lines_per_packet * i

            # Create packet
            packet = (b'\x05\xAE\x00\x68' + 
                    i.to_bytes(2, byteorder='big') + 
                    self.inum.to_bytes(2, byteorder='big') + 
                    offset.to_bytes(6, byteorder='big') + 
                    self.image.tobytes()[start:end] # Pull bytes from this strip
                    )
            
            yield packet
    
    def show(self):
        self.image.show()
    
    def save(self, file_path:str):
        self.image.save(file_path)


class StripValueError(ValueError):
    """Exception raised for parameter value errors in the Strip class."""

    @staticmethod
    def check_packet_size(lines_per_packet: int, img: bytes, width:int=1920):
        
        # Check expected packet size
        payload_size = lines_per_packet * (width//8)

        if len(img) % (width//8) != 0:

            raise StripValueError(
                f"""The number of bytes in img is not a multiple of the bytes per line.
                {len(img)} bytes, {width//8} bytes per line."""
                )
        
        if len(img) % (payload_size) != 0:

            raise StripValueError(
                f"""The number of bytes in img is not a multiple of the expected packet size.
                {len(img)} bytes, {payload_size} bytes per packet."""
                )
        
        if (14 + payload_size) > 1500:
            raise StripValueError(
                f"""Expected packet size exceed 1500.
                {14 + payload_size} bytes, 1500 bytes max."""
                )

    @staticmethod  
    def check_inum_size(inum: int):
            
            if inum > 65535:
                raise StripValueError(
                    f"""inum must be less than 65536."
                    {inum} bytes, 65535 max."""
                    )
    

class Grayscale:

    def __init__(self, file_path:str, strip_width:int=1920, level=255):

        GrayscaleValueError.check_level(level)

        self.strip_width = strip_width

        # Initialize correctly sized, buffered, and grayscaled image
        self.image = grayscale.add_buffer(Image.open(file_path), strip_width)

        self.width, self.height = self.image.size
        self.level = level
        self.num_strips = self.width // self.strip_width

        self.strips = self.get_strips()

    def get_strips(self):
        """
        Generator that yields each strip of the image after splitting and grayscale multiplication.

        1. The strips are split from the image horizontally (resulting in long vertical strips)
        2. Each strip is split into self.level number of strips by multiplying the image with a thresholded grayscale.

        Yields:
            Strip: The next strip in the sequence of strips. The strip is split into self.level number of strips with thresholded grayscales, where the threshold is calculated as i * 255 // self.level.
        """
        
        for split in grayscale.split_image(self.image, self.strip_width):
            
            for inum, strip in enumerate(grayscale.multiply_image(split, self.level)):
                yield Strip(image=strip, inum=inum)
    
    def show(self):
        """Shows the image."""
        self.image.show()

    def save_strips(self, directory:str):
        """Saves the strips to a given directory.

        Args:
            directory (str): The path to the directory to save the strips in.
        """
        
        for i, strip in enumerate(self.strips):
            strip.save(f"{directory}\\{i + 1}_inum-{strip.inum}.bmp")

class GrayscaleValueError(ValueError):
    """Exception raised for parameter value errors in the Grayscale class."""

    @staticmethod
    def check_level(level:int):
        """
        Checks if the level is within the valid range.

        Args:
            level (int): The level to check.

        Raises:
            GrayscaleValueError: If the level is not within the valid range (1-256).
        """
        if level > 256:
            raise GrayscaleValueError(
                f"""Level must be less than 256.
                {level} bytes, 256 max."""
                )
        if level < 1:
            raise GrayscaleValueError(
                f"""Level must be greater than 0.
                {level} bytes, 1 min."""
                )
    



#
# 
#
if __name__ == '__main__':
    
    file_path = r"..\test\test-repo\grayscale_test.bmp"

    strip_width = 960

    gs = Grayscale(file_path, strip_width, 4)

    gs.show()
    print(gs.num_strips)

    count = 0
    for strip in gs.strips:
        count += 1
    print(count)