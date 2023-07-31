from PIL import Image


def adjust_image_size(image, target_size):
    image.thumbnail(target_size)

def resize_and_split_image(input_path):
    try:
        # Open the original image
        image = Image.open(input_path)

        # Resize the image to 3240×1440 with 'Lanczos' filter
        new_size = (3240, 1440)
        resized_image = image.resize(new_size, Image.LANCZOS)

        # Save the resized image with adjusted size
        adjust_image_size(resized_image, (1080, 480))
        resized_image.save(input_path.replace(".png", "_adjusted.png"))

        # Split the image into three 1080×1440 images
        width, height = resized_image.size
        split_width = width // 3

        for i in range(3):
            left = i * split_width
            right = (i + 1) * split_width
            split_image = resized_image.crop((left, 0, right, height))

            # Generate the filename: add "_1", "_2", "_3" to the original filename
            output_path = input_path.replace(".png", f"_{i+1}.png")

            # Save the split image
            split_image.save(output_path)

        print("Image processing completed!")
    except Exception as e:
        print(f"Error processing the image: {e}")



# 调用方法，传入图片的全路径
image_path = r"D:\油管资料\露营\AtikAilesi\2023-06-16_YZENADIRIMIZATERASYAPTIKlGlzerinde24SaatKamp\YZENADIRIMIZATERASYAPTIKlGlzerinde24SaatKamp.png"
resize_and_split_image(image_path)
