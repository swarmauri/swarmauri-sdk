![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_prompt_sampler/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_prompt_sampler" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_prompt_sampler/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_prompt_sampler.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_prompt_sampler/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_prompt_sampler" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_prompt_sampler/">
        <img src="https://img.shields.io/pypi/l/swarmauri_prompt_sampler" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_prompt_sampler/">
        <img src="https://img.shields.io/pypi/v/swarmauri_prompt_sampler?label=swarmauri_prompt_sampler&color=green" alt="PyPI - swarmauri_prompt_sampler"/></a>
</p>

---

# Swarmauri Prompt Sampler

A utility for randomly sampling prompts from a list.

## Installation

```bash
pip install swarmauri_prompt_sampler
```

## Usage

```python
from swarmauri_prompt_sampler import PromptSampler

sampler = PromptSampler(prompts=["Hello", "Hi", "Hey"])
print(sampler.sample())
```
