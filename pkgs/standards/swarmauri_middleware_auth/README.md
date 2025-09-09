<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri-middleware-auth/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-middleware-auth" alt="PyPI - Downloads"/>
    </a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri-middleware-auth">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri-middleware-auth&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-middleware-auth/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-middleware-auth" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-middleware-auth/">
        <img src="https://img.shields.io/pypi/l/swarmauri-middleware-auth" alt="PyPI - License"/>
    </a>
    <br />
    <a href="https://pypi.org/project/swarmauri-middleware-auth/">
        <img src="https://img.shields.io/pypi/v/swarmauri-middleware-auth?label=swarmauri-middleware-auth&color=green" alt="PyPI - swarmauri-middleware-auth"/>
    </a>
</p>

---

# `swarmauri-middleware-auth`

Authentication middleware for validating request headers and tokens in Swarmauri applications.

## Purpose

This package provides middleware for handling request authentication in Swarmauri applications. It validates authentication headers or tokens before allowing requests to proceed through the application stack.

## Installation

To install `swarmauri-middleware-auth`, you can use Poetry or pip: