"""Invocation orchestration over existing service and transport contracts."""

from typing import Any, Literal
from dataclasses import replace
from urllib.parse import urlsplit

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.invocations import InvokerBase
from swarmauri_core.invocations import (
    EdgeAuthorizationBinding,
    IAuthorityStrategy,
)
from swarmauri_core.permissions import IPermissionPolicy
from swarmauri_core.service_registries.IServiceRegistry import IServiceRegistry
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_core.workflows import ServiceBinding

from .codec import (
    decode_request,
    decode_result,
    encode_request,
    encode_result,
)


@ComponentBase.register_type(InvokerBase, "DefaultInvoker")
class DefaultInvoker(InvokerBase):
    """Authorize configured edges and reuse HTTP or local delivery.

    InvocationContext is host-established, never an LLM tool argument.
    """

    type: Literal["DefaultInvoker"] = "DefaultInvoker"
    services: IServiceRegistry = Field(exclude=True, repr=False)
    policy: IPermissionPolicy = Field(exclude=True, repr=False)
    edges: dict[str, EdgeAuthorizationBinding]
    authorities: dict[str, IAuthorityStrategy] = Field(
        exclude=True, repr=False
    )
    http_client: IHttpClient | None = Field(default=None, exclude=True)
    local_endpoints: dict[str, Any] = Field(
        default_factory=dict, exclude=True, repr=False
    )
    timeout: float = Field(default=30, gt=0)

    async def invoke(self, request, context):
        request = replace(request, parent_execution_id=context.execution_id)
        edge = self.edges[request.edge_id]
        if (
            edge.caller != context.actor
            or edge.operation != request.operation
            or context.task_id != request.task_id
            or request.arguments.get("resource") != request.permission.resource
            or not self.policy.authorize(
                edge.permissions, request.permission
            ).allowed
        ):
            raise PermissionError("Invocation is outside the edge policy")
        details = self.services.get_service(edge.service)
        if details is None:
            raise KeyError(edge.service)
        service = ServiceBinding(
            service=edge.service,
            subject=details["subject"],
            audience=details["audience"],
            endpoint=details["endpoint"],
            protocol=details.get("protocol", "local"),
        )
        token = await self.authorities[edge.edge_id].credential(
            request, context, service.audience
        )
        body = encode_request(request)
        if service.protocol == "local":
            # Use the same codec and receiver checks for both delivery paths.
            result = await self.local_endpoints[service.endpoint].invoke(
                decode_request(body), token
            )
            return decode_result(encode_result(result), request.invocation_id)
        url = urlsplit(service.endpoint)
        if url.scheme != "https" and not (
            url.scheme == "http"
            and url.hostname in {"127.0.0.1", "localhost", "::1"}
        ):
            raise ValueError("Remote invocation requires HTTPS")
        if self.http_client is None:
            raise ValueError("Configure an existing IHttpClient")
        response = await self.http_client.arequest(
            "POST",
            service.endpoint,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            body=body,
            timeout=self.timeout,
        )
        if response.status_code == 403:
            raise PermissionError("Remote invocation denied")
        if response.status_code != 200:
            raise RuntimeError("Remote invocation failed")
        return decode_result(response.read(), request.invocation_id)
