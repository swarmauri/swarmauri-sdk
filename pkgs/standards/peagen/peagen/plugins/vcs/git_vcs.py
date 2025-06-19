from __future__ import annotations

from pathlib import Path
from typing import Iterable

from git import Repo

from .constants import PEAGEN_REFS_PREFIX


class GitVCS:
    """Lightweight wrapper around :class:`git.Repo`."""

    def __init__(self, path: str | Path, *, remote_url: str | None = None) -> None:
        p = Path(path)
        if (p / ".git").exists():
            self.repo = Repo(p)
        elif remote_url:
            self.repo = Repo.clone_from(remote_url, p)
        else:
            self.repo = Repo.init(p)

        if remote_url:
            if "origin" in self.repo.remotes:
                self.repo.remotes.origin.set_url(remote_url)
            else:
                self.repo.create_remote("origin", remote_url)

            with self.repo.config_writer() as cw:
                sect = 'remote "origin"'
                cw.set_value(sect, "fetch", f"+{PEAGEN_REFS_PREFIX}/*:{PEAGEN_REFS_PREFIX}/*")
                cw.set_value(sect, "push", f"{PEAGEN_REFS_PREFIX}/*:{PEAGEN_REFS_PREFIX}/*")

    # ------------------------------------------------------------------ init/use
    @classmethod
    def open(cls, path: str | Path, remote_url: str | None = None) -> "GitVCS":
        return cls(path, remote_url=remote_url)

    @classmethod
    def ensure_repo(cls, path: str | Path, remote_url: str | None = None) -> "GitVCS":
        """Initialise ``path`` if needed and return a :class:`GitVCS`."""
        return cls(path, remote_url=remote_url)

    # ------------------------------------------------------------------ branch mgmt
    def create_branch(self, name: str, base_ref: str = "HEAD", *, checkout: bool = False) -> None:
        """Create *name* at *base_ref* and optionally check it out."""
        self.repo.git.branch(name, base_ref)
        if checkout:
            self.repo.git.checkout(name)

    def switch(self, branch: str) -> None:
        """Switch to *branch*."""
        self.repo.git.switch(branch)

    def fan_out(self, base_ref: str, branches: Iterable[str]) -> None:
        """Create many branches at ``base_ref``."""
        for b in branches:
            self.repo.git.branch(b, base_ref)

    # ------------------------------------------------------------------ fetch/checkout
    def fetch(self, ref: str, *, remote: str = "origin", checkout: bool = True) -> None:
        """Fetch ``ref`` from *remote`` and optionally check it out."""
        self.repo.git.fetch(remote, ref)
        if checkout:
            self.repo.git.checkout("FETCH_HEAD")

    def push(self, ref: str, *, remote: str = "origin") -> None:
        """Push ``ref`` to *remote*."""
        self.repo.git.push(remote, ref)

    def checkout(self, ref: str) -> None:
        """Check out *ref* (branch or commit)."""
        self.repo.git.checkout(ref)

    # ------------------------------------------------------------------ commit/merge/tag
    def commit(self, paths: Iterable[str], message: str) -> str:
        self.repo.git.add(*paths)
        self.repo.git.commit("-m", message)
        return self.repo.head.commit.hexsha

    def fan_in(self, refs: Iterable[str], message: str) -> str:
        if refs:
            self.repo.git.merge("--no-ff", "--no-edit", *refs)
        self.repo.git.commit("-m", message)
        return self.repo.head.commit.hexsha

    def tag(self, name: str) -> None:
        self.repo.create_tag(name)

    def promote(self, src_ref: str, dest_branch: str) -> None:
        sha = self.repo.rev_parse(src_ref)
        if dest_branch in self.repo.heads:
            self.repo.delete_head(dest_branch, force=True)
        self.repo.create_head(dest_branch, sha)

    # ------------------------------------------------------------------ clean/reset
    def clean_reset(self) -> None:
        self.repo.git.reset("--hard")
        self.repo.git.clean("-fd")

