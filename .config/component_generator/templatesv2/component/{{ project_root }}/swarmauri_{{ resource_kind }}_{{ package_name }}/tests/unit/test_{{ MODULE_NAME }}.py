import pytest
import {{ MODULE_NAME }}


def test_resource():
    assert {{ MODULE_NAME }}.resource == {{ resource_kind }}

def test_type():
    assert {{ MODULE_NAME }}.type == {{ MODULE_NAME }}

def test_serialization():
    assert {{ MODULE_NAME }}.id == {{ MODULE_NAME }}.model_validate_json()