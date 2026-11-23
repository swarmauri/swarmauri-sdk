import inspect
import pytest

from swarmauri_core.executions import IExecutionController, IExecutionDriver
from swarmauri_core.tasks import ITaskManager, ITaskStore
from swarmauri_core.permissions import IPermissionPolicy, Permission
from swarmauri_core.delegation import IDelegationService, IGrantStore
from swarmauri_core.invocations import IInvoker, IAuthorityStrategy
from swarmauri_core.workflows import (
    GraphDefinition,
    EdgeDefinition,
    NodeDefinition,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "contract",
    [
        IExecutionController,
        IExecutionDriver,
        ITaskManager,
        ITaskStore,
        IPermissionPolicy,
        IDelegationService,
        IGrantStore,
        IInvoker,
        IAuthorityStrategy,
    ],
)
def test_contracts_require_implementations(contract):
    assert inspect.isabstract(contract)
    with pytest.raises(TypeError):
        contract()


def test_graph_rejects_invalid_references_without_creating_registry():
    with pytest.raises(ValueError):
        GraphDefinition(
            "graph",
            "v1",
            (NodeDefinition("A", "service-A"),),
            (EdgeDefinition("A-to-B", "A", "B"),),
        )
    with pytest.raises(ValueError):
        Permission("read", 123, "tenant")
