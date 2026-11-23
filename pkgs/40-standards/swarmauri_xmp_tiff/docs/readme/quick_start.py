from swarmauri_xmp_tiff import TIFFXMP

handler = TIFFXMP()

try:
    handler.read_xmp(b"II*\x00...")
except NotImplementedError:
    print("TIFF XMP support is planned and currently unimplemented.")
