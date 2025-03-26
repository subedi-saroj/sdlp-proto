from PIL import Image
from typing import Iterator

def add_buffer(img:Image, strip_width) -> Image.Image:
    
    img_width, img_height = img.size
    
    # Calculate black-pixel buffer zones
    total_buffer = strip_width - img_width % strip_width # total amount of black pixel buffer needed
    buffer_left = total_buffer // 2 # left buffer
    buffer_right = total_buffer - buffer_left # right buffer... will have 1 more pixel if total_buffer is odd

    # Add buffer zones
    new_img = Image.new('L', (img_width + buffer_left + buffer_right, img_height), 0)
    new_img.paste(img, (buffer_left, 0))
    return new_img

def split_image(img:Image.Image, strip_width) -> Iterator[Image.Image]:
    
    width, height = img.size
    
    # Split image into a list of images
    num_images = width // strip_width

    for i in range(0, num_images):
        yield img.crop((i * strip_width, 0, (i + 1) * strip_width, height))

def multiply_image(img:Image, factor:int) -> Iterator[Image.Image]:

    """
    Multiply an image by a factor by splitting it into N images with thresholded grayscales.

    Args:
        img (Image): The image to be split.
        factor (int): The number of images to split the image into.
            WARNING: must be between 1 and 256. 0 will not generate any images.

    Yields:
        Image: The next image in the sequence of images. The image is split into N images with thresholded grayscales, where the threshold is calculated as i * 255 // factor.
    """
    for i in range(0, factor):

        threshold = i * 255 // factor

        yield img.point(lambda p: 255 if p > threshold else 0)

def stitch_images(images:Iterator[Image.Image]) -> Image.Image:
    """
    Stitch a list of images together vertically.

    Args:
        images (Iterator[Image.Image]): The images to be stitched together.

    Returns:
        Image.Image: The stitched image.
    """

    new_img = Image.new('L', (1920, 17280))

    y_offset = 0
    for img in images:
        new_img.paste(img, (0, y_offset))
        y_offset += img.height

    return new_img



if __name__ == '__main__':
        
    file_path = r"..\test\test-grayscale\1920x4320_gs4_B.bmp"

    strip_width = 1920

    with Image.open(file_path) as img:   

        imgs = multiply_image(img, 4)
        strip = stitch_images(imgs)
        print(strip.size)
        strip.save(r"..\test\test-grayscale\1920x4320_gs4_B_stitched.bmp")
            


