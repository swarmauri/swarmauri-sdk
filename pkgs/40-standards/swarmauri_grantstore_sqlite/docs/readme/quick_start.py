from swarmauri_grantstore_sqlite import SqliteGrantStore


def store_grant(*, grant):
    """Bind caller-owned resources before executing this integration."""
    store = SqliteGrantStore(path="grants.db")
    # Grant records are produced by the delegation service.
    store.create(grant)
    restored = store.load(grant.grant_id)
    # save() returns an incremented revision and rejects stale writers.
