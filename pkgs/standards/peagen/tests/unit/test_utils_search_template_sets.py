import pytest
from pathlib import Path
from peagen._utils._search_template_sets import (
    build_global_template_search_paths,
    build_ptree_template_search_paths,
    build_file_template_search_paths,
)


@pytest.fixture
def tmp_dirs(tmp_path: Path):
    """Create temporary base and template directories for search path tests."""
    base_dir = tmp_path / "cwd"
    base_dir.mkdir()

    template_base_dir = tmp_path / "base_templates"
    template_base_dir.mkdir()

    return {
        "base_dir": base_dir,
        "template_base_dir": template_base_dir,
    }


def test_build_global_template_search_paths(tmp_dirs):
    """build_global_template_search_paths ends with the caller-supplied base_dir."""

    paths = build_global_template_search_paths(base_dir=tmp_dirs["base_dir"])

    assert paths[-1] == tmp_dirs["base_dir"].resolve()


def test_build_ptree_template_search_paths(tmp_dirs):
    """ptree search path is [package_template_dir, base_dir]."""

    package_template_dir = tmp_dirs["template_base_dir"] / "my_set"
    package_template_dir.mkdir()

    ptree_paths = build_ptree_template_search_paths(
        package_template_dir=package_template_dir,
        base_dir=tmp_dirs["base_dir"],
    )

    expected = [
        package_template_dir.resolve(),
        tmp_dirs["base_dir"].resolve(),
    ]
    assert ptree_paths == expected


def test_build_file_template_search_paths(tmp_dirs):
    """build_file_template_search_paths prepends record dir then ptree paths."""
    record_dir = tmp_dirs["template_base_dir"] / "my_set"
    record_dir.mkdir()

    # Suppose ptree_paths is:
    ptree_paths = [record_dir, tmp_dirs["base_dir"]]

    file_paths = build_file_template_search_paths(
        record_template_dir=record_dir,
        ptree_search_paths=ptree_paths,
    )

    expected = [record_dir.resolve(), *[p.resolve() for p in ptree_paths]]
    assert file_paths == expected
