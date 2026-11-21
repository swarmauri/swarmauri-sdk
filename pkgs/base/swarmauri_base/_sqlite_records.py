"""Shared on-disk JSON persistence with atomic revision checks."""

import json
import sqlite3
from contextlib import closing
from dataclasses import asdict, replace
from pathlib import Path

from swarmauri_core.permissions import Permission


class SqliteRecords:
    """Store task/grant records without coupling their repositories."""

    def __init__(self, path, table, record_type, conflict):
        if str(path) == ":memory:":
            raise ValueError("Use an on-disk database for durable records")
        if table not in {"tasks", "grants"}:
            raise ValueError("Unknown record table")
        self.path = Path(path)
        self.table = table
        self.record_type = record_type
        self.conflict = conflict
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute(
                f"CREATE TABLE IF NOT EXISTS {table} "
                "(id TEXT PRIMARY KEY, revision INTEGER NOT NULL, "
                "payload TEXT NOT NULL)"
            )

    def create(self, record):
        if record.revision != 0:
            raise self.conflict("New records require revision zero")
        identifier = getattr(record, self.table[:-1] + "_id")
        with closing(sqlite3.connect(self.path)) as db, db:
            try:
                db.execute(
                    f"INSERT INTO {self.table} VALUES (?, ?, ?)",
                    (identifier, 0, json.dumps(asdict(record))),
                )
            except sqlite3.IntegrityError as exc:
                raise self.conflict("Record already exists") from exc

    def load(self, identifier):
        with closing(sqlite3.connect(self.path)) as db:
            row = db.execute(
                f"SELECT payload FROM {self.table} WHERE id = ?",
                (identifier,),
            ).fetchone()
        if row is None:
            raise KeyError(identifier)
        data = json.loads(row[0])
        data["permissions"] = tuple(
            Permission(**p) for p in data["permissions"]
        )
        if "execution_ids" in data:
            data["execution_ids"] = tuple(data["execution_ids"])
        return self.record_type(**data)

    def save(self, record):
        identifier = getattr(record, self.table[:-1] + "_id")
        updated = replace(record, revision=record.revision + 1)
        with closing(sqlite3.connect(self.path)) as db, db:
            cursor = db.execute(
                f"UPDATE {self.table} SET revision = ?, payload = ? "
                "WHERE id = ? AND revision = ?",
                (
                    updated.revision,
                    json.dumps(asdict(updated)),
                    identifier,
                    record.revision,
                ),
            )
            if cursor.rowcount != 1:
                raise self.conflict("Stale record revision")
        return updated
