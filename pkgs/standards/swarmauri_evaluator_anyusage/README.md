<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_evaluator_anyusage/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_evaluator_anyusage" alt="PyPI - Downloads"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluator_anyusage/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_evaluator_anyusage" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluator_anyusage/">
        <img src="https://img.shields.io/pypi/l/swarmauri_evaluator_anyusage" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluator_anyusage/">
        <img src="https://img.shields.io/pypi/v/swarmauri_evaluator_anyusage?label=swarmauri_evaluator_anyusage&color=green" alt="PyPI - swarmauri_evaluator_anyusage"/></a>
</p>

---

# Swarmauri Evaluator Anyusage

An evaluator component that detects and penalizes usage of the `Any` type in Python code.

## Installation

```bash
pip install swarmauri_evaluator_anyusage
```
