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
    images = []

    num_images = width // strip_width

    for i in range(0, num_images):
        images.append(img.crop((i * strip_width, 0, (i + 1) * strip_width, height)))
        
    return images

if __name__ == '__main__':
        
    file_path = r"..\test\test-repo\grayscale_split_test.bmp"

    strip_width = 960

    with Image.open(file_path) as img:
        width, height = img.size

        new_img = add_buffer(img, height, width, strip_width)
        width, height = new_img.size

        print(f"New image size: {new_img.size}\t|\t {strip_width}")

        imgs = split_image(new_img, height, width, strip_width)
        
        for img in imgs:
            input("Press Enter to display img...")
            img.show()
            


