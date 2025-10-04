"""CLI tests for the EmbeddedSigner utility."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from EmbeddedSigner import cli
from swarmauri_core.signing.types import Signature


class _StubSigner:
    instances: list["_StubSigner"] = []

    def __init__(self, *args, **kwargs) -> None:
        self.embed_calls: list[tuple[bytes, str, str | None]] = []
        self.remove_calls: list[Path] = []
        self.sign_calls: list[tuple[str, object, bool, str | None, dict | None]] = []
        self.read_responses: dict[Path, str | None] = {}
        _StubSigner.instances.append(self)

    def embed_bytes(
        self, data: bytes, xmp_xml: str, *, path: Path | None = None
    ) -> bytes:
        self.embed_calls.append((data, xmp_xml, None if path is None else str(path)))
        return b"embedded"

    def read_xmp_file(self, path: Path) -> str | None:
        return self.read_responses.get(path, "<x/>")

    def remove_xmp_file(self, path: Path) -> bytes:
        self.remove_calls.append(path)
        return b"stripped"

    async def sign_file(
        self,
        path: Path,
        *,
        fmt: str,
        key,
        attached: bool,
        alg: str | None,
        signer_opts: dict | None = None,
    ):
        self.sign_calls.append((fmt, key, attached, alg, signer_opts))
        return [
            Signature(
                kid="k",
                version=1,
                format=fmt,
                mode="attached" if attached else "detached",
                alg=alg or "none",
                artifact=b"sig",
            )
        ]


@pytest.fixture(autouse=True)
def _reset_stub(monkeypatch):
    _StubSigner.instances.clear()
    monkeypatch.setattr(cli, "EmbedSigner", _StubSigner)
    yield
    _StubSigner.instances.clear()


def test_embed_command_writes_output(tmp_path: Path) -> None:
    src = tmp_path / "image.png"
    src.write_bytes(b"payload")
    out = tmp_path / "out.png"

    rc = cli.main(["embed", str(src), "--xmp", "<x/>", "--output", str(out)])

    assert rc == 0
    assert out.read_bytes() == b"embedded"
    stub = _StubSigner.instances[0]
    assert stub.embed_calls[0][0] == b"payload"
    assert stub.embed_calls[0][1] == "<x/>"


def test_read_command_prints_metadata(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "image.png"
    src.write_bytes(b"payload")

    rc = cli.main(["read", str(src)])

    captured = capsys.readouterr()
    assert rc == 0
    assert "<x/>" in captured.out


def test_sign_command_outputs_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "asset.bin"
    src.write_bytes(b"payload")

    rc = cli.main(
        [
            "sign",
            str(src),
            "--format",
            "JWSSigner",
            "--key-ref",
            "provider:key",
        ]
    )

    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload[0]["format"] == "JWSSigner"
    assert payload[0]["artifact"]
    stub = _StubSigner.instances[0]
    fmt, key, attached, alg, _ = stub.sign_calls[0]
    assert fmt == "JWSSigner"
    assert key == "provider:key"
    assert attached is True
    assert alg is None
