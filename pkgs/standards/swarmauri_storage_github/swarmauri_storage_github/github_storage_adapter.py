import warnings

warnings.warn(
    "GithubStorageAdapter is deprecated; use peagen.plugins.git_filters.github_filter instead",
    DeprecationWarning,
    stacklevel=2,
)


class GithubStorageAdapter:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def upload(self, path: str, dest: str) -> str:
        return f"github://{dest}"
