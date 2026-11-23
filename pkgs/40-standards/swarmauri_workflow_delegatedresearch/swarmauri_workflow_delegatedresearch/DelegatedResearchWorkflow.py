"""Deliver three delegated hops with real Swarmauri agent runners."""

import time
from typing import Literal
from uuid import uuid4

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.workflows import WorkflowDefinitionBase
from swarmauri_core.invocations import (
    EdgeAuthorizationBinding,
    InvocationContext,
    InvocationRequest,
)
from swarmauri_core.workflows import (
    GraphDefinition,
    NodeDefinition,
    EdgeDefinition,
)
from swarmauri_workflow_statedriven import StateDrivenExecutionDriver
from swarmauri_workflow_documentassistant import DocumentAssistantWorkflow
from swarmauri_workflow_documentassistant.composition import create_runtime

from .definition import research_graph


@ComponentBase.register_type(
    WorkflowDefinitionBase, "DelegatedResearchWorkflow"
)
class DelegatedResearchWorkflow(DocumentAssistantWorkflow):
    """Coordinate research and retrieval with host-managed credentials."""

    type: Literal["DelegatedResearchWorkflow"] = "DelegatedResearchWorkflow"

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
        definitions = [
            ("coordinator-to-research", "agent:coordinator", "research"),
            ("research-to-retrieval", "agent:research", "retrieval"),
            ("retrieval-to-documents", "agent:retrieval", "documents"),
        ]
        edges = {
            name: EdgeAuthorizationBinding(
                name, actor, service, "read", (permission,)
            )
            for name, actor, service in definitions
        }
        runtime = runtime_factory(
            directory,
            tokens=tokens,
            kid=kid,
            issuer=issuer,
            edges=edges,
            recipients={
                "research": "agent:research",
                "retrieval": "agent:retrieval",
                "documents": "service:documents",
            },
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

        async def research(request, context):
            return await workflow.run_child(
                request, context, "research-to-retrieval"
            )

        async def retrieval(request, context):
            return await workflow.run_child(
                request, context, "retrieval-to-documents"
            )

        runtime.endpoint("documents", "service:documents", read)
        runtime.endpoint("retrieval", "agent:retrieval", retrieval)
        runtime.endpoint("research", "agent:research", research)
        return workflow

    def definition(self):
        return GraphDefinition(
            "delegated-research",
            "1",
            tuple(
                NodeDefinition(name, name)
                for name in (
                    "coordinator",
                    "research",
                    "retrieval",
                    "documents",
                )
            ),
            tuple(
                EdgeDefinition(name, source, target)
                for name, source, target in (
                    ("coordinator-to-research", "coordinator", "research"),
                    ("research-to-retrieval", "research", "retrieval"),
                    ("retrieval-to-documents", "retrieval", "documents"),
                )
            ),
        )

    async def run_child(self, request, context, edge):
        driver = self.bind_runner(
            context.task_id,
            context.grant_id,
            request.permission.resource,
            context.actor,
            edge,
        )
        snapshot = self.runtime.controller.start(
            context.task_id,
            driver,
            {
                "prompt": request.permission.resource,
                "grant_id": context.grant_id,
                "resource": request.permission.resource,
            },
            parent_id=context.execution_id,
        )
        for _ in range(100):
            snapshot = await self.runtime.controller.advance(
                snapshot.execution_id
            )
            if snapshot.status == "completed":
                return snapshot.result
            if snapshot.status != "ready":
                raise RuntimeError("Child execution did not complete")
        raise RuntimeError("Child execution step limit reached")

    def bind_workflow(self, task_id, grant_id):
        async def dispatch(name, data, snapshot):
            if name == "coordinator":
                return snapshot.state["resource"]
            request = InvocationRequest(
                str(uuid4()),
                "coordinator-to-research",
                task_id,
                "read",
                self.permission,
                {"resource": snapshot.state["resource"]},
            )
            result = await self.runtime.invoker.invoke(
                request,
                InvocationContext(
                    "agent:coordinator",
                    task_id,
                    grant_id,
                    snapshot.execution_id,
                ),
            )
            return result.value

        driver_id = f"workflow:{task_id}"
        self.runtime.controller.drivers[driver_id] = (
            StateDrivenExecutionDriver(
                graph=research_graph(),
                definition_version="1",
                dispatcher=dispatch,
            )
        )
        return driver_id

    def start(self, subject, *, lifetime=600):
        if lifetime <= 0 or not self.authorize(subject, self.permission):
            raise PermissionError("User cannot start this research task")
        task = self.runtime.manager.start(
            subject,
            self.permission.tenant,
            (self.permission,),
            int(time.time()) + lifetime,
        )
        root = self.runtime.delegations.root(
            task.task_id, "agent:coordinator", (self.permission,), 3
        )
        driver = self.bind_workflow(task.task_id, root.grant_id)
        return self.runtime.controller.start(
            task.task_id,
            driver,
            {
                "start": "coordinator",
                "input": self.permission.resource,
                "grant_id": root.grant_id,
                "resource": self.permission.resource,
            },
        )

    def restore(self, execution_id):
        snapshot = self.runtime.controller.get(execution_id)
        self.bind_workflow(snapshot.task_id, snapshot.state["grant_id"])
        return snapshot
