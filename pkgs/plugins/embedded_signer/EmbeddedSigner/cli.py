"""Command line interface for the :mod:`EmbeddedSigner` plugin."""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from ._embed_signer import EmbedSigner


def _load_xmp_from_args(args: argparse.Namespace) -> str:
    if args.xmp is not None and args.xmp_file is not None:
        raise SystemExit("Specify either --xmp or --xmp-file, not both.")
    if args.xmp is not None:
        return args.xmp
    if args.xmp_file is not None:
        return Path(args.xmp_file).read_text(encoding="utf-8")
    raise SystemExit("An XMP payload is required for this command.")


def _resolve_key_argument(args: argparse.Namespace) -> Any:
    provided = [
        value
        for value in (args.key_ref, args.key_json, args.key_file)
        if value is not None
    ]
    if len(provided) != 1:
        raise SystemExit("Provide exactly one of --key-ref, --key-json, or --key-file.")
    if args.key_ref:
        return args.key_ref
    if args.key_json:
        try:
            return json.loads(args.key_json)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise SystemExit(f"Invalid JSON passed to --key-json: {exc}") from exc
    if args.key_file:
        return json.loads(Path(args.key_file).read_text(encoding="utf-8"))
    raise SystemExit("A key reference or JSON description must be supplied.")


def _serialise_signature(signature: Mapping[str, Any]) -> Mapping[str, Any]:
    payload: dict[str, Any] = dict(signature)
    artifact = payload.get("artifact")
    if isinstance(artifact, (bytes, bytearray)):
        payload["artifact"] = base64.b64encode(artifact).decode("ascii")
        payload.setdefault("artifact_encoding", "base64")
    return payload


def _create_signer(args: argparse.Namespace) -> EmbedSigner:
    provider_name = getattr(args, "key_provider", None)
    return EmbedSigner(key_provider_name=provider_name)


def _command_embed(args: argparse.Namespace) -> int:
    signer = _create_signer(args)
    xmp_xml = _load_xmp_from_args(args)
    src = Path(args.input)
    payload = src.read_bytes()
    updated = signer.embed_bytes(payload, xmp_xml, path=src)
    target = Path(args.output) if args.output else src
    target.write_bytes(updated)
    return 0


def _command_read(args: argparse.Namespace) -> int:
    signer = _create_signer(args)
    src = Path(args.input)
    metadata = signer.read_xmp_file(src)
    if metadata is None:
        return 1
    sys.stdout.write(metadata)
    if not metadata.endswith("\n"):
        sys.stdout.write("\n")
    return 0


def _command_remove(args: argparse.Namespace) -> int:
    signer = _create_signer(args)
    src = Path(args.input)
    updated = signer.remove_xmp_file(src)
    target = Path(args.output) if args.output else src
    target.write_bytes(updated)
    return 0


async def _async_sign(
    signer: EmbedSigner,
    *,
    src: Path,
    fmt: str,
    key: Any,
    attached: bool,
    alg: str | None,
    opts: Mapping[str, Any] | None,
) -> Sequence[Mapping[str, Any]]:
    signatures = await signer.sign_file(
        src,
        fmt=fmt,
        key=key,
        attached=attached,
        alg=alg,
        signer_opts=opts,
    )
    return [_serialise_signature(sig) for sig in signatures]


def _command_sign(args: argparse.Namespace) -> int:
    signer = _create_signer(args)
    src = Path(args.input)
    key = _resolve_key_argument(args)
    opts: dict[str, Any] | None = None
    if args.option:
        opts = {}
        for token in args.option:
            name, _, value = token.partition("=")
            if not name:
                raise SystemExit("Signer options must use the form name=value.")
            opts[name] = value
    signatures = asyncio.run(
        _async_sign(
            signer,
            src=src,
            fmt=args.format,
            key=key,
            attached=not args.detached,
            alg=args.alg,
            opts=opts,
        )
    )
    output = json.dumps(signatures, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")
    return 0


async def _async_embed_sign(
    signer: EmbedSigner,
    *,
    src: Path,
    fmt: str,
    xmp_xml: str,
    key: Any,
    attached: bool,
    alg: str | None,
    opts: Mapping[str, Any] | None,
    write_back: bool,
    output: Path | None,
) -> Sequence[Mapping[str, Any]]:
    embedded, signatures = await signer.embed_and_sign_file(
        src,
        fmt=fmt,
        xmp_xml=xmp_xml,
        key=key,
        attached=attached,
        alg=alg,
        signer_opts=opts,
        write_back=write_back and output is None,
    )
    if output is not None:
        output.write_bytes(embedded)
    return [_serialise_signature(sig) for sig in signatures]


def _command_embed_sign(args: argparse.Namespace) -> int:
    signer = _create_signer(args)
    src = Path(args.input)
    xmp_xml = _load_xmp_from_args(args)
    key = _resolve_key_argument(args)
    opts: dict[str, Any] | None = None
    if args.option:
        opts = {}
        for token in args.option:
            name, _, value = token.partition("=")
            if not name:
                raise SystemExit("Signer options must use the form name=value.")
            opts[name] = value
    output_path = Path(args.output) if args.output else None
    signatures = asyncio.run(
        _async_embed_sign(
            signer,
            src=src,
            fmt=args.format,
            xmp_xml=xmp_xml,
            key=key,
            attached=not args.detached,
            alg=args.alg,
            opts=opts,
            write_back=args.write_back,
            output=output_path,
        )
    )
    output = json.dumps(signatures, indent=2)
    if args.signature_output:
        Path(args.signature_output).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Embed XMP metadata and sign media.")
    parser.add_argument(
        "--key-provider",
        dest="key_provider",
        help="Default key provider to use when resolving key references.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    embed_parser = subparsers.add_parser("embed", help="Embed XMP into a file")
    embed_parser.add_argument("input", help="Path to the media file")
    embed_parser.add_argument("--xmp", help="Inline XMP XML payload")
    embed_parser.add_argument("--xmp-file", help="Read the XMP payload from a file")
    embed_parser.add_argument("--output", help="Write the embedded media to this path")
    embed_parser.set_defaults(func=_command_embed)

    read_parser = subparsers.add_parser("read", help="Read XMP metadata from a file")
    read_parser.add_argument("input", help="Path to the media file")
    read_parser.set_defaults(func=_command_read)

    remove_parser = subparsers.add_parser(
        "remove", help="Strip XMP metadata from a file"
    )
    remove_parser.add_argument("input", help="Path to the media file")
    remove_parser.add_argument("--output", help="Write the stripped media to this path")
    remove_parser.set_defaults(func=_command_remove)

    sign_parser = subparsers.add_parser("sign", help="Generate signatures for a file")
    sign_parser.add_argument("input", help="Path to the media file")
    sign_parser.add_argument("--format", required=True, help="MediaSigner format name")
    sign_parser.add_argument("--key-ref", dest="key_ref", help="Key reference string")
    sign_parser.add_argument(
        "--key-json",
        dest="key_json",
        help="Inline JSON description of the signing key",
    )
    sign_parser.add_argument(
        "--key-file",
        dest="key_file",
        help="Path to a JSON file describing the signing key",
    )
    sign_parser.add_argument(
        "--option",
        action="append",
        help="Additional signer option in the form name=value",
    )
    sign_parser.add_argument("--alg", help="Explicit algorithm identifier")
    sign_parser.add_argument(
        "--detached",
        action="store_true",
        help="Produce detached signatures when supported",
    )
    sign_parser.add_argument(
        "--output", help="Write the generated signatures to a file"
    )
    sign_parser.set_defaults(func=_command_sign)

    embed_sign_parser = subparsers.add_parser(
        "embed-sign", help="Embed metadata and sign the updated file"
    )
    embed_sign_parser.add_argument("input", help="Path to the media file")
    embed_sign_parser.add_argument("--xmp", help="Inline XMP XML payload")
    embed_sign_parser.add_argument(
        "--xmp-file", help="Read the XMP payload from a file"
    )
    embed_sign_parser.add_argument(
        "--format", required=True, help="MediaSigner format name"
    )
    embed_sign_parser.add_argument(
        "--key-ref", dest="key_ref", help="Key reference string"
    )
    embed_sign_parser.add_argument(
        "--key-json",
        dest="key_json",
        help="Inline JSON description of the signing key",
    )
    embed_sign_parser.add_argument(
        "--key-file",
        dest="key_file",
        help="Path to a JSON file describing the signing key",
    )
    embed_sign_parser.add_argument(
        "--option",
        action="append",
        help="Additional signer option in the form name=value",
    )
    embed_sign_parser.add_argument("--alg", help="Explicit algorithm identifier")
    embed_sign_parser.add_argument(
        "--detached",
        action="store_true",
        help="Produce detached signatures when supported",
    )
    embed_sign_parser.add_argument(
        "--write-back",
        action="store_true",
        help="Persist embedded bytes back to the original input file",
    )
    embed_sign_parser.add_argument(
        "--output",
        help="Write embedded bytes to this path instead of the input file",
    )
    embed_sign_parser.add_argument(
        "--signature-output",
        help="Write generated signatures to this JSON file",
    )
    embed_sign_parser.set_defaults(func=_command_embed_sign)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
