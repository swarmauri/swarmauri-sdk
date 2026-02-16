from tigrbl_client import TigrblClient


def test_collection_path_builds_collection_and_collection_op() -> None:
    assert TigrblClient.collection_path("widget") == "/widget"
    assert TigrblClient.collection_path("widget", "bulk_merge") == "/widget/bulk_merge"


def test_member_path_builds_member_and_member_op() -> None:
    assert TigrblClient.member_path("widget", "abc-123") == "/widget/__/abc-123"
    assert (
        TigrblClient.member_path("widget", "abc-123", "rotate")
        == "/widget/__/abc-123/rotate"
    )


def test_child_member_path_builds_nested_member_path() -> None:
    assert (
        TigrblClient.child_member_path("widget", "w1", "version", "v2")
        == "/widget/__/w1/version/__/v2"
    )
    assert (
        TigrblClient.child_member_path("widget", "w1", "version", "v2", "read")
        == "/widget/__/w1/version/__/v2/read"
    )
