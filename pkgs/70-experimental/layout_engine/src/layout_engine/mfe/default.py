from __future__ import annotations
from typing import Iterable

from .spec import Remote
from .base import IRemoteRegistry, IImportMapBuilder


class RemoteRegistry(IRemoteRegistry):
    def __init__(self, remotes: Iterable[Remote] = ()):
        self._r: dict[str, Remote] = {}
        for r in remotes:
            self.register(r)

    def register(self, remote: Remote) -> None:
        if remote.id in self._r:
            raise ValueError(f"remote id already registered: {remote.id}")
        self._r[remote.id] = remote

    def register_many(self, remotes: Iterable[Remote]) -> None:
        for r in remotes:
            self.register(r)

    def get(self, id: str) -> Remote:
        try:
            return self._r[id]
        except KeyError:
            raise KeyError(f"unknown remote id: {id}")

    def try_get(self, id: str) -> Remote | None:
        return self._r.get(id)

    def remove(self, id: str) -> None:
        self._r.pop(id, None)

    def all(self):
        return list(self._r.values())

    def to_dict(self) -> dict[str, dict]:
        from .bindings import to_dict as _to

        return {rid: _to(r) for rid, r in self._r.items()}

    def update_from_dict(self, data: dict[str, dict]) -> None:
        from .bindings import from_dict as _from

        for rid, obj in data.items():
            r = _from(obj)
            # ensure key and dataclass id aligned (use dict key as authority)
            if rid != r.id:
                r = Remote(
                    id=rid,
                    framework=r.framework,
                    entry=r.entry,
                    exposed=r.exposed,
                    integrity=r.integrity,
                )
            # upsert
            self._r[rid] = r


class ImportMapBuilder(IImportMapBuilder):
    def build(
        self,
        registry: IRemoteRegistry,
        *,
        extra_imports: dict[str, str] | None = None,
        scopes: dict[str, dict[str, str]] | None = None,
    ) -> dict:
        imports = {rid: r.entry for rid, r in registry.to_dict().items()}
        if extra_imports:
            imports.update(extra_imports)
        out = {"imports": imports}
        if scopes:
            out["scopes"] = scopes
        return out
