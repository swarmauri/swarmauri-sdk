"""Command line utility for interacting with the MediaSigner facade."""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

from .signer import MediaSigner

BytesLike = bytes | bytearray


def _read_bytes(path: str | None) -> bytes:
    if path is None or path == "-":
        return sys.stdin.buffer.read()
    return Path(path).read_bytes()


def _write_text(path: str | None, content: str) -> None:
    if path is None or path == "-":
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
        return
    Path(path).write_text(content)


def _load_json_file(path: str | None) -> Any:
    if path is None:
        return None
    data = Path(path).read_text()
    return json.loads(data)


def _bytes_field(value: BytesLike) -> dict[str, str]:
    return {"b64": base64.b64encode(bytes(value)).decode("ascii")}


def _signature_to_json(signature: Mapping[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for key, value in signature.items():
        if isinstance(value, (bytes, bytearray)):
            record[key] = _bytes_field(value)
        elif (
            isinstance(value, tuple)
            and value
            and isinstance(value[0], (bytes, bytearray))
        ):
            record[key] = [_bytes_field(item) for item in value]  # type: ignore[arg-type]
        else:
            record[key] = value
    return record


def _signature_from_json(data: Mapping[str, Any]) -> MutableMapping[str, Any]:
    result: MutableMapping[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, Mapping) and "b64" in value:
            result[key] = base64.b64decode(str(value["b64"]))
        elif (
            isinstance(value, list)
            and value
            and isinstance(value[0], Mapping)
            and "b64" in value[0]
        ):
            result[key] = tuple(base64.b64decode(str(entry["b64"])) for entry in value)
        else:
            result[key] = value
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Interact with Swarmauri signing plugins"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List discovered signing formats")
    list_parser.set_defaults(func=_cmd_list)

    supports_parser = subparsers.add_parser(
        "supports", help="Describe plugin capabilities"
    )
    supports_parser.add_argument("format", help="Format token, e.g. jws or cms")
    supports_parser.add_argument(
        "--key-ref", dest="key_ref", help="Optional key reference string"
    )
    supports_parser.set_defaults(func=_cmd_supports)

    sign_parser = subparsers.add_parser(
        "sign-bytes", help="Sign raw bytes using a plugin"
    )
    sign_parser.add_argument("format", help="Format token")
    sign_parser.add_argument("--alg", dest="alg", help="Algorithm hint for the signer")
    sign_parser.add_argument(
        "--key", required=True, help="Path to a JSON file describing the KeyRef"
    )
    sign_parser.add_argument("--input", required=True, help="Payload file to sign")
    sign_parser.add_argument(
        "--output", help="Write signatures to this file (defaults to stdout)"
    )
    sign_parser.add_argument("--opts", help="Path to JSON options passed to the signer")
    sign_parser.set_defaults(func=_cmd_sign_bytes)

    verify_parser = subparsers.add_parser(
        "verify-bytes", help="Verify signatures over raw bytes"
    )
    verify_parser.add_argument("format", help="Format token")
    verify_parser.add_argument("--input", required=True, help="Payload file")
    verify_parser.add_argument(
        "--sigs", required=True, help="JSON file produced by sign-bytes"
    )
    verify_parser.add_argument(
        "--opts", help="JSON file providing verification options"
    )
    verify_parser.add_argument(
        "--require", help="JSON file describing verification policy"
    )
    verify_parser.set_defaults(func=_cmd_verify_bytes)

    return parser


async def _cmd_list(args: argparse.Namespace) -> int:
    signer = Signer()
    for fmt in sorted(signer.supported_formats()):
        print(fmt)
    return 0


async def _cmd_supports(args: argparse.Namespace) -> int:
    signer = Signer()
    info = signer.supports(args.format, key_ref=args.key_ref)
    print(json.dumps(info, indent=2, sort_keys=True))
    return 0


async def _cmd_sign_bytes(args: argparse.Namespace) -> int:
    signer = Signer()
    key_data = _load_json_file(args.key)
    if not isinstance(key_data, Mapping):
        raise SystemExit("--key must reference a JSON object")
    payload = _read_bytes(args.input)
    opts = _load_json_file(args.opts)
    signatures = await signer.sign_bytes(
        args.format, key_data, payload, alg=args.alg, opts=opts
    )
    json_out = [_signature_to_json(dict(sig)) for sig in signatures]
    _write_text(args.output, json.dumps(json_out, indent=2))
    return 0


async def _cmd_verify_bytes(args: argparse.Namespace) -> int:
    signer = Signer()
    payload = _read_bytes(args.input)
    sig_payload = _load_json_file(args.sigs)
    if not isinstance(sig_payload, list):
        raise SystemExit("--sigs must point to a JSON array")
    signature_entries = [_signature_from_json(entry) for entry in sig_payload]
    opts = _load_json_file(args.opts)
    require = _load_json_file(args.require)
    ok = await signer.verify_bytes(
        args.format,
        payload,
        signature_entries,
        require=require,
        opts=opts,
    )
    print("true" if ok else "false")
    return 0 if ok else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return asyncio.run(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
