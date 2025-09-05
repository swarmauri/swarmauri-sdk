from __future__ import annotations

from pathlib import Path
from typing import Iterable
import os
import json
import tempfile
import time
import hashlib
import httpx
from github import Github

from git import Repo
from git.exc import GitCommandError

from peagen.errors import (
    GitRemoteMissingError,
    GitCloneError,
    GitFetchError,
    GitPushError,
    GitCommitError,
)
from peagen.plugins import PluginManager
from peagen._utils.config_loader import resolve_cfg

from .constants import PEAGEN_REFS_PREFIX


class GitVCS:
    """Lightweight wrapper around :class:`git.Repo`."""

    def __init__(
        self,
        path: str | Path = ".",
        *,
        remote_url: str | None = None,
        mirror_git_url: str | None = None,
        mirror_git_token: str | None = None,
        owner: str | None = None,
        remotes: dict[str, str] | None = None,
    ) -> None:
        self.mirror_git_url = mirror_git_url
        self.mirror_git_token = mirror_git_token
        self.owner = owner

        p = Path(path)
        remotes = remotes or {}
        if remote_url and "origin" not in remotes:
            remotes["origin"] = remote_url

        if (p / ".git").exists():
            self.repo = Repo(p)
        elif remote_url:
            if "origin" not in remotes:
                remotes["origin"] = remote_url
            try:
                self.repo = Repo.clone_from(remote_url, p)
            except GitCommandError as exc:
                raise GitCloneError(remote_url) from exc
        else:
            self.repo = Repo.init(p)
            with self.repo.config_writer() as cw:
                cw.set_value("receive", "denyCurrentBranch", "updateInstead")

        ordered: list[tuple[str, str]] = []
        if "origin" in remotes:
            ordered.append(("origin", remotes["origin"]))
        if "upstream" in remotes:
            ordered.append(("upstream", remotes["upstream"]))
        for name, url in remotes.items():
            if name in {"origin", "upstream"}:
                continue
            ordered.append((name, url))

        for name, url in ordered:
            self.configure_remote(url, name=name)

        if mirror_git_url:
            url = mirror_git_url
            if mirror_git_token and url.startswith("http"):
                scheme, rest = url.split("://", 1)
                url = f"{scheme}://{mirror_git_token}@{rest}"
            self.configure_remote(url, name="mirror")

        # ensure we have a commit identity to avoid git errors
        with self.repo.config_reader() as cr, self.repo.config_writer() as cw:
            if not cr.has_option("user", "name"):
                cw.set_value("user", "name", os.getenv("GIT_AUTHOR_NAME", "Peagen"))
            if not cr.has_option("user", "email"):
                cw.set_value(
                    "user", "email", os.getenv("GIT_AUTHOR_EMAIL", "peagen@example.com")
                )

    # ------------------------------------------------------------------ init/use
    # NOTE: ``open_repo`` and ``ensure_repo`` moved to ``peagen.core.mirror_core``

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

        try:
            self.repo.git.fetch(remote, ref)
        except GitCommandError as exc:
            raise GitFetchError(ref, remote) from exc
        if checkout:
            self.repo.git.checkout("FETCH_HEAD")

        new_sha = None
        try:
            new_sha = self.repo.head.commit.hexsha
        except Exception:  # pragma: no cover - should not happen after fetch
            pass

        return new_sha, new_sha != old_sha

    def push(
        self,
        ref: str,
        *,
        remote: str = "origin",
        gateway_url: str | None = None,
    ) -> None:
        """Push ``ref`` to *remote*.

        If the ``DEPLOY_KEY_SECRET`` environment variable is set, the
        deploy key will be fetched from ``gateway_url`` and used for
        authentication.
        """
        secret_name = os.getenv("DEPLOY_KEY_SECRET")
        if secret_name:
            gateway = gateway_url or os.getenv(
                "PEAGEN_GATEWAY", "http://localhost:8000/rpc"
            )
            self.push_with_secret(ref, secret_name, remote=remote, gateway_url=gateway)
            return

        self.require_remote(remote)
        push_ref = ref
        if ref == "HEAD":
            try:
                push_ref = self.repo.active_branch.name
            except TypeError:  # pragma: no cover - detached HEAD
                try:
                    remote_head = self.repo.git.symbolic_ref(
                        f"refs/remotes/{remote}/HEAD"
                    )
                    remote_branch = remote_head.split("/")[-1]
                    push_ref = f"HEAD:refs/heads/{remote_branch}"
                except Exception:
                    push_ref = ref
        try:
            self.repo.git.push(remote, push_ref)
        except GitCommandError as exc:
            raise GitPushError(ref, remote) from exc

        if self.mirror_git_url:
            mirror_remote = "mirror"
            if mirror_remote not in [r.name for r in self.repo.remotes]:
                self.configure_remote(self.mirror_git_url, name=mirror_remote)
            try:
                self.repo.git.push(mirror_remote, push_ref)
            except GitCommandError as exc:
                raise GitPushError(ref, mirror_remote) from exc

    def push_with_secret(
        self,
        ref: str,
        secret_name: str,
        *,
        remote: str = "origin",
        gateway_url: str = "http://localhost:8000/rpc",
    ) -> None:
        """Push ``ref`` using an encrypted deploy key secret."""
        envelope = {
            "jsonrpc": "2.0",
            "method": "Secrets.get",
            "params": {"name": secret_name},
        }
        res = httpx.post(gateway_url, json=envelope, timeout=10.0)
        res.raise_for_status()
        cipher = res.json()["result"]["secret"].encode()

        pm = PluginManager(resolve_cfg())
        crypto = pm.get("cryptos")
        token = crypto.decrypt_text(cipher).strip()

        # Use PyGithub to verify access and obtain the remote repository
        remote_url = self.repo.remotes[remote].url
        https_url = remote_url
        if remote_url.startswith("git@"):
            host, path = remote_url.split(":", 1)
            https_url = f"https://{host.split('@')[1]}/{path}"
        https_url = https_url.rstrip(".git")
        owner_repo = https_url.split("https://")[-1]

        gh = Github(token)
        gh_repo = gh.get_repo(owner_repo)
        push_url = gh_repo.clone_url.replace("https://", f"https://{token}@")

        try:
            self.repo.git.push(push_url, ref)
        except GitCommandError as exc:
            raise GitPushError(ref, remote) from exc

        if self.mirror_git_url:
            mirror_remote = "mirror"
            mirror_push_url = self.mirror_git_url.replace(
                "https://", f"https://{token}@"
            )
            try:
                self.repo.git.push(mirror_push_url, ref)
            except GitCommandError as exc:
                raise GitPushError(ref, mirror_remote) from exc

    # ------------------------------------------------------------------ remote helpers
    def has_remote(self, name: str = "origin") -> bool:
        """Return ``True`` if ``name`` is a configured remote."""
        return name in [r.name for r in self.repo.remotes]

    def configure_remote(self, url: str, *, name: str = "origin") -> None:
        """Add or update a remote called ``name`` with ``url``."""
        if name in self.repo.remotes:
            self.repo.remotes[name].set_url(url)
        else:
            self.repo.create_remote(name, url)

        with self.repo.config_writer() as cw:
            sect = f'remote "{name}"'
            cw.set_value(
                sect, "fetch", f"+{PEAGEN_REFS_PREFIX}/*:{PEAGEN_REFS_PREFIX}/*"
            )
            cw.set_value(sect, "push", f"{PEAGEN_REFS_PREFIX}/*:{PEAGEN_REFS_PREFIX}/*")

    def require_remote(self, name: str = "origin") -> None:
        """Raise :class:`GitRemoteMissingError` if ``name`` is not configured."""
        if not self.has_remote(name):
            raise GitRemoteMissingError(
                f"Remote '{name}' is not configured; changes cannot be pushed"
            )

    def checkout(self, ref: str) -> None:
        """Check out *ref* (branch or commit)."""
        self.repo.git.checkout(ref)

    # ------------------------------------------------------------------ commit/merge/tag
    def commit(self, paths: Iterable[str], message: str) -> str:
        try:
            self.repo.git.add(*paths)
            self.repo.git.commit("-m", message)
        except GitCommandError as exc:
            reason = (
                exc.stderr.strip()
                if hasattr(exc, "stderr") and exc.stderr
                else str(exc)
            )
            raise GitCommitError(list(paths), reason) from exc
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

    def record_key_audit(
        self, ciphertext: bytes, user_fpr: str, gateway_fp: str
    ) -> str:
        """Record a key audit commit for ``ciphertext``.

        Parameters
        ----------
        ciphertext:
            Encrypted secret bytes used to derive the audit ref.
        user_fpr:
            Fingerprint of the submitting user's key.
        gateway_fp:
            Gateway public key fingerprint.

        Returns
        -------
        str
            The new commit SHA.
        """
        from .constants import pea_ref

        sha = hashlib.sha256(ciphertext).hexdigest()
        data = {
            "user_fpr": user_fpr,
            "gateway_fp": gateway_fp,
            "created_at": int(time.time()),
        }
        ref = pea_ref("key_audit", sha)
        return self.fast_import_json_ref(ref, data)

    def blob_oid(self, path: str, *, ref: str = "HEAD") -> str:
        """Return the object ID for ``path`` at ``ref``."""
        return self.repo.git.rev_parse(f"{ref}:{path}")

    # ------------------------------------------------------------------ oid helpers
    def object_type(self, oid: str) -> str:
        """Return the git object type for ``oid``."""
        return self.repo.git.cat_file("-t", oid).strip()

    def object_size(self, oid: str) -> int:
        """Return the size of ``oid`` in bytes."""
        return int(self.repo.git.cat_file("-s", oid).strip())

    def object_pretty(self, oid: str) -> str:
        """Return the pretty-printed content for ``oid``."""
        return self.repo.git.cat_file("-p", oid)

    # ------------------------------------------------------------------ clean/reset
    def clean_reset(self) -> None:
        self.repo.git.reset("--hard")
        self.repo.git.clean("-fd")
