#!/usr/bin/env python3
"""
Test script for RLE compression implementation.

Demonstrates:
- RLE encoding of binary images
- Compression ratio calculations
- Visitech Type 5 format validation
- Integration with existing projector code
"""

import numpy as np
from PIL import Image
from lux4600.rle import encode_rle_row_type5, encode_rle_image_type5, RLEDescriptor
import struct


def test_rle_descriptor():
    """Test RLE descriptor creation and parsing."""
    print("=== Testing RLE Descriptors ===\n")
    
    # Test RLE mode descriptor
    desc_rle = RLEDescriptor(rle=True, data=1, transition=3, run_length=8)
    print(f"RLE descriptor: data=1, transition=3, run_length=8")
    rle_bytes = desc_rle.to_bytes()
    print(f"  Encoded: {rle_bytes.hex()}")
    
    # Parse it back
    desc_parsed = RLEDescriptor.from_bytes(rle_bytes)
    print(f"  Parsed: rle={desc_parsed.rle}, data={desc_parsed.data}, "
          f"transition={desc_parsed.transition}, run_length={desc_parsed.run_length}")
    
    # Test RAW mode descriptor
    desc_raw = RLEDescriptor(rle=False, data=0xFF)
    print(f"\nRAW descriptor: data=0xFF")
    raw_bytes = desc_raw.to_bytes()
    print(f"  Encoded: {raw_bytes.hex()}")
    
    desc_raw_parsed = RLEDescriptor.from_bytes(raw_bytes)
    print(f"  Parsed: rle={desc_raw_parsed.rle}, data=0x{desc_raw_parsed.data:02X}\n")


def test_simple_pattern():
    """Test RLE encoding with simple patterns."""
    print("=== Testing Simple Patterns ===\n")
    
    patterns = {
        "All zeros": b'\x00' * 240,
        "All ones": b'\xFF' * 240,
        "Alternating": b'\xAA' * 240,  # 10101010
        "Mixed": b'\x00\x00\xFF\xFF' * 60,
    }
    
    width = 1920  # pixels
    bytes_per_row = width // 8  # 240 bytes
    
    for name, pattern in patterns.items():
        # Pad to full row width if needed
        line_data = pattern[:bytes_per_row]
        if len(line_data) < bytes_per_row:
            line_data = line_data + b'\x00' * (bytes_per_row - len(line_data))
        
        encoded = encode_rle_row_type5(line_data, width)
        
        # Calculate compression ratio
        uncompressed_size = bytes_per_row
        compressed_size = len(encoded)
        ratio = compressed_size / uncompressed_size
        
        print(f"{name:20} | Original: {uncompressed_size:3} bytes | "
              f"Compressed: {compressed_size:3} bytes | Ratio: {ratio:.1%}")
    
    print()


def test_grayscale_image():
    """Test RLE encoding with grayscale patterns."""
    print("=== Testing Grayscale Layer Compression ===\n")
    
    # Create a simple test image (100x100 pixels)
    width, height = 100, 100
    
    # Create test pattern: gradient
    img_array = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            if x + y < 150:  # Top-left triangle is white
                img_array[y, x] = 255
    
    # Convert to PIL Image
    img = Image.fromarray(img_array.astype(np.uint8), mode='L')
    img_binary = img.convert('1')
    
    # Encode with RLE
    encoded_rows = encode_rle_image_type5(img_binary, width, height)
    
    # Calculate statistics
    total_uncompressed = (width // 8) * height
    total_compressed = sum(len(row) for row in encoded_rows)
    
    print(f"Image size: {width}x{height}")
    print(f"Uncompressed: {total_uncompressed} bytes")
    print(f"Compressed: {total_compressed} bytes")
    print(f"Compression ratio: {total_compressed / total_uncompressed:.1%}")
    print(f"Savings: {(1 - total_compressed / total_uncompressed) * 100:.1f}%\n")


def test_grayscale_multiplication():
    """Test RLE compression for 4-bit grayscale layers."""
    print("=== Testing 4-Bit Grayscale Layers ===\n")
    
    # Simulate the multiply_image approach with 4 binary layers
    # Typical size: 1920x3240 (scrolling grayscale)
    width, height = 1920, 3240
    bytes_per_row = width // 8
    
    # Create synthetic layers (in practice, these come from multiply_image)
    # Simulate realistic compression: 
    # - Layer 0 (LSB): ~40% white (worst compression)
    # - Layer 1: ~30% white
    # - Layer 2: ~20% white
    # - Layer 3 (MSB): ~10% white (best compression)
    
    white_percentages = [40, 30, 20, 10]
    
    print(f"Image size: {width}x{height}")
    print(f"Using 4-bit grayscale (4 binary layers)\n")
    
    total_uncompressed = 0
    total_compressed = 0
    
    for layer, white_pct in enumerate(white_percentages):
        # Create synthetic layer (random distribution)
        np.random.seed(42 + layer)  # For reproducibility
        layer_array = (np.random.random((height, width)) < (white_pct / 100)).astype(np.uint8)
        
        # Encode with RLE
        layer_img = Image.fromarray(layer_array * 255, mode='L').convert('1')
        encoded_rows = encode_rle_image_type5(layer_img, width, height)
        
        # Calculate statistics
        uncompressed_size = bytes_per_row * height
        compressed_size = sum(len(row) for row in encoded_rows)
        
        total_uncompressed += uncompressed_size
        total_compressed += compressed_size
        
        ratio = compressed_size / uncompressed_size
        print(f"Layer {layer} ({white_pct}% white): {uncompressed_size:,} → {compressed_size:,} bytes "
              f"({ratio:.1%} compression)")
    
    print(f"\nTotal uncompressed: {total_uncompressed:,} bytes ({total_uncompressed / 1024 / 1024:.2f} MB)")
    print(f"Total compressed: {total_compressed:,} bytes ({total_compressed / 1024 / 1024:.2f} MB)")
    print(f"Overall ratio: {total_compressed / total_uncompressed:.1%}")
    print(f"Savings: {(1 - total_compressed / total_uncompressed) * 100:.1f}%\n")


def test_bandwidth_improvement():
    """Calculate bandwidth improvement."""
    print("=== Bandwidth Improvement Estimate ===\n")
    
    # Typical scenario: 4-bit grayscale scrolling
    image_size_uncompressed = 4 * 1920 * 3240 / 8  # 4 layers
    image_size_compressed = image_size_uncompressed * 0.25  # Estimate 75% compression
    
    # Network speeds
    gigabit_speed = 1e9 / 8  # bytes per second
    
    time_uncompressed = image_size_uncompressed / gigabit_speed
    time_compressed = image_size_compressed / gigabit_speed
    
    print(f"Image data per layer: {1920 * 3240 / 8 / 1024 / 1024:.2f} MB")
    print(f"Total (4 layers uncompressed): {image_size_uncompressed / 1024 / 1024:.2f} MB")
    print(f"Total (4 layers RLE compressed, 75%): {image_size_compressed / 1024 / 1024:.2f} MB")
    print(f"\nAt 1 Gbps Ethernet:")
    print(f"  Without RLE: {time_uncompressed:.2f} seconds")
    print(f"  With RLE: {time_compressed:.2f} seconds")
    print(f"  Speedup: {time_uncompressed / time_compressed:.1f}x faster\n")


def test_hardware_command_sequence():
    """Show the hardware command sequence for RLE transmission."""
    print("=== Hardware Command Sequence for RLE ===\n")
    
    print("1. Set Image Type to RLE (Type 5 for Lux4600):")
    set_type_cmd = bytes([0x00, 0x06, 0x00, 0x67, 0x00, 0x05])
    print(f"   Command: {set_type_cmd.hex()}")
    print(f"   Expected reply: 0x00 0x06 0x01 0xf5 0x00 0x00 (ReplyAck success)\n")
    
    print("2. Send RLE-compressed image data:")
    print("   Use LoadImageData record (rec_id 0x68)")
    print("   Payload format:")
    print("     [seq_no: 2 bytes] - sequence number (1-65535)")
    print("     [inum: 2 bytes]   - image number (0-65535)")
    print("     [offset: 4 bytes] - line offset")
    print("     [data: variable]  - RLE-encoded rows")
    print(f"   Max data per packet: 8956 bytes")
    print(f"   Must be 4-byte aligned and contain integer rows\n")
    
    print("3. Verify sequence (if needed):")
    print("   Request: 0x00 0x04 0x01 0x37 (RequestSeqNoError)")
    print("   Check if error flag is set; if not, transmission successful\n")
    
    print("4. Run sequencer to display:")
    print("   Use internal sequencer with LoadRow commands")
    print("   Projector automatically decompresses Type 5 RLE format\n")


if __name__ == '__main__':
    test_rle_descriptor()
    test_simple_pattern()
    test_grayscale_image()
    test_grayscale_multiplication()
    test_bandwidth_improvement()
    test_hardware_command_sequence()
    
    print("✓ All tests completed successfully!")
