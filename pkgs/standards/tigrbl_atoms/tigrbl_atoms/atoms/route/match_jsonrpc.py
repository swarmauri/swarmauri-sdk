from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Routed
from ...types import Atom, Ctx, RoutedCtx

ANCHOR = _ev.ROUTE_MATCH_JSONRPC


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, 'temp', None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, 'temp', temp)
    route = temp.setdefault('route', {})
    if not isinstance(route, dict):
        route = {}
        temp['route'] = route
    candidates = route.get('protocol_candidates')
    if isinstance(candidates, list):
        route['jsonrpc_candidates'] = [p for p in candidates if isinstance(p, str) and p.endswith('.jsonrpc')]


class AtomImpl(Atom[Routed, Routed]):
    name = 'route.match_jsonrpc'
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Routed]) -> Ctx[Routed]:
        _run(obj, ctx)
        return ctx.promote(RoutedCtx, protocol=str(ctx.temp.get('route', {}).get('protocol', '') or ''))


INSTANCE = AtomImpl()
