<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_composite" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_composite/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_composite.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_composite" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_composite" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_composite?label=swarmauri_tokens_composite&color=green" alt="PyPI - swarmauri_tokens_composite"/></a>
</p>

---

## Swarmauri Token Composite

Algorithm-routing token service delegating to child providers based on JWT headers, claims, or algorithms.

## Installation

```bash
pip install swarmauri_tokens_composite
```

## Usage

```python
from swarmauri_tokens_composite import CompositeTokenService

svc = CompositeTokenService([...])  # pass in other ITokenService providers
```

## Entry point

The provider is registered under the `swarmauri.tokens` entry-point as `CompositeTokenService`.
