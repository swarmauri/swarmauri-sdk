# tigrbl/v2/precedence.py
from typing import Mapping, Iterable, Callable, Optional, Tuple
from .phase_enum import Phase  # your enum above

HookMap = Mapping[Phase, Iterable[Callable]]


def _get(hooks: Optional[HookMap], p: Phase) -> Tuple[Callable, ...]:
    if not hooks:
        return ()
    v = hooks.get(p, ())
    return tuple(v) if isinstance(v, Iterable) else ()


def precedence_for_phase(
    p: Phase,
    *,
    api: HookMap | None,
    table: HookMap | None,
    op: HookMap | None,
    imperative: HookMap | None,
) -> Tuple[Callable, ...]:
    pre_like = {Phase.PRE_TX_BEGIN, Phase.PRE_HANDLER, Phase.PRE_COMMIT}
    post_like = {
        Phase.POST_HANDLER,
        Phase.POST_COMMIT,
        Phase.POST_RESPONSE,
        Phase.FINAL,
    }
    error_like = {
        Phase.ON_ROLLBACK,
        Phase.ON_PRE_HANDLER_ERROR,
        Phase.ON_HANDLER_ERROR,
        Phase.ON_POST_HANDLER_ERROR,
        Phase.ON_PRE_COMMIT_ERROR,
        Phase.ON_COMMIT_ERROR,
        Phase.ON_POST_COMMIT_ERROR,
        Phase.ON_POST_RESPONSE_ERROR,
        Phase.ON_ERROR,
    }

    if p in pre_like:
        # Pre/enter: broad → specific
        return _get(api, p) + _get(table, p) + _get(op, p) + _get(imperative, p)
    if p in post_like:
        # Post/exit/finally: specific → broad
        return _get(imperative, p) + _get(op, p) + _get(table, p) + _get(api, p)
    if p in error_like:
        # Errors/rollback: nearest handler first
        return _get(imperative, p) + _get(op, p) + _get(table, p) + _get(api, p)

    # Safe default: treat like pre
    return _get(api, p) + _get(table, p) + _get(op, p) + _get(imperative, p)
