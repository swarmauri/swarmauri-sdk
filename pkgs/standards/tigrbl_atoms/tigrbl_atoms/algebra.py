from __future__ import annotations
from typing import Any, Awaitable, Callable, Iterable, Sequence, cast
from .types import Atom, Ctx, S, T, U

Pred = Callable[[Ctx[S]], bool]
Acquire = Callable[[Ctx[S]], Awaitable[Any]]
Release = Callable[[Ctx[T], Any], Awaitable[None]]


def seq(a: Atom[S, T], b: Atom[T, U]) -> Atom[S, U]:
    class _Seq(Atom[S, U]):
        name = f"seq({a.name};{b.name})"
        anchor = getattr(b, "anchor", "")

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[U]:
            return await b(obj, await a(obj, ctx))

    return _Seq()


def when(pred: Pred[S], a: Atom[S, S]) -> Atom[S, S]:
    class _When(Atom[S, S]):
        name = f"when({getattr(pred, '__name__', 'pred')}) {a.name}"
        anchor = getattr(a, "anchor", "")

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[S]:
            return await a(obj, ctx) if pred(ctx) else ctx

    return _When()


def chain(*atoms: Atom[Any, Any]) -> Atom[Any, Any]:
    if not atoms:
        raise ValueError("chain requires >=1 atom")
    p: Atom[Any, Any] = atoms[0]
    for n in atoms[1:]:
        p = seq(cast(Atom[Any, Any], p), cast(Atom[Any, Any], n))
    return p


def id_atom(name: str = "id") -> Atom[S, S]:
    class _Id(Atom[S, S]):
        anchor = ""

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[S]:
            return ctx

    i = _Id()
    i.name = name
    return i


def choice(
    cases: Sequence[tuple[Pred[S], Atom[S, T]]], *, default: Atom[S, T] | None = None
) -> Atom[S, T]:
    class _Choice(Atom[S, T]):
        name = "choice"
        anchor = getattr(default, "anchor", "") if default else ""

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[T]:
            for p, a in cases:
                if p(ctx):
                    return await a(obj, ctx)
            if default is None:
                raise LookupError("choice: no case matched")
            return await default(obj, ctx)

    return _Choice()


def try_(a: Atom[S, T]) -> Atom[S, T]:
    class _Try(Atom[S, T]):
        name = f"try({a.name})"
        anchor = getattr(a, "anchor", "")

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[T]:
            try:
                return await a(obj, ctx)
            except Exception as e:
                ctx.error = e
                return ctx.promote(type(ctx))

    return _Try()


def recover(
    pred: Pred[T], handler: Atom[T, T], *, label: str = "recover"
) -> Atom[T, T]:
    class _Recover(Atom[T, T]):
        name = label
        anchor = getattr(handler, "anchor", "")

        async def __call__(self, obj: object | None, ctx: Ctx[T]) -> Ctx[T]:
            return await handler(obj, ctx) if pred(ctx) else ctx

    return _Recover()


def bracket(
    acquire: Acquire[S],
    use: Atom[S, T],
    release: Release[T],
    *,
    resource_key: str = "resource",
) -> Atom[S, T]:
    class _Bracket(Atom[S, T]):
        name = f"bracket({use.name})"
        anchor = getattr(use, "anchor", "")

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[T]:
            res = await acquire(ctx)
            ctx.bag[resource_key] = res
            try:
                return await use(obj, ctx)
            finally:
                await release(ctx.promote(type(ctx)), res)

    return _Bracket()


def loop_over(
    key: str, body: Callable[[Ctx[S], Any], Awaitable[None]], *, label: str = "loop"
) -> Atom[S, S]:
    class _Loop(Atom[S, S]):
        name = label
        anchor = ""

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[S]:
            it = ctx.bag.get(key)
            if not isinstance(it, Iterable):
                raise TypeError(f"ctx.bag[{key!r}] must be Iterable")
            for item in it:
                await body(ctx, item)
            return ctx

    return _Loop()


def fold_over(
    key: str,
    init: Any,
    step: Callable[[Any, Any, Ctx[S]], Any],
    *,
    out_key: str,
    label: str = "fold",
) -> Atom[S, S]:
    class _Fold(Atom[S, S]):
        name = label
        anchor = ""

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[S]:
            it = ctx.bag.get(key)
            if not isinstance(it, Iterable):
                raise TypeError(f"ctx.bag[{key!r}] must be Iterable")
            acc = init
            for item in it:
                acc = step(acc, item, ctx)
            ctx.bag[out_key] = acc
            return ctx

    return _Fold()


def map_(
    src_key: str, dst_key: str, f: Callable[[Any], Any], *, label: str = "map"
) -> Atom[S, S]:
    class _Map(Atom[S, S]):
        name = label
        anchor = ""

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[S]:
            ctx.bag[dst_key] = f(ctx.bag.get(src_key))
            return ctx

    return _Map()


def bind_(
    src_key: str,
    dst_key: str,
    f: Callable[[Any, Ctx[S]], Awaitable[Any]],
    *,
    label: str = "bind",
) -> Atom[S, S]:
    class _Bind(Atom[S, S]):
        name = label
        anchor = ""

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[S]:
            ctx.bag[dst_key] = await f(ctx.bag.get(src_key), ctx)
            return ctx

    return _Bind()


def tap(
    effect: Callable[[Ctx[S]], Awaitable[None]] | Callable[[Ctx[S]], None],
    *,
    label: str = "tap",
) -> Atom[S, S]:
    class _Tap(Atom[S, S]):
        name = label
        anchor = ""

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[S]:
            r = effect(ctx)
            if hasattr(r, "__await__"):
                await cast(Awaitable[None], r)
            return ctx

    return _Tap()


def assert_(pred: Pred[S], msg: str, *, label: str = "assert") -> Atom[S, S]:
    class _Assert(Atom[S, S]):
        name = label
        anchor = ""

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[S]:
            if not pred(ctx):
                raise AssertionError(msg)
            return ctx

    return _Assert()


def require(
    getter: Callable[[Ctx[S]], Any], msg: str, *, label: str = "require"
) -> Atom[S, S]:
    class _Require(Atom[S, S]):
        name = label
        anchor = ""

        async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[S]:
            if not getter(ctx):
                raise ValueError(msg)
            return ctx

    return _Require()
