import yaml
import pytest

from peagen.core.process_core import load_projects_payload
from peagen.errors import (
    ProjectsPayloadValidationError,
    ProjectsPayloadFormatError,
    MissingProjectsListError,
)


@pytest.mark.unit
def test_load_projects_payload_remote(tmp_path):
    data = {
        "schemaVersion": "1.0.0",
        "PROJECTS": [
            {
                "NAME": "A",
                "ROOT": ".",
                "PACKAGES": [{"NAME": "pkg", "MODULES": [{"NAME": "m", "EXTRAS": {}}]}],
            }
        ],
    }
    yaml_text = yaml.safe_dump(data)
    yaml_file = tmp_path / "pp.yaml"
    yaml_file.write_text(yaml_text)

    projects = load_projects_payload(str(yaml_file))
    assert projects and projects[0]["NAME"] == "A"


@pytest.mark.unit
def test_load_projects_payload_validation_error(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("PROJECTS:\n  - NAME: foo\n")

    with pytest.raises(ProjectsPayloadValidationError):
        load_projects_payload(str(bad))


@pytest.mark.unit
def test_load_projects_payload_format_error(tmp_path):
    bad = tmp_path / "str.yaml"
    bad.write_text("just a string")

    with pytest.raises(ProjectsPayloadFormatError):
        load_projects_payload(str(bad))


@pytest.mark.unit
def test_load_projects_payload_missing_projects_list(tmp_path):
    bad = tmp_path / "missing.yaml"
    bad.write_text("schemaVersion: '1.0.0'\nPROJECTS: {}\n")

    # Missing list should trigger a dedicated error
    with pytest.raises(MissingProjectsListError):
        load_projects_payload(str(bad))


@pytest.mark.unit
def test_load_projects_payload_path_object(tmp_path):
    bad = tmp_path / "missing.yaml"
    bad.write_text("schemaVersion: '1.0.0'\nPROJECTS: {}\n")

    # PathLike values should be accepted
    with pytest.raises(MissingProjectsListError):
        load_projects_payload(bad)
