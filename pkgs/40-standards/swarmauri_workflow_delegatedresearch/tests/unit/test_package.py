"""Verify the installed component's public contract and discovery."""

from importlib.metadata import distribution
import pytest
from swarmauri_workflow_delegatedresearch import (
    DelegatedResearchWorkflow,
    __version__,
)
from swarmauri_base.workflows import WorkflowDefinitionBase


@pytest.mark.unit
def test_installed_component_contract():
    assert issubclass(DelegatedResearchWorkflow, WorkflowDefinitionBase)
    installed = distribution("swarmauri_workflow_delegatedresearch")
    assert installed.version == __version__
    entry = next(
        e
        for e in installed.entry_points
        if e.name == "DelegatedResearchWorkflow"
    )
    assert entry.group == "swarmauri.workflows"
    assert entry.load() is DelegatedResearchWorkflow
