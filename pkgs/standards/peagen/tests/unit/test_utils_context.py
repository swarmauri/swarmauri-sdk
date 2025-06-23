import pytest
from peagen._utils._context import _create_context


class DummyLogger:
    def __init__(self):
        self.debug_messages = []

    def debug(self, msg: str) -> None:
        self.debug_messages.append(msg)


@pytest.mark.unit
def test_create_context_builds_nested_structures():
    file_record = {
        "PROJECT_NAME": "Demo",
        "PACKAGE_NAME": "pkg1",
        "MODULE_NAME": "modA",
    }
    project_attrs = {"PACKAGES": [{"NAME": "pkg1", "MODULES": [{"NAME": "modA"}]}]}
    logger = DummyLogger()
    ctx = _create_context(file_record, project_attrs, logger)
    assert ctx["PROJ"] == project_attrs
    assert ctx["PKG"]["NAME"] == "pkg1"
    assert ctx["MOD"]["NAME"] == "modA"
    assert ctx["FILE"] == file_record
    assert any("context" in m for m in logger.debug_messages)
