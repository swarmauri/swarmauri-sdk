import pytest
import DeepInfraToolModel


def test_resource():
    assert DeepInfraToolModel.resource == llms

def test_type():
    assert DeepInfraToolModel.type == DeepInfraToolModel

def test_serialization():
    assert DeepInfraToolModel.id == DeepInfraToolModel.model_validate_json()