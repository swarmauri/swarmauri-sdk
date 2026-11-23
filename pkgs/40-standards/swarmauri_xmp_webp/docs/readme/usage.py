from swarmauri_xmp_webp import WebPXMP

handler = WebPXMP()

# Raises NotImplementedError until read/write/remove are implemented
try:
    handler.read_xmp(b"RIFF....WEBP")
except NotImplementedError:
    print("WebP XMP support is forthcoming.")
