import pytest
import logging
import json
from swarmauri_standard.tools.AdditionTool import AdditionTool
from swarmauri_standard.toolkits.Toolkit import Toolkit

from swarmauri_standard.schema_converters.MistralSchemaConverter import (
    MistralSchemaConverter as Schema,
)


@pytest.mark.unit
def test_ubc_resource():
    assert Schema().resource == "SchemaConverter"


@pytest.mark.unit
def test_ubc_type():
    schema = Schema()
    assert schema.type == "MistralSchemaConverter"


@pytest.mark.unit
def test_serialization():
    schema = Schema()
    assert schema.id == Schema.model_validate_json(schema.model_dump_json()).id


@pytest.mark.unit
def test_convert():
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)
    result = [Schema().convert(toolkit.tools[tool]) for tool in toolkit.tools]
    logging.info(result)
    assert json.loads(json.dumps(result))
