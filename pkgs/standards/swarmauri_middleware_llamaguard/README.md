<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri-middleware-llamaguard/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-middleware-llamaguard" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri-middleware-llamaguard">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri-middleware-llamaguard&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri-middleware-llamaguard/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-middleware-llamaguard" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri-middleware-llamaguard/">
        <img src="https://img.shields.io/pypi/l/swarmauri-middleware-llamaguard" alt="PyPI - License"/></a>
    <br />
    <a href="https://pypi.org/project/swarmauri-middleware-llamaguard/">
        <img src="https://img.shields.io/pypi/v/swarmauri-middleware-llamaguard?label=swarmauri-middleware-llamaguard&color=green" alt="PyPI - swarmauri-middleware-llamaguard"/></a>
</p>

---

# `swarmauri-middleware-llamaguard`

A FastAPI middleware that integrates LlamaGuard for comprehensive content inspection and filtering. This middleware ensures both incoming requests and outgoing responses are free from unsafe or malicious content.

## Installation

To install the package, use pip: