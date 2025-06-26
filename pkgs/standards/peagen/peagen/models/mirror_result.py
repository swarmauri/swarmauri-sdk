from pydantic import BaseModel, HttpUrl


class MirrorResult(BaseModel):
    """Result of :func:`ensure_mirror`."""

    repo_uri: str
    gitea_repo: HttpUrl
    created: bool
