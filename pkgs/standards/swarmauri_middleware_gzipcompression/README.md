![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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


## Installation

To install the package, run: