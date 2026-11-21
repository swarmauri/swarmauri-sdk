from swarmauri_xmp_mp4 import MP4XMP

handler = MP4XMP()

try:
    handler.write_xmp(b"\x00\x00\x00\x18ftypmp42...", "<rdf:RDF>...</rdf:RDF>")
except NotImplementedError:
    print("MP4 XMP support is forthcoming.")
