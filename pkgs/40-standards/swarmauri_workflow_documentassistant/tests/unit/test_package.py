"""Verify the installed component's public contract and discovery."""

from importlib.metadata import distribution
import pytest
from swarmauri_workflow_documentassistant import (
    DocumentAssistantWorkflow,
    __version__,
)
from swarmauri_base.workflows import WorkflowDefinitionBase


@pytest.mark.unit
def test_installed_component_contract():
    assert issubclass(DocumentAssistantWorkflow, WorkflowDefinitionBase)
    installed = distribution("swarmauri_workflow_documentassistant")
    assert installed.version == __version__
    entry = next(
        e
        for e in installed.entry_points
        if e.name == "DocumentAssistantWorkflow"
    )
    assert entry.group == "swarmauri.workflows"
    assert entry.load() is DocumentAssistantWorkflow
