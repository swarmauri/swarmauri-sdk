from pathlib import Path

from swarmauri_xmp_svg import SVGXMP

handler = SVGXMP()
svg_path = Path("example.svg")
xmp_packet = (
    "<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"
)

# Insert metadata into the SVG root element
updated_bytes = handler.write_xmp(svg_path.read_bytes(), xmp_packet)
svg_path.write_bytes(updated_bytes)

# Read the packet back
restored_xml = handler.read_xmp(updated_bytes)
print(restored_xml)

# Remove it if necessary
clean_bytes = handler.remove_xmp(updated_bytes)
