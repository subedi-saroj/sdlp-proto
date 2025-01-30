import scripts  
from PIL import Image

def add_buffer(img:Image, height, img_width, strip_width):
    
    # Calculate black-pixel buffer zones
    total_buffer = strip_width - img_width % strip_width # total amount of black pixel buffer needed
    buffer_left = total_buffer // 2 # left buffer
    buffer_right = total_buffer - buffer_left # right buffer... will have 1 more pixel if total_buffer is odd

    # Add buffer zones
    new_img = Image.new('L', (img_width + buffer_left + buffer_right, height), 0)
    new_img.paste(img, (buffer_left, 0))
    return new_img

def split_image(img:Image, height, width, strip_width):
    
    # Split image into a list of images
    
    num_images = width // strip_width

    for i in range(0, num_images):
        yield img.crop((i * strip_width, 0, (i + 1) * strip_width, height))

def multiply_image(img:Image, factor:int):

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

if __name__ == '__main__':
        
    file_path = r"..\test\test-repo\grayscale_test.bmp"

    strip_width = 960

    with Image.open(file_path) as img:
        width, height = img.size

        new_img = add_buffer(img, height, width, strip_width)
        width, height = new_img.size

        print(f"New image size: {new_img.size}\t|\t {strip_width}")

        imgs = split_image(new_img, height, width, strip_width)

        _ = next(imgs)
        _.show()
        
        gray_imgs = multiply_image(_, 256)

        for i, img in enumerate(gray_imgs):
            img.save(f"..\\test\\test-repo\\8-bit-splits\\{i + 1}.bmp")
            


