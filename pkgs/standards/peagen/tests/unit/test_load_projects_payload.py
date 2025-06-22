import io
import yaml
import pytest

from peagen.core.process_core import load_projects_payload
from peagen.plugins.storage_adapters.file_storage_adapter import FileStorageAdapter


@pytest.mark.unit
def test_load_projects_payload_remote(tmp_path):
    data = {"PROJECTS": [{"NAME": "A"}]}
    yaml_text = yaml.safe_dump(data)
    adapter = FileStorageAdapter(tmp_path)
    uri = adapter.upload("pp.yaml", io.BytesIO(yaml_text.encode()))

    projects = load_projects_payload(uri)
    assert projects and projects[0]["NAME"] == "A"
