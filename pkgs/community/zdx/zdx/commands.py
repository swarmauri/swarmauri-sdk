"""Command execution helpers for the ZDX CLI."""

import subprocess
import sys


def run_gen_api(
    manifest: str = "api_manifest.yaml",
    docs_dir: str = ".",
    mkdocs_yml: str = "mkdocs.yml",
    api_output_dir: str = "api",
    changed_only: bool = False,
) -> None:
    """Run the API docs generation script.

    manifest (str): Path to the API manifest YAML file.
    docs_dir (str): Directory containing documentation sources.
    mkdocs_yml (str): Path to the MkDocs configuration file.
    api_output_dir (str): Relative output directory for API pages.
    changed_only (bool): Only rebuild pages for changed sources.
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
    subprocess.run(cmd, check=True)


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
    cmd = ["mkdocs", "serve", "-f", mkdocs_yml, "-a", dev_addr]
    subprocess.run(cmd, check=True, cwd=docs_dir)


def run_gen_readmes(docs_dir: str = ".") -> None:
    """Run the README generation script.

    docs_dir (str): Root directory containing project documentation.
    RETURNS (None): This function operates via side effects.
    """
    cmd = [sys.executable, "-m", "zdx.scripts.gen_readmes"]
    subprocess.run(cmd, check=True, cwd=docs_dir)


__all__ = ["run_gen_api", "run_mkdocs_serve", "run_gen_readmes"]
