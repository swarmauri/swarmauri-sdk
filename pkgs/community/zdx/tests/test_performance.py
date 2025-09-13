import os
import sys
import time
from pathlib import Path
from typing import Dict, List

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from zdx.scripts.gen_api import (
    Target,
    extract_classes_from_source,
    file_hash,
    iter_python_files,
    is_valid_package_path,
    module_allowed,
    write_class_page,
    ensure_home_page,
    process_target,
)


def _create_dummy_package(root: Path, modules: int = 60, classes: int = 30) -> None:
    pkg_dir = root / "src" / "pkg"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    class_def = "\n".join(f"class C{i}:\n    pass" for i in range(classes))
    for m in range(modules):
        (pkg_dir / f"mod{m}.py").write_text(class_def, encoding="utf-8")


def _baseline_process_target(
    docs_root: str, api_output_dir: str, target: Target, cache: Dict, changed_only: bool
) -> Dict[str, List[str]]:
    search_path = os.path.normpath(os.path.join(docs_root, target.search_path))
    packages = [(target.package, search_path)] if target.package else []
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
            if not is_valid_package_path(package_root, fpath):
                continue
            try:
                with open(fpath, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except Exception:
                continue
            classes = extract_classes_from_source(content)
            module_classes.setdefault(module, []).extend(classes)
            mtime = os.path.getmtime(fpath)
            h = file_hash(content)
            ckey = os.path.relpath(fpath, docs_root)
            prev = cache["files"].get(ckey)
            dirty = prev is None or prev.get("mtime") != mtime or prev.get("hash") != h
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
                cache["files"][ckey] = {"mtime": mtime, "hash": h}
                continue
            for cls in classes:
                out_path = os.path.join(mod_dir, f"{cls}.md")
                if (not changed_only) or dirty or (not os.path.exists(out_path)):
                    write_class_page(out_path, module, cls)
            cache["files"][ckey] = {"mtime": mtime, "hash": h}
    for k, v in list(module_classes.items()):
        module_classes[k] = sorted(set(v))
    return module_classes


def _timed(func, docs_root: Path) -> float:
    cache: Dict = {}
    target = Target(name="Test", search_path="src", package="pkg")
    start = time.perf_counter()
    func(
        docs_root=str(docs_root),
        api_output_dir="api",
        target=target,
        cache=cache,
        changed_only=False,
    )
    return time.perf_counter() - start


@pytest.mark.skip("Performance comparison is unstable across environments")
def test_process_target_speed(tmp_path: Path) -> None:
    baseline_root = tmp_path / "baseline"
    optimized_root = tmp_path / "optimized"
    for root in (baseline_root, optimized_root):
        (root / "docs").mkdir(parents=True)
        _create_dummy_package(root)
    slow = _timed(_baseline_process_target, baseline_root)
    fast = _timed(process_target, optimized_root)
    assert fast <= slow * 0.75
