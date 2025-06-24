import io
import yaml
import pytest

from peagen.core.process_core import load_projects_payload
from peagen.errors import ProjectsPayloadValidationError
from peagen.plugins.storage_adapters.file_storage_adapter import FileStorageAdapter


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
    adapter = FileStorageAdapter(tmp_path)
    uri = adapter.upload("pp.yaml", io.BytesIO(yaml_text.encode()))

    projects = load_projects_payload(uri)
    assert projects and projects[0]["NAME"] == "A"


@pytest.mark.unit
def test_load_projects_payload_validation_error(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("PROJECTS:\n  - NAME: foo\n")

    with pytest.raises(ProjectsPayloadValidationError):
        load_projects_payload(str(bad))
