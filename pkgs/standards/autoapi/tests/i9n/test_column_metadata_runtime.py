"""Tests for deprecated column metadata configuration."""

import pytest

from autoapi.v3 import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.schema import _build_schema
from autoapi.v3.types import Column, String


@pytest.mark.i9n
def test_col_info_autoapi_emits_deprecation_warning():
    with pytest.deprecated_call(match=r"col\.info\['autoapi'\] is deprecated"):

        class Example(Base, GUIDPk):
            __tablename__ = "example_model"
            name = Column(String, info={"autoapi": {"read_only": True}})

        _build_schema(Example, verb="read")
