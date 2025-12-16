

"""
Run-Length Encoding for binary image data (Visitech RLE Format).

Provides utilities for compressing 1-bit binary images using Visitech RLE format (Type 5)
specifically designed for the Lux4600 projector. This format reduces bandwidth requirements
when transmitting images.

Reference:
    - Lux4600/4700 Software Interface Document, Section 7.3
    - RLE Compression Scheme for lb4k6 - image type 5
"""

import struct
from typing import List, Tuple, Union
from PIL import Image
import numpy as np


class RLEDescriptor:
    """16-bit RLE descriptor for Visitech Type 5 format."""
    
    def __init__(self, rle: bool, data: int, transition: int = 0, run_length: int = 0):
        """
        Create RLE descriptor.
        
        Args:
            rle: True for RLE mode, False for RAW mode
            data: Bit value (0 or 1) for RLE mode, or raw byte for RAW mode
            transition: Transition position (bits 13:11) - valid only for RLE mode
            run_length: Run length in bytes (bits 10:0) - valid only for RLE mode
        """
        self.rle = rle
        self.data = data
        self.transition = transition & 0x7  # 3 bits
        self.run_length = run_length & 0x7FF  # 11 bits
    
    def to_bytes(self) -> bytes:
        """Convert descriptor to 2-byte big-endian format."""
        if self.rle:
            # RLE mode: bits 15=1, 14=data, 13:11=transition, 10:0=run_length
            word = (1 << 15) | (self.data << 14) | (self.transition << 11) | self.run_length
        else:
            # RAW mode: bits 15=0, bits 14:0=block length (number of raw bytes that follow)
            word = self.run_length & 0x7FFF
        
        # Big-endian 16-bit word
        return struct.pack('>H', word)
    
    @staticmethod
    def from_bytes(data: bytes) -> 'RLEDescriptor':
        """Parse 2-byte descriptor."""
        word = struct.unpack('>H', data)[0]
        rle = bool(word & 0x8000)
        if rle:
            data_val = (word >> 14) & 1
            transition = (word >> 11) & 0x7
            run_length = word & 0x7FF
            return RLEDescriptor(True, data_val, transition, run_length)
        else:
            data_val = word & 0xFF
            return RLEDescriptor(False, data_val)


def encode_rle_row_type5(line_data: bytes, width: int) -> bytes:
    """
    Encode a single binary row using Visitech RLE Type 5 (lb4k6) bit-level format.
    
    Type 5 RLE format chains bit-run pairs across the entire row. Each 16-bit descriptor 
    encodes TWO consecutive runs:
      - Bit 0: data A (0 or 1)
      - Bits 10-1: run length A (in BITS)
      - Bit 11: data B
      - Bits 15-12: run length B (in BITS)
    
    Descriptors chain: bits flow from one descriptor to the next until the row 
    is complete (1920 bits). The last descriptor ends exactly at row boundary.
    
    Args:
        line_data: Binary row data (width/8 bytes)
        width: Pixel width (for validation, typically 1920)
    
    Returns:
        RLE-encoded row as bytes (chained 16-bit descriptors)
    """
    bytes_per_line = width // 8
    if len(line_data) != bytes_per_line:
        raise ValueError(f"Expected {bytes_per_line} bytes, got {len(line_data)}")
    
    # Convert bytes to bit array (MSB first)
    bit_array = np.unpackbits(np.frombuffer(line_data, dtype=np.uint8), bitorder='big')
    
    encoded = bytearray()
    bit_pos = 0
    
    while bit_pos < len(bit_array):
        # Read first run (full length, no cap yet)
        current_bit = bit_array[bit_pos]
        run_length_a_full = 0
        temp_pos = bit_pos
        while temp_pos < len(bit_array) and bit_array[temp_pos] == current_bit:
            run_length_a_full += 1
            temp_pos += 1
        
        data_a = current_bit & 1
        
        # Cap run_length_a to 10 bits (max 1023)
        run_length_a = min(run_length_a_full, 1023)
        bit_pos += run_length_a  # Advance by actual encoded length
        
        # Read second run (if any bits remain and we used full run_a)
        if bit_pos < len(bit_array) and run_length_a == run_length_a_full:
            current_bit = bit_array[bit_pos]
            run_length_b_full = 0
            temp_pos = bit_pos
            while temp_pos < len(bit_array) and bit_array[temp_pos] == current_bit:
                run_length_b_full += 1
                temp_pos += 1
            
            data_b = current_bit & 1
            # Cap run_length_b to 4 bits (max 15)
            run_length_b = min(run_length_b_full, 15)
            bit_pos += run_length_b  # Advance by actual encoded length
        else:
            run_length_b = 0
            data_b = 0
        
        # Pack into 16-bit descriptor:
        # Bit 0: data_a
        # Bits 10-1: run_length_a (10 bits)
        # Bit 11: data_b
        # Bits 15-12: run_length_b (4 bits)
        word = (
            (data_a & 1) |
            ((run_length_a & 0x3FF) << 1) |
            ((data_b & 1) << 11) |
            ((run_length_b & 0x0F) << 12)
        )
        
        encoded.extend(struct.pack('<H', word))
    
    return bytes(encoded)


def encode_rle_image_type5(image_data: Union[Image.Image, np.ndarray], 
                           width: int, height: int) -> List[bytes]:
    """
    Encode complete 1-bit image using Visitech RLE Type 5 format.
    
    Processes image row-by-row, encoding each row independently.
    
    Args:
        image_data: PIL Image (mode '1') or numpy array (dtype uint8, values 0/255)
        width: Image width in pixels (typically 1920)
        height: Image height in pixels
    
    Returns:
        List of encoded rows (each row is bytes of RLE descriptors)
    """
    if isinstance(image_data, Image.Image):
        if image_data.mode != '1':
            image_data = image_data.convert('1')
        img_array = np.array(image_data, dtype=bool).astype(np.uint8)
    else:
        img_array = np.asarray(image_data, dtype=np.uint8)
        if img_array.max() > 1:
            img_array = (img_array > 0).astype(np.uint8)
    
    if img_array.shape != (height, width):
        raise ValueError(f"Expected shape ({height}, {width}), got {img_array.shape}")
    
    # Pack bits: 8 pixels per byte
    encoded_rows = []
    bytes_per_row = (width + 7) // 8
    
    for row_idx in range(height):
        row_bits = img_array[row_idx]
        # Pad to byte boundary
        row_bits_padded = np.pad(row_bits, (0, 8 - (width % 8))) if width % 8 else row_bits
        # Pack into bytes
        row_bytes = np.packbits(row_bits_padded[:bytes_per_row * 8]).tobytes()
        # Encode this row
        encoded_row = encode_rle_row_type5(row_bytes, width)
        encoded_rows.append(encoded_row)
    
    return encoded_rows


def encode_rle(data: bytes, width: int, height: int):
    """
    [LEGACY] Encode binary image data row-by-row using basic run-length encoding.
    
    .. deprecated:: Use encode_rle_image_type5() for Visitech Type 5 format
    
    Yields RLE-encoded rows as a generator for memory efficiency.
    
    Args:
        data: Binary image data as bytes (width bytes per row)
        width: Row width in bytes
        height: Image height in rows
    
    Yields:
        Encoded rows as bytes
    """
    for row_idx in range(height):
        line_start = row_idx * width
        line_end = line_start + width
        line_data = data[line_start:line_end]
        
        yield rle_encode_line(line_data)


def rle_encode_line(line: bytes) -> bytes:
    """
    [LEGACY] Encode a single binary line using basic value-count encoding.
    
    .. deprecated:: Use encode_rle_row_type5() for Visitech Type 5 format
    
    Format: [value, count, value, count, ...]
    where value is the byte value and count is consecutive occurrences.
    
    Args:
        line: Single line of binary data as bytes
    
    Returns:
        RLE-encoded line as bytes
    """
    if not line:
        return b''
    
    encoded_packet = b''
    count = 1
    prev = line[0]

    for byte in line[1:]:
        if byte == prev:
            count += 1
        else:
            encoded_packet += bytes([prev, count])
            count = 1
            prev = byte

    encoded_packet += bytes([prev, count])

    return encoded_packet
 
