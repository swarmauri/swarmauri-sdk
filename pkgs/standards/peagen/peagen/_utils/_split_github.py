from urllib.parse import urlparse


def _split_github(url: str) -> tuple[str, str]:
    """
    https://github.com/<org>/<repo>.git -> ('org', 'repo')
    """
    parts = urlparse(url)
    path = parts.path.lstrip("/").removesuffix(".git")
    return tuple(path.split("/", 1))  # type: ignore[misc]
