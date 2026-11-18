"""Receiving authorization and durable duplicate handling for invocations."""

import hashlib
import json
import time
from dataclasses import asdict
from typing import Callable

from swarmauri_core.invocations import InvocationContext, InvocationResult
from swarmauri_core.run_stores import RunCheckpoint, RunConflictError
from swarmauri_core.transports.i_appserver import HttpApp

from .codec import (
    decode_request,
    encode_request,
    encode_result,
)


class InvocationEndpoint(HttpApp):
    """Admit local/HTTP requests before invoking a host-bound handler.

    Handlers receive trusted context separately from model-visible arguments.
    Completed retries return a saved result. Uncertain in-flight requests are
    rejected instead of repeating an external side effect.
    """

    def __init__(
        self,
        *,
        service,
        audience,
        edges,
        tokens,
        issuer,
        tasks,
        policy,
        checkpoints,
        handler: Callable,
        delegations=None,
    ):
        self.service = service
        self.audience = audience
        self.edges = edges
        self.tokens = tokens
        self.issuer = issuer
        self.tasks = tasks
        self.policy = policy
        self.checkpoints = checkpoints
        self.handler = handler
        self.delegations = delegations

    async def invoke(self, request, token):
        edge = self.edges[request.edge_id]
        if (
            edge.operation != request.operation
            or request.arguments.get("resource") != request.permission.resource
            or not self.policy.authorize(
                edge.permissions, request.permission
            ).allowed
        ):
            raise PermissionError("Invocation binding mismatch")
        task = self.tasks.load(request.task_id)
        if (
            task.status != "active"
            or task.expires_at <= int(time.time())
            or task.tenant != request.permission.tenant
        ):
            raise PermissionError("Task is inactive or expired")
        claims = await self.tokens.verify(
            token, issuer=self.issuer, audience=self.audience, leeway_s=0
        )
        if not {"sub", "exp", "task_id"}.issubset(claims):
            raise PermissionError("Required token claims are missing")
        if claims["task_id"] != request.task_id:
            raise PermissionError("Token belongs to another task")
        if edge.delegated:
            if self.delegations is None:
                raise PermissionError("Delegation is not configured")
            grant = await self.delegations.verify(
                token, self.audience, request.permission
            )
            if (
                grant.holder != self.service
                or claims.get("act", {}).get("sub") != edge.caller
            ):
                raise PermissionError("Delegated recipient/caller mismatch")
            context = InvocationContext(
                self.service,
                request.task_id,
                grant.grant_id,
                request.parent_execution_id,
            )
        else:
            if claims["sub"] != edge.caller or claims.get(
                "permission"
            ) != asdict(request.permission):
                raise PermissionError("Workload credential mismatch")
            context = InvocationContext(
                self.service,
                request.task_id,
                execution_id=request.parent_execution_id,
            )
        key = f"invocation:{self.service}:{request.invocation_id}"
        digest = hashlib.sha256(
            encode_request(request) + edge.caller.encode()
        ).hexdigest()
        record = {"digest": digest, "status": "dispatching"}
        try:
            self.checkpoints.create(RunCheckpoint(key, 0, json.dumps(record)))
        except RunConflictError:
            saved = json.loads(self.checkpoints.load(key).payload)
            if saved["digest"] != digest:
                raise PermissionError("Invocation ID was reused")
            if saved["status"] != "completed":
                raise RuntimeError(
                    "Invocation outcome requires reconciliation"
                )
            return InvocationResult(request.invocation_id, saved["value"])
        try:
            value = await self.handler(request, context)
            payload = json.dumps(
                {**record, "status": "completed", "value": value}
            )
        except BaseException:
            self.checkpoints.save(
                RunCheckpoint(
                    key, 0, json.dumps({**record, "status": "failed"})
                )
            )
            raise
        self.checkpoints.save(RunCheckpoint(key, 0, payload))
        return InvocationResult(request.invocation_id, value)

    async def __call__(self, method, path, headers, body):
        if method != "POST" or path != "/invocations":
            return 404, {}, b""
        try:
            if len(body) > 1_048_576:
                raise ValueError("Request is too large")
            normalized = {k.lower(): v for k, v in headers.items()}
            authorization = normalized.get("authorization", "")
            if not authorization.startswith("Bearer "):
                raise PermissionError("Missing credential")
            result = await self.invoke(
                decode_request(body), authorization.removeprefix("Bearer ")
            )
            return (
                200,
                {"content-type": "application/json"},
                encode_result(result),
            )
        except PermissionError:
            return 403, {}, b""
        except (ValueError, KeyError, TypeError):
            return 400, {}, b""
        except Exception:
            return 500, {}, b""

    async def asgi(self, scope, receive, send):
        """Adapt HttpApp explicitly to ASGI; transport still hosts the app."""
        if scope["type"] != "http":
            raise ValueError("Only HTTP scopes are supported")
        body = bytearray()
        while True:
            event = await receive()
            if event["type"] == "http.disconnect":
                return
            body.extend(event.get("body", b""))
            if len(body) > 1_048_576:
                await send(
                    {
                        "type": "http.response.start",
                        "status": 413,
                        "headers": [],
                    }
                )
                await send({"type": "http.response.body", "body": b""})
                return
            if not event.get("more_body"):
                break
        status, headers, response = await self(
            scope["method"],
            scope["path"],
            {
                k.decode("latin1"): v.decode("latin1")
                for k, v in scope["headers"]
            },
            bytes(body),
        )
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (k.encode(), v.encode()) for k, v in headers.items()
                ],
            }
        )
        await send({"type": "http.response.body", "body": response})
