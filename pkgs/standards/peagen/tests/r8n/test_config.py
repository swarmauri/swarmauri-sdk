# tests/unit/test_config.py
import pytest
from peagen._config import __logger_name__, _config


@pytest.mark.r8n
class TestConfig:
    def test_config_default_values(self):
        """Test that _config has expected default values"""
        assert isinstance(_config, dict)
        assert __logger_name__ == "pea"

    def test_config_transitive_flag(self):
        """Test that the transitive flag can be set and retrieved"""
        original = _config.get("transitive", False)

        _config["transitive"] = not original
        assert _config["transitive"] == (not original)

        _config["transitive"] = original
        assert _config["transitive"] == original
