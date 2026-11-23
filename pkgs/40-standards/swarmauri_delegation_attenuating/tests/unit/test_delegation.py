import time
from dataclasses import replace
import pytest
from swarmauri_core.permissions import Permission
from swarmauri_core.tasks import TaskRecord
from swarmauri_taskstore_sqlite import SqliteTaskStore
from swarmauri_grantstore_sqlite import SqliteGrantStore
from swarmauri_permission_explicit import ExplicitPermissionPolicy
from swarmauri_delegation_attenuating import AttenuatingDelegationService
from swarmauri_workflow_documentassistant.demo import demo_tokens

pytestmark = pytest.mark.unit


async def setup_service(tmp_path):
    tokens, kid, issuer = await demo_tokens()
    tasks = SqliteTaskStore(path=tmp_path / "tasks.db")
    permission = Permission("read", "doc:123", "tenant")
    tasks.create(
        TaskRecord(
            "task",
            "alice",
            "tenant",
            (permission,),
            int(time.time()) + 60,
        )
    )
    service = AttenuatingDelegationService(
        tasks=tasks,
        grants=SqliteGrantStore(path=tmp_path / "grants.db"),
        policy=ExplicitPermissionPolicy(),
        tokens=tokens,
        kid=kid,
        issuer=issuer,
        edges=frozenset({("A", "B"), ("B", "C")}),
    )
    return service, permission


async def test_real_jwt_and_live_ancestry_revocation(tmp_path):
    service, permission = await setup_service(tmp_path)
    root = service.root("task", "A", (permission,), 2)
    child = service.delegate(root.grant_id, "A", "B", (permission,))
    credential = await service.credential(child.grant_id, "A", "B", permission)
    assert (await service.verify(credential.token, "B", permission)) == child
    with pytest.raises(Exception):
        await service.verify(credential.token, "C", permission)
    service.revoke(root.grant_id)
    with pytest.raises(PermissionError):
        await service.verify(credential.token, "B", permission)


async def test_narrowing_depth_actor_tenant_and_task_state(tmp_path):
    service, permission = await setup_service(tmp_path)
    root = service.root("task", "A", (permission,), 1)
    for requested in (
        Permission("write", "doc:123", "tenant"),
        Permission("read", "doc:456", "tenant"),
        Permission("read", "doc:123", "other"),
    ):
        with pytest.raises(PermissionError):
            service.delegate(root.grant_id, "A", "B", (requested,))
    with pytest.raises(PermissionError):
        service.delegate(root.grant_id, "intruder", "B", (permission,))
    child = service.delegate(root.grant_id, "A", "B", (permission,))
    with pytest.raises(PermissionError):
        service.delegate(child.grant_id, "B", "C", (permission,))
    task = service.tasks.load("task")
    service.tasks.save(replace(task, status="paused"))
    with pytest.raises(PermissionError):
        service.validate(child.grant_id, "B", permission)


async def test_expired_and_cyclic_grants_fail_closed(tmp_path):
    service, permission = await setup_service(tmp_path)
    root = service.root("task", "A", (permission,), 2)
    service.grants.save(replace(root, parent_id=root.grant_id))
    with pytest.raises(PermissionError):
        service.validate(root.grant_id, "A", permission)
    expired = service.root("task", "A", (permission,), 1)
    service.grants.save(replace(expired, expires_at=int(time.time()) - 1))
    with pytest.raises(PermissionError):
        service.validate(expired.grant_id, "A", permission)
