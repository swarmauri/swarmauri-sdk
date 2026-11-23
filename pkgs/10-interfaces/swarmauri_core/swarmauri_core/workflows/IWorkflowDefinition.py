"""IWorkflowDefinition contract."""

from abc import ABC, abstractmethod

from .models import GraphDefinition


class IWorkflowDefinition(ABC):
    """Define the interchangeable WorkflowDefinition contract."""

    @abstractmethod
    def definition(self) -> GraphDefinition: ...
