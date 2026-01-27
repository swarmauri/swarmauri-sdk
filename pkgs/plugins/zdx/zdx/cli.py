"""Command-line helpers for the ZDX documentation toolkit."""

import argparse
import os
import shutil
import shlex
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence

import tomllib
import yaml

from zdx.scripts.gen_api import (
    discover_packages,
    load_manifest,
    load_mkdocs_yml,
    save_mkdocs_yml,
)


class FailureMode(Enum):
    """Strategies for handling subprocess failures."""

    FAIL = "fail"
    WARN = "warn"
    IGNORE = "ignore"

    @classmethod
    def from_value(cls, value: str) -> "FailureMode":
        """Return a :class:`FailureMode` from user input."""

        try:
            return cls(value.lower())
        except ValueError as exc:  # pragma: no cover - defensive guard
            raise argparse.ArgumentTypeError(
                f"Unsupported failure mode '{value}'."
            ) from exc


def _default_failure_mode_from_env() -> FailureMode:
    """Derive the default failure mode from ``ZDX_FAILURE_MODE``."""

    env_value = os.environ.get("ZDX_FAILURE_MODE")
    if not env_value:
        return FailureMode.FAIL
    try:
        return FailureMode(env_value.lower())
    except ValueError:
        print(
            "WARNING: Ignoring unknown ZDX_FAILURE_MODE="
            f"{env_value!r}; defaulting to 'fail'."
        )
        return FailureMode.FAIL


def _run_command(
    cmd: Sequence[str],
    *,
    cwd: str | None = None,
    failure_mode: FailureMode,
    description: str | None = None,
) -> subprocess.CompletedProcess[bytes]:
    """Execute ``cmd`` honouring the requested ``failure_mode``."""

    result = subprocess.run(cmd, cwd=cwd, check=False)
    if result.returncode == 0:
        return result

    cmd_str = description or shlex.join(cmd)
    message = f"Command '{cmd_str}' exited with code {result.returncode}."

    if failure_mode is FailureMode.FAIL:
        raise subprocess.CalledProcessError(result.returncode, cmd)
    if failure_mode is FailureMode.WARN:
        print(f"WARNING: {message}")
    return result


def _normalize_api_path(value: str) -> str:
    """Return a normalized API path for comparisons."""

    return value.replace("\\", "/").lstrip("./")


def _prune_nav_entries(node: object, prefixes: set[str]) -> object | None:
    """Remove nav entries that point into any of ``prefixes``."""

    if isinstance(node, list):
        pruned_list = []
        for item in node:
            cleaned = _prune_nav_entries(item, prefixes)
            if cleaned is not None:
                pruned_list.append(cleaned)
        return pruned_list or None

    if isinstance(node, dict):
        pruned_dict: dict[str, object] = {}
        for key, value in node.items():
            cleaned = _prune_nav_entries(value, prefixes)
            if cleaned is not None:
                pruned_dict[key] = cleaned
        return pruned_dict or None

    if isinstance(node, str):
        normalized = _normalize_api_path(node)
        for prefix in prefixes:
            if normalized == prefix or normalized.startswith(prefix + "/"):
                return None
        return node

    return node


def _prune_failed_package_docs(
    *,
    docs_dir: str,
    api_output_dir: str,
    mkdocs_yml: str,
    failed_packages: set[str],
) -> None:
    """Remove generated API docs and nav entries for failed packages."""

    if not failed_packages:
        return

    docs_root = Path(docs_dir)
    api_root = docs_root / "docs" / api_output_dir
    if not api_root.exists():
        return

    removed_prefixes: set[str] = set()

    for target_dir in api_root.iterdir():
        if not target_dir.is_dir():
            continue
        for pkg in failed_packages:
            candidate = target_dir / pkg
            if candidate.exists():
                shutil.rmtree(candidate)
                removed_prefixes.add(
                    _normalize_api_path(
                        os.path.join(api_output_dir, target_dir.name, pkg)
                    )
                )

    if not removed_prefixes:
        return

    mkdocs_path = docs_root / mkdocs_yml
    if not mkdocs_path.exists():
        return

    cfg = load_mkdocs_yml(str(mkdocs_path))
    if not isinstance(cfg, dict) or "nav" not in cfg:
        return

    pruned_nav = _prune_nav_entries(cfg["nav"], removed_prefixes)
    if pruned_nav is None:
        cfg.pop("nav", None)
    else:
        cfg["nav"] = pruned_nav

    save_mkdocs_yml(str(mkdocs_path), cfg)


def _add_failure_mode_argument(parser: argparse.ArgumentParser) -> None:
    """Attach the ``--on-error`` argument to a sub-parser."""

    default_mode = _default_failure_mode_from_env()
    parser.add_argument(
        "--on-error",
        choices=[mode.value for mode in FailureMode],
        default=default_mode.value,
        help=(
            "Control how zdx reacts when a subprocess fails. "
            "Defaults to the value of ZDX_FAILURE_MODE (if set) or 'fail'."
        ),
    )


def run_gen_api(
    manifest: str = "api_manifest.yaml",
    docs_dir: str = ".",
    mkdocs_yml: str = "mkdocs.yml",
    api_output_dir: str = "api",
    changed_only: bool = False,
    skip_packages: Sequence[str] | None = None,
    failure_mode: FailureMode = FailureMode.FAIL,
) -> None:
    """Run the API docs generation script.

    manifest (str): Path to the API manifest YAML file.
    docs_dir (str): Directory containing documentation sources.
    mkdocs_yml (str): Path to the MkDocs configuration file.
    api_output_dir (str): Relative output directory for API pages.
    changed_only (bool): Only rebuild pages for changed sources.
    skip_packages (Sequence[str] | None): Package names to skip when
        generating API stubs.
    failure_mode (FailureMode): Strategy for handling subprocess failures.
    RETURNS (None): This function operates via side effects.
    """
    cmd = [
        sys.executable,
        "-m",
        "zdx.scripts.gen_api",
        "--manifest",
        manifest,
        "--docs-dir",
        docs_dir,
        "--mkdocs-yml",
        mkdocs_yml,
        "--api-output-dir",
        api_output_dir,
    ]
    if changed_only:
        cmd.append("--changed-only")
    for pkg in sorted(set(skip_packages or [])):
        cmd.extend(["--skip-package", pkg])
    _run_command(cmd, failure_mode=failure_mode)


@dataclass(frozen=True)
class WorkspaceSpec:
    """Details for a documentation workspace defined in a manifest."""

    root: Path
    pyproject: Path


def _resolve_workspace_directory(manifest_path: Path) -> WorkspaceSpec | None:
    """Return the workspace specification defined in the manifest, if any."""

    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        return None

    workspace_cfg = data.get("workspace")
    if not workspace_cfg:
        return None

    def _make_path(value: str) -> Path:
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = (manifest_path.parent / candidate).resolve()
        return candidate

    root: Path | None = None
    pyproject: Path | None = None

    if isinstance(workspace_cfg, str):
        candidate = _make_path(workspace_cfg)
        if candidate.is_file():
            pyproject = candidate
            root = candidate.parent
        else:
            root = candidate
            pyproject = candidate / "pyproject.toml"
    elif isinstance(workspace_cfg, dict):
        if "pyproject" in workspace_cfg:
            pyproject = _make_path(workspace_cfg["pyproject"])
            root = pyproject.parent
        elif "root" in workspace_cfg:
            root = _make_path(workspace_cfg["root"])
            pyproject = root / "pyproject.toml"

    if not root or not pyproject:
        return None

    if pyproject.is_dir():
        pyproject = pyproject / "pyproject.toml"

    if not pyproject.is_file():
        return None

    return WorkspaceSpec(root=root, pyproject=pyproject)


def _load_workspace_members(spec: WorkspaceSpec) -> list[Path]:
    """Load workspace members defined in ``spec``'s ``pyproject.toml``."""

    try:
        data = tomllib.loads(spec.pyproject.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    except tomllib.TOMLDecodeError:
        return []

    workspace_cfg = data.get("tool", {}).get("uv", {}).get("workspace", {})
    members = (
        workspace_cfg.get("members", []) if isinstance(workspace_cfg, dict) else []
    )

    resolved: list[Path] = []
    for entry in members:
        if not isinstance(entry, str):
            continue
        candidate = (spec.root / entry).resolve()
        if candidate.is_dir():
            resolved.append(candidate)
    return resolved


def install_manifest_packages(
    manifest: str, failure_mode: FailureMode = FailureMode.FAIL
) -> set[str]:
    """Install all packages referenced in the API manifest.

    This ensures modules documented via ``mkdocstrings`` can be imported
    successfully when building or serving the docs.

    Returns a set of package names that failed to install. When
    ``failure_mode`` is :class:`FailureMode.FAIL` the function will raise on
    the first failure, so the returned set is empty. Callers using ``WARN`` or
    ``IGNORE`` can use the set to omit API generation for missing packages.

    failure_mode (FailureMode): Strategy for handling installation errors.
    """

    manifest_path = Path(manifest).resolve()
    targets = load_manifest(manifest)
    manifest_parent = manifest_path.parent

    workspace_spec = _resolve_workspace_directory(manifest_path)
    workspace_result: subprocess.CompletedProcess[bytes] | None = None
    installed_members: set[Path] = set()

    if workspace_spec is not None:
        member_paths = _load_workspace_members(workspace_spec)
        target_paths: list[Path] = []
        for target in targets:
            base_path = Path(target.search_path)
            if not base_path.is_absolute():
                base_path = (manifest_parent / base_path).resolve()
            target_paths.append(base_path)

        desired_members: list[Path] = []
        for member in member_paths:
            for base_path in target_paths:
                if member == base_path or member.is_relative_to(base_path):
                    desired_members.append(member)
                    break
                if base_path.is_relative_to(member):
                    desired_members.append(member)
                    break

        if desired_members:
            cmd = ["uv", "pip", "install"]
            if not (os.environ.get("VIRTUAL_ENV") or sys.prefix != sys.base_prefix):
                cmd.append("--system")
            for member in desired_members:
                cmd.extend(["--editable", str(member)])
            workspace_result = _run_command(
                cmd,
                failure_mode=failure_mode,
                description="uv pip install (workspace members)",
            )
            if workspace_result.returncode == 0:
                installed_members = {member.resolve() for member in desired_members}
        else:
            cmd = [
                "uv",
                "pip",
                "install",
                "--directory",
                str(workspace_spec.root),
            ]
            if not (os.environ.get("VIRTUAL_ENV") or sys.prefix != sys.base_prefix):
                cmd.append("--system")
            cmd.append(".")
            workspace_result = _run_command(
                cmd,
                failure_mode=failure_mode,
                description=f"uv pip install --directory {workspace_spec.root}",
            )
            if workspace_result.returncode == 0:
                installed_members = {workspace_spec.root.resolve()}

    workspace_success = (
        workspace_result is not None and workspace_result.returncode == 0
    )

    failed_packages: set[str] = set()

    def _install_path(pkg_name: str, pkg_path: Path) -> None:
        if workspace_success and installed_members:
            for member in installed_members:
                if pkg_path.is_relative_to(member):
                    return
        if not pkg_path.is_dir():
            return
        if not (
            (pkg_path / "pyproject.toml").is_file() or (pkg_path / "setup.py").is_file()
        ):
            print(f"Skipping {pkg_path}: no pyproject.toml or setup.py found")
            return

        cmd = [
            "uv",
            "pip",
            "install",
            "--directory",
            str(pkg_path),
        ]
        if not (os.environ.get("VIRTUAL_ENV") or sys.prefix != sys.base_prefix):
            cmd.append("--system")
        cmd.append(".")
        result = _run_command(
            cmd,
            failure_mode=failure_mode,
            description=f"uv pip install --directory {pkg_path}",
        )
        if result.returncode != 0:
            failed_packages.add(pkg_name)

    for target in targets:
        base_path = Path(target.search_path)
        if not base_path.is_absolute():
            base_path = (manifest_parent / base_path).resolve()

        if target.discover:
            for package_name, package_dir in discover_packages(str(base_path)):
                _install_path(package_name, Path(package_dir))
        else:
            if not target.package:
                continue
            _install_path(target.package, base_path)

    return failed_packages


def run_mkdocs_build(
    docs_dir: str = ".",
    mkdocs_yml: str = "mkdocs.yml",
    *,
    failure_mode: FailureMode = FailureMode.FAIL,
) -> None:
    """Build the documentation site with MkDocs.

    docs_dir (str): Directory containing documentation sources.
    mkdocs_yml (str): Path to the MkDocs configuration file.
    failure_mode (FailureMode): Strategy for handling mkdocs failures.
    RETURNS (None): The build completes or continues based on the failure mode.
    """
    os.makedirs(os.path.join(docs_dir, "docs"), exist_ok=True)
    cmd = ["mkdocs", "build", "-f", mkdocs_yml]
    _run_command(
        cmd,
        cwd=docs_dir,
        failure_mode=failure_mode,
        description=f"mkdocs build -f {mkdocs_yml}",
    )


def run_mkdocs_serve(
    docs_dir: str = ".",
    mkdocs_yml: str = "mkdocs.yml",
    dev_addr: str = "0.0.0.0:8000",
    *,
    failure_mode: FailureMode = FailureMode.FAIL,
) -> None:
    """Launch a MkDocs development server.

    docs_dir (str): Directory containing documentation sources.
    mkdocs_yml (str): Path to the MkDocs configuration file.
    dev_addr (str): Address and port for the server to bind to.
    failure_mode (FailureMode): Strategy for handling mkdocs failures.
    RETURNS (None): The server runs until interrupted.
    """
    # Ensure the docs directory exists so MkDocs has a working tree.
    os.makedirs(os.path.join(docs_dir, "docs"), exist_ok=True)
    cmd = ["mkdocs", "serve", "-f", mkdocs_yml, "-a", dev_addr]
    _run_command(
        cmd,
        cwd=docs_dir,
        failure_mode=failure_mode,
        description=f"mkdocs serve -f {mkdocs_yml} -a {dev_addr}",
    )


def run_gen_readmes(
    docs_dir: str = ".",
    *,
    failure_mode: FailureMode = FailureMode.FAIL,
) -> None:
    """Run the README generation script.

    docs_dir (str): Root directory containing project documentation.
    RETURNS (None): This function operates via side effects.
    """
    # Ensure the target docs directory exists before generating content.
    os.makedirs(os.path.join(docs_dir, "docs"), exist_ok=True)
    cmd = [sys.executable, "-m", "zdx.scripts.gen_readmes"]
    _run_command(
        cmd,
        cwd=docs_dir,
        failure_mode=failure_mode,
        description="python -m zdx.scripts.gen_readmes",
    )


def main() -> None:
    """Entry point for the ``zdx`` command-line interface.

    Parses arguments and dispatches to the requested subcommand.
    RETURNS (None): The CLI exits based on the invoked command.
    """

    parser = argparse.ArgumentParser(prog="zdx")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate API docs from a manifest")
    gen.add_argument("--manifest", default="api_manifest.yaml")
    gen.add_argument("--docs-dir", default=".")
    gen.add_argument("--mkdocs-yml", default="mkdocs.yml")
    gen.add_argument("--api-output-dir", default="api")
    gen.add_argument("--changed-only", action="store_true")
    _add_failure_mode_argument(gen)

    def generate_cmd(args: argparse.Namespace) -> None:
        failure_mode = FailureMode.from_value(args.on_error)
        failed = install_manifest_packages(args.manifest, failure_mode=failure_mode)
        if failed:
            print(
                "WARNING: Skipping API generation for packages that failed to "
                f"install: {', '.join(sorted(failed))}"
            )
            _prune_failed_package_docs(
                docs_dir=args.docs_dir,
                api_output_dir=args.api_output_dir,
                mkdocs_yml=args.mkdocs_yml,
                failed_packages=failed,
            )
        run_gen_api(
            manifest=args.manifest,
            docs_dir=args.docs_dir,
            mkdocs_yml=args.mkdocs_yml,
            api_output_dir=args.api_output_dir,
            changed_only=args.changed_only,
            skip_packages=failed,
            failure_mode=failure_mode,
        )

    gen.set_defaults(func=generate_cmd)

    readmes = sub.add_parser("readmes", help="Generate documentation from README files")
    readmes.add_argument("--docs-dir", default=".")
    _add_failure_mode_argument(readmes)

    def readmes_cmd(args: argparse.Namespace) -> None:
        run_gen_readmes(
            docs_dir=args.docs_dir,
            failure_mode=FailureMode.from_value(args.on_error),
        )

    readmes.set_defaults(func=readmes_cmd)

    serve = sub.add_parser("serve", help="Serve the documentation with MkDocs")
    serve.add_argument("--docs-dir", default=".")
    serve.add_argument("--mkdocs-yml", default="mkdocs.yml")
    serve.add_argument("--dev-addr", default="0.0.0.0:8000")
    serve.add_argument("--manifest", default="api_manifest.yaml")
    serve.add_argument("--api-output-dir", default="api")
    serve.add_argument("--changed-only", action="store_true")
    serve.add_argument(
        "--generate",
        action="store_true",
        help="Generate API docs before serving",
    )
    _add_failure_mode_argument(serve)

    def serve_cmd(args: argparse.Namespace) -> None:
        failure_mode = FailureMode.from_value(args.on_error)
        failed = install_manifest_packages(args.manifest, failure_mode=failure_mode)
        if failed:
            print(
                "WARNING: Skipping API generation for packages that failed to "
                f"install: {', '.join(sorted(failed))}"
            )
            _prune_failed_package_docs(
                docs_dir=args.docs_dir,
                api_output_dir=args.api_output_dir,
                mkdocs_yml=args.mkdocs_yml,
                failed_packages=failed,
            )
        if args.generate:
            run_gen_api(
                manifest=args.manifest,
                docs_dir=args.docs_dir,
                mkdocs_yml=args.mkdocs_yml,
                api_output_dir=args.api_output_dir,
                changed_only=args.changed_only,
                skip_packages=failed,
                failure_mode=failure_mode,
            )
        run_mkdocs_serve(
            docs_dir=args.docs_dir,
            mkdocs_yml=args.mkdocs_yml,
            dev_addr=args.dev_addr,
            failure_mode=failure_mode,
        )

    serve.set_defaults(func=serve_cmd)

    install = sub.add_parser(
        "install", help="Install packages referenced in an API manifest"
    )
    install.add_argument("--manifest", default="api_manifest.yaml")
    _add_failure_mode_argument(install)

    install.set_defaults(
        func=lambda args: install_manifest_packages(
            args.manifest, failure_mode=FailureMode.from_value(args.on_error)
        )
    )

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
