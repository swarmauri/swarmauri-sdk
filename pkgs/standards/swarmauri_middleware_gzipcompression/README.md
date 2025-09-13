<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri-middleware-gzipcompression/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-middleware-gzipcompression" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri-middleware-gzipcompression">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri-middleware-gzipcompression&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri-middleware-gzipcompression/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-middleware-gzipcompression" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri-middleware-gzipcompression/">
        <img src="https://img.shields.io/pypi/l/swarmauri-middleware-gzipcompression" alt="PyPI - License"/></a>
    <br />
    <a href="https://pypi.org/project/swarmauri-middleware-gzipcompression/">
        <img src="https://img.shields.io/pypi/v/swarmauri-middleware-gzipcompression?label=swarmauri-middleware-gzipcompression&color=green" alt="PyPI - swarmauri-middleware-gzipcompression"/></a>
</p>

---

# `swarmauri_middleware_gzipcompression`

Middleware for adding gzip compression to FastAPI responses.

## Purpose

This package provides a middleware that automatically compresses outgoing responses using gzip encoding. It ensures that responses are only compressed when supported by the client and when the content type is appropriate for compression.

## Authors

- **Michael Nwogha** - [michael@swarmauri.com](mailto:michael@swarmauri.com)

## Installation

To install the package, run: