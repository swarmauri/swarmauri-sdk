#!/usr/bin/env python3
"""Build and validate the Swarmauri package layer index."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

try:  # Python >=3.11
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib  # type: ignore


REPO_ROOT = Path(__file__).resolve().parent.parent
PKGS_DIR = REPO_ROOT / "pkgs"
PACKAGE_INDEX = PKGS_DIR / "package-index.toml"
PACKAGE_INDEX_MD = PKGS_DIR / "PACKAGE_INDEX.md"

LAYER_ORDER = (
    "00-typing",
    "10-interfaces",
    "20-bases",
    "30-standard-kernel",
    "40-standards",
    "50-community",
    "60-plugins",
    "70-experimental",
    "80-facades",
    "90-deprecated",
)

LAYER_DESCRIPTIONS = {
    "00-typing": "typing helpers and generic type composition primitives",
    "10-interfaces": "interface and protocol contracts",
    "20-bases": "reusable base classes, mixins, and component models",
    "30-standard-kernel": "bundled first-party standard component kernel",
    "40-standards": "first-party split standard packages",
    "50-community": "community and provider-specific packages",
    "60-plugins": "plugin packages and plugin examples",
    "70-experimental": "incubating and planning-stage packages",
    "80-facades": "aggregate user-facing facade packages",
    "90-deprecated": "deprecated compatibility packages",
}

PATH_LAYER_DEFAULTS = {
    "typing": "00-typing",
    "core": "10-interfaces",
    "base": "20-bases",
    "swarmauri_standard": "30-standard-kernel",
    "standards": "40-standards",
    "community": "50-community",
    "plugins": "60-plugins",
    "experimental": "70-experimental",
    "swarmauri": "80-facades",
    "deprecated": "90-deprecated",
}

MATURITY_BY_LAYER = {
    "00-typing": "foundation",
    "10-interfaces": "foundation",
    "20-bases": "foundation",
    "30-standard-kernel": "standard-kernel",
    "40-standards": "standard",
    "50-community": "community",
    "60-plugins": "plugin",
    "70-experimental": "experimental",
    "80-facades": "facade",
    "90-deprecated": "deprecated",
}

DIRECT_FAMILIES = {
    "typing": "typing",
    "core": "interfaces",
    "base": "bases",
    "swarmauri_standard": "standard-kernel",
    "swarmauri": "facade",
}

COMPOUND_FAMILIES = (
    "auth_idp",
    "cipher_suite",
    "mre_crypto",
    "vectorstore",
    "documentstore",
    "certservice",
    "evaluatorpool",
    "keyprovider",
    "keyproviders",
    "gitfilter",
    "toolkit",
    "middleware",
    "measurement",
    "embedding",
    "publisher",
    "transport",
    "signing",
    "storage",
    "tokens",
    "crypto",
    "certs",
    "billing",
    "parser",
    "metric",
    "matrix",
    "state",
    "tests",
    "tool",
    "llm",
    "ocr",
    "pop",
    "xmp",
)

PACKAGE_PREFIXES = ("swarmauri_", "swamauri_", "swm_", "tigrbl_")
FOUNDATION_LAYERS = {"00-typing", "10-interfaces", "20-bases", "30-standard-kernel"}
ORDER_SOURCE_VALUES = {"explicit", "inferred"}
IGNORED_PATH_PARTS = {
    ".benchmarks",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tmp",
    ".uv-cache",
    ".venv",
    "__pycache__",
}


@dataclass(frozen=True)
class PackageRecord:
    name: str
    path: str
    layer: str
    order: int
    family: str
    role: str
    maturity: str
    workspace: bool
    order_source: str
    order_reason: str
    composes: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "PackageRecord":
        required = {
            "name",
            "path",
            "layer",
            "order",
            "family",
            "role",
            "maturity",
            "workspace",
            "order_source",
            "order_reason",
        }
        missing = required.difference(data)
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(f"package index entry is missing: {missing_list}")
        composes = data.get("composes", [])
        if composes is None:
            composes = []
        if not isinstance(composes, list):
            raise ValueError(f"{data['path']}: composes must be a list when present")
        return cls(
            name=str(data["name"]),
            path=str(data["path"]),
            layer=str(data["layer"]),
            order=int(data["order"]),
            family=str(data["family"]),
            role=str(data["role"]),
            maturity=str(data["maturity"]),
            workspace=bool(data["workspace"]),
            order_source=str(data["order_source"]),
            order_reason=str(data["order_reason"]),
            composes=tuple(str(name) for name in composes),
        )


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _canonical_name(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def _toml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _should_ignore(path: Path) -> bool:
    try:
        rel_parts = path.relative_to(PKGS_DIR).parts
    except ValueError:
        rel_parts = path.parts
    return any(part in IGNORED_PATH_PARTS for part in rel_parts)


def workspace_members() -> set[str]:
    data = _load_toml(PKGS_DIR / "pyproject.toml")
    members = data.get("tool", {}).get("uv", {}).get("workspace", {}).get("members")
    if not isinstance(members, list):
        raise ValueError("pkgs/pyproject.toml is missing tool.uv.workspace.members")
    return {str(member).replace("\\", "/").rstrip("/") for member in members}


def _project_name(package_dir: Path) -> str:
    data = _load_toml(package_dir / "pyproject.toml")
    name = data.get("project", {}).get("name")
    if not isinstance(name, str) or not name:
        raise ValueError(f"{package_dir / 'pyproject.toml'} is missing project.name")
    return name


def _infer_layer(path: str) -> str:
    top_level = path.split("/", 1)[0]
    try:
        return PATH_LAYER_DEFAULTS[top_level]
    except KeyError as exc:
        raise ValueError(f"cannot infer package layer for {path}") from exc


def _infer_maturity(layer: str) -> str:
    try:
        return MATURITY_BY_LAYER[layer]
    except KeyError as exc:
        raise ValueError(f"unknown package layer: {layer}") from exc


def _infer_family(name: str, path: str) -> str:
    top_level = path.split("/", 1)[0]
    if top_level in DIRECT_FAMILIES:
        return DIRECT_FAMILIES[top_level]

    normalized = name.replace("-", "_").lower()
    for prefix in PACKAGE_PREFIXES:
        if normalized.startswith(prefix):
            normalized = normalized.removeprefix(prefix)
            break

    for family in COMPOUND_FAMILIES:
        if normalized == family or normalized.startswith(f"{family}_"):
            return family

    return normalized.split("_", 1)[0]


def _project_data(package_dir: Path) -> dict[str, Any]:
    return _load_toml(package_dir / "pyproject.toml").get("project", {})


def _text_signals(project: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("name", "description"):
        value = project.get(key)
        if isinstance(value, str):
            values.append(value)
    keywords = project.get("keywords", [])
    if isinstance(keywords, list):
        values.extend(str(keyword) for keyword in keywords)
    return " ".join(values).lower().replace("-", "_")


def _default_role(layer: str, order: int) -> str:
    if layer == "00-typing":
        return "atomic-foundation"
    if layer == "10-interfaces":
        return "interface-contract"
    if layer == "20-bases":
        return "base-implementation"
    if layer == "30-standard-kernel":
        return "standard-kernel"
    if layer == "60-plugins":
        return ("plugin", "plugin-composite", "plugin-orchestrator")[min(order, 2)]
    if layer == "70-experimental":
        return (
            "experimental-atomic",
            "experimental-composite",
            "experimental-orchestrator",
        )[min(order, 2)]
    if layer == "80-facades":
        return "facade"
    if layer == "90-deprecated":
        return ("compat", "compat-composite", "compat-orchestrator")[min(order, 2)]
    return ("atomic-concrete", "composite-concrete", "orchestrator")[min(order, 2)]


def _infer_order(
    *,
    layer: str,
    family: str,
    project: dict[str, Any],
    composes: tuple[str, ...],
) -> tuple[int, str, str]:
    signals = _text_signals(project)
    name = str(project.get("name", ""))

    if layer == "80-facades":
        return 3, "facade", "facade layer packages are aggregate surfaces"
    if layer in FOUNDATION_LAYERS:
        return 0, _default_role(layer, 0), "foundation layers are atomic by policy"

    orchestrator_terms = (
        "orchestrator",
        "unified",
        "aggregating",
        "bundling",
        "coordinator",
    )
    composite_terms = (
        "composite",
        "routing",
        "feature_routing",
        "multi_algorithm",
        "multi-algorithm",
    )

    if family in {"toolkit", "workflow"} or any(
        term in signals for term in orchestrator_terms
    ):
        order = 2
        role = _default_role(layer, order)
        return order, role, f"orchestrator signal from metadata for {name}"

    if any(term in signals for term in composite_terms):
        order = 1
        role = _default_role(layer, order)
        return order, role, f"composite signal from metadata for {name}"

    if len(composes) >= 2:
        order = 1
        role = _default_role(layer, order)
        return (
            order,
            role,
            f"depends on {len(composes)} internal concrete packages",
        )

    return 0, _default_role(layer, 0), "single-capability package by default"


def _existing_index_entries() -> dict[str, dict[str, Any]]:
    if not PACKAGE_INDEX.is_file():
        return {}
    data = _load_toml(PACKAGE_INDEX)
    packages = data.get("packages", [])
    if not isinstance(packages, list):
        return {}
    return {
        str(entry["path"]): entry
        for entry in packages
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }


def _internal_dependency_names(
    project: dict[str, Any],
    indexed_names: dict[str, tuple[str, str]],
) -> tuple[str, ...]:
    dependencies = project.get("dependencies", [])
    if not isinstance(dependencies, list):
        return ()
    internal: list[str] = []
    for dependency in dependencies:
        if not isinstance(dependency, str):
            continue
        dependency_name = _requirement_name(dependency)
        if dependency_name is None or dependency_name not in indexed_names:
            continue
        package_name, layer = indexed_names[dependency_name]
        if layer in FOUNDATION_LAYERS or layer == "80-facades":
            continue
        internal.append(package_name)
    return tuple(sorted(dict.fromkeys(internal)))


def _raise_orders_for_same_layer_dependencies(
    records: list[PackageRecord],
) -> list[PackageRecord]:
    updated = records
    changed = True
    iterations = 0
    max_iterations = len(records) + 1
    while changed:
        iterations += 1
        if iterations > max_iterations:
            raise ValueError(
                "same-layer package dependency cycle prevents order inference"
            )
        changed = False
        next_records: list[PackageRecord] = []
        current_by_name = {_canonical_name(record.name): record for record in updated}
        for record in updated:
            if record.order_source == "explicit":
                next_records.append(record)
                continue
            raised_by: PackageRecord | None = None
            for dependency in _read_project_dependencies(record):
                dependency_name = _requirement_name(dependency)
                if dependency_name is None or dependency_name not in current_by_name:
                    continue
                dependency_record = current_by_name[dependency_name]
                if dependency_record.layer != record.layer:
                    continue
                if dependency_record.order >= record.order:
                    if raised_by is None or dependency_record.order > raised_by.order:
                        raised_by = dependency_record
            if raised_by is None:
                next_records.append(record)
                continue
            raised_order = raised_by.order + 1
            next_records.append(
                replace(
                    record,
                    order=raised_order,
                    role=_default_role(record.layer, raised_order),
                    order_reason=(
                        f"raised to order {raised_order} because it depends on "
                        f"same-layer package {raised_by.name} at "
                        f"{_display_index(raised_by)}"
                    ),
                )
            )
            changed = True
        updated = next_records
    return sort_records(updated)


def discover_packages() -> list[PackageRecord]:
    members = workspace_members()
    existing_entries = _existing_index_entries()
    discovered: list[dict[str, Any]] = []
    indexed_names: dict[str, tuple[str, str]] = {}
    for pyproject in sorted(PKGS_DIR.rglob("pyproject.toml")):
        if pyproject.parent == PKGS_DIR or _should_ignore(pyproject):
            continue
        path = pyproject.parent.relative_to(PKGS_DIR).as_posix()
        layer = _infer_layer(path)
        project = _project_data(pyproject.parent)
        name = str(project.get("name"))
        family = _infer_family(name, path)
        discovered.append(
            {
                "name": name,
                "path": path,
                "layer": layer,
                "family": family,
                "maturity": _infer_maturity(layer),
                "workspace": path in members,
                "project": project,
            }
        )
        indexed_names[_canonical_name(name)] = (name, layer)

    records: list[PackageRecord] = []
    for item in discovered:
        path = item["path"]
        existing = existing_entries.get(path, {})
        inferred_composes = _internal_dependency_names(item["project"], indexed_names)
        if existing.get("order_source") == "explicit":
            order = int(existing["order"])
            role = str(existing["role"])
            order_source = "explicit"
            order_reason = str(existing.get("order_reason", "explicit index override"))
            composes = tuple(
                str(name) for name in existing.get("composes", inferred_composes)
            )
        else:
            composes = inferred_composes
            order, role, order_reason = _infer_order(
                layer=item["layer"],
                family=item["family"],
                project=item["project"],
                composes=composes,
            )
            order_source = "inferred"
        records.append(
            PackageRecord(
                name=item["name"],
                path=item["path"],
                layer=item["layer"],
                order=order,
                family=item["family"],
                role=role,
                maturity=item["maturity"],
                workspace=item["workspace"],
                order_source=order_source,
                order_reason=order_reason,
                composes=composes,
            )
        )
    return _raise_orders_for_same_layer_dependencies(sort_records(records))


def sort_records(records: list[PackageRecord]) -> list[PackageRecord]:
    rank = {layer: index for index, layer in enumerate(LAYER_ORDER)}
    return sorted(
        records,
        key=lambda record: (
            rank.get(record.layer, 999),
            record.order,
            record.family,
            record.name,
        ),
    )


def load_index() -> list[PackageRecord]:
    data = _load_toml(PACKAGE_INDEX)
    packages = data.get("packages")
    if not isinstance(packages, list):
        raise ValueError("pkgs/package-index.toml is missing [[packages]] entries")
    return sort_records([PackageRecord.from_mapping(entry) for entry in packages])


def render_toml(records: list[PackageRecord]) -> str:
    lines = [
        "# Generated by `python scripts/package_index.py --write`.",
        "# Keep published distribution names and import roots stable; this file indexes",
        "# current package paths rather than moving packages into numbered directories.",
        'schema_version = "1.0"',
        "",
        "[layers]",
    ]
    for layer in LAYER_ORDER:
        lines.append(
            f"{_toml_string(layer)} = {_toml_string(LAYER_DESCRIPTIONS[layer])}"
        )
    lines.append("")

    for record in sort_records(records):
        lines.extend(
            [
                "[[packages]]",
                f"name = {_toml_string(record.name)}",
                f"path = {_toml_string(record.path)}",
                f"layer = {_toml_string(record.layer)}",
                f"order = {record.order}",
                f"family = {_toml_string(record.family)}",
                f"role = {_toml_string(record.role)}",
                f"maturity = {_toml_string(record.maturity)}",
                f"workspace = {str(record.workspace).lower()}",
                f"order_source = {_toml_string(record.order_source)}",
                f"order_reason = {_toml_string(record.order_reason)}",
            ]
        )
        if record.composes:
            composed_names = ", ".join(_toml_string(name) for name in record.composes)
            lines.append(f"composes = [{composed_names}]")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _workspace_label(record: PackageRecord) -> str:
    return "yes" if record.workspace else "no"


def _package_link(record: PackageRecord) -> str:
    return f"[{record.name}]({record.path}/)"


def _display_index(record: PackageRecord) -> str:
    layer_number = record.layer.split("-", 1)[0]
    return f"{layer_number}.{record.order}"


def render_markdown(records: list[PackageRecord]) -> str:
    sorted_records = sort_records(records)
    by_layer: dict[str, list[PackageRecord]] = defaultdict(list)
    by_family: dict[str, list[PackageRecord]] = defaultdict(list)
    for record in sorted_records:
        by_layer[record.layer].append(record)
        by_family[record.family].append(record)

    lines = [
        "# Swarmauri Package Index",
        "",
        "Generated from `package-index.toml`. Do not move package directories as part of",
        "index maintenance; this index records current paths and keeps distribution names",
        "and import roots stable.",
        "",
        "Index values are displayed as `layer.order`, where `layer` captures package",
        "citizenship/dependency band and `order` captures composition depth. A",
        "same-layer package that composes another package is indexed at a higher",
        "order than the package it composes.",
        "",
        "Order is `explicit` when `package-index.toml` carries an intentional",
        "override. Otherwise it is inferred from the package layer, family, metadata",
        "signals, and internal runtime dependencies. Same-layer dependency cycles",
        "fail validation because they make composition order ambiguous.",
        "",
        "## Layer Summary",
        "",
        "| Layer | Packages | Workspace packages | Purpose |",
        "|---|---:|---:|---|",
    ]
    for layer in LAYER_ORDER:
        records_for_layer = by_layer.get(layer, [])
        workspace_count = sum(record.workspace for record in records_for_layer)
        lines.append(
            f"| `{layer}` | {len(records_for_layer)} | {workspace_count} | "
            f"{LAYER_DESCRIPTIONS[layer]} |"
        )

    lines.extend(["", "## By Layer", ""])
    for layer in LAYER_ORDER:
        records_for_layer = by_layer.get(layer, [])
        if not records_for_layer:
            continue
        lines.extend(
            [
                f"### `{layer}`",
                "",
                "| Index | Package | Path | Family | Role | Maturity | Workspace |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for record in records_for_layer:
            lines.append(
                f"| `{_display_index(record)}` | {_package_link(record)} | "
                f"`{record.path}` | `{record.family}` | `{record.role}` | "
                f"`{record.maturity}` | {_workspace_label(record)} |"
            )
        lines.append("")

    lines.extend(["## By Layer And Order", ""])
    order_groups: dict[tuple[str, int], list[PackageRecord]] = defaultdict(list)
    for record in sorted_records:
        order_groups[(record.layer, record.order)].append(record)
    for layer in LAYER_ORDER:
        orders = sorted(
            order for current_layer, order in order_groups if current_layer == layer
        )
        for order in orders:
            records_for_order = order_groups[(layer, order)]
            display = _display_index(records_for_order[0])
            lines.extend(
                [
                    f"### `{display}`",
                    "",
                    "| Package | Family | Role | Source | Composes | Order reason |",
                    "|---|---|---|---|---:|---|",
                ]
            )
            for record in records_for_order:
                lines.append(
                    f"| {_package_link(record)} | `{record.family}` | "
                    f"`{record.role}` | `{record.order_source}` | "
                    f"{len(record.composes)} | "
                    f"{record.order_reason} |"
                )
            lines.append("")

    lines.extend(["## By Domain Family", ""])
    for family in sorted(by_family):
        records_for_family = sort_records(by_family[family])
        lines.extend(
            [
                f"### `{family}`",
                "",
                "| Index | Package | Layer | Path | Role | Maturity | Workspace |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for record in records_for_family:
            lines.append(
                f"| `{_display_index(record)}` | {_package_link(record)} | "
                f"`{record.layer}` | `{record.path}` | `{record.role}` | "
                f"`{record.maturity}` | {_workspace_label(record)} |"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _read_project_dependencies(record: PackageRecord) -> list[str]:
    data = _load_toml(PKGS_DIR / record.path / "pyproject.toml")
    dependencies = data.get("project", {}).get("dependencies", [])
    if not isinstance(dependencies, list):
        return []
    return [dependency for dependency in dependencies if isinstance(dependency, str)]


def _requirement_name(requirement: str) -> str | None:
    requirement = requirement.split(";", 1)[0].strip()
    if not requirement:
        return None
    if " @ " in requirement:
        name = requirement.split(" @ ", 1)[0]
    else:
        name = re.split(r"[\s\[]", requirement, maxsplit=1)[0]
    name = name.strip()
    return _canonical_name(name) if name else None


def validate_index(check_docs: bool = False) -> list[str]:
    errors: list[str] = []

    if not PACKAGE_INDEX.is_file():
        return [f"{PACKAGE_INDEX.relative_to(REPO_ROOT)} is missing"]

    try:
        records = load_index()
    except Exception as exc:
        return [str(exc)]

    discovered_by_path = {record.path: record for record in discover_packages()}
    indexed_by_path: dict[str, PackageRecord] = {}
    indexed_by_name: dict[str, PackageRecord] = {}

    for record in records:
        if record.layer not in LAYER_ORDER:
            errors.append(f"{record.path}: unknown layer {record.layer!r}")
            continue
        if record.maturity != _infer_maturity(record.layer):
            errors.append(
                f"{record.path}: maturity {record.maturity!r} does not match "
                f"layer {record.layer!r}"
            )
        if record.path in indexed_by_path:
            errors.append(f"{record.path}: duplicate package-index path")
        indexed_by_path[record.path] = record

        canonical = _canonical_name(record.name)
        if canonical in indexed_by_name:
            errors.append(f"{record.name}: duplicate package-index name")
        indexed_by_name[canonical] = record

        package_dir = PKGS_DIR / record.path
        pyproject = package_dir / "pyproject.toml"
        if not pyproject.is_file():
            errors.append(f"{record.path}: missing pyproject.toml")
            continue
        project_name = _project_name(package_dir)
        if project_name != record.name:
            errors.append(
                f"{record.path}: package-index name {record.name!r} does not match "
                f"project.name {project_name!r}"
            )

    missing_index_paths = sorted(set(discovered_by_path).difference(indexed_by_path))
    for path in missing_index_paths:
        errors.append(f"{path}: package directory is missing from package-index.toml")

    stale_index_paths = sorted(set(indexed_by_path).difference(discovered_by_path))
    for path in stale_index_paths:
        errors.append(f"{path}: package-index.toml points at a missing package")

    members = workspace_members()
    indexed_workspace = {record.path for record in records if record.workspace}
    for path in sorted(members.difference(indexed_workspace)):
        errors.append(f"{path}: workspace member is not marked workspace = true")
    for path in sorted(indexed_workspace.difference(members)):
        errors.append(f"{path}: package-index workspace flag is not in uv workspace")

    layer_rank = {layer: index for index, layer in enumerate(LAYER_ORDER)}
    for record in records:
        if record.order < 0:
            errors.append(f"{record.path}: order must be non-negative")
        expected_role = _default_role(record.layer, record.order)
        if record.role != expected_role:
            errors.append(
                f"{record.path}: role {record.role!r} does not match "
                f"layer/order role {expected_role!r}"
            )
        if record.order_source not in ORDER_SOURCE_VALUES:
            errors.append(
                f"{record.path}: order_source must be one of "
                f"{sorted(ORDER_SOURCE_VALUES)}"
            )
        if not record.order_reason:
            errors.append(f"{record.path}: order_reason must not be empty")
        for composed_name in record.composes:
            canonical_composed = _canonical_name(composed_name)
            if canonical_composed not in indexed_by_name:
                errors.append(
                    f"{record.path}: composes unknown package {composed_name!r}"
                )

        for dependency in _read_project_dependencies(record):
            dependency_name = _requirement_name(dependency)
            if dependency_name is None or dependency_name not in indexed_by_name:
                continue
            dependency_record = indexed_by_name[dependency_name]
            if layer_rank[record.layer] < layer_rank[dependency_record.layer]:
                errors.append(
                    f"{record.path}: layer {record.layer} depends on higher layer "
                    f"{dependency_record.layer} via {dependency_record.name}"
                )
            if (
                record.layer == dependency_record.layer
                and record.order <= dependency_record.order
            ):
                errors.append(
                    f"{record.path}: index {_display_index(record)} depends on "
                    f"same-layer index {_display_index(dependency_record)} via "
                    f"{dependency_record.name}"
                )

    if check_docs:
        expected_markdown = render_markdown(records)
        if not PACKAGE_INDEX_MD.is_file():
            errors.append(f"{PACKAGE_INDEX_MD.relative_to(REPO_ROOT)} is missing")
        elif PACKAGE_INDEX_MD.read_text(encoding="utf-8") != expected_markdown:
            errors.append(
                f"{PACKAGE_INDEX_MD.relative_to(REPO_ROOT)} is out of date; "
                "run `python scripts/package_index.py --write-docs`"
            )

    return errors


def write_index() -> None:
    records = discover_packages()
    PACKAGE_INDEX.write_text(render_toml(records), encoding="utf-8")
    PACKAGE_INDEX_MD.write_text(render_markdown(records), encoding="utf-8")


def write_docs() -> None:
    PACKAGE_INDEX_MD.write_text(render_markdown(load_index()), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="refresh package-index.toml and PACKAGE_INDEX.md from package metadata",
    )
    parser.add_argument(
        "--write-docs",
        action="store_true",
        help="refresh PACKAGE_INDEX.md from package-index.toml",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate package-index.toml and generated markdown",
    )
    args = parser.parse_args(argv)

    if args.write:
        write_index()
    elif args.write_docs:
        write_docs()

    errors = validate_index(check_docs=args.check or args.write or args.write_docs)
    if errors:
        for error in errors:
            print(f"package-index: {error}", file=sys.stderr)
        return 1
    print("package-index: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
