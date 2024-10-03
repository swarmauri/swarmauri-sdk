import re
import base64


def encode_file(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def is_url(string):
    # Regular expression pattern to match a typical URL structure
    url_pattern = re.compile(
        r"^(https?://)?"  # Optional http or https
        r"([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}"  # Domain name
        r"(/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=%]*)?$"  # Optional path
    )
    return re.match(url_pattern, string) is not None
