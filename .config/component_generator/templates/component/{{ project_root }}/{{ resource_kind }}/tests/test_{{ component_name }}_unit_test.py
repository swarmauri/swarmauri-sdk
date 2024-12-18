import pytest
import {{ component_name }}


def test_resource():
    assert {{ component_name }}.resource == {{ resource_kind }}

def test_type():
    assert {{ component_name }}.type == {{ component_name }}

def test_serialization():
    assert {{ component_name }}.id == {{ component_name }}.model_validate_json()