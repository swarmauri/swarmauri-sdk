import subprocess

import pytest
import yaml

from zdx.cli import (
    FailureMode,
    install_manifest_packages,
    run_gen_api,
    run_gen_readmes,
    run_mkdocs_build,
    run_mkdocs_serve,
)


def _write_manifest(tmp_path, targets):
    manifest = tmp_path / "api_manifest.yaml"
    manifest.write_text(yaml.safe_dump({"targets": targets}))
    return manifest


def test_install_packages_warn_continues(monkeypatch, tmp_path, capsys):
    pkg_one = tmp_path / "pkg_one"
    pkg_two = tmp_path / "pkg_two"
    pkg_one.mkdir()
    pkg_two.mkdir()
    (pkg_one / "pyproject.toml").write_text("")
    (pkg_two / "pyproject.toml").write_text("")

    manifest = _write_manifest(
        tmp_path,
        [
            {"name": "One", "search_path": str(pkg_one), "package": "pkg_one"},
            {"name": "Two", "search_path": str(pkg_two), "package": "pkg_two"},
        ],
    )

    calls = []

    def fake_run(cmd, cwd=None, check=False):
        returncode = 1 if len(calls) == 0 else 0
        calls.append((cmd, cwd, check, returncode))
        return subprocess.CompletedProcess(cmd, returncode)

    monkeypatch.setattr("zdx.cli.subprocess.run", fake_run)

    failed = install_manifest_packages(str(manifest), failure_mode=FailureMode.WARN)

    assert len(calls) == 2
    assert failed == {"pkg_one"}
    output = capsys.readouterr().out
    assert "WARNING" in output


def test_install_packages_fail_raises(monkeypatch, tmp_path):
    pkg_dir = tmp_path / "pkg_fail"
    pkg_dir.mkdir()
    (pkg_dir / "pyproject.toml").write_text("")

    manifest = _write_manifest(
        tmp_path, [{"name": "One", "search_path": str(pkg_dir), "package": "pkg_fail"}]
    )

    def always_fail(cmd, cwd=None, check=False):
        return subprocess.CompletedProcess(cmd, 1)

    monkeypatch.setattr("zdx.cli.subprocess.run", always_fail)

    with pytest.raises(subprocess.CalledProcessError):
        install_manifest_packages(str(manifest), failure_mode=FailureMode.FAIL)


def test_install_packages_workspace(monkeypatch, tmp_path):
    workspace = tmp_path / "repo"
    package_dir = workspace / "pkg_one"
    workspace.mkdir()
    package_dir.mkdir(parents=True)
    (workspace / "pyproject.toml").write_text("")
    (package_dir / "pyproject.toml").write_text("")

    manifest = tmp_path / "api_manifest.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "workspace": {"pyproject": str(workspace / "pyproject.toml")},
                "targets": [
                    {
                        "name": "One",
                        "search_path": str(package_dir),
                        "package": "pkg_one",
                    }
                ],
            }
        )
    )

    calls = []

    def fake_run(cmd, cwd=None, check=False):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr("zdx.cli.subprocess.run", fake_run)

    failed = install_manifest_packages(str(manifest), failure_mode=FailureMode.FAIL)

    assert len(calls) == 1
    assert calls[0][:4] == ["uv", "pip", "install", "--directory"]
    assert str(workspace) == calls[0][4]
    assert calls[0][-1] == "."
    assert failed == set()


def test_install_packages_workspace_warn_runs_package(monkeypatch, tmp_path):
    workspace = tmp_path / "repo"
    package_dir = workspace / "pkg_one"
    workspace.mkdir()
    package_dir.mkdir(parents=True)
    (workspace / "pyproject.toml").write_text("")
    (package_dir / "pyproject.toml").write_text("")

    manifest = tmp_path / "api_manifest.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "workspace": {"root": str(workspace)},
                "targets": [
                    {
                        "name": "One",
                        "search_path": str(package_dir),
                        "package": "pkg_one",
                    }
                ],
            }
        )
    )

    calls = []

    def fake_run(cmd, cwd=None, check=False):
        returncode = 1 if not calls else 0
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, returncode)

    monkeypatch.setattr("zdx.cli.subprocess.run", fake_run)

    failed = install_manifest_packages(str(manifest), failure_mode=FailureMode.WARN)

    assert len(calls) == 2
    assert calls[0][:4] == ["uv", "pip", "install", "--directory"]
    assert calls[1][:4] == ["uv", "pip", "install", "--directory"]
    assert failed == set()


def test_run_gen_api_ignore_suppresses_warning(monkeypatch, capsys):
    calls = []

    def fake_run(cmd, cwd=None, check=False):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 1)

    monkeypatch.setattr("zdx.cli.subprocess.run", fake_run)

    run_gen_api(failure_mode=FailureMode.IGNORE)

    assert len(calls) == 1
    output = capsys.readouterr().out
    assert "WARNING" not in output


def test_run_gen_readmes_warn_reports_but_continues(monkeypatch, tmp_path, capsys):
    def fake_run(cmd, cwd=None, check=False):
        assert cwd == str(tmp_path)
        return subprocess.CompletedProcess(cmd, 1)

    monkeypatch.setattr("zdx.cli.subprocess.run", fake_run)

    run_gen_readmes(docs_dir=str(tmp_path), failure_mode=FailureMode.WARN)

    output = capsys.readouterr().out
    assert "WARNING" in output


def test_run_gen_readmes_fail_raises(monkeypatch, tmp_path):
    def fake_run(cmd, cwd=None, check=False):
        return subprocess.CompletedProcess(cmd, 1)

    monkeypatch.setattr("zdx.cli.subprocess.run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        run_gen_readmes(docs_dir=str(tmp_path), failure_mode=FailureMode.FAIL)


def test_run_mkdocs_build_warn_reports_but_continues(monkeypatch, tmp_path, capsys):
    def fake_run(cmd, cwd=None, check=False):
        assert cwd == str(tmp_path)
        return subprocess.CompletedProcess(cmd, 1)

    monkeypatch.setattr("zdx.cli.subprocess.run", fake_run)

    run_mkdocs_build(docs_dir=str(tmp_path), failure_mode=FailureMode.WARN)

    output = capsys.readouterr().out
    assert "WARNING" in output


def test_run_mkdocs_build_fail_raises(monkeypatch, tmp_path):
    def fake_run(cmd, cwd=None, check=False):
        return subprocess.CompletedProcess(cmd, 1)

    monkeypatch.setattr("zdx.cli.subprocess.run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        run_mkdocs_build(docs_dir=str(tmp_path), failure_mode=FailureMode.FAIL)


def test_run_mkdocs_serve_warn_reports_but_continues(monkeypatch, tmp_path, capsys):
    def fake_run(cmd, cwd=None, check=False):
        assert cwd == str(tmp_path)
        return subprocess.CompletedProcess(cmd, 1)

    monkeypatch.setattr("zdx.cli.subprocess.run", fake_run)

    run_mkdocs_serve(docs_dir=str(tmp_path), failure_mode=FailureMode.WARN)

    output = capsys.readouterr().out
    assert "WARNING" in output


def test_run_mkdocs_serve_fail_raises(monkeypatch, tmp_path):
    def fake_run(cmd, cwd=None, check=False):
        return subprocess.CompletedProcess(cmd, 1)

    monkeypatch.setattr("zdx.cli.subprocess.run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        run_mkdocs_serve(docs_dir=str(tmp_path), failure_mode=FailureMode.FAIL)
