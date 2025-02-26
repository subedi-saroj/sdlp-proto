from PIL import Image
from typing import Iterator
import grayscale


class Strip:
    '''A class representing a 1-bit strip of an image to be sent to the projector.'''

    def __init__(self, image:Image.Image, inum:int):
        """
        Constructor for Strip class.

        Args:
            image (Image.Image): A PIL Image object representing the strip to be sent to the projector.
                - The image will be converted to 1-bit mode
                - The image should generally be 1920 pixels wide
            inum (int): The inum of the strip to be sent to the projector.
                - The inum should be less than 65536 and greater than or equal to 0

        Attributes:
            image (Image.Image): A PIL Image object representing the strip to be sent to the projector.
            width (int): The width of the strip in pixels.
            height (int): The height of the strip in pixels.
            inum (int): The inum of the strip to be sent to the projector.
            packets (Iterator[bytes]): A generator that yields the packets of the strip to be sent to the projector.
        """
        self.image = image

        self.image = self.image.convert("1") # Convert to 1-bit bmp
        self.image.show()
        self.width, self.height = self.image.size
        self.inum = inum

    def to_packets(self, lines_per_packet:int) -> Iterator[bytes]:
        '''
        Return a generator that yields the packets of the strip to be sent to the projector.
        '''
        
        # Check inum and lines per packet
        StripValueError.check_inum_size(self.inum)
        StripValueError.check_packet_size(lines_per_packet, self.image.tobytes(), self.width)

        
        # Calculate the number of lines in the image and the number of packets
        num_packets = self.height // lines_per_packet
        print(num_packets)

        # Split the image into packets
        for packet_idx in range(num_packets):

            # Calculate range of bytes to send
            start, end, offset = self.get_packet_range(packet_idx, lines_per_packet)

            # Yield the packet
            yield self.get_packet(packet_idx, start, end, offset)


    def get_packet_range(self, packet_idx:int, lines_per_packet:int) -> bytes:
        """
        Calculates the packet range for a given packet number.

        Args:
            packet_idx (int): The packet number to get.
            lines_per_packet (int): The number of lines per packet.
            packet_range (tuple): The range of bytes to get from the image.

        Returns:
            start (int): The start byte of the packet.
            end (int): The end byte of the packet.
            offset (int): The offset of the packet.
            
        """

        # Calculate range of bytes to send
        start = packet_idx * lines_per_packet * (self.width//8)
        end = (packet_idx + 1) * lines_per_packet * (self.width//8)
        offset = lines_per_packet * packet_idx

        return start, end, offset
    
    def get_packet(self, packet_idx:int, start:int, end:int, offset:int) -> bytes:
        """
        Constructs a packet of image data.
        Args:
            packet_idx (int): The index of the packet.
            lines_per_packet (int): The number of lines per packet.
            start (int): The starting byte index of the image data to include in the packet.
            end (int): The ending byte index of the image data to include in the packet.
            offset (int): The offset value to include in the packet.
        Returns:
            bytes: The constructed packet containing the specified image data.
        """

        return (b'\x05\xAE\x00\x68' + 
                packet_idx.to_bytes(2, byteorder='big') + 
                self.inum.to_bytes(2, byteorder='big') + 
                offset.to_bytes(6, byteorder='big') + 
                self.image.tobytes()[start:end] # Pull bytes from this strip
                )
    
    def get_bin_image_data(self, skip_header:int=130) -> bytes:
        """
        Returns the binary image data (a 1-bit .bmp file with the bitmap header removed)

        Args:
            skip_header (int): The number of bytes to remove from the image.
                This is typically 62 bytes for a 1-bit .bmp file according to the luxbeam manual,
                but I couldn't get it to work with 62 bytes. I use 130 bytes instead which works.

        Returns:
            bytes: The binary image data with the bitmap header removed.
        """
        
        # Remove bytes from the image
        byte_data = self.image.tobytes()[skip_header:]

        return byte_data
    
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