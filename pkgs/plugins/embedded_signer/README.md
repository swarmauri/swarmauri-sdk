<p align="center">
  <img src="../../../assets/swarmauri.brand.theme.svg" alt="Swarmauri logotype" width="420" />
</p>

<h1 align="center">EmbeddedSigner</h1>

<p align="center">
  <a href="https://img.shields.io/pypi/dm/EmbeddedSigner?style=for-the-badge"><img src="https://img.shields.io/pypi/dm/EmbeddedSigner?style=for-the-badge" alt="PyPI - Downloads" /></a>
  <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/embedded_signer/"><img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/embedded_signer.svg?style=for-the-badge" alt="Repo views" /></a>
  <a href="https://img.shields.io/pypi/pyversions/EmbeddedSigner?style=for-the-badge"><img src="https://img.shields.io/pypi/pyversions/EmbeddedSigner?style=for-the-badge" alt="Supported Python versions" /></a>
  <a href="https://img.shields.io/pypi/l/EmbeddedSigner?style=for-the-badge"><img src="https://img.shields.io/pypi/l/EmbeddedSigner?style=for-the-badge" alt="License" /></a>
  <a href="https://img.shields.io/pypi/v/EmbeddedSigner?style=for-the-badge"><img src="https://img.shields.io/pypi/v/EmbeddedSigner?style=for-the-badge" alt="Latest release" /></a>
</p>

EmbeddedSigner composes the dynamic XMP embedding utilities from
[`EmbedXMP`](../EmbedXMP) with the signing facade exposed by
[`MediaSigner`](../media_signer). It embeds metadata into media assets and then
routes signing requests to the appropriate media-aware signer in either
attached or detached mode. The class orchestrates key provider plugins so that
opaque key references can be resolved automatically before signatures are
produced.

## Features

- **One-shot embed & sign** – inject XMP metadata and produce signatures with a
  single call.
- **Media-aware detection** – delegates to all registered `EmbedXmpBase`
  handlers so PNG, GIF, JPEG, SVG, WEBP, TIFF, PDF, and MP4 assets are
  processed consistently.
- **Pluggable signers** – forwards signing requests to every
  `SigningBase` registered with `MediaSigner`, including CMS, JWS, OpenPGP, PDF,
  and XMLDSig providers.
- **Key provider integration** – loads providers from the
  `swarmauri.key_providers` entry point group and resolves opaque key reference
  strings (e.g. `local://kid@2`) before invoking a signer.
- **Attached or detached output** – toggle between embedded signatures or
  detached artifacts via a simple flag.
- **File and byte workflows** – operate on in-memory payloads or update files
  on disk with helpers for embedding, reading, removing, and signing.
- **Command line tooling** – bundle a ready-to-use `embedded-signer` CLI for
  ad-hoc embedding, signing, and combined workflows.

## Installation

### Using `uv`

```bash
uv add EmbeddedSigner
```

Optional dependencies align with the available key providers, EmbedXMP handlers,
and MediaSigner backends:

```bash
uv add "EmbeddedSigner[local]"      # enable LocalKeyProvider resolution
uv add "EmbeddedSigner[memory]"     # enable InMemoryKeyProvider resolution
uv add "EmbeddedSigner[xmp_png]"    # add PNG embedding support
uv add "EmbeddedSigner[xmp_all]"    # install every EmbedXMP handler
uv add "EmbeddedSigner[signing_pdf]"  # enable PDF signer backend
uv add "EmbeddedSigner[signing_all]"  # install every MediaSigner backend
uv add "EmbeddedSigner[full]"       # bring in all extras and key providers
```

### Using `pip`

```bash
pip install EmbeddedSigner
```

Extras mirror the `uv` workflow:

```bash
pip install "EmbeddedSigner[local]"
pip install "EmbeddedSigner[memory]"
pip install "EmbeddedSigner[xmp_png]"
pip install "EmbeddedSigner[xmp_all]"
pip install "EmbeddedSigner[signing_pdf]"
pip install "EmbeddedSigner[signing_all]"
pip install "EmbeddedSigner[full]"
```

### Extras overview

| Extra name | Purpose |
| --- | --- |
| `local` / `memory` | Enable Swarmauri key provider resolution for local filesystem and in-memory secrets. |
| `xmp_gif`, `xmp_jpeg`, `xmp_png`, `xmp_svg`, `xmp_webp`, `xmp_tiff`, `xmp_pdf`, `xmp_mp4` | Pull in the corresponding `swarmauri_xmp_*` handler so EmbedXMP can embed metadata for that media format. |
| `xmp_all` | Install every EmbedXMP media handler dependency at once. |
| `signing_cms`, `signing_jws`, `signing_openpgp`, `signing_pdf`, `signing_xmld` | Add the matching MediaSigner backend plugin for CMS, JWS, OpenPGP, PDF, or XMLDSig signing. |
| `signing_all` | Install all MediaSigner backends together. |
| `full` | Bring in every key provider, EmbedXMP handler, and MediaSigner backend for maximum coverage. |

## Usage

```python
import asyncio
from pathlib import Path

from EmbeddedSigner import EmbedSigner

xmp_xml = """
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""/>
  </rdf:RDF>
</x:xmpmeta>
""".strip()

async def embed_and_sign() -> None:
    signer = EmbedSigner()
    media_bytes = Path("image.png").read_bytes()
    embedded, signatures = await signer.embed_and_sign_bytes(
        media_bytes,
        fmt="JWSSigner",
        xmp_xml=xmp_xml,
        key={"kind": "raw", "key": b"\x00" * 32},
        path="image.png",
        attached=True,
        signer_opts={"alg": "HS256"},
    )
    Path("image.signed.png").write_bytes(embedded)
    print(signatures[0].mode)  # "attached"

asyncio.run(embed_and_sign())
```

### Key provider integration

When you install a key provider plugin such as
`swarmauri_keyprovider_local`, EmbeddedSigner can resolve string key references
on the fly:

```python
signer = EmbedSigner(key_provider_name="LocalKeyProvider")
embedded, signatures = await signer.embed_and_sign_file(
    Path("report.pdf"),
    fmt="PDFSigner",
    xmp_xml=xmp_xml,
    key="LocalKeyProvider://a1b2c3@1",
    attached=False,
    signer_opts={"alg": "SHA256"},
)
```

EmbeddedSigner parses the opaque reference, looks up the provider by name, and
retrieves the specified key version using the provider's asynchronous API.

### File helpers

`EmbedSigner` offers mirrored helpers that operate on file paths when you need
to persist updates directly on disk:

```python
signer = EmbedSigner()

# Embed metadata into a file and write it back in place.
signer.embed_file("image.png", xmp_xml)

# Read embedded metadata without materialising the bytes in memory.
print(signer.read_xmp_file("image.png"))

# Remove metadata and persist the stripped bytes to a new path.
signer.remove_xmp_file("image.png", write_back=True)

# Sign file contents without manual IO boilerplate.
signatures = asyncio.run(
    signer.sign_file(
        "image.png",
        fmt="JWSSigner",
        key="LocalKeyProvider://img-key",
        attached=True,
    )
)
```

### Command line interface

Installing the package exposes an `embedded-signer` executable that wraps the
most common workflows:

```bash
# Embed metadata from a file into an image in place.
embedded-signer embed example.png --xmp-file metadata.xmp

# Read metadata to stdout (non-zero exit if none is embedded).
embedded-signer read example.png

# Remove metadata and write the result to a new file.
embedded-signer remove example.png --output clean.png

# Sign using a key reference exposed by a provider plugin.
embedded-signer sign example.png --format JWSSigner --key-ref local://img-key

# Embed and sign in one step, writing signatures to JSON.
embedded-signer embed-sign example.png \
  --xmp-file metadata.xmp \
  --format JWSSigner \
  --key-ref local://img-key \
  --signature-output signatures.json
```

## Development

1. Install development dependencies:

   ```bash
   uv pip install -e ".[dev]"
   ```

2. Format and lint code with `ruff`:

   ```bash
   uv run ruff format .
   uv run ruff check . --fix
   ```

3. Run the unit tests in isolation:

   ```bash
   uv run --package EmbeddedSigner --directory plugins/embedded_signer pytest
   ```

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/embedded_signer>
- Documentation: <https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/embedded_signer#readme>
- Issues: <https://github.com/swarmauri/swarmauri-sdk/issues>
- Releases: <https://github.com/swarmauri/swarmauri-sdk/releases>
- Discussions: <https://github.com/orgs/swarmauri/discussions>

## License

EmbeddedSigner is released under the Apache 2.0 License. See the
[LICENSE](LICENSE) file for details.
