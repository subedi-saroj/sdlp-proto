import warnings
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
import cv2
import os
from PIL import Image

def sequence_to_packets(data:bytes, chunk_size=1440) -> bytes:
    '''Splits a sequence into packets for transmission.'''
    
    # check chunk size
    if chunk_size > 1500:
        warnings.warn("Chunk size exceeds 1500.")
    if chunk_size % 8 != 0:
        raise ValueError("Chunk size must be a multiple of 8.")
    
    packets = []
    while len(data) > chunk_size:
        packets.append(data[:chunk_size])
        data = data[chunk_size:]
    packets.append(data)
    
    for i in range(len(packets)):
        len_chunk = len(packets[i]).to_bytes(2, byteorder='big')
        i_of_total = (i+1).to_bytes(2, byteorder='big') + len(packets).to_bytes(2, byteorder='big')
        packets[i] = b'\x00\x69' + i_of_total + len_chunk + packets[i]
        packets[i] = (len(packets[i]) + 2).to_bytes(2, byteorder='big') + packets[i]
    
    return packets

def open_sequence() -> bytes:
    '''Opens a file dialog to select a sequence file and returns the bytes.'''
    # root = Tk()
    # root.withdraw()
    # file_path = askopenfilename(filetypes=[("Sequence files", "*.seq;*.txt")])
    file_path = r"test\multi-image-scroll-seq.txt"

    with open(file_path, 'rb') as file:
        sequence = file.read()
    return sequence

def bmp_to_packets(inum: int, lines_per_packet: int, data: bytes, width:int=1920) -> list:
    '''Splits a bitmap image into packets for transmission.'''
    
    # Check expected packet size
    payload_size = lines_per_packet * (width//8)

    if len(data) % (width//8) != 0:
        raise ValueError("The number of bytes in data is not a multiple of the bytes per line.")
    if len(data) % (payload_size) != 0:
        raise ValueError("The number of bytes in data is not a multiple of the expected packet size.")
    if (14 + payload_size) > 1500:
        warnings.warn("Expected packet size exceed 1500.")
    if inum > 65535:
        raise ValueError("inum must be less than 65536.")


    #split into packets
    packets = []
    lines = len(data) // (width//8)  # Assuming each line is 1920 pixels wide and 1 bit per pixel = 240 bytes
    num_packets = lines // lines_per_packet

    for i in range(num_packets):
        start = i * lines_per_packet * (width//8)
        end = (i + 1) * lines_per_packet * (width//8)
        offset = lines_per_packet*i
        packet = b'\x05\xAE\x00\x68' + i.to_bytes(2, byteorder='big') + inum.to_bytes(2, byteorder='big') + offset.to_bytes(6, byteorder='big') + data[start:end]
        packets.append(packet)
    return packets

def to_bmp(file_path:str, size:int=1080, width:int=1920) -> bytes:
    '''Converts an image file to BMP format and returns the bytes.

    Args:
        file_path (str): The path to the image file.
        size (int, optional): The desired size of the BMP image. Defaults to 1080.
        width (int, optional): The desired width of the BMP image. Defaults to 1920.

    Returns:
        bytes: The bytes representing the BMP image.

    Raises:
        ValueError: If the number of bytes in the image does not match the specified size and width.
    '''
    # Resize and convert the image to 1-bit mode (black and white)
    with Image.open(file_path) as img:
        img = img.resize((width, size))
        bmp_data = img.convert("1").tobytes()

    # Check the number of bytes in the image (should never raise a ValueError due to resize)    
    expected_bytes = size * (width // 8)

    if len(bmp_data) != expected_bytes:
        raise ValueError("The number of bytes in the image does not match the specified size and width.")

    return bmp_data
    
def open_image(size:int=1080, width:int=1920) -> bytes:
    '''Opens a file dialog to select an image file and returns the bytes.'''
    root = Tk()
    root.withdraw()
    file_path = askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])

    # Convert the image to 1-bit BMP format
    bmp_data = to_bmp(file_path, size, width)
    return bmp_data

def open_images(size:int=1080, width:int=1920) -> list[bytes]:
    '''Opens a file dialog to select a folder containing sliced images and returns a list of bytes.

    Args:
        directory (str): The path to the directory containing the images.
        size (int, optional): The desired size of the images. Defaults to 1080.
        width (int, optional): The desired width of the images. Defaults to 1920.

    Returns:
        list[bytes]: A list of bytes representing the images.
    '''

    #open a file dialog to select a folder
    root = Tk()
    root.withdraw()
    directory = askdirectory()
    if not directory:
        return
    image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # sort image files based on the numerical order of filenames, e.g. 9 is before 10
    image_files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
    
    # convert each image to 1-bit BMP format and add to the list
    images = []
    for file in image_files:
        file_path = os.path.join(directory, file)
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')): # Check if the file is an image file
            
            image = to_bmp(file_path, size, width)
            images.append(image)
    return images
