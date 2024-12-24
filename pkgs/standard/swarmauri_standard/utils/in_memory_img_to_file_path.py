from PIL import Image

def in_memory_img_to_file_path(image: Image.Image, file_path: str) -> None:
    image.save(file_path)
