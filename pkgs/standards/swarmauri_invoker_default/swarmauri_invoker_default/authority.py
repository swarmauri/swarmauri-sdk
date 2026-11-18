"""Interchangeable standing-workload and delegated authority strategies."""

from dataclasses import asdict
from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.invocations import AuthorityStrategyBase
from swarmauri_core.delegation import IDelegationService
from swarmauri_core.permissions import IPermissionPolicy, Permission
from swarmauri_core.tokens import ITokenService


@ComponentBase.register_type(
    AuthorityStrategyBase, "DelegatedAuthorityStrategy"
)
class DelegatedAuthorityStrategy(AuthorityStrategyBase):
    """Narrow a task grant for the configured receiving workload."""

    type: Literal["DelegatedAuthorityStrategy"] = "DelegatedAuthorityStrategy"
    delegations: IDelegationService = Field(exclude=True, repr=False)
    recipient: str

    async def credential(self, request, context, audience):
        if context.task_id != request.task_id or not context.grant_id:
            raise PermissionError("A matching task grant is required")
        parent = self.delegations.validate(
            context.grant_id, context.actor, request.permission
        )
        if parent.task_id != request.task_id:
            raise PermissionError("Grant belongs to another task")
        child = self.delegations.delegate(
            parent.grant_id,
            context.actor,
            self.recipient,
            (request.permission,),
        )
        credential = await self.delegations.credential(
            child.grant_id, context.actor, audience, request.permission
        )
        return credential.token


@ComponentBase.register_type(
    AuthorityStrategyBase, "WorkloadAuthorityStrategy"
)
class WorkloadAuthorityStrategy(AuthorityStrategyBase):
    """Use standing service permissions without inheriting user authority."""

    type: Literal["WorkloadAuthorityStrategy"] = "WorkloadAuthorityStrategy"
    tokens: ITokenService = Field(exclude=True, repr=False)
    policy: IPermissionPolicy = Field(exclude=True, repr=False)
    permissions: dict[str, tuple[Permission, ...]]
    issuer: str
    kid: str
    algorithm: str = "RS256"

    async def credential(self, request, context, audience):
        available = self.permissions.get(context.actor, ())
        if not self.policy.authorize(available, request.permission).allowed:
            raise PermissionError("Workload permission denied")
        return await self.tokens.mint(
            {
                "sub": context.actor,
                "task_id": context.task_id,
                "permission": asdict(request.permission),
            },
            alg=self.algorithm,
            kid=self.kid,
            issuer=self.issuer,
            audience=audience,
            lifetime_s=120,
        )
