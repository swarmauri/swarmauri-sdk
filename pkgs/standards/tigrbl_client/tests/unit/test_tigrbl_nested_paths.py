import pytest

from tigrbl_client import TigrblClient


@pytest.mark.unit
def test_member_path_uses_hash_segment():
    client = TigrblClient("http://example.com/api")
    assert client.member_path("users", "u1") == "/users/#/u1"
    assert client.member_path("users", "u1", "disable") == "/users/#/u1/disable"


@pytest.mark.unit
def test_child_member_path_uses_hash_segments():
    client = TigrblClient("http://example.com/api")
    assert (
        client.child_member_path("users", "u1", "posts", "p1")
        == "/users/#/u1/posts/#/p1"
    )
    assert (
        client.child_member_path("users", "u1", "posts", "p1", "publish")
        == "/users/#/u1/posts/#/p1/publish"
    )


@pytest.mark.unit
def test_collection_op_path_format():
    client = TigrblClient("http://example.com/api")
    assert client.collection_op_path("users", "search") == "/users/search"
