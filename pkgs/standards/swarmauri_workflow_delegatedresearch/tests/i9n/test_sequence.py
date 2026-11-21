import pytest

from swarmauri_core.permissions import Permission
from swarmauri_workflow_documentassistant.demo import (
    ScriptedDocumentModel,
    demo_tokens,
)
from swarmauri_workflow_delegatedresearch import DelegatedResearchWorkflow

pytestmark = pytest.mark.i9n


async def test_three_hop_chain_has_real_agent_runs_and_narrowed_grants(
    tmp_path,
):
    tokens, kid, issuer = await demo_tokens()
    workflow = DelegatedResearchWorkflow.create(
        tmp_path,
        tokens=tokens,
        kid=kid,
        issuer=issuer,
        model_factory=ScriptedDocumentModel,
        authorize=lambda subject, p: subject == "alice",
        documents={"document:123": "verified content"},
        permission=Permission("documents:read", "document:123", "tenant"),
    )
    captures = []
    for endpoint in workflow.runtime.endpoints.values():
        original = endpoint.handler

        async def capture(request, context, handler=original):
            grant = workflow.runtime.grants.load(context.grant_id)
            captures.append((context.actor, grant.remaining_depth))
            return await handler(request, context)

        endpoint.handler = capture
    result = await workflow.run("alice")
    assert result.status == "completed", result.error
    assert "verified content" in result.result["research"]
    assert captures == [
        ("agent:research", 2),
        ("agent:retrieval", 1),
        ("service:documents", 0),
    ]
    assert len(workflow.runners) == 2
    task = workflow.runtime.tasks.load(result.task_id)
    assert len(task.execution_ids) == 3
    children = [
        workflow.runtime.controller.get(identifier)
        for identifier in task.execution_ids[1:]
    ]
    assert children[0].parent_id == result.execution_id
    assert children[1].parent_id == children[0].execution_id


async def test_state_driven_pause_resume_after_coordinator(tmp_path):
    tokens, kid, issuer = await demo_tokens()
    kwargs = dict(
        tokens=tokens,
        kid=kid,
        issuer=issuer,
        model_factory=ScriptedDocumentModel,
        authorize=lambda subject, p: True,
        documents={"document:123": "content"},
        permission=Permission("documents:read", "document:123", "tenant"),
    )
    workflow = DelegatedResearchWorkflow.create(tmp_path, **kwargs)
    execution = workflow.start("alice")
    execution = await workflow.runtime.controller.advance(
        execution.execution_id
    )
    assert execution.status == "ready"
    assert execution.state["queue"][0][0] == "research"
    workflow.runtime.manager.pause(execution.task_id)
    restored = DelegatedResearchWorkflow.create(tmp_path, **kwargs)
    restored.restore(execution.execution_id)
    restored.runtime.manager.resume(execution.task_id)
    execution = await restored.runtime.controller.advance(
        execution.execution_id
    )
    assert execution.status == "completed", execution.error
