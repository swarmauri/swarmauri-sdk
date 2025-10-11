from __future__ import annotations

from .expected_metadata import EXPECTED_METADATA
from .utils import load_table_metadata

TABLE_NAME = "customer_balance"


def test_customer_balance_columns() -> None:
    metadata = load_table_metadata(TABLE_NAME)
    assert metadata["columns"] == EXPECTED_METADATA[TABLE_NAME]["columns"]


def test_customer_balance_foreign_keys() -> None:
    metadata = load_table_metadata(TABLE_NAME)
    assert metadata["foreign_keys"] == EXPECTED_METADATA[TABLE_NAME]["foreign_keys"]


def test_customer_balance_request_schema() -> None:
    metadata = load_table_metadata(TABLE_NAME)
    assert metadata["requests"] == EXPECTED_METADATA[TABLE_NAME]["requests"]


def test_customer_balance_response_schema() -> None:
    metadata = load_table_metadata(TABLE_NAME)
    assert metadata["responses"] == EXPECTED_METADATA[TABLE_NAME]["responses"]
