#
# Base code for handling .bmp files. 
# Short scripts removed from classes to improve readability and clarity.# 
#

def bmp_to_packets(inum: int, lines_per_packet: int, img: bytes, width:int=1920):
    """
    Splits a bitmap image into packets for transmission.

    Args:
        inum (int): An identifier for the image, must be less than 65536.
        lines_per_packet (int): The number of lines of the image to include in each packet.
        img (bytes): The bytes representing the bitmap image.
        width (int, optional): The width of the image in pixels. Defaults to 1920.

    Yields:
        bytes: The packet containing a portion of the bitmap image.

    Raises:
        ValueError: If the image data does not align with the specified width and packet requirements,
                    or if the inum is out of valid range.
    """

    # Check given parameters
    check_packet_size(lines_per_packet, img, width)
    check_inum_size(inum)
    
    #split into packets
    lines = len(img) // (width//8)  # Assuming each line is 1920 pixels wide and 1 bit per pixel = 240 bytes
    num_packets = lines // lines_per_packet

    for i in range(num_packets):

        # calculate range of bytes to send
        start = i * lines_per_packet * (width//8)
        end = (i + 1) * lines_per_packet * (width//8)
        offset = lines_per_packet * i

        # create packet
        packet = (b'\x05\xAE\x00\x68' + 
                  i.to_bytes(2, byteorder='big') + 
                  inum.to_bytes(2, byteorder='big') + 
                  offset.to_bytes(6, byteorder='big') + 
                  img[start:end]
                  )
        
        yield packet

def check_packet_size(lines_per_packet: int, img: bytes, width:int=1920):
    
    # Check expected packet size
    payload_size = lines_per_packet * (width//8)

    if len(img) % (width//8) != 0:

        raise ValueError(
            f"""The number of bytes in img is not a multiple of the bytes per line.
            {len(img)} bytes, {width//8} bytes per line."""
            )
    
    if len(img) % (payload_size) != 0:

        raise ValueError(
            f"""The number of bytes in img is not a multiple of the expected packet size.
            {len(img)} bytes, {payload_size} bytes per packet."""
            )
    
    if (14 + payload_size) > 1500:
        raise ValueError(
            f"""Expected packet size exceed 1500.
            {14 + payload_size} bytes, 1500 bytes max."""
            )
    
def check_inum_size(inum: int):
        
        if inum > 65535:
            raise ValueError(
                f"""inum must be less than 65536."
                {inum} bytes, 65535 max."""
                )