#!/usr/bin/env python3
"""Generate and validate the Swarmauri entity manifest.

The manifest is the bootstrap source for future multi-language entity
generators. It inventories public Swarmauri core contracts, base abstractions,
and concrete package classes without importing package code.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:  # Python 3.11+
    import tomllib as _toml

    _TOML_READS_BYTES = True
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import toml as _toml  # type: ignore[no-redef]

    _TOML_READS_BYTES = False


REPO_ROOT = Path(__file__).resolve().parent.parent
PKGS_ROOT = REPO_ROOT / "pkgs"
WORKSPACE_PYPROJECT = PKGS_ROOT / "pyproject.toml"
DEFAULT_OUTPUT = REPO_ROOT / "entity_specs" / "swarmauri_entities.v1.json"
SCHEMA_PATH = REPO_ROOT / "entity_specs" / "schema.v1.json"
SOURCE_SPECS_DIR = REPO_ROOT / "entity_specs" / "sources"

MANIFEST_VERSION = "1"
GENERATOR_ID = "scripts/generate_entity_manifest.py"
TARGETS = ["python", "rust", "npm", "tsx", "react+tsx", "vue+tsx", "svelte+tsx"]
EXCLUDED_PACKAGE_PREFIXES = ("peagen", "tigr", "tigrcorn", "swm_example")
LEGACY_SWARMAURI_PREFIXES = ("swamauri_",)
EXCLUDED_SOURCE_PARTS = {
    ".benchmarks",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "tests",
}


@dataclass(frozen=True)
class Package:
    """Workspace package selected for entity inventory."""

    name: str
    member: str
    path: Path
    scope_reason: str


def _load_toml(path: Path) -> dict[str, Any]:
    if _TOML_READS_BYTES:
        with path.open("rb") as handle:
            return _toml.load(handle)
    return _toml.loads(path.read_text(encoding="utf-8"))


def _project_name(package_path: Path) -> str | None:
    pyproject = package_path / "pyproject.toml"
    if not pyproject.is_file():
        return None
    return _load_toml(pyproject).get("project", {}).get("name")


def _scope_reason(name: str) -> str | None:
    if name in {"swarmauri_core", "swarmauri_base", "swarmauri_standard"}:
        return name
    if any(name.startswith(prefix) for prefix in EXCLUDED_PACKAGE_PREFIXES):
        return None
    if name.startswith("swarmauri_"):
        return "swarmauri_prefix"
    if any(name.startswith(prefix) for prefix in LEGACY_SWARMAURI_PREFIXES):
        return "legacy_swamauri_prefix"
    return None


def _workspace_packages() -> list[Package]:
    workspace = _load_toml(WORKSPACE_PYPROJECT)
    members = workspace.get("tool", {}).get("uv", {}).get("workspace", {}).get(
        "members", []
    )
    packages: dict[Path, Package] = {}
    for member in members:
        path = (PKGS_ROOT / member).resolve()
        name = _project_name(path)
        if not name:
            continue
        reason = _scope_reason(name)
        if not reason:
            continue
        packages[path] = Package(name=name, member=member, path=path, scope_reason=reason)
    return sorted(packages.values(), key=lambda package: (package.name, package.member))


def _module_name(package: Package, path: Path) -> str:
    parts = list(path.with_suffix("").parts)
    package_tokens = {package.name, package.name.replace("-", "_")}
    for index in range(len(parts) - 1, -1, -1):
        if parts[index] in package_tokens:
            module_parts = parts[index:]
            if module_parts[-1] == "__init__":
                module_parts = module_parts[:-1]
            return ".".join(module_parts)
    relative = path.with_suffix("").relative_to(package.path)
    module_parts = [part for part in relative.parts if part != "__init__"]
    return ".".join(module_parts)


def _iter_python_files(package: Package) -> list[Path]:
    files: list[Path] = []
    for path in package.path.rglob("*.py"):
        relative_parts = set(path.relative_to(package.path).parts)
        if relative_parts & EXCLUDED_SOURCE_PARTS:
            continue
        files.append(path)
    return sorted(files)


def _unparse(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - defensive fallback
        return None


def _base_names(node: ast.ClassDef) -> list[str]:
    return [_unparse(base) or "" for base in node.bases]


def _decorator_names(node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    return [_unparse(decorator) or "" for decorator in node.decorator_list]


def _simple_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return _unparse(node)


def _literal_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        return _simple_name(node.func)
    return None


def _registration_from_decorator(
    decorator: ast.AST,
    class_bases: list[str],
) -> dict[str, Any] | None:
    if not isinstance(decorator, ast.Call):
        return None
    call_name = _call_name(decorator)
    if call_name not in {"register_model", "register_type"}:
        return None

    registrar = None
    if isinstance(decorator.func, ast.Attribute):
        registrar = _unparse(decorator.func.value)
    elif isinstance(decorator.func, ast.Name):
        registrar = decorator.func.id

    registration: dict[str, Any] = {
        "kind": call_name,
        "registrar": registrar,
        "base_types": [],
        "type_name": None,
    }

    if call_name == "register_type":
        if decorator.args:
            first = decorator.args[0]
            if isinstance(first, (ast.List, ast.Tuple)):
                registration["base_types"] = [
                    _unparse(element) or "" for element in first.elts
                ]
            else:
                registration["base_types"] = [_unparse(first) or ""]
        else:
            registration["base_types"] = [
                base
                for base in class_bases
                if base not in {"DynamicBase", "ComponentBase", "ObserveBase"}
            ]
        if len(decorator.args) > 1:
            registration["type_name"] = _literal_string(decorator.args[1])
        for keyword in decorator.keywords:
            if keyword.arg == "type_name":
                registration["type_name"] = _literal_string(keyword.value)

    return registration


def _class_registration(node: ast.ClassDef) -> dict[str, Any] | None:
    bases = _base_names(node)
    for decorator in node.decorator_list:
        registration = _registration_from_decorator(decorator, bases)
        if registration:
            return registration
    return None


def _inherits_from_any(bases: list[str], suffixes: tuple[str, ...]) -> bool:
    return any(base.split(".")[-1].endswith(suffixes) for base in bases)


def _has_base_name(bases: list[str], names: set[str]) -> bool:
    return any(base.split(".")[-1] in names for base in bases)


def _entity_role(package: Package, node: ast.ClassDef) -> str | None:
    if node.name.startswith("_"):
        return None
    bases = _base_names(node)
    registration = _class_registration(node)

    if package.name == "swarmauri_core":
        if _has_base_name(bases, {"Enum", "Flag"}):
            return "core_enum"
        if _has_base_name(bases, {"TypedDict"}):
            return "core_typed_dict"
        if _has_base_name(bases, {"Protocol"}):
            return "core_protocol"
        if _has_base_name(bases, {"Exception", "RuntimeError", "ValueError"}):
            return "core_exception"
        if _has_base_name(bases, {"ABC"}) or node.name.startswith("I"):
            return "core_interface"
        return "core_type"

    if package.name == "swarmauri_base":
        if registration and registration["kind"] == "register_type":
            return "base_registered_type"
        if registration and registration["kind"] == "register_model":
            return "base_registered_model"
        if node.name.endswith("Base"):
            return "base_class"
        if node.name.endswith("Mixin"):
            return "base_mixin"
        if _has_base_name(bases, {"Enum", "Flag"}):
            return "base_enum"
        if _has_base_name(bases, {"BaseModel", "TypedDict", "Protocol"}):
            return "base_type"
        if _has_base_name(bases, {"Exception", "RuntimeError", "ValueError"}):
            return "base_exception"
        return "base_type"

    if registration and registration["kind"] == "register_type":
        return "concrete_registered_type"
    if _inherits_from_any(bases, ("Base", "Mixin")):
        return "concrete_class"
    if package.name == "swarmauri_standard":
        return "standard_type"
    return None


def _layer(package: Package) -> str:
    if package.name == "swarmauri_core":
        return "core"
    if package.name == "swarmauri_base":
        return "base"
    return "concrete"


def _field_from_ann_assign(node: ast.AnnAssign) -> dict[str, Any] | None:
    if not isinstance(node.target, ast.Name):
        return None
    name = node.target.id
    if name.startswith("_"):
        return None
    annotation = _unparse(node.annotation)
    return {
        "name": name,
        "annotation": annotation,
        "default": _unparse(node.value),
        "class_var": bool(annotation and annotation.startswith("ClassVar")),
    }


def _enum_members(node: ast.ClassDef) -> list[dict[str, str | None]]:
    if not _has_base_name(_base_names(node), {"Enum", "Flag"}):
        return []
    members: list[dict[str, str | None]] = []
    for statement in node.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    members.append({"name": target.id, "value": _unparse(statement.value)})
    return members


def _fields(node: ast.ClassDef) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for statement in node.body:
        if isinstance(statement, ast.AnnAssign):
            field = _field_from_ann_assign(statement)
            if field:
                fields.append(field)
    return fields


def _type_literal(fields: list[dict[str, Any]]) -> str | None:
    for field in fields:
        if field["name"] != "type":
            continue
        annotation = field.get("annotation") or ""
        match = re.match(r"Literal\[['\"]([^'\"]+)['\"]\]", annotation)
        if match:
            return match.group(1)
        default = field.get("default")
        if default and len(default) >= 2 and default[0] in {'"', "'"}:
            return default.strip("'\"")
    return None


def _resource_default(fields: list[dict[str, Any]]) -> str | None:
    for field in fields:
        if field["name"] == "resource":
            return field.get("default")
    return None


def _parameter(
    name: str,
    annotation: ast.AST | None,
    default: ast.AST | None,
    kind: str,
) -> dict[str, str | None]:
    return {
        "name": name,
        "kind": kind,
        "annotation": _unparse(annotation),
        "default": _unparse(default),
    }


def _parameters(args: ast.arguments) -> list[dict[str, str | None]]:
    parameters: list[dict[str, str | None]] = []

    positional = list(args.posonlyargs) + list(args.args)
    defaults: list[ast.AST | None] = [None] * (len(positional) - len(args.defaults))
    defaults.extend(args.defaults)

    for index, arg in enumerate(positional):
        kind = "positional_only" if index < len(args.posonlyargs) else "positional"
        parameters.append(
            _parameter(arg.arg, arg.annotation, defaults[index], kind)
        )

    if args.vararg:
        parameters.append(
            _parameter(args.vararg.arg, args.vararg.annotation, None, "var_positional")
        )

    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        parameters.append(_parameter(arg.arg, arg.annotation, default, "keyword_only"))

    if args.kwarg:
        parameters.append(
            _parameter(args.kwarg.arg, args.kwarg.annotation, None, "var_keyword")
        )

    return parameters


def _methods(node: ast.ClassDef) -> list[dict[str, Any]]:
    methods: list[dict[str, Any]] = []
    for statement in node.body:
        if not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if statement.name.startswith("_") and statement.name != "__call__":
            continue
        decorators = _decorator_names(statement)
        methods.append(
            {
                "name": statement.name,
                "async": isinstance(statement, ast.AsyncFunctionDef),
                "decorators": decorators,
                "abstract": any("abstractmethod" in decorator for decorator in decorators),
                "parameters": _parameters(statement.args),
                "returns": _unparse(statement.returns),
            }
        )
    return methods


def _class_entity(package: Package, path: Path, node: ast.ClassDef) -> dict[str, Any] | None:
    role = _entity_role(package, node)
    if not role:
        return None
    module = _module_name(package, path)
    fields = _fields(node)
    registration = _class_registration(node)
    entity_id = f"{module}.{node.name}"
    source_path = path.relative_to(REPO_ROOT).as_posix()
    return {
        "id": entity_id,
        "name": node.name,
        "layer": _layer(package),
        "role": role,
        "package": package.name,
        "module": module,
        "source_path": source_path,
        "line": node.lineno,
        "bases": _base_names(node),
        "decorators": _decorator_names(node),
        "registration": registration,
        "type_discriminator": _type_literal(fields),
        "resource_default": _resource_default(fields),
        "doc": ast.get_docstring(node),
        "fields": fields,
        "enum_members": _enum_members(node),
        "methods": _methods(node),
    }


def _entities_for_package(package: Package) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    for path in _iter_python_files(package):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            raise SystemExit(f"Unable to parse {path}: {exc}") from exc
        for statement in tree.body:
            if isinstance(statement, ast.ClassDef):
                entity = _class_entity(package, path, statement)
                if entity:
                    entities.append(entity)
    return sorted(entities, key=lambda entity: entity["id"])


def build_manifest() -> dict[str, Any]:
    packages = _workspace_packages()
    entities: list[dict[str, Any]] = []
    package_rows: list[dict[str, Any]] = []

    for package in packages:
        package_entities = _entities_for_package(package)
        if package_entities:
            package_rows.append(
                {
                    "name": package.name,
                    "member": package.member,
                    "scope_reason": package.scope_reason,
                    "entity_count": len(package_entities),
                }
            )
        entities.extend(package_entities)

    entities = sorted(entities, key=lambda entity: entity["id"])
    return {
        "manifest_version": MANIFEST_VERSION,
        "schema": SCHEMA_PATH.relative_to(REPO_ROOT).as_posix(),
        "generated_by": GENERATOR_ID,
        "targets": TARGETS,
        "scope": {
            "workspace": WORKSPACE_PYPROJECT.relative_to(REPO_ROOT).as_posix(),
            "include": [
                "swarmauri_core",
                "swarmauri_base",
                "swarmauri_standard",
                "swarmauri_*",
                "legacy swamauri_* packages with registered Swarmauri entities",
            ],
            "exclude_prefixes": list(EXCLUDED_PACKAGE_PREFIXES),
            "exclude_source_parts": sorted(EXCLUDED_SOURCE_PARTS),
        },
        "summary": _summary(entities, package_rows),
        "packages": sorted(package_rows, key=lambda row: (row["name"], row["member"])),
        "entities": entities,
    }


def _summary(
    entities: list[dict[str, Any]],
    packages: list[dict[str, Any]],
) -> dict[str, Any]:
    by_layer: dict[str, int] = {}
    by_role: dict[str, int] = {}
    for entity in entities:
        by_layer[entity["layer"]] = by_layer.get(entity["layer"], 0) + 1
        by_role[entity["role"]] = by_role.get(entity["role"], 0) + 1
    return {
        "package_count": len(packages),
        "entity_count": len(entities),
        "by_layer": dict(sorted(by_layer.items())),
        "by_role": dict(sorted(by_role.items())),
    }


def _normalized_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2) + "\n"


def validate_manifest(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("manifest_version") != MANIFEST_VERSION:
        errors.append("manifest_version must be 1")
    entities = data.get("entities")
    if not isinstance(entities, list):
        return errors + ["entities must be a list"]

    seen: set[str] = set()
    for index, entity in enumerate(entities):
        entity_id = entity.get("id")
        if not isinstance(entity_id, str) or not entity_id:
            errors.append(f"entities[{index}].id must be a non-empty string")
            continue
        if entity_id in seen:
            errors.append(f"duplicate entity id: {entity_id}")
        seen.add(entity_id)
        for key in ["name", "layer", "role", "package", "module", "source_path"]:
            if not isinstance(entity.get(key), str) or not entity.get(key):
                errors.append(f"{entity_id}.{key} must be a non-empty string")
        if entity.get("layer") not in {"core", "base", "concrete"}:
            errors.append(f"{entity_id}.layer is invalid: {entity.get('layer')}")
        if not isinstance(entity.get("fields"), list):
            errors.append(f"{entity_id}.fields must be a list")
        if not isinstance(entity.get("methods"), list):
            errors.append(f"{entity_id}.methods must be a list")

    summary = data.get("summary", {})
    if isinstance(summary, dict) and summary.get("entity_count") != len(entities):
        errors.append("summary.entity_count does not match entities length")
    return errors


def _source_spec_files() -> list[Path]:
    if not SOURCE_SPECS_DIR.is_dir():
        return []
    return sorted(SOURCE_SPECS_DIR.glob("*.json"))


def _validate_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        return [f"{label} must be a list"]
    errors: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            errors.append(f"{label}[{index}] must be a non-empty string")
    return errors


def validate_source_specs(manifest: dict[str, Any]) -> list[str]:
    """Validate editable source-spec pilots against the bootstrap manifest."""
    errors: list[str] = []
    manifest_entities = {
        entity["id"]: entity
        for entity in manifest.get("entities", [])
        if isinstance(entity, dict) and isinstance(entity.get("id"), str)
    }

    for path in _source_spec_files():
        label = path.relative_to(REPO_ROOT).as_posix()
        try:
            source_spec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{label} is not valid JSON: {exc}")
            continue

        if not isinstance(source_spec, dict):
            errors.append(f"{label} must be a JSON object")
            continue

        for required in ["manifest_version", "family", "targets", "entities"]:
            if required not in source_spec:
                errors.append(f"{label}.{required} is required")

        if source_spec.get("manifest_version") != MANIFEST_VERSION:
            errors.append(f"{label}.manifest_version must be {MANIFEST_VERSION}")
        if not isinstance(source_spec.get("family"), str) or not source_spec.get(
            "family"
        ):
            errors.append(f"{label}.family must be a non-empty string")

        errors.extend(_validate_string_list(source_spec.get("targets"), f"{label}.targets"))
        for target in source_spec.get("targets", []):
            if isinstance(target, str) and target not in TARGETS:
                errors.append(f"{label}.targets contains unsupported target: {target}")

        entities = source_spec.get("entities")
        if not isinstance(entities, list):
            errors.append(f"{label}.entities must be a list")
            continue
        if not entities:
            errors.append(f"{label}.entities must not be empty")

        for index, entity in enumerate(entities):
            entity_label = f"{label}.entities[{index}]"
            if not isinstance(entity, dict):
                errors.append(f"{entity_label} must be an object")
                continue
            for required in ["id", "name", "layer", "role", "fields"]:
                if required not in entity:
                    errors.append(f"{entity_label}.{required} is required")

            entity_id = entity.get("id")
            if not isinstance(entity_id, str) or not entity_id:
                errors.append(f"{entity_label}.id must be a non-empty string")
                continue
            manifest_entity = manifest_entities.get(entity_id)
            if not manifest_entity:
                errors.append(f"{entity_label}.id is not in the bootstrap manifest")
                continue

            for key in ["name", "layer", "role"]:
                if entity.get(key) != manifest_entity.get(key):
                    errors.append(
                        f"{entity_label}.{key} must match manifest value "
                        f"{manifest_entity.get(key)!r}"
                    )

            if not isinstance(entity.get("fields"), list):
                errors.append(f"{entity_label}.fields must be a list")

    return errors


def write_manifest(path: Path) -> None:
    manifest = build_manifest()
    errors = validate_manifest(manifest)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_normalized_json(manifest), encoding="utf-8")
    print(f"Wrote {path.relative_to(REPO_ROOT).as_posix()}")
    print(json.dumps(manifest["summary"], indent=2, sort_keys=True))


def check_manifest(path: Path) -> None:
    expected = _normalized_json(build_manifest())
    if not path.is_file():
        raise SystemExit(f"Manifest does not exist: {path}")
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        print(
            f"{path.relative_to(REPO_ROOT).as_posix()} is out of date. "
            f"Run `{GENERATOR_ID} generate`.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(f"{path.relative_to(REPO_ROOT).as_posix()} is up to date")


def validate_file(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"Manifest does not exist: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_manifest(data)
    errors.extend(validate_source_specs(data))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)
    print(f"{path.relative_to(REPO_ROOT).as_posix()} is valid")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Manifest output path.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("generate", help="Generate the entity manifest.")
    subparsers.add_parser("check", help="Check the manifest for source drift.")
    subparsers.add_parser("validate", help="Validate the committed manifest shape.")
    args = parser.parse_args(argv)
    if not args.command:
        args.command = "generate"
    args.output = args.output.resolve()
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.command == "generate":
        write_manifest(args.output)
    elif args.command == "check":
        check_manifest(args.output)
    elif args.command == "validate":
        validate_file(args.output)
    else:  # pragma: no cover - argparse protects this path
        raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
