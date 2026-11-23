import pytest
import inspect
from swarmauri_base.ComponentBase import ComponentBase
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
def test_optional_component_registration(namespace, name, module, monkeypatch):
    """The facade must not require every standalone plugin to be installed.

    Concrete inheritance and entry-point loading are checked in each
    implementation package's test_package.py.
    """
    import importlib

    original_import = importlib.import_module

    def without_optional_plugin(import_name, *args, **kwargs):
        if import_name == module or import_name.startswith(module + "."):
            pytest.fail("Facade registry imported an optional implementation")
        return original_import(import_name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", without_optional_plugin)
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            f"swarmauri.{namespace}.{name}"
        ]
        == f"{module}.{name}"
    )
    base = InterfaceRegistry.get_interface_for_resource(
        f"swarmauri.{namespace}"
    )
    assert issubclass(base, ComponentBase)
    assert inspect.isabstract(base)
