import json
import tomllib

import pytest
import yaml

from jollof.plugin_manager import PluginManager
from .dummy_plugins import ExamplePlugin


@pytest.mark.parametrize(
    "fmt,config,parser",
    [
        ("json", '{"name": "a", "value": 1}', json.loads),
        ("yaml", "name: a\nvalue: 1\n", yaml.safe_load),
        ("toml", 'name = "a"\nvalue = 1\n', tomllib.loads),
    ],
)
def test_roundtrip_formats(fmt, config, parser):
    pm = PluginManager()
    pm.register("examples", "ExamplePlugin", ExamplePlugin)
    inst = pm.load("examples", "ExamplePlugin", config, fmt)
    dumped = pm.dump(inst, fmt)
    assert parser(dumped) == {"name": "a", "value": 1}
