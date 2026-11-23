"""Issue task-bounded authority through interchangeable factors."""

import time
from dataclasses import replace
from typing import Literal
from uuid import uuid4

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.delegation import DelegationServiceBase
from swarmauri_core.delegation import DelegatedCredential, Grant
from swarmauri_core.delegation import IGrantStore
from swarmauri_core.permissions import IPermissionPolicy
from swarmauri_core.tasks import ITaskStore
from swarmauri_core.tokens import ITokenService


@ComponentBase.register_type(
    DelegationServiceBase, "AttenuatingDelegationService"
)
class AttenuatingDelegationService(DelegationServiceBase):
    """Validate live ancestry before issuance and resource admission.

    Methods are trusted broker operations. Hosts authenticate callers before
    supplying actor/holder identities. This class is not an OAuth endpoint.
    """

    type: Literal["AttenuatingDelegationService"] = (
        "AttenuatingDelegationService"
    )
    grants: IGrantStore = Field(exclude=True, repr=False)
    tasks: ITaskStore = Field(exclude=True, repr=False)
    policy: IPermissionPolicy = Field(exclude=True, repr=False)
    tokens: ITokenService = Field(exclude=True, repr=False)
    kid: str
    edges: frozenset[tuple[str, str]]
    algorithm: str = "RS256"
    issuer: str
    credential_lifetime: int = Field(default=120, gt=0)

    def _task(self, task_id):
        task = self.tasks.load(task_id)
        if task.status != "active" or task.expires_at <= int(time.time()):
            raise PermissionError("Task is inactive or expired")
        return task

    def root(self, task_id, holder, permissions, remaining_depth=3):
        task = self._task(task_id)
        permissions = self.policy.attenuate(task.permissions, permissions)
        grant = Grant(
            str(uuid4()),
            task_id,
            task.subject,
            holder,
            task.tenant,
            permissions,
            task.expires_at,
            remaining_depth,
        )
        self.grants.create(grant)
        return grant

    def validate(self, grant_id, holder, permission):
        grant = self.grants.load(grant_id)
        task = self._task(grant.task_id)
        if grant.holder != holder:
            raise PermissionError("Grant holder mismatch")
        seen = set()
        child = None
        current = grant
        while True:
            if current.grant_id in seen or len(seen) >= 64:
                raise PermissionError("Invalid grant ancestry")
            seen.add(current.grant_id)
            if (
                current.revoked
                or current.expires_at <= int(time.time())
                or current.task_id != task.task_id
                or current.subject != task.subject
                or current.tenant != task.tenant
                or current.expires_at > task.expires_at
            ):
                raise PermissionError("Grant is invalid or revoked")
            self.policy.attenuate(task.permissions, current.permissions)
            if child is not None:
                self.policy.attenuate(current.permissions, child.permissions)
                if (
                    child.expires_at > current.expires_at
                    or child.remaining_depth >= current.remaining_depth
                    or (current.holder, child.holder) not in self.edges
                ):
                    raise PermissionError("Invalid delegation ancestry")
            if current.parent_id is None:
                break
            child = current
            current = self.grants.load(current.parent_id)
        if not self.policy.authorize(grant.permissions, permission).allowed:
            raise PermissionError("Resource is outside the grant")
        return grant

    def delegate(self, parent_id, actor, recipient, permissions):
        if not permissions:
            raise PermissionError("Empty delegation")
        parent = self.validate(parent_id, actor, permissions[0])
        permissions = self.policy.attenuate(parent.permissions, permissions)
        if parent.remaining_depth == 0 or (actor, recipient) not in self.edges:
            raise PermissionError("Delegation edge or depth denied")
        grant = Grant(
            str(uuid4()),
            parent.task_id,
            parent.subject,
            recipient,
            parent.tenant,
            permissions,
            parent.expires_at,
            parent.remaining_depth - 1,
            parent.grant_id,
        )
        self.grants.create(grant)
        return grant

    def revoke(self, grant_id):
        grant = self.grants.load(grant_id)
        return self.grants.save(replace(grant, revoked=True))

    async def credential(self, grant_id, actor, audience, permission):
        grant = self.grants.load(grant_id)
        self.validate(grant_id, grant.holder, permission)
        expected = (
            self.grants.load(grant.parent_id).holder
            if grant.parent_id
            else grant.holder
        )
        if actor not in {grant.holder, expected}:
            raise PermissionError("Caller cannot present this grant")
        lifetime = min(
            self.credential_lifetime, grant.expires_at - int(time.time())
        )
        if lifetime <= 0:
            raise PermissionError("Grant expired")
        token = await self.tokens.mint(
            {
                "sub": grant.subject,
                "grant_id": grant.grant_id,
                "task_id": grant.task_id,
                "holder": grant.holder,
                "act": {"sub": actor},
            },
            alg=self.algorithm,
            kid=self.kid,
            issuer=self.issuer,
            audience=audience,
            lifetime_s=lifetime,
        )
        return DelegatedCredential(grant, token)

    async def verify(self, token, audience, permission):
        claims = await self.tokens.verify(
            token, issuer=self.issuer, audience=audience, leeway_s=0
        )
        required = {"sub", "grant_id", "task_id", "holder", "act", "exp"}
        if not required.issubset(claims):
            raise PermissionError("Missing credential claims")
        grant = self.validate(claims["grant_id"], claims["holder"], permission)
        if (
            claims["sub"] != grant.subject
            or claims["task_id"] != grant.task_id
            or claims["exp"] > grant.expires_at
        ):
            raise PermissionError("Credential and grant disagree")
        previous = (
            self.grants.load(grant.parent_id).holder
            if grant.parent_id
            else grant.holder
        )
        if claims["act"].get("sub") not in {grant.holder, previous}:
            raise PermissionError("Invalid credential actor")
        return grant
