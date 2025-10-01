from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "zdx"))

from zdx.cli import install_manifest_packages


def _create_package(root: Path, name: str) -> Path:
    package_dir = root / name
    src_dir = package_dir / name.replace("-", "_")
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text("__all__ = ()\n")
    (package_dir / "pyproject.toml").write_text(
        """
[project]
name = "test-package"
version = "0.1.0"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
""".strip()
    )
    return package_dir


def test_install_manifest_packages_uses_workspace(monkeypatch, tmp_path):
    repo_root = tmp_path
    workspace_pyproject = repo_root / "pyproject.toml"
    first_pkg = _create_package(repo_root, "alpha")
    second_pkg = _create_package(repo_root, "beta")

    workspace_pyproject.write_text(
        """
[project]
name = "monorepo"
version = "0.0.1"
description = "test"
requires-python = ">=3.10"
package = false

[tool.uv.workspace]
members = ["alpha", "beta"]
""".strip()
    )

    manifest = repo_root / "api_manifest.yaml"
    manifest.write_text(
        "\n".join(
            [
                f"workspace_pyproject: {workspace_pyproject}",
                "targets:",
                "  - name: Alpha",
                "    package: alpha",
                f"    search_path: {first_pkg}",
                "  - name: Beta",
                "    package: beta",
                f"    search_path: {second_pkg}",
            ]
        )
    )

    called_commands: list[list[str]] = []

    def fake_run(cmd, check):
        called_commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    # Ensure the environment appears as a system interpreter so --system is added
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    monkeypatch.setenv("PATH", os.environ.get("PATH", ""))

    install_manifest_packages(str(manifest))

    assert len(called_commands) == 1
    cmd = called_commands[0]
    assert cmd[0] == "uv"
    assert cmd[1:3] == ["pip", "install"]
    assert "--editable" in cmd
    assert any(str(first_pkg) == entry for entry in cmd)
    assert any(str(second_pkg) == entry for entry in cmd)


def test_install_manifest_packages_falls_back_for_missing_members(
    monkeypatch, tmp_path
):
    repo_root = tmp_path
    workspace_pyproject = repo_root / "pyproject.toml"
    first_pkg = _create_package(repo_root, "alpha")
    second_pkg = _create_package(repo_root, "beta")
    extra_pkg = _create_package(repo_root, "gamma")

    workspace_pyproject.write_text(
        """
[project]
name = "monorepo"
version = "0.0.1"
description = "test"
requires-python = ">=3.10"
package = false

[tool.uv.workspace]
members = ["alpha", "beta"]
""".strip()
    )

    manifest = repo_root / "api_manifest.yaml"
    manifest.write_text(
        "\n".join(
            [
                f"workspace_pyproject: {workspace_pyproject}",
                "targets:",
                "  - name: Alpha",
                "    package: alpha",
                f"    search_path: {first_pkg}",
                "  - name: Beta",
                "    package: beta",
                f"    search_path: {second_pkg}",
                "  - name: Gamma",
                "    package: gamma",
                f"    search_path: {extra_pkg}",
            ]
        )
    )

    called_commands: list[list[str]] = []

    def fake_run(cmd, check, **kwargs):
        called_commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    install_manifest_packages(str(manifest))

    assert len(called_commands) == 2
    workspace_cmd, fallback_cmd = called_commands

    assert workspace_cmd[:3] == ["uv", "pip", "install"]
    assert "--editable" in workspace_cmd
    assert any(str(first_pkg) == entry for entry in workspace_cmd)
    assert any(str(second_pkg) == entry for entry in workspace_cmd)

    assert fallback_cmd[:3] == ["uv", "pip", "install"]
    assert "--directory" in fallback_cmd
    assert str(extra_pkg) in fallback_cmd
