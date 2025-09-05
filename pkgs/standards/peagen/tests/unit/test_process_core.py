import yaml
import pytest
from pathlib import Path

import peagen.core.process_core as process_core
from peagen.core.process_core import _render_package_ptree, process_single_project
from peagen.core.sort_core import sort_file_records


@pytest.fixture
def tmp_template_set(tmp_path: Path) -> Path:
    """
    Create a temporary template set directory containing:
      - ptree.yaml.j2
      - A simple file-level template file1.txt.j2
    """
    tmpl_dir = tmp_path / "python_orm"
    tmpl_dir.mkdir()

    # Write ptree.yaml.j2 that loops over PROJ.PKGS (each with MODULES)
    ptree = tmpl_dir / "ptree.yaml.j2"
    ptree_contents = """
{%- for PKG in PROJ.PKGS %}
{%- for MOD in PKG.MODULES %}
- FILE_NAME: "{{ PROJ.ROOT }}/{{ PKG.NAME }}/{{ MOD.NAME }}.txt.j2"
  RENDERED_FILE_NAME: "{{ PROJ.ROOT }}/{{ PKG.NAME }}/{{ MOD.NAME }}.txt"
  PROCESS_TYPE: "GENERATE"
  PROMPT_TEMPLATE: "file1.txt.j2"
  PROJECT_NAME: "{{ PROJ.NAME }}"
  PACKAGE_NAME: "{{ PKG.NAME }}"
  MODULE_NAME: "{{ MOD.NAME }}"
  EXTRAS: {}
{%- endfor %}
{%- endfor %}
"""
    ptree.write_text(ptree_contents)

    # Create a file-level Jinja template at tmpl_dir/file1.txt.j2
    file1 = tmpl_dir / "file1.txt.j2"
    file1.write_text(
        "Generated for {{ PROJ.NAME }}: {{ PACKAGE_NAME }}.{{ MODULE_NAME }}"
    )

    return tmpl_dir


@pytest.fixture
def tmp_project_payload(tmp_path: Path, tmp_template_set: Path) -> Path:
    """
    Create a project payload YAML that references the above template set.
    """
    # Create a project structure
    root_dir = tmp_path / "project_root"
    (root_dir / "pkgA").mkdir(parents=True)

    project_payload = {
        "PROJECTS": [
            {
                "NAME": "test_project",
                "ROOT": "project_root",
                "TEMPLATE_SET": "python_orm",
                "PACKAGES": [
                    {
                        "NAME": "pkgA",
                        "TEMPLATE_SET": "python_orm",
                        "MODULES": [
                            {
                                "NAME": "mod1",
                                "EXTRAS": {
                                    "PURPOSE": "test",
                                    "DESCRIPTION": "desc",
                                    "REQUIREMENTS": [],
                                    "MODEL_NAME": "Mod1",
                                    "HAS_CHILDREN": False,
                                    "CHILD_NAME": None,
                                    "FIELD_DEFINITIONS": "",
                                    "DEPENDENCIES": [],
                                },
                            }
                        ],
                    }
                ],
                "SOURCE_PACKAGES": [],
            }
        ]
    }
    payload_file = tmp_path / "projects.yml"
    payload_file.write_text(yaml.dump(project_payload))

    # Create a file system structure so PROJ.ROOT resolves:
    #   project_root/pkgA directory must exist
    return payload_file


def test_render_package_ptree(
    tmp_path: Path, tmp_template_set: Path, tmp_project_payload: Path
):
    """
    Verify that _render_package_ptree produces correct file-record list from ptree.yaml.j2.
    """
    # Build minimal global search path
    global_search_paths = [tmp_template_set.parent]

    # Load project and package dict
    payload = yaml.safe_load(tmp_project_payload.read_text())
    project = payload["PROJECTS"][0]
    pkg = project["PACKAGES"][0]

    records = _render_package_ptree(
        project=project,
        pkg=pkg,
        global_search_paths=global_search_paths,
        project_dir=tmp_path,
        log=None,
    )

    # Expect exactly one record for module "mod1"
    assert len(records) == 1
    rec = records[0]
    assert rec["FILE_NAME"].endswith("project_root/pkgA/mod1.txt.j2")
    assert rec["RENDERED_FILE_NAME"].endswith("project_root/pkgA/mod1.txt")
    assert rec["PROCESS_TYPE"] == "GENERATE"
    assert rec["PROMPT_TEMPLATE"] == "file1.txt.j2"
    assert rec["TEMPLATE_SET"].endswith("python_orm")
    assert isinstance(rec["PTREE_SEARCH_PATHS"], list)


def test_process_single_project_integration(
    tmp_path: Path, tmp_template_set: Path, tmp_project_payload: Path, monkeypatch
):
    """
    End-to-end integration: process_single_project should:
      - Render ptree.yaml.j2,
      - Generate a file mod1.txt with correct content,
      - Write a tracking record for the generated file.
    """
    payload = yaml.safe_load(tmp_project_payload.read_text())
    project = payload["PROJECTS"][0]

    class DummyAdapter:
        root_uri = "file://dummy/"

        def upload(self, key, fsrc):
            # pretend to upload and return an artifact URI
            return f"{self.root_uri}{key}"

    monkeypatch.setattr(
        "peagen.core.render_core.call_external_agent",
        lambda prompt, agent_env, logger=None: "Generated for test_project: pkgA.mod1",
    )

    monkeypatch.setattr(
        process_core,
        "sort_file_records",
        lambda records,
        start_idx=0,
        start_file=None,
        transitive=False: sort_file_records(
            file_records=records,
            start_idx=start_idx,
            start_file=start_file,
            transitive=transitive,
        ),
    )

    cfg = {
        "logger": None,
        "storage_adapter": DummyAdapter(),
        "peagen_version": "test",
        "agent_env": {},
        "worktree": tmp_path,
    }

    sorted_records, next_idx, commit_sha, oids = process_single_project(
        project=project,
        cfg=cfg,
        start_idx=0,
        start_file=None,
        transitive=False,
    )

    # Expect one record
    assert len(sorted_records) == 1
    rec = sorted_records[0]
    assert isinstance(oids, list)

    # Check that the file was written
    out_file = Path(cfg["worktree"]) / rec["RENDERED_FILE_NAME"]
    assert out_file.exists()

    # The content should match the template ("Generated for test_project: pkgA.mod1")
    content = out_file.read_text()
    assert "Generated for test_project: pkgA.mod1" in content
