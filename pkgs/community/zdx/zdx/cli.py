"""Command-line helpers for the ZDX documentation toolkit."""

import argparse
import os
import shlex
import subprocess
import sys
from enum import Enum
from typing import Sequence
from pathlib import Path

import yaml

from zdx.scripts.gen_api import discover_packages, load_manifest


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
    failure_mode: FailureMode = FailureMode.FAIL,
) -> None:
    """Run the API docs generation script.

    manifest (str): Path to the API manifest YAML file.
    docs_dir (str): Directory containing documentation sources.
    mkdocs_yml (str): Path to the MkDocs configuration file.
    api_output_dir (str): Relative output directory for API pages.
    changed_only (bool): Only rebuild pages for changed sources.
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
    _run_command(cmd, failure_mode=failure_mode)


def _resolve_workspace_directory(manifest_path: Path) -> Path | None:
    """Return the workspace root defined in the manifest, if any."""

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

    workspace_dir: Path | None = None
    if isinstance(workspace_cfg, str):
        workspace_dir = _make_path(workspace_cfg)
    elif isinstance(workspace_cfg, dict):
        if "pyproject" in workspace_cfg:
            pyproject_path = _make_path(workspace_cfg["pyproject"])
            workspace_dir = pyproject_path.parent
        elif "root" in workspace_cfg:
            workspace_dir = _make_path(workspace_cfg["root"])

    if not workspace_dir:
        return None

    if workspace_dir.is_file():
        workspace_dir = workspace_dir.parent

    pyproject = workspace_dir / "pyproject.toml"
    if not pyproject.is_file():
        return None

    return workspace_dir


def install_manifest_packages(
    manifest: str, failure_mode: FailureMode = FailureMode.FAIL
) -> None:
    """Install all packages referenced in the API manifest.

    This ensures modules documented via ``mkdocstrings`` can be imported
    successfully when building or serving the docs.

    failure_mode (FailureMode): Strategy for handling installation errors.
    """

    manifest_path = Path(manifest).resolve()
    workspace_dir = _resolve_workspace_directory(manifest_path)

    workspace_result: subprocess.CompletedProcess[bytes] | None = None
    if workspace_dir is not None:
        cmd = [
            "uv",
            "pip",
            "install",
            "--directory",
            str(workspace_dir),
        ]
        if not (os.environ.get("VIRTUAL_ENV") or sys.prefix != sys.base_prefix):
            cmd.append("--system")
        cmd.append(".")
        workspace_result = _run_command(
            cmd,
            failure_mode=failure_mode,
            description=f"uv pip install --directory {workspace_dir}",
        )

    targets = load_manifest(manifest)
    package_dirs = set()
    for t in targets:
        if t.package:
            package_dirs.add(t.search_path)
        if t.discover:
            for _, pkg_dir in discover_packages(t.search_path):
                package_dirs.add(pkg_dir)

    manifest_parent = manifest_path.parent
    workspace_success = (
        workspace_result is not None and workspace_result.returncode == 0
    )

    for pkg_dir in sorted(package_dirs):
        pkg_path = Path(pkg_dir)
        if not pkg_path.is_absolute():
            pkg_path = (manifest_parent / pkg_path).resolve()

        if workspace_success and workspace_dir is not None:
            if pkg_path.is_relative_to(workspace_dir):
                continue
        if not pkg_path.is_dir():
            continue
        if not (
            (pkg_path / "pyproject.toml").is_file() or (pkg_path / "setup.py").is_file()
        ):
            print(f"Skipping {pkg_path}: no pyproject.toml or setup.py found")
            continue
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
        _run_command(
            cmd,
            failure_mode=failure_mode,
            description=f"uv pip install --directory {pkg_path}",
        )


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
        install_manifest_packages(args.manifest, failure_mode=failure_mode)
        run_gen_api(
            manifest=args.manifest,
            docs_dir=args.docs_dir,
            mkdocs_yml=args.mkdocs_yml,
            api_output_dir=args.api_output_dir,
            changed_only=args.changed_only,
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
        install_manifest_packages(args.manifest, failure_mode=failure_mode)
        if args.generate:
            run_gen_api(
                manifest=args.manifest,
                docs_dir=args.docs_dir,
                mkdocs_yml=args.mkdocs_yml,
                api_output_dir=args.api_output_dir,
                changed_only=args.changed_only,
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
