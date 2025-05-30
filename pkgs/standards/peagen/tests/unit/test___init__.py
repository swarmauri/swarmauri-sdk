import random; random.seed(0xA11A)
import importlib
import types
import sys
import pytest

import peagen.plugin_registry as pr


@pytest.mark.unit
def test_determine_plugin_mode(monkeypatch):
    monkeypatch.setattr(pr, "discover_and_register_plugins", lambda mode=None: None)
    monkeypatch.setattr(sys, "argv", ["peagen", "--plugin-mode", "switch"])
    mod = importlib.reload(importlib.import_module("peagen"))
    assert mod._determine_plugin_mode() == "switch"
