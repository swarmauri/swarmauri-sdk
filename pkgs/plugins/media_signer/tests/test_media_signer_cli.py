import copy
import importlib
import json
from typing import Dict

import pytest

from swarmauri_core.signing.types import Signature

import MediaSigner.cli as cli
from MediaSigner import MediaSigner
from swarmauri_base.signing.SigningBase import SigningBase


FORMATS = ("cms", "jws", "openpgp", "pdf", "xmld")


class _BaseStubSigner(SigningBase):
    """Stub ``SigningBase`` implementation for exercising the facade."""

    FORMAT: str = "stub"

    def __init__(self, **data):
        super().__init__(**data)
        self.sign_inputs: list[dict[str, object]] = []
        self.verify_inputs: list[dict[str, object]] = []
        self.last_signature: Signature | None = None

    def supports(self, key_ref: str | None = None):  # type: ignore[override]
        info: dict[str, object] = {
            "formats": [self.FORMAT],
            "modes": ["detached"],
        }
        if key_ref is not None:
            info["key_ref"] = key_ref
        return info

    async def sign_bytes(  # type: ignore[override]
        self,
        key,
        payload: bytes,
        *,
        alg: str | None = None,
        opts: dict[str, object] | None = None,
    ) -> list[Signature]:
        artifact = bytes(payload)
        signature = Signature(
            kid=str(key.get("kid", "stub")) if isinstance(key, dict) else None,
            version=key.get("version") if isinstance(key, dict) else None,
            format=self.FORMAT,
            mode="detached",
            alg=alg or "stub-alg",
            artifact=artifact,
            sig=artifact[::-1],
        )
        self.sign_inputs.append(
            {
                "key": key,
                "payload": artifact,
                "alg": alg,
                "opts": opts,
            }
        )
        self.last_signature = signature
        return [signature]

    async def verify_bytes(  # type: ignore[override]
        self,
        payload: bytes,
        signatures,
        *,
        require=None,
        opts=None,
    ) -> bool:
        if not signatures:
            return False
        first = signatures[0]
        if isinstance(first, Signature):
            artifact = first.artifact
        else:
            artifact = first.get("artifact")
        self.verify_inputs.append(
            {
                "payload": payload,
                "signatures": signatures,
                "require": require,
                "opts": opts,
            }
        )
        return artifact == payload


def _make_stub(format_name: str):
    return type(
        f"Stub{format_name.upper()}Signer",
        (_BaseStubSigner,),
        {
            "__module__": __name__,
            "FORMAT": format_name,
            "__annotations__": {"FORMAT": str},
        },
    )


@pytest.fixture()
def stub_signer_registry(monkeypatch) -> Dict[str, type[_BaseStubSigner]]:
    """Replace the dynamic registry with deterministic stub plugins."""

    original_entry = copy.deepcopy(SigningBase._registry.get("SigningBase"))
    subtypes = {fmt: _make_stub(fmt) for fmt in FORMATS}
    monkeypatch.setitem(
        SigningBase._registry,
        "SigningBase",
        {"model_cls": SigningBase, "subtypes": subtypes},
    )
    try:
        yield subtypes
    finally:
        if original_entry is None:
            SigningBase._registry.pop("SigningBase", None)
        else:
            SigningBase._registry["SigningBase"] = original_entry


def test_can_import_media_signer():
    module = importlib.import_module("MediaSigner")
    assert hasattr(module, "MediaSigner")


@pytest.mark.asyncio()
async def test_sign_bytes_across_all_formats(stub_signer_registry):
    signer = MediaSigner()
    assert set(signer.supported_formats()) == set(FORMATS)
    key = {"kid": "k1", "version": 1}
    payload = b"payload"

    for fmt in FORMATS:
        result = await signer.sign_bytes(fmt, key, payload)
        assert result and result[0].format == fmt
        plugin = signer._plugins[fmt]
        assert plugin.sign_inputs
        ok = await signer.verify_bytes(fmt, payload, result)
        assert ok
        assert plugin.verify_inputs


def test_cli_list_outputs_all_formats(stub_signer_registry, capsys):
    exit_code = cli.main(["list"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert captured.out.splitlines() == sorted(FORMATS)


def test_cli_supports_emits_json(stub_signer_registry, capsys):
    exit_code = cli.main(["supports", "cms", "--key-ref", "primary"])
    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert data["formats"] == ["cms"]
    assert data["modes"] == ["detached"]
    assert data["key_ref"] == "primary"


def test_cli_sign_and_verify_roundtrip(stub_signer_registry, tmp_path, capsys):
    key_path = tmp_path / "key.json"
    key_path.write_text(json.dumps({"kid": "k1", "version": 1}))

    payload_path = tmp_path / "payload.bin"
    payload = b"payload"
    payload_path.write_bytes(payload)

    exit_code = cli.main(
        [
            "sign-bytes",
            "cms",
            "--key",
            str(key_path),
            "--input",
            str(payload_path),
            "--output",
            "-",
        ]
    )
    assert exit_code == 0
    sign_out = capsys.readouterr()
    signatures_json = sign_out.out
    signatures = json.loads(signatures_json)
    assert signatures[0]["format"] == "cms"

    sig_path = tmp_path / "signatures.json"
    sig_path.write_text(signatures_json)

    exit_code = cli.main(
        [
            "verify-bytes",
            "cms",
            "--input",
            str(payload_path),
            "--sigs",
            str(sig_path),
        ]
    )
    verify_out = capsys.readouterr()
    assert exit_code == 0
    assert verify_out.out.strip() == "true"
    assert verify_out.err == ""
