from .base import (
    ITaskHandler,
    TaskHandlerBase,
    TaskHandler,
    can_handle,
)
from .render_handler import RenderHandler
from .mutate_patch import PatchMutatorHandler
from .exec_docker import ExecuteDockerHandler
from .exec_gpu import ExecuteGPUHandler
from .eval_handler import EvaluateHandler
from ..plugin_registry import registry, discover_and_register_plugins

if not registry.get("task_handlers"):
    discover_and_register_plugins()

__all__ = [
    "ITaskHandler",
    "TaskHandlerBase",
    "TaskHandler",
    "can_handle",
    "RenderHandler",
    "PatchMutatorHandler",
    "ExecuteDockerHandler",
    "ExecuteGPUHandler",
    "EvaluateHandler",
]
