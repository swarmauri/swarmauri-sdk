from __future__ import annotations

from pathlib import Path
from typing import Iterable
import os
import json
import tempfile
import time

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
                cw.set_value(
                    sect, "fetch", f"+{PEAGEN_REFS_PREFIX}/*:{PEAGEN_REFS_PREFIX}/*"
                )
                cw.set_value(
                    sect, "push", f"{PEAGEN_REFS_PREFIX}/*:{PEAGEN_REFS_PREFIX}/*"
                )

        # ensure we have a commit identity to avoid git errors
        with self.repo.config_reader() as cr, self.repo.config_writer() as cw:
            if not cr.has_option("user", "name"):
                cw.set_value("user", "name", os.getenv("GIT_AUTHOR_NAME", "Peagen"))
            if not cr.has_option("user", "email"):
                cw.set_value(
                    "user", "email", os.getenv("GIT_AUTHOR_EMAIL", "peagen@example.com")
                )

    # ------------------------------------------------------------------ init/use
    @classmethod
    def open(cls, path: str | Path, remote_url: str | None = None) -> "GitVCS":
        return cls(path, remote_url=remote_url)

    @classmethod
    def ensure_repo(cls, path: str | Path, remote_url: str | None = None) -> "GitVCS":
        """Initialise ``path`` if needed and return a :class:`GitVCS`."""
        return cls(path, remote_url=remote_url)

    # ------------------------------------------------------------------ branch mgmt
    def create_branch(
        self, name: str, base_ref: str = "HEAD", *, checkout: bool = False
    ) -> None:
        """Create *name* at *base_ref* and optionally check it out."""
        if name.startswith("refs/"):
            # Ensure custom ref namespaces like ``refs/pea`` are created
            self.repo.git.update_ref(name, base_ref)
            if checkout:
                self.repo.git.checkout(name)
        else:
            self.repo.git.branch(name, base_ref)
            if checkout:
                self.repo.git.checkout(name)

    def switch(self, branch: str) -> None:
        """Switch to *branch*."""
        # ``git switch`` only accepts local branch names. Use ``checkout`` so
        # callers may specify fully-qualified refs like ``refs/pea/*``.
        self.repo.git.checkout(branch)

    def fan_out(self, base_ref: str, branches: Iterable[str]) -> None:
        """Create many branches at ``base_ref``."""
        for b in branches:
            self.repo.git.branch(b, base_ref)

    # ------------------------------------------------------------------ fetch/checkout
    def fetch(
        self, ref: str, *, remote: str = "origin", checkout: bool = True
    ) -> tuple[str | None, bool]:
        """Fetch ``ref`` from *remote`` and optionally check it out.

        Returns a tuple of ``(commit, updated)`` where ``commit`` is the new
        HEAD SHA and ``updated`` indicates if the commit changed.
        """
        old_sha = None
        try:
            old_sha = self.repo.head.commit.hexsha
        except Exception:  # pragma: no cover - HEAD may not exist
            pass

        self.repo.git.fetch(remote, ref)
        if checkout:
            self.repo.git.checkout("FETCH_HEAD")

        new_sha = None
        try:
            new_sha = self.repo.head.commit.hexsha
        except Exception:  # pragma: no cover - should not happen after fetch
            pass

        return new_sha, new_sha != old_sha

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

    def merge_ours(self, ref: str, message: str) -> str:
        """Merge ``ref`` using the ``ours`` strategy and commit."""
        self.repo.git.merge("--no-ff", "-s", "ours", ref, "-m", message)
        return self.repo.head.commit.hexsha

    def tag(self, name: str) -> None:
        self.repo.create_tag(name)

    def promote(self, src_ref: str, dest_branch: str) -> None:
        sha = self.repo.rev_parse(src_ref)
        if dest_branch in self.repo.heads:
            self.repo.delete_head(dest_branch, force=True)
        self.repo.create_head(dest_branch, sha)

    def fast_import_json_ref(
        self, ref: str, data: dict, *, message: str = "key audit"
    ) -> str:
        """Create a commit at ``ref`` containing ``data`` as ``audit.json``."""
        json_text = json.dumps(data, sort_keys=True)
        if not json_text.endswith("\n"):
            json_text += "\n"
        now = int(time.time())
        script = (
            "blob\n"
            "mark :1\n"
            f"data {len(json_text)}\n"
            f"{json_text}\n"
            f"commit {ref}\n"
            "mark :2\n"
            f"author Peagen <peagen@example.com> {now} +0000\n"
            f"committer Peagen <peagen@example.com> {now} +0000\n"
            f"data {len(message)}\n{message}\n"
            "M 100644 :1 audit.json\n"
            "done\n"
        )
        with tempfile.NamedTemporaryFile("wb", delete=False) as tmp:
            tmp.write(script.encode())
            tmp_name = tmp.name
        self.repo.git.execute(["git", "fast-import"], istream=open(tmp_name, "rb"))
        os.unlink(tmp_name)
        return self.repo.rev_parse(ref)

    # ------------------------------------------------------------------ clean/reset
    def clean_reset(self) -> None:
        self.repo.git.reset("--hard")
        self.repo.git.clean("-fd")
