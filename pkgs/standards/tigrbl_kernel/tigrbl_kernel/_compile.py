from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping

from tigrbl_runtime.hook_types import StepFn

from . import events as _ev
from .models import KernelPlan, OpKey, OpMeta, OpView
from .opview_compiler import compile_opview_from_specs
from .types import DEFAULT_PHASE_ORDER as _DEFAULT_PHASE_ORDER
from .utils import (
    _canonicalize_app,
    _compile_path_pattern,
    _opspecs,
    _phase_info_map,
    _route_payload_template,
    _table_iter,
    deepmerge_phase_chains,
)


DEFAULT_PHASE_ORDER = tuple(getattr(_ev, "PHASES", ())) or _DEFAULT_PHASE_ORDER


def _compile_opview_from_specs(self: Any, specs: Mapping[str, Any], sp: Any) -> OpView:
    return compile_opview_from_specs(specs, sp)


def _compile_plan(self: Any, app: Any) -> KernelPlan:
    app = _canonicalize_app(app)

    from tigrbl_core._spec.binding_spec import (
        HttpJsonRpcBindingSpec,
        HttpRestBindingSpec,
        WsBindingSpec,
    )

    route_data: dict[str, Any] = _route_payload_template()
    opmeta: list[OpMeta] = []
    opkey_to_meta: dict[OpKey, int] = {}
    phase_chains: dict[int, Mapping[str, list[StepFn]]] = {}
    ingress_chain = self._build_ingress(app)
    egress_chain = self._build_egress(app)
    phases, mainline_phases, error_phases = _phase_info_map(DEFAULT_PHASE_ORDER)

    for model in _table_iter(app):
        for sp in _opspecs(model):
            meta_index = len(opmeta)
            target = (getattr(sp, "target", sp.alias) or sp.alias).lower()
            opmeta.append(OpMeta(model=model, alias=sp.alias, target=target))
            phase_chains[meta_index] = deepmerge_phase_chains(
                ingress_chain,
                self._build_op(model, sp.alias),
                egress_chain,
            )

            for binding in getattr(sp, "bindings", ()) or ():
                if isinstance(binding, HttpRestBindingSpec):
                    bucket = route_data.setdefault(
                        binding.proto, {"exact": {}, "templated": []}
                    )
                    for method in binding.methods:
                        selector = f"{method.upper()} {binding.path}"
                        opkey_to_meta[OpKey(proto=binding.proto, selector=selector)] = (
                            meta_index
                        )
                        if "{" in binding.path and "}" in binding.path:
                            pattern, names = _compile_path_pattern(binding.path)
                            bucket["templated"].append(
                                {
                                    "method": method.upper(),
                                    "path": binding.path,
                                    "pattern": pattern,
                                    "names": names,
                                    "meta_index": meta_index,
                                    "selector": selector,
                                }
                            )
                        else:
                            bucket["exact"][selector] = meta_index

                elif isinstance(binding, HttpJsonRpcBindingSpec):
                    opkey_to_meta[
                        OpKey(proto=binding.proto, selector=binding.rpc_method)
                    ] = meta_index
                    route_data.setdefault(binding.proto, {})[binding.rpc_method] = (
                        meta_index
                    )

                elif isinstance(binding, WsBindingSpec):
                    bucket = route_data.setdefault(
                        binding.proto, {"exact": {}, "templated": []}
                    )
                    selector = binding.path
                    opkey_to_meta[OpKey(proto=binding.proto, selector=selector)] = (
                        meta_index
                    )

                    if "{" in binding.path and "}" in binding.path:
                        pattern, names = _compile_path_pattern(binding.path)
                        bucket["templated"].append(
                            {
                                "path": binding.path,
                                "pattern": pattern,
                                "names": names,
                                "meta_index": meta_index,
                                "selector": selector,
                                "subprotocols": tuple(binding.subprotocols or ()),
                            }
                        )
                    else:
                        bucket["exact"][selector] = meta_index

    semantic = KernelPlan(
        proto_indices=route_data,
        opmeta=tuple(opmeta),
        opkey_to_meta=opkey_to_meta,
        ingress_chain=ingress_chain,
        phase_chains=phase_chains,
        egress_chain=egress_chain,
        phases=phases,
        mainline_phases=mainline_phases,
        error_phases=error_phases,
    )
    return replace(semantic, packed=self._pack_kernel_plan(semantic))
