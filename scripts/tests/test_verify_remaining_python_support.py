import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location(
    "verify_remaining_python_support",
    Path(__file__).resolve().parents[1] / "verify_remaining_python_support.py",
)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def test_waits_for_successful_index_installation(monkeypatch):
    responses = iter(
        [
            SimpleNamespace(returncode=1, stdout="", stderr="No matching version"),
            SimpleNamespace(returncode=0, stdout="Installed", stderr=""),
        ]
    )
    calls = []

    def install(command, **kwargs):
        calls.append(command)
        return next(responses)

    monkeypatch.setattr(verifier.subprocess, "run", install)
    monkeypatch.setattr(verifier.time, "sleep", lambda _: None)
    command = [
        "uv",
        "pip",
        "install",
        "--index-url",
        "https://pypi.org/simple/",
        "--no-cache",
        "--refresh",
        "swarmauri_provider_gemini==0.1.0.dev4",
    ]
    verifier.install_published_runtime(command, poll_seconds=0)
    assert calls == [command, command]
    assert "--find-links" not in calls[-1]


def test_install_failure_never_satisfies_publication_gate(monkeypatch):
    times = iter([0, 0, 2])
    monkeypatch.setattr(verifier.time, "monotonic", lambda: next(times))
    monkeypatch.setattr(verifier.time, "sleep", lambda _: None)
    monkeypatch.setattr(
        verifier.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=1, stdout="", stderr="No matching version"
        ),
    )
    with pytest.raises(TimeoutError, match="PyPI runtime installation did not succeed"):
        verifier.install_published_runtime(
            ["uv", "pip", "install"], timeout=1, poll_seconds=0
        )
