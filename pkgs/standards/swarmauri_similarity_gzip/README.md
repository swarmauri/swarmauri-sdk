# GzipSimilarity

![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

GzipSimilarity provides a dependency-light Swarmauri similarity implementation based on gzip compression and Normalized Compression Distance (NCD).

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_similarity_gzip)](https://pepy.tech/projects/swarmauri_similarity_gzip)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_similarity_gzip.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_similarity_gzip/)
[![Python Versions](https://img.shields.io/pypi/pyversions/swarmauri_similarity_gzip)](https://pypi.org/project/swarmauri_similarity_gzip/)
[![License](https://img.shields.io/pypi/l/swarmauri_similarity_gzip)](https://pypi.org/project/swarmauri_similarity_gzip/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_similarity_gzip)](https://pypi.org/project/swarmauri_similarity_gzip/)

## Features

- Implements `SimilarityBase` from `swarmauri_base`.
- Compares text and binary values through shared gzip compressibility.
- Supports deterministic gzip sizing and configurable compression levels.
- Supports symmetric concatenation-order handling.
- Exposes both bounded similarity and raw NCD values.

## Installation

```bash
uv add swarmauri_similarity_gzip
```

```bash
pip install swarmauri_similarity_gzip
```

## Usage

```python
from swarmauri_similarity_gzip import GzipSimilarity

similarity = GzipSimilarity()

score = similarity.similarity(
    "The quick brown fox",
    "Le renard brun rapide",
)

ncd = similarity.ncd(
    "The quick brown fox",
    "Le renard brun rapide",
)
```

`similarity()` returns a score in `[0.0, 1.0]`, where higher values indicate greater shared compressibility. `ncd()` exposes the underlying Normalized Compression Distance. The result is a compression-based similarity estimate and should not be interpreted as semantic similarity without corpus-specific validation.

For language comparison, use balanced samples, consistent UTF-8 encoding and preprocessing, and sufficiently large inputs to reduce gzip framing effects.

The implementation is based on Benedetto, Caglioti, and Loreto, [Language Trees and Zipping](https://arxiv.org/abs/cond-mat/0108530).

## License

Apache-2.0
