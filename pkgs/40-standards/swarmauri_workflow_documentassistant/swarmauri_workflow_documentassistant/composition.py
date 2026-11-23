"""Wire existing factors into an injectable reference runtime."""

from dataclasses import dataclass, field
from pathlib import Path

from swarmauri_standard.service_registries.ServiceRegistry import (
    ServiceRegistry,
)
from swarmauri_runstore_sqlite import SqliteRunStore
from swarmauri_execution_default import DefaultExecutionController
from swarmauri_taskmanager_default import DefaultTaskManager
from swarmauri_taskstore_sqlite import SqliteTaskStore
from swarmauri_grantstore_sqlite import SqliteGrantStore
from swarmauri_permission_explicit import ExplicitPermissionPolicy
from swarmauri_delegation_attenuating import AttenuatingDelegationService
from swarmauri_invoker_default import (
    DefaultInvoker,
    DelegatedAuthorityStrategy,
    InvocationEndpoint,
)


@dataclass
class ReferenceRuntime:
    """Keep infrastructure dependencies explicit and replaceable."""

    tasks: object
    grants: object
    checkpoints: object
    policy: object
    delegations: object
    controller: object
    manager: object
    services: object
    invoker: object
    tokens: object
    issuer: str
    endpoints: dict
    edges: dict
    events: list[dict] = field(default_factory=list)

    def endpoint(self, name, subject, handler):
        """Install the same receiving application used by HTTP delivery."""

        async def admitted(request, context):
            grant = (
                self.grants.load(context.grant_id)
                if context.grant_id
                else None
            )
            self.events.append(
                {
                    "invocation_id": request.invocation_id,
                    "task_id": context.task_id,
                    "recipient": context.actor,
                    "resource": request.permission.resource,
                    "remaining_depth": (
                        grant.remaining_depth if grant is not None else None
                    ),
                }
            )
            return await handler(request, context)

        endpoint = InvocationEndpoint(
            service=subject,
            audience=subject,
            edges={k: v for k, v in self.edges.items() if v.service == name},
            tokens=self.tokens,
            issuer=self.issuer,
            tasks=self.tasks,
            policy=self.policy,
            checkpoints=self.checkpoints,
            handler=admitted,
            delegations=self.delegations,
        )
        self.endpoints[name] = endpoint
        self.services.register_service(
            name,
            {
                "subject": subject,
                "audience": subject,
                "endpoint": name,
                "protocol": "local",
            },
        )
        return endpoint


def create_runtime(
    directory,
    *,
    tokens,
    kid,
    issuer,
    edges,
    recipients,
    http_client=None,
    algorithm="RS256",
    tasks=None,
    grants=None,
    checkpoints=None,
    policy=None,
    services=None,
    delegations=None,
):
    """Use SQLite, service discovery, token services and existing HTTP I/O."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    tasks = (
        tasks
        if tasks is not None
        else SqliteTaskStore(path=directory / "tasks.db")
    )
    grants = (
        grants
        if grants is not None
        else SqliteGrantStore(path=directory / "grants.db")
    )
    checkpoints = (
        checkpoints
        if checkpoints is not None
        else SqliteRunStore(path=directory / "runs.db")
    )
    policy = policy if policy is not None else ExplicitPermissionPolicy()
    delegations = (
        delegations
        if delegations is not None
        else AttenuatingDelegationService(
            grants=grants,
            tasks=tasks,
            policy=policy,
            tokens=tokens,
            kid=kid,
            issuer=issuer,
            algorithm=algorithm,
            edges=frozenset(
                (edge.caller, recipients[edge.service])
                for edge in edges.values()
            ),
        )
    )
    controller = DefaultExecutionController(
        checkpoints=checkpoints, tasks=tasks, drivers={}
    )
    manager = DefaultTaskManager(store=tasks, executions=controller)
    services = services if services is not None else ServiceRegistry()
    endpoints = {}
    authorities = {
        key: DelegatedAuthorityStrategy(
            delegations=delegations, recipient=recipients[edge.service]
        )
        for key, edge in edges.items()
    }
    invoker = DefaultInvoker(
        services=services,
        policy=policy,
        edges=edges,
        authorities=authorities,
        http_client=http_client,
        local_endpoints=endpoints,
    )
    # Pydantic copies mappings during validation. Expose the actual mapping.
    endpoints = invoker.local_endpoints
    return ReferenceRuntime(
        tasks,
        grants,
        checkpoints,
        policy,
        delegations,
        controller,
        manager,
        services,
        invoker,
        tokens,
        issuer,
        endpoints,
        edges,
    )
