![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_gitfilter_gh_release/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_gitfilter_gh_release" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_gh_release/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_gh_release.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_gh_release/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_gitfilter_gh_release" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_gh_release/">
        <img src="https://img.shields.io/pypi/l/swarmauri_gitfilter_gh_release" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_gh_release/">
        <img src="https://img.shields.io/pypi/v/swarmauri_gitfilter_gh_release?label=swarmauri_gitfilter_gh_release&color=green" alt="PyPI - swarmauri_gitfilter_gh_release"/>
    </a>
</p>

---

# Swarmauri Git Filter GitHub Release

Store artifacts in GitHub Releases.

## Installation

```bash
pip install swarmauri_gitfilter_gh_release
```

## Usage

```python
from swarmauri_gitfilter_gh_release import GithubReleaseFilter

filt = GithubReleaseFilter.from_uri("ghrel://org/repo/tag")
```
