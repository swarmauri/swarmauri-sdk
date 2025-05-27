import sys
import types
from pathlib import Path
import pytest

# Provide a minimal jsonschema stub if jsonschema is unavailable
if 'jsonschema' not in sys.modules:
    js = types.ModuleType('jsonschema')

    class Draft7Validator:
        def __init__(self, schema):
            self.schema = schema

        def iter_errors(self, data):
            return []

    js.Draft7Validator = Draft7Validator
    js.ValidationError = Exception
    js.validate = lambda instance, schema: None
    sys.modules['jsonschema'] = js

from typer import Exit
from peagen.commands import validate as validate_cmds

EXAMPLES = Path(__file__).resolve().parent.parent / 'examples'


@pytest.mark.unit
def test_validate_config_success(tmp_path):
    cfg_src = EXAMPLES / 'peagen_tomls' / '.peagen.toml'
    cfg_dst = tmp_path / '.peagen.toml'
    cfg_dst.write_text(cfg_src.read_text())

    validate_cmds.validate_config(None, path=cfg_dst)


@pytest.mark.unit
def test_validate_config_missing():
    with pytest.raises(Exit):
        validate_cmds.validate_config(None, path=Path('nonexistent.toml'))


@pytest.mark.unit
def test_validate_doe_success():
    spec = EXAMPLES / 'doe_specs' / 'doe_spec.yaml'
    validate_cmds.validate_doe_spec(None, spec_path=spec)


@pytest.mark.unit
def test_validate_manifest_success():
    manifest = EXAMPLES / 'manifests' / 'ExampleParserProject_manifest.json'
    validate_cmds.validate_manifest(None, manifest_path=manifest)


@pytest.mark.unit
def test_validate_manifest_invalid_json(tmp_path):
    bad = tmp_path / 'bad.json'
    bad.write_text('{invalid json')
    with pytest.raises(Exit):
        validate_cmds.validate_manifest(None, manifest_path=bad)


@pytest.mark.unit
def test_validate_ptree_success():
    ptree = EXAMPLES / 'ptrees' / 'ptree.yaml'
    validate_cmds.validate_ptree(None, ptree_path=ptree)


@pytest.mark.unit
def test_validate_projects_payload_success():
    payload = EXAMPLES / 'projects_payloads' / 'projects_payload.yaml'
    validate_cmds.validate_projects_payload(None, payload_path=payload)

