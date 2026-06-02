![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/EmbeddedSigner/">
        <img src="https://static.pepy.tech/badge/EmbeddedSigner/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/embedded_signer/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/embedded_signer.svg"/></a>
    <a href="https://pypi.org/project/EmbeddedSigner/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/EmbeddedSigner/">
        <img src="https://img.shields.io/pypi/l/EmbeddedSigner" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/EmbeddedSigner/">
        <img src="https://img.shields.io/pypi/v/EmbeddedSigner?label=EmbeddedSigner&color=green" alt="PyPI - EmbeddedSigner"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

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

- Source: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/embedded_signer>
- Documentation: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/embedded_signer#readme>
- Issues: <https://github.com/swarmauri/swarmauri-sdk/issues>
- Releases: <https://github.com/swarmauri/swarmauri-sdk/releases>
- Discussions: <https://github.com/orgs/swarmauri/discussions>

## License

EmbeddedSigner is released under the Apache 2.0 License. See the
[LICENSE](LICENSE) file for details.


