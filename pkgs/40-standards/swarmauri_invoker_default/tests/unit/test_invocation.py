from dataclasses import replace
from uuid import uuid4

import httpx
import pytest
from swarmauri_core.invocations import InvocationContext, InvocationRequest
from swarmauri_core.permissions import Permission
from swarmauri_transport_httpx import HttpxClient
from swarmauri_workflow_documentassistant import DocumentAssistantWorkflow
from swarmauri_workflow_documentassistant.demo import (
    ScriptedDocumentModel,
    demo_tokens,
)

pytestmark = pytest.mark.unit


async def setup_workflow(tmp_path):
    tokens, kid, issuer = await demo_tokens()
    permission = Permission("documents:read", "document:123", "tenant")
    workflow = DocumentAssistantWorkflow.create(
        tmp_path,
        tokens=tokens,
        kid=kid,
        issuer=issuer,
        model_factory=ScriptedDocumentModel,
        authorize=lambda subject, p: subject == "alice",
        documents={"document:123": "allowed", "document:456": "secret"},
        permission=permission,
    )
    execution = workflow.start("alice")
    context = InvocationContext(
        "agent:assistant", execution.task_id, execution.state["grant_id"]
    )
    request = InvocationRequest(
        str(uuid4()),
        "assistant-to-documents",
        execution.task_id,
        "read",
        permission,
        {"resource": "document:123"},
    )
    return workflow, request, context


async def test_local_and_real_http_contract_share_idempotency(tmp_path):
    workflow, request, context = await setup_workflow(tmp_path)
    endpoint = workflow.runtime.endpoints["documents"]
    calls = []
    handler = endpoint.handler

    async def counted(req, ctx):
        calls.append(req.invocation_id)
        return await handler(req, ctx)

    endpoint.handler = counted
    local = await workflow.runtime.invoker.invoke(request, context)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=endpoint.asgi)
    ) as client:
        workflow.runtime.invoker.http_client = HttpxClient(async_client=client)
        workflow.runtime.services.update_service(
            "documents",
            {
                "protocol": "http",
                "endpoint": "http://localhost/invocations",
            },
        )
        remote = await workflow.runtime.invoker.invoke(request, context)
    assert remote == local
    assert remote.value == "allowed"
    assert calls == [request.invocation_id]


async def test_resource_arguments_cannot_bypass_permission(tmp_path):
    workflow, request, context = await setup_workflow(tmp_path)
    with pytest.raises(PermissionError):
        await workflow.runtime.invoker.invoke(
            replace(request, arguments={"resource": "document:456"}), context
        )
    with pytest.raises(PermissionError):
        await workflow.runtime.invoker.invoke(
            request, replace(context, actor="attacker")
        )
    endpoint = workflow.runtime.endpoints["documents"]
    assert (await endpoint("POST", "/invocations", {}, b"{}"))[0] == 403


async def test_receiver_rechecks_revocation_before_cached_result(tmp_path):
    workflow, request, context = await setup_workflow(tmp_path)
    edge = request.edge_id
    token = await workflow.runtime.invoker.authorities[edge].credential(
        request, context, "service:documents"
    )
    endpoint = workflow.runtime.endpoints["documents"]
    assert (await endpoint.invoke(request, token)).value == "allowed"
    workflow.runtime.delegations.revoke(context.grant_id)
    with pytest.raises(PermissionError):
        await endpoint.invoke(request, token)


async def test_uncertain_side_effect_is_not_repeated(tmp_path):
    workflow, request, context = await setup_workflow(tmp_path)
    endpoint = workflow.runtime.endpoints["documents"]
    calls = []

    async def failing(req, ctx):
        calls.append(req.invocation_id)
        raise RuntimeError("Effect outcome unknown")

    endpoint.handler = failing
    with pytest.raises(RuntimeError):
        await workflow.runtime.invoker.invoke(request, context)
    with pytest.raises(RuntimeError, match="reconciliation"):
        await workflow.runtime.invoker.invoke(request, context)
    assert calls == [request.invocation_id]


async def test_standing_workload_authority_is_interchangeable(tmp_path):
    from swarmauri_invoker_default import WorkloadAuthorityStrategy

    workflow, request, context = await setup_workflow(tmp_path)
    runtime = workflow.runtime
    edge = replace(runtime.edges[request.edge_id], delegated=False)
    runtime.invoker.edges[edge.edge_id] = edge
    runtime.endpoints["documents"].edges[edge.edge_id] = edge
    runtime.invoker.authorities[edge.edge_id] = WorkloadAuthorityStrategy(
        tokens=runtime.tokens,
        policy=runtime.policy,
        permissions={"agent:assistant": (request.permission,)},
        issuer=runtime.issuer,
        kid=runtime.delegations.kid,
    )
    result = await runtime.invoker.invoke(
        request, replace(context, grant_id=None)
    )
    assert result.value == "allowed"
    runtime.invoker.authorities[edge.edge_id].permissions = {}
    with pytest.raises(PermissionError):
        await runtime.invoker.invoke(request, context)
