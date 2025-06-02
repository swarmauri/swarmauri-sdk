from __future__ import annotations
import asyncio, uuid, logging
from typing import Dict, Set
from ..models import Pool, User, Role
from .rbac import check_role


log = logging.getLogger(__name__)


class PoolManager:
    """In-memory registry; swap to Redis/DB for HA."""

    _pools: Dict[str, Pool] = {}
    _members: Dict[str, Set[str]] = {}  # pool -> member ids

    # ────────────────────────── pool ops ──────────────────────────
    @classmethod
    def create_pool(cls, name: str, user: User) -> Pool:
        check_role(user, {Role.admin})
        if name in cls._pools:
            raise ValueError("Pool exists")
        pool = Pool(name=name)
        cls._pools[name] = pool
        cls._members[name] = set()
        return pool

    @classmethod
    def join_pool(cls, name: str, member_id: str) -> Pool:
        if name not in cls._pools:
            raise ValueError("Pool not found")
        cls._members[name].add(member_id)
        cls._pools[name].members.append(member_id)
        log.debug("Member %s joined %s", member_id, name)
        return cls._pools[name]

    # ────────────────────────── status ──────────────────────────
    @classmethod
    def get_pool(cls, name: str) -> Pool:
        return cls._pools[name]

    @classmethod
    def list_pools(cls):
        return list(cls._pools.values())

    # ────────────────────────── utils ──────────────────────────
    @staticmethod
    def new_member_id() -> str:
        return str(uuid.uuid4())[:8]
