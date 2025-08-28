![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-gitfilter-gh-release/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-gitfilter-gh-release" alt="PyPI - Downloads"/>
    </a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/standards/swarmauri_gitfilter_gh_release">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/standards/swarmauri_gitfilter_gh_release&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-gitfilter-gh-release/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-gitfilter-gh-release" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-gitfilter-gh-release/">
        <img src="https://img.shields.io/pypi/l/swarmauri-gitfilter-gh-release" alt="PyPI - License"/>
    </a>
    <br />
    <a href="https://pypi.org/project/swarmauri-gitfilter-gh-release/">
        <img src="https://img.shields.io/pypi/v/swarmauri-gitfilter-gh-release?label=swarmauri-gitfilter-gh-release&color=green" alt="PyPI - swarmauri-gitfilter-gh-release"/>
    </a>
</p>

---

# `swarmauri-gitfilter-gh-release`

GitHub Release git filter for Peagen.

## Installation

This package is part of the Swarmauri SDK monorepo.

## Usage

```python
from swarmauri_gitfilter_gh_release import GithubReleaseFilter

flt = GithubReleaseFilter.from_uri("ghrel://org/repo/tag")
```
