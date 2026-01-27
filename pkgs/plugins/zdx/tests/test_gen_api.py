import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "zdx"))
from zdx.scripts.gen_api import Target, load_manifest, process_target


def test_load_manifest_default_include(tmp_path):
    manifest = tmp_path / "api_manifest.yaml"
    manifest.write_text("targets:\n- name: Foo\n  search_path: pkgs/foo\n")
    targets = load_manifest(str(manifest))
    assert targets[0].include == ["*.*"]


def test_process_target_discovers_packages(tmp_path):
    docs_root = tmp_path
    pkg_root = docs_root / "pkgs" / "community" / "test_pkg" / "test_pkg"
    pkg_root.mkdir(parents=True)
    (pkg_root / "__init__.py").write_text("")
    (pkg_root / "mod.py").write_text("class MyClass:\n    pass\n")

    target = Target(
        name="Community",
        search_path="pkgs/community",
        discover=True,
        include=["*.*"],
        exclude=[],
    )
    cache = {}
    module_classes = process_target(
        docs_root=str(docs_root),
        api_output_dir="api",
        target=target,
        cache=cache,
        changed_only=False,
    )
    assert "test_pkg.mod" in module_classes
    doc_file = docs_root / "docs" / "api" / "community" / "test_pkg" / "MyClass.md"
    assert doc_file.is_file()


def test_process_target_skips_requested_packages(tmp_path):
    docs_root = tmp_path
    for name in ("keep_pkg", "skip_pkg"):
        pkg_root = docs_root / "pkgs" / "community" / name / name
        pkg_root.mkdir(parents=True)
        (pkg_root / "__init__.py").write_text("")
        (pkg_root / "mod.py").write_text("class Thing:\n    pass\n")

    target = Target(
        name="Community",
        search_path="pkgs/community",
        discover=True,
        include=["*.*"],
        exclude=[],
    )
    cache: dict = {}
    module_classes = process_target(
        docs_root=str(docs_root),
        api_output_dir="api",
        target=target,
        cache=cache,
        changed_only=False,
        skip_packages={"skip_pkg"},
    )

    assert "keep_pkg.mod" in module_classes
    assert "skip_pkg.mod" not in module_classes
    skipped_file = docs_root / "docs" / "api" / "community" / "skip_pkg" / "Thing.md"
    assert not skipped_file.exists()


def test_process_target_reuses_cached_classes(tmp_path, monkeypatch):
    docs_root = tmp_path
    pkg_root = docs_root / "pkgs" / "community" / "cached_pkg" / "cached_pkg"
    pkg_root.mkdir(parents=True)
    (pkg_root / "__init__.py").write_text("")
    mod_file = pkg_root / "mod.py"
    mod_file.write_text("class Cached:\n    pass\n")

    target = Target(
        name="Community",
        search_path="pkgs/community",
        discover=True,
        include=["*.*"],
        exclude=[],
    )
    cache: dict = {}
    process_target(
        docs_root=str(docs_root),
        api_output_dir="api",
        target=target,
        cache=cache,
        changed_only=False,
    )

    cache_key = str(mod_file.relative_to(docs_root))
    cached_entry = cache["files"][cache_key]
    assert cached_entry["classes"] == ["Cached"]
    assert cached_entry["size"] == mod_file.stat().st_size

    def _boom(*args, **kwargs):
        raise AssertionError("analyze should not run for cached entries")

    monkeypatch.setattr("zdx.scripts.gen_api._analyze_file", _boom)

    process_target(
        docs_root=str(docs_root),
        api_output_dir="api",
        target=target,
        cache=cache,
        changed_only=False,
    )
