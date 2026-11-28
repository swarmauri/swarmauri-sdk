from pathlib import Path

from swarmauri_xmp_gif import GIFXMP

handler = GIFXMP()
gif_path = Path("example.gif")
xmp_packet = (
    "<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"
)

# Embed using an application extension block
updated_bytes = handler.write_xmp(gif_path.read_bytes(), xmp_packet)
gif_path.write_bytes(updated_bytes)

# Retrieve the RDF/XML payload
restored_xml = handler.read_xmp(updated_bytes)
print(restored_xml)

# Remove the extension again
clean_bytes = handler.remove_xmp(updated_bytes)
