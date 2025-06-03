import random; random.seed(0xA11A)
import yaml
import pytest
from peagen.core import Peagen


@pytest.mark.unit
def test_load_projects(tmp_path):
    f = tmp_path / "p.yml"
    f.write_text(yaml.safe_dump({"PROJECTS": [{"NAME": "Proj"}]}))
    pg = Peagen(projects_payload_path=str(f))
    projects = pg.load_projects()
    assert projects[0]["NAME"] == "Proj"
    assert pg.slug_map["proj"] == "Proj"
