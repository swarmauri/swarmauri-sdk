"""Deliver authenticated task admission and a real tool-agent execution."""

import asyncio
import time
from typing import Any, Callable, Literal
from uuid import uuid4

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.workflows import WorkflowDefinitionBase
from swarmauri_core.invocations import (
    EdgeAuthorizationBinding,
    InvocationContext,
    InvocationRequest,
)
from swarmauri_core.permissions import Permission
from swarmauri_core.workflows import (
    GraphDefinition,
    NodeDefinition,
    EdgeDefinition,
)
from swarmauri_agent_runner import AgentRunner, AgentRunnerExecutionDriver

from .composition import create_runtime
from .tools import AuthorizedDocumentTool


@ComponentBase.register_type(
    WorkflowDefinitionBase, "DocumentAssistantWorkflow"
)
class DocumentAssistantWorkflow(WorkflowDefinitionBase):
    """Compose injected identity, model, authorization and execution factors.

    authorize(subject, permission) is the host's resource authorization hook.
    A verified IdP identity alone does not grant access to a document.
    """

    type: Literal["DocumentAssistantWorkflow"] = "DocumentAssistantWorkflow"
    runtime: Any = Field(exclude=True, repr=False)
    model_factory: Callable = Field(exclude=True, repr=False)
    authorize: Callable = Field(exclude=True, repr=False)
    documents: dict[str, str] = Field(exclude=True, repr=False)
    permission: Permission
    runners: dict[str, Any] = Field(default_factory=dict, exclude=True)
    execution_ids: dict[str, str] = Field(default_factory=dict, exclude=True)

    @classmethod
    def create(
        cls,
        directory,
        *,
        tokens,
        kid,
        issuer,
        model_factory,
        authorize,
        documents,
        permission,
        http_client=None,
        runtime_factory=create_runtime,
        runtime_options=None,
    ):
        edge = EdgeAuthorizationBinding(
            "assistant-to-documents",
            "agent:assistant",
            "documents",
            "read",
            (permission,),
        )
        runtime = runtime_factory(
            directory,
            tokens=tokens,
            kid=kid,
            issuer=issuer,
            edges={edge.edge_id: edge},
            recipients={"documents": "service:documents"},
            http_client=http_client,
            **(runtime_options or {}),
        )
        workflow = cls(
            runtime=runtime,
            model_factory=model_factory,
            authorize=authorize,
            documents=documents,
            permission=permission,
        )

        async def read(request, context):
            return workflow.documents[request.permission.resource]

        runtime.endpoint("documents", "service:documents", read)
        return workflow

    def definition(self):
        return GraphDefinition(
            "document-assistant",
            "1",
            (
                NodeDefinition("assistant", "assistant"),
                NodeDefinition("documents", "documents"),
            ),
            (
                EdgeDefinition(
                    "assistant-to-documents", "assistant", "documents"
                ),
            ),
        )

    def bind_runner(self, task_id, grant_id, resource, actor, edge_id):
        """Reconstruct a driver after restart using durable run checkpoints."""
        context = InvocationContext(actor, task_id, grant_id)
        loop = asyncio.get_running_loop()

        def invoke(requested_resource):
            permission = Permission(
                "documents:read", requested_resource, self.permission.tenant
            )
            request = InvocationRequest(
                str(uuid4()),
                edge_id,
                task_id,
                "read",
                permission,
                {"resource": requested_resource},
            )
            future = asyncio.run_coroutine_threadsafe(
                self.runtime.invoker.invoke(
                    request,
                    InvocationContext(
                        context.actor,
                        context.task_id,
                        context.grant_id,
                        self.execution_ids.get(driver_id),
                    ),
                ),
                loop,
            )
            return future.result(timeout=30).value

        runner = AgentRunner(
            self.model_factory(resource),
            self.runtime.checkpoints,
            tools={"ReadDocument": AuthorizedDocumentTool(callback=invoke)},
        )
        driver_id = f"assistant:{task_id}:{actor}"
        self.runtime.controller.drivers[driver_id] = (
            AgentRunnerExecutionDriver(
                runner=runner,
                before_step=lambda snapshot: self.execution_ids.__setitem__(
                    driver_id, snapshot.execution_id
                ),
            )
        )
        self.runners[driver_id] = runner
        return driver_id

    def start(self, subject, *, lifetime=600):
        """Admit a host-authenticated subject after resource authorization."""
        if lifetime <= 0 or not self.authorize(subject, self.permission):
            raise PermissionError("User cannot start this document task")
        task = self.runtime.manager.start(
            subject,
            self.permission.tenant,
            (self.permission,),
            int(time.time()) + lifetime,
        )
        root = self.runtime.delegations.root(
            task.task_id, "agent:assistant", (self.permission,), 1
        )
        driver = self.bind_runner(
            task.task_id,
            root.grant_id,
            self.permission.resource,
            "agent:assistant",
            "assistant-to-documents",
        )
        return self.runtime.controller.start(
            task.task_id,
            driver,
            {
                "prompt": self.permission.resource,
                "grant_id": root.grant_id,
                "resource": self.permission.resource,
            },
        )

    def restore(self, execution_id):
        snapshot = self.runtime.controller.get(execution_id)
        self.bind_runner(
            snapshot.task_id,
            snapshot.state["grant_id"],
            snapshot.state["resource"],
            "agent:assistant",
            "assistant-to-documents",
        )
        return snapshot

    async def run(self, subject):
        snapshot = self.start(subject)
        for _ in range(100):
            snapshot = await self.runtime.controller.advance(
                snapshot.execution_id
            )
            if snapshot.status not in {"ready", "running"}:
                return snapshot
        raise RuntimeError("Reference execution step limit reached")
