import pytest

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


@pytest.fixture(autouse=True)
def restore_registry():
    """Restore plugin registries after each test."""
    first = PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY.copy()
    second = PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY.copy()
    third = PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.copy()
    yield
    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY = first
    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY = second
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY = third


@pytest.mark.unit
def test_add_and_remove_entry():
    PluginCitizenshipRegistry.add_to_registry(
        "first", "swarmauri.agents.TestAgent", "tests.test_module.TestAgent"
    )
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.agents.TestAgent"
        ]
        == "tests.test_module.TestAgent"
    )

    PluginCitizenshipRegistry.remove_from_registry(
        "first", "swarmauri.agents.TestAgent"
    )
    assert (
        "swarmauri.agents.TestAgent"
        not in PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY
    )


@pytest.mark.unit
def test_add_duplicate_entry_noop():
    PluginCitizenshipRegistry.add_to_registry(
        "third", "swarmauri.plugins.sample", "math"
    )
    # Duplicate addition should be ignored without raising an error
    PluginCitizenshipRegistry.add_to_registry(
        "third", "swarmauri.plugins.sample", "math"
    )
    assert (
        PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY[
            "swarmauri.plugins.sample"
        ]
        == "math"
    )


@pytest.mark.unit
def test_s3_over_sftp_storage_adapter_is_first_class():
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.storage_adapters.S3OverSftpStorageAdapter"
        ]
        == "swarmauri_storage_s3_over_sftp.S3OverSftpStorageAdapter"
    )


@pytest.mark.unit
def test_dummy_skills_are_first_class():
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.skills.DummyFileSystemSkill"
        ]
        == "swarmauri_skill_dummy_filesystem.DummyFileSystemSkill"
    )
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.skills.DummyLocalSkill"
        ]
        == "swarmauri_skill_dummy_local.DummyLocalSkill"
    )


@pytest.mark.unit
def test_skill_execution_tool_is_first_class():
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.tools.SkillExecutionTool"
        ]
        == "swarmauri_tool_skill_execution.SkillExecutionTool"
    )


@pytest.mark.unit
def test_update_and_delete_entry():
    PluginCitizenshipRegistry.add_to_registry(
        "second", "swarmauri.chains.TestChain", "pkg.Chain"
    )
    PluginCitizenshipRegistry.update_entry(
        "second", "swarmauri.chains.TestChain", "pkg.NewChain"
    )
    assert (
        PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY[
            "swarmauri.chains.TestChain"
        ]
        == "pkg.NewChain"
    )

    PluginCitizenshipRegistry.delete_entry(
        "second", "swarmauri.chains.TestChain"
    )
    assert (
        "swarmauri.chains.TestChain"
        not in PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    )

@pytest.mark.unit
def test_query_tools_are_second_class():
    assert PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY[
        "swarmauri.tools.QueryImageVectorStoreTool"
    ] == (
        "swarmauri_tool_queryimagevectorstore.QueryImageVectorStoreTool"
    )
    assert PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY[
        "swarmauri.tools.QueryKnowledgeBaseTool"
    ] == "swarmauri_tool_queryknowledgebase.QueryKnowledgeBaseTool"
