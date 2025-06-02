from dqueue.pools.manager import PoolManager, User, Role


def test_join_spawn():
    admin = User(username="boss", role=Role.admin)
    pool = PoolManager.create_pool("zeta", admin)
    member_id = PoolManager.new_member_id()
    PoolManager.join_pool(pool.name, member_id)
    assert member_id in pool.members
