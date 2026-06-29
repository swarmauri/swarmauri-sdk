#!/usr/bin/env python3
"""Generate entity code from source specs.

This first generator intentionally supports only the documents source-spec
family and only emits Python into an output directory or compares generated
Python with the current package sources.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "entity_specs" / "swarmauri_entities.v1.json"
DEFAULT_SPEC = REPO_ROOT / "entity_specs" / "sources" / "documents.v1.json"
DEFAULT_OUTPUT = REPO_ROOT / ".tmp_entity_generation"
SUPPORTED_FAMILY = "documents"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _quoted_default(field: dict[str, Any]) -> str | None:
    default = field.get("default")
    if default is None:
        return None
    if field.get("discriminator"):
        return repr(default).replace("'", '"')
    return str(default)


def _render_field(field: dict[str, Any]) -> str:
    annotation = field["annotation"]
    name = field["name"]
    default = _quoted_default(field)
    if field.get("required") and default is None:
        return f"    {name}: {annotation}"
    if field.get("frozen"):
        return f"    {name}: {annotation} = Field(default={default}, frozen=True)"
    return f"    {name}: {annotation} = {default}"


def _render_decorator(entity: dict[str, Any]) -> str:
    registration = entity.get("registration") or {}
    kind = registration.get("kind")
    registrar = registration.get("registrar")
    if kind == "register_model":
        return f"@{registrar}.register_model()"
    if kind == "register_type":
        base_types = registration.get("base_types") or []
        type_name = registration.get("type_name")
        if not base_types or not type_name:
            raise ValueError(f"{entity['id']} missing register_type metadata")
        return f"@{registrar}.register_type({base_types[0]}, \"{type_name}\")"
    raise ValueError(f"{entity['id']} has unsupported registration kind: {kind!r}")


def _render_python_entity(entity: dict[str, Any]) -> str:
    python = entity.get("python") or {}
    imports = python.get("imports") or []
    bases = python.get("bases") or []
    if not imports:
        raise ValueError(f"{entity['id']} missing python.imports")
    if not bases:
        raise ValueError(f"{entity['id']} missing python.bases")

    lines: list[str] = []
    lines.extend(imports)
    lines.extend(["", "", _render_decorator(entity)])
    lines.append(f"class {entity['name']}({', '.join(bases)}):")

    fields = entity.get("fields") or []
    deferred_fields = {"resource", "type"}
    model_config = python.get("model_config")
    for field in fields:
        if field.get("name") not in deferred_fields:
            lines.append(_render_field(field))
    if model_config:
        lines.append(f"    model_config = {model_config}")
    for field in fields:
        if field.get("name") in deferred_fields:
            lines.append(_render_field(field))
    return "\n".join(lines) + "\n"


def _manifest_entities(path: Path) -> dict[str, dict[str, Any]]:
    manifest = _read_json(path)
    return {
        entity["id"]: entity
        for entity in manifest.get("entities", [])
        if isinstance(entity, dict) and isinstance(entity.get("id"), str)
    }


def _load_documents_spec(spec_path: Path) -> dict[str, Any]:
    spec = _read_json(spec_path)
    family = spec.get("family")
    if family != SUPPORTED_FAMILY:
        raise SystemExit(
            f"Only the {SUPPORTED_FAMILY!r} family is supported; got {family!r}"
        )
    return spec


def _generated_files(
    spec_path: Path,
    manifest_path: Path,
) -> dict[Path, str]:
    spec = _load_documents_spec(spec_path)
    manifest = _manifest_entities(manifest_path)
    generated: dict[Path, str] = {}
    for entity in spec.get("entities", []):
        source_path = entity.get("python", {}).get("source_path")
        if not source_path:
            manifest_entity = manifest.get(entity.get("id"), {})
            source_path = manifest_entity.get("source_path")
        if not source_path:
            raise ValueError(f"{entity.get('id')} missing python.source_path")
        generated[Path(source_path)] = _render_python_entity(entity)
    return generated


def generate(spec_path: Path, manifest_path: Path, output: Path) -> None:
    generated = _generated_files(spec_path, manifest_path)
    for source_path, content in generated.items():
        target = output / source_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"Wrote {target.relative_to(REPO_ROOT).as_posix()}")


def check(spec_path: Path, manifest_path: Path) -> None:
    generated = _generated_files(spec_path, manifest_path)
    failed = False
    for source_path, expected in generated.items():
        actual_path = REPO_ROOT / source_path
        if not actual_path.is_file():
            print(f"Missing source file: {source_path.as_posix()}", file=sys.stderr)
            failed = True
            continue
        actual = _normalize_text(actual_path.read_text(encoding="utf-8"))
        expected = _normalize_text(expected)
        if actual != expected:
            failed = True
            diff = difflib.unified_diff(
                actual.splitlines(),
                expected.splitlines(),
                fromfile=source_path.as_posix(),
                tofile=f"generated/{source_path.as_posix()}",
                lineterm="",
            )
            print("\n".join(diff), file=sys.stderr)
    if failed:
        raise SystemExit(1)
    print(f"{SUPPORTED_FAMILY} Python generation matches current sources")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    subparsers = parser.add_subparsers(dest="command")
    generate_parser = subparsers.add_parser(
        "generate",
        help="Emit generated files under --output.",
    )
    generate_parser.add_argument("--output", type=Path, default=argparse.SUPPRESS)
    subparsers.add_parser("check", help="Compare generated files to current sources.")
    args = parser.parse_args(argv)
    if not args.command:
        args.command = "check"
    args.spec = args.spec.resolve()
    args.manifest = args.manifest.resolve()
    args.output = args.output.resolve()
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.command == "generate":
        generate(args.spec, args.manifest, args.output)
    elif args.command == "check":
        check(args.spec, args.manifest)
    else:  # pragma: no cover - argparse protects this path
        raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
