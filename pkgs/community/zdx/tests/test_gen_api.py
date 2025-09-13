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
