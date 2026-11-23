from pathlib import Path

from EmbedXMP import EmbedXMP, embed, embed_file, read, read_file_xmp

manager = EmbedXMP()
image = Path("example.png")
packet = (
    "<x:xmpmeta xmlns:x='adobe:ns:meta/'>"
    "<rdf:RDF>...</rdf:RDF></x:xmpmeta>"
)

# Embed into the file in place.
embed_file(image, packet)

# Inspect metadata via the manager API.
xmp_text = manager.read(image.read_bytes(), str(image))
print(xmp_text)

# Remove metadata from the file when it is no longer required.
manager.remove(image.read_bytes(), str(image))
