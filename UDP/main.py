from Projector import Projector
from Records import Records

from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

import asyncio
from zaber_motion import Units
from zaber_motion import Measurement
from zaber_motion.ascii import Connection
from zaber_motion.ascii import LockstepAxes

import os
import time
import cv2
from PIL import Image
import numpy as np



# open a file dialog to selct a single bmp image
tkinter_root = Tk()
tkinter_root.withdraw()
file_path = askopenfilename(filetypes=[("Bitmap files", "*.bmp")], initialdir=".\\")
if not file_path:
    print("No file selected")
    exit()

# read all the images from a folder
#Read the images and modify the images by adding black 1100 rows on top and 1100 rows on the bottom

def read_images_from_directory(directory, save_modified=True):
    # List all files in the given directory
    image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    images = []

    # Create a subdirectory for modified images
    modified_directory = os.path.join(directory, "modified_images")
    if save_modified and not os.path.exists(modified_directory):
        os.makedirs(modified_directory)

    for file in image_files:
        file_path = os.path.join(directory, file)
        
        # Check if the file is an image file
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            # Read the image using OpenCV
            image = cv2.imread(file_path)
            
            if image is not None:
                # Add 1100 black rows on top and bottom
                top_bottom_padding = 1100
                height, width, channels = image.shape
                black_top = np.zeros((top_bottom_padding, width, channels), dtype=np.uint8)
                black_bottom = np.zeros((top_bottom_padding, width, channels), dtype=np.uint8)
                modified_image = np.vstack((black_top, image, black_bottom))
                
                # Save the modified image to the modified directory
                if save_modified:
                    modified_image_path = os.path.join(modified_directory, file)
                    cv2.imwrite(modified_image_path, modified_image)
                
                # Append the modified image to the list
                images.append(modified_image)
            else:
                print(f"Unable to read image: {file}")
    
    return images


# def read_images_from_directory(directory):
#     image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
#     images = []
#     for file in image_files:
#         file_path = os.path.join(directory, file)
        
#         if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')): # Check if the file is an image file
            
#             image = cv2.imread(file_path) # Read the image using OpenCV
            
#             if image is not None: # Append the image to the list
#                 images.append(image)
#             else:
#                 print(f"Unable to read image: {file}")
#     return images

# convert the images to 1-bit bmp
def convert_to_1bit_bmp(image_list, output_directory):
    images = []
    for idx, img in enumerate(image_list):
        # Convert to grayscale
        img = img.convert('L')
        
        # Threshold to convert to binary (black and white)
        img = img.point(lambda x: 0 if x < 128 else 255, '1')
        
        img.append(img)
    return images

dir_path = r"C:\Users\dmale\OneDrive\Desktop\Personal\Active Research\DMPM Lab\Visitech Scrolling DLP Projector\1920x3280 Lattice Test"
images = read_images_from_directory(dir_path)
images = convert_to_1bit_bmp(images, dir_path)

image_size = 3240

# create a projector object
projector = Projector()

# prepare the projector
print(projector.send(Records.SetImageType(4).bytes()))
print(projector.send(Records.SetInumSize(image_size).bytes()))
print(projector.send(Records.ResetSeqNo().bytes()))
print(projector.send(Records.SetSequencerState(1, False).bytes()))
print(projector.send(Records.SetSequencerState(2, True).bytes()))

# send the images
for i, img in enumerate(images):
    image = projector.read_bmp_file(file_path, image_size)
    image_packets = projector.split_img_into_packets(0, 5, image)
    projector.send_image(image_packets)
    print(f"Done sending image{i}")

# ask for out of sequence packets
print(projector.send(Records.RequestSeqNoError().bytes()))

if input("continue y/n?:  ") == 'n':
    exit()

# home axes
with Connection.open_serial_port("COM3") as connection:
    connection.enable_alerts()

    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))

    device = device_list[0]

    y = device.get_lockstep(1) # lockstep axes 1 and 2 -> y

    if not y.is_enabled():
        y.enable(1, 2)

    x = device.get_axis(3) # axis 3 -> x

    # home the axes
    def home_axes():
        x_coroutine = x.move_absolute_async(0)
        y_coroutine = y.move_absolute_async(0)

        move_coroutine = asyncio.gather(x_coroutine, y_coroutine)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(move_coroutine)
    
    home_axes()

    velocity = 10.95
    #length = 196 # at inum size 20000
    length = 31.75 # at inum size 3240
    x.move_absolute(20, Units.LENGTH_MILLIMETRES)
    cont = True
    while cont:

        projector.start_sequencer()
        y.move_absolute(length, Units.LENGTH_MILLIMETRES, velocity=velocity, velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND)
        y.move_absolute(0, Units.LENGTH_MILLIMETRES, velocity=velocity, velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND)
        projector.stop_sequencer()
        
        cont = input("continue (y)?:  ") == 'y'

        


