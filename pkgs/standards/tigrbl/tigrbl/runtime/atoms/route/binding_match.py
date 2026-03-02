from __future__ import annotations

import re
from typing import Any, Mapping

from ... import events as _ev

ANCHOR = _ev.ROUTE_BINDING_MATCH
_PATH_PARAM_RE = re.compile(r"\{([^{}]+)\}")


def _match_rest_index(index: Any, method: str, path: str) -> tuple[int, dict[str, str]]:
    if callable(index):
        return index(method, path)

    match = getattr(index, "match", None)
    if callable(match):
        return match(method, path)

    if not isinstance(index, Mapping):
        raise KeyError(f"{method.upper()} {path}")

    selector = f"{method.upper()} {path}"
    exact = index.get(selector)
    if isinstance(exact, int):
        return exact, {}

    for candidate, meta_index in index.items():
        if not (isinstance(candidate, str) and isinstance(meta_index, int)):
            continue
        route_method, sep, route_path = candidate.partition(" ")
        if not sep or route_method.upper() != method.upper():
            continue

        names: list[str] = []

        def _replace(match_obj: re.Match[str]) -> str:
            names.append(match_obj.group(1))
            return rf"(?P<{names[-1]}>[^/]+)"

        pattern = "^" + _PATH_PARAM_RE.sub(_replace, route_path) + "$"
        matched = re.match(pattern, path)
        if matched:
            return meta_index, {k: str(v) for k, v in matched.groupdict().items()}

    raise KeyError(selector)


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})

    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    proto = route.get("protocol") or getattr(ctx, "proto", None)
    if not isinstance(proto, str):
        return

    proto_indices = getattr(plan, "proto_indices", None)
    if not isinstance(proto_indices, dict):
        route.setdefault("binding", getattr(ctx, "binding", None))
        return

    selector = None
    if proto.endswith(".rest"):
        env = getattr(ctx, "gw_raw", None)
        method = getattr(env, "method", None)
        path = getattr(env, "path", None)
        if isinstance(method, str) and isinstance(path, str):
            candidates = [proto]
            if proto == "http.rest":
                candidates.append("https.rest")
            elif proto == "https.rest":
                candidates.append("http.rest")

            for candidate in candidates:
                index = proto_indices.get(candidate)
                if index is None:
                    continue
                try:
                    binding, path_params = _match_rest_index(index, method, path)
                except KeyError:
                    continue
                route["binding"] = binding
                if path_params:
                    route["path_params"] = path_params
                return
    elif proto.endswith(".jsonrpc"):
        selector = route.get("rpc_method")

    if isinstance(selector, str):
        index = proto_indices.get(proto)
        if isinstance(index, dict):
            route["binding"] = index.get(selector)
