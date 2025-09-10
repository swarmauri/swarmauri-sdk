import argparse
import ast
import fnmatch
import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import yaml


CACHE_DIR = ".cache"
CACHE_FILE = os.path.join(CACHE_DIR, "api_index.json")


@dataclass
class Target:
    name: str  # Top label (e.g., Core, Base, Standard, First_Class)
    search_path: str  # Path (relative to docs/) where source lives
    package: Optional[str] = None  # Root package name, or None for discover
    discover: bool = False  # If true, discover packages under search_path
    include: Optional[List[str]] = None  # include patterns for module names
    exclude: Optional[List[str]] = None  # exclude patterns for module names


def load_manifest(path: str) -> List[Target]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    targets = []
    for t in data.get("targets", []):
        targets.append(
            Target(
                name=t["name"],
                search_path=t["search_path"],
                package=t.get("package"),
                discover=bool(t.get("discover", False)),
                include=t.get("include", ["*."]),
                exclude=t.get("exclude", []),
            )
        )
    return targets


def read_cache(cache_path: str) -> Dict:
    if os.path.isfile(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def write_cache(cache_path: str, data: Dict) -> None:
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def file_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()


def is_package_dir(path: str) -> bool:
    # Heuristic: a directory containing a subdir with same name and __init__.py
    if not os.path.isdir(path):
        return False
    name = os.path.basename(path)
    candidate = os.path.join(path, name)
    return os.path.isfile(os.path.join(candidate, "__init__.py"))


def discover_packages(search_path: str) -> List[Tuple[str, str]]:
    # Returns list of (package_name, package_root_dir)
    packages = []
    if not os.path.isdir(search_path):
        return packages
    for entry in os.listdir(search_path):
        if entry.startswith("."):
            continue
        full = os.path.join(search_path, entry)
        if is_package_dir(full):
            packages.append((entry, full))
    return packages


def iter_python_files(root_pkg_dir: str, package_name: str):
    # Walk the <root>/<package_name> tree yielding (file_path, module_name)
    base = os.path.join(root_pkg_dir, package_name)
    for dirpath, _, filenames in os.walk(base):
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, root_pkg_dir)
            mod = rel[:-3].replace(os.sep, ".")  # strip .py
            if mod.endswith(".__init__"):
                mod = mod[: -len(".__init__")]
            yield fpath, mod


def is_valid_package_path(package_root: str, module_file: str) -> bool:
    """Return True if every directory from package root to the module file
    contains an __init__.py, ensuring it's importable as a regular package path.
    """
    # e.g., package_root=/repo/pkgs/base, module_file=/repo/pkgs/base/swarmauri_base/foo/bar.py
    # We need to check /repo/pkgs/base/swarmauri_base[/foo]... all dirs to bar.py have __init__.py
    rel = os.path.relpath(module_file, package_root)
    parts = rel.split(os.sep)
    # drop filename
    dirs = parts[:-1]
    cur = package_root
    for d in dirs:
        cur = os.path.join(cur, d)
        if not os.path.isdir(cur):
            return False
        if not os.path.isfile(os.path.join(cur, "__init__.py")):
            return False
    return True


def module_allowed(module: str, includes: List[str], excludes: List[str]) -> bool:
    inc_ok = (
        any(fnmatch.fnmatch(module, patt) for patt in includes) if includes else True
    )
    exc_ok = (
        not any(fnmatch.fnmatch(module, patt) for patt in excludes)
        if excludes
        else True
    )
    return inc_ok and exc_ok


def extract_classes_from_source(src: str) -> List[str]:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    classes = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            name = node.name
            if not name.startswith("_"):
                classes.append(name)
    return classes


def ensure_home_page(base_dir: str) -> None:
    os.makedirs(base_dir, exist_ok=True)
    idx = os.path.join(base_dir, "index.md")
    if not os.path.exists(idx):
        with open(idx, "w", encoding="utf-8") as f:
            f.write("# Welcome\n\nThis is the home page.\n")


def write_class_page(out_path: str, module: str, cls: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Class `{module}.{cls}`\n\n")
        f.write(f"::: {module}.{cls}\n")
        f.write("    options.extra:\n")
        f.write("      show_inheritance: true\n")


def build_nav_structure(
    top_label: str, api_rel_dir: str, module_classes: Dict[str, List[str]]
):
    # Organize classes by category inferred from module path after the package name
    # e.g., swarmauri_standard.agents.foo -> category "Agents"
    by_category: Dict[str, List[Dict[str, str]]] = {}
    for module, classes in module_classes.items():
        if not classes:
            continue
        parts = module.split(".")
        category = parts[1] if len(parts) > 1 else parts[0]
        display = category.replace("_", " ").title()
        if display not in by_category:
            by_category[display] = []
        # Build path for each class page
        mod_dir = os.path.dirname(module.replace(".", "/"))
        for cls in sorted(set(classes)):
            rel_path = os.path.join(
                api_rel_dir, top_label.lower(), mod_dir, f"{cls}.md"
            )
            by_category[display].append({cls: rel_path})

    # Deduplicate and sort entries
    nav = [{"Home": os.path.join(api_rel_dir, top_label.lower(), "index.md")}]
    for cat in sorted(by_category):
        items = by_category[cat]
        seen = set()
        uniq = []
        for item in sorted(items, key=lambda x: list(x.keys())[0]):
            name = list(item.keys())[0]
            if name not in seen:
                seen.add(name)
                uniq.append(item)
        nav.append({cat: uniq})
    return [{top_label: nav}]


def load_mkdocs_yml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_mkdocs_yml(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def merge_api_nav(mkdocs_cfg: dict, new_section: list):
    if "nav" not in mkdocs_cfg:
        mkdocs_cfg["nav"] = []

    # Ensure API Documentation section exists
    api_idx = None
    for i, sect in enumerate(mkdocs_cfg["nav"]):
        if isinstance(sect, dict) and "API Documentation" in sect:
            api_idx = i
            break
    if api_idx is None:
        mkdocs_cfg["nav"].append({"API Documentation": ["api/index.md"]})
        api_idx = len(mkdocs_cfg["nav"]) - 1

    api_section = mkdocs_cfg["nav"][api_idx]["API Documentation"]
    top_label = list(new_section[0].keys())[0]

    # Replace or append top_label section
    replaced = False
    for i, item in enumerate(api_section):
        if isinstance(item, dict) and top_label in item:
            api_section[i] = new_section[0]
            replaced = True
            break
    if not replaced:
        api_section.append(new_section[0])

    mkdocs_cfg["nav"][api_idx]["API Documentation"] = api_section


def process_target(
    docs_root: str,
    api_output_dir: str,
    target: Target,
    cache: Dict,
    changed_only: bool,
):
    # Resolve search_path relative to docs_root
    search_path = os.path.normpath(os.path.join(docs_root, target.search_path))
    packages: List[Tuple[str, str]] = []  # (package_name, package_root_dir)

    if target.discover:
        # search_path/<pkg>/<pkg>/__init__.py
        for entry in discover_packages(search_path):
            pkg_name = os.path.basename(entry[1])  # the inner dir name
            # entry[1] is search_path/<pkg>, package dir is the same basename
            packages.append((pkg_name, search_path))
    else:
        if not target.package:
            return {}
        packages.append((target.package, search_path))

    includes = target.include or ["*."]
    excludes = target.exclude or []

    module_classes: Dict[str, List[str]] = {}
    cache.setdefault("files", {})

    for package_name, package_root in packages:
        pkg_dir = os.path.join(package_root, package_name)
        if not os.path.isdir(pkg_dir):
            continue
        for fpath, module in iter_python_files(package_root, package_name):
            if not module_allowed(module, includes, excludes):
                continue
            # Ensure the module is importable as a package path; skip otherwise to avoid mkdocstrings errors
            if not is_valid_package_path(package_root, fpath):
                print(
                    f"Skipping non-package module (missing __init__.py in path): {module}"
                )
                continue
            try:
                with open(fpath, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except Exception:
                continue
            classes = extract_classes_from_source(content)
            module_classes.setdefault(module, []).extend(classes)

            # Cache check
            mtime = os.path.getmtime(fpath)
            h = file_hash(content)
            ckey = os.path.relpath(fpath, docs_root)
            prev = cache["files"].get(ckey)
            dirty = prev is None or prev.get("mtime") != mtime or prev.get("hash") != h

            # Write pages if needed
            top_dir = os.path.join(
                docs_root, "docs", api_output_dir, target.name.lower()
            )
            ensure_home_page(top_dir)
            mod_dir = os.path.join(
                docs_root,
                "docs",
                api_output_dir,
                target.name.lower(),
                os.path.dirname(module.replace(".", "/")),
            )
            if not classes:
                # no class pages to emit
                cache["files"][ckey] = {"mtime": mtime, "hash": h}
                continue
            for cls in classes:
                out_path = os.path.join(mod_dir, f"{cls}.md")
                if (not changed_only) or dirty or (not os.path.exists(out_path)):
                    write_class_page(out_path, module, cls)
            cache["files"][ckey] = {"mtime": mtime, "hash": h}

    # Deduplicate class lists
    for k, v in list(module_classes.items()):
        module_classes[k] = sorted(set(v))

    return module_classes


def main():
    parser = argparse.ArgumentParser(
        description="Generate per-class Markdown using static parsing"
    )
    parser.add_argument(
        "--manifest",
        default="api_manifest.yaml",
        help="Path to api manifest YAML (relative to docs/)",
    )
    parser.add_argument(
        "--docs-dir", default=".", help="Docs working directory (default: current)"
    )
    parser.add_argument(
        "--api-output-dir", default="api", help="Relative output dir under docs/docs/"
    )
    parser.add_argument(
        "--mkdocs-yml",
        default="mkdocs.yml",
        help="Path to mkdocs.yml relative to docs/",
    )
    parser.add_argument(
        "--changed-only",
        action="store_true",
        help="Only rewrite pages for changed sources",
    )
    args = parser.parse_args()

    docs_root = os.path.abspath(args.docs_dir)
    manifest_path = os.path.join(docs_root, args.manifest)
    mkdocs_path = os.path.join(docs_root, args.mkdocs_yml)

    targets = load_manifest(manifest_path)
    cache = read_cache(os.path.join(docs_root, CACHE_FILE))

    accumulated_nav_sections = []

    for tgt in targets:
        module_classes = process_target(
            docs_root=docs_root,
            api_output_dir=args.api_output_dir,
            target=tgt,
            cache=cache,
            changed_only=args.changed_only,
        )
        if module_classes:
            nav_section = build_nav_structure(
                top_label=tgt.name,
                api_rel_dir=args.api_output_dir,
                module_classes=module_classes,
            )
            accumulated_nav_sections.append(nav_section)

    # Update mkdocs.yml
    if accumulated_nav_sections:
        cfg = load_mkdocs_yml(mkdocs_path)
        for section in accumulated_nav_sections:
            merge_api_nav(cfg, section)
        save_mkdocs_yml(mkdocs_path, cfg)

    # Write cache
    write_cache(os.path.join(docs_root, CACHE_FILE), cache)

    print("API docs generation completed.")


if __name__ == "__main__":
    main()
