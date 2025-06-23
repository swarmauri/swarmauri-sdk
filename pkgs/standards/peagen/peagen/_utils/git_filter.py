from __future__ import annotations

from pathlib import Path
import sys
import textwrap
import tomllib
from git import Repo


def _dump_simple_toml(data: dict) -> str:
    lines = []
    if "storage" in data:
        storage = data["storage"]
        lines.append("[storage]")
        for k, v in storage.items():
            if not isinstance(v, dict):
                lines.append(f'{k} = "{v}"')
        lines.append("")
        filters = storage.get("filters", {})
        for name, cfg in filters.items():
            lines.append(f"[storage.filters.{name}]")
            for ck, cv in cfg.items():
                lines.append(f'{ck} = "{cv}"')
            lines.append("")
    return "\n".join(lines)


DEFAULT_FILTER_URI = "s3://peagen"


def add_filter(
    uri: str | None = None, name: str = "default", config: Path = Path(".peagen.toml")
) -> None:
    """Add a git filter entry to ``config``.

    If *uri* is omitted, ``s3://peagen`` is used with :class:`S3FSFilter`.
    """
    uri = uri or DEFAULT_FILTER_URI
    cfg: dict = {}
    if config.exists():
        cfg = tomllib.loads(config.read_text())
    storage = cfg.setdefault("storage", {})
    filters = storage.setdefault("filters", {})
    filters[name] = {"uri": uri}
    if "default_filter" not in storage:
        storage["default_filter"] = name
    config.write_text(_dump_simple_toml(cfg), encoding="utf-8")


def init_git_filter(
    repo: Repo | str,
    uri: str | None = None,
    *,
    name: str = "default",
) -> None:
    """Configure ``repo`` to use *name* for workspace paths.

    The filter will store blobs using ``peagen.plugins.git_filters`` based on
    ``uri``. ``clean`` and ``smudge`` helper scripts are written into the
    repository's ``.git/filters/<name>`` directory and referenced from the git
    config. ``.gitattributes`` is updated so ``workspace/**`` is processed by the
    filter while ``workspace/artifacts/**`` is ignored.
    """

    uri = uri or DEFAULT_FILTER_URI
    r = Repo(repo) if not isinstance(repo, Repo) else repo

    filter_dir = Path(r.git_dir) / "filters" / name
    filter_dir.mkdir(parents=True, exist_ok=True)

    clean_script = filter_dir / "clean.py"
    smudge_script = filter_dir / "smudge.py"

    clean_script.write_text(
        textwrap.dedent(
            f"""
            import hashlib, io, sys
            from peagen.plugins.git_filters import make_filter_for_uri

            FILTER_URI = {uri!r}
            filt = make_filter_for_uri(FILTER_URI)

            data = sys.stdin.buffer.read()
            oid = "sha256:" + hashlib.sha256(data).hexdigest()
            try:
                filt.download(oid)
            except FileNotFoundError:
                filt.upload(oid, io.BytesIO(data))
            sys.stdout.write(oid)
            """
        ),
        encoding="utf-8",
    )

    smudge_script.write_text(
        textwrap.dedent(
            f"""
            import sys
            from peagen.plugins.git_filters import make_filter_for_uri

            FILTER_URI = {uri!r}
            filt = make_filter_for_uri(FILTER_URI)

            oid = sys.stdin.read().strip()
            with filt.download(oid) as fh:
                sys.stdout.buffer.write(fh.read())
            """
        ),
        encoding="utf-8",
    )

    clean_script.chmod(0o755)
    smudge_script.chmod(0o755)

    clean_cmd = f"{sys.executable} {clean_script}"
    smudge_cmd = f"{sys.executable} {smudge_script}"

    with r.config_writer() as cw:
        s = f'filter "{name}"'
        cw.set_value(s, "clean", clean_cmd)
        cw.set_value(s, "smudge", smudge_cmd)
        cw.set_value(s, "required", "true")

    attr_file = Path(r.working_tree_dir) / ".gitattributes"
    attr_content = textwrap.dedent(
        f"""
        workspace/** filter={name} diff={name}
        workspace/artifacts/** -filter -diff
        """
    )
    attr_file.write_text(attr_content, encoding="utf-8")
