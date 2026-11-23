import pytest
from swarmauri_core.permissions import Permission
from swarmauri_workflow_documentassistant import DocumentAssistantWorkflow
from swarmauri_workflow_documentassistant.demo import (
    ScriptedDocumentModel,
    demo_tokens,
)
from swarmauri_workflow_documentassistant.login import OIDCAdmission

pytestmark = pytest.mark.i9n


async def test_real_agent_tool_grants_and_restart(tmp_path):
    tokens, kid, issuer = await demo_tokens()
    kwargs = dict(
        tokens=tokens,
        kid=kid,
        issuer=issuer,
        model_factory=ScriptedDocumentModel,
        authorize=lambda subject, p: subject == "alice",
        documents={"document:123": "test content"},
        permission=Permission("documents:read", "document:123", "tenant"),
    )
    workflow = DocumentAssistantWorkflow.create(tmp_path, **kwargs)
    with pytest.raises(PermissionError):
        workflow.start("mallory")
    execution = workflow.start("alice")
    workflow.runtime.manager.pause(execution.task_id)
    assert (
        await workflow.runtime.controller.advance(execution.execution_id)
    ).status == "paused"
    restarted = DocumentAssistantWorkflow.create(tmp_path, **kwargs)
    restarted.restore(execution.execution_id)
    restarted.runtime.manager.resume(execution.task_id)
    for _ in range(5):
        execution = await restarted.runtime.controller.advance(
            execution.execution_id
        )
        if execution.status == "completed":
            break
    assert execution.status == "completed"
    assert "test content" in execution.result


async def test_login_binds_one_time_provider_state_to_browser():
    class LoginFixture:
        """Only the provider exchange is a test double."""

        async def auth_url(self):
            return {"url": "https://idp.test/login", "state": "signed-state"}

        async def exchange_and_identity(self, code, state):
            assert code == "code"
            return {"sub": "alice"}

    admission = OIDCAdmission(
        LoginFixture(), resolve_identity=lambda identity: identity["sub"]
    )
    payload, binding = await admission.begin()
    with pytest.raises(PermissionError):
        await admission.complete("code", payload["state"], "wrong-browser")
    assert (
        await admission.complete("code", payload["state"], binding) == "alice"
    )
    with pytest.raises(PermissionError):
        await admission.complete("code", payload["state"], binding)
