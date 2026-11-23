from pathlib import Path

from swarmauri_xmp_png import PNGXMP

handler = PNGXMP()
image_path = Path("example.png")
xmp_packet = """<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"""

# Embed an XMP packet
updated_bytes = handler.write_xmp(image_path.read_bytes(), xmp_packet)
image_path.write_bytes(updated_bytes)

# Verify the packet can be recovered
restored_xml = handler.read_xmp(updated_bytes)
print(restored_xml)

# Remove XMP if necessary
clean_bytes = handler.remove_xmp(updated_bytes)
