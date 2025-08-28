import warnings

warnings.warn(
    "peagen.plugins.storage_adapters.github_storage_adapter is deprecated; use swarmauri_gitfilter_gh_release instead",
    DeprecationWarning,
    stacklevel=2,
)


class GithubStorageAdapter:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def upload(self, path: str, dest: str) -> str:
        return f"github://{dest}"
