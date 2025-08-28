# Swarmauri GitHub Release Git Filter

Git filter storing artifacts as GitHub release assets.

## Installation

```bash
# pip install swarmauri_gitfilter_github_release (when published)
```

## Usage

```python
from swarmauri_gitfilter_github_release import GithubReleaseFilter

filt = GithubReleaseFilter.from_uri("ghrel://org/repo/tag")
```
