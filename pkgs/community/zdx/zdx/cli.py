"""Command-line helpers for the ZDX documentation toolkit."""

import argparse
import os
import shlex
import subprocess
import sys
from enum import Enum
from typing import Sequence

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


def install_manifest_packages(
    manifest: str, failure_mode: FailureMode = FailureMode.FAIL
) -> None:
    """Install all packages referenced in the API manifest.

    This ensures modules documented via ``mkdocstrings`` can be imported
    successfully when building or serving the docs.

    failure_mode (FailureMode): Strategy for handling installation errors.
    """

    targets = load_manifest(manifest)
    package_dirs = set()
    for t in targets:
        if t.package:
            package_dirs.add(t.search_path)
        if t.discover:
            for _, pkg_dir in discover_packages(t.search_path):
                package_dirs.add(pkg_dir)

    for pkg_dir in sorted(package_dirs):
        if not os.path.isdir(pkg_dir):
            continue
        if not (
            os.path.isfile(os.path.join(pkg_dir, "pyproject.toml"))
            or os.path.isfile(os.path.join(pkg_dir, "setup.py"))
        ):
            print(f"Skipping {pkg_dir}: no pyproject.toml or setup.py found")
            continue
        cmd = [
            "uv",
            "pip",
            "install",
            "--directory",
            pkg_dir,
        ]
        if not (os.environ.get("VIRTUAL_ENV") or sys.prefix != sys.base_prefix):
            cmd.append("--system")
        cmd.append(".")
        _run_command(
            cmd,
            failure_mode=failure_mode,
            description=f"uv pip install --directory {pkg_dir}",
        )


def run_mkdocs_serve(
    docs_dir: str = ".",
    mkdocs_yml: str = "mkdocs.yml",
    dev_addr: str = "0.0.0.0:8000",
) -> None:
    """Launch a MkDocs development server.

    docs_dir (str): Directory containing documentation sources.
    mkdocs_yml (str): Path to the MkDocs configuration file.
    dev_addr (str): Address and port for the server to bind to.
    RETURNS (None): The server runs until interrupted.
    """
    # Ensure the docs directory exists so MkDocs has a working tree.
    os.makedirs(os.path.join(docs_dir, "docs"), exist_ok=True)
    cmd = ["mkdocs", "serve", "-f", mkdocs_yml, "-a", dev_addr]
    subprocess.run(cmd, check=True, cwd=docs_dir)


def run_gen_readmes(docs_dir: str = ".") -> None:
    """Run the README generation script.

    docs_dir (str): Root directory containing project documentation.
    RETURNS (None): This function operates via side effects.
    """
    # Ensure the target docs directory exists before generating content.
    os.makedirs(os.path.join(docs_dir, "docs"), exist_ok=True)
    cmd = [sys.executable, "-m", "zdx.scripts.gen_readmes"]
    subprocess.run(cmd, check=True, cwd=docs_dir)


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
    readmes.set_defaults(func=lambda args: run_gen_readmes(docs_dir=args.docs_dir))

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
