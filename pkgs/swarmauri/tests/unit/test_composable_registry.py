import pytest
from swarmauri.interface_registry import InterfaceRegistry
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "namespace,name,module",
    [
        (
            "executions",
            "DefaultExecutionController",
            "swarmauri_execution_default",
        ),
        ("tasks", "DefaultTaskManager", "swarmauri_taskmanager_default"),
        ("task_stores", "SqliteTaskStore", "swarmauri_taskstore_sqlite"),
        (
            "permissions",
            "ExplicitPermissionPolicy",
            "swarmauri_permission_explicit",
        ),
        (
            "delegations",
            "AttenuatingDelegationService",
            "swarmauri_delegation_attenuating",
        ),
        ("grant_stores", "SqliteGrantStore", "swarmauri_grantstore_sqlite"),
        ("invocations", "DefaultInvoker", "swarmauri_invoker_default"),
        (
            "workflows",
            "DocumentAssistantWorkflow",
            "swarmauri_workflow_documentassistant",
        ),
        (
            "workflows",
            "DelegatedResearchWorkflow",
            "swarmauri_workflow_delegatedresearch",
        ),
    ],
)
def test_concrete_registration_and_matching_base(namespace, name, module):
    import importlib

    concrete = getattr(importlib.import_module(module), name)
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            f"swarmauri.{namespace}.{name}"
        ]
        == f"{module}.{name}"
    )
    base = InterfaceRegistry.get_interface_for_resource(
        f"swarmauri.{namespace}"
    )
    assert issubclass(concrete, base)
