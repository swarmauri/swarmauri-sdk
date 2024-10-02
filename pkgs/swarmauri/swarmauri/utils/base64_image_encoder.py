import re
import base64


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return f'data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode("utf-8")}'


def is_url(string):
    # Regular expression pattern to match a typical URL structure
    url_pattern = re.compile(
        r"^(https?://)?"  # Optional http or https
        r"([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}"  # Domain name
        r"(/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=%]*)?$"  # Optional path
    )
    return re.match(url_pattern, string) is not None
