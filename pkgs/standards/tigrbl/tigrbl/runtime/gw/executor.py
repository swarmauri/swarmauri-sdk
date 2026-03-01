from __future__ import annotations

import json
from typing import Any

from .. import events as _events
from ..executor import _Ctx, _invoke
from ..kernel.core import Kernel
from ..kernel.atoms import _discover_atoms
from .raw import GwRawEnvelope


class RawEnvelopeExecutor:
    """Runtime ingress for ASGI3 raw envelopes."""

    def __init__(self, *, app: Any) -> None:
        self.app = app
        self._kernel = Kernel()
        self._route_atoms: list[tuple[str, Any]] | None = None

    def _routing_atoms(self) -> list[tuple[str, Any]]:
        if self._route_atoms is not None:
            return self._route_atoms
        order = {name: idx for idx, name in enumerate(_events.all_events_ordered())}
        atoms = []
        for anchor, run in _discover_atoms():
            if _events.phase_for_event(anchor) not in {
                "INGRESS_BEGIN",
                "INGRESS_PARSE",
                "INGRESS_ROUTE",
            }:
                continue
            atoms.append((anchor, run))
        atoms.sort(key=lambda item: order.get(item[0], 10_000))
        self._route_atoms = atoms
        return atoms

    async def invoke(self, env: GwRawEnvelope) -> None:
        scope_type = env.scope.get("type")

        if scope_type == "lifespan":
            await self._handle_lifespan(env)
            return

        if scope_type != "http":
            return

        await self._invoke_http(env)

    async def _invoke_http(self, env: GwRawEnvelope) -> None:
        plan = self._kernel.kernel_plan(self.app)
        ctx = _Ctx.ensure(request=None, db=None)
        ctx.app = self.app
        ctx.router = self.app
        ctx.raw = env
        ctx.kernel_plan = plan

        for _anchor, atom_run in self._routing_atoms():
            result = atom_run(None, ctx)
            if hasattr(result, "__await__"):
                await result

        route = ctx.temp.get("route", {}) if isinstance(ctx.temp, dict) else {}
        opmeta_index = route.get("opmeta_index")
        if not isinstance(opmeta_index, int) or not (
            0 <= opmeta_index < len(plan.opmeta)
        ):
            await self._send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return

        opmeta = plan.opmeta[opmeta_index]
        ctx.model = opmeta.model
        ctx.op = opmeta.alias
        ctx.opview = self._kernel.get_opview(self.app, opmeta.model, opmeta.alias)

        selected = dict(plan.phase_chains.get(opmeta_index, {}))
        selected["INGRESS_BEGIN"] = []
        selected["INGRESS_PARSE"] = []
        selected["INGRESS_ROUTE"] = []

        await _invoke(request=None, db=None, phases=selected, ctx=ctx)

        egress = ctx.temp.get("egress", {}) if isinstance(ctx.temp, dict) else {}
        response = (
            egress.get("transport_response") if isinstance(egress, dict) else None
        )
        if isinstance(response, dict):
            await self._send_transport_response(env, response)
            return

        status = int(getattr(ctx, "status_code", 200) or 200)
        body = getattr(ctx, "result", None)
        await self._send_json(env, status, body)

    async def _send_transport_response(
        self, env: GwRawEnvelope, response: dict[str, Any]
    ) -> None:
        status = int(response.get("status_code", 200) or 200)
        headers_obj = response.get("headers")
        headers: list[tuple[bytes, bytes]] = []
        if isinstance(headers_obj, dict):
            headers = [
                (str(k).encode("latin-1"), str(v).encode("latin-1"))
                for k, v in headers_obj.items()
            ]
        body = response.get("body", b"")
        if isinstance(body, str):
            body = body.encode("utf-8")
        elif body is None:
            body = b""
        elif not isinstance(body, (bytes, bytearray)):
            body = json.dumps(body).encode("utf-8")

        await env.send(
            {"type": "http.response.start", "status": status, "headers": headers}
        )
        await env.send(
            {"type": "http.response.body", "body": bytes(body), "more_body": False}
        )

    async def _send_json(self, env: GwRawEnvelope, status: int, payload: Any) -> None:
        await env.send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await env.send(
            {
                "type": "http.response.body",
                "body": json.dumps(payload).encode("utf-8"),
                "more_body": False,
            }
        )

    async def _handle_lifespan(self, env: GwRawEnvelope) -> None:
        while True:
            message = await env.receive()
            message_type = message.get("type")
            if message_type == "lifespan.startup":
                await self.app.run_event_handlers("startup")
                await env.send({"type": "lifespan.startup.complete"})
                continue
            if message_type == "lifespan.shutdown":
                await self.app.run_event_handlers("shutdown")
                await env.send({"type": "lifespan.shutdown.complete"})
            return
