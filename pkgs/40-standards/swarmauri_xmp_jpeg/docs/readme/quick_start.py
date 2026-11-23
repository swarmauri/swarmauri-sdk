from pathlib import Path

from swarmauri_xmp_jpeg import JPEGXMP

handler = JPEGXMP()
photo_path = Path("example.jpg")
xmp_packet = (
    "<x:xmpmeta xmlns:x='adobe:ns:meta/'>"
    "<rdf:RDF>...</rdf:RDF></x:xmpmeta>"
)

# Insert the packet right after the SOI marker
updated_bytes = handler.write_xmp(photo_path.read_bytes(), xmp_packet)
photo_path.write_bytes(updated_bytes)

# Confirm it can be recovered later
restored_xml = handler.read_xmp(updated_bytes)
print(restored_xml)

# Strip the packet if needed
clean_bytes = handler.remove_xmp(updated_bytes)
