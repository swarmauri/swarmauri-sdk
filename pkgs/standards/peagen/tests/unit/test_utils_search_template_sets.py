import pytest
from pathlib import Path
from peagen._utils._search_template_sets import (
    build_global_template_search_paths,
    build_ptree_template_search_paths,
    build_file_template_search_paths,
)


@pytest.fixture
def tmp_dirs(tmp_path: Path):
    """
    Creates a temporary directory structure for testing:
      - workspace_root
      - two source-package dests under workspace_root
      - a base_dir
      - a template_base_dir
      - some built-in or plugin paths (simulated)
    """
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()

    # Simulate two source-package dests
    src1 = {"dest": "pkgA"}
    src2 = {"dest": "pkgB"}
    (workspace_root / "pkgA").mkdir()
    (workspace_root / "pkgB").mkdir()

    # template_base_dir override
    template_base_dir = tmp_path / "base_templates"
    template_base_dir.mkdir()

    # base_dir (project root)
    base_dir = tmp_path / "cwd"
    base_dir.mkdir()

    return {
        "workspace_root": workspace_root,
        "source_packages": [src1, src2],
        "template_base_dir": template_base_dir,
        "base_dir": base_dir,
    }


def test_build_global_template_search_paths(tmp_dirs):
    """
    Verify that build_global_template_search_paths orders entries as:
      [workspace_root,
       built-in paths (peagen.templates),
       plugin paths,
       workspace_root/pkgA, workspace_root/pkgB,
       template_base_dir,
       base_dir]
    """
    # We can't easily check built-ins or plugins here without mocking,
    # but we can check that workspace_root is first and template_base_dir/base_dir are last two.
    paths = build_global_template_search_paths(
        workspace_root=tmp_dirs["workspace_root"],
        source_packages=tmp_dirs["source_packages"],
        base_dir=tmp_dirs["base_dir"],
    )

    # 1st must be workspace_root
    assert paths[0] == tmp_dirs["workspace_root"].resolve()
    # Last path must be base_dir
    assert paths[-1] == tmp_dirs["base_dir"].resolve()


def test_build_ptree_template_search_paths(tmp_dirs):
    """
    Verify build_ptree_template_search_paths returns exactly:
      [package_template_dir,
       base_dir,
       workspace_root/pkgA, workspace_root/pkgB]
    """
    package_template_dir = tmp_dirs["template_base_dir"] / "my_set"
    package_template_dir.mkdir()

    ptree_paths = build_ptree_template_search_paths(
        package_template_dir=package_template_dir,
        base_dir=tmp_dirs["base_dir"],
        workspace_root=tmp_dirs["workspace_root"],
        source_packages=tmp_dirs["source_packages"],
    )

    expected = [
        package_template_dir.resolve(),
        tmp_dirs["base_dir"].resolve(),
        (tmp_dirs["workspace_root"] / "pkgA").resolve(),
        (tmp_dirs["workspace_root"] / "pkgB").resolve(),
    ]
    assert ptree_paths == expected


def test_build_file_template_search_paths(tmp_dirs):
    """
    Verify build_file_template_search_paths prepends record_template_dir and workspace_root,
    then appends everything except the first element of ptree_paths.
    """
    record_dir = tmp_dirs["template_base_dir"] / "my_set"
    record_dir.mkdir()

    # Suppose ptree_paths is:
    ptree_paths = [
        record_dir,
        tmp_dirs["base_dir"],
        (tmp_dirs["workspace_root"] / "pkgA"),
    ]

    file_paths = build_file_template_search_paths(
        record_template_dir=record_dir,
        workspace_root=tmp_dirs["workspace_root"],
        ptree_search_paths=ptree_paths,
    )

    # Expected:
    # [record_dir, workspace_root, base_dir, workspace_root/pkgA]
    expected = [
        record_dir.resolve(),
        tmp_dirs["workspace_root"].resolve(),
        tmp_dirs["base_dir"].resolve(),
        (tmp_dirs["workspace_root"] / "pkgA").resolve(),
    ]
    assert file_paths == expected
